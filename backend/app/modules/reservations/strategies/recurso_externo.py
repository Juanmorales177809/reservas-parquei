"""RecursoExternoStrategy: préstamo de recursos autorizados para salir del
campus (RN-TIP-RE). Idéntica a `RecursoCampusStrategy` salvo la tabla de
detalle; comparte `PrestamoFisicoPolicy`."""

from __future__ import annotations

from app.core.errors import Conflicto, EstadoIncompatible, NoEncontrado, Validacion
from app.modules.reservations import repository as repo
from app.modules.reservations.policies import prestamo_fisico as prestamo_policy
from app.modules.reservations.strategies.reservation_strategy import ReservationStrategy
from app.modules.resources import repository as rec_repo


class RecursoExternoStrategy(ReservationStrategy):
    codigo = "RECURSO_EXTERNO"

    def validar_crear(self, reserva, datos: dict, condiciones: dict) -> None:
        prestamo_policy.validar_creacion(
            condiciones["db"], detalle=datos["detalle"], recursos=datos.get("recursos") or [],
            ahora=condiciones["ahora"], excluir_reserva_id=condiciones.get("excluir_reserva_id"),
        )

    def cambios_crear(self, reserva, datos: dict, condiciones: dict) -> dict:
        detalle = datos["detalle"]
        return {
            "detalle_externo": {"fecha_salida": detalle["fecha_salida"], "fecha_devolucion_estimada": detalle["fecha_devolucion_estimada"]},
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

    # --- §4.1 Aprobación (API-14) -------------------------------------------------------

    def validar_aprobar(self, reserva, datos: dict, condiciones: dict) -> None:
        """RN-APR-07: revalida habilitación, operatividad y disponibilidad
        física excluyendo el compromiso propio, ya establecido desde la
        creación (RN-EST-02); las fechas no se revalidan porque no cambian."""
        db = condiciones["db"]
        for r in datos["recursos"]:
            recurso = rec_repo.obtener_recurso(db, r["recurso_id"])
            if recurso is None or not recurso.habilitado:
                raise NoEncontrado(f"El recurso {r['recurso_id']} no existe o no está habilitado.")
            if recurso.tipo == "EQUIPO":
                equipo = rec_repo.obtener_especializacion(db, "EQUIPO", r["recurso_id"])
                if equipo is not None and equipo.estado is False:
                    raise Conflicto(f"El recurso {r['recurso_id']} no está operativo.")
            prestamo_policy.validar_recurso_disponible_fisicamente(db, r["recurso_id"], excluir_reserva_id=condiciones.get("excluir_reserva_id"))

    # --- §6.1/§6.2 Salida física (API-14) ------------------------------------------------

    def validar_ejecutar(self, reserva, datos: dict, condiciones: dict) -> None:
        """RN-TIP-RE-09: la entrega debe cubrir exactamente los recursos
        vigentes de la reserva, todos habilitados, operativos y sin otro
        compromiso ajeno (excluyendo el propio)."""
        if condiciones.get("estado_actual") != "APROBADA":
            raise EstadoIncompatible("Solo se puede entregar una reserva APROBADA.")
        db = condiciones["db"]
        vigentes = repo.asignaciones_de_reserva(db, reserva.cabecera.id, solo_vigentes=True)
        ids_vigentes = {a.id for a in vigentes}
        ids_enviados = {r["reserva_recurso_id"] for r in datos["recursos"]}
        if ids_enviados != ids_vigentes:
            raise Validacion("Debe entregarse exactamente el conjunto de recursos vigentes de la reserva.")
        for a in vigentes:
            recurso = rec_repo.obtener_recurso(db, a.recurso_id)
            if recurso is None or not recurso.habilitado:
                raise Conflicto(f"El recurso {a.recurso_id} no está habilitado.")
            if recurso.tipo == "EQUIPO":
                equipo = rec_repo.obtener_especializacion(db, "EQUIPO", a.recurso_id)
                if equipo is not None and equipo.estado is False:
                    raise Conflicto(f"El recurso {a.recurso_id} no está operativo.")
            prestamo_policy.validar_recurso_disponible_fisicamente(db, a.recurso_id, excluir_reserva_id=reserva.cabecera.id)

    def cambios_ejecutar(self, reserva, datos: dict, condiciones: dict) -> dict:
        return {"entregas": datos["recursos"]}

    def validar_finalizar(self, reserva, datos: dict, condiciones: dict) -> None:
        """RN-TIP-RE-10: la devolución debe cubrir exactamente las entregas abiertas; no admite cierre parcial."""
        if condiciones.get("estado_actual") != "EN_EJECUCION":
            raise EstadoIncompatible("Solo se puede finalizar una reserva EN_EJECUCION.")
        db = condiciones["db"]
        abiertas = repo.entregas_abiertas_de_reserva(db, reserva.cabecera.id)
        ids_abiertas = {e.reserva_recurso_id for e in abiertas}
        ids_enviados = {r["reserva_recurso_id"] for r in datos["recursos"]}
        if ids_enviados != ids_abiertas:
            raise EstadoIncompatible("Debe registrarse la devolución de exactamente los recursos con entrega abierta.")

    def cambios_finalizar(self, reserva, datos: dict, condiciones: dict) -> dict:
        return {"devoluciones": datos["recursos"]}
