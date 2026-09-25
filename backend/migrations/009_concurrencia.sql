-- Garantías de disponibilidad y retiro por préstamo (DB-12).
--
-- Instala lo que ADR-001 dejó pendiente de diseño: la exclusión temporal
-- por solapamiento (ya prevista con las columnas `periodo`/`bloqueante` que
-- BK-08 encontró ya creadas, pero nunca sincronizadas por nada) y la
-- garantía de compromiso físico único por `recurso_id` para
-- RECURSO_CAMPUS/RECURSO_EXTERNO (RN-DIS-06, RN-RES-14, hallazgo 1 del
-- 2026-09-24), que la exclusión temporal por sí sola no cubre: dos
-- préstamos con fechas distintas no se solapan en periodo, pero deben
-- seguir siendo incompatibles.
--
-- DISEÑO
--
-- 1. `reserva_recursos` gana `compromiso_fisico`, una proyección técnica
--    aparte de `bloqueante`: `bloqueante` sigue protegiendo solapamientos
--    de periodo (interno por franja, complementarios de espacio, y también
--    campus/externo como caso particular); `compromiso_fisico` protege la
--    exclusividad física de campus/externo con independencia del periodo,
--    vía un índice único parcial sobre `recurso_id`. Las dos conviven sin
--    conflicto: un recurso con compromiso físico vigente nunca tiene una
--    segunda fila con compromiso físico, así que la exclusión temporal no
--    llega a evaluar ese caso.
--
-- 2. Cada tipo calcula su periodo distinto (RN-DIS-06, RN-TIP-PE-24,
--    RN-TIP-RI-13, ADR-001):
--    - ESPACIO (complementarios, rol ADICIONAL): copia el periodo de
--      `reserva_espacio`, salvo que se haya incorporado durante la
--      ejecución (`incorporado_at` más tardío que el inicio de la franja).
--      Nunca es compromiso físico (RN-TIP-PE-28).
--    - RECURSO_INTERNO: franja horaria propia del detalle, con el mismo
--      ajuste de `incorporado_at`. Nunca es compromiso físico.
--    - RECURSO_CAMPUS / RECURSO_EXTERNO: día completo desde `fecha_salida`
--      hasta el día siguiente a `fecha_devolucion_estimada`, o rango
--      abierto `[inicio, )` mientras exista una entrega sin devolución en
--      `reserva_ejecucion_recursos` (decisión DB-11: la entrega abre el
--      rango). Siempre es compromiso físico mientras esté ASIGNADO en un
--      estado bloqueante.
--    Todas las conversiones usan `America/Bogota` explícito (DB-11), nunca
--    la zona implícita de la conexión.
--
-- 3. Los disparadores recalculan solo cuando cambia algo que afecta al
--    periodo: la asociación (`estado_asignacion`, `incorporado_at`), el
--    detalle por tipo, el registro de entrega/devolución, o el estado de
--    la reserva. La función de recálculo hace un UPDATE que nunca toca
--    esas mismas columnas de origen, así que los disparadores declarados
--    con `UPDATE OF <columnas de origen>` no se reactivan a sí mismos: no
--    hace falta guardia de recursión.
--
-- 4. `establecer_compromiso_fisico()` es la única vía para el efecto de
--    RN-TIP-PE-28: bloquea (`FOR UPDATE`) las reservas de espacio que
--    tienen ese recurso como complementario vigente —eso protege también
--    la carrera con el inicio automático del espacio, que solo puede
--    tocar esa misma fila de `reservas.reservas` después de que esta
--    función suelte el bloqueo—, rechaza si alguna está EN_EJECUCION, y si
--    ninguna lo está, retira las demás con su trazabilidad completa en la
--    misma transacción. No inserta la nueva asignación física: eso lo hace
--    el llamador a continuación, en la misma transacción, y el índice
--    único de compromiso físico la protege igual que a cualquier otra.
--
-- Ejecutar con: psql -v ON_ERROR_STOP=1

BEGIN;
SET LOCAL lock_timeout = '5s';
SET LOCAL statement_timeout = '60s';

-- btree_gist ya está instalada en este entorno; se declara igual por si
-- este script corre sobre una base que todavía no la tiene.
CREATE EXTENSION IF NOT EXISTS btree_gist;

-- --- 1. Columnas nuevas -----------------------------------------------------

ALTER TABLE reservas.reserva_recursos
    ADD COLUMN compromiso_fisico   boolean NOT NULL DEFAULT false,
    ADD COLUMN retirado_at         timestamptz,
    ADD COLUMN causa_retiro        varchar(40),
    ADD COLUMN reserva_causante_id integer REFERENCES reservas.reservas(id);

