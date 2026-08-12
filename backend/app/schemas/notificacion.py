from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class NotificacionResponse(BaseModel):
    id: int
    usuario_id: int
    reserva_id: int | None
    tipo: Literal["Pendiente", "Aprobada", "Rechazada", "Cancelada"]
    leida: bool
    created_at: datetime
    mensaje: str


class NotificacionesSinLeerResponse(BaseModel):
    cantidad: int
