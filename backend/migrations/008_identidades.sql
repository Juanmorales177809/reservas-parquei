-- Tres ajustes de identidad que comparten archivo a propósito (DB-06, DB-07,
-- DB-15): las tres tocan columnas de identidad y van al mismo carril para
-- que dos personas no editen el mismo archivo en paralelo.
--
-- Sin CASCADE: una dependencia no prevista debe abortar, no borrarse.
-- Última sentencia: la fila del ledger (convención de 011_gobierno.sql).
--
-- Ejecutar con: psql -v ON_ERROR_STOP=1

BEGIN;
SET LOCAL lock_timeout = '5s';
SET LOCAL statement_timeout = '60s';

-- ----------------------------------------------------------------------
-- DB-06: personal.personal.estado como NOT NULL DEFAULT true.
-- Fija en true las filas existentes con NULL ANTES de restringir, sin
-- deducir el valor de otros campos: desactivar personal activo por una
-- inferencia es peor que el NULL (nota de migración de base-de-datos.md).
-- ----------------------------------------------------------------------

UPDATE personal.personal SET estado = true WHERE estado IS NULL;
ALTER TABLE personal.personal
    ALTER COLUMN estado SET DEFAULT true,
    ALTER COLUMN estado SET NOT NULL;

-- ----------------------------------------------------------------------
-- DB-07: unidad_organizacional.estado, para la baja lógica de RN-UNI-04/05.
-- Columna nueva: no exige backfill.
-- ----------------------------------------------------------------------

ALTER TABLE "unidadOrganizacional".unidad_organizacional
    ADD COLUMN estado boolean NOT NULL DEFAULT true;

-- ----------------------------------------------------------------------
-- DB-15: columnas objetivo de usuarios.usuarios (RN-DAT), y el CHECK de
-- nombre. El modelo exige completar los faltantes y resolver duplicados
-- ANTES de restringir, sin inventar valores. Si hay filas existentes, esta
-- migración aborta en vez de improvisar: nada las completa aquí.
-- ----------------------------------------------------------------------

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM usuarios.usuarios) THEN
        RAISE EXCEPTION
            'usuarios.usuarios tiene filas existentes: completar documento, '
            'telefono, institucion y dependencia, y resolver duplicados, '
            'antes de aplicar DB-15. No se inventan valores en la migración.';
    END IF;
END $$;

ALTER TABLE usuarios.usuarios
    ADD COLUMN documento   varchar(20)  NOT NULL,
    ADD COLUMN telefono    varchar(20)  NOT NULL,
    ADD COLUMN institucion varchar(255) NOT NULL,
    ADD COLUMN dependencia varchar(255) NOT NULL,
    ADD CONSTRAINT uq_usuarios_documento UNIQUE (documento),
    ADD CONSTRAINT uq_usuarios_telefono UNIQUE (telefono),
    ADD CONSTRAINT ck_usuarios_nombre CHECK (btrim(nombre) <> ''),
    ADD CONSTRAINT ck_usuarios_documento CHECK (btrim(documento) <> ''),
    ADD CONSTRAINT ck_usuarios_telefono CHECK (btrim(telefono) <> ''),
    ADD CONSTRAINT ck_usuarios_institucion CHECK (btrim(institucion) <> ''),
    ADD CONSTRAINT ck_usuarios_dependencia CHECK (btrim(dependencia) <> '');

INSERT INTO public.schema_migrations (nombre) VALUES ('008_identidades');

COMMIT;
