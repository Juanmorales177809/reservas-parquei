"""Pruebas de API-20: GET /api/reportes/resumen (T-REP-11..15).

Solo lectura (RN-REP-02): agrega demanda (RN-OCU-05) y uso (RN-OCU-04),
compara con el periodo previo, `null` sin horario (RN-OCU-06) y ámbito
por rol (RN-AMB-01/02).
"""

from __future__ import annotations

from datetime import date, datetime, time, timezone

from sqlalchemy import text

from .conftest import (
    crear_admin,
    crear_tecnico,
    crear_usuario_cuenta,
    headers_autenticados,
    iniciar_sesion,
)

from app.db.models.reservas import Espacios, LaboratoriosConfig, LaboratoriosConfigHistorico
from app.modules.reservations import repository as repo


def _setup(db, tag: str, id_unidad: int, con_horario: bool = True) -> dict:
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
        id_unidad=id_unidad, nombre=f"Espacio api20 {tag}", capacidad=10,
        habilitado=True, created_at=ahora, updated_at=ahora,
    )
    db.add(espacio)
    db.commit()
    return {"id_unidad": id_unidad, "espacio_id": espacio.id}


def _reserva(db, s: dict, cuenta_id: int, estado: str, dia: str, tag: str) -> int:
    tipo_id = db.scalar(text("SELECT id FROM reservas.tipos_reserva WHERE codigo = 'ESPACIO'"))
    estado_id = db.scalar(
        text("SELECT id FROM reservas.estados_reserva WHERE codigo = :e"), {"e": estado})
    r = repo.crear_reserva(
        db, id_unidad=s["id_unidad"], tipo_reserva_id=tipo_id, id_cuenta=cuenta_id,
        estado_id=estado_id, observacion=f"api20-{tag}", requiere_apoyo=False,
        created_by=cuenta_id,
    )
    repo.crear_detalle_espacio(
        db, r.id, espacio_id=s["espacio_id"], fecha=date.fromisoformat(dia),
        hora_inicio=time(10, 0), hora_fin=time(12, 0), asistentes=0,
    )
    db.commit()
    return r.id


def _reserva_lista(db, s: dict, cuenta_id: int, estado: str, horas: float | None, tag: str) -> int:
    tipo_id = db.scalar(text("SELECT id FROM reservas.tipos_reserva WHERE codigo = 'LISTA_ESPERA'"))
    estado_id = db.scalar(
        text("SELECT id FROM reservas.estados_reserva WHERE codigo = :e"), {"e": estado})
    r = repo.crear_reserva(
        db, id_unidad=s["id_unidad"], tipo_reserva_id=tipo_id, id_cuenta=cuenta_id,
        estado_id=estado_id, observacion=f"api20-le-{tag}", requiere_apoyo=False,
        created_by=cuenta_id,
    )
    detalle = repo.crear_detalle_lista_espera(db, r.id, descripcion_necesidad="api20-le")
    detalle.horas_ejecucion = horas
    db.commit()
    return r.id


def _teardown(db, s: dict, rids: list[int]) -> None:
    for rid in rids:
        for tabla in ("reserva_historial_estado", "reserva_contexto", "reserva_espacio",
                      "reserva_lista_espera_formulario", "reserva_lista_espera"):
            db.execute(text(f"DELETE FROM reservas.{tabla} WHERE reserva_id = :i"), {"i": rid})
        db.execute(text("DELETE FROM reservas.reservas WHERE id = :i"), {"i": rid})
    db.execute(text("DELETE FROM reservas.espacios WHERE id_unidad = :u"), {"u": s["id_unidad"]})
    db.execute(
        text("DELETE FROM reservas.laboratorios_config_historico WHERE id_unidad = :u"),
        {"u": s["id_unidad"]},
    )
    db.execute(
        text("DELETE FROM reservas.laboratorios_config WHERE id_unidad = :u"),
        {"u": s["id_unidad"]},
    )
    db.commit()


def _login_tec(client, db, tag):
    cuenta, id_unidad = crear_tecnico(db, tag)
    s = _setup(db, tag, id_unidad)
    _, jar, _ = iniciar_sesion(client, cuenta.correo, "una frase larga de paso tec")
    return headers_autenticados(jar), cuenta, s


def _login_admin(client, db, tag):
    cuenta = crear_admin(db, tag)
    _, jar, _ = iniciar_sesion(client, cuenta.correo, "una frase larga de paso admin")
    return headers_autenticados(jar), cuenta


def test_resumen_200_con_seis_estados(client, db, tag):
    """T-REP-11: 200 con las seis secciones y los seis estados siempre presentes."""
    h, cta, s = _login_tec(client, db, f"a{tag}")
    rids: list[int] = []
    try:
        rids.append(_reserva(db, s, cta.id_cuenta, "SOLICITADA", "2030-06-03", tag))
        rids.append(_reserva(db, s, cta.id_cuenta, "APROBADA", "2030-06-04", tag))
        r = client.get("/api/reportes/resumen?desde=2030-06-01&hasta=2030-06-30", headers=h)
        assert r.status_code == 200, r.text
        cuerpo = r.json()
        assert set(cuerpo) == {
            "resumen", "indicadores", "por_estado", "por_fecha",
            "por_laboratorio", "recursos_mas_reservados", "ocupacion_dia_hora",
        }
        assert set(cuerpo["por_estado"]) == {
            "solicitada", "aprobada", "rechazada", "en_ejecucion", "finalizada", "cancelada",
        }
        assert cuerpo["por_estado"]["solicitada"] == 1
        assert cuerpo["indicadores"]["solicitadas"] == 1
        assert cuerpo["indicadores"]["reservas"]["actual"] == 2
        assert cuerpo["resumen"]["desde_previo"] == "2030-05-02"
        assert cuerpo["resumen"]["hasta_previo"] == "2030-05-31"
        assert len(cuerpo["por_fecha"]) == 2
    finally:
        _teardown(db, s, rids)


