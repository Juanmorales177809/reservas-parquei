import uuid

from sqlalchemy.orm import Session

from app.models.personal import Personal
from app.models.usuario_laboratorio import UsuarioLaboratorio
from app.schemas.personal import PersonalCreate, PersonalUpdate


def get_personal(db: Session, personal_id: int) -> Personal | None:
    return db.query(Personal).filter(Personal.id == personal_id).first()


def get_personal_by_username(db: Session, username: str) -> Personal | None:
    return db.query(Personal).filter(Personal.username == username).first()


def get_personal_by_email(db: Session, email: str) -> Personal | None:
    return db.query(Personal).filter(Personal.email == email).first()


def get_personal_by_supabase_id(db: Session, supabase_id: uuid.UUID) -> Personal | None:
    return db.query(Personal).filter(Personal.supabase_id == supabase_id).first()


def listar_personal(db: Session, skip: int = 0, limit: int = 100) -> list[Personal]:
    return db.query(Personal).order_by(Personal.username.asc()).offset(skip).limit(limit).all()


def crear_personal(db: Session, data: PersonalCreate, supabase_id: uuid.UUID) -> Personal:
    db_personal = Personal(
        username=data.username,
        email=data.email,
        rol=data.rol.value,
        supabase_id=supabase_id,
    )
    db.add(db_personal)
    db.flush()
    if db_personal.rol == "gestor" and data.laboratorio_id is not None:
        db.add(UsuarioLaboratorio(usuario_id=db_personal.id, laboratorio_id=data.laboratorio_id))
    db.commit()
    db.refresh(db_personal)
    return db_personal


def actualizar_personal(db: Session, db_personal: Personal, data: PersonalUpdate) -> Personal:
    """No maneja `rol == usuario` -- eso es una degradación entre tablas
    (`services/migrar_actor.py::degradar_a_usuario`), resuelta en
    `api/personal.py` ANTES de llegar acá. Esta función solo cubre
    ediciones que se quedan dentro de `personal` (admin<->gestor, perfil,
    laboratorio)."""
    update_data = data.model_dump(exclude_unset=True)
    laboratorio_id = update_data.pop("laboratorio_id", None)
    if "rol" in update_data and update_data["rol"] is not None:
        update_data["rol"] = update_data["rol"].value if hasattr(update_data["rol"], "value") else update_data["rol"]
    for field, value in update_data.items():
        setattr(db_personal, field, value)

    asignacion = db.query(UsuarioLaboratorio).filter(UsuarioLaboratorio.usuario_id == db_personal.id).first()
    if db_personal.rol != "gestor":
        if asignacion is not None:
            db.delete(asignacion)
    elif laboratorio_id is not None:
        if asignacion is None:
            db.add(UsuarioLaboratorio(usuario_id=db_personal.id, laboratorio_id=laboratorio_id))
        else:
            asignacion.laboratorio_id = laboratorio_id

    db.add(db_personal)
    db.commit()
    db.refresh(db_personal)
    return db_personal


def eliminar_personal(db: Session, db_personal: Personal) -> None:
    db.delete(db_personal)
    db.commit()
