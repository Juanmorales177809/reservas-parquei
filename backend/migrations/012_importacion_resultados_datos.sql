-- Agrega administration.importacion_resultados.datos (API-12).
--
-- POR QUE EXISTE ESTE ARCHIVO
-- El contrato de importaciones confirma en dos pasos: `POST
-- /api/importaciones` valida sin escribir, y `POST
-- /api/importaciones/{id}/confirmacion` confirma sin cuerpo. Hasta esta
-- migración, `importacion_resultados` solo guardaba el resultado de cada
-- fila (CREADO/ACTUALIZADO/DESACTIVADO/ERROR) y su detalle de error, nunca
-- los valores de la fila. Sin ellos, el paso de confirmación no tiene de
-- dónde tomar qué escribir en investigacion o recursos, porque el archivo
-- original no se conserva en ningún lado y la confirmación no lo reenvía.
--
-- `datos` guarda los valores normalizados de cada fila que vaya a crear o
-- actualizar un registro (CREADO/ACTUALIZADO); queda NULL en filas ERROR,
-- que no escriben nada. La confirmación lee esta columna en vez de volver
-- a parsear el archivo. Para `EQUIPOS`, `datos` también incluye `id_unidad`
-- (RN-IMP-12 de administration): no hay otra columna donde conservar la
-- unidad seleccionada al iniciar la carga hasta el momento de confirmar.
--
-- `importaciones.confirmado_at` resuelve un segundo vacío del mismo diseño:
-- sin una marca explícita, "ya fue confirmada" (409 CONFLICTO del contrato
-- §4.2) no se puede distinguir de una carga válida que aún no se confirmó,
-- porque los tres contadores nacen en 0 y una confirmación real que no crea
-- ni actualiza nada (archivo sin filas de datos) los deja también en 0.
--
-- Ejecutar con: psql -v ON_ERROR_STOP=1

BEGIN;
SET LOCAL lock_timeout = '5s';
SET LOCAL statement_timeout = '60s';

ALTER TABLE administration.importacion_resultados
    ADD COLUMN datos jsonb;

ALTER TABLE administration.importaciones
    ADD COLUMN confirmado_at timestamptz;

INSERT INTO public.schema_migrations (nombre) VALUES ('012_importacion_resultados_datos');

COMMIT;
