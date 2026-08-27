import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.auth.auth import NOMBRE_COOKIE_ACCESO, atributos_cookie_acceso, max_age_cookie_acceso
from app.crud.usuarios import get_usuario_by_supabase_id
from app.db import get_db
from app.deps import decode_token
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
    # Reusa el mismo decodificador que `deps.py` (ES256 vía JWKS público de
    # Supabase, con HS256 como fallback solo para tests) -- antes este
    # endpoint tenía su propia verificación duplicada, siempre HS256, y
    # rechazaba con 401 CUALQUIER login real: un proyecto de Supabase real
    # firma con ES256, nunca con el secreto compartido legado. Confirmado
    # corriendo el flujo completo contra un proyecto real el 2026-08-27.
    # El mensaje de error se preserva tal cual (pineado en
    # test_api_auth.py y test_exception_handler.py) envolviendo el 401
    # genérico de `decode_token` con el propio de este endpoint.
    try:
        claims = decode_token(payload.supabase_token)
    except HTTPException as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de Supabase inválido") from exc
    sub = claims.get("sub")
    if sub is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de Supabase inválido")
    try:
        supabase_id = uuid.UUID(str(sub))
    except ValueError as exc:
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
