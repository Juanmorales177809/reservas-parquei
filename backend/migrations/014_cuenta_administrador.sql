-- Cuentas de tipo ADMINISTRADOR: el administrador de Reservas es una cuenta propia, sin ficha en LIA.
--
-- POR QUE EXISTE ESTE ARCHIVO
-- Decisión 2026-09-30 (specs/docs/decisions/origen-externo-estructura-institucional.md): el personal, los
-- cargos y los laboratorios vienen de LIA, y el administrador de Reservas no tiene nada allá. Hasta ahora toda
-- cuenta debía apuntar a un Usuario o a una ficha de Personal (ck_auth_cuentas_identidad), así que el
-- administrador se fingía como Personal con un permiso global. Ahora es una cuenta de tipo ADMINISTRADOR, sin
-- identidad asociada, y el rol (no una asignación manual) define qué puede hacer.
--
-- Qué hace: amplía las dos restricciones CHECK de auth.cuentas para admitir el tipo ADMINISTRADOR con
-- id_usuario e id_persona en NULL. Las cuentas existentes siguen cumpliéndolas: no se reescribe ninguna fila.
-- No borra datos, no toca auth.cuenta_permisos (queda sin uso y se retirará en otra migración).

BEGIN;

ALTER TABLE auth.cuentas DROP CONSTRAINT ck_auth_cuentas_tipo;
ALTER TABLE auth.cuentas DROP CONSTRAINT ck_auth_cuentas_identidad;

ALTER TABLE auth.cuentas
    ADD CONSTRAINT ck_auth_cuentas_tipo
    CHECK (tipo_cuenta IN ('USUARIO', 'PERSONAL', 'ADMINISTRADOR'));

ALTER TABLE auth.cuentas
    ADD CONSTRAINT ck_auth_cuentas_identidad
    CHECK (
        (tipo_cuenta = 'USUARIO'       AND id_usuario IS NOT NULL AND id_persona IS NULL)
     OR (tipo_cuenta = 'PERSONAL'      AND id_persona IS NOT NULL AND id_usuario IS NULL)
     OR (tipo_cuenta = 'ADMINISTRADOR' AND id_usuario IS NULL     AND id_persona IS NULL)
    );

-- Verificación: las dos restricciones existen y validan las filas actuales (ADD CONSTRAINT ya las valida).
DO $$
BEGIN
    IF (SELECT count(*) FROM pg_constraint
         WHERE conrelid = 'auth.cuentas'::regclass
           AND conname IN ('ck_auth_cuentas_tipo', 'ck_auth_cuentas_identidad')) <> 2 THEN
        RAISE EXCEPTION 'Faltan las restricciones de auth.cuentas';
    END IF;
END
$$;

INSERT INTO public.schema_migrations (nombre) VALUES ('014_cuenta_administrador');

COMMIT;
