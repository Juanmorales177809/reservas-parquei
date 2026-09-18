# Modelo de datos — Reservas

## Fuente y estado del modelo

Este documento conserva el diseño objetivo cabecera–detalle y, al final, el inventario de reservas procedente del [modelo principal](../../docs/data-model.md). Son versiones distintas: las tablas objetivo no se consideran aplicadas por estar documentadas aquí. La transición requiere migraciones explícitas.

Modelo cabecera–detalle del dominio. `reservas.reservas` contiene atributos comunes y cada tipo tiene un detalle específico. Los tipos de PK/FK mantienen el modelo existente: `integer` para unidades, espacios, tipos, estados y recursos; `bigint` para cuentas.

## Catálogos

### `reservas.tipos_reserva`

| Campo | Tipo | Restricción |
|---|---|---|
| `id` | integer | PK |
| `codigo` | varchar(40) | UNIQUE, NOT NULL |
| `nombre` | varchar(100) | NOT NULL |
| `descripcion` | text | NULL |
| `habilitado` | boolean | NOT NULL |
| `created_at`, `updated_at` | timestamptz | NOT NULL |

`codigo` contempla `ESPACIO`, `RECURSO_INTERNO`, `RECURSO_CAMPUS`, `RECURSO_EXTERNO`, `LISTA_ESPERA` y `SERVICIO`.

### `reservas.estados_reserva`

`id integer PK`, `codigo varchar(30) UNIQUE NOT NULL`, `nombre varchar(100) NOT NULL`, `habilitado boolean NOT NULL`. Los códigos globales son `SOLICITADA`, `APROBADA`, `RECHAZADA`, `EN_EJECUCION`, `FINALIZADA` y `CANCELADA`; no se deben deshabilitar estados usados históricamente.

### `reservas.laboratorio_tipos_reserva`

| Campo | Tipo | Restricción |
|---|---|---|
| `id_unidad` | integer | PK, FK a `unidadOrganizacional.unidad_organizacional(id_unidad)` |
| `tipo_reserva_id` | integer | PK, FK a `tipos_reserva(id)` |
| `habilitado` | boolean | NOT NULL |
| `created_at`, `updated_at` | timestamptz | NOT NULL |

La PK compuesta impide duplicados. Los tipos seleccionables se obtienen filtrando `habilitado = true` y el catálogo global también habilitado; una sola opción permite selección automática. Índice `(tipo_reserva_id, habilitado)`.

## Cabecera

### `reservas.reservas`

| Campo | Tipo | Restricción |
|---|---|---|
| `id` | integer | PK |
| `id_cuenta` | bigint | NOT NULL, FK a `auth.cuentas(id_cuenta)` |
| `id_unidad` | integer | NOT NULL, FK a `unidadOrganizacional.unidad_organizacional(id_unidad)` |
| `tipo_reserva_id` | integer | NOT NULL, FK |
| `estado_id` | integer | NOT NULL, FK |
| `observacion` | text | NULL |
| `requiere_apoyo` | boolean | NOT NULL, DEFAULT `false`; requerimiento efectivo de apoyo técnico |
| `created_at`, `updated_at` | timestamptz | NOT NULL |
| `created_by` | bigint | NOT NULL, FK a `auth.cuentas(id_cuenta)` |
| `fecha_aprobacion` | timestamptz | NULL |
| `fecha_cancelacion` | timestamptz | NULL |
| `motivo_cancelacion` | text | NULL |

Índices: `(id_cuenta, created_at)`, `(id_unidad, estado_id)`, `(tipo_reserva_id, estado_id)`.

Cada reserva debe tener exactamente un detalle compatible con su tipo. La cabecera, el detalle y sus asociaciones se escriben en una única transacción; el backend valida la correspondencia. Cada detalle usa `reserva_id` como PK y FK, por lo que solo admite una fila de ese subtipo. Si se permiten escrituras directas fuera del servicio, se requiere una restricción diferida equivalente; no se propone un trigger complejo como requisito general.

