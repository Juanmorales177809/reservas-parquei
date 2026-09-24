-- DB-09: carga los catorce codigos de auth.permisos, del catalogo inicial de
-- auth/data-model.md. Sin esto no hay autorizacion real posible: exigir_permiso
-- (BK-07) no tiene contra que resolver un codigo.
--
-- El catalogo crece cuando aparezca una operacion que hoy no existe, no cuando
-- se anada un endpoint a un area ya cubierta (auth/data-model.md#catalogo-inicial).
--
-- Idempotente: ON CONFLICT (codigo) DO NOTHING permite reaplicarlo sin duplicar.
-- Dependencia: DB-14 (crea auth.permisos).
--
-- Ejecutar con: psql -v ON_ERROR_STOP=1

BEGIN;

INSERT INTO auth.permisos (codigo, nombre, descripcion, habilitado) VALUES
    ('reservas.administrar', 'Administrar reservas',
        'Aprobar, rechazar, agregar o retirar recursos, iniciar ejecución, finalizar y cancelar reservas ajenas de la unidad.', true),
    ('reservas.exportar', 'Exportar reservas',
        'Exportar listados e historial de reservas.', true),
    ('espacios.administrar', 'Administrar espacios',
        'Crear, editar y habilitar espacios, sus recursos asociados y sus campos adicionales.', true),
    ('recursos.administrar', 'Administrar mobiliarios y otros recursos',
        'Crear, editar y habilitar mobiliarios y otros recursos.', true),
    ('recursos.editar_equipos', 'Editar equipos',
        'Editar datos y estados de equipos existentes de la unidad; no permite crearlos, eliminarlos ni cambiar su unidad responsable.', true),
    ('recursos.administrar_equipos', 'Administrar equipos globalmente',
        'Registrar y administrar globalmente equipos del inventario institucional; crear equipos e intervenir sobre cualquier unidad.', true),
    ('recursos.reasignar_unidad', 'Reasignar unidad de un recurso',
        'Cambiar la unidad responsable de un recurso.', true),
    ('laboratorios.configurar', 'Configurar laboratorio',
        'Horario de atención, antelación, aprobación automática, tipos de reserva y visibilidad de la unidad.', true),
    ('cuentas.administrar', 'Administrar cuentas',
        'Invitar, activar, desactivar y cambiar el tipo de identidad de una cuenta.', true),
    ('usuarios.administrar', 'Administrar usuarios',
        'Crear, editar y habilitar identidades funcionales de Usuario.', true),
    ('permisos.asignar', 'Asignar permisos',
        'Otorgar y retirar permisos a otras cuentas.', true),
    ('unidades.administrar', 'Administrar unidades y cargos',
        'Gestionar unidades organizacionales y cargos.', true),
    ('importacion.ejecutar', 'Ejecutar importaciones',
        'Importar catálogos masivamente.', true),
    ('reportes.consultar', 'Consultar reportes',
        'Consultar informes de ocupación y uso.', true)
ON CONFLICT (codigo) DO NOTHING;

-- Gobierno del esquema (DB-13): esta migracion se registra en el ledger.
INSERT INTO public.schema_migrations (nombre) VALUES ('seeds/permisos')
ON CONFLICT (nombre) DO NOTHING;

COMMIT;
