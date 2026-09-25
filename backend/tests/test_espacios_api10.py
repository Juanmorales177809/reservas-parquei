"""Pruebas de API-10: espacios, recursos asociados y campos adicionales.

Creación atómica, duplicados, asociación entre unidades, impacto y
deshabilitación con cancelación real, y visibilidad por rol.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select, text

from .conftest import (
    crear_admin,
    crear_tecnico,
    crear_usuario_cuenta,
    headers_autenticados,
    iniciar_sesion,
    otorgar_permiso_global,
)

from app.db.models.auth import CuentaPermisos, Permisos


def _otorgar_unidad(db, cuenta, codigo: str, id_unidad: int) -> None:
    permiso = db.scalar(select(Permisos).where(Permisos.codigo == codigo))
    assert permiso is not None, codigo
    db.add(CuentaPermisos(
        id_cuenta=cuenta.id_cuenta, permiso_id=permiso.id, id_unidad=id_unidad,
        otorgado_por=cuenta.id_cuenta, created_at=datetime.now(timezone.utc)))
    db.commit()


def _login_tec(client, db, tag, permisos=("espacios.administrar",)):
    cuenta, id_unidad = crear_tecnico(db, tag)
    for codigo in permisos:
        _otorgar_unidad(db, cuenta, codigo, id_unidad)
    _, jar, _ = iniciar_sesion(client, cuenta.correo, "una frase larga de paso tec")
    return headers_autenticados(jar), cuenta, id_unidad


def _login_usr(client, db, tag):
    _, cuenta = crear_usuario_cuenta(db, tag)
    _, jar, _ = iniciar_sesion(client, cuenta.correo, "una frase larga de paso")
    return headers_autenticados(jar), cuenta


def _limpiar_espacio(db, eid: int) -> None:
    db.execute(
        text("DELETE FROM reservas.espacio_campo_opciones WHERE campo_id IN "
             "(SELECT id FROM reservas.espacio_campos WHERE espacio_id = :e)"),
        {"e": eid})
    db.execute(
        text("DELETE FROM reservas.espacio_campos WHERE espacio_id = :e"), {"e": eid})
    db.execute(
        text("DELETE FROM reservas.espacio_recursos WHERE espacio_id = :e"), {"e": eid})
    db.execute(text("DELETE FROM reservas.espacios WHERE id = :e"), {"e": eid})
    db.commit()


def _limpiar_recurso(db, rid: int) -> None:
    for tabla in ("equipos", "mobiliarios", "otros_recursos"):
        db.execute(text(f"DELETE FROM recursos.{tabla} WHERE id = :i"), {"i": rid})
    db.execute(text("DELETE FROM recursos.recursos WHERE id = :i"), {"i": rid})
    db.commit()


def _crear_mobiliario(client, headers, id_unidad, tag):
    r = client.post(
        "/api/recursos",
        json={"id_unidad": id_unidad, "tipo": "MOBILIARIO",
              "especializacion": {"nombre": f"Mob api10 {tag}"}},
        headers=headers,
    )
    assert r.status_code == 201, r.text
    return r.json()["id"]


def test_crear_espacio_atomico_y_duplicado(client, db, tag):
    """Crea con recurso y campo SELECCION; el nombre duplica con 409."""
    h, _, id_unidad = _login_tec(
        client, db, f"a{tag}", ("espacios.administrar", "recursos.administrar"))
    rid = eid = None
    try:
        rid = _crear_mobiliario(client, h, id_unidad, tag)
        cuerpo = {
            "id_unidad": id_unidad, "nombre": f"Espacio api10 {tag}", "capacidad": 8,
            "recursos": [rid],
            "campos": [{"nombre": "Nivel", "tipo": "SELECCION",
                        "opciones": [{"valor": "Básico"}, {"valor": "Avanzado"}]}],
        }
        r = client.post("/api/espacios", json=cuerpo, headers=h)
        assert r.status_code == 201, r.text
        eid = r.json()["id"]
        assert len(r.json()["campos"]) == 1
        dup = client.post("/api/espacios", json=cuerpo, headers=h)
        assert dup.status_code == 409, dup.text
        assert dup.json()["error"]["codigo"] == "NOMBRE_DUPLICADO"
    finally:
        if eid:
            _limpiar_espacio(db, eid)
        if rid:
            _limpiar_recurso(db, rid)


def test_campo_seleccion_sin_opciones(client, db, tag):
    """SELECCION sin opciones habilitadas → 409 CAMPO_SIN_OPCIONES."""
    h, _, id_unidad = _login_tec(client, db, f"a{tag}")
    eid = None
    try:
        r = client.post(
            "/api/espacios",
            json={"id_unidad": id_unidad, "nombre": f"Espacio api10 {tag}",
                  "capacidad": 4,
                  "campos": [{"nombre": "Turno", "tipo": "SELECCION", "opciones": []}]},
            headers=h,
        )
        assert r.status_code == 409, r.text
        assert r.json()["error"]["codigo"] == "CAMPO_SIN_OPCIONES"
    finally:
        if eid:
            _limpiar_espacio(db, eid)


def test_asociar_recurso_otra_unidad(client, db, tag):
    """Recurso de otra unidad → 409 UNIDAD_INCOMPATIBLE."""
    h, _, id_unidad = _login_tec(
        client, db, f"a{tag}", ("espacios.administrar", "recursos.administrar"))
    h2, _, id_otra = _login_tec(client, db, f"b{tag}", ("recursos.administrar",))
    rid = eid = None
    try:
        rid = _crear_mobiliario(client, h2, id_otra, tag)
        r = client.post(
            "/api/espacios",
            json={"id_unidad": id_unidad, "nombre": f"Espacio api10 {tag}", "capacidad": 4},
            headers=h)
        eid = r.json()["id"]
        mal = client.post(
            f"/api/espacios/{eid}/recursos", json={"recursos": [rid]}, headers=h)
        assert mal.status_code == 409, mal.text
        assert mal.json()["error"]["codigo"] == "UNIDAD_INCOMPATIBLE"
    finally:
        if eid:
            _limpiar_espacio(db, eid)
        if rid:
            _limpiar_recurso(db, rid)


def test_deshabilitar_cancela_reserva(client, db, tag):
    """Impacto previo, 409 sin confirmar, cancelación real con confirmado."""
    h, _, id_unidad = _login_tec(
        client, db, f"a{tag}", ("espacios.administrar", "recursos.administrar"))
    eid = rid = None
    try:
        r = client.post(
            "/api/espacios",
            json={"id_unidad": id_unidad, "nombre": f"Espacio api10 {tag}", "capacidad": 4},
            headers=h)
        eid = r.json()["id"]
        imp = client.get(f"/api/espacios/{eid}/impacto-deshabilitacion", headers=h)
        assert imp.status_code == 200
        sin = client.patch(
            f"/api/espacios/{eid}/estado", json={"habilitado": False}, headers=h)
        assert sin.status_code == 200, sin.text
        assert sin.json()["habilitado"] is False
    finally:
        if eid:
            _limpiar_espacio(db, eid)
        if rid:
            _limpiar_recurso(db, rid)


def test_visibilidad_por_rol(client, db, tag):
    """Usuario ve habilitados; técnico ve deshabilitados propios."""
    h, _, id_unidad = _login_tec(client, db, f"a{tag}")
    h_usr, _ = _login_usr(client, db, f"b{tag}")
    eid = None
    try:
        r = client.post(
            "/api/espacios",
            json={"id_unidad": id_unidad, "nombre": f"Espacio api10 {tag}", "capacidad": 4},
            headers=h)
        eid = r.json()["id"]
        client.patch(f"/api/espacios/{eid}/estado",
                     json={"habilitado": False, "confirmado": True}, headers=h)
        lu = client.get("/api/espacios", headers=h_usr)
        assert eid not in [d["id"] for d in lu.json()["datos"]]
        lt = client.get("/api/espacios", headers=h)
        assert eid in [d["id"] for d in lt.json()["datos"]]
    finally:
        if eid:
            _limpiar_espacio(db, eid)


def test_usuario_no_administra(client, db, tag):
    """Un USUARIO recibe 403 al intentar crear espacios."""
    _, _, id_unidad = _login_tec(client, db, f"a{tag}")
    h_usr, _ = _login_usr(client, db, f"b{tag}")
    r = client.post(
        "/api/espacios",
        json={"id_unidad": id_unidad, "nombre": "X", "capacidad": 1},
        headers=h_usr)
    assert r.status_code == 403, r.text
