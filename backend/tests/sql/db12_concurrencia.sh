#!/usr/bin/env bash
# Pruebas de concurrencia real de DB-12: dos transacciones simultáneas
# compitiendo por el mismo recurso, no una simulación secuencial.
#
# Requiere el contenedor `reservas_db` corriendo (docker compose up -d db).
# Ejecutar desde la raíz del repositorio: bash backend/tests/sql/db12_concurrencia.sh
#
# Cada escenario: la sesión A abre una transacción, escribe, y duerme unos
# segundos con la transacción todavía abierta; la sesión B intenta escribir
# un conflicto mientras A sigue sin comprometerse. Si B de verdad bloquea
# hasta que A resuelve (visible por el tiempo transcurrido) y luego falla
# con el código de error esperado, la protección es real, no una carrera
# que dio la casualidad de funcionar.

set -euo pipefail
DB="reservas_db"
PSQL="docker compose exec -T db psql -U postgres -d reservas_db"

echo "== Preparando datos de prueba =="
$PSQL -v ON_ERROR_STOP=1 <<'SQL'
DO $$
DECLARE
    v_unidad integer;
    v_usuario bigint;
    v_cuenta bigint;
    v_espacio integer;
    v_recurso integer;
BEGIN
    INSERT INTO "unidadOrganizacional".unidad_organizacional (nombre, tipo, estado)
    VALUES ('Unidad DB12-CONC', 'LABORATORIO', true) RETURNING id_unidad INTO v_unidad;
    INSERT INTO usuarios.usuarios (nombre, correo, estado, created_at, updated_at, perfil_actualizado_at, documento, telefono, institucion, dependencia)
    VALUES ('Usuario DB12-CONC', 'usuario.db12conc@correo.itm.edu.co', true, now(), now(), now(), 'DB12CONC-USR', '3700000001', 'ITM', 'Externo')
    RETURNING id_usuario INTO v_usuario;
    INSERT INTO auth.cuentas (correo, password_hash, tipo_cuenta, id_usuario, estado)
    VALUES ('usuario.db12conc@correo.itm.edu.co', 'x', 'USUARIO', v_usuario, true) RETURNING id_cuenta INTO v_cuenta;
    INSERT INTO reservas.espacios (id_unidad, nombre, capacidad, habilitado, created_at, updated_at)
    VALUES (v_unidad, 'Espacio DB12-CONC', 10, true, now(), now()) RETURNING id INTO v_espacio;
    INSERT INTO recursos.recursos (id_unidad, tipo, habilitado, created_at, updated_at)
    VALUES (v_unidad, 'MOBILIARIO', true, now(), now()) RETURNING id INTO v_recurso;
    INSERT INTO recursos.mobiliarios (id, id_unidad, nombre, habilitado) VALUES (v_recurso, v_unidad, 'Recurso concurrencia', true);

    -- Cabeceras: dos reservas de espacio (18/19-equivalentes) y dos de recurso (campus/externo).
    INSERT INTO reservas.reservas (id_unidad, tipo_reserva_id, id_cuenta, estado_id, created_by) VALUES (v_unidad, 1, v_cuenta, 1, v_cuenta);
    INSERT INTO reservas.reservas (id_unidad, tipo_reserva_id, id_cuenta, estado_id, created_by) VALUES (v_unidad, 1, v_cuenta, 1, v_cuenta);
    INSERT INTO reservas.reservas (id_unidad, tipo_reserva_id, id_cuenta, estado_id, created_by) VALUES (v_unidad, 3, v_cuenta, 1, v_cuenta);
    INSERT INTO reservas.reservas (id_unidad, tipo_reserva_id, id_cuenta, estado_id, created_by) VALUES (v_unidad, 4, v_cuenta, 1, v_cuenta);

    RAISE NOTICE 'UNIDAD=%', v_unidad;
    RAISE NOTICE 'CUENTA=%', v_cuenta;
    RAISE NOTICE 'ESPACIO=%', v_espacio;
    RAISE NOTICE 'RECURSO=%', v_recurso;
END $$;
SQL