## Detalles por tipo

### `reservas.reserva_espacio`

`reserva_id integer PK/FK`, `espacio_id integer NOT NULL FK a `espacios(id)`, `fecha date NOT NULL`, `hora_inicio time NOT NULL`, `hora_fin time NOT NULL`, `asistentes integer NOT NULL CHECK (asistentes >= 0)`.

CHECK `hora_inicio < hora_fin`. Capacidad, habilitación, horario y solapamientos son reglas de negocio.

### `reservas.reserva_recurso_interno`

`reserva_id integer PK/FK`, `fecha_inicio date NOT NULL`, `fecha_fin date NOT NULL`, CHECK `fecha_fin >= fecha_inicio`. Debe tener al menos un recurso asociado y puede tener adicionales.

### `reservas.reserva_recurso_campus` y `reservas.reserva_recurso_externo`

Cada tabla contiene `reserva_id integer PK/FK`, `fecha_salida date NOT NULL`, `fecha_devolucion date NOT NULL`, CHECK `fecha_devolucion >= fecha_salida`. Cada reserva tiene exactamente un recurso `PRINCIPAL` activo, admite `ADICIONAL`es (`RN-TIP-RC-01`, `RN-TIP-RE-01`) y tiene una orden del tipo correspondiente que lista todos sus recursos. `fecha_salida`/`fecha_devolucion` aplican a todos los recursos de la reserva.

### `reservas.reserva_lista_espera`

`reserva_id integer PK/FK`, `descripcion_necesidad text NOT NULL`, `viable boolean NULL`, `fecha_evaluacion_viabilidad timestamptz NULL`, `fecha_recepcion_material timestamptz NULL`, `prioridad integer NULL`, `horas_ejecucion numeric NULL CHECK (horas_ejecucion >= 0)`. No requiere fecha ni horario de ejecución.

### `reservas.reserva_servicio`

`reserva_id integer PK/FK`. Sus atributos quedan pendientes hasta definir el flujo funcional.

## Recursos

El catálogo raíz `reservas.recursos` y la relación 1:1 con equipos, mobiliarios y otros se definen en [Resources](../resources/data-model.md#reservasrecursos). Este módulo define las asignaciones de dichos recursos a reservas. La configuración de laboratorios pertenece a Resources y los espacios a [Espacios](../espacios/data-model.md).

### `reservas.reserva_recursos`

| Campo | Tipo | Restricción |
|---|---|---|
| `id` | integer | PK |
| `reserva_id` | integer | NOT NULL, FK |
| `recurso_id` | integer | NOT NULL, FK a `recursos.recursos(id)` |
| `rol` | varchar(20) | NOT NULL, CHECK `PRINCIPAL` o `ADICIONAL` |
| `estado_asignacion` | varchar(20) | NOT NULL, CHECK `SOLICITADO`, `ASIGNADO`, `NO_DISPONIBLE`, `RETIRADO` |
| `solicitado_at` | timestamptz | NOT NULL |
| `asignado_at`, `retirado_at` | timestamptz | NULL |
| `fecha_inicio_uso`, `fecha_fin_uso` | timestamptz | NULL |
| `incorporado_por` | bigint | NOT NULL, FK a `auth.cuentas` |
| `created_at` | timestamptz | NOT NULL |

Índices `(recurso_id, fecha_inicio_uso, fecha_fin_uso)` y `(reserva_id, recurso_id, created_at)`. No se borran asociaciones: los cambios conservan historial. Índice único parcial sobre `(reserva_id, recurso_id)` para asociaciones activas. La aplicación exige exactamente un `PRINCIPAL` por reserva en todos los tipos; `ADICIONAL`es se admiten en `INTERNO`, `ESPACIO`, `CAMPUS` y `EXTERNO`. Para `CAMPUS` y `EXTERNO`, todo `ADICIONAL` comparte las fechas de salida/devolución del `PRINCIPAL` (`reserva_recurso_campus`/`reserva_recurso_externo`) y aparece listado en la misma orden de salida.

## Contexto y campos de espacio

### `reservas.reserva_contexto`

Una fila máxima por reserva. El contexto cumple las reglas [RN-CTX](business-rules.md#contexto-de-la-reserva--rn-ctx).

| Campo | Tipo | Restricción |
|---|---|---|
| `reserva_id` | integer | PK, FK a `reservas.reservas(id)` |
| `proyecto_id` | integer | NULL, FK a `investigacion.proyectos(id_proyecto)` |
| `semillero_id` | integer | NULL, FK a `investigacion.semilleros(id_semillero)` |
| `pasantia_id` | integer | NULL, FK a `investigacion.pasantias(id_pasantia)` |
| `trabajo_grado_id` | integer | NULL, FK a `investigacion.trabajos_grado(id_trabajo_grado)` |
| `actividad_institucional_id` | integer | NULL, FK al catálogo correspondiente, pendiente de definir |

`investigacion` administra las entidades y vinculaciones académicas/investigativas descritas en el [modelo general](../../docs/data-model.md#schema-investigacion). `reservas` registra las entidades que justificaron la reserva; sus FK apuntan a las entidades, no a las tablas de vinculación. Las nuevas tablas y sus FK están definidas en el modelo y pendientes de aplicar en la base de datos.

Se permite cualquier combinación no vacía de proyecto, semillero, pasantía y trabajo de grado. Una actividad institucional solo puede registrarse si los cuatro campos académicos/investigativos son `NULL`. La restricción propuesta para cada fila es:

```sql
CONSTRAINT ck_reserva_contexto_composicion CHECK (
    (
        actividad_institucional_id IS NULL
        AND num_nonnulls(proyecto_id, semillero_id, pasantia_id, trabajo_grado_id) >= 1
    )
    OR (
        actividad_institucional_id IS NOT NULL
        AND num_nonnulls(proyecto_id, semillero_id, pasantia_id, trabajo_grado_id) = 0
    )
)
```

Cuando el tipo de reserva requiera contexto, el backend debe exigir esta fila dentro de la transacción de creación o modificación. Si el contexto es opcional y no se selecciona ninguno, no se registra una fila vacía. El backend valida las vinculaciones seleccionadas con el dominio responsable conforme a `RN-CTX-05`; las FK por sí solas no acreditan la vinculación del usuario. Para pasantías y trabajos de grado, se utiliza el `id_usuario` de la cuenta reservista y se consulta `investigacion.usuario_pasantias` o `investigacion.usuario_trabajos_grado`, respectivamente; tanto la vinculación como la entidad deben estar activas. No se utiliza `id_cuenta` como `id_usuario` ni se crean vinculaciones desde reservas.

Se conservan snapshots `proyecto_codigo`, `proyecto_nombre`, `semillero_codigo`, `semillero_nombre` y `actividad_nombre`. Para las nuevas entidades se conservan `pasantia_snapshot jsonb NULL` con `universidad`, `docente_itm_nombre` y `docente_itm_correo`, y `trabajo_grado_snapshot jsonb NULL` con `director_nombre` y `director_correo`, completados al seleccionar el contexto correspondiente. Estas copias mantienen la interpretación histórica conforme a `RN-CTX-07`, aunque los datos o vinculaciones cambien posteriormente; no constituyen catálogos administrados por reservas.

### `reservas.reserva_campos_valores`

`id integer PK`, `reserva_id integer NOT NULL FK`, `campo_id integer NOT NULL FK al campo configurado`, `campo_nombre_snapshot varchar(150) NOT NULL`, `campo_tipo_snapshot varchar(30) NOT NULL`, `obligatorio_snapshot boolean NOT NULL`, `valor_texto text NULL`, `opcion_id integer NULL`, `opcion_nombre_snapshot varchar(255) NULL`; UNIQUE `(reserva_id, campo_id)`.

La aplicación verifica que el campo pertenece al espacio del detalle, que los obligatorios tengan valor y que la opción pertenezca al campo. Los snapshots conservan la interpretación histórica.

## Adjuntos, ejecución y salida

`reservas.reserva_adjuntos`: `id integer PK`, `reserva_id integer FK`, `tipo_adjunto`, `nombre_original`, `storage_key`, `content_type`, `size_bytes`, `uploaded_by bigint FK a cuentas`, `created_at`.

`reservas.reserva_ejecucion_recursos`: `id integer PK`, `reserva_recurso_id integer FK`, `entregado_por bigint FK`, `recibido_por bigint FK NULL`, `entregado_at timestamptz`, `devuelto_at timestamptz NULL`, `observacion_entrega`, `observacion_devolucion`. Registra entrega y devolución física de recursos internos.

### `reservas.ordenes_salida`

Datos con los que el sistema **prellena** el formato "FGL 030 Orden de salida equipos y herramientas" (`RN-TIP-RC-11`, `RN-TIP-RE-11`) para imprimirlo, generado para una reserva `CAMPUS`/`EXTERNA` y listando todos sus recursos —`PRINCIPAL` y `ADICIONAL`es— (`RN-TIP-RC-01`, `RN-TIP-RE-01`, `RN-TIP-RC-07`, `RN-TIP-RE-07`). Esta tabla **no captura firmas ni autorizaciones**: los jefes de cartera/laboratorios, el V.o.B.o del Centro Parque I y el técnico de bienes muebles firman físicamente sobre el documento impreso (`RN-TIP-RC-14`, `RN-TIP-RE-14`); igual ocurre con quien entrega, retira, regresa y recibe el bien. Ninguno de esos campos existe aquí. Los datos que sí se guardan se copian como snapshot en el momento de generación — los que se prellenan desde otra tabla (`RN-TIP-RC-13`, `RN-TIP-RE-13`) se copian, no se referencian, para que la orden conserve exactamente lo impreso aunque la fuente cambie después — el mismo principio de `reserva_contexto` (`RN-CTX-07`).

| Campo | Tipo | Restricción |
|---|---|---|
| `id` | integer | PK |
| `reserva_id` | integer | UNIQUE NOT NULL, FK a `reservas(id)` |
| `tipo_orden` | varchar(10) | NOT NULL, CHECK (`CAMPUS`, `EXTERNA`) |
| `fecha_generacion` | timestamptz | NOT NULL |

**1. Información general** — capturados al crear la reserva, sin fuente previa (`RN-TIP-RC-12`, `RN-TIP-RE-12`):

| Campo | Tipo | Restricción |
|---|---|---|
| `razon_solicitud` | text | NOT NULL |
| `nombre_actividad_evento` | varchar(255) | NULL |
| `lugar_nombre` | varchar(150) | NOT NULL |
| `lugar_direccion` | varchar(255) | NOT NULL |

Prellenados y copiados como snapshot desde su fuente al generar el documento:

| Campo | Tipo | Restricción |
|---|---|---|
| `dependencia_solicitante_snapshot` | varchar(150) | NOT NULL — de `reservas.id_unidad` |
| `fecha_retiro_snapshot` | date | NOT NULL — de `reserva_recurso_campus`/`reserva_recurso_externo.fecha_salida` |
| `fecha_regreso_snapshot` | date | NOT NULL — de `...fecha_devolucion` |
| `actividad_tipo_snapshot` | varchar(30) | NOT NULL, CHECK (`PROYECTO_INVESTIGACION`, `SEMILLERO_INVESTIGACION`, `SERVICIO_EXTENSION`, `PROYECTO_ACADEMICO`, `CALIBRACION`, `DOCENCIA`, `MANTENIMIENTO`, `OTRO`) — de `reserva_contexto`; `CALIBRACION`, `DOCENCIA`, `MANTENIMIENTO` y `OTRO` no tienen contexto asociado y se registran directamente en la orden |
| `proyecto_codigo_snapshot` | varchar(60) | NULL, solo si `actividad_tipo_snapshot = 'PROYECTO_INVESTIGACION'` — de `reserva_contexto` |
| `responsable_nombre_snapshot` | varchar(150) | NOT NULL — de la cuenta (`reservas.id_cuenta`) |
| `responsable_cedula_snapshot` | varchar(20) | NOT NULL |
| `responsable_contacto_snapshot` | varchar(255) | NOT NULL |

Cédula y contacto no están definidos hoy en `usuarios.usuarios`/`personal.personal`/`auth.cuentas` (ver Puntos pendientes); hasta que existan allí, se capturan manualmente al generar la orden.

Campos generales restantes del formato:

| Campo | Tipo | Restricción |
|---|---|---|
| `observaciones` | text | NULL |
| `fecha_prorroga` | date | NULL |

`fecha_prorroga` se actualiza cuando la reserva se reprograma extendiendo su fecha de devolución (`RN-TIP-RC-15`, `RN-TIP-RE-15`); no reemplaza `fecha_regreso_snapshot`, que conserva la fecha originalmente impresa.

### `reservas.orden_salida_items`

**2. Información técnica** del FGL 030: una fila por cada recurso de la reserva (`PRINCIPAL` y `ADICIONAL`es), snapshot tomado del recurso vía `reserva_recurso_id` ([Resources](../resources/data-model.md#reservasrecursos)) al generar la orden.

| Campo | Tipo | Restricción |
|---|---|---|
| `id` | integer | PK |
| `orden_salida_id` | integer | NOT NULL, FK a `ordenes_salida(id)` |
| `reserva_recurso_id` | integer | NOT NULL, FK a `reserva_recursos(id)` |
| `placa_snapshot` | varchar(30) | NULL — el recurso puede no tener placa (`RN-TIP-RC-05`, `RN-TIP-RE-05`) |
| `descripcion_snapshot` | varchar(255) | NOT NULL |
| `bodega_snapshot` | varchar(100) | NULL |
| `cc_snapshot` | varchar(30) | NULL |
| `fecha_compra_snapshot` | date | NULL |

UNIQUE `(orden_salida_id, reserva_recurso_id)`; índice `(reserva_recurso_id)`.

Las secciones 3, 4 y 5 del FGL 030 (autorizaciones y firmas; recibido al retirar; recibido al ingresar) son enteramente físicas y no tienen columnas en ninguna de las dos tablas: se firman a mano sobre el PDF generado. El seguimiento digital de entrega y devolución de cada recurso, que dispara `EN_EJECUCION` y `FINALIZADA` (`RN-TIP-RC-09`/`10`, `RN-TIP-RE-09`/`10`), ya existe en `reserva_recursos.asignado_at`/`retirado_at`; no se duplica aquí.

La aplicación comprueba que la orden coincide con el tipo de reserva y que `orden_salida_items` incluye exactamente los recursos activos (`PRINCIPAL` y `ADICIONAL`es) de esa reserva, sin faltantes ni sobrantes.

## Estados y auditoría

`reservas.reserva_historial_estado` registra únicamente transiciones: `id integer PK`, `reserva_id integer FK`, `estado_anterior_id integer FK NULL`, `estado_nuevo_id integer FK`, `actor_cuenta_id bigint NOT NULL FK a `auth.cuentas`, `motivo`, `created_at`.

