# -*- coding: utf-8 -*-
"""Rate limiting de POST /auth/login (Fase 9C).

Integración contra el endpoint real. El limitador es un singleton de
módulo (`app.api.auth.limitador_login`); cada test lo reemplaza por una
instancia fresca con reloj controlable, vía monkeypatch, para aislamiento
total entre tests y para simular el paso del tiempo sin sleep real.
"""

from datetime import datetime, timedelta

import pytest

from app.services.rate_limit import LimitadorIntentosLogin
from tests.conftest import crear_usuario


class _RelojControlable:
    def __init__(self, valor: datetime):
        self.valor = valor

    def ahora(self) -> datetime:
        return self.valor

    def avanzar(self, delta: timedelta) -> None:
        self.valor += delta


@pytest.fixture()
def reloj():
    return _RelojControlable(datetime(2026, 8, 17, 10, 0))


@pytest.fixture(autouse=True)
def limitador_limpio(monkeypatch, reloj):
    """Instancia fresca del limitador por test: aislamiento total, sin
    contaminar el estado del proceso pytest entre tests ni con la app real."""
    import app.api.auth as auth_module

    limitador = LimitadorIntentosLogin(reloj=reloj, limite=5, ventana=timedelta(minutes=15))
    monkeypatch.setattr(auth_module, "limitador_login", limitador)
    return limitador


def _login(client, username, password):
    return client.post("/auth/login", json={"username": username, "password": password})


class TestLoginValidoNoSeBloquea:
    def test_login_correcto_repetido_no_dispara_429(self, client, db):
        crear_usuario(db, username="ana", email="ana@example.com", password="secret123")
        for _ in range(10):
            respuesta = _login(client, "ana", "secret123")
            assert respuesta.status_code == 200


class TestIntentosInvalidosSeCuentan:
    def test_cuarto_intento_fallido_no_bloquea_aun(self, client, db):
        crear_usuario(db, username="ana", email="ana@example.com", password="secret123")
        for _ in range(4):
            respuesta = _login(client, "ana", "incorrecta")
            assert respuesta.status_code == 401

    def test_sexto_intento_bloquea_tras_cinco_fallos(self, client, db):
        crear_usuario(db, username="ana", email="ana@example.com", password="secret123")
        for _ in range(5):
            respuesta = _login(client, "ana", "incorrecta")
            assert respuesta.status_code == 401  # los 5 primeros se procesan normal

        sexto = _login(client, "ana", "incorrecta")
        assert sexto.status_code == 429  # el sexto ya ve 5 fallos vigentes

    def test_intentos_contra_usuario_inexistente_tambien_cuentan(self, client, db):
        for _ in range(5):
            respuesta = _login(client, "fantasma", "cualquiera")
            assert respuesta.status_code == 401
        sexto = _login(client, "fantasma", "cualquiera")
        assert sexto.status_code == 429


class TestBloqueoImpideIncluirCredencialesCorrectas:
    def test_bloqueado_incluso_con_password_correcta(self, client, db):
        crear_usuario(db, username="ana", email="ana@example.com", password="secret123")
        for _ in range(5):
            _login(client, "ana", "incorrecta")

        respuesta = _login(client, "ana", "secret123")

        assert respuesta.status_code == 429


class TestReinicioTrasExito:
    def test_login_exitoso_reinicia_el_contador(self, client, db):
        crear_usuario(db, username="ana", email="ana@example.com", password="secret123")
        for _ in range(4):
            _login(client, "ana", "incorrecta")

        exito = _login(client, "ana", "secret123")
        assert exito.status_code == 200

        # El contador se reinició: 4 fallos más no deberían bloquear (el
        # límite es 5, y ya se limpió el historial previo).
        for _ in range(4):
            respuesta = _login(client, "ana", "incorrecta")
            assert respuesta.status_code == 401


class TestClavesSeparadas:
    def test_usuarios_distintos_no_comparten_bloqueo(self, client, db):
        crear_usuario(db, username="ana", email="ana@example.com", password="secret123")
        crear_usuario(db, username="beto", email="beto@example.com", password="secret123")
        for _ in range(5):
            _login(client, "ana", "incorrecta")

        respuesta = _login(client, "beto", "secret123")

        assert respuesta.status_code == 200

    def test_ips_distintas_no_comparten_bloqueo(self, client, db):
        crear_usuario(db, username="ana", email="ana@example.com", password="secret123")
        for _ in range(5):
            client.post(
                "/auth/login",
                json={"username": "ana", "password": "incorrecta"},
                headers={"X-Forwarded-For": "9.9.9.9"},
            )

        # request.client.host en TestClient no cambia por un header
        # arbitrario (no se confía en X-Forwarded-For): sigue siendo la
        # misma IP de conexión directa que los 5 intentos anteriores, así
        # que el sexto intento también debe bloquear (prueba que el header
        # no sirve para evadir el límite).
        respuesta = _login(client, "ana", "secret123")
        assert respuesta.status_code == 429


class TestNoFiltraExistenciaDeUsuario:
    def test_mensaje_429_no_distingue_usuario_existente_o_no(self, client, db):
        crear_usuario(db, username="ana", email="ana@example.com", password="secret123")
        for _ in range(5):
            _login(client, "ana", "incorrecta")
        for _ in range(5):
            _login(client, "fantasma", "incorrecta")

        respuesta_existente = _login(client, "ana", "secret123")
        respuesta_inexistente = _login(client, "fantasma", "secret123")

        assert respuesta_existente.status_code == 429
        assert respuesta_inexistente.status_code == 429
        assert respuesta_existente.json()["detail"] == respuesta_inexistente.json()["detail"]


class TestVentanaExpira:
    def test_ventana_expirada_permite_login_de_nuevo(self, client, db, reloj):
        crear_usuario(db, username="ana", email="ana@example.com", password="secret123")
        for _ in range(5):
            _login(client, "ana", "incorrecta")
        assert _login(client, "ana", "secret123").status_code == 429

        reloj.avanzar(timedelta(minutes=15, seconds=1))

        assert _login(client, "ana", "secret123").status_code == 200


class TestErroresNoRelacionadosNoConsumenIntentos:
    def test_payload_invalido_da_422_y_no_cuenta_como_intento(self, client, db):
        crear_usuario(db, username="ana", email="ana@example.com", password="secret123")
        for _ in range(10):
            respuesta = client.post("/auth/login", json={"username": "ana"})  # falta password
            assert respuesta.status_code == 422

        # Ningún 422 debió registrarse como intento fallido.
        exito = _login(client, "ana", "secret123")
        assert exito.status_code == 200
