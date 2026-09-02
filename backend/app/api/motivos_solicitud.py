from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.motivos_solicitud import listar_motivos_por_laboratorio
from app.db import get_db
from app.deps import get_current_user
from app.models import Personal, Usuario
from app.schemas.motivo_solicitud import MotivoSolicitudResponse

router = APIRouter(prefix="/motivos-solicitud", tags=["motivos-solicitud"])


@router.get("", response_model=list[MotivoSolicitudResponse])
def listar_motivos(
    laboratorio_id: int,
    db: Session = Depends(get_db),
    current_user: Personal | Usuario = Depends(get_current_user),
):
    if laboratorio_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="laboratorio_id es requerido")
    return listar_motivos_por_laboratorio(db, laboratorio_id)
