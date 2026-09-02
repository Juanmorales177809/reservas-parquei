from sqlalchemy.orm import Session

from app.domain.valor import HorarioAtencion
from app.models import Laboratorio
from app.schemas.laboratorio import LaboratorioCreate, LaboratorioUpdate


def get_laboratorio(db: Session, laboratorio_id: int) -> Laboratorio | None:
    return db.query(Laboratorio).filter(Laboratorio.id == laboratorio_id).first()


def get_laboratorio_by_nombre(db: Session, nombre: str) -> Laboratorio | None:
    return db.query(Laboratorio).filter(Laboratorio.nombre == nombre).first()


def create_laboratorio(db: Session, data: LaboratorioCreate) -> Laboratorio:
    # Horario por defecto validado por el dominio y serializado al formato
    # exacto que ya se persistía: {"0": [7..19], ..., "5": [7..19]}.
    horario = HorarioAtencion({dia: list(range(7, 20)) for dia in range(6)})
    db_laboratorio = Laboratorio(
        nombre=data.nombre,
        ubicacion=data.ubicacion,
        capacidad=data.capacidad,
        estado=data.estado,
        horario_atencion={
            str(dia): list(horario.horas_del_dia(dia)) for dia in horario.dias
        },
        correo=data.correo,
    )
    db.add(db_laboratorio)
    db.commit()
    db.refresh(db_laboratorio)
    return db_laboratorio


def update_laboratorio(db: Session, laboratorio_id: int, data: LaboratorioUpdate) -> Laboratorio | None:
    db_laboratorio = get_laboratorio(db, laboratorio_id)
    if db_laboratorio is None:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_laboratorio, key, value)

    db.commit()
    db.refresh(db_laboratorio)
    return db_laboratorio
