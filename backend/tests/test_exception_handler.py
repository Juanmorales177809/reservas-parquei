# -*- coding: utf-8 -*-
"""Handler global de excepciones no controladas (backend/app/main.py).

Usa un TestClient con raise_server_exceptions=False para observar la
respuesta HTTP real que vería un cliente (igual que Uvicorn en producción,
donde una excepción nunca revienta el proceso) en vez del comportamiento de
conveniencia de pytest, que por defecto re-lanza la excepción dentro del
test.

El vehículo para forzar la excepción es `POST /auth/supabase/sesion`
(único endpoint público que hace trabajo real tras decodificar el token) --
se manda un JWT de Supabase VÁLIDO y correctamente firmado, para que la
ejecución llegue al punto donde se monkeypatchea la excepción.
"""

import logging

import pytest
from fastapi.testclient import TestClient
from jose import jwt as jose_jwt

from app.config import settings
from app.main import app
from tests.conftest import crear_usuario

TOKEN_SENTINELA = "secreto-de-autorizacion-que-nunca-debe-aparecer-en-logs"
MENSAJE_INTERNO_SENSIBLE = "detalle-interno-sensible-password=hunter2"


def _token_supabase_valido() -> str:
    import uuid

    return jose_jwt.encode(
        {"sub": str(uuid.uuid4()), "email": "x@example.com", "aud": "authenticated"},
        settings.supabase_jwt_secret,
        algorithm=settings.algorithm,
    )


@pytest.fixture()
def client_sin_relanzar():
    """Cliente que refleja el comportamiento real de un servidor desplegado:
    una excepción no controlada se convierte en una respuesta HTTP, nunca
    revienta el proceso ni el test."""
    return TestClient(app, raise_server_exceptions=False)


def _forzar_excepcion_en_sesion(monkeypatch, mensaje=MENSAJE_INTERNO_SENSIBLE):
    def _boom(*args, **kwargs):
        raise RuntimeError(mensaje)

    monkeypatch.setattr("app.api.auth.get_usuario_by_supabase_id", _boom)


class TestRespuesta500Sanitizada:
    def test_excepcion_no_controlada_da_500(self, client_sin_relanzar, monkeypatch):
        _forzar_excepcion_en_sesion(monkeypatch)

        respuesta = client_sin_relanzar.post(
            "/auth/supabase/sesion", json={"supabase_token": _token_supabase_valido()}
        )

        assert respuesta.status_code == 500

    def test_respuesta_no_incluye_str_de_la_excepcion(self, client_sin_relanzar, monkeypatch):
        _forzar_excepcion_en_sesion(monkeypatch)

        respuesta = client_sin_relanzar.post(
            "/auth/supabase/sesion", json={"supabase_token": _token_supabase_valido()}
        )

        cuerpo = respuesta.text
        assert MENSAJE_INTERNO_SENSIBLE not in cuerpo
        assert "hunter2" not in cuerpo
        assert "RuntimeError" not in cuerpo

    def test_respuesta_no_incluye_traceback_ni_rutas_internas(self, client_sin_relanzar, monkeypatch):
        _forzar_excepcion_en_sesion(monkeypatch)

        respuesta = client_sin_relanzar.post(
            "/auth/supabase/sesion", json={"supabase_token": _token_supabase_valido()}
        )

        cuerpo = respuesta.text
        assert "Traceback" not in cuerpo
        assert "File \"" not in cuerpo
        assert "app/api/auth.py" not in cuerpo
        assert "app\\api\\auth.py" not in cuerpo

    def test_mensaje_es_generico_y_estable(self, client_sin_relanzar, monkeypatch):
        _forzar_excepcion_en_sesion(monkeypatch)

        respuesta = client_sin_relanzar.post(
            "/auth/supabase/sesion", json={"supabase_token": _token_supabase_valido()}
        )

        cuerpo = respuesta.json()
        assert isinstance(cuerpo.get("detail"), str)
        assert len(cuerpo["detail"]) > 0

    def test_mismo_mensaje_para_distintos_tipos_de_excepcion(self, client_sin_relanzar, monkeypatch):
        _forzar_excepcion_en_sesion(monkeypatch, mensaje="primer error")
        primera = client_sin_relanzar.post(
            "/auth/supabase/sesion", json={"supabase_token": _token_supabase_valido()}
        )

        def _boom_valueerror(*args, **kwargs):
            raise ValueError("segundo error, tipo distinto")

        monkeypatch.setattr("app.api.auth.get_usuario_by_supabase_id", _boom_valueerror)
        segunda = client_sin_relanzar.post(
            "/auth/supabase/sesion", json={"supabase_token": _token_supabase_valido()}
        )

        assert primera.json()["detail"] == segunda.json()["detail"]


class TestLogSeguroConContexto:
    def test_log_incluye_metodo_ruta_y_tipo_de_excepcion(
        self, client_sin_relanzar, monkeypatch, caplog
    ):
        _forzar_excepcion_en_sesion(monkeypatch)

        with caplog.at_level(logging.ERROR):
            client_sin_relanzar.post(
                "/auth/supabase/sesion", json={"supabase_token": _token_supabase_valido()}
            )

        texto_log = caplog.text
        assert "POST" in texto_log
        assert "/auth/supabase/sesion" in texto_log
        assert "RuntimeError" in texto_log

    def test_log_incluye_traceback_para_diagnostico_en_servidor(
        self, client_sin_relanzar, monkeypatch, caplog
    ):
        _forzar_excepcion_en_sesion(monkeypatch)

        with caplog.at_level(logging.ERROR):
            client_sin_relanzar.post(
                "/auth/supabase/sesion", json={"supabase_token": _token_supabase_valido()}
            )

        # El traceback SÍ debe quedar en el log del servidor (para
        # diagnóstico), a diferencia de la respuesta HTTP al cliente.
        assert "Traceback" in caplog.text
        assert MENSAJE_INTERNO_SENSIBLE in caplog.text

    def test_log_no_incluye_authorization_ni_password_del_request(
        self, client_sin_relanzar, monkeypatch, caplog
    ):
        _forzar_excepcion_en_sesion(monkeypatch)

        with caplog.at_level(logging.ERROR):
            client_sin_relanzar.post(
                "/auth/supabase/sesion",
                json={"supabase_token": _token_supabase_valido()},
                headers={"Authorization": f"Bearer {TOKEN_SENTINELA}"},
            )

        assert TOKEN_SENTINELA not in caplog.text


class TestErroresControladosSinCambios:
    def test_401_conserva_su_comportamiento(self, client_sin_relanzar, db):
        crear_usuario(db, username="ana", email="ana_exc@example.com")

        respuesta = client_sin_relanzar.post(
            "/auth/supabase/sesion", json={"supabase_token": "no-es-un-jwt-valido"}
        )

        assert respuesta.status_code == 401
        assert respuesta.json()["detail"] == "Token de Supabase inválido"

    def test_422_conserva_su_comportamiento(self, client_sin_relanzar):
        respuesta = client_sin_relanzar.post("/auth/supabase/sesion", json={})

        assert respuesta.status_code == 422
        assert "detail" in respuesta.json()
