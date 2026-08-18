from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums import EstadoEntidad


class ZonaCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    espacio_id: int
    descripcion: str | None = None
    capacidad: int | None = Field(default=None, gt=0)
    estado: EstadoEntidad = EstadoEntidad.ACTIVO


class ZonaUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=100)
    espacio_id: int | None = None
    descripcion: str | None = None
    capacidad: int | None = Field(default=None, gt=0)
    estado: EstadoEntidad | None = None


class ZonaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    espacio_id: int
    descripcion: str | None
    capacidad: int | None
    estado: EstadoEntidad
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: int


class ZonaRecursosUpdate(BaseModel):
    """Fase 12C-3: reemplazo completo de la asociación Zona<->Recurso."""

    recurso_ids: list[int] = Field(default_factory=list)


class ZonaRecursosResponse(BaseModel):
    """Respuesta de PUT /zonas/{zona_id}/recursos. Deliberadamente no
    extiende ZonaResponse (que no incluye `recursos` todavía, ver 12C-2) —
    esta subfase agrega su propio schema mínimo en vez de ampliar el
    contrato ya aprobado de ZonaResponse sin necesidad."""

    zona_id: int
    recurso_ids: list[int]
