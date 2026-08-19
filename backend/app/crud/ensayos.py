from sqlalchemy.orm import Session

from app.models.ensayo import Ensayo
from app.schemas.ensayo import EnsayoCreate


def get_ensayo(db: Session, ensayo_id: int) -> Ensayo | None:
    return db.query(Ensayo).filter(Ensayo.id == ensayo_id).first()


def create_ensayo(db: Session, data: EnsayoCreate, usuario_id: int) -> Ensayo:
    ensayo = Ensayo(
        nombre=data.nombre,
        zona_id=data.zona_id,
        estado=data.estado,
        created_by=usuario_id,
        updated_by=usuario_id,
    )
    db.add(ensayo)
    db.commit()
    db.refresh(ensayo)
    return ensayo


def update_ensayo(db: Session, ensayo: Ensayo, cambios: dict, usuario_id: int) -> Ensayo:
    for campo, valor in cambios.items():
        setattr(ensayo, campo, valor)
    ensayo.updated_by = usuario_id
    db.commit()
    db.refresh(ensayo)
    return ensayo
