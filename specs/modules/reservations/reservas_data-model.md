# Modelo de datos — Reservas

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

Cada tabla contiene `reserva_id integer PK/FK`, `fecha_salida date NOT NULL`, `fecha_devolucion date NOT NULL`, CHECK `fecha_devolucion >= fecha_salida`. Cada reserva tiene exactamente un recurso principal activo y una orden del tipo correspondiente.

### `reservas.reserva_lista_espera`

`reserva_id integer PK/FK`, `descripcion_necesidad text NOT NULL`, `viable boolean NULL`, `fecha_evaluacion_viabilidad timestamptz NULL`, `fecha_recepcion_material timestamptz NULL`, `prioridad integer NULL`, `horas_ejecucion numeric NULL CHECK (horas_ejecucion >= 0)`. No requiere fecha ni horario de ejecución.

### `reservas.reserva_servicio`

`reserva_id integer PK/FK`. Sus atributos quedan pendientes hasta definir el flujo funcional.

## Recursos

### `reservas.recursos`

Catálogo raíz para evitar `recurso_id` ambiguo: `id integer PK`, `id_unidad integer NOT NULL FK`, `tipo varchar(20) NOT NULL CHECK (tipo IN ('EQUIPO','MOBILIARIO','OTRO'))`, `habilitado boolean NOT NULL`, `created_at timestamptz NOT NULL`, `updated_at timestamptz NOT NULL`.

`equipos`, `mobiliarios` y `otros` conservan sus atributos propios y se relacionan 1:1 con `recursos.id` mediante PK/FK. Las reservas referencian solo `recursos.id`.

### `reservas.reserva_recursos`

| Campo | Tipo | Restricción |
|---|---|---|
| `id` | integer | PK |
| `reserva_id` | integer | NOT NULL, FK |
| `recurso_id` | integer | NOT NULL, FK a `recursos(id)` |
| `rol` | varchar(20) | NOT NULL, CHECK `PRINCIPAL` o `ADICIONAL` |
| `estado_asignacion` | varchar(20) | NOT NULL, CHECK `SOLICITADO`, `ASIGNADO`, `NO_DISPONIBLE`, `RETIRADO` |
| `solicitado_at` | timestamptz | NOT NULL |
| `asignado_at`, `retirado_at` | timestamptz | NULL |
| `fecha_inicio_uso`, `fecha_fin_uso` | timestamptz | NULL |
| `incorporado_por` | bigint | NOT NULL, FK a `auth.cuentas` |
| `created_at` | timestamptz | NOT NULL |

Índices `(recurso_id, fecha_inicio_uso, fecha_fin_uso)` y `(reserva_id, recurso_id, created_at)`. No se borran asociaciones: los cambios conservan historial. Índice único parcial sobre `(reserva_id, recurso_id)` para asociaciones activas. Para `CAMPUS` y `EXTERNO` la aplicación limita a un `PRINCIPAL`; `INTERNO` y `ESPACIO` admiten adicionales.

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

`reservas.ordenes_salida`: `id integer PK`, `reserva_id integer UNIQUE NOT NULL FK`, `reserva_recurso_id integer UNIQUE NOT NULL FK a `reserva_recursos(id)`, `tipo_orden varchar(10) NOT NULL CHECK (tipo_orden IN ('CAMPUS','EXTERNA'))`, `fecha_generacion`, `aprobado_por bigint FK NULL`, `fecha_aprobacion`, `fecha_entrega`, `recepcion_usuario_at`, `fecha_devolucion_real`, `observacion`. La aplicación comprueba que la orden coincide con el tipo de reserva y su único recurso principal. No se inventan campos FGL 030 no definidos.

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