`reservas.reserva_auditoria` registra creación, modificación, aprobación, rechazo, cambios de recursos, cambios de horario/fechas, cancelación, inicio y finalización: `id integer PK`, `reserva_id integer FK`, `accion varchar(40) NOT NULL`, `actor_cuenta_id bigint NOT NULL FK`, `datos_anteriores jsonb NULL`, `datos_nuevos jsonb NULL`, `motivo text NULL`, `created_at timestamptz NOT NULL`.

## Decisiones de integridad

- PK/FK y la transacción de servicio garantizan la creación completa; el backend exige exactamente un detalle compatible con el tipo.
- CHECK cubre comparaciones invariantes de horas y fechas. Fechas pasadas, disponibilidad, capacidad, pertenencia a unidad y horario vigente son reglas de negocio.
- La exclusividad temporal de espacios y recursos requiere la garantía transaccional del dominio; los índices no la sustituyen.
- Todas las cuentas y actores usan FK real a `auth.cuentas`.

## Puntos pendientes

- Definir atributos de `SERVICIO`, catálogo de actividades y estructura exacta de campos de espacios.
- Definir migración 1:1 de equipos, mobiliarios y otros hacia `recursos`.
- Precisar la garantía transaccional contra solapamientos.
- Propuestas/contrapropuestas, recordatorios e invitaciones de calendario quedan fuera hasta contar con especificación funcional.
- Cédula y contacto (ubicación, correo, teléfono/celular) del responsable de la solicitud para el FGL 030: no están definidos en `usuarios.usuarios`, `personal.personal` ni `auth.cuentas`; requieren definición en esos módulos, no en reservas.

