from sqlalchemy import text

from app.db import engine


def migrate_resource_reservations() -> None:
    """Bring older installations to the resource-based reservation model."""
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
        "ALTER TABLE espacios ALTER COLUMN dias_atencion SET NOT NULL",
        "ALTER TABLE espacios ALTER COLUMN hora_apertura SET NOT NULL",
        "ALTER TABLE espacios ALTER COLUMN hora_cierre SET NOT NULL",
        "ALTER TABLE espacios ALTER COLUMN horario_atencion SET NOT NULL",
        "ALTER TABLE espacios ALTER COLUMN horas_antelacion SET NOT NULL",
        "ALTER TABLE espacios ALTER COLUMN aprobacion_automatica SET DEFAULT false",
        "ALTER TABLE espacios ALTER COLUMN aprobacion_automatica SET NOT NULL",
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
        END $$;
        """,
    )

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))
