from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.tipos_reserva import create_tipo_reserva, get_tipo_reserva, update_tipo_reserva
from app.db import get_db
from app.deps import get_current_user_optional, get_managed_laboratory_id, require_resource_manager
from app.domain.enums import Rol
from app.models import Laboratorio, Personal, Reserva, Usuario
from app.models.tipo_reserva import TipoReserva
from app.schemas.tipo_reserva import TipoReservaCreate, TipoReservaResponse, TipoReservaUpdate

router = APIRouter(prefix="/tipos-reserva", tags=["tipos-reserva"])


@router.get("", response_model=list[TipoReservaResponse])
def listar_tipos_reserva(
    laboratorio_id: int | None = None,
    db: Session = Depends(get_db),
    usuario: Usuario | None = Depends(get_current_user_optional),
):
    """Listar tipos de reserva. No requiere autenticacion (mismo criterio
    RN-005 que GET /laboratorios y GET /espacios): anonimo/usuario solo ven
    tipos activos; gestor/admin ven todos, para poder gestionarlos."""
    query = db.query(TipoReserva)
    if laboratorio_id is not None:
        query = query.filter(TipoReserva.laboratorio_id == laboratorio_id)
    if usuario is None or usuario.rol == Rol.USUARIO.value:
        query = query.filter(TipoReserva.estado == "activo")
    return query.order_by(TipoReserva.nombre.asc()).all()


@router.post("", response_model=TipoReservaResponse, status_code=status.HTTP_201_CREATED)
def crear_tipo_reserva(
    payload: TipoReservaCreate,
    current_user: Personal = Depends(require_resource_manager),
    db: Session = Depends(get_db),
):
    laboratorio_gestionado = get_managed_laboratory_id(db, current_user)
    if laboratorio_gestionado is not None and payload.laboratorio_id != laboratorio_gestionado:
        raise HTTPException(status_code=403, detail="Solo puedes gestionar tipos de reserva de tu laboratorio")
    if db.query(Laboratorio).filter(Laboratorio.id == payload.laboratorio_id).first() is None:
        raise HTTPException(status_code=404, detail="Laboratorio no encontrado")
    return create_tipo_reserva(db, payload, current_user.id)


@router.put("/{tipo_reserva_id}", response_model=TipoReservaResponse)
def actualizar_tipo_reserva(
    tipo_reserva_id: int,
    payload: TipoReservaUpdate,
    current_user: Personal = Depends(require_resource_manager),
    db: Session = Depends(get_db),
):
    tipo_reserva = get_tipo_reserva(db, tipo_reserva_id)
    if tipo_reserva is None:
        raise HTTPException(status_code=404, detail="Tipo de reserva no encontrado")
    laboratorio_gestionado = get_managed_laboratory_id(db, current_user)
    if laboratorio_gestionado is not None and tipo_reserva.laboratorio_id != laboratorio_gestionado:
        raise HTTPException(status_code=403, detail="Solo puedes gestionar tipos de reserva de tu laboratorio")

    cambios = payload.model_dump(exclude_unset=True)
    return update_tipo_reserva(db, tipo_reserva, cambios, current_user.id)


@router.delete("/{tipo_reserva_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_tipo_reserva(
    tipo_reserva_id: int,
    current_user: Personal = Depends(require_resource_manager),
    db: Session = Depends(get_db),
):
    tipo_reserva = get_tipo_reserva(db, tipo_reserva_id)
    if tipo_reserva is None:
        raise HTTPException(status_code=404, detail="Tipo de reserva no encontrado")
    laboratorio_gestionado = get_managed_laboratory_id(db, current_user)
    if laboratorio_gestionado is not None and tipo_reserva.laboratorio_id != laboratorio_gestionado:
        raise HTTPException(status_code=403, detail="Solo puedes gestionar tipos de reserva de tu laboratorio")
    if db.query(Reserva).filter(Reserva.tipo_reserva_id == tipo_reserva_id).first() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar un tipo de reserva en uso",
        )
    db.delete(tipo_reserva)
    db.commit()
    return None
