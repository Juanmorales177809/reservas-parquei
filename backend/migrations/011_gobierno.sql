-- Gobierno del esquema: ledger de migraciones aplicadas (DB-13).
--
-- POR QUE EXISTE ESTE ARCHIVO
-- architecture.md §15 y §16.10 exigen migraciones reproducibles y
-- versionadas, sin cambios manuales como mecanismo normal. Hasta ahora
-- nada registraba qué scripts se aplicaron salvo database-status.md,
-- escrito a mano. Este ledger hace el estado aplicado consultable con
-- un SELECT, sin inspeccionar la base a mano.
--
-- CONVENCION
-- Cada migración futura termina su transacción insertando su propia fila
-- en public.schema_migrations, con el nombre del archivo como identificador
-- estable (el mismo criterio de tasks.md: el número es identificador, no
-- orden). El orden de aplicación lo siguen fijando tasks.md y las
-- dependencias de cada tarea.
--
-- SELLO DE LA LINEA BASE
-- Este archivo también sella lo ya aplicado en este entorno: la cadena
-- reconstruccion/000_base_compartida, 001_shared_postgres,
-- 001b_transicion_cuenta, 002_reservas_objetivo y
-- reconstruccion/003_limpieza_heredada. Idempotente a propósito: si el
-- ledger ya existe con esas filas, no hace nada en lugar de fallar.
--
-- Ejecutar con: psql -v ON_ERROR_STOP=1

BEGIN;
SET LOCAL lock_timeout = '5s';
SET LOCAL statement_timeout = '60s';

CREATE TABLE IF NOT EXISTS public.schema_migrations (
    nombre      text PRIMARY KEY,
    aplicada_at timestamptz NOT NULL DEFAULT now()
);

INSERT INTO public.schema_migrations (nombre) VALUES
    ('000_base_compartida'),
    ('001_shared_postgres'),
    ('001b_transicion_cuenta'),
    ('002_reservas_objetivo'),
    ('003_limpieza_heredada')
ON CONFLICT (nombre) DO NOTHING;

COMMIT;
