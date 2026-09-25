"""Esquemas Pydantic del contrato de espacios (API-10)."""

from __future__ import annotations

from datetime import time
from typing import Literal

from pydantic import BaseModel

TipoCampo = Literal["TEXTO", "TEXTO_LARGO", "NUMERO", "BOOLEANO", "SELECCION"]


# --- §2 Espacios ----------------------------------------------------------------


class EspacioCampoOpcionCrear(BaseModel):
    valor: str
    orden: int = 0


class EspacioCampoCrear(BaseModel):
    nombre: str
    tipo: TipoCampo
    obligatorio: bool = False
    orden: int = 0
    opciones: list[EspacioCampoOpcionCrear] = []


class EspacioCrear(BaseModel):
    id_unidad: int
    nombre: str
    ubicacion: str | None = None
    capacidad: int
    descripcion: str | None = None
    recursos: list[int] = []
    campos: list[EspacioCampoCrear] = []


class EspacioActualizar(BaseModel):
    nombre: str | None = None
    ubicacion: str | None = None
    capacidad: int | None = None
    descripcion: str | None = None


class EspacioResumen(BaseModel):
    id: int
    id_unidad: int
    nombre: str
    capacidad: int
    habilitado: bool


class RecursoAsociado(BaseModel):
    recurso_id: int
    nombre: str | None
    habilitado: bool


class EspacioCampoOpcion(BaseModel):
    id: int
    valor: str
    orden: int
    habilitado: bool


class EspacioCampoDetalle(BaseModel):
    id: int
    nombre: str
    tipo: str
    obligatorio: bool
    orden: int
    habilitado: bool
    opciones: list[EspacioCampoOpcion] = []


class HorarioUnidad(BaseModel):
    dias_atencion: list[int]
    hora_apertura: time
    hora_cierre: time


class EspacioDetalle(BaseModel):
    id: int
    id_unidad: int
    nombre: str
    ubicacion: str | None
    capacidad: int
    descripcion: str | None
    habilitado: bool
    horario_unidad: HorarioUnidad | None
    recursos: list[RecursoAsociado]
    campos: list[EspacioCampoDetalle]


class EstadoActualizar(BaseModel):
    habilitado: bool
    confirmado: bool = False


class EstadoRespuesta(BaseModel):
    id: int
    habilitado: bool
    reservas_canceladas: int


class ImpactoRespuesta(BaseModel):
    reservas_a_cancelar: int


# --- §3 Recursos asociados --------------------------------------------------------


class RecursosAsociar(BaseModel):
    recursos: list[int]


# --- §4 Campos adicionales ---------------------------------------------------------


class CampoActualizar(BaseModel):
    nombre: str | None = None
    obligatorio: bool | None = None
    orden: int | None = None


class CampoEstadoActualizar(BaseModel):
    habilitado: bool


class OrdenItem(BaseModel):
    campo_id: int
    orden: int


class OrdenActualizar(BaseModel):
    orden: list[OrdenItem]


class OpcionesCrear(BaseModel):
    opciones: list[EspacioCampoOpcionCrear]


class OpcionActualizar(BaseModel):
    valor: str | None = None
    orden: int | None = None
    habilitado: bool | None = None
