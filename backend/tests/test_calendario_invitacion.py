# -*- coding: utf-8 -*-
"""Pruebas de integración de la invitación de Outlook Calendar por correo
(2026-09-03, rediseño -- `services/calendario.py`) y su enganche en los
eventos de reserva (`services/reservas.py`).

Reemplaza `test_calendario_saliente.py` (retirado): la primera versión de
esta feature llamaba a la API de eventos de Microsoft Graph desde un
outbox propio; esa API quedó bloqueada por política de admin del tenant
del ITM (ver `backend/CLAUDE.md`). Ahora la invitación viaja como adjunto
`.ics` (`METHOD:REQUEST`/`CANCEL`) de un correo normal -- se verifica
sobre el mismo outbox de correo (`CorreoSaliente`) que ya usa el resto del
proyecto, sin outbox propio.
"""

import base64

import pytest

from app.config import settings
from app.models import CorreoSaliente, Reserva
from app.services import email as email_service

from tests.conftest import (
    cookies_para,
    crear_laboratorio,
    crear_recurso,
    crear_usuario,
    fecha_habilitada,
    payload_reserva,
)


def _setup(db, *, nombre_espacio="Sala Invitacion"):
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
def email_habilitado(monkeypatch):
    """Mismo doble que `test_correo_saliente.py` -- activa el envío contra
    un `_enviar_smtp` inofensivo, nunca la red real."""
    monkeypatch.setattr(settings, "email_enabled", True)
    monkeypatch.setattr(email_service, "_enviar_smtp", lambda *a, **kw: None)


def _ics_de(correo: CorreoSaliente) -> str:
    assert correo.adjunto_content_type == "text/calendar"
    return base64.b64decode(correo.adjunto_contenido).decode("utf-8")


class TestInvitacionAlAprobar:
    def test_aprobacion_automatica_manda_invitacion_a_gestor_y_usuario(self, client, db, email_habilitado):
        laboratorio = crear_laboratorio(db, nombre="Sala Inv Auto")
        laboratorio.aprobacion_automatica = True
        db.commit()
        usuario = crear_usuario(db, username="user_inv_auto", email="user_inv_auto@example.com")
        gestor = crear_usuario(db, username="gestor_inv_auto", email="gestor_inv_auto@example.com", rol="gestor", laboratorio_id=laboratorio.id)
        recurso = crear_recurso(db, laboratorio=laboratorio, usuario=usuario)

        respuesta = client.post(
            "/reservas", json=payload_reserva(recurso.id, fecha_habilitada()), headers=cookies_para(usuario)
        )
        assert respuesta.status_code == 201

        invitacion_usuario = db.query(CorreoSaliente).filter(
            CorreoSaliente.destinatario == usuario.email, CorreoSaliente.asunto.like("Invitación:%")
        ).one()
        invitacion_gestor = db.query(CorreoSaliente).filter(
            CorreoSaliente.destinatario == gestor.email, CorreoSaliente.asunto.like("Invitación:%")
        ).one()
        assert invitacion_usuario.estado == "enviado"
        assert invitacion_gestor.estado == "enviado"

        ics = _ics_de(invitacion_usuario)
        assert "METHOD:REQUEST" in ics
        assert "SEQUENCE:0" in ics
        assert "ATTENDEE" in ics and usuario.email in ics
        assert gestor.email in ics
        assert "CATEGORIES:Sala Inv Auto" in ics

        reserva = db.query(Reserva).filter(Reserva.id == respuesta.json()["id"]).one()
        assert reserva.graph_event_id == f"reserva-{reserva.id}@reservas-parquei"
        assert reserva.calendario_secuencia == 0

    def test_aprobar_reserva_pendiente_manda_invitacion(self, client, db, email_habilitado):
        usuario, gestor, _, recurso = _setup(db, nombre_espacio="Sala Inv Aprobar")
        creada = client.post(
            "/reservas", json=payload_reserva(recurso.id, fecha_habilitada()), headers=cookies_para(usuario)
        ).json()

        aprobada = client.put(
            f"/reservas/{creada['id']}/estado", json={"nuevo_estado": "aprobada"}, headers=cookies_para(gestor)
        )
        assert aprobada.status_code == 200

        invitaciones = db.query(CorreoSaliente).filter(CorreoSaliente.asunto.like("Invitación:%")).all()
        destinatarios = {c.destinatario for c in invitaciones}
        assert destinatarios == {usuario.email, gestor.email}
        assert all(c.estado == "enviado" for c in invitaciones)

    def test_reserva_rechazada_no_manda_invitacion(self, client, db, email_habilitado):
        usuario, gestor, _, recurso = _setup(db, nombre_espacio="Sala Inv Rechazo")
        creada = client.post(
            "/reservas", json=payload_reserva(recurso.id, fecha_habilitada()), headers=cookies_para(usuario)
        ).json()

        client.put(
            f"/reservas/{creada['id']}/estado",
            json={"nuevo_estado": "rechazada", "motivo": "no disponible"},
            headers=cookies_para(gestor),
        )

        assert db.query(CorreoSaliente).filter(CorreoSaliente.asunto.like("Invitación:%")).count() == 0

    def test_invitacion_independiente_del_toggle_de_correo_opcional(self, client, db, email_habilitado):
        """Decisión confirmada: apagar el correo de reservas del
        laboratorio NO debe apagar la invitación de calendario -- son dos
        preferencias separadas."""
        laboratorio = crear_laboratorio(db, nombre="Sala Inv Correo Apagado")
        laboratorio.aprobacion_automatica = True
        laboratorio.notificar_por_correo = False
        db.commit()
        usuario = crear_usuario(db, username="user_inv_apagado", email="user_inv_apagado@example.com")
        recurso = crear_recurso(db, laboratorio=laboratorio, usuario=usuario)

        respuesta = client.post(
            "/reservas", json=payload_reserva(recurso.id, fecha_habilitada()), headers=cookies_para(usuario)
        )
        assert respuesta.status_code == 201

        # El correo normal de "aprobada" está apagado, pero la invitación sigue.
        assert db.query(CorreoSaliente).filter(CorreoSaliente.asunto == "Tu reserva fue aprobada").count() == 0
        assert db.query(CorreoSaliente).filter(CorreoSaliente.asunto.like("Invitación:%")).count() == 1


