"""Router de auditoría administrativa (API-08 §5.1).

Solo lectura: no existe ningún endpoint de escritura sobre la auditoría
(RN-AUD-05). Los registros los genera el sistema en cada operación.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import ContextoAutenticado, exigir_permiso_dep
from app.core.pagination import envolver_listado, paginacion_para
from app.db.session import get_db
from app.modules.administration import schemas, service

_PERMISO = exigir_permiso_dep("unidades.administrar")
_PAG = paginacion_para(
    filtros_admitidos=frozenset(
        {"entidad", "entidad_id", "actor_cuenta_id", "accion", "desde", "hasta"}
    ),
    ordenes_admitidos=frozenset({"created_at"}),
)

router = APIRouter(prefix="/api/auditoria", tags=["auditoria"])


@router.get("", response_model=dict)
def listar_auditoria(
    db: Session = Depends(get_db),
    _permiso: ContextoAutenticado = Depends(_PERMISO),
    paginacion=Depends(_PAG),
    entidad: str | None = None,
    entidad_id: str | None = None,
    actor_cuenta_id: str | None = None,
    accion: str | None = None,
    desde: str | None = None,
    hasta: str | None = None,
) -> dict:
    """§5.1. Actor, acción, entidad, identificador y momento (RN-AUD-02)."""
    datos, total = service.listar_auditoria(
        db, entidad=entidad, entidad_id=entidad_id, actor_cuenta_id=actor_cuenta_id,
        accion=accion, desde=desde, hasta=hasta, paginacion=paginacion,
    )
    return envolver_listado(
        [schemas.AuditoriaRespuesta(**d).model_dump(mode="json") for d in datos],
        pagina=paginacion.pagina, tamano=paginacion.tamano, total=total,
    )
