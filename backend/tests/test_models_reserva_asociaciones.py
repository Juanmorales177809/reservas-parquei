# -*- coding: utf-8 -*-
"""Pruebas de los modelos ReservaRecurso y ReservaEspacio (Fase 12C-4a).

Alcance de esta subfase: las tablas de asociación son creables y
consultables de forma aislada. NO se sincronizan todavía con `Reserva`
(sin backfill, sin escritura desde `services/reservas.py`, sin retiro de
`Reserva.recurso_id`) -- eso corresponde a 12C-4b en adelante.
"""

from datetime import date, time

import pytest
from sqlalchemy.exc import IntegrityError

from app.db import Base, engine
from app.models.reserva import Reserva
from app.models.reserva_recurso import ReservaRecurso
from app.models.reserva_espacio import ReservaEspacio
from app.models.espacio import Espacio
from app.services.actores import columnas_actor
from tests.conftest import crear_laboratorio, crear_recurso, crear_usuario


def _crear_reserva(db, *, usuario, laboratorio, recurso, fecha=None, estado="esperando"):
    reserva = Reserva(
        **columnas_actor(usuario),
        laboratorio_id=laboratorio.id,
        recurso_id=recurso.id,
        fecha=fecha or date(2026, 9, 1),
        hora_inicio=time(8, 0),
        hora_fin=time(9, 0),
        estado=estado,
        asistentes=1,
    )
    db.add(reserva)
    db.commit()
    db.refresh(reserva)
    return reserva


def _crear_espacio(db, *, laboratorio, usuario, nombre="Espacio de pruebas"):
    espacio = Espacio(nombre=nombre, laboratorio_id=laboratorio.id, created_by=usuario.id, updated_by=usuario.id)
    db.add(espacio)
    db.commit()
    db.refresh(espacio)
    return espacio


class TestImportacionYCreacionDeTablas:
    def test_reserva_recurso_se_crea(self, db):
        laboratorio = crear_laboratorio(db)
        admin = crear_usuario(db, username="admin_rr1", email="admin_rr1@example.com", rol="admin")
        recurso = crear_recurso(db, laboratorio=laboratorio, usuario=admin)
        reserva = _crear_reserva(db, usuario=admin, laboratorio=laboratorio, recurso=recurso)

        asociacion = ReservaRecurso(
            reserva_id=reserva.id,
            recurso_id=recurso.id,
            fecha=reserva.fecha,
            hora_inicio=reserva.hora_inicio,
            hora_fin=reserva.hora_fin,
            estado=reserva.estado,
        )
        db.add(asociacion)
        db.commit()
        db.refresh(asociacion)
        assert asociacion.id is not None

    def test_reserva_espacio_se_crea(self, db):
        laboratorio = crear_laboratorio(db)
        admin = crear_usuario(db, username="admin_rz1", email="admin_rz1@example.com", rol="admin")
        recurso = crear_recurso(db, laboratorio=laboratorio, usuario=admin)
        reserva = _crear_reserva(db, usuario=admin, laboratorio=laboratorio, recurso=recurso)
        espacio = _crear_espacio(db, laboratorio=laboratorio, usuario=admin)

        asociacion = ReservaEspacio(
            reserva_id=reserva.id,
            espacio_id=espacio.id,
            fecha=reserva.fecha,
            hora_inicio=reserva.hora_inicio,
            hora_fin=reserva.hora_fin,
            estado=reserva.estado,
        )
        db.add(asociacion)
        db.commit()
        db.refresh(asociacion)
        assert asociacion.id is not None


