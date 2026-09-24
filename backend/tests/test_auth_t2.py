"""AUTH-T2 — Pruebas de tokens y no enumeración (carril B).

Cubre el criterio de aceptación de AUTH-T2 en specs/modules/auth/tasks.md:
reutilizar un token de recuperación o de invitación falla, reemitir invalida
el anterior, y registro, recuperación e inicio de sesión responden igual con
correo existente e inexistente.

Reglas citadas por identificador completo (testing.md); nunca por familia.
"""

from __future__ import annotations

from app.core.security import generar_token, hashear_token
from app.modules.auth import repository_cuentas as repo_cuentas
from tests.conftest import (
    correo_para,
    crear_admin,
    crear_usuario_cuenta,
    headers_autenticados,
    iniciar_sesion,
    obtener_csrf,
)

MENSAJE_REGISTRO = "Si el correo puede registrarse, la cuenta quedará disponible para iniciar sesión."
MENSAJE_RECUPERACION = "Si existe una cuenta asociada, se enviarán las instrucciones de recuperación."
NUEVA_CONTRASENA = "una frase nueva de paso larga"


def test_token_recuperacion_es_de_un_solo_uso_y_revoca_sesiones(client, db, tag):
    """T-AUTH-13 · SEC-TOK-05, SEC-REC-03 (auth): reusar da 410 y revoca sesiones."""
    _, cuenta = crear_usuario_cuenta(db, tag)
    _, jar, _ = iniciar_sesion(client, cuenta.correo, "una frase larga de paso")

    crudo, _ = generar_token()
    repo_cuentas.crear_token_recuperacion(db, cuenta.id_cuenta, hashear_token(crudo))
    db.commit()

    headers, _ = obtener_csrf(client)
    restablecer = client.post(
        f"/api/auth/recuperacion/{crudo}",
        json={"contrasena": NUEVA_CONTRASENA},
        headers=headers,
    )
    assert restablecer.status_code == 204, restablecer.text

    # La sesión anterior quedó revocada.
    actual = client.get(
        "/api/auth/sesiones/actual",
        headers=headers_autenticados(jar),
    )
    assert actual.status_code == 401

    # Reutilizar el mismo token falla y la contraseña nueva sí sirve.
    headers2, _ = obtener_csrf(client)
    reuso = client.post(
        f"/api/auth/recuperacion/{crudo}",
        json={"contrasena": "otra frase larga de paso"},
        headers=headers2,
    )
    assert reuso.status_code == 410
    assert reuso.json()["error"]["codigo"] == "TOKEN_NO_VIGENTE"

    _, jar_nueva, _ = iniciar_sesion(client, cuenta.correo, NUEVA_CONTRASENA)
    assert "rp_access" in jar_nueva


def test_reenviar_invitacion_invalida_la_anterior(client, db, tag):
    """T-AUTH-14 · SEC-INV-02, SEC-INV-03 (auth): el primer token ya no sirve."""
    admin = crear_admin(db, tag)
    correo = correo_para(tag, "invitado")
    usuario = repo_cuentas.crear_identidad_usuario(
        db,
        nombre=f"Invitado {tag}",
        documento=f"40{tag[:8]}",
        telefono=f"303{tag[:7]}",
        institucion="ITM",
        dependencia="Facultad",
        correo=correo,
    )
    db.commit()

    crudo_viejo, _ = generar_token()
    inv = repo_cuentas.crear_invitacion(
        db,
        correo=correo,
        tipo_cuenta="USUARIO",
        token_hash=hashear_token(crudo_viejo),
        creada_por=admin.id_cuenta,
        id_usuario=usuario.id_usuario,
    )
    db.commit()

    _, jar_admin, _ = iniciar_sesion(client, admin.correo, "una frase larga de paso admin")
    reenvio = client.post(
        f"/api/auth/invitaciones/{inv.id}/reenvio",
        headers=headers_autenticados(jar_admin),
    )
    assert reenvio.status_code == 200, reenvio.text

    headers2, _ = obtener_csrf(client)
    activar_viejo = client.post(
        f"/api/auth/invitaciones/{crudo_viejo}/activacion",
        json={"contrasena": NUEVA_CONTRASENA},
        headers=headers2,
    )
    assert activar_viejo.status_code == 410
    assert activar_viejo.json()["error"]["codigo"] == "TOKEN_NO_VIGENTE"


