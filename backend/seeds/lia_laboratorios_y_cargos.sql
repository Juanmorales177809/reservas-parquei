-- Carga inicial de laboratorios y cargos desde LIA (https://lia.quantaiot.co), la base de origen.
-- Decisión 2026-09-30: specs/docs/decisions/origen-externo-estructura-institucional.md
--
-- Qué hace: inserta los cinco laboratorios de LIA y los tres cargos que pertenecen a un laboratorio, tal
-- como LIA los lista (los nombres se conservan idénticos, incluidas las tildes que LIA no lleva, para que
-- una sincronización futura coincida). No borra ni modifica nada: cada fila se inserta solo si todavía no
-- existe.
--
-- Qué NO carga, a propósito: las unidades «Parque i», «Gestión Laboratorios» y «Dirección de Gestión de la
-- Investigación» ni los cargos administrativos que cuelgan de «Gestión Laboratorios»: aquí solo importan
-- los laboratorios. Tampoco carga personal (LIA no guarda documento, correo ni teléfono, que aquí son
-- obligatorios), ni cuentas ni contraseñas, ni la configuración de reservas de cada laboratorio (se hace
-- desde «Laboratorios y cargos» → Configurar).
--
-- Cómo correrlo (cliente en UTF-8; una carga con otra codificación guardó «??» en los acentos):
--   PGCLIENTENCODING=UTF8 psql -v ON_ERROR_STOP=1 -U postgres -d <base> -f lia_laboratorios_y_cargos.sql
-- Primero en una copia (reservas_e2e); en la base viva solo con autorización expresa.

BEGIN;

INSERT INTO "unidadOrganizacional".unidad_organizacional (nombre, tipo)
SELECT v.nombre, 'LABORATORIO'
FROM (VALUES
    ('Laboratorio de Ciencias Termicas'),
    ('Laboratorio de Materiales Polimericos'),
    ('Laboratorio de Microscopia'),
    ('Laboratorio de Optica y Fotonica'),
    ('Laboratorio de sistemas de Control y Robotica')
) AS v(nombre)
WHERE NOT EXISTS (
    SELECT 1 FROM "unidadOrganizacional".unidad_organizacional u WHERE lower(u.nombre) = lower(v.nombre)
);

-- Cargos: cada uno pertenece al laboratorio de su «unidad asociada»
INSERT INTO cargos.cargo (nombre_cargo, id_unidad)
SELECT v.cargo, u.id_unidad
FROM (VALUES
    ('Responsable Técnico', 'Laboratorio de Optica y Fotonica'),
    ('Técnico Especializado', 'Laboratorio de sistemas de Control y Robotica'),
    ('Técnico Especializado', 'Laboratorio de Materiales Polimericos')
) AS v(cargo, unidad)
JOIN "unidadOrganizacional".unidad_organizacional u ON lower(u.nombre) = lower(v.unidad)
WHERE NOT EXISTS (
    SELECT 1 FROM cargos.cargo c WHERE c.nombre_cargo = v.cargo AND c.id_unidad = u.id_unidad
);

-- Verificación: deben existir los 5 laboratorios y los 3 cargos; si no, se deshace todo.
DO $$
DECLARE
    n_labs integer;
    n_cargos integer;
BEGIN
    SELECT count(*) INTO n_labs FROM "unidadOrganizacional".unidad_organizacional
    WHERE lower(nombre) IN ('laboratorio de ciencias termicas', 'laboratorio de materiales polimericos',
        'laboratorio de microscopia', 'laboratorio de optica y fotonica',
        'laboratorio de sistemas de control y robotica');
    SELECT count(*) INTO n_cargos FROM cargos.cargo c
    JOIN "unidadOrganizacional".unidad_organizacional u ON u.id_unidad = c.id_unidad
    WHERE c.nombre_cargo IN ('Responsable Técnico', 'Técnico Especializado')
      AND lower(u.nombre) IN ('laboratorio de optica y fotonica',
        'laboratorio de sistemas de control y robotica', 'laboratorio de materiales polimericos');
    IF n_labs <> 5 THEN RAISE EXCEPTION 'Se esperaban 5 laboratorios de LIA y hay %', n_labs; END IF;
    IF n_cargos <> 3 THEN RAISE EXCEPTION 'Se esperaban 3 cargos de LIA y hay %', n_cargos; END IF;
END $$;

COMMIT;
