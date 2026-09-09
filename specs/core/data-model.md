# Modelo de datos — Reservas

## 1. Alcance y arquitectura

LIA y Reservas viven en una sola instancia PostgreSQL. La separación es lógica: cada dominio conserva sus schemas y documentación. Reservas puede referenciar tablas maestras de LIA mediante FK PostgreSQL; LIA no contiene tablas, FK ni reglas que dependan de Reservas.

La fuente de verdad de identidad, unidades, cargos y equipos es LIA. Reservas no mantiene copias de esas entidades ni columnas duplicadas de sus identificadores.

Referencias maestras de LIA: `unidadOrganizacional.unidad_organizacional(id_unidad, nombre)`, `personal.personal(id_persona, supabase_id, ...)`, `cargos.cargo(id_cargo, id_unidad, ...)` y `equipos.equipos(id_equipo, id_unidad, estado_operativo, ...)`.

## 2. Schemas y tablas de Reservas

### `reservas.usuarios`

Reservistas de la aplicación. `id` es PK y la identidad autenticada debe ser única. No representa personal administrativo de LIA ni sustituye `personal.personal`.

### `reservas.laboratorios_config`

Configuración local de Reservas para una unidad de LIA que puede operar como laboratorio:

| Campo | Regla |
|---|---|
| `id` | PK local |
| `id_unidad` | `INTEGER NOT NULL UNIQUE`, FK a `unidadOrganizacional.unidad_organizacional.id_unidad` |
| `habilitado_reservas` | configuración local |
| `ubicacion`, `descripcion` | configuración local |
| `dias_atencion`, `hora_apertura`, `hora_cierre`, `horario_atencion` | horario local validable |
| `horas_antelacion` | configuración no negativa |
| `aprobacion_automatica`, `modalidad_reserva` | política local |
| `correo`, `notificar_por_correo` | notificaciones |

No existe `nombre` local: se obtiene mediante join a la unidad de LIA. `id_unidad` identifica el laboratorio en Reservas; no todas las unidades de LIA requieren una fila aquí.

### `reservas.espacios`

`id` PK, `id_unidad` FK obligatoria a la unidad del laboratorio, `nombre`, `ubicacion`, `capacidad`, `descripcion`, `habilitado`. Restricciones: `capacidad > 0` y `UNIQUE (id_unidad, nombre)`. Un espacio pertenece a un único laboratorio configurado.

### `reservas.mobiliarios` y `reservas.otros`

Recursos administrados localmente por Reservas. Cada fila tiene PK, `id_unidad` FK a la unidad del laboratorio, nombre, descripción y habilitación. Sus nombres pueden repetirse; la disponibilidad se controla por fila, no por nombre.

### `reservas.reservas`

Entidad principal: `id` PK; `usuario_id` FK obligatoria a `reservas.usuarios.id`; `id_unidad` FK obligatoria a `unidadOrganizacional.unidad_organizacional.id_unidad`; `espacio_id` FK opcional a `reservas.espacios.id`; fecha, `hora_inicio`, `hora_fin`, `asistentes`, `ubicacion_uso`; `tipo_uso` (`ESPACIO_RESERVADO`, `DENTRO_CAMPUS`, `FUERA_CAMPUS`); `tipo_reserva_id` FK obligatoria y `motivo_solicitud_id` FK opcional; `estado` (`PENDIENTE`, `APROBADA`, `RECHAZADA`, `CANCELADA`); timestamps y datos de auditoría necesarios.

Invariantes: `hora_inicio < hora_fin`, horas enteras, sin cruce de medianoche, intervalo `[hora_inicio, hora_fin)`, `asistentes >= 0`, al menos un espacio o recurso asociado, `ESPACIO_RESERVADO` exige espacio, `DENTRO_CAMPUS` sin espacio exige `ubicacion_uso`, `FUERA_CAMPUS` exige `espacio_id IS NULL` y `ubicacion_uso`, y si hay espacio `asistentes <= espacios.capacidad`. `id_unidad` debe coincidir con la unidad del espacio y de cada recurso asociado.

### Asociaciones

`reservas.reserva_equipos` contiene `reserva_id` FK a `reservas.reservas.id` y `id_equipo` FK directa a `equipos.equipos.id_equipo`; `UNIQUE (reserva_id, id_equipo)`. No existe copia local de equipos. `reservas.reserva_mobiliarios` y `reservas.reserva_otros` siguen el mismo patrón con sus tablas locales. `reservas.reserva_acompanantes` registra acompañantes.

Un equipo debe estar operativo según el dato actual de LIA para ser incluido en una nueva reserva o aprobado. El historial no se reescribe por cambios posteriores en LIA.

### Catálogos

`reservas.tipos_reserva` y `reservas.motivos_solicitud` tienen `id`, `nombre`, `descripcion`, `habilitado`. `tipo_reserva_id` es obligatorio; `motivo_solicitud_id` es opcional salvo política específica. Los registros usados históricamente no se eliminan físicamente.

### Notificaciones, colas y auditoría

`reservas.notificaciones`, colas de correo/calendario y `reservas.control_cambios` conservan avisos y trazabilidad. La auditoría usa `actor_tipo`, `actor_id` y `actor_nombre`; puede conservar el nombre histórico sin crear copias de personal. No existe `lista_espera`.

## 3. Estados y disponibilidad

Solo `PENDIENTE` y `APROBADA` bloquean disponibilidad. `RECHAZADA` y `CANCELADA` no bloquean. No se usa `FINALIZADA`.

La disponibilidad debe impedir solapamientos por espacio y por cada recurso. Se aplica exclusión de intervalos `[inicio, fin)` o una garantía equivalente dentro de la misma transacción.

## 4. Garantía transaccional obligatoria

Crear una reserva, editar horario, agregar o cambiar espacio o recurso y aprobar deben validar y persistir en una única transacción con aislamiento, bloqueo o restricción de exclusión que impida doble reserva bajo concurrencia. Consultar disponibilidad antes de guardar no es suficiente. Los conflictos abortan la operación y no se interpretan como disponibilidad.

La anticipación mínima, fechas no pasadas, horario de atención, capacidad, pertenencia y estado operativo se validan al crear o reprogramar; la aprobación también valida disponibilidad, horario, capacidad, estado y pertenencia, pero no vuelve a exigir una nueva anticipación mínima.

## 5. Integridad y responsabilidad

Reservas puede hacer joins y FK hacia LIA dentro de esta PostgreSQL. No hay sincronización, proyecciones, cachés persistentes, eventos de reconciliación ni tablas espejo. LIA conserva la propiedad de sus tablas y no conoce las tablas de Reservas.

La documentación funcional se distribuye en [bookings](../features/bookings.md), [spaces and resources](../features/spaces-and-resources.md) e [identity](../features/identity.md). La configuración general está en [configuration](configuration.md).
