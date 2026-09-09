# Modelo de datos principal

## Alcance

Este documento describe el modelo real consultado en la base `reservas_db` del servicio PostgreSQL `db`.

- Motor: PostgreSQL 13.
- Esquema: `public`.
- Tablas: 21.
- Extensión: `btree_gist`.
- Identificadores: claves `integer` con secuencias.
- Fechas de auditoría: `timestamp with time zone`.

> Nota: la base contiene nombres heredados como `laboratorios`, `espacios` y restricciones con nombres `zonas`. Debe considerarse este esquema como la fuente de verdad del SDD hasta que se complete una migración de nombres.

## Modelo objetivo pendiente de migración

Los siguientes cambios son contractuales para el próximo modelo. Solo están documentados; todavía no se han aplicado físicamente en `reservas_db`.

### Usuarios y actores

- Se eliminará la tabla `personal`.
- Se eliminará `usuarios_laboratorios`.
- `usuarios` será la única entidad de reservistas.
- `reservas.usuario_id` será obligatorio y tendrá una FK a `usuarios.id`.
- Se eliminará `personal_id` de `reservas`, `lista_espera` y `notificaciones`.
- Se eliminarán las restricciones de actor exclusivo `usuario_id/personal_id`.

Las columnas `created_by` y `updated_by` que hoy apuntan a `personal` se conservarán sin FK. No se creará una tabla sustituta.

### Auditoría

`control_cambios` se rediseñará para contener:

| Columna | Tipo | Regla |
|---|---|---|
| `actor_tipo` | varchar | Tipo lógico del actor. |
| `actor_id` | integer | Identificador lógico, cuando exista. |
| `actor_nombre` | varchar | Nombre capturado para conservar el contexto histórico. |

Se eliminarán `usuario_id`, `personal_id` y la restricción `ck_control_cambios_actor_unico`. La auditoría no dependerá de una FK a actores.

### Integración con LIA

Se agregará `laboratorios.lia_unidad_id INTEGER NOT NULL UNIQUE` como referencia lógica a `lia_db.unidadOrganizacional.unidad_organizacional.id_unidad`.

No habrá FK nativa entre bases de datos PostgreSQL; la integridad deberá validarse en la aplicación o mediante sincronización.

## Modelo actual

La base actualmente contiene 21 tablas en `public`, incluyendo `personal`, `usuarios_laboratorios` y columnas `personal_id`. Esta sección representa el estado desplegado y no el contrato futuro.

## Modelo objetivo

El modelo objetivo elimina toda entidad local de personal administrativo/técnico. `usuarios` representa exclusivamente a los reservistas de `reservas_db`.

```text
RESERVAS_DB

usuarios
   ├──< reservas
   ├──< lista_espera
   └──< notificaciones

laboratorios
   ├──< espacios
   ├──< recursos
   ├──< tipos_reserva
   ├──< motivos_solicitud
   └── lia_unidad_id ─ ─ ─ referencia lógica ─ ─ ─► LIA_DB.unidad_organizacional

control_cambios
   └── actor_tipo + actor_id + actor_nombre
       (auditoría desacoplada de FK de actores)
```

En el modelo objetivo no aparecen `personal`, `usuarios_laboratorios` ni relaciones `usuarios/personal`.

### Referencia organizacional con LIA

`laboratorios.lia_unidad_id` es `INTEGER NOT NULL UNIQUE` y relaciona lógicamente un laboratorio con `lia_db."unidadOrganizacional".unidad_organizacional.id_unidad`.

No es una FK física PostgreSQL porque las bases son independientes. La identificación del personal que administra un laboratorio se resuelve en LIA mediante:

```text
personal → cargo → unidad_organizacional
```

El resultado se compara con `reservas_db.laboratorios.lia_unidad_id`.

La cardinalidad es:

```text
LIA unidad_organizacional 1 ─── 0..1 reservas.laboratorios
```

Solo las unidades de LIA que representan laboratorios reservables tienen una fila correspondiente en `reservas_db.laboratorios`. Las unidades que solo agrupan otras unidades o laboratorios no deben existir en `reservas_db.laboratorios`.

## Modelo lógico actual

```text
personal ───────────────┐
                        ├── laboratorios ─── espacios
                        │        │               │
                        │        ├── recursos ───┤
                        │        ├── tipos_reserva
                        │        └── motivos_solicitud
                        │
usuarios ─── reservas ───┼── reserva_acompanantes
    │          │         ├── reserva_recursos ─── recursos
    │          │         ├── reserva_espacios ─── espacios
    │          │         ├── reserva_ensayos ─── ensayos
    │          │         ├── notificaciones
    │          │         └── evento_calendario_saliente
    │
    └── usuarios_laboratorios ─── laboratorios

recursos ─── tipos_recursos
recursos ─── lista_espera
usuarios/personal ─── control_cambios
```

