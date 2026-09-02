from sqlalchemy.orm import Session

from app.models.motivo_solicitud import MotivoSolicitud


def listar_motivos_por_laboratorio(db: Session, laboratorio_id: int) -> list[MotivoSolicitud]:
    return db.query(MotivoSolicitud).filter(MotivoSolicitud.laboratorio_id == laboratorio_id, MotivoSolicitud.estado == "activo").order_by(MotivoSolicitud.nombre).all()


def listar_todos_motivos(db: Session) -> list[MotivoSolicitud]:
    return db.query(MotivoSolicitud).order_by(MotivoSolicitud.laboratorio_id, MotivoSolicitud.nombre).all()
