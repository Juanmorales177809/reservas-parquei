# -*- coding: utf-8 -*-
"""Pruebas de la doble escritura controlada de `reserva_recursos` (Fase 12C-4d).

Al crear una `Reserva` singular o modificar su recurso, fecha, horas o
estado, `services/reservas.py` mantiene `reservas` y exactamente una fila
por reserva en `reserva_recursos`, con las columnas desnormalizadas
(`fecha`, `hora_inicio`, `hora_fin`, `estado`) y el `recurso_id`
sincronizados. En 12C-6 el contrato pasó a `recurso_ids`/`zona_ids`; estas
pruebas (regresión del flujo singular) crean y actualizan reservas a través
del eje `recurso_ids` y verifican que la invariante de una sola fila
sincronizada se mantiene bajo el nuevo mecanismo de reescritura de
asociaciones.

Estas pruebas ejercitan los servicios reales contra PostgreSQL real (nunca
SQLite): la doble escritura convive con las constraints `btree_gist`
`reservas_sin_solapamiento` (histórica) y `reserva_recursos_sin_solapamiento`
(Fase 12C-4c), que solo existen en PostgreSQL.
"""

from datetime import time

import pytest
from fastapi import HTTPException
from sqlalchemy import text

from app.migrations import migrate_resource_reservations
from app.models.reserva import Reserva
from app.models.reserva_recurso import ReservaRecurso
from app.models.reserva_zona import ReservaZona
from app.schemas.reserva import ReservaCreate, ReservaUpdate
from app.services.reservas import (
    actualizar_reserva,
    cambiar_estado,
    cancelar_reserva_usuario,
    crear_reserva,
)
from tests.conftest import crear_espacio, crear_recurso, crear_usuario, fecha_habilitada


def _setup(db, *, rol="usuario", es_gestor_del_espacio=False):
    espacio = crear_espacio(db)
    usuario = crear_usuario(
        db,
        username=f"dd_{rol}_{es_gestor_del_espacio}",
        email=f"dd_{rol}_{es_gestor_del_espacio}@example.com",
        rol=rol,
        espacio_id=espacio.id if (rol == "gestor" and es_gestor_del_espacio) else None,
    )
    recurso = crear_recurso(db, espacio=espacio, usuario=usuario)
    return usuario, espacio, recurso


def _crear_reserva_servicio(
    db,
    usuario,
    *,
    recurso_id,
    fecha,
    hora_inicio=time(8, 0),
    hora_fin=time(9, 0),
    asistentes=2,
):
    return crear_reserva(
        db,
        ReservaCreate(
            recurso_ids=[recurso_id],
            fecha=fecha,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            asistentes=asistentes,
        ),
        usuario,
    )


def _invariantes(
    db,
    reserva_id,
    *,
    recurso_id,
    fecha,
    hora_inicio,
    hora_fin,
    estado,
    total_filas=None,
):
    """Invariante obligatoria de 12C-4d: exactamente una fila por reserva y
    coincidencia exacta de `recurso_id`, `fecha`, `hora_inicio`, `hora_fin`
    y `estado` entre `reservas` y `reserva_recursos`."""
    fila = db.query(ReservaRecurso).filter(ReservaRecurso.reserva_id == reserva_id).one()
    reserva = db.query(Reserva).filter(Reserva.id == reserva_id).one()
    assert (fila.recurso_id, fila.fecha, fila.hora_inicio, fila.hora_fin, fila.estado) == (
        recurso_id, fecha, hora_inicio, hora_fin, estado,
    )
    assert (reserva.recurso_id, reserva.fecha, reserva.hora_inicio, reserva.hora_fin, reserva.estado) == (
        recurso_id, fecha, hora_inicio, hora_fin, estado,
    )
    assert db.query(ReservaRecurso).filter(ReservaRecurso.reserva_id == reserva_id).count() == 1
    if total_filas is not None:
        assert db.query(ReservaRecurso).count() == total_filas


