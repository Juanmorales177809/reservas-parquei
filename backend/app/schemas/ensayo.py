from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums import EstadoEntidad


class EnsayoCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    zona_id: int
    estado: EstadoEntidad = EstadoEntidad.ACTIVO


class EnsayoUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=100)
    zona_id: int | None = None
    estado: EstadoEntidad | None = None


class EnsayoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    zona_id: int
    estado: EstadoEntidad
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: int
