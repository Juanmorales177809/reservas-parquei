from datetime import time

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.domain.enums import EstadoEntidad
from app.domain.valor import HorarioAtencion


class EspacioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    ubicacion: str
    capacidad: int
    estado: EstadoEntidad
    dias_atencion: list[int]
    hora_apertura: time
    hora_cierre: time
    horario_atencion: dict[int, list[int]]
    horas_antelacion: int


class EspacioCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    ubicacion: str = Field(default="Sede Central", max_length=200)
    capacidad: int = Field(gt=0)
    estado: EstadoEntidad = EstadoEntidad.ACTIVO


class EspacioUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=100)
    ubicacion: str | None = Field(default=None, max_length=200)
    capacidad: int | None = Field(default=None, gt=0)
    estado: EstadoEntidad | None = None


class ConfiguracionEspacioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    espacio_id: int
    espacio_nombre: str
    dias_atencion: list[int]
    hora_apertura: time
    hora_cierre: time
    horario_atencion: dict[int, list[int]]
    horas_antelacion: int
    aprobacion_automatica: bool


class ConfiguracionEspacioUpdate(BaseModel):
    horario_atencion: dict[int, list[int]]
    horas_antelacion: int = Field(ge=0, le=8760)
    aprobacion_automatica: bool

    @field_validator("horario_atencion")
    @classmethod
    def validar_horario_atencion(cls, value: dict[int, list[int]]) -> dict[int, list[int]]:
        # Validación y normalización de contrato conservadas exactamente
        # (opción A): los días vacíos se mantienen con listas [] en la salida.
        horario: dict[int, list[int]] = {}
        for dia, horas in value.items():
            if dia < 0 or dia > 6:
                raise ValueError("Los días de atención deben estar entre 0 y 6")
            if any(hora < 0 or hora > 22 for hora in horas):
                raise ValueError("Las horas deben estar entre 0 y 22")
            horario[dia] = sorted(set(horas))
        if not any(horario.values()):
            raise ValueError("Debes seleccionar al menos una franja de atención")
        # Respaldo de invariantes de dominio: HorarioAtencion valida las mismas
        # reglas con su propia normalización interna (elimina días vacíos),
        # pero NO reemplaza la salida pública del schema. api/espacios.py
        # filtra posteriormente las listas vacías.
        HorarioAtencion(horario)
        return horario
