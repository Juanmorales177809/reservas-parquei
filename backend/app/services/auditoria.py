# -*- coding: utf-8 -*-
"""Auditoría de cambios administrativos.

`AuditoriaSesion` es el adaptador del protocolo `RegistroAuditoria` del
dominio a la persistencia SQLAlchemy: recibe únicamente primitivas y crea la
fila `ControlCambio` en la sesión inyectada. El commit sigue siendo
responsabilidad del flujo que la usa (igual que antes).

`registrar_cambio()` se conserva como wrapper compatible para los módulos
que ya lo importan (`api/usuarios.py`, `api/espacios.py`, `api/recursos.py`,
`services/reservas.py`).
"""

from sqlalchemy.orm import Session

from app.models import ControlCambio, Usuario


class AuditoriaSesion:
    """Adaptador RegistroAuditoria → persistencia."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def registrar(
        self,
        *,
        usuario_id: int,
        accion: str,
        entidad: str,
        entidad_id: int | None,
        descripcion: str,
    ) -> None:
        self._db.add(
            ControlCambio(
                usuario_id=usuario_id,
                accion=accion,
                entidad=entidad,
                entidad_id=entidad_id,
                descripcion=descripcion,
            )
        )


def registrar_cambio(
    db: Session,
    usuario: Usuario,
    accion: str,
    entidad: str,
    entidad_id: int | None,
    descripcion: str,
) -> None:
    """Wrapper compatible: delega en AuditoriaSesion."""
    AuditoriaSesion(db).registrar(
        usuario_id=usuario.id,
        accion=accion,
        entidad=entidad,
        entidad_id=entidad_id,
        descripcion=descripcion,
    )
