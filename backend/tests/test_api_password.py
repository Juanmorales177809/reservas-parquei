# -*- coding: utf-8 -*-
"""Pruebas de los tres flujos de contraseña nuevos:

1. Alta de usuario: el backend genera la contraseña (nunca la que envía el
   admin), la entrega por correo, y marca `debe_cambiar_password`.
2. `POST /auth/cambiar-password`: cambio obligatorio/autoservicio.
3. `POST /auth/recuperar` + `POST /auth/restablecer`: recuperación por
   código de 6 dígitos, en memoria (nunca en la base).

Sigue el mismo patrón de aislamiento de `test_api_auth_rate_limit.py`:
instancias frescas de los limitadores/reloj por test, vía monkeypatch.
"""

from datetime import datetime, timedelta

import pytest

from app.config import settings
from app.models import CorreoSaliente
from app.services import email as email_service
from app.services.rate_limit import LimitadorIntentosLogin
from app.services.recuperacion import RecuperacionPassword

from tests.conftest import cookies_para, crear_usuario


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
def _estado_limpio(monkeypatch, reloj):
    """Instancias frescas del limitador de recuperación y del generador de
    códigos por test -- mismo criterio de aislamiento que
    test_api_auth_rate_limit.py::limitador_limpio."""
    import app.api.auth as auth_module

    limitador = LimitadorIntentosLogin(reloj=reloj, limite=5, ventana=timedelta(minutes=15))
    monkeypatch.setattr(auth_module, "limitador_recuperacion", limitador)
    recuperacion = RecuperacionPassword(reloj=reloj, ventana=timedelta(minutes=15))
    monkeypatch.setattr(auth_module, "recuperacion_password", recuperacion)
    return limitador, recuperacion


class _SMTPFalso:
    instancias: list["_SMTPFalso"] = []

    def __init__(self, host, port, timeout=None):
        self.mensajes_enviados: list = []
        _SMTPFalso.instancias.append(self)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def starttls(self):
        pass

    def login(self, user, password):
        pass

    def send_message(self, mensaje):
        self.mensajes_enviados.append(mensaje)


@pytest.fixture()
def email_habilitado(monkeypatch):
    _SMTPFalso.instancias = []
    monkeypatch.setattr(settings, "email_enabled", True)
    monkeypatch.setattr(settings, "smtp_host", "smtp.prueba.local")
    monkeypatch.setattr(settings, "smtp_from", "reservas@prueba.local")
    monkeypatch.setattr(email_service.smtplib, "SMTP", _SMTPFalso)
    return _SMTPFalso


def _login(client, username, password):
    return client.post("/auth/login", json={"username": username, "password": password})


class TestAltaDeUsuarioGeneraCredenciales:
    def test_password_enviada_por_el_admin_se_ignora_siempre(self, client, db, email_habilitado):
        admin = crear_usuario(db, username="admin_pw", email="admin_pw@example.com", rol="admin")
        respuesta = client.post(
            "/usuarios",
            json={
                "username": "nuevo_pw",
                "email": "nuevo_pw@example.com",
                "password": "loQueElijaElAdmin123",
                "rol": "usuario",
            },
            headers=cookies_para(admin),
        )
        assert respuesta.status_code == 201
        assert respuesta.json()["debe_cambiar_password"] is True

        # La contraseña enviada en el payload NUNCA funciona para loguearse.
        assert _login(client, "nuevo_pw", "loQueElijaElAdmin123").status_code == 401

        correo = db.query(CorreoSaliente).one()
        assert correo.destinatario == "nuevo_pw@example.com"
        assert correo.estado == "enviado"
        assert "Contraseña temporal:" in correo.cuerpo

        temporal = correo.cuerpo.split("Contraseña temporal: ")[1].splitlines()[0]
        login_temporal = _login(client, "nuevo_pw", temporal)
        assert login_temporal.status_code == 200
        assert login_temporal.json()["user"]["debe_cambiar_password"] is True

    def test_sin_email_enabled_el_alta_funciona_igual(self, client, db):
        admin = crear_usuario(db, username="admin_pw2", email="admin_pw2@example.com", rol="admin")
        respuesta = client.post(
            "/usuarios",
            json={"username": "nuevo_pw2", "email": "nuevo_pw2@example.com", "rol": "usuario"},
            headers=cookies_para(admin),
        )
        assert respuesta.status_code == 201
        # El outbox queda pendiente (nunca se intenta el envío real), pero
        # el alta del usuario no se ve afectada por eso.
        assert db.query(CorreoSaliente).one().estado == "pendiente"


class TestCambiarPassword:
    def test_requiere_password_actual_correcta(self, client, db):
        usuario = crear_usuario(db, username="cp1", email="cp1@example.com", password="actual123")
        respuesta = client.post(
            "/auth/cambiar-password",
            json={"password_actual": "incorrecta", "password_nueva": "nueva12345"},
            headers=cookies_para(usuario),
        )
        assert respuesta.status_code == 401

    def test_cambio_exitoso_limpia_debe_cambiar_password_y_habilita_login_nuevo(self, client, db):
        usuario = crear_usuario(db, username="cp2", email="cp2@example.com", password="actual123")
        usuario.debe_cambiar_password = True
        db.add(usuario)
        db.commit()

        respuesta = client.post(
            "/auth/cambiar-password",
            json={"password_actual": "actual123", "password_nueva": "nueva12345"},
            headers=cookies_para(usuario),
        )
        assert respuesta.status_code == 204

        assert _login(client, "cp2", "actual123").status_code == 401
        login_nuevo = _login(client, "cp2", "nueva12345")
        assert login_nuevo.status_code == 200
        assert login_nuevo.json()["user"]["debe_cambiar_password"] is False

    def test_exige_sesion(self, client, db):
        respuesta = client.post(
            "/auth/cambiar-password",
            json={"password_actual": "x", "password_nueva": "nueva12345"},
        )
        assert respuesta.status_code == 401


