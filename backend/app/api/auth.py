import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from jose import JWTError, jwt as jose_jwt
from sqlalchemy.orm import Session

from app.auth.auth import NOMBRE_COOKIE_ACCESO, atributos_cookie_acceso, max_age_cookie_acceso
from app.config import settings
from app.crud.usuarios import get_usuario_by_supabase_id
from app.db import get_db
from app.schemas.usuario import LoginResponse, SupabaseSesionRequest, UsuarioResponse


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response) -> None:
    """Cierra la sesión de cookie.

    Idempotente: no falla si no existe una cookie previa. No exige
    autenticación — debe poder limpiar una cookie inválida o expirada sin
    requerir que el cliente tenga un token válido.
    """
    response.delete_cookie(key=NOMBRE_COOKIE_ACCESO, **atributos_cookie_acceso())


@router.post("/supabase/sesion", response_model=LoginResponse)
def supabase_sesion(
    payload: SupabaseSesionRequest,
    response: Response,
    db: Session = Depends(get_db),
) -> LoginResponse:
    """Intercambia un JWT de Supabase (ya autenticado contra Supabase Cloud
    por el cliente) por la cookie de sesión `HttpOnly` de siempre.

    Este endpoint SOLO busca por `usuarios.supabase_id` ya existente —
    NUNCA crea un usuario nuevo ni vincula por email. La única forma de que
    una cuenta exista acá es que un admin la haya invitado antes
    (`app/api/usuarios.py::create_usuario_admin`, vía
    `app/services/supabase_admin.py`). Esto es deliberado: una versión
    anterior de este mismo endpoint auto-vinculaba por email cualquier JWT
    válido a una cuenta existente (incluido un admin) sin ningún control —
    era una vía de apropiación de cuenta para cualquiera que pudiera
    registrarse en el proyecto de Supabase con ese email. No reintroducir
    esa lógica.
    """
    try:
        claims = jose_jwt.decode(
            payload.supabase_token,
            settings.supabase_jwt_secret,
            algorithms=[settings.algorithm],
            options={"verify_aud": False},
        )
        sub = claims.get("sub")
        if sub is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de Supabase inválido")
        supabase_id = uuid.UUID(str(sub))
    except HTTPException:
        raise
    except (JWTError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de Supabase inválido") from exc

    usuario = get_usuario_by_supabase_id(db, supabase_id)
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta cuenta de Supabase no está asociada a ningún usuario. Pedile a un administrador que te cree la cuenta.",
        )

    response.set_cookie(
        key=NOMBRE_COOKIE_ACCESO,
        value=payload.supabase_token,
        max_age=max_age_cookie_acceso(),
        **atributos_cookie_acceso(),
    )
    return LoginResponse(user=UsuarioResponse.model_validate(usuario))