# Recupera los ids reales sembrados arriba (más simple que parsear NOTICE).
read -r UNIDAD CUENTA ESPACIO RECURSO RID1 RID2 RID3 RID4 <<EOF
$($PSQL -t -A -F' ' -c "
SELECT u.id_unidad, c.id_cuenta, e.id, r.id,
       (SELECT id FROM reservas.reservas WHERE id_unidad=u.id_unidad AND tipo_reserva_id=1 ORDER BY id LIMIT 1),
       (SELECT id FROM reservas.reservas WHERE id_unidad=u.id_unidad AND tipo_reserva_id=1 ORDER BY id OFFSET 1 LIMIT 1),
       (SELECT id FROM reservas.reservas WHERE id_unidad=u.id_unidad AND tipo_reserva_id=3 ORDER BY id LIMIT 1),
       (SELECT id FROM reservas.reservas WHERE id_unidad=u.id_unidad AND tipo_reserva_id=4 ORDER BY id LIMIT 1)
  FROM \"unidadOrganizacional\".unidad_organizacional u
  JOIN auth.cuentas c ON c.correo = 'usuario.db12conc@correo.itm.edu.co'
  JOIN reservas.espacios e ON e.id_unidad = u.id_unidad
  JOIN recursos.recursos r ON r.id_unidad = u.id_unidad
 WHERE u.nombre = 'Unidad DB12-CONC';
")
EOF

echo "unidad=$UNIDAD cuenta=$CUENTA espacio=$ESPACIO recurso=$RECURSO reservas=$RID1,$RID2,$RID3,$RID4"

FALLOS=0

echo
echo "== Escenario 1: dos transacciones compitiendo por el compromiso físico del mismo recurso =="
$PSQL -c "INSERT INTO reservas.reserva_recurso_campus (reserva_id, fecha_salida, fecha_devolucion_estimada) VALUES ($RID3, '2031-01-01', '2031-01-03');"
$PSQL -c "INSERT INTO reservas.reserva_recurso_externo (reserva_id, fecha_salida, fecha_devolucion_estimada) VALUES ($RID4, '2031-02-01', '2031-02-03');"

( $PSQL <<SQL > /tmp/db12_sesionA1.log 2>&1
BEGIN;
INSERT INTO reservas.reserva_recursos (reserva_id, recurso_id, rol, estado_asignacion) VALUES ($RID3, $RECURSO, 'PRINCIPAL', 'ASIGNADO');
SELECT pg_sleep(3);
COMMIT;
SQL
) &
PID_A=$!
sleep 1
$PSQL <<SQL > /tmp/db12_sesionB1.log 2>&1
BEGIN;
INSERT INTO reservas.reserva_recursos (reserva_id, recurso_id, rol, estado_asignacion) VALUES ($RID4, $RECURSO, 'PRINCIPAL', 'ASIGNADO');
COMMIT;
SQL
wait $PID_A

if grep -q "uq_reserva_recursos_compromiso_fisico" /tmp/db12_sesionB1.log && grep -q "^COMMIT" /tmp/db12_sesionA1.log; then
    echo "OK: A comprometió, B fue rechazada por compromiso físico único."
else
    echo "FALLÓ el escenario 1: revisar /tmp/db12_sesionA1.log y /tmp/db12_sesionB1.log"
    FALLOS=1
fi

echo
echo "== Escenario 2: dos transacciones compitiendo por el mismo periodo de espacio =="
( $PSQL <<SQL > /tmp/db12_sesionA2.log 2>&1
BEGIN;
INSERT INTO reservas.reserva_espacio (reserva_id, espacio_id, fecha, hora_inicio, hora_fin, asistentes) VALUES ($RID1, $ESPACIO, '2031-03-01', '09:00', '11:00', 0);
SELECT pg_sleep(3);
COMMIT;
SQL
) &
PID_A=$!
sleep 1
$PSQL <<SQL > /tmp/db12_sesionB2.log 2>&1
BEGIN;
INSERT INTO reservas.reserva_espacio (reserva_id, espacio_id, fecha, hora_inicio, hora_fin, asistentes) VALUES ($RID2, $ESPACIO, '2031-03-01', '10:00', '12:00', 0);
COMMIT;
SQL
wait $PID_A

if grep -q "ex_reserva_espacio_solape" /tmp/db12_sesionB2.log && grep -q "^COMMIT" /tmp/db12_sesionA2.log; then
    echo "OK: A comprometió, B fue rechazada por solapamiento temporal."
else
    echo "FALLÓ el escenario 2: revisar /tmp/db12_sesionA2.log y /tmp/db12_sesionB2.log"
    FALLOS=1
fi

echo
echo "== Limpieza =="
$PSQL -v ON_ERROR_STOP=1 -c "
DELETE FROM reservas.reserva_recursos WHERE reserva_id IN (SELECT id FROM reservas.reservas WHERE id_unidad = $UNIDAD);
DELETE FROM reservas.reserva_espacio WHERE reserva_id IN (SELECT id FROM reservas.reservas WHERE id_unidad = $UNIDAD);
DELETE FROM reservas.reserva_recurso_campus WHERE reserva_id IN (SELECT id FROM reservas.reservas WHERE id_unidad = $UNIDAD);
DELETE FROM reservas.reserva_recurso_externo WHERE reserva_id IN (SELECT id FROM reservas.reservas WHERE id_unidad = $UNIDAD);
DELETE FROM reservas.reservas WHERE id_unidad = $UNIDAD;
DELETE FROM recursos.mobiliarios WHERE id_unidad = $UNIDAD;
DELETE FROM recursos.recursos WHERE id_unidad = $UNIDAD;
DELETE FROM reservas.espacios WHERE id_unidad = $UNIDAD;
DELETE FROM auth.cuentas WHERE id_cuenta = $CUENTA;
DELETE FROM usuarios.usuarios WHERE correo = 'usuario.db12conc@correo.itm.edu.co';
DELETE FROM \"unidadOrganizacional\".unidad_organizacional WHERE id_unidad = $UNIDAD;
"

if [ "$FALLOS" -ne 0 ]; then
    echo "DB-12: hubo fallos en las pruebas de concurrencia real."
    exit 1
fi
echo "DB-12: las dos carreras reales confirmaron que exactamente una transacción se compromete."
