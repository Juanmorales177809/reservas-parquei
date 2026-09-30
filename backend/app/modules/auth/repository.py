"""Acceso a datos de sesión y cuentas (carril A: AUTH-A2, AUTH-A3).

Nunca crea ni modifica tablas: solo lee y escribe filas conforme al esquema
que las migraciones ya instalaron.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.auth import Cuentas, Sesiones
from app.db.models.identidad import Personal, Usuarios


def obtener_cuenta_por_correo(db: Session, correo: str) -> Cuentas | None:
    return db.scalar(select(Cuentas).where(Cuentas.correo == correo))


def obtener_cuenta(db: Session, id_cuenta: int) -> Cuentas | None:
    return db.get(Cuentas, id_cuenta)


def identidad_activa(db: Session, cuenta: Cuentas) -> bool:
    """`RN-AUTH-ID-01`/`RN-AUTH-ID-05`: la identidad vinculada también debe estar activa."""
    if cuenta.tipo_cuenta == "ADMINISTRADOR":
        return True  # no tiene identidad asociada: basta con que la cuenta esté activa
    if cuenta.tipo_cuenta == "PERSONAL":
        persona = db.get(Personal, cuenta.id_persona)
        return persona is not None and bool(persona.estado)
    usuario = db.get(Usuarios, cuenta.id_usuario)
    return usuario is not None and bool(usuario.estado)


def crear_sesion(
    db: Session, id_cuenta: int, refresh_hash: str, vigencia_segundos: int
) -> Sesiones:
    ahora = datetime.now(timezone.utc)
    sesion = Sesiones(
        id_cuenta=id_cuenta,
        refresh_token_hash=refresh_hash,
        created_at=ahora,
        expires_at=ahora + timedelta(seconds=vigencia_segundos),
        ultima_actividad_at=ahora,
    )
    db.add(sesion)
    db.flush()  # asigna id_sesion (default gen_random_uuid en la base)
    db.refresh(sesion)
    return sesion


def obtener_sesion(db: Session, id_sesion: UUID | str) -> Sesiones | None:
    return db.get(Sesiones, id_sesion)


def revocar_sesion(db: Session, sesion: Sesiones) -> None:
    if sesion.revoked_at is None:
        sesion.revoked_at = datetime.now(timezone.utc)


def revocar_todas_las_sesiones(db: Session, id_cuenta: int) -> int:
    """Revoca las sesiones activas de la cuenta. Devuelve cuántas se revocaron (SEC-SES-10)."""
    ahora = datetime.now(timezone.utc)
    activas = db.scalars(
        select(Sesiones).where(Sesiones.id_cuenta == id_cuenta, Sesiones.revoked_at.is_(None))
    ).all()
    for s in activas:
        s.revoked_at = ahora
    return len(activas)


def rotar_refresh(db: Session, sesion: Sesiones, nuevo_hash: str, vigencia_segundos: int) -> None:
    sesion.refresh_token_hash = nuevo_hash
    sesion.expires_at = datetime.now(timezone.utc) + timedelta(seconds=vigencia_segundos)


def marcar_reautenticado(db: Session, sesion: Sesiones) -> None:
    sesion.reautenticado_at = datetime.now(timezone.utc)
