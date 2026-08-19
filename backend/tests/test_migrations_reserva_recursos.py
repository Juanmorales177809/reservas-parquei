# -*- coding: utf-8 -*-
"""Pruebas del backfill idempotente de reserva_recursos (Fase 12C-4b) y de
las constraints EXCLUDE de reserva_recursos/reserva_zonas (Fase 12C-4c).

Alcance de 12C-4b: `migrate_resource_reservations()` puebla
`reserva_recursos` a partir de `Reserva.recurso_id` para toda reserva
existente, y aborta con una excepción real de PostgreSQL si detecta
alguna reserva sin fila asociada tras el backfill.

Alcance de 12C-4c: la misma función agrega `reserva_recursos_sin_solapamiento`
y `reserva_zonas_sin_solapamiento` (EXCLUDE USING gist, mismo patrón que
`reservas_sin_solapamiento`). NINGÚN consumidor lee todavía desde estas
tablas (sin doble escritura, sin lectura desde servicios/CRUD);
`Reserva.recurso_id`, sus índices y `reservas_sin_solapamiento` no se
tocan.

Nota de aislamiento de conexión: `migrate_resource_reservations()` abre su
propia conexión sobre `app.db.engine` y ejecuta `ALTER TABLE ... ADD
COLUMN IF NOT EXISTS` (idempotente, pero de todos modos exige un lock
ACCESS EXCLUSIVE sobre `reservas` en PostgreSQL). La sesión `db` de estos
tests es una conexión aparte: si queda con una transacción implícita
abierta (por ejemplo, tras un `.query()` o `.refresh()` sin commit) en el
momento de llamar a `migrate_resource_reservations()`, esa transacción
bloquea el `ALTER TABLE` y el test se cuelga esperando un lock que su
propio hilo nunca podrá liberar. Por eso cada llamada a
`migrate_resource_reservations()` en este archivo va precedida de un
`db.commit()` explícito.
"""

from datetime import date, time

import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.orm import Session

from app.migrations import _GATE_RESERVA_RECURSOS_COMPLETO, migrate_resource_reservations
from app.models.reserva import Reserva
from app.models.reserva_recurso import ReservaRecurso
from app.models.reserva_zona import ReservaZona
from app.models.zona import Zona
from tests.conftest import crear_espacio, crear_recurso, crear_usuario


def _crear_zona(db: Session, *, espacio, usuario, nombre="Zona de pruebas"):
    zona = Zona(nombre=nombre, espacio_id=espacio.id, created_by=usuario.id, updated_by=usuario.id)
    db.add(zona)
    db.commit()
    db.refresh(zona)
    return zona


