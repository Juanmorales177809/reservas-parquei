from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums import EstadoEntidad


class EspacioCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    laboratorio_id: int
    descripcion: str | None = None
    capacidad: int | None = Field(default=None, gt=0)
    estado: EstadoEntidad = EstadoEntidad.ACTIVO


class EspacioUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=100)
    laboratorio_id: int | None = None
    descripcion: str | None = None
    capacidad: int | None = Field(default=None, gt=0)
    estado: EstadoEntidad | None = None


class EspacioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    laboratorio_id: int
    descripcion: str | None
    capacidad: int | None
    estado: EstadoEntidad
    created_at: datetime
    updated_at: datetime
    # Nullable desde 2026-08-29 (bug real de producción, ver
    # backend/CLAUDE.md): un created_by/updated_by huérfano se limpia a
    # NULL en la migración en vez de romperla.
    created_by: int | None
    updated_by: int | None
    # Fase A1 (recursos por espacio): qué recursos tiene asociados hoy el
    # espacio -- sin esto, la UI que deja editar la asociación (reemplazo
    # completo vía PUT /espacios/{id}/recursos) no puede mostrar la
    # selección actual antes de dejarla cambiar.
    recurso_ids: list[int] = Field(default_factory=list)


class EspacioRecursosUpdate(BaseModel):
    """Fase 12C-3: reemplazo completo de la asociación Espacio<->Recurso."""

    recurso_ids: list[int] = Field(default_factory=list)


class EspacioRecursosResponse(BaseModel):
    """Respuesta de PUT /espacios/{espacio_id}/recursos. Deliberadamente no
    extiende EspacioResponse (que no incluye `recursos` todavía, ver 12C-2) —
    esta subfase agrega su propio schema mínimo en vez de ampliar el
    contrato ya aprobado de EspacioResponse sin necesidad."""

    espacio_id: int
    recurso_ids: list[int]
