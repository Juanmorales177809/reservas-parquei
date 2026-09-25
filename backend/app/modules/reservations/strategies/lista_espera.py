"""ListaEsperaStrategy: viabilidad explícita, formulario habilitado tras
viabilidad y partes por actor (RN-TIP-PLE). No asigna recursos, no ocupa
franjas y no registra entrega física; la gestión del archivo la hace el
caso de uso, esta estrategia solo decide su admisibilidad.
"""

from __future__ import annotations

import math

from app.core.errors import Conflicto, EstadoIncompatible, Validacion
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

    # --- §4.1 Recepción y aprobación conjunta (API-14) ----------------------------------

    def validar_aprobar(self, reserva, datos: dict, condiciones: dict) -> None:
        """RN-TIP-PLE-05: exige confirmación expresa de recepción, viabilidad
        positiva, parte del reservista y parte técnica con revisión vigente."""
        if datos.get("material_recibido") is not True:
            raise Validacion("material_recibido debe ser true para aprobar una lista de espera.")
        if condiciones.get("viable") is not True:
            raise Conflicto("La reserva no tiene viabilidad positiva registrada.")
        formulario = condiciones.get("formulario")
        if formulario is None or not formulario.datos_usuario:
            raise Conflicto("Falta la parte del reservista del formulario.")
        if not formulario.datos_tecnico or formulario.revisado_at is None:
            raise Conflicto("Falta la parte técnica del formulario con revisión vigente.")

    # --- §6.1 Inicio de fabricación/prestación (API-14) ---------------------------------

    def validar_ejecutar(self, reserva, datos: dict, condiciones: dict) -> None:
        """RN-TIP-PLE-07: sin entrega física ni recursos."""
        if condiciones.get("estado_actual") != "APROBADA":
            raise EstadoIncompatible("Solo se puede iniciar fabricación/prestación desde APROBADA.")

    def cambios_ejecutar(self, reserva, datos: dict, condiciones: dict) -> dict:
        return {}

    # --- §6.2 Finalización con horas (API-14) --------------------------------------------

    def validar_finalizar(self, reserva, datos: dict, condiciones: dict) -> None:
        """RN-TIP-PLE-08: horas finitas y no negativas; sin devoluciones."""
        if condiciones.get("estado_actual") != "EN_EJECUCION":
            raise EstadoIncompatible("Solo se puede finalizar desde EN_EJECUCION.")
        horas = datos.get("horas_ejecucion")
        if horas is None or isinstance(horas, bool) or not isinstance(horas, (int, float)) or not math.isfinite(horas) or horas < 0:
            raise Validacion("horas_ejecucion debe ser un número finito mayor o igual a cero.")

    def cambios_finalizar(self, reserva, datos: dict, condiciones: dict) -> dict:
        return {}
