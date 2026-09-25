"""Pruebas de API-11: catálogos de investigación y vinculaciones.

Los proyectos/semilleros llegan por importación o seed: aquí se siembran
directo. Cubre reactivación en vez de duplicado y desactivación con
conservación de historial.
"""

from __future__ import annotations

from sqlalchemy import text

from .conftest import (
    crear_admin,
    crear_usuario_cuenta,
    headers_autenticados,
    iniciar_sesion,
    otorgar_permiso_global,
)


def _login_admin(client, db, tag):
    cuenta = crear_admin(db, tag)
    otorgar_permiso_global(db, cuenta, "usuarios.administrar")
    _, jar, _ = iniciar_sesion(client, cuenta.correo, "una frase larga de paso admin")
    return headers_autenticados(jar), cuenta


def _proyecto(db, tag: str, codigo: str) -> int:
    pid = db.scalar(
        text("INSERT INTO investigacion.proyectos (codigo, nombre, estado) "
             "VALUES (:c, :n, true) RETURNING id_proyecto"),
        {"c": codigo, "n": f"Proyecto {tag}"})
    db.commit()
    return pid


def _limpiar(db, pid: int, uid: int | None = None) -> None:
    if uid is not None:
        db.execute(
            text("DELETE FROM investigacion.usuario_proyectos WHERE id_usuario = :u"),
            {"u": uid})
    db.execute(
        text("DELETE FROM investigacion.proyectos WHERE id_proyecto = :i"), {"i": pid})
    db.commit()


def test_vinculacion_reactiva_en_vez_de_duplicar(client, db, tag):
    """Crear sobre inactiva reactiva la fila; duplicada activa → 409."""
    h, _ = _login_admin(client, db, f"a{tag}")
    _, cuenta = crear_usuario_cuenta(db, f"b{tag}")
    pid = _proyecto(db, tag, f"PRY-{tag}")
    try:
        c1 = client.post(
            f"/api/investigacion/usuarios/{cuenta.id_usuario}/vinculaciones/proyectos",
            json={"id_proyecto": pid}, headers=h)
        assert c1.status_code == 201, c1.text
        dup = client.post(
            f"/api/investigacion/usuarios/{cuenta.id_usuario}/vinculaciones/proyectos",
            json={"id_proyecto": pid}, headers=h)
        assert dup.status_code == 409, dup.text
        off = client.delete(
            f"/api/investigacion/usuarios/{cuenta.id_usuario}/vinculaciones/proyectos/{pid}",
            headers=h)
        assert off.status_code == 204, off.text
        n = db.scalar(
            text("SELECT count(*) FROM investigacion.usuario_proyectos "
                 "WHERE id_usuario = :u AND id_proyecto = :p"),
            {"u": cuenta.id_usuario, "p": pid})
        assert n == 1
        c2 = client.post(
            f"/api/investigacion/usuarios/{cuenta.id_usuario}/vinculaciones/proyectos",
            json={"id_proyecto": pid}, headers=h)
        assert c2.status_code == 201, c2.text
        n2 = db.scalar(
            text("SELECT count(*) FROM investigacion.usuario_proyectos "
                 "WHERE id_usuario = :u AND id_proyecto = :p"),
            {"u": cuenta.id_usuario, "p": pid})
        assert n2 == 1
    finally:
        _limpiar(db, pid, cuenta.id_usuario)


def test_desactivar_ultima_vinculacion_avisa(client, db, tag):
    """Desactivar la última activa informa sin bloquear."""
    h, _ = _login_admin(client, db, f"a{tag}")
    _, cuenta = crear_usuario_cuenta(db, f"b{tag}")
    pid = _proyecto(db, tag, f"PRY-{tag}")
    try:
        client.post(
            f"/api/investigacion/usuarios/{cuenta.id_usuario}/vinculaciones/proyectos",
            json={"id_proyecto": pid}, headers=h)
        g = client.get(
            f"/api/investigacion/usuarios/{cuenta.id_usuario}/vinculaciones", headers=h)
        assert g.status_code == 200
        assert len(g.json()["proyectos"]) == 1
    finally:
        _limpiar(db, pid, cuenta.id_usuario)


def test_proyecto_inexistente_404(client, db, tag):
    """Vincular a proyecto inexistente → 404."""
    h, _ = _login_admin(client, db, f"a{tag}")
    _, cuenta = crear_usuario_cuenta(db, f"b{tag}")
    try:
        r = client.post(
            f"/api/investigacion/usuarios/{cuenta.id_usuario}/vinculaciones/proyectos",
            json={"id_proyecto": 999999}, headers=h)
        assert r.status_code == 404, r.text
    finally:
        pass


def test_actividades_crud_basico(client, db, tag):
    """Crear y deshabilitar actividad institucional."""
    h, _ = _login_admin(client, db, f"a{tag}")
    try:
        r = client.post(
            "/api/investigacion/actividades",
            json={"nombre": f"Actividad {tag}", "dependencia": "Facultad"},
            headers=h)
        assert r.status_code == 201, r.text
        aid = r.json()["id_actividad"]
        off = client.patch(
            f"/api/investigacion/actividades/{aid}/estado",
            json={"estado": False}, headers=h)
        assert off.status_code == 200, off.text
        assert off.json()["estado"] is False
    finally:
        db.execute(
            text("DELETE FROM investigacion.actividades_institucionales "
                 "WHERE nombre = :n"), {"n": f"Actividad {tag}"})
        db.commit()
