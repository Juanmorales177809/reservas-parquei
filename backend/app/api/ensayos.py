from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.ensayos import create_ensayo, get_ensayo, update_ensayo
from app.db import get_db
from app.deps import get_current_user_optional, get_managed_space_id, require_resource_manager
from app.domain.enums import Rol
from app.models import Espacio, Usuario
from app.models.ensayo import Ensayo
from app.models.reserva_ensayo import ReservaEnsayo
from app.models.zona import Zona
from app.schemas.ensayo import EnsayoCreate, EnsayoResponse, EnsayoUpdate

router = APIRouter(prefix="/ensayos", tags=["ensayos"])


@router.get("", response_model=list[EnsayoResponse])
def listar_ensayos(
    zona_id: int | None = None,
    db: Session = Depends(get_db),
    usuario: Usuario | None = Depends(get_current_user_optional),
):
    """Listar ensayos. No requiere autenticación (mismo criterio RN-005 que
    GET /zonas): anónimo/usuario solo ven ensayos activos de zonas activas
    de espacios activos; gestor/admin ven todo."""
    query = db.query(Ensayo).join(Zona, Ensayo.zona_id == Zona.id).join(Espacio, Zona.espacio_id == Espacio.id)
    if zona_id is not None:
        query = query.filter(Ensayo.zona_id == zona_id)
    if usuario is None or usuario.rol == Rol.USUARIO.value:
        query = query.filter(Ensayo.estado == "activo", Zona.estado == "activo", Espacio.estado == "activo")
    return query.order_by(Ensayo.nombre.asc()).all()


@router.post("", response_model=EnsayoResponse, status_code=status.HTTP_201_CREATED)
def crear_ensayo_endpoint(
    payload: EnsayoCreate,
    current_user: Usuario = Depends(require_resource_manager),
    db: Session = Depends(get_db),
):
    zona = db.query(Zona).filter(Zona.id == payload.zona_id).first()
    if zona is None:
        raise HTTPException(status_code=404, detail="Zona no encontrada")
    espacio_gestionado = get_managed_space_id(db, current_user)
    if espacio_gestionado is not None and zona.espacio_id != espacio_gestionado:
        raise HTTPException(status_code=403, detail="Solo puedes gestionar ensayos de tu espacio")
    return create_ensayo(db, payload, current_user.id)


@router.put("/{ensayo_id}", response_model=EnsayoResponse)
def actualizar_ensayo_endpoint(
    ensayo_id: int,
    payload: EnsayoUpdate,
    current_user: Usuario = Depends(require_resource_manager),
    db: Session = Depends(get_db),
):
    ensayo = get_ensayo(db, ensayo_id)
    if ensayo is None:
        raise HTTPException(status_code=404, detail="Ensayo no encontrado")
    # dos saltos: ensayo -> zona -> espacio
    zona_actual = db.query(Zona).filter(Zona.id == ensayo.zona_id).first()
    espacio_gestionado = get_managed_space_id(db, current_user)
    if espacio_gestionado is not None and zona_actual and zona_actual.espacio_id != espacio_gestionado:
        raise HTTPException(status_code=403, detail="Solo puedes gestionar ensayos de tu espacio")

    cambios = payload.model_dump(exclude_unset=True)
    if espacio_gestionado is not None:
        # gestor no puede mover ensayo fuera de su espacio
        if "zona_id" in cambios:
            nueva_zona = db.query(Zona).filter(Zona.id == cambios["zona_id"]).first()
            if nueva_zona is None:
                raise HTTPException(status_code=404, detail="Zona no encontrada")
            if nueva_zona.espacio_id != espacio_gestionado:
                cambios.pop("zona_id", None)
    if "zona_id" in cambios:
        nueva_zona = db.query(Zona).filter(Zona.id == cambios["zona_id"]).first()
        if nueva_zona is None:
            raise HTTPException(status_code=404, detail="Zona no encontrada")

    return update_ensayo(db, ensayo, cambios, current_user.id)


@router.delete("/{ensayo_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_ensayo_endpoint(
    ensayo_id: int,
    current_user: Usuario = Depends(require_resource_manager),
    db: Session = Depends(get_db),
):
    ensayo = get_ensayo(db, ensayo_id)
    if ensayo is None:
        raise HTTPException(status_code=404, detail="Ensayo no encontrado")
    zona_actual = db.query(Zona).filter(Zona.id == ensayo.zona_id).first()
    espacio_gestionado = get_managed_space_id(db, current_user)
    if espacio_gestionado is not None and zona_actual and zona_actual.espacio_id != espacio_gestionado:
        raise HTTPException(status_code=403, detail="Solo puedes gestionar ensayos de tu espacio")
    if db.query(ReservaEnsayo).filter(ReservaEnsayo.ensayo_id == ensayo_id).first() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar un ensayo referenciado por una reserva",
        )
    db.delete(ensayo)
    db.commit()
    return None
