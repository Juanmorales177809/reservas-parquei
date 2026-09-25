"""Selector de estrategias: exactamente las cinco correspondencias del
catálogo (`architecture.md`). El tipo de una reserva existente determina su
estrategia; no se cambia de estrategia para eludir restricciones.
"""

from __future__ import annotations

from app.core.errors import TipoNoAdmitido
from app.modules.reservations.strategies.espacio import EspacioStrategy
from app.modules.reservations.strategies.lista_espera import ListaEsperaStrategy
from app.modules.reservations.strategies.recurso_campus import RecursoCampusStrategy
from app.modules.reservations.strategies.recurso_externo import RecursoExternoStrategy
from app.modules.reservations.strategies.recurso_interno import RecursoInternoStrategy
from app.modules.reservations.strategies.reservation_strategy import ReservationStrategy

_ESTRATEGIAS: dict[str, ReservationStrategy] = {
    "ESPACIO": EspacioStrategy(),
    "RECURSO_INTERNO": RecursoInternoStrategy(),
    "RECURSO_CAMPUS": RecursoCampusStrategy(),
    "RECURSO_EXTERNO": RecursoExternoStrategy(),
    "LISTA_ESPERA": ListaEsperaStrategy(),
}


def seleccionar(codigo_tipo: str) -> ReservationStrategy:
    estrategia = _ESTRATEGIAS.get(codigo_tipo)
    if estrategia is None:
        raise TipoNoAdmitido(f"Tipo de reserva desconocido: {codigo_tipo}.")
    return estrategia