def _crear_reserva(db: Session, *, usuario, espacio, recurso, fecha=None, estado="esperando"):
    reserva = Reserva(
        usuario_id=usuario.id,
        espacio_id=espacio.id,
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


class TestBackfillPueblaReservaRecursos:
    def test_reserva_historica_sin_asociacion_previa_queda_backfillada(self, db):
        """Una reserva creada directamente (sin pasar por ningún backfill
        todavía) no tiene fila en reserva_recursos hasta que se ejecuta
        migrate_resource_reservations()."""
        espacio = crear_espacio(db)
        admin = crear_usuario(db, username="admin_bf1", email="admin_bf1@example.com", rol="admin")
        recurso = crear_recurso(db, espacio=espacio, usuario=admin)
        reserva = _crear_reserva(db, usuario=admin, espacio=espacio, recurso=recurso)

        assert db.query(ReservaRecurso).filter(ReservaRecurso.reserva_id == reserva.id).count() == 0

        db.commit()
        migrate_resource_reservations()

        filas = db.query(ReservaRecurso).filter(ReservaRecurso.reserva_id == reserva.id).all()
        assert len(filas) == 1
        assert filas[0].recurso_id == recurso.id
        assert filas[0].fecha == reserva.fecha
        assert filas[0].hora_inicio == reserva.hora_inicio
        assert filas[0].hora_fin == reserva.hora_fin
        assert filas[0].estado == reserva.estado

    def test_conserva_fecha_hora_estado_exactamente_para_varias_reservas(self, db):
        espacio = crear_espacio(db)
        admin = crear_usuario(db, username="admin_bf2", email="admin_bf2@example.com", rol="admin")
        recurso = crear_recurso(db, espacio=espacio, usuario=admin)
        r1 = _crear_reserva(db, usuario=admin, espacio=espacio, recurso=recurso, fecha=date(2026, 9, 1), estado="esperando")
        r2 = _crear_reserva(db, usuario=admin, espacio=espacio, recurso=recurso, fecha=date(2026, 9, 2), estado="aprobada")

        db.commit()
        migrate_resource_reservations()

        for reserva in (r1, r2):
            fila = (
                db.query(ReservaRecurso)
                .filter(ReservaRecurso.reserva_id == reserva.id)
                .one()
            )
            assert (fila.recurso_id, fila.fecha, fila.hora_inicio, fila.hora_fin, fila.estado) == (
                reserva.recurso_id, reserva.fecha, reserva.hora_inicio, reserva.hora_fin, reserva.estado,
            )

    def test_correspondencia_exacta_una_fila_por_reserva_ni_mas_ni_menos(self, db):
        espacio = crear_espacio(db)
        admin = crear_usuario(db, username="admin_bf3", email="admin_bf3@example.com", rol="admin")
        recurso = crear_recurso(db, espacio=espacio, usuario=admin)
        reservas = [
            _crear_reserva(db, usuario=admin, espacio=espacio, recurso=recurso, fecha=date(2026, 9, dia))
            for dia in (1, 2, 3)
        ]

        db.commit()
        migrate_resource_reservations()

        total_reservas = db.query(Reserva).count()
        total_asociaciones = db.query(ReservaRecurso).count()
        assert total_asociaciones == total_reservas == len(reservas)
        for reserva in reservas:
            assert db.query(ReservaRecurso).filter(ReservaRecurso.reserva_id == reserva.id).count() == 1

    def test_no_modifica_la_tabla_reservas(self, db):
        """El backfill es puramente aditivo hacia reserva_recursos --
        Reserva conserva sus valores exactos (recurso_id incluido)."""
        espacio = crear_espacio(db)
        admin = crear_usuario(db, username="admin_bf4", email="admin_bf4@example.com", rol="admin")
        recurso = crear_recurso(db, espacio=espacio, usuario=admin)
        reserva = _crear_reserva(db, usuario=admin, espacio=espacio, recurso=recurso)
        antes = (reserva.recurso_id, reserva.fecha, reserva.hora_inicio, reserva.hora_fin, reserva.estado, reserva.asistentes)

        db.commit()
        migrate_resource_reservations()

        db.refresh(reserva)
        despues = (reserva.recurso_id, reserva.fecha, reserva.hora_inicio, reserva.hora_fin, reserva.estado, reserva.asistentes)
        assert antes == despues


class TestIdempotencia:
    def test_ejecutar_dos_veces_no_duplica_filas(self, db):
        espacio = crear_espacio(db)
        admin = crear_usuario(db, username="admin_bf5", email="admin_bf5@example.com", rol="admin")
        recurso = crear_recurso(db, espacio=espacio, usuario=admin)
        reserva = _crear_reserva(db, usuario=admin, espacio=espacio, recurso=recurso)

        db.commit()
        migrate_resource_reservations()
        primera_cuenta = db.query(ReservaRecurso).filter(ReservaRecurso.reserva_id == reserva.id).count()

        db.commit()
        migrate_resource_reservations()
        segunda_cuenta = db.query(ReservaRecurso).filter(ReservaRecurso.reserva_id == reserva.id).count()

        assert primera_cuenta == 1
        assert segunda_cuenta == 1

    def test_ejecutar_tres_veces_conserva_conteo_total_estable(self, db):
        espacio = crear_espacio(db)
        admin = crear_usuario(db, username="admin_bf6", email="admin_bf6@example.com", rol="admin")
        recurso = crear_recurso(db, espacio=espacio, usuario=admin)
        for dia in (1, 2, 3, 4):
            _crear_reserva(db, usuario=admin, espacio=espacio, recurso=recurso, fecha=date(2026, 9, dia))

        db.commit()
        migrate_resource_reservations()
        cuenta_1 = db.query(ReservaRecurso).count()
        db.commit()
        migrate_resource_reservations()
        cuenta_2 = db.query(ReservaRecurso).count()
        db.commit()
        migrate_resource_reservations()
        cuenta_3 = db.query(ReservaRecurso).count()

        assert cuenta_1 == cuenta_2 == cuenta_3 == 4


class TestGateDeCobertura:
    def test_gate_pasa_cuando_el_backfill_esta_completo(self, db):
        espacio = crear_espacio(db)
        admin = crear_usuario(db, username="admin_bf7", email="admin_bf7@example.com", rol="admin")
        recurso = crear_recurso(db, espacio=espacio, usuario=admin)
        _crear_reserva(db, usuario=admin, espacio=espacio, recurso=recurso)

        db.commit()
        # No debe lanzar: migrate_resource_reservations() ya deja el
        # backfill completo antes de que el gate se ejecute.
        migrate_resource_reservations()

    def test_gate_detecta_una_reserva_sin_fila_asociada(self, db):
        """Simula la pérdida de una asociación ya backfillada (escenario
        que el backfill actual no puede producir por sí mismo, ya que
        Reserva.recurso_id es NOT NULL y el backfill cubre todo -- pero
        que el gate debe seguir detectando si alguna vez ocurriera). Se
        ejecuta el gate de forma AISLADA (no la función completa, que lo
        sanaría de inmediato al re-insertar la fila antes de llegar al
        gate)."""
        espacio = crear_espacio(db)
        admin = crear_usuario(db, username="admin_bf8", email="admin_bf8@example.com", rol="admin")
        recurso = crear_recurso(db, espacio=espacio, usuario=admin)
        reserva = _crear_reserva(db, usuario=admin, espacio=espacio, recurso=recurso)

        db.commit()
        migrate_resource_reservations()
        db.execute(text("DELETE FROM reserva_recursos WHERE reserva_id = :id"), {"id": reserva.id})
        db.commit()

        with pytest.raises(DBAPIError):
            db.execute(text(_GATE_RESERVA_RECURSOS_COMPLETO))
        db.rollback()


class TestNoAfectaElEsquemaHistorico:
    def test_recurso_id_indices_y_exclusion_siguen_intactos(self, db):
        espacio = crear_espacio(db)
        admin = crear_usuario(db, username="admin_bf9", email="admin_bf9@example.com", rol="admin")
        recurso = crear_recurso(db, espacio=espacio, usuario=admin)
        _crear_reserva(db, usuario=admin, espacio=espacio, recurso=recurso)

        db.commit()
        migrate_resource_reservations()

        columnas = [
            fila[0]
            for fila in db.execute(text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_schema = 'public' AND table_name = 'reservas'"
            )).fetchall()
        ]
        assert "recurso_id" in columnas

        indices = {
            fila[0]
            for fila in db.execute(text(
                "SELECT indexname FROM pg_indexes WHERE tablename = 'reservas'"
            )).fetchall()
        }
        assert "ix_reservas_recurso_id" in indices
        assert "ix_reservas_recurso_fecha_estado" in indices

        constraints = {
            fila[0]
            for fila in db.execute(text(
                "SELECT conname FROM pg_constraint WHERE conname = 'reservas_sin_solapamiento'"
            )).fetchall()
        }
        assert "reservas_sin_solapamiento" in constraints

    def test_reserva_recursos_solo_contiene_filas_de_backfill_ninguna_extra(self, db):
        """No hay doble escritura todavía: el único origen de filas en
        reserva_recursos en esta subfase es el backfill de
        migrate_resource_reservations(), nunca services/reservas.py
        (que no fue tocado)."""
        espacio = crear_espacio(db)
        admin = crear_usuario(db, username="admin_bf10", email="admin_bf10@example.com", rol="admin")
        recurso = crear_recurso(db, espacio=espacio, usuario=admin)
        reserva = _crear_reserva(db, usuario=admin, espacio=espacio, recurso=recurso)

        db.commit()
        migrate_resource_reservations()

        total = db.query(ReservaRecurso).count()
        assert total == 1
        fila = db.query(ReservaRecurso).one()
        assert fila.reserva_id == reserva.id


