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

from app.models import CorreoSaliente, Usuario
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


def test_eliminar_usuario_borra_tambien_su_identidad_de_supabase(client, db, monkeypatch):
    """Regresión de un bug real en producción (2026-08-27): borrar un
    usuario solo tocaba reservas_db, nunca Supabase -- la identidad
    quedaba huérfana ahí y reinvitar el mismo email fallaba con 422
    email_exists contra una cuenta que ya no existía de nuestro lado."""
    admin = _admin(db)
    objetivo = crear_usuario(db, username="a_borrar", email="a_borrar@example.com")

    llamadas = []
    monkeypatch.setattr("app.api.usuarios.eliminar_usuario_supabase", lambda supabase_id: llamadas.append(supabase_id))

    respuesta = client.delete(f"/usuarios/{objetivo.id}", headers=cookies_para(admin))

    assert respuesta.status_code == 204
    assert llamadas == [objetivo.supabase_id]
    assert db.query(Usuario).filter(Usuario.id == objetivo.id).first() is None


def test_eliminar_usuario_si_supabase_falla_da_502_y_no_borra_la_fila_local(client, db, monkeypatch):
    """Orden deliberado (Supabase primero, fila local después): si
    Supabase falla, la fila local se conserva -- lo contrario dejaría al
    admin creyendo que borró al usuario mientras su identidad de Supabase
    sigue viva y funcional."""
    admin = _admin(db)
    objetivo = crear_usuario(db, username="no_se_borra", email="no_se_borra@example.com")

    def _falla(supabase_id):
        raise SupabaseAdminError("simulado: Supabase Cloud no responde")

    monkeypatch.setattr("app.api.usuarios.eliminar_usuario_supabase", _falla)

    respuesta = client.delete(f"/usuarios/{objetivo.id}", headers=cookies_para(admin))

    assert respuesta.status_code == 502
    assert db.query(Usuario).filter(Usuario.id == objetivo.id).first() is not None


def test_reenviar_invitacion_devuelve_el_link(client, db, monkeypatch):
    """Regresión de un pedido real: el correo original puede no llegar
    (spam) o el link vencer -- /auth/v1/invite no sirve para reenviar
    (Supabase lo rechaza con email_exists para cualquier email ya
    registrado, probado contra el proyecto real el 2026-08-27), así que el
    endpoint usa generate_link en su lugar."""
    admin = _admin(db)
    objetivo = crear_usuario(db, username="a_reinvitar", email="a_reinvitar@example.com")

    monkeypatch.setattr(
        "app.api.usuarios.generar_link_invitacion",
        lambda email: f"https://ijktwqnkknemjrokwcdn.supabase.co/auth/v1/verify?token=fake&type=invite&email={email}",
    )

    respuesta = client.post(f"/usuarios/{objetivo.id}/reenviar-invitacion", headers=cookies_para(admin))

    assert respuesta.status_code == 200
    data = respuesta.json()
    assert "a_reinvitar@example.com" in data["link"]
    # EMAIL_ENABLED=false en tests (conftest.py no lo activa): el correo
    # queda encolado pero no se intenta enviar de verdad.
    assert data["correo_enviado"] is False

    correo = db.query(CorreoSaliente).filter(CorreoSaliente.destinatario == "a_reinvitar@example.com").one()
    assert correo.es_html is True
    assert "a_reinvitar" in correo.cuerpo
    assert "Reservas Parque i" in correo.cuerpo


def test_reenviar_invitacion_solo_admin(client, db, monkeypatch):
    monkeypatch.setattr("app.api.usuarios.generar_link_invitacion", lambda email: "https://example.com/link")
    usuario = crear_usuario(db, username="no_admin", email="no_admin@example.com")
    objetivo = crear_usuario(db, username="objetivo_reenvio", email="objetivo_reenvio@example.com")

    respuesta = client.post(f"/usuarios/{objetivo.id}/reenviar-invitacion", headers=cookies_para(usuario))

    assert respuesta.status_code == 403


def test_reenviar_invitacion_usuario_inexistente_da_404(client, db, monkeypatch):
    monkeypatch.setattr("app.api.usuarios.generar_link_invitacion", lambda email: "https://example.com/link")
    admin = _admin(db)

    respuesta = client.post("/usuarios/999999/reenviar-invitacion", headers=cookies_para(admin))

    assert respuesta.status_code == 404


def test_reenviar_invitacion_sin_supabase_id_da_409(client, db, monkeypatch):
    """No debería poder pasar en la práctica (todo usuario se crea vía
    invitar_usuario, que siempre guarda un supabase_id), pero si alguna
    vez queda una fila así, reenviar debe fallar con un mensaje claro en
    vez de mandarle `None` a Supabase."""
    monkeypatch.setattr("app.api.usuarios.generar_link_invitacion", lambda email: "https://example.com/link")
    admin = _admin(db)
    objetivo = crear_usuario(db, username="sin_supabase_id", email="sin_supabase_id@example.com")
    objetivo.supabase_id = None
    db.commit()

    respuesta = client.post(f"/usuarios/{objetivo.id}/reenviar-invitacion", headers=cookies_para(admin))

    assert respuesta.status_code == 409


def test_reenviar_invitacion_si_supabase_falla_da_502(client, db, monkeypatch):
    admin = _admin(db)
    objetivo = crear_usuario(db, username="reenvio_falla", email="reenvio_falla@example.com")

    def _falla(email):
        raise SupabaseAdminError("simulado: Supabase Cloud no responde")

    monkeypatch.setattr("app.api.usuarios.generar_link_invitacion", _falla)

    respuesta = client.post(f"/usuarios/{objetivo.id}/reenviar-invitacion", headers=cookies_para(admin))

    assert respuesta.status_code == 502