ALTER TABLE reservas.reserva_recursos
    ADD CONSTRAINT ck_reserva_recursos_retiro_prestamo CHECK (
        (causa_retiro IS NULL AND retirado_at IS NULL AND reserva_causante_id IS NULL)
        OR (
            causa_retiro = 'PRESTAMO_FISICO'
            AND retirado_at IS NOT NULL
            AND reserva_causante_id IS NOT NULL
            AND estado_asignacion = 'RETIRADO'
            AND rol = 'ADICIONAL'
        )
    );

-- --- 2. Función auxiliar: ¿el estado de la reserva bloquea? -----------------

CREATE OR REPLACE FUNCTION reservas.es_estado_bloqueante(p_estado_id integer)
RETURNS boolean
LANGUAGE sql
STABLE
AS $$
    SELECT codigo IN ('SOLICITADA', 'APROBADA', 'EN_EJECUCION')
    FROM reservas.estados_reserva
    WHERE id = p_estado_id;
$$;

-- --- 3. Recálculo de la proyección de una fila de reserva_recursos ---------

CREATE OR REPLACE FUNCTION reservas.recalcular_proyeccion_recurso(p_id integer)
RETURNS void
LANGUAGE plpgsql
AS $$
DECLARE
    v_rec         reservas.reserva_recursos%ROWTYPE;
    v_reserva_id  integer;
    v_estado_id   integer;
    v_tipo_codigo varchar;
    v_inicio      timestamptz;
    v_fin         timestamptz;
    v_periodo     tstzrange;
    v_bloqueante  boolean := false;
    v_compromiso  boolean := false;
    v_abierta     boolean;
BEGIN
    SELECT * INTO v_rec FROM reservas.reserva_recursos WHERE id = p_id FOR UPDATE;
    IF NOT FOUND THEN
        RETURN;
    END IF;

    SELECT r.id, r.estado_id, t.codigo
      INTO v_reserva_id, v_estado_id, v_tipo_codigo
      FROM reservas.reservas r
      JOIN reservas.tipos_reserva t ON t.id = r.tipo_reserva_id
     WHERE r.id = v_rec.reserva_id;

    IF v_rec.estado_asignacion = 'ASIGNADO' AND reservas.es_estado_bloqueante(v_estado_id) THEN

        IF v_tipo_codigo = 'ESPACIO' THEN
            -- Complementario: comparte la franja del espacio (RN-TIP-PE-24),
            -- salvo incorporación posterior durante la ejecución.
            SELECT (lower(periodo) AT TIME ZONE 'America/Bogota'),
                   (upper(periodo) AT TIME ZONE 'America/Bogota')
              INTO v_inicio, v_fin
              FROM reservas.reserva_espacio
             WHERE reserva_id = v_reserva_id;
            IF v_rec.incorporado_at IS NOT NULL
               AND (v_inicio IS NULL OR v_rec.incorporado_at > v_inicio) THEN
                v_inicio := v_rec.incorporado_at;
            END IF;
            IF v_inicio IS NOT NULL AND v_fin IS NOT NULL AND v_inicio < v_fin THEN
                v_periodo := tstzrange(v_inicio, v_fin, '[)');
                v_bloqueante := true;
            END IF;

        ELSIF v_tipo_codigo = 'RECURSO_INTERNO' THEN
            SELECT (fecha + hora_inicio) AT TIME ZONE 'America/Bogota',
                   (fecha + hora_fin) AT TIME ZONE 'America/Bogota'
              INTO v_inicio, v_fin
              FROM reservas.reserva_recurso_interno
             WHERE reserva_id = v_reserva_id;
            IF v_rec.incorporado_at IS NOT NULL
               AND (v_inicio IS NULL OR v_rec.incorporado_at > v_inicio) THEN
                v_inicio := v_rec.incorporado_at;
            END IF;
            IF v_inicio IS NOT NULL AND v_fin IS NOT NULL AND v_inicio < v_fin THEN
                v_periodo := tstzrange(v_inicio, v_fin, '[)');
                v_bloqueante := true;
            END IF;

        ELSIF v_tipo_codigo IN ('RECURSO_CAMPUS', 'RECURSO_EXTERNO') THEN
            IF v_tipo_codigo = 'RECURSO_CAMPUS' THEN
                SELECT (fecha_salida::timestamp) AT TIME ZONE 'America/Bogota',
                       ((fecha_devolucion_estimada + 1)::timestamp) AT TIME ZONE 'America/Bogota'
                  INTO v_inicio, v_fin
                  FROM reservas.reserva_recurso_campus
                 WHERE reserva_id = v_reserva_id;
            ELSE
                SELECT (fecha_salida::timestamp) AT TIME ZONE 'America/Bogota',
                       ((fecha_devolucion_estimada + 1)::timestamp) AT TIME ZONE 'America/Bogota'
                  INTO v_inicio, v_fin
                  FROM reservas.reserva_recurso_externo
                 WHERE reserva_id = v_reserva_id;
            END IF;
            IF v_rec.incorporado_at IS NOT NULL
               AND (v_inicio IS NULL OR v_rec.incorporado_at > v_inicio) THEN
                v_inicio := v_rec.incorporado_at;
            END IF;

            SELECT true INTO v_abierta
              FROM reservas.reserva_ejecucion_recursos
             WHERE reserva_recurso_id = v_rec.id AND devuelto_at IS NULL
             LIMIT 1;

            IF v_inicio IS NOT NULL THEN
                IF v_abierta THEN
                    v_periodo := tstzrange(v_inicio, NULL, '[)');
                ELSIF v_fin IS NOT NULL THEN
                    v_periodo := tstzrange(v_inicio, v_fin, '[)');
                END IF;
                IF v_periodo IS NOT NULL THEN
                    v_bloqueante := true;
                    v_compromiso := true;
                END IF;
            END IF;
        END IF;
    END IF;

    UPDATE reservas.reserva_recursos
       SET periodo = v_periodo, bloqueante = v_bloqueante, compromiso_fisico = v_compromiso
     WHERE id = p_id;
