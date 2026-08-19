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
    # Opcional (Fase 12E): datos legado migrados no siempre traen capacidad
    # conocida. Cuando falta, la validación de aforo de la reserva se salta
    # para ese recurso (ver services/reservas.py::_capacidad_efectiva).
    capacidad: int | None = Field(default=None, gt=0)
    estado: EstadoEntidad = EstadoEntidad.ACTIVO
    espacio_id: int | None = None
    # RN-009: recurso de "prestación de servicios" (PS). Visibilidad y
    # reserva restringidas a gestor/admin — ver app/api/recursos.py y
    # app/services/reservas.py (Fase 12B).
    es_prestacion_servicio: bool = False


class RecursoUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=100)
    tipo_recurso_id: int | None = None
    descripcion: str | None = None
    capacidad: int | None = Field(default=None, gt=0)
    estado: EstadoEntidad | None = None
    espacio_id: int | None = None
    es_prestacion_servicio: bool | None = None


class RecursoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    espacio_id: int
    tipo_recurso_id: int
    descripcion: str | None
    capacidad: int | None
    estado: EstadoEntidad
    espacio: EspacioResponse
    tipo: TipoRecursoResponse
    es_prestacion_servicio: bool
