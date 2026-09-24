"""Acceso a datos de identidades funcionales (API-06).

Solo lee y escribe filas conforme al esquema de las migraciones. Las lecturas
sobre `auth` (cuenta asociada, último administrador) son consultas de
integridad de este dominio, no reglas de auth.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.db.models.auth import CuentaPermisos, Cuentas, Permisos
from app.db.models.identidad import Cargo, Personal, UnidadOrganizacional, Usuarios


def _ahora() -> datetime:
    return datetime.now(timezone.utc)


# --- Usuarios -----------------------------------------------------------------


def crear_usuario(
    db: Session, *, nombre: str, documento: str, telefono: str,
    institucion: str, dependencia: str, correo: str,
) -> Usuarios:
    ahora = _ahora()
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


def obtener_usuario(db: Session, id_usuario: int) -> Usuarios | None:
    return db.get(Usuarios, id_usuario)


def obtener_usuario_por_correo(db: Session, correo: str) -> Usuarios | None:
    return db.scalar(select(Usuarios).where(Usuarios.correo == correo))


def existe_documento_usuario(db: Session, documento: str, excluir_id: int | None = None) -> bool:
    consulta = select(Usuarios.id_usuario).where(Usuarios.documento == documento)
    if excluir_id is not None:
        consulta = consulta.where(Usuarios.id_usuario != excluir_id)
    return db.scalar(consulta) is not None


def existe_telefono_usuario(db: Session, telefono: str, excluir_id: int | None = None) -> bool:
    consulta = select(Usuarios.id_usuario).where(Usuarios.telefono == telefono)
    if excluir_id is not None:
        consulta = consulta.where(Usuarios.id_usuario != excluir_id)
    return db.scalar(consulta) is not None


def existe_correo_usuario(db: Session, correo: str, excluir_id: int | None = None) -> bool:
    consulta = select(Usuarios.id_usuario).where(Usuarios.correo == correo)
    if excluir_id is not None:
        consulta = consulta.where(Usuarios.id_usuario != excluir_id)
    return db.scalar(consulta) is not None


def listar_usuarios(
    db: Session, *, estado: bool | None, busqueda: str | None,
    limite: int, desplazamiento: int, orden: str | None,
) -> tuple[list[Usuarios], int]:
    consulta = select(Usuarios)
    conteo = select(func.count()).select_from(Usuarios)
    if estado is not None:
        consulta = consulta.where(Usuarios.estado.is_(estado))
        conteo = conteo.where(Usuarios.estado.is_(estado))
    if busqueda:
        patron = f"%{busqueda}%"
        condicion = or_(
            Usuarios.nombre.ilike(patron),
            Usuarios.documento.ilike(patron),
            Usuarios.correo.ilike(patron),
        )
        consulta = consulta.where(condicion)
        conteo = conteo.where(condicion)
    total = db.scalar(conteo) or 0
    consulta = _ordenar_usuarios(consulta, orden)
    return list(db.scalars(consulta.limit(limite).offset(desplazamiento)).all()), total


def _ordenar_usuarios(consulta, orden: str | None):
    if not orden:
        return consulta.order_by(Usuarios.id_usuario)
    descendente = orden.startswith("-")
    campo = orden.removeprefix("-")
    columna = {"nombre": Usuarios.nombre, "correo": Usuarios.correo}.get(campo, Usuarios.id_usuario)
    return consulta.order_by(columna.desc() if descendente else columna)


# --- Personal ------------------------------------------------------------------


def crear_personal(
    db: Session, *, nombre: str, documento: str, correo: str, telefono: str, id_cargo: int,
) -> Personal:
    persona = Personal(
        nombre=nombre,
        documento=documento,
        correo=correo,
        telefono=telefono,
        id_cargo=id_cargo,
        estado=True,
    )
    db.add(persona)
    db.flush()
    return persona


def obtener_personal(db: Session, id_persona: int) -> Personal | None:
    return db.get(Personal, id_persona)


def obtener_persona_por_correo(db: Session, correo: str) -> Personal | None:
    return db.scalar(select(Personal).where(Personal.correo == correo))


def existe_documento_personal(db: Session, documento: str, excluir_id: int | None = None) -> bool:
    consulta = select(Personal.id_persona).where(Personal.documento == documento)
    if excluir_id is not None:
        consulta = consulta.where(Personal.id_persona != excluir_id)
    return db.scalar(consulta) is not None


def existe_correo_personal(db: Session, correo: str, excluir_id: int | None = None) -> bool:
    consulta = select(Personal.id_persona).where(Personal.correo == correo)
    if excluir_id is not None:
        consulta = consulta.where(Personal.id_persona != excluir_id)
    return db.scalar(consulta) is not None


def existe_telefono_personal(db: Session, telefono: str, excluir_id: int | None = None) -> bool:
    consulta = select(Personal.id_persona).where(Personal.telefono == telefono)
    if excluir_id is not None:
        consulta = consulta.where(Personal.id_persona != excluir_id)
    return db.scalar(consulta) is not None


def listar_personal(
    db: Session, *, estado: bool | None, id_unidad: int | None, busqueda: str | None,
    limite: int, desplazamiento: int, orden: str | None,
) -> tuple[list[Personal], int]:
    consulta = select(Personal).join(Cargo, Cargo.id_cargo == Personal.id_cargo)
    conteo = select(func.count()).select_from(Personal).join(Cargo, Cargo.id_cargo == Personal.id_cargo)
    if estado is not None:
        consulta = consulta.where(Personal.estado.is_(estado))
        conteo = conteo.where(Personal.estado.is_(estado))
    if id_unidad is not None:
        consulta = consulta.where(Cargo.id_unidad == id_unidad)
        conteo = conteo.where(Cargo.id_unidad == id_unidad)
    if busqueda:
        patron = f"%{busqueda}%"
        condicion = or_(
            Personal.nombre.ilike(patron),
            Personal.documento.ilike(patron),
            Personal.correo.ilike(patron),
        )
        consulta = consulta.where(condicion)
        conteo = conteo.where(condicion)
    total = db.scalar(conteo) or 0
    if orden:
        descendente = orden.startswith("-")
        columna = {"nombre": Personal.nombre, "correo": Personal.correo}.get(
            orden.removeprefix("-"), Personal.id_persona
        )
        consulta = consulta.order_by(columna.desc() if descendente else columna)
    else:
        consulta = consulta.order_by(Personal.id_persona)
    return list(db.scalars(consulta.limit(limite).offset(desplazamiento)).all()), total


# --- Cargo y unidad (lectura para la ficha) ------------------------------------


def obtener_cargo(db: Session, id_cargo: int) -> Cargo | None:
    return db.get(Cargo, id_cargo)


def obtener_unidad(db: Session, id_unidad: int) -> UnidadOrganizacional | None:
    return db.get(UnidadOrganizacional, id_unidad)


# --- Integridad con cuentas (lectura) -------------------------------------------


def cuenta_de_usuario(db: Session, id_usuario: int) -> Cuentas | None:
    return db.scalar(select(Cuentas).where(Cuentas.id_usuario == id_usuario))


def cuenta_de_persona(db: Session, id_persona: int) -> Cuentas | None:
    return db.scalar(select(Cuentas).where(Cuentas.id_persona == id_persona))


def es_administrador_activo(db: Session, id_cuenta: int) -> bool:
    """¿La cuenta tiene al menos una asignación global vigente? (RN-AUTH-ROL-09 de auth)."""
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


def otros_administradores_activos(db: Session, excluir_id_cuenta: int) -> int:
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
            Cuentas.id_cuenta != excluir_id_cuenta,
        )
    )
    return len(db.scalars(consulta).all())
