"""Pruebas de reservations §2.9 y §2.10: opciones de contexto y de acompañantes.

`RN-CTX-05` (el Usuario solo elige sus vinculaciones activas), `RN-CTX-08` (el Personal elige
del catálogo general), `RN-ACT-02` (solo actividades activas) y `RN-ACO-02`/`RN-ACO-04`
(acompañantes con vinculación activa). Limpieza total al terminar.
"""

from __future__ import annotations

from sqlalchemy import text

from .conftest import (
    crear_tecnico,
    crear_usuario_cuenta,
    headers_autenticados,
    iniciar_sesion,
)

from app.db.models.investigacion import (
    ActividadesInstitucionales,
    Proyectos,
    UsuarioProyectos,
)


def _login_usuario(client, cuenta):
    _, jar, _ = iniciar_sesion(client, cuenta.correo, "una frase larga de paso")
    return headers_autenticados(jar)


def _limpiar(db, proyectos: list[int], actividades: list[int]) -> None:
    for pid in proyectos:
        db.execute(text("DELETE FROM investigacion.usuario_proyectos WHERE id_proyecto = :p"), {"p": pid})
        db.execute(text("DELETE FROM investigacion.proyectos WHERE id_proyecto = :p"), {"p": pid})
    for aid in actividades:
        db.execute(text("DELETE FROM investigacion.actividades_institucionales WHERE id_actividad = :a"), {"a": aid})
    db.commit()


def test_usuario_solo_ve_sus_vinculaciones_y_personal_el_catalogo(client, db, tag):
    usuario, cuenta = crear_usuario_cuenta(db, f"c{tag}")
    propio = Proyectos(codigo=f"PRY-P{tag}", nombre=f"Propio {tag}", estado=True)
    ajeno = Proyectos(codigo=f"PRY-A{tag}", nombre=f"Ajeno {tag}", estado=True)
    inactivo = Proyectos(codigo=f"PRY-I{tag}", nombre=f"Inactivo {tag}", estado=False)
    actividad = ActividadesInstitucionales(nombre=f"Actividad {tag}", dependencia="Extensión", estado=True)
    db.add_all([propio, ajeno, inactivo, actividad])
    db.flush()
    db.add(UsuarioProyectos(id_usuario=usuario.id_usuario, id_proyecto=propio.id_proyecto, estado=True))
    db.commit()
    ids = [propio.id_proyecto, ajeno.id_proyecto, inactivo.id_proyecto]
    try:
        r = client.get("/api/reservas/contexto/opciones", headers=_login_usuario(client, cuenta))
        assert r.status_code == 200, r.text
        cuerpo = r.json()
        assert [p["id"] for p in cuerpo["proyectos"]] == [propio.id_proyecto]
        assert actividad.id_actividad in [a["id"] for a in cuerpo["actividades"]]
        assert cuerpo["pasantias"] == [] and cuerpo["trabajos_grado"] == []

        # RN-CTX-08: una cuenta PERSONAL ve el catálogo general activo, sin actividades.
        tecnico, _ = crear_tecnico(db, f"t{tag}")
        _, jar, _ = iniciar_sesion(client, tecnico.correo, "una frase larga de paso tec")
        r = client.get("/api/reservas/contexto/opciones", headers=headers_autenticados(jar))
        assert r.status_code == 200, r.text
        cuerpo = r.json()
        ofrecidos = {p["id"] for p in cuerpo["proyectos"]}
        assert {propio.id_proyecto, ajeno.id_proyecto} <= ofrecidos
        assert inactivo.id_proyecto not in ofrecidos
        assert cuerpo["actividades"] == [] and cuerpo["pasantias"] == []
    finally:
        _limpiar(db, ids, [actividad.id_actividad])


def test_acompanantes_son_los_vinculados_menos_quien_consulta(client, db, tag):
    u1, c1 = crear_usuario_cuenta(db, f"d{tag}")
    u2, c2 = crear_usuario_cuenta(db, f"e{tag}")
    u3, c3 = crear_usuario_cuenta(db, f"f{tag}")  # sin vinculación
    proyecto = Proyectos(codigo=f"PRY-C{tag}", nombre=f"Compartido {tag}", estado=True)
    db.add(proyecto)
    db.flush()
    db.add_all([
        UsuarioProyectos(id_usuario=u1.id_usuario, id_proyecto=proyecto.id_proyecto, estado=True),
        UsuarioProyectos(id_usuario=u2.id_usuario, id_proyecto=proyecto.id_proyecto, estado=True),
    ])
    db.commit()
    try:
        h = _login_usuario(client, c1)
        r = client.get(f"/api/reservas/acompanantes/opciones?proyecto_id={proyecto.id_proyecto}", headers=h)
        assert r.status_code == 200, r.text
        assert [a["id_cuenta"] for a in r.json()["datos"]] == [c2.id_cuenta]

        r = client.get("/api/reservas/acompanantes/opciones", headers=h)
        assert r.status_code == 422, r.text
        r = client.get("/api/reservas/acompanantes/opciones?proyecto_id=999999999", headers=h)
        assert r.status_code == 404, r.text
    finally:
        _limpiar(db, [proyecto.id_proyecto], [])


