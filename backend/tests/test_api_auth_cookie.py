# -*- coding: utf-8 -*-
"""Autenticación por cookie HttpOnly (Fase 9G, cookie-only).

Hasta la Fase 9F-A: `POST /auth/login` devolvía `TokenResponse` (con
`access_token` en el body) y además fijaba una cookie HttpOnly; los endpoints
protegidos aceptaban cookie o `Authorization: Bearer`, con precedencia del
header cuando ambos estaban presentes.

Fase 9G: se retira el body de login (`access_token`/`token_type`), el login
solo devuelve `LoginResponse{user}`, y los dependientes de `app/deps.py`
leen únicamente la cookie `access_token` de `request.cookies`. El header
`Authorization: Bearer` ya no se acepta: si se envía y no hay cookie, la
respuesta es 401 sin `WWW-Authenticate: Bearer`; si hay cookie y Bearer,
solo decide la cookie. `POST /auth/logout` sigue borrando la cookie y es
idempotente.

El OpenAPI documenta el mecanismo real: security scheme `cookieAuth`
(`apiKey` en cookie `access_token`) exigido en los endpoints protegidos.
Frontend (`AuthContext`/`api.ts`), `localStorage` y E2E ya no dependían del
body desde la Fase 9F-B; esta suite ejercita el backend directamente.
"""

import logging
from datetime import timedelta

from fastapi.testclient import TestClient

from app.auth.auth import create_access_token
from app.config import settings
from app.main import app
from app.services.rate_limit import LimitadorIntentosLogin
from tests.conftest import bearer_para, cookies_para, crear_usuario

NOMBRE_COOKIE = "access_token"


def _login(client, username="ana", password="secret123"):
    return client.post("/auth/login", json={"username": username, "password": password})


class TestLoginEmiteSoloCookieYLoginResponse:
    def test_login_no_devuelve_access_token_ni_token_type(self, client, db):
        crear_usuario(db, username="ana", email="ana@example.com", password="secret123")
        respuesta = _login(client)

        assert respuesta.status_code == 200
        cuerpo = respuesta.json()
        assert "access_token" not in cuerpo
        assert "token_type" not in cuerpo
        assert cuerpo["user"]["username"] == "ana"

    def test_login_emite_set_cookie(self, client, db):
        crear_usuario(db, username="ana", email="ana@example.com", password="secret123")
        respuesta = _login(client)

        assert NOMBRE_COOKIE in respuesta.cookies
        assert respuesta.cookies[NOMBRE_COOKIE]

    def test_cookie_incluye_atributos_esperados_en_desarrollo(self, client, db):
        assert settings.environment == "development"
        crear_usuario(db, username="ana", email="ana@example.com", password="secret123")
        respuesta = _login(client)

        cabecera = respuesta.headers["set-cookie"]
        assert "HttpOnly" in cabecera
        assert "SameSite=lax" in cabecera
        assert "Path=/" in cabecera
        assert f"Max-Age={settings.access_token_expire_minutes * 60}" in cabecera
        assert "Secure" not in cabecera

    def test_cookie_incluye_secure_en_produccion(self, client, db, monkeypatch):
        monkeypatch.setattr(settings, "environment", "production")
        crear_usuario(db, username="ana", email="ana@example.com", password="secret123")

        respuesta = _login(client)

        assert "Secure" in respuesta.headers["set-cookie"]


class TestCookieAutenticaEndpointsProtegidos:
    def test_cookie_valida_autentica_sin_header(self, client, db):
        crear_usuario(db, username="ana", email="ana@example.com", password="secret123")
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

    def test_cookie_con_jwt_expirado_da_401(self, client, db):
        # Fase 9G (auditoría): a diferencia de los demás tests de "token
        # inválido" de esta clase (cadenas malformadas), este construye un
        # JWT estructuralmente válido y correctamente firmado, pero con
        # `exp` en el pasado (expires_delta negativo) — ejercita la
        # validación real de expiración de python-jose, no solo el manejo
        # de tokens corruptos.
        usuario = crear_usuario(db, username="ana", email="ana@example.com", password="secret123")
        token_expirado = create_access_token(
            data={"sub": str(usuario.id), "rol": usuario.rol, "role": usuario.rol},
            expires_delta=timedelta(minutes=-1),
        )
        client.cookies.set(NOMBRE_COOKIE, token_expirado)

        respuesta = client.get("/usuarios/me")

        assert respuesta.status_code == 401
        assert respuesta.json()["detail"] == "No se pudo validar la autenticación"


class TestBearerRechazado:
    def test_bearer_sin_cookie_da_401(self, client, db):
        usuario = crear_usuario(db, username="ana", email="ana@example.com", password="secret123")

        respuesta = client.get("/usuarios/me", headers=bearer_para(usuario))

        assert respuesta.status_code == 401

    def test_espacios_optional_ignora_el_header(self, client, db):
        usuario = crear_usuario(db, username="admin1", email="admin1@example.com", rol="admin")

        respuesta = client.get("/espacios", headers=bearer_para(usuario))

        assert respuesta.status_code == 200  # público: el header es irrelevante

    def test_401_no_incluye_www_authenticate_bearer(self, client, db):
        usuario = crear_usuario(db, username="ana", email="ana@example.com", password="secret123")

        respuesta = client.get("/usuarios/me", headers=bearer_para(usuario))

        assert respuesta.status_code == 401
        assert "www-authenticate" not in respuesta.headers