## Inventario de reservas procedente del principal

Las siguientes definiciones describen el inventario documentado, no el diseño objetivo anterior. Se conservan íntegramente para preparar la transición y evitar perder campos o constraints existentes.

### `reservas.tipos_reserva`

| Campo | Tipo | Null | PK/UQ/FK/default/check |
|---|---|---|---|
| `id` | integer | NN | PK `tipos_reserva_pkey`; identity |
| `nombre` | varchar(100) | NN | — |
| `descripcion` | text | Sí | — |
| `habilitado` | boolean | NN | DEFAULT `true` |

### `reservas.motivos_solicitud`

| Campo | Tipo | Null | PK/UQ/FK/default/check |
|---|---|---|---|
| `id` | integer | NN | PK `motivos_solicitud_pkey`; identity |
| `nombre` | varchar(100) | NN | — |
| `descripcion` | text | Sí | — |
| `habilitado` | boolean | NN | DEFAULT `true` |

### `reservas.reservas`

| Campo | Tipo | Null | PK/UQ/FK/default/check |
|---|---|---|---|
| `id` | integer | NN | PK `reservas_pkey`; identity |
| `id_cuenta` | bigint | NN | FK `fk_reservas_cuenta` → `auth.cuentas(id_cuenta)` |
| `id_unidad` | integer | NN | FK `reservas_id_unidad_fkey` → unidad organizacional |
| `espacio_id` | integer | Sí | FK `reservas_espacio_id_fkey` → `reservas.espacios(id)` |
| `fecha` | date | NN | — |
| `hora_inicio` | time | NN | Parte de `ck_reservas_horario` |
| `hora_fin` | time | NN | Parte de `ck_reservas_horario` |
| `asistentes` | integer | NN | CHECK `>= 0` |
| `ubicacion_uso` | varchar(255) | Sí | Condicional según `tipo_uso` |
| `tipo_uso` | varchar(30) | NN | CHECK `ESPACIO_RESERVADO`, `DENTRO_CAMPUS`, `FUERA_CAMPUS` |
| `tipo_reserva_id` | integer | NN | FK → `reservas.tipos_reserva(id)` |
| `motivo_solicitud_id` | integer | Sí | FK → `reservas.motivos_solicitud(id)` |
| `estado` | varchar(20) | NN | DEFAULT `PENDIENTE`; CHECK `PENDIENTE`, `APROBADA`, `RECHAZADA`, `CANCELADA` |
| `created_at` | timestamptz | NN | DEFAULT `now()` |
| `updated_at` | timestamptz | NN | DEFAULT `now()` |

