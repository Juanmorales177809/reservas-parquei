# -*- coding: utf-8 -*-
"""Pruebas del rollback condicionado de la Fase 12C-4e.

Ejercitan el procedimiento `_ROLLBACK_RESERVA_LEGACY` (definido como constante
de `app/migrations.py`, NO conectado al arranque) **únicamente contra esquemas
desechables** que este módulo crea y elimina con `CREATE/DROP SCHEMA` dentro de
`reservas_test` — nunca contra `public` y nunca contra el esquema real. El
procedimiento es esquema-agnóstico (resuelve contra `search_path`), por lo que
puede ejecutarse en un esquema efímero con las tres tablas mínimas que los
gates consultan (reservas, reserva_recursos, reserva_zonas), sin FKs.

Reglas verificadas aquí (contrato de la Fase 12C-4e):
- aborta ANTES de modificar datos si detecta: G1 multi-recurso, G2 cualquier
  reserva con zona, G3 divergencia de ancla, G4 divergencia de fecha/hora/
  estado, G5 reserva huérfana;
- el mensaje de aborto identifica el gate y la(s) reserva(s) afectada(s);
- el dataset reversible (solo reservas singulares coherentes) completa el
  rollback en una única transacción y restaura el esquema legacy;
- una segunda ejecución falla explícitamente como "ya revertido" (idempotencia);
- un error forzado tras el DDL revierte TODO (rollback transaccional);
- no quedan sesiones idle in transaction ni bloqueos tras los flujos.
"""

import uuid

import pytest
from sqlalchemy import text

from app.db import engine
from app.migrations import _ROLLBACK_RESERVA_LEGACY


# Tablas mínimas: mismas columnas que los modelos (`backend/app/models/`) que
# los gates y la restauración consultan. Sin FKs a propósito — el procedimiento
# solo lee/escribe estas tres tablas y DDL sobre ellas.
_TABLAS_MINIMAS = """
CREATE TABLE {s}.reservas (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    espacio_id INTEGER NOT NULL,
    recurso_id INTEGER NOT NULL,
    fecha DATE NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    estado VARCHAR(20) NOT NULL,
    asistentes INTEGER NOT NULL
);
CREATE TABLE {s}.reserva_recursos (
    id SERIAL PRIMARY KEY,
    reserva_id INTEGER NOT NULL,
    recurso_id INTEGER NOT NULL,
    fecha DATE NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    estado VARCHAR(20) NOT NULL
);
CREATE TABLE {s}.reserva_zonas (
    id SERIAL PRIMARY KEY,
    reserva_id INTEGER NOT NULL,
    zona_id INTEGER NOT NULL,
    fecha DATE NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    estado VARCHAR(20) NOT NULL
);
"""


@pytest.fixture()
def esquema_desechable():
    """Crea un esquema efímero con las tres tablas mínimas y lo elimina al
    terminar (teardown garantizado incluso si el test falla)."""
    nombre = f"proof_12c4e_{uuid.uuid4().hex[:8]}"
    with engine.begin() as conn:
        conn.execute(text(f"CREATE SCHEMA {nombre}"))
        conn.execute(text(_TABLAS_MINIMAS.format(s=nombre)))
    yield nombre
    with engine.begin() as conn:
        conn.execute(text(f"DROP SCHEMA IF EXISTS {nombre} CASCADE"))


def _ejecutar(nombre, sql, incluir_public=True):
    """Ejecuta SQL con search_path al esquema desechable (SET LOCAL: no se
    filtra a la sesión de pool usada por otros tests). `incluir_public=False`
    deja fuera a public para que `to_regclass` (p. ej. G0) NO resuelva las
    tablas de asociación reales del esquema public."""
    ruta = f"{nombre}, public" if incluir_public else nombre
    with engine.begin() as conn:
        conn.execute(text(f"SET LOCAL search_path TO {ruta}"))
        conn.execute(text(sql))


