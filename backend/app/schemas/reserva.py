from datetime import date, datetime, time
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.domain.enums import EstadoEntidad, EstadoReserva, Rol


class ReservaCreate(BaseModel):
    # Fase 12C-6: contrato aprobado. `recurso_id` legacy se rechaza con 422
    # (`extra="forbid"`), no se acepta como alias silencioso.
    model_config = ConfigDict(extra="forbid")

    recurso_ids: list[int] = Field(default_factory=list)
    zona_ids: list[int] = Field(default_factory=list)
    fecha: date
    hora_inicio: time
    hora_fin: time
    asistentes: int = Field(gt=0)

    @model_validator(mode="after")
    def _al_menos_un_recurso_o_zona(self) -> "ReservaCreate":
        if not self.recurso_ids and not self.zona_ids:
            raise ValueError("Debes indicar al menos un recurso o una zona")
        return self


class ReservaUpdate(BaseModel):
    # Fase 12C-6: ejes de reemplazo completo. Un eje ausente no modifica su
    # conjunto actual; un eje presente lo reemplaza entero. La combinación
    # final se valida en el servicio (puede quedar vacía según estado actual).
    model_config = ConfigDict(extra="forbid")

    recurso_ids: list[int] | None = None
    zona_ids: list[int] | None = None
    fecha: date | None = None
    hora_inicio: time | None = None
    hora_fin: time | None = None
    asistentes: int | None = Field(default=None, gt=0)


class ReservaEstadoUpdate(BaseModel):
    nuevo_estado: Literal[
        EstadoReserva.APROBADA, EstadoReserva.RECHAZADA, EstadoReserva.CANCELADA
    ]


class UsuarioReservaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    rol: Rol


class EspacioReservaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    capacidad: int
    estado: EstadoEntidad


class RecursoReservaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    capacidad: int
    estado: EstadoEntidad
    espacio: EspacioReservaResponse


class ZonaReservaResponse(BaseModel):
    """Zona asociada a una reserva (Fase 12C-6). Misma base mínima que
    `ZonaResponse` sin timestamps/auditoría — suficiente para la respuesta
    de la reserva y los mensajes de notificación."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    espacio_id: int
    descripcion: str | None
    capacidad: int | None
    estado: EstadoEntidad


class ReservaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
    espacio_id: int
    fecha: date
    hora_inicio: time
    hora_fin: time
    estado: EstadoReserva
    asistentes: int
    created_at: datetime
    updated_at: datetime
    usuario: UsuarioReservaResponse
    espacio: EspacioReservaResponse
    # Fase 12C-4e-schemas: `recurso_id`/`recurso` (el ancla singular) se
    # retiran del contrato. `recursos_asociados` (`crud.reservas`) sigue
    # siendo la fuente de verdad para los conjuntos -- `reservas.recurso_id`
    # (la columna), `Reserva.recurso` (la relación ORM) y
    # `reservas_sin_solapamiento` NO se tocan en esta subfase, solo dejan de
    # exponerse aquí.
    recurso_ids: list[int] = Field(default_factory=list)
    recursos: list[RecursoReservaResponse] = Field(default_factory=list)
    zona_ids: list[int] = Field(default_factory=list)
    zonas: list[ZonaReservaResponse] = Field(default_factory=list)
