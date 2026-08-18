from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.auth.auth import create_access_token, verify_password
from app.crud.usuarios import get_usuario_by_username
from app.db import get_db
from app.schemas.usuario import UsuarioLogin, UsuarioResponse, TokenResponse
from app.services.rate_limit import limitador_login


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: UsuarioLogin, request: Request, db: Session = Depends(get_db)):
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
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UsuarioResponse.model_validate(usuario),
    )
