from sqlalchemy.orm import Session

from app.models.tipo_reserva import TipoReserva
from app.schemas.tipo_reserva import TipoReservaCreate


def get_tipo_reserva(db: Session, tipo_reserva_id: int) -> TipoReserva | None:
    return db.query(TipoReserva).filter(TipoReserva.id == tipo_reserva_id).first()


def listar_tipos_reserva(db: Session, laboratorio_id: int | None) -> list[TipoReserva]:
    query = db.query(TipoReserva)
    if laboratorio_id is not None:
        query = query.filter(TipoReserva.laboratorio_id == laboratorio_id)
    return query.order_by(TipoReserva.nombre.asc()).all()


def create_tipo_reserva(db: Session, data: TipoReservaCreate, usuario_id: int) -> TipoReserva:
    tipo_reserva = TipoReserva(
        laboratorio_id=data.laboratorio_id,
        nombre=data.nombre,
        estado=data.estado,
        created_by=usuario_id,
        updated_by=usuario_id,
    )
    db.add(tipo_reserva)
    db.commit()
    db.refresh(tipo_reserva)
    return tipo_reserva


def update_tipo_reserva(db: Session, tipo_reserva: TipoReserva, cambios: dict, usuario_id: int) -> TipoReserva:
    for campo, valor in cambios.items():
        setattr(tipo_reserva, campo, valor)
    tipo_reserva.updated_by = usuario_id
    db.commit()
    db.refresh(tipo_reserva)
    return tipo_reserva