class TestSoloLaCookieDecide:
    def test_cookie_autentica_y_ignora_bearer_de_otro_usuario(self, client, db):
        crear_usuario(db, username="ana", email="ana@example.com", password="secret123")
        beto = crear_usuario(db, username="beto", email="beto@example.com", password="secret123")

        _login(client, "ana", "secret123")  # cookie = ana
        respuesta = client.get("/usuarios/me", headers=bearer_para(beto))  # Bearer = beto

        assert respuesta.status_code == 200
        assert respuesta.json()["username"] == "ana"

    def test_cookie_invalida_no_se_rescata_con_bearer_valido(self, client, db):
        ana = crear_usuario(db, username="ana", email="ana@example.com", password="secret123")
        client.cookies.set(NOMBRE_COOKIE, "token-corrupto")

        respuesta = client.get("/usuarios/me", headers=bearer_para(ana))

        assert respuesta.status_code == 401


class TestLogout:
    def test_logout_borra_la_cookie(self, client, db):
        crear_usuario(db, username="ana", email="ana@example.com", password="secret123")
        _login(client)
        assert client.get("/usuarios/me").status_code == 200

        respuesta_logout = client.post("/auth/logout")

        assert respuesta_logout.status_code == 204
        assert client.get("/usuarios/me").status_code == 401

    def test_logout_sin_cookie_previa_es_seguro(self, client):
        respuesta = client.post("/auth/logout")

        assert respuesta.status_code == 204

    def test_logout_con_cookie_valida_es_seguro(self, client, db):
        usuario = crear_usuario(db, username="ana", email="ana@example.com", password="secret123")

        respuesta = client.post("/auth/logout", headers=cookies_para(usuario))

        assert respuesta.status_code == 204

    def test_logout_no_exige_autenticacion(self, client):
        # Debe poder limpiar una cookie inválida/expirada sin exigir un
        # token válido: de lo contrario un cliente con sesión vencida
        # nunca podría completar el logout.
        client.cookies.set(NOMBRE_COOKIE, "token-corrupto")

        respuesta = client.post("/auth/logout")

        assert respuesta.status_code == 204


class TestComportamientoExistenteSinCambios:
    def test_401_con_cookie_invalida_conserva_mensaje_y_sin_www_authenticate(self, client):
        client.cookies.set(NOMBRE_COOKIE, "token-corrupto")

        respuesta = client.get("/usuarios/me")

        assert respuesta.status_code == 401
        assert respuesta.json()["detail"] == "No se pudo validar la autenticación"
        assert "www-authenticate" not in respuesta.headers

    def test_403_por_rol_insuficiente_sin_cambios(self, client, db):
        usuario = crear_usuario(
            db, username="ana", email="ana@example.com", password="secret123", rol="usuario"
        )

        respuesta = client.post(
            "/usuarios",
            json={"username": "x", "email": "x@example.com", "password": "secret123"},
            headers=cookies_para(usuario),
        )

        assert respuesta.status_code == 403

    def test_422_por_payload_invalido_sin_cambios(self, client):
        respuesta = client.post("/auth/login", json={"username": "ana"})

        assert respuesta.status_code == 422

    def test_429_por_rate_limit_sin_cambios(self, client, db, monkeypatch):
        import app.api.auth as auth_module

        limitador = LimitadorIntentosLogin(limite=5, ventana=timedelta(minutes=15))
        monkeypatch.setattr(auth_module, "limitador_login", limitador)
        crear_usuario(db, username="ana", email="ana@example.com", password="secret123")

        for _ in range(5):
            _login(client, "ana", "incorrecta")
        respuesta = _login(client, "ana", "secret123")

        assert respuesta.status_code == 429


class TestNoSeRegistranCredenciales:
    def test_valor_de_cookie_no_aparece_en_logs_ante_error_no_controlado(
        self, db, monkeypatch, caplog
    ):
        crear_usuario(db, username="ana", email="ana@example.com", password="secret123")
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


class TestOpenApiReflejaCookieOnly:
    def test_logout_aparece_en_openapi(self, client):
        esquema = client.get("/openapi.json").json()

        assert "/auth/logout" in esquema["paths"]
        assert "post" in esquema["paths"]["/auth/logout"]

    def test_login_response_es_loginresponse_sin_access_token(self, client):
        esquema = client.get("/openapi.json").json()

        componentes = esquema["components"]["schemas"]
        assert "LoginResponse" in componentes
        assert "TokenResponse" not in componentes
        propiedades = componentes["LoginResponse"]["properties"]
        assert set(propiedades.keys()) == {"user"}
        assert componentes["LoginResponse"]["required"] == ["user"]

    def test_security_scheme_cookie_auth(self, client):
        esquema = client.get("/openapi.json").json()

        cookie_auth = esquema["components"]["securitySchemes"]["cookieAuth"]
        assert cookie_auth["type"] == "apiKey"
        assert cookie_auth["in"] == "cookie"
        assert cookie_auth["name"] == "access_token"

    def test_endpoint_protegido_exige_security_cookie_auth(self, client):
        esquema = client.get("/openapi.json").json()

        security = esquema["paths"]["/usuarios/me"]["get"].get("security")
        assert security == [{"cookieAuth": []}]

    def test_endpoint_publico_no_exige_security(self, client):
        esquema = client.get("/openapi.json").json()

        login_security = esquema["paths"]["/auth/login"]["post"].get("security")
        assert login_security in (None, [])
        espacios_get = esquema["paths"]["/espacios"]["get"].get("security")
        assert espacios_get in (None, [])