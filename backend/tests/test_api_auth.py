# -*- coding: utf-8 -*-
"""Pruebas de integración del endpoint de autenticación (api/auth.py).

Reglas cubiertas:
- Inicio de sesión con credenciales válidas entrega JWT y datos del usuario.
- Credenciales inválidas o usuario inexistente responden 401 genérico.
- La respuesta nunca expone el hash de contraseña.
"""

from tests.conftest import crear_usuario


def test_login_exitoso(client, db):
    crear_usuario(db, username="ana", email="ana@example.com", password="secret123")
    respuesta = client.post(
        "/auth/login", json={"username": "ana", "password": "secret123"}
    )
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["token_type"] == "bearer"
    assert cuerpo["access_token"]
    assert cuerpo["user"]["username"] == "ana"
    assert "hashed_password" not in cuerpo["user"]


def test_login_password_incorrecta_da_401(client, db):
    crear_usuario(db, username="ana", email="ana@example.com", password="secret123")
    respuesta = client.post(
        "/auth/login", json={"username": "ana", "password": "incorrecta"}
    )
    assert respuesta.status_code == 401


def test_login_usuario_inexistente_da_401(client, db):
    respuesta = client.post(
        "/auth/login", json={"username": "fantasma", "password": "secret123"}
    )
    assert respuesta.status_code == 401