## Tablas principales — estado actual

### `laboratorios`

Catálogo de laboratorios y sus reglas operativas.

| Columna | Tipo | Nulo | Descripción |
|---|---|---:|---|
| `id` | integer | No | Identificador. |
| `nombre` | varchar(100) | No | Caché local del nombre oficial de LIA; no editable desde Reservas. |
| `ubicacion` | varchar(200) | No | Ubicación. |
| `capacidad` | integer | No | Capacidad general. |
| `estado` | varchar(20) | No | Estado operativo. |
| `descripcion` | text | Sí | Descripción. |
| `dias_atencion` | json | No | Días habilitados; default lunes-sábado. |
| `hora_apertura` / `hora_cierre` | time | No | Ventana de atención; defaults 07:00-20:00. |
| `horario_atencion` | json | No | Bloques horarios por día. |
| `horas_antelacion` | integer | No | Anticipación mínima; default 24. |
| `aprobacion_automatica` | boolean | No | Aprobación automática; default false. |
| `modalidad_reserva` | varchar(20) | No | `equipos`, `zonas` o `mixto`. |
| `correo` | varchar(255) | Sí | Correo del laboratorio. |
| `create_at`, `updated_at` | timestamptz | Sí | Fechas de modificación. |
| `created_by`, `updated_by` | integer | Sí | Referencias a `personal`. |

Modelo objetivo: agregar `lia_unidad_id INTEGER NOT NULL UNIQUE` como referencia lógica externa a LIA. No es una FK física porque pertenece a otra base de datos. Las FK actuales de `created_by` y `updated_by` hacia `personal` se eliminan; las columnas pueden permanecer sin FK física.

La fuente de verdad de `nombre` es `lia_db."unidadOrganizacional".unidad_organizacional.nombre`. Si cambia en LIA, debe actualizarse la caché local. La caché permite consultas rápidas y mantiene operativa Reservas cuando LIA no está disponible temporalmente.
| `notificar_por_correo` | boolean | No | Default true. |

Restricciones: `hora_apertura < hora_cierre`, `horas_antelacion >= 0` y modalidad dentro de `equipos`, `zonas`, `mixto`.

### `espacios`

Espacios o zonas pertenecientes a un laboratorio.

| Columna | Tipo | Nulo |
|---|---|---:|
| `id` | integer | No |
| `nombre` | varchar(100) | No |
| `laboratorio_id` | integer | No |
| `descripcion` | text | Sí |
| `capacidad` | integer | Sí |
| `estado` | varchar(20) | No |
| `created_at`, `updated_at` | timestamptz | No |
| `created_by`, `updated_by` | integer | Sí |

Modelo objetivo: `laboratorio_id` → `laboratorios.id`. Las FK actuales de autor hacia `personal` se eliminan; las columnas de autor pueden permanecer sin FK física.

### `recursos`

Equipos o servicios reservables.

| Columna | Tipo | Nulo |
|---|---|---:|
| `id` | integer | No |
| `nombre` | varchar(100) | No |
| `laboratorio_id` | integer | No |
| `tipo_recurso_id` | integer | No |
| `descripcion` | text | Sí |
| `capacidad` | integer | No |
| `estado` | varchar(30) | No |
| `es_prestacion_servicio` | boolean | No |
| `create_at`, `update_at` | timestamptz | No |
| `created_by`, `update_by` | integer | Sí |
| `placa` | varchar(50) | Sí |
| `requiere_apoyo_auxiliar` | boolean | No |

Modelo objetivo: `laboratorio_id` → `laboratorios.id` y `tipo_recurso_id` → `tipos_recursos.id`. Las FK actuales de responsables hacia `personal` se eliminan; las columnas pueden permanecer sin FK física. `placa` tiene índice único `uq_recursos_placa`.

### `reservas`

Entidad central de solicitudes de reserva.

