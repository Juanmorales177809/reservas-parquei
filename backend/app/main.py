from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI
from sqlalchemy import text

from app.core.errors import registrar_manejadores
from app.db.session import SessionLocal, engine
from app.modules.administration.router_auditoria import router as auditoria_router
from app.modules.administration.router_estructura import router_cargos, router_unidades
from app.modules.administration.router_importaciones import router as importaciones_router
from app.modules.administration.router_permisos import router as permisos_router
from app.modules.auth.router import router as auth_router
from app.modules.auth.router_cuentas import router as auth_cuentas_router
from app.modules.auth.router_invitaciones import router as auth_invitaciones_router
from app.modules.espacios.router import router as espacios_router
from app.modules.notifications.router import router as notificaciones_router
from app.modules.reports.router import router as reportes_router
from app.modules.researchs.router import router as investigacion_router
from app.modules.reservations.router import router as reservas_router
from app.modules.resources.router import router_laboratorios, router_recursos
from app.modules.usuarios.router import router as perfil_router
from app.modules.usuarios.router_admin import router_personal, router_usuarios


async def _bucle_transiciones() -> None:
    """API-16: avanza espacio/interno por horario cada 60 s, en este proceso.
    Cada tick abre su propia sesión; un fallo se registra y no tumba el ciclo."""
    import asyncio
    import logging

    from app.modules.reservations.transiciones import avanzar_por_horario

    logger = logging.getLogger("reservas.transiciones")
    while True:
        try:
            await asyncio.sleep(60)
            db = SessionLocal()
            try:
                avanzar_por_horario(db, datetime.now(timezone.utc))
            finally:
                db.close()
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Fallo el tick de transiciones automáticas")


async def _bucle_notificaciones() -> None:
    """API-18/UF-NOT-03: entrega y recordatorios cada 30 s (< 1 min, la
    espera más corta de RN-COR-03). Sesión propia por tick."""
    import asyncio
    import logging

    from app.modules.notifications.entrega import procesar_pendientes
    from app.modules.notifications.recordatorio import revisar_recordatorios

    logger = logging.getLogger("reservas.notificaciones")
    while True:
        try:
            await asyncio.sleep(30)
            db = SessionLocal()
            try:
                procesar_pendientes(db)
                revisar_recordatorios(db, datetime.now(timezone.utc))
            finally:
                db.close()
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Fallo el tick de notificaciones")


@asynccontextmanager
async def _ciclo_vida(_app: FastAPI):
    import asyncio

    transiciones = asyncio.create_task(_bucle_transiciones())
    notificaciones = asyncio.create_task(_bucle_notificaciones())
    try:
        yield
    finally:
        transiciones.cancel()
        notificaciones.cancel()


app = FastAPI(title="Reservas Parquei", lifespan=_ciclo_vida)
registrar_manejadores(app)
app.include_router(auth_router)
app.include_router(auth_cuentas_router)
app.include_router(auth_invitaciones_router)
app.include_router(perfil_router)
app.include_router(router_usuarios)
app.include_router(router_personal)
app.include_router(router_unidades)
app.include_router(router_cargos)
app.include_router(permisos_router)
app.include_router(auditoria_router)
app.include_router(importaciones_router)
app.include_router(router_recursos)
app.include_router(router_laboratorios)
app.include_router(espacios_router)
app.include_router(investigacion_router)
app.include_router(reservas_router)
app.include_router(notificaciones_router)
app.include_router(reportes_router)


@app.get("/health")
def health() -> dict[str, str]:
    # Informa el estado de la base; nunca la crea ni la modifica (BK-02).
    try:
        with engine.connect() as conexion:
            conexion.execute(text("SELECT 1"))
        base_de_datos = "conectada"
    except Exception:
        base_de_datos = "sin_conexion"
    return {"estado": "ok", "base_de_datos": base_de_datos}
