from sqlalchemy.orm import Session

from app.models import Espacio
from app.schemas.espacio import EspacioCreate, EspacioUpdate


def get_espacio(db: Session, espacio_id: int) -> Espacio | None:
    return db.query(Espacio).filter(Espacio.id == espacio_id).first()


def get_espacio_by_nombre(db: Session, nombre: str) -> Espacio | None:
    return db.query(Espacio).filter(Espacio.nombre == nombre).first()


def create_espacio(db: Session, data: EspacioCreate) -> Espacio:
    db_espacio = Espacio(
        nombre=data.nombre,
        ubicacion=data.ubicacion,
        capacidad=data.capacidad,
        estado=data.estado,
        horario_atencion={str(dia): list(range(7, 20)) for dia in range(6)},
    )
    db.add(db_espacio)
    db.commit()
    db.refresh(db_espacio)
    return db_espacio


def update_espacio(db: Session, espacio_id: int, data: EspacioUpdate) -> Espacio | None:
    db_espacio = get_espacio(db, espacio_id)
    if db_espacio is None:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_espacio, key, value)

    db.commit()
    db.refresh(db_espacio)
    return db_espacio