class TestFKsYNulabilidad:
    def test_reserva_recurso_reserva_id_obligatorio(self, db):
        laboratorio = crear_laboratorio(db)
        admin = crear_usuario(db, username="admin_rr2", email="admin_rr2@example.com", rol="admin")
        recurso = crear_recurso(db, laboratorio=laboratorio, usuario=admin)
        asociacion = ReservaRecurso(
            recurso_id=recurso.id, fecha=date(2026, 9, 1),
            hora_inicio=time(8, 0), hora_fin=time(9, 0), estado="esperando",
        )
        db.add(asociacion)
        with pytest.raises(IntegrityError):
            db.commit()

    def test_reserva_recurso_recurso_id_obligatorio(self, db):
        laboratorio = crear_laboratorio(db)
        admin = crear_usuario(db, username="admin_rr3", email="admin_rr3@example.com", rol="admin")
        recurso = crear_recurso(db, laboratorio=laboratorio, usuario=admin)
        reserva = _crear_reserva(db, usuario=admin, laboratorio=laboratorio, recurso=recurso)
        asociacion = ReservaRecurso(
            reserva_id=reserva.id, fecha=date(2026, 9, 1),
            hora_inicio=time(8, 0), hora_fin=time(9, 0), estado="esperando",
        )
        db.add(asociacion)
        with pytest.raises(IntegrityError):
            db.commit()

    def test_reserva_recurso_reserva_id_inexistente_rechazado_por_fk(self, db):
        laboratorio = crear_laboratorio(db)
        admin = crear_usuario(db, username="admin_rr3b", email="admin_rr3b@example.com", rol="admin")
        recurso = crear_recurso(db, laboratorio=laboratorio, usuario=admin)
        asociacion = ReservaRecurso(
            reserva_id=999999, recurso_id=recurso.id, fecha=date(2026, 9, 1),
            hora_inicio=time(8, 0), hora_fin=time(9, 0), estado="esperando",
        )
        db.add(asociacion)
        with pytest.raises(IntegrityError):
            db.commit()

    def test_reserva_recurso_recurso_id_inexistente_rechazado_por_fk(self, db):
        laboratorio = crear_laboratorio(db)
        admin = crear_usuario(db, username="admin_rr3c", email="admin_rr3c@example.com", rol="admin")
        recurso = crear_recurso(db, laboratorio=laboratorio, usuario=admin)
        reserva = _crear_reserva(db, usuario=admin, laboratorio=laboratorio, recurso=recurso)
        asociacion = ReservaRecurso(
            reserva_id=reserva.id, recurso_id=999999, fecha=date(2026, 9, 1),
            hora_inicio=time(8, 0), hora_fin=time(9, 0), estado="esperando",
        )
        db.add(asociacion)
        with pytest.raises(IntegrityError):
            db.commit()

    def test_reserva_espacio_espacio_id_obligatorio(self, db):
        laboratorio = crear_laboratorio(db)
        admin = crear_usuario(db, username="admin_rz2", email="admin_rz2@example.com", rol="admin")
        recurso = crear_recurso(db, laboratorio=laboratorio, usuario=admin)
        reserva = _crear_reserva(db, usuario=admin, laboratorio=laboratorio, recurso=recurso)
        asociacion = ReservaEspacio(
            reserva_id=reserva.id, fecha=date(2026, 9, 1),
            hora_inicio=time(8, 0), hora_fin=time(9, 0), estado="esperando",
        )
        db.add(asociacion)
        with pytest.raises(IntegrityError):
            db.commit()

    def test_reserva_espacio_reserva_id_inexistente_rechazado_por_fk(self, db):
        laboratorio = crear_laboratorio(db)
        admin = crear_usuario(db, username="admin_rz3b", email="admin_rz3b@example.com", rol="admin")
        espacio = _crear_espacio(db, laboratorio=laboratorio, usuario=admin)
        asociacion = ReservaEspacio(
            reserva_id=999999, espacio_id=espacio.id, fecha=date(2026, 9, 1),
            hora_inicio=time(8, 0), hora_fin=time(9, 0), estado="esperando",
        )
        db.add(asociacion)
        with pytest.raises(IntegrityError):
            db.commit()

    def test_reserva_espacio_espacio_id_inexistente_rechazado_por_fk(self, db):
        laboratorio = crear_laboratorio(db)
        admin = crear_usuario(db, username="admin_rz3", email="admin_rz3@example.com", rol="admin")
        recurso = crear_recurso(db, laboratorio=laboratorio, usuario=admin)
        reserva = _crear_reserva(db, usuario=admin, laboratorio=laboratorio, recurso=recurso)
        asociacion = ReservaEspacio(
            reserva_id=reserva.id, espacio_id=999999, fecha=date(2026, 9, 1),
            hora_inicio=time(8, 0), hora_fin=time(9, 0), estado="esperando",
        )
        db.add(asociacion)
        with pytest.raises(IntegrityError):
            db.commit()


