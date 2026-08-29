from datetime import date, time

from sqlalchemy.orm import Session, joinedload

from app.models.personal import Personal
from app.models.recurso import Recurso
from app.models.reserva import ESTADOS_BLOQUEANTES, Reserva
from app.models.reserva_recurso import ReservaRecurso
from app.models.reserva_zona import ReservaZona
from app.models.usuario import Usuario

_OPTIONS_CARGA = (
    joinedload(Reserva.usuario),
    joinedload(Reserva.personal),
    joinedload(Reserva.espacio),
    joinedload(Reserva.recursos_asociados).joinedload(ReservaRecurso.recurso).joinedload(Recurso.espacio),
    joinedload(Reserva.zonas_asociadas),
    joinedload(Reserva.zonas),
    joinedload(Reserva.ensayos),
    joinedload(Reserva.acompanantes),
)


def _enriquecer_con_asociaciones(reservas: list[Reserva]) -> list[Reserva]:
    """Adjunta los conjuntos resueltos desde las tablas de asociación como
    atributos de instancia (no columnas) para que `ReservaResponse` los
    serialice (Fase 12C-6/12C-4e). Los ids se ordenan de forma estable.

    Fase 12C-4e-schemas: `ReservaResponse` retiró `recurso_id`/`recurso`
    (el ancla singular) -- esta función ya no necesita resolverlos ni
    asignarlos. `reservas.recurso_id` (la columna) y `Reserva.recurso` (la
    relación ORM) siguen intactos en el modelo; simplemente no se leen
    aquí. `.recursos` (plural, objetos `Recurso` completos, vía
    `reserva_recursos`) es el reemplazo expuesto en el schema."""
    for reserva in reservas:
        recursos_por_id = {fila.recurso_id: fila.recurso for fila in reserva.recursos_asociados or ()}
        reserva.recurso_ids = sorted(recursos_por_id)
        reserva.recursos = [recursos_por_id[i] for i in sorted(recursos_por_id)]
        reserva.zona_ids = sorted({fila.zona_id for fila in reserva.zonas_asociadas or ()})
        reserva.ensayo_ids = sorted({e.id for e in reserva.ensayos or ()})
    return reservas


