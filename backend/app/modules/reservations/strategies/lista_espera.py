"""ListaEsperaStrategy: viabilidad explícita, formulario habilitado tras
viabilidad y partes por actor (RN-TIP-PLE). No asigna recursos, no ocupa
franjas y no registra entrega física; la gestión del archivo la hace el
caso de uso, esta estrategia solo decide su admisibilidad.
"""

from __future__ import annotations

from app.core.errors import Conflicto, Validacion
from app.modules.reservations.strategies.reservation_strategy import ReservationStrategy


class ListaEsperaStrategy(ReservationStrategy):
    codigo = "LISTA_ESPERA"

    def validar_crear(self, reserva, datos: dict, condiciones: dict) -> None:
        detalle = datos["detalle"]
        if not (detalle.get("descripcion_necesidad") or "").strip():
            raise Validacion("detalle.descripcion_necesidad es obligatorio.")
        if datos.get("recursos"):
            raise Validacion("LISTA_ESPERA no admite recursos.")
        if datos.get("acompanantes"):
            raise Validacion("LISTA_ESPERA no admite acompañantes.")

    def cambios_crear(self, reserva, datos: dict, condiciones: dict) -> dict:
        return {"detalle_lista_espera": {"descripcion_necesidad": datos["detalle"]["descripcion_necesidad"]}}

    def validar_editar(self, reserva, datos: dict, condiciones: dict) -> None:
        detalle = datos.get("detalle") or {}
        if "descripcion_necesidad" in detalle and not (detalle["descripcion_necesidad"] or "").strip():
            raise Validacion("detalle.descripcion_necesidad no puede quedar vacío.")
        if datos.get("recursos") is not None or datos.get("acompanantes") is not None:
            raise Validacion("LISTA_ESPERA no admite recursos ni acompañantes.")

    def cambios_editar(self, reserva, datos: dict, condiciones: dict) -> dict:
        detalle = datos.get("detalle") or {}
        cambios = {}
        if "descripcion_necesidad" in detalle:
            cambios["descripcion_necesidad"] = detalle["descripcion_necesidad"]
        return {"detalle_lista_espera": cambios}

    # --- §2.3 Formulario ---------------------------------------------------------------

    def validar_lista_espera_formulario(self, reserva, datos: dict, condiciones: dict) -> None:
        if not condiciones.get("viable"):
            raise Conflicto("La reserva no tiene viabilidad positiva registrada.")
        parte = datos["parte"]
        if parte == "tecnica" and not condiciones.get("formulario_reservista_existente"):
            raise Conflicto("El Técnico no puede completar su parte sin la del reservista.")

    def cambios_lista_espera_formulario(self, reserva, datos: dict, condiciones: dict) -> dict:
        return {"parte": datos["parte"], "valor": datos["valor"]}

    # --- §2.4 Viabilidad -----------------------------------------------------------------

    def validar_lista_espera_viabilidad(self, reserva, datos: dict, condiciones: dict) -> None:
        if datos["viable"] is False and not (datos.get("motivo") or "").strip():
            raise Validacion("motivo es obligatorio cuando viable es false.")

    def cambios_lista_espera_viabilidad(self, reserva, datos: dict, condiciones: dict) -> dict:
        return {"viable": datos["viable"], "motivo": datos.get("motivo")}
