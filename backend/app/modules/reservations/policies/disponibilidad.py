"""DisponibilidadPolicy: traduce las consultas de solapamiento y compromiso
físico del repositorio a los códigos de conflicto del contrato (RN-DIS).

Las consultas viven en `repository.py`, porque acceden a la base; esta
política solo decide qué excepción corresponde a cada resultado, para que
ninguna estrategia repita el mapeo.
"""

from __future__ import annotations

from app.core.errors import Conflicto, Solapamiento


def exigir_sin_solapamiento(solapa: bool, mensaje: str = "El espacio o recurso ya está ocupado en el periodo solicitado.") -> None:
    if solapa:
        raise Solapamiento(mensaje)


def exigir_sin_compromiso_fisico_ajeno(comprometido: bool, mensaje: str = "El recurso tiene un compromiso vigente y no puede incluirse en otra solicitud.") -> None:
    if comprometido:
        raise Conflicto(mensaje)


def exigir_habilitado_y_operativo(habilitado: bool, operativo: bool | None, mensaje: str = "El recurso no está habilitado u operativo.") -> None:
    if not habilitado or operativo is False:
        raise Conflicto(mensaje)
