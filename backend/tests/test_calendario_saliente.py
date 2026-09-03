# -*- coding: utf-8 -*-
"""Pruebas del outbox de eventos de Outlook Calendar
(`app/services/calendario.py`) y su enganche en los eventos de reserva
(`app/services/reservas.py`, 2026-09-03).

Nunca le pegan a Graph real -- `crear_evento_calendario_graph`/
`actualizar_evento_calendario_graph`/`cancelar_evento_calendario_graph` se
reemplazan por dobles (mismo criterio que `test_correo_saliente.py` con
`enviar_graph`).
"""

import pytest

from app.config import settings
from app.models import EventoCalendarioSaliente, Reserva
from app.services import calendario as calendario_service
from app.services import email as email_service

from tests.conftest import (
    cookies_para,
    crear_laboratorio,
    crear_recurso,
    crear_usuario,
    fecha_habilitada,
    payload_reserva,
)


def _setup(db, *, nombre_espacio="Sala Calendario"):
    laboratorio = crear_laboratorio(db, nombre=nombre_espacio)
    usuario = crear_usuario(
        db,
        username=f"user_{nombre_espacio.replace(' ', '')}",
        email=f"user-{nombre_espacio.replace(' ', '')}@example.com",
    )
    gestor = crear_usuario(
        db,
        username=f"gestor_{nombre_espacio.replace(' ', '')}",
        email=f"gestor-{nombre_espacio.replace(' ', '')}@example.com",
        rol="gestor",
        laboratorio_id=laboratorio.id,
    )
    recurso = crear_recurso(db, laboratorio=laboratorio, usuario=usuario)
    return usuario, gestor, laboratorio, recurso


@pytest.fixture()
def calendario_habilitado(monkeypatch):
    """Activa el procesamiento (contra dobles de Graph, nunca la red real).

    `email_enabled=True` es el mismo interruptor que gatea el outbox de
    CORREO -- sin mockear también `_enviar_smtp`, cada aprobación de esta
    suite intentaría una conexión SMTP real (falla lenta contra un host
    que no existe) solo por el efecto secundario de tener el calendario
    habilitado."""
    monkeypatch.setattr(settings, "email_enabled", True)
    monkeypatch.setattr(email_service, "_enviar_smtp", lambda *a, **kw: None)
    llamadas = {"crear": [], "actualizar": [], "cancelar": []}

    def _crear_falso(*, asunto, cuerpo, inicio, fin, ubicacion, asistentes):
        llamadas["crear"].append(
            {"asunto": asunto, "cuerpo": cuerpo, "inicio": inicio, "fin": fin, "ubicacion": ubicacion, "asistentes": asistentes}
        )
        return "evento-falso-1"

    def _actualizar_falso(event_id, *, inicio, fin):
        llamadas["actualizar"].append({"event_id": event_id, "inicio": inicio, "fin": fin})

    def _cancelar_falso(event_id, *, comentario=""):
        llamadas["cancelar"].append({"event_id": event_id, "comentario": comentario})

    monkeypatch.setattr(calendario_service, "crear_evento_calendario_graph", _crear_falso)
    monkeypatch.setattr(calendario_service, "actualizar_evento_calendario_graph", _actualizar_falso)
    monkeypatch.setattr(calendario_service, "cancelar_evento_calendario_graph", _cancelar_falso)
    return llamadas


