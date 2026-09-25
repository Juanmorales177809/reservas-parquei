-- DB-10 (ampliación API-18): tipos de evento para las comunicaciones de
-- autenticación (RN-DES-06, RN-PREF-03, SEC-REC-04). El catálogo está
-- diseñado para crecer sin migrar CHECKs. Idempotente por código.
--
-- Ejecutar con: psql -v ON_ERROR_STOP=1

BEGIN;
SET LOCAL lock_timeout = '5s';
SET LOCAL statement_timeout = '60s';

INSERT INTO notificaciones.tipos_evento (codigo, nombre, descripcion, habilitado) VALUES
    ('INVITACION_CUENTA', 'Invitación a crear cuenta',
     'Enlace de un solo uso para activar una cuenta invitada', true),
    ('RECUPERACION_CONTRASENA', 'Recuperación de contraseña',
     'Enlace de un solo uso para restablecer la contraseña', true),
    ('CONTRASENA_CAMBIADA', 'Contraseña actualizada',
     'Aviso de que la contraseña de la cuenta cambió', true)
ON CONFLICT DO NOTHING;

INSERT INTO public.schema_migrations (nombre) VALUES ('seed_tipos_evento_auth')
ON CONFLICT (nombre) DO NOTHING;

COMMIT;
