from datetime import date, datetime, time
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums import EstadoEntidad, EstadoReserva, Rol


class ReservaCreate(BaseModel):
    recurso_id: int
    fecha: date
    hora_inicio: time
    hora_fin: time
    asistentes: int = Field(gt=0)


class ReservaUpdate(BaseModel):
    recurso_id: int | None = None
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


class ReservaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
    espacio_id: int
    recurso_id: int
    fecha: date
    hora_inicio: time
    hora_fin: time
    estado: EstadoReserva
    asistentes: int
    created_at: datetime
    updated_at: datetime
    usuario: UsuarioReservaResponse
    espacio: EspacioReservaResponse
    recurso: RecursoReservaResponse
