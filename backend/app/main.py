from fastapi import FastAPI
from sqlalchemy import text

from app.core.errors import registrar_manejadores
from app.db.session import engine
from app.modules.administration.router_auditoria import router as auditoria_router
from app.modules.administration.router_estructura import router_cargos, router_unidades
from app.modules.administration.router_permisos import router as permisos_router
from app.modules.auth.router import router as auth_router
from app.modules.auth.router_cuentas import router as auth_cuentas_router
from app.modules.auth.router_invitaciones import router as auth_invitaciones_router
from app.modules.espacios.router import router as espacios_router
from app.modules.resources.router import router_laboratorios, router_recursos
from app.modules.usuarios.router import router as perfil_router
from app.modules.usuarios.router_admin import router_personal, router_usuarios

app = FastAPI(title="Reservas Parquei")
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
app.include_router(router_recursos)
app.include_router(router_laboratorios)
app.include_router(espacios_router)


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