class TestCancelacionDeInvitacion:
    def test_usuario_cancela_reserva_aprobada_manda_cancelacion(self, client, db, email_habilitado):
        usuario, gestor, _, recurso = _setup(db, nombre_espacio="Sala Inv Cancelar Usuario")
        creada = client.post(
            "/reservas", json=payload_reserva(recurso.id, fecha_habilitada()), headers=cookies_para(usuario)
        ).json()
        client.put(f"/reservas/{creada['id']}/estado", json={"nuevo_estado": "aprobada"}, headers=cookies_para(gestor))
        db.query(CorreoSaliente).delete()
        db.commit()

        cancelada = client.put(f"/reservas/{creada['id']}/cancelar", headers=cookies_para(usuario))
        assert cancelada.status_code == 200

        cancelaciones = db.query(CorreoSaliente).filter(CorreoSaliente.asunto.like("Reserva cancelada:%")).all()
        destinatarios = {c.destinatario for c in cancelaciones}
        assert destinatarios == {usuario.email, gestor.email}
        ics = _ics_de(cancelaciones[0])
        assert "METHOD:CANCEL" in ics
        assert "STATUS:CANCELLED" in ics
        assert "SEQUENCE:1" in ics  # 0 al crear, 1 al cancelar

    def test_gestor_cancela_via_cambiar_estado_manda_cancelacion(self, client, db, email_habilitado):
        usuario, gestor, _, recurso = _setup(db, nombre_espacio="Sala Inv Cancelar Gestor")
        creada = client.post(
            "/reservas", json=payload_reserva(recurso.id, fecha_habilitada()), headers=cookies_para(usuario)
        ).json()
        client.put(f"/reservas/{creada['id']}/estado", json={"nuevo_estado": "aprobada"}, headers=cookies_para(gestor))
        db.query(CorreoSaliente).delete()
        db.commit()

        cancelada = client.put(
            f"/reservas/{creada['id']}/estado", json={"nuevo_estado": "cancelada"}, headers=cookies_para(gestor)
        )
        assert cancelada.status_code == 200
        assert db.query(CorreoSaliente).filter(CorreoSaliente.asunto.like("Reserva cancelada:%")).count() == 2

    def test_eliminar_reserva_aprobada_manda_cancelacion(self, client, db, email_habilitado):
        usuario, gestor, _, recurso = _setup(db, nombre_espacio="Sala Inv Eliminar")
        creada = client.post(
            "/reservas", json=payload_reserva(recurso.id, fecha_habilitada()), headers=cookies_para(usuario)
        ).json()
        client.put(f"/reservas/{creada['id']}/estado", json={"nuevo_estado": "aprobada"}, headers=cookies_para(gestor))
        db.query(CorreoSaliente).delete()
        db.commit()

        respuesta = client.delete(f"/reservas/{creada['id']}", headers=cookies_para(gestor))
        assert respuesta.status_code == 204

        assert db.query(CorreoSaliente).filter(CorreoSaliente.asunto.like("Reserva cancelada:%")).count() == 2

    def test_eliminar_reserva_pendiente_sin_invitacion_no_manda_cancelacion(self, client, db, email_habilitado):
        usuario, gestor, _, recurso = _setup(db, nombre_espacio="Sala Inv Eliminar Pendiente")
        creada = client.post(
            "/reservas", json=payload_reserva(recurso.id, fecha_habilitada()), headers=cookies_para(usuario)
        ).json()

        respuesta = client.delete(f"/reservas/{creada['id']}", headers=cookies_para(gestor))
        assert respuesta.status_code == 204
        assert db.query(CorreoSaliente).filter(CorreoSaliente.asunto.like("Reserva cancelada:%")).count() == 0


