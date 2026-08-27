# -*- coding: utf-8 -*-
"""Middleware de Request ID (backend/app/middleware/request_id.py) y su
integración con el handler global de excepciones (backend/app/main.py).

Fase "Request ID y trazabilidad". Contrato verificado aquí:
- lee X-Request-ID, lo normaliza (strip + minúsculas) y solo acepta UUID
  canónico; si falta, excede 128 caracteres o no coincide, genera `uuid4`.
- guarda el id en `request.state.request_id`;
- agrega X-Request-ID a toda respuesta normal y controlada (por middleware) y
  a la respuesta 500 (por el handler, que además lo incluye en el log con el
  mismo id);
- nunca registra Authorization, cookies, tokens, contraseñas, cuerpos ni
  headers completos.

El caso 500 usa `TestClient(raise_server_exceptions=False)` para observar la
respuesta real que vería un cliente (igual que Uvicorn en producción), no la
conveniencia de pytest de re-lanzar la excepción.
"""

import logging
import re
import uuid

import pytest
from fastapi.testclient import TestClient
from jose import jwt as jose_jwt

from app.config import settings
from app.main import app

UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
HEADER = "X-Request-ID"


@pytest.fixture()
def client_sin_relanzar():
    """Cliente que refleja el comportamiento real de un servidor desplegado:
    una excepción no controlada se convierte en una respuesta HTTP 500."""
    return TestClient(app, raise_server_exceptions=False)


def _indice_id_en_caplog(texto_log):
    match = re.search(r"request_id=([0-9a-f-]{36})", texto_log)
    assert match is not None, f"request_id ausente en el log: {texto_log!r}"
    return match.group(1)


def _token_supabase_valido() -> str:
    return jose_jwt.encode(
        {"sub": str(uuid.uuid4()), "email": "x@example.com", "aud": "authenticated"},
        settings.supabase_jwt_secret,
        algorithm=settings.algorithm,
    )


def _forzar_excepcion_en_sesion(monkeypatch, mensaje="detalle-interno-sensible"):
    def _boom(*args, **kwargs):
        raise RuntimeError(mensaje)

    monkeypatch.setattr("app.api.auth.get_usuario_by_supabase_id", _boom)


class TestRespuestasNormalesYControladas:
    def test_respuesta_exitosa_incluye_uuid_valido(self, client):
        response = client.get("/health")

        assert response.status_code == 200
        assert HEADER in response.headers
        assert UUID_RE.match(response.headers[HEADER])

    def test_dos_requests_generan_ids_distintos(self, client):
        primero = client.get("/health").headers[HEADER]
        segundo = client.get("/health").headers[HEADER]

        assert UUID_RE.match(primero)
        assert UUID_RE.match(segundo)
        assert primero != segundo

    def test_uuid_valido_entrante_se_conserva(self, client):
        entrante = str(uuid.uuid4())

        response = client.get("/health", headers={HEADER: entrante})

        assert response.headers[HEADER] == entrante

    def test_uuid_mayuscula_entrante_se_normaliza_a_minusculas(self, client):
        entrante_mayuscula = str(uuid.uuid4()).upper()

        response = client.get("/health", headers={HEADER: entrante_mayuscula})

        assert response.headers[HEADER] == entrante_mayuscula.lower()
        assert entrante_mayuscula != response.headers[HEADER]

    def test_header_invalido_se_reemplaza(self, client):
        invalido = "no-es-un-uuid"

        response = client.get("/health", headers={HEADER: invalido})

        assert HEADER in response.headers
        assert UUID_RE.match(response.headers[HEADER])
        assert response.headers[HEADER] != invalido

    def test_header_con_espacios_se_reemplaza(self, client):
        # El strip del contrato normaliza espacios periféricos; un espacio
        # interno (que sobrevive al strip) hace que el valor no sea un UUID
        # canónico y deba reemplazarse.
        con_espacios = "00000000-0000-0000-0000-0000 00000000"

        response = client.get("/health", headers={HEADER: con_espacios})

        assert HEADER in response.headers
        assert UUID_RE.match(response.headers[HEADER])
        assert response.headers[HEADER] != con_espacios

    def test_header_con_caracteres_de_control_se_reemplaza_sin_propagarse(self, client):
        con_control = "GOTCHA\ntab\tvalue"

        response = client.get("/health", headers={HEADER: con_control})

        assert HEADER in response.headers
        assert UUID_RE.match(response.headers[HEADER])
        assert response.headers[HEADER] != con_control
        assert "GOTCHA" not in str(response.headers)

    def test_header_mas_de_128_caracteres_se_reemplaza(self, client):
        demasiado_largo = "a" * 200

        response = client.get("/health", headers={HEADER: demasiado_largo})

        assert HEADER in response.headers
        assert UUID_RE.match(response.headers[HEADER])
        assert response.headers[HEADER] != demasiado_largo


