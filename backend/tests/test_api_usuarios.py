# -*- coding: utf-8 -*-
"""Pruebas de integración de administración de usuarios (api/usuarios.py).

Reglas cubiertas:
- RN-002 (análogo): solo el admin crea usuarios.
- RN-003: gestor requiere espacio asignado.
- RN-004: un único rol por usuario (validado por patrón).
- Unicidad de username y email (409).
- Protección: el admin no puede eliminar su propia cuenta.
- Migración a Supabase Auth: crear un usuario invita por email vía la API
  de administración de Supabase y guarda el `supabase_id` devuelto -- nunca
  se le pega a la red real de Supabase en tests (ver el fixture
  `_supabase_invitar_mockeado` abajo).
"""

import uuid

import pytest

from app.models import Usuario
from app.services.supabase_admin import SupabaseAdminError
from tests.conftest import crear_espacio, crear_usuario, cookies_para


@pytest.fixture(autouse=True)
def _supabase_invitar_mockeado(monkeypatch):
    """`create_usuario_admin` invita por email vía Supabase en cada alta --
    se reemplaza por un doble que nunca toca la red, devolviendo un UUID
    nuevo por llamada (mismo criterio que el doble de SMTP en
    test_correo_saliente.py)."""
    monkeypatch.setattr("app.api.usuarios.invitar_usuario", lambda email: uuid.uuid4())


def _admin(db):
    return crear_usuario(db, username="admin_usr", email="admin_usr@example.com", rol="admin")


def test_crear_usuario_como_admin(client, db):
    admin = _admin(db)
    payload = {
        "username": "nuevo",
        "email": "nuevo@example.com",
        "password": "secret123",
        "rol": "usuario",
    }
    respuesta = client.post("/usuarios", json=payload, headers=cookies_para(admin))
    assert respuesta.status_code == 201
    assert respuesta.json()["rol"] == "usuario"


def test_crear_usuario_guarda_el_supabase_id_de_la_invitacion(client, db):
    admin = _admin(db)
    payload = {"username": "nuevo_supa", "email": "nuevo_supa@example.com", "rol": "usuario"}

    respuesta = client.post("/usuarios", json=payload, headers=cookies_para(admin))

    assert respuesta.status_code == 201
    creado = db.query(Usuario).filter(Usuario.username == "nuevo_supa").first()
    assert creado.supabase_id is not None


def test_crear_usuario_si_supabase_falla_da_502_y_no_crea_nada(client, db, monkeypatch):
    admin = _admin(db)

    def _falla(email):
        raise SupabaseAdminError("simulado: Supabase Cloud no responde")

    monkeypatch.setattr("app.api.usuarios.invitar_usuario", _falla)

    payload = {"username": "fallido", "email": "fallido@example.com", "rol": "usuario"}
    respuesta = client.post("/usuarios", json=payload, headers=cookies_para(admin))

    assert respuesta.status_code == 502
    assert db.query(Usuario).filter(Usuario.username == "fallido").first() is None


def test_crear_usuario_solo_admin(client, db):
    usuario = crear_usuario(db, username="user_crea", email="user_crea@example.com")
    payload = {
        "username": "nuevo2",
        "email": "nuevo2@example.com",
        "password": "secret123",
        "rol": "usuario",
    }
    respuesta = client.post("/usuarios", json=payload, headers=cookies_para(usuario))
    assert respuesta.status_code == 403


def test_username_duplicado_da_409(client, db):
    admin = _admin(db)
    crear_usuario(db, username="dup", email="dup@example.com")
    payload = {
        "username": "dup",
        "email": "dup2@example.com",
        "password": "secret123",
        "rol": "usuario",
    }
    respuesta = client.post("/usuarios", json=payload, headers=cookies_para(admin))
    assert respuesta.status_code == 409


def test_email_duplicado_da_409(client, db):
    admin = _admin(db)
    crear_usuario(db, username="dup_a", email="repetido@example.com")
    payload = {
        "username": "dup_b",
        "email": "repetido@example.com",
        "password": "secret123",
        "rol": "usuario",
    }
    respuesta = client.post("/usuarios", json=payload, headers=cookies_para(admin))
    assert respuesta.status_code == 409


def test_gestor_sin_espacio_da_400(client, db):
    admin = _admin(db)
    payload = {
        "username": "gestor_solo",
        "email": "gestor_solo@example.com",
        "password": "secret123",
        "rol": "gestor",
    }
    respuesta = client.post("/usuarios", json=payload, headers=cookies_para(admin))
    assert respuesta.status_code == 400


def test_gestor_con_espacio(client, db):
    admin = _admin(db)
    espacio = crear_espacio(db, nombre="Sala Gestores")
    payload = {
        "username": "gestor_ok",
        "email": "gestor_ok@example.com",
        "password": "secret123",
        "rol": "gestor",
        "espacio_id": espacio.id,
    }
    respuesta = client.post("/usuarios", json=payload, headers=cookies_para(admin))
    assert respuesta.status_code == 201
    assert respuesta.json()["espacio"]["nombre"] == "Sala Gestores"


def test_admin_no_puede_eliminarse_a_si_mismo(client, db):
    admin = _admin(db)
    respuesta = client.delete(f"/usuarios/{admin.id}", headers=cookies_para(admin))
    assert respuesta.status_code == 409


def test_listar_usuarios_solo_admin(client, db):
    usuario = crear_usuario(db, username="user_list", email="user_list@example.com")
    admin = _admin(db)
    assert client.get("/usuarios", headers=cookies_para(usuario)).status_code == 403
    respuesta = client.get("/usuarios", headers=cookies_para(admin))
    assert respuesta.status_code == 200
    assert len(respuesta.json()) == 2


def test_actualizar_email_de_usuario(client, db):
    admin = _admin(db)
    objetivo = crear_usuario(db, username="objetivo", email="objetivo@example.com")
    respuesta = client.put(
        f"/usuarios/{objetivo.id}",
        json={"email": "objetivo_nuevo@example.com"},
        headers=cookies_para(admin),
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["email"] == "objetivo_nuevo@example.com"
