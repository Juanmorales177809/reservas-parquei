"""Repositorio de reports (API-19): solo lectura sobre fuentes propietarias.

No crea tablas ni modifica nada (RN-REP-02/06). Las relaciones se resuelven
por identificadores persistentes (RN-DIM-07, RN-CON-02).
"""

from __future__ import annotations

from datetime import date

from sqlalchemy import Date, func, select
from sqlalchemy.orm import Session

from app.db.models.identidad import UnidadOrganizacional
from app.db.models.investigacion import Proyectos, Semilleros
from app.db.models.recursos import Equipos, Mobiliarios, OtrosRecursos, Recursos
from app.db.models.reservas import (
    Espacios,
    EstadosReserva,
    LaboratoriosConfigHistorico,
    ReservaContexto,
    ReservaEspacio,
    ReservaListaEspera,
    ReservaRecursoCampus,
    ReservaRecursoExterno,
    ReservaRecursoInterno,
    ReservaRecursos,
    Reservas,
    TiposReserva,
)


def unidades(db: Session, ids: list[int] | None) -> list[UnidadOrganizacional]:
    stmt = select(UnidadOrganizacional)
    if ids is not None:
        stmt = stmt.where(UnidadOrganizacional.id_unidad.in_(ids))
    return list(db.scalars(stmt.order_by(UnidadOrganizacional.id_unidad)).all())


def espacios_de(db: Session, unidad_ids: list[int] | None, espacio_id: int | None) -> list[Espacios]:
    stmt = select(Espacios)
    if unidad_ids is not None:
        stmt = stmt.where(Espacios.id_unidad.in_(unidad_ids))
    if espacio_id is not None:
        stmt = stmt.where(Espacios.id == espacio_id)
    return list(db.scalars(stmt.order_by(Espacios.id)).all())


def recursos_de(db: Session, unidad_ids: list[int] | None, recurso_id: int | None) -> list[Recursos]:
    stmt = select(Recursos)
    if unidad_ids is not None:
        stmt = stmt.where(Recursos.id_unidad.in_(unidad_ids))
    if recurso_id is not None:
        stmt = stmt.where(Recursos.id == recurso_id)
    return list(db.scalars(stmt.order_by(Recursos.id)).all())


def nombre_recurso(db: Session, recurso_id: int) -> str:
    for modelo, campo in (
        (Equipos, "nombre_equipo"), (Mobiliarios, "nombre"), (OtrosRecursos, "nombre"),
    ):
        fila = db.get(modelo, recurso_id)
        if fila is not None:
            return getattr(fila, campo)
    return f"Recurso {recurso_id}"


def proyectos_de(db: Session, proyecto_id: int | None) -> list[Proyectos]:
    stmt = select(Proyectos)
    if proyecto_id is not None:
        stmt = stmt.where(Proyectos.id_proyecto == proyecto_id)
    return list(db.scalars(stmt.order_by(Proyectos.id_proyecto)).all())


def semilleros_de(db: Session, semillero_id: int | None) -> list[Semilleros]:
    stmt = select(Semilleros)
    if semillero_id is not None:
        stmt = stmt.where(Semilleros.id_semillero == semillero_id)
    return list(db.scalars(stmt.order_by(Semilleros.id_semillero)).all())


def reservas_base(db: Session, unidad_ids: list[int] | None, estados: list[str] | None):
    """(reserva, tipo_codigo, estado_codigo) con filtros de ámbito y estado."""
    stmt = (
        select(Reservas, TiposReserva.codigo, EstadosReserva.codigo)
        .join(TiposReserva, TiposReserva.id == Reservas.tipo_reserva_id)
        .join(EstadosReserva, EstadosReserva.id == Reservas.estado_id)
    )
    if unidad_ids is not None:
        stmt = stmt.where(Reservas.id_unidad.in_(unidad_ids))
    if estados is not None:
        stmt = stmt.where(EstadosReserva.codigo.in_(estados))
    return list(db.execute(stmt.order_by(Reservas.id)).all())


