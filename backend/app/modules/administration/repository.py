"""Acceso a datos de estructura institucional y asignaciones (API-07, API-08).

No crea modelos nuevos: unidad/cargo viven en `identidad.py`, permisos en
`auth.py` y auditoría en `models/administration.py` (BK-08, API-08). Solo lee
y escribe filas.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.db.models.administration import Auditoria
from app.db.models.auth import CuentaPermisos, Cuentas, Permisos
from app.db.models.identidad import Cargo, Personal, UnidadOrganizacional


def _ahora() -> datetime:
    return datetime.now(timezone.utc)


# --- Unidades ---------------------------------------------------------------------


def crear_unidad(db: Session, *, nombre: str, tipo: str, id_unidad_padre: int | None) -> UnidadOrganizacional:
    unidad = UnidadOrganizacional(
        nombre=nombre, tipo=tipo, id_unidad_padre=id_unidad_padre, estado=True
    )
    db.add(unidad)
    db.flush()
    return unidad


def obtener_unidad(db: Session, id_unidad: int) -> UnidadOrganizacional | None:
    return db.get(UnidadOrganizacional, id_unidad)


def existe_nombre_unidad(db: Session, nombre: str, excluir_id: int | None = None) -> bool:
    consulta = select(UnidadOrganizacional.id_unidad).where(UnidadOrganizacional.nombre == nombre)
    if excluir_id is not None:
        consulta = consulta.where(UnidadOrganizacional.id_unidad != excluir_id)
    return db.scalar(consulta) is not None


def descendientes_unidad(db: Session, id_unidad: int) -> set[int]:
    """Ids bajo la unidad, para detectar ciclos (contrato §2.3).

    Poner como padre a un descendiente cerraría un ciclo: se camina hacia
    abajo desde la unidad editada, no hacia arriba.
    """
    vistos: set[int] = set()
    pendientes = [id_unidad]
    while pendientes:
        actual = pendientes.pop()
        hijos = db.scalars(
            select(UnidadOrganizacional.id_unidad).where(
                UnidadOrganizacional.id_unidad_padre == actual
            )
        ).all()
        for hijo in hijos:
            if hijo not in vistos:
                vistos.add(hijo)
                pendientes.append(hijo)
    return vistos


def listar_unidades(
    db: Session, *, estado: bool | None, tipo: str | None, id_unidad_padre: int | None,
    busqueda: str | None, limite: int, desplazamiento: int, orden: str | None,
) -> tuple[list[UnidadOrganizacional], int]:
    consulta = select(UnidadOrganizacional)
    conteo = select(func.count()).select_from(UnidadOrganizacional)
    if estado is not None:
        consulta = consulta.where(UnidadOrganizacional.estado.is_(estado))
        conteo = conteo.where(UnidadOrganizacional.estado.is_(estado))
    if tipo is not None:
        consulta = consulta.where(UnidadOrganizacional.tipo == tipo)
        conteo = conteo.where(UnidadOrganizacional.tipo == tipo)
    if id_unidad_padre is not None:
        consulta = consulta.where(UnidadOrganizacional.id_unidad_padre == id_unidad_padre)
        conteo = conteo.where(UnidadOrganizacional.id_unidad_padre == id_unidad_padre)
    if busqueda:
        condicion = UnidadOrganizacional.nombre.ilike(f"%{busqueda}%")
        consulta = consulta.where(condicion)
        conteo = conteo.where(condicion)
    total = db.scalar(conteo) or 0
    consulta = _ordenar_unidades(consulta, orden)
    return list(db.scalars(consulta.limit(limite).offset(desplazamiento)).all()), total


def _ordenar_unidades(consulta, orden: str | None):
    if not orden:
        return consulta.order_by(UnidadOrganizacional.id_unidad)
    descendente = orden.startswith("-")
    columna = {"nombre": UnidadOrganizacional.nombre, "tipo": UnidadOrganizacional.tipo}.get(
        orden.removeprefix("-"), UnidadOrganizacional.id_unidad
    )
    return consulta.order_by(columna.desc() if descendente else columna)


# --- Cargos -------------------------------------------------------------------------


def crear_cargo(db: Session, *, nombre_cargo: str, id_unidad: int) -> Cargo:
    cargo = Cargo(nombre_cargo=nombre_cargo, id_unidad=id_unidad)
    db.add(cargo)
    db.flush()
    return cargo


def obtener_cargo(db: Session, id_cargo: int) -> Cargo | None:
    return db.get(Cargo, id_cargo)


def listar_cargos(
    db: Session, *, id_unidad: int | None, limite: int, desplazamiento: int, orden: str | None,
) -> tuple[list[Cargo], int]:
    consulta = select(Cargo)
    conteo = select(func.count()).select_from(Cargo)
    if id_unidad is not None:
        consulta = consulta.where(Cargo.id_unidad == id_unidad)
        conteo = conteo.where(Cargo.id_unidad == id_unidad)
    total = db.scalar(conteo) or 0
    if orden:
        descendente = orden.startswith("-")
        columna = {"nombre_cargo": Cargo.nombre_cargo}.get(orden.removeprefix("-"), Cargo.id_cargo)
        consulta = consulta.order_by(columna.desc() if descendente else columna)
    else:
        consulta = consulta.order_by(Cargo.id_cargo)
    return list(db.scalars(consulta.limit(limite).offset(desplazamiento)).all()), total


# --- Permisos --------------------------------------------------------------------------


def listar_permisos(db: Session) -> list[Permisos]:
    return list(db.scalars(select(Permisos).order_by(Permisos.codigo)).all())


def obtener_permiso_por_codigo(db: Session, codigo: str) -> Permisos | None:
    return db.scalar(select(Permisos).where(Permisos.codigo == codigo))


def asignaciones_de_cuenta(db: Session, id_cuenta: int) -> list[CuentaPermisos]:
    return list(
        db.scalars(
            select(CuentaPermisos)
            .where(CuentaPermisos.id_cuenta == id_cuenta)
            .order_by(CuentaPermisos.id_cuenta_permiso)
        ).all()
    )


def otorgar_permiso(
    db: Session, *, id_cuenta: int, permiso_id: int, id_unidad: int | None, otorgado_por: int,
) -> CuentaPermisos:
    fila = CuentaPermisos(
        id_cuenta=id_cuenta,
        permiso_id=permiso_id,
        id_unidad=id_unidad,
        otorgado_por=otorgado_por,
        created_at=_ahora(),
    )
    db.add(fila)
    db.flush()
    return fila


def retirar_permisos_por_codigo(db: Session, id_cuenta: int, permiso_id: int) -> list[CuentaPermisos]:
    filas = list(
        db.scalars(
            select(CuentaPermisos).where(
                CuentaPermisos.id_cuenta == id_cuenta, CuentaPermisos.permiso_id == permiso_id
            )
        ).all()
    )
    for fila in filas:
        db.delete(fila)
    return filas


# --- Integridad con cuentas y personal (lectura) -------------------------------------------


def obtener_cuenta(db: Session, id_cuenta: int) -> Cuentas | None:
    return db.get(Cuentas, id_cuenta)


def persona_de_cuenta(db: Session, cuenta: Cuentas) -> Personal | None:
    if cuenta.tipo_cuenta != "PERSONAL" or cuenta.id_persona is None:
        return None
    return db.get(Personal, cuenta.id_persona)


def unidad_del_cargo(db: Session, id_cargo: int) -> int | None:
    cargo = db.get(Cargo, id_cargo)
    return cargo.id_unidad if cargo else None


def es_administrador_activo(db: Session, id_cuenta: int) -> bool:
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


# --- Auditoría (§5, API-08; solo lectura) -------------------------------------------------


def listar_auditoria(
    db: Session, *, entidad: str | None, entidad_id: str | None, actor_cuenta_id: int | None,
    accion: str | None, desde: datetime | None, hasta: datetime | None,
    limite: int, desplazamiento: int, descendente: bool,
) -> tuple[list[Auditoria], int]:
    consulta = select(Auditoria)
    conteo = select(func.count()).select_from(Auditoria)
    condiciones = []
    if entidad is not None:
        condiciones.append(Auditoria.entidad == entidad)
    if entidad_id is not None:
        condiciones.append(Auditoria.entidad_id == entidad_id)
    if actor_cuenta_id is not None:
        condiciones.append(Auditoria.actor_cuenta_id == actor_cuenta_id)
    if accion is not None:
        condiciones.append(Auditoria.accion == accion)
    if desde is not None:
        condiciones.append(Auditoria.created_at >= desde)
    if hasta is not None:
        condiciones.append(Auditoria.created_at <= hasta)
    if condiciones:
        consulta = consulta.where(*condiciones)
        conteo = conteo.where(*condiciones)
    total = db.scalar(conteo) or 0
    orden = Auditoria.created_at.desc() if descendente else Auditoria.created_at
    filas = db.scalars(
        consulta.order_by(orden).limit(limite).offset(desplazamiento)
    ).all()
    return list(filas), total
