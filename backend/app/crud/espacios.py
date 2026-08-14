from sqlalchemy.orm import Session

from app.domain.valor import HorarioAtencion
from app.models import Espacio
from app.schemas.espacio import EspacioCreate, EspacioUpdate


def get_espacio(db: Session, espacio_id: int) -> Espacio | None:
    return db.query(Espacio).filter(Espacio.id == espacio_id).first()


def get_espacio_by_nombre(db: Session, nombre: str) -> Espacio | None:
    return db.query(Espacio).filter(Espacio.nombre == nombre).first()


def create_espacio(db: Session, data: EspacioCreate) -> Espacio:
    # Horario por defecto validado por el dominio y serializado al formato
    # exacto que ya se persistía: {"0": [7..19], ..., "5": [7..19]}.
    horario = HorarioAtencion({dia: list(range(7, 20)) for dia in range(6)})
    db_espacio = Espacio(
        nombre=data.nombre,
        ubicacion=data.ubicacion,
        capacidad=data.capacidad,
        estado=data.estado,
        horario_atencion={
            str(dia): list(horario.horas_del_dia(dia)) for dia in horario.dias
        },
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