END;
$$;

-- --- 4. Disparadores que disparan el recálculo ------------------------------

CREATE OR REPLACE FUNCTION reservas.trg_reserva_recursos_recalcular()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    PERFORM reservas.recalcular_proyeccion_recurso(NEW.id);
    RETURN NULL;
END;
$$;

CREATE TRIGGER trg_reserva_recursos_recalcular
    AFTER INSERT OR UPDATE OF estado_asignacion, incorporado_at ON reservas.reserva_recursos
    FOR EACH ROW EXECUTE FUNCTION reservas.trg_reserva_recursos_recalcular();

CREATE OR REPLACE FUNCTION reservas.trg_detalle_recurso_recalcular()
RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE
    r record;
BEGIN
    FOR r IN SELECT id FROM reservas.reserva_recursos WHERE reserva_id = NEW.reserva_id LOOP
        PERFORM reservas.recalcular_proyeccion_recurso(r.id);
    END LOOP;
    RETURN NULL;
END;
$$;

CREATE TRIGGER trg_reserva_recurso_interno_recalcular
    AFTER INSERT OR UPDATE OF fecha, hora_inicio, hora_fin ON reservas.reserva_recurso_interno
    FOR EACH ROW EXECUTE FUNCTION reservas.trg_detalle_recurso_recalcular();

CREATE TRIGGER trg_reserva_recurso_campus_recalcular
    AFTER INSERT OR UPDATE OF fecha_salida, fecha_devolucion_estimada ON reservas.reserva_recurso_campus
    FOR EACH ROW EXECUTE FUNCTION reservas.trg_detalle_recurso_recalcular();

CREATE TRIGGER trg_reserva_recurso_externo_recalcular
    AFTER INSERT OR UPDATE OF fecha_salida, fecha_devolucion_estimada ON reservas.reserva_recurso_externo
    FOR EACH ROW EXECUTE FUNCTION reservas.trg_detalle_recurso_recalcular();

CREATE OR REPLACE FUNCTION reservas.trg_ejecucion_recurso_recalcular()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    PERFORM reservas.recalcular_proyeccion_recurso(COALESCE(NEW.reserva_recurso_id, OLD.reserva_recurso_id));
    RETURN NULL;
END;
$$;

CREATE TRIGGER trg_reserva_ejecucion_recalcular
    AFTER INSERT OR UPDATE OF devuelto_at ON reservas.reserva_ejecucion_recursos
    FOR EACH ROW EXECUTE FUNCTION reservas.trg_ejecucion_recurso_recalcular();

-- reservas: al cambiar el estado, sincroniza espacio (bloqueante) y todas
-- las asignaciones de recursos de esa reserva.
CREATE OR REPLACE FUNCTION reservas.trg_reservas_estado_recalcular()
RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE
    r record;
BEGIN
    UPDATE reservas.reserva_espacio
       SET bloqueante = reservas.es_estado_bloqueante(NEW.estado_id)
     WHERE reserva_id = NEW.id;

    FOR r IN SELECT id FROM reservas.reserva_recursos WHERE reserva_id = NEW.id LOOP
        PERFORM reservas.recalcular_proyeccion_recurso(r.id);
    END LOOP;
    RETURN NULL;
END;
$$;

CREATE TRIGGER trg_reservas_estado_recalcular
    AFTER UPDATE OF estado_id ON reservas.reservas
    FOR EACH ROW EXECUTE FUNCTION reservas.trg_reservas_estado_recalcular();

-- reserva_espacio: `periodo` ya es GENERATED; solo falta fijar `bloqueante`
-- al insertar, desde el estado vigente de la reserva ya existente.
CREATE OR REPLACE FUNCTION reservas.trg_reserva_espacio_insertar()
RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE
    v_estado_id integer;
