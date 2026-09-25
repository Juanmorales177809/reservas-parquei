"""`Reserva`: Context del patrón Strategy de reservations (`architecture.md`
§"Context e interfaz común"; API-13).

Objeto de trabajo en memoria, no una tabla ni un registro de auditoría. No
posee la transacción, no ejecuta SQL y no sustituye al servicio: agrega la
información ya cargada por `service.py`/`repository.py` y delega el
comportamiento específico del tipo a su `ReservationStrategy`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.modules.reservations.strategies.reservation_strategy import ReservationStrategy


@dataclass
class Reserva:
    """`cabecera` es el modelo `Reservas` ya persistido (edición) o `None`
    (creación, antes de existir la fila). `tipo_codigo` identifica el tipo
    de forma estable incluso antes de crear la cabecera."""

    tipo_codigo: str
    strategy: ReservationStrategy
    cabecera: Any = None
    detalle_actual: Any = None
    extra: dict[str, Any] = field(default_factory=dict)

    def validar(self, operacion: str, datos: dict, condiciones: dict) -> None:
        self.strategy.validar_operacion(self, operacion, datos, condiciones)

    def determinar_cambios(self, operacion: str, datos: dict, condiciones: dict) -> dict:
        return self.strategy.determinar_cambios(self, operacion, datos, condiciones)
