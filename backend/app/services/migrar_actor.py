# -*- coding: utf-8 -*-
"""Mueve una cuenta entre `usuarios` y `personal` cuando un cambio de rol
cruza la frontera entre las dos tablas (usuario -> gestor/admin, o
gestor/admin -> usuario) -- ver
`~/.claude/plans/dazzling-wobbling-zebra.md`.

No es un `UPDATE` simple: hay que insertar en la tabla destino (con un id
NUEVO de su propia secuencia -- ver el porqué en el docstring de
`promover_a_personal`), repuntar cualquier reserva/notificación/auditoría
que tuviera a esa persona como actor (`usuario_id`/`personal_id`
polimórficos, ver `Reserva.actor`) al id nuevo, y solo entonces borrar la
fila de la tabla origen. Todo dentro de la sesión que ya trae `db` -- si
algo falla más adelante en el mismo request, todo el movimiento se
revierte junto con el resto (ningún `db.commit()` intermedio acá).
"""

import secrets

from sqlalchemy.orm import Session
from sqlalchemy import text

from app.auth.auth import hash_password
from app.models.personal import Personal
from app.models.usuario import Usuario
from app.models.usuario_espacio import UsuarioEspacio


def promover_a_personal(db: Session, usuario: Usuario, rol: str, espacio_id: int | None) -> Personal:
    """usuario -> gestor/admin. `rol` ya validado por quien llama (admin o
    gestor, nunca usuario -- ver `schemas/personal.py::PersonalCreate`).

    A diferencia de la migración inicial (`migrations.py::
    _COPIAR_ADMIN_GESTOR_A_PERSONAL`, que preserva el mismo `id` porque
    mueve TODAS las filas admin/gestor a una tabla `personal` recién
    creada y todavía vacía), acá `personal` puede ya tener filas de su
    propia secuencia -- reusar el `id` de `usuario` chocaría con un id ya
    ocupado en `personal` (las dos tablas tienen secuencias
    independientes que arrancan igual en 1, 2, 3...). Por eso acá se dejar
    que `personal` asigne un id nuevo con su propio `SERIAL` y se repuntan
    las referencias existentes del id viejo al nuevo."""
    viejo_id = usuario.id
    nuevo_id = db.execute(
        text(
            """
            INSERT INTO personal (
                username, email, supabase_id, rol,
                documento_identificacion, telefono, institucion, vinculacion, dependencia,
                created_at, updated_at
            )
            SELECT
                username, email, supabase_id, :rol,
                documento_identificacion, telefono, institucion, vinculacion, dependencia,
                created_at, updated_at
            FROM usuarios WHERE id = :usuario_id
            RETURNING id
            """
        ),
        {"usuario_id": viejo_id, "rol": rol},
    ).scalar_one()
    for tabla in ("reservas", "notificaciones", "control_cambios"):
        db.execute(
            text(f"UPDATE {tabla} SET personal_id = :nuevo_id, usuario_id = NULL WHERE usuario_id = :viejo_id"),
            {"nuevo_id": nuevo_id, "viejo_id": viejo_id},
        )
    db.execute(text("DELETE FROM usuarios WHERE id = :id"), {"id": viejo_id})
    db.flush()

    if rol == "gestor" and espacio_id is not None:
        db.add(UsuarioEspacio(usuario_id=nuevo_id, espacio_id=espacio_id))

    db.commit()
    nuevo = db.query(Personal).filter(Personal.id == nuevo_id).first()
    db.refresh(nuevo)
    return nuevo


def degradar_a_usuario(db: Session, personal: Personal) -> Usuario:
    """gestor/admin -> usuario. Falla con `IntegrityError` (traducido a 409
    por quien llama, `api/personal.py`) si esta persona todavía figura
    como `created_by`/`updated_by` de algún recurso/zona/ensayo/espacio --
    esas FK apuntan a `personal.id` sin `ON DELETE`, así que Postgres
    rechaza el `DELETE` en vez de dejar una referencia rota. No se intenta
    detectar ese caso de antemano: dejar que la constraint real lo
    resuelva es más simple y más seguro que reimplementar la misma
    verificación a mano."""
    viejo_id = personal.id
    nuevo_id = db.execute(
        text(
            """
            INSERT INTO usuarios (
                username, email, hashed_password, rol, supabase_id,
                documento_identificacion, telefono, institucion, vinculacion, dependencia,
                created_at, updated_at
            )
            SELECT
                username, email, :hashed_password, 'usuario', supabase_id,
                documento_identificacion, telefono, institucion, vinculacion, dependencia,
                created_at, updated_at
            FROM personal WHERE id = :personal_id
            RETURNING id
            """
        ),
        {"personal_id": viejo_id, "hashed_password": hash_password(secrets.token_urlsafe(32))},
    ).scalar_one()
    for tabla in ("reservas", "notificaciones", "control_cambios"):
        db.execute(
            text(f"UPDATE {tabla} SET usuario_id = :nuevo_id, personal_id = NULL WHERE personal_id = :viejo_id"),
            {"nuevo_id": nuevo_id, "viejo_id": viejo_id},
        )
    db.execute(text("DELETE FROM usuarios_espacios WHERE usuario_id = :id"), {"id": viejo_id})
    db.execute(text("DELETE FROM personal WHERE id = :id"), {"id": viejo_id})
    db.commit()
    nuevo = db.query(Usuario).filter(Usuario.id == nuevo_id).first()
    db.refresh(nuevo)
    return nuevo
