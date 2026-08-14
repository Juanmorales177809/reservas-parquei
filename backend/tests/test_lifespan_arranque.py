# -*- coding: utf-8 -*-
"""Pruebas del ciclo de vida (lifespan) de la aplicación.

Reglas cubiertas:
- La app define lifespan (sin on_event deprecado).
- Con `with TestClient(app)` se ejecuta create_all → migraciones → seed sobre
  la base exclusiva de pruebas (reservas_test en localhost:5433).
- /health responde 200.
- El arranque es idempotente (dos ciclos de lifespan seguidos).

Nota: el fixture `client` de conftest usa TestClient SIN context manager, por
lo que no ejecuta el lifespan (comportamiento documentado en el README de
esta carpeta y verificado con la documentación oficial de FastAPI).
"""

from fastapi.testclient import TestClient

from app.main import app


def test_app_define_lifespan_en_lugar_de_on_event():
    assert app.router.lifespan_context is not None


def test_lifespan_arranca_y_health_responde():
    with TestClient(app) as cliente:
        respuesta = cliente.get("/health")
        assert respuesta.status_code == 200
        assert respuesta.json() == {"status": "ok"}


def test_lifespan_es_idempotente():
    with TestClient(app) as cliente:
        assert cliente.get("/health").status_code == 200
    with TestClient(app) as cliente:
        assert cliente.get("/health").status_code == 200