class TestActualizacionDeInvitacion:
    def test_cambio_de_horario_en_aprobada_manda_actualizacion_con_secuencia_incrementada(self, client, db, email_habilitado):
        usuario, gestor, _, recurso = _setup(db, nombre_espacio="Sala Inv Actualizar")
        creada = client.post(
            "/reservas", json=payload_reserva(recurso.id, fecha_habilitada()), headers=cookies_para(usuario)
        ).json()
        client.put(f"/reservas/{creada['id']}/estado", json={"nuevo_estado": "aprobada"}, headers=cookies_para(gestor))
        db.query(CorreoSaliente).delete()
        db.commit()

        respuesta = client.patch(
            f"/reservas/{creada['id']}", json={"hora_inicio": "11:00", "hora_fin": "13:00"}, headers=cookies_para(gestor)
        )
        assert respuesta.status_code == 200

        invitaciones = db.query(CorreoSaliente).filter(CorreoSaliente.asunto.like("Invitación:%")).all()
        assert {c.destinatario for c in invitaciones} == {usuario.email, gestor.email}
        ics = _ics_de(invitaciones[0])
        assert "METHOD:REQUEST" in ics
        assert "SEQUENCE:1" in ics
        assert "DTSTART:" in ics and "T110000" in ics

        reserva = db.query(Reserva).filter(Reserva.id == creada["id"]).one()
        assert reserva.calendario_secuencia == 1

    def test_actualizar_sin_cambiar_horario_no_manda_nada(self, client, db, email_habilitado):
        usuario, gestor, _, recurso = _setup(db, nombre_espacio="Sala Inv Sin Cambio")
        creada = client.post(
            "/reservas", json=payload_reserva(recurso.id, fecha_habilitada()), headers=cookies_para(usuario)
        ).json()
        client.put(f"/reservas/{creada['id']}/estado", json={"nuevo_estado": "aprobada"}, headers=cookies_para(gestor))
        db.query(CorreoSaliente).delete()
        db.commit()

        respuesta = client.patch(f"/reservas/{creada['id']}", json={"asistentes": 3}, headers=cookies_para(gestor))
        assert respuesta.status_code == 200
        assert db.query(CorreoSaliente).filter(CorreoSaliente.asunto.like("Invitación:%")).count() == 0

    def test_actualizar_reserva_esperando_no_manda_nada(self, client, db, email_habilitado):
        """Una reserva `esperando` todavía no tiene invitación creada --
        no hay nada que reprogramar."""
        usuario, gestor, _, recurso = _setup(db, nombre_espacio="Sala Inv Esperando")
        creada = client.post(
            "/reservas", json=payload_reserva(recurso.id, fecha_habilitada()), headers=cookies_para(usuario)
        ).json()
        db.query(CorreoSaliente).delete()
        db.commit()

        respuesta = client.patch(f"/reservas/{creada['id']}", json={"asistentes": 3}, headers=cookies_para(usuario))
        assert respuesta.status_code == 200
        assert db.query(CorreoSaliente).filter(CorreoSaliente.asunto.like("Invitación:%")).count() == 0
