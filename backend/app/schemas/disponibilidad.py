from pydantic import BaseModel

from app.domain.enums import EstadoSlot


class DisponibilidadSlot(BaseModel):
    hora_inicio: str  # "HH:MM"
    hora_fin: str  # "HH:MM"
    estado: EstadoSlot  # "libre" | "ocupado" | "mantenimiento"
