from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.crud.identidad import buscar_por_email, buscar_por_username
from app.crud.personal import actualizar_personal, crear_personal, eliminar_personal, get_personal, listar_personal
from app.crud.usuarios import get_usuario
from app.db import get_db
from app.deps import require_admin
from app.domain.enums import Rol
from app.models.laboratorio import Laboratorio
from app.models.personal import Personal
from app.schemas.personal import PersonalCreate, PersonalUpdate
from app.schemas.usuario import ReenviarInvitacionResponse, UsuarioResponse
from app.services.auditoria import registrar_cambio
from app.services.email import encolar_correo, procesar_pendientes
from app.services.email_templates import plantilla_invitacion
from app.services.migrar_actor import degradar_a_usuario, promover_a_personal
from app.services.supabase_admin import (
    SupabaseAdminError,
    crear_usuario_y_generar_link,
    eliminar_usuario as eliminar_usuario_supabase,
    generar_link_invitacion,
)


router = APIRouter(prefix="/personal", tags=["personal"])
ADMIN_LOCK_ID = 728_341


def proteger_administradores(
    db: Session,
    objetivo: Personal,
    current_user: Personal,
    rol_final: str | None = None,
    eliminando: bool = False,
) -> None:
    """Mismo mecanismo que antes de la separación (ver
    `~/.claude/plans/dazzling-wobbling-zebra.md`), consultando `Personal`
    en vez de `Usuario`: nunca te quedás sin al menos un admin, y nadie se
    puede eliminar ni degradar la propia cuenta administrativa."""
    if objetivo.rol != "admin":
        return
    if not eliminando and rol_final == "admin":
        return
    if objetivo.id == current_user.id:
        accion = "eliminar" if eliminando else "cambiar el rol de"
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"No puedes {accion} tu propia cuenta administrativa",
        )

    db.execute(text("SELECT pg_advisory_xact_lock(:lock_id)"), {"lock_id": ADMIN_LOCK_ID})
    administradores = db.query(Personal).filter(Personal.rol == "admin").count()
    if administradores <= 1:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Debe permanecer al menos un administrador en el sistema",
        )


