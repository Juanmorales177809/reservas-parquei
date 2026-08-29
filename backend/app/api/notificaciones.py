from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import case, func
from sqlalchemy.orm import Session, joinedload

from app.db import get_db
from app.deps import get_current_user
from app.models import Notificacion, Personal, Recurso, Reserva, Usuario
from app.models.reserva_recurso import ReservaRecurso
from app.schemas.notificacion import NotificacionResponse, NotificacionesSinLeerResponse
from app.services.actores import mismo_actor


router = APIRouter(prefix="/notificaciones", tags=["notificaciones"])


def _etiqueta_objetivo(notificacion: Notificacion) -> str:
    """Nombre mostrable de una reserva para los mensajes (Fase 12C-4e-lectores):
    la/s zona/s si la reserva las tiene; si no, TODOS los recursos asociados
    (vía `reserva_recursos`), no solo el ancla singular `Reserva.recurso`."""
    reserva = notificacion.reserva
    if reserva is None:
        return "el recurso"
    zonas = list(reserva.zonas or [])
    if zonas:
        return "la zona " + ", ".join(z.nombre for z in zonas)
    nombres = [
        fila.recurso.nombre
        for fila in sorted(reserva.recursos_asociados or (), key=lambda fila: fila.recurso_id)
        if fila.recurso is not None
    ]
    return ", ".join(nombres) if nombres else "el recurso"


def _mensaje(notificacion: Notificacion) -> str:
    etiqueta = _etiqueta_objetivo(notificacion)
    if notificacion.tipo == "Pendiente":
        return f"Nueva reserva pendiente para {etiqueta}"
    if notificacion.tipo == "Aprobada":
        return f"Tu reserva de {etiqueta} fue aprobada"
    if notificacion.tipo == "Rechazada":
        base = f"Tu reserva de {etiqueta} fue rechazada"
        motivo = getattr(notificacion.reserva, "motivo_rechazo", None) if notificacion.reserva else None
        if motivo:
            return f"{base}: {motivo}"
        return base
    if notificacion.tipo == "Actualizada":
        return f"Tu reserva de {etiqueta} fue actualizada con nuevos recursos"
    # Cancelada: dos remitentes posibles con el mismo tipo (ver
    # services/reservas.py) -- el propio dueño de la reserva (gestor/admin
    # la canceló, cambiar_estado) o un gestor del espacio (el dueño canceló
    # su propia reserva ya aprobada, cancelar_reserva_usuario). Distinguir
    # por destinatario evita el "Tu reserva..." engañoso cuando quien lee
    # la notificación no es quien la hizo.
    reserva = notificacion.reserva
    if reserva is not None and not mismo_actor(notificacion, reserva):
        return f"Se canceló la reserva de {etiqueta}"
    return f"Tu reserva de {etiqueta} fue cancelada"


def _respuesta(notificacion: Notificacion) -> NotificacionResponse:
    return NotificacionResponse(
        id=notificacion.id,
        usuario_id=notificacion.actor.id,
        reserva_id=notificacion.reserva_id,
        tipo=notificacion.tipo,
        leida=notificacion.leida,
        created_at=notificacion.created_at,
        mensaje=_mensaje(notificacion),
    )


def _columna_actor(actor: Personal | Usuario):
    """Polimórfico, mismo motivo que `services/actores.py::columnas_actor`
    -- un gestor también recibe notificaciones (reserva pendiente de su
    espacio, cancelación de una reserva aprobada), así que `/notificaciones`
    no puede filtrar siempre por `Notificacion.usuario_id`."""
    return Notificacion.personal_id if isinstance(actor, Personal) else Notificacion.usuario_id


def _query_actor(db: Session, actor: Personal | Usuario):
    return (
        db.query(Notificacion)
        .options(
            joinedload(Notificacion.reserva)
            .joinedload(Reserva.recursos_asociados)
            .joinedload(ReservaRecurso.recurso)
            .joinedload(Recurso.espacio),
            joinedload(Notificacion.reserva).joinedload(Reserva.zonas),
        )
        .filter(_columna_actor(actor) == actor.id)
    )


@router.get("", response_model=list[NotificacionResponse])
def listar_mis_notificaciones(
    current_user: Personal | Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    notificaciones = (
        _query_actor(db, current_user)
        .order_by(
            case((Notificacion.leida.is_(False), 0), else_=1),
            Notificacion.created_at.desc(),
        )
        .all()
    )
    return [_respuesta(notificacion) for notificacion in notificaciones]


@router.get("/sin-leer/count", response_model=NotificacionesSinLeerResponse)
def contar_mis_notificaciones_sin_leer(
    current_user: Personal | Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cantidad = (
        db.query(func.count(Notificacion.id))
        .filter(
            _columna_actor(current_user) == current_user.id,
            Notificacion.leida.is_(False),
        )
        .scalar()
    )
    return {"cantidad": cantidad or 0}


@router.patch("/leer-todas", response_model=NotificacionesSinLeerResponse)
def marcar_todas_como_leidas(
    current_user: Personal | Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    actualizadas = (
        db.query(Notificacion)
        .filter(
            _columna_actor(current_user) == current_user.id,
            Notificacion.leida.is_(False),
        )
        .update({Notificacion.leida: True}, synchronize_session=False)
    )
    db.commit()
    return {"cantidad": actualizadas}


@router.patch("/{notificacion_id}/leer", response_model=NotificacionResponse)
def marcar_como_leida(
    notificacion_id: int,
    current_user: Personal | Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    notificacion = (
        _query_actor(db, current_user)
        .filter(Notificacion.id == notificacion_id)
        .first()
    )
    if notificacion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificación no encontrada",
        )
    if not notificacion.leida:
        notificacion.leida = True
        db.commit()
        db.refresh(notificacion)
    return _respuesta(notificacion)
