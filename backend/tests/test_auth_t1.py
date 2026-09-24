"""AUTH-T1 — Pruebas de sesión y autorización (carril A).

Cubre el criterio de aceptación de AUTH-T1 en specs/modules/auth/tasks.md:
sesión revocada, sesión vencida, inactividad superada, token con algoritmo
alterado, operación fuera de ámbito y operación sin permiso comprobable.

Reglas citadas por identificador completo (testing.md); nunca por familia.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt
import pytest

from app.core.authz import exigir_permiso, resolver_rol
from app.core.errors import NoAutorizado
from app.core.security import (
    ALGORITMO,
    AUDIENCIA,
    EMISOR,
    TIPO_ACCESO,
    emitir_token_acceso,
    verificar_token_acceso,
)
from app.db.models.auth import Sesiones
from tests.conftest import (
    crear_tecnico,
    crear_usuario_cuenta,
    headers_autenticados,
    iniciar_sesion,
)


def test_sesion_revocada_no_sirve(client, db, tag):
    """T-AUTH-03 · SEC-SES-07 (auth): cerrar sesión revoca; reusar la cookie da 401."""
    _, cuenta = crear_usuario_cuenta(db, tag)
    _, jar, _ = iniciar_sesion(client, cuenta.correo, "una frase larga de paso")

    cierre = client.delete("/api/auth/sesiones/actual", headers=headers_autenticados(jar))
    assert cierre.status_code == 204

    actual = client.get("/api/auth/sesiones/actual", headers=headers_autenticados(jar))
    assert actual.status_code == 401
    assert actual.json()["error"]["codigo"] == "NO_AUTENTICADO"


def test_sesion_vencida_no_sirve(client, db, tag):
    """T-AUTH-03 · SEC-SES-09 (auth): vigencia máxima superada da 401 aunque la firma valga."""
    _, cuenta = crear_usuario_cuenta(db, tag)
    _, jar, _ = iniciar_sesion(client, cuenta.correo, "una frase larga de paso")

    sesion = db.query(Sesiones).filter_by(id_cuenta=cuenta.id_cuenta).one()
    # El CHECK exige expires_at > created_at: se atrasa la sesión entera.
    sesion.created_at = datetime.now(timezone.utc) - timedelta(hours=13)
    sesion.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    db.commit()

    actual = client.get("/api/auth/sesiones/actual", headers=headers_autenticados(jar))
    assert actual.status_code == 401
    assert actual.json()["error"]["codigo"] == "NO_AUTENTICADO"


def test_inactividad_superada_no_sirve(client, db, tag):
    """T-AUTH-03 · SEC-SES-09 (auth): 30 min sin actividad dan 401."""
    _, cuenta = crear_usuario_cuenta(db, tag)
    _, jar, _ = iniciar_sesion(client, cuenta.correo, "una frase larga de paso")

    sesion = db.query(Sesiones).filter_by(id_cuenta=cuenta.id_cuenta).one()
    sesion.ultima_actividad_at = datetime.now(timezone.utc) - timedelta(minutes=31)
    db.commit()

    actual = client.get("/api/auth/sesiones/actual", headers=headers_autenticados(jar))
    assert actual.status_code == 401
    assert actual.json()["error"]["codigo"] == "NO_AUTENTICADO"


def test_token_manipulado_se_rechaza(db, tag):
    """T-AUTH-02 · SEC-JWT-01, SEC-JWT-02, SEC-JWT-05 (auth): servicio rechaza los cuatro."""
    from app.core.errors import NoAutenticado

    _, cuenta = crear_usuario_cuenta(db, tag)
    base = {
        "iss": EMISOR,
        "aud": AUDIENCIA,
        "sub": str(cuenta.id_cuenta),
        "sid": "00000000-0000-0000-0000-000000000000",
        "typ": TIPO_ACCESO,
    }

    import time

    ahora = int(time.time())
    bueno = emitir_token_acceso(sub=str(cuenta.id_cuenta), sid=base["sid"])
    assert verificar_token_acceso(bueno)["sub"] == str(cuenta.id_cuenta)

    # alg:none
    ninguno = jwt.encode({**base, "iat": ahora, "exp": ahora + 60}, key=None, algorithm="none")
    # algoritmo distinto (HS512 firmado con el secreto real)
    from app.core.config import get_settings

    distinto = jwt.encode(
        {**base, "iat": ahora, "exp": ahora + 60},
        get_settings().jwt_secret,
        algorithm="HS512",
    )
    # audiencia ajena
    ajena = jwt.encode(
        {**base, "aud": "otro-sistema", "iat": ahora, "exp": ahora + 60},
        get_settings().jwt_secret,
        algorithm=ALGORITMO,
    )
    # tipo incorrecto
    mal_tipo = jwt.encode(
        {**base, "typ": "refresh", "iat": ahora, "exp": ahora + 60},
        get_settings().jwt_secret,
        algorithm=ALGORITMO,
    )
    for token in (ninguno, distinto, ajena, mal_tipo):
        with pytest.raises(NoAutenticado):
            verificar_token_acceso(token)


def test_token_invalido_por_contrato_da_401(client):
    """T-AUTH-02 · SEC-JWT-01 (auth), nivel contrato: cookie forjada da 401, no 500."""
    respuesta = client.get(
        "/api/auth/sesiones/actual",
        headers={"Cookie": "rp_access=forjado"},
    )
    assert respuesta.status_code == 401
    assert respuesta.json()["error"]["codigo"] == "NO_AUTENTICADO"


def test_tecnico_fuera_de_su_unidad_vigente_se_deniega(db, tag):
    """T-AUTH-08 · RN-AUTH-ROL-05, RN-AUTH-ROL-06, SEC-AUTZ-01 (auth).

    El ámbito es la unidad vigente del cargo, nunca la unión de asignaciones:
    sobre una unidad ajena deniega sin comprobar el permiso.
    """
    cuenta, id_unidad = crear_tecnico(db, tag)

    contexto = resolver_rol(db, cuenta.id_cuenta)
    assert contexto.rol == "TECNICO"
    assert contexto.unidades_autorizadas == [id_unidad]

    # En su unidad con el permiso concedido: procede.
    exigir_permiso(db, cuenta.id_cuenta, "reservas.administrar", id_unidad=id_unidad)

    # Fuera de ámbito: deniega aunque el código exista.
    with pytest.raises(NoAutorizado):
        exigir_permiso(db, cuenta.id_cuenta, "reservas.administrar", id_unidad=id_unidad + 999983)


def test_sin_permiso_comprobable_deniega(db, tag):
    """T-AUTH-07 · SEC-AUTZ-02, SEC-AUTZ-04 (auth): el fallo abierto no es opción."""
    _, cuenta = crear_usuario_cuenta(db, tag)

    # Código inexistente, cuenta sin permisos y cuenta inexistente: las tres deniegan.
    with pytest.raises(NoAutorizado):
        exigir_permiso(db, cuenta.id_cuenta, "codigo.que.no.existe")
    with pytest.raises(NoAutorizado):
        exigir_permiso(db, cuenta.id_cuenta, "cuentas.administrar")
    with pytest.raises(NoAutorizado):
        exigir_permiso(db, 999999999, "cuentas.administrar")

    contexto = resolver_rol(db, 999999999)
    assert contexto.rol == "USUARIO"
    assert contexto.unidades_autorizadas == []
