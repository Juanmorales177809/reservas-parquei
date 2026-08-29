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

Desde la migración a Supabase Auth, `seed_admin_user()` (parte del lifespan)
crea el admin inicial también en Supabase vía `crear_usuario_confirmado`
(`app/main.py`) -- se mockea igual que `invitar_usuario` en
`test_api_usuarios.py`, nunca se le pega a la red real. `SUPABASE_URL` en
`conftest.py` es un dominio ficticio (`proyecto-de-prueba.supabase.co`) que
no resuelve por DNS; sin este mock, `with TestClient(app)` fallaba con
`httpx.ConnectError: Name or service not known` en CI.
"""

import uuid

from fastapi.testclient import TestClient

from app.config import settings
from app.main import app


def test_app_define_lifespan_en_lugar_de_on_event():
    assert app.router.lifespan_context is not None


def test_lifespan_arranca_y_health_responde(monkeypatch):
    monkeypatch.setattr("app.main.crear_usuario_confirmado", lambda email, password: uuid.uuid4())
    with TestClient(app) as cliente:
        respuesta = cliente.get("/health")
        assert respuesta.status_code == 200
        assert respuesta.json() == {"status": "ok"}


def test_lifespan_es_idempotente(monkeypatch):
    monkeypatch.setattr("app.main.crear_usuario_confirmado", lambda email, password: uuid.uuid4())
    with TestClient(app) as cliente:
        assert cliente.get("/health").status_code == 200
    with TestClient(app) as cliente:
        assert cliente.get("/health").status_code == 200


def test_scheduler_de_recordatorios_no_arranca_sin_email_enabled(monkeypatch):
    """`settings.email_enabled` es False por defecto en el entorno de tests
    (ver conftest.py) -- sin correo, el `BackgroundScheduler` de
    `services/recordatorios.py` no tiene nada útil que hacer."""
    monkeypatch.setattr("app.main.crear_usuario_confirmado", lambda email, password: uuid.uuid4())
    with TestClient(app):
        assert app.state.scheduler is None


def test_scheduler_de_recordatorios_arranca_y_para_con_email_enabled(monkeypatch):
    monkeypatch.setattr("app.main.crear_usuario_confirmado", lambda email, password: uuid.uuid4())
    monkeypatch.setattr(settings, "email_enabled", True)
    with TestClient(app):
        assert app.state.scheduler is not None
        assert app.state.scheduler.running is True
    assert app.state.scheduler.running is False
