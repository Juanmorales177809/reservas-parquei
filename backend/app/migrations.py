from sqlalchemy import text

from app.db import engine


# Fase 12C-4b: backfill idempotente de reserva_recursos desde
# Reserva.recurso_id, y su gate de cobertura. Extraídos como constantes de
# módulo (a diferencia del resto de `migrate_resource_reservations()`, que
# usa literales inline) para que los tests puedan ejercitar el gate de
# forma aislada sin depender de que el backfill ya lo haya sanado --
# ver backend/tests/test_migrations_reserva_recursos.py.
_BACKFILL_RESERVA_RECURSOS = """
    INSERT INTO reserva_recursos (reserva_id, recurso_id, fecha, hora_inicio, hora_fin, estado)
    SELECT id, recurso_id, fecha, hora_inicio, hora_fin, estado
    FROM reservas
    WHERE recurso_id IS NOT NULL
      AND NOT EXISTS (
          SELECT 1 FROM reserva_recursos rr WHERE rr.reserva_id = reservas.id
      )
"""

_GATE_RESERVA_RECURSOS_COMPLETO = """
    DO $$
    DECLARE
        huerfanas INTEGER;
    BEGIN
        SELECT COUNT(*) INTO huerfanas FROM reservas r
        WHERE NOT EXISTS (SELECT 1 FROM reserva_recursos WHERE reserva_id = r.id);
        IF huerfanas > 0 THEN
            RAISE EXCEPTION 'Backfill de reserva_recursos incompleto: % reservas sin fila asociada', huerfanas;
        END IF;
    END $$;
"""

# Fase 12C-4c: constraints EXCLUDE nuevas sobre reserva_recursos y
# reserva_zonas -- mismo patrón exacto que reservas_sin_solapamiento
# (btree_gist, ya instalada más arriba en este mismo archivo antes de
# este bloque). Un ALTER TABLE ADD CONSTRAINT EXCLUDE valida TODAS las
# filas ya existentes de la tabla en el momento de agregarse; si alguna
# violara la exclusión, el ALTER TABLE falla y, por el contrato
# transaccional de esta función (ver docstring de
# migrate_resource_reservations), toda la migración de esta ejecución se
# revierte -- nunca queda una constraint a medio aplicar ni un backfill
# parcial. No hay manejo especial de excepción aquí: un fallo por
# solapamiento real o por ausencia de btree_gist se propaga tal cual,
# igual que el resto de este archivo.
_CONSTRAINTS_EXCLUDE_RESERVA_ASOCIACIONES = """
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM pg_constraint
            WHERE conname = 'reserva_recursos_sin_solapamiento'
              AND conrelid = 'reserva_recursos'::regclass
        ) THEN
            ALTER TABLE reserva_recursos
            ADD CONSTRAINT reserva_recursos_sin_solapamiento
            EXCLUDE USING gist (
                recurso_id WITH =,
                fecha WITH =,
                tsrange(
                    fecha + hora_inicio,
                    fecha + hora_fin,
                    '[)'
                ) WITH &&
            )
            WHERE (estado IN ('esperando', 'aprobada'));
        END IF;
        IF NOT EXISTS (
            SELECT 1 FROM pg_constraint
            WHERE conname = 'reserva_zonas_sin_solapamiento'
              AND conrelid = 'reserva_zonas'::regclass
        ) THEN
            ALTER TABLE reserva_zonas
            ADD CONSTRAINT reserva_zonas_sin_solapamiento
            EXCLUDE USING gist (
                zona_id WITH =,
                fecha WITH =,
                tsrange(
                    fecha + hora_inicio,
                    fecha + hora_fin,
                    '[)'
                ) WITH &&
            )
            WHERE (estado IN ('esperando', 'aprobada'));
        END IF;
    END $$;
"""


