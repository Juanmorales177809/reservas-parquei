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

# Fase 12C-4e: PROCEDIMIENTO DE ROLLBACK CONDICIONADO. NO forma parte del
# arranque de la aplicación ni de migrate_resource_reservations() -- es una
# operación manual/operatoria para revertir el modelo 12C-6 (reserva_recursos/
# reserva_zonas como fuente de verdad) al esquema histórico exclusivamente
# cuando TODOS los datos son representables sin pérdida en el modelo antiguo.
#
# Contrato exigido (ver backend/app/models/README.md y CHANGELOG.md, Fase
# 12C-4e):
#   - Una sola transacción: el bloque DO es UNA sentencia; si falla, PostgreSQL
#     revierte todo (los DDL van por EXECUTE dentro del mismo bloque).
#   - Aborta ANTES de modificar datos si existe: (G1) alguna reserva con más de
#     un recurso, (G2) cualquier reserva con zona (solo-zona, mixta o zona con
#     recursos efectivos -- todas pierden la dimensión zona en el esquema
#     antiguo), (G3) divergencia del ancla (reservas.recurso_id distinto de la
#     única fila de reserva_recursos), (G4) divergencia de fecha/hora/estado
#     entre reservas y sus asociaciones, o (G5) reservas sin ninguna asociación.
#   - Nunca usa UPDATE parcial + SET NOT NULL para ocultar datos no
#     representables: si un gate detecta algo, RAISE EXCEPTION propaga y
#     revierte; el rollback solo progresa cuando el dataset es EXCLUSIVAMENTE
#     reservas singulares coherentes (reversible sin pérdida).
#   - Restaura la columna desde la única asociación (no-op por G3), re-crea la
#     constraint histórica reservas_sin_solapamiento y los índices históricos
#     si faltan, y solo entonces elimina constraints/tablas nuevas.
#   - Idempotencia: la segunda ejecución sobre un esquema ya revertido falla
#     explícitamente con G0 ("ya_revertido"), sin alterar nada.
#
# Esquema-agnóstico a propósito (sin prefijo public.): se resuelve contra el
# search_path de la conexión, por lo que los tests lo ejercitan en esquemas
# desechables (CREATE/DROP SCHEMA) dentro de reservas_test, sin tocar public.
# Este procedimiento NO se debe invocar desde el ciclo de vida de la app ni
# desde la migración de arranque.
_ROLLBACK_RESERVA_LEGACY = """
    DO $rollback$
    DECLARE
        v_ids bigint[];
    BEGIN
        -- G0: estado ya revertido (idempotencia / fail-fast)
        IF to_regclass('reserva_recursos') IS NULL
           OR to_regclass('reserva_zonas') IS NULL THEN
            RAISE EXCEPTION 'G0 ya_revertido: tablas de asociacion ausentes (reserva_recursos/reserva_zonas)';
        END IF;

        -- G1: más de un recurso por reserva (no representable en una columna única)
        SELECT array_agg(r.id) INTO v_ids FROM reservas r
        JOIN (SELECT reserva_id, COUNT(*) n FROM reserva_recursos GROUP BY reserva_id) x
          ON x.reserva_id = r.id
        WHERE x.n > 1;
        IF v_ids IS NOT NULL THEN
            RAISE EXCEPTION 'G1 multi_recurso no representable: reservas %', v_ids;
        END IF;

        -- G2: cualquier reserva con zona (pierde la dimensión zona en el esquema antiguo)
        SELECT array_agg(DISTINCT r.id) INTO v_ids FROM reservas r
        JOIN reserva_zonas rz ON rz.reserva_id = r.id;
        IF v_ids IS NOT NULL THEN
            RAISE EXCEPTION 'G2 reserva_con_zona no representable (perdida dimension zona): reservas %', v_ids;
        END IF;

        -- G3: divergencia del ancla en reservas con exactamente un recurso
        SELECT array_agg(r.id) INTO v_ids FROM reservas r
        JOIN (SELECT reserva_id, MIN(recurso_id) m, COUNT(*) n FROM reserva_recursos GROUP BY reserva_id) x
          ON x.reserva_id = r.id AND x.n = 1
        WHERE r.recurso_id IS DISTINCT FROM x.m;
        IF v_ids IS NOT NULL THEN
            RAISE EXCEPTION 'G3 divergencia_ancla (reservas.recurso_id != unica fila de reserva_recursos): reservas %', v_ids;
        END IF;

        -- G4: divergencias fecha/hora/estado en cualquiera de las dos asociaciones
        SELECT array_agg(DISTINCT r.id) INTO v_ids FROM reservas r
        JOIN reserva_recursos rr ON rr.reserva_id = r.id
        WHERE (rr.fecha, rr.hora_inicio, rr.hora_fin, rr.estado)
              IS DISTINCT FROM (r.fecha, r.hora_inicio, r.hora_fin, r.estado);
        IF v_ids IS NOT NULL THEN
            RAISE EXCEPTION 'G4 divergencia_fecha_hora_estado en reserva_recursos: reservas %', v_ids;
        END IF;
        SELECT array_agg(DISTINCT r.id) INTO v_ids FROM reservas r
        JOIN reserva_zonas rz ON rz.reserva_id = r.id
        WHERE (rz.fecha, rz.hora_inicio, rz.hora_fin, rz.estado)
              IS DISTINCT FROM (r.fecha, r.hora_inicio, r.hora_fin, r.estado);
        IF v_ids IS NOT NULL THEN
            RAISE EXCEPTION 'G4b divergencia_fecha_hora_estado en reserva_zonas: reservas %', v_ids;
        END IF;

        -- G5: reservas sin ninguna asociación
        SELECT array_agg(r.id) INTO v_ids FROM reservas r
        WHERE NOT EXISTS (SELECT 1 FROM reserva_recursos WHERE reserva_id = r.id)
          AND NOT EXISTS (SELECT 1 FROM reserva_zonas WHERE reserva_id = r.id);
        IF v_ids IS NOT NULL THEN
            RAISE EXCEPTION 'G5 reserva_huerfana (sin ninguna asociacion): reservas %', v_ids;
        END IF;

        -- Dataset reversible: restauración de la columna desde la única
        -- asociación (no-op garantizada por G3; nunca deja NULL).
        UPDATE reservas r SET recurso_id = x.m
        FROM (SELECT reserva_id, MIN(recurso_id) m, COUNT(*) n FROM reserva_recursos GROUP BY reserva_id) x
        WHERE x.reserva_id = r.id AND x.n = 1 AND r.recurso_id IS DISTINCT FROM x.m;

        -- Restaurar la constraint histórica y los índices históricos si faltan
        IF NOT EXISTS (
            SELECT 1 FROM pg_constraint
            WHERE conname = 'reservas_sin_solapamiento'
              AND conrelid = 'reservas'::regclass
        ) THEN
            EXECUTE $ddl$
                ALTER TABLE reservas ADD CONSTRAINT reservas_sin_solapamiento
                EXCLUDE USING gist (
                    recurso_id WITH =,
                    fecha WITH =,
                    tsrange(fecha + hora_inicio, fecha + hora_fin, '[)') WITH &&
                )
                WHERE (estado IN ('esperando', 'aprobada'))
            $ddl$;
        END IF;
        EXECUTE 'CREATE INDEX IF NOT EXISTS ix_reservas_recurso_id ON reservas (recurso_id)';
        EXECUTE 'CREATE INDEX IF NOT EXISTS ix_reservas_recurso_fecha_estado ON reservas (recurso_id, fecha, estado)';

        -- Eliminar el esquema nuevo SOLO después de validar todos los gates
        EXECUTE 'ALTER TABLE reserva_recursos DROP CONSTRAINT IF EXISTS reserva_recursos_sin_solapamiento';
        EXECUTE 'ALTER TABLE reserva_recursos DROP CONSTRAINT IF EXISTS uq_reserva_recursos_reserva_recurso';
        EXECUTE 'ALTER TABLE reserva_zonas DROP CONSTRAINT IF EXISTS reserva_zonas_sin_solapamiento';
        EXECUTE 'ALTER TABLE reserva_zonas DROP CONSTRAINT IF EXISTS uq_reserva_zonas_reserva_zona';
        EXECUTE 'DROP TABLE reserva_zonas';
        EXECUTE 'DROP TABLE reserva_recursos';

        RAISE NOTICE 'Rollback 12C-4e completado: esquema legacy restaurado (datos sin perdida)';
    END
    $rollback$;
"""


