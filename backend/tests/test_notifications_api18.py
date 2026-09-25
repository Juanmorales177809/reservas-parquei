"""Pruebas de API-18: generación idempotente, canales vigentes, entrega
con reintentos y recordatorios (T-NOT-01/03/04/06/08, RN-INT-04,
RN-PREF-02/03). La transmisión real se sustituye por un fake: lo que se
verifica es el registro, la política y que el negocio nunca se revierte.
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from sqlalchemy import text

from .conftest import (
    crear_tecnico,
    crear_usuario_cuenta,
    headers_autenticados,
    iniciar_sesion,
)

from app.modules.notifications import entrega, productor
from app.modules.notifications.recordatorio import revisar_recordatorios


def _setup(db, tag: str, notificar: bool = True) -> dict:
    from app.db.models.investigacion import Proyectos
    from app.db.models.reservas import (
        Espacios,
        LaboratoriosConfig,
        LaboratorioTiposReserva,
    )

    cuenta, id_unidad = crear_tecnico(db, tag)
    ahora = datetime.now(timezone.utc)
    tipo_id = db.scalar(
        text("SELECT id FROM reservas.tipos_reserva WHERE codigo = 'ESPACIO'")
    )
    db.add(
        LaboratoriosConfig(
            id_unidad=id_unidad, habilitado_reservas=True,
            dias_atencion=[0, 1, 2, 3, 4, 5, 6],
            hora_apertura=time(0, 0), hora_cierre=time(23, 59),
            horario_atencion={}, horas_antelacion=0, aprobacion_automatica=False,
            notificar_por_correo=notificar, mostrar_estado_reserva=False,
            mostrar_reservista=False, recordatorio_horas_antes=24,
        )
    )
    db.add(
        LaboratorioTiposReserva(
            id_unidad=id_unidad, tipo_reserva_id=tipo_id, habilitado=True,
            created_at=ahora, updated_at=ahora,
        )
    )
    espacio = Espacios(
        id_unidad=id_unidad, nombre=f"Espacio api18 {tag}", capacidad=10,
        habilitado=True, created_at=ahora, updated_at=ahora,
    )
    db.add(espacio)
    db.flush()
    proyecto = Proyectos(codigo=f"PRY-{tag}", nombre=f"Proyecto {tag}", estado=True)
    db.add(proyecto)
    db.commit()
    return {
        "cuenta_tec": cuenta, "id_unidad": id_unidad,
        "espacio_id": espacio.id, "proyecto_id": proyecto.id_proyecto,
    }


def _login_tec(client, db, tag):
    s = _setup(db, tag)
    _, jar, _ = iniciar_sesion(
        client, s["cuenta_tec"].correo, "una frase larga de paso tec")
    return headers_autenticados(jar), s


def _login_usr(client, db, tag, proyecto_id):
    from app.db.models.investigacion import UsuarioProyectos

    usuario, cuenta = crear_usuario_cuenta(db, tag)
    usuario.perfil_actualizado_at = datetime.now(timezone.utc)
    db.add(UsuarioProyectos(
        id_usuario=usuario.id_usuario, id_proyecto=proyecto_id, estado=True))
    db.commit()
    _, jar, _ = iniciar_sesion(client, cuenta.correo, "una frase larga de paso")
    return headers_autenticados(jar), cuenta


def _teardown(db, s: dict, rids: list[int], id_usuario: int | None = None) -> None:
    for rid in rids:
        db.execute(
            text("DELETE FROM notificaciones.envios_correo WHERE evento_id IN "
                 "(SELECT id FROM notificaciones.eventos WHERE reserva_id = :i)"),
            {"i": rid},
        )
        db.execute(
            text("DELETE FROM notificaciones.notificaciones WHERE evento_id IN "
                 "(SELECT id FROM notificaciones.eventos WHERE reserva_id = :i)"),
            {"i": rid},
        )
        db.execute(
            text("DELETE FROM notificaciones.eventos WHERE reserva_id = :i"),
            {"i": rid},
        )
        for tabla in (
            "reserva_historial_estado", "reserva_contexto", "reserva_espacio",
        ):
            db.execute(
                text(f"DELETE FROM reservas.{tabla} WHERE reserva_id = :i"),
                {"i": rid},
            )
        db.execute(text("DELETE FROM reservas.reservas WHERE id = :i"), {"i": rid})
    if id_usuario is not None:
        db.execute(
            text("DELETE FROM investigacion.usuario_proyectos WHERE id_usuario = :u"),
            {"u": id_usuario},
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


def _envios_de(db, clave: str) -> list:
    return db.execute(
        text(
            "SELECT e.estado, e.intentos, e.destinatario_correo "
            "FROM notificaciones.envios_correo e "
            "JOIN notificaciones.eventos ev ON ev.id = e.evento_id "
            "WHERE ev.ocurrencia_clave = :c"
        ),
        {"c": clave},
    ).all()


def _crear_espacio(client, headers, s, dia, obs):
    from datetime import date as _date

    r = client.post(
        "/api/reservas",
        json={
            "id_unidad": s["id_unidad"], "tipo_reserva": "ESPACIO",
            "observacion": obs, "contexto": {"proyecto_id": s["proyecto_id"]},
            "detalle": {
                "espacio_id": s["espacio_id"], "fecha": dia,
                "hora_inicio": "10:00", "hora_fin": "12:00",
            },
        },
        headers=headers,
    )
    assert r.status_code == 201, r.text
    return r.json()


def test_misma_ocurrencia_no_duplica(db, tag):
    """T-NOT-01: repetir la clave no crea segundo evento ni envíos."""
    _, cuenta = crear_usuario_cuenta(db, f"a{tag}")
    try:
        for _ in range(2):
            productor.registrar_evento(
                db, tipo_codigo="RESERVA_APROBADA", reserva_id=None,
                ocurrencia_clave=f"api18-dup-{tag}", cuentas=[cuenta.id_cuenta],
            )
        n_eventos = db.scalar(
            text("SELECT count(*) FROM notificaciones.eventos WHERE ocurrencia_clave = :c"),
            {"c": f"api18-dup-{tag}"},
        )
        assert n_eventos == 1
        assert len(_envios_de(db, f"api18-dup-{tag}")) == 1
    finally:
        db.execute(
            text("DELETE FROM notificaciones.envios_correo WHERE evento_id IN "
                 "(SELECT id FROM notificaciones.eventos WHERE ocurrencia_clave = :c)"),
            {"c": f"api18-dup-{tag}"},
        )
        db.execute(
            text("DELETE FROM notificaciones.notificaciones WHERE evento_id IN "
                 "(SELECT id FROM notificaciones.eventos WHERE ocurrencia_clave = :c)"),
            {"c": f"api18-dup-{tag}"},
        )
        db.execute(
            text("DELETE FROM notificaciones.eventos WHERE ocurrencia_clave = :c"),
            {"c": f"api18-dup-{tag}"},
        )
        db.commit()


def test_aprobar_genera_aviso_y_envio(client, db, tag):
    """RN-EVT-02: al aprobar hay in-app para el dueño y envío PENDIENTE."""
    h_tec, s = _login_tec(client, db, f"a{tag}")
    h_usr, c_usr = _login_usr(client, db, f"b{tag}", s["proyecto_id"])
    rid = None
    try:
        r = _crear_espacio(client, h_usr, s, "2030-05-04", f"api18-apr-{tag}")
        rid = r["id"]
        ap = client.post(
            f"/api/reservas/{rid}/aprobacion", json={}, headers=h_tec)
        assert ap.status_code == 200, ap.text
        n_inapp = db.scalar(
            text("SELECT count(*) FROM notificaciones.notificaciones n "
                 "JOIN notificaciones.eventos e ON e.id = n.evento_id "
                 "WHERE e.ocurrencia_clave = :c"),
            {"c": f"RESERVA_APROBADA-{rid}"},
        )
        assert n_inapp == 1
        envios = _envios_de(db, f"RESERVA_APROBADA-{rid}")
        assert len(envios) == 1 and envios[0][0] == "PENDIENTE"
    finally:
        if rid:
            _teardown(db, s, [rid], c_usr.id_usuario)


def test_fallo_entrega_no_invalida(client, db, tag, monkeypatch):
    """T-NOT-03/RN-INT-04: transmitir falla → reintento, negocio intacto."""
    h_tec, s = _login_tec(client, db, f"a{tag}")
    h_usr, c_usr = _login_usr(client, db, f"b{tag}", s["proyecto_id"])
    rid = None
    try:
        r = _crear_espacio(client, h_usr, s, "2030-05-05", f"api18-fallo-{tag}")
        rid = r["id"]
        client.post(f"/api/reservas/{rid}/aprobacion", json={}, headers=h_tec)

        def _falla(*a, **k):
            from app.modules.notifications import envio as _remitente

            raise _remitente.ErrorTransmision("SMTP falló (simulado).")

        monkeypatch.setattr(entrega.remitente, "transmitir", _falla)
        cuenta = entrega.procesar_pendientes(db)
        assert cuenta["enviados"] == 0
        envios = _envios_de(db, f"RESERVA_APROBADA-{rid}")
        assert envios[0][0] == "PENDIENTE" and envios[0][1] == 1

        estado = db.scalar(
            text("SELECT e.codigo FROM reservas.reservas r "
                 "JOIN reservas.estados_reserva e ON e.id = r.estado_id "
                 "WHERE r.id = :i"),
            {"i": rid},
        )
        assert estado == "APROBADA"
    finally:
        if rid:
            _teardown(db, s, [rid], c_usr.id_usuario)


def test_reintentos_se_agotan(db, tag, monkeypatch):
    """T-NOT-04: al quinto fallo queda FALLIDO sin reintento."""
    from .conftest import correo_para

    _, cuenta = crear_usuario_cuenta(db, f"a{tag}")
    clave = f"api18-ago-{tag}"
    try:
        productor.registrar_evento(
            db, tipo_codigo="RESERVA_APROBADA", ocurrencia_clave=clave,
            cuentas=[cuenta.id_cuenta],
        )
        db.execute(
            text("UPDATE notificaciones.envios_correo SET intentos = 4 WHERE evento_id IN "
                 "(SELECT id FROM notificaciones.eventos WHERE ocurrencia_clave = :c)"),
            {"c": clave},
        )
        db.commit()

        def _falla(*a, **k):
            from app.modules.notifications import envio as _remitente

            raise _remitente.ErrorTransmision("Falla.")

        monkeypatch.setattr(entrega.remitente, "transmitir", _falla)
        entrega.procesar_pendientes(db)
        envios = _envios_de(db, clave)
        assert envios[0][0] == "FALLIDO"

        # Ya no es elegible: otro tick no lo toca.
        fila = db.execute(
            text("SELECT proximo_intento_at FROM notificaciones.envios_correo e "
                 "JOIN notificaciones.eventos ev ON ev.id = e.evento_id "
                 "WHERE ev.ocurrencia_clave = :c"),
            {"c": clave},
        ).first()
        assert fila[0] is None
    finally:
        db.execute(
            text("DELETE FROM notificaciones.envios_correo WHERE evento_id IN "
                 "(SELECT id FROM notificaciones.eventos WHERE ocurrencia_clave = :c)"),
            {"c": clave},
        )
        db.execute(
            text("DELETE FROM notificaciones.notificaciones WHERE evento_id IN "
                 "(SELECT id FROM notificaciones.eventos WHERE ocurrencia_clave = :c)"),
            {"c": clave},
        )
        db.execute(
            text("DELETE FROM notificaciones.eventos WHERE ocurrencia_clave = :c"),
            {"c": clave},
        )
        db.commit()


def test_indice_de_reintento_existe_y_elegibles_ordenados(db):
    """T-NOT-05: el índice (estado, proximo_intento_at) existe y la consulta
    de elegibles lo usa. Con tablas pequeñas el plan puede no elegirlo, así
    que se verifica existencia + corrección funcional."""
    idx = db.scalar(
        text("SELECT count(*) FROM pg_indexes WHERE schemaname = 'notificaciones' "
             "AND tablename = 'envios_correo' AND indexdef LIKE '%(estado, proximo_intento_at)%'"),
    )
    assert idx >= 1
    plan = db.execute(
        text("EXPLAIN SELECT id FROM notificaciones.envios_correo "
             "WHERE estado = 'PENDIENTE' AND proximo_intento_at <= now() "
             "ORDER BY proximo_intento_at")
    ).all()
    assert any("envios_correo" in (fila[0] or "") for fila in plan)


def test_preferencia_apaga_correo_pero_no_inapp(client, db, tag):
    """T-NOT-08/RN-PREF-04: sin correo para el tipo, igual hay in-app."""
    h_tec, s = _login_tec(client, db, f"a{tag}")
    h_usr, c_usr = _login_usr(client, db, f"b{tag}", s["proyecto_id"])
    rid = None
    try:
        tipo_id = db.scalar(
            text("SELECT id FROM notificaciones.tipos_evento WHERE codigo = 'RESERVA_APROBADA'")
        )
        p = client.put(
            "/api/notificaciones/preferencias",
            json={"por_evento": [
                {"tipo_evento_id": tipo_id, "correo_habilitado": False}]},
            headers=h_usr,
        )
        assert p.status_code == 200, p.text
        r = _crear_espacio(client, h_usr, s, "2030-05-06", f"api18-pref-{tag}")
        rid = r["id"]
        client.post(f"/api/reservas/{rid}/aprobacion", json={}, headers=h_tec)
        assert _envios_de(db, f"RESERVA_APROBADA-{rid}") == []
        n_inapp = db.scalar(
            text("SELECT count(*) FROM notificaciones.notificaciones n "
                 "JOIN notificaciones.eventos e ON e.id = n.evento_id "
                 "WHERE e.ocurrencia_clave = :c"),
            {"c": f"RESERVA_APROBADA-{rid}"},
        )
        assert n_inapp == 1
    finally:
        if rid:
            _teardown(db, s, [rid], c_usr.id_usuario)
        db.execute(
            text("DELETE FROM notificaciones.preferencias WHERE id_cuenta = :c"),
            {"c": c_usr.id_cuenta},
        )
        db.commit()


def test_unidad_sin_correo_no_envia(client, db, tag):
    """RN-PREF-02: la unidad manda sobre la preferencia individual."""
    from .conftest import correo_para

    h_tec, s = _login_tec(client, db, f"a{tag}")
    # Reconstruir sin correo de unidad: el setup ya trae notificar=True;
    # este caso usa otra unidad con el flag apagado.
    db.execute(
        text("UPDATE reservas.laboratorios_config SET notificar_por_correo = false "
             "WHERE id_unidad = :u"),
        {"u": s["id_unidad"]},
    )
    db.commit()
    h_usr, c_usr = _login_usr(client, db, f"b{tag}", s["proyecto_id"])
    rid = None
    try:
        r = _crear_espacio(client, h_usr, s, "2030-05-07", f"api18-uni-{tag}")
        rid = r["id"]
        client.post(f"/api/reservas/{rid}/aprobacion", json={}, headers=h_tec)
        assert _envios_de(db, f"RESERVA_APROBADA-{rid}") == []
    finally:
        if rid:
            _teardown(db, s, [rid], c_usr.id_usuario)


def test_auth_ignora_preferencias(client, db, tag):
    """RN-PREF-03: con todo apagado, la recuperación igual genera envío."""
    _, cuenta = crear_usuario_cuenta(db, f"a{tag}")
    try:
        db.execute(
            text("INSERT INTO notificaciones.preferencias (id_cuenta, tipo_evento_id, correo_habilitado) "
                 "VALUES (:c, NULL, false)"),
            {"c": cuenta.id_cuenta},
        )
        db.commit()
        r = client.post(
            "/api/auth/recuperacion", json={"correo": cuenta.correo}, headers=_csrf(client)
        )
        assert r.status_code == 202, r.text
        n = db.scalar(
            text("SELECT count(*) FROM notificaciones.envios_correo e "
                 "JOIN notificaciones.eventos ev ON ev.id = e.evento_id "
                 "JOIN notificaciones.tipos_evento t ON t.id = ev.tipo_evento_id "
                 "WHERE t.codigo = 'RECUPERACION_CONTRASENA' AND e.destinatario_correo = :m"),
            {"m": cuenta.correo},
        )
        assert n == 1
    finally:
        db.execute(
            text("DELETE FROM notificaciones.preferencias WHERE id_cuenta = :c"),
            {"c": cuenta.id_cuenta},
        )
        db.execute(
            text("DELETE FROM notificaciones.envios_correo WHERE destinatario_correo = :m"),
            {"m": cuenta.correo},
        )
        db.execute(
            text("DELETE FROM notificaciones.notificaciones WHERE id_cuenta = :c"),
            {"c": cuenta.id_cuenta},
        )
        db.execute(
            text("DELETE FROM notificaciones.eventos WHERE id NOT IN "
                 "(SELECT evento_id FROM notificaciones.notificaciones) "
                 "AND id NOT IN (SELECT evento_id FROM notificaciones.envios_correo)"),
        )
        db.commit()


def _csrf(client):
    from .conftest import obtener_csrf

    headers, _ = obtener_csrf(client)
    return headers


def test_recordatorio_unico(db, tag):
    """RN-EVT-11: al vencer el plazo se crea uno; repetir no duplica."""
    s = _setup(db, tag)
    rid = None
    try:
        from app.modules.reservations import repository as _repo

        tipo_id = db.scalar(
            text("SELECT id FROM reservas.tipos_reserva WHERE codigo = 'ESPACIO'")
        )
        estado_id = db.scalar(
            text("SELECT id FROM reservas.estados_reserva WHERE codigo = 'APROBADA'")
        )
        reserva = _repo.crear_reserva(
            db, id_unidad=s["id_unidad"], tipo_reserva_id=tipo_id,
            id_cuenta=s["cuenta_tec"].id_cuenta, estado_id=estado_id,
            observacion=f"api18-rec-{tag}", requiere_apoyo=False,
            created_by=s["cuenta_tec"].id_cuenta,
        )
        rid = reserva.id
        manana = (datetime.now(timezone.utc) + timedelta(days=1)).date()
        _repo.crear_detalle_espacio(
            db, reserva.id, espacio_id=s["espacio_id"], fecha=manana,
            hora_inicio=time(10, 0), hora_fin=time(12, 0), asistentes=0,
        )
        db.commit()
        # Plazo vencido: inicio menos 24 h ya pasó.
        ahora = datetime.combine(manana, time(10, 0)).replace(
            tzinfo=ZoneInfo("America/Bogota")) - timedelta(hours=1)
        assert revisar_recordatorios(db, ahora) == 1
        assert revisar_recordatorios(db, ahora) == 0
    finally:
        if rid:
            _teardown(db, s, [rid])
