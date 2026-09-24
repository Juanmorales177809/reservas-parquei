-- DB-10: carga notificaciones.tipos_evento con los eventos notificables de
-- RN-EVT-01 a RN-EVT-11 (notifications/business-rules.md).
--
-- Son NUEVE códigos, no once: la propia tabla "Correspondencia entre eventos
-- y flujos productores" del módulo enumera los eventos reales, y no
-- coincide 1:1 con la numeración de reglas.
--   - RN-EVT-03 y RN-EVT-04 comparten un solo evento: el motivo de rechazo
--     es contenido de esa notificación, no otro disparador.
--   - RN-EVT-07 "no define un evento propio": es una regla de acotación
--     (limita cuándo una modificación repite un evento ya listado), según
--     su propia fila en esa tabla.
-- El resto es 1:1. `RESERVA_APROBADA` y `RESERVA_RECORDATORIO` ya aparecen
-- con ese código exacto en contratos/notifications/api-contract.md.
--
-- Idempotente: ON CONFLICT (codigo) DO NOTHING.
-- Dependencia: DB-04 (crea notificaciones.tipos_evento).
--
-- Ejecutar con: psql -v ON_ERROR_STOP=1

BEGIN;

INSERT INTO notificaciones.tipos_evento (codigo, nombre, descripcion) VALUES
    ('SOLICITUD_REGISTRADA', 'Solicitud de reserva registrada',
        'RN-EVT-01: confirma al reservista que su solicitud quedó registrada.'),
    ('RESERVA_APROBADA', 'Reserva aprobada',
        'RN-EVT-02: informa al reservista el nuevo estado.'),
    ('RESERVA_RECHAZADA', 'Reserva rechazada',
        'RN-EVT-03/04: informa el nuevo estado; incorpora el motivo cuando está registrado.'),
    ('RESERVA_CANCELADA', 'Reserva cancelada',
        'RN-EVT-05: informa a quienes deban conocer la cancelación.'),
    ('RESERVA_AFECTADA_DESHABILITACION', 'Reserva futura afectada por deshabilitación',
        'RN-EVT-06: aviso cuando una reserva futura se ve afectada por deshabilitar un espacio o recurso.'),
    ('PROPUESTA_PERIODO_REGISTRADA', 'Propuesta o contrapropuesta de periodo registrada',
        'RN-EVT-08: notifica a la contraparte del intercambio de horario.'),
    ('RECURSO_ADICIONAL_INCORPORADO', 'Recurso adicional incorporado',
        'RN-EVT-09: informa al reservista el recurso agregado a una reserva ya aprobada.'),
    ('LISTA_ESPERA_CAMBIO_ESTADO', 'Cambio de estado de lista de espera',
        'RN-EVT-10: cambios de estado de una reserva de tipo lista de espera.'),
    ('RESERVA_RECORDATORIO', 'Recordatorio de reserva',
        'RN-EVT-11: aviso previo al inicio, sin ser una operación sobre la reserva.')
ON CONFLICT (codigo) DO NOTHING;

INSERT INTO public.schema_migrations (nombre) VALUES ('seeds/tipos_evento')
ON CONFLICT (nombre) DO NOTHING;

COMMIT;
