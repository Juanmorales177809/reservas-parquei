"""Esquemas Pydantic del contrato de reports (API-19, API-20 §3.4)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class ReporteResumen(BaseModel):
    dimension: str | None = None
    desde: str | None = None
    hasta: str | None = None
    filtros: dict[str, Any] = {}


class ReporteRespuesta(BaseModel):
    resumen: ReporteResumen
    datos: list[dict[str, Any]]
    paginacion: dict[str, int]


class ResumenPeriodo(BaseModel):
    desde: str
    hasta: str
    desde_previo: str
    hasta_previo: str
    filtros: dict[str, Any] = {}


class IndicadorPar(BaseModel):
    actual: int
    previo: int


class IndicadorHoras(BaseModel):
    actual: float
    previo: float


class IndicadorPorcentaje(BaseModel):
    actual: float | None
    previo: float | None


class ResumenIndicadores(BaseModel):
    reservas: IndicadorPar
    solicitadas: int
    horas_reservadas: IndicadorHoras
    porcentaje_ocupacion: IndicadorPorcentaje


class FilaLaboratorio(BaseModel):
    id_unidad: int
    nombre: str
    reservas: int
    horas_reservadas: float
    porcentaje_ocupacion: float | None


class RecursoTop(BaseModel):
    recurso_id: int
    nombre: str
    reservas: int


class CeldaCalor(BaseModel):
    dia: int
    hora: int
    cantidad: int


class PuntoFecha(BaseModel):
    fecha: str
    reservas: int


class ResumenRespuesta(BaseModel):
    resumen: ResumenPeriodo
    indicadores: ResumenIndicadores
    por_estado: dict[str, int]
    por_fecha: list[PuntoFecha]
    por_laboratorio: list[FilaLaboratorio]
    recursos_mas_reservados: list[RecursoTop]
    ocupacion_dia_hora: list[CeldaCalor]