class TestUnicidadPorPar:
    def test_mismo_par_reserva_recurso_rechazado(self, db):
        laboratorio = crear_laboratorio(db)
        admin = crear_usuario(db, username="admin_rr4", email="admin_rr4@example.com", rol="admin")
        recurso = crear_recurso(db, laboratorio=laboratorio, usuario=admin)
        reserva = _crear_reserva(db, usuario=admin, laboratorio=laboratorio, recurso=recurso)
        db.add(ReservaRecurso(
            reserva_id=reserva.id, recurso_id=recurso.id, fecha=reserva.fecha,
            hora_inicio=reserva.hora_inicio, hora_fin=reserva.hora_fin, estado=reserva.estado,
        ))
        db.commit()

        db.add(ReservaRecurso(
            reserva_id=reserva.id, recurso_id=recurso.id, fecha=reserva.fecha,
            hora_inicio=reserva.hora_inicio, hora_fin=reserva.hora_fin, estado=reserva.estado,
        ))
        with pytest.raises(IntegrityError):
            db.commit()

    def test_mismo_recurso_en_distinta_reserva_permitido(self, db):
        """La unicidad es por PAR (reserva_id, recurso_id) -- a diferencia
        de espacio_recursos (12C-3), que restringe por recurso_id solo, un
        mismo recurso puede aparecer en varias reservas distintas."""
        laboratorio = crear_laboratorio(db)
        admin = crear_usuario(db, username="admin_rr5", email="admin_rr5@example.com", rol="admin")
        recurso = crear_recurso(db, laboratorio=laboratorio, usuario=admin)
        reserva_a = _crear_reserva(db, usuario=admin, laboratorio=laboratorio, recurso=recurso, fecha=date(2026, 9, 1))
        reserva_b = _crear_reserva(db, usuario=admin, laboratorio=laboratorio, recurso=recurso, fecha=date(2026, 9, 2))

        db.add(ReservaRecurso(
            reserva_id=reserva_a.id, recurso_id=recurso.id, fecha=reserva_a.fecha,
            hora_inicio=reserva_a.hora_inicio, hora_fin=reserva_a.hora_fin, estado=reserva_a.estado,
        ))
        db.add(ReservaRecurso(
            reserva_id=reserva_b.id, recurso_id=recurso.id, fecha=reserva_b.fecha,
            hora_inicio=reserva_b.hora_inicio, hora_fin=reserva_b.hora_fin, estado=reserva_b.estado,
        ))
        db.commit()

        total = db.query(ReservaRecurso).filter(ReservaRecurso.recurso_id == recurso.id).count()
        assert total == 2

    def test_mismo_par_reserva_espacio_rechazado(self, db):
        laboratorio = crear_laboratorio(db)
        admin = crear_usuario(db, username="admin_rz4", email="admin_rz4@example.com", rol="admin")
        recurso = crear_recurso(db, laboratorio=laboratorio, usuario=admin)
        reserva = _crear_reserva(db, usuario=admin, laboratorio=laboratorio, recurso=recurso)
        espacio = _crear_espacio(db, laboratorio=laboratorio, usuario=admin)
        db.add(ReservaEspacio(
            reserva_id=reserva.id, espacio_id=espacio.id, fecha=reserva.fecha,
            hora_inicio=reserva.hora_inicio, hora_fin=reserva.hora_fin, estado=reserva.estado,
        ))
        db.commit()

        db.add(ReservaEspacio(
            reserva_id=reserva.id, espacio_id=espacio.id, fecha=reserva.fecha,
            hora_inicio=reserva.hora_inicio, hora_fin=reserva.hora_fin, estado=reserva.estado,
        ))
        with pytest.raises(IntegrityError):
            db.commit()


