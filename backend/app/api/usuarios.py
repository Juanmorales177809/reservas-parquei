from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.crud.usuarios import create_usuario, get_usuario_by_email, get_usuario_by_username, get_usuarios, get_usuario, update_usuario, delete_usuario
from app.db import get_db
from app.deps import get_current_user, require_admin
from app.models.espacio import Espacio
from app.models.usuario import Usuario
from app.schemas.usuario import AdminUsuarioCreate, UsuarioResponse, UsuarioUpdate
from app.services.auditoria import registrar_cambio
from app.services.supabase_admin import SupabaseAdminError, invitar_usuario


router = APIRouter(prefix="/usuarios", tags=["usuarios"])
ADMIN_LOCK_ID = 728_341


def proteger_administradores(
    db: Session,
    usuario_objetivo: Usuario,
    current_user: Usuario,
    rol_final: str | None = None,
    eliminando: bool = False,
) -> None:
    if usuario_objetivo.rol != "admin":
        return
    if not eliminando and rol_final == "admin":
        return
    if usuario_objetivo.id == current_user.id:
        accion = "eliminar" if eliminando else "cambiar el rol de"
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"No puedes {accion} tu propia cuenta administrativa",
        )

    # Serializa cambios de rol y eliminaciones para que dos solicitudes
    # concurrentes no puedan dejar el sistema sin administradores.
    db.execute(text("SELECT pg_advisory_xact_lock(:lock_id)"), {"lock_id": ADMIN_LOCK_ID})
    administradores = db.query(Usuario).filter(Usuario.rol == "admin").count()
    if administradores <= 1:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Debe permanecer al menos un administrador en el sistema",
        )


@router.get("/me", response_model=UsuarioResponse)
def get_me(current_user: Usuario = Depends(get_current_user)):
    return current_user


@router.get("", response_model=list[UsuarioResponse])
def list_usuarios(
    current_user: Usuario = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return get_usuarios(db)


@router.post("", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def create_usuario_admin(
    payload: AdminUsuarioCreate,
    current_user: Usuario = Depends(require_admin),
    db: Session = Depends(get_db),
):
    if get_usuario_by_username(db, payload.username) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El nombre de usuario ya está registrado",
        )
    if get_usuario_by_email(db, payload.email) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El email ya está registrado",
        )

    if payload.rol == "gestor":
        if payload.espacio_id is None:
            raise HTTPException(status_code=400, detail="Debes asignar un espacio al gestor")
        if db.query(Espacio).filter(Espacio.id == payload.espacio_id).first() is None:
            raise HTTPException(status_code=404, detail="Espacio no encontrado")

    # La identidad de autenticación la crea Supabase, no este backend: se
    # invita por email y Supabase manda SU PROPIO correo con el link para
    # que la persona fije su contraseña. `supabase_id` se guarda de una,
    # en el mismo momento -- es la única forma en que puede llegar a
    # existir (ver el docstring de supabase_sesion en app/api/auth.py:
    # ese endpoint solo busca, nunca crea ni vincula).
    try:
        supabase_id = invitar_usuario(payload.email)
    except SupabaseAdminError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"No se pudo crear la cuenta en Supabase: {exc}",
        ) from exc

    usuario = create_usuario(db, payload, supabase_id)
    registrar_cambio(db, current_user, "crear", "usuario", usuario.id, f"Creó el usuario {usuario.username} con rol {usuario.rol}")
    db.commit()
    return usuario


@router.put("/{usuario_id}", response_model=UsuarioResponse)
def update_usuario_endpoint(
    usuario_id: int,
    payload: UsuarioUpdate,
    current_user: Usuario = Depends(require_admin),
    db: Session = Depends(get_db),
):
    db_user = get_usuario(db, usuario_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
    if payload.username and payload.username != db_user.username:
        if get_usuario_by_username(db, payload.username):
            raise HTTPException(status_code=409, detail="Nombre de usuario ya está en uso")
            
    if payload.email and payload.email != db_user.email:
        if get_usuario_by_email(db, payload.email):
            raise HTTPException(status_code=409, detail="Email ya está en uso")

    rol_final = payload.rol or db_user.rol
    proteger_administradores(db, db_user, current_user, rol_final=rol_final)
    if rol_final == "gestor":
        espacio_actual = db_user.espacio.id if db_user.espacio else None
        if payload.espacio_id is None and espacio_actual is None:
            raise HTTPException(status_code=400, detail="Debes asignar un espacio al gestor")
        if payload.espacio_id is not None and db.query(Espacio).filter(Espacio.id == payload.espacio_id).first() is None:
            raise HTTPException(status_code=404, detail="Espacio no encontrado")
            
    usuario = update_usuario(db, db_user, payload)
    registrar_cambio(db, current_user, "actualizar", "usuario", usuario.id, f"Actualizó el usuario {usuario.username}")
    db.commit()
    return usuario


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_usuario_endpoint(
    usuario_id: int,
    current_user: Usuario = Depends(require_admin),
    db: Session = Depends(get_db),
):
    db_user = get_usuario(db, usuario_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    proteger_administradores(db, db_user, current_user, eliminando=True)
        
    descripcion = f"Eliminó el usuario {db_user.username}"
    delete_usuario(db, db_user)
    registrar_cambio(db, current_user, "eliminar", "usuario", usuario_id, descripcion)
    db.commit()
    return None
