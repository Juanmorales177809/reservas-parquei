# -*- coding: utf-8 -*-
"""Prueba de regresión del incidente real en producción (2026-08-29,
despliegue del commit `fb246f3`): `migrate_resource_reservations()`
reventaba con

    psycopg2.errors.ForeignKeyViolation: insert or update on table
    "recursos" violates foreign key constraint "recursos_created_by_fkey"
    DETAIL:  Key (created_by)=(2) is not present in table "personal".

Causa real: antes de la separación `personal`/`usuarios`, `PUT /usuarios/{id}`
permitía bajar a alguien de `gestor` a `usuario` con un `UPDATE` directo (sin
el `degradar_a_usuario` de `services/migrar_actor.py`, que no existía
todavía) -- dejando `created_by`/`updated_by`/`update_by` de
`recursos`/`espacios`/`laboratorios` (y `usuario_id` de
`usuarios_laboratorios`) apuntando a un `usuarios.id` cuyo `rol` actual ya es
`'usuario'`.

Nota (Fase 1 de `~/.claude/plans/dazzling-wobbling-zebra.md`): la tabla
`ensayos` ya no forma parte de este escenario -- la feature de Ensayos se
retiró por completo y `_LIMPIAR_CREATED_BY_HUERFANOS`/`_REPUNTAR_FK_DE_PERSONAL`
ya no la referencian.

Corrección real (`_LIMPIAR_CREATED_BY_HUERFANOS`, `app/migrations.py`):
limpiar esas referencias huérfanas a NULL (columnas de auditoría, se
volvieron nullable) y borrar la fila de `usuarios_laboratorios` huérfana (esa
sí es una asignación real, no auditoría) -- **antes** de repuntar las FK,
en vez de intentar copiar al usuario degradado a `personal` (una primera
versión de esta corrección lo hacía, pero eso arriesgaba corromper en
silencio el backfill de `reservas`/`notificaciones`/`control_cambios`
moviendo a `personal_id` incluso las filas creadas por esa persona
DESPUÉS de la degradación).

Se ejercita **únicamente contra un esquema desechable** (mismo patrón que
`test_migrations_rollback_12c4e.py`) con tablas mínimas que reproducen el
estado real de producción -- nunca contra `public`.
"""

import uuid

import pytest
from sqlalchemy import text

from app.db import engine
from app.migrations import (
    _COPIAR_ADMIN_GESTOR_A_PERSONAL,
    _LIMPIAR_CREATED_BY_HUERFANOS,
    _REPUNTAR_FK_DE_PERSONAL,
)

_TABLAS_MINIMAS = """
CREATE TABLE {s}.usuarios (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    supabase_id UUID,
    rol VARCHAR(20) NOT NULL,
    documento_identificacion VARCHAR(30),
    telefono VARCHAR(30),
    institucion VARCHAR(120),
    vinculacion VARCHAR(30),
    dependencia VARCHAR(150),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE {s}.personal (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    supabase_id UUID,
    rol VARCHAR(20) NOT NULL CHECK (rol IN ('admin', 'gestor')),
    documento_identificacion VARCHAR(30),
    telefono VARCHAR(30),
    institucion VARCHAR(120),
    vinculacion VARCHAR(30),
    dependencia VARCHAR(150),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE {s}.usuarios_laboratorios (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER
);
CREATE TABLE {s}.recursos (
    id SERIAL PRIMARY KEY,
    created_by INTEGER,
    update_by INTEGER
);
CREATE TABLE {s}.espacios (
    id SERIAL PRIMARY KEY,
    created_by INTEGER,
    updated_by INTEGER
);
CREATE TABLE {s}.laboratorios (
    id SERIAL PRIMARY KEY,
    created_by INTEGER,
    updated_by INTEGER
);
"""


@pytest.fixture()
def esquema_desechable():
    nombre = f"proof_personal_legacy_{uuid.uuid4().hex[:8]}"
    with engine.begin() as conn:
        conn.execute(text(f"CREATE SCHEMA {nombre}"))
        conn.execute(text(_TABLAS_MINIMAS.format(s=nombre)))
    yield nombre
    with engine.begin() as conn:
        conn.execute(text(f"DROP SCHEMA IF EXISTS {nombre} CASCADE"))


