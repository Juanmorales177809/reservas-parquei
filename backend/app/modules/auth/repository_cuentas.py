"""Acceso a datos de alta, invitaciones, recuperación y administración
(carril B: AUTH-B1 a AUTH-B5)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.auth import CuentaPermisos, Cuentas, Invitaciones, Permisos, Sesiones, TokensRecuperacion
from app.db.models.identidad import Cargo, Personal, Usuarios

VIGENCIA_INVITACION_SEGUNDOS = 7 * 24 * 60 * 60
VIGENCIA_RECUPERACION_SEGUNDOS = 60 * 60


# --- Identidades (usuarios.usuarios) ----------------------------------------


def obtener_usuario_por_correo(db: Session, correo: str) -> Usuarios | None:
    return db.scalar(select(Usuarios).where(Usuarios.correo == correo))


def documento_o_telefono_duplicado(db: Session, documento: str, telefono: str) -> bool:
    return (
        db.scalar(
            select(Usuarios.id_usuario).where(
                (Usuarios.documento == documento) | (Usuarios.telefono == telefono)
            )
        )
        is not None
    )


def crear_identidad_usuario(
    db: Session, *, nombre: str, documento: str, telefono: str, institucion: str, dependencia: str, correo: str
) -> Usuarios:
    ahora = datetime.now(timezone.utc)
    usuario = Usuarios(
        nombre=nombre,
        documento=documento,
        telefono=telefono,
        institucion=institucion,
        dependencia=dependencia,
        correo=correo,
        estado=True,
        created_at=ahora,
        updated_at=ahora,
        perfil_actualizado_at=None,
    )
    db.add(usuario)
    db.flush()
    return usuario


# --- Cuentas -----------------------------------------------------------------


def crear_cuenta(
    db: Session, *, correo: str, password_hash: str, tipo_cuenta: str,
    id_usuario: int | None = None, id_persona: int | None = None,
) -> Cuentas:
    ahora = datetime.now(timezone.utc)
    cuenta = Cuentas(
        correo=correo,
        password_hash=password_hash,
        tipo_cuenta=tipo_cuenta,
        id_usuario=id_usuario,
        id_persona=id_persona,
        estado=True,
        created_at=ahora,
        updated_at=ahora,
    )
    db.add(cuenta)
    db.flush()
    return cuenta


def obtener_cuenta_por_correo(db: Session, correo: str) -> Cuentas | None:
    return db.scalar(select(Cuentas).where(Cuentas.correo == correo))


def obtener_cuenta(db: Session, id_cuenta: int) -> Cuentas | None:
    return db.get(Cuentas, id_cuenta)


def actualizar_password(db: Session, cuenta: Cuentas, nuevo_hash: str) -> None:
    cuenta.password_hash = nuevo_hash
    cuenta.updated_at = datetime.now(timezone.utc)


def contar_administradores_activos(db: Session, excluir_id_cuenta: int | None = None) -> int:
    """Cuentas `PERSONAL` activas con al menos una asignación global vigente
    (`RN-AUTH-ROL-03`), sin importar el código del permiso."""
    consulta = (
        select(Cuentas.id_cuenta)
        .distinct()
        .join(CuentaPermisos, CuentaPermisos.id_cuenta == Cuentas.id_cuenta)
        .join(Permisos, Permisos.id == CuentaPermisos.permiso_id)
        .where(
            Cuentas.tipo_cuenta == "PERSONAL",
            Cuentas.estado.is_(True),
            CuentaPermisos.id_unidad.is_(None),
            Permisos.habilitado.is_(True),
        )
    )
    if excluir_id_cuenta is not None:
        consulta = consulta.where(Cuentas.id_cuenta != excluir_id_cuenta)
    return len(db.scalars(consulta).all())


# --- Tokens de recuperación --------------------------------------------------


def crear_token_recuperacion(db: Session, id_cuenta: int, token_hash: str) -> TokensRecuperacion:
    ahora = datetime.now(timezone.utc)
    token = TokensRecuperacion(
        id_cuenta=id_cuenta,
        token_hash=token_hash,
        expira_at=ahora + timedelta(seconds=VIGENCIA_RECUPERACION_SEGUNDOS),
        created_at=ahora,
    )
    db.add(token)
    db.flush()
    return token


def obtener_token_recuperacion(db: Session, token_hash: str) -> TokensRecuperacion | None:
    return db.scalar(select(TokensRecuperacion).where(TokensRecuperacion.token_hash == token_hash))


# --- Invitaciones --------------------------------------------------------------


def obtener_personal_por_correo(db: Session, correo: str) -> Personal | None:
    return db.scalar(select(Personal).where(Personal.correo == correo))


def obtener_unidad_del_cargo(db: Session, id_cargo: int) -> int | None:
    cargo = db.get(Cargo, id_cargo)
    return cargo.id_unidad if cargo else None


def invitacion_utilizable_por_correo(db: Session, correo: str) -> Invitaciones | None:
    return db.scalar(
        select(Invitaciones).where(
            Invitaciones.correo == correo,
            Invitaciones.usada_at.is_(None),
            Invitaciones.revocada_at.is_(None),
        )
    )


def crear_invitacion(
    db: Session, *, correo: str, tipo_cuenta: str, token_hash: str, creada_por: int,
    id_usuario: int | None = None, id_persona: int | None = None,
) -> Invitaciones:
    ahora = datetime.now(timezone.utc)
    inv = Invitaciones(
        correo=correo,
        tipo_cuenta=tipo_cuenta,
        id_usuario=id_usuario,
        id_persona=id_persona,
        token_hash=token_hash,
        expira_at=ahora + timedelta(seconds=VIGENCIA_INVITACION_SEGUNDOS),
        creada_por=creada_por,
        created_at=ahora,
    )
    db.add(inv)
    db.flush()
    return inv


def obtener_invitacion(db: Session, id_invitacion: int) -> Invitaciones | None:
    return db.get(Invitaciones, id_invitacion)


def obtener_invitacion_por_token_hash(db: Session, token_hash: str) -> Invitaciones | None:
    return db.scalar(select(Invitaciones).where(Invitaciones.token_hash == token_hash))


def revocar_invitacion(db: Session, invitacion: Invitaciones) -> None:
    if invitacion.usada_at is None and invitacion.revocada_at is None:
        invitacion.revocada_at = datetime.now(timezone.utc)


def renovar_token_invitacion(db: Session, invitacion: Invitaciones, token_hash: str) -> None:
    """§4.2 — reenvío: opera sobre la MISMA fila, no crea otra. El token
    anterior queda invalidado porque deja de coincidir con ningún hash
    almacenado (SEC-INV-03)."""
    invitacion.token_hash = token_hash
    invitacion.expira_at = datetime.now(timezone.utc) + timedelta(seconds=VIGENCIA_INVITACION_SEGUNDOS)


def es_administrador_activo(db: Session, id_cuenta: int) -> bool:
    """Si retirar esta cuenta del conteo global la afecta: tiene al menos
    una asignación global vigente (RN-AUTH-ROL-03)."""
    return (
        db.scalar(
            select(CuentaPermisos.id_cuenta_permiso)
            .join(Permisos, Permisos.id == CuentaPermisos.permiso_id)
            .join(Cuentas, Cuentas.id_cuenta == CuentaPermisos.id_cuenta)
            .where(
                CuentaPermisos.id_cuenta == id_cuenta,
                CuentaPermisos.id_unidad.is_(None),
                Permisos.habilitado.is_(True),
                Cuentas.tipo_cuenta == "PERSONAL",
                Cuentas.estado.is_(True),
            )
        )
        is not None
    )


def marcar_invitacion_usada(db: Session, invitacion: Invitaciones) -> None:
    invitacion.usada_at = datetime.now(timezone.utc)


def marcar_token_recuperacion_usado(db: Session, token: TokensRecuperacion) -> None:
    token.usado_at = datetime.now(timezone.utc)


def revocar_todas_las_sesiones(db: Session, id_cuenta: int) -> int:
    ahora = datetime.now(timezone.utc)
    activas = db.scalars(
        select(Sesiones).where(Sesiones.id_cuenta == id_cuenta, Sesiones.revoked_at.is_(None))
    ).all()
    for s in activas:
        s.revoked_at = ahora
    return len(activas)
