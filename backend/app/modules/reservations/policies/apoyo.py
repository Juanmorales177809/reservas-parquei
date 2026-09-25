"""ApoyoPolicy: derivación del apoyo obligatorio y la solicitud voluntaria
(RN-RES-09, RN-RES-10)."""

from __future__ import annotations


def apoyo_efectivo(solicitado: bool, requiere_por_algun_equipo: bool) -> bool:
    """Un equipo con `requiere_apoyo = true` fuerza el apoyo, sin importar lo
    solicitado; el Usuario nunca puede desmarcarlo (RN-RES-09). Si ninguno lo
    exige, se persiste la solicitud voluntaria tal cual (RN-RES-10)."""
    return True if requiere_por_algun_equipo else solicitado


def algun_recurso_requiere_apoyo(db, recurso_ids: list[int]) -> bool:
    """Aplica a cualquier tipo con recursos: complementarios de ESPACIO,
    RECURSO_INTERNO, RECURSO_CAMPUS y RECURSO_EXTERNO (RN-RES-09)."""
    from app.modules.resources import repository as rec_repo

    for recurso_id in recurso_ids:
        recurso = rec_repo.obtener_recurso(db, recurso_id)
        if recurso is None or recurso.tipo != "EQUIPO":
            continue
        equipo = rec_repo.obtener_especializacion(db, "EQUIPO", recurso_id)
        if equipo is not None and equipo.requiere_apoyo:
            return True
    return False
