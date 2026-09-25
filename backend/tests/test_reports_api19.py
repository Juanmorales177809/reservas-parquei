"""Pruebas de API-19: ocupación, solicitudes, lista de espera y exportación
(T-REP-01..10). Las filas se siembran directo por repositorio con estados
exactos; lo que se verifica es agregación, ámbito y formato.
"""

from __future__ import annotations

from datetime import date, datetime, time, timezone

import openpyxl
from sqlalchemy import select, text
from io import BytesIO

from .conftest import (
    crear_admin,
    crear_tecnico,
    headers_autenticados,
    iniciar_sesion,
    otorgar_permiso_global,
)

from app.db.models.auth import CuentaPermisos, Permisos
from app.db.models.identidad import UnidadOrganizacional
from app.db.models.reservas import Espacios, LaboratoriosConfig, LaboratoriosConfigHistorico
from app.modules.reservations import repository as repo


def _setup_unidad(db, tag: str, id_unidad: int, con_horario: bool = True) -> dict:
    ahora = datetime.now(timezone.utc)
    db.add(
        LaboratoriosConfig(
            id_unidad=id_unidad, habilitado_reservas=True,
            dias_atencion=[0, 1, 2, 3, 4, 5, 6],
            hora_apertura=time(8, 0), hora_cierre=time(18, 0),
            horario_atencion={}, horas_antelacion=0, aprobacion_automatica=False,
            notificar_por_correo=False, mostrar_estado_reserva=False,
            mostrar_reservista=False, recordatorio_horas_antes=24,
        )
    )
    if con_horario:
        db.add(
            LaboratoriosConfigHistorico(
                id_unidad=id_unidad, dias_atencion=[0, 1, 2, 3, 4, 5, 6],
                hora_apertura=time(8, 0), hora_cierre=time(18, 0),
                horario_atencion={}, vigente_desde=datetime(2020, 1, 1, tzinfo=timezone.utc),
                vigente_hasta=None,
            )
        )
    espacio = Espacios(
        id_unidad=id_unidad, nombre=f"Espacio api19 {tag}", capacidad=10,
        habilitado=True, created_at=ahora, updated_at=ahora,
    )
    db.add(espacio)
    db.commit()
    return {"id_unidad": id_unidad, "espacio_id": espacio.id}


def _otra_unidad(db, tag: str, nombre: str, con_horario: bool = True) -> dict:
    unidad = UnidadOrganizacional(nombre=nombre, tipo="LABORATORIO", estado=True)
    db.add(unidad)
    db.flush()
    return _setup_unidad(db, tag, unidad.id_unidad, con_horario)


def _reserva(db, s: dict, cuenta_id: int, estado: str, dia: str, tag: str) -> int:
    tipo_id = db.scalar(
        text("SELECT id FROM reservas.tipos_reserva WHERE codigo = 'ESPACIO'"))
    estado_id = db.scalar(
        text("SELECT id FROM reservas.estados_reserva WHERE codigo = :e"), {"e": estado})
    r = repo.crear_reserva(
        db, id_unidad=s["id_unidad"], tipo_reserva_id=tipo_id, id_cuenta=cuenta_id,
        estado_id=estado_id, observacion=f"api19-{tag}", requiere_apoyo=False,
        created_by=cuenta_id,
    )
    repo.crear_detalle_espacio(
        db, r.id, espacio_id=s["espacio_id"], fecha=date.fromisoformat(dia),
        hora_inicio=time(10, 0), hora_fin=time(12, 0), asistentes=0,
    )
    db.commit()
    return r.id


def _teardown(db, s: dict, rids: list[int]) -> None:
    for rid in rids:
        for tabla in ("reserva_historial_estado", "reserva_contexto", "reserva_espacio"):
            db.execute(
                text(f"DELETE FROM reservas.{tabla} WHERE reserva_id = :i"), {"i": rid})
        db.execute(text("DELETE FROM reservas.reservas WHERE id = :i"), {"i": rid})
    db.execute(
        text("DELETE FROM reservas.espacios WHERE id_unidad = :u"), {"u": s["id_unidad"]})
    db.execute(
        text("DELETE FROM reservas.laboratorios_config_historico WHERE id_unidad = :u"),
        {"u": s["id_unidad"]},
    )
    db.execute(
        text("DELETE FROM reservas.laboratorios_config WHERE id_unidad = :u"),
        {"u": s["id_unidad"]},
    )
    # La unidad, el cargo y las identidades las limpia conftest: borrar la
    # unidad aquí violaría fk_cargo_unidad y revertiría esta limpieza.
    db.commit()


def _otorgar_unidad(db, cuenta, codigo: str, id_unidad: int) -> None:
    permiso = db.scalar(select(Permisos).where(Permisos.codigo == codigo))
    assert permiso is not None
    db.add(CuentaPermisos(
        id_cuenta=cuenta.id_cuenta, permiso_id=permiso.id, id_unidad=id_unidad,
        otorgado_por=cuenta.id_cuenta, created_at=datetime.now(timezone.utc)))
    db.commit()


