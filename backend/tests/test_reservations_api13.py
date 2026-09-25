"""Pruebas de API-13: creación de los cinco tipos, edición en SOLICITADA,
disponibilidad y preparación de lista de espera.
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone

from sqlalchemy import text

from .conftest import (
    crear_tecnico,
    crear_usuario_cuenta,
    headers_autenticados,
    iniciar_sesion,
)

from app.db.models.investigacion import Proyectos, UsuarioProyectos
from app.db.models.recursos import Equipos, Recursos
from app.db.models.reservas import (
    Espacios,
    LaboratoriosConfig,
    LaboratorioTiposReserva,
)


def _tipo_id(db, codigo: str) -> int:
    return db.scalar(
        text("SELECT id FROM reservas.tipos_reserva WHERE codigo = :c"), {"c": codigo})


def _setup(db, tag: str, id_unidad: int) -> dict:
    ahora = datetime.now(timezone.utc)
    db.add(LaboratoriosConfig(
        id_unidad=id_unidad, habilitado_reservas=True,
        dias_atencion=[0, 1, 2, 3, 4, 5, 6],
        hora_apertura=time(0, 0), hora_cierre=time(23, 59),
        horario_atencion={}, horas_antelacion=0, aprobacion_automatica=False,
        notificar_por_correo=False, mostrar_estado_reserva=False,
        mostrar_reservista=False, recordatorio_horas_antes=24))
    for codigo in ("ESPACIO", "RECURSO_INTERNO", "RECURSO_CAMPUS",
                   "RECURSO_EXTERNO", "LISTA_ESPERA"):
        db.add(LaboratorioTiposReserva(
            id_unidad=id_unidad, tipo_reserva_id=_tipo_id(db, codigo),
            habilitado=True, created_at=ahora, updated_at=ahora))
    espacio = Espacios(
        id_unidad=id_unidad, nombre=f"Espacio api13 {tag}", capacidad=10,
        habilitado=True, created_at=ahora, updated_at=ahora)
    db.add(espacio)
    db.flush()
    proyecto = Proyectos(codigo=f"PRY-{tag}", nombre=f"Proyecto {tag}", estado=True)
    db.add(proyecto)
    db.flush()
    recurso = Recursos(
        id_unidad=id_unidad, tipo="EQUIPO", habilitado=True,
        created_at=ahora, updated_at=ahora)
    db.add(recurso)
    db.flush()
    db.add(Equipos(id=recurso.id, nombre_equipo=f"Equipo api13 {tag}",
                   requiere_apoyo=False, acreditado=False))
    recurso2 = Recursos(
        id_unidad=id_unidad, tipo="EQUIPO", habilitado=True,
        created_at=ahora, updated_at=ahora)
    db.add(recurso2)
    db.flush()
    db.add(Equipos(id=recurso2.id, nombre_equipo=f"Equipo api13 B {tag}",
                   requiere_apoyo=False, acreditado=False))
    db.commit()
    return {"id_unidad": id_unidad, "espacio_id": espacio.id,
            "proyecto_id": proyecto.id_proyecto, "recurso_id": recurso.id,
            "recurso2_id": recurso2.id}


def _teardown(db, s: dict, rids: list[int], id_usuario: int | None = None) -> None:
    for rid in rids:
        db.execute(
            text("DELETE FROM reservas.orden_salida_items WHERE orden_salida_id IN "
                 "(SELECT id FROM reservas.ordenes_salida WHERE reserva_id = :i)"),
            {"i": rid})
        db.execute(
            text("DELETE FROM reservas.orden_salida_actividades WHERE orden_salida_id IN "
                 "(SELECT id FROM reservas.ordenes_salida WHERE reserva_id = :i)"),
            {"i": rid})
        db.execute(
            text("DELETE FROM reservas.ordenes_salida WHERE reserva_id = :i"), {"i": rid})
        db.execute(
            text("DELETE FROM notificaciones.envios_correo WHERE evento_id IN "
                 "(SELECT id FROM notificaciones.eventos WHERE reserva_id = :i)"),
            {"i": rid})
        db.execute(
            text("DELETE FROM notificaciones.notificaciones WHERE evento_id IN "
                 "(SELECT id FROM notificaciones.eventos WHERE reserva_id = :i)"),
            {"i": rid})
        db.execute(
            text("DELETE FROM notificaciones.eventos WHERE reserva_id = :i"), {"i": rid})
        for tabla in (
            "reserva_historial_estado", "reserva_propuestas", "reserva_recursos",
            "reserva_contexto", "reserva_espacio", "reserva_recurso_interno",
            "reserva_datos_salida", "reserva_recurso_campus", "reserva_recurso_externo",
            "reserva_lista_espera", "reserva_lista_espera_formulario", "reserva_adjuntos",
        ):
            db.execute(text(f"DELETE FROM reservas.{tabla} WHERE reserva_id = :i"),
                       {"i": rid})
        db.execute(text("DELETE FROM reservas.reservas WHERE id = :i"), {"i": rid})
    if id_usuario is not None:
        db.execute(
            text("DELETE FROM investigacion.usuario_proyectos WHERE id_usuario = :u"),
            {"u": id_usuario})
    db.execute(
        text("DELETE FROM investigacion.proyectos WHERE id_proyecto = :i"),
        {"i": s["proyecto_id"]})
    db.execute(text("DELETE FROM recursos.equipos WHERE id = :i"), {"i": s["recurso_id"]})
    db.execute(text("DELETE FROM recursos.equipos WHERE id = :i"), {"i": s["recurso2_id"]})
    db.execute(text("DELETE FROM recursos.recursos WHERE id = :i"), {"i": s["recurso_id"]})
    db.execute(text("DELETE FROM recursos.recursos WHERE id = :i"), {"i": s["recurso2_id"]})
    db.execute(text("DELETE FROM reservas.espacios WHERE id = :i"), {"i": s["espacio_id"]})
    db.execute(
        text("DELETE FROM reservas.laboratorio_tipos_reserva WHERE id_unidad = :u"),
        {"u": s["id_unidad"]})
    db.execute(
        text("DELETE FROM reservas.laboratorios_config WHERE id_unidad = :u"),
        {"u": s["id_unidad"]})
    db.commit()


def _login_tec(client, db, tag):
    cuenta, id_unidad = crear_tecnico(db, tag)
    s = _setup(db, tag, id_unidad)
    _, jar, _ = iniciar_sesion(client, cuenta.correo, "una frase larga de paso tec")
    return headers_autenticados(jar), cuenta, s


def _login_usr(client, db, tag, proyecto_id):
    usuario, cuenta = crear_usuario_cuenta(db, tag)
    usuario.perfil_actualizado_at = datetime.now(timezone.utc)
    db.add(UsuarioProyectos(
        id_usuario=usuario.id_usuario, id_proyecto=proyecto_id, estado=True))
    db.commit()
    _, jar, _ = iniciar_sesion(client, cuenta.correo, "una frase larga de paso")
    return headers_autenticados(jar), cuenta, usuario.id_usuario


def _fecha(i: int) -> str:
    return (date(2030, 7, 3) + timedelta(days=i)).isoformat()


def _base(s: dict, tipo: str, obs: str) -> dict:
    return {"id_unidad": s["id_unidad"], "tipo_reserva": tipo,
            "observacion": obs, "contexto": {"proyecto_id": s["proyecto_id"]}}


def test_crear_cinco_tipos(client, db, tag):
    """Cada tipo se crea con su detalle y estado inicial correcto."""
    h_tec, _, s = _login_tec(client, db, f"a{tag}")
    rids: list[int] = []
    try:
        cuerpos = [
            ("ESPACIO", {"espacio_id": s["espacio_id"], "fecha": _fecha(1),
                         "hora_inicio": "10:00", "hora_fin": "12:00"}, None),
            ("RECURSO_INTERNO", {"fecha": _fecha(2), "hora_inicio": "10:00",
                                 "hora_fin": "12:00"},
             [{"recurso_id": s["recurso_id"], "rol": "PRINCIPAL"}]),
            ("RECURSO_CAMPUS", {"fecha_salida": _fecha(3),
                                "fecha_devolucion_estimada": _fecha(4),
                                "razon_solicitud": "Práctica",
                                "lugar_nombre": "Sede", "lugar_direccion": "Calle 1"},
             [{"recurso_id": s["recurso_id"], "rol": "PRINCIPAL"}]),
            ("RECURSO_EXTERNO", {"fecha_salida": _fecha(5),
                                 "fecha_devolucion_estimada": _fecha(6),
                                 "razon_solicitud": "Evento",
                                 "lugar_nombre": "Sede", "lugar_direccion": "Calle 1"},
             [{"recurso_id": s["recurso2_id"], "rol": "PRINCIPAL"}]),
            ("LISTA_ESPERA", {"descripcion_necesidad": "Fabricar pieza"}, None),
        ]
        for i, (tipo, detalle, recursos) in enumerate(cuerpos):
            cuerpo = _base(s, tipo, f"api13-{i}-{tag}")
            cuerpo["detalle"] = detalle
            if recursos:
                cuerpo["recursos"] = recursos
            r = client.post("/api/reservas", json=cuerpo, headers=h_tec)
            assert r.status_code == 201, (tipo, r.text)
            assert r.json()["tipo_reserva"] == tipo
            # PERSONAL nace APROBADA, salvo lista de espera (siempre SOLICITADA).
            esperado = "SOLICITADA" if tipo == "LISTA_ESPERA" else "APROBADA"
            assert r.json()["estado"] == esperado, (tipo, r.text)
            rids.append(r.json()["id"])
    finally:
        _teardown(db, s, rids)


def test_solapamiento_409(client, db, tag):
    """Segunda reserva sobre la misma franja → 409 SOLAPAMIENTO."""
    h_tec, _, s = _login_tec(client, db, f"a{tag}")
    rids = []
    try:
        cuerpo = _base(s, "ESPACIO", f"api13-sol-{tag}")
        cuerpo["detalle"] = {"espacio_id": s["espacio_id"], "fecha": _fecha(10),
                             "hora_inicio": "10:00", "hora_fin": "12:00"}
        r1 = client.post("/api/reservas", json=cuerpo, headers=h_tec)
        assert r1.status_code == 201, r1.text
        rids.append(r1.json()["id"])
        r2 = client.post("/api/reservas", json=cuerpo, headers=h_tec)
        assert r2.status_code == 409, r2.text
        assert r2.json()["error"]["codigo"] == "SOLAPAMIENTO"
    finally:
        _teardown(db, s, rids)


def test_editar_solo_solicitada(client, db, tag):
    """PATCH en SOLICITADA edita; en APROBADA responde 409."""
    h_tec, _, s = _login_tec(client, db, f"a{tag}")
    h_usr, _, id_usuario = _login_usr(client, db, f"b{tag}", s["proyecto_id"])
    rids = []
    try:
        cuerpo = _base(s, "ESPACIO", f"api13-edit-{tag}")
        cuerpo["detalle"] = {"espacio_id": s["espacio_id"], "fecha": _fecha(11),
                             "hora_inicio": "10:00", "hora_fin": "12:00"}
        r = client.post("/api/reservas", json=cuerpo, headers=h_usr)
        assert r.json()["estado"] == "SOLICITADA"
        rid = r.json()["id"]
        rids.append(rid)
        ok = client.patch(f"/api/reservas/{rid}",
                          json={"observacion": "Nueva obs"}, headers=h_usr)
        assert ok.status_code == 200, ok.text
        assert ok.json()["observacion"] == "Nueva obs"
        client.post(f"/api/reservas/{rid}/aprobacion", json={}, headers=h_tec)
        mala = client.patch(f"/api/reservas/{rid}",
                            json={"observacion": "Otra"}, headers=h_usr)
        assert mala.status_code == 409, mala.text
    finally:
        _teardown(db, s, rids, id_usuario)


def test_disponibilidad(client, db, tag):
    """GET disponibilidad con franjas ocupadas y horario de unidad."""
    h_tec, _, s = _login_tec(client, db, f"a{tag}")
    rids = []
    try:
        cuerpo = _base(s, "ESPACIO", f"api13-disp-{tag}")
        cuerpo["detalle"] = {"espacio_id": s["espacio_id"], "fecha": _fecha(12),
                             "hora_inicio": "10:00", "hora_fin": "12:00"}
        rids.append(client.post("/api/reservas", json=cuerpo, headers=h_tec).json()["id"])
        d = client.get(
            f"/api/reservas/disponibilidad?id_unidad={s['id_unidad']}"
            f"&espacio_id={s['espacio_id']}&desde={_fecha(12)}&hasta={_fecha(12)}",
            headers=h_tec)
        assert d.status_code == 200, d.text
        assert d.json()["franjas"][0]["disponible"] is False
    finally:
        _teardown(db, s, rids)


def test_lista_espera_flujo(client, db, tag):
    """Viabilidad + formulario + adjunto en lista de espera."""
    h_tec, _, s = _login_tec(client, db, f"a{tag}")
    h_usr, _, id_usuario = _login_usr(client, db, f"b{tag}", s["proyecto_id"])
    rids = []
    try:
        cuerpo = _base(s, "LISTA_ESPERA", f"api13-le-{tag}")
        cuerpo["detalle"] = {"descripcion_necesidad": "Fabricar pieza"}
        r = client.post("/api/reservas", json=cuerpo, headers=h_usr)
        assert r.status_code == 201, r.text
        rid = r.json()["id"]
        rids.append(rid)
        v = client.post(f"/api/reservas/{rid}/lista-espera/viabilidad",
                        json={"viable": True}, headers=h_tec)
        assert v.status_code == 200, v.text
        f = client.put(f"/api/reservas/{rid}/lista-espera/formulario",
                       json={"datos_usuario": {"contacto": "x"}}, headers=h_usr)
        assert f.status_code == 200, f.text
        a = client.post(
            f"/api/reservas/{rid}/lista-espera/adjuntos",
            files={"archivo": ("plano.pdf", b"%PDF-1.4 fake", "application/pdf")},
            data={"tipo_adjunto": "DOCUMENTO"}, headers=h_usr)
        assert a.status_code == 201, a.text
        li = client.get(f"/api/reservas/{rid}/lista-espera/adjuntos", headers=h_usr)
        assert li.json()["paginacion"]["total"] == 1
    finally:
        _teardown(db, s, rids, id_usuario)
