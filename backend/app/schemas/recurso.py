from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums import EstadoEntidad
from app.schemas.laboratorio import LaboratorioResponse


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
    laboratorio_id: int | None = None
    # RN-009: recurso de "prestación de servicios" (PS). Visibilidad y
    # reserva restringidas a gestor/admin — ver app/api/recursos.py y
    # app/services/reservas.py (Fase 12B).
    es_prestacion_servicio: bool = False
    # Acompañamiento obligatorio del auxiliar/técnico -- ver
    # `app/models/recurso.py` y `app/services/reservas.py`.
    requiere_apoyo_auxiliar: bool = False


class RecursoUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=100)
    tipo_recurso_id: int | None = None
    descripcion: str | None = None
    capacidad: int | None = Field(default=None, gt=0)
    estado: EstadoEntidad | None = None
    laboratorio_id: int | None = None
    es_prestacion_servicio: bool | None = None
    requiere_apoyo_auxiliar: bool | None = None


class RecursoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    laboratorio_id: int
    tipo_recurso_id: int
    descripcion: str | None
    capacidad: int
    estado: EstadoEntidad
    laboratorio: LaboratorioResponse
    tipo: TipoRecursoResponse
    es_prestacion_servicio: bool
    requiere_apoyo_auxiliar: bool
    # Fase D: identificador de activo físico del inventario institucional
    # (ej. "05087964") -- `null` para un recurso creado a mano desde la UI.
    placa: str | None = None
