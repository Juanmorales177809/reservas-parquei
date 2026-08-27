# -*- coding: utf-8 -*-
"""Verifica que `deps.py::decode_token` acepta el esquema REAL de
Supabase (JWT firmado ES256, verificado contra el JWKS público) además del
esquema HS256 legado que ya usa el resto de la suite
(`tests/conftest.py::token_supabase_para`).

Regresión de un bug real, confirmado corriendo el flujo completo contra un
proyecto de Supabase real el 2026-08-27: el backend rechazaba TODO login
real con 401, porque `decode_token` verificaba siempre con HS256 contra
`SUPABASE_JWT_SECRET`, y los proyectos de Supabase actuales firman con
ES256 (clave asimétrica, "JWT Signing Keys") -- un secreto compartido no
tiene nada que ver con eso.

Genera su propio par de claves EC P-256 local (nunca la clave privada real
de Supabase, que no sale de sus servidores) y mockea
`app.services.supabase_jwks._obtener_jwks` para nunca pegarle a la red --
mismo criterio que el resto de la suite con `httpx.post` de Supabase (ver
test_api_usuarios.py).
"""

import uuid

import pytest
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from jose import jwk as jose_jwk
from jose import jwt as jose_jwt

from app import deps
from app.services import supabase_jwks
from tests.conftest import crear_usuario

_KID = "clave-de-prueba-es256"


@pytest.fixture()
def par_de_claves_es256():
    """Genera un par EC P-256 local y lo devuelve como (pem_privada, jwk_publica)."""
    clave_privada = ec.generate_private_key(ec.SECP256R1())
    pem_privada = clave_privada.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    pem_publica = clave_privada.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    jwk_publica = jose_jwk.construct(pem_publica, algorithm="ES256").to_dict()
    jwk_publica["kid"] = _KID
    jwk_publica["use"] = "sig"
    return pem_privada, jwk_publica


@pytest.fixture(autouse=True)
def _limpia_cache_jwks():
    supabase_jwks._reset_cache_para_tests()
    yield
    supabase_jwks._reset_cache_para_tests()


def _token_es256(pem_privada, sub) -> str:
    return jose_jwt.encode(
        {"sub": str(sub), "email": "quien-sea@example.com", "aud": "authenticated"},
        pem_privada,
        algorithm="ES256",
        headers={"kid": _KID},
    )


def test_token_es256_valido_se_acepta(client, db, par_de_claves_es256, monkeypatch):
    pem_privada, jwk_publica = par_de_claves_es256
    monkeypatch.setattr(supabase_jwks, "_obtener_jwks", lambda forzar_refresco=False: {"keys": [jwk_publica]})

    usuario = crear_usuario(db, username="es256_ok", email="es256_ok@example.com")
    token = _token_es256(pem_privada, usuario.supabase_id)

    respuesta = client.get("/usuarios/me", cookies={"access_token": token})

    assert respuesta.status_code == 200
    assert respuesta.json()["id"] == usuario.id


def test_kid_no_encontrado_reintenta_una_vez_antes_de_rendirse(client, db, par_de_claves_es256, monkeypatch):
    """Simula rotación de clave: la primera respuesta del JWKS no trae la
    clave (como si Supabase la hubiera rotado hace poco), la segunda
    (forzada) sí -- `obtener_clave` debe recuperarse sola."""
    pem_privada, jwk_publica = par_de_claves_es256
    llamadas = []

    def _obtener_jwks_falso(forzar_refresco=False):
        llamadas.append(forzar_refresco)
        # Sin forzar: JWKS "viejo", sin la clave todavía. Forzado (la
        # rotación): ya trae la clave nueva.
        return {"keys": [jwk_publica]} if forzar_refresco else {"keys": []}

    monkeypatch.setattr(supabase_jwks, "_obtener_jwks", _obtener_jwks_falso)

    usuario = crear_usuario(db, username="es256_rot", email="es256_rot@example.com")
    token = _token_es256(pem_privada, usuario.supabase_id)

    respuesta = client.get("/usuarios/me", cookies={"access_token": token})

    assert respuesta.status_code == 200
    assert llamadas == [False, True]


def test_kid_inexistente_en_ambas_respuestas_da_401(client, db, par_de_claves_es256, monkeypatch):
    monkeypatch.setattr(supabase_jwks, "_obtener_jwks", lambda forzar_refresco=False: {"keys": []})

    usuario = crear_usuario(db, username="es256_sin_kid", email="es256_sin_kid@example.com")
    pem_privada, _ = par_de_claves_es256
    token = _token_es256(pem_privada, usuario.supabase_id)

    respuesta = client.get("/usuarios/me", cookies={"access_token": token})

    assert respuesta.status_code == 401


def test_token_firmado_con_otra_clave_es256_se_rechaza(client, db, par_de_claves_es256, monkeypatch):
    """La clave pública en el JWKS no coincide con la que firmó el token:
    debe fallar la verificación de firma, no solo la búsqueda de `kid`."""
    _, jwk_publica = par_de_claves_es256
    monkeypatch.setattr(supabase_jwks, "_obtener_jwks", lambda forzar_refresco=False: {"keys": [jwk_publica]})

    otra_clave_privada = ec.generate_private_key(ec.SECP256R1())
    otra_pem_privada = otra_clave_privada.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    usuario = crear_usuario(db, username="es256_firma_mala", email="es256_firma_mala@example.com")
    token = _token_es256(otra_pem_privada, usuario.supabase_id)

    respuesta = client.get("/usuarios/me", cookies={"access_token": token})

    assert respuesta.status_code == 401


def test_algoritmo_no_soportado_da_401(client, db):
    """Un token con un algoritmo que no es ES256 ni HS256 (el único otro
    que este backend acepta, y solo para tests) debe rechazarse sin
    intentar verificarlo con ninguna clave."""
    usuario = crear_usuario(db, username="alg_no_soportado", email="alg_no_soportado@example.com")
    token = jose_jwt.encode(
        {"sub": str(usuario.supabase_id), "aud": "authenticated"},
        "cualquier-secreto-de-32-caracteres-o-mas",
        algorithm="HS512",
    )

    respuesta = client.get("/usuarios/me", cookies={"access_token": token})

    assert respuesta.status_code == 401


def test_hs256_legado_sigue_funcionando_para_tests(client, db):
    """No se rompió el camino HS256 que usa el resto de la suite
    (tests/conftest.py::token_supabase_para) -- coexiste con ES256."""
    from tests.conftest import cookies_para

    usuario = crear_usuario(db, username="hs256_legado", email="hs256_legado@example.com")
    respuesta = client.get("/usuarios/me", headers=cookies_para(usuario))
    assert respuesta.status_code == 200