class TestCreacion:
    def test_crear_reserva_escribe_exactamente_una_fila_sincronizada(self, db):
        usuario, _, recurso = _setup(db)
        fecha = fecha_habilitada()
        reserva = _crear_reserva_servicio(db, usuario, recurso_id=recurso.id, fecha=fecha)

        _invariantes(
            db, reserva.id,
            recurso_id=recurso.id, fecha=fecha,
            hora_inicio=time(8, 0), hora_fin=time(9, 0), estado="esperando",
            total_filas=1,
        )

    def test_crear_aprobada_sincroniza_estado(self, db):
        usuario, _, recurso = _setup(db, rol="gestor", es_gestor_del_espacio=True)
        fecha = fecha_habilitada()
        reserva = _crear_reserva_servicio(db, usuario, recurso_id=recurso.id, fecha=fecha)

        assert reserva.estado == "aprobada"
        _invariantes(
            db, reserva.id,
            recurso_id=recurso.id, fecha=fecha,
            hora_inicio=time(8, 0), hora_fin=time(9, 0), estado="aprobada",
            total_filas=1,
        )

    def test_crear_no_escribe_en_reserva_zonas(self, db):
        """No se habilita reserva solo por zona en esta subfase:
        la creación de una reserva de recurso no produce ninguna fila en
        `reserva_zonas`."""
        usuario, _, recurso = _setup(db)
        _crear_reserva_servicio(db, usuario, recurso_id=recurso.id, fecha=fecha_habilitada())

        assert db.query(ReservaRecurso).count() == 1
        assert db.query(ReservaZona).count() == 0


class TestActualizarRecurso:
    def test_cambiar_recurso_sincroniza_recurso_id_sin_duplicar_fila(self, db):
        usuario, espacio, recurso_a = _setup(db)
        recurso_b = crear_recurso(db, espacio=espacio, usuario=usuario, nombre="Recurso B")
        fecha = fecha_habilitada()
        reserva = _crear_reserva_servicio(db, usuario, recurso_id=recurso_a.id, fecha=fecha)

        actualizada = actualizar_reserva(db, reserva.id, ReservaUpdate(recurso_ids=[recurso_b.id]), usuario)

        assert actualizada.recurso_id == recurso_b.id
        _invariantes(
            db, reserva.id,
            recurso_id=recurso_b.id, fecha=fecha,
            hora_inicio=time(8, 0), hora_fin=time(9, 0), estado="esperando",
            total_filas=1,
        )


class TestActualizarFechaHora:
    def test_cambiar_fecha_y_horas_sincroniza(self, db):
        usuario, _, recurso = _setup(db)
        reserva = _crear_reserva_servicio(
            db, usuario, recurso_id=recurso.id, fecha=fecha_habilitada(),
            hora_inicio=time(8, 0), hora_fin=time(9, 0),
        )
        nueva_fecha = fecha_habilitada(dias=12)

        actualizada = actualizar_reserva(
            db,
            reserva.id,
            ReservaUpdate(fecha=nueva_fecha, hora_inicio=time(9, 0), hora_fin=time(11, 0)),
            usuario,
        )

        assert actualizada.fecha == nueva_fecha
        _invariantes(
            db, reserva.id,
            recurso_id=recurso.id, fecha=nueva_fecha,
            hora_inicio=time(9, 0), hora_fin=time(11, 0), estado="esperando",
            total_filas=1,
        )

    def test_cambiar_solo_asistentes_no_desincroniza_la_fila(self, db):
        usuario, _, recurso = _setup(db)
        fecha = fecha_habilitada()
        reserva = _crear_reserva_servicio(db, usuario, recurso_id=recurso.id, fecha=fecha)

        actualizada = actualizar_reserva(db, reserva.id, ReservaUpdate(asistentes=5), usuario)

        assert actualizada.asistentes == 5
        _invariantes(
            db, reserva.id,
            recurso_id=recurso.id, fecha=fecha,
            hora_inicio=time(8, 0), hora_fin=time(9, 0), estado="esperando",
            total_filas=1,
        )


