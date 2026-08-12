from datetime import date, datetime, time
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


ReservaEstado = Literal["esperando", "aprobada", "rechazada", "cancelada"]


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
    nuevo_estado: Literal["aprobada", "rechazada", "cancelada"]


class UsuarioReservaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    rol: str


class EspacioReservaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    capacidad: int
    estado: str


class RecursoReservaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    capacidad: int
    estado: str
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
    estado: ReservaEstado
    asistentes: int
    created_at: datetime
    updated_at: datetime
    usuario: UsuarioReservaResponse
    espacio: EspacioReservaResponse
    recurso: RecursoReservaResponse

    @field_validator("estado")
    @classmethod
    def validar_estado(cls, value: str) -> str:
        if value not in {"esperando", "aprobada", "rechazada", "cancelada"}:
            raise ValueError("Estado de reserva inválido")
        return value
