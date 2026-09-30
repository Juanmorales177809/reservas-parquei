-- Carga de los equipos reservables desde LIA (https://lia.quantaiot.co), la base de origen.
-- Decisión 2026-09-30: specs/docs/decisions/origen-externo-estructura-institucional.md
--
-- De LIA solo se trae lo que una reserva necesita: el laboratorio, el nombre, la marca, el modelo, la placa
-- y el serial del equipo, su estado operativo (RN-EQP-03) y si requiere calibración. No se trae la
-- categoría (Patrón o Auxiliar), las frecuencias, los archivos (imagen, guía, instalador, manual) ni los datos
-- técnicos. `requiere_apoyo` y `acreditado` no existen en LIA: son de este sistema (RN-REC-10, RN-REC-11) y
-- quedan en `false` hasta que el laboratorio decida.
--
-- Qué equipos: solo los DOS activos de LIA. Los otros tres (Microscopio, TGA y Maquina Universal) están
-- inactivos, no se podrían reservar (RN-EQP-03) y traen datos que chocan con las restricciones de unicidad
-- de este sistema: tres comparten el serial «SER-MINIO-02» y dos comparten la placa «5256541». Parecen datos
-- de prueba de LIA; si se corrigen allá, se cargan después.
--
-- Requiere que los laboratorios ya estén cargados (lia_laboratorios_y_cargos.sql). Es idempotente: un
-- equipo con la misma placa no se vuelve a insertar. Se deshace todo si falta un laboratorio.
--
-- Cómo correrlo (cliente en UTF-8): PGCLIENTENCODING=UTF8 psql -v ON_ERROR_STOP=1 -U postgres -d <base> -f lia_equipos.sql
-- Primero en una copia (reservas_e2e); en la base viva solo con autorización expresa.

BEGIN;

DO $$
DECLARE
    e record;
    id_lab integer;
    id_rec integer;
BEGIN
    FOR e IN
        SELECT * FROM (VALUES
            ('Laboratorio de sistemas de Control y Robotica', 'Pie de Rey', '551235654', 'FG456JH', 'Mitutoyo', 'FT180H', false),
            ('Laboratorio de sistemas de Control y Robotica', 'Cámara Climática Constante', '5098230', 'W416.0256', 'MEMMERT', 'HPP 110', true)
        ) AS v(laboratorio, nombre, placa, serial, marca, modelo, requiere_calibracion)
    LOOP
        SELECT id_unidad INTO id_lab FROM "unidadOrganizacional".unidad_organizacional
        WHERE lower(nombre) = lower(e.laboratorio);
        IF id_lab IS NULL THEN
            RAISE EXCEPTION 'Falta el laboratorio %: cargue primero lia_laboratorios_y_cargos.sql', e.laboratorio;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM recursos.equipos WHERE placa = e.placa) THEN
            INSERT INTO recursos.recursos (id_unidad, tipo, habilitado) VALUES (id_lab, 'EQUIPO', true)
            RETURNING id INTO id_rec;
            INSERT INTO recursos.equipos (id, nombre_equipo, placa, serial, marca, modelo, estado,
                                          requiere_calibracion, requiere_apoyo, acreditado)
            VALUES (id_rec, e.nombre, e.placa, e.serial, e.marca, e.modelo, true,
                    e.requiere_calibracion, false, false);
        END IF;
    END LOOP;

    IF (SELECT count(*) FROM recursos.equipos WHERE placa IN ('551235654', '5098230')) <> 2 THEN
        RAISE EXCEPTION 'Se esperaban los 2 equipos de LIA';
    END IF;
END $$;

COMMIT;
