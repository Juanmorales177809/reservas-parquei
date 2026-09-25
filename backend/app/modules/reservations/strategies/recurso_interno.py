"""RecursoInternoStrategy: creación y edición de reservas de recurso interno
(RN-TIP-RI). Sin entrega/devolución física ni compromiso físico exclusivo:
admite franjas sucesivas no solapadas (RN-TIP-RI-03/13). Un compromiso
físico ajeno de campus/externo sigue impidiendo incluir el recurso.
"""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from app.core.errors import Conflicto, NoEncontrado, Validacion
from app.modules.reservations import repository as repo
from app.modules.reservations.policies import disponibilidad as disp_policy
from app.modules.reservations.policies import horario as horario_policy
from app.modules.reservations.strategies.reservation_strategy import ReservationStrategy
from app.modules.resources import repository as rec_repo


_ZONA_OPERATIVA = ZoneInfo("America/Bogota")


def _periodo_utc(fecha, hora_inicio, hora_fin):
    inicio = datetime.combine(fecha, hora_inicio, tzinfo=_ZONA_OPERATIVA)
    fin = datetime.combine(fecha, hora_fin, tzinfo=_ZONA_OPERATIVA)
    return inicio, fin


class RecursoInternoStrategy(ReservationStrategy):
    codigo = "RECURSO_INTERNO"

    def validar_crear(self, reserva, datos: dict, condiciones: dict) -> None:
        db = condiciones["db"]
        detalle = datos["detalle"]
        for campo in ("fecha", "hora_inicio", "hora_fin"):
            if detalle.get(campo) is None:
                raise Validacion(f"detalle.{campo} es obligatorio.")

        horario_policy.validar_franja(
            fecha=detalle["fecha"], hora_inicio=detalle["hora_inicio"], hora_fin=detalle["hora_fin"],
            config=condiciones["config"], ahora=condiciones["ahora"],
        )
        horario_policy.validar_antelacion(
            fecha=detalle["fecha"], hora_inicio=detalle["hora_inicio"],
            config=condiciones["config"], ahora=condiciones["ahora"],
        )

        recursos = datos.get("recursos") or []
        principales = [r for r in recursos if r["rol"] == "PRINCIPAL"]
        if len(principales) != 1:
            raise Validacion("RECURSO_INTERNO exige exactamente un recurso PRINCIPAL.")

        inicio, fin = _periodo_utc(detalle["fecha"], detalle["hora_inicio"], detalle["hora_fin"])
        for r in recursos:
            recurso = rec_repo.obtener_recurso(db, r["recurso_id"])
            if recurso is None or not recurso.habilitado:
                raise NoEncontrado(f"El recurso {r['recurso_id']} no existe o no está habilitado.")
            if recurso.tipo == "EQUIPO":
                equipo = rec_repo.obtener_especializacion(db, "EQUIPO", r["recurso_id"])
                if equipo is not None and equipo.estado is False:
                    raise Conflicto(f"El recurso {r['recurso_id']} no está operativo.")
            if repo.tiene_compromiso_fisico_vigente(db, r["recurso_id"]):
                raise Conflicto(f"El recurso {r['recurso_id']} tiene un compromiso físico vigente de campus/externo.")
            solapa = repo.existe_solapamiento_recurso_interno(db, r["recurso_id"], inicio, fin, excluir_reserva_id=condiciones.get("excluir_reserva_id"))
            disp_policy.exigir_sin_solapamiento(solapa)

    def cambios_crear(self, reserva, datos: dict, condiciones: dict) -> dict:
        detalle = datos["detalle"]
        recursos = [{"recurso_id": r["recurso_id"], "rol": r["rol"]} for r in datos.get("recursos") or []]
        return {
            "detalle_interno": {"fecha": detalle["fecha"], "hora_inicio": detalle["hora_inicio"], "hora_fin": detalle["hora_fin"]},
            "recursos": recursos,
        }

    def validar_editar(self, reserva, datos: dict, condiciones: dict) -> None:
        self.validar_crear(reserva, datos, condiciones)

    def cambios_editar(self, reserva, datos: dict, condiciones: dict) -> dict:
        return self.cambios_crear(reserva, datos, condiciones)

    # --- §4.1 Aprobación (API-14) -------------------------------------------------------

    def validar_aprobar(self, reserva, datos: dict, condiciones: dict) -> None:
        """RN-APR-06/07: revalida horario y cada recurso, excluyendo el
        propio compromiso; sin exigir antelación (RN-HOR-06)."""
        db = condiciones["db"]
        detalle = datos["detalle"]
        horario_policy.validar_franja(
            fecha=detalle["fecha"], hora_inicio=detalle["hora_inicio"], hora_fin=detalle["hora_fin"],
            config=condiciones["config"], ahora=condiciones["ahora"],
        )
        inicio, fin = _periodo_utc(detalle["fecha"], detalle["hora_inicio"], detalle["hora_fin"])
        for r in datos["recursos"]:
            recurso = rec_repo.obtener_recurso(db, r["recurso_id"])
            if recurso is None or not recurso.habilitado:
                raise NoEncontrado(f"El recurso {r['recurso_id']} no existe o no está habilitado.")
            if recurso.tipo == "EQUIPO":
                equipo = rec_repo.obtener_especializacion(db, "EQUIPO", r["recurso_id"])
                if equipo is not None and equipo.estado is False:
                    raise Conflicto(f"El recurso {r['recurso_id']} no está operativo.")
            if repo.tiene_compromiso_fisico_vigente(db, r["recurso_id"]):
                raise Conflicto(f"El recurso {r['recurso_id']} tiene un compromiso físico vigente de campus/externo.")
            solapa = repo.existe_solapamiento_recurso_interno(db, r["recurso_id"], inicio, fin, excluir_reserva_id=condiciones.get("excluir_reserva_id"))
            disp_policy.exigir_sin_solapamiento(solapa)

    # --- §4.3/§4.4 Recursos adicionales (API-14) ----------------------------------------

    def validar_agregar_recursos(self, reserva, datos: dict, condiciones: dict) -> None:
        """RN-TIP-RI-10/11/12: incorporación permitida solo como ADICIONAL;
        revalida habilitación, operatividad, compromiso ajeno y solapamiento
        desde `incorporado_at` cuando la reserva está EN_EJECUCION."""
        db = condiciones["db"]
        detalle = datos["detalle"]
        inicio, fin = _periodo_utc(detalle["fecha"], detalle["hora_inicio"], detalle["hora_fin"])
        incorporado_at = condiciones.get("incorporado_at")
        if incorporado_at is not None and incorporado_at > inicio:
            inicio = incorporado_at
        for r in datos["recursos"]:
            if r["rol"] != "ADICIONAL":
                raise Validacion("Solo se admite rol ADICIONAL.")
            recurso = rec_repo.obtener_recurso(db, r["recurso_id"])
            if recurso is None or not recurso.habilitado:
                raise NoEncontrado(f"El recurso {r['recurso_id']} no existe o no está habilitado.")
            if recurso.tipo == "EQUIPO":
                equipo = rec_repo.obtener_especializacion(db, "EQUIPO", r["recurso_id"])
                if equipo is not None and equipo.estado is False:
                    raise Conflicto(f"El recurso {r['recurso_id']} no está operativo.")
            if repo.tiene_compromiso_fisico_vigente(db, r["recurso_id"]):
                raise Conflicto(f"El recurso {r['recurso_id']} tiene un compromiso físico vigente de campus/externo.")
            solapa = repo.existe_solapamiento_recurso_interno(db, r["recurso_id"], inicio, fin, excluir_reserva_id=reserva.cabecera.id)
            disp_policy.exigir_sin_solapamiento(solapa)

    def cambios_agregar_recursos(self, reserva, datos: dict, condiciones: dict) -> dict:
        return {"recursos": [{"recurso_id": r["recurso_id"], "rol": "ADICIONAL"} for r in datos["recursos"]]}

    def validar_retirar_recurso(self, reserva, datos: dict, condiciones: dict) -> None:
        """RN-TIP-RI-10: el PRINCIPAL no puede retirarse mediante esta operación."""
        if datos["asignacion"].rol == "PRINCIPAL":
            raise Conflicto("No se puede retirar el recurso PRINCIPAL de RECURSO_INTERNO.")

    def cambios_retirar_recurso(self, reserva, datos: dict, condiciones: dict) -> dict:
        return {}
