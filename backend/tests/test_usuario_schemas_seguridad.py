# -*- coding: utf-8 -*-
"""Fase 9E: refuerzo de validaciones de seguridad en schemas de usuario/auth.

Cuatro cambios aprobados, solo en backend/app/schemas/usuario.py:
1. UsuarioLogin.username: min_length=1, max_length=80.
2. UsuarioLogin.password: min_length=1, max_length=72.
3. UsuarioCreate.password y UsuarioUpdate.password: max_length=72.
4. UsuarioCreate.email: mismo validador de formato que AdminUsuarioCreate/UsuarioUpdate.

72 = límite real de bcrypt (passlib+bcrypt trunca en silencio pasado ese
byte); 80 = mismo máximo ya usado para username en Create/Update.

No se toca: normalización de username, complejidad de contraseña, mensajes
existentes, rate limiting, auth/cookies/JWT, frontend, Docker, CI, migraciones.
"""

import pytest
from pydantic import ValidationError

from app.schemas.usuario import (
    AdminUsuarioCreate,
    UsuarioCreate,
    UsuarioLogin,
    UsuarioResponse,
    UsuarioUpdate,
)
from tests.conftest import crear_usuario


def _payload_admin_create_valido(**overrides):
    base = {"username": "nuevo_usuario", "email": "nuevo@example.com", "password": "secret123"}
    base.update(overrides)
    return base


class TestUsuarioLoginLimites:
    def test_username_vacio_rechazado(self):
        with pytest.raises(ValidationError):
            UsuarioLogin(username="", password="secret123")

    def test_username_maximo_80_aceptado(self):
        UsuarioLogin(username="u" * 80, password="secret123")

    def test_username_81_caracteres_rechazado(self):
        with pytest.raises(ValidationError):
            UsuarioLogin(username="u" * 81, password="secret123")

    def test_password_vacia_rechazada(self):
        with pytest.raises(ValidationError):
            UsuarioLogin(username="ana", password="")

    def test_password_maximo_72_aceptada(self):
        UsuarioLogin(username="ana", password="p" * 72)

    def test_password_73_caracteres_rechazada(self):
        with pytest.raises(ValidationError):
            UsuarioLogin(username="ana", password="p" * 73)

    def test_username_1_caracter_aceptado(self):
        # min_length=1, no min_length=3 como en Create/Update: login no
        # normaliza ni exige la misma política de creación de cuentas.
        UsuarioLogin(username="a", password="secret123")

    def test_password_1_caracter_aceptada(self):
        UsuarioLogin(username="ana", password="p")


class TestPasswordMaximoEnCreateYUpdate:
    def test_create_password_72_aceptada(self):
        AdminUsuarioCreate(**_payload_admin_create_valido(password="p" * 72))

    def test_create_password_73_rechazada(self):
        with pytest.raises(ValidationError):
            AdminUsuarioCreate(**_payload_admin_create_valido(password="p" * 73))

    def test_create_password_vacia_sigue_rechazada_por_minimo_existente(self):
        # min_length=6 ya existía; no se toca, solo se confirma que sigue.
        with pytest.raises(ValidationError):
            AdminUsuarioCreate(**_payload_admin_create_valido(password=""))

    def test_create_password_por_debajo_del_minimo_existente_sigue_rechazada(self):
        with pytest.raises(ValidationError):
            AdminUsuarioCreate(**_payload_admin_create_valido(password="abc12"))  # 5 < 6

    def test_update_password_72_aceptada(self):
        UsuarioUpdate(password="p" * 72)

    def test_update_password_73_rechazada(self):
        with pytest.raises(ValidationError):
            UsuarioUpdate(password="p" * 73)

    def test_update_password_none_sigue_aceptado(self):
        # Campo opcional: no togar el contrato de "no cambiar password".
        UsuarioUpdate(password=None)


