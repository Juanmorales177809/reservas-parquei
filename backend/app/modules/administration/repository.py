"""Acceso a datos de estructura institucional y asignaciones (API-07, API-08).

No crea modelos nuevos: unidad/cargo viven en `identidad.py`, permisos en
`auth.py` y auditoría en `models/administration.py` (BK-08, API-08). Solo lee
y escribe filas.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.db.models.administration import Auditoria, ImportacionResultados, Importaciones
from app.db.models.auth import Cuentas
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


# --- Importaciones masivas (API-12) ----------------------------------------------


def crear_importacion(db: Session, *, actor_cuenta_id: int, catalogo: str, archivo_referencia: str) -> Importaciones:
    importacion = Importaciones(
        actor_cuenta_id=actor_cuenta_id, catalogo=catalogo, archivo_referencia=archivo_referencia,
        registros_creados=0, registros_actualizados=0, registros_desactivados=0,
        created_at=_ahora(), confirmado_at=None,
    )
    db.add(importacion)
    db.flush()
    return importacion


def obtener_importacion(db: Session, id_importacion: int) -> Importaciones | None:
    return db.get(Importaciones, id_importacion)


def agregar_resultado_fila(
    db: Session, *, importacion_id: int, numero_fila: int, codigo: str | None,
    resultado: str, detalle: str | None, datos: dict | None,
) -> ImportacionResultados:
    fila = ImportacionResultados(
        importacion_id=importacion_id, numero_fila=numero_fila, codigo=codigo,
        resultado=resultado, detalle=detalle, datos=datos,
    )
    db.add(fila)
    return fila


def resultados_de_importacion(db: Session, importacion_id: int) -> list[ImportacionResultados]:
    stmt = (
        select(ImportacionResultados)
        .where(ImportacionResultados.importacion_id == importacion_id)
        .order_by(ImportacionResultados.numero_fila)
    )
    return list(db.scalars(stmt).all())


def listar_importaciones(
    db: Session, *, catalogo: str | None, desde: datetime | None, hasta: datetime | None,
    limite: int, desplazamiento: int,
) -> tuple[list[Importaciones], int]:
    consulta = select(Importaciones)
    conteo = select(func.count()).select_from(Importaciones)
    condiciones = []
    if catalogo is not None:
        condiciones.append(Importaciones.catalogo == catalogo)
    if desde is not None:
        condiciones.append(Importaciones.created_at >= desde)
    if hasta is not None:
        condiciones.append(Importaciones.created_at <= hasta)
    if condiciones:
        consulta = consulta.where(*condiciones)
        conteo = conteo.where(*condiciones)
    total = db.scalar(conteo) or 0
    filas = db.scalars(
        consulta.order_by(Importaciones.created_at.desc()).limit(limite).offset(desplazamiento)
    ).all()
    return list(filas), total
