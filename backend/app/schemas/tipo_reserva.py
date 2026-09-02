from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# Solo 2 estados a propósito (a diferencia de EstadoEntidad, que agrega
# "mantenimiento" para espacios/recursos físicos -- un tipo de reserva no es
# un espacio físico, no tiene sentido "en mantenimiento"). Mismo par de
# valores que el CheckConstraint de app/models/tipo_reserva.py.
EstadoTipoReserva = Literal["activo", "inactivo"]


class TipoReservaCreate(BaseModel):
    laboratorio_id: int
    nombre: str = Field(min_length=1, max_length=100)
    estado: EstadoTipoReserva = "activo"


class TipoReservaUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=100)
    estado: EstadoTipoReserva | None = None


class TipoReservaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    laboratorio_id: int
    nombre: str
    estado: EstadoTipoReserva
    created_at: datetime
    updated_at: datetime
    created_by: int | None
    updated_by: int | None