BEGIN
    SELECT estado_id INTO v_estado_id FROM reservas.reservas WHERE id = NEW.reserva_id;
    NEW.bloqueante := reservas.es_estado_bloqueante(v_estado_id);
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_reserva_espacio_insertar
    BEFORE INSERT ON reservas.reserva_espacio
    FOR EACH ROW EXECUTE FUNCTION reservas.trg_reserva_espacio_insertar();

-- Una entrega abierta no se libera cambiando estado_asignacion: ninguna vía
-- —manual ni automática— puede eludir la devolución dejando de contar la
-- asignación como vigente mientras `reserva_ejecucion_recursos` siga sin
-- `devuelto_at` para esa fila (verificación 6 de ADR-001).
CREATE OR REPLACE FUNCTION reservas.trg_reserva_recursos_impedir_liberar_entrega_abierta()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    IF OLD.estado_asignacion = 'ASIGNADO' AND NEW.estado_asignacion <> 'ASIGNADO' THEN
        IF EXISTS (
            SELECT 1 FROM reservas.reserva_ejecucion_recursos
             WHERE reserva_recurso_id = OLD.id AND devuelto_at IS NULL
        ) THEN
            RAISE EXCEPTION USING
                ERRCODE = 'P0001',
                MESSAGE = format('El recurso de la asignación %s tiene una entrega abierta; debe registrarse la devolución antes de retirarlo.', OLD.id);
        END IF;
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_reserva_recursos_impedir_liberar_entrega_abierta
    BEFORE UPDATE OF estado_asignacion ON reservas.reserva_recursos
    FOR EACH ROW EXECUTE FUNCTION reservas.trg_reserva_recursos_impedir_liberar_entrega_abierta();

-- --- 5. Restricciones de exclusión e índice de compromiso físico -----------

ALTER TABLE reservas.reserva_espacio
    ADD CONSTRAINT ex_reserva_espacio_solape
    EXCLUDE USING gist (espacio_id WITH =, periodo WITH &&)
    WHERE (bloqueante AND periodo IS NOT NULL);

ALTER TABLE reservas.reserva_recursos
    ADD CONSTRAINT ex_reserva_recursos_solape
    EXCLUDE USING gist (recurso_id WITH =, periodo WITH &&)
    WHERE (bloqueante AND periodo IS NOT NULL);

CREATE UNIQUE INDEX uq_reserva_recursos_compromiso_fisico
    ON reservas.reserva_recursos (recurso_id)
    WHERE compromiso_fisico;

-- --- 6. Retiro atómico de complementarios al establecer un préstamo --------
-- (RN-TIP-PE-28). El llamador invoca esta función ANTES de insertar o
-- reactivar la asignación física de campus/externo, en la misma
-- transacción; si lanza excepción, nada se ha escrito todavía.

CREATE OR REPLACE FUNCTION reservas.establecer_compromiso_fisico(
    p_recurso_id integer,
    p_reserva_causante_id integer
) RETURNS void
LANGUAGE plpgsql
AS $$
DECLARE
    r record;
BEGIN
    FOR r IN
        SELECT res.id AS reserva_id, es.codigo AS estado_codigo
          FROM reservas.reserva_recursos rr
          JOIN reservas.reservas res ON res.id = rr.reserva_id
          JOIN reservas.tipos_reserva t ON t.id = res.tipo_reserva_id
          JOIN reservas.estados_reserva es ON es.id = res.estado_id
         WHERE rr.recurso_id = p_recurso_id
           AND rr.estado_asignacion = 'ASIGNADO'
           AND t.codigo = 'ESPACIO'
           AND es.codigo IN ('SOLICITADA', 'APROBADA', 'EN_EJECUCION')
         FOR UPDATE OF res
    LOOP
        IF r.estado_codigo = 'EN_EJECUCION' THEN
            RAISE EXCEPTION USING
                ERRCODE = 'P0001',
                MESSAGE = format('El recurso %s está en uso por un espacio en ejecución (reserva %s).', p_recurso_id, r.reserva_id);
        END IF;
    END LOOP;

    UPDATE reservas.reserva_recursos rr
       SET estado_asignacion = 'RETIRADO',
           retirado_at = now(),
           causa_retiro = 'PRESTAMO_FISICO',
           reserva_causante_id = p_reserva_causante_id
      FROM reservas.reservas res, reservas.tipos_reserva t
     WHERE rr.reserva_id = res.id
       AND res.tipo_reserva_id = t.id
       AND rr.recurso_id = p_recurso_id
       AND rr.estado_asignacion = 'ASIGNADO'
       AND t.codigo = 'ESPACIO';
END;
$$;

INSERT INTO public.schema_migrations (nombre) VALUES ('009_concurrencia');

COMMIT;