class TestCambioEstado:
    def _setup_gestor(self, db, espacio):
        return crear_usuario(
            db,
            username="dd_gestor_estado",
            email="dd_gestor_estado@example.com",
            rol="gestor",
            espacio_id=espacio.id,
        )

    def test_aprobar_sincroniza_estado(self, db):
        usuario, espacio, recurso = _setup(db)
        gestor = self._setup_gestor(db, espacio)
        fecha = fecha_habilitada()
        reserva = _crear_reserva_servicio(db, usuario, recurso_id=recurso.id, fecha=fecha)

        cambiar_estado(db, reserva.id, "aprobada", gestor)

        _invariantes(
            db, reserva.id,
            recurso_id=recurso.id, fecha=fecha,
            hora_inicio=time(8, 0), hora_fin=time(9, 0), estado="aprobada",
            total_filas=1,
        )

    def test_rechazar_sincroniza_estado(self, db):
        usuario, espacio, recurso = _setup(db)
        gestor = self._setup_gestor(db, espacio)
        fecha = fecha_habilitada()
        reserva = _crear_reserva_servicio(db, usuario, recurso_id=recurso.id, fecha=fecha)

        cambiar_estado(db, reserva.id, "rechazada", gestor)

        _invariantes(
            db, reserva.id,
            recurso_id=recurso.id, fecha=fecha,
            hora_inicio=time(8, 0), hora_fin=time(9, 0), estado="rechazada",
            total_filas=1,
        )

    def test_cancelar_por_usuario_sincroniza_estado(self, db):
        usuario, espacio, recurso = _setup(db)
        gestor = self._setup_gestor(db, espacio)
        fecha = fecha_habilitada()
        reserva = _crear_reserva_servicio(db, usuario, recurso_id=recurso.id, fecha=fecha)
        cambiar_estado(db, reserva.id, "aprobada", gestor)

        cancelar_reserva_usuario(db, reserva.id, usuario)

        _invariantes(
            db, reserva.id,
            recurso_id=recurso.id, fecha=fecha,
            hora_inicio=time(8, 0), hora_fin=time(9, 0), estado="cancelada",
            total_filas=1,
        )


