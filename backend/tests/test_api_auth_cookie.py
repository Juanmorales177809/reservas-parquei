# -*- coding: utf-8 -*-
"""Autenticación dual por cookie HttpOnly y header Authorization (Fase 9F-A).

Decisión aprobada: `POST /auth/login` sigue devolviendo `access_token` en
el body (`TokenResponse` sin cambios de contrato) y además fija una cookie
HttpOnly con el mismo token. Los endpoints protegidos aceptan cookie o
`Authorization: Bearer`; cuando ambos están presentes, el header tiene
prioridad (ver `app/deps.py`) porque es la señal explícita de un cliente
que declara sus propias credenciales por request, mientras que la cookie
es un fallback ambiental para clientes de navegador. `POST /auth/logout`
(nuevo) borra la cookie y es idempotente si no existe.

Frontend, `AuthContext`, `api.ts`, `localStorage` y E2E NO se tocan en
esta fase (Fase 9F-A es backend-only); esta suite solo ejercita el
backend directamente, igual que el resto de `tests/test_api_auth*.py`.
"""

import logging
from datetime import timedelta

from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.services.rate_limit import LimitadorIntentosLogin
from tests.conftest import crear_usuario, headers_para

NOMBRE_COOKIE = "access_token"


def _login(client, username="ana", password="secret123"):
    return client.post("/auth/login", json={"username": username, "password": password})


class TestLoginEmiteCookieYConservaBody:
    def test_access_token_sigue_en_el_body(self, client, db):
        crear_usuario(db, username="ana", email="ana@test.com", password="secret123")
        respuesta = _login(client)
        assert respuesta.status_code == 200
        assert respuesta.json()["access_token"]
        assert respuesta.json()["token_type"] == "bearer"

    def test_login_emite_set_cookie(self, client, db):
        crear_usuario(db, username="ana", email="ana@test.com", password="secret123")
        respuesta = _login(client)
        assert NOMBRE_COOKIE in respuesta.cookies
        assert respuesta.cookies[NOMBRE_COOKIE] == respuesta.json()["access_token"]

    def test_cookie_incluye_atributos_esperados_en_desarrollo(self, client, db):
        assert settings.environment == "development"
        crear_usuario(db, username="ana", email="ana@test.com", password="secret123")
        respuesta = _login(client)

        cabecera = respuesta.headers["set-cookie"]
        assert "HttpOnly" in cabecera
        assert "SameSite=lax" in cabecera
        assert "Path=/" in cabecera
        assert f"Max-Age={settings.access_token_expire_minutes * 60}" in cabecera
        assert "Secure" not in cabecera

    def test_cookie_incluye_secure_en_produccion(self, client, db, monkeypatch):
        monkeypatch.setattr(settings, "environment", "production")
        crear_usuario(db, username="ana", email="ana@test.com", password="secret123")

        respuesta = _login(client)

        assert "Secure" in respuesta.headers["set-cookie"]


class TestCookieAutenticaEndpointsProtegidos:
    def test_cookie_valida_autentica_sin_header(self, client, db):
        crear_usuario(db, username="ana", email="ana@test.com", password="secret123")
        _login(client)  # la cookie queda en el jar del TestClient (igual que un navegador)

        respuesta = client.get("/usuarios/me")

        assert respuesta.status_code == 200
        assert respuesta.json()["username"] == "ana"

    def test_cookie_invalida_da_401(self, client, db):
        client.cookies.set(NOMBRE_COOKIE, "token-corrupto")

        respuesta = client.get("/usuarios/me")

        assert respuesta.status_code == 401

    def test_sin_cookie_ni_header_sigue_dando_401(self, client, db):
        respuesta = client.get("/usuarios/me")

        assert respuesta.status_code == 401


class TestAuthorizationHeaderSigueFuncionando:
    def test_header_autentica_sin_cookie(self, client, db):
        usuario = crear_usuario(db, username="ana", email="ana@test.com", password="secret123")

        respuesta = client.get("/usuarios/me", headers=headers_para(usuario))

        assert respuesta.status_code == 200
        assert respuesta.json()["username"] == "ana"

    def test_espacios_optional_sigue_funcionando_con_header(self, client, db):
        usuario = crear_usuario(db, username="admin1", email="admin1@test.com", rol="admin")

        respuesta = client.get("/espacios", headers=headers_para(usuario))

        assert respuesta.status_code == 200