`ck_reservas_tipo_uso`: `ESPACIO_RESERVADO` exige `espacio_id`; `DENTRO_CAMPUS` exige espacio o `ubicacion_uso` no vacío; `FUERA_CAMPUS` exige `espacio_id IS NULL` y `ubicacion_uso` no vacío. Índices: `ix_reservas_fecha_estado(fecha, estado)` y `ix_reservas_unidad_fecha(id_unidad, fecha)`.

### `reservas.reserva_acompanantes`

| Campo | Tipo | Null | PK/UQ/FK/default/check |
|---|---|---|---|
| `id` | integer | NN | PK `reserva_acompanantes_pkey`; identity |
| `reserva_id` | integer | NN | FK → `reservas.reservas(id)` ON DELETE CASCADE |
| `nombre` | varchar(150) | NN | — |
| `correo` | varchar(255) | Sí | — |

### `reservas.reserva_equipos`

| Campo | Tipo | Null | PK/UQ/FK/default/check |
|---|---|---|---|
| `id` | integer | NN | PK `reserva_equipos_pkey`; identity |
| `reserva_id` | integer | NN | FK → `reservas.reservas(id)` ON DELETE CASCADE |
| `id_equipo` | integer | NN | FK → `equipos.equipos(id_equipo)` |

UQ `uq_reserva_equipo(reserva_id, id_equipo)`; índice `ix_reserva_equipos_equipo(id_equipo)`.

