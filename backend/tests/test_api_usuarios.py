# -*- coding: utf-8 -*-
"""Pruebas de integración de administración de usuarios (api/usuarios.py).

Reglas cubiertas:
- RN-002 (análogo): solo el admin crea usuarios.
- RN-003: gestor requiere espacio asignado.
- RN-004: un único rol por usuario (validado por patrón).
- Unicidad de username y email (409).
- Protección: el admin no puede eliminar su propia cuenta.
"""

from tests.conftest import crear_espacio, crear_usuario, headers_para


def _admin(db):
    return crear_usuario(db, username="admin_usr", email="admin_usr@test.com", rol="admin")


def test_crear_usuario_como_admin(client, db):
    admin = _admin(db)
    payload = {
        "username": "nuevo",
        "email": "nuevo@test.com",
        "password": "secret123",
        "rol": "usuario",
    }
    respuesta = client.post("/usuarios", json=payload, headers=headers_para(admin))
    assert respuesta.status_code == 201
    assert respuesta.json()["rol"] == "usuario"


def test_crear_usuario_solo_admin(client, db):
    usuario = crear_usuario(db, username="user_crea", email="user_crea@test.com")
    payload = {
        "username": "nuevo2",
        "email": "nuevo2@test.com",
        "password": "secret123",
        "rol": "usuario",
    }
    respuesta = client.post("/usuarios", json=payload, headers=headers_para(usuario))
    assert respuesta.status_code == 403


def test_username_duplicado_da_409(client, db):
    admin = _admin(db)
    crear_usuario(db, username="dup", email="dup@test.com")
    payload = {
        "username": "dup",
        "email": "dup2@test.com",
        "password": "secret123",
        "rol": "usuario",
    }
    respuesta = client.post("/usuarios", json=payload, headers=headers_para(admin))
    assert respuesta.status_code == 409


def test_email_duplicado_da_409(client, db):
    admin = _admin(db)
    crear_usuario(db, username="dup_a", email="repetido@test.com")
    payload = {
        "username": "dup_b",
        "email": "repetido@test.com",
        "password": "secret123",
        "rol": "usuario",
    }
    respuesta = client.post("/usuarios", json=payload, headers=headers_para(admin))
    assert respuesta.status_code == 409


def test_gestor_sin_espacio_da_400(client, db):
    admin = _admin(db)
    payload = {
        "username": "gestor_solo",
        "email": "gestor_solo@test.com",
        "password": "secret123",
        "rol": "gestor",
    }
    respuesta = client.post("/usuarios", json=payload, headers=headers_para(admin))
    assert respuesta.status_code == 400


def test_gestor_con_espacio(client, db):
    admin = _admin(db)
    espacio = crear_espacio(db, nombre="Sala Gestores")
    payload = {
        "username": "gestor_ok",
        "email": "gestor_ok@test.com",
        "password": "secret123",
        "rol": "gestor",
        "espacio_id": espacio.id,
    }
    respuesta = client.post("/usuarios", json=payload, headers=headers_para(admin))
    assert respuesta.status_code == 201
    assert respuesta.json()["espacio"]["nombre"] == "Sala Gestores"


def test_admin_no_puede_eliminarse_a_si_mismo(client, db):
    admin = _admin(db)
    respuesta = client.delete(f"/usuarios/{admin.id}", headers=headers_para(admin))
    assert respuesta.status_code == 409


def test_listar_usuarios_solo_admin(client, db):
    usuario = crear_usuario(db, username="user_list", email="user_list@test.com")
    admin = _admin(db)
    assert client.get("/usuarios", headers=headers_para(usuario)).status_code == 403
    respuesta = client.get("/usuarios", headers=headers_para(admin))
    assert respuesta.status_code == 200
    assert len(respuesta.json()) == 2


def test_actualizar_email_de_usuario(client, db):
    admin = _admin(db)
    objetivo = crear_usuario(db, username="objetivo", email="objetivo@test.com")
    respuesta = client.put(
        f"/usuarios/{objetivo.id}",
        json={"email": "objetivo_nuevo@test.com"},
        headers=headers_para(admin),
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["email"] == "objetivo_nuevo@test.com"
