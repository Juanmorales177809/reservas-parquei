"""PropuestasPolicy: admisibilidad por tipo/estado y bloqueo por FGL de la
negociación de periodo (RN-PROP-01, RN-PROP-05, RN-PROP-07). La contraparte
autorizada para aceptar/rechazar se resuelve en el servicio, porque depende
de `acceso_policy`/`exigir_permiso` según el `origen` de la propuesta.
"""

from __future__ import annotations

from app.core.errors import EstadoIncompatible, TipoNoAdmitido

_TIPOS_CON_PROPUESTA = ("ESPACIO", "RECURSO_INTERNO", "RECURSO_CAMPUS", "RECURSO_EXTERNO")
_TIPOS_CON_PRESTAMO_FISICO = ("RECURSO_CAMPUS", "RECURSO_EXTERNO")


def validar_tipo_admite_propuesta(tipo_codigo: str) -> None:
    if tipo_codigo not in _TIPOS_CON_PROPUESTA:
        raise TipoNoAdmitido("LISTA_ESPERA no admite propuestas de periodo.")


def validar_estado_negociable(estado_codigo: str) -> None:
    if estado_codigo not in ("SOLICITADA", "APROBADA"):
        raise EstadoIncompatible("La negociación de periodo solo aplica en SOLICITADA o APROBADA.")


def validar_sin_fgl(tipo_codigo: str, orden_existente: bool) -> None:
    """RN-PROP-01/RN-PROP-05: en campus/externo, una FGL 030 ya generada
    impide proponer, contraproponer o aceptar cambios de periodo, incluso
    para una propuesta creada antes de aprobar."""
    if tipo_codigo in _TIPOS_CON_PRESTAMO_FISICO and orden_existente:
        raise EstadoIncompatible("La orden de salida ya fue generada; no se admiten cambios de periodo.")
