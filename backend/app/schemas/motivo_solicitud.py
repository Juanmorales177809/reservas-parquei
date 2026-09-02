from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MotivoSolicitudCreate(BaseModel):
    laboratorio_id: int
    nombre: str
    codigo: str
    estado: str = "activo"


class MotivoSolicitudUpdate(BaseModel):
    nombre: str | None = None
    codigo: str | None = None
    estado: str | None = None


class MotivoSolicitudResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    laboratorio_id: int
    nombre: str
    codigo: str
    estado: str
    created_at: datetime
    updated_at: datetime
    created_by: int | None = None
    updated_by: int | None = None