| Columna | Tipo | Nulo | Descripción |
|---|---|---:|---|
| `id` | integer | No | Identificador. |
| `usuario_id` | integer | Sí | Usuario solicitante. |
| `usuario_id` | integer | No | Usuario reservista obligatorio. |
| `laboratorio_id` | integer | No | Laboratorio. |
| `recurso_id` | integer | No | Recurso principal. |
| `fecha` | date | No | Fecha de uso. |
| `hora_inicio`, `hora_fin` | time | No | Intervalo. |
| `estado` | varchar(20) | No | `esperando`, `aprobada`, `rechazada`, `cancelada`. |
| `asistentes` | integer | No | Cantidad de asistentes. |
| `tipo` | varchar(30) | Sí | Tipo de reserva. |
| `asistio` | boolean | Sí | Registro de asistencia. |
| `created_at`, `updated_at` | timestamptz | No | Fechas de auditoría. |
| `motivo_rechazo`, `descripcion` | text | Sí | Información adicional. |
| `tipo_solicitud` | varchar(30) | No | Tipo de solicitud; default `reserva_en_laboratorio`. |
| `ubicacion_uso` | varchar(200) | Sí | Lugar de uso. |
| `requiere_apoyo_auxiliar` | boolean | No | Default false. |
| `recordatorio_enviado_en` | timestamptz | Sí | Fecha del recordatorio. |
| `serie_id`, `grupo_id` | uuid | Sí | Agrupación de reservas. |
| `tipo_reserva_id` | integer | Sí | Tipo configurable. |
| `propuesta_motivo`, `propuesta_horarios` | text | Sí | Propuestas de cambio. |
| `propuesta_por` | varchar(20) | Sí | `tecnico` o `usuario`. |
| `propuesta_en` | timestamptz | Sí | Fecha de propuesta. |
| `motivo_solicitud_id` | integer | Sí | Motivo catalogado. |
| `graph_event_id` | varchar(255) | Sí | Evento de calendario externo. |
| `calendario_secuencia` | integer | No | Secuencia de sincronización; default 0. |

Restricciones:

- `hora_inicio < hora_fin`.
- `asistentes > 0`.
- El actor es `usuario_id`; no se admite `personal_id` en el modelo objetivo.
- Estados y tipos de solicitud deben pertenecer a sus catálogos definidos.
- `tipo` permite `trabajo_investigacion`, `trabajo_grado` y `servicio_de_ensayo`.

Modelo objetivo: FK a laboratorio, recurso, `usuarios`, tipo de reserva y motivo de solicitud. Se elimina `personal_id`, la FK correspondiente y la restricción polimórfica `usuario_id/personal_id`. `usuario_id` queda `NOT NULL` y referencia `usuarios.id`.

## Usuarios

### `usuarios`

Usuarios de la aplicación.

Columnas: `id`, `username`, `email`, `hashed_password`, `rol`, `created_at`, `updated_at`, `debe_cambiar_password`, `supabase_id`, `documento_identificacion`, `telefono`, `institucion`, `vinculacion`, `dependencia`, `recibir_correos`.

`username`, `email` y `supabase_id` tienen índices únicos. El rol es obligatorio.

En el modelo objetivo, `usuarios` es la única entidad de reservistas y actores de aplicación. No se conserva una tabla paralela `personal`.

## Catálogos

### `tipos_recursos`

Columnas: `id`, `nombre`, `descripcion`, `activo`.

### `tipos_reserva`

Columnas: `id`, `laboratorio_id`, `nombre`, `estado`, `created_at`, `updated_at`, `created_by`, `updated_by`.

### `motivos_solicitud`

Columnas: `id`, `laboratorio_id`, `nombre`, `codigo`, `estado`, `created_at`, `updated_at`, `created_by`, `updated_by`.

`codigo` permite `reserva_en_laboratorio`, `reserva_fuera_laboratorio` y `orden_salida`. `estado` permite `activo` e `inactivo`.

### `ensayos`

Ensayos asociados a un espacio.

Columnas: `id`, `nombre`, `zona_id`, `estado`, `created_at`, `updated_at`, `created_by`, `updated_by`.

El estado permite `activo`, `inactivo` y `mantenimiento`; `zona_id` referencia `espacios.id`.

## Tablas dependientes de reservas

### `reserva_acompanantes`

Columnas: `id`, `reserva_id`, `nombre`, `correo`. Cada fila registra un acompañante; `reserva_id` referencia `reservas.id` con eliminación en cascada.

### `reserva_ensayos`

Columnas: `id`, `reserva_id`, `ensayo_id`. Relaciona reservas con ensayos.

### `reserva_espacios`

Columnas: `id`, `reserva_id`, `espacio_id`, `fecha`, `hora_inicio`, `hora_fin`, `estado`. Relaciona una reserva con espacios/zona y conserva su intervalo.

### `reserva_recursos`

