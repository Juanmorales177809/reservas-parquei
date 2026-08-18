# -*- coding: utf-8 -*-
"""Middleware de Request ID (Fase "Request ID y trazabilidad").

Contrato (aprobado, ver `backend/app/middleware/README.md`):
- Lee el header `X-Request-ID` de la petición.
- Normaliza: `strip` + minúsculas.
- Acepta solamente el UUID canónico `^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$`.
- Si falta, excede 128 caracteres o no coincide: genera un `uuid4` nuevo.
- Guarda el id en `request.state.request_id`.
- Agrega `X-Request-ID` a toda respuesta normal y controlada (respuestas de
  rutas y de errores HTTP controlados 4xx/422; el 500 lo cubre el handler
  global de `backend/app/main.py`, que lee `request.state.request_id` y
  agrega el mismo id al log y al header de la respuesta).

Sin access log adicional, sin ContextVar, sin documentación en OpenAPI.

Nunca registra `Authorization`, cookies, tokens, contraseñas, cuerpos ni
headers completos: este módulo solo lee un header (`X-Request-ID`) y no emite
ningún log propio.
"""

import re
import uuid

from starlette.datastructures import MutableHeaders
from starlette.requests import Request

HEADER = "X-Request-ID"
MAXIMO_LONGITUD = 128
_UUID_CANONICO = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
)


def resolver_request_id(valor_entrante: str | None) -> str:
    """Resuelve el id de la petición según el contrato.

    Devuelve el header entrante si, tras `strip` y normalización a minúsculas,
    es un UUID canónico; en caso contrario (ausente, vacío, más de 128
    caracteres o que no coincide con el patrón) devuelve un `uuid4` nuevo.
    """
    if not valor_entrante:
        return str(uuid.uuid4())
    normalizado = valor_entrante.strip().lower()
    if len(normalizado) > MAXIMO_LONGITUD:
        return str(uuid.uuid4())
    if not _UUID_CANONICO.match(normalizado):
        return str(uuid.uuid4())
    return normalizado


class RequestIdMiddleware:
    """ASGI: resuelve el id de la petición e inyecta el header en toda
    respuesta que atraviese el middleware (normales y errores controlados).

    Registrado como el primer middleware de `app` (`add_middleware` antes que
    CORS): en el stack de Starlette queda por fuera de los demás middleware de
    usuario y del `ExceptionMiddleware`, por lo que ve las respuestas de
    rutas, de validación (422) y de errores HTTP controlados (401/403/409/429),
    y le agrega el header. El 500 no atraviesa el wrapper (lo genera el
    `ServerErrorMiddleware`, más externo): ese caso lo cubre
    `manejar_excepcion_no_controlada` en `backend/app/main.py`.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope)
        request_id = resolver_request_id(request.headers.get(HEADER))
        request.state.request_id = request_id

        async def enriquecer_respuesta(message):
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers[HEADER] = request_id
            await send(message)

        await self.app(scope, receive, enriquecer_respuesta)