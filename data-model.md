# Modelo de datos — reservas-parquei

> Estado final tras las Fases 1–7 de Juan Carlos (renombres `Espacio→Laboratorio` / `Zona→Espacio`, remoción de Ensayos/recurrentes/Modalidad/PS-gate, y tabla `tipos_reserva` por laboratorio). Complementa a `backend/CLAUDE.md` y `app_flutter/CLAUDE.md` — pensado para lectura externa, no solo para quien ya conoce el código.

Última revisión: 2026-09-02. Commit de referencia: `bd014e1` (forma única + recursos editables + motivos en tabla + links en correos + propuesta/contrapropuesta).

## Convenciones

- **Motor:** PostgreSQL (13 en desarrollo, 17 en `reservas_test`). Extensión `btree_gist` requerida por los `EXCLUDE` de solapamiento.
- **Migraciones:** `backend/app/migrations.py` — SQL idempotente dentro de `engine.begin()` (una única transacción). `Base.metadata.create_all()` corre **antes** y crea vacías las tablas nuevas; las migraciones solo rellenan/backfillean y crean constraints. Nunca se hace `DROP TABLE`/`DROP COLUMN` automático sin confirmación explícita aparte (`ensayos`, `serie_id`, `reservas.tipo` quedan huérfanos sin uso — ver § Historial).
- **Auditoría:** `created_at`/`updated_at` (`timestamptz`, `server_default=now()`) y `created_by`/`updated_by` (`FK personal.id`, siempre `NULL`able desde 2026-08-29 — se limpia a `NULL` si la FK apunta a un id que ya no es `personal`, ver `migrations.py:_LIMPIAR_CREATED_BY_HUERFANOS`).
- **Soft-delete:** no existe `deleted_at`; se usa `estado` (`activo`/`inactivo`/`mantenimiento` para entidades gestionables).
- **Fechas/horas:** `reservas.fecha` (`date`) + `hora_inicio`/`hora_fin` (`time`) naive en `America/Bogota` (así las devuelve el backend, así se persisten — sin conversión a `timestamptz`).

## Diagrama ER (simplificado)

```
Laboratorio 1──N Espacio
Laboratorio 1──N Recurso
Laboratorio 1──N TipoReserva
Laboratorio 1──N MotivoSolicitud
Laboratorio 1──N Reserva
Laboratorio 1──N UsuarioLaboratorio N──1 Personal (gestor)

Espacio N──N Recurso (vía espacio_recursos, con UNIQUE(recurso_id))

Reserva N──N Recurso (vía reserva_recursos, desnormalizado)
Reserva N──N Espacio (vía reserva_espacios, desnormalizado)
Reserva 1──N ReservaAcompanante
Reserva N──1 TipoReserva (nullable)
Reserva N──1 MotivoSolicitud (nullable, FK motivo_solicitud_id)
Reserva N──1 Laboratorio, N──1 Recurso (ancla histórica recurso_id)

Personal 1──N Reserva (personal_id)  |  Usuario 1──N Reserva (usuario_id)
       ↕ polimórfico: exactamente uno NO NULL (ck_reservas_actor_unico)
```

## Tablas principales

### `laboratorios` — Laboratorio (antes `espacios`)

Entidad de nivel superior. Un laboratorio agrupa espacios, recursos, tipos de reserva y reservas.

| Columna | Tipo | Nulos | Notas |
|---|---|---|---|
| `id` | `serial PK` | NO | |
| `nombre` | `varchar(100)` | NO | |
| `ubicacion` | `varchar(200)` | NO | default `Principal` |
| `capacidad` | `integer` | NO | `CHECK ck_laboratorios_horario_atencion: hora_apertura < hora_cierre` + `ck_laboratorios_horas_antelacion >=0` |
| `estado` | `varchar(20)` | NO | `activo` por defecto; CHECK `activo`/`inactivo`/`mantenimiento` |
| `descripcion` | `text` | SÍ | |
| `dias_atencion` | `jsonb` | NO | default `[0,1,2,3,4,5]` (lun–sáb) |
| `hora_apertura` | `time` | NO | default `07:00` |
| `hora_cierre` | `time` | NO | default `20:00` |
| `horario_atencion` | `jsonb` | NO | `{ "0": [7,8,…], … }` — 16 franjas 06–22 |
| `horas_antelacion` | `integer` | NO | default 24 |
| `aprobacion_automatica` | `boolean` | NO | default false |
| `correo` | `varchar(255)` | SÍ | contacto del laboratorio |
| `create_at` / `updated_at` | `timestamptz` | SÍ/ SÍ | |
| `created_by` / `updated_by` | `FK personal.id` | SÍ | nullable desde 2026-08-29 |

