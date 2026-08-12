from datetime import datetime

from pydantic import BaseModel


class ControlCambioResponse(BaseModel):
    id: int
    usuario_id: int | None
    usuario: str
    accion: str
    entidad: str
    entidad_id: int | None
    descripcion: str
    created_at: datetime
