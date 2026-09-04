# -*- coding: utf-8 -*-
"""Pruebas del outbox de correo saliente (`app/services/email.py`) y su
enganche en los eventos de reserva (`app/services/reservas.py`).

`CorreoSaliente` viaja en la MISMA transacción que la `Notificacion`
in-app que ya existía (ver `services/reservas.py::crear_reserva` y
`cambiar_estado`) -- estas pruebas verifican ambos efectos juntos, no solo
el correo aislado.
"""

import pytest

from app.config import settings
from app.models import CorreoSaliente
from app.services import email as email_service

from tests.conftest import (
    cookies_para,
    crear_laboratorio,
    crear_recurso,
    crear_usuario,
    fecha_habilitada,
    payload_reserva,
)


class _SMTPFalso:
    """Doble de `smtplib.SMTP`: nunca abre un socket real, solo registra."""

    instancias: list["_SMTPFalso"] = []

    def __init__(self, host, port, timeout=None):
        self.host = host
        self.port = port
        self.starttls_llamado = False
        self.login_llamado = None
        self.mensajes_enviados: list = []
        _SMTPFalso.instancias.append(self)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def starttls(self):
        self.starttls_llamado = True

    def login(self, user, password):
        self.login_llamado = (user, password)

    def send_message(self, mensaje):
        self.mensajes_enviados.append(mensaje)


@pytest.fixture()
def email_habilitado(monkeypatch):
    """Activa el envío (contra el doble de SMTP, nunca la red) para un test."""
    _SMTPFalso.instancias = []
    monkeypatch.setattr(settings, "email_enabled", True)
    monkeypatch.setattr(settings, "smtp_host", "smtp.prueba.local")
    monkeypatch.setattr(settings, "smtp_from", "reservas@prueba.local")
    monkeypatch.setattr(settings, "smtp_starttls", True)
    monkeypatch.setattr(email_service.smtplib, "SMTP", _SMTPFalso)
    return _SMTPFalso


def _setup(db, *, nombre_espacio="Sala Correo"):
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


