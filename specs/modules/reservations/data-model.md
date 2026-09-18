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

`codigo` contempla `ESPACIO`, `RECURSO_INTERNO`, `RECURSO_CAMPUS`, `RECURSO_EXTERNO` y `LISTA_ESPERA`.

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

Al crear una reserva para una cuenta Usuario, el backend aplica RN-RES-11 usando el `id_usuario` asociado a la cuenta: comprueba la actualización inicial y consulta en `investigacion` la existencia de al menos una vinculación activa y válida. Revalida esta condición al guardar, aunque el formulario se haya abierto antes de perder la última vinculación. Las FK y `perfil_actualizado_at` por sí solos no acreditan esta condición vigente; no se almacena un indicador duplicado de habilitación en la reserva. Esta comprobación es independiente de la validación del contexto seleccionado.

Cada reserva debe tener exactamente un detalle compatible con su tipo. La cabecera, el detalle y sus asociaciones se escriben en una única transacción; el backend valida la correspondencia. Cada detalle usa `reserva_id` como PK y FK, por lo que solo admite una fila de ese subtipo. Si se permiten escrituras directas fuera del servicio, se requiere una restricción diferida equivalente; no se propone un trigger complejo como requisito general.

## Detalles por tipo

### `reservas.reserva_espacio`

