from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.zona import Zona
from app.models.zona_recurso import ZonaRecurso
from app.schemas.zona import ZonaCreate


def get_zona(db: Session, zona_id: int) -> Zona | None:
    return db.query(Zona).filter(Zona.id == zona_id).first()


def create_zona(db: Session, data: ZonaCreate, usuario_id: int) -> Zona:
    zona = Zona(
        nombre=data.nombre,
        espacio_id=data.espacio_id,
        descripcion=data.descripcion,
        capacidad=data.capacidad,
        estado=data.estado,
        created_by=usuario_id,
        updated_by=usuario_id,
    )
    db.add(zona)
    db.commit()
    db.refresh(zona)
    return zona


def update_zona(db: Session, zona: Zona, cambios: dict, usuario_id: int) -> Zona:
    for campo, valor in cambios.items():
        setattr(zona, campo, valor)
    zona.updated_by = usuario_id
    db.commit()
    db.refresh(zona)
    return zona


def reemplazar_recursos_de_zona(db: Session, zona_id: int, recurso_ids: set[int]) -> set[int]:
    """Reemplazo completo de la asociación Zona<->Recurso (Fase 12C-3).

    Las validaciones de negocio (existencia de recursos/zona, pertenencia
    al mismo espacio, conflicto con otra zona) ya se resolvieron en
    `app/api/zonas.py` antes de llamar a esta función. El try/except de
    aquí es una red de seguridad para una condición de carrera genuina
    entre el momento en que se validó y el commit -- no ejercitada de
    forma determinista por los tests de esta subfase, pero protegida por
    la misma `UniqueConstraint` de BD que ya se prueba directamente en
    `tests/test_models_zona_recurso.py`. Mismo patrón que
    `services/reservas.py::_traducir_error_integridad`.
    """
    actuales = {
        zr.recurso_id
        for zr in db.query(ZonaRecurso).filter(ZonaRecurso.zona_id == zona_id).all()
    }
    a_quitar = actuales - recurso_ids
    a_agregar = recurso_ids - actuales

    if a_quitar:
        db.query(ZonaRecurso).filter(
            ZonaRecurso.zona_id == zona_id, ZonaRecurso.recurso_id.in_(a_quitar)
        ).delete(synchronize_session=False)
    for recurso_id in a_agregar:
        db.add(ZonaRecurso(zona_id=zona_id, recurso_id=recurso_id))

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Uno de los recursos ya fue asociado a otra zona",
        ) from exc
    return recurso_ids
