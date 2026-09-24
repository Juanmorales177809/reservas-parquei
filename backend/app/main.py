from fastapi import FastAPI
from sqlalchemy import text

from app.core.errors import registrar_manejadores
from app.db.session import engine

app = FastAPI(title="Reservas Parquei")
registrar_manejadores(app)


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
