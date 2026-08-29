# -*- coding: utf-8 -*-
"""Pruebas de integración de `POST /auth/supabase/sesion` (api/auth.py).

Reglas cubiertas:
- Un JWT de Supabase válido, cuyo `sub` coincide con un `usuarios.supabase_id`
  existente, entrega los datos de ese usuario; la sesión viaja en la cookie
  HttpOnly, el body nunca lleva el token.
- Un token inválido (malformado o mal firmado) responde 401 genérico.
- **El caso central de esta migración**: un JWT de Supabase válido y
  correctamente firmado, pero cuyo `sub` NO corresponde a ningún usuario
  dado de alta acá, responde 403 -- nunca crea una cuenta nueva ni la
  vincula por email. Es la prueba directa del hueco de seguridad que tenía
  la versión anterior de este mismo endpoint (auto-alta/auto-vínculo por
  email desde un request anónimo).
- La respuesta nunca expone el hash de contraseña.
"""

import uuid

from jose import jwt as jose_jwt

from app.config import settings
from app.models import CorreoSaliente, Usuario
from app.services.supabase_admin import SupabaseAdminError
from tests.conftest import crear_usuario, token_supabase_para


def test_supabase_sesion_exitosa_con_usuario_existente(client, db):
    usuario = crear_usuario(db, username="ana", email="ana@example.com")

    respuesta = client.post(
        "/auth/supabase/sesion",
        json={"supabase_token": token_supabase_para(usuario)},
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["user"]["username"] == "ana"
    assert "hashed_password" not in cuerpo["user"]
    assert "access_token" not in cuerpo


def test_supabase_sesion_exitosa_con_personal_admin_o_gestor(client, db):
    """Regresión real encontrada en esta misma sesión: al separar
    `personal`/`usuarios` en dos tablas (ver
    `~/.claude/plans/dazzling-wobbling-zebra.md`), este endpoint quedó
    buscando solo en `usuarios` -- un admin o gestor real (vive en
    `personal` desde la separación) no podía iniciar sesión en absoluto.
    Ningún test lo detectó porque todos los `test_supabase_sesion_*`
    existentes usaban `crear_usuario(...)` con el rol default (usuario).
    """
    admin = crear_usuario(db, username="admin_login", email="admin_login@example.com", rol="admin")
    gestor = crear_usuario(db, username="gestor_login", email="gestor_login@example.com", rol="gestor")

    for personal in (admin, gestor):
        respuesta = client.post(
            "/auth/supabase/sesion",
            json={"supabase_token": token_supabase_para(personal)},
        )
        assert respuesta.status_code == 200
        assert respuesta.json()["user"]["username"] == personal.username
        assert respuesta.json()["user"]["rol"] == personal.rol


def test_supabase_sesion_fija_la_cookie(client, db):
    usuario = crear_usuario(db, username="ana2", email="ana2@example.com")

    respuesta = client.post(
        "/auth/supabase/sesion",
        json={"supabase_token": token_supabase_para(usuario)},
    )

    assert "access_token" in respuesta.cookies
    assert respuesta.cookies["access_token"]


def test_supabase_sesion_token_malformado_da_401(client):
    respuesta = client.post(
        "/auth/supabase/sesion",
        json={"supabase_token": "esto-no-es-un-jwt-en-absoluto"},
    )
    assert respuesta.status_code == 401
    assert respuesta.json()["detail"] == "Token de Supabase inválido"


def test_supabase_sesion_usuario_no_existente_da_403_no_crea_ni_vincula(client, db):
    """El caso que cierra el hueco de seguridad: un JWT perfectamente
    válido (firmado con el mismo secreto, `sub` con forma de UUID
    correcta) pero para un `supabase_id` que ningún admin dio de alta acá.
    """
    crear_usuario(db, username="ana3", email="ana3@example.com")
    token = jose_jwt.encode(
        {"sub": str(uuid.uuid4()), "email": "quien-sea@example.com", "aud": "authenticated"},
        settings.supabase_jwt_secret,
        algorithm=settings.algorithm,
    )

    respuesta = client.post("/auth/supabase/sesion", json={"supabase_token": token})

    assert respuesta.status_code == 403
    # No se creó ninguna cuenta nueva a partir de este intento.
    assert db.query(Usuario).filter(Usuario.email == "quien-sea@example.com").first() is None


def test_recuperar_password_cuenta_existente_encola_el_correo(client, db, monkeypatch):
    crear_usuario(db, username="con_cuenta", email="con_cuenta@example.com")
    monkeypatch.setattr(
        "app.api.auth.generar_link_recuperacion",
        lambda email: f"https://ejemplo.supabase.co/auth/v1/verify?token=fake&type=recovery&email={email}",
    )

    respuesta = client.post("/auth/recuperar", json={"email": "con_cuenta@example.com"})

    assert respuesta.status_code == 204
    correo = db.query(CorreoSaliente).filter(CorreoSaliente.destinatario == "con_cuenta@example.com").one()
    assert correo.es_html is True
    assert "con_cuenta" in correo.cuerpo


def test_recuperar_password_cuenta_de_personal_tambien_encola_el_correo(client, db, monkeypatch):
    """Un admin/gestor (vive en `personal`) también puede recuperar su
    contraseña -- antes de este fix, `recuperar_password` solo consultaba
    `usuarios`, así que un admin real nunca recibía el correo pese a que
    `generar_link_recuperacion` sí generaba el link contra Supabase."""
    crear_usuario(db, username="gestor_recupera", email="gestor_recupera@example.com", rol="gestor")
    monkeypatch.setattr(
        "app.api.auth.generar_link_recuperacion",
        lambda email: f"https://ejemplo.supabase.co/auth/v1/verify?token=fake&type=recovery&email={email}",
    )

    respuesta = client.post("/auth/recuperar", json={"email": "gestor_recupera@example.com"})

    assert respuesta.status_code == 204
    correo = db.query(CorreoSaliente).filter(CorreoSaliente.destinatario == "gestor_recupera@example.com").one()
    assert correo.es_html is True
    assert "gestor_recupera" in correo.cuerpo


def test_recuperar_password_cuenta_inexistente_responde_igual_sin_encolar(client, db, monkeypatch):
    """El invariante central: la respuesta (204, sin body) es idéntica exista
    o no la cuenta -- acá simulamos el `None` que devuelve
    `generar_link_recuperacion` cuando Supabase rechaza `type=recovery` para
    un email no registrado."""
    monkeypatch.setattr("app.api.auth.generar_link_recuperacion", lambda email: None)

    respuesta = client.post("/auth/recuperar", json={"email": "no-existe@example.com"})

    assert respuesta.status_code == 204
    assert db.query(CorreoSaliente).filter(CorreoSaliente.destinatario == "no-existe@example.com").first() is None


def test_recuperar_password_email_invalido_da_422(client):
    respuesta = client.post("/auth/recuperar", json={"email": "no-es-un-email"})
    assert respuesta.status_code == 422


def test_registro_exitoso_crea_usuario_con_rol_usuario(client, db, monkeypatch):
    monkeypatch.setattr("app.api.auth.crear_usuario_confirmado", lambda email, password: uuid.uuid4())

    respuesta = client.post(
        "/auth/registro",
        json={"username": "nuevo", "email": "nuevo@example.com", "password": "ClaveSegura123"},
    )

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["username"] == "nuevo"
    assert cuerpo["rol"] == "usuario"
    assert "hashed_password" not in cuerpo
    usuario = db.query(Usuario).filter(Usuario.email == "nuevo@example.com").first()
    assert usuario is not None
    assert usuario.supabase_id is not None


def test_registro_username_duplicado_da_409(client, db, monkeypatch):
    crear_usuario(db, username="ya_existe", email="otro@example.com")
    monkeypatch.setattr("app.api.auth.crear_usuario_confirmado", lambda email, password: uuid.uuid4())

    respuesta = client.post(
        "/auth/registro",
        json={"username": "ya_existe", "email": "nuevo2@example.com", "password": "ClaveSegura123"},
    )

    assert respuesta.status_code == 409


def test_registro_email_duplicado_da_409(client, db, monkeypatch):
    crear_usuario(db, username="otro_user", email="ocupado@example.com")
    monkeypatch.setattr("app.api.auth.crear_usuario_confirmado", lambda email, password: uuid.uuid4())

    respuesta = client.post(
        "/auth/registro",
        json={"username": "nuevo3", "email": "ocupado@example.com", "password": "ClaveSegura123"},
    )

    assert respuesta.status_code == 409


def test_registro_username_duplicado_contra_personal_da_409(client, db, monkeypatch):
    """Mismo motivo que `test_supabase_sesion_exitosa_con_personal_admin_o_gestor`:
    la unicidad de username/email ya no la garantiza PostgreSQL sola (dos
    tablas separadas, cada una con su propia constraint) -- el check de
    aplicación tiene que mirar `personal` también."""
    crear_usuario(db, username="gestor_ya_existe", email="gestor_existe@example.com", rol="gestor")
    monkeypatch.setattr("app.api.auth.crear_usuario_confirmado", lambda email, password: uuid.uuid4())

    respuesta = client.post(
        "/auth/registro",
        json={"username": "gestor_ya_existe", "email": "nuevo5b@example.com", "password": "ClaveSegura123"},
    )

    assert respuesta.status_code == 409


def test_registro_email_duplicado_contra_personal_da_409(client, db, monkeypatch):
    crear_usuario(db, username="admin_ya_existe", email="admin_existe@example.com", rol="admin")
    monkeypatch.setattr("app.api.auth.crear_usuario_confirmado", lambda email, password: uuid.uuid4())

    respuesta = client.post(
        "/auth/registro",
        json={"username": "nuevo5c", "email": "admin_existe@example.com", "password": "ClaveSegura123"},
    )

    assert respuesta.status_code == 409


def test_registro_password_corta_da_422(client):
    respuesta = client.post(
        "/auth/registro",
        json={"username": "nuevo4", "email": "nuevo4@example.com", "password": "corta"},
    )

    assert respuesta.status_code == 422


def test_registro_email_invalido_da_422(client):
    respuesta = client.post(
        "/auth/registro",
        json={"username": "nuevo5", "email": "no-es-un-email", "password": "ClaveSegura123"},
    )

    assert respuesta.status_code == 422


def test_registro_falla_en_supabase_da_502_y_no_crea_usuario_local(client, db, monkeypatch):
    def _falla(email, password):
        raise SupabaseAdminError("boom")

    monkeypatch.setattr("app.api.auth.crear_usuario_confirmado", _falla)

    respuesta = client.post(
        "/auth/registro",
        json={"username": "nuevo6", "email": "nuevo6@example.com", "password": "ClaveSegura123"},
    )

    assert respuesta.status_code == 502
    assert db.query(Usuario).filter(Usuario.email == "nuevo6@example.com").first() is None