`reserva_id integer PK/FK`, `espacio_id integer NOT NULL FK a `espacios(id)`, `fecha date NOT NULL`, `hora_inicio time NOT NULL`, `hora_fin time NOT NULL`, `asistentes integer NOT NULL CHECK (asistentes >= 1)`.

CHECK `hora_inicio < hora_fin`. `asistentes` es la ocupación total declarada, incluido el reservista; el CHECK garantiza el mínimo de uno, mientras que la relación con los acompañantes registrados y el tope de capacidad se validan en la aplicación conforme a `RN-TIP-PE-05`. Capacidad, habilitación, horario y solapamientos son reglas de negocio.

### `reservas.reserva_recurso_interno`

`reserva_id integer PK/FK`, `fecha date NOT NULL`, `hora_inicio time NOT NULL`, `hora_fin time NOT NULL`.

CHECK `hora_inicio < hora_fin`. Debe tener al menos un recurso asociado y puede tener adicionales. Horario, habilitación y solapamientos son reglas de negocio.

### `reservas.reserva_recurso_campus` y `reservas.reserva_recurso_externo`

Cada tabla contiene `reserva_id integer PK/FK`, `fecha_salida date NOT NULL`, `fecha_devolucion date NOT NULL`, CHECK `fecha_devolucion >= fecha_salida`. Cada reserva tiene exactamente un recurso `PRINCIPAL` activo, admite `ADICIONAL`es (`RN-TIP-RC-01`, `RN-TIP-RE-01`) y tiene una orden de salida que lista todos sus recursos. `fecha_salida`/`fecha_devolucion` aplican a todos los recursos de la reserva.

### `reservas.reserva_lista_espera`

`reserva_id integer PK/FK`, `descripcion_necesidad text NOT NULL`, `viable boolean NULL`, `fecha_evaluacion_viabilidad timestamptz NULL`, `fecha_recepcion_material timestamptz NULL`, `prioridad integer NULL`, `horas_ejecucion numeric NULL CHECK (horas_ejecucion >= 0)`. No requiere fecha ni horario de ejecución.

## Recursos

El catálogo raíz `recursos.recursos` y la relación 1:1 con equipos, mobiliarios y otros se definen en [Resources](../resources/data-model.md#recursosrecursos). Este módulo define las asignaciones de dichos recursos a reservas. La configuración de laboratorios pertenece a Resources y los espacios a [Espacios](../espacios/data-model.md).

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

Índices `(recurso_id, fecha_inicio_uso, fecha_fin_uso)` y `(reserva_id, recurso_id, created_at)`. No se borran asociaciones: los cambios conservan historial. Índice único parcial sobre `(reserva_id, recurso_id)` para asociaciones activas.

La cardinalidad se valida por tipo conforme a RN-RES-12: `ESPACIO` admite cero o más recursos complementarios con rol `ADICIONAL`, sin recurso `PRINCIPAL`; `RECURSO_INTERNO`, `RECURSO_CAMPUS` y `RECURSO_EXTERNO` requieren un `PRINCIPAL` activo y admiten adicionales según sus reglas. Para `LISTA_ESPERA` no se impone un principal por defecto: su composición depende de la definición funcional del tipo. Para `RECURSO_CAMPUS` y `RECURSO_EXTERNO`, todos los adicionales comparten las fechas del principal y aparecen en la misma orden de salida.

`asignado_at` registra la asignación a la reserva y `retirado_at` su desasignación; ninguno acredita entrega ni devolución física. Estas últimas se registran en `reserva_ejecucion_recursos`.

## Disponibilidad y configuración por unidad

El cálculo aplica [RN-DIS](business-rules.md#disponibilidad--rn-dis); los estados bloqueantes y no bloqueantes se definen únicamente en RN-EST-02 y RN-EST-03.

La asignación del espacio corresponde a `reserva_espacio.espacio_id`, con el periodo definido por `fecha`, `hora_inicio` y `hora_fin`. Para recursos, la asignación efectiva corresponde a una fila de `reserva_recursos` con `estado_asignacion = 'ASIGNADO'` y un periodo definido. Este estado de asignación es independiente de la aprobación de la reserva: puede asignarse un recurso al registrar la solicitud, antes de su aprobación. Las filas `SOLICITADO`, `NO_DISPONIBLE` y `RETIRADO` no representan asignaciones bloqueantes.

El periodo del recurso se obtiene del detalle de su tipo o de `fecha_inicio_uso` y `fecha_fin_uso` cuando corresponda a su uso efectivo; las fechas deben ser consistentes con el detalle. La comparación conserva la semántica horaria o por días de RN-DIS-01 y RN-DIS-02. Sin periodo definido no se genera un bloqueo temporal, incluso para solicitudes de lista de espera. Asignar un periodo posteriormente exige la misma validación transaccional.

Los recursos complementarios no disponibles se conservan como `NO_DISPONIBLE`, sin asignación para el periodo incompatible, conforme a RN-TIP-PE-14. No impiden guardar la reserva del espacio. Al modificar o aprobar, la comparación excluye las asignaciones de la propia reserva.

Las opciones `mostrar_estado_reserva` y `mostrar_reservista` se almacenan únicamente en [reservas.laboratorios_config](../resources/data-model.md#reservaslaboratorios_config), ambas `boolean NOT NULL DEFAULT false`, por `id_unidad`. Reservations consulta esa configuración conforme a RN-DIS-07 a RN-DIS-10; no duplica esos campos en cada reserva. El backend filtra la respuesta de disponibilidad antes de enviarla al Usuario.

### Garantía transaccional — pendiente de implementación

Validar conflictos y escribir la reserva, el detalle y las asignaciones debe constituir una operación atómica protegida frente a concurrencia, conforme a RN-DIS-05. Dos operaciones incompatibles no pueden confirmar ambas. Un fallo de validación revierte las escrituras de la operación.

Queda pendiente seleccionar e implementar el mecanismo de protección en backend y PostgreSQL, incluyendo creación, reprogramación, cambio de elementos y aprobación. Una transacción sin protección específica frente a concurrencia, una consulta previa o los índices ordinarios no acreditan esta garantía. Esta documentación define el requisito, no una protección ya implementada.

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
| `actividad_institucional_id` | integer | NULL, FK a `investigacion.actividades_institucionales(id_actividad)` |
| `proyecto_codigo` | varchar(50) | NULL |
| `proyecto_nombre` | varchar(255) | NULL |
| `semillero_codigo` | varchar(50) | NULL |
| `semillero_nombre` | varchar(150) | NULL |
| `actividad_nombre` | varchar(255) | NULL |
| `pasantia_universidad` | varchar(255) | NULL |
| `pasantia_docente_nombre` | varchar(150) | NULL |
| `pasantia_docente_correo` | varchar(150) | NULL |
| `trabajo_grado_director_nombre` | varchar(150) | NULL |
| `trabajo_grado_director_correo` | varchar(150) | NULL |

`investigacion` administra las entidades, las actividades institucionales y las vinculaciones académicas/investigativas descritas en el [modelo general](../../docs/data-model.md#schema-investigacion). `reservas` registra las entidades que justificaron la reserva; sus FK apuntan a las entidades, no a las tablas de vinculación. La disponibilidad de una actividad institucional para nuevas reservas se valida conforme a RN-ACT del módulo Researchs; reservas no duplica esa regla. Las nuevas tablas y sus FK están definidas en el modelo y pendientes de aplicar en la base de datos.

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

Las diez columnas de snapshot se completan al seleccionar el contexto correspondiente y solo tienen valor cuando su FK asociada no es `NULL`: `proyecto_codigo` y `proyecto_nombre` acompañan a `proyecto_id`; `semillero_codigo` y `semillero_nombre` a `semillero_id`; `pasantia_universidad`, `pasantia_docente_nombre` y `pasantia_docente_correo` a `pasantia_id`; `trabajo_grado_director_nombre` y `trabajo_grado_director_correo` a `trabajo_grado_id`; y `actividad_nombre` a `actividad_institucional_id`. Estas copias mantienen la interpretación histórica conforme a `RN-CTX-07`, aunque los datos o vinculaciones cambien posteriormente; no constituyen catálogos administrados por reservas.

### `reservas.reserva_campos_valores`

`id integer PK`, `reserva_id integer NOT NULL FK`, `campo_id integer NOT NULL FK al campo configurado`, `campo_nombre_snapshot varchar(150) NOT NULL`, `campo_tipo_snapshot varchar(30) NOT NULL`, `obligatorio_snapshot boolean NOT NULL`, `valor_texto text NULL`, `opcion_id integer NULL`, `opcion_nombre_snapshot varchar(255) NULL`; UNIQUE `(reserva_id, campo_id)`.

La aplicación verifica que el campo pertenece al espacio del detalle, que los obligatorios tengan valor y que la opción pertenezca al campo. Los snapshots conservan la interpretación histórica.

## Adjuntos, ejecución y salida

`reservas.reserva_adjuntos`: `id integer PK`, `reserva_id integer FK`, `tipo_adjunto`, `nombre_original`, `storage_key`, `content_type`, `size_bytes`, `uploaded_by bigint FK a cuentas`, `created_at`.

### `reservas.reserva_ejecucion_recursos`

Registro de entrega y devolución física para `RECURSO_INTERNO`, `RECURSO_CAMPUS` y `RECURSO_EXTERNO`, independiente de la asignación temporal y de las firmas físicas del FGL 030.

| Campo | Tipo | Restricción |
|---|---|---|
| `id` | integer | PK |
| `reserva_recurso_id` | integer | NOT NULL, FK a `reservas.reserva_recursos(id)` |
| `entregado_por` | bigint | NOT NULL, FK a `auth.cuentas(id_cuenta)` |
| `recibido_por` | bigint | NULL, FK a `auth.cuentas(id_cuenta)` |
| `entregado_at` | timestamptz | NOT NULL |
| `devuelto_at` | timestamptz | NULL; debe ser mayor o igual que `entregado_at` |
| `observacion_entrega` | text | NULL |
| `observacion_devolucion` | text | NULL |

`recibido_por` y `devuelto_at` se completan juntos al devolver el recurso. No puede existir más de una entrega abierta por `reserva_recurso_id`. Las transiciones de la reserva se rigen por las reglas de ejecución del tipo; asignar o desasignar un recurso no provoca por sí solo el inicio o la finalización de ejecución.

### `reservas.ordenes_salida`

Datos con los que el sistema **prellena** el formato "FGL 030 Orden de salida equipos y herramientas" (`RN-TIP-RC-11`, `RN-TIP-RE-11`) para imprimirlo, generado para una reserva de tipo `RECURSO_CAMPUS` o `RECURSO_EXTERNO` y listando todos sus recursos —`PRINCIPAL` y `ADICIONAL`es— (`RN-TIP-RC-01`, `RN-TIP-RE-01`, `RN-TIP-RC-07`, `RN-TIP-RE-07`). Esta tabla **no captura firmas ni autorizaciones**: los jefes de cartera/laboratorios, el V.o.B.o del Centro Parque I y el técnico de bienes muebles firman físicamente sobre el documento impreso (`RN-TIP-RC-14`, `RN-TIP-RE-14`); igual ocurre con quien entrega, retira, regresa y recibe el bien. Ninguno de esos campos existe aquí. Los datos que sí se guardan se copian como snapshot en el momento de generación — los que se prellenan desde otra tabla (`RN-TIP-RC-13`, `RN-TIP-RE-13`) se copian, no se referencian, para que la orden conserve exactamente lo impreso aunque la fuente cambie después — el mismo principio de `reserva_contexto` (`RN-CTX-07`).

| Campo | Tipo | Restricción |
|---|---|---|
| `id` | integer | PK |
| `reserva_id` | integer | UNIQUE NOT NULL, FK a `reservas(id)` |
| `fecha_generacion` | timestamptz | NOT NULL |

**1. Información general** — capturados al crear la reserva, sin fuente previa (`RN-TIP-RC-12`, `RN-TIP-RE-12`):

| Campo | Tipo | Restricción |
|---|---|---|
| `razon_solicitud` | text | NOT NULL |
| `nombre_actividad_evento` | varchar(255) | NULL; obligatorio cuando entre las actividades marcadas figure `OTRO`, para que el documento impreso identifique de qué se trata |
| `lugar_nombre` | varchar(150) | NOT NULL |
| `lugar_direccion` | varchar(255) | NOT NULL |

Prellenados y copiados como snapshot desde su fuente al generar el documento:

| Campo | Tipo | Restricción |
|---|---|---|
| `dependencia_solicitante_snapshot` | varchar(255) | NOT NULL — afiliación de quien solicita: `usuarios.usuarios.dependencia` para cuentas `USUARIO`, la unidad del cargo para cuentas `PERSONAL`. No es la unidad receptora de la reserva |
| `fecha_retiro_snapshot` | date | NOT NULL — de `reserva_recurso_campus`/`reserva_recurso_externo.fecha_salida` |
| `fecha_regreso_snapshot` | date | NOT NULL — de `...fecha_devolucion` |
| `proyecto_codigo_snapshot` | varchar(60) | NULL, obligatorio cuando entre las actividades marcadas figure `PROYECTO_INVESTIGACION` — de `reserva_contexto` |
| `responsable_nombre_snapshot` | varchar(150) | NOT NULL — `nombre` de la identidad asociada a `reservas.id_cuenta` |
| `responsable_cedula_snapshot` | varchar(20) | NOT NULL — `documento` de esa identidad |
| `responsable_contacto_snapshot` | varchar(255) | NOT NULL — compuesto con `correo` y `telefono` de esa identidad |

Los tres se prellenan desde el perfil y nunca se capturan manualmente (`RN-TIP-RC-13`, `RN-TIP-RE-13`). La fuente depende del tipo de cuenta, conforme a `RN-AUTH-ID-03`: para `USUARIO` es `usuarios.usuarios`, que registra `nombre`, `documento`, `telefono` y `correo` obligatorios por `RN-DAT-01`; para `PERSONAL` es `personal.personal`, que ya define `documento`, `correo` y `telefono` como `NOT NULL`. En ambos casos el valor se copia como snapshot al generar la orden.

Campos generales restantes del formato:

| Campo | Tipo | Restricción |
|---|---|---|
| `observaciones` | text | NULL |
| `fecha_prorroga` | date | NULL |

`fecha_prorroga` se actualiza cuando la reserva se reprograma extendiendo su fecha de devolución (`RN-TIP-RC-15`, `RN-TIP-RE-15`); no reemplaza `fecha_regreso_snapshot`, que conserva la fecha originalmente impresa.

### `reservas.orden_salida_actividades`

Casillas marcadas en "Actividad asociada a" del FGL 030. El formato dice "marque cuando aplique", por lo que admite varias simultáneas, coherente con `RN-CTX-03`.

| Campo | Tipo | Restricción |
|---|---|---|
| `orden_salida_id` | integer | PK compuesta, FK a `ordenes_salida(id)` |
| `actividad` | varchar(30) | PK compuesta, CHECK (`PROYECTO_INVESTIGACION`, `SEMILLERO_INVESTIGACION`, `SERVICIO_EXTENSION`, `PROYECTO_ACADEMICO`, `CALIBRACION`, `DOCENCIA`, `MANTENIMIENTO`, `OTRO`) |

La PK compuesta impide marcar dos veces la misma casilla. Toda orden debe tener al menos una fila. Los ocho valores corresponden exactamente a las casillas del formato impreso y no deben ampliarse sin una nueva versión del FGL 030.

El mapeo desde `reserva_contexto` al generar la orden es:

| Contexto registrado | Casilla marcada |
|---|---|
| `proyecto_id` | `PROYECTO_INVESTIGACION`, más `proyecto_codigo_snapshot` |
| `semillero_id` | `SEMILLERO_INVESTIGACION` |
| `pasantia_id` | `OTRO` |
| `trabajo_grado_id` | `OTRO` |
| `actividad_institucional_id` | la casilla que corresponda a la actividad, o `OTRO` |

Pasantía y trabajo de grado no tienen casilla propia en el formato: se marcan como `OTRO` y su detalle concreto se imprime en `nombre_actividad_evento`, que por eso pasa a ser obligatorio en ese caso. `CALIBRACION`, `DOCENCIA`, `MANTENIMIENTO` y `SERVICIO_EXTENSION` no provienen de `reserva_contexto` y se marcan directamente en la orden.

### `reservas.orden_salida_items`

**2. Información técnica** del FGL 030: una fila por cada recurso de la reserva (`PRINCIPAL` y `ADICIONAL`es), snapshot tomado del recurso vía `reserva_recurso_id` ([Resources](../resources/data-model.md#recursosrecursos)) al generar la orden.

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

Las secciones 3, 4 y 5 del FGL 030 se firman físicamente sobre el documento. El seguimiento digital de entrega y devolución utiliza `reserva_ejecucion_recursos.entregado_at` y `devuelto_at`, con las cuentas responsables, conforme a las reglas de ejecución del tipo. No utiliza `reserva_recursos.asignado_at` ni `retirado_at` y no representa las firmas del formato.

La orden no almacena su propio tipo: se deriva de `reserva_id`, que es UNIQUE, hacia `tipos_reserva.codigo`, y solo existe para los tipos `RECURSO_CAMPUS` y `RECURSO_EXTERNO`. La aplicación comprueba que `orden_salida_items` incluye exactamente los recursos activos (`PRINCIPAL` y `ADICIONAL`es) de esa reserva, sin faltantes ni sobrantes.

## Propuestas de horario

### `reservas.reserva_propuestas`

Propuestas y contrapropuestas de horario o fecha alternativa (`RN-PROP-01` a `RN-PROP-07`). Conserva la negociación completa: las propuestas no se borran ni se sobrescriben.

| Campo | Tipo | Restricción |
|---|---|---|
| `id` | integer | PK |
| `reserva_id` | integer | NOT NULL, FK a `reservas(id)` |
| `origen` | varchar(10) | NOT NULL, CHECK (`TECNICO`, `USUARIO`) |
| `fecha_propuesta` | date | NOT NULL |
| `hora_inicio`, `hora_fin` | time | NULL; obligatorias cuando el tipo de reserva tenga horario |
| `motivo` | text | NOT NULL |
| `estado` | varchar(15) | NOT NULL, CHECK (`VIGENTE`, `ACEPTADA`, `RECHAZADA`, `SUSTITUIDA`) |
| `creada_por` | bigint | NOT NULL, FK a `auth.cuentas` |
| `resuelta_por` | bigint | NULL, FK a `auth.cuentas` |
| `created_at` | timestamptz | NOT NULL |
| `resuelta_at` | timestamptz | NULL |

CHECK `hora_inicio < hora_fin` cuando ambas tienen valor. Índice único parcial sobre `(reserva_id)` para filas con `estado = 'VIGENTE'`, que garantiza `RN-PROP-07`: una sola propuesta o contrapropuesta vigente a la vez. Índice `(reserva_id, created_at)` para reconstruir la negociación.

Una contrapropuesta marca la propuesta anterior como `SUSTITUIDA` y crea una fila nueva con `origen = 'USUARIO'`, conforme a `RN-PROP-03`. Aceptar una propuesta revalida las reglas del tipo antes de reprogramar la reserva (`RN-PROP-05`); rechazarla deja la reserva en `SOLICITADA` con su horario original (`RN-PROP-06`). Ninguna propuesta cambia por sí misma el estado de la reserva (`RN-PROP-02`).

## Estados y auditoría

`reservas.reserva_historial_estado` registra únicamente transiciones: `id integer PK`, `reserva_id integer FK`, `estado_anterior_id integer FK NULL`, `estado_nuevo_id integer FK`, `actor_cuenta_id bigint NOT NULL FK a `auth.cuentas`, `motivo`, `created_at`.