# Separación personal/usuarios (2026-08-28, ver
# ~/.claude/plans/dazzling-wobbling-zebra.md): `personal` (admin/gestor) ya
# existe como tabla nueva (creada por Base.metadata.create_all() antes de
# esta función, mismo criterio que reserva_recursos/correo_saliente) --
# acá solo se migran los DATOS y se repuntan las FK. Preservar el mismo
# `id` al copiar (ON CONFLICT DO NOTHING + setval) es lo que permite NO
# tener que reescribir ningún valor de FK existente, solo su constraint.
_COPIAR_ADMIN_GESTOR_A_PERSONAL = """
    INSERT INTO personal (
        id, username, email, supabase_id, rol,
        documento_identificacion, telefono, institucion, vinculacion, dependencia,
        created_at, updated_at
    )
    SELECT
        id, username, email, supabase_id, rol,
        documento_identificacion, telefono, institucion, vinculacion, dependencia,
        created_at, updated_at
    FROM usuarios WHERE rol IN ('admin', 'gestor')
    ON CONFLICT (id) DO NOTHING;
    SELECT setval(pg_get_serial_sequence('personal', 'id'), COALESCE((SELECT MAX(id) FROM personal), 1));
"""

# Repuntar las FK "de personal" (usuarios(id) -> personal(id)) -- válido
# recién DESPUÉS de _COPIAR_ADMIN_GESTOR_A_PERSONAL, porque el ADD
# CONSTRAINT valida los valores ya existentes en cada columna contra la
# nueva tabla referenciada. Patrón drop+add sin guarda de existencia
# (mismo que notificaciones_tipo_check más arriba): idempotente porque
# DROP CONSTRAINT IF EXISTS nunca falla y el ADD que sigue siempre puede
# recrearla.
_REPUNTAR_FK_DE_PERSONAL = """
    ALTER TABLE usuarios_espacios DROP CONSTRAINT IF EXISTS usuarios_espacios_usuario_id_fkey;
    ALTER TABLE usuarios_espacios ADD CONSTRAINT usuarios_espacios_usuario_id_fkey
        FOREIGN KEY (usuario_id) REFERENCES personal(id);

    ALTER TABLE recursos DROP CONSTRAINT IF EXISTS recursos_created_by_fkey;
    ALTER TABLE recursos ADD CONSTRAINT recursos_created_by_fkey
        FOREIGN KEY (created_by) REFERENCES personal(id);
    ALTER TABLE recursos DROP CONSTRAINT IF EXISTS recursos_update_by_fkey;
    ALTER TABLE recursos ADD CONSTRAINT recursos_update_by_fkey
        FOREIGN KEY (update_by) REFERENCES personal(id);

    ALTER TABLE zonas DROP CONSTRAINT IF EXISTS zonas_created_by_fkey;
    ALTER TABLE zonas ADD CONSTRAINT zonas_created_by_fkey
        FOREIGN KEY (created_by) REFERENCES personal(id);
    ALTER TABLE zonas DROP CONSTRAINT IF EXISTS zonas_updated_by_fkey;
    ALTER TABLE zonas ADD CONSTRAINT zonas_updated_by_fkey
        FOREIGN KEY (updated_by) REFERENCES personal(id);

    ALTER TABLE ensayos DROP CONSTRAINT IF EXISTS ensayos_created_by_fkey;
    ALTER TABLE ensayos ADD CONSTRAINT ensayos_created_by_fkey
        FOREIGN KEY (created_by) REFERENCES personal(id);
    ALTER TABLE ensayos DROP CONSTRAINT IF EXISTS ensayos_updated_by_fkey;
    ALTER TABLE ensayos ADD CONSTRAINT ensayos_updated_by_fkey
        FOREIGN KEY (updated_by) REFERENCES personal(id);

    ALTER TABLE espacios DROP CONSTRAINT IF EXISTS espacios_created_by_fkey;
    ALTER TABLE espacios ADD CONSTRAINT espacios_created_by_fkey
        FOREIGN KEY (created_by) REFERENCES personal(id);
    ALTER TABLE espacios DROP CONSTRAINT IF EXISTS espacios_updated_by_fkey;
    ALTER TABLE espacios ADD CONSTRAINT espacios_updated_by_fkey
        FOREIGN KEY (updated_by) REFERENCES personal(id);
"""

