import secrets
import uuid

from sqlalchemy.orm import Session

from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate


def get_usuario(db: Session, usuario_id: int) -> Usuario | None:
    return db.query(Usuario).filter(Usuario.id == usuario_id).first()


def get_usuario_by_username(db: Session, username: str) -> Usuario | None:
    return db.query(Usuario).filter(Usuario.username == username).first()


def get_usuario_by_email(db: Session, email: str) -> Usuario | None:
    return db.query(Usuario).filter(Usuario.email == email).first()


def get_usuario_by_supabase_id(db: Session, supabase_id: uuid.UUID) -> Usuario | None:
    return db.query(Usuario).filter(Usuario.supabase_id == supabase_id).first()


def get_usuarios(db: Session, skip: int = 0, limit: int = 100) -> list[Usuario]:
    return db.query(Usuario).order_by(Usuario.username.asc()).offset(skip).limit(limit).all()


def create_usuario(db: Session, usuario: UsuarioCreate, supabase_id: uuid.UUID) -> Usuario:
    """Rol siempre `usuario` -- esta tabla ya no acepta admin/gestor desde
    la separación en `personal` (ver `app/crud/personal.py`)."""
    from app.auth.auth import hash_password

    db_usuario = Usuario(
        username=usuario.username,
        email=usuario.email,
        # Vestigial: Supabase gestiona la contraseña real de esta cuenta;
        # esta columna es NOT NULL en el esquema pero nunca se lee para
        # autenticar. Se guarda un valor aleatorio inutilizable.
        hashed_password=hash_password(secrets.token_urlsafe(32)),
        rol="usuario",
        supabase_id=supabase_id,
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario


def update_usuario(db: Session, db_usuario: Usuario, data: UsuarioUpdate) -> Usuario:
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_usuario, field, value)
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario


def delete_usuario(db: Session, db_usuario: Usuario) -> None:
    db.delete(db_usuario)
    db.commit()
