"""Pruebas de contrato de reservations §7-§8 (API-15).

Orden de salida (JSON/PDF), calendario .ics y exportación csv/excel,
incluidos los casos de aceptación: snapshots inmutables, 409/404 de orden,
.ics solo para espacio/interno y exportación con permiso y ámbito.
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from io import BytesIO

import openpyxl
from sqlalchemy import select, text

from .conftest import (
    crear_tecnico,
    crear_usuario_cuenta,
    headers_autenticados,
    iniciar_sesion,
)

from app.db.models.auth import CuentaPermisos, Permisos
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


def _setup_unidad(db, tag: str, id_unidad: int) -> dict:
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
    for codigo in ("ESPACIO", "RECURSO_INTERNO", "RECURSO_CAMPUS"):
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
        nombre=f"Espacio api15 {tag}",
        ubicacion="Bloque B, piso 2",
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
            id=recurso.id, nombre_equipo=f"Equipo api15 {tag}",
            placa=f"PL-{tag[:8]}", requiere_apoyo=False, acreditado=False,
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
        db.execute(
            text("DELETE FROM investigacion.usuario_proyectos WHERE id_usuario = :u"),
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
    # API-18: cada operación deja evento + in-app + envíos con FK.
    db.execute(
        text(
            "DELETE FROM notificaciones.envios_correo WHERE evento_id IN "
            "(SELECT id FROM notificaciones.eventos WHERE reserva_id = :i)"
        ),
        {"i": reserva_id},
    )
    db.execute(
        text(
            "DELETE FROM notificaciones.notificaciones WHERE evento_id IN "
            "(SELECT id FROM notificaciones.eventos WHERE reserva_id = :i)"
        ),
        {"i": reserva_id},
    )
    db.execute(
        text("DELETE FROM notificaciones.eventos WHERE reserva_id = :i"),
        {"i": reserva_id},
    )
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
    return (date(2030, 3, 3) + timedelta(days=i)).isoformat()


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


def _otorgar_exportar(db, cuenta, id_unidad):
    permiso = db.scalar(select(Permisos).where(Permisos.codigo == "reservas.exportar"))
    assert permiso is not None
    db.add(
        CuentaPermisos(
            id_cuenta=cuenta.id_cuenta,
            permiso_id=permiso.id,
            id_unidad=id_unidad,
            otorgado_por=cuenta.id_cuenta,
            created_at=datetime.now(timezone.utc),
        )
    )
    db.commit()


def _crear_campus(client, headers, s: dict, dia: int, obs: str) -> dict:
    r = client.post(
        "/api/reservas",
        json={
            "id_unidad": s["id_unidad"],
            "tipo_reserva": "RECURSO_CAMPUS",
            "observacion": obs,
            "contexto": {"proyecto_id": s["proyecto_id"]},
            "detalle": {
                "fecha_salida": _fecha(dia),
                "fecha_devolucion_estimada": _fecha(dia + 1),
                "razon_solicitud": "Práctica externa",
                "lugar_nombre": "Sede alterna",
                "lugar_direccion": "Calle 1 # 2-3",
            },
            "recursos": [{"recurso_id": s["recurso_id"], "rol": "PRINCIPAL"}],
        },
        headers=headers,
    )
    assert r.status_code == 201, r.text
    return r.json()


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


def test_orden_json_e_inmutable(client, db, tag):
    """§7.1: snapshots, actividades e ítems; dos lecturas idénticas."""
    s = None
    rid = None
    try:
        h_tec, _, id_unidad = _login_tecnico(client, db, tag)
        s = _setup_unidad(db, tag, id_unidad)
        rid = _crear_campus(client, h_tec, s, 1, f"api15-orden-{tag}")["id"]

        o1 = client.get(f"/api/reservas/{rid}/orden-salida", headers=h_tec)
        assert o1.status_code == 200, o1.text
        d1 = o1.json()
        assert d1["reserva_id"] == rid
        assert d1["razon_solicitud"] == "Práctica externa"
        assert d1["lugar_nombre"] == "Sede alterna"
        assert "PROYECTO_INVESTIGACION" in d1["actividades"]
        assert len(d1["items"]) == 1
        assert d1["items"][0]["placa_snapshot"] == f"PL-{tag[:8]}"
        assert "firma" not in o1.text.lower()

        o2 = client.get(f"/api/reservas/{rid}/orden-salida", headers=h_tec)
        assert o2.json() == d1
    finally:
        if rid:
            _borrar_reserva(db, rid)
        if s:
            _teardown_unidad(db, s)


def test_orden_errores(client, db, tag):
    """§7.1: tipo sin FGL → 409; campus sin aprobar → 404."""
    s = None
    r_esp = None
    r_sol = None
    try:
        h_tec, _, id_unidad = _login_tecnico(client, db, tag)
        s = _setup_unidad(db, tag, id_unidad)
        h_usr, _, id_usuario = _login_usuario(client, db, tag, s["proyecto_id"])

        r_esp = _crear_espacio(client, h_tec, s, 3, f"api15-orden-esp-{tag}")
        o = client.get(f"/api/reservas/{r_esp['id']}/orden-salida", headers=h_tec)
        assert o.status_code == 409, o.text
        assert o.json()["error"]["codigo"] == "TIPO_NO_ADMITIDO"

        r_sol = _crear_campus(client, h_usr, s, 4, f"api15-orden-sol-{tag}")
        assert r_sol["estado"] == "SOLICITADA"
        o2 = client.get(f"/api/reservas/{r_sol['id']}/orden-salida", headers=h_tec)
        assert o2.status_code == 404, o2.text
    finally:
        for rid in (r_esp["id"] if r_esp else None, r_sol["id"] if r_sol else None):
            if rid:
                _borrar_reserva(db, rid)
        if s:
            _teardown_unidad(db, s, id_usuario)


def test_orden_pdf(client, db, tag):
    """§7.2: PDF imprimible generado de snapshots, sin firmas capturadas."""
    s = None
    rid = None
    try:
        h_tec, _, id_unidad = _login_tecnico(client, db, tag)
        s = _setup_unidad(db, tag, id_unidad)
        rid = _crear_campus(client, h_tec, s, 5, f"api15-pdf-{tag}")["id"]

        p = client.get(f"/api/reservas/{rid}/orden-salida.pdf", headers=h_tec)
        assert p.status_code == 200, p.content[:200]
        assert "application/pdf" in p.headers["content-type"]
        assert p.content.startswith(b"%PDF")
        assert len(p.content) > 2000
    finally:
        if rid:
            _borrar_reserva(db, rid)
        if s:
            _teardown_unidad(db, s)


def test_ics_espacio_e_interno(client, db, tag):
    """§8.1: VCALENDAR con periodo y ubicación en espacio/interno aprobadas."""
    s = None
    r1 = r2 = None
    try:
        h_tec, _, id_unidad = _login_tecnico(client, db, tag)
        s = _setup_unidad(db, tag, id_unidad)
        r1 = _crear_espacio(client, h_tec, s, 6, f"api15-ics-esp-{tag}")
        assert r1["estado"] == "APROBADA"

        ics = client.get(f"/api/reservas/{r1['id']}/calendario.ics", headers=h_tec)
        assert ics.status_code == 200, ics.text
        assert "text/calendar" in ics.headers["content-type"]
        cuerpo = ics.text
        assert "BEGIN:VCALENDAR" in cuerpo and "BEGIN:VEVENT" in cuerpo
        assert f"DTSTART;TZID=America/Bogota:{_fecha(6).replace('-', '')}T100000" in cuerpo
        assert f"DTEND;TZID=America/Bogota:{_fecha(6).replace('-', '')}T120000" in cuerpo
        assert "Bloque B" in cuerpo
    finally:
        for r in (r1, r2):
            if r:
                _borrar_reserva(db, r["id"])
        if s:
            _teardown_unidad(db, s)


def test_ics_errores(client, db, tag):
    """§8.1: campus → 409 TIPO_NO_ADMITIDO; no aprobada → 409 ESTADO_INCOMPATIBLE."""
    s = None
    r_campus = r_sol = None
    try:
        h_tec, _, id_unidad = _login_tecnico(client, db, tag)
        s = _setup_unidad(db, tag, id_unidad)
        h_usr, _, id_usuario = _login_usuario(client, db, tag, s["proyecto_id"])

        r_campus = _crear_campus(client, h_tec, s, 7, f"api15-ics-cam-{tag}")
        c = client.get(
            f"/api/reservas/{r_campus['id']}/calendario.ics", headers=h_tec
        )
        assert c.status_code == 409, c.text
        assert c.json()["error"]["codigo"] == "TIPO_NO_ADMITIDO"

        r_sol = _crear_espacio(client, h_usr, s, 8, f"api15-ics-sol-{tag}")
        assert r_sol["estado"] == "SOLICITADA"
        c2 = client.get(
            f"/api/reservas/{r_sol['id']}/calendario.ics", headers=h_usr
        )
        assert c2.status_code == 409, c2.text
        assert c2.json()["error"]["codigo"] == "ESTADO_INCOMPATIBLE"
    finally:
        for r in (r_campus, r_sol):
            if r:
                _borrar_reserva(db, r["id"])
        if s:
            _teardown_unidad(db, s, id_usuario)


def test_exportacion_csv_y_excel(client, db, tag):
    """§8.2: csv y excel con lo visible; formato malo → 400; sin permiso → 403."""
    s = None
    r = None
    try:
        h_tec, cuenta_tec, id_unidad = _login_tecnico(client, db, tag)
        s = _setup_unidad(db, tag, id_unidad)
        _otorgar_exportar(db, cuenta_tec, id_unidad)
        h_usr, _, id_usuario = _login_usuario(client, db, tag, s["proyecto_id"])
        r = _crear_espacio(client, h_tec, s, 9, f"api15-exp-{tag}")

        csv_r = client.get(
            "/api/reservas/exportacion?formato=csv", headers=h_tec
        )
        assert csv_r.status_code == 200, csv_r.text
        assert "text/csv" in csv_r.headers["content-type"]
        lineas = csv_r.text.strip().splitlines()
        assert lineas[0].split(",")[:4] == ["id", "estado", "tipo_reserva", "id_unidad"]
        assert any(str(r["id"]) in l for l in lineas[1:])

        xls = client.get(
            "/api/reservas/exportacion?formato=excel", headers=h_tec
        )
        assert xls.status_code == 200
        libro = openpyxl.load_workbook(filename=BytesIO(xls.content))
        hoja = libro.active
        assert [c.value for c in hoja[1]][:4] == ["id", "estado", "tipo_reserva", "id_unidad"]
        assert any(row[0].value == str(r["id"]) for row in hoja.iter_rows(min_row=2))

        mala = client.get(
            "/api/reservas/exportacion?formato=xls", headers=h_tec
        )
        assert mala.status_code == 400, mala.text

        denegada = client.get(
            "/api/reservas/exportacion?formato=csv", headers=h_usr
        )
        assert denegada.status_code == 403, denegada.text
    finally:
        if r:
            _borrar_reserva(db, r["id"])
        if s:
            _teardown_unidad(db, s, id_usuario)