class TestEmailUsuarioCreate:
    def test_email_formato_invalido_rechazado(self):
        with pytest.raises(ValidationError):
            UsuarioCreate(username="ana", email="no-es-un-email", password="secret123")

    def test_email_vacio_rechazado(self):
        with pytest.raises(ValidationError):
            UsuarioCreate(username="ana", email="", password="secret123")

    def test_email_valido_aceptado(self):
        UsuarioCreate(username="ana", email="ana@example.com", password="secret123")

    def test_email_maximo_255_sigue_vigente(self):
        # max_length=255 ya existía en UsuarioCreate; se confirma que el
        # nuevo validador de formato no lo reemplaza.
        email_largo_valido = f"{'a' * 240}@example.com"  # <= 255, formato válido
        assert len(email_largo_valido) <= 255
        UsuarioCreate(username="ana", email=email_largo_valido, password="secret123")

    def test_email_256_caracteres_rechazado(self):
        email_demasiado_largo = f"{'a' * 250}@example.com"  # > 255
        with pytest.raises(ValidationError):
            UsuarioCreate(username="ana", email=email_demasiado_largo, password="secret123")


class TestTiposIncorrectos:
    def test_username_numerico_en_login_rechazado(self):
        with pytest.raises(ValidationError):
            UsuarioLogin(username=12345, password="secret123")  # type: ignore[arg-type]

    def test_password_numerica_en_login_rechazada(self):
        with pytest.raises(ValidationError):
            UsuarioLogin(username="ana", password=123456)  # type: ignore[arg-type]

    def test_espacio_id_no_numerico_en_create_rechazado(self):
        with pytest.raises(ValidationError):
            AdminUsuarioCreate(**_payload_admin_create_valido(espacio_id="no-es-int"))


class TestCompatibilidadPayloadsValidosExistentes:
    """Los payloads que ya pasaban antes de la Fase 9E deben seguir pasando."""

    def test_admin_usuario_create_tipico_sigue_valido(self):
        AdminUsuarioCreate(username="ana", email="ana@example.com", password="secret123")

    def test_usuario_update_parcial_sigue_valido(self):
        UsuarioUpdate(username="nuevo_nombre")

    def test_usuario_login_tipico_sigue_valido(self):
        UsuarioLogin(username="ana", password="secret123")


class TestUsuarioResponseSinDatosSensibles:
    def test_usuario_response_no_declara_password_ni_hash(self):
        campos = set(UsuarioResponse.model_fields.keys())
        assert "password" not in campos
        assert "hashed_password" not in campos


class TestLoginVaciosDan422NoConsumenRateLimit:
    def test_username_vacio_en_login_da_422_no_401(self, client, db):
        crear_usuario(db, username="ana", email="ana_9e@example.com", password="secret123")

        respuesta = client.post("/auth/login", json={"username": "", "password": "secret123"})

        assert respuesta.status_code == 422

    def test_password_vacia_en_login_da_422_no_401(self, client, db):
        crear_usuario(db, username="ana", email="ana_9e2@example.com", password="secret123")

        respuesta = client.post("/auth/login", json={"username": "ana", "password": ""})

        assert respuesta.status_code == 422

    def test_422_por_campos_vacios_no_consume_intento_de_rate_limit(self, client, db):
        crear_usuario(db, username="ana", email="ana_9e3@example.com", password="secret123")

        for _ in range(10):
            respuesta = client.post("/auth/login", json={"username": "", "password": ""})
            assert respuesta.status_code == 422

        # Si esos 10 intentos hubieran consumido el rate limit (5/15min de
        # la Fase 9C), este login válido devolvería 429 en vez de 200.
        exito = client.post("/auth/login", json={"username": "ana", "password": "secret123"})
        assert exito.status_code == 200


class TestCredencialesValidasExistentesSiguenFuncionando:
    def test_login_exitoso_sin_cambios(self, client, db):
        crear_usuario(db, username="beto", email="beto_9e@example.com", password="secret123")

        respuesta = client.post("/auth/login", json={"username": "beto", "password": "secret123"})

        assert respuesta.status_code == 200
        cuerpo = respuesta.json()
        assert cuerpo["user"]["username"] == "beto"
        assert "password" not in cuerpo["user"]
        assert "hashed_password" not in cuerpo["user"]
