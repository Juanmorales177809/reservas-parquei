-- DB-08: carga los catalogos de reservas.tipos_reserva y reservas.estados_reserva.
-- Sin esto ninguna reserva puede resolver tipo_reserva_id ni estado_id.
--
-- Los cinco tipos y los seis estados globales son los que RN-TIP y RN-EST de
-- reservations/business-rules.md declaran cerrados; no es un catalogo abierto
-- a crecer desde el backend.
--
-- Idempotente: ON CONFLICT (codigo) DO NOTHING permite reaplicarlo sin duplicar.
--
-- Ejecutar con: psql -v ON_ERROR_STOP=1

BEGIN;

INSERT INTO reservas.tipos_reserva (codigo, nombre, descripcion, habilitado) VALUES
    ('ESPACIO', 'Espacio',
        'Reserva de un espacio del laboratorio para su uso dentro del horario de atención.', true),
    ('RECURSO_INTERNO', 'Recurso interno',
        'Préstamo de un recurso que permanece dentro del laboratorio, sin entrega física.', true),
    ('RECURSO_CAMPUS', 'Recurso en campus',
        'Préstamo de un recurso que sale del laboratorio y permanece dentro del campus.', true),
    ('RECURSO_EXTERNO', 'Recurso fuera del campus',
        'Préstamo de un recurso autorizado para uso fuera del campus.', true),
    ('LISTA_ESPERA', 'Lista de espera',
        'Solicitud de fabricación o prestación técnica, sujeta a evaluación de viabilidad.', true)
ON CONFLICT (codigo) DO NOTHING;

INSERT INTO reservas.estados_reserva (codigo, nombre, habilitado) VALUES
    ('SOLICITADA', 'Solicitada', true),
    ('APROBADA', 'Aprobada', true),
    ('RECHAZADA', 'Rechazada', true),
    ('EN_EJECUCION', 'En ejecución', true),
    ('FINALIZADA', 'Finalizada', true),
    ('CANCELADA', 'Cancelada', true)
ON CONFLICT (codigo) DO NOTHING;

-- Gobierno del esquema (DB-13): esta migracion se registra en el ledger.
INSERT INTO public.schema_migrations (nombre) VALUES ('seeds/catalogos_reservas')
ON CONFLICT (nombre) DO NOTHING;

COMMIT;