def test_registro_responde_igual_exista_o_no(client, tag):
    """T-AUTH-11 · SEC-ABU-02 (auth): la respuesta no revela si el correo existe."""
    cuerpo = {
        "nombre": f"Registro {tag}",
        "documento": f"50{tag[:8]}",
        "telefono": f"304{tag[:7]}",
        "institucion": "ITM",
        "dependencia": "Facultad",
        "correo": correo_para(tag, "nuevo"),
        "contrasena": "una frase larga de paso",
    }
    headers, _ = obtener_csrf(client)
    primera = client.post("/api/auth/registro", json=cuerpo, headers=headers)
    assert primera.status_code == 202

    headers2, _ = obtener_csrf(client)
    segunda = client.post("/api/auth/registro", json=cuerpo, headers=headers2)
    assert segunda.status_code == 202
    assert segunda.json() == primera.json() == {"mensaje": MENSAJE_REGISTRO}


def test_recuperacion_responde_igual_exista_o_no(client, db, tag):
    """T-AUTH-11 · SEC-REC-01 (auth): la solicitud no revela cuentas registradas."""
    _, cuenta = crear_usuario_cuenta(db, tag)

    headers, _ = obtener_csrf(client)
    existente = client.post(
        "/api/auth/recuperacion", json={"correo": cuenta.correo}, headers=headers
    )
    assert existente.status_code == 202

    headers2, _ = obtener_csrf(client)
    inexistente = client.post(
        "/api/auth/recuperacion",
        json={"correo": correo_para(tag, "nadie")},
        headers=headers2,
    )
    assert inexistente.status_code == 202
    assert inexistente.json() == existente.json() == {"mensaje": MENSAJE_RECUPERACION}


def test_login_no_distingue_la_causa(client, db, tag):
    """T-AUTH-10 · RN-AUTH-ID-01, SEC-ABU-02 (auth): mismo 401 en los tres casos."""
    _, cuenta = crear_usuario_cuenta(db, tag)

    headers, _ = obtener_csrf(client)
    mala_clave = client.post(
        "/api/auth/sesiones",
        json={"correo": cuenta.correo, "contrasena": "clave incorrecta larga"},
        headers=headers,
    )
    assert mala_clave.status_code == 401

    headers2, _ = obtener_csrf(client)
    inexistente = client.post(
        "/api/auth/sesiones",
        json={"correo": correo_para(tag, "fantasma"), "contrasena": "clave incorrecta larga"},
        headers=headers2,
    )
    assert inexistente.status_code == 401

    cuenta.estado = False
    db.commit()
    headers3, _ = obtener_csrf(client)
    inactiva = client.post(
        "/api/auth/sesiones",
        json={"correo": cuenta.correo, "contrasena": "una frase larga de paso"},
        headers=headers3,
    )
    assert inactiva.status_code == 401

    assert mala_clave.json() == inexistente.json() == inactiva.json()
    assert mala_clave.json()["error"]["codigo"] == "CREDENCIALES_INVALIDAS"


def test_token_nunca_aparece_en_una_respuesta(client, db, tag):
    """T-AUTH-15 · SEC-TOK-02, SEC-INV-01 (auth): emisión y solicitud no exponen el token."""
    admin = crear_admin(db, tag)
    correo = correo_para(tag, "invitado")
    repo_cuentas.crear_identidad_usuario(
        db,
        nombre=f"Invitado {tag}",
        documento=f"60{tag[:8]}",
        telefono=f"305{tag[:7]}",
        institucion="ITM",
        dependencia="Facultad",
        correo=correo,
    )
    db.commit()

    _, jar_admin, _ = iniciar_sesion(client, admin.correo, "una frase larga de paso admin")
    emision = client.post(
        "/api/auth/invitaciones",
        json={"correo": correo, "tipo_cuenta": "USUARIO", "id_unidad": None},
        headers=headers_autenticados(jar_admin),
    )
    assert emision.status_code == 201, emision.text
    cuerpo = emision.json()
    assert set(cuerpo) == {"id", "correo", "tipo_cuenta", "expira_en", "estado"}
    assert "token" not in emision.text.lower().replace("tipo_cuenta", "")

    headers2, _ = obtener_csrf(client)
    solicitud = client.post(
        "/api/auth/recuperacion", json={"correo": correo}, headers=headers2
    )
    assert solicitud.status_code == 202
    assert solicitud.json() == {"mensaje": MENSAJE_RECUPERACION}
    assert "token_hash" not in solicitud.text