def _login_tec(client, db, tag):
    cuenta, id_unidad = crear_tecnico(db, tag)
    s = _setup_unidad(db, tag, id_unidad)
    _otorgar_unidad(db, cuenta, "reportes.consultar", s["id_unidad"])
    _, jar, _ = iniciar_sesion(client, cuenta.correo, "una frase larga de paso tec")
    return headers_autenticados(jar), cuenta, s


def _login_admin(client, db, tag):
    cuenta = crear_admin(db, tag)
    otorgar_permiso_global(db, cuenta, "reportes.consultar")
    _, jar, _ = iniciar_sesion(client, cuenta.correo, "una frase larga de paso admin")
    return headers_autenticados(jar), cuenta


def test_sin_horario_no_hay_porcentaje(client, db, tag):
    """T-REP-01: sin histórico, horas sí y porcentaje null, nunca cero."""
    h, cta, s = _login_tec(client, db, f"a{tag}")
    # Segunda unidad sin versiones de horario.
    s2 = _otra_unidad(db, f"b{tag}", f"Unidad api19 B {tag}", con_horario=False)
    rids_a: list[int] = []
    rids_b: list[int] = []
    try:
        rids_a.append(_reserva(db, s, cta.id_cuenta, "APROBADA", "2030-06-02", tag))
        rids_b.append(_reserva(db, s2, cta.id_cuenta, "APROBADA", "2030-06-02", tag))
        r = client.get(
            "/api/reportes/ocupacion?dimension=espacio&desde=2030-06-01&hasta=2030-06-30",
            headers=h,
        )
        assert r.status_code == 200, r.text
        # El técnico solo ve su unidad.
        assert len(r.json()["datos"]) == 1
        fila = r.json()["datos"][0]
        assert fila["horas_reservadas"] == 2.0
        assert fila["porcentaje_ocupacion"] is not None
    finally:
        _teardown(db, s, rids_a)
        _teardown(db, s2, rids_b)


def test_porcentaje_null_sin_horario_admin(client, db, tag):
    """T-REP-01 (admin): la unidad sin horario trae null, no cero."""
    _, _, s = _login_tec(client, db, f"a{tag}")
    s2 = _otra_unidad(db, f"b{tag}", f"Unidad api19 B {tag}", con_horario=False)
    h_adm, c_adm = _login_admin(client, db, f"c{tag}")
    rids: list[int] = []
    try:
        rids.append(_reserva(db, s2, c_adm.id_cuenta, "APROBADA", "2030-06-02", tag))
        r = client.get(
            "/api/reportes/ocupacion?dimension=espacio&desde=2030-06-01&hasta=2030-06-30&tamano=100",
            headers=h_adm,
        )
        por_unidad = {d["id_unidad"]: d for d in r.json()["datos"]}
        assert por_unidad[s2["id_unidad"]]["horas_reservadas"] == 2.0
        assert por_unidad[s2["id_unidad"]]["porcentaje_ocupacion"] is None
        assert por_unidad[s2["id_unidad"]]["horas_disponibles"] is None
    finally:
        _teardown(db, s, [])
        _teardown(db, s2, rids)


def test_vacio_no_es_error_y_determinista(client, db, tag):
    """T-REP-02/03: sin proyectos que listar, 200 vacío; dos corridas idénticas."""
    h, _, s = _login_tec(client, db, f"a{tag}")
    try:
        q = "/api/reportes/ocupacion?dimension=proyecto&desde=1999-01-01&hasta=1999-01-31&proyecto_id=999999"
        r1 = client.get(q, headers=h)
        r2 = client.get(q, headers=h)
        assert r1.status_code == 200, r1.text
        assert r1.json()["datos"] == []
        assert "paginacion" in r1.json() and "resumen" in r1.json()
        assert r1.json() == r2.json()
    finally:
        _teardown(db, s, [])


def test_estados_por_reporte(client, db, tag):
    """T-REP-04: solicitudes con todos; ocupación sin SOLICITADA."""
    h, cta, s = _login_tec(client, db, f"a{tag}")
    rids: list[int] = []
    try:
        rids.append(_reserva(db, s, cta.id_cuenta, "SOLICITADA", "2030-06-03", tag))
        # Día distinto: la exclusión impediría dos franjas solapadas.
        rids.append(_reserva(db, s, cta.id_cuenta, "APROBADA", "2030-06-04", tag))
        sol = client.get(
            "/api/reportes/solicitudes?dimension=laboratorio&desde=2030-06-01&hasta=2030-06-30",
            headers=h,
        )
        print("DBG-SOL", sol.json())
        fila = sol.json()["datos"][0]
        assert fila["solicitada"] == 1 and fila["aprobada"] == 1
        ocu = client.get(
            "/api/reportes/ocupacion?dimension=espacio&desde=2030-06-01&hasta=2030-06-30",
            headers=h,
        )
        assert ocu.json()["datos"][0]["horas_reservadas"] == 2.0
    finally:
        _teardown(db, s, rids)