def test_tecnico_acotado_a_su_unidad(client, db, tag):
    """T-REP-12: sin filtro ve solo la suya; la ajena responde 403."""
    from app.db.models.identidad import UnidadOrganizacional

    h, _, s = _login_tec(client, db, f"a{tag}")
    otra = UnidadOrganizacional(nombre=f"Otra api20 {tag}", tipo="LABORATORIO", estado=True)
    db.add(otra)
    db.flush()
    s2 = _setup(db, f"b{tag}", otra.id_unidad)
    try:
        propio = client.get("/api/reportes/resumen?desde=2030-06-01&hasta=2030-06-30", headers=h)
        assert propio.status_code == 200, propio.text
        assert {f["id_unidad"] for f in propio.json()["por_laboratorio"]} == {s["id_unidad"]}
        ajeno = client.get(
            f"/api/reportes/resumen?desde=2030-06-01&hasta=2030-06-30&id_unidad={s2['id_unidad']}",
            headers=h,
        )
        assert ajeno.status_code == 403, ajeno.text
        assert ajeno.json()["error"]["codigo"] == "NO_AUTORIZADO"
    finally:
        _teardown(db, s, [])
        _teardown(db, s2, [])


def test_periodo_invalido_422(client, db, tag):
    """T-REP-13: sin periodo o invertido responde 422 VALIDACION."""
    h, _, s = _login_tec(client, db, f"a{tag}")
    try:
        sin = client.get("/api/reportes/resumen", headers=h)
        assert sin.status_code == 422, sin.text
        assert sin.json()["error"]["codigo"] == "VALIDACION"
        invertido = client.get(
            "/api/reportes/resumen?desde=2030-06-30&hasta=2030-06-01", headers=h)
        assert invertido.status_code == 422, invertido.text
    finally:
        _teardown(db, s, [])


def test_sin_permiso_403(client, db, tag):
    """T-REP-14: un USUARIO (sin reportes.consultar) recibe 403."""
    _, _, s = _login_tec(client, db, f"a{tag}")
    _, cta_usr = crear_usuario_cuenta(db, f"u{tag}")
    _, jar, _ = iniciar_sesion(client, cta_usr.correo, "una frase larga de paso")
    try:
        r = client.get(
            "/api/reportes/resumen?desde=2030-06-01&hasta=2030-06-30",
            headers=headers_autenticados(jar),
        )
        assert r.status_code == 403, r.text
        assert r.json()["error"]["codigo"] == "NO_AUTORIZADO"
    finally:
        _teardown(db, s, [])


def test_lista_finalizada_suma_horas_por_creacion(client, db, tag):
    """T-REP-16: horas_ejecucion de lista FINALIZADA suman por fecha de creación."""
    from datetime import timedelta

    h, cta, s = _login_tec(client, db, f"a{tag}")
    hoy = date.today()
    desde = (hoy - timedelta(days=60)).isoformat()
    hasta = (hoy + timedelta(days=1)).isoformat()
    rids: list[int] = []
    try:
        rids.append(_reserva_lista(db, s, cta.id_cuenta, "FINALIZADA", 4.5, tag))
        rids.append(_reserva_lista(db, s, cta.id_cuenta, "SOLICITADA", 9.0, tag))
        r = client.get(f"/api/reportes/resumen?desde={desde}&hasta={hasta}", headers=h)
        assert r.status_code == 200, r.text
        cuerpo = r.json()
        assert cuerpo["indicadores"]["horas_reservadas"]["actual"] == 4.5
        assert cuerpo["indicadores"]["horas_reservadas"]["previo"] == 0
        fila = cuerpo["por_laboratorio"][0]
        assert fila["horas_reservadas"] == 4.5
        # Las horas de lista no usan el horario: no entran en la ocupación.
        assert cuerpo["indicadores"]["porcentaje_ocupacion"]["actual"] == 0
        assert fila["porcentaje_ocupacion"] == 0
        # Sin fecha, recursos ni reloj: esas secciones no cambian.
        assert cuerpo["por_fecha"] == []
        assert cuerpo["recursos_mas_reservados"] == []
        assert cuerpo["ocupacion_dia_hora"] == []
    finally:
        _teardown(db, s, rids)


def test_porcentaje_null_sin_horario(client, db, tag):
    """T-REP-15: sin histórico, horas sí y porcentaje null, nunca cero."""
    h_adm, cta_adm = _login_admin(client, db, f"c{tag}")
    _, _, s = _login_tec(client, db, f"a{tag}")
    from app.db.models.identidad import UnidadOrganizacional

    otra = UnidadOrganizacional(nombre=f"SinHor api20 {tag}", tipo="LABORATORIO", estado=True)
    db.add(otra)
    db.flush()
    s2 = _setup(db, f"b{tag}", otra.id_unidad, con_horario=False)
    rids: list[int] = []
    try:
        rids.append(_reserva(db, s2, cta_adm.id_cuenta, "APROBADA", "2030-06-02", tag))
        r = client.get(
            f"/api/reportes/resumen?desde=2030-06-01&hasta=2030-06-30&id_unidad={s2['id_unidad']}",
            headers=h_adm,
        )
        assert r.status_code == 200, r.text
        fila = r.json()["por_laboratorio"][0]
        assert fila["horas_reservadas"] == 2.0
        assert fila["porcentaje_ocupacion"] is None
        assert r.json()["indicadores"]["porcentaje_ocupacion"]["actual"] is None
    finally:
        _teardown(db, s, [])
        _teardown(db, s2, rids)
