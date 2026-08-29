"""Lecturas y escrituras que necesitan mirar `personal` y `usuarios` a la
vez -- desde la separación en dos tablas (ver
`~/.claude/plans/dazzling-wobbling-zebra.md`), PostgreSQL solo garantiza
unicidad de `username`/`email` DENTRO de cada tabla, no entre las dos. Los
checks 409 de creación/edición (`api/auth.py`, `api/usuarios.py`,
`api/personal.py`) tienen que consultar ambas para no dejar colar el
mismo username/email en las dos tablas a la vez."""

import uuid

from sqlalchemy.orm import Session

from app.models.personal import Personal
from app.models.usuario import Usuario
from app.schemas.usuario import PerfilUpdate


def buscar_por_username(db: Session, username: str) -> Personal | Usuario | None:
    return (
        db.query(Personal).filter(Personal.username == username).first()
        or db.query(Usuario).filter(Usuario.username == username).first()
    )


def buscar_por_email(db: Session, email: str) -> Personal | Usuario | None:
    return (
        db.query(Personal).filter(Personal.email == email).first()
        or db.query(Usuario).filter(Usuario.email == email).first()
    )


def buscar_por_supabase_id(db: Session, supabase_id: uuid.UUID) -> Personal | Usuario | None:
    return (
        db.query(Personal).filter(Personal.supabase_id == supabase_id).first()
        or db.query(Usuario).filter(Usuario.supabase_id == supabase_id).first()
    )


def actualizar_perfil(db: Session, identidad: Personal | Usuario, data: PerfilUpdate) -> Personal | Usuario:
    """`PUT /me` self-service -- funciona igual para `Personal` que para
    `Usuario`, los 5 campos de perfil tienen el mismo nombre en ambos
    modelos (ver `Personal`/`Usuario`)."""
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(identidad, field, value)
    db.add(identidad)
    db.commit()
    db.refresh(identidad)
    return identidad
