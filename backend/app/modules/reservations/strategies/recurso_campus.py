"""RecursoCampusStrategy: préstamo que sale del laboratorio y permanece en
campus (RN-TIP-RC). Comparte compromiso físico, proceso de salida y FGL 030
con externo mediante `PrestamoFisicoPolicy`; la diferencia entre ambas es
únicamente la tabla de detalle."""

from __future__ import annotations

from app.modules.reservations.policies import prestamo_fisico as prestamo_policy
from app.modules.reservations.strategies.reservation_strategy import ReservationStrategy


class RecursoCampusStrategy(ReservationStrategy):
    codigo = "RECURSO_CAMPUS"

    def validar_crear(self, reserva, datos: dict, condiciones: dict) -> None:
        prestamo_policy.validar_creacion(
            condiciones["db"], detalle=datos["detalle"], recursos=datos.get("recursos") or [],
            ahora=condiciones["ahora"], excluir_reserva_id=condiciones.get("excluir_reserva_id"),
        )

    def cambios_crear(self, reserva, datos: dict, condiciones: dict) -> dict:
        detalle = datos["detalle"]
        return {
            "detalle_campus": {"fecha_salida": detalle["fecha_salida"], "fecha_devolucion_estimada": detalle["fecha_devolucion_estimada"]},
            "datos_salida": {
                "razon_solicitud": detalle["razon_solicitud"], "lugar_nombre": detalle["lugar_nombre"],
                "lugar_direccion": detalle["lugar_direccion"], "nombre_actividad_evento": detalle.get("nombre_actividad_evento"),
            },
            "recursos": [{"recurso_id": r["recurso_id"], "rol": r["rol"]} for r in datos.get("recursos") or []],
        }

    def validar_editar(self, reserva, datos: dict, condiciones: dict) -> None:
        self.validar_crear(reserva, datos, condiciones)

    def cambios_editar(self, reserva, datos: dict, condiciones: dict) -> dict:
        return self.cambios_crear(reserva, datos, condiciones)
