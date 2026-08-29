# -*- coding: utf-8 -*-
"""Pruebas unitarias de `services/recordatorios.py::enviar_recordatorios_pendientes`
(2026-08-29) -- reloj inyectado (`_RelojFijo`), mismo patrón que
`test_reservas_validaciones.py`. El wiring del `BackgroundScheduler`
(`app/main.py`) no se prueba acá -- no hay nada que verificar ahí que no
sea "¿arranca sin explotar?", ya cubierto indirectamente por
`test_lifespan_arranque.py` (EMAIL_ENABLED es False en tests, así que el
scheduler ni se instancia).
"""

from datetime import date, datetime, time

from app.models import CorreoSaliente, Reserva
from app.services.actores import columnas_actor
from app.services.recordatorios import enviar_recordatorios_pendientes

from tests.conftest import crear_espacio, crear_recurso, crear_usuario


class _RelojFijo:
    def __init__(self, valor: datetime):
        self._valor = valor

    def ahora(self) -> datetime:
        return self._valor


def _reserva_aprobada(db, usuario, espacio, recurso, *, fecha, hora_inicio, hora_fin=time(10, 0), recordatorio_enviado_en=None):
    reserva = Reserva(
        **columnas_actor(usuario),
        espacio_id=espacio.id,
        recurso_id=recurso.id,
        fecha=fecha,
        hora_inicio=hora_inicio,
        hora_fin=hora_fin,
        estado="aprobada",
        asistentes=1,
        recordatorio_enviado_en=recordatorio_enviado_en,
    )
    db.add(reserva)
    db.commit()
    db.refresh(reserva)
    return reserva


def _setup(db, *, username="recordatorio_user"):
    espacio = crear_espacio(db, nombre=f"Espacio {username}")
    usuario = crear_usuario(db, username=username, email=f"{username}@example.com", rol="usuario")
    recurso = crear_recurso(db, espacio=espacio, usuario=usuario, nombre=f"Recurso {username}")
    return usuario, espacio, recurso


def test_envia_recordatorio_dentro_de_la_ventana(db):
    usuario, espacio, recurso = _setup(db)
    ahora = datetime(2026, 8, 29, 9, 0)
    reserva = _reserva_aprobada(db, usuario, espacio, recurso, fecha=date(2026, 8, 29), hora_inicio=time(9, 30))

    enviados = enviar_recordatorios_pendientes(db, reloj=_RelojFijo(ahora))

    assert enviados == 1
    db.refresh(reserva)
    assert reserva.recordatorio_enviado_en is not None
    assert reserva.recordatorio_enviado_en.replace(tzinfo=None) == ahora
    correo = db.query(CorreoSaliente).filter(CorreoSaliente.destinatario == usuario.email).first()
    assert correo is not None
    assert correo.asunto == "Tu reserva empieza pronto"


def test_no_envia_si_falta_mas_de_una_hora(db):
    usuario, espacio, recurso = _setup(db, username="recordatorio_lejos")
    ahora = datetime(2026, 8, 29, 9, 0)
    _reserva_aprobada(db, usuario, espacio, recurso, fecha=date(2026, 8, 29), hora_inicio=time(11, 0), hora_fin=time(12, 0))

    enviados = enviar_recordatorios_pendientes(db, reloj=_RelojFijo(ahora))

    assert enviados == 0
    assert db.query(CorreoSaliente).filter(CorreoSaliente.destinatario == usuario.email).count() == 0


def test_no_envia_si_ya_paso_la_hora_de_inicio(db):
    usuario, espacio, recurso = _setup(db, username="recordatorio_pasado")
    ahora = datetime(2026, 8, 29, 9, 0)
    _reserva_aprobada(db, usuario, espacio, recurso, fecha=date(2026, 8, 29), hora_inicio=time(8, 0), hora_fin=time(10, 0))

    enviados = enviar_recordatorios_pendientes(db, reloj=_RelojFijo(ahora))

    assert enviados == 0


def test_no_envia_para_reserva_esperando(db):
    usuario, espacio, recurso = _setup(db, username="recordatorio_esperando")
    ahora = datetime(2026, 8, 29, 9, 0)
    reserva = _reserva_aprobada(db, usuario, espacio, recurso, fecha=date(2026, 8, 29), hora_inicio=time(9, 30))
    reserva.estado = "esperando"
    db.commit()

    enviados = enviar_recordatorios_pendientes(db, reloj=_RelojFijo(ahora))

    assert enviados == 0


def test_idempotente_no_reenvia_dos_veces(db):
    usuario, espacio, recurso = _setup(db, username="recordatorio_idempotente")
    ahora = datetime(2026, 8, 29, 9, 0)
    _reserva_aprobada(db, usuario, espacio, recurso, fecha=date(2026, 8, 29), hora_inicio=time(9, 30))

    primero = enviar_recordatorios_pendientes(db, reloj=_RelojFijo(ahora))
    segundo = enviar_recordatorios_pendientes(db, reloj=_RelojFijo(ahora))

    assert primero == 1
    assert segundo == 0
    assert db.query(CorreoSaliente).filter(CorreoSaliente.destinatario == usuario.email).count() == 1


def test_respeta_horas_antes_personalizado(db):
    usuario, espacio, recurso = _setup(db, username="recordatorio_custom")
    ahora = datetime(2026, 8, 29, 9, 0)
    _reserva_aprobada(db, usuario, espacio, recurso, fecha=date(2026, 8, 29), hora_inicio=time(11, 30), hora_fin=time(12, 30))

    enviados = enviar_recordatorios_pendientes(db, horas_antes=3, reloj=_RelojFijo(ahora))

    assert enviados == 1


def test_gestor_dueno_de_su_propia_reserva_tambien_recibe(db):
    espacio = crear_espacio(db, nombre="Espacio Gestor Recordatorio")
    gestor = crear_usuario(db, username="gestor_recordatorio", email="gestor_recordatorio@example.com", rol="gestor", espacio_id=espacio.id)
    recurso = crear_recurso(db, espacio=espacio, usuario=gestor, nombre="Recurso Gestor Recordatorio")
    ahora = datetime(2026, 8, 29, 9, 0)
    _reserva_aprobada(db, gestor, espacio, recurso, fecha=date(2026, 8, 29), hora_inicio=time(9, 30))

    enviados = enviar_recordatorios_pendientes(db, reloj=_RelojFijo(ahora))

    assert enviados == 1
    assert db.query(CorreoSaliente).filter(CorreoSaliente.destinatario == gestor.email).count() == 1
