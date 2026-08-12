from sqlalchemy.orm import Session

from app.models import ControlCambio, Usuario


def registrar_cambio(
    db: Session,
    usuario: Usuario,
    accion: str,
    entidad: str,
    entidad_id: int | None,
    descripcion: str,
) -> None:
    db.add(
        ControlCambio(
            usuario_id=usuario.id,
            accion=accion,
            entidad=entidad,
            entidad_id=entidad_id,
            descripcion=descripcion,
        )
    )