def test_listado_y_detalle_traen_nombres_ademas_de_ids(client, db, tag):
    """FE-28: las pantallas muestran nombres; el contrato los entrega junto a los identificadores."""
    from datetime import date, timedelta

    from .test_reservations_api13 import _setup, _teardown

    tecnico, id_unidad = crear_tecnico(db, f"n{tag}")
    s = _setup(db, tag, id_unidad)
    rids: list[int] = []
    try:
        _, jar, _ = iniciar_sesion(client, tecnico.correo, "una frase larga de paso tec")
        h = headers_autenticados(jar)
        fecha = (date.today() + timedelta(days=3)).isoformat()
        r = client.post("/api/reservas", headers=h, json={
            "id_unidad": id_unidad, "tipo_reserva": "ESPACIO", "contexto": {"proyecto_id": s["proyecto_id"]},
            "detalle": {"espacio_id": s["espacio_id"], "fecha": fecha, "hora_inicio": "09:00", "hora_fin": "10:00"},
        })
        assert r.status_code == 201, r.text
        rids.append(r.json()["id"])

        fila = next(x for x in client.get(f"/api/reservas?id_unidad={id_unidad}", headers=h).json()["datos"] if x["id"] == rids[0])
        assert fila["objeto"] == f"Espacio api13 {tag}"
        assert fila["periodo"]["fecha"] == fecha
        assert fila["solicitante_nombre"] == f"Tecnico n{tag}"
        assert fila["unidad_nombre"] == f"Unidad n{tag}"

        d = client.get(f"/api/reservas/{rids[0]}", headers=h).json()
        assert d["detalle"]["espacio_nombre"] == f"Espacio api13 {tag}"
        assert d["unidad_nombre"] == f"Unidad n{tag}"
        assert d["solicitante_nombre"] == f"Tecnico n{tag}"
        assert d["historial"][0]["actor_nombre"]
    finally:
        _teardown(db, s, rids)


def test_desde_y_hasta_filtran_por_fecha_de_uso(client, db, tag):
    """FE-31: `desde` y `hasta` acotan por el periodo de la reserva (RN-DIS-02), no por su creación."""
    from .test_reservations_api13 import _base, _fecha, _login_tec, _teardown

    h, _, s = _login_tec(client, db, f"f{tag}")
    rids: list[int] = []
    try:
        cuerpos = [
            ("ESPACIO", {"espacio_id": s["espacio_id"], "fecha": _fecha(1), "hora_inicio": "10:00", "hora_fin": "12:00"}, None),
            ("RECURSO_INTERNO", {"fecha": _fecha(2), "hora_inicio": "10:00", "hora_fin": "12:00"},
             [{"recurso_id": s["recurso_id"], "rol": "PRINCIPAL"}]),
            ("RECURSO_CAMPUS", {"fecha_salida": _fecha(3), "fecha_devolucion_estimada": _fecha(4), "razon_solicitud": "P",
                                "lugar_nombre": "Sede", "lugar_direccion": "Calle 1"},
             [{"recurso_id": s["recurso_id"], "rol": "PRINCIPAL"}]),
            ("RECURSO_EXTERNO", {"fecha_salida": _fecha(5), "fecha_devolucion_estimada": _fecha(6), "razon_solicitud": "E",
                                 "lugar_nombre": "Sede", "lugar_direccion": "Calle 1"},
             [{"recurso_id": s["recurso2_id"], "rol": "PRINCIPAL"}]),
            ("LISTA_ESPERA", {"descripcion_necesidad": "Pieza"}, None),
        ]
        por_tipo: dict[str, int] = {}
        for i, (tipo, detalle, recursos) in enumerate(cuerpos):
            cuerpo = _base(s, tipo, f"fechas-{i}-{tag}")
            cuerpo["detalle"] = detalle
            if recursos:
                cuerpo["recursos"] = recursos
            r = client.post("/api/reservas", json=cuerpo, headers=h)
            assert r.status_code == 201, (tipo, r.text)
            rids.append(r.json()["id"])
            por_tipo[tipo] = r.json()["id"]

        def ids(filtro: str) -> set[int]:
            r = client.get(f"/api/reservas?id_unidad={s['id_unidad']}&tamano=100{filtro}", headers=h)
            assert r.status_code == 200, r.text
            return {x["id"] for x in r.json()["datos"]}

        assert ids("") == set(rids)  # sin fechas, todas (incluida la lista de espera)
        assert ids(f"&desde={_fecha(3)}&hasta={_fecha(3)}") == {por_tipo["RECURSO_CAMPUS"]}
        assert ids(f"&desde={_fecha(4)}&hasta={_fecha(5)}") == {por_tipo["RECURSO_CAMPUS"], por_tipo["RECURSO_EXTERNO"]}
        assert ids(f"&desde={_fecha(5)}") == {por_tipo["RECURSO_EXTERNO"]}
        assert ids(f"&hasta={_fecha(1)}") == {por_tipo["ESPACIO"]}
        assert por_tipo["LISTA_ESPERA"] not in ids(f"&desde={_fecha(0)}")  # sin fecha: fuera al filtrar

        for malo in (f"&desde={_fecha(5)}&hasta={_fecha(1)}", "&desde=ayer"):
            r = client.get(f"/api/reservas?id_unidad={s['id_unidad']}{malo}", headers=h)
            assert r.status_code == 422, (malo, r.text)
    finally:
        _teardown(db, s, rids)