class TestOndeleteCascade:
    def test_eliminar_reserva_elimina_sus_reserva_recursos(self, db):
        laboratorio = crear_laboratorio(db)
        admin = crear_usuario(db, username="admin_rr6", email="admin_rr6@example.com", rol="admin")
        recurso = crear_recurso(db, laboratorio=laboratorio, usuario=admin)
        reserva = _crear_reserva(db, usuario=admin, laboratorio=laboratorio, recurso=recurso)
        db.add(ReservaRecurso(
            reserva_id=reserva.id, recurso_id=recurso.id, fecha=reserva.fecha,
            hora_inicio=reserva.hora_inicio, hora_fin=reserva.hora_fin, estado=reserva.estado,
        ))
        db.commit()

        db.delete(reserva)
        db.commit()

        assert db.query(ReservaRecurso).filter(ReservaRecurso.recurso_id == recurso.id).first() is None

    def test_eliminar_reserva_elimina_sus_reserva_espacios(self, db):
        laboratorio = crear_laboratorio(db)
        admin = crear_usuario(db, username="admin_rz5", email="admin_rz5@example.com", rol="admin")
        recurso = crear_recurso(db, laboratorio=laboratorio, usuario=admin)
        reserva = _crear_reserva(db, usuario=admin, laboratorio=laboratorio, recurso=recurso)
        espacio = _crear_espacio(db, laboratorio=laboratorio, usuario=admin)
        db.add(ReservaEspacio(
            reserva_id=reserva.id, espacio_id=espacio.id, fecha=reserva.fecha,
            hora_inicio=reserva.hora_inicio, hora_fin=reserva.hora_fin, estado=reserva.estado,
        ))
        db.commit()

        db.delete(reserva)
        db.commit()

        assert db.query(ReservaEspacio).filter(ReservaEspacio.espacio_id == espacio.id).first() is None

    def test_eliminar_recurso_referenciado_es_rechazado_sin_cascada(self, db):
        """recurso_id NO tiene ondelete=CASCADE (a diferencia de
        espacio_recursos en 12C-3): un recurso referenciado solo en
        reserva_recursos (no en la columna vieja Reserva.recurso_id, que
        aqui usa un recurso "ancla" distinto para aislar exactamente qué
        constraint se ejercita) no puede eliminarse silenciosamente."""
        laboratorio = crear_laboratorio(db)
        admin = crear_usuario(db, username="admin_rr7", email="admin_rr7@example.com", rol="admin")
        recurso_ancla = crear_recurso(db, laboratorio=laboratorio, usuario=admin, nombre="Recurso Ancla")
        recurso_bajo_prueba = crear_recurso(db, laboratorio=laboratorio, usuario=admin, nombre="Recurso Bajo Prueba")
        reserva = _crear_reserva(db, usuario=admin, laboratorio=laboratorio, recurso=recurso_ancla)
        db.add(ReservaRecurso(
            reserva_id=reserva.id, recurso_id=recurso_bajo_prueba.id, fecha=reserva.fecha,
            hora_inicio=reserva.hora_inicio, hora_fin=reserva.hora_fin, estado=reserva.estado,
        ))
        db.commit()

        db.delete(recurso_bajo_prueba)
        with pytest.raises(IntegrityError):
            db.commit()

    def test_eliminar_espacio_referenciada_es_rechazada_sin_cascada(self, db):
        """espacio_id tampoco tiene ondelete=CASCADE en reserva_espacios."""
        laboratorio = crear_laboratorio(db)
        admin = crear_usuario(db, username="admin_rz6", email="admin_rz6@example.com", rol="admin")
        recurso = crear_recurso(db, laboratorio=laboratorio, usuario=admin)
        reserva = _crear_reserva(db, usuario=admin, laboratorio=laboratorio, recurso=recurso)
        espacio = _crear_espacio(db, laboratorio=laboratorio, usuario=admin)
        db.add(ReservaEspacio(
            reserva_id=reserva.id, espacio_id=espacio.id, fecha=reserva.fecha,
            hora_inicio=reserva.hora_inicio, hora_fin=reserva.hora_fin, estado=reserva.estado,
        ))
        db.commit()

        db.delete(espacio)
        with pytest.raises(IntegrityError):
            db.commit()


class TestCreateAllIdempotente:
    def test_create_all_no_falla_al_ejecutarse_dos_veces(self):
        Base.metadata.create_all(bind=engine)
        Base.metadata.create_all(bind=engine)
