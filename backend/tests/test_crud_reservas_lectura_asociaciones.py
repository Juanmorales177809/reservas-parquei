# -*- coding: utf-8 -*-
"""Pruebas de la migración de lectura a las tablas de asociación (Fase 12C-5).

Objetivo: las consultas internas *por recurso* dejan de depender de la
columna histórica `Reserva.recurso_id` y leen `reserva_recursos` (la misma
tabla que sostiene la constraint `reserva_recursos_sin_solapamiento` y la
doble escritura de 12C-4d). El contrato público pasó a `recurso_ids`/
`zona_ids`/`recursos` (12C-6/12C-4e-schemas) -- `ReservaResponse` ya no
expone `recurso`/`recurso_id`. `Reserva.recurso` (la relación ORM) y
`Reserva.recurso_id` (la columna) siguen intactos a nivel de modelo; las
aserciones `.recurso.id` de este archivo ejercitan esa relación ORM
directamente (lazy-load vía la columna histórica), no la respuesta pública.

Los tests RED demuestran el vacío semántico: una consulta basada solo en la
columna histórica no ve la asociación cuando el recurso de una reserva vive
únicamente en `reserva_recursos` (escenario de filas divergentes solo
producible por manipulación directa de la base — la doble escritura y el
backfill mantienen columna y asociación idénticas para todos los flujos
legítimos).

PostgreSQL real únicamente: `reserva_recursos` y sus constraints EXCLUDE son
específicas de PostgreSQL.
"""

from datetime import time

import pytest
from fastapi import HTTPException

from app.crud.reservas import get_recurso_ids_reserva, get_reservas_bloqueantes
from app.migrations import migrate_resource_reservations
from app.models.reserva import Reserva
from app.models.reserva_recurso import ReservaRecurso
from app.schemas.reserva import ReservaCreate, ReservaUpdate
from app.services.reservas import actualizar_reserva, cambiar_estado, crear_reserva
from app.services.actores import columnas_actor
from tests.conftest import crear_espacio, crear_recurso, crear_usuario, fecha_habilitada


def _setup(db):
    espacio = crear_espacio(db)
    usuario = crear_usuario(db, username="lec_user", email="lec_user@example.com")
    admin = crear_usuario(db, username="lec_admin", email="lec_admin@example.com", rol="admin")
    return espacio, usuario, admin


def _crear_reserva_raw(db, *, usuario, espacio, recurso, fecha, estado="esperando"):
    reserva = Reserva(
        **columnas_actor(usuario),
        espacio_id=espacio.id,
        recurso_id=recurso.id,
        fecha=fecha,
        hora_inicio=time(8, 0),
        hora_fin=time(9, 0),
        estado=estado,
        asistentes=2,
    )
    db.add(reserva)
    db.commit()
    db.refresh(reserva)
    return reserva


def _asociar(db, *, reserva, recurso, fecha, hora_inicio=time(8, 0), hora_fin=time(9, 0), estado="esperando"):
    db.add(ReservaRecurso(
        reserva_id=reserva.id,
        recurso_id=recurso.id,
        fecha=fecha,
        hora_inicio=hora_inicio,
        hora_fin=hora_fin,
        estado=estado,
    ))
    db.commit()


def _crear_reserva_servicio(db, usuario, *, recurso_id, fecha, hora_inicio=time(8, 0), hora_fin=time(9, 0)):
    return crear_reserva(
        db,
        ReservaCreate(
            recurso_ids=[recurso_id], fecha=fecha,
            hora_inicio=hora_inicio, hora_fin=hora_fin, asistentes=2,
        ),
        usuario,
    )


