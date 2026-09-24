"""Envolvente de error común y catálogo compartido (BK-04, API-01).

Toda respuesta de error tiene la forma `{"error": {"codigo", "mensaje",
"detalles"}}`, conforme a `specs/contratos/README.md` §2. `detalles` nunca
contiene trazas, SQL ni variables de entorno (`SEC-INF-04`).

Un módulo lanza `DomainError` con su propio código cuando el catálogo común
no lo cubre; no redefine el significado de un código común existente.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("reservas.errores")


class DomainError(Exception):
    """Error de dominio con su código, mensaje y estado HTTP ya resueltos."""

    def __init__(
        self,
        status_code: int,
        codigo: str,
        mensaje: str,
        detalles: list | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.status_code = status_code
        self.codigo = codigo
        self.mensaje = mensaje
        self.detalles = detalles or []
        self.headers = headers or {}
        super().__init__(mensaje)


# --- Catálogo común de specs/contratos/README.md §2 -------------------------
# Una subclase por código para que los módulos no repitan el status HTTP.


class SolicitudInvalida(DomainError):
    def __init__(self, mensaje: str, detalles: list | None = None) -> None:
        super().__init__(400, "SOLICITUD_INVALIDA", mensaje, detalles)


class NoAutenticado(DomainError):
    def __init__(self, mensaje: str = "Se requiere una sesión válida.") -> None:
        super().__init__(401, "NO_AUTENTICADO", mensaje)


class CredencialesInvalidas(DomainError):
    def __init__(self, mensaje: str = "Credenciales inválidas.") -> None:
        super().__init__(401, "CREDENCIALES_INVALIDAS", mensaje)


class ReautenticacionRequerida(DomainError):
    def __init__(self, mensaje: str = "Esta operación exige autenticación reciente.") -> None:
        super().__init__(401, "REAUTENTICACION_REQUERIDA", mensaje)


class NoAutorizado(DomainError):
    def __init__(self, mensaje: str = "No autorizado.") -> None:
        super().__init__(403, "NO_AUTORIZADO", mensaje)


class PerfilInicialPendiente(DomainError):
    def __init__(self, mensaje: str = "Debe completar la actualización inicial de su perfil.") -> None:
        super().__init__(403, "PERFIL_INICIAL_PENDIENTE", mensaje)


class VinculacionRequerida(DomainError):
    def __init__(self, mensaje: str = "No conserva ninguna vinculación activa y válida.") -> None:
        super().__init__(403, "VINCULACION_REQUERIDA", mensaje)


class NoEncontrado(DomainError):
    def __init__(self, mensaje: str = "Recurso no encontrado.") -> None:
        super().__init__(404, "NO_ENCONTRADO", mensaje)


class Conflicto(DomainError):
    def __init__(self, mensaje: str, detalles: list | None = None) -> None:
        super().__init__(409, "CONFLICTO", mensaje, detalles)


class UnidadIncompatible(DomainError):
    def __init__(self, mensaje: str) -> None:
        super().__init__(409, "UNIDAD_INCOMPATIBLE", mensaje)


class TokenNoVigente(DomainError):
    def __init__(self, mensaje: str = "El token no es vigente.") -> None:
        super().__init__(410, "TOKEN_NO_VIGENTE", mensaje)


class Validacion(DomainError):
    def __init__(self, mensaje: str, detalles: list | None = None) -> None:
        super().__init__(422, "VALIDACION", mensaje, detalles)


class DemasiadosIntentos(DomainError):
    def __init__(self, mensaje: str = "Demasiados intentos.", retry_after: int | None = None) -> None:
        headers = {"Retry-After": str(retry_after)} if retry_after is not None else {}
        super().__init__(429, "DEMASIADOS_INTENTOS", mensaje, headers=headers)


def _envolver(status_code: int, codigo: str, mensaje: str, detalles: list, headers: dict | None = None) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"codigo": codigo, "mensaje": mensaje, "detalles": detalles}},
        headers=headers or {},
    )


def registrar_manejadores(app: FastAPI) -> None:
    """Instala los manejadores de excepción. Se llama una vez desde main.py."""

    @app.exception_handler(DomainError)
    async def _domain_error(_: Request, exc: DomainError) -> JSONResponse:
        return _envolver(exc.status_code, exc.codigo, exc.mensaje, exc.detalles, exc.headers)

    @app.exception_handler(RequestValidationError)
    async def _validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        # Los detalles de pydantic son ubicación y tipo de campo, nunca el
        # valor enviado por el cliente ni información del servidor.
        detalles = [
            {"campo": ".".join(str(p) for p in e["loc"] if p != "body"), "motivo": e["msg"]}
            for e in exc.errors()
        ]
        return _envolver(422, "VALIDACION", "Uno o más campos no son válidos.", detalles)

    @app.exception_handler(StarletteHTTPException)
    async def _http_error(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        # Ruta inexistente o método no admitido: FastAPI los produce solo,
        # antes de llegar a ningún router.
        if exc.status_code == 404:
            return _envolver(404, "NO_ENCONTRADO", "Recurso no encontrado.", [])
        if exc.status_code == 405:
            return _envolver(404, "NO_ENCONTRADO", "Recurso no encontrado.", [])
        mensaje = exc.detail if isinstance(exc.detail, str) else "Error de solicitud."
        return _envolver(exc.status_code, "SOLICITUD_INVALIDA", mensaje, [])

    @app.exception_handler(Exception)
    async def _error_no_controlado(_: Request, exc: Exception) -> JSONResponse:
        # Se registra en el log del servidor, nunca en la respuesta (SEC-INF-04).
        logger.exception("Error no controlado")
        return _envolver(500, "ERROR_INTERNO", "Ocurrió un error inesperado.", [])
