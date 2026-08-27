import secrets
import uuid

from sqlalchemy.orm import Session

from app.models.usuario import Usuario
from app.models.usuario_espacio import UsuarioEspacio
from app.schemas.usuario import PerfilUpdate, UsuarioCreate, UsuarioUpdate


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
    from app.auth.auth import hash_password

    db_usuario = Usuario(
        username=usuario.username,
        email=usuario.email,
        # Vestigial: Supabase gestiona la contraseña real de esta cuenta
        # (ver create_usuario_admin en app/api/usuarios.py); esta columna es
        # NOT NULL en el esquema pero nunca se lee para autenticar. Se
        # guarda un valor aleatorio inutilizable, no la contraseña real de
        # nadie.
        hashed_password=hash_password(secrets.token_urlsafe(32)),
        rol=getattr(usuario, "rol", "usuario"),
        supabase_id=supabase_id,
    )
    db.add(db_usuario)
    db.flush()
    if db_usuario.rol == "gestor" and getattr(usuario, "espacio_id", None) is not None:
        db.add(UsuarioEspacio(usuario_id=db_usuario.id, espacio_id=usuario.espacio_id))
    db.commit()
    db.refresh(db_usuario)
    return db_usuario


def update_usuario(db: Session, db_usuario: Usuario, data: UsuarioUpdate) -> Usuario:
    update_data = data.model_dump(exclude_unset=True)
    espacio_id = update_data.pop("espacio_id", None)
    for field, value in update_data.items():
        setattr(db_usuario, field, value)

    asignacion = (
        db.query(UsuarioEspacio)
        .filter(UsuarioEspacio.usuario_id == db_usuario.id)
        .first()
    )
    if db_usuario.rol != "gestor":
        if asignacion is not None:
            db.delete(asignacion)
    elif espacio_id is not None:
        if asignacion is None:
            db.add(UsuarioEspacio(usuario_id=db_usuario.id, espacio_id=espacio_id))
        else:
            asignacion.espacio_id = espacio_id

    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario


def actualizar_perfil(db: Session, db_usuario: Usuario, data: PerfilUpdate) -> Usuario:
    """Fase A2: self-service, solo los 5 campos de perfil -- a diferencia
    de `update_usuario`, acá no hay `rol`/`espacio_id` que resolver."""
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
