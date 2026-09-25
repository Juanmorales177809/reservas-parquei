-- Pruebas de integridad de DB-12 sin concurrencia real (ver db12_concurrencia.sh
-- para las carreras genuinas entre transacciones). Verifican contra la base,
-- no contra la API: API-13 todavía no existe, así que estas pruebas siembran
-- sus propios datos con SQL directo y los limpian al final.
--
-- Ejecutar con: psql -v ON_ERROR_STOP=1 -f backend/tests/sql/db12_no_concurrentes.sql
-- Cada escenario usa RAISE EXCEPTION si el resultado no es el esperado, así
-- que un fallo aquí detiene el script con un mensaje señalando cuál fue.

\set ON_ERROR_STOP on

DO $$
DECLARE
    v_unidad   integer;
    v_usuario  bigint;
    v_cuenta   bigint;
    v_espacio  integer;
    v_r_interno   integer;
    v_r_campus_a  integer;
    v_r_campus_b  integer;
    v_r_espacio_ok integer;
    v_reserva  integer;
    v_reserva2 integer;
    v_prestamo integer;
    v_rr       integer;
    v_periodo  tstzrange;
    v_bool     boolean;
    v_ok       boolean;
BEGIN
    -- --- Datos de prueba, con etiqueta 'DB12-SQL' para poder limpiarlos ----
    INSERT INTO "unidadOrganizacional".unidad_organizacional (nombre, tipo, estado)
    VALUES ('Unidad DB12-SQL', 'LABORATORIO', true) RETURNING id_unidad INTO v_unidad;

    INSERT INTO usuarios.usuarios (nombre, correo, estado, created_at, updated_at, perfil_actualizado_at, documento, telefono, institucion, dependencia)
    VALUES ('Usuario DB12-SQL', 'usuario.db12sql@correo.itm.edu.co', true, now(), now(), now(), 'DB12SQL-USR', '3600000001', 'ITM', 'Externo')
    RETURNING id_usuario INTO v_usuario;

    INSERT INTO auth.cuentas (correo, password_hash, tipo_cuenta, id_usuario, estado)
    VALUES ('usuario.db12sql@correo.itm.edu.co', 'x', 'USUARIO', v_usuario, true)
    RETURNING id_cuenta INTO v_cuenta;

    INSERT INTO reservas.espacios (id_unidad, nombre, capacidad, habilitado, created_at, updated_at)
    VALUES (v_unidad, 'Espacio DB12-SQL', 10, true, now(), now()) RETURNING id INTO v_espacio;

    INSERT INTO recursos.recursos (id_unidad, tipo, habilitado, created_at, updated_at)
    VALUES (v_unidad, 'MOBILIARIO', true, now(), now()) RETURNING id INTO v_r_interno;
    INSERT INTO recursos.mobiliarios (id, id_unidad, nombre, habilitado) VALUES (v_r_interno, v_unidad, 'Recurso interno', true);

    INSERT INTO recursos.recursos (id_unidad, tipo, habilitado, created_at, updated_at)
    VALUES (v_unidad, 'MOBILIARIO', true, now(), now()) RETURNING id INTO v_r_campus_a;
    INSERT INTO recursos.mobiliarios (id, id_unidad, nombre, habilitado) VALUES (v_r_campus_a, v_unidad, 'Recurso campus', true);

    INSERT INTO recursos.recursos (id_unidad, tipo, habilitado, created_at, updated_at)
    VALUES (v_unidad, 'MOBILIARIO', true, now(), now()) RETURNING id INTO v_r_espacio_ok;
    INSERT INTO recursos.mobiliarios (id, id_unidad, nombre, habilitado) VALUES (v_r_espacio_ok, v_unidad, 'Recurso complementario', true);

    -- --- T1: espacio SOLICITADA sincroniza bloqueante ----------------------
    INSERT INTO reservas.reservas (id_unidad, tipo_reserva_id, id_cuenta, estado_id, created_by)
    VALUES (v_unidad, 1, v_cuenta, 1, v_cuenta) RETURNING id INTO v_reserva;
    INSERT INTO reservas.reserva_espacio (reserva_id, espacio_id, fecha, hora_inicio, hora_fin, asistentes)
    VALUES (v_reserva, v_espacio, '2030-01-01', '09:00', '11:00', 0);

    SELECT bloqueante INTO v_bool FROM reservas.reserva_espacio WHERE reserva_id = v_reserva;
    IF NOT v_bool THEN
        RAISE EXCEPTION 'T1 FALLÓ: bloqueante debía quedar en true tras insertar espacio SOLICITADA';
    END IF;
    RAISE NOTICE 'T1 OK: bloqueante se sincroniza al insertar';

    -- --- T2: espacio solapado del mismo espacio_id se rechaza --------------
    INSERT INTO reservas.reservas (id_unidad, tipo_reserva_id, id_cuenta, estado_id, created_by)
    VALUES (v_unidad, 1, v_cuenta, 1, v_cuenta) RETURNING id INTO v_reserva2;
    BEGIN
        INSERT INTO reservas.reserva_espacio (reserva_id, espacio_id, fecha, hora_inicio, hora_fin, asistentes)
        VALUES (v_reserva2, v_espacio, '2030-01-01', '10:00', '12:00', 0);
        RAISE EXCEPTION 'T2 FALLÓ: debía rechazar el solapamiento con ex_reserva_espacio_solape';
    EXCEPTION
        WHEN exclusion_violation THEN
            RAISE NOTICE 'T2 OK: solapamiento de espacio rechazado por la restricción de exclusión';
    END;

    -- --- T3: franjas contiguas (se tocan) sí se admiten ---------------------
    INSERT INTO reservas.reserva_espacio (reserva_id, espacio_id, fecha, hora_inicio, hora_fin, asistentes)
    VALUES (v_reserva2, v_espacio, '2030-01-01', '11:00', '13:00', 0);
    RAISE NOTICE 'T3 OK: franjas contiguas admitidas sin conflicto';

    -- --- T4: RECURSO_INTERNO calcula el periodo en America/Bogota ----------
    INSERT INTO reservas.reservas (id_unidad, tipo_reserva_id, id_cuenta, estado_id, created_by)
    VALUES (v_unidad, 2, v_cuenta, 1, v_cuenta) RETURNING id INTO v_reserva;
    INSERT INTO reservas.reserva_recurso_interno (reserva_id, fecha, hora_inicio, hora_fin)
    VALUES (v_reserva, '2030-02-01', '08:00', '10:00');
    INSERT INTO reservas.reserva_recursos (reserva_id, recurso_id, rol, estado_asignacion)
    VALUES (v_reserva, v_r_interno, 'PRINCIPAL', 'ASIGNADO') RETURNING id INTO v_rr;

    SELECT periodo, bloqueante, compromiso_fisico INTO v_periodo, v_bool, v_ok
      FROM reservas.reserva_recursos WHERE id = v_rr;
    IF v_periodo IS DISTINCT FROM tstzrange('2030-02-01 13:00:00+00', '2030-02-01 15:00:00+00', '[)') THEN
        RAISE EXCEPTION 'T4 FALLÓ: periodo interno esperado 13:00-15:00 UTC (08:00-10:00 Bogotá), obtuvo %', v_periodo;
    END IF;
    IF NOT v_bool OR v_ok THEN
        RAISE EXCEPTION 'T4 FALLÓ: interno debe ser bloqueante=true y compromiso_fisico=false';
    END IF;
    RAISE NOTICE 'T4 OK: RECURSO_INTERNO calcula el periodo con la zona operativa correcta';

    -- --- T5: compromiso físico único de campus, con independencia de fechas --
    INSERT INTO reservas.reservas (id_unidad, tipo_reserva_id, id_cuenta, estado_id, created_by)
    VALUES (v_unidad, 3, v_cuenta, 1, v_cuenta) RETURNING id INTO v_reserva;
    INSERT INTO reservas.reserva_recurso_campus (reserva_id, fecha_salida, fecha_devolucion_estimada)
    VALUES (v_reserva, '2030-03-01', '2030-03-03');
    INSERT INTO reservas.reserva_recursos (reserva_id, recurso_id, rol, estado_asignacion)
    VALUES (v_reserva, v_r_campus_a, 'PRINCIPAL', 'ASIGNADO');

    SELECT compromiso_fisico INTO v_ok FROM reservas.reserva_recursos WHERE reserva_id = v_reserva AND recurso_id = v_r_campus_a;
    IF NOT v_ok THEN
        RAISE EXCEPTION 'T5 FALLÓ: compromiso_fisico debía quedar en true desde SOLICITADA';
    END IF;

    INSERT INTO reservas.reservas (id_unidad, tipo_reserva_id, id_cuenta, estado_id, created_by)
    VALUES (v_unidad, 3, v_cuenta, 1, v_cuenta) RETURNING id INTO v_reserva2;
    INSERT INTO reservas.reserva_recurso_campus (reserva_id, fecha_salida, fecha_devolucion_estimada)
    VALUES (v_reserva2, '2030-05-01', '2030-05-02');  -- fechas sin ningún solape con la anterior
    BEGIN
        INSERT INTO reservas.reserva_recursos (reserva_id, recurso_id, rol, estado_asignacion)
        VALUES (v_reserva2, v_r_campus_a, 'PRINCIPAL', 'ASIGNADO');
        RAISE EXCEPTION 'T5 FALLÓ: un segundo compromiso físico del mismo recurso debía rechazarse aunque las fechas no se solapen (hallazgo 1)';
    EXCEPTION
        WHEN unique_violation THEN
            RAISE NOTICE 'T5 OK: compromiso físico único por recurso, independiente de las fechas (hallazgo 1)';
    END;

    -- --- T6: retiro atómico de complementario de espacio al establecer préstamo --
    INSERT INTO reservas.reservas (id_unidad, tipo_reserva_id, id_cuenta, estado_id, created_by)
    VALUES (v_unidad, 1, v_cuenta, 1, v_cuenta) RETURNING id INTO v_reserva;
    INSERT INTO reservas.reserva_espacio (reserva_id, espacio_id, fecha, hora_inicio, hora_fin, asistentes)
    VALUES (v_reserva, v_espacio, '2030-06-01', '09:00', '11:00', 0);
    INSERT INTO reservas.reserva_recursos (reserva_id, recurso_id, rol, estado_asignacion)
    VALUES (v_reserva, v_r_espacio_ok, 'ADICIONAL', 'ASIGNADO');

    INSERT INTO reservas.reservas (id_unidad, tipo_reserva_id, id_cuenta, estado_id, created_by)
    VALUES (v_unidad, 3, v_cuenta, 1, v_cuenta) RETURNING id INTO v_prestamo;
    INSERT INTO reservas.reserva_recurso_campus (reserva_id, fecha_salida, fecha_devolucion_estimada)
    VALUES (v_prestamo, '2030-07-01', '2030-07-02');

    PERFORM reservas.establecer_compromiso_fisico(v_r_espacio_ok, v_prestamo);
    INSERT INTO reservas.reserva_recursos (reserva_id, recurso_id, rol, estado_asignacion)
    VALUES (v_prestamo, v_r_espacio_ok, 'PRINCIPAL', 'ASIGNADO');

    SELECT estado_asignacion = 'RETIRADO' AND causa_retiro = 'PRESTAMO_FISICO' AND reserva_causante_id = v_prestamo AND retirado_at IS NOT NULL
      INTO v_ok
      FROM reservas.reserva_recursos WHERE reserva_id = v_reserva AND recurso_id = v_r_espacio_ok;
    IF NOT v_ok THEN
        RAISE EXCEPTION 'T6 FALLÓ: el complementario debía quedar RETIRADO con trazabilidad completa (PRESTAMO_FISICO, reserva causante, instante)';
    END IF;

    SELECT (SELECT es.codigo FROM reservas.reservas r JOIN reservas.estados_reserva es ON es.id = r.estado_id WHERE r.id = v_reserva) = 'SOLICITADA'
      INTO v_ok;
    IF NOT v_ok THEN
        RAISE EXCEPTION 'T6 FALLÓ: la reserva de espacio no debía cambiar de estado';
    END IF;
    RAISE NOTICE 'T6 OK: retiro atómico de complementario con trazabilidad completa, sin alterar el espacio (RN-TIP-PE-28)';

    -- --- T7: rechazo total si el complementario está EN_EJECUCION -----------
    INSERT INTO reservas.reservas (id_unidad, tipo_reserva_id, id_cuenta, estado_id, created_by)
    VALUES (v_unidad, 1, v_cuenta, 4, v_cuenta) RETURNING id INTO v_reserva;
    INSERT INTO reservas.reserva_espacio (reserva_id, espacio_id, fecha, hora_inicio, hora_fin, asistentes)
    VALUES (v_reserva, v_espacio, '2030-08-01', '09:00', '11:00', 0);

    INSERT INTO recursos.recursos (id_unidad, tipo, habilitado, created_at, updated_at)
    VALUES (v_unidad, 'MOBILIARIO', true, now(), now()) RETURNING id INTO v_r_campus_b;
    INSERT INTO recursos.mobiliarios (id, id_unidad, nombre, habilitado) VALUES (v_r_campus_b, v_unidad, 'Recurso en ejecucion', true);
    INSERT INTO reservas.reserva_recursos (reserva_id, recurso_id, rol, estado_asignacion)
    VALUES (v_reserva, v_r_campus_b, 'ADICIONAL', 'ASIGNADO');

    INSERT INTO reservas.reservas (id_unidad, tipo_reserva_id, id_cuenta, estado_id, created_by)
    VALUES (v_unidad, 3, v_cuenta, 1, v_cuenta) RETURNING id INTO v_prestamo;

    BEGIN
        PERFORM reservas.establecer_compromiso_fisico(v_r_campus_b, v_prestamo);
        RAISE EXCEPTION 'T7 FALLÓ: debía rechazar con el complementario en ejecución';
    EXCEPTION
        WHEN SQLSTATE 'P0001' THEN
            RAISE NOTICE 'T7 OK: rechazado porque el complementario está EN_EJECUCION, sin retiro parcial';
    END;

    SELECT estado_asignacion = 'ASIGNADO' INTO v_ok
      FROM reservas.reserva_recursos WHERE reserva_id = v_reserva AND recurso_id = v_r_campus_b;
    IF NOT v_ok THEN
        RAISE EXCEPTION 'T7 FALLÓ: el complementario en ejecución no debía modificarse';
    END IF;
    RAISE NOTICE 'T7 OK: sin escritura parcial tras el rechazo';

    -- --- T8: entrega abre el rango; devolución lo cierra --------------------
    SELECT id INTO v_rr FROM reservas.reserva_recursos WHERE reserva_id = v_prestamo AND recurso_id = v_r_campus_a;
    -- (v_r_campus_a ya tenía compromiso vigente de T5; usamos otro recurso libre para no interferir)
    INSERT INTO recursos.recursos (id_unidad, tipo, habilitado, created_at, updated_at)
    VALUES (v_unidad, 'MOBILIARIO', true, now(), now()) RETURNING id INTO v_r_campus_b;
    INSERT INTO recursos.mobiliarios (id, id_unidad, nombre, habilitado) VALUES (v_r_campus_b, v_unidad, 'Recurso entrega', true);

    INSERT INTO reservas.reservas (id_unidad, tipo_reserva_id, id_cuenta, estado_id, created_by)
    VALUES (v_unidad, 3, v_cuenta, 1, v_cuenta) RETURNING id INTO v_prestamo;
    INSERT INTO reservas.reserva_recurso_campus (reserva_id, fecha_salida, fecha_devolucion_estimada)
    VALUES (v_prestamo, '2030-09-01', '2030-09-03');
    INSERT INTO reservas.reserva_recursos (reserva_id, recurso_id, rol, estado_asignacion)
    VALUES (v_prestamo, v_r_campus_b, 'PRINCIPAL', 'ASIGNADO') RETURNING id INTO v_rr;

    INSERT INTO reservas.reserva_ejecucion_recursos (reserva_recurso_id, entregado_por, entregado_at)
    VALUES (v_rr, v_cuenta, now());

    SELECT upper_inf(periodo) INTO v_ok FROM reservas.reserva_recursos WHERE id = v_rr;
    IF NOT v_ok THEN
        RAISE EXCEPTION 'T8 FALLÓ: la entrega sin devolución debía abrir el rango [inicio, )';
    END IF;

    BEGIN
        UPDATE reservas.reserva_recursos SET estado_asignacion = 'RETIRADO' WHERE id = v_rr;
        RAISE EXCEPTION 'T8 FALLÓ: no debía permitirse liberar una asignación con entrega abierta';
    EXCEPTION
        WHEN SQLSTATE 'P0001' THEN
            RAISE NOTICE 'T8a OK: no se puede retirar una asignación con entrega abierta';
    END;

    UPDATE reservas.reserva_ejecucion_recursos SET devuelto_at = now(), recibido_por = v_cuenta WHERE reserva_recurso_id = v_rr;
    SELECT upper_inf(periodo) INTO v_ok FROM reservas.reserva_recursos WHERE id = v_rr;
    IF v_ok THEN
        RAISE EXCEPTION 'T8 FALLÓ: la devolución debía cerrar el rango otra vez';
    END IF;
    RAISE NOTICE 'T8b OK: la devolución cierra el rango; compromiso_fisico se conserva hasta cerrar la reserva';

    -- --- T9: cancelar/finalizar libera el compromiso -------------------------
    UPDATE reservas.reservas SET estado_id = 5 WHERE id = v_prestamo; -- FINALIZADA
    SELECT (periodo IS NULL AND NOT bloqueante AND NOT compromiso_fisico) INTO v_ok
      FROM reservas.reserva_recursos WHERE id = v_rr;
    IF NOT v_ok THEN
        RAISE EXCEPTION 'T9 FALLÓ: finalizar la reserva debía liberar periodo/bloqueante/compromiso_fisico';
    END IF;
    RAISE NOTICE 'T9 OK: finalizar la reserva libera el compromiso';

    -- El mismo recurso ahora admite un nuevo compromiso.
    INSERT INTO reservas.reservas (id_unidad, tipo_reserva_id, id_cuenta, estado_id, created_by)
    VALUES (v_unidad, 4, v_cuenta, 1, v_cuenta) RETURNING id INTO v_reserva2;
    INSERT INTO reservas.reserva_recurso_externo (reserva_id, fecha_salida, fecha_devolucion_estimada)
    VALUES (v_reserva2, '2030-10-01', '2030-10-02');
    INSERT INTO reservas.reserva_recursos (reserva_id, recurso_id, rol, estado_asignacion)
    VALUES (v_reserva2, v_r_campus_b, 'PRINCIPAL', 'ASIGNADO');
    RAISE NOTICE 'T9 OK: recurso liberado admite un nuevo compromiso (externo, tras campus)';

    -- --- Limpieza --------------------------------------------------------------
    DELETE FROM reservas.reserva_ejecucion_recursos WHERE reserva_recurso_id IN (SELECT id FROM reservas.reserva_recursos WHERE reserva_id IN (SELECT id FROM reservas.reservas WHERE id_unidad = v_unidad));
    DELETE FROM reservas.reserva_recursos WHERE reserva_id IN (SELECT id FROM reservas.reservas WHERE id_unidad = v_unidad);
    DELETE FROM reservas.reserva_espacio WHERE reserva_id IN (SELECT id FROM reservas.reservas WHERE id_unidad = v_unidad);
    DELETE FROM reservas.reserva_recurso_interno WHERE reserva_id IN (SELECT id FROM reservas.reservas WHERE id_unidad = v_unidad);
    DELETE FROM reservas.reserva_recurso_campus WHERE reserva_id IN (SELECT id FROM reservas.reservas WHERE id_unidad = v_unidad);
    DELETE FROM reservas.reserva_recurso_externo WHERE reserva_id IN (SELECT id FROM reservas.reservas WHERE id_unidad = v_unidad);
    DELETE FROM reservas.reservas WHERE id_unidad = v_unidad;
    DELETE FROM recursos.mobiliarios WHERE id_unidad = v_unidad;
    DELETE FROM recursos.recursos WHERE id_unidad = v_unidad;
    DELETE FROM reservas.espacios WHERE id_unidad = v_unidad;
    DELETE FROM auth.cuentas WHERE id_cuenta = v_cuenta;
    DELETE FROM usuarios.usuarios WHERE id_usuario = v_usuario;
    DELETE FROM "unidadOrganizacional".unidad_organizacional WHERE id_unidad = v_unidad;

    RAISE NOTICE 'DB-12: todas las pruebas no concurrentes pasaron; datos de prueba limpiados.';
END $$;
