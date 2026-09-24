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


class PermisoResumen(BaseModel):
    codigo: str
    nombre: str
    descripcion: str | None
    habilitado: bool
    ambito: str


class AsignacionRespuesta(BaseModel):
    id_cuenta_permiso: int
    id_cuenta: int
    codigo: str
    id_unidad: int | None
    otorgado_por: int
    created_at: datetime


class PermisoOtorgar(BaseModel):
    codigo: str
    id_unidad: int | None = None