class TestGetReservasBloqueantes:
    def test_considera_recurso_presente_solo_en_la_asociacion(self, db):
        """La consulta por recurso debe hacer JOIN contra reserva_recursos:
        una reserva cuyo recurso vive únicamente en la asociación (no en la
        columna histórica) debe detectarse como bloqueante para ese recurso."""
        espacio, usuario, admin = _setup(db)
        recurso_ancla = crear_recurso(db, espacio=espacio, usuario=admin, nombre="Ancla")
        recurso_bajo_prueba = crear_recurso(db, espacio=espacio, usuario=admin, nombre="Bajo Prueba")
        fecha = fecha_habilitada()
        reserva = _crear_reserva_raw(db, usuario=usuario, espacio=espacio, recurso=recurso_ancla, fecha=fecha)
        _asociar(db, reserva=reserva, recurso=recurso_bajo_prueba, fecha=fecha)

        bloqueantes = get_reservas_bloqueantes(db, recurso_bajo_prueba.id, fecha, time(8, 0), time(9, 0))

        assert [r.id for r in bloqueantes] == [reserva.id]

    def test_una_reserva_con_varias_filas_asociadas_se_retorna_una_vez(self, db):
        """Distinct: una reserva con varias filas de asociación (distintos
        recursos) aparece exactamente una vez al consultar por uno de ellos,
        aunque la fila de la columna histórica no coincida."""
        espacio, usuario, admin = _setup(db)
        recurso_ancla = crear_recurso(db, espacio=espacio, usuario=admin, nombre="Ancla")
        recurso_a = crear_recurso(db, espacio=espacio, usuario=admin, nombre="A")
        recurso_b = crear_recurso(db, espacio=espacio, usuario=admin, nombre="B")
        fecha = fecha_habilitada(dias=14)
        reserva = _crear_reserva_raw(db, usuario=usuario, espacio=espacio, recurso=recurso_ancla, fecha=fecha)
        _asociar(db, reserva=reserva, recurso=recurso_a, fecha=fecha)
        _asociar(db, reserva=reserva, recurso=recurso_b, fecha=fecha, hora_inicio=time(10, 0), hora_fin=time(11, 0))

        por_a = get_reservas_bloqueantes(db, recurso_a.id, fecha, time(8, 0), time(9, 0))
        por_b = get_reservas_bloqueantes(db, recurso_b.id, fecha, time(10, 0), time(11, 0))

        assert [r.id for r in por_a] == [reserva.id]
        assert [r.id for r in por_b] == [reserva.id]

    def test_estado_no_bloqueante_en_asociacion_no_bloquea(self, db):
        """La consulta replica la EXCLUDE de 12C-4c: filas de asociación en
        estados no bloqueantes (rechazada/cancelada) no bloquean."""
        espacio, usuario, admin = _setup(db)
        recurso_ancla = crear_recurso(db, espacio=espacio, usuario=admin, nombre="Ancla")
        recurso_bajo_prueba = crear_recurso(db, espacio=espacio, usuario=admin, nombre="Bajo Prueba")
        fecha = fecha_habilitada()
        reserva = _crear_reserva_raw(db, usuario=usuario, espacio=espacio, recurso=recurso_ancla, fecha=fecha)
        _asociar(db, reserva=reserva, recurso=recurso_bajo_prueba, fecha=fecha, estado="rechazada")

        assert get_reservas_bloqueantes(db, recurso_bajo_prueba.id, fecha, time(8, 0), time(9, 0)) == []

    def test_respeta_exclude_id(self, db):
        """Una reserva excluida explícitamente (exclude_id) no se reporta --
        mismo contrato que antes de la migración."""
        espacio, usuario, admin = _setup(db)
        recurso = crear_recurso(db, espacio=espacio, usuario=admin)
        fecha = fecha_habilitada(dias=16)
        reserva = _crear_reserva_raw(db, usuario=usuario, espacio=espacio, recurso=recurso, fecha=fecha)

        assert get_reservas_bloqueantes(
            db, recurso.id, fecha, time(8, 0), time(9, 0), exclude_id=reserva.id
        ) == []


class TestGetRecursosDeReserva:
    def test_devuelve_recurso_de_la_asociacion(self, db):
        espacio, usuario, admin = _setup(db)
        recurso_ancla = crear_recurso(db, espacio=espacio, usuario=admin, nombre="Ancla")
        recurso_asoc = crear_recurso(db, espacio=espacio, usuario=admin, nombre="Asoc")
        fecha = fecha_habilitada()
        reserva = _crear_reserva_raw(db, usuario=usuario, espacio=espacio, recurso=recurso_ancla, fecha=fecha)
        _asociar(db, reserva=reserva, recurso=recurso_asoc, fecha=fecha)

        assert get_recurso_ids_reserva(db, reserva.id) == [recurso_asoc.id]

    def test_devuelve_todos_con_distinct(self, db):
        espacio, usuario, admin = _setup(db)
        recurso_ancla = crear_recurso(db, espacio=espacio, usuario=admin, nombre="Ancla")
        recurso_a = crear_recurso(db, espacio=espacio, usuario=admin, nombre="A")
        recurso_b = crear_recurso(db, espacio=espacio, usuario=admin, nombre="B")
        fecha = fecha_habilitada(dias=18)
        reserva = _crear_reserva_raw(db, usuario=usuario, espacio=espacio, recurso=recurso_ancla, fecha=fecha)
        _asociar(db, reserva=reserva, recurso=recurso_a, fecha=fecha)
        _asociar(db, reserva=reserva, recurso=recurso_b, fecha=fecha, hora_inicio=time(10, 0), hora_fin=time(11, 0))

        assert sorted(get_recurso_ids_reserva(db, reserva.id)) == sorted([recurso_a.id, recurso_b.id])