Relaciones: `laboratorio.recursos` (`Recurso.laboratorio_id`), `laboratorio.gestores` (`UsuarioLaboratorio.laboratorio_id`), `laboratorio.reservas` (`Reserva.laboratorio_id`).

Origen: `backend/app/models/laboratorio.py:8`, `migrations.py:_RENOMBRAR_LABORATORIO_Y_ESPACIO` (ordena `espacios→laboratorios` antes que `zonas→espacios` para liberar el nombre).

### `espacios` — Espacio (antes `zonas`)

Sub-área dentro de un laboratorio. Siempre pertenece a exactamente un laboratorio.

| Columna | Tipo | Nulos | Notas |
|---|---|---|---|
| `id` | `serial PK` | NO | |
| `nombre` | `varchar(100)` | NO | |
| `laboratorio_id` | `FK laboratorios.id` | NO | `index`, antes `zonas.espacio_id` |
| `descripcion` | `text` | SÍ | |
| `capacidad` | `integer` | SÍ | nullable — si es `NULL` no limita asistentes |
| `estado` | `varchar(20)` | NO | default `activo`, CHECK `activo`/`inactivo`/`mantenimiento` (`ck_espacios_estado`) |
| `created_at` / `updated_at` | `timestamptz` | NO | `server_default=now()` |
| `created_by` / `updated_by` | `FK personal.id` | SÍ | |

Relaciones: `espacio.laboratorio` (`Laboratorio`), `espacio.recursos` vía `espacio_recursos` (`viewonly` — la escritura pasa solo por `PUT /espacios/{id}/recursos`, `app/models/espacio.py:32`).

### `tipos_recursos` / `recursos`

Catálogo de tipos de recurso (global) y recursos físicos.

**`tipos_recursos`** (`TipoRecurso`, `backend/app/models/recurso.py:7`): `id PK`, `nombre varchar(80)`, `descripcion text default ""`, `activo varchar(50) default activo`. Semilla `General` si la tabla está vacía (`migrations.py`).

**`recursos`** (`Recurso`):

| Columna | Tipo | Nulos | Notas |
|---|---|---|---|
| `id` | `serial PK` | NO | |
| `nombre` | `varchar(100)` | NO | |
| `laboratorio_id` | `FK laboratorios.id` | NO | antes `espacio_id`; `index ix_recursos_laboratorio_id` |
| `tipo_recurso_id` | `FK tipos_recursos.id` | NO | |
| `descripcion` | `text` | SÍ | |
| `capacidad` | `integer` | NO | `CHECK ... SET NOT NULL` restaurado tras revert Fase 12E |
| `estado` | `varchar(30)` | NO | default `activo` |
| `es_prestacion_servicio` | `boolean` | NO | informativo desde Fase 4 (el gate `validar_acceso_ps` se quitó de `services/reservas.py`) |
| `placa` | `varchar(50)` | SÍ | identificador de activo físico, `UNIQUE uq_recursos_placa` (NULLs no colisionan) |
| `create_at` / `update_at` | `timestamptz` | NO | `server_default=now()` |
| `created_by` / `update_by` | `FK personal.id` | SÍ | nullable |

Índices/FKs: `fk_recursos_tipo`, `recursos_created_by_fkey` / `update_by_fkey` → `personal.id`.

### `tipos_reserva` — TipoReserva (Fase 7)

Catálogo **por laboratorio** (reemplaza el enum fijo `TipoReserva` de `domain/enums.py`).

