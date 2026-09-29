-- Repara los textos de tres tipos de evento cuyos acentos se guardaron como '??'.
--
-- POR QUE EXISTE ESTE ARCHIVO
-- seeds/tipos_evento_auth.sql está bien escrito en UTF-8, pero se cargó con una
-- codificación de cliente que no era UTF8 (típico en una consola de Windows) y
-- PostgreSQL guardó dos signos '?' literales en lugar de cada carácter con
-- acento. Como la semilla usa ON CONFLICT DO NOTHING, volver a cargarla no
-- corrige nada: hace falta un UPDATE.
--
-- Los textos van con escapes \u (E'...') a propósito: así este archivo no
-- depende de la codificación del cliente que lo ejecute, que fue la causa.
-- Solo toca filas que aún contienen '??'; corrida dos veces, no cambia nada.
-- No borra ni recrea filas: las notificaciones ya emitidas conservan su tipo.

BEGIN;

SET LOCAL client_encoding = 'UTF8';

UPDATE notificaciones.tipos_evento
   SET nombre = E'Invitaci\u00f3n a crear cuenta'
 WHERE codigo = 'INVITACION_CUENTA' AND nombre LIKE '%??%';

UPDATE notificaciones.tipos_evento
   SET nombre = E'Recuperaci\u00f3n de contrase\u00f1a',
       descripcion = E'Enlace de un solo uso para restablecer la contrase\u00f1a'
 WHERE codigo = 'RECUPERACION_CONTRASENA' AND (nombre LIKE '%??%' OR descripcion LIKE '%??%');

UPDATE notificaciones.tipos_evento
   SET nombre = E'Contrase\u00f1a actualizada',
       descripcion = E'Aviso de que la contrase\u00f1a de la cuenta cambi\u00f3'
 WHERE codigo = 'CONTRASENA_CAMBIADA' AND (nombre LIKE '%??%' OR descripcion LIKE '%??%');

-- Verificación: ninguna fila del catálogo debe conservar '??'.
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM notificaciones.tipos_evento
         WHERE nombre LIKE '%??%' OR descripcion LIKE '%??%'
    ) THEN
        RAISE EXCEPTION 'Quedan textos con ?? en notificaciones.tipos_evento';
    END IF;
END
$$;

INSERT INTO public.schema_migrations (nombre) VALUES ('013_corregir_textos_tipos_evento');

COMMIT;
