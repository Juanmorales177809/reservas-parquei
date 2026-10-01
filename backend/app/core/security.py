"""JWT de acceso, cookies de sesión y CSRF de doble envío (BK-06, API-03).

Lo que este módulo NO hace: no consulta `auth.sesiones`. Verificar que una
sesión no esté revocada o vencida exige esa tabla y es responsabilidad de
`BK-07`/`AUTH-A3` en adelante. Aquí solo vive el mecanismo — firma, cookies,
doble envío — conforme a `auth/security.md` (`SEC-JWT-*`, `SEC-SES-*`,
`SEC-CSRF-*`) y al contrato de auth §2.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
import time
from typing import Any

import bcrypt
import jwt
from fastapi import Request, Response

from app.core.config import get_settings
from app.core.errors import NoAutenticado, NoAutorizado

# --- Contraseñas (SEC-PWD-02, SEC-PWD-06) -----------------------------------
# architecture.md §3 fija bcrypt. Factor de trabajo 12: por encima del mínimo
# de 10 de SEC-PWD-06, ajustable si la capacidad del servidor lo exige.
_BCRYPT_ROUNDS = 12


def hash_contrasena(contrasena: str) -> str:
    # bcrypt trunca a 72 bytes; SEC-PWD-07 exige como máximo 64 caracteres,
    # que en UTF-8 no supera ese límite salvo con caracteres de varios bytes
    # en el extremo superior. Se acota explícitamente en vez de confiar en
    # el truncado silencioso de la librería.
    datos = contrasena.encode("utf-8")
    if len(datos) > 72:
        raise ValueError("La contraseña excede el límite de bytes de bcrypt.")
    return bcrypt.hashpw(datos, bcrypt.gensalt(rounds=_BCRYPT_ROUNDS)).decode("ascii")


def verificar_contrasena(contrasena: str, hash_almacenado: str) -> bool:
    try:
        return bcrypt.checkpw(contrasena.encode("utf-8"), hash_almacenado.encode("ascii"))
    except (ValueError, TypeError):
        # Hash corrupto o con formato inesperado: nunca autentica.
        return False


# --- Tokens de un solo uso (invitación, recuperación) — SEC-TOK-04 ---------


def generar_token() -> tuple[str, str]:
    """Devuelve `(token, hash)`. El token se entrega una sola vez; solo el
    hash se persiste (SEC-TOK-02): la base nunca puede reconstruir el token."""
    token = secrets.token_urlsafe(32)
    return token, hashear_token(token)


def hashear_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

# SEC-JWT-01: el algoritmo se fija explícitamente en el servidor; un token
# que declare alg:none o cualquier otro algoritmo se rechaza, nunca se infiere
# del propio token.
ALGORITMO = "HS256"
EMISOR = "reservas-parquei"
AUDIENCIA = "reservas-parquei-api"
TIPO_ACCESO = "access"

COOKIE_ACCESO = "rp_access"
COOKIE_REFRESH = "rp_refresh"
COOKIE_CSRF = "rp_csrf"

# "/" y no "/api": el frontend decide la sesión en el servidor (layout de `(app)`),
# y el navegador solo envía a una página las cookies cuyo Path la cubre. Con "/api"
# ninguna pantalla autenticada era alcanzable. Sigue siendo HttpOnly y Secure; el
# Path no era una frontera de seguridad (contrato de auth, §2 Cookies).
RUTA_COOKIE_ACCESO = "/"
RUTA_COOKIE_REFRESH = "/api/auth/sesiones"

ENCABEZADO_CSRF = "X-CSRF-Token"


def _secreto() -> str:
    secreto = get_settings().jwt_secret
    if not secreto:
        # Fallar aquí y no firmar con un valor por defecto conocido.
        raise RuntimeError("JWT_SECRET no está configurado.")
    return secreto


def emitir_token_acceso(sub: str, sid: str, vigencia_segundos: int | None = None) -> str:
    """Firma un JWT de acceso. Nunca incluye rol, permisos ni ámbito (SEC-JWT-04)."""
    ahora = int(time.time())
    vigencia = vigencia_segundos or get_settings().jwt_vigencia_acceso_segundos
    claims: dict[str, Any] = {
        "iss": EMISOR,
        "aud": AUDIENCIA,
        "sub": sub,
        "sid": sid,
        "typ": TIPO_ACCESO,
        "iat": ahora,
        "exp": ahora + vigencia,
    }
    return jwt.encode(claims, _secreto(), algorithm=ALGORITMO)


def verificar_token_acceso(token: str) -> dict[str, Any]:
    """Valida firma, `iss`, `aud`, `exp` y `typ` (SEC-JWT-02).

    No comprueba revocación de sesión: eso exige `auth.sesiones` y es
    responsabilidad de la capa que la consulte (SEC-JWT-05, BK-07 en
    adelante). Cualquier fallo de validación se traduce a `401
    NO_AUTENTICADO`, nunca a una excepción de la librería sin controlar.
    """
    try:
        claims = jwt.decode(
            token,
            _secreto(),
            algorithms=[ALGORITMO],  # nunca se acepta "none" ni se infiere del token
            issuer=EMISOR,
            audience=AUDIENCIA,
            options={"require": ["exp", "iat", "sub", "sid", "typ"]},
        )
    except jwt.PyJWTError:
        raise NoAutenticado("Sesión no válida.")

    if claims.get("typ") != TIPO_ACCESO:
        raise NoAutenticado("Sesión no válida.")
    return claims


# --- Cookies ------------------------------------------------------------


def emitir_cookie_acceso(response: Response, token: str, vigencia_segundos: int) -> None:
    response.set_cookie(
        COOKIE_ACCESO, token,
        max_age=vigencia_segundos, httponly=True, secure=get_settings().cookie_secure,
        samesite="lax", path=RUTA_COOKIE_ACCESO,
    )


def emitir_cookie_refresh(response: Response, secreto: str, vigencia_segundos: int) -> None:
    response.set_cookie(
        COOKIE_REFRESH, secreto,
        max_age=vigencia_segundos, httponly=True, secure=get_settings().cookie_secure,
        samesite="lax", path=RUTA_COOKIE_REFRESH,
    )


def borrar_cookies_sesion(response: Response) -> None:
    response.delete_cookie(COOKIE_ACCESO, path=RUTA_COOKIE_ACCESO)
    response.delete_cookie(COOKIE_REFRESH, path=RUTA_COOKIE_REFRESH)


# --- CSRF de doble envío (SEC-CSRF-01, SEC-CSRF-02) ----------------------


def asegurar_cookie_csrf(request: Request, response: Response) -> None:
    """`GET /api/auth/csrf`: conserva la cookie vigente o emite una nueva.

    El navegador ya descarta una cookie vencida antes de reenviarla, así que
    "vencida" equivale a "ausente" desde el servidor: no hace falta estado
    adicional para distinguirlas.
    """
    if request.cookies.get(COOKIE_CSRF):
        return
    token = secrets.token_urlsafe(32)
    response.set_cookie(
        COOKIE_CSRF, token,
        max_age=get_settings().csrf_vigencia_segundos,
        httponly=False,  # rp_csrf es el único valor que el cliente debe leer
        secure=get_settings().cookie_secure, samesite="lax", path="/",
    )


def exigir_csrf(request: Request) -> None:
    """Dependencia para toda escritura: doble envío obligatorio (SEC-CSRF-01/02).

    Se aplica también a los endpoints públicos de sesión: el token se
    obtiene antes mediante `GET /api/auth/csrf`, que no exige sesión previa.
    """
    del_cookie = request.cookies.get(COOKIE_CSRF)
    encabezado = request.headers.get(ENCABEZADO_CSRF)
    if not del_cookie or not encabezado or not hmac.compare_digest(del_cookie, encabezado):
        raise NoAutorizado("Falta o no coincide el encabezado X-CSRF-Token.")
