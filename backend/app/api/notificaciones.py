from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import case, func
from sqlalchemy.orm import Session, joinedload

from app.db import get_db
from app.deps import get_current_user
from app.models import Notificacion, Recurso, Reserva, Usuario
from app.schemas.notificacion import NotificacionResponse, NotificacionesSinLeerResponse


router = APIRouter(prefix="/notificaciones", tags=["notificaciones"])


def _mensaje(notificacion: Notificacion) -> str:
    reserva = notificacion.reserva
    recurso = reserva.recurso.nombre if reserva and reserva.recurso else "el recurso"
    if notificacion.tipo == "Pendiente":
        return f"Nueva reserva pendiente para {recurso}"
    if notificacion.tipo == "Aprobada":
        return f"Tu reserva de {recurso} fue aprobada"
    if notificacion.tipo == "Rechazada":
        return f"Tu reserva de {recurso} fue rechazada"
    return f"Tu reserva de {recurso} fue cancelada"


def _respuesta(notificacion: Notificacion) -> NotificacionResponse:
    return NotificacionResponse(
        id=notificacion.id,
        usuario_id=notificacion.usuario_id,
        reserva_id=notificacion.reserva_id,
        tipo=notificacion.tipo,
        leida=notificacion.leida,
        created_at=notificacion.created_at,
        mensaje=_mensaje(notificacion),
    )


def _query_usuario(db: Session, usuario_id: int):
    return (
        db.query(Notificacion)
        .options(joinedload(Notificacion.reserva).joinedload(Reserva.recurso).joinedload(Recurso.espacio))
        .filter(Notificacion.usuario_id == usuario_id)
    )


@router.get("", response_model=list[NotificacionResponse])
def listar_mis_notificaciones(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    notificaciones = (
        _query_usuario(db, current_user.id)
        .order_by(
            case((Notificacion.leida.is_(False), 0), else_=1),
            Notificacion.created_at.desc(),
        )
        .all()
    )
    return [_respuesta(notificacion) for notificacion in notificaciones]


@router.get("/sin-leer/count", response_model=NotificacionesSinLeerResponse)
def contar_mis_notificaciones_sin_leer(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cantidad = (
        db.query(func.count(Notificacion.id))
        .filter(
            Notificacion.usuario_id == current_user.id,
            Notificacion.leida.is_(False),
        )
        .scalar()
    )
    return {"cantidad": cantidad or 0}


@router.patch("/leer-todas", response_model=NotificacionesSinLeerResponse)
def marcar_todas_como_leidas(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    actualizadas = (
        db.query(Notificacion)
        .filter(
            Notificacion.usuario_id == current_user.id,
            Notificacion.leida.is_(False),
        )
        .update({Notificacion.leida: True}, synchronize_session=False)
    )
    db.commit()
    return {"cantidad": actualizadas}


@router.patch("/{notificacion_id}/leer", response_model=NotificacionResponse)
def marcar_como_leida(
    notificacion_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    notificacion = (
        _query_usuario(db, current_user.id)
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