def test_created_by_huerfano_se_limpia_a_null_y_no_revienta(esquema_desechable):
    """Reproduce exactamente el estado real de producción: un usuario que
    fue gestor (creó un recurso), se degradó a 'usuario' con un UPDATE
    directo, y encima administraba un espacio (usuarios_laboratorios)."""
    with engine.begin() as conn:
        conn.execute(text(f"SET search_path TO {esquema_desechable}, public"))

        conn.execute(
            text(
                "INSERT INTO usuarios (username, email, rol) "
                "VALUES ('gestor_degradado', 'gestor_degradado@example.com', 'gestor')"
            )
        )
        usuario_id = conn.execute(text("SELECT id FROM usuarios WHERE username = 'gestor_degradado'")).scalar_one()
        conn.execute(text("INSERT INTO recursos (created_by, update_by) VALUES (:id, :id)"), {"id": usuario_id})
        conn.execute(text("INSERT INTO espacios (created_by, updated_by) VALUES (:id, :id)"), {"id": usuario_id})
        conn.execute(text("INSERT INTO laboratorios (created_by, updated_by) VALUES (:id, :id)"), {"id": usuario_id})
        conn.execute(text("INSERT INTO usuarios_laboratorios (usuario_id) VALUES (:id)"), {"id": usuario_id})
        # ...y después se degradó a usuario común (UPDATE directo, como
        # permitía PUT /usuarios/{id} antes de esta separación).
        conn.execute(text("UPDATE usuarios SET rol = 'usuario' WHERE id = :id"), {"id": usuario_id})

        # No debe lanzar ForeignKeyViolation.
        conn.execute(text(_COPIAR_ADMIN_GESTOR_A_PERSONAL))
        conn.execute(text(_LIMPIAR_CREATED_BY_HUERFANOS))
        conn.execute(text(_REPUNTAR_FK_DE_PERSONAL))

        # personal NO debe contener a este usuario -- ya no es gestor.
        assert conn.execute(text("SELECT 1 FROM personal WHERE id = :id"), {"id": usuario_id}).first() is None

        assert conn.execute(text("SELECT created_by, update_by FROM recursos")).first() == (None, None)
        assert conn.execute(text("SELECT created_by, updated_by FROM espacios")).first() == (None, None)
        assert conn.execute(text("SELECT created_by, updated_by FROM laboratorios")).first() == (None, None)
        # La asignación usuarios_laboratorios se borra entera, no se deja en NULL.
        assert conn.execute(text("SELECT count(*) FROM usuarios_laboratorios")).scalar_one() == 0

        # El usuario real (rol actual) sigue intacto en usuarios.
        rol_actual = conn.execute(text("SELECT rol FROM usuarios WHERE id = :id"), {"id": usuario_id}).scalar_one()
        assert rol_actual == "usuario"


def test_created_by_de_admin_gestor_vigente_no_se_toca(esquema_desechable):
    """No regresión: un created_by/updated_by de alguien que SIGUE siendo
    admin/gestor no se limpia -- solo se limpian los huérfanos."""
    with engine.begin() as conn:
        conn.execute(text(f"SET search_path TO {esquema_desechable}, public"))
        conn.execute(text("INSERT INTO usuarios (username, email, rol) VALUES ('gestor_vigente', 'gestor_vigente@example.com', 'gestor')"))
        usuario_id = conn.execute(text("SELECT id FROM usuarios WHERE username = 'gestor_vigente'")).scalar_one()
        conn.execute(text("INSERT INTO recursos (created_by, update_by) VALUES (:id, :id)"), {"id": usuario_id})

        conn.execute(text(_COPIAR_ADMIN_GESTOR_A_PERSONAL))
        conn.execute(text(_LIMPIAR_CREATED_BY_HUERFANOS))
        conn.execute(text(_REPUNTAR_FK_DE_PERSONAL))

        assert conn.execute(text("SELECT created_by, update_by FROM recursos")).first() == (usuario_id, usuario_id)