### `reservas.reserva_mobiliarios`

| Campo | Tipo | Null | PK/UQ/FK/default/check |
|---|---|---|---|
| `id` | integer | NN | PK `reserva_mobiliarios_pkey`; identity |
| `reserva_id` | integer | NN | FK → `reservas.reservas(id)` ON DELETE CASCADE |
| `mobiliario_id` | integer | NN | FK → `recursos.mobiliarios(id)` |

UQ `uq_reserva_mobiliario(reserva_id, mobiliario_id)`; índice `ix_reserva_mobiliarios_mobiliario(mobiliario_id)`.

### `reservas.reserva_otros`

| Campo | Tipo | Null | PK/UQ/FK/default/check |
|---|---|---|---|
| `id` | integer | NN | PK `reserva_otros_pkey`; identity |
| `reserva_id` | integer | NN | FK → `reservas.reservas(id)` ON DELETE CASCADE |
| `otro_id` | integer | NN | FK → `recursos.otros_recursos(id)` |

UQ `uq_reserva_otro(reserva_id, otro_id)`; índice `ix_reserva_otros_otro(otro_id)`.

## Diferencias que debe resolver la migración

- Trasladar fecha, horario, espacio y asistentes de la cabecera a los detalles compatibles con cada tipo; resolver `tipo_uso` y `ubicacion_uso`.
- Mapear `estado` al catálogo `estados_reserva`, incluyendo la transición de `PENDIENTE` a `SOLICITADA` sin perder historial.
- Incorporar código y configuración por laboratorio de los tipos; conciliar descripción nullable del inventario con la descripción obligatoria del objetivo.
- Definir el destino de `motivos_solicitud` y `motivo_solicitud_id`, ausentes del objetivo.
- Definir acompañantes vinculados a cuentas conforme a RN-ACO; el inventario solo contiene nombre y correo.
- Migrar asociaciones de equipos, mobiliarios y otros hacia `reserva_recursos`, preservando referencias históricas.
- Coordinar notificaciones y auditoría con sus módulos propietarios. Los `ON DELETE CASCADE` del inventario requieren revisión frente a las reglas de conservación histórica.

Los campos abreviados sin tipo, las FK sin destino completo y los índices parciales sin predicado del diseño objetivo deben concretarse antes de generar una migración ejecutable.