class TestEnganchesDeReserva:
    """Integración vía API: los mismos eventos que ya generan/quitan el
    adjunto `.ics` deben encolar/cancelar el evento de calendario."""

    def test_aprobacion_automatica_encola_y_procesa_accion_crear(self, client, db, calendario_habilitado):
        laboratorio = crear_laboratorio(db, nombre="Sala Cal Auto")
        laboratorio.aprobacion_automatica = True
        db.commit()
        usuario = crear_usuario(db, username="user_cal_auto", email="user_cal_auto@example.com")
        recurso = crear_recurso(db, laboratorio=laboratorio, usuario=usuario)

        respuesta = client.post(
            "/reservas", json=payload_reserva(recurso.id, fecha_habilitada()), headers=cookies_para(usuario)
        )
        assert respuesta.status_code == 201
        assert respuesta.json()["estado"] == "aprobada"

        evento = db.query(EventoCalendarioSaliente).one()
        assert evento.accion == "crear"
        assert evento.estado == "enviado"
        assert evento.graph_event_id == "evento-falso-1"
        reserva = db.query(Reserva).filter(Reserva.id == respuesta.json()["id"]).one()
        assert reserva.graph_event_id == "evento-falso-1"
        asistentes_emails = {a[0] for a in calendario_habilitado["crear"][0]["asistentes"]}
        assert usuario.email in asistentes_emails

    def test_reserva_pendiente_no_encola_nada(self, client, db, calendario_habilitado):
        usuario, _, _, recurso = _setup(db, nombre_espacio="Sala Cal Pendiente")
        respuesta = client.post(
            "/reservas", json=payload_reserva(recurso.id, fecha_habilitada()), headers=cookies_para(usuario)
        )
        assert respuesta.status_code == 201
        assert respuesta.json()["estado"] == "esperando"
        assert db.query(EventoCalendarioSaliente).count() == 0

    def test_aprobar_reserva_pendiente_encola_y_procesa_accion_crear(self, client, db, calendario_habilitado):
        usuario, gestor, _, recurso = _setup(db, nombre_espacio="Sala Cal Aprobar")
        creada = client.post(
            "/reservas", json=payload_reserva(recurso.id, fecha_habilitada()), headers=cookies_para(usuario)
        ).json()

        aprobada = client.put(
            f"/reservas/{creada['id']}/estado", json={"nuevo_estado": "aprobada"}, headers=cookies_para(gestor)
        )
        assert aprobada.status_code == 200

        evento = db.query(EventoCalendarioSaliente).filter(EventoCalendarioSaliente.reserva_id == creada["id"]).one()
        assert evento.accion == "crear"
        assert evento.estado == "enviado"

    def test_rechazar_reserva_no_encola_nada(self, client, db, calendario_habilitado):
        usuario, gestor, _, recurso = _setup(db, nombre_espacio="Sala Cal Rechazo")
        creada = client.post(
            "/reservas", json=payload_reserva(recurso.id, fecha_habilitada()), headers=cookies_para(usuario)
        ).json()

        client.put(
            f"/reservas/{creada['id']}/estado",
            json={"nuevo_estado": "rechazada", "motivo": "No hay disponibilidad"},
            headers=cookies_para(gestor),
        )

        assert db.query(EventoCalendarioSaliente).count() == 0

    def test_usuario_cancela_reserva_aprobada_con_evento_encola_accion_cancelar(self, client, db, calendario_habilitado):
        usuario, gestor, _, recurso = _setup(db, nombre_espacio="Sala Cal Cancelar Usuario")
        creada = client.post(
            "/reservas", json=payload_reserva(recurso.id, fecha_habilitada()), headers=cookies_para(usuario)
        ).json()
        client.put(f"/reservas/{creada['id']}/estado", json={"nuevo_estado": "aprobada"}, headers=cookies_para(gestor))
        db.query(EventoCalendarioSaliente).delete()  # aislar el efecto de la cancelación
        db.commit()
        reserva = db.query(Reserva).filter(Reserva.id == creada["id"]).one()
        assert reserva.graph_event_id == "evento-falso-1"

        cancelada = client.put(f"/reservas/{creada['id']}/cancelar", headers=cookies_para(usuario))
        assert cancelada.status_code == 200

        evento = db.query(EventoCalendarioSaliente).one()
        assert evento.accion == "cancelar"
        assert evento.graph_event_id == "evento-falso-1"
        assert evento.estado == "enviado"
        assert calendario_habilitado["cancelar"][-1]["event_id"] == "evento-falso-1"

    def test_gestor_cancela_via_cambiar_estado_encola_accion_cancelar(self, client, db, calendario_habilitado):
        usuario, gestor, _, recurso = _setup(db, nombre_espacio="Sala Cal Cancelar Gestor")
        creada = client.post(
            "/reservas", json=payload_reserva(recurso.id, fecha_habilitada()), headers=cookies_para(usuario)
        ).json()
        client.put(f"/reservas/{creada['id']}/estado", json={"nuevo_estado": "aprobada"}, headers=cookies_para(gestor))
        db.query(EventoCalendarioSaliente).delete()
        db.commit()

        cancelada = client.put(
            f"/reservas/{creada['id']}/estado", json={"nuevo_estado": "cancelada"}, headers=cookies_para(gestor)
        )
        assert cancelada.status_code == 200

        evento = db.query(EventoCalendarioSaliente).one()
        assert evento.accion == "cancelar"
        assert evento.estado == "enviado"

    def test_eliminar_reserva_aprobada_con_evento_encola_accion_cancelar(self, client, db, calendario_habilitado):
        usuario, gestor, _, recurso = _setup(db, nombre_espacio="Sala Cal Eliminar")
        creada = client.post(
            "/reservas", json=payload_reserva(recurso.id, fecha_habilitada()), headers=cookies_para(usuario)
        ).json()
        client.put(f"/reservas/{creada['id']}/estado", json={"nuevo_estado": "aprobada"}, headers=cookies_para(gestor))
        db.query(EventoCalendarioSaliente).delete()
        db.commit()

        respuesta = client.delete(f"/reservas/{creada['id']}", headers=cookies_para(gestor))
        assert respuesta.status_code == 204

        evento = db.query(EventoCalendarioSaliente).one()
        assert evento.accion == "cancelar"
        assert evento.estado == "enviado"

    def test_eliminar_reserva_pendiente_sin_evento_no_encola_nada(self, client, db, calendario_habilitado):
        usuario, gestor, _, recurso = _setup(db, nombre_espacio="Sala Cal Eliminar Pendiente")
        creada = client.post(
            "/reservas", json=payload_reserva(recurso.id, fecha_habilitada()), headers=cookies_para(usuario)
        ).json()

        respuesta = client.delete(f"/reservas/{creada['id']}", headers=cookies_para(gestor))
        assert respuesta.status_code == 204
        assert db.query(EventoCalendarioSaliente).count() == 0

    def test_actualizar_reserva_aprobada_con_cambio_de_horario_encola_accion_actualizar(self, client, db, calendario_habilitado):
        usuario, gestor, _, recurso = _setup(db, nombre_espacio="Sala Cal Actualizar")
        creada = client.post(
            "/reservas", json=payload_reserva(recurso.id, fecha_habilitada()), headers=cookies_para(usuario)
        ).json()
        client.put(f"/reservas/{creada['id']}/estado", json={"nuevo_estado": "aprobada"}, headers=cookies_para(gestor))
        db.query(EventoCalendarioSaliente).delete()
        db.commit()

        respuesta = client.patch(
            f"/reservas/{creada['id']}",
            json={"hora_inicio": "11:00", "hora_fin": "13:00"},
            headers=cookies_para(gestor),
        )
        assert respuesta.status_code == 200

        # actualizar_reserva no llama a procesar_pendientes/procesar_eventos_...
        # (mismo criterio ya existente para el correo de Feature B) -- la fila
        # queda encolada, no procesada todavía.
        evento = db.query(EventoCalendarioSaliente).one()
        assert evento.accion == "actualizar"
        assert evento.graph_event_id == "evento-falso-1"
        assert evento.estado == "pendiente"

    def test_actualizar_reserva_sin_cambiar_horario_no_encola_nada(self, client, db, calendario_habilitado):
        usuario, gestor, _, recurso = _setup(db, nombre_espacio="Sala Cal Actualizar Sin Cambio")
        creada = client.post(
            "/reservas", json=payload_reserva(recurso.id, fecha_habilitada()), headers=cookies_para(usuario)
        ).json()
        client.put(f"/reservas/{creada['id']}/estado", json={"nuevo_estado": "aprobada"}, headers=cookies_para(gestor))
        db.query(EventoCalendarioSaliente).delete()
        db.commit()

        respuesta = client.patch(
            f"/reservas/{creada['id']}", json={"asistentes": 3}, headers=cookies_para(gestor)
        )
        assert respuesta.status_code == 200
        assert db.query(EventoCalendarioSaliente).count() == 0


