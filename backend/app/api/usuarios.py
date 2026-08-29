from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.identidad import actualizar_perfil, buscar_por_email, buscar_por_username
from app.crud.usuarios import create_usuario, delete_usuario, get_usuario, get_usuarios, update_usuario
from app.db import get_db
from app.deps import get_current_user, require_admin
from app.models.personal import Personal
from app.models.usuario import Usuario
from app.schemas.usuario import PerfilUpdate, ReenviarInvitacionResponse, UsuarioCreate, UsuarioResponse, UsuarioUpdate
from app.services.auditoria import registrar_cambio
from app.services.email import encolar_correo, procesar_pendientes
from app.services.email_templates import plantilla_invitacion
from app.services.supabase_admin import (
    SupabaseAdminError,
    crear_usuario_y_generar_link,
    eliminar_usuario as eliminar_usuario_supabase,
    generar_link_invitacion,
)


router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.get("/me", response_model=UsuarioResponse)
def get_me(current_user: Personal | Usuario = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UsuarioResponse)
def actualizar_mi_perfil(
    payload: PerfilUpdate,
    current_user: Personal | Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Self-service: cualquier identidad autenticada (`Personal` o
    `Usuario`) edita su propio perfil. Registrada ANTES de
    `PUT /usuarios/{usuario_id}` a propósito -- si quedara después,
    FastAPI intentaría parsear "me" como el `int` de esa ruta."""
    return actualizar_perfil(db, current_user, payload)


@router.get("", response_model=list[UsuarioResponse])
def list_usuarios(
    current_user: Personal = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Rol `usuario` únicamente desde la separación en `personal`/
    `usuarios` -- ver `GET /personal` para admin/gestor."""
    return get_usuarios(db)


@router.post("", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def create_usuario_admin(
    payload: UsuarioCreate,
    current_user: Personal = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Alta de una cuenta rol `usuario` por un admin -- distinta del
    autoregistro abierto (`POST /auth/registro`): acá la identidad de
    Supabase se crea vía invitación (la persona nunca elige su propia
    contraseña en este flujo)."""
    if buscar_por_username(db, payload.username) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El nombre de usuario ya está registrado",
        )
    if buscar_por_email(db, payload.email) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El email ya está registrado",
        )

    try:
        supabase_id, link = crear_usuario_y_generar_link(payload.email)
    except SupabaseAdminError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"No se pudo crear la cuenta en Supabase: {exc}",
        ) from exc

    usuario = create_usuario(db, payload, supabase_id)
    encolar_correo(
        db,
        destinatario=payload.email,
        asunto="Invitación a Reservas Parque i",
        cuerpo=plantilla_invitacion(link=link, nombre_saludo=payload.username),
        es_html=True,
    )
    registrar_cambio(db, current_user, "crear", "usuario", usuario.id, f"Creó el usuario {usuario.username}")
    db.commit()
    procesar_pendientes(db)
    db.refresh(usuario)
    return usuario


@router.post("/{usuario_id}/reenviar-invitacion", response_model=ReenviarInvitacionResponse)
def reenviar_invitacion_endpoint(
    usuario_id: int,
    current_user: Personal = Depends(require_admin),
    db: Session = Depends(get_db),
):
    db_user = get_usuario(db, usuario_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if db_user.supabase_id is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este usuario no tiene una identidad de Supabase asociada",
        )

    try:
        link = generar_link_invitacion(db_user.email)
    except SupabaseAdminError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"No se pudo generar el link de invitación en Supabase: {exc}",
        ) from exc

    correo = encolar_correo(
        db,
        destinatario=db_user.email,
        asunto="Invitación a Reservas Parque i",
        cuerpo=plantilla_invitacion(link=link, nombre_saludo=db_user.username),
        es_html=True,
    )
    registrar_cambio(db, current_user, "reenviar_invitacion", "usuario", db_user.id, f"Reenvió la invitación a {db_user.username}")
    db.commit()
    procesar_pendientes(db)
    db.refresh(correo)

    return ReenviarInvitacionResponse(link=link, correo_enviado=correo.estado == "enviado")


@router.put("/{usuario_id}", response_model=UsuarioResponse)
def update_usuario_endpoint(
    usuario_id: int,
    payload: UsuarioUpdate,
    current_user: Personal = Depends(require_admin),
    db: Session = Depends(get_db),
):
    db_user = get_usuario(db, usuario_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if payload.username and payload.username != db_user.username:
        if buscar_por_username(db, payload.username):
            raise HTTPException(status_code=409, detail="Nombre de usuario ya está en uso")
    if payload.email and payload.email != db_user.email:
        if buscar_por_email(db, payload.email):
            raise HTTPException(status_code=409, detail="Email ya está en uso")

    usuario = update_usuario(db, db_user, payload)
    registrar_cambio(db, current_user, "actualizar", "usuario", usuario.id, f"Actualizó el usuario {usuario.username}")
    db.commit()
    return usuario


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_usuario_endpoint(
    usuario_id: int,
    current_user: Personal = Depends(require_admin),
    db: Session = Depends(get_db),
):
    db_user = get_usuario(db, usuario_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if db_user.supabase_id is not None:
        try:
            eliminar_usuario_supabase(db_user.supabase_id)
        except SupabaseAdminError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"No se pudo eliminar la cuenta en Supabase: {exc}",
            ) from exc

    descripcion = f"Eliminó el usuario {db_user.username}"
    delete_usuario(db, db_user)
    registrar_cambio(db, current_user, "eliminar", "usuario", usuario_id, descripcion)
    db.commit()
    return None
