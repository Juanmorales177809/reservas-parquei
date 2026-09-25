"""EspacioStrategy: creación y edición de reservas por espacio (RN-TIP-PE).

Los complementarios de `ESPACIO` nunca constituyen compromiso físico
(RN-TIP-PE-28): un recurso con compromiso físico vigente se rechaza por
completo, ni siquiera como fila `NO_DISPONIBLE` (RN-TIP-PE-14). Esta
estrategia no reimplementa la exclusión temporal real (garantía de DB-12);
revalida en memoria con los mismos datos que la restricción de base
protegerá de todas formas.
"""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from app.core.errors import CapacidadExcedida, Conflicto, NoEncontrado, Validacion
from app.modules.espacios import repository as esp_repo
from app.modules.reservations import repository as repo
from app.modules.reservations.policies import disponibilidad as disp_policy
from app.modules.reservations.policies import horario as horario_policy
from app.modules.reservations.strategies.reservation_strategy import ReservationStrategy
from app.modules.resources import repository as rec_repo


_ZONA_OPERATIVA = ZoneInfo("America/Bogota")


def _periodo_utc(fecha, hora_inicio, hora_fin):
    """`fecha`/`hora_inicio`/`hora_fin` son hora local de la unidad (DB-11);
    se etiquetan con esa zona, no con la de `ahora`, para no mezclar UTC con
    hora local al construir el periodo comparado."""
    inicio = datetime.combine(fecha, hora_inicio, tzinfo=_ZONA_OPERATIVA)
    fin = datetime.combine(fecha, hora_fin, tzinfo=_ZONA_OPERATIVA)
    return inicio, fin


class EspacioStrategy(ReservationStrategy):
    codigo = "ESPACIO"

    def validar_crear(self, reserva, datos: dict, condiciones: dict) -> None:
        db = condiciones["db"]
        detalle = datos["detalle"]
        for campo in ("espacio_id", "fecha", "hora_inicio", "hora_fin"):
            if detalle.get(campo) is None:
                raise Validacion(f"detalle.{campo} es obligatorio.")

        espacio = esp_repo.obtener_espacio(db, detalle["espacio_id"])
        if espacio is None or not espacio.habilitado:
            raise NoEncontrado("El espacio no existe o no está habilitado.")
        if espacio.id_unidad != datos["id_unidad"]:
            raise Validacion("El espacio no pertenece a la unidad receptora.")

        horario_policy.validar_franja(
            fecha=detalle["fecha"], hora_inicio=detalle["hora_inicio"], hora_fin=detalle["hora_fin"],
            config=condiciones["config"], ahora=condiciones["ahora"],
        )
        horario_policy.validar_antelacion(
            fecha=detalle["fecha"], hora_inicio=detalle["hora_inicio"],
            config=condiciones["config"], ahora=condiciones["ahora"],
        )

        asistentes = detalle.get("asistentes") or 0
        acompanantes = datos.get("acompanantes") or []
        if asistentes != len(acompanantes):
            raise Validacion("detalle.asistentes debe coincidir con la cantidad de acompanantes.")
        if asistentes > espacio.capacidad:
            raise CapacidadExcedida()

        inicio, fin = _periodo_utc(detalle["fecha"], detalle["hora_inicio"], detalle["hora_fin"])
        solapa = repo.existe_solapamiento_espacio(db, detalle["espacio_id"], inicio, fin, excluir_reserva_id=condiciones.get("excluir_reserva_id"))
        disp_policy.exigir_sin_solapamiento(solapa)

        for r in datos.get("recursos") or []:
            if r["rol"] != "ADICIONAL":
                raise Validacion("En ESPACIO, los recursos solo admiten rol ADICIONAL.")
            recurso = rec_repo.obtener_recurso(db, r["recurso_id"])
            if recurso is None or not recurso.habilitado:
                raise NoEncontrado(f"El recurso {r['recurso_id']} no existe o no está habilitado.")
            if repo.tiene_compromiso_fisico_vigente(db, r["recurso_id"]):
                raise Conflicto(f"El recurso {r['recurso_id']} tiene un compromiso físico vigente y no puede incluirse.")

        campos_espacio = {c.id: c for c in esp_repo.campos_del_espacio(db, detalle["espacio_id"]) if c.habilitado}
        enviados = {c["campo_id"]: c for c in datos.get("campos_adicionales") or []}
        for campo_id, campo in campos_espacio.items():
            if campo.obligatorio and campo_id not in enviados:
                raise Validacion(f"El campo '{campo.nombre}' es obligatorio.")
        for campo_id in enviados:
            if campo_id not in campos_espacio:
                raise Validacion(f"El campo {campo_id} no pertenece a este espacio.")

    def cambios_crear(self, reserva, datos: dict, condiciones: dict) -> dict:
        detalle = datos["detalle"]
        recursos = [{"recurso_id": r["recurso_id"], "rol": "ADICIONAL"} for r in datos.get("recursos") or []]
        return {
            "detalle_espacio": {
                "espacio_id": detalle["espacio_id"], "fecha": detalle["fecha"],
                "hora_inicio": detalle["hora_inicio"], "hora_fin": detalle["hora_fin"],
                "asistentes": detalle.get("asistentes") or 0,
            },
            "recursos": recursos,
        }

    def validar_editar(self, reserva, datos: dict, condiciones: dict) -> None:
        # Misma validación que crear, sobre los valores resultantes tras la fusión.
        self.validar_crear(reserva, datos, condiciones)

    def cambios_editar(self, reserva, datos: dict, condiciones: dict) -> dict:
        return self.cambios_crear(reserva, datos, condiciones)
