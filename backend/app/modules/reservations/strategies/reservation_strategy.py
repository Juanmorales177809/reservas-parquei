"""Interfaz común `ReservationStrategy` (`architecture.md` §"Context e
interfaz común"; API-13).

`operacion` identifica únicamente los casos de uso ya existentes en el
contrato (`crear`, `editar`, `lista_espera_formulario`,
`lista_espera_viabilidad`, ...). Cada estrategia concreta implementa
`validar_<operacion>`/`cambios_<operacion>` solo para las que admite; el
despacho por defecto produce `TIPO_NO_ADMITIDO` para las demás, conforme al
contrato (nunca un método vacío que aparente éxito).

Ni `validar_operacion` ni `determinar_cambios` obtienen sesión, ejecutan
SQL o confirman transacciones: reciben `condiciones` ya resueltas por el
servicio (disponibilidad, configuración vigente, instante de evaluación) y
devuelven una decisión en memoria. La revalidación de concurrencia al
escribir sigue siendo responsabilidad de la transacción del servicio y de
las garantías de `DB-12`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.core.errors import TipoNoAdmitido

if TYPE_CHECKING:
    from app.modules.reservations.domain.reserva import Reserva


class ReservationStrategy:
    codigo: str

    def validar_operacion(self, reserva: "Reserva", operacion: str, datos: dict, condiciones: dict) -> None:
        metodo = getattr(self, f"validar_{operacion}", None)
        if metodo is None:
            raise TipoNoAdmitido(f"'{operacion}' no aplica al tipo {self.codigo}.")
        metodo(reserva, datos, condiciones)

    def determinar_cambios(self, reserva: "Reserva", operacion: str, datos: dict, condiciones: dict) -> dict:
        metodo = getattr(self, f"cambios_{operacion}", None)
        if metodo is None:
            raise TipoNoAdmitido(f"'{operacion}' no aplica al tipo {self.codigo}.")
        return metodo(reserva, datos, condiciones)
