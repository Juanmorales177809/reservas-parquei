"""Pruebas de contrato de reservations §4-§6 (API-14).

Cubre gestión por el Técnico, propuestas de periodo y ejecución,
incluidos los tres casos de aceptación de la tarea:
finalizar ESPACIO → 409 CONFLICTO, ejecutar ESPACIO →
409 TIPO_NO_ADMITIDO y finalizar recursos sin devolución completa →
error sin cierre parcial.
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
        text("SELECT id FROM reservas.tipos_reserva WHERE codigo = :c"), {"c": codigo}
    )


def _setup_unidad(db, tag: str, id_unidad: int, tipos: tuple[str, ...] = ("ESPACIO",)) -> dict:
    """Config, tipos habilitados, un espacio, un proyecto y un equipo
    sobre la unidad dada (la del cargo vigente del técnico)."""
    ahora = datetime.now(timezone.utc)
    db.add(
        LaboratoriosConfig(
            id_unidad=id_unidad,
            habilitado_reservas=True,
            dias_atencion=[0, 1, 2, 3, 4, 5, 6],
            hora_apertura=time(0, 0),
            hora_cierre=time(23, 59),
            horario_atencion={},
            horas_antelacion=0,
            aprobacion_automatica=False,
            notificar_por_correo=False,
            mostrar_estado_reserva=False,
            mostrar_reservista=False,
            recordatorio_horas_antes=24,
        )
    )
    for codigo in tipos:
        db.add(
            LaboratorioTiposReserva(
                id_unidad=id_unidad,
                tipo_reserva_id=_tipo_id(db, codigo),
                habilitado=True,
                created_at=ahora,
                updated_at=ahora,
            )
        )
    espacio = Espacios(
        id_unidad=id_unidad,
        nombre=f"Espacio api14 {tag}",
        capacidad=10,
        habilitado=True,
        created_at=ahora,
        updated_at=ahora,
    )
    db.add(espacio)
    db.flush()
    proyecto = Proyectos(codigo=f"PRY-{tag}", nombre=f"Proyecto {tag}", estado=True)
    db.add(proyecto)
    db.flush()
    recurso = Recursos(
        id_unidad=id_unidad, tipo="EQUIPO", habilitado=True,
        created_at=ahora, updated_at=ahora,
    )
    db.add(recurso)
    db.flush()
    db.add(
        Equipos(
            id=recurso.id, nombre_equipo=f"Equipo api14 {tag}",
            requiere_apoyo=False, acreditado=False,
        )
    )
    db.commit()
    return {
        "id_unidad": id_unidad,
        "espacio_id": espacio.id,
        "proyecto_id": proyecto.id_proyecto,
        "recurso_id": recurso.id,
    }


def _teardown_unidad(db, s: dict, id_usuario: int | None = None) -> None:
    if id_usuario is not None:
        for tabla in (
            "usuario_proyectos",
            "usuario_semilleros",
            "usuario_pasantias",
            "usuario_trabajos_grado",
        ):
            db.execute(
                text(f"DELETE FROM investigacion.{tabla} WHERE id_usuario = :u"),
                {"u": id_usuario},
            )
    db.execute(
        text("DELETE FROM recursos.equipos WHERE id = :i"), {"i": s["recurso_id"]}
    )
    db.execute(
        text("DELETE FROM recursos.recursos WHERE id = :i"), {"i": s["recurso_id"]}
    )
    db.execute(
        text("DELETE FROM investigacion.proyectos WHERE id_proyecto = :i"),
        {"i": s["proyecto_id"]},
    )
    db.execute(
        text("DELETE FROM reservas.espacios WHERE id = :i"), {"i": s["espacio_id"]}
    )
    db.execute(
        text("DELETE FROM reservas.laboratorio_tipos_reserva WHERE id_unidad = :u"),
        {"u": s["id_unidad"]},
    )
    db.execute(
        text("DELETE FROM reservas.laboratorios_config WHERE id_unidad = :u"),
        {"u": s["id_unidad"]},
    )
    db.commit()


def _borrar_reserva(db, reserva_id: int) -> None:
    db.execute(
        text(
            "DELETE FROM reservas.orden_salida_items WHERE orden_salida_id IN "
            "(SELECT id FROM reservas.ordenes_salida WHERE reserva_id = :i)"
        ),
        {"i": reserva_id},
    )
    db.execute(
        text(
            "DELETE FROM reservas.orden_salida_actividades WHERE orden_salida_id IN "
            "(SELECT id FROM reservas.ordenes_salida WHERE reserva_id = :i)"
        ),
        {"i": reserva_id},
    )
    db.execute(
        text("DELETE FROM reservas.ordenes_salida WHERE reserva_id = :i"),
        {"i": reserva_id},
    )
    db.execute(
        text(
            "DELETE FROM reservas.reserva_ejecucion_recursos WHERE reserva_recurso_id IN "
            "(SELECT id FROM reservas.reserva_recursos WHERE reserva_id = :i)"
        ),
        {"i": reserva_id},
    )
    for tabla in (
        "reserva_historial_estado",
        "reserva_propuestas",
        "reserva_recursos",
        "reserva_contexto",
        "reserva_espacio",
        "reserva_recurso_interno",
        "reserva_datos_salida",
        "reserva_recurso_campus",
        "reserva_recurso_externo",
    ):
        db.execute(
            text(f"DELETE FROM reservas.{tabla} WHERE reserva_id = :i"),
            {"i": reserva_id},
        )
    db.execute(text("DELETE FROM reservas.reservas WHERE id = :i"), {"i": reserva_id})
    db.commit()


def _fecha(i: int) -> str:
    return (date(2030, 2, 3) + timedelta(days=i)).isoformat()


def _crear_espacio(client, headers, s: dict, dia: int, obs: str) -> dict:
    r = client.post(
        "/api/reservas",
        json={
            "id_unidad": s["id_unidad"],
            "tipo_reserva": "ESPACIO",
            "observacion": obs,
            "contexto": {"proyecto_id": s["proyecto_id"]},
            "detalle": {
                "espacio_id": s["espacio_id"],
                "fecha": _fecha(dia),
                "hora_inicio": "10:00",
                "hora_fin": "12:00",
            },
        },
        headers=headers,
    )
    assert r.status_code == 201, r.text
    return r.json()


def _login_tecnico(client, db, tag):
    cuenta, id_unidad = crear_tecnico(db, tag)
    _, jar, _ = iniciar_sesion(client, cuenta.correo, "una frase larga de paso tec")
    return headers_autenticados(jar), cuenta, id_unidad


def _login_usuario(client, db, tag, proyecto_id):
    usuario, cuenta = crear_usuario_cuenta(db, tag)
    usuario.perfil_actualizado_at = datetime.now(timezone.utc)
    db.add(
        UsuarioProyectos(
            id_usuario=usuario.id_usuario, id_proyecto=proyecto_id, estado=True
        )
    )
    db.commit()
    _, jar, _ = iniciar_sesion(client, cuenta.correo, "una frase larga de paso")
    return headers_autenticados(jar), cuenta, usuario.id_usuario


def test_aprobacion_y_rechazo(client, db, tag):
    """§4.1/§4.2: SOLICITADA de USUARIO se aprueba y otra se rechaza con motivo."""
    s = None
    creadas: list[int] = []
    try:
        h_tec, _, id_unidad = _login_tecnico(client, db, tag)
        s = _setup_unidad(db, tag, id_unidad)
        h_usr, _, id_usuario = _login_usuario(client, db, tag, s["proyecto_id"])

        r1 = _crear_espacio(client, h_usr, s, 1, f"api14-aprobar-{tag}")
        creadas.append(r1["id"])
        assert r1["estado"] == "SOLICITADA"
        ap = client.post(
            f"/api/reservas/{r1['id']}/aprobacion", json={}, headers=h_tec
        )
        assert ap.status_code == 200, ap.text
        assert ap.json()["estado"] == "APROBADA"
        assert ap.json()["fecha_aprobacion"]

        r2 = _crear_espacio(client, h_usr, s, 2, f"api14-rechazar-{tag}")
        creadas.append(r2["id"])
        re = client.post(
            f"/api/reservas/{r2['id']}/rechazo",
            json={"motivo": "Sin disponibilidad"},
            headers=h_tec,
        )
        assert re.status_code == 200, re.text
        assert re.json()["estado"] == "RECHAZADA"
        assert re.json()["motivo"] == "Sin disponibilidad"
    finally:
        for rid in creadas:
            _borrar_reserva(db, rid)
        if s:
            _teardown_unidad(db, s, id_usuario)


def test_agregar_y_retirar_recurso_espacio(client, db, tag):
    """§4.3/§4.4: complementario ADICIONAL se agrega (201) y se retira (204)."""
    s = None
    r: dict | None = None
    try:
        h_tec, _, id_unidad = _login_tecnico(client, db, tag)
        s = _setup_unidad(db, tag, id_unidad)
        r = _crear_espacio(client, h_tec, s, 3, f"api14-recursos-{tag}")
        ag = client.post(
            f"/api/reservas/{r['id']}/recursos",
            json={"recursos": [{"recurso_id": s["recurso_id"], "rol": "ADICIONAL"}]},
            headers=h_tec,
        )
        assert ag.status_code == 201, ag.text
        asignaciones = ag.json()["datos"]
        assert len(asignaciones) == 1
        assert asignaciones[0]["estado_asignacion"] == "ASIGNADO"

        ret = client.delete(
            f"/api/reservas/{r['id']}/recursos/{asignaciones[0]['reserva_recurso_id']}",
            headers=h_tec,
        )
        assert ret.status_code == 204, ret.text
        det = client.get(f"/api/reservas/{r['id']}", headers=h_tec)
        assert det.status_code == 200
        assert all(
            a["estado_asignacion"] == "RETIRADO" for a in det.json()["recursos"]
        )
    finally:
        if r:
            _borrar_reserva(db, r["id"])
        if s:
            _teardown_unidad(db, s)


def test_propuesta_aceptada_reprograma(client, db, tag):
    """§5.1/§5.2: la contraparte acepta y la franja cambia sin cambiar el estado."""
    s = None
    r = None
    try:
        h_tec, _, id_unidad = _login_tecnico(client, db, tag)
        s = _setup_unidad(db, tag, id_unidad)
        h_usr, _, id_usuario = _login_usuario(client, db, tag, s["proyecto_id"])
        r = _crear_espacio(client, h_usr, s, 4, f"api14-prop-{tag}")

        pr = client.post(
            f"/api/reservas/{r['id']}/propuestas",
            json={
                "fecha_inicio_propuesta": _fecha(5),
                "fecha_fin_propuesta": _fecha(5),
                "hora_inicio": "14:00",
                "hora_fin": "16:00",
                "motivo": "Mantenimiento matinal",
            },
            headers=h_tec,
        )
        assert pr.status_code == 201, pr.text
        assert pr.json()["origen"] == "TECNICO"
        assert pr.json()["estado"] == "VIGENTE"

        ac = client.post(
            f"/api/reservas/{r['id']}/propuestas/vigente/aceptacion", headers=h_usr
        )
        assert ac.status_code == 200, ac.text
        assert ac.json()["estado"] == "SOLICITADA"
        det = client.get(f"/api/reservas/{r['id']}", headers=h_usr)
        assert det.json()["detalle"]["fecha"] == _fecha(5)
    finally:
        if r:
            _borrar_reserva(db, r["id"])
        if s:
            _teardown_unidad(db, s, id_usuario)


def test_propuesta_rechazada_conserva_horario(client, db, tag):
    """§5.3: rechazar no revoca ni mueve la franja original."""
    s = None
    r = None
    try:
        h_tec, _, id_unidad = _login_tecnico(client, db, tag)
        s = _setup_unidad(db, tag, id_unidad)
        h_usr, _, id_usuario = _login_usuario(client, db, tag, s["proyecto_id"])
        r = _crear_espacio(client, h_usr, s, 6, f"api14-no-prop-{tag}")

        pr = client.post(
            f"/api/reservas/{r['id']}/propuestas",
            json={
                "fecha_inicio_propuesta": _fecha(7),
                "fecha_fin_propuesta": _fecha(7),
                "hora_inicio": "14:00",
                "hora_fin": "16:00",
                "motivo": "Sugerencia",
            },
            headers=h_tec,
        )
        assert pr.status_code == 201, pr.text
        rech = client.post(
            f"/api/reservas/{r['id']}/propuestas/vigente/rechazo", headers=h_usr
        )
        assert rech.status_code == 200, rech.text
        assert rech.json()["estado"] == "RECHAZADA"
        det = client.get(f"/api/reservas/{r['id']}", headers=h_usr)
        assert det.json()["estado"] == "SOLICITADA"
        assert det.json()["detalle"]["fecha"] == _fecha(6)
    finally:
        if r:
            _borrar_reserva(db, r["id"])
        if s:
            _teardown_unidad(db, s, id_usuario)


def test_finalizar_espacio_no_admitido(client, db, tag):
    """Aceptación API-14 + contrato §6.2: finalizar ESPACIO → 409 TIPO_NO_ADMITIDO."""
    s = None
    r = None
    try:
        h_tec, _, id_unidad = _login_tecnico(client, db, tag)
        s = _setup_unidad(db, tag, id_unidad)
        r = _crear_espacio(client, h_tec, s, 8, f"api14-fin-esp-{tag}")
        assert r["estado"] == "APROBADA"
        fin = client.post(
            f"/api/reservas/{r['id']}/finalizacion", json={}, headers=h_tec
        )
        assert fin.status_code == 409, fin.text
        assert fin.json()["error"]["codigo"] == "TIPO_NO_ADMITIDO"
    finally:
        if r:
            _borrar_reserva(db, r["id"])
        if s:
            _teardown_unidad(db, s)


def test_ejecutar_espacio_no_admitido(client, db, tag):
    """Aceptación API-14: ejecutar ESPACIO responde 409 TIPO_NO_ADMITIDO."""
    s = None
    r = None
    try:
        h_tec, _, id_unidad = _login_tecnico(client, db, tag)
        s = _setup_unidad(db, tag, id_unidad)
        r = _crear_espacio(client, h_tec, s, 9, f"api14-eje-esp-{tag}")
        eje = client.post(
            f"/api/reservas/{r['id']}/ejecucion", json={}, headers=h_tec
        )
        assert eje.status_code == 409, eje.text
        assert eje.json()["error"]["codigo"] == "TIPO_NO_ADMITIDO"
    finally:
        if r:
            _borrar_reserva(db, r["id"])
        if s:
            _teardown_unidad(db, s)


def test_transiciones_internas_automaticas(client, db, tag):
    """Contrato §6.1/§6.2: en RECURSO_INTERNO ejecutar y finalizar manuales
    responden 409 TIPO_NO_ADMITIDO (inicio y fin automáticos por horario)."""
    s = None
    rid: int | None = None
    try:
        h_tec, _, id_unidad = _login_tecnico(client, db, tag)
        s = _setup_unidad(db, tag, id_unidad, tipos=("ESPACIO", "RECURSO_INTERNO"))
        r = client.post(
            "/api/reservas",
            json={
                "id_unidad": s["id_unidad"],
                "tipo_reserva": "RECURSO_INTERNO",
                "observacion": f"api14-interno-{tag}",
                "contexto": {"proyecto_id": s["proyecto_id"]},
                "detalle": {
                    "fecha": _fecha(10),
                    "hora_inicio": "10:00",
                    "hora_fin": "12:00",
                },
                "recursos": [
                    {"recurso_id": s["recurso_id"], "rol": "PRINCIPAL"}
                ],
            },
            headers=h_tec,
        )
        assert r.status_code == 201, r.text
        rid = r.json()["id"]
        eje = client.post(
            f"/api/reservas/{rid}/ejecucion", json={}, headers=h_tec
        )
        assert eje.status_code == 409, eje.text
        assert eje.json()["error"]["codigo"] == "TIPO_NO_ADMITIDO"
        fin = client.post(
            f"/api/reservas/{rid}/finalizacion", json={}, headers=h_tec
        )
        assert fin.status_code == 409, fin.text
        assert fin.json()["error"]["codigo"] == "TIPO_NO_ADMITIDO"
    finally:
        if rid:
            _borrar_reserva(db, rid)
        if s:
            _teardown_unidad(db, s)


def test_finalizar_campus_sin_devolucion_falla(client, db, tag):
    """Aceptación API-14: sin devolución completa hay error y no hay cierre parcial."""
    s = None
    rid = None
    try:
        h_tec, _, id_unidad = _login_tecnico(client, db, tag)
        s = _setup_unidad(db, tag, id_unidad, tipos=("ESPACIO", "RECURSO_CAMPUS"))
        r = client.post(
            "/api/reservas",
            json={
                "id_unidad": s["id_unidad"],
                "tipo_reserva": "RECURSO_CAMPUS",
                "observacion": f"api14-campus-{tag}",
                "contexto": {"proyecto_id": s["proyecto_id"]},
                "detalle": {
                    "fecha_salida": _fecha(11),
                    "fecha_devolucion_estimada": _fecha(12),
                    "razon_solicitud": "Práctica externa",
                    "lugar_nombre": "Sede alterna",
                    "lugar_direccion": "Calle 1 # 2-3",
                },
                "recursos": [
                    {"recurso_id": s["recurso_id"], "rol": "PRINCIPAL"}
                ],
            },
            headers=h_tec,
        )
        assert r.status_code == 201, r.text
        rid = r.json()["id"]
        det = client.get(f"/api/reservas/{rid}", headers=h_tec).json()
        asig = det["recursos"][0]["reserva_recurso_id"]

        eje = client.post(
            f"/api/reservas/{rid}/ejecucion",
            json={"recursos": [{"reserva_recurso_id": asig}]},
            headers=h_tec,
        )
        assert eje.status_code == 200, eje.text

        mala = client.post(
            f"/api/reservas/{rid}/finalizacion",
            json={"recursos": []},
            headers=h_tec,
        )
        assert mala.status_code == 409, mala.text
        det2 = client.get(f"/api/reservas/{rid}", headers=h_tec).json()
        assert det2["estado"] == "EN_EJECUCION"

        buena = client.post(
            f"/api/reservas/{rid}/finalizacion",
            json={"recursos": [{"reserva_recurso_id": asig}]},
            headers=h_tec,
        )
        assert buena.status_code == 200, buena.text
        assert buena.json()["estado"] == "FINALIZADA"
    finally:
        if rid:
            _borrar_reserva(db, rid)
        if s:
            _teardown_unidad(db, s)


def test_cancelacion_y_errores_basicos(client, db, tag):
    """§6.3: el dueño cancela; reserva inexistente → 404; sin CSRF → 403."""
    s = None
    r = None
    try:
        h_tec, _, id_unidad = _login_tecnico(client, db, tag)
        s = _setup_unidad(db, tag, id_unidad)
        h_usr, _, id_usuario = _login_usuario(client, db, tag, s["proyecto_id"])
        r = _crear_espacio(client, h_usr, s, 13, f"api14-cancel-{tag}")

        sin_csrf = dict(h_usr)
        sin_csrf.pop("X-CSRF-Token")
        c0 = client.post(
            f"/api/reservas/{r['id']}/cancelacion",
            json={"motivo": "x"},
            headers=sin_csrf,
        )
        assert c0.status_code == 403, c0.text

        c1 = client.post(
            f"/api/reservas/{r['id']}/cancelacion",
            json={"motivo": "Ya no se necesita"},
            headers=h_usr,
        )
        assert c1.status_code == 200, c1.text
        assert c1.json()["estado"] == "CANCELADA"

        c2 = client.post(
            "/api/reservas/999999/cancelacion", json={}, headers=h_tec
        )
        assert c2.status_code == 404, c2.text
    finally:
        if r:
            _borrar_reserva(db, r["id"])
        if s:
            _teardown_unidad(db, s, id_usuario)