class TestConstraintsExcludeSolapamiento:
    """Fase 12C-4c: reserva_recursos_sin_solapamiento y
    reserva_zonas_sin_solapamiento. Las filas de prueba se insertan
    directamente en las tablas de asociación (no vía backfill) para
    controlar con precisión los escenarios de solapamiento -- consistente
    con que estas tablas siguen desnormalizadas y sin sincronizar (ver
    docstring del módulo).

    Cada reserva usa un "recurso ancla" distinto del/los recurso(s) bajo
    prueba para satisfacer el NOT NULL de la columna vieja
    Reserva.recurso_id: el backfill de 12C-4b crea automáticamente una
    fila (reserva_id, recurso_ancla_id) en reserva_recursos para cada
    reserva creada -- si el recurso bajo prueba fuera el mismo que el
    ancla, la fila manual insertada por el test colisionaría con la del
    backfill en la UniqueConstraint(reserva_id, recurso_id), enmascarando
    la prueba de la constraint EXCLUDE que en realidad se quiere
    ejercitar."""

    def test_constraint_de_recurso_bloquea_solapamiento(self, db):
        espacio = crear_espacio(db)
        admin = crear_usuario(db, username="admin_ex1", email="admin_ex1@example.com", rol="admin")
        recurso_ancla = crear_recurso(db, espacio=espacio, usuario=admin, nombre="Recurso Ancla 1")
        recurso = crear_recurso(db, espacio=espacio, usuario=admin, nombre="Recurso Bajo Prueba 1")
        r1 = _crear_reserva(db, usuario=admin, espacio=espacio, recurso=recurso_ancla)
        r2 = _crear_reserva(db, usuario=admin, espacio=espacio, recurso=recurso_ancla, fecha=date(2026, 9, 5))

        db.commit()
        migrate_resource_reservations()

        db.add(ReservaRecurso(
            reserva_id=r1.id, recurso_id=recurso.id, fecha=date(2026, 9, 10),
            hora_inicio=time(8, 0), hora_fin=time(9, 0), estado="esperando",
        ))
        db.commit()

        db.add(ReservaRecurso(
            reserva_id=r2.id, recurso_id=recurso.id, fecha=date(2026, 9, 10),
            hora_inicio=time(8, 30), hora_fin=time(9, 30), estado="aprobada",
        ))
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()

    def test_constraint_de_recurso_permite_intervalos_adyacentes(self, db):
        espacio = crear_espacio(db)
        admin = crear_usuario(db, username="admin_ex2", email="admin_ex2@example.com", rol="admin")
        recurso_ancla = crear_recurso(db, espacio=espacio, usuario=admin, nombre="Recurso Ancla 2")
        recurso = crear_recurso(db, espacio=espacio, usuario=admin, nombre="Recurso Bajo Prueba 2")
        r1 = _crear_reserva(db, usuario=admin, espacio=espacio, recurso=recurso_ancla)
        r2 = _crear_reserva(db, usuario=admin, espacio=espacio, recurso=recurso_ancla, fecha=date(2026, 9, 5))

        db.commit()
        migrate_resource_reservations()

        db.add(ReservaRecurso(
            reserva_id=r1.id, recurso_id=recurso.id, fecha=date(2026, 9, 11),
            hora_inicio=time(8, 0), hora_fin=time(9, 0), estado="esperando",
        ))
        db.add(ReservaRecurso(
            reserva_id=r2.id, recurso_id=recurso.id, fecha=date(2026, 9, 11),
            hora_inicio=time(9, 0), hora_fin=time(10, 0), estado="esperando",
        ))
        db.commit()  # no debe lanzar: [8-9) y [9-10) no se superponen

        total = db.query(ReservaRecurso).filter(ReservaRecurso.fecha == date(2026, 9, 11)).count()
        assert total == 2

    def test_constraint_de_recurso_ignora_estados_no_bloqueantes(self, db):
        espacio = crear_espacio(db)
        admin = crear_usuario(db, username="admin_ex3", email="admin_ex3@example.com", rol="admin")
        recurso_ancla = crear_recurso(db, espacio=espacio, usuario=admin, nombre="Recurso Ancla 3")
        recurso = crear_recurso(db, espacio=espacio, usuario=admin, nombre="Recurso Bajo Prueba 3")
        r1 = _crear_reserva(db, usuario=admin, espacio=espacio, recurso=recurso_ancla)
        r2 = _crear_reserva(db, usuario=admin, espacio=espacio, recurso=recurso_ancla, fecha=date(2026, 9, 5))

        db.commit()
        migrate_resource_reservations()

        db.add(ReservaRecurso(
            reserva_id=r1.id, recurso_id=recurso.id, fecha=date(2026, 9, 12),
            hora_inicio=time(8, 0), hora_fin=time(9, 0), estado="rechazada",
        ))
        db.add(ReservaRecurso(
            reserva_id=r2.id, recurso_id=recurso.id, fecha=date(2026, 9, 12),
            hora_inicio=time(8, 0), hora_fin=time(9, 0), estado="cancelada",
        ))
        db.commit()  # no debe lanzar: ninguno de los dos estados bloquea

        total = db.query(ReservaRecurso).filter(ReservaRecurso.fecha == date(2026, 9, 12)).count()
        assert total == 2

    def test_constraint_de_recurso_permite_recursos_distintos(self, db):
        espacio = crear_espacio(db)
        admin = crear_usuario(db, username="admin_ex4", email="admin_ex4@example.com", rol="admin")
        recurso_ancla = crear_recurso(db, espacio=espacio, usuario=admin, nombre="Recurso Ancla 4")
        recurso_a = crear_recurso(db, espacio=espacio, usuario=admin, nombre="Recurso A")
        recurso_b = crear_recurso(db, espacio=espacio, usuario=admin, nombre="Recurso B")
        r1 = _crear_reserva(db, usuario=admin, espacio=espacio, recurso=recurso_ancla)
        r2 = _crear_reserva(db, usuario=admin, espacio=espacio, recurso=recurso_ancla, fecha=date(2026, 9, 5))

        db.commit()
        migrate_resource_reservations()

        db.add(ReservaRecurso(
            reserva_id=r1.id, recurso_id=recurso_a.id, fecha=date(2026, 9, 13),
            hora_inicio=time(8, 0), hora_fin=time(9, 0), estado="esperando",
        ))
        db.add(ReservaRecurso(
            reserva_id=r2.id, recurso_id=recurso_b.id, fecha=date(2026, 9, 13),
            hora_inicio=time(8, 0), hora_fin=time(9, 0), estado="esperando",
        ))
        db.commit()  # no debe lanzar: recursos distintos

        total = db.query(ReservaRecurso).filter(ReservaRecurso.fecha == date(2026, 9, 13)).count()
        assert total == 2

    def test_constraint_de_zona_bloquea_solapamiento(self, db):
        espacio = crear_espacio(db)
        admin = crear_usuario(db, username="admin_ex5", email="admin_ex5@example.com", rol="admin")
        recurso = crear_recurso(db, espacio=espacio, usuario=admin)
        zona = _crear_zona(db, espacio=espacio, usuario=admin)
        r1 = _crear_reserva(db, usuario=admin, espacio=espacio, recurso=recurso)
        r2 = _crear_reserva(db, usuario=admin, espacio=espacio, recurso=recurso, fecha=date(2026, 9, 5))

        db.commit()
        migrate_resource_reservations()

        db.add(ReservaZona(
            reserva_id=r1.id, zona_id=zona.id, fecha=date(2026, 9, 14),
            hora_inicio=time(8, 0), hora_fin=time(9, 0), estado="esperando",
        ))
        db.commit()

        db.add(ReservaZona(
            reserva_id=r2.id, zona_id=zona.id, fecha=date(2026, 9, 14),
            hora_inicio=time(8, 30), hora_fin=time(9, 30), estado="aprobada",
        ))
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()

    def test_constraint_de_zona_permite_zonas_distintas(self, db):
        espacio = crear_espacio(db)
        admin = crear_usuario(db, username="admin_ex6", email="admin_ex6@example.com", rol="admin")
        recurso = crear_recurso(db, espacio=espacio, usuario=admin)
        zona_a = _crear_zona(db, espacio=espacio, usuario=admin, nombre="Zona A")
        zona_b = _crear_zona(db, espacio=espacio, usuario=admin, nombre="Zona B")
        r1 = _crear_reserva(db, usuario=admin, espacio=espacio, recurso=recurso)
        r2 = _crear_reserva(db, usuario=admin, espacio=espacio, recurso=recurso, fecha=date(2026, 9, 5))

        db.commit()
        migrate_resource_reservations()

        db.add(ReservaZona(
            reserva_id=r1.id, zona_id=zona_a.id, fecha=date(2026, 9, 15),
            hora_inicio=time(8, 0), hora_fin=time(9, 0), estado="esperando",
        ))
        db.add(ReservaZona(
            reserva_id=r2.id, zona_id=zona_b.id, fecha=date(2026, 9, 15),
            hora_inicio=time(8, 0), hora_fin=time(9, 0), estado="esperando",
        ))
        db.commit()  # no debe lanzar: zonas distintas

        total = db.query(ReservaZona).filter(ReservaZona.fecha == date(2026, 9, 15)).count()
        assert total == 2

    def test_reserva_zona_y_reserva_recurso_coexisten_sin_validacion_cruzada(self, db):
        """Según las reglas actuales (12C-4c): reserva_recursos y
        reserva_zonas tienen cada una su propia EXCLUDE, independiente de
        la otra tabla. No existe todavía ninguna regla que bloquee un
        recurso porque su zona esté reservada (o viceversa) -- esa
        transitividad es una decisión de una fase posterior (12C-5),
        aprobada conceptualmente pero no implementada aquí."""
        espacio = crear_espacio(db)
        admin = crear_usuario(db, username="admin_ex7", email="admin_ex7@example.com", rol="admin")
        recurso_ancla = crear_recurso(db, espacio=espacio, usuario=admin, nombre="Recurso Ancla 7")
        recurso = crear_recurso(db, espacio=espacio, usuario=admin, nombre="Recurso Bajo Prueba 7")
        zona = _crear_zona(db, espacio=espacio, usuario=admin)
        r1 = _crear_reserva(db, usuario=admin, espacio=espacio, recurso=recurso_ancla)
        r2 = _crear_reserva(db, usuario=admin, espacio=espacio, recurso=recurso_ancla, fecha=date(2026, 9, 5))

        db.commit()
        migrate_resource_reservations()

        db.add(ReservaRecurso(
            reserva_id=r1.id, recurso_id=recurso.id, fecha=date(2026, 9, 16),
            hora_inicio=time(8, 0), hora_fin=time(9, 0), estado="esperando",
        ))
        db.add(ReservaZona(
            reserva_id=r2.id, zona_id=zona.id, fecha=date(2026, 9, 16),
            hora_inicio=time(8, 0), hora_fin=time(9, 0), estado="esperando",
        ))
        db.commit()  # no debe lanzar: tablas distintas, sin validacion cruzada todavia

        assert db.query(ReservaRecurso).filter(ReservaRecurso.fecha == date(2026, 9, 16)).count() == 1
        assert db.query(ReservaZona).filter(ReservaZona.fecha == date(2026, 9, 16)).count() == 1

    def test_migracion_completa_ejecutada_dos_veces_sin_error(self, db):
        espacio = crear_espacio(db)
        admin = crear_usuario(db, username="admin_ex8", email="admin_ex8@example.com", rol="admin")
        recurso = crear_recurso(db, espacio=espacio, usuario=admin)
        _crear_reserva(db, usuario=admin, espacio=espacio, recurso=recurso)

        db.commit()
        migrate_resource_reservations()
        db.commit()
        migrate_resource_reservations()  # segunda ejecucion: no debe lanzar

        constraints = {
            fila[0]
            for fila in db.execute(text(
                "SELECT conname FROM pg_constraint "
                "WHERE conname IN ('reserva_recursos_sin_solapamiento', 'reserva_zonas_sin_solapamiento')"
            )).fetchall()
        }
        assert constraints == {"reserva_recursos_sin_solapamiento", "reserva_zonas_sin_solapamiento"}

    def test_migracion_no_deja_sesiones_bloqueadas(self, db):
        """Verificacion directa de pg_stat_activity: tras ejecutar la
        migracion, ninguna conexion queda 'idle in transaction' ni
        esperando un lock -- mismo tipo de deadlock ya diagnosticado y
        corregido en 12C-4b, ahora verificado explicitamente."""
        espacio = crear_espacio(db)
        admin = crear_usuario(db, username="admin_ex9", email="admin_ex9@example.com", rol="admin")
        recurso = crear_recurso(db, espacio=espacio, usuario=admin)
        _crear_reserva(db, usuario=admin, espacio=espacio, recurso=recurso)

        db.commit()
        migrate_resource_reservations()
        db.commit()

        bloqueadas = db.execute(text("""
            SELECT pid, state, wait_event_type
            FROM pg_stat_activity
            WHERE datname = current_database()
              AND pid != pg_backend_pid()
              AND (state = 'idle in transaction' OR wait_event_type = 'Lock')
        """)).fetchall()
        assert bloqueadas == [], f"sesiones bloqueadas/idle-in-transaction encontradas: {bloqueadas}"
