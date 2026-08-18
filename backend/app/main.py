import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.api import admin_dashboard, auth, control_cambios, espacios, notificaciones, recursos, reservas, usuarios, zonas
from app.auth.auth import hash_password
from app.config import settings
from app.db import Base, engine, SessionLocal
from app import models  # noqa: F401
from app.middleware.request_id import HEADER, RequestIdMiddleware, resolver_request_id
from app.migrations import migrate_resource_reservations


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Orden conservado: create_all → migraciones → seed. Idempotente.
    Base.metadata.create_all(bind=engine)
    migrate_resource_reservations()
    seed_admin_user()
    yield
    # engine.dispose() solo cierra conexiones del pool; el engine global de
    # app.db sigue siendo utilizable después (nuevas conexiones al usarlo).
    engine.dispose()


app = FastAPI(
    title="Gestión de Reservas de Recursos Institucionales",
    description="API para gestionar recursos y sus reservas",
    version="1.0.0",
    lifespan=lifespan,
)

# Request ID: primer middleware (más externo del stack, ver
# app/middleware/request_id.py): resuelve/valida el X-Request-ID y lo agrega a
# toda respuesta normal y controlada.
app.add_middleware(RequestIdMiddleware)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    # False porque el JWT viaja en la cabecera Authorization (frontend/src/services/api.ts),
    # nunca en cookies: no hay credencial que el navegador deba adjuntar automáticamente.
    allow_credentials=False,
    # Únicos verbos que emite el frontend (frontend/src/services/*.ts); GET es
    # el default de fetch cuando no se especifica method.
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    # Únicas cabeceras que agrega apiFetch (frontend/src/services/api.ts).
    allow_headers=["Content-Type", "Authorization"],
)

# Rutas de documentación interactiva: Swagger UI/ReDoc cargan script/CSS desde
# cdn.jsdelivr.net e inyectan un <script> inline de inicialización, incompatibles
# con la CSP restrictiva del resto de la API. Se excluyen solo de esa cabecera.
_RUTAS_SIN_CSP = {"/docs", "/redoc"}


@app.middleware("http")
async def agregar_cabeceras_seguridad(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if request.url.path not in _RUTAS_SIN_CSP:
        response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
    if settings.environment == "production":
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    return response


_logger_errores = logging.getLogger("app.errores_no_controlados")
_MENSAJE_ERROR_GENERICO = "Ha ocurrido un error interno. Inténtalo de nuevo más tarde."


@app.exception_handler(Exception)
async def manejar_excepcion_no_controlada(request: Request, exc: Exception) -> JSONResponse:
    """Único punto de salida para cualquier excepción que ninguna capa
    superior atrapó. FastAPI ya registra handlers específicos y más
    concretos para HTTPException y RequestValidationError (401/403/404/409/
    422/429 entre otros): esos siguen resolviéndose con ese handler propio,
    nunca con este, así que su comportamiento no cambia.

    Log: método, ruta, request_id y tipo de excepción en el mensaje, más el
    traceback completo vía exc_info — todo queda solo en el log del servidor,
    nunca en la respuesta. No se registra el cuerpo de la petición, headers,
    Authorization ni ninguna credencial.

    Respuesta al cliente: siempre 500 con un mensaje genérico y estable,
    igual sin importar el tipo de excepción real, para no filtrar detalles
    internos ni permitir distinguir un tipo de fallo de otro. Incluye el
    X-Request-ID de la petición (el mismo que registró el middleware en
    request.state y que se anotó en el log), sin alterar el body genérico.
    """
    request_id = getattr(request.state, "request_id", None) or resolver_request_id(None)
    _logger_errores.error(
        "Excepción no controlada en %s %s [request_id=%s]: %s",
        request.method,
        request.url.path,
        request_id,
        type(exc).__name__,
        exc_info=exc,
    )
    respuesta = JSONResponse(status_code=500, content={"detail": _MENSAJE_ERROR_GENERICO})
    respuesta.headers[HEADER] = request_id
    return respuesta


@app.get("/", tags=["health"])
def read_root():
    return {"mensaje": "Bienvenido al sistema de gestión de reservas de recursos institucionales"}


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}


def seed_admin_user() -> None:
    db: Session = SessionLocal()
    try:
        from app.models.usuario import Usuario
        from app.initial_data.espacios import init_espacios

        # Poblar espacios iniciales
        init_espacios(db)

        admin = db.query(Usuario).filter(Usuario.rol == "admin").first()
        admin_username = settings.initial_admin_username
        admin_email = settings.initial_admin_email
        admin_password = settings.initial_admin_password
        if admin is not None or admin_username is None:
            return
        # Settings.validate() guarantees that the remaining values are present.
        assert admin_email is not None
        assert admin_password is not None

        existing_identity = (
            db.query(Usuario)
            .filter(
                (Usuario.username == admin_username)
                | (Usuario.email == admin_email)
            )
            .first()
        )
        if existing_identity is not None:
            raise RuntimeError(
                "No se pudo crear el administrador inicial: el usuario o email ya existe"
            )

        db.add(
            Usuario(
                username=admin_username,
                email=admin_email,
                hashed_password=hash_password(admin_password),
                rol="admin",
            )
        )
        db.commit()
    finally:
        db.close()


# Incluir routers
app.include_router(auth.router)
app.include_router(admin_dashboard.router)
app.include_router(admin_dashboard.gestion_router)
app.include_router(control_cambios.router)
app.include_router(usuarios.router)
app.include_router(espacios.router)
app.include_router(recursos.router)
app.include_router(zonas.router)
app.include_router(reservas.router)
app.include_router(notificaciones.router)