class TestPrecedenciaCuandoHayAmbosMecanismos:
    """Comportamiento documentado: el header Authorization, cuando está
    presente, tiene prioridad sobre la cookie."""

    def test_header_gana_sobre_cookie_de_otro_usuario(self, client, db):
        crear_usuario(db, username="ana", email="ana@test.com", password="secret123")
        beto = crear_usuario(db, username="beto", email="beto@test.com", password="secret123")

        _login(client, "ana", "secret123")  # cookie = ana
        respuesta = client.get("/usuarios/me", headers=headers_para(beto))  # header = beto

        assert respuesta.status_code == 200
        assert respuesta.json()["username"] == "beto"

    def test_cookie_invalida_no_bloquea_si_el_header_es_valido(self, client, db):
        ana = crear_usuario(db, username="ana", email="ana@test.com", password="secret123")
        client.cookies.set(NOMBRE_COOKIE, "token-corrupto")

        respuesta = client.get("/usuarios/me", headers=headers_para(ana))

        assert respuesta.status_code == 200
        assert respuesta.json()["username"] == "ana"


class TestLogout:
    def test_logout_borra_la_cookie(self, client, db):
        crear_usuario(db, username="ana", email="ana@test.com", password="secret123")
        _login(client)
        assert client.get("/usuarios/me").status_code == 200

        respuesta_logout = client.post("/auth/logout")

        assert respuesta_logout.status_code == 204
        assert client.get("/usuarios/me").status_code == 401

    def test_logout_sin_cookie_previa_es_seguro(self, client):
        respuesta = client.post("/auth/logout")

        assert respuesta.status_code == 204

    def test_logout_con_header_pero_sin_cookie_es_seguro(self, client, db):
        usuario = crear_usuario(db, username="ana", email="ana@test.com", password="secret123")

        respuesta = client.post("/auth/logout", headers=headers_para(usuario))

        assert respuesta.status_code == 204

    def test_logout_no_exige_autenticacion(self, client):
        # Debe poder limpiar una cookie inválida/expirada sin exigir un
        # token válido: de lo contrario un cliente con sesión vencida
        # nunca podría completar el logout.
        client.cookies.set(NOMBRE_COOKIE, "token-corrupto")

        respuesta = client.post("/auth/logout")

        assert respuesta.status_code == 204


class TestComportamientoExistenteSinCambios:
    def test_401_con_token_invalido_conserva_mensaje(self, client):
        respuesta = client.get(
            "/usuarios/me", headers={"Authorization": "Bearer token-corrupto"}
        )

        assert respuesta.status_code == 401
        assert respuesta.json()["detail"] == "No se pudo validar la autenticación"

    def test_403_por_rol_insuficiente_sin_cambios(self, client, db):
        usuario = crear_usuario(
            db, username="ana", email="ana@test.com", password="secret123", rol="usuario"
        )

        respuesta = client.post(
            "/usuarios",
            json={"username": "x", "email": "x@test.com", "password": "secret123"},
            headers=headers_para(usuario),
        )

        assert respuesta.status_code == 403

    def test_422_por_payload_invalido_sin_cambios(self, client):
        respuesta = client.post("/auth/login", json={"username": "ana"})

        assert respuesta.status_code == 422

    def test_429_por_rate_limit_sin_cambios(self, client, db, monkeypatch):
        import app.api.auth as auth_module

        limitador = LimitadorIntentosLogin(limite=5, ventana=timedelta(minutes=15))
        monkeypatch.setattr(auth_module, "limitador_login", limitador)
        crear_usuario(db, username="ana", email="ana@test.com", password="secret123")

        for _ in range(5):
            _login(client, "ana", "incorrecta")
        respuesta = _login(client, "ana", "secret123")

        assert respuesta.status_code == 429


class TestNoSeRegistranCredenciales:
    def test_valor_de_cookie_no_aparece_en_logs_ante_error_no_controlado(
        self, db, monkeypatch, caplog
    ):
        crear_usuario(db, username="ana", email="ana@test.com", password="secret123")
        cliente_sin_relanzar = TestClient(app, raise_server_exceptions=False)
        login = cliente_sin_relanzar.post(
            "/auth/login", json={"username": "ana", "password": "secret123"}
        )
        token_cookie = login.cookies[NOMBRE_COOKIE]

        def _boom(*args, **kwargs):
            raise RuntimeError("fallo-interno-no-relacionado-con-el-token")

        monkeypatch.setattr("app.deps._decode_token", _boom)

        with caplog.at_level(logging.ERROR):
            cliente_sin_relanzar.get("/usuarios/me")

        assert token_cookie not in caplog.text


class TestOpenApiReflejaLogout:
    def test_logout_aparece_en_openapi(self, client):
        esquema = client.get("/openapi.json").json()

        assert "/auth/logout" in esquema["paths"]
        assert "post" in esquema["paths"]["/auth/logout"]

    def test_token_response_conserva_access_token(self, client):
        esquema = client.get("/openapi.json").json()

        propiedades = esquema["components"]["schemas"]["TokenResponse"]["properties"]
        assert "access_token" in propiedades
