"""Acceso a datos de espacios, sus recursos asociados y campos adicionales (API-10)."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import ColumnElement, func, select
from sqlalchemy.orm import Session

from app.db.models.identidad import UnidadOrganizacional
from app.db.models.recursos import Equipos, Mobiliarios, OtrosRecursos, Recursos
from app.db.models.reservas import (
    EspacioCampoOpciones,
    EspacioCampos,
    EspacioRecursos,
    Espacios,
    EstadosReserva,
    LaboratoriosConfig,
    ReservaEspacio,
    ReservaHistorialEstado,
    Reservas,
)

_ESTADOS_BLOQUEANTES = ("SOLICITADA", "APROBADA")


# --- Espacios ---------------------------------------------------------------------


def obtener_unidad(db: Session, id_unidad: int) -> UnidadOrganizacional | None:
    return db.get(UnidadOrganizacional, id_unidad)


def obtener_espacio(db: Session, id_espacio: int) -> Espacios | None:
    return db.get(Espacios, id_espacio)


def existe_nombre(db: Session, id_unidad: int, nombre: str, excluir_id: int | None = None) -> bool:
    stmt = select(Espacios.id).where(Espacios.id_unidad == id_unidad, Espacios.nombre == nombre)
    if excluir_id is not None:
        stmt = stmt.where(Espacios.id != excluir_id)
    return db.scalar(stmt) is not None


def crear_espacio(db: Session, id_unidad: int, nombre: str, ubicacion: str | None, capacidad: int, descripcion: str | None) -> Espacios:
    ahora = datetime.now(timezone.utc)
    espacio = Espacios(
        id_unidad=id_unidad, nombre=nombre, ubicacion=ubicacion, capacidad=capacidad,
        descripcion=descripcion, habilitado=True, created_at=ahora, updated_at=ahora,
    )
    db.add(espacio)
    db.flush()
    return espacio


def cambiar_habilitado(db: Session, espacio: Espacios, habilitado: bool) -> None:
    espacio.habilitado = habilitado
    espacio.updated_at = datetime.now(timezone.utc)


def listar_espacios(
    db: Session, *, id_unidad: int | None, habilitado: bool | None, capacidad_minima: int | None,
    clausula_visibilidad: ColumnElement | None, orden: str | None, offset: int, tamano: int,
):
    stmt = select(Espacios)
    if clausula_visibilidad is not None:
        stmt = stmt.where(clausula_visibilidad)
    if id_unidad is not None:
        stmt = stmt.where(Espacios.id_unidad == id_unidad)
    if habilitado is not None:
        stmt = stmt.where(Espacios.habilitado == habilitado)
    if capacidad_minima is not None:
        stmt = stmt.where(Espacios.capacidad >= capacidad_minima)

    total = db.scalar(select(func.count()).select_from(stmt.subquery()))

    if orden == "nombre":
        stmt = stmt.order_by(Espacios.nombre, Espacios.id)
    elif orden == "-nombre":
        stmt = stmt.order_by(Espacios.nombre.desc(), Espacios.id)
    elif orden == "capacidad":
        stmt = stmt.order_by(Espacios.capacidad, Espacios.id)
    elif orden == "-capacidad":
        stmt = stmt.order_by(Espacios.capacidad.desc(), Espacios.id)
    else:
        stmt = stmt.order_by(Espacios.id)

    items = db.scalars(stmt.offset(offset).limit(tamano)).all()
    return items, total


# --- Horario compartido de la unidad (solo lectura; lo administra resources) ------


def obtener_horario_unidad(db: Session, id_unidad: int) -> LaboratoriosConfig | None:
    return db.scalar(select(LaboratoriosConfig).where(LaboratoriosConfig.id_unidad == id_unidad))


# --- Recursos asociados -------------------------------------------------------------


def obtener_recurso(db: Session, id_recurso: int) -> Recursos | None:
    return db.get(Recursos, id_recurso)


def nombre_recurso(db: Session, recurso: Recursos) -> str | None:
    if recurso.tipo == "EQUIPO":
        return db.scalar(select(Equipos.nombre_equipo).where(Equipos.id == recurso.id))
    if recurso.tipo == "MOBILIARIO":
        return db.scalar(select(Mobiliarios.nombre).where(Mobiliarios.id == recurso.id))
    return db.scalar(select(OtrosRecursos.nombre).where(OtrosRecursos.id == recurso.id))


def obtener_asociacion(db: Session, espacio_id: int, recurso_id: int) -> EspacioRecursos | None:
    return db.get(EspacioRecursos, {"espacio_id": espacio_id, "recurso_id": recurso_id})


def tiene_asociacion_activa(db: Session, recurso_id: int) -> bool:
    return db.scalar(
        select(EspacioRecursos.espacio_id).where(
            EspacioRecursos.recurso_id == recurso_id, EspacioRecursos.habilitado.is_(True),
        )
    ) is not None


def asociacion_activa_en_otro_espacio(db: Session, recurso_id: int, espacio_id: int) -> bool:
    return db.scalar(
        select(EspacioRecursos.espacio_id).where(
            EspacioRecursos.recurso_id == recurso_id,
            EspacioRecursos.habilitado.is_(True),
            EspacioRecursos.espacio_id != espacio_id,
        )
    ) is not None


def asociar_recurso(db: Session, espacio_id: int, recurso_id: int) -> EspacioRecursos:
    ahora = datetime.now(timezone.utc)
    existente = obtener_asociacion(db, espacio_id, recurso_id)
    if existente is not None:
        existente.habilitado = True
        existente.updated_at = ahora
        return existente
    fila = EspacioRecursos(espacio_id=espacio_id, recurso_id=recurso_id, habilitado=True, created_at=ahora, updated_at=ahora)
    db.add(fila)
    db.flush()
    return fila


def retirar_recurso(db: Session, asociacion: EspacioRecursos) -> None:
    asociacion.habilitado = False
    asociacion.updated_at = datetime.now(timezone.utc)


def recursos_asociados(db: Session, espacio_id: int) -> list[EspacioRecursos]:
    stmt = select(EspacioRecursos).where(EspacioRecursos.espacio_id == espacio_id, EspacioRecursos.habilitado.is_(True))
    return list(db.scalars(stmt).all())


# --- Campos adicionales ----------------------------------------------------------


def obtener_campo(db: Session, id_campo: int) -> EspacioCampos | None:
    return db.get(EspacioCampos, id_campo)


def existe_nombre_campo(db: Session, espacio_id: int, nombre: str, excluir_id: int | None = None) -> bool:
    stmt = select(EspacioCampos.id).where(EspacioCampos.espacio_id == espacio_id, EspacioCampos.nombre == nombre)
    if excluir_id is not None:
        stmt = stmt.where(EspacioCampos.id != excluir_id)
    return db.scalar(stmt) is not None


def crear_campo(db: Session, espacio_id: int, nombre: str, tipo: str, obligatorio: bool, orden: int) -> EspacioCampos:
    ahora = datetime.now(timezone.utc)
    campo = EspacioCampos(
        espacio_id=espacio_id, nombre=nombre, tipo_campo=tipo, obligatorio=obligatorio,
        orden=orden, habilitado=True, created_at=ahora, updated_at=ahora,
    )
    db.add(campo)
    db.flush()
    return campo


def campos_del_espacio(db: Session, espacio_id: int) -> list[EspacioCampos]:
    stmt = select(EspacioCampos).where(EspacioCampos.espacio_id == espacio_id).order_by(EspacioCampos.orden)
    return list(db.scalars(stmt).all())


def opciones_del_campo(db: Session, campo_id: int) -> list[EspacioCampoOpciones]:
    stmt = select(EspacioCampoOpciones).where(EspacioCampoOpciones.campo_id == campo_id).order_by(EspacioCampoOpciones.orden)
    return list(db.scalars(stmt).all())


def contar_opciones_habilitadas(db: Session, campo_id: int, excluir_id: int | None = None) -> int:
    stmt = select(func.count()).where(EspacioCampoOpciones.campo_id == campo_id, EspacioCampoOpciones.habilitado.is_(True))
    if excluir_id is not None:
        stmt = stmt.where(EspacioCampoOpciones.id != excluir_id)
    return db.scalar(stmt) or 0


def obtener_opcion(db: Session, id_opcion: int) -> EspacioCampoOpciones | None:
    return db.get(EspacioCampoOpciones, id_opcion)


def existe_valor_opcion(db: Session, campo_id: int, valor: str, excluir_id: int | None = None) -> bool:
    stmt = select(EspacioCampoOpciones.id).where(EspacioCampoOpciones.campo_id == campo_id, EspacioCampoOpciones.valor == valor)
    if excluir_id is not None:
        stmt = stmt.where(EspacioCampoOpciones.id != excluir_id)
    return db.scalar(stmt) is not None


def crear_opcion(db: Session, campo_id: int, valor: str, orden: int) -> EspacioCampoOpciones:
    ahora = datetime.now(timezone.utc)
    opcion = EspacioCampoOpciones(campo_id=campo_id, valor=valor, orden=orden, habilitado=True, created_at=ahora, updated_at=ahora)
    db.add(opcion)
    db.flush()
    return opcion


# --- Impacto de deshabilitación (RN-ESP-HAB-05, RN-CAN-04) -----------------------


def contar_impacto(db: Session, id_espacio: int) -> int:
    stmt = (
        select(func.count())
        .select_from(ReservaEspacio)
        .join(Reservas, Reservas.id == ReservaEspacio.reserva_id)
        .join(EstadosReserva, EstadosReserva.id == Reservas.estado_id)
        .where(ReservaEspacio.espacio_id == id_espacio, EstadosReserva.codigo.in_(_ESTADOS_BLOQUEANTES))
    )
    return db.scalar(stmt) or 0


def reservas_vigentes(db: Session, id_espacio: int) -> list[Reservas]:
    stmt = (
        select(Reservas)
        .join(ReservaEspacio, ReservaEspacio.reserva_id == Reservas.id)
        .join(EstadosReserva, EstadosReserva.id == Reservas.estado_id)
        .where(ReservaEspacio.espacio_id == id_espacio, EstadosReserva.codigo.in_(_ESTADOS_BLOQUEANTES))
    )
    return list(db.scalars(stmt).all())


def obtener_estado_id(db: Session, codigo: str) -> int:
    return db.scalar(select(EstadosReserva.id).where(EstadosReserva.codigo == codigo))


def cancelar_reserva(db: Session, reserva: Reservas, motivo: str, actor_cuenta_id: int | None) -> None:
    estado_anterior = reserva.estado_id
    reserva.estado_id = obtener_estado_id(db, "CANCELADA")
    reserva.fecha_cancelacion = datetime.now(timezone.utc)
    reserva.motivo_cancelacion = motivo
    db.add(ReservaHistorialEstado(
        reserva_id=reserva.id, estado_anterior_id=estado_anterior, estado_nuevo_id=reserva.estado_id,
        actor_cuenta_id=actor_cuenta_id, motivo=motivo, created_at=datetime.now(timezone.utc),
    ))
