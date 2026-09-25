"""Esquemas Pydantic del contrato de resources (API-09)."""

from __future__ import annotations

from datetime import date, datetime, time
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

TipoRecurso = Literal["EQUIPO", "MOBILIARIO", "OTRO"]


def _no_vacio(v: str, maximo: int) -> str:
    v = v.strip()
    if not v:
        raise ValueError("No puede estar vacío ni compuesto solo por espacios.")
    if len(v) > maximo:
        raise ValueError(f"Supera el máximo de {maximo} caracteres.")
    return v


# --- §2 Catálogo de recursos --------------------------------------------------


class RecursoCrear(BaseModel):
    id_unidad: int
    tipo: TipoRecurso
    especializacion: dict[str, Any]


class RecursoResumen(BaseModel):
    id: int
    tipo: TipoRecurso
    id_unidad: int
    habilitado: bool


class RecursoDetalle(BaseModel):
    id: int
    tipo: TipoRecurso
    id_unidad: int
    habilitado: bool
    created_at: datetime
    updated_at: datetime
    especializacion: dict[str, Any]


class RecursoActualizar(BaseModel):
    """Campos admitidos dependen del tipo; el servicio los valida contra el
    conjunto editable de cada especialización (contrato §2.4)."""

    especializacion: dict[str, Any]


class EstadoActualizar(BaseModel):
    habilitado: bool
    confirmado: bool = False


class EstadoRespuesta(BaseModel):
    id: int
    habilitado: bool
    reservas_canceladas: int
    reservas_afectadas: int


class ImpactoRespuesta(BaseModel):
    reservas_a_cancelar: int
    reservas_a_retirar: int


class UnidadActualizar(BaseModel):
    id_unidad: int


# --- §3 Configuración del laboratorio -----------------------------------------


class ConfiguracionRespuesta(BaseModel):
    id_unidad: int
    habilitado_reservas: bool
    dias_atencion: list[int]
    hora_apertura: time
    hora_cierre: time
    horas_antelacion: int
    aprobacion_automatica: bool
    recordatorio_horas_antes: int
    mostrar_estado_reserva: bool
    mostrar_reservista: bool
    tipos_reserva: list[str]


class ConfiguracionActualizar(BaseModel):
    habilitado_reservas: bool | None = None
    dias_atencion: list[int] | None = None
    hora_apertura: time | None = None
    hora_cierre: time | None = None
    horas_antelacion: int | None = Field(default=None, ge=0)
    aprobacion_automatica: bool | None = None
    recordatorio_horas_antes: int | None = Field(default=None, gt=0)
    ubicacion: str | None = None
    descripcion: str | None = None
    modalidad_reserva: str | None = None
    correo: str | None = None
    notificar_por_correo: bool | None = None

    @field_validator("dias_atencion")
    @classmethod
    def _v_dias(cls, v):
        if v is not None:
            if not v or any(d < 0 or d > 6 for d in v):
                raise ValueError("dias_atencion debe ser una lista no vacía de enteros 0-6 (0=domingo).")
        return v


class TiposReservaActualizar(BaseModel):
    tipos: list[str]


class VisibilidadActualizar(BaseModel):
    mostrar_estado_reserva: bool
    mostrar_reservista: bool