def _insertar_reserva(nombre, *, recurso_id, fecha, estado="aprobada"):
    with engine.begin() as conn:
        conn.execute(text(f"SET LOCAL search_path TO {nombre}, public"))
        return conn.execute(text(
            "INSERT INTO reservas "
            "(usuario_id, espacio_id, recurso_id, fecha, hora_inicio, hora_fin, estado, asistentes) "
            f"VALUES (1, 1, {recurso_id}, '{fecha}', '08:00', '10:00', '{estado}', 2) "
            "RETURNING id"
        )).scalar()


def _insertar_rr(nombre, reserva_id, recurso_id, fecha, estado="aprobada"):
    with engine.begin() as conn:
        conn.execute(text(f"SET LOCAL search_path TO {nombre}, public"))
        conn.execute(text(
            "INSERT INTO reserva_recursos "
            "(reserva_id, recurso_id, fecha, hora_inicio, hora_fin, estado) "
            f"VALUES ({reserva_id}, {recurso_id}, '{fecha}', '08:00', '10:00', '{estado}')"
        ))


def _insertar_rz(nombre, reserva_id, zona_id, fecha, estado="aprobada"):
    with engine.begin() as conn:
        conn.execute(text(f"SET LOCAL search_path TO {nombre}, public"))
        conn.execute(text(
            "INSERT INTO reserva_zonas "
            "(reserva_id, zona_id, fecha, hora_inicio, hora_fin, estado) "
            f"VALUES ({reserva_id}, {zona_id}, '{fecha}', '08:00', '10:00', '{estado}')"
        ))


def _foto(nombre):
    """Snapshot de filas para comparaciones pre/post de los abortos."""
    with engine.connect() as conn:
        conn.execute(text(f"SET LOCAL search_path TO {nombre}, public"))
        return {
            "reservas": [
                tuple(fila) for fila in conn.execute(text(
                    "SELECT id, recurso_id, estado, fecha FROM reservas ORDER BY id"
                )).fetchall()
            ],
            "rr": [
                tuple(fila) for fila in conn.execute(text(
                    "SELECT reserva_id, recurso_id, estado FROM reserva_recursos ORDER BY reserva_id"
                )).fetchall()
            ],
            "rz": [
                tuple(fila) for fila in conn.execute(text(
                    "SELECT reserva_id, zona_id, estado FROM reserva_zonas ORDER BY reserva_id"
                )).fetchall()
            ],
        }


def _tabla_existe(nombre, tabla):
    with engine.connect() as conn:
        return conn.execute(text(
            f"SELECT to_regclass('{nombre}.{tabla}') IS NOT NULL"
        )).scalar() is True


def _constraint_presente(nombre, conname):
    with engine.connect() as conn:
        return conn.execute(text(
            "SELECT COUNT(*) FROM pg_constraint c "
            "JOIN pg_namespace n ON n.oid = c.connamespace "
            f"WHERE n.nspname = '{nombre}' AND c.conname = '{conname}'"
        )).scalar() > 0


def _indices_historicos_presentes(nombre):
    with engine.connect() as conn:
        return conn.execute(text(
            "SELECT COUNT(*) FROM pg_indexes "
            f"WHERE schemaname = '{nombre}' "
            "AND indexname IN ('ix_reservas_recurso_id', 'ix_reservas_recurso_fecha_estado')"
        )).scalar() == 2


def _recurso_id_nullable(nombre):
    with engine.connect() as conn:
        return conn.execute(text(
            "SELECT is_nullable FROM information_schema.columns "
            f"WHERE table_schema = '{nombre}' AND table_name = 'reservas' "
            "AND column_name = 'recurso_id'"
        )).scalar() == "YES"


def _espera_aborto(nombre, fragmento, antes):
    """Ejecuta el procedimiento esperando aborto con el fragmento indicado;
    verifica el mensaje (gate + reservas afectadas) y que NADA cambió."""
    with pytest.raises(Exception) as excinfo:
        _ejecutar(nombre, _ROLLBACK_RESERVA_LEGACY)
    assert fragmento in str(excinfo.value), f"mensaje recibido: {excinfo.value}"
    assert "reservas {" in str(excinfo.value), "el mensaje debe identificar las reservas afectadas"
    assert _foto(nombre) == antes, "el aborto modificó datos: debe abortar antes de escribir"
    assert _tabla_existe(nombre, "reserva_recursos") is True
    assert _tabla_existe(nombre, "reserva_zonas") is True


