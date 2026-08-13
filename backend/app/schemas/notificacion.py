from datetime import datetime

from pydantic import BaseModel

from app.domain.enums import TipoNotificacion


class NotificacionResponse(BaseModel):
    id: int
    usuario_id: int
    reserva_id: int | None
    tipo: TipoNotificacion
    leida: bool
    created_at: datetime
    mensaje: str


class NotificacionesSinLeerResponse(BaseModel):
    cantidad: int