# reservas/notificaciones/control_cambios son polimórficas (el actor puede
# ser rol `usuario` o `personal`, ver el docstring de Reserva.actor) --
# ganan `personal_id` nullable, `usuario_id` pasa a nullable (ya lo era en
# control_cambios), backfill de las filas que en realidad eran de
# personal, y un CHECK de "a lo sumo/exactamente una llena" según la tabla
# (control_cambios ya admitía las dos en NULL por su `ondelete=SET NULL`
# previo a esta separación).
_POLIMORFISMO_ACTOR_RESERVAS_NOTIFICACIONES = """
    ALTER TABLE reservas ALTER COLUMN usuario_id DROP NOT NULL;
    ALTER TABLE reservas ADD COLUMN IF NOT EXISTS personal_id INTEGER;
    ALTER TABLE notificaciones ALTER COLUMN usuario_id DROP NOT NULL;
    ALTER TABLE notificaciones ADD COLUMN IF NOT EXISTS personal_id INTEGER;
    ALTER TABLE control_cambios ADD COLUMN IF NOT EXISTS personal_id INTEGER;
"""

_FK_PERSONAL_ID_RESERVAS_NOTIFICACIONES_CONTROL_CAMBIOS = """
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'reservas_personal_id_fkey') THEN
            ALTER TABLE reservas ADD CONSTRAINT reservas_personal_id_fkey
            FOREIGN KEY (personal_id) REFERENCES personal(id);
        END IF;
        IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'notificaciones_personal_id_fkey') THEN
            ALTER TABLE notificaciones ADD CONSTRAINT notificaciones_personal_id_fkey
            FOREIGN KEY (personal_id) REFERENCES personal(id) ON DELETE CASCADE;
        END IF;
        IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'control_cambios_personal_id_fkey') THEN
            ALTER TABLE control_cambios ADD CONSTRAINT control_cambios_personal_id_fkey
            FOREIGN KEY (personal_id) REFERENCES personal(id) ON DELETE SET NULL;
        END IF;
    END $$;
"""

