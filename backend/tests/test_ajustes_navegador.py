"""Pruebas de los ajustes hechos al probar la aplicación en un navegador real.

- La cookie de acceso usa Path=/ (si no, el frontend no la recibe al renderizar páginas).
- El listado de recursos devuelve `nombre`, para elegirlos por nombre en las pantallas.
- Usuarios y personal devuelven `id_cuenta`, para elegir cuentas por nombre.
"""

from __future__ import annotations

from sqlalchemy import text

from .conftest import (
    crear_admin,
    crear_usuario_cuenta,
    headers_autenticados,
    iniciar_sesion,
    obtener_csrf,
    otorgar_permiso_global,
)

from app.db.models.identidad import UnidadOrganizacional


def test_cookie_de_acceso_usa_path_raiz(client, db, tag):
    _, cuenta = crear_usuario_cuenta(db, f"c{tag}")
    headers, _ = obtener_csrf(client)
    r = client.post(
        "/api/auth/sesiones",
        json={"correo": cuenta.correo, "contrasena": "una frase larga de paso"},
        headers=headers,
    )
    assert r.status_code == 201
    cookies = {c.split("=", 1)[0]: c.lower() for c in r.headers.get_list("set-cookie")}
    assert "path=/;" in cookies["rp_access"] and "path=/api" not in cookies["rp_access"]
    assert "httponly" in cookies["rp_access"] and "secure" in cookies["rp_access"]
    assert "path=/api/auth/sesiones" in cookies["rp_refresh"]


def test_listado_de_recursos_incluye_nombre(client, db, tag):
    cuenta = crear_admin(db, f"n{tag}")
    otorgar_permiso_global(db, cuenta, "recursos.administrar")
    _, jar, _ = iniciar_sesion(client, cuenta.correo, "una frase larga de paso admin")
    h = headers_autenticados(jar)
    unidad = UnidadOrganizacional(nombre=f"Unidad nombres {tag}", tipo="LABORATORIO", estado=True)
    db.add(unidad)
    db.commit()
    rid = None
    try:
        r = client.post(
            "/api/recursos",
            json={"id_unidad": unidad.id_unidad, "tipo": "MOBILIARIO", "especializacion": {"nombre": f"Mesa {tag}"}},
            headers=h,
        )
        assert r.status_code == 201, r.text
        rid = r.json()["id"]
        r = client.get(f"/api/recursos?id_unidad={unidad.id_unidad}", headers=h)
        assert r.status_code == 200
        assert [(x["id"], x["nombre"]) for x in r.json()["datos"]] == [(rid, f"Mesa {tag}")]
    finally:
        if rid is not None:
            db.execute(text("DELETE FROM recursos.mobiliarios WHERE id = :i"), {"i": rid})
            db.execute(text("DELETE FROM recursos.recursos WHERE id = :i"), {"i": rid})
            db.commit()


def test_usuarios_y_personal_traen_id_cuenta(client, db, tag):
    admin = crear_admin(db, f"p{tag}")
    otorgar_permiso_global(db, admin, "usuarios.administrar")
    usuario, cuenta_usuario = crear_usuario_cuenta(db, f"u{tag}")
    _, jar, _ = iniciar_sesion(client, admin.correo, "una frase larga de paso admin")
    h = headers_autenticados(jar)

    r = client.get(f"/api/usuarios?busqueda={cuenta_usuario.correo}", headers=h)
    assert r.status_code == 200, r.text
    assert [x["id_cuenta"] for x in r.json()["datos"]] == [cuenta_usuario.id_cuenta]

    r = client.get(f"/api/personal?busqueda={admin.correo}", headers=h)
    assert r.status_code == 200, r.text
    assert [x["id_cuenta"] for x in r.json()["datos"]] == [admin.id_cuenta]


def test_configuracion_devuelve_notificar_por_correo(client, db, tag):
    """FE-29: la pantalla del laboratorio necesita ver el valor que puede modificar (RN-LAB-07)."""
    from .test_resources_api09 import _limpiar_unidad, _login_admin, _otra_unidad

    h, _ = _login_admin(client, db, f"l{tag}", ("laboratorios.configurar",))
    id_unidad = _otra_unidad(db, tag)
    try:
        r = client.patch(
            f"/api/laboratorios/{id_unidad}/configuracion",
            json={"hora_apertura": "07:00", "hora_cierre": "19:00", "notificar_por_correo": True},
            headers=h,
        )
        assert r.status_code == 200, r.text
        assert r.json()["notificar_por_correo"] is True
        r = client.get(f"/api/laboratorios/{id_unidad}/configuracion", headers=h)
        assert r.json()["notificar_por_correo"] is True
    finally:
        _limpiar_unidad(db, id_unidad)


def test_catalogo_de_laboratorios_lo_lee_cualquier_cuenta(client, db, tag):
    """FE-23: una cuenta sin permisos administrativos elige el laboratorio por nombre (contrato resources §3.0)."""
    from .test_resources_api09 import _limpiar_unidad, _login_admin, _otra_unidad

    h_admin, _ = _login_admin(client, db, f"m{tag}", ("laboratorios.configurar",))
    id_unidad = _otra_unidad(db, tag)
    _, cuenta = crear_usuario_cuenta(db, f"k{tag}")
    _, jar, _ = iniciar_sesion(client, cuenta.correo, "una frase larga de paso")
    h_usuario = headers_autenticados(jar)
    try:
        assert client.patch(
            f"/api/laboratorios/{id_unidad}/configuracion",
            json={"hora_apertura": "07:00", "hora_cierre": "19:00"}, headers=h_admin,
        ).status_code == 200
        # Un usuario no puede listar unidades (administración)...
        assert client.get("/api/unidades", headers=h_usuario).status_code == 403
        # ...pero sí el catálogo de laboratorios.
        r = client.get("/api/laboratorios", headers=h_usuario)
        assert r.status_code == 200, r.text
        fila = next(x for x in r.json()["datos"] if x["id_unidad"] == id_unidad)
        assert fila["nombre"] == f"Unidad api09 B {tag}" and fila["habilitado_reservas"] is True
    finally:
        _limpiar_unidad(db, id_unidad)
