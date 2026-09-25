"""Repositorio de notifications (API-17): solo lectura de la bandeja y
preferencias propias. La generación de eventos y envíos es API-18; aquí no
se crea ninguna notificación.
"""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models.notificaciones import (
    Eventos,
    Notificaciones,
    Preferencias,
    TiposEvento,
)


def bandeja(
    db: Session, id_cuenta: int, *, leida: bool | None, tipo_codigo: str | None,
    offset: int, tamano: int,
) -> tuple[list[tuple[Notificaciones, Eventos, TiposEvento]], int]:
    stmt = (
        select(Notificaciones, Eventos, TiposEvento)
        .join(Eventos, Eventos.id == Notificaciones.evento_id)
        .join(TiposEvento, TiposEvento.id == Eventos.tipo_evento_id)
        .where(Notificaciones.id_cuenta == id_cuenta)
    )
    if leida is True:
        stmt = stmt.where(Notificaciones.leida_at.is_not(None))
    elif leida is False:
        stmt = stmt.where(Notificaciones.leida_at.is_(None))
    if tipo_codigo is not None:
        stmt = stmt.where(TiposEvento.codigo == tipo_codigo)
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    filas = db.execute(
        stmt.order_by(Notificaciones.created_at.desc()).offset(offset).limit(tamano)
    ).all()
    return list(filas), total


def obtener_notificacion(db: Session, id_notificacion: int, id_cuenta: int) -> Notificaciones | None:
    """Solo propia: ajena e inexistente son indistinguibles (RN-CON-01)."""
    return db.scalar(
        select(Notificaciones).where(
            Notificaciones.id == id_notificacion, Notificaciones.id_cuenta == id_cuenta
        )
    )


def marcar_leida(db: Session, notificacion: Notificaciones, ahora) -> Notificaciones:
    if notificacion.leida_at is None:
        notificacion.leida_at = ahora
    return notificacion


def tipos_habilitados(db: Session) -> list[TiposEvento]:
    return list(db.scalars(
        select(TiposEvento).where(TiposEvento.habilitado.is_(True)).order_by(TiposEvento.id)
    ).all())


def obtener_tipo(db: Session, tipo_evento_id: int) -> TiposEvento | None:
    return db.get(TiposEvento, tipo_evento_id)


def preferencias_de_cuenta(db: Session, id_cuenta: int) -> list[Preferencias]:
    return list(db.scalars(
        select(Preferencias).where(Preferencias.id_cuenta == id_cuenta)
    ).all())


def reemplazar_preferencias(db: Session, id_cuenta: int, general: bool, por_evento: list[dict]) -> None:
    db.query(Preferencias).filter(Preferencias.id_cuenta == id_cuenta).delete()
    db.add(Preferencias(id_cuenta=id_cuenta, tipo_evento_id=None, correo_habilitado=general))
    for item in por_evento:
        db.add(Preferencias(
            id_cuenta=id_cuenta, tipo_evento_id=item["tipo_evento_id"],
            correo_habilitado=item["correo_habilitado"],
        ))
    db.flush()