# ---------------------------------------------------------------------------
# Conexión con el arranque
# ---------------------------------------------------------------------------


def test_la_migracion_de_arranque_no_ejecuta_el_rollback():
    """El procedimiento es manual/operatorio: tras la migración de arranque de
    la suite (fixture `preparar_esquema`), reserva_recursos/reserva_zonas
    siguen existiendo en public. El rollback solo se ejecuta en esquemas
    desechables desde este módulo."""
    with engine.connect() as conn:
        assert conn.execute(text("SELECT to_regclass('public.reserva_recursos') IS NOT NULL")).scalar() is True
        assert conn.execute(text("SELECT to_regclass('public.reserva_zonas') IS NOT NULL")).scalar() is True


# ---------------------------------------------------------------------------
# Abortos: G0..G5 (nunca modifican datos; el mensaje identifica gate + reservas)
# ---------------------------------------------------------------------------


def test_g0_segunda_ejecucion_falla_ya_revertido():
    """En un esquema sin tablas de asociación, el procedimiento falla con G0
    sin alterar nada. Se usa un esquema desnudo y search_path SIN public para
    que to_regclass no resuelva las tablas reales del esquema public (que sí
    existen y harían pasar el gate por error)."""
    nombre = f"proof_12c4e_{uuid.uuid4().hex[:8]}"
    with engine.begin() as conn:
        conn.execute(text(f"CREATE SCHEMA {nombre}"))
    try:
        assert _tabla_existe(nombre, "reserva_recursos") is False
        with pytest.raises(Exception) as excinfo:
            _ejecutar(nombre, _ROLLBACK_RESERVA_LEGACY, incluir_public=False)
        assert "G0 ya_revertido" in str(excinfo.value)
    finally:
        with engine.begin() as conn:
            conn.execute(text(f"DROP SCHEMA IF EXISTS {nombre} CASCADE"))


def test_g1_multi_recurso_aborta_sin_modificar(esquema_desechable):
    r1 = _insertar_reserva(esquema_desechable, recurso_id=10, fecha="2026-09-01")
    _insertar_rr(esquema_desechable, r1, 10, "2026-09-01")
    r2 = _insertar_reserva(esquema_desechable, recurso_id=10, fecha="2026-09-02")
    _insertar_rr(esquema_desechable, r2, 10, "2026-09-02")
    _insertar_rr(esquema_desechable, r2, 11, "2026-09-02")
    _espera_aborto(esquema_desechable, "G1 multi_recurso", _foto(esquema_desechable))


@pytest.mark.parametrize(
    "armar",
    [
        lambda s: _armar_solo_zona(s),
        lambda s: _armar_mixta(s),
        lambda s: _armar_zona_con_efectivos(s),
    ],
    ids=["solo_zona", "mixta", "zona_con_efectivos"],
)
def test_g2_cualquier_reserva_con_zona_aborta_sin_modificar(esquema_desechable, armar):
    armar(esquema_desechable)
    _espera_aborto(esquema_desechable, "G2 reserva_con_zona", _foto(esquema_desechable))


def _armar_solo_zona(s):
    """Reserva solo por zona sin recursos: fila en reserva_zonas, sin rr."""
    r = _insertar_reserva(s, recurso_id=10, fecha="2026-09-03")
    _insertar_rz(s, r, 20, "2026-09-03")


def _armar_mixta(s):
    """Reserva mixta: zona (con su recurso efectivo 10) + recurso directo 11."""
    r = _insertar_reserva(s, recurso_id=10, fecha="2026-09-04")
    _insertar_rz(s, r, 20, "2026-09-04")
    _insertar_rr(s, r, 10, "2026-09-04")
    _insertar_rr(s, r, 11, "2026-09-04")


