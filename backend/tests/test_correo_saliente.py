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
    crear_espacio,
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
    espacio = crear_espacio(db, nombre=nombre_espacio)
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
        espacio_id=espacio.id,
    )
    recurso = crear_recurso(db, espacio=espacio, usuario=usuario)
    return usuario, gestor, espacio, recurso


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
        monkeypatch.setattr(email_service, "enviar_graph", lambda d, a, c, h=False: llamadas_graph.append((d, a, c)))
        monkeypatch.setattr(email_service, "_enviar_smtp", lambda d, a, c, h=False: llamadas_smtp.append((d, a, c)))

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
        """Cuando el espacio aprueba automáticamente (o el gestor reserva su
        propio espacio) no hay nada 'pendiente' que confirmar -- el
        solicitante recibe directo el correo de aprobación."""
        espacio = crear_espacio(db, nombre="Sala Auto")
        espacio.aprobacion_automatica = True
        db.commit()
        usuario = crear_usuario(db, username="user_auto", email="user_auto@example.com")
        recurso = crear_recurso(db, espacio=espacio, usuario=usuario)

        respuesta = client.post(
            "/reservas",
            json=payload_reserva(recurso.id, fecha_habilitada()),
            headers=cookies_para(usuario),
        )
        assert respuesta.status_code == 201
        assert respuesta.json()["estado"] == "aprobada"

        correo = db.query(CorreoSaliente).filter(CorreoSaliente.destinatario == usuario.email).one()
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

        correo = db.query(CorreoSaliente).one()
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

        correo = db.query(CorreoSaliente).filter(CorreoSaliente.destinatario == gestor.email).one()
        assert correo.estado == "enviado"
        assert correo.es_html is True
        assert "Tu reserva" not in correo.cuerpo

        notificacion = db.query(Notificacion).filter(Notificacion.usuario_id == gestor.id).one()
        assert notificacion.tipo == "Cancelada"

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
