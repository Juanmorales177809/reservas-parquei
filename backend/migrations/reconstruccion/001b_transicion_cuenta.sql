-- Transición de identidad de la cabecera: usuario_id -> id_cuenta.
--
-- POR QUE EXISTE ESTE ARCHIVO
-- 001 crea reservas.reservas.usuario_id INT -> reservas.usuarios(id), del
-- backend anterior. La base viva ya había evolucionado antes del snapshot
-- 20260923_reservas_antes.sql: su tabla reservas.reservas trae
-- id_cuenta bigint NOT NULL -> auth.cuentas(id_cuenta) con el nombre
-- fk_reservas_cuenta (líneas 345-360 y 607-608), sin columna usuario_id
-- y sin tabla reservas.usuarios (el snapshot trae 13 tablas, sin usuarios).
-- 002 asume ese estado: indexa id_cuenta (:59) y el test
-- reservas_objetivo.sql:24-25 exige la cabecera con id_cuenta.
-- Sin este eslabón, 002 falla con 'column "id_cuenta" does not exist'.
--
-- QUE HACE
-- Reproduce esa evolución perdida sobre tablas vacías: retira la FK de
-- notificaciones.usuario_id hacia reservas.usuarios (el snapshot la trae
-- sin esa FK: solo PK, FK de reserva_id e índice), cambia la cabecera a
-- id_cuenta con el mismo nombre de constraint del snapshot, y retira
-- reservas.usuarios. No toca 002 (congelado): lo deja ejecutable.
--
-- Ejecutar con: psql -v ON_ERROR_STOP=1

BEGIN;
SET LOCAL lock_timeout = '5s';
SET LOCAL statement_timeout = '60s';

-- Como 002: abortar si apareció información desde la inspección.
DO $$
DECLARE t record; occupied boolean;
BEGIN
  FOR t IN SELECT tablename FROM pg_tables WHERE schemaname = 'reservas' ORDER BY tablename LOOP
    EXECUTE format('LOCK TABLE reservas.%I IN ACCESS EXCLUSIVE MODE', t.tablename);
    EXECUTE format('SELECT EXISTS (SELECT 1 FROM reservas.%I)', t.tablename) INTO occupied;
    IF occupied THEN RAISE EXCEPTION 'La tabla reservas.% contiene datos; transición cancelada', t.tablename; END IF;
  END LOOP;
END $$;

-- La FK de notificaciones.usuario_id tiene nombre generado (la crea 001
-- inline con ON DELETE CASCADE); se retira por catálogo, conservando la
-- columna, igual que el snapshot.
DO $$
DECLARE r record;
BEGIN
  FOR r IN SELECT conname FROM pg_constraint
    WHERE conrelid = 'reservas.notificaciones'::regclass
      AND confrelid = 'reservas.usuarios'::regclass LOOP
    EXECUTE format('ALTER TABLE reservas.notificaciones DROP CONSTRAINT %I', r.conname);
  END LOOP;
END $$;

-- Cabecera: fuera usuario_id, dentro id_cuenta con el nombre del snapshot.
-- DROP COLUMN retira su FK implícita; sin CASCADE.
ALTER TABLE reservas.reservas DROP COLUMN usuario_id;
ALTER TABLE reservas.reservas
  ADD COLUMN id_cuenta bigint NOT NULL
  CONSTRAINT fk_reservas_cuenta REFERENCES auth.cuentas(id_cuenta);

-- Tabla de auth antigua del backend anterior; vacía y sin referencias
-- restantes a este punto. Sin CASCADE: una dependencia no prevista aborta.
DROP TABLE reservas.usuarios;

COMMIT;