class TestSolapamiento:
    def test_creacion_con_solapamiento_da_409_sin_filas_parciales(self, db):
        """El solapamiento clásico (`reservas_sin_solapamiento`, validado por
        el servicio contra `reservas`) sigue devolviendo 409 y no deja ninguna
        fila parcial: ni una reserva extra ni una fila de asociación huérfana."""
        usuario, _, recurso = _setup(db)
        fecha = fecha_habilitada()
        _crear_reserva_servicio(db, usuario, recurso_id=recurso.id, fecha=fecha)

        with pytest.raises(HTTPException) as exc:
            _crear_reserva_servicio(db, usuario, recurso_id=recurso.id, fecha=fecha)
        assert exc.value.status_code == 409

        assert db.query(Reserva).count() == 1
        assert db.query(ReservaRecurso).count() == 1

    def test_actualizacion_con_solapamiento_da_409(self, db):
        """Actualizar una reserva hacia un horario que solapa otra reserva
        sigue devolviendo 409 (validación de servicio sobre `reservas`) y no
        deja cambios parciales."""
        usuario, _, recurso = _setup(db)
        fecha = fecha_habilitada()
        _crear_reserva_servicio(db, usuario, recurso_id=recurso.id, fecha=fecha)
        segunda = _crear_reserva_servicio(
            db, usuario, recurso_id=recurso.id, fecha=fecha,
            hora_inicio=time(10, 0), hora_fin=time(11, 0),
        )

        with pytest.raises(HTTPException) as exc:
            actualizar_reserva(
                db,
                segunda.id,
                ReservaUpdate(hora_inicio=time(8, 0), hora_fin=time(10, 0)),
                usuario,
            )
        assert exc.value.status_code == 409

        db.refresh(segunda)
        assert segunda.hora_inicio == time(10, 0)
        assert db.query(ReservaRecurso).count() == 2

    def test_creacion_bloqueada_por_la_constraint_nueva_no_deja_filas_parciales(self, db):
        """Ejercita el EXCLUDE `reserva_recursos_sin_solapamiento` (Fase
        12C-4c) a través del servicio: una fila manual en `reserva_recursos`
        sin equivalente en `reservas` bloquea crear una reserva del mismo
        recurso y horario. Desde 12C-6 la validación de servicio ya lee
        `reserva_recursos` y el 409 lo produce el propio servicio; la
        constraint de la base queda como segunda línea de defensa. En ambos
        casos la transacción entera debe revertirse (sin filas parciales)."""
        usuario, espacio, recurso_ancla = _setup(db)
        recurso_bajo_prueba = crear_recurso(db, espacio=espacio, usuario=usuario, nombre="Bajo Prueba")
        fecha = fecha_habilitada()
        ancla = _crear_reserva_servicio(db, usuario, recurso_id=recurso_ancla.id, fecha=fecha)
        db.add(ReservaRecurso(
            reserva_id=ancla.id,
            recurso_id=recurso_bajo_prueba.id,
            fecha=fecha,
            hora_inicio=time(8, 0),
            hora_fin=time(9, 0),
            estado="esperando",
        ))
        db.commit()

        with pytest.raises(HTTPException) as exc:
            _crear_reserva_servicio(db, usuario, recurso_id=recurso_bajo_prueba.id, fecha=fecha)
        assert exc.value.status_code == 409

        assert db.query(Reserva).count() == 1
        assert db.query(ReservaRecurso).count() == 2  # la fila sincronizada del ancla + la manual
        assert db.query(ReservaRecurso).filter(ReservaRecurso.reserva_id == ancla.id).count() == 2

    def test_actualizacion_bloqueada_por_la_constraint_nueva_da_409_sin_cambios(self, db):
        """Mismo escenario vía `actualizar_reserva`: pasar una reserva a un
        recurso/horario ocupado solo en `reserva_recursos` debe fallar con
        409 y revertir completo (la reserva conserva su recurso y horario
        originales en ambas tablas)."""
        usuario, espacio, recurso_ancla = _setup(db)
        recurso_bajo_prueba = crear_recurso(db, espacio=espacio, usuario=usuario, nombre="Bajo Prueba")
        fecha = fecha_habilitada()
        ancla = _crear_reserva_servicio(db, usuario, recurso_id=recurso_ancla.id, fecha=fecha)
        reserva_b = _crear_reserva_servicio(
            db, usuario, recurso_id=recurso_ancla.id, fecha=fecha,
            hora_inicio=time(10, 0), hora_fin=time(11, 0),
        )
        db.add(ReservaRecurso(
            reserva_id=ancla.id,
            recurso_id=recurso_bajo_prueba.id,
            fecha=fecha,
            hora_inicio=time(8, 0),
            hora_fin=time(9, 0),
            estado="esperando",
        ))
        db.commit()

        with pytest.raises(HTTPException) as exc:
            actualizar_reserva(
                db,
                reserva_b.id,
                ReservaUpdate(
                    recurso_ids=[recurso_bajo_prueba.id],
                    fecha=fecha,
                    hora_inicio=time(8, 0),
                    hora_fin=time(9, 0),
                ),
                usuario,
            )
        assert exc.value.status_code == 409

        db.refresh(reserva_b)
        assert reserva_b.recurso_id == recurso_ancla.id
        assert (reserva_b.fecha, reserva_b.hora_inicio, reserva_b.hora_fin) == (
            fecha, time(10, 0), time(11, 0),
        )
        _invariantes(
            db, reserva_b.id,
            recurso_id=recurso_ancla.id, fecha=fecha,
            hora_inicio=time(10, 0), hora_fin=time(11, 0), estado="esperando",
        )


class TestReservaHistoricaBackfilled:
    def test_reserva_historica_backfilled_no_se_duplica_al_actualizarla(self, db):
        """Una reserva creada por ORM crudo (sin doble escritura) y backfillada
        por `migrate_resource_reservations()` (12C-4b) conserva su única fila:
        al actualizarla por el servicio, la fila existente se actualiza en
        lugar de crearse una nueva."""
        espacio = crear_espacio(db)
        admin = crear_usuario(db, username="dd_hist_bk", email="dd_hist_bk@example.com", rol="admin")
        recurso = crear_recurso(db, espacio=espacio, usuario=admin)
        fecha = fecha_habilitada()
        reserva = Reserva(
            usuario_id=admin.id,
            espacio_id=espacio.id,
            recurso_id=recurso.id,
            fecha=fecha,
            hora_inicio=time(8, 0),
            hora_fin=time(9, 0),
            estado="esperando",
            asistentes=2,
        )
        db.add(reserva)
        db.commit()
        db.refresh(reserva)

        db.commit()
        migrate_resource_reservations()
        db.commit()
        db.expire_all()

        assert db.query(ReservaRecurso).filter(ReservaRecurso.reserva_id == reserva.id).count() == 1

        nueva_fecha = fecha_habilitada(dias=12)
        actualizada = actualizar_reserva(db, reserva.id, ReservaUpdate(fecha=nueva_fecha), admin)

        assert actualizada.fecha == nueva_fecha
        _invariantes(
            db, reserva.id,
            recurso_id=recurso.id, fecha=nueva_fecha,
            hora_inicio=time(8, 0), hora_fin=time(9, 0), estado="esperando",
            total_filas=1,
        )