# Backfill: cualquier fila que hoy apunta con `usuario_id` a alguien que en
# realidad ya está en `personal` (porque _COPIAR_ADMIN_GESTOR_A_PERSONAL
# preservó el mismo id) mueve ese valor a `personal_id`. Siempre
# re-ejecutable sin efecto tras la primera vez: en la segunda corrida no
# queda ningún `usuario_id` apuntando a un id de `personal` (ya se movió).
_BACKFILL_ACTOR_RESERVAS_NOTIFICACIONES_CONTROL_CAMBIOS = """
    UPDATE reservas SET personal_id = usuario_id, usuario_id = NULL
    WHERE usuario_id IN (SELECT id FROM personal);
    UPDATE notificaciones SET personal_id = usuario_id, usuario_id = NULL
    WHERE usuario_id IN (SELECT id FROM personal);
    UPDATE control_cambios SET personal_id = usuario_id, usuario_id = NULL
    WHERE usuario_id IN (SELECT id FROM personal);
"""

_CHECK_ACTOR_UNICO_RESERVAS_NOTIFICACIONES_CONTROL_CAMBIOS = """
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'ck_reservas_actor_unico') THEN
            ALTER TABLE reservas ADD CONSTRAINT ck_reservas_actor_unico
            CHECK ((usuario_id IS NOT NULL) != (personal_id IS NOT NULL));
        END IF;
        IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'ck_notificaciones_actor_unico') THEN
            ALTER TABLE notificaciones ADD CONSTRAINT ck_notificaciones_actor_unico
            CHECK ((usuario_id IS NOT NULL) != (personal_id IS NOT NULL));
        END IF;
        IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'ck_control_cambios_actor_unico') THEN
            ALTER TABLE control_cambios ADD CONSTRAINT ck_control_cambios_actor_unico
            CHECK (usuario_id IS NULL OR personal_id IS NULL);
        END IF;
    END $$;
"""