class TestOutbox:
    """Unitarias de `app/services/email.py`, sin pasar por la API."""

    def test_encolar_correo_no_hace_commit(self, db):
        email_service.encolar_correo(db, destinatario="x@example.com", asunto="Asunto", cuerpo="Cuerpo")
        db.rollback()
        assert db.query(CorreoSaliente).count() == 0

    def test_procesar_pendientes_no_hace_nada_si_email_deshabilitado(self, db):
        # settings.email_enabled es False por defecto en el entorno de tests.
        email_service.encolar_correo(db, destinatario="x@example.com", asunto="A", cuerpo="B")
        db.commit()
        email_service.procesar_pendientes(db)
        correo = db.query(CorreoSaliente).one()
        assert correo.estado == "pendiente"

    def test_procesar_pendientes_envia_y_marca_enviado(self, db, email_habilitado):
        email_service.encolar_correo(db, destinatario="x@example.com", asunto="A", cuerpo="B")
        db.commit()
        email_service.procesar_pendientes(db)
        correo = db.query(CorreoSaliente).one()
        assert correo.estado == "enviado"
        assert correo.enviado_en is not None
        assert len(email_habilitado.instancias) == 1
        assert email_habilitado.instancias[0].mensajes_enviados

    def test_procesar_pendientes_pasa_a_fallido_tras_max_intentos(self, db, monkeypatch):
        monkeypatch.setattr(settings, "email_enabled", True)
        monkeypatch.setattr(settings, "smtp_host", "smtp.prueba.local")
        monkeypatch.setattr(settings, "smtp_from", "reservas@prueba.local")

        def _falla(destinatario, asunto, cuerpo):
            raise RuntimeError("smtp caído (simulado)")

        monkeypatch.setattr(email_service, "_enviar_smtp", _falla)

        email_service.encolar_correo(db, destinatario="x@example.com", asunto="A", cuerpo="B")
        db.commit()

        for _ in range(email_service.MAX_INTENTOS):
            email_service.procesar_pendientes(db)

        correo = db.query(CorreoSaliente).one()
        assert correo.estado == "fallido"
        assert correo.intentos == email_service.MAX_INTENTOS

    def test_encolar_correo_html_se_manda_como_text_html(self, db, email_habilitado):
        email_service.encolar_correo(db, destinatario="x@example.com", asunto="A", cuerpo="<p>Hola</p>", es_html=True)
        db.commit()
        email_service.procesar_pendientes(db)

        correo = db.query(CorreoSaliente).one()
        assert correo.es_html is True
        assert correo.estado == "enviado"
        mensaje_enviado = email_habilitado.instancias[0].mensajes_enviados[0]
        assert mensaje_enviado.get_content_type() == "text/html"

    def test_encolar_correo_sin_es_html_sigue_texto_plano_por_default(self, db, email_habilitado):
        email_service.encolar_correo(db, destinatario="x@example.com", asunto="A", cuerpo="Hola")
        db.commit()
        email_service.procesar_pendientes(db)

        correo = db.query(CorreoSaliente).one()
        assert correo.es_html is False
        mensaje_enviado = email_habilitado.instancias[0].mensajes_enviados[0]
        assert mensaje_enviado.get_content_type() == "text/plain"

    def test_procesar_pendientes_usa_graph_si_transport_es_graph_delegado(self, db, monkeypatch):
        """Puente temporal (app/services/email_graph.py): con
        EMAIL_TRANSPORT=graph_delegado, procesar_pendientes NO debe tocar
        SMTP en absoluto."""
        monkeypatch.setattr(settings, "email_enabled", True)
        monkeypatch.setattr(settings, "email_transport", "graph_delegado")
        monkeypatch.setattr(settings, "graph_mail_sender", "sgc-lia@itm.edu.co")

        llamadas_graph = []
        llamadas_smtp = []
        monkeypatch.setattr(email_service, "enviar_graph", lambda d, a, c, h=False, adj=None: llamadas_graph.append((d, a, c)))
        monkeypatch.setattr(email_service, "_enviar_smtp", lambda d, a, c, h=False, adj=None: llamadas_smtp.append((d, a, c)))

        email_service.encolar_correo(db, destinatario="x@example.com", asunto="A", cuerpo="B")
        db.commit()
        email_service.procesar_pendientes(db)

        correo = db.query(CorreoSaliente).one()
        assert correo.estado == "enviado"
        assert llamadas_graph == [("x@example.com", "A", "B")]
        assert llamadas_smtp == []