def detalles_espacio(db: Session, reserva_ids: list[int]) -> dict[int, ReservaEspacio]:
    if not reserva_ids:
        return {}
    filas = db.scalars(
        select(ReservaEspacio).where(ReservaEspacio.reserva_id.in_(reserva_ids))
    ).all()
    return {f.reserva_id: f for f in filas}


def detalles_internos(db: Session, reserva_ids: list[int]) -> dict[int, ReservaRecursoInterno]:
    if not reserva_ids:
        return {}
    filas = db.scalars(
        select(ReservaRecursoInterno).where(ReservaRecursoInterno.reserva_id.in_(reserva_ids))
    ).all()
    return {f.reserva_id: f for f in filas}


def detalles_campus(db: Session, reserva_ids: list[int]) -> dict[int, ReservaRecursoCampus]:
    if not reserva_ids:
        return {}
    filas = db.scalars(
        select(ReservaRecursoCampus).where(ReservaRecursoCampus.reserva_id.in_(reserva_ids))
    ).all()
    return {f.reserva_id: f for f in filas}


def detalles_externos(db: Session, reserva_ids: list[int]) -> dict[int, ReservaRecursoExterno]:
    if not reserva_ids:
        return {}
    filas = db.scalars(
        select(ReservaRecursoExterno).where(ReservaRecursoExterno.reserva_id.in_(reserva_ids))
    ).all()
    return {f.reserva_id: f for f in filas}


def detalles_lista_espera(db: Session, reserva_ids: list[int]) -> dict[int, ReservaListaEspera]:
    """Detalles de lista de espera por reserva (API-21: sus horas_ejecucion)."""
    if not reserva_ids:
        return {}
    filas = db.scalars(
        select(ReservaListaEspera).where(ReservaListaEspera.reserva_id.in_(reserva_ids))
    ).all()
    return {f.reserva_id: f for f in filas}


def contextos_de(db: Session, reserva_ids: list[int]) -> dict[int, ReservaContexto]:
    if not reserva_ids:
        return {}
    filas = db.scalars(
        select(ReservaContexto).where(ReservaContexto.reserva_id.in_(reserva_ids))
    ).all()
    return {f.reserva_id: f for f in filas}


def asignaciones_activas(db: Session, reserva_ids: list[int]) -> dict[int, list[ReservaRecursos]]:
    if not reserva_ids:
        return {}
    filas = db.scalars(
        select(ReservaRecursos).where(
            ReservaRecursos.reserva_id.in_(reserva_ids),
            ReservaRecursos.estado_asignacion == "ASIGNADO",
        )
    ).all()
    grupos: dict[int, list] = {}
    for f in filas:
        grupos.setdefault(f.reserva_id, []).append(f)
    return grupos


def historico_horario(db: Session, id_unidad: int) -> list[LaboratoriosConfigHistorico]:
    return list(db.scalars(
        select(LaboratoriosConfigHistorico)
        .where(LaboratoriosConfigHistorico.id_unidad == id_unidad)
        .order_by(LaboratoriosConfigHistorico.vigente_desde)
    ).all())


def lista_espera_agregada(db: Session, unidad_ids: list[int] | None, desde: date, hasta: date):
    """(id_unidad, n_reservas, suma_horas) del periodo por fecha de creación."""
    stmt = (
        select(
            Reservas.id_unidad, func.count(),
            func.coalesce(func.sum(ReservaListaEspera.horas_ejecucion), 0),
        )
        .join(ReservaListaEspera, ReservaListaEspera.reserva_id == Reservas.id)
        .where(func.timezone("America/Bogota", Reservas.created_at).cast(Date) >= desde)
        .where(func.timezone("America/Bogota", Reservas.created_at).cast(Date) <= hasta)
        .group_by(Reservas.id_unidad)
    )
    if unidad_ids is not None:
        stmt = stmt.where(Reservas.id_unidad.in_(unidad_ids))
    return list(db.execute(stmt).all())