| Columna | Tipo | Nulos | Notas |
|---|---|---|---|
| `id` | `serial PK` | NO | |
| `laboratorio_id` | `FK laboratorios.id` | NO | `index` |
| `nombre` | `varchar(100)` | NO | |
| `estado` | `varchar(20)` | NO | default `activo`, CHECK `activo`/`inactivo` (`ck_tipos_reserva_estado`) |
| `created_at` / `updated_at` | `timestamptz` | NO | |
| `created_by` / `updated_by` | `FK personal.id` | SÍ | |

Constraint: `UNIQUE (laboratorio_id, nombre)` (`uq_tipos_reserva_laboratorio_nombre`). Sin valores compartidos entre laboratorios ni catálogo global — cada laboratorio da de alta los suyos vía `POST /tipos-reserva` (`backend/app/api/tipos_reserva.py`, `crud/tipos_reserva.py`).

En Flutter: `app_flutter/lib/features/tipos_reserva/domain/tipo_reserva.dart` (`@freezed`, `estado: String` plano `activo`/`inactivo`, no `EstadoEntidad`).

### `motivos_solicitud` — MotivoSolicitud (Fase 2, 2026-09-02)

Catálogo **por laboratorio** (espejo de `tipos_reserva`) para el dropdown de motivo dentro de la forma única de reserva.

| Columna | Tipo | Nulos | Notas |
|---|---|---|---|
| `id` | `serial PK` | NO | |
| `laboratorio_id` | `FK laboratorios.id` | NO | `index` |
| `nombre` | `varchar(100)` | NO | ej. `Reserva en laboratorio` |
| `codigo` | `varchar(30)` | NO | `CHECK reserva_en_laboratorio/reserva_fuera_laboratorio/orden_salida` (`ck_motivos_solicitud_codigo`), `UNIQUE(laboratorio_id,codigo)` |
| `estado` | `varchar(20)` | NO | default `activo`, `CHECK activo/inactivo` |
| `created_at` / `updated_at` | `timestamptz` | NO | |
| `created_by` / `updated_by` | `FK personal.id` | SÍ | |

Backfill idempotente por laboratorio en `migrations.py` (3 motivos base). API `GET /motivos-solicitud?laboratorio_id=` (`backend/app/api/motivos_solicitud.py`), Flutter `features/motivos_solicitud/` (domain `MotivoSolicitud`, repo `motivosSolicitudProvider`).

### `reservas` — Reserva

Tabla central. Una reserva siempre ocurre en un laboratorio, sobre una fecha y un rango horario de un mismo día, con uno o varios recursos y/o espacios.