`reservas.reserva_auditoria` registra creación, modificación, aprobación, rechazo, cambios de recursos, cambios de horario/fechas, cancelación, inicio y finalización: `id integer PK`, `reserva_id integer FK`, `accion varchar(40) NOT NULL`, `actor_cuenta_id bigint NOT NULL FK`, `datos_anteriores jsonb NULL`, `datos_nuevos jsonb NULL`, `motivo text NULL`, `created_at timestamptz NOT NULL`.

## Decisiones de integridad

- PK/FK y la transacción de servicio garantizan la creación completa; el backend exige exactamente un detalle compatible con el tipo.
- CHECK cubre comparaciones invariantes de horas y fechas. Fechas pasadas, disponibilidad, capacidad, pertenencia a unidad y horario vigente son reglas de negocio.
- La exclusividad temporal de espacios y recursos requiere la garantía transaccional del dominio; los índices no la sustituyen.
- Todas las cuentas y actores usan FK real a `auth.cuentas`.

## Puntos pendientes

- Definir catálogo de actividades y estructura exacta de campos de espacios.
- Definir migración 1:1 de equipos, mobiliarios y otros hacia `recursos`.
- Implementar y verificar el mecanismo contra solapamientos descrito en «Garantía transaccional — pendiente de implementación» y migrar las opciones de visibilidad por unidad.
- Las propuestas y contrapropuestas ya tienen reglas (`RN-PROP`), flujo (`UF-RES-15`) y respaldo persistente en `reserva_propuestas`. Los recordatorios tienen reglas (`RN-REC`), flujo (`UF-RES-16`) y su anticipación configurable en `laboratorios_config.recordatorio_horas_antes`; su constancia de envío pertenece a notificaciones y no se duplica aquí. El archivo `.ics` de confirmación se genera y adjunta al correo sin una tabla propia, sin sincronización directa con calendarios externos y sin persistir identificadores de eventos externos, conforme a RN-CAL.
- Definir cómo se compone `responsable_contacto_snapshot` a partir de `correo` y `telefono`, dado que el FGL 030 imprime una sola línea de contacto que además contempla ubicación y celular.

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
| `reserva_id` | integer | NN | PK compuesta; FK → `reservas.reservas(id)` |
| `id_cuenta` | bigint | NN | PK compuesta; FK → `auth.cuentas(id_cuenta)` |

La PK compuesta `(reserva_id, id_cuenta)` impide repetir una cuenta en la misma reserva. La aplicación solo permite insertar la asociación cuando la reserva tiene proyecto o semillero y la cuenta mantiene una vinculación activa con al menos uno de ellos; si ambos existen, valida la unión de ambas vinculaciones. Esta es la única estructura de acompañantes del modelo de Reservations.

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
- Migrar asociaciones de equipos, mobiliarios y otros hacia `reserva_recursos`, preservando referencias históricas.
- Coordinar notificaciones y auditoría con sus módulos propietarios. Los `ON DELETE CASCADE` del inventario requieren revisión frente a las reglas de conservación histórica.

Los campos abreviados sin tipo, las FK sin destino completo y los índices parciales sin predicado del diseño objetivo deben concretarse antes de generar una migración ejecutable.
