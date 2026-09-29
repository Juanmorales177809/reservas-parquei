"""Acceso a datos de recursos y configuración del laboratorio (API-09)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models.identidad import UnidadOrganizacional
from app.db.models.recursos import CategoriasEquipos, Equipos, Mobiliarios, OtrosRecursos, Recursos
from app.db.models.reservas import (
    EspacioRecursos,
    Espacios,
    EstadosReserva,
    LaboratoriosConfig,
    LaboratoriosConfigHistorico,
    LaboratorioTiposReserva,
    ReservaHistorialEstado,
    ReservaRecursos,
    Reservas,
    TiposReserva,
)

ESPECIALIZACION = {"EQUIPO": Equipos, "MOBILIARIO": Mobiliarios, "OTRO": OtrosRecursos}


# --- Recursos ------------------------------------------------------------------


def obtener_unidad(db: Session, id_unidad: int) -> UnidadOrganizacional | None:
    return db.get(UnidadOrganizacional, id_unidad)


def obtener_recurso(db: Session, id_recurso: int) -> Recursos | None:
    return db.get(Recursos, id_recurso)


def obtener_especializacion(db: Session, tipo: str, id_recurso: int):
    return db.get(ESPECIALIZACION[tipo], id_recurso)


def crear_recurso(db: Session, id_unidad: int, tipo: str) -> Recursos:
    ahora = datetime.now(timezone.utc)
    recurso = Recursos(id_unidad=id_unidad, tipo=tipo, habilitado=True, created_at=ahora, updated_at=ahora)
    db.add(recurso)
    db.flush()
    return recurso


def crear_equipo(db: Session, id_recurso: int, **campos) -> Equipos:
    equipo = Equipos(id=id_recurso, requiere_apoyo=campos.pop("requiere_apoyo", False),
                      acreditado=campos.pop("acreditado", False), **campos)
    db.add(equipo)
    db.flush()
    return equipo


def crear_mobiliario_u_otro(db: Session, tipo: str, id_recurso: int, id_unidad: int, nombre: str, descripcion: str | None):
    modelo = ESPECIALIZACION[tipo]
    fila = modelo(id=id_recurso, id_unidad=id_unidad, nombre=nombre, descripcion=descripcion, habilitado=True)
    db.add(fila)
    db.flush()
    return fila


def existe_placa(db: Session, placa: str, excluir_id: int | None = None) -> bool:
    stmt = select(Equipos.id).where(Equipos.placa == placa)
    if excluir_id is not None:
        stmt = stmt.where(Equipos.id != excluir_id)
    return db.scalar(stmt) is not None


def obtener_equipo_por_placa(db: Session, placa: str) -> Equipos | None:
    """Idempotencia de la importación masiva por placa (API-12, RN-IMP-02 de resources)."""
    return db.scalar(select(Equipos).where(Equipos.placa == placa))


def existe_serial(db: Session, serial: str, excluir_id: int | None = None) -> bool:
    stmt = select(Equipos.id).where(Equipos.serial == serial)
    if excluir_id is not None:
        stmt = stmt.where(Equipos.id != excluir_id)
    return db.scalar(stmt) is not None


def existe_categoria(db: Session, id_categoria: int) -> bool:
    return db.get(CategoriasEquipos, id_categoria) is not None


def listar_recursos(
    db: Session, *, id_unidad: int | None, tipo: str | None, habilitado: bool | None,
    busqueda: str | None, reservable: bool, orden: str | None, offset: int, tamano: int,
):
    # nombre vive en cada especialización, placa solo en equipos: se resuelve
    # con OUTER JOIN a las tres, porque un recurso solo tiene fila en una.
    stmt = (
        select(Recursos)
        .outerjoin(Equipos, Equipos.id == Recursos.id)
        .outerjoin(Mobiliarios, Mobiliarios.id == Recursos.id)
        .outerjoin(OtrosRecursos, OtrosRecursos.id == Recursos.id)
    )
    if id_unidad is not None:
        stmt = stmt.where(Recursos.id_unidad == id_unidad)
    if tipo is not None:
        stmt = stmt.where(Recursos.tipo == tipo)
    if habilitado is not None:
        stmt = stmt.where(Recursos.habilitado == habilitado)
    if busqueda is not None:
        patron = f"%{busqueda}%"
        stmt = stmt.where(
            Equipos.nombre_equipo.ilike(patron) | Equipos.placa.ilike(patron)
            | Mobiliarios.nombre.ilike(patron) | OtrosRecursos.nombre.ilike(patron)
        )
    if reservable:
        # RN-REC-11: excluye equipos acreditados del listado reservable.
        stmt = stmt.where((Recursos.tipo != "EQUIPO") | (Equipos.acreditado.is_(False)))

    total = db.scalar(select(func.count()).select_from(stmt.subquery()))

    nombre_unificado = func.coalesce(Equipos.nombre_equipo, Mobiliarios.nombre, OtrosRecursos.nombre)
    if orden == "nombre":
        stmt = stmt.order_by(nombre_unificado, Recursos.id)
    elif orden == "-nombre":
        stmt = stmt.order_by(nombre_unificado.desc(), Recursos.id)
    elif orden == "tipo":
        stmt = stmt.order_by(Recursos.tipo, Recursos.id)
    elif orden == "-tipo":
        stmt = stmt.order_by(Recursos.tipo.desc(), Recursos.id)
    else:
        stmt = stmt.order_by(Recursos.id)

    items = db.scalars(stmt.offset(offset).limit(tamano)).all()
    return items, total


def nombres_de_recursos(db: Session, ids: list[int]) -> dict[int, str | None]:
    """Nombre visible de cada recurso (vive en su especialización)."""
    if not ids:
        return {}
    nombre = func.coalesce(Equipos.nombre_equipo, Mobiliarios.nombre, OtrosRecursos.nombre)
    filas = db.execute(
        select(Recursos.id, nombre)
        .outerjoin(Equipos, Equipos.id == Recursos.id)
        .outerjoin(Mobiliarios, Mobiliarios.id == Recursos.id)
        .outerjoin(OtrosRecursos, OtrosRecursos.id == Recursos.id)
        .where(Recursos.id.in_(ids))
    ).all()
    return {fila[0]: fila[1] for fila in filas}


def cambiar_habilitado(db: Session, recurso: Recursos, habilitado: bool) -> None:
    recurso.habilitado = habilitado
    recurso.updated_at = datetime.now(timezone.utc)


def unidad_espacio_vinculado(db: Session, id_recurso: int) -> int | None:
    """`id_unidad` del espacio al que el recurso está asociado activamente
    (contrato §2.7: la unidad de destino debe coincidir), o `None` si no
    tiene una asociación vigente. `espacios/espacio_recursos` los modela
    `resources`, pero los gestiona el módulo `espacios` (`API-10`, aún sin
    construir); no puede haber filas todavía, así que este chequeo hoy nunca
    dispara, pero queda correcto para cuando ese módulo empiece a escribir."""
    return db.scalar(
        select(Espacios.id_unidad)
        .join(EspacioRecursos, EspacioRecursos.espacio_id == Espacios.id)
        .where(EspacioRecursos.recurso_id == id_recurso, EspacioRecursos.habilitado.is_(True))
    )


def cambiar_unidad(db: Session, recurso: Recursos, id_unidad: int, especializacion) -> None:
    recurso.id_unidad = id_unidad
    recurso.updated_at = datetime.now(timezone.utc)
    if hasattr(especializacion, "id_unidad"):
        especializacion.id_unidad = id_unidad


# --- Impacto de deshabilitación (RN-DES-06/07, RN-CAN-04/05) -----------------

_ESTADOS_BLOQUEANTES = ("SOLICITADA", "APROBADA")


def contar_impacto(db: Session, id_recurso: int) -> tuple[int, int]:
    """`(reservas_a_cancelar, reservas_a_retirar)` — asignaciones vigentes en
    estados bloqueantes, por rol. No ejecuta ningún cambio."""
    base = (
        select(ReservaRecursos.rol, func.count())
        .join(Reservas, Reservas.id == ReservaRecursos.reserva_id)
        .join(EstadosReserva, EstadosReserva.id == Reservas.estado_id)
        .where(
            ReservaRecursos.recurso_id == id_recurso,
            ReservaRecursos.estado_asignacion == "ASIGNADO",
            EstadosReserva.codigo.in_(_ESTADOS_BLOQUEANTES),
        )
        .group_by(ReservaRecursos.rol)
    )
    conteos = dict(db.execute(base).all())
    return conteos.get("PRINCIPAL", 0), conteos.get("ADICIONAL", 0)


def asignaciones_vigentes(db: Session, id_recurso: int) -> list[ReservaRecursos]:
    stmt = (
        select(ReservaRecursos)
        .join(Reservas, Reservas.id == ReservaRecursos.reserva_id)
        .join(EstadosReserva, EstadosReserva.id == Reservas.estado_id)
        .where(
            ReservaRecursos.recurso_id == id_recurso,
            ReservaRecursos.estado_asignacion == "ASIGNADO",
            EstadosReserva.codigo.in_(_ESTADOS_BLOQUEANTES),
        )
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


def retirar_asignacion(db: Session, asignacion: ReservaRecursos) -> None:
    asignacion.estado_asignacion = "RETIRADO"


# --- Configuración del laboratorio ---------------------------------------------


def listar_laboratorios(db: Session) -> list[tuple[int, str, bool]]:
    """Unidades activas con configuración de reservas, por nombre."""
    filas = db.execute(
        select(UnidadOrganizacional.id_unidad, UnidadOrganizacional.nombre, LaboratoriosConfig.habilitado_reservas)
        .join(LaboratoriosConfig, LaboratoriosConfig.id_unidad == UnidadOrganizacional.id_unidad)
        .where(UnidadOrganizacional.estado.is_(True))
        .order_by(UnidadOrganizacional.nombre)
    ).all()
    return [(f[0], f[1], f[2]) for f in filas]


def obtener_config(db: Session, id_unidad: int) -> LaboratoriosConfig | None:
    return db.scalar(select(LaboratoriosConfig).where(LaboratoriosConfig.id_unidad == id_unidad))


def catalogo_tipos_reserva(db: Session) -> dict[str, int]:
    return dict(db.execute(select(TiposReserva.codigo, TiposReserva.id)).all())


def obtener_tipos_habilitados(db: Session, id_unidad: int) -> list[str]:
    stmt = (
        select(TiposReserva.codigo)
        .join(LaboratorioTiposReserva, LaboratorioTiposReserva.tipo_reserva_id == TiposReserva.id)
        .where(LaboratorioTiposReserva.id_unidad == id_unidad, LaboratorioTiposReserva.habilitado.is_(True))
    )
    return list(db.scalars(stmt).all())


def cerrar_version_vigente(db: Session, id_unidad: int, hasta: datetime) -> None:
    """RN-LAB-08: la versión vigente (`vigente_hasta IS NULL`) se cierra
    antes de abrir la siguiente, para que no se solapen."""
    vigente = db.scalar(
        select(LaboratoriosConfigHistorico).where(
            LaboratoriosConfigHistorico.id_unidad == id_unidad,
            LaboratoriosConfigHistorico.vigente_hasta.is_(None),
        )
    )
    if vigente is not None:
        vigente.vigente_hasta = hasta


def abrir_version_historico(db: Session, config: LaboratoriosConfig, desde: datetime) -> None:
    db.add(LaboratoriosConfigHistorico(
        id_unidad=config.id_unidad, dias_atencion=config.dias_atencion,
        hora_apertura=config.hora_apertura, hora_cierre=config.hora_cierre,
        horario_atencion=config.horario_atencion, vigente_desde=desde, vigente_hasta=None,
    ))


def actualizar_tipos_reserva(db: Session, id_unidad: int, codigos_habilitados: set[str], todos_los_codigos: dict[str, int]) -> None:
    existentes = {
        lt.tipo_reserva_id: lt
        for lt in db.scalars(select(LaboratorioTiposReserva).where(LaboratorioTiposReserva.id_unidad == id_unidad))
    }
    ahora = datetime.now(timezone.utc)
    for codigo, tipo_id in todos_los_codigos.items():
        habilitado = codigo in codigos_habilitados
        if tipo_id in existentes:
            existentes[tipo_id].habilitado = habilitado
            existentes[tipo_id].updated_at = ahora
        elif habilitado:
            db.add(LaboratorioTiposReserva(
                id_unidad=id_unidad, tipo_reserva_id=tipo_id, habilitado=True,
                created_at=ahora, updated_at=ahora,
            ))