class TestEnganchesDeReserva:
    """Integración vía API: cada evento de reserva que ya crea una
    `Notificacion` in-app debe encolar y enviar el correo correspondiente."""

    def test_crear_reserva_esperando_notifica_a_los_gestores_del_espacio(self, client, db, email_habilitado):
        usuario, gestor, _, recurso = _setup(db)
        respuesta = client.post(
            "/reservas",
            json=payload_reserva(recurso.id, fecha_habilitada()),
            headers=cookies_para(usuario),
        )
        assert respuesta.status_code == 201
        assert respuesta.json()["estado"] == "esperando"

        correo = db.query(CorreoSaliente).filter(CorreoSaliente.destinatario == gestor.email).one()
        assert correo.estado == "enviado"
        assert "pendiente" in correo.asunto.lower()
        assert correo.es_html is True
        assert "<!DOCTYPE html>" in correo.cuerpo
        assert gestor.username in correo.cuerpo

    def test_crear_reserva_esperando_tambien_confirma_al_solicitante(self, client, db, email_habilitado):
        """Contraparte del correo al gestor: quien crea la reserva también
        recibe confirmación de que la solicitud quedó registrada (pendiente
        de aprobación), no solo el gestor que debe resolverla."""
        usuario, _, _, recurso = _setup(db)
        respuesta = client.post(
            "/reservas",
            json=payload_reserva(recurso.id, fecha_habilitada()),
            headers=cookies_para(usuario),
        )
        assert respuesta.status_code == 201

        correo = db.query(CorreoSaliente).filter(CorreoSaliente.destinatario == usuario.email).one()
        assert correo.estado == "enviado"
        assert "recibimos" in correo.asunto.lower()
        assert correo.es_html is True
        assert usuario.username in correo.cuerpo

    def test_crear_reserva_con_aprobacion_automatica_confirma_directamente_aprobada(self, client, db, email_habilitado):
        """Cuando el laboratorio aprueba automáticamente (o el gestor reserva su
        propio laboratorio) no hay nada 'pendiente' que confirmar -- el
        solicitante recibe directo el correo de aprobación."""
        laboratorio = crear_laboratorio(db, nombre="Sala Auto")
        laboratorio.aprobacion_automatica = True
        db.commit()
        usuario = crear_usuario(db, username="user_auto", email="user_auto@example.com")
        recurso = crear_recurso(db, laboratorio=laboratorio, usuario=usuario)

        respuesta = client.post(
            "/reservas",
            json=payload_reserva(recurso.id, fecha_habilitada()),
            headers=cookies_para(usuario),
        )
        assert respuesta.status_code == 201
        assert respuesta.json()["estado"] == "aprobada"

        # Filtrado por asunto exacto -- la invitación de calendario
        # (2026-09-03) también le manda un correo aparte al mismo
        # destinatario, ver `test_calendario_invitacion.py`.
        correo = db.query(CorreoSaliente).filter(
            CorreoSaliente.destinatario == usuario.email, CorreoSaliente.asunto == "Tu reserva fue aprobada"
        ).one()
        assert correo.estado == "enviado"
        assert "aprobada" in correo.asunto.lower()
        assert correo.es_html is True

    def test_aprobar_reserva_notifica_al_propietario(self, client, db, email_habilitado):
        usuario, gestor, _, recurso = _setup(db)
        creada = client.post(
            "/reservas",
            json=payload_reserva(recurso.id, fecha_habilitada()),
            headers=cookies_para(usuario),
        ).json()
        # El correo de "pendiente" a el/la gestor/a ya se encoló y procesó acá;
        # se descarta para aislar el efecto de la aprobación.
        db.query(CorreoSaliente).delete()
        db.commit()

        aprobada = client.put(
            f"/reservas/{creada['id']}/estado",
            json={"nuevo_estado": "aprobada"},
            headers=cookies_para(gestor),
        )
        assert aprobada.status_code == 200

        # La invitación de calendario (2026-09-03) también manda su propio
        # correo al aprobar -- filtrado por asunto exacto, ver
        # `test_calendario_invitacion.py` para esa parte.
        correo = db.query(CorreoSaliente).filter(CorreoSaliente.asunto == "Tu reserva fue aprobada").one()
        assert correo.destinatario == usuario.email
        assert correo.estado == "enviado"
        assert "aprobada" in correo.asunto.lower()
        assert correo.es_html is True
        assert "<!DOCTYPE html>" in correo.cuerpo

    def test_rechazar_reserva_incluye_el_motivo_en_el_correo(self, client, db, email_habilitado):
        usuario, gestor, _, recurso = _setup(db)
        creada = client.post(
            "/reservas",
            json=payload_reserva(recurso.id, fecha_habilitada()),
            headers=cookies_para(usuario),
        ).json()
        db.query(CorreoSaliente).delete()
        db.commit()

        rechazada = client.put(
            f"/reservas/{creada['id']}/estado",
            json={"nuevo_estado": "rechazada", "motivo": "No hay disponibilidad"},
            headers=cookies_para(gestor),
        )
        assert rechazada.status_code == 200

        correo = db.query(CorreoSaliente).one()
        assert correo.destinatario == usuario.email
        assert "rechazada" in correo.asunto.lower()
        assert "No hay disponibilidad" in correo.cuerpo
        assert correo.es_html is True

    def test_cancelar_reserva_usuario_notifica_al_gestor(self, client, db, email_habilitado):
        """Gap encontrado auditando los puntos de notificación existentes:
        cuando el usuario cancela su propia reserva ya aprobada, el gestor
        que la había aprobado tiene que enterarse -- antes no pasaba nada."""
        from app.models import CorreoSaliente, Notificacion

        usuario, gestor, _, recurso = _setup(db)
        creada = client.post(
            "/reservas",
            json=payload_reserva(recurso.id, fecha_habilitada()),
            headers=cookies_para(usuario),
        ).json()
        client.put(
            f"/reservas/{creada['id']}/estado",
            json={"nuevo_estado": "aprobada"},
            headers=cookies_para(gestor),
        )
        db.query(CorreoSaliente).delete()
        db.query(Notificacion).delete()
        db.commit()

        cancelada = client.put(f"/reservas/{creada['id']}/cancelar", headers=cookies_para(usuario))
        assert cancelada.status_code == 200

        # La invitación de calendario (2026-09-03) también manda su propio
        # aviso de cancelación al mismo destinatario -- filtrado por
        # asunto exacto, ver `test_calendario_invitacion.py`.
        correo = db.query(CorreoSaliente).filter(
            CorreoSaliente.destinatario == gestor.email, CorreoSaliente.asunto == "Se canceló una reserva aprobada"
        ).one()
        assert correo.estado == "enviado"
        assert correo.es_html is True
        assert "Tu reserva" not in correo.cuerpo

        notificacion = db.query(Notificacion).filter(Notificacion.personal_id == gestor.id).one()
        assert notificacion.tipo == "Cancelada"

    def test_gestor_elimina_reserva_de_otro_notifica_al_dueno(self, client, db, email_habilitado):
        """DELETE /reservas/{id} es distinto de cancelar (services/reservas.py::
        eliminar_reserva) -- sin esto, el dueño de la reserva no tenía
        forma de enterarse de que un gestor la borró directamente."""
        usuario, gestor, _, recurso = _setup(db)
        creada = client.post(
            "/reservas",
            json=payload_reserva(recurso.id, fecha_habilitada()),
            headers=cookies_para(usuario),
        ).json()
        db.query(CorreoSaliente).delete()
        db.commit()

        respuesta = client.delete(f"/reservas/{creada['id']}", headers=cookies_para(gestor))
        assert respuesta.status_code == 204

        correo = db.query(CorreoSaliente).filter(CorreoSaliente.destinatario == usuario.email).one()
        assert correo.estado == "enviado"
        assert correo.es_html is True
        assert "eliminada" in correo.cuerpo.lower()

    def test_gestor_elimina_su_propia_reserva_no_se_autonotifica(self, client, db, email_habilitado):
        usuario, gestor, laboratorio, _ = _setup(db, nombre_espacio="Sala Correo Self Delete")
        recurso_gestor = crear_recurso(db, laboratorio=laboratorio, usuario=gestor)
        creada = client.post(
            "/reservas",
            json=payload_reserva(recurso_gestor.id, fecha_habilitada()),
            headers=cookies_para(gestor),
        ).json()
        db.query(CorreoSaliente).delete()
        db.commit()

        respuesta = client.delete(f"/reservas/{creada['id']}", headers=cookies_para(gestor))
        assert respuesta.status_code == 204

        # Sin autonotificación del correo informativo "Tu reserva fue
        # eliminada" -- pero SÍ le llega el aviso de cancelación de la
        # invitación de calendario (2026-09-03): es su propio calendario
        # el que pierde el evento, distinto del correo informativo
        # redundante que este test evita.
        assert db.query(CorreoSaliente).filter(CorreoSaliente.asunto == "Tu reserva fue eliminada").count() == 0
        cancelacion = db.query(CorreoSaliente).filter(
            CorreoSaliente.destinatario == gestor.email, CorreoSaliente.asunto.like("Reserva cancelada:%")
        ).one()
        assert cancelacion.estado == "enviado"

    def test_sin_email_enabled_no_se_intenta_enviar_pero_la_reserva_se_crea_igual(self, client, db):
        # Sin la fixture email_habilitado: EMAIL_ENABLED sigue en false. La
        # fila queda en el outbox sin enviarse, y la reserva/notificación
        # in-app no se ven afectadas -- es la garantía central del diseño.
        usuario, _, _, recurso = _setup(db)
        respuesta = client.post(
            "/reservas",
            json=payload_reserva(recurso.id, fecha_habilitada()),
            headers=cookies_para(usuario),
        )
        assert respuesta.status_code == 201
        correos = db.query(CorreoSaliente).all()
        assert len(correos) == 2  # gestor (pendiente de aprobación) + solicitante (confirmación)
        assert all(correo.estado == "pendiente" for correo in correos)


