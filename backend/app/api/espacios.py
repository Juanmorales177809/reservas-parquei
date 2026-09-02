from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.espacios import create_espacio, get_espacio, reemplazar_recursos_de_espacio, update_espacio
from app.db import get_db
from app.deps import get_current_user_optional, get_managed_laboratory_id, require_resource_manager
from app.domain.enums import Rol
from app.models import Laboratorio, Personal, Recurso, Usuario
from app.models.espacio import Espacio
from app.models.espacio_recurso import EspacioRecurso
from app.schemas.espacio import (
    EspacioCreate,
    EspacioRecursosResponse,
    EspacioRecursosUpdate,
    EspacioResponse,
    EspacioUpdate,
)

router = APIRouter(prefix="/espacios", tags=["espacios"])


@router.get("", response_model=list[EspacioResponse])
def listar_espacios(
    laboratorio_id: int | None = None,
    db: Session = Depends(get_db),
    usuario: Usuario | None = Depends(get_current_user_optional),
):
    """Listar espacios. No requiere autenticacion (mismo criterio RN-005 que
    GET /laboratorios): anonimo/usuario solo ven espacios activos de
    laboratorios activos; gestor/admin ven todo."""
    query = db.query(Espacio).join(Laboratorio, Espacio.laboratorio_id == Laboratorio.id)
    if laboratorio_id is not None:
        query = query.filter(Espacio.laboratorio_id == laboratorio_id)
    if usuario is None or usuario.rol == Rol.USUARIO.value:
        query = query.filter(Espacio.estado == "activo", Laboratorio.estado == "activo")
    return query.order_by(Espacio.nombre.asc()).all()


@router.post("", response_model=EspacioResponse, status_code=status.HTTP_201_CREATED)
def crear_espacio(
    payload: EspacioCreate,
    current_user: Personal = Depends(require_resource_manager),
    db: Session = Depends(get_db),
):
    laboratorio_gestionado = get_managed_laboratory_id(db, current_user)
    if laboratorio_gestionado is not None and payload.laboratorio_id != laboratorio_gestionado:
        raise HTTPException(status_code=403, detail="Solo puedes gestionar espacios de tu laboratorio")
    if db.query(Laboratorio).filter(Laboratorio.id == payload.laboratorio_id).first() is None:
        raise HTTPException(status_code=404, detail="Laboratorio no encontrado")
    return create_espacio(db, payload, current_user.id)


@router.put("/{espacio_id}", response_model=EspacioResponse)
def actualizar_espacio(
    espacio_id: int,
    payload: EspacioUpdate,
    current_user: Personal = Depends(require_resource_manager),
    db: Session = Depends(get_db),
):
    espacio = get_espacio(db, espacio_id)
    if espacio is None:
        raise HTTPException(status_code=404, detail="Espacio no encontrado")
    laboratorio_gestionado = get_managed_laboratory_id(db, current_user)
    if laboratorio_gestionado is not None and espacio.laboratorio_id != laboratorio_gestionado:
        raise HTTPException(status_code=403, detail="Solo puedes gestionar espacios de tu laboratorio")

    cambios = payload.model_dump(exclude_unset=True)
    if laboratorio_gestionado is not None:
        # Un gestor no puede mover un espacio fuera de su propio
        # laboratorio, igual que ya rige para Recurso (api/recursos.py).
        cambios.pop("laboratorio_id", None)
    nuevo_laboratorio_id = cambios.get("laboratorio_id", espacio.laboratorio_id)
    if db.query(Laboratorio).filter(Laboratorio.id == nuevo_laboratorio_id).first() is None:
        raise HTTPException(status_code=404, detail="Laboratorio no encontrado")

    return update_espacio(db, espacio, cambios, current_user.id)


@router.put("/{espacio_id}/recursos", response_model=EspacioRecursosResponse)
def actualizar_recursos_de_espacio(
    espacio_id: int,
    payload: EspacioRecursosUpdate,
    current_user: Personal = Depends(require_resource_manager),
    db: Session = Depends(get_db),
):
    """Reemplazo completo de la asociación Espacio<->Recurso (Fase 12C-3):
    la lista recibida sustituye por completo a la actual -- lo ausente se
    elimina, lo nuevo se inserta. Unicidad funcional: un recurso ya
    asociado a OTRO espacio responde 409 sin dejar cambios parciales (todas
    las validaciones se resuelven antes de tocar la base de datos)."""
    espacio = get_espacio(db, espacio_id)
    if espacio is None:
        raise HTTPException(status_code=404, detail="Espacio no encontrado")
    laboratorio_gestionado = get_managed_laboratory_id(db, current_user)
    if laboratorio_gestionado is not None and espacio.laboratorio_id != laboratorio_gestionado:
        raise HTTPException(status_code=403, detail="Solo puedes gestionar espacios de tu laboratorio")

    recurso_ids = set(payload.recurso_ids)
    if recurso_ids:
        recursos = db.query(Recurso).filter(Recurso.id.in_(recurso_ids)).all()
        encontrados = {r.id for r in recursos}
        faltantes = recurso_ids - encontrados
        if faltantes:
            raise HTTPException(
                status_code=404,
                detail=f"Recurso(s) no encontrado(s): {sorted(faltantes)}",
            )
        fuera_de_laboratorio = sorted(r.id for r in recursos if r.laboratorio_id != espacio.laboratorio_id)
        if fuera_de_laboratorio:
            raise HTTPException(
                status_code=400,
                detail=f"Los recursos {fuera_de_laboratorio} no pertenecen al laboratorio del espacio",
            )
        conflictivos = sorted(
            er.recurso_id
            for er in db.query(EspacioRecurso)
            .filter(EspacioRecurso.recurso_id.in_(recurso_ids), EspacioRecurso.espacio_id != espacio_id)
            .all()
        )
        if conflictivos:
            raise HTTPException(
                status_code=409,
                detail=f"Los recursos {conflictivos} ya pertenecen a otro espacio",
            )

    resultado = reemplazar_recursos_de_espacio(db, espacio_id, recurso_ids)
    return EspacioRecursosResponse(espacio_id=espacio_id, recurso_ids=sorted(resultado))


@router.delete("/{espacio_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_espacio(
    espacio_id: int,
    current_user: Personal = Depends(require_resource_manager),
    db: Session = Depends(get_db),
):
    espacio = get_espacio(db, espacio_id)
    if espacio is None:
        raise HTTPException(status_code=404, detail="Espacio no encontrado")
    laboratorio_gestionado = get_managed_laboratory_id(db, current_user)
    if laboratorio_gestionado is not None and espacio.laboratorio_id != laboratorio_gestionado:
        raise HTTPException(status_code=403, detail="Solo puedes gestionar espacios de tu laboratorio")
    if db.query(EspacioRecurso).filter(EspacioRecurso.espacio_id == espacio_id).first() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar un espacio con recursos asociados",
        )
    db.delete(espacio)
    db.commit()
    return None
