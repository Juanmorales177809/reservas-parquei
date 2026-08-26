from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.auth.auth import (
    NOMBRE_COOKIE_ACCESO,
    atributos_cookie_acceso,
    create_access_token,
    hash_password,
    max_age_cookie_acceso,
    verify_password,
)
from app.config import settings
from app.crud.usuarios import get_usuario_by_email, get_usuario_by_username
from app.db import get_db
from app.deps import get_current_user
from app.models.usuario import Usuario
from app.schemas.usuario import (
    CambiarPasswordRequest,
    LoginResponse,
    RestablecerPasswordRequest,
    SolicitarRecuperacionRequest,
    SupabaseSesionRequest,
    UsuarioLogin,
    UsuarioResponse,
)
from app.services.email import encolar_correo, procesar_pendientes
from app.services.rate_limit import limitador_login, limitador_recuperacion
from app.services.recuperacion import recuperacion_password


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

    # Scopes OAuth2 (aditivo, sin romper): se emiten junto a rol/role para exigencias externas.
    # Jerarquía: admin implica gestor y usuario, gestor implica usuario.
    scopes_por_rol = {
        "admin": ["admin:*", "gestor:*", "usuario:*"],
        "gestor": ["gestor:*", "usuario:*"],
        "usuario": ["usuario:*"],
    }
    scopes = scopes_por_rol.get(usuario.rol, ["usuario:*"])
    # Compatibilidad: algunos validadores leen `scope` (string space-separated) y otros `scopes` (lista).
    access_token = create_access_token(
        data={
            "sub": str(usuario.id),
            "rol": usuario.rol,
            "role": usuario.rol,
            "scope": " ".join(scopes),
            "scopes": scopes,
        }
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


def _usuario_por_identificador(db: Session, identificador: str) -> Usuario | None:
    return get_usuario_by_username(db, identificador) or get_usuario_by_email(db, identificador)


@router.post("/cambiar-password", status_code=status.HTTP_204_NO_CONTENT)
def cambiar_password(
    payload: CambiarPasswordRequest,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """Fija una contraseña definitiva. Cubre dos casos con el mismo
    endpoint: el cambio obligatorio tras recibir una temporal (alta de
    usuario o recuperación, `debe_cambiar_password=true`) y el autoservicio
    voluntario de cualquier usuario -- que hoy tampoco existía.

    Exige la contraseña ACTUAL como confirmación (aunque sea la temporal
    recién recibida por correo): una sesión ya autenticada no debe poder
    cambiarla sin que quien la usa la conozca.
    """
    if not verify_password(payload.password_actual, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="La contraseña actual es incorrecta")
    current_user.hashed_password = hash_password(payload.password_nueva)
    current_user.debe_cambiar_password = False
    db.add(current_user)
    db.commit()


@router.post("/recuperar", status_code=status.HTTP_204_NO_CONTENT)
def solicitar_recuperacion(
    payload: SolicitarRecuperacionRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> None:
    """Solicita un código de recuperación por correo.

    La respuesta es SIEMPRE 204 sin cuerpo, exista o no el identificador --
    mismo criterio anti-enumeración que ya prueba `TestNoFiltraExistenciaDeUsuario`
    para /auth/login. Cada pedido (exista o no el usuario) cuenta contra
    `limitador_recuperacion`: sin esto, alguien podría bombardear de correos
    de recuperación a un usuario real sin límite -- acá no hay "éxito" que
    deba resetear el contador, a diferencia del login.
    """
    ip = request.client.host if request.client else "desconocido"
    if limitador_recuperacion.bloqueado(ip, payload.identificador):
        return
    limitador_recuperacion.registrar_fallo(ip, payload.identificador)

    usuario = _usuario_por_identificador(db, payload.identificador)
    if usuario is None or not settings.email_enabled:
        return
    codigo = recuperacion_password.generar_codigo(usuario.id)
    encolar_correo(
        db,
        destinatario=usuario.email,
        asunto="Código para recuperar tu contraseña",
        cuerpo=(
            f"Hola {usuario.username},\n\n"
            f"Tu código para restablecer la contraseña es: {codigo}\n"
            "Vence en 15 minutos. Si no lo solicitaste, podés ignorar este correo."
        ),
    )
    db.commit()
    procesar_pendientes(db)


@router.post("/restablecer", status_code=status.HTTP_204_NO_CONTENT)
def restablecer_password(
    payload: RestablecerPasswordRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> None:
    """Aplica el código de recuperación. A diferencia de /auth/recuperar,
    acá sí hay un "éxito" real (código correcto) que reinicia el contador
    de intentos -- mismo patrón exacto que /auth/login."""
    ip = request.client.host if request.client else "desconocido"
    if limitador_recuperacion.bloqueado(ip, payload.identificador):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Demasiados intentos. Espera unos minutos e inténtalo de nuevo.",
        )

    usuario = _usuario_por_identificador(db, payload.identificador)
    if usuario is None or not recuperacion_password.verificar_codigo(usuario.id, payload.codigo):
        limitador_recuperacion.registrar_fallo(ip, payload.identificador)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Código inválido o vencido")

    limitador_recuperacion.reiniciar(ip, payload.identificador)
    usuario.hashed_password = hash_password(payload.password_nueva)
    usuario.debe_cambiar_password = False
    db.add(usuario)
    db.commit()


@router.post("/supabase/sesion", response_model=LoginResponse)
def supabase_sesion(
    payload: SupabaseSesionRequest,
    response: Response,
    db: Session = Depends(get_db),
) -> LoginResponse:
    """Intercambia un JWT de Supabase por sesión de cookie (hybrid).

    Con SUPABASE_ENABLED=false responde 404 para no exponer superficie
    nueva. Con true: verifica el JWT con SUPABASE_JWT_SECRET (aud sin
    verificar, ver deps._decode_token), extrae sub=UUID + email, busca
    Usuario por supabase_id o por email (auto-link), o crea uno nuevo con
    rol usuario si no existe -- institucional sin recursos: alta abierta
    pero sin privilegios. El JWT de Supabase se fija tal cual como cookie
    `access_token`; el resto de la API lo verifica vía deps hybrid.
    """
    if not settings.supabase_enabled or not settings.supabase_jwt_secret:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supabase Auth no habilitado")
    # Verificación con el mismo criterio que deps._decode_token (aud no verificado).
    try:
        from jose import JWTError, jwt as jose_jwt
        import uuid as _uuid

        claims = jose_jwt.decode(
            payload.supabase_token, settings.supabase_jwt_secret, algorithms=[settings.algorithm], options={"verify_aud": False}
        )
        sub = claims.get("sub")
        email = claims.get("email")
        if sub is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de Supabase inválido")
        try:
            supa_uuid = _uuid.UUID(str(sub))
        except ValueError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de Supabase inválido")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de Supabase inválido")

    usuario = db.query(Usuario).filter(Usuario.supabase_id == supa_uuid).first()
    if usuario is None and email:
        usuario = get_usuario_by_email(db, str(email))
        if usuario is not None:
            # Auto-link en el primer login con Supabase (migración progresiva).
            usuario.supabase_id = supa_uuid
            db.add(usuario)
            db.commit()
            db.refresh(usuario)
    if usuario is None:
        # Alta automática institucional: sin privilegios (usuario base).
        # Username derivado de email para no colisionar con existentes.
        if not email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El token de Supabase no trae email")
        base_username = str(email).split("@")[0][:80]
        username = base_username
        suffix = 0
        while get_usuario_by_username(db, username) is not None:
            suffix += 1
            username = f"{base_username[:70]}{suffix}"[:80]
            if suffix > 1000:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No se pudo generar username")
        # Password aleatoria: nunca se usa (login es via Supabase), pero el
        # modelo exige hashed_password. Se genera y se marca debe_cambiar=false.
        import secrets

        temp_pw = secrets.token_urlsafe(12)
        usuario = Usuario(
            username=username,
            email=str(email),
            hashed_password=hash_password(temp_pw),
            rol="usuario",
            supabase_id=supa_uuid,
            debe_cambiar_password=False,
        )
        db.add(usuario)
        db.commit()
        db.refresh(usuario)

    response.set_cookie(
        key=NOMBRE_COOKIE_ACCESO,
        value=payload.supabase_token,
        max_age=max_age_cookie_acceso(),
        **atributos_cookie_acceso(),
    )
    return LoginResponse(user=UsuarioResponse.model_validate(usuario))