def get_reservas(db: Session, skip: int = 0, limit: int = 100) -> list[Reserva]:
    return _enriquecer_con_asociaciones(
        db.query(Reserva)
        .options(*_OPTIONS_CARGA)
        .order_by(Reserva.fecha.desc(), Reserva.hora_inicio.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_reservas_gestion(
    db: Session,
    espacio_id: int | None,
    skip: int = 0,
    limit: int = 100,
) -> list[Reserva]:
    query = db.query(Reserva).options(*_OPTIONS_CARGA)
    if espacio_id is not None:
        query = query.filter(Reserva.espacio_id == espacio_id)
    return _enriquecer_con_asociaciones(
        query.order_by(Reserva.fecha.desc(), Reserva.hora_inicio.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_mis_reservas(db: Session, actor: Personal | Usuario) -> list[Reserva]:
    """Polimórfico (ver `services/actores.py`): filtra por `personal_id`
    o `usuario_id` según de qué tabla venga `actor` -- sin esto, un
    gestor que llamara este endpoint vería (o peor, colisionaría con) las
    reservas de un `Usuario` con el mismo id numérico."""
    columna = Reserva.personal_id if isinstance(actor, Personal) else Reserva.usuario_id
    return _enriquecer_con_asociaciones(
        db.query(Reserva)
        .options(*_OPTIONS_CARGA)
        .filter(columna == actor.id)
        .order_by(Reserva.fecha.desc(), Reserva.hora_inicio.desc())
        .all()
    )


def get_reservas_de_serie(db: Session, serie_id, actor: Personal | Usuario) -> list[Reserva]:
    """Las ocurrencias de una reserva recurrente (`Reserva.serie_id`,
    2026-08-29) que pertenecen a `actor` -- mismo criterio de propiedad que
    `get_mis_reservas`, nadie ve la serie de otra persona."""
    columna = Reserva.personal_id if isinstance(actor, Personal) else Reserva.usuario_id
    return _enriquecer_con_asociaciones(
        db.query(Reserva)
        .options(*_OPTIONS_CARGA)
        .filter(Reserva.serie_id == serie_id, columna == actor.id)
        .order_by(Reserva.fecha.asc())
        .all()
    )


def get_reserva(db: Session, reserva_id: int) -> Reserva | None:
    reserva = (
        db.query(Reserva)
        .options(*_OPTIONS_CARGA)
        .filter(Reserva.id == reserva_id)
        .first()
    )
    if reserva is None:
        return None
    return _enriquecer_con_asociaciones([reserva])[0]


def get_reservas_bloqueantes(
    db: Session,
    recurso_id: int,
    fecha: date,
    hora_inicio: time,
    hora_fin: time,
    exclude_id: int | None = None,
) -> list[Reserva]:
    """Reservas que bloquean el recurso/horario consultado.

    Fase 12C-5: la consulta por recurso hace JOIN contra `reserva_recursos`
    (la misma tabla que sostiene las constraints `reservas_sin_solapamiento`
    y `reserva_recursos_sin_solapamiento`), filtrando por sus columnas
    desnormalizadas -- ya no depende de la columna histórica
    `Reserva.recurso_id`. `distinct()` evita duplicar una reserva cuando
    tenga varias filas asociadas. Para los flujos legítimos (doble escritura
    y backfill) el resultado es idéntico al anterior.
    """
    query = (
        db.query(Reserva)
        .join(ReservaRecurso, ReservaRecurso.reserva_id == Reserva.id)
        .filter(
            ReservaRecurso.recurso_id == recurso_id,
            ReservaRecurso.fecha == fecha,
            ReservaRecurso.hora_inicio < hora_fin,
            ReservaRecurso.hora_fin > hora_inicio,
            ReservaRecurso.estado.in_(ESTADOS_BLOQUEANTES),
        )
    )
    if exclude_id is not None:
        query = query.filter(Reserva.id != exclude_id)
    return query.distinct().all()


def get_recurso_ids_reserva(db: Session, reserva_id: int) -> list[int]:
    """Recursos asociados a una reserva según `reserva_recursos` (Fase 12C-5).

    `distinct()`: una reserva con varias filas asociadas no repite recurso.
    La tabla de asociación es la fuente de verdad para la lectura interna;
    la columna histórica `Reserva.recurso_id` ya no se consulta aquí.
    """
    return [
        recurso_id
        for (recurso_id,) in (
            db.query(ReservaRecurso.recurso_id)
            .filter(ReservaRecurso.reserva_id == reserva_id)
            .distinct()
            .all()
        )
    ]


def get_zona_ids_reserva(db: Session, reserva_id: int) -> list[int]:
    """Zonas asociadas a una reserva según `reserva_zonas` (Fase 12C-6)."""
    return [
        zona_id
        for (zona_id,) in (
            db.query(ReservaZona.zona_id)
            .filter(ReservaZona.reserva_id == reserva_id)
            .distinct()
            .all()
        )
    ]


def get_zonas_bloqueantes(
    db: Session,
    zona_id: int,
    fecha: date,
    hora_inicio: time,
    hora_fin: time,
    exclude_id: int | None = None,
) -> list[Reserva]:
    """Reservas que bloquean la zona/horario consultado (Fase 12C-6).

    JOIN contra `reserva_zonas`, la misma tabla de la constraint
    `reserva_zonas_sin_solapamiento`; filtra por sus columnas
    desnormalizadas. `distinct()` evita duplicar reservas con varias zonas.
    """
    query = (
        db.query(Reserva)
        .join(ReservaZona, ReservaZona.reserva_id == Reserva.id)
        .filter(
            ReservaZona.zona_id == zona_id,
            ReservaZona.fecha == fecha,
            ReservaZona.hora_inicio < hora_fin,
            ReservaZona.hora_fin > hora_inicio,
            ReservaZona.estado.in_(ESTADOS_BLOQUEANTES),
        )
    )
    if exclude_id is not None:
        query = query.filter(Reserva.id != exclude_id)
    return query.distinct().all()


def get_ensayo_ids_reserva(db: Session, reserva_id: int) -> list[int]:
    """Ensayos asociados a una reserva según `reserva_ensayos` (Fase 12E)."""

    from app.models.reserva_ensayo import ReservaEnsayo

    return [
        ensayo_id
        for (ensayo_id,) in (
            db.query(ReservaEnsayo.ensayo_id)
            .filter(ReservaEnsayo.reserva_id == reserva_id)
            .distinct()
            .all()
        )
    ]