class TestInvariantesExactas:
    def test_ciclo_completo_mantiene_invariantes_en_cada_paso(self, db):
        """Ciclo de vida completo (crear → cambiar recurso → cambiar
        fecha/horas → aprobar → cancelar) mantiene la invariante de
        exactamente una fila sincronizada en cada paso."""
        usuario, espacio, recurso_a = _setup(db)
        recurso_b = crear_recurso(db, espacio=espacio, usuario=usuario, nombre="Recurso B")
        gestor = crear_usuario(
            db,
            username="dd_gestor_inv",
            email="dd_gestor_inv@example.com",
            rol="gestor",
            espacio_id=espacio.id,
        )
        fecha = fecha_habilitada()

        reserva = _crear_reserva_servicio(db, usuario, recurso_id=recurso_a.id, fecha=fecha)
        _invariantes(
            db, reserva.id,
            recurso_id=recurso_a.id, fecha=fecha,
            hora_inicio=time(8, 0), hora_fin=time(9, 0), estado="esperando",
        )

        actualizar_reserva(db, reserva.id, ReservaUpdate(recurso_ids=[recurso_b.id]), usuario)
        _invariantes(
            db, reserva.id,
            recurso_id=recurso_b.id, fecha=fecha,
            hora_inicio=time(8, 0), hora_fin=time(9, 0), estado="esperando",
        )

        nueva_fecha = fecha_habilitada(dias=12)
        actualizar_reserva(
            db,
            reserva.id,
            ReservaUpdate(fecha=nueva_fecha, hora_inicio=time(9, 0), hora_fin=time(11, 0)),
            usuario,
        )
        _invariantes(
            db, reserva.id,
            recurso_id=recurso_b.id, fecha=nueva_fecha,
            hora_inicio=time(9, 0), hora_fin=time(11, 0), estado="esperando",
        )

        cambiar_estado(db, reserva.id, "aprobada", gestor)
        _invariantes(
            db, reserva.id,
            recurso_id=recurso_b.id, fecha=nueva_fecha,
            hora_inicio=time(9, 0), hora_fin=time(11, 0), estado="aprobada",
        )

        cancelar_reserva_usuario(db, reserva.id, usuario)
        _invariantes(
            db, reserva.id,
            recurso_id=recurso_b.id, fecha=nueva_fecha,
            hora_inicio=time(9, 0), hora_fin=time(11, 0), estado="cancelada",
            total_filas=1,
        )


class TestAusenciaDeBloqueos:
    def test_operaciones_no_dejan_sesiones_bloqueadas_ni_idle_in_transaction(self, db):
        """Tras un ciclo completo de doble escritura, ninguna conexión queda
        'idle in transaction' ni esperando un lock (mismo chequeo que el test
        de migración de 12C-4b/12C-4c, ahora para las operaciones de
        servicio)."""
        usuario, espacio, recurso = _setup(db)
        gestor = crear_usuario(
            db,
            username="dd_gestor_lock",
            email="dd_gestor_lock@example.com",
            rol="gestor",
            espacio_id=espacio.id,
        )
        fecha = fecha_habilitada()
        reserva = _crear_reserva_servicio(db, usuario, recurso_id=recurso.id, fecha=fecha)
        actualizar_reserva(
            db,
            reserva.id,
            ReservaUpdate(hora_inicio=time(9, 0), hora_fin=time(10, 0)),
            usuario,
        )
        cambiar_estado(db, reserva.id, "aprobada", gestor)
        cancelar_reserva_usuario(db, reserva.id, usuario)

        db.commit()
        bloqueadas = db.execute(text("""
            SELECT pid, state, wait_event_type
            FROM pg_stat_activity
            WHERE datname = current_database()
              AND pid != pg_backend_pid()
              AND (state = 'idle in transaction' OR wait_event_type = 'Lock')
        """)).fetchall()
        assert bloqueadas == [], f"sesiones bloqueadas/idle-in-transaction: {bloqueadas}"