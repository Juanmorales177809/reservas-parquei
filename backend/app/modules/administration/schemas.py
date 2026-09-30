"""Esquemas Pydantic del contrato de administration §2 y §3 (API-07)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


def _no_vacio(v: str, maximo: int) -> str:
    v = v.strip()
    if not v:
        raise ValueError("No puede estar vacío ni compuesto solo por espacios.")
    if len(v) > maximo:
        raise ValueError(f"Supera el máximo de {maximo} caracteres.")
    return v


def _opt_100(v: str | None) -> str | None:
    return None if v is None else _no_vacio(v, 100)


def _opt_50(v: str | None) -> str | None:
    return None if v is None else _no_vacio(v, 50)


# --- §2 Unidades y cargos --------------------------------------------------------


class UnidadCrear(BaseModel):
    nombre: str = Field(max_length=100)
    tipo: str = Field(max_length=50)
    id_unidad_padre: int | None = None

    @field_validator("nombre")
    @classmethod
    def _v_nombre(cls, v):
        return _no_vacio(v, 100)

    @field_validator("tipo")
    @classmethod
    def _v_tipo(cls, v):
        return _no_vacio(v, 50)


class UnidadActualizar(BaseModel):
    nombre: str | None = Field(default=None, max_length=100)
    tipo: str | None = Field(default=None, max_length=50)
    id_unidad_padre: int | None = None

    @field_validator("nombre")
    @classmethod
    def _v_nombre(cls, v):
        return _opt_100(v)

    @field_validator("tipo")
    @classmethod
    def _v_tipo(cls, v):
        return _opt_50(v)


class UnidadRespuesta(BaseModel):
    id_unidad: int
    nombre: str
    tipo: str
    id_unidad_padre: int | None
    estado: bool


class EstadoSolicitud(BaseModel):
    estado: bool


class CargoCrear(BaseModel):
    nombre_cargo: str = Field(max_length=50)
    id_unidad: int

    @field_validator("nombre_cargo")
    @classmethod
    def _v_nombre(cls, v):
        return _no_vacio(v, 50)


class CargoActualizar(BaseModel):
    nombre_cargo: str | None = Field(default=None, max_length=50)
    id_unidad: int | None = None

    @field_validator("nombre_cargo")
    @classmethod
    def _v_nombre(cls, v):
        return _opt_50(v)


class CargoRespuesta(BaseModel):
    id_cargo: int
    nombre_cargo: str
    id_unidad: int


# --- §3 Permisos ------------------------------------------------------------------


class ImportacionResultadoFila(BaseModel):
    numero_fila: int
    codigo: str | None
    resultado: str
    detalle: str | None


class ImportacionTotalesValidacion(BaseModel):
    a_crear: int
    a_actualizar: int
    con_error: int


class ImportacionValidacionRespuesta(BaseModel):
    id: int
    catalogo: str
    id_unidad: int | None
    archivo_referencia: str
    confirmable: bool
    totales: ImportacionTotalesValidacion
    resultados: list[ImportacionResultadoFila]


class ImportacionTotalesConfirmacion(BaseModel):
    registros_creados: int
    registros_actualizados: int
    registros_desactivados: int


class ImportacionResumen(BaseModel):
    id: int
    actor_cuenta_id: int
    catalogo: str
    archivo_referencia: str
    registros_creados: int
    registros_actualizados: int
    registros_desactivados: int
    created_at: datetime
    confirmado_at: datetime | None


class ImportacionDetalle(ImportacionResumen):
    resultados: list[ImportacionResultadoFila]


# --- §5 Auditoría ----------------------------------------------------------------------


class AuditoriaRespuesta(BaseModel):
    id: int
    actor_cuenta_id: int
    entidad: str
    entidad_id: str
    accion: str
    datos_anteriores: dict | None = None
    datos_nuevos: dict | None = None
    motivo: str | None = None
    created_at: datetime