Columnas: `id`, `reserva_id`, `recurso_id`, `fecha`, `hora_inicio`, `hora_fin`, `estado`. Relaciona una reserva con recursos adicionales.

## Disponibilidad y notificaciones

### `lista_espera`

Lista de espera por recurso y franja horaria.

Modelo objetivo: columnas `id`, `usuario_id`, `recurso_id`, `fecha`, `hora_inicio`, `hora_fin`, `estado`, `created_at`, `notificada_en`. `usuario_id` referencia exclusivamente a `usuarios.id`; se elimina `personal_id` y la restricción polimórfica.

El actor debe ser exactamente uno: usuario o personal. Estados: `activa`, `notificada`, `cancelada`, `expirada`. El intervalo debe ser válido.

### `notificaciones`

Modelo objetivo: columnas `id`, `usuario_id`, `reserva_id`, `tipo`, `leida`, `created_at`. `usuario_id` es la única referencia de actor; se elimina `personal_id` y la restricción polimórfica. No se introduce un modelo de notificaciones para personal de LIA.

El actor debe ser exactamente uno. Tipos: `Pendiente`, `Aprobada`, `Rechazada`, `Cancelada`, `Actualizada`.

### `evento_calendario_saliente`

Cola de sincronización con calendario externo.

Columnas: `id`, `reserva_id`, `accion`, `estado`, `intentos`, `graph_event_id`, `asunto`, `cuerpo`, `ubicacion`, `inicio`, `fin`, `asistentes`, `comentario`, `creado_en`, `procesado_en`.

Acciones: `crear`, `actualizar`, `cancelar`. Estados: `pendiente`, `enviado`, `fallido`.

### `correo_saliente`

Cola de correos.

Columnas: `id`, `destinatario`, `asunto`, `cuerpo`, `estado`, `intentos`, `creado_en`, `enviado_en`, `es_html`, `adjunto_nombre`, `adjunto_content_type`, `adjunto_contenido`.

Estados: `pendiente`, `enviado`, `fallido`.

## Auditoría

### `control_cambios`

Registro de cambios del sistema.

Modelo objetivo: columnas `id`, `actor_tipo`, `actor_id`, `actor_nombre`, `accion`, `entidad`, `entidad_id`, `descripcion`, `created_at`.

`actor_tipo` puede ser `usuario`, `lia_personal` o `sistema`. `actor_id` apunta a `usuarios.id` cuando el tipo es `usuario`, a `lia_db.personal.personal.id_persona` cuando es `lia_personal`, y puede ser `NULL` para `sistema`. `actor_nombre` conserva un snapshot textual. No habrá FK física a usuarios ni a LIA.

## Relaciones y eliminación

Relaciones relevantes:

- Laboratorio → espacios, recursos, tipos de reserva y motivos de solicitud.
- Recurso → reservas, lista de espera y tipos de recurso.
- Reserva → acompañantes, ensayos, espacios, recursos, notificaciones y eventos de calendario.
- Usuario → reservas y notificaciones.
- Espacio → ensayos y relación espacio-recurso.

Las relaciones de detalle de una reserva usan principalmente `ON DELETE CASCADE`. Las relaciones de auditoría usan `ON DELETE SET NULL` para conservar el registro histórico.

## Índices relevantes

- Índices por fecha, estado, usuario, recurso y laboratorio en `reservas`.
- Índice compuesto `ix_reservas_recurso_fecha_estado`.
- Índices de consulta en lista de espera, notificaciones y eventos de calendario.
- Índices únicos para username/email de usuarios.
- Índice único para placa de recursos.
- Extensión `btree_gist` disponible para restricciones de exclusión de intervalos.

## Observaciones para el SDD

1. El esquema de base actual es más amplio que los modelos ORM principales del backend.
2. El modelo objetivo elimina la separación entre `usuarios` y `personal`.
3. `espacios` representa zonas dentro de `laboratorios`; no debe confundirse con el concepto de laboratorio.
4. La base actual exige `asistentes > 0`, aunque la regla funcional del SDD puede definir otra política.
5. Los estados de `ensayos`, `espacios` y `recursos` incluyen `mantenimiento` en la base actual; cualquier cambio a solo `activo/inactivo` requiere migración.
6. Debe revisarse la consistencia entre `laboratorio_id`, `espacio_id` y los nombres históricos `zona_id` antes de nuevas migraciones.
7. El modelo objetivo elimina dos tablas y varias columnas, por lo que requiere una migración de datos antes de aplicar `NOT NULL` sobre `reservas.usuario_id`.