def test_editar_lista_de_espera_solicitada(client, db, tag):
    """FE-31: editar una lista de espera cambia su descripción; la viabilidad se invalida solo si la descripción cambia (RN-TIP-PLE-09)."""
    from .test_reservations_api13 import _base, _login_tec, _teardown

    h, _, s = _login_tec(client, db, f"g{tag}")
    rids: list[int] = []
    try:
        cuerpo = _base(s, "LISTA_ESPERA", f"edit-lista-{tag}")
        cuerpo["detalle"] = {"descripcion_necesidad": "Pieza inicial"}
        r = client.post("/api/reservas", json=cuerpo, headers=h)
        assert r.status_code == 201, r.text
        rid = r.json()["id"]
        rids.append(rid)

        r = client.patch(f"/api/reservas/{rid}", json={"detalle": {"descripcion_necesidad": "Pieza mejorada"}, "observacion": "Urgente"}, headers=h)
        assert r.status_code == 200, r.text
        assert r.json()["detalle"]["descripcion_necesidad"] == "Pieza mejorada"

        assert client.post(f"/api/reservas/{rid}/lista-espera/viabilidad", json={"viable": True}, headers=h).status_code == 200
        client.patch(f"/api/reservas/{rid}", json={"detalle": {"descripcion_necesidad": "Pieza mejorada"}}, headers=h)
        assert client.get(f"/api/reservas/{rid}", headers=h).json()["lista_espera"]["viable"] is True  # misma descripción: nada se invalida

        r = client.patch(f"/api/reservas/{rid}", json={"detalle": {"descripcion_necesidad": "Otra pieza"}}, headers=h)
        assert r.status_code == 200, r.text
        assert client.get(f"/api/reservas/{rid}", headers=h).json()["lista_espera"]["viable"] is None

        # Bloques que la lista de espera no tiene se rechazan aunque vayan vacíos.
        for bloque in ({"recursos": []}, {"acompanantes": []}):
            r = client.patch(f"/api/reservas/{rid}", json=bloque, headers=h)
            assert r.status_code == 422, (bloque, r.text)
    finally:
        _teardown(db, s, rids)


def test_editar_espacio_con_bloques_completos(client, db, tag):
    """FE-31: contexto, recursos, periodo y observación viajan como bloques y el resultado los refleja (contrato §2.8)."""
    from .test_reservations_api13 import _base, _fecha, _login_tec, _login_usr, _teardown

    _, _, s = _login_tec(client, db, f"h{tag}")
    h, _, id_usuario = _login_usr(client, db, f"i{tag}", s["proyecto_id"])
    rids: list[int] = []
    try:
        cuerpo = _base(s, "ESPACIO", f"edit-espacio-{tag}")
        cuerpo["detalle"] = {"espacio_id": s["espacio_id"], "fecha": _fecha(20), "hora_inicio": "10:00", "hora_fin": "12:00"}
        r = client.post("/api/reservas", json=cuerpo, headers=h)
        assert r.status_code == 201 and r.json()["estado"] == "SOLICITADA", r.text
        rid = r.json()["id"]
        rids.append(rid)

        r = client.patch(f"/api/reservas/{rid}", headers=h, json={
            "detalle": {"hora_fin": "13:00"},
            "recursos": [{"recurso_id": s["recurso2_id"], "rol": "ADICIONAL"}],
            "observacion": "Con un equipo",
            "contexto": {"proyecto_id": s["proyecto_id"]},
        })
        assert r.status_code == 200, r.text
        d = r.json()
        assert d["estado"] == "SOLICITADA" and d["observacion"] == "Con un equipo"
        assert d["detalle"]["hora_fin"].startswith("13:00")
        assert [(x["recurso_id"], x["rol"]) for x in d["recursos"] if x["estado_asignacion"] == "ASIGNADO"] == [(s["recurso2_id"], "ADICIONAL")]

        # Bloque vacío: quita los complementarios (el tipo lo permite) y conserva el resto.
        r = client.patch(f"/api/reservas/{rid}", json={"recursos": []}, headers=h)
        assert r.status_code == 200, r.text
        assert [x for x in r.json()["recursos"] if x["estado_asignacion"] == "ASIGNADO"] == []
        assert r.json()["detalle"]["hora_fin"].startswith("13:00")
    finally:
        _teardown(db, s, rids, id_usuario)
