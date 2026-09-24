"""Router de asignación de permisos (API-07 §3).

Todo exige `permisos.asignar` global. Administration administra las
asignaciones; auth las evalúa en cada operación (RN-PER-01).
"""

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.core.deps import ContextoAutenticado, exigir_permiso_dep
from app.core.security import exigir_csrf
from app.db.session import get_db
from app.modules.administration import schemas, service

_PERMISO = exigir_permiso_dep("permisos.asignar")

router = APIRouter(prefix="/api/permisos", tags=["permisos"])


@router.get("", response_model=dict)
def catalogo(
    db: Session = Depends(get_db),
    _permiso: ContextoAutenticado = Depends(_PERMISO),
) -> dict:
    """§3.1. Catálogo cerrado: solo datos, sin paginación."""
    return {"datos": [schemas.PermisoResumen(**p).model_dump(mode="json") for p in service.catalogo_permisos(db)]}


@router.get("/cuentas/{id_cuenta}", response_model=list[schemas.AsignacionRespuesta])
def asignaciones(
    id_cuenta: int,
    db: Session = Depends(get_db),
    _permiso: ContextoAutenticado = Depends(_PERMISO),
) -> list[schemas.AsignacionRespuesta]:
    """§3.2. Asignaciones vigentes de una cuenta, con su ámbito."""
    return [schemas.AsignacionRespuesta(**a) for a in service.asignaciones_de_cuenta(db, id_cuenta)]


@router.post("/cuentas/{id_cuenta}", status_code=201, response_model=schemas.AsignacionRespuesta)
def otorgar(
    id_cuenta: int,
    cuerpo: schemas.PermisoOtorgar,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(_PERMISO),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.AsignacionRespuesta:
    """§3.3. USUARIO → 422; unidad ajena al cargo → 422; duplicado → 409."""
    return schemas.AsignacionRespuesta(**service.otorgar_permiso(db, id_cuenta, cuerpo, contexto))


@router.delete("/cuentas/{id_cuenta}/{codigo}", status_code=204)
def retirar(
    id_cuenta: int,
    codigo: str,
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(_PERMISO),
    _csrf: None = Depends(exigir_csrf),
) -> Response:
    """§3.4. Retira todas las asignaciones del código; rige lo posterior (RN-PER-04)."""
    service.retirar_permiso(db, id_cuenta, codigo, contexto)
    return Response(status_code=204)