# Último paso: ya con todo repuntado y respaldado en `personal`, las filas
# admin/gestor sobran en `usuarios`. DELETE simple -- no dispara ningún
# ON DELETE CASCADE relevante (sus reservas/notificaciones/control_cambios
# ya se movieron a personal_id en el paso de backfill, sus
# usuarios_espacios/recursos/zonas/ensayos/espacios ya referencian
# personal(id) desde _REPUNTAR_FK_DE_PERSONAL).
_BORRAR_ADMIN_GESTOR_DE_USUARIOS = "DELETE FROM usuarios WHERE rol IN ('admin', 'gestor')"


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

    El procedimiento de ROLLBACK condicionado de la Fase 12C-4e NO se
    ejecuta aquí (ni en el arranque): es una operación manual/operatoria,
    disponible como constante `_ROLLBACK_RESERVA_LEGACY` y probada por
    `backend/tests/test_migrations_rollback_12c4e.py` únicamente contra
    esquemas desechables.
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
        CHECK (tipo IN ('Pendiente', 'Aprobada', 'Rechazada', 'Cancelada', 'Actualizada'));
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
        # Fase 12E: "capacidad opcional" se intentó y se revirtió en la misma
        # sesión (fuera de alcance de 12D/12E, ver CHANGELOG.md) porque
        # `ALTER COLUMN ... DROP NOT NULL` ya se había aplicado en algunos
        # entornos antes del revert -- `SET NOT NULL` restaura la constraint
        # original. Es idempotente (falla solo si ya quedara una fila NULL,
        # lo cual no debería ocurrir dado que el campo nunca se expuso como
        # opcional en un contrato publicado).
        "ALTER TABLE espacios ALTER COLUMN capacidad SET NOT NULL",
        "ALTER TABLE recursos ALTER COLUMN capacidad SET NOT NULL",
        # Fase 12D (parcial): `Reserva.tipo` (tipo de reserva académica,
        # RN-012/RN-015). Columna nullable sin backfill ni default: no hay
        # dato legado que migrar en este plan. El guard para el
        # CheckConstraint sigue el patrón exacto de `ck_espacios_modalidad_reserva`.
        "ALTER TABLE reservas ADD COLUMN IF NOT EXISTS tipo VARCHAR(30)",
        """
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'ck_reservas_tipo') THEN
                ALTER TABLE reservas ADD CONSTRAINT ck_reservas_tipo
                CHECK (tipo IN ('trabajo_investigacion', 'trabajo_grado', 'servicio_de_ensayo'));
            END IF;
        END $$;
        """,
        # Fase 12D-bis: `Reserva.asistio` (booleano nullable, sin
        # CheckConstraint). El más simple de los cuatro cambios de este plan.
        "ALTER TABLE reservas ADD COLUMN IF NOT EXISTS asistio BOOLEAN",
        # Fase 6: motivo de rechazo (texto libre, solo para rechazada).
        "ALTER TABLE reservas ADD COLUMN IF NOT EXISTS motivo_rechazo TEXT",
        # Fase A3: descripción libre y opcional de la actividad ("Actividad
        # a realizar" del formulario real) -- puramente aditivo, sin CHECK.
        "ALTER TABLE reservas ADD COLUMN IF NOT EXISTS descripcion TEXT",
        # Correo saliente (alta de usuario / recuperación de contraseña):
        # marca que la contraseña actual es una temporal generada por el
        # backend y debe cambiarse en el próximo login. `correo_saliente`
        # no necesita entrada aquí: es tabla nueva, la crea
        # Base.metadata.create_all() como el resto de tablas nuevas (mismo
        # criterio ya documentado más arriba para reserva_recursos/
        # reserva_zonas).
        "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS debe_cambiar_password BOOLEAN NOT NULL DEFAULT false",
        # Supabase Auth hybrid (institucional sin recursos extra): puente
        # UUID nullable + índice único. Mantiene PK Integer y 8 FKs intactos
        # (ver ya-tenemos-el-ci-calm-octopus.md) -- con SUPABASE_ENABLED=false
        # esta columna queda NULL y no afecta el flujo clásico.
        "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS supabase_id UUID",
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_usuarios_supabase_id ON usuarios (supabase_id)",
        # Fase A2 (perfil de usuario): datos del formulario real de
        # solicitud de laboratorios del ITM (documento, teléfono,
        # institución, vinculación, dependencia) que hoy no existían en
        # ningún lado del sistema. Todos nullable, sin backfill posible.
        "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS documento_identificacion VARCHAR(30)",
        "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS telefono VARCHAR(30)",
        "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS institucion VARCHAR(120)",
        "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS vinculacion VARCHAR(30)",
        "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS dependencia VARCHAR(150)",
        # `IS NULL OR` es obligatorio: sin él, ninguna fila existente (todas
        # con vinculacion NULL) pasaría el CHECK.
        """
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'ck_usuarios_vinculacion') THEN
                ALTER TABLE usuarios ADD CONSTRAINT ck_usuarios_vinculacion
                CHECK (vinculacion IS NULL OR vinculacion IN
                    ('docente', 'estudiante', 'contratista_empleado', 'extension', 'otra'));
            END IF;
        END $$;
        """,
        # Fase B: motivo de la solicitud (TipoSolicitud) -- NOT NULL con
        # backfill, mismo molde que `modalidad_reserva` de Espacio: ADD con
        # DEFAULT inline (cubre filas nuevas) -> UPDATE explícito (cubre
        # filas viejas, insertadas antes de que la columna existiera, que
        # quedan NULL pese al DEFAULT) -> SET DEFAULT -> SET NOT NULL.
        "ALTER TABLE reservas ADD COLUMN IF NOT EXISTS tipo_solicitud VARCHAR(30) DEFAULT 'reserva_en_laboratorio'",
        "ALTER TABLE reservas ADD COLUMN IF NOT EXISTS ubicacion_uso VARCHAR(200)",
        "ALTER TABLE reservas ADD COLUMN IF NOT EXISTS requiere_apoyo_auxiliar BOOLEAN DEFAULT false",
        "UPDATE reservas SET tipo_solicitud = 'reserva_en_laboratorio' WHERE tipo_solicitud IS NULL",
        "UPDATE reservas SET requiere_apoyo_auxiliar = false WHERE requiere_apoyo_auxiliar IS NULL",
        "ALTER TABLE reservas ALTER COLUMN tipo_solicitud SET DEFAULT 'reserva_en_laboratorio'",
        "ALTER TABLE reservas ALTER COLUMN tipo_solicitud SET NOT NULL",
        "ALTER TABLE reservas ALTER COLUMN requiere_apoyo_auxiliar SET DEFAULT false",
        "ALTER TABLE reservas ALTER COLUMN requiere_apoyo_auxiliar SET NOT NULL",
        # Acotado a los 2 valores que de verdad llegan por ReservaCreate hoy
        # -- 'orden_salida' se agrega recién en la Fase C, cuando exista el
        # código que lo materializa. Es la garantía estructural de que un
        # bug de ruteo en esa fase futura no pueda colar una fila de ese
        # tipo en `reservas` sin que la base de datos la rechace.
        """
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'ck_reservas_tipo_solicitud') THEN
                ALTER TABLE reservas ADD CONSTRAINT ck_reservas_tipo_solicitud
                CHECK (tipo_solicitud IN ('reserva_en_laboratorio', 'reserva_fuera_laboratorio'));
            END IF;
        END $$;
        """,
        # Fase D (import de inventario institucional): identificador de
        # activo físico. Nullable (un recurso creado a mano nunca lo trae) +
        # índice único -- NULL no colisiona consigo mismo en Postgres (ni en
        # ningún motor SQL estándar), así que múltiples recursos sin placa
        # conviven sin problema; dos con la MISMA placa sí chocan, que es
        # justo la garantía que necesita `scripts/importar_inventario.py`
        # para reintentar sin duplicar.
        "ALTER TABLE recursos ADD COLUMN IF NOT EXISTS placa VARCHAR(50)",
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_recursos_placa ON recursos (placa)",
        # Plantillas de correo institucional en HTML (invitación de usuario,
        # app/services/email_templates.py) -- `correo_saliente` ya existe en
        # bases reales (a diferencia de cuando se creó, no alcanza con
        # `create_all`). Default false conserva texto plano para todas las
        # filas existentes y para el resto de notificaciones del outbox.
        "ALTER TABLE correo_saliente ADD COLUMN IF NOT EXISTS es_html BOOLEAN NOT NULL DEFAULT false",
        # Separación personal/usuarios (2026-08-28) -- orden estricto: copiar
        # antes de repuntar FK (la constraint valida contra personal(id)),
        # habilitar el polimorfismo antes de backfillear, backfillear antes
        # del CHECK (que exige exactamente una llena), y borrar de usuarios
        # solo al final, con todo lo demás ya migrado.
        _COPIAR_ADMIN_GESTOR_A_PERSONAL,
        _REPUNTAR_FK_DE_PERSONAL,
        _POLIMORFISMO_ACTOR_RESERVAS_NOTIFICACIONES,
        _FK_PERSONAL_ID_RESERVAS_NOTIFICACIONES_CONTROL_CAMBIOS,
        _BACKFILL_ACTOR_RESERVAS_NOTIFICACIONES_CONTROL_CAMBIOS,
        _CHECK_ACTOR_UNICO_RESERVAS_NOTIFICACIONES_CONTROL_CAMBIOS,
        _BORRAR_ADMIN_GESTOR_DE_USUARIOS,
        # Fase 2026-08-29: marca de idempotencia del recordatorio de reserva
        # próxima (`services/recordatorios.py`) -- nullable, sin backfill:
        # las reservas existentes simplemente no tienen recordatorio enviado
        # todavía, que es el estado correcto para ellas.
        "ALTER TABLE reservas ADD COLUMN IF NOT EXISTS recordatorio_enviado_en TIMESTAMPTZ",
        # Fase 2026-08-29: correlación de las N filas de una reserva
        # recurrente (`services/reservas.py::crear_reserva`) -- nullable,
        # sin backfill (NULL = no recurrente, la inmensa mayoría).
        "ALTER TABLE reservas ADD COLUMN IF NOT EXISTS serie_id UUID",
        "CREATE INDEX IF NOT EXISTS ix_reservas_serie_id ON reservas (serie_id)",
    )

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))