class TestCorreoOpcional:
    """Correo opcional (2026-09-03): dos flags independientes,
    `Laboratorio.notificar_por_correo` y `Personal.recibir_correos` /
    `Usuario.recibir_correos` (ver `services/preferencias_correo.py`).
    Ninguno de los dos debe afectar la `Notificacion` in-app, solo el
    correo."""

    def test_laboratorio_con_correo_apagado_no_encola_nada_pero_notificacion_in_app_sigue(self, client, db, email_habilitado):
        from app.models import Notificacion

        usuario, gestor, laboratorio, recurso = _setup(db, nombre_espacio="Sala Correo Apagado Lab")
        laboratorio.notificar_por_correo = False
        db.commit()

        respuesta = client.post(
            "/reservas",
            json=payload_reserva(recurso.id, fecha_habilitada()),
            headers=cookies_para(usuario),
        )
        assert respuesta.status_code == 201

        assert db.query(CorreoSaliente).count() == 0
        assert db.query(Notificacion).filter(Notificacion.personal_id == gestor.id).count() == 1

    def test_gestor_con_correo_personal_apagado_no_recibe_pero_solicitante_si(self, client, db, email_habilitado):
        """Los dos flags se evalúan por destinatario: que el gestor haya
        apagado su propio correo no debe afectar al correo de confirmación
        que recibe el solicitante por el mismo evento."""
        usuario, gestor, _, recurso = _setup(db, nombre_espacio="Sala Correo Apagado Gestor")
        gestor.recibir_correos = False
        db.commit()

        respuesta = client.post(
            "/reservas",
            json=payload_reserva(recurso.id, fecha_habilitada()),
            headers=cookies_para(usuario),
        )
        assert respuesta.status_code == 201

        assert db.query(CorreoSaliente).filter(CorreoSaliente.destinatario == gestor.email).first() is None
        correo_usuario = db.query(CorreoSaliente).filter(CorreoSaliente.destinatario == usuario.email).one()
        assert correo_usuario.estado == "enviado"

    def test_usuario_con_correo_personal_apagado_no_recibe_confirmacion_pero_gestor_si(self, client, db, email_habilitado):
        usuario, gestor, _, recurso = _setup(db, nombre_espacio="Sala Correo Apagado Usuario")
        usuario.recibir_correos = False
        db.commit()

        respuesta = client.post(
            "/reservas",
            json=payload_reserva(recurso.id, fecha_habilitada()),
            headers=cookies_para(usuario),
        )
        assert respuesta.status_code == 201

        assert db.query(CorreoSaliente).filter(CorreoSaliente.destinatario == usuario.email).first() is None
        correo_gestor = db.query(CorreoSaliente).filter(CorreoSaliente.destinatario == gestor.email).one()
        assert correo_gestor.estado == "enviado"

    def test_aprobar_reserva_con_laboratorio_apagado_no_notifica_al_propietario(self, client, db, email_habilitado):
        usuario, gestor, laboratorio, recurso = _setup(db, nombre_espacio="Sala Correo Apagado Aprobar")
        creada = client.post(
            "/reservas",
            json=payload_reserva(recurso.id, fecha_habilitada()),
            headers=cookies_para(usuario),
        ).json()
        db.query(CorreoSaliente).delete()
        db.commit()
        laboratorio.notificar_por_correo = False
        db.commit()

        aprobada = client.put(
            f"/reservas/{creada['id']}/estado",
            json={"nuevo_estado": "aprobada"},
            headers=cookies_para(gestor),
        )
        assert aprobada.status_code == 200
        # El correo normal de "aprobada" queda apagado -- pero la
        # invitación de calendario (2026-09-03) es independiente de este
        # toggle a propósito, ver `test_calendario_invitacion.py`.
        assert db.query(CorreoSaliente).filter(CorreoSaliente.asunto == "Tu reserva fue aprobada").count() == 0
