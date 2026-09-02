# -*- coding: utf-8 -*-
"""Auditoría de cambios administrativos.

`AuditoriaSesion` es el adaptador del protocolo `RegistroAuditoria` del
dominio a la persistencia SQLAlchemy: recibe únicamente primitivas y crea la
fila `ControlCambio` en la sesión inyectada. El commit sigue siendo
responsabilidad del flujo que la usa (igual que antes).

`registrar_cambio()` se conserva como wrapper compatible para los módulos
que ya lo importan (`api/usuarios.py`, `api/laboratorios.py`, `api/recursos.py`,
`services/reservas.py`).
"""

from sqlalchemy.orm import Session

from app.models import ControlCambio, Personal, Usuario
from app.services.actores import columnas_actor


class AuditoriaSesion:
    """Adaptador RegistroAuditoria → persistencia."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def registrar(
        self,
        *,
        usuario_id: int | None,
        personal_id: int | None,
        accion: str,
        entidad: str,
        entidad_id: int | None,
        descripcion: str,
    ) -> None:
        self._db.add(
            ControlCambio(
                usuario_id=usuario_id,
                personal_id=personal_id,
                accion=accion,
                entidad=entidad,
                entidad_id=entidad_id,
                descripcion=descripcion,
            )
        )


def registrar_cambio(
    db: Session,
    actor: Personal | Usuario,
    accion: str,
    entidad: str,
    entidad_id: int | None,
    descripcion: str,
) -> None:
    """Wrapper compatible: delega en AuditoriaSesion. `actor` puede ser
    `Personal` o `Usuario` -- el actor de un cambio de auditoría es
    polimórfico (ver `columnas_actor`)."""
    AuditoriaSesion(db).registrar(
        **columnas_actor(actor),
        accion=accion,
        entidad=entidad,
        entidad_id=entidad_id,
        descripcion=descripcion,
    )
