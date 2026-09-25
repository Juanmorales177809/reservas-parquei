"""ContextoPolicy: contexto obligatorio y combinaciones válidas por tipo de
cuenta (RN-CTX-01 a RN-CTX-04, RN-CTX-08). La existencia y vigencia de cada
elemento (proyecto/semillero/pasantía/trabajo de grado/actividad) la
resuelve el servicio contra `researchs.repository`, porque requiere acceso
a datos que esta política no ejecuta.
"""

from __future__ import annotations

from app.core.errors import Validacion

_CAMPOS_ACADEMICOS = ("proyecto_id", "semillero_id", "pasantia_id", "trabajo_grado_id")


def validar_composicion(contexto: dict) -> None:
    """RN-CTX-01/02/03/04: al menos un elemento; una actividad institucional
    no coexiste con los académicos."""
    tiene_academico = any(contexto.get(c) is not None for c in _CAMPOS_ACADEMICOS)
    tiene_actividad = contexto.get("actividad_institucional_id") is not None
    if not tiene_academico and not tiene_actividad:
        raise Validacion("contexto es obligatorio: incluya al menos un elemento académico o una actividad institucional.")
    if tiene_academico and tiene_actividad:
        raise Validacion("Una actividad institucional no puede combinarse con proyecto, semillero, pasantía o trabajo de grado.")


def validar_para_personal(contexto: dict) -> None:
    """RN-CTX-08: PERSONAL solo proyecto/semillero del catálogo general."""
    if contexto.get("pasantia_id") or contexto.get("trabajo_grado_id") or contexto.get("actividad_institucional_id"):
        raise Validacion("Una cuenta PERSONAL solo puede usar proyecto o semillero como contexto.")
    if not contexto.get("proyecto_id") and not contexto.get("semillero_id"):
        raise Validacion("Una cuenta PERSONAL debe seleccionar al menos un proyecto o semillero.")
