# -*- coding: utf-8 -*-
"""Pruebas unitarias de `services/lista_espera.py::vencer_y_reencolar`
(2026-08-29, ronda 2) -- reloj inyectado (`_RelojFijo`), mismo patrón que
`test_recordatorios.py`.
"""

from datetime import date, datetime, time

from app.models import CorreoSaliente, ListaEspera, Reserva
from app.models.reserva_recurso import ReservaRecurso
from app.services.actores import columnas_actor
from app.services.lista_espera import notificar_primero_en_espera, vencer_y_reencolar

from tests.conftest import crear_espacio, crear_recurso, crear_usuario


class _RelojFijo:
    def __init__(self, valor: datetime):
        self._valor = valor

    def ahora(self) -> datetime:
        return self._valor


def _entrada(db, actor, recurso, *, fecha, hora_inicio=time(8, 0), hora_fin=time(10, 0), estado="activa", notificada_en=None):
    entrada = ListaEspera(
        **columnas_actor(actor),
        recurso_id=recurso.id,
        fecha=fecha,
        hora_inicio=hora_inicio,
        hora_fin=hora_fin,
        estado=estado,
        notificada_en=notificada_en,
    )
    db.add(entrada)
    db.commit()
    db.refresh(entrada)
    return entrada


def _setup(db, *, sufijo="reintento"):
    espacio = crear_espacio(db, nombre=f"Espacio {sufijo}")
    usuario = crear_usuario(db, username=f"reintento_{sufijo}", email=f"reintento_{sufijo}@example.com", rol="usuario")
    recurso = crear_recurso(db, espacio=espacio, usuario=usuario, nombre=f"Recurso {sufijo}")
    return espacio, usuario, recurso


def test_expira_y_notifica_al_siguiente_si_sigue_libre(db):
    espacio, primero, recurso = _setup(db, sufijo="expira_libre")
    segundo = crear_usuario(db, username="segundo_expira_libre", email="segundo_expira_libre@example.com", rol="usuario")
    fecha = date(2026, 9, 1)
    ahora = datetime(2026, 9, 1, 9, 0)

    e1 = _entrada(db, primero, recurso, fecha=fecha, estado="notificada", notificada_en=datetime(2026, 9, 1, 6, 0))
    e2 = _entrada(db, segundo, recurso, fecha=fecha, estado="activa")

    vencidas = vencer_y_reencolar(db, horas_expiracion=2, reloj=_RelojFijo(ahora))

    assert vencidas == 1
    db.refresh(e1)
    db.refresh(e2)
    assert e1.estado == "expirada"
    assert e2.estado == "notificada"
    assert db.query(CorreoSaliente).filter(CorreoSaliente.destinatario == segundo.email).count() == 1


def test_expira_sin_notificar_a_nadie_si_ya_no_hay_nadie_en_cola(db):
    espacio, primero, recurso = _setup(db, sufijo="expira_solo")
    fecha = date(2026, 9, 1)
    ahora = datetime(2026, 9, 1, 9, 0)

    e1 = _entrada(db, primero, recurso, fecha=fecha, estado="notificada", notificada_en=datetime(2026, 9, 1, 6, 0))

    vencidas = vencer_y_reencolar(db, horas_expiracion=2, reloj=_RelojFijo(ahora))

    assert vencidas == 1
    db.refresh(e1)
    assert e1.estado == "expirada"
    assert db.query(CorreoSaliente).count() == 0


def test_expira_sin_renotificar_si_el_recurso_ya_no_esta_libre(db):
    espacio, primero, recurso = _setup(db, sufijo="expira_ocupado")
    segundo = crear_usuario(db, username="segundo_expira_ocupado", email="segundo_expira_ocupado@example.com", rol="usuario")
    otro_dueno = crear_usuario(db, username="dueno_expira_ocupado", email="dueno_expira_ocupado@example.com", rol="usuario")
    fecha = date(2026, 9, 1)
    ahora = datetime(2026, 9, 1, 9, 0)

    e1 = _entrada(db, primero, recurso, fecha=fecha, estado="notificada", notificada_en=datetime(2026, 9, 1, 6, 0))
    e2 = _entrada(db, segundo, recurso, fecha=fecha, estado="activa")
    # Alguien más ya ocupó ese horario por fuera de la lista de espera.
    # `get_reservas_bloqueantes` (que usa `vencer_y_reencolar` para decidir
    # si "sigue libre") hace JOIN contra `reserva_recursos`, no contra la
    # columna legacy `Reserva.recurso_id` -- hace falta la fila de
    # asociación real, igual que hace `crear_reserva` en producción.
    reserva_ocupante = Reserva(
        **columnas_actor(otro_dueno),
        espacio_id=espacio.id,
        recurso_id=recurso.id,
        fecha=fecha,
        hora_inicio=time(8, 0),
        hora_fin=time(10, 0),
        estado="aprobada",
        asistentes=1,
    )
    db.add(reserva_ocupante)
    db.flush()
    db.add(
        ReservaRecurso(
            reserva_id=reserva_ocupante.id,
            recurso_id=recurso.id,
            fecha=fecha,
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
            estado="aprobada",
        )
    )
    db.commit()

    vencidas = vencer_y_reencolar(db, horas_expiracion=2, reloj=_RelojFijo(ahora))

    assert vencidas == 1
    db.refresh(e1)
    db.refresh(e2)
    assert e1.estado == "expirada"
    assert e2.estado == "activa"  # nunca se le avisó
    assert db.query(CorreoSaliente).count() == 0


def test_no_expira_si_todavia_no_paso_el_tiempo(db):
    espacio, primero, recurso = _setup(db, sufijo="no_expira")
    fecha = date(2026, 9, 1)
    ahora = datetime(2026, 9, 1, 9, 0)

    e1 = _entrada(db, primero, recurso, fecha=fecha, estado="notificada", notificada_en=datetime(2026, 9, 1, 8, 0))

    vencidas = vencer_y_reencolar(db, horas_expiracion=2, reloj=_RelojFijo(ahora))

    assert vencidas == 0
    db.refresh(e1)
    assert e1.estado == "notificada"


def test_notificar_primero_en_espera_setea_notificada_en(db):
    espacio, primero, recurso = _setup(db, sufijo="notificada_en")
    fecha = date(2026, 9, 1)
    ahora = datetime(2026, 9, 1, 9, 0)
    e1 = _entrada(db, primero, recurso, fecha=fecha, estado="activa")

    notificar_primero_en_espera(
        db, recurso_id=recurso.id, fecha=fecha, hora_inicio=time(8, 0), hora_fin=time(10, 0), reloj=_RelojFijo(ahora)
    )

    db.refresh(e1)
    assert e1.estado == "notificada"
    assert e1.notificada_en.replace(tzinfo=None) == ahora