def _armar_zona_con_efectivos(s):
    """Reserva por zona con recursos efectivos: rz + rr con su único efectivo."""
    r = _insertar_reserva(s, recurso_id=10, fecha="2026-09-07")
    _insertar_rz(s, r, 20, "2026-09-07")
    _insertar_rr(s, r, 10, "2026-09-07")


def test_g3_divergencia_de_ancla_aborta_sin_modificar(esquema_desechable):
    r = _insertar_reserva(esquema_desechable, recurso_id=12, fecha="2026-09-08")  # columna ≠ asociación
    _insertar_rr(esquema_desechable, r, 10, "2026-09-08")  # única fila dice recurso 10
    _espera_aborto(esquema_desechable, "G3 divergencia_ancla", _foto(esquema_desechable))


def test_g4_divergencia_de_fecha_hora_estado_aborta_sin_modificar(esquema_desechable):
    r = _insertar_reserva(esquema_desechable, recurso_id=10, fecha="2026-09-09", estado="aprobada")
    _insertar_rr(esquema_desechable, r, 10, "2026-09-09", estado="esperando")  # asociación desincronizada
    _espera_aborto(esquema_desechable, "G4 divergencia_fecha_hora_estado", _foto(esquema_desechable))


def test_g5_reserva_huerfana_aborta_sin_modificar(esquema_desechable):
    _insertar_reserva(esquema_desechable, recurso_id=10, fecha="2026-09-10")  # sin rr ni rz
    _espera_aborto(esquema_desechable, "G5 reserva_huerfana", _foto(esquema_desechable))


# ---------------------------------------------------------------------------
# Rollback exitoso (dataset reversible) + restauración de esquema
# ---------------------------------------------------------------------------


def test_rollback_reversible_restaura_esquema_legacy_y_conteos(esquema_desechable):
    r1 = _insertar_reserva(esquema_desechable, recurso_id=10, fecha="2026-09-01")
    _insertar_rr(esquema_desechable, r1, 10, "2026-09-01")
    r2 = _insertar_reserva(esquema_desechable, recurso_id=11, fecha="2026-09-11")
    _insertar_rr(esquema_desechable, r2, 11, "2026-09-11")

    # Estado inicial del esquema desechable: tablas nuevas presentes, esquema
    # histórico ausente (constraint e índices se restaurarán).
    assert _tabla_existe(esquema_desechable, "reserva_recursos") is True
    assert _tabla_existe(esquema_desechable, "reserva_zonas") is True
    assert _constraint_presente(esquema_desechable, "reservas_sin_solapamiento") is False
    assert _indices_historicos_presentes(esquema_desechable) is False

    _ejecutar(esquema_desechable, _ROLLBACK_RESERVA_LEGACY)  # una sola sentencia/transacción

    # Tablas nuevas eliminadas; esquema histórico restaurado.
    assert _tabla_existe(esquema_desechable, "reserva_recursos") is False
    assert _tabla_existe(esquema_desechable, "reserva_zonas") is False
    assert _constraint_presente(esquema_desechable, "reservas_sin_solapamiento") is True
    assert _indices_historicos_presentes(esquema_desechable) is True
    assert _recurso_id_nullable(esquema_desechable) is False

    # Datos preservados sin pérdida y sin NULLs.
    with engine.connect() as conn:
        conn.execute(text(f"SET LOCAL search_path TO {esquema_desechable}, public"))
        assert conn.execute(text("SELECT COUNT(*) FROM reservas")).scalar() == 2
        assert conn.execute(text("SELECT COUNT(*) FROM reservas WHERE recurso_id IS NULL")).scalar() == 0


