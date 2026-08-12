from pydantic import BaseModel


class DisponibilidadSlot(BaseModel):
    hora_inicio: str  # "HH:MM"
    hora_fin: str  # "HH:MM"
    estado: str  # "libre" | "ocupado" | "mantenimiento"
