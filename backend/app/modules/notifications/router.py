"""Router de notifications (API-17): `/api/notificaciones`.

Sin permiso administrativo: todo opera sobre la cuenta de la sesión
(contrato §1). La generación de notificaciones no se expone (API-18).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from app.core.deps import ContextoAutenticado, obtener_contexto
from app.core.errors import SolicitudInvalida
from app.core.pagination import envolver_catalogo, envolver_listado, paginacion_para
from app.core.security import exigir_csrf
from app.db.session import get_db
from app.modules.notifications import schemas, service

router = APIRouter(prefix="/api/notificaciones", tags=["notificaciones"])

_FILTROS_BANDEJA = frozenset({"leida", "tipo_evento"})
_ORDENES_BANDEJA = frozenset({"created_at"})


def _leida(request: Request) -> bool | None:
    v = request.query_params.get("leida")
    if v is None:
        return None
    if v == "true":
        return True
    if v == "false":
        return False
    raise SolicitudInvalida("'leida' admite 'true' o 'false'.")


@router.get("", response_model=dict)
def bandeja(
    request: Request,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
    pag=Depends(paginacion_para(filtros_admitidos=_FILTROS_BANDEJA, ordenes_admitidos=_ORDENES_BANDEJA)),
) -> dict:
    """§2.1. Solo propias; consultar no modifica nada."""
    datos, total = service.listar_notificaciones(
        db, {"leida": _leida(request), "tipo_evento": request.query_params.get("tipo_evento")},
        pag.pagina, pag.tamano, contexto,
    )
    return envolver_listado(
        [schemas.NotificacionItem(**d).model_dump(mode="json") for d in datos],
        pagina=pag.pagina, tamano=pag.tamano, total=total,
    )


@router.post("/{id_notificacion}/lectura", response_model=schemas.LecturaRespuesta)
def marcar_lectura(
    id_notificacion: int,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.LecturaRespuesta:
    """§2.2. Ajena o inexistente: 404 sin distinguir."""
    return schemas.LecturaRespuesta(**service.marcar_lectura(db, id_notificacion, contexto))


@router.get("/preferencias", response_model=schemas.PreferenciasRespuesta)
def obtener_preferencias(
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
) -> schemas.PreferenciasRespuesta:
    """§3.1."""
    return schemas.PreferenciasRespuesta(**service.obtener_preferencias(db, contexto))


@router.put("/preferencias", response_model=schemas.PreferenciasRespuesta)
def reemplazar_preferencias(
    cuerpo: schemas.PreferenciasCuerpo,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.PreferenciasRespuesta:
    """§3.2. Reemplazo completo."""
    return schemas.PreferenciasRespuesta(**service.reemplazar_preferencias(db, cuerpo, contexto))


@router.get("/tipos-evento", response_model=dict)
def tipos_evento(
    db: Session = Depends(get_db),
    _contexto: ContextoAutenticado = Depends(obtener_contexto),
) -> dict:
    """§3.3. Catálogo cerrado, solo habilitados."""
    return envolver_catalogo(
        [schemas.TipoEventoItem(**t).model_dump(mode="json") for t in service.tipos_evento(db)]
    )
