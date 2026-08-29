# -*- coding: utf-8 -*-
"""Pruebas de ReservaAcompanante (Fase 12E, N:1 Reserva)."""

from datetime import date, time

import pytest
from sqlalchemy.exc import IntegrityError

from app.db import Base, engine
from app.models.reserva import Reserva
from app.models.reserva_acompanante import ReservaAcompanante
from app.services.actores import columnas_actor
from tests.conftest import crear_espacio, crear_recurso, crear_usuario


def _crear_reserva(db, *, usuario, espacio, recurso):
    reserva = Reserva(
        **columnas_actor(usuario),
        espacio_id=espacio.id,
        recurso_id=recurso.id,
        fecha=date(2026, 9, 1),
        hora_inicio=time(8, 0),
        hora_fin=time(9, 0),
        estado="esperando",
        asistentes=1,
    )
    db.add(reserva)
    db.commit()
    db.refresh(reserva)
    return reserva


class TestReservaAcompananteCreacion:
    def test_se_crea_via_create_all(self, db):
        espacio = crear_espacio(db)
        admin = crear_usuario(db, username="adm_ac1", email="adm_ac1@example.com", rol="admin")
        recurso = crear_recurso(db, espacio=espacio, usuario=admin)
        reserva = _crear_reserva(db, usuario=admin, espacio=espacio, recurso=recurso)
        ac = ReservaAcompanante(reserva_id=reserva.id, nombre="Ana", correo="ana@example.com")
        db.add(ac)
        db.commit()
        db.refresh(ac)
        assert ac.id is not None

    def test_unique_correo_por_reserva(self, db):
        espacio = crear_espacio(db)
        admin = crear_usuario(db, username="adm_ac2", email="adm_ac2@example.com", rol="admin")
        recurso = crear_recurso(db, espacio=espacio, usuario=admin)
        reserva = _crear_reserva(db, usuario=admin, espacio=espacio, recurso=recurso)
        db.add(ReservaAcompanante(reserva_id=reserva.id, nombre="Ana", correo="ana@example.com"))
        db.commit()
        db.add(ReservaAcompanante(reserva_id=reserva.id, nombre="Ana2", correo="ana@example.com"))
        with pytest.raises(IntegrityError):
            db.commit()

    def test_mismo_correo_en_distinta_reserva_permitido(self, db):
        espacio = crear_espacio(db)
        admin = crear_usuario(db, username="adm_ac3", email="adm_ac3@example.com", rol="admin")
        recurso = crear_recurso(db, espacio=espacio, usuario=admin)
        r1 = _crear_reserva(db, usuario=admin, espacio=espacio, recurso=recurso)
        r2 = Reserva(
            **columnas_actor(admin), espacio_id=espacio.id, recurso_id=recurso.id,
            fecha=date(2026, 9, 2), hora_inicio=time(8, 0), hora_fin=time(9, 0),
            estado="esperando", asistentes=1,
        )
        db.add(r2)
        db.commit()
        db.refresh(r2)
        db.add(ReservaAcompanante(reserva_id=r1.id, nombre="Ana", correo="ana@example.com"))
        db.add(ReservaAcompanante(reserva_id=r2.id, nombre="Ana", correo="ana@example.com"))
        db.commit()
        assert db.query(ReservaAcompanante).filter(ReservaAcompanante.correo == "ana@example.com").count() == 2


class TestReservaAcompananteOnDelete:
    def test_eliminar_reserva_cascade(self, db):
        espacio = crear_espacio(db)
        admin = crear_usuario(db, username="adm_ac4", email="adm_ac4@example.com", rol="admin")
        recurso = crear_recurso(db, espacio=espacio, usuario=admin)
        reserva = _crear_reserva(db, usuario=admin, espacio=espacio, recurso=recurso)
        db.add(ReservaAcompanante(reserva_id=reserva.id, nombre="Ana", correo="ana@example.com"))
        db.commit()
        db.delete(reserva)
        db.commit()
        assert db.query(ReservaAcompanante).filter(ReservaAcompanante.correo == "ana@example.com").first() is None

    def test_create_all_idempotente(self):
        Base.metadata.create_all(bind=engine)
        Base.metadata.create_all(bind=engine)