@router.get("", response_model=list[UsuarioResponse])
def list_personal(
    current_user: Personal = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return listar_personal(db)


@router.post("", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def create_personal_admin(
    payload: PersonalCreate,
    current_user: Personal = Depends(require_admin),
    db: Session = Depends(get_db),
):
    if buscar_por_username(db, payload.username) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El nombre de usuario ya está registrado")
    if buscar_por_email(db, payload.email) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El email ya está registrado")

    if payload.rol == Rol.GESTOR:
        if payload.laboratorio_id is None:
            raise HTTPException(status_code=400, detail="Debes asignar un laboratorio al gestor")
        if db.query(Laboratorio).filter(Laboratorio.id == payload.laboratorio_id).first() is None:
            raise HTTPException(status_code=404, detail="Laboratorio no encontrado")

    try:
        supabase_id, link = crear_usuario_y_generar_link(payload.email)
    except SupabaseAdminError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"No se pudo crear la cuenta en Supabase: {exc}",
        ) from exc

    personal = crear_personal(db, payload, supabase_id)
    encolar_correo(
        db,
        destinatario=payload.email,
        asunto="Invitación a Reservas Parque i",
        cuerpo=plantilla_invitacion(link=link, nombre_saludo=payload.username),
        es_html=True,
    )
    registrar_cambio(db, current_user, "crear", "personal", personal.id, f"Creó el personal {personal.username} con rol {personal.rol}")
    db.commit()
    procesar_pendientes(db)
    db.refresh(personal)
    return personal


@router.post("/promover/{usuario_id}", response_model=UsuarioResponse)
def promover_usuario_a_personal(
    usuario_id: int,
    payload: PersonalCreate,
    current_user: Personal = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Asciende una cuenta existente de `usuarios` (rol `usuario`) a
    `personal` (`admin`/`gestor`) -- distinto de `create_personal_admin`,
    que crea una identidad nueva desde cero. Mueve la misma fila (mismo
    `id`, mismo `supabase_id`) y repunta cualquier reserva/notificación/
    auditoría existente -- ver `services/migrar_actor.py`."""
    db_usuario = get_usuario(db, usuario_id)
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if payload.rol == Rol.GESTOR:
        if payload.laboratorio_id is None:
            raise HTTPException(status_code=400, detail="Debes asignar un laboratorio al gestor")
        if db.query(Laboratorio).filter(Laboratorio.id == payload.laboratorio_id).first() is None:
            raise HTTPException(status_code=404, detail="Laboratorio no encontrado")

    personal = promover_a_personal(db, db_usuario, payload.rol.value, payload.laboratorio_id)
    registrar_cambio(
        db, current_user, "promover", "personal", personal.id, f"Ascendió a {personal.username} a rol {personal.rol}"
    )
    db.commit()
    return personal


@router.post("/{personal_id}/reenviar-invitacion", response_model=ReenviarInvitacionResponse)
def reenviar_invitacion_endpoint(
    personal_id: int,
    current_user: Personal = Depends(require_admin),
    db: Session = Depends(get_db),
):
    db_personal = get_personal(db, personal_id)
    if not db_personal:
        raise HTTPException(status_code=404, detail="Personal no encontrado")
    if db_personal.supabase_id is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este usuario no tiene una identidad de Supabase asociada",
        )

    try:
        link = generar_link_invitacion(db_personal.email)
    except SupabaseAdminError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"No se pudo generar el link de invitación en Supabase: {exc}",
        ) from exc

    correo = encolar_correo(
        db,
        destinatario=db_personal.email,
        asunto="Invitación a Reservas Parque i",
        cuerpo=plantilla_invitacion(link=link, nombre_saludo=db_personal.username),
        es_html=True,
    )
    registrar_cambio(db, current_user, "reenviar_invitacion", "personal", db_personal.id, f"Reenvió la invitación a {db_personal.username}")
    db.commit()
    procesar_pendientes(db)
    db.refresh(correo)

    return ReenviarInvitacionResponse(link=link, correo_enviado=correo.estado == "enviado")


@router.put("/{personal_id}", response_model=UsuarioResponse)
def update_personal_endpoint(
    personal_id: int,
    payload: PersonalUpdate,
    current_user: Personal = Depends(require_admin),
    db: Session = Depends(get_db),
):
    db_personal = get_personal(db, personal_id)
    if not db_personal:
        raise HTTPException(status_code=404, detail="Personal no encontrado")

    if payload.username and payload.username != db_personal.username:
        if buscar_por_username(db, payload.username):
            raise HTTPException(status_code=409, detail="Nombre de usuario ya está en uso")
    if payload.email and payload.email != db_personal.email:
        if buscar_por_email(db, payload.email):
            raise HTTPException(status_code=409, detail="Email ya está en uso")

    if payload.rol == Rol.USUARIO:
        # Degradación: sale de `personal`, entra a `usuarios` -- ver
        # docstring de PersonalUpdate.rol.
        proteger_administradores(db, db_personal, current_user, eliminando=True)
        try:
            usuario = degradar_a_usuario(db, db_personal)
        except IntegrityError as exc:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No se puede degradar: esta persona todavía figura como creador/actualizador de "
                "recursos, espacios o laboratorios.",
            ) from exc
        registrar_cambio(db, current_user, "degradar", "usuario", usuario.id, f"Degradó a {usuario.username} a rol usuario")
        db.commit()
        return usuario

    rol_final = payload.rol.value if payload.rol is not None else db_personal.rol
    proteger_administradores(db, db_personal, current_user, rol_final=rol_final)
    if rol_final == "gestor":
        laboratorio_actual = db_personal.laboratorio.id if db_personal.laboratorio else None
        if payload.laboratorio_id is None and laboratorio_actual is None:
            raise HTTPException(status_code=400, detail="Debes asignar un laboratorio al gestor")
        if payload.laboratorio_id is not None and db.query(Laboratorio).filter(Laboratorio.id == payload.laboratorio_id).first() is None:
            raise HTTPException(status_code=404, detail="Laboratorio no encontrado")

    personal = actualizar_personal(db, db_personal, payload)
    registrar_cambio(db, current_user, "actualizar", "personal", personal.id, f"Actualizó el personal {personal.username}")
    db.commit()
    return personal


@router.delete("/{personal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_personal_endpoint(
    personal_id: int,
    current_user: Personal = Depends(require_admin),
    db: Session = Depends(get_db),
):
    db_personal = get_personal(db, personal_id)
    if not db_personal:
        raise HTTPException(status_code=404, detail="Personal no encontrado")
    proteger_administradores(db, db_personal, current_user, eliminando=True)

    if db_personal.supabase_id is not None:
        try:
            eliminar_usuario_supabase(db_personal.supabase_id)
        except SupabaseAdminError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"No se pudo eliminar la cuenta en Supabase: {exc}",
            ) from exc

    descripcion = f"Eliminó el personal {db_personal.username}"
    eliminar_personal(db, db_personal)
    registrar_cambio(db, current_user, "eliminar", "personal", personal_id, descripcion)
    db.commit()
    return None
