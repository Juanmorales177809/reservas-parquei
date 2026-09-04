# -*- coding: utf-8 -*-
"""Pruebas del adjunto `.ics` en la confirmación de una reserva aprobada
(2026-08-29, ronda 2) -- solo cuando la reserva queda `aprobada` de una
(auto-aprobación o `cambiar_estado`), nunca en `esperando`/`rechazada`/
`cancelada`.
"""

import base64

from app.models import CorreoSaliente

from tests.conftest import cookies_para, crear_laboratorio, crear_recurso, crear_usuario, fecha_habilitada, payload_reserva


def test_auto_aprobacion_adjunta_ics(client, db):
    laboratorio = crear_laboratorio(db, nombre="Laboratorio ICS Auto")
    gestor = crear_usuario(db, username="gestor_ics_auto", email="gestor_ics_auto@example.com", rol="gestor", laboratorio_id=laboratorio.id)
    recurso = crear_recurso(db, laboratorio=laboratorio, usuario=gestor, nombre="Recurso ICS Auto")

    respuesta = client.post("/reservas", json=payload_reserva(recurso.id, fecha_habilitada()), headers=cookies_para(gestor))
    assert respuesta.json()["estado"] == "aprobada"

    # Ahora también existe la invitación de calendario (2026-09-03, independiente de
    # este correo de confirmación) para el mismo destinatario -- se filtra por asunto
    # para aislar el correo de confirmación de reserva, no la invitación.
    correo = (
        db.query(CorreoSaliente)
        .filter(CorreoSaliente.destinatario == gestor.email, CorreoSaliente.asunto == "Tu reserva fue aprobada")
        .one()
    )
    assert correo.adjunto_nombre is not None
    assert correo.adjunto_content_type == "text/calendar"
    contenido = base64.b64decode(correo.adjunto_contenido).decode("utf-8")
    assert contenido.startswith("BEGIN:VCALENDAR")


def test_reserva_esperando_no_adjunta_ics(client, db):
    laboratorio = crear_laboratorio(db, nombre="Laboratorio ICS Esperando")
    usuario = crear_usuario(db, username="usuario_ics_esperando", email="usuario_ics_esperando@example.com", rol="usuario")
    recurso = crear_recurso(db, laboratorio=laboratorio, usuario=usuario, nombre="Recurso ICS Esperando")

    respuesta = client.post("/reservas", json=payload_reserva(recurso.id, fecha_habilitada()), headers=cookies_para(usuario))
    assert respuesta.json()["estado"] == "esperando"

    correo = db.query(CorreoSaliente).filter(CorreoSaliente.destinatario == usuario.email).one()
    assert correo.adjunto_contenido is None


def test_cambiar_estado_a_aprobada_adjunta_ics(client, db):
    laboratorio = crear_laboratorio(db, nombre="Laboratorio ICS Estado")
    admin = crear_usuario(db, username="admin_ics_estado", email="admin_ics_estado@example.com", rol="admin")
    dueno = crear_usuario(db, username="dueno_ics_estado", email="dueno_ics_estado@example.com", rol="usuario")
    recurso = crear_recurso(db, laboratorio=laboratorio, usuario=admin, nombre="Recurso ICS Estado")
    creada = client.post("/reservas", json=payload_reserva(recurso.id, fecha_habilitada()), headers=cookies_para(dueno)).json()

    client.put(f"/reservas/{creada['id']}/estado", json={"nuevo_estado": "aprobada"}, headers=cookies_para(admin))

    correos = db.query(CorreoSaliente).filter(CorreoSaliente.destinatario == dueno.email).all()
    assert any(c.adjunto_contenido is not None for c in correos)


def test_cambiar_estado_a_rechazada_no_adjunta_ics(client, db):
    laboratorio = crear_laboratorio(db, nombre="Laboratorio ICS Rechazo")
    admin = crear_usuario(db, username="admin_ics_rechazo", email="admin_ics_rechazo@example.com", rol="admin")
    dueno = crear_usuario(db, username="dueno_ics_rechazo", email="dueno_ics_rechazo@example.com", rol="usuario")
    recurso = crear_recurso(db, laboratorio=laboratorio, usuario=admin, nombre="Recurso ICS Rechazo")
    creada = client.post("/reservas", json=payload_reserva(recurso.id, fecha_habilitada()), headers=cookies_para(dueno)).json()

    client.put(
        f"/reservas/{creada['id']}/estado",
        json={"nuevo_estado": "rechazada", "motivo": "No disponible"},
        headers=cookies_para(admin),
    )

    correos = db.query(CorreoSaliente).filter(CorreoSaliente.destinatario == dueno.email).all()
    assert all(c.adjunto_contenido is None for c in correos)