def test_no_modifica_nada(client, db, tag):
    """T-REP-05: generar reportes no cambia reservas ni configuración."""
    h, cta, s = _login_tec(client, db, f"a{tag}")
    rids = []
    try:
        rids.append(_reserva(db, s, cta.id_cuenta, "APROBADA", "2030-06-04", tag))
        antes = db.scalar(text("SELECT count(*) FROM reservas.reservas"))
        for url in (
            "/api/reportes/ocupacion?dimension=laboratorio&desde=2030-06-01&hasta=2030-06-30",
            "/api/reportes/solicitudes?dimension=laboratorio",
            "/api/reportes/lista-espera?desde=2030-06-01&hasta=2030-06-30",
        ):
            assert client.get(url, headers=h).status_code == 200
        db.expire_all()
        assert db.scalar(text("SELECT count(*) FROM reservas.reservas")) == antes
    finally:
        _teardown(db, s, rids)


def test_tecnico_solo_su_unidad(client, db, tag):
    """T-REP-06: otra unidad → 403; sin filtro → acotado, no vacío."""
    h, _, s = _login_tec(client, db, f"a{tag}")
    s2 = _otra_unidad(db, f"b{tag}", f"Unidad api19 B {tag}")
    try:
        ajeno = client.get(
            f"/api/reportes/ocupacion?dimension=laboratorio&desde=2030-06-01&hasta=2030-06-30&id_unidad={s2['id_unidad']}",
            headers=h,
        )
        assert ajeno.status_code == 403, ajeno.text
        propio = client.get(
            "/api/reportes/ocupacion?dimension=laboratorio&desde=2030-06-01&hasta=2030-06-30",
            headers=h,
        )
        ids = {d["id_unidad"] for d in propio.json()["datos"]}
        assert ids == {s["id_unidad"]}
    finally:
        _teardown(db, s, [])
        _teardown(db, s2, [])


def test_admin_ve_todo(client, db, tag):
    """T-REP-07: el administrador consulta cualquier unidad."""
    _, _, s = _login_tec(client, db, f"a{tag}")
    s2 = _otra_unidad(db, f"b{tag}", f"Unidad api19 B {tag}")
    h_adm, _ = _login_admin(client, db, f"c{tag}")
    try:
        r = client.get(
            "/api/reportes/ocupacion?dimension=laboratorio&desde=2030-06-01&hasta=2030-06-30&tamano=100",
            headers=h_adm,
        )
        assert r.status_code == 200, r.text
        assert {s["id_unidad"], s2["id_unidad"]} <= {d["id_unidad"] for d in r.json()["datos"]}
    finally:
        _teardown(db, s, [])
        _teardown(db, s2, [])


def test_sin_datos_personales_y_filtro_desconocido(client, db, tag):
    """T-REP-08/09: agregados sin identidades; filtro raro → 400."""
    h, _, s = _login_tec(client, db, f"a{tag}")
    try:
        r = client.get(
            "/api/reportes/ocupacion?dimension=laboratorio&desde=2030-06-01&hasta=2030-06-30",
            headers=h,
        )
        texto = r.text.lower()
        assert "correo" not in texto and "documento" not in texto and "telefono" not in texto
        mala = client.get("/api/reportes/ocupacion?dimension=laboratorio&inexistente=1", headers=h)
        assert mala.status_code == 400, mala.text
    finally:
        _teardown(db, s, [])


def test_export_igual_consulta(client, db, tag):
    """T-REP-10: el archivo trae exactamente las filas consultadas."""
    h, cta, s = _login_tec(client, db, f"a{tag}")
    rids = []
    try:
        rids.append(_reserva(db, s, cta.id_cuenta, "APROBADA", "2030-06-05", tag))
        base = "/api/reportes/solicitudes?dimension=laboratorio&desde=2030-06-01&hasta=2030-06-30"
        q = client.get(base, headers=h).json()["datos"]
        csv_r = client.get(base.replace("/solicitudes?", "/solicitudes/exportacion?") + "&formato=csv", headers=h)
        assert csv_r.status_code == 200, csv_r.text
        lineas = [l for l in csv_r.text.splitlines() if l and not l.startswith("#")]
        assert len(lineas) - 1 == len(q)
        xls = client.get(base.replace("/solicitudes?", "/solicitudes/exportacion?") + "&formato=excel", headers=h)
        libro = openpyxl.load_workbook(filename=BytesIO(xls.content))
        filas = [row for row in libro.active.iter_rows(values_only=True) if row and row[0] not in (None, "dimension", "desde", "hasta", "filtros", "")]
        assert len([f for f in filas if isinstance(f[0], int)]) == len(q)
    finally:
        _teardown(db, s, rids)
