# -*- coding: utf-8 -*-
"""Pruebas de ReservaEnsayo (Fase 12E, N:N reserva↔ensayo).

Tabla plana sin agenda propia ni EXCLUDE — solo etiqueta.
"""

from datetime import date, time

import pytest
from sqlalchemy.exc import IntegrityError

from app.db import Base, engine
from app.models.ensayo import Ensayo
from app.models.reserva import Reserva
from app.models.reserva_ensayo import ReservaEnsayo
from app.models.zona import Zona
from app.services.actores import columnas_actor
from tests.conftest import crear_espacio, crear_recurso, crear_usuario


def _crear_reserva(db, *, usuario, espacio, recurso, fecha=None):
    reserva = Reserva(
        **columnas_actor(usuario),
        espacio_id=espacio.id,
        recurso_id=recurso.id,
        fecha=fecha or date(2026, 9, 1),
        hora_inicio=time(8, 0),
        hora_fin=time(9, 0),
        estado="esperando",
        asistentes=1,
    )
    db.add(reserva)
    db.commit()
    db.refresh(reserva)
    return reserva


def _crear_ensayo(db, *, zona, usuario):
    ensayo = Ensayo(nombre="Ensayo X", zona_id=zona.id, created_by=usuario.id, updated_by=usuario.id)
    db.add(ensayo)
    db.commit()
    db.refresh(ensayo)
    return ensayo


class TestReservaEnsayoCreacion:
    def test_se_crea_via_create_all(self, db):
        espacio = crear_espacio(db)
        admin = crear_usuario(db, username="adm_re1", email="adm_re1@example.com", rol="admin")
        recurso = crear_recurso(db, espacio=espacio, usuario=admin)
        reserva = _crear_reserva(db, usuario=admin, espacio=espacio, recurso=recurso)
        zona = Zona(nombre="Z RE", espacio_id=espacio.id, created_by=admin.id, updated_by=admin.id)
        db.add(zona)
        db.commit()
        db.refresh(zona)
        ensayo = _crear_ensayo(db, zona=zona, usuario=admin)
        assoc = ReservaEnsayo(reserva_id=reserva.id, ensayo_id=ensayo.id)
        db.add(assoc)
        db.commit()
        db.refresh(assoc)
        assert assoc.id is not None

    def test_unique_constraint_par(self, db):
        espacio = crear_espacio(db)
        admin = crear_usuario(db, username="adm_re2", email="adm_re2@example.com", rol="admin")
        recurso = crear_recurso(db, espacio=espacio, usuario=admin)
        reserva = _crear_reserva(db, usuario=admin, espacio=espacio, recurso=recurso)
        zona = Zona(nombre="Z RE2", espacio_id=espacio.id, created_by=admin.id, updated_by=admin.id)
        db.add(zona)
        db.commit()
        db.refresh(zona)
        ensayo = _crear_ensayo(db, zona=zona, usuario=admin)
        db.add(ReservaEnsayo(reserva_id=reserva.id, ensayo_id=ensayo.id))
        db.commit()
        db.add(ReservaEnsayo(reserva_id=reserva.id, ensayo_id=ensayo.id))
        with pytest.raises(IntegrityError):
            db.commit()

    def test_fk_reserva_id_inexistente(self, db):
        espacio = crear_espacio(db)
        admin = crear_usuario(db, username="adm_re3", email="adm_re3@example.com", rol="admin")
        zona = Zona(nombre="Z RE3", espacio_id=espacio.id, created_by=admin.id, updated_by=admin.id)
        db.add(zona)
        db.commit()
        db.refresh(zona)
        ensayo = _crear_ensayo(db, zona=zona, usuario=admin)
        db.add(ReservaEnsayo(reserva_id=999999, ensayo_id=ensayo.id))
        with pytest.raises(IntegrityError):
            db.commit()


class TestReservaEnsayoOnDelete:
    def test_eliminar_reserva_cascade(self, db):
        espacio = crear_espacio(db)
        admin = crear_usuario(db, username="adm_re4", email="adm_re4@example.com", rol="admin")
        recurso = crear_recurso(db, espacio=espacio, usuario=admin)
        reserva = _crear_reserva(db, usuario=admin, espacio=espacio, recurso=recurso)
        zona = Zona(nombre="Z RE4", espacio_id=espacio.id, created_by=admin.id, updated_by=admin.id)
        db.add(zona)
        db.commit()
        db.refresh(zona)
        ensayo = _crear_ensayo(db, zona=zona, usuario=admin)
        db.add(ReservaEnsayo(reserva_id=reserva.id, ensayo_id=ensayo.id))
        db.commit()
        db.delete(reserva)
        db.commit()
        assert db.query(ReservaEnsayo).filter(ReservaEnsayo.ensayo_id == ensayo.id).first() is None

    def test_eliminar_ensayo_referenciado_bloquea_sin_cascade(self, db):
        espacio = crear_espacio(db)
        admin = crear_usuario(db, username="adm_re5", email="adm_re5@example.com", rol="admin")
        recurso = crear_recurso(db, espacio=espacio, usuario=admin)
        reserva = _crear_reserva(db, usuario=admin, espacio=espacio, recurso=recurso)
        zona = Zona(nombre="Z RE5", espacio_id=espacio.id, created_by=admin.id, updated_by=admin.id)
        db.add(zona)
        db.commit()
        db.refresh(zona)
        ensayo = _crear_ensayo(db, zona=zona, usuario=admin)
        db.add(ReservaEnsayo(reserva_id=reserva.id, ensayo_id=ensayo.id))
        db.commit()
        db.delete(ensayo)
        with pytest.raises(IntegrityError):
            db.commit()

    def test_create_all_idempotente(self):
        Base.metadata.create_all(bind=engine)
        Base.metadata.create_all(bind=engine)
