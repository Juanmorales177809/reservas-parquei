-- Retira lo que 001 dejo y el modelo objetivo ya no contempla.
--
-- 001 pertenecia al arranque del backend anterior y, ademas de crear el
-- esquema de reservas que 002 transforma, tocaba cosas que hoy no aplican:
--
--   - anadia personal.personal.supabase_id, que el modelo declara retirada
--     ("la tabla ya no contiene supabase_id", usuarios/data-model.md);
--   - estrechaba personal.personal.correo a varchar(150), cuando el modelo
--     lo define como varchar(255);
--   - creaba el schema reservas_legacy para mover tablas de public, que en
--     una base vacia no existen.
--
-- Se ejecuta despues de 002 porque antes 001 volveria a ponerlo.
--
-- Ejecutar con: psql -v ON_ERROR_STOP=1

BEGIN;

DROP INDEX IF EXISTS personal.uq_personal_supabase_id;
ALTER TABLE personal.personal DROP COLUMN IF EXISTS supabase_id;

-- Sin USING: solo se amplia el ancho, no se convierte ningun valor.
ALTER TABLE personal.personal ALTER COLUMN correo TYPE varchar(255);

-- Sin CASCADE: si alguna tabla quedo dentro, la operacion debe abortar y
-- obligar a mirarla, no borrarla en silencio.
DROP SCHEMA IF EXISTS reservas_legacy;

-- equipos queda huerfano al retirar 002 la tabla reservas.reserva_equipos.
-- El modelo objetivo no lo contempla: recursos.equipos lo sustituye (DB-01).
-- Tambien sin CASCADE, por lo mismo.
DROP TABLE IF EXISTS equipos.equipos;
DROP SCHEMA IF EXISTS equipos;

COMMIT;