class TestActualizarReservaLeeAsociacion:
    def test_validacion_de_solapamiento_usa_el_recurso_de_la_asociacion(self, db):
        """Al actualizar solo fecha/horas (sin cambiar recurso), el
        solapamiento debe validarse contra el recurso que la reserva tiene en
        `reserva_recursos`, no contra la columna histórica."""
        espacio, usuario, admin = _setup(db)
        recurso_x = crear_recurso(db, espacio=espacio, usuario=admin, nombre="X")
        recurso_y = crear_recurso(db, espacio=espacio, usuario=admin, nombre="Y")
        fecha_1 = fecha_habilitada()
        fecha_2 = fecha_habilitada(dias=12)

        reserva_1 = _crear_reserva_raw(db, usuario=usuario, espacio=espacio, recurso=recurso_x, fecha=fecha_1)
        _asociar(db, reserva=reserva_1, recurso=recurso_y, fecha=fecha_1)
        reserva_2 = _crear_reserva_servicio(
            db, usuario, recurso_id=recurso_y.id, fecha=fecha_2,
            hora_inicio=time(10, 0), hora_fin=time(11, 0),
        )
        assert reserva_2.id != reserva_1.id

        with pytest.raises(HTTPException) as exc:
            actualizar_reserva(
                db,
                reserva_1.id,
                ReservaUpdate(fecha=fecha_2, hora_inicio=time(10, 0), hora_fin=time(11, 0)),
                usuario,
            )
        assert exc.value.status_code == 409

        db.refresh(reserva_1)
        assert reserva_1.fecha == fecha_1
        assert reserva_1.recurso_id == recurso_x.id
        filas = db.query(ReservaRecurso).filter(ReservaRecurso.reserva_id == reserva_1.id).all()
        assert [(f.recurso_id, f.fecha) for f in filas] == [(recurso_y.id, fecha_1)]


class TestCambioEstadoCompatibilidad:
    def test_aprobar_resuelve_recurso_desde_la_asociacion(self, db):
        """Compatibilidad: aprobar una reserva sigue funcionando y resuelve
        el recurso para el chequeo de solapamiento desde la asociación."""
        espacio, usuario, admin = _setup(db)
        recurso = crear_recurso(db, espacio=espacio, usuario=admin)
        fecha = fecha_habilitada()
        reserva = _crear_reserva_servicio(db, usuario, recurso_id=recurso.id, fecha=fecha)

        cambiar_estado(db, reserva.id, "aprobada", admin)

        assert reserva.estado == "aprobada"
        fila = db.query(ReservaRecurso).filter(ReservaRecurso.reserva_id == reserva.id).one()
        assert fila.estado == "aprobada"


class TestCompatibilidadListados:
    def test_gestor_y_mis_reservas_devuelven_mismo_recurso(self, db):
        """Las respuestas públicas siguen construyéndose con la forma
        singular actual y devuelven el mismo recurso que la asociación."""
        from app.crud.reservas import (  # import local para no acoplar el módulo
            get_mis_reservas,
            get_reserva,
            get_reservas_gestion,
        )

        espacio, usuario, admin = _setup(db)
        recurso = crear_recurso(db, espacio=espacio, usuario=admin)
        gestor = crear_usuario(
            db, username="lec_gestor", email="lec_gestor@example.com",
            rol="gestor", espacio_id=espacio.id,
        )
        fecha = fecha_habilitada()
        reserva = _crear_reserva_servicio(db, usuario, recurso_id=recurso.id, fecha=fecha)

        gestionadas = get_reservas_gestion(db, None)
        assert [r.id for r in gestionadas] == [reserva.id]
        assert gestionadas[0].recurso.id == recurso.id

        misas = get_mis_reservas(db, usuario)
        assert [r.id for r in misas] == [reserva.id]
        assert misas[0].recurso.id == recurso.id

        individual = get_reserva(db, reserva.id)
        assert individual is not None
        assert individual.recurso.id == recurso.id

    def test_reserva_historica_backfilled_devuelve_mismo_recurso(self, db):
        """Compatibilidad con el backfill de 12C-4b: una reserva histórica
        devuelve exactamente el mismo recurso en la respuesta singular."""
        from app.crud.reservas import get_reserva

        espacio, usuario, admin = _setup(db)
        recurso = crear_recurso(db, espacio=espacio, usuario=admin)
        fecha = fecha_habilitada()
        reserva = _crear_reserva_raw(db, usuario=usuario, espacio=espacio, recurso=recurso, fecha=fecha)

        db.commit()
        migrate_resource_reservations()
        db.commit()
        db.expire_all()

        individual = get_reserva(db, reserva.id)
        assert individual is not None
        assert individual.recurso.id == recurso.id
        fila = db.query(ReservaRecurso).filter(ReservaRecurso.reserva_id == reserva.id).one()
        assert fila.recurso_id == recurso.id