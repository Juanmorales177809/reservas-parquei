from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.zonas import create_zona, get_zona, reemplazar_recursos_de_zona, update_zona
from app.db import get_db
from app.deps import get_current_user_optional, get_managed_space_id, require_resource_manager
from app.domain.enums import Rol
from app.models import Espacio, Recurso, Usuario
from app.models.zona import Zona
from app.models.zona_recurso import ZonaRecurso
from app.schemas.zona import (
    ZonaCreate,
    ZonaRecursosResponse,
    ZonaRecursosUpdate,
    ZonaResponse,
    ZonaUpdate,
)

router = APIRouter(prefix="/zonas", tags=["zonas"])


@router.get("", response_model=list[ZonaResponse])
def listar_zonas(
    espacio_id: int | None = None,
    db: Session = Depends(get_db),
    usuario: Usuario | None = Depends(get_current_user_optional),
):
    """Listar zonas. No requiere autenticacion (mismo criterio RN-005 que
    GET /espacios): anonimo/usuario solo ven zonas activas de espacios
    activos; gestor/admin ven todo."""
    query = db.query(Zona).join(Espacio, Zona.espacio_id == Espacio.id)
    if espacio_id is not None:
        query = query.filter(Zona.espacio_id == espacio_id)
    if usuario is None or usuario.rol == Rol.USUARIO.value:
        query = query.filter(Zona.estado == "activo", Espacio.estado == "activo")
    return query.order_by(Zona.nombre.asc()).all()


@router.post("", response_model=ZonaResponse, status_code=status.HTTP_201_CREATED)
def crear_zona(
    payload: ZonaCreate,
    current_user: Usuario = Depends(require_resource_manager),
    db: Session = Depends(get_db),
):
    espacio_gestionado = get_managed_space_id(db, current_user)
    if espacio_gestionado is not None and payload.espacio_id != espacio_gestionado:
        raise HTTPException(status_code=403, detail="Solo puedes gestionar zonas de tu espacio")
    if db.query(Espacio).filter(Espacio.id == payload.espacio_id).first() is None:
        raise HTTPException(status_code=404, detail="Espacio no encontrado")
    return create_zona(db, payload, current_user.id)


@router.put("/{zona_id}", response_model=ZonaResponse)
def actualizar_zona(
    zona_id: int,
    payload: ZonaUpdate,
    current_user: Usuario = Depends(require_resource_manager),
    db: Session = Depends(get_db),
):
    zona = get_zona(db, zona_id)
    if zona is None:
        raise HTTPException(status_code=404, detail="Zona no encontrada")
    espacio_gestionado = get_managed_space_id(db, current_user)
    if espacio_gestionado is not None and zona.espacio_id != espacio_gestionado:
        raise HTTPException(status_code=403, detail="Solo puedes gestionar zonas de tu espacio")

    cambios = payload.model_dump(exclude_unset=True)
    if espacio_gestionado is not None:
        # Un gestor no puede mover una zona fuera de su propio espacio,
        # igual que ya rige para Recurso (api/recursos.py).
        cambios.pop("espacio_id", None)
    nuevo_espacio_id = cambios.get("espacio_id", zona.espacio_id)
    if db.query(Espacio).filter(Espacio.id == nuevo_espacio_id).first() is None:
        raise HTTPException(status_code=404, detail="Espacio no encontrado")

    return update_zona(db, zona, cambios, current_user.id)


@router.put("/{zona_id}/recursos", response_model=ZonaRecursosResponse)
def actualizar_recursos_de_zona(
    zona_id: int,
    payload: ZonaRecursosUpdate,
    current_user: Usuario = Depends(require_resource_manager),
    db: Session = Depends(get_db),
):
    """Reemplazo completo de la asociación Zona<->Recurso (Fase 12C-3):
    la lista recibida sustituye por completo a la actual -- lo ausente se
    elimina, lo nuevo se inserta. Unicidad funcional: un recurso ya
    asociado a OTRA zona responde 409 sin dejar cambios parciales (todas
    las validaciones se resuelven antes de tocar la base de datos)."""
    zona = get_zona(db, zona_id)
    if zona is None:
        raise HTTPException(status_code=404, detail="Zona no encontrada")
    espacio_gestionado = get_managed_space_id(db, current_user)
    if espacio_gestionado is not None and zona.espacio_id != espacio_gestionado:
        raise HTTPException(status_code=403, detail="Solo puedes gestionar zonas de tu espacio")

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
        fuera_de_espacio = sorted(r.id for r in recursos if r.espacio_id != zona.espacio_id)
        if fuera_de_espacio:
            raise HTTPException(
                status_code=400,
                detail=f"Los recursos {fuera_de_espacio} no pertenecen al espacio de la zona",
            )
        conflictivos = sorted(
            zr.recurso_id
            for zr in db.query(ZonaRecurso)
            .filter(ZonaRecurso.recurso_id.in_(recurso_ids), ZonaRecurso.zona_id != zona_id)
            .all()
        )
        if conflictivos:
            raise HTTPException(
                status_code=409,
                detail=f"Los recursos {conflictivos} ya pertenecen a otra zona",
            )

    resultado = reemplazar_recursos_de_zona(db, zona_id, recurso_ids)
    return ZonaRecursosResponse(zona_id=zona_id, recurso_ids=sorted(resultado))


@router.delete("/{zona_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_zona(
    zona_id: int,
    current_user: Usuario = Depends(require_resource_manager),
    db: Session = Depends(get_db),
):
    zona = get_zona(db, zona_id)
    if zona is None:
        raise HTTPException(status_code=404, detail="Zona no encontrada")
    espacio_gestionado = get_managed_space_id(db, current_user)
    if espacio_gestionado is not None and zona.espacio_id != espacio_gestionado:
        raise HTTPException(status_code=403, detail="Solo puedes gestionar zonas de tu espacio")
    if db.query(ZonaRecurso).filter(ZonaRecurso.zona_id == zona_id).first() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar una zona con recursos asociados",
        )
    db.delete(zona)
    db.commit()
    return None
