from typing import Literal

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload

from app.db import get_db
from app.deps import require_admin
from app.models import ControlCambio, Personal
from app.schemas.control_cambio import ControlCambioResponse
from app.services.exportar_archivo import respuesta_streaming
from app.services.exportar_reservas import construir_csv_control_cambios, construir_xlsx_control_cambios


router = APIRouter(prefix="/admin/control-cambios", tags=["control-cambios"])


def _listar(db: Session, limit: int) -> list[ControlCambioResponse]:
    cambios = (
        db.query(ControlCambio)
        .options(joinedload(ControlCambio.usuario), joinedload(ControlCambio.personal))
        .order_by(ControlCambio.created_at.desc(), ControlCambio.id.desc())
        .limit(limit)
        .all()
    )
    return [
        ControlCambioResponse(
            id=cambio.id,
            usuario_id=cambio.usuario_id,
            usuario=cambio.actor.username if cambio.actor else "Sistema",
            accion=cambio.accion,
            entidad=cambio.entidad,
            entidad_id=cambio.entidad_id,
            descripcion=cambio.descripcion,
            created_at=cambio.created_at,
        )
        for cambio in cambios
    ]


@router.get("", response_model=list[ControlCambioResponse])
def listar_control_cambios(
    limit: int = Query(default=200, ge=1, le=500),
    _: Personal = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return _listar(db, limit)


@router.get("/export")
def exportar_control_cambios_endpoint(
    formato: Literal["csv", "xlsx"] = Query(...),
    limit: int = Query(default=200, ge=1, le=500),
    _: Personal = Depends(require_admin),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    cambios = _listar(db, limit)
    contenido = construir_csv_control_cambios(cambios) if formato == "csv" else construir_xlsx_control_cambios(cambios)
    return respuesta_streaming(contenido, formato, "auditoria")