class TestRecuperarYRestablecer:
    def test_flujo_feliz_completo(self, client, db, email_habilitado):
        crear_usuario(db, username="rec1", email="rec1@example.com", password="viejaClave1")

        solicitud = client.post("/auth/recuperar", json={"identificador": "rec1"})
        assert solicitud.status_code == 204

        correo = db.query(CorreoSaliente).one()
        assert correo.destinatario == "rec1@example.com"
        codigo = correo.cuerpo.split("código para restablecer la contraseña es: ")[1][:6]

        restablecer = client.post(
            "/auth/restablecer",
            json={"identificador": "rec1", "codigo": codigo, "password_nueva": "nuevaClave2"},
        )
        assert restablecer.status_code == 204

        assert _login(client, "rec1", "viejaClave1").status_code == 401
        assert _login(client, "rec1", "nuevaClave2").status_code == 200

    def test_recuperar_responde_igual_exista_o_no_el_usuario(self, client, db):
        existente = client.post("/auth/recuperar", json={"identificador": "fantasma"})
        crear_usuario(db, username="rec2", email="rec2@example.com")
        real = client.post("/auth/recuperar", json={"identificador": "rec2"})
        assert existente.status_code == real.status_code == 204
        # Ninguna de las dos respuestas tiene cuerpo que las distinga.
        assert existente.content == real.content == b""

    def test_codigo_incorrecto_rechazado(self, client, db, email_habilitado):
        crear_usuario(db, username="rec3", email="rec3@example.com", password="viejaClave1")
        client.post("/auth/recuperar", json={"identificador": "rec3"})

        respuesta = client.post(
            "/auth/restablecer",
            json={"identificador": "rec3", "codigo": "000000", "password_nueva": "nuevaClave2"},
        )
        assert respuesta.status_code == 400
        assert _login(client, "rec3", "viejaClave1").status_code == 200

    def test_codigo_vencido_rechazado(self, client, db, email_habilitado, reloj):
        crear_usuario(db, username="rec4", email="rec4@example.com", password="viejaClave1")
        client.post("/auth/recuperar", json={"identificador": "rec4"})
        correo = db.query(CorreoSaliente).one()
        codigo = correo.cuerpo.split("código para restablecer la contraseña es: ")[1][:6]

        reloj.avanzar(timedelta(minutes=15, seconds=1))

        respuesta = client.post(
            "/auth/restablecer",
            json={"identificador": "rec4", "codigo": codigo, "password_nueva": "nuevaClave2"},
        )
        assert respuesta.status_code == 400

    def test_codigo_ya_usado_no_se_puede_reutilizar(self, client, db, email_habilitado):
        crear_usuario(db, username="rec5", email="rec5@example.com", password="viejaClave1")
        client.post("/auth/recuperar", json={"identificador": "rec5"})
        correo = db.query(CorreoSaliente).one()
        codigo = correo.cuerpo.split("código para restablecer la contraseña es: ")[1][:6]

        primero = client.post(
            "/auth/restablecer",
            json={"identificador": "rec5", "codigo": codigo, "password_nueva": "nuevaClave2"},
        )
        assert primero.status_code == 204

        segundo = client.post(
            "/auth/restablecer",
            json={"identificador": "rec5", "codigo": codigo, "password_nueva": "otraClave3"},
        )
        assert segundo.status_code == 400

    def test_intento_fallido_no_quema_el_codigo(self, client, db, email_habilitado):
        crear_usuario(db, username="rec6", email="rec6@example.com", password="viejaClave1")
        client.post("/auth/recuperar", json={"identificador": "rec6"})
        correo = db.query(CorreoSaliente).one()
        codigo = correo.cuerpo.split("código para restablecer la contraseña es: ")[1][:6]

        fallido = client.post(
            "/auth/restablecer",
            json={"identificador": "rec6", "codigo": "999999", "password_nueva": "nuevaClave2"},
        )
        assert fallido.status_code == 400

        exitoso = client.post(
            "/auth/restablecer",
            json={"identificador": "rec6", "codigo": codigo, "password_nueva": "nuevaClave2"},
        )
        assert exitoso.status_code == 204

    def test_restablecer_se_bloquea_tras_intentos_repetidos(self, client, db):
        crear_usuario(db, username="rec7", email="rec7@example.com", password="viejaClave1")
        for _ in range(5):
            respuesta = client.post(
                "/auth/restablecer",
                json={"identificador": "rec7", "codigo": "000000", "password_nueva": "x123456"},
            )
            assert respuesta.status_code == 400
        bloqueado = client.post(
            "/auth/restablecer",
            json={"identificador": "rec7", "codigo": "000000", "password_nueva": "x123456"},
        )
        assert bloqueado.status_code == 429