def test_rollback_respeta_constraint_historica_ya_existente(esquema_desechable):
    """Si la constraint histórica ya está presente, el procedimiento la
    conserva (no la duplica ni falla)."""
    r = _insertar_reserva(esquema_desechable, recurso_id=10, fecha="2026-09-01")
    _insertar_rr(esquema_desechable, r, 10, "2026-09-01")
    with engine.begin() as conn:
        conn.execute(text(f"SET LOCAL search_path TO {esquema_desechable}, public"))
        conn.execute(text(
            "ALTER TABLE reservas ADD CONSTRAINT reservas_sin_solapamiento "
            "EXCLUDE USING gist (recurso_id WITH =, fecha WITH =, "
            "tsrange(fecha + hora_inicio, fecha + hora_fin, '[)') WITH &&) "
            "WHERE (estado IN ('esperando', 'aprobada'))"
        ))
    assert _constraint_presente(esquema_desechable, "reservas_sin_solapamiento") is True

    _ejecutar(esquema_desechable, _ROLLBACK_RESERVA_LEGACY)

    assert _tabla_existe(esquema_desechable, "reserva_recursos") is False
    assert _constraint_presente(esquema_desechable, "reservas_sin_solapamiento") is True


def test_rollback_fallo_tras_ddl_revierte_todo(esquema_desechable):
    """Se ejecuta el procedimiento (que ya hizo DDL dentro de la transacción) y
    se fuerza un error ANTES del commit: la transacción única revierte todo."""
    r = _insertar_reserva(esquema_desechable, recurso_id=10, fecha="2026-09-01")
    _insertar_rr(esquema_desechable, r, 10, "2026-09-01")
    antes = _foto(esquema_desechable)

    with pytest.raises(Exception) as excinfo:
        with engine.begin() as conn:
            conn.execute(text(f"SET LOCAL search_path TO {esquema_desechable}, public"))
            conn.execute(text(_ROLLBACK_RESERVA_LEGACY))  # aquí el DO ya borró rr/rz
            conn.execute(text("SELECT 1 / 0"))  # error forzado post-DDL
    assert "division by zero" in str(excinfo.value).lower()

    # Todo revertido: tablas nuevas de vuelta, datos idénticos, sin cambios de esquema.
    assert _tabla_existe(esquema_desechable, "reserva_recursos") is True
    assert _tabla_existe(esquema_desechable, "reserva_zonas") is True
    assert _foto(esquema_desechable) == antes
    assert _constraint_presente(esquema_desechable, "reservas_sin_solapamiento") is False


def test_rollback_no_deja_sesiones_bloqueadas(esquema_desechable):
    """Tras el flujo, ninguna sesión queda idle in transaction ni esperando lock."""
    r = _insertar_reserva(esquema_desechable, recurso_id=10, fecha="2026-09-01")
    _insertar_rr(esquema_desechable, r, 10, "2026-09-01")
    _ejecutar(esquema_desechable, _ROLLBACK_RESERVA_LEGACY)
    with engine.connect() as conn:
        bloqueadas = conn.execute(text(
            "SELECT COUNT(*) FROM pg_stat_activity "
            "WHERE state = 'idle in transaction' OR wait_event_type = 'Lock'"
        )).scalar()
    assert bloqueadas == 0


def test_rollback_idempotente_segunda_ejecucion_ya_revertido(esquema_desechable):
    r = _insertar_reserva(esquema_desechable, recurso_id=10, fecha="2026-09-01")
    _insertar_rr(esquema_desechable, r, 10, "2026-09-01")
    _ejecutar(esquema_desechable, _ROLLBACK_RESERVA_LEGACY)  # primera ejecución exitosa

    assert _tabla_existe(esquema_desechable, "reserva_recursos") is False
    assert _constraint_presente(esquema_desechable, "reservas_sin_solapamiento") is True

    with pytest.raises(Exception) as excinfo:
        _ejecutar(esquema_desechable, _ROLLBACK_RESERVA_LEGACY)
    assert "G0 ya_revertido" in str(excinfo.value)

    # La segunda ejecución no altera nada.
    assert _tabla_existe(esquema_desechable, "reserva_recursos") is False
    assert _tabla_existe(esquema_desechable, "reserva_zonas") is False
    assert _constraint_presente(esquema_desechable, "reservas_sin_solapamiento") is True
    with engine.connect() as conn:
        conn.execute(text(f"SET LOCAL search_path TO {esquema_desechable}, public"))
        assert conn.execute(text("SELECT COUNT(*) FROM reservas")).scalar() == 1