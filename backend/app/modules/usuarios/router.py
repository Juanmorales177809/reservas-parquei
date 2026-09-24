"""Router de perfil propio (API-06 §2.1, §2.2).

Sin permiso administrativo: opera sobre la identidad de la sesión.
`§2.3`, `§3` y `§4` quedan para API-11 (researchs).
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import ContextoAutenticado, obtener_contexto
from app.core.security import exigir_csrf
from app.db.session import get_db
from app.modules.usuarios import schemas, service

router = APIRouter(prefix="/api/perfil", tags=["perfil"])


@router.get("", response_model=schemas.PerfilRespuesta)
def leer_perfil(
    db: Session = Depends(get_db),
    contexto: ContextoAutenticado = Depends(obtener_contexto),
) -> schemas.PerfilRespuesta:
    """§2.1. El correo se devuelve como solo lectura. PERSONAL → 404."""
    return schemas.PerfilRespuesta(**service.obtener_perfil(db, contexto))


@router.patch("", response_model=schemas.PerfilRespuesta)
def editar_perfil(
    cuerpo: schemas.PerfilActualizar,
    contexto: ContextoAutenticado = Depends(obtener_contexto),
    db: Session = Depends(get_db),
    _csrf: None = Depends(exigir_csrf),
) -> schemas.PerfilRespuesta:
    """§2.2. Cinco campos editables; el correo se rechaza con 409."""
    return schemas.PerfilRespuesta(**service.actualizar_perfil(db, contexto, cuerpo))