def migrate_resource_reservations() -> None:
    """Bring older installations to the resource-based reservation model.

    Contrato transaccional: todos los `statements` de esta función se
    ejecutan dentro de una única transacción (`with engine.begin() as
    connection: ...`, ver el final de esta función). Si cualquier
    statement falla -- un `RAISE EXCEPTION` de un gate, una constraint
    `EXCLUDE`/`CHECK` violada, o cualquier otro error de PostgreSQL --
    la excepción se propaga sin capturarse y toda la transacción se
    revierte: nada de lo ejecutado en esa llamada (backfills, nuevas
    columnas, constraints) queda aplicado a medias. La siguiente vez que
    se llame a esta función (p. ej. en el próximo arranque) vuelve a
    intentar desde el principio, de forma idempotente. No se silencia ni
    se reintenta en bucle dentro de esta función.
    """
    statements = (
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'recursos' AND column_name = ' tipo_recurso_id'
            ) AND NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'recursos' AND column_name = 'tipo_recurso_id'
            ) THEN
                ALTER TABLE recursos RENAME COLUMN " tipo_recurso_id" TO tipo_recurso_id;
            END IF;
        END $$;
        """,
        "ALTER TABLE recursos ADD COLUMN IF NOT EXISTS nombre VARCHAR(100)",
        "ALTER TABLE recursos ADD COLUMN IF NOT EXISTS tipo_recurso_id INTEGER",
        "ALTER TABLE recursos ADD COLUMN IF NOT EXISTS create_at TIMESTAMPTZ DEFAULT now()",
        "ALTER TABLE espacios ADD COLUMN IF NOT EXISTS dias_atencion JSONB DEFAULT '[0,1,2,3,4,5]'::jsonb",
        "ALTER TABLE espacios ADD COLUMN IF NOT EXISTS hora_apertura TIME DEFAULT '07:00'",
        "ALTER TABLE espacios ADD COLUMN IF NOT EXISTS hora_cierre TIME DEFAULT '20:00'",
        "ALTER TABLE espacios ADD COLUMN IF NOT EXISTS horario_atencion JSONB DEFAULT '{}'::jsonb",
        "ALTER TABLE espacios ADD COLUMN IF NOT EXISTS horas_antelacion INTEGER DEFAULT 24",
        "ALTER TABLE espacios ADD COLUMN IF NOT EXISTS aprobacion_automatica BOOLEAN DEFAULT false",
        "ALTER TABLE espacios ADD COLUMN IF NOT EXISTS modalidad_reserva VARCHAR(20) DEFAULT 'equipos'",
        "ALTER TABLE espacios ADD COLUMN IF NOT EXISTS correo VARCHAR(255)",
        "ALTER TABLE recursos ADD COLUMN IF NOT EXISTS es_prestacion_servicio BOOLEAN DEFAULT false",
        "ALTER TABLE espacios ALTER COLUMN dias_atencion SET DEFAULT '[0,1,2,3,4,5]'::jsonb",
        "ALTER TABLE espacios ALTER COLUMN hora_apertura SET DEFAULT '07:00'",
        "ALTER TABLE espacios ALTER COLUMN hora_cierre SET DEFAULT '20:00'",
        "ALTER TABLE espacios ALTER COLUMN horario_atencion SET DEFAULT '{}'::jsonb",
        "ALTER TABLE espacios ALTER COLUMN horas_antelacion SET DEFAULT 24",
        "UPDATE espacios SET dias_atencion = '[0,1,2,3,4,5]'::jsonb WHERE dias_atencion IS NULL",
        "UPDATE espacios SET hora_apertura = '07:00' WHERE hora_apertura IS NULL",
        "UPDATE espacios SET hora_cierre = '20:00' WHERE hora_cierre IS NULL",
        """
        UPDATE espacios e
        SET horario_atencion = (
            SELECT COALESCE(
                jsonb_object_agg(
                    dia::text,
                    (
                        SELECT jsonb_agg(hora ORDER BY hora)
                        FROM generate_series(
                            EXTRACT(HOUR FROM e.hora_apertura)::integer,
                            EXTRACT(HOUR FROM e.hora_cierre)::integer - 1
                        ) AS hora
                    )
                ),
                '{}'::jsonb
            )
            FROM jsonb_array_elements_text(e.dias_atencion::jsonb) AS dia
        )
        WHERE horario_atencion IS NULL OR horario_atencion::jsonb = '{}'::jsonb
        """,
        "UPDATE espacios SET horas_antelacion = 24 WHERE horas_antelacion IS NULL",
        "UPDATE espacios SET aprobacion_automatica = false WHERE aprobacion_automatica IS NULL",
        "UPDATE espacios SET modalidad_reserva = 'equipos' WHERE modalidad_reserva IS NULL",
        "UPDATE recursos SET es_prestacion_servicio = false WHERE es_prestacion_servicio IS NULL",
        "ALTER TABLE espacios ALTER COLUMN dias_atencion SET NOT NULL",
        "ALTER TABLE espacios ALTER COLUMN hora_apertura SET NOT NULL",
        "ALTER TABLE espacios ALTER COLUMN hora_cierre SET NOT NULL",
        "ALTER TABLE espacios ALTER COLUMN horario_atencion SET NOT NULL",
        "ALTER TABLE espacios ALTER COLUMN horas_antelacion SET NOT NULL",
        "ALTER TABLE espacios ALTER COLUMN aprobacion_automatica SET DEFAULT false",
        "ALTER TABLE espacios ALTER COLUMN aprobacion_automatica SET NOT NULL",
        "ALTER TABLE espacios ALTER COLUMN modalidad_reserva SET DEFAULT 'equipos'",
        "ALTER TABLE espacios ALTER COLUMN modalidad_reserva SET NOT NULL",
        "ALTER TABLE recursos ALTER COLUMN es_prestacion_servicio SET DEFAULT false",
        "ALTER TABLE recursos ALTER COLUMN es_prestacion_servicio SET NOT NULL",
        "ALTER TABLE recursos ALTER COLUMN create_at SET DEFAULT now()",
        "ALTER TABLE recursos ALTER COLUMN update_at SET DEFAULT now()",
        "UPDATE recursos SET nombre = COALESCE(NULLIF(descripcion, ''), 'Recurso ' || id) WHERE nombre IS NULL",
        "UPDATE recursos SET create_at = now() WHERE create_at IS NULL",
        """
        INSERT INTO tipos_recursos (nombre, descripcion, activo)
        SELECT 'General', 'Tipo general de recurso', 'activo'
        WHERE NOT EXISTS (SELECT 1 FROM tipos_recursos)
        """,
        "UPDATE recursos SET tipo_recurso_id = (SELECT id FROM tipos_recursos ORDER BY id LIMIT 1) WHERE tipo_recurso_id IS NULL",
        "ALTER TABLE recursos ALTER COLUMN nombre SET NOT NULL",
        "ALTER TABLE recursos ALTER COLUMN tipo_recurso_id SET NOT NULL",
        "ALTER TABLE recursos ALTER COLUMN create_at SET NOT NULL",
        "ALTER TABLE reservas ADD COLUMN IF NOT EXISTS recurso_id INTEGER",
        """
        INSERT INTO recursos (
            nombre, espacio_id, tipo_recurso_id, descripcion, capacidad, estado,
            create_at, update_at, created_by, update_by
        )
        SELECT
            e.nombre, e.id, tr.id, 'Recurso migrado desde la reserva de espacio',
            e.capacidad, e.estado, now(), now(), r.usuario_id, r.usuario_id
        FROM (SELECT DISTINCT espacio_id, usuario_id FROM reservas WHERE recurso_id IS NULL) r
        JOIN espacios e ON e.id = r.espacio_id
        CROSS JOIN LATERAL (SELECT id FROM tipos_recursos ORDER BY id LIMIT 1) tr
        WHERE NOT EXISTS (
            SELECT 1 FROM recursos rc
            WHERE rc.espacio_id = e.id AND rc.nombre = e.nombre
        )
        """,
        """
        UPDATE reservas r
        SET recurso_id = rc.id
        FROM recursos rc
        WHERE r.recurso_id IS NULL
          AND rc.espacio_id = r.espacio_id
          AND rc.id = (
              SELECT rc2.id FROM recursos rc2
              WHERE rc2.espacio_id = r.espacio_id
              ORDER BY rc2.id LIMIT 1
          )
        """,
        """
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM reservas WHERE recurso_id IS NULL) THEN
                ALTER TABLE reservas ALTER COLUMN recurso_id SET NOT NULL;
            END IF;
        END $$;
        """,
        "CREATE INDEX IF NOT EXISTS ix_recursos_espacio_id ON recursos (espacio_id)",
        "CREATE INDEX IF NOT EXISTS ix_reservas_recurso_id ON reservas (recurso_id)",
        "CREATE INDEX IF NOT EXISTS ix_reservas_recurso_fecha_estado ON reservas (recurso_id, fecha, estado)",
        "CREATE EXTENSION IF NOT EXISTS btree_gist",
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_constraint
                WHERE conname = 'reservas_sin_solapamiento'
                  AND conrelid = 'reservas'::regclass
            ) THEN
                ALTER TABLE reservas
                ADD CONSTRAINT reservas_sin_solapamiento
                EXCLUDE USING gist (
                    recurso_id WITH =,
                    fecha WITH =,
                    tsrange(
                        fecha + hora_inicio,
                        fecha + hora_fin,
                        '[)'
                    ) WITH &&
                )
                WHERE (estado IN ('esperando', 'aprobada'));
            END IF;
        END $$;
        """,
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_usuarios_espacios_usuario ON usuarios_espacios (usuario_id)",
        """
        ALTER TABLE notificaciones DROP CONSTRAINT IF EXISTS notificaciones_tipo_check;
        ALTER TABLE notificaciones ADD CONSTRAINT notificaciones_tipo_check
        CHECK (tipo IN ('Pendiente', 'Aprobada', 'Rechazada', 'Cancelada'));
        """,
        """
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_reservas_recurso') THEN
                ALTER TABLE reservas ADD CONSTRAINT fk_reservas_recurso
                FOREIGN KEY (recurso_id) REFERENCES recursos(id);
            END IF;
            IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_recursos_tipo') THEN
                ALTER TABLE recursos ADD CONSTRAINT fk_recursos_tipo
                FOREIGN KEY (tipo_recurso_id) REFERENCES tipos_recursos(id);
            END IF;
            IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'ck_espacios_horario_atencion') THEN
                ALTER TABLE espacios ADD CONSTRAINT ck_espacios_horario_atencion
                CHECK (hora_apertura < hora_cierre);
            END IF;
            IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'ck_espacios_horas_antelacion') THEN
                ALTER TABLE espacios ADD CONSTRAINT ck_espacios_horas_antelacion
                CHECK (horas_antelacion >= 0);
            END IF;
            IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'ck_espacios_modalidad_reserva') THEN
                ALTER TABLE espacios ADD CONSTRAINT ck_espacios_modalidad_reserva
                CHECK (modalidad_reserva IN ('equipos', 'zonas', 'mixto'));
            END IF;
        END $$;
        """,
        # Fase 12C-4b: reserva_recursos y reserva_zonas ya existen (creadas
        # por Base.metadata.create_all() antes de esta función, igual que
        # zonas/zona_recursos en 12C-1/12C-3) -- ningún guard de existencia
        # de tabla es necesario, mismo patrón que el resto de este archivo,
        # que nunca verifica la existencia de una tabla ya creada por
        # create_all antes de insertar en ella.
        _BACKFILL_RESERVA_RECURSOS,
        _GATE_RESERVA_RECURSOS_COMPLETO,
        _CONSTRAINTS_EXCLUDE_RESERVA_ASOCIACIONES,
    )

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))
