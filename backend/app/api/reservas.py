import uuid
from typing import Literal

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.crud.reservas import get_mis_reservas, get_reservas_de_serie, get_reservas_gestion
from app.db import get_db
from app.deps import get_current_user, get_managed_space_id, require_resource_manager
from app.models import Personal, Usuario
from app.schemas.reserva import (
    ReservaAsistioUpdate,
    ReservaCreate,
    ReservaEstadoUpdate,
    ReservaResponse,
    ReservaSerieCancelResponse,
    ReservaSerieResponse,
    ReservaUpdate,
)
from app.services.exportar_archivo import respuesta_streaming
from app.services.exportar_reservas import construir_csv_mis_reservas, construir_xlsx_mis_reservas
from app.services.reservas import (
    actualizar_reserva,
    cambiar_estado,
    cancelar_reserva_usuario,
    cancelar_serie,
    crear_reserva,
    crear_reserva_serie,
    eliminar_reserva,
    marcar_asistencia,
)


router = APIRouter(prefix="/reservas", tags=["reservas"])


@router.post("", response_model=ReservaResponse | ReservaSerieResponse, status_code=201)
def crear_reserva_endpoint(
    data: ReservaCreate,
    db: Session = Depends(get_db),
    current_user: Personal | Usuario = Depends(get_current_user),
):
    if data.repetir_semanas is None:
        return crear_reserva(db, data, current_user)
    creadas, omitidas = crear_reserva_serie(db, data, current_user)
    return ReservaSerieResponse(creadas=creadas, omitidas=omitidas)


@router.get("", response_model=list[ReservaResponse])
def listar_reservas_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin_user: Personal = Depends(require_resource_manager),
):
    espacio_id = get_managed_space_id(db, admin_user)
    return get_reservas_gestion(db, espacio_id, skip, limit)


@router.get("/mis-reservas", response_model=list[ReservaResponse])
def listar_mis_reservas_endpoint(
    db: Session = Depends(get_db),
    current_user: Personal | Usuario = Depends(get_current_user),
):
    return get_mis_reservas(db, current_user)


@router.get("/mis-reservas/export")
def exportar_mis_reservas_endpoint(
    formato: Literal["csv", "xlsx"] = Query(...),
    db: Session = Depends(get_db),
    current_user: Personal | Usuario = Depends(get_current_user),
) -> StreamingResponse:
    reservas = get_mis_reservas(db, current_user)
    contenido = construir_csv_mis_reservas(reservas) if formato == "csv" else construir_xlsx_mis_reservas(reservas)
    return respuesta_streaming(contenido, formato, "mis_reservas")


@router.get("/serie/{serie_id}", response_model=list[ReservaResponse])
def listar_serie_endpoint(
    serie_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: Personal | Usuario = Depends(get_current_user),
):
    return get_reservas_de_serie(db, serie_id, current_user)


@router.put("/serie/{serie_id}/cancelar", response_model=ReservaSerieCancelResponse)
def cancelar_serie_endpoint(
    serie_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: Personal | Usuario = Depends(get_current_user),
):
    canceladas, omitidas = cancelar_serie(db, serie_id, current_user)
    return ReservaSerieCancelResponse(canceladas=canceladas, omitidas=omitidas)


@router.put("/{reserva_id}/asistio", response_model=ReservaResponse)
def marcar_asistencia_endpoint(
    reserva_id: int,
    data: ReservaAsistioUpdate,
    db: Session = Depends(get_db),
    admin_user: Personal = Depends(require_resource_manager),
):
    return marcar_asistencia(db, reserva_id, data.asistio, admin_user)


@router.put("/{reserva_id}/estado", response_model=ReservaResponse)
def cambiar_estado_endpoint(
    reserva_id: int,
    data: ReservaEstadoUpdate,
    db: Session = Depends(get_db),
    admin_user: Personal = Depends(require_resource_manager),
):
    return cambiar_estado(db, reserva_id, data.nuevo_estado, admin_user, motivo=data.motivo)


@router.patch("/{reserva_id}", response_model=ReservaResponse)
def actualizar_reserva_endpoint(
    reserva_id: int,
    data: ReservaUpdate,
    db: Session = Depends(get_db),
    current_user: Personal | Usuario = Depends(get_current_user),
):
    return actualizar_reserva(db, reserva_id, data, current_user)


@router.put("/{reserva_id}/cancelar", response_model=ReservaResponse)
def cancelar_reserva_usuario_endpoint(
    reserva_id: int,
    db: Session = Depends(get_db),
    current_user: Personal | Usuario = Depends(get_current_user),
):
    return cancelar_reserva_usuario(db, reserva_id, current_user)


@router.delete("/{reserva_id}", status_code=204)
def eliminar_reserva_endpoint(
    reserva_id: int,
    db: Session = Depends(get_db),
    current_user: Personal | Usuario = Depends(get_current_user),
):
    eliminar_reserva(db, reserva_id, current_user)
    return None
