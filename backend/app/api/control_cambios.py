from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from app.db import get_db
from app.deps import require_admin
from app.models import ControlCambio, Usuario
from app.schemas.control_cambio import ControlCambioResponse


router = APIRouter(prefix="/admin/control-cambios", tags=["control-cambios"])


@router.get("", response_model=list[ControlCambioResponse])
def listar_control_cambios(
    limit: int = Query(default=200, ge=1, le=500),
    _: Usuario = Depends(require_admin),
    db: Session = Depends(get_db),
):
    cambios = (
        db.query(ControlCambio)
        .options(joinedload(ControlCambio.usuario))
        .order_by(ControlCambio.created_at.desc(), ControlCambio.id.desc())
        .limit(limit)
        .all()
    )
    return [
        ControlCambioResponse(
            id=cambio.id,
            usuario_id=cambio.usuario_id,
            usuario=cambio.usuario.username if cambio.usuario else "Sistema",
            accion=cambio.accion,
            entidad=cambio.entidad,
            entidad_id=cambio.entidad_id,
            descripcion=cambio.descripcion,
            created_at=cambio.created_at,
        )
        for cambio in cambios
    ]
