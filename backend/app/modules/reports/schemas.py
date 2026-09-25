"""Esquemas Pydantic del contrato de reports (API-19)."""

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
