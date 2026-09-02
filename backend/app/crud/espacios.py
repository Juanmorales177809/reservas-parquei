from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.espacio import Espacio
from app.models.espacio_recurso import EspacioRecurso
from app.schemas.espacio import EspacioCreate


def get_espacio(db: Session, espacio_id: int) -> Espacio | None:
    return db.query(Espacio).filter(Espacio.id == espacio_id).first()


def create_espacio(db: Session, data: EspacioCreate, usuario_id: int) -> Espacio:
    espacio = Espacio(
        nombre=data.nombre,
        laboratorio_id=data.laboratorio_id,
        descripcion=data.descripcion,
        capacidad=data.capacidad,
        estado=data.estado,
        created_by=usuario_id,
        updated_by=usuario_id,
    )
    db.add(espacio)
    db.commit()
    db.refresh(espacio)
    return espacio


def update_espacio(db: Session, espacio: Espacio, cambios: dict, usuario_id: int) -> Espacio:
    for campo, valor in cambios.items():
        setattr(espacio, campo, valor)
    espacio.updated_by = usuario_id
    db.commit()
    db.refresh(espacio)
    return espacio


def reemplazar_recursos_de_espacio(db: Session, espacio_id: int, recurso_ids: set[int]) -> set[int]:
    """Reemplazo completo de la asociación Espacio<->Recurso (Fase 12C-3).

    Las validaciones de negocio (existencia de recursos/espacio, pertenencia
    al mismo laboratorio, conflicto con otro espacio) ya se resolvieron en
    `app/api/espacios.py` antes de llamar a esta función. El try/except de
    aquí es una red de seguridad para una condición de carrera genuina
    entre el momento en que se validó y el commit -- no ejercitada de
    forma determinista por los tests de esta subfase, pero protegida por
    la misma `UniqueConstraint` de BD que ya se prueba directamente en
    `tests/test_models_espacio_recurso.py`. Mismo patrón que
    `services/reservas.py::_traducir_error_integridad`.
    """
    actuales = {
        er.recurso_id
        for er in db.query(EspacioRecurso).filter(EspacioRecurso.espacio_id == espacio_id).all()
    }
    a_quitar = actuales - recurso_ids
    a_agregar = recurso_ids - actuales

    if a_quitar:
        db.query(EspacioRecurso).filter(
            EspacioRecurso.espacio_id == espacio_id, EspacioRecurso.recurso_id.in_(a_quitar)
        ).delete(synchronize_session=False)
    for recurso_id in a_agregar:
        db.add(EspacioRecurso(espacio_id=espacio_id, recurso_id=recurso_id))

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Uno de los recursos ya fue asociado a otro espacio",
        ) from exc
    return recurso_ids
