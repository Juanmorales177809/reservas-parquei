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
from app.models import Usuario
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
