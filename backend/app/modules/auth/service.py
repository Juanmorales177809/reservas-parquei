"""Lógica de sesión: inicio, renovación, cierre (carril A: AUTH-A1 a AUTH-A3)."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core import audit
from app.core.authz import resolver_rol
from app.core.config import get_settings
from app.core.errors import CredencialesInvalidas, NoAutenticado
from app.core.rate_limit import limitar
from app.core.security import (
    emitir_token_acceso,
    generar_token,
    hash_contrasena,
    hashear_token,
    verificar_contrasena,
)
from app.db.models.auth import Sesiones
from app.db.models.identidad import Usuarios
from app.modules.auth import repository as repo

# Hash de referencia para que verificar una contraseña contra una cuenta
# inexistente cueste lo mismo en CPU que contra una real (equivalencia de
# tiempo de SEC-ABU-02). Generado una sola vez al importar el módulo.
_HASH_SEÑUELO = hash_contrasena("contraseña-señuelo-sin-significado-especial")

VIGENCIA_REFRESH_SEGUNDOS = 12 * 60 * 60  # igual a la vigencia máxima de sesión


def _aware(dt: datetime) -> datetime:
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def limitar_login(clave: str) -> None:
    limitar(f"login:{clave}", maximo=5, ventana_segundos=15 * 60)


def _actualizacion_inicial_pendiente(db: Session, cuenta) -> bool | None:
    if cuenta.tipo_cuenta != "USUARIO":
        return None
    usuario = db.get(Usuarios, cuenta.id_usuario)
    return usuario.perfil_actualizado_at is None


def iniciar_sesion(db: Session, correo: str, contrasena: str) -> tuple[dict, str, str]:
    """Devuelve `(datos_respuesta, token_acceso, secreto_refresh)`.

    Contraseña incorrecta, correo inexistente, cuenta inactiva e identidad
    inactiva producen exactamente el mismo resultado observable: se decide
    todo **después** de la verificación de contraseña, nunca antes, para no
    filtrar por tiempo cuál de las cuatro causas fue (RN-AUTH-ID-01,
    RN-AUTH-ID-05, SEC-ABU-02).
    """
    cuenta = repo.obtener_cuenta_por_correo(db, correo)
    hash_a_verificar = cuenta.password_hash if cuenta else _HASH_SEÑUELO
    contrasena_ok = verificar_contrasena(contrasena, hash_a_verificar)

    valido = (
        cuenta is not None
        and contrasena_ok
        and cuenta.estado
        and repo.identidad_activa(db, cuenta)
    )
    if not valido:
        # SEC-AUD-02: "intentos fallidos relevantes". Sin cuenta no hay actor
        # a quien atribuir el registro (FK NOT NULL de administration.auditoria);
        # se audita solo cuando la cuenta existe.
        if cuenta is not None:
            audit.registrar(
                db, actor_cuenta_id=cuenta.id_cuenta, entidad="auth.cuentas",
                entidad_id=cuenta.id_cuenta, accion="INICIO_SESION_FALLIDO",
            )
            db.commit()
        raise CredencialesInvalidas()

    refresh_token, refresh_hash = generar_token()
    sesion = repo.crear_sesion(db, cuenta.id_cuenta, refresh_hash, VIGENCIA_REFRESH_SEGUNDOS)
    audit.registrar(
        db, actor_cuenta_id=cuenta.id_cuenta, entidad="auth.sesiones",
        entidad_id=sesion.id_sesion, accion="INICIO_SESION",
    )
    db.commit()

    token_acceso = emitir_token_acceso(sub=str(cuenta.id_cuenta), sid=str(sesion.id_sesion))
    rol = resolver_rol(db, cuenta.id_cuenta).rol

    datos = {
        "id_cuenta": cuenta.id_cuenta,
        "tipo_cuenta": cuenta.tipo_cuenta,
        "rol": rol,
        "actualizacion_inicial_pendiente": _actualizacion_inicial_pendiente(db, cuenta),
        "correo": cuenta.correo,
        "id_sesion": str(sesion.id_sesion),
        "expira_en": sesion.expires_at,
    }
    return datos, token_acceso, refresh_token


def renovar_sesion(db: Session, refresh_token: str | None) -> tuple[dict, str, str]:
    """Devuelve `(datos_respuesta, nuevo_token_acceso, nuevo_secreto_refresh)`."""
    if not refresh_token:
        raise NoAutenticado()

    hash_recibido = hashear_token(refresh_token)
    sesion = db.scalar(select(Sesiones).where(Sesiones.refresh_token_hash == hash_recibido))
    if sesion is None or sesion.revoked_at is not None:
        raise NoAutenticado()

    ahora = datetime.now(timezone.utc)
    if _aware(sesion.expires_at) <= ahora:
        raise NoAutenticado()
    inactividad_maxima = get_settings().sesion_inactividad_maxima_segundos
    if (ahora - _aware(sesion.ultima_actividad_at)).total_seconds() > inactividad_maxima:
        raise NoAutenticado()

    cuenta = repo.obtener_cuenta(db, sesion.id_cuenta)
    if cuenta is None or not cuenta.estado or not repo.identidad_activa(db, cuenta):
        raise NoAutenticado()

    nuevo_refresh, nuevo_hash = generar_token()
    repo.rotar_refresh(db, sesion, nuevo_hash, VIGENCIA_REFRESH_SEGUNDOS)
    sesion.ultima_actividad_at = ahora
    db.commit()

    nuevo_acceso = emitir_token_acceso(sub=str(cuenta.id_cuenta), sid=str(sesion.id_sesion))

    datos = {
        "id_sesion": str(sesion.id_sesion),
        "expira_en": sesion.expires_at,
        "actualizacion_inicial_pendiente": _actualizacion_inicial_pendiente(db, cuenta),
    }
    return datos, nuevo_acceso, nuevo_refresh


def cerrar_sesion(db: Session, id_sesion: str) -> None:
    """`204` siempre: una sesión ya vencida o revocada produce el mismo resultado."""
    sesion = repo.obtener_sesion(db, id_sesion)
    if sesion is not None:
        ya_revocada = sesion.revoked_at is not None
        repo.revocar_sesion(db, sesion)
        if not ya_revocada:
            audit.registrar(
                db, actor_cuenta_id=sesion.id_cuenta, entidad="auth.sesiones",
                entidad_id=sesion.id_sesion, accion="CIERRE_SESION",
            )
        db.commit()
