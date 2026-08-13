from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums import EstadoEntidad
from app.schemas.espacio import EspacioResponse


class TipoRecursoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    descripcion: str
    activo: str


class RecursoCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    tipo_recurso_id: int
    descripcion: str | None = None
    capacidad: int = Field(gt=0)
    estado: EstadoEntidad = EstadoEntidad.ACTIVO
    espacio_id: int | None = None


class RecursoUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=100)
    tipo_recurso_id: int | None = None
    descripcion: str | None = None
    capacidad: int | None = Field(default=None, gt=0)
    estado: EstadoEntidad | None = None
    espacio_id: int | None = None


class RecursoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    espacio_id: int
    tipo_recurso_id: int
    descripcion: str | None
    capacidad: int
    estado: EstadoEntidad
    espacio: EspacioResponse
    tipo: TipoRecursoResponse