| Columna | Tipo | Nulos | Notas |
|---|---|---|---|
| `id` | `serial PK` | NO | |
| `usuario_id` | `FK usuarios.id` | SÍ | polimórfico — exactamente uno de `usuario_id`/`personal_id` es NO NULL (`ck_reservas_actor_unico: (usuario_id IS NOT NULL) != (personal_id IS NOT NULL)`) |
| `personal_id` | `FK personal.id` | SÍ | idem; `Reserva.actor` (`usuario or personal`) |
| `laboratorio_id` | `FK laboratorios.id` | NO | `index`; antes `espacio_id` |
| `recurso_id` | `FK recursos.id` | NO | **ancla histórica** (Fase 12C-4a) — se conserva como columna única aunque la fuente de verdad multi-eje viva en `reserva_recursos`/`reserva_espacios` |
| `fecha` | `date` | NO | `index` |
| `hora_inicio` / `hora_fin` | `time` | NO | `CHECK hora_inicio < hora_fin` |
| `estado` | `varchar(20)` | NO | default `esperando`, CHECK `esperando`/`aprobada`/`rechazada`/`cancelada`; transiciones `esperando→{aprobada,rechazada,cancelada}`, `aprobada→cancelada` (`domain/enums.py:159`, `services/reservas.py`) |
| `asistentes` | `integer` | NO | `CHECK >0` |
| `tipo` | `varchar(30)` | SÍ | **legado inerte** — enum viejo `trabajo_investigacion`/`trabajo_grado`/`servicio_de_ensayo` (`ck_reservas_tipo`); se deja sin backfill ni lectura/escritura nueva (ver § Historial) |
| `tipo_reserva_id` | `FK tipos_reserva.id` | SÍ | **nuevo** (Fase 7) — opcional, reemplaza `tipo` hacia adelante; sin CHECK (el catálogo es dinámico) |
| `asistio` | `boolean` | SÍ | nullable, solo gestor/admin vía `PUT /reservas/{id}/asistio` |
| `motivo_rechazo` | `text` | SÍ | solo cuando `estado=rechazada`; se limpia al salir de rechazada |
| `descripcion` | `text` | SÍ | Fase A3 — "Actividad a realizar" (texto libre) |
| `tipo_solicitud` | `varchar(30)` | NO | default `reserva_en_laboratorio`, CHECK `reserva_en_laboratorio`/`reserva_fuera_laboratorio` (`ck_reservas_tipo_solicitud`); `orden_salida` existe en el enum `TipoSolicitud` pero **no** está en el CHECK todavía — se agregará en Fase C cuando `services/solicitudes.py` materialice filas reales con ese valor |
| `motivo_solicitud_id` | `FK motivos_solicitud.id` | SÍ | nullable, reemplaza progresivamente `tipo_solicitud` (dropdown por laboratorio) |
| `ubicacion_uso` | `varchar(200)` | SÍ | solo cuando `tipo_solicitud=reserva_fuera_laboratorio` **o** `motivo_solicitud.codigo=reserva_fuera_laboratorio` (validado en `services/reservas.py`) |
| `requiere_apoyo_auxiliar` | `boolean` | NO | default false (pregunta 18 del formulario real) |
| `propuesta_motivo` / `propuesta_horarios` / `propuesta_por` / `propuesta_en` | `text` / `text` / `varchar(20) CHECK tecnico/usuario` / `timestamptz` | SÍ | Fase C (propuesta/contrapropuesta) — queda `esperando` con bloque activo, `NULL` = sin propuesta |
| `recordatorio_enviado_en` | `timestamptz` | SÍ | marca idempotente de `services/recordatorios.py` |
| `created_at` / `updated_at` | `timestamptz` | NO | |

Índices y exclusión:
- `ix_reservas_recurso_fecha_estado (recurso_id, fecha, estado)` y `ix_reservas_recurso_id`.
- `EXCLUDE USING gist (recurso_id WITH =, fecha WITH =, tsrange(fecha+hora_inicio, fecha+hora_fin, '[)') WITH &&) WHERE (estado IN ('esperando','aprobada'))` (`reservas_sin_solapamiento`, `btree_gist`) — evita solapamiento **inclusive** en el recurso ancla. Las tablas de asociación tienen sus propios `EXCLUDE` equivalentes (`reserva_recursos_sin_solapamiento`, `reserva_espacios_sin_solapamiento`, `migrations.py:_CONSTRAINTS_EXCLUDE_RESERVA_ASOCIACIONES`).

Relaciones ORM: `reservas.tipo_reserva` (`TipoReserva`), `reservas.recursos_asociados`/`espacios_asociados`/`espacios` (viewonly)/`acompanantes` (all con `cascade="all, delete-orphan"` + `passive_deletes=True`).

### `personal` vs `usuarios`

Separados en tablas reales (2026-08-28, `backend/app/models/personal.py:9`).

**`personal`** — `admin`/`gestor` exclusivamente (`CHECK rol IN ('admin','gestor')`, `ck_personal_rol`):
`id`, `username`/`email` únicos, `supabase_id UUID unique`, `rol`, `documento_identificacion`/`telefono`/`institucion`/`vinculacion`/`dependencia` (perfil A2, nullable), `created_at`/`updated_at`. Sin `hashed_password`/`debe_cambiar_password` (vestigio no arrastrado).

**`usuarios`** — solo rol `usuario` en la práctica (`rol default usuario`; filas `admin`/`gestor` fueron borradas tras copiar a `personal`, `migrations.py:_BORRAR_ADMIN_GESTOR_DE_USUARIOS`):
`id`, `username`/`email` únicos, `hashed_password`, `debe_cambiar_password boolean default false` (vestigial), `supabase_id UUID unique`, mismos 5 campos de perfil A2, `created_at`/`updated_at`, `rol` (siempre `usuario`). Property `usuario.espacio` siempre `None` (solo `Personal` tiene laboratorio asignado).

