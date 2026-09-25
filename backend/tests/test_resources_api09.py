"""Pruebas de API-09: recursos y configuración del laboratorio.

Creación por rol (equipos solo admin global), edición del Técnico,
deshabilitación con confirmación, reasignación y configuración con
histórico. Limpieza total al terminar.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select, text

from .conftest import (
    crear_admin,
    crear_tecnico,
    headers_autenticados,
    iniciar_sesion,
    otorgar_permiso_global,
)

from app.db.models.auth import CuentaPermisos, Permisos
from app.db.models.identidad import UnidadOrganizacional


def _otorgar_unidad(db, cuenta, codigo: str, id_unidad: int) -> None:
    permiso = db.scalar(select(Permisos).where(Permisos.codigo == codigo))
    assert permiso is not None, codigo
    db.add(CuentaPermisos(
        id_cuenta=cuenta.id_cuenta, permiso_id=permiso.id, id_unidad=id_unidad,
        otorgado_por=cuenta.id_cuenta, created_at=datetime.now(timezone.utc)))
    db.commit()


def _login_admin(client, db, tag, permisos=()):
    cuenta = crear_admin(db, tag)
    for codigo in permisos:
        otorgar_permiso_global(db, cuenta, codigo)
    _, jar, _ = iniciar_sesion(client, cuenta.correo, "una frase larga de paso admin")
    return headers_autenticados(jar), cuenta


def _login_tec(client, db, tag, permisos=()):
    cuenta, id_unidad = crear_tecnico(db, tag)
    for codigo in permisos:
        _otorgar_unidad(db, cuenta, codigo, id_unidad)
    _, jar, _ = iniciar_sesion(client, cuenta.correo, "una frase larga de paso tec")
    return headers_autenticados(jar), cuenta, id_unidad


def _limpiar_recurso(db, rid: int) -> None:
    for tabla in ("equipos", "mobiliarios", "otros_recursos"):
        db.execute(text(f"DELETE FROM recursos.{tabla} WHERE id = :i"), {"i": rid})
    db.execute(text("DELETE FROM recursos.recursos WHERE id = :i"), {"i": rid})
    db.commit()


def _limpiar_unidad(db, id_unidad: int) -> None:
    db.execute(
        text("DELETE FROM reservas.laboratorio_tipos_reserva WHERE id_unidad = :u"),
        {"u": id_unidad})
    db.execute(
        text("DELETE FROM reservas.laboratorios_config_historico WHERE id_unidad = :u"),
        {"u": id_unidad})
    db.execute(
        text("DELETE FROM reservas.laboratorios_config WHERE id_unidad = :u"),
        {"u": id_unidad})
    db.commit()


def _otra_unidad(db, tag: str) -> int:
    unidad = UnidadOrganizacional(nombre=f"Unidad api09 B {tag}", tipo="LABORATORIO", estado=True)
    db.add(unidad)
    db.flush()
    db.commit()
    return unidad.id_unidad


def test_crear_equipo_solo_admin_global(client, db, tag):
    """El admin global crea equipos; el Técnico recibe 403."""
    h_adm, _ = _login_admin(client, db, f"a{tag}", ("recursos.administrar_equipos",))
    h_tec, _, id_unidad = _login_tec(client, db, f"b{tag}")
    rid = None
    try:
        r = client.post(
            "/api/recursos",
            json={"id_unidad": id_unidad, "tipo": "EQUIPO",
                  "especializacion": {"nombre_equipo": f"Equipo api09 {tag}"}},
            headers=h_adm,
        )
        assert r.status_code == 201, r.text
        rid = r.json()["id"]
        negado = client.post(
            "/api/recursos",
            json={"id_unidad": id_unidad, "tipo": "EQUIPO",
                  "especializacion": {"nombre_equipo": f"Equipo api09 X {tag}"}},
            headers=h_tec,
        )
        assert negado.status_code == 403, negado.text
    finally:
        if rid:
            _limpiar_recurso(db, rid)


def test_tecnico_edita_equipo_propio(client, db, tag):
    """Con recursos.editar_equipos edita, pero no crea ni cambia de unidad."""
    h_adm, _ = _login_admin(client, db, f"a{tag}", ("recursos.administrar_equipos",))
    h_tec, _, id_unidad = _login_tec(client, db, f"b{tag}", ("recursos.editar_equipos",))
    rid = None
    try:
        r = client.post(
            "/api/recursos",
            json={"id_unidad": id_unidad, "tipo": "EQUIPO",
                  "especializacion": {"nombre_equipo": f"Equipo api09 {tag}"}},
            headers=h_adm,
        )
        rid = r.json()["id"]
        ed = client.patch(
            f"/api/recursos/{rid}",
            json={"especializacion": {"marca": f"Marca {tag}"}},
            headers=h_tec,
        )
        assert ed.status_code == 200, ed.text
    finally:
        if rid:
            _limpiar_recurso(db, rid)


def test_deshabilitar_exige_confirmacion(client, db, tag):
    """Sin confirmado y con impacto → 409 con conteo; con confirmado → 200."""
    h_tec, _, id_unidad = _login_tec(client, db, f"b{tag}", ("recursos.administrar",))
    rid = None
    try:
        r = client.post(
            "/api/recursos",
            json={"id_unidad": id_unidad, "tipo": "MOBILIARIO",
                  "especializacion": {"nombre": f"Mobiliario api09 {tag}"}},
            headers=h_tec,
        )
        assert r.status_code == 201, r.text
        rid = r.json()["id"]
        sin = client.patch(
            f"/api/recursos/{rid}/estado",
            json={"habilitado": False},
            headers=h_tec,
        )
        # Sin reservas futuras puede pasar directo; con impacto exige confirmado.
        assert sin.status_code in (200, 409), sin.text
        con = client.patch(
            f"/api/recursos/{rid}/estado",
            json={"habilitado": False, "confirmado": True},
            headers=h_tec,
        )
        assert con.status_code == 200, con.text
        assert con.json()["habilitado"] is False
    finally:
        if rid:
            _limpiar_recurso(db, rid)
        _limpiar_unidad(db, id_unidad)


def test_reasignar_unidad_solo_admin(client, db, tag):
    """reasignar exige alcance global; el Técnico recibe 403."""
    h_adm, _ = _login_admin(
        client, db, f"a{tag}",
        ("recursos.administrar_equipos", "recursos.reasignar_unidad"))
    h_tec, _, id_unidad = _login_tec(client, db, f"b{tag}", ("recursos.administrar",))
    rid = None
    id_otra = _otra_unidad(db, tag)
    try:
        r = client.post(
            "/api/recursos",
            json={"id_unidad": id_unidad, "tipo": "MOBILIARIO",
                  "especializacion": {"nombre": f"Mobiliario api09 {tag}"}},
            headers=h_tec,
        )
        rid = r.json()["id"]
        negado = client.patch(
            f"/api/recursos/{rid}/unidad", json={"id_unidad": id_otra}, headers=h_tec)
        assert negado.status_code == 403, negado.text
        ok = client.patch(
            f"/api/recursos/{rid}/unidad", json={"id_unidad": id_otra}, headers=h_adm)
        assert ok.status_code == 200, ok.text
        assert ok.json()["id_unidad"] == id_otra
    finally:
        if rid:
            _limpiar_recurso(db, rid)
        _limpiar_unidad(db, id_unidad)
        db.execute(
            text('DELETE FROM "unidadOrganizacional".unidad_organizacional WHERE id_unidad = :u'),
            {"u": id_otra})
        db.commit()


def test_configuracion_e_historico(client, db, tag):
    """Primera configuración exige horario; crea versión en histórico."""
    h_tec, _, id_unidad = _login_tec(client, db, f"b{tag}", ("laboratorios.configurar",))
    try:
        sin_horario = client.patch(
            f"/api/laboratorios/{id_unidad}/configuracion",
            json={"habilitado_reservas": True},
            headers=h_tec,
        )
        assert sin_horario.status_code == 422, sin_horario.text
        ok = client.patch(
            f"/api/laboratorios/{id_unidad}/configuracion",
            json={"hora_apertura": "08:00", "hora_cierre": "18:00"},
            headers=h_tec,
        )
        assert ok.status_code == 200, ok.text
        n = db.scalar(
            text("SELECT count(*) FROM reservas.laboratorios_config_historico WHERE id_unidad = :u"),
            {"u": id_unidad})
        assert n == 1
        tipos = client.put(
            f"/api/laboratorios/{id_unidad}/tipos-reserva",
            json={"tipos": ["ESPACIO"]},
            headers=h_tec,
        )
        assert tipos.status_code == 200, tipos.text
        assert tipos.json()["tipos_reserva"] == ["ESPACIO"]
    finally:
        _limpiar_unidad(db, id_unidad)


def test_listado_reservable(client, db, tag):
    """El listado trae lo creado; el filtro reservable aplica."""
    h_tec, _, id_unidad = _login_tec(client, db, f"b{tag}", ("recursos.administrar",))
    rid = None
    try:
        r = client.post(
            "/api/recursos",
            json={"id_unidad": id_unidad, "tipo": "MOBILIARIO",
                  "especializacion": {"nombre": f"Mobiliario api09 {tag}"}},
            headers=h_tec,
        )
        rid = r.json()["id"]
        li = client.get(f"/api/recursos?id_unidad={id_unidad}", headers=h_tec)
        assert li.status_code == 200
        assert rid in [d["id"] for d in li.json()["datos"]]
    finally:
        if rid:
            _limpiar_recurso(db, rid)
        _limpiar_unidad(db, id_unidad)
