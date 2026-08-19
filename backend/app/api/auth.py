from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.auth.auth import (
    NOMBRE_COOKIE_ACCESO,
    atributos_cookie_acceso,
    create_access_token,
    max_age_cookie_acceso,
    verify_password,
)
from app.crud.usuarios import get_usuario_by_username
from app.db import get_db
from app.schemas.usuario import LoginResponse, UsuarioLogin, UsuarioResponse
from app.services.rate_limit import limitador_login


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: UsuarioLogin, request: Request, response: Response, db: Session = Depends(get_db)):
    # Sin X-Forwarded-For: no hay proxy confiable configurado en este
    # despliegue (ver app/services/rate_limit.py). request.client es la
    # conexión TCP directa.
    ip = request.client.host if request.client else "desconocido"

    # Se comprueba antes de tocar la base y sin registrar nada: un cliente
    # ya bloqueado no debe poder extender su propio bloqueo reintentando.
    if limitador_login.bloqueado(ip, payload.username):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Demasiados intentos. Espera unos minutos e inténtalo de nuevo.",
        )

    usuario = get_usuario_by_username(db, payload.username)
    if usuario is None:
        limitador_login.registrar_fallo(ip, payload.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
        )

    if not verify_password(payload.password, usuario.hashed_password):
        limitador_login.registrar_fallo(ip, payload.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
        )

    limitador_login.reiniciar(ip, payload.username)

    access_token = create_access_token(
        data={"sub": str(usuario.id), "rol": usuario.rol, "role": usuario.rol}
    )
    # Fase 9G (cookie-only): la cookie HttpOnly es el único mecanismo de
    # sesión. El body devuelve únicamente el usuario; `access_token` ya no
    # se expone (el frontend solo leía `data.user` desde la Fase 9F-B).
    response.set_cookie(
        key=NOMBRE_COOKIE_ACCESO,
        value=access_token,
        max_age=max_age_cookie_acceso(),
        **atributos_cookie_acceso(),
    )
    return LoginResponse(user=UsuarioResponse.model_validate(usuario))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response) -> None:
    """Cierra la sesión de cookie (Fase 9F-A).

    Idempotente: no falla si no existe una cookie previa. No exige
    autenticación — debe poder limpiar una cookie inválida o expirada sin
    requerir que el cliente tenga un token válido.
    """
    response.delete_cookie(key=NOMBRE_COOKIE_ACCESO, **atributos_cookie_acceso())