Migración preserva `id` al copiar (`ON CONFLICT DO NOTHING` + `setval`), así que las FK existentes no se reescriben — solo se repuntan las constraints (`recursos.created_by`/`update_by`, `espacios.created_by`, `laboratorios.created_by`, etc. → `personal.id`).

### `usuarios_laboratorios` — asignación gestor→laboratorio

Pese al nombre (no se renombró la columna `usuario_id` para no ampliar la superficie), `usuario_id` apunta a `personal.id` (solo `Personal` gestor tiene laboratorio). `id PK`, `usuario_id FK personal.id NOT NULL`, `laboratorio_id FK laboratorios.id NOT NULL`, `UNIQUE(usuario_id)` (`uq_usuarios_laboratorios_usuario`) — un gestor administra **como máximo** un laboratorio. Tabla renombrada desde `usuarios_espacios` (columna `espacio_id→laboratorio_id`).

## Tablas de asociación

### `espacio_recursos` — Espacio↔Recurso (N:N técnico)

`id PK`, `espacio_id FK espacios.id CASCADE NOT NULL` (`index`), `recurso_id FK recursos.id CASCADE NOT NULL`, `UNIQUE(recurso_id)` (`uq_espacio_recursos_recurso`) — un recurso pertenece **como máximo** a un espacio. Renombrada desde `zona_recursos` (`zona_id→espacio_id`). Escritura solo por `PUT /espacios/{id}/recursos` (reemplazo completo).

### `reserva_recursos` / `reserva_espacios` — Reserva↔Recurso / Reserva↔Espacio (N:N, desnormalizados)

Islas creadas por `Base.metadata.create_all()`; backfill desde `reservas.recurso_id` (`migrations.py:_BACKFILL_RESERVA_RECURSOS`, gate `reservas sin fila asociada`).

**`reserva_recursos`**: `id PK`, `reserva_id FK reservas.id CASCADE NOT NULL index`, `recurso_id FK recursos.id NOT NULL index`, `fecha`, `hora_inicio`, `hora_fin`, `estado` (todos desnormalizados desde `Reserva` para que el `EXCLUDE gist` no necesite JOIN), `UNIQUE(reserva_id, recurso_id)`, `EXCLUDE reserva_recursos_sin_solapamiento` (mismo predicado que `reservas`).

**`reserva_espacios`**: `id PK`, `reserva_id FK reservas.id CASCADE`, `espacio_id FK espacios.id NOT NULL`, `fecha`, `hora_inicio`, `hora_fin`, `estado`, `UNIQUE(reserva_id, espacio_id)`, `EXCLUDE reserva_espacios_sin_solapamiento`. Renombrada desde `reserva_zonas` (`zona_id→espacio_id`).

### `reserva_acompanantes` — acompañantes por reserva

`id PK`, `reserva_id FK reservas.id CASCADE NOT NULL index`, `nombre varchar(150) NOT NULL`, `correo varchar(255) NOT NULL`, `UNIQUE(reserva_id, correo)` (`uq_reserva_acompanantes_correo`).

## Dos ejes independientes en `Reserva` — `tipo_reserva_id` vs `tipo_solicitud`

> **Son conceptos distintos con nombres parecidos. No son intercambiables y no se derivan uno del otro.**

| Eje | Columna | Tipo de dato | Obligatorio | Valores | Origen | Pregunta que responde |
|---|---|---|---|---|---|---|
| **Tipo de reserva académica** | `reservas.tipo_reserva_id` → `tipos_reserva.id` | FK catálogo **por laboratorio** | **Opcional** (`NULL` = "Sin especificar") | Los que cada laboratorio defina (`UNIQUE(laboratorio_id, nombre)`), p.ej. "Investigación", "Clase demostrativa", "Préstamo inter-sede". Antes era el enum fijo `TipoReserva` (`trabajo_investigacion`/`trabajo_grado`/`servicio_de_ensayo`, hoy conservado solo como `reservas.tipo` legado). | Usuario elige en el dropdown del sheet (`tiposReservaProvider(laboratorioId)`) — si el laboratorio no definió ninguno, el campo ni se muestra. | **¿Qué actividad académica origina la reserva?** |
| **Motivo de la solicitud** | `reservas.tipo_solicitud` | `varchar(30)` con `CHECK` | **Obligatorio** (default `reserva_en_laboratorio`, backfill cubre filas viejas) | `reserva_en_laboratorio` (dentro del laboratorio, modelo de siempre) / `reserva_fuera_laboratorio` (equipo usado fuera del laboratorio pero dentro de la sede). `orden_salida` (equipo fuera de la sede, rango de días) y `mano_obra` (vive solo en `solicitudes_especiales`, nunca en `reservas`) pertenecen al mismo formulario real pero **no** son valores de esta columna hoy — `orden_salida` se agregará al CHECK en Fase C. | Se elige en `_MotivoSolicitudDialog` (pregunta 11 del formulario real del ITM, `EspacioDetalleScreen` → `LaboratorioReservaSheet` con `tipoSolicitud` prefijado). | **¿Dónde y bajo qué figura se solicita el recurso?** |

