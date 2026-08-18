# -*- coding: utf-8 -*-
"""Cabeceras HTTP de seguridad agregadas en Fase 9A (backend/app/main.py)."""

from app.config import settings


class TestCabecerasSiempreExplicitas:
    def test_endpoint_normal_incluye_cabeceras_de_seguridad(self, client):
        response = client.get("/")

        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Frame-Options"] == "DENY"
        assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
        assert response.headers["Permissions-Policy"] == "camera=(), microphone=(), geolocation=()"

    def test_no_altera_cuerpo_ni_codigo_de_respuesta(self, client):
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestContentSecurityPolicy:
    def test_endpoint_normal_incluye_csp_restrictiva(self, client):
        response = client.get("/")

        assert response.headers["Content-Security-Policy"] == "default-src 'none'; frame-ancestors 'none'"

    def test_docs_no_incluye_csp_para_no_romper_swagger_ui(self, client):
        response = client.get("/docs")

        assert response.status_code == 200
        assert "Content-Security-Policy" not in response.headers
        # Las demás cabeceras sí deben seguir presentes en /docs.
        assert response.headers["X-Content-Type-Options"] == "nosniff"

    def test_redoc_no_incluye_csp(self, client):
        response = client.get("/redoc")

        assert response.status_code == 200
        assert "Content-Security-Policy" not in response.headers


class TestHSTSyCOOP:
    """HSTS y COOP comparten el mismo gate: ambos requieren HTTPS real para
    tener sentido (COOP sin HTTPS puede aislar de forma inconsistente
    ventanas cross-origin en desarrollo), así que ninguno se envía sin
    ENVIRONMENT=production explícito."""

    def test_ausentes_en_desarrollo(self, client):
        assert settings.environment == "development"

        response = client.get("/")

        assert "Strict-Transport-Security" not in response.headers
        assert "Cross-Origin-Opener-Policy" not in response.headers

    def test_presentes_cuando_environment_es_production(self, client, monkeypatch):
        monkeypatch.setattr(settings, "environment", "production")

        response = client.get("/")

        assert response.headers["Strict-Transport-Security"] == "max-age=63072000; includeSubDomains"
        assert response.headers["Cross-Origin-Opener-Policy"] == "same-origin"
