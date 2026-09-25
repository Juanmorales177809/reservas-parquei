"""AccesoPolicy: propiedad, ámbito, cuenta y unidad (RN-RES-02, RN-RES-11,
RN-RES-15, RN-PRO-02, RN-PRO-06). El servicio resuelve los datos (rol,
unidad del cargo, vinculación mínima) y esta política decide.
"""

from __future__ import annotations

from app.core.deps import ContextoAutenticado
from app.core.errors import EstadoIncompatible, NoAutorizado


def validar_unidad_receptora(contexto: ContextoAutenticado, id_unidad: int, unidad_del_cargo: int | None) -> None:
    """RN-RES-15: una cuenta PERSONAL solo reserva en la unidad de su cargo
    vigente, sin importar su alcance administrativo."""
    if contexto.tipo_cuenta == "PERSONAL" and id_unidad != unidad_del_cargo:
        raise NoAutorizado("Una cuenta PERSONAL solo puede reservar en la unidad de su cargo vigente.")


def validar_propietario(contexto: ContextoAutenticado, id_cuenta_reserva: int) -> None:
    """RN-PRO-02: la edición directa en SOLICITADA es solo del reservista propietario."""
    if contexto.id_cuenta != id_cuenta_reserva:
        raise NoAutorizado("Solo el reservista propietario puede editar directamente esta reserva.")


def validar_ambito_lectura(contexto: ContextoAutenticado, id_cuenta_reserva: int, id_unidad_reserva: int) -> bool:
    """RN-PRO-01/03/04: Usuario/Personal sin permiso solo ve lo propio;
    Técnico ve su unidad; Administrador ve cualquiera. Devuelve si el actor
    tiene acceso; no exige un permiso administrativo por sí sola."""
    if contexto.id_cuenta == id_cuenta_reserva:
        return True
    if contexto.rol == "ADMINISTRADOR":
        return True
    if contexto.rol == "TECNICO" and contexto.unidades_autorizadas != "GLOBAL":
        return id_unidad_reserva in contexto.unidades_autorizadas
    return False


def exigir_solicitada(estado_codigo: str) -> None:
    if estado_codigo != "SOLICITADA":
        raise EstadoIncompatible("La operación solo aplica mientras la reserva esté SOLICITADA.")