Notas:

- Una reserva puede ser a la vez `tipo_solicitud=reserva_fuera_laboratorio` (requiere `ubicacion_uso`) y `tipo_reserva_id=5` ("Trabajo de grado") — la combinación es válida y ortogonal.
- `reserva.tipos` histórico (`reservas.tipo`, `backend/app/domain/enums.py:28 TipoReserva`) no se lee ni escribe en código nuevo; queda como dato histórico inerte (mismo criterio que `serie_id`/`ensayos`). No hacer `DROP COLUMN` sin confirmación explícita aparte.
- En el enum `TipoSolicitud` (`backend/app/domain/enums.py:45`, `app_flutter/lib/core/domain/enums.dart:TipoSolicitud`) `ORDEN_SALIDA` ya existe para no reabrir el `CHECK` dos veces, pero nunca llega desde `ReservaCreate` — el servicio lo rechaza con 422 si llegara (solo `services/solicitudes.py` Fase C lo materializará día por día).

## Otras tablas (resumen)

- **`tipos_recursos`** ya descrita; **`recursos`** con `placa UNIQUE`.
- **`notificaciones`** — `id`, `usuario_id`/`personal_id` polimórfico (`ck_notificaciones_actor_unico`), `reserva_id FK`, `tipo` CHECK `Pendiente/Aprobada/Rechazada/Cancelada/Actualizada` (capitalizados), `leida boolean`, `created_at`.
- **`control_cambios`** — auditoría `usuario_id`/`personal_id` (`ck_control_cambios_actor_unico` permite ambos `NULL` por `ON DELETE SET NULL`), `accion`, `descripcion` (inyecta `motivo_rechazo` cuando aplica), `created_at`.
- **`lista_espera`** — `recurso_id`, `usuario_id`/`personal_id` polimórfico, `fecha`, `hora_inicio`/`hora_fin`, `estado` CHECK `activa`/`notificada`/`cancelada`/`expirada`, `notificada_en timestamptz`.
- **`correo_saliente`** — outbox (`destinatario`, `asunto`, `cuerpo`, `es_html boolean default false`, adjunto `adjunto_nombre`/`content_type`/`contenido TEXT` para `.ics`, `created_at`, `enviado_en`).
- Tablas legacy huérfanas **sin uso** que se conservan sin `DROP` hasta confirmación explícita: `ensayos`, `reserva_ensayos` (Fase 1), y las columnas `reservas.serie_id` / `reservas.tipo` (Fases 2/7).

## Referencias

- Código: `backend/app/models/*.py`, `backend/app/domain/enums.py`, `backend/app/migrations.py`, `app_flutter/lib/features/laboratorios/` / `espacios/` / `tipos_reserva/`.
- Docs: `backend/CLAUDE.md`, `app_flutter/CLAUDE.md`, `backend/tests/CLAUDE.md`, `README.md`, `CHANGELOG.md`.

> Cualquier cambio que toque `CHECK`/`EXCLUDE`/`FK`/`UNIQUE` aquí debe replicarse en `migrations.py` con el patrón idempotente del proyecto y probarse primero contra `reservas_test` (nunca `reservas_db`), preferentemente en un `SCHEMA` descartable (`CREATE SCHEMA proof_xxx` + `DROP SCHEMA … CASCADE`) como en `backend/tests/test_migrations_rollback_12c4e.py`.