class TestProcesarEventosCalendarioPendientes:
    """Unitarias de `services/calendario.py`, sin pasar por la API."""

    def test_sin_pendientes_no_hace_nada(self, db, calendario_habilitado):
        calendario_service.procesar_eventos_calendario_pendientes(db)
        assert db.query(EventoCalendarioSaliente).count() == 0

    def test_no_procesa_nada_si_email_deshabilitado(self, client, db):
        # settings.email_enabled sigue en False por defecto en el entorno de tests.
        usuario, gestor, _, recurso = _setup(db, nombre_espacio="Sala Cal Sin Enabled")
        creada = client.post(
            "/reservas", json=payload_reserva(recurso.id, fecha_habilitada()), headers=cookies_para(usuario)
        ).json()
        client.put(f"/reservas/{creada['id']}/estado", json={"nuevo_estado": "aprobada"}, headers=cookies_para(gestor))

        evento = db.query(EventoCalendarioSaliente).one()
        assert evento.estado == "pendiente"
        assert evento.graph_event_id is None

    def test_pasa_a_fallido_tras_max_intentos(self, client, db, calendario_habilitado, monkeypatch):
        usuario, gestor, _, recurso = _setup(db, nombre_espacio="Sala Cal Fallido")
        creada = client.post(
            "/reservas", json=payload_reserva(recurso.id, fecha_habilitada()), headers=cookies_para(usuario)
        ).json()

        def _falla(**kwargs):
            raise RuntimeError("Graph caído (simulado)")

        monkeypatch.setattr(calendario_service, "crear_evento_calendario_graph", _falla)

        client.put(f"/reservas/{creada['id']}/estado", json={"nuevo_estado": "aprobada"}, headers=cookies_para(gestor))
        evento = db.query(EventoCalendarioSaliente).one()
        assert evento.estado == "pendiente"  # el primer intento (dentro del PUT) ya falló

        for _ in range(calendario_service.MAX_INTENTOS):
            calendario_service.procesar_eventos_calendario_pendientes(db)

        db.refresh(evento)
        assert evento.estado == "fallido"
        assert evento.intentos == calendario_service.MAX_INTENTOS
        # La reserva en sí no se ve afectada -- solo el outbox de calendario.
        reserva = db.query(Reserva).filter(Reserva.id == creada["id"]).one()
        assert reserva.estado == "aprobada"
        assert reserva.graph_event_id is None

    def test_falla_de_graph_nunca_propaga_a_la_request_que_la_encolo(self, client, db, calendario_habilitado, monkeypatch):
        usuario, gestor, _, recurso = _setup(db, nombre_espacio="Sala Cal Sin Propagar")
        creada = client.post(
            "/reservas", json=payload_reserva(recurso.id, fecha_habilitada()), headers=cookies_para(usuario)
        ).json()

        monkeypatch.setattr(
            calendario_service, "crear_evento_calendario_graph", lambda **kw: (_ for _ in ()).throw(RuntimeError("caído"))
        )

        respuesta = client.put(
            f"/reservas/{creada['id']}/estado", json={"nuevo_estado": "aprobada"}, headers=cookies_para(gestor)
        )
        # La aprobación en sí tiene éxito aunque Graph esté caído.
        assert respuesta.status_code == 200
        assert respuesta.json()["estado"] == "aprobada"