class TestErroresHTTPContienenXRequestID:
    def test_422_contiene_x_request_id(self, client):
        response = client.post("/auth/supabase/sesion", json={})

        assert response.status_code == 422
        assert HEADER in response.headers
        assert UUID_RE.match(response.headers[HEADER])

    def test_401_contiene_x_request_id(self, client):
        response = client.post(
            "/auth/supabase/sesion", json={"supabase_token": "token-invalido-reqid"}
        )

        assert response.status_code == 401
        assert HEADER in response.headers
        assert UUID_RE.match(response.headers[HEADER])


class TestExcepcionNoControlada500:
    def test_500_contiene_x_request_id(self, client_sin_relanzar, monkeypatch, caplog):
        _forzar_excepcion_en_sesion(monkeypatch)

        with caplog.at_level(logging.ERROR):
            response = client_sin_relanzar.post(
                "/auth/supabase/sesion", json={"supabase_token": _token_supabase_valido()}
            )

        assert response.status_code == 500
        assert HEADER in response.headers
        assert UUID_RE.match(response.headers[HEADER])

    def test_el_id_del_500_coincide_con_el_registrado_en_caplog(
        self, client_sin_relanzar, monkeypatch, caplog
    ):
        _forzar_excepcion_en_sesion(monkeypatch)

        with caplog.at_level(logging.ERROR):
            response = client_sin_relanzar.post(
                "/auth/supabase/sesion", json={"supabase_token": _token_supabase_valido()}
            )

        assert response.status_code == 500
        assert response.headers[HEADER] == _indice_id_en_caplog(caplog.text)

    def test_500_mantiene_body_generico_sin_detalles_internos(
        self, client_sin_relanzar, monkeypatch
    ):
        _forzar_excepcion_en_sesion(monkeypatch, mensaje="detalle-interno-sensible-password=hunter2")

        response = client_sin_relanzar.post(
            "/auth/supabase/sesion", json={"supabase_token": _token_supabase_valido()}
        )

        assert response.status_code == 500
        assert "detalle-interno-sensible" not in response.text
        assert "hunter2" not in response.text
        assert "RuntimeError" not in response.text
        assert response.json()["detail"] == "Ha ocurrido un error interno. Inténtalo de nuevo más tarde."


class TestLogsNoRegistranSecretos:
    def test_logs_de_error_no_incluyen_authorization_cookies_tokens_ni_password(
        self, client_sin_relanzar, monkeypatch, caplog
    ):
        token_sentinel = "secreto-de-autorizacion-que-nunca-debe-aparecer"
        cookie_sentinel = "secreto-de-cookie-que-nunca-debe-aparecer"
        _forzar_excepcion_en_sesion(monkeypatch)

        with caplog.at_level(logging.ERROR):
            client_sin_relanzar.post(
                "/auth/supabase/sesion",
                json={"supabase_token": _token_supabase_valido()},
                headers={
                    "Authorization": f"Bearer {token_sentinel}",
                    "Cookie": f"access_token={cookie_sentinel}",
                },
            )

        assert token_sentinel not in caplog.text
        assert cookie_sentinel not in caplog.text

    def test_log_de_error_incluye_metodo_ruta_tipo_y_request_id(
        self, client_sin_relanzar, monkeypatch, caplog
    ):
        _forzar_excepcion_en_sesion(monkeypatch)

        with caplog.at_level(logging.ERROR):
            client_sin_relanzar.post(
                "/auth/supabase/sesion", json={"supabase_token": _token_supabase_valido()}
            )

        assert "POST" in caplog.text
        assert "/auth/supabase/sesion" in caplog.text
        assert "RuntimeError" in caplog.text
        assert _indice_id_en_caplog(caplog.text)  # existe el request_id