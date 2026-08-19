# services

## Propósito

Reglas de negocio de la aplicación: validaciones de reserva, horarios, hora local de negocio y auditoría. Tras la Fase 3, esta capa consume los enums, value objects y protocols de `app/domain/` sin cambiar los contratos de la API.

## Cambios realizados

| Archivo | Acción | Descripción |
|---|---|---|
| reloj.py | Modificado | Nueva clase `RelojLocal` que implementa el protocolo `Reloj` (datetime NAIVE en `APP_TIMEZONE`); `ahora_local()` queda como wrapper de compatibilidad |
| horarios.py | Modificado | `horas_atencion_dia` y `horario_cubre_reserva` delegan en `HorarioAtencion`/`FranjaHoraria` con guard explícito para horario vacío |
| reservas.py | Modificado | `TRANSICIONES_ESTADO` duplicado eliminado → `EstadoReserva.puede_transicionar_a()`; `validar_anticipacion` acepta `Reloj` inyectable (default `RelojLocal`); literales de estado/rol/notificación reemplazados por enums usando siempre `.value` |
| reservas.py | Modificado (Fase 12B) | Nueva `validar_acceso_ps(recurso, usuario)`, invocada desde `validar_creacion` (POST) y `actualizar_reserva` (PATCH, al cambiar de recurso) |
| reservas.py | Modificado (Fase 12C-4d) | Doble escritura controlada de `reserva_recursos` para reservas singulares: `_sincronizar_reserva_recurso()` crea o actualiza la única fila por reserva al crear/modificar recurso, fecha, horas o estado; `_es_conflicto_solapamiento` ampliado a la constraint nueva `reserva_recursos_sin_solapamiento` |
| reservas.py | Modificado (Fase 12C-5) | La lectura interna del recurso actual de una reserva pasa a la asociación: `_recurso_id_reserva()` resuelve desde `reserva_recursos` (vía `crud::get_recurso_ids_reserva`) en `cambiar_estado` (chequeo de solapamiento al aprobar) y `actualizar_reserva` (recurso actual cuando no se cambia) |
| auditoria.py | Modificado | Nueva `AuditoriaSesion` (adaptador de `RegistroAuditoria`, solo primitivas); `registrar_cambio()` conservado como wrapper |
| reservas.py | Modificado (Fase 12C-6) | Contrato plural: `validar_creacion` reemplazada por `_validar_objetivo`; nueva maquinaria `_resolver_objetivo`/`_resolver_efectivos`/`_capacidad_efectiva`/`_recurso_ancla`/`_validar_solapamiento_efectivos`/`_reescribir_asociaciones`/`_sincronizar_campos_asociaciones`/`_etiqueta_objetivo`; `crear_reserva`, `actualizar_reserva`, `cambiar_estado` y `cancelar_reserva_usuario` migrados a ejes; `_recurso_id_reserva` (12C-5) retirada en favor de `crud::get_recurso_ids_reserva`/`get_zona_ids_reserva` |

## Reglas de negocio relacionadas

- RN-017, RN-019, RN-020, RN-021: ciclo de aprobación → `EstadoReserva`/`TipoNotificacion` (mensajes y estados idénticos a los actuales).
- RN-005 / RN-008 (análogos): estado activo → `EstadoEntidad.ACTIVO.value`.
- Recomendación 11.2 del documento (auditoría) → `AuditoriaSesion`.
- Reglas adicionales del código: bloques de hora completa, anticipación mínima (reloj inyectable), horario de atención por día.

## Decisiones técnicas

- **`Reloj` inyectable**: `validar_anticipacion(..., reloj: Reloj | None = None)` usa `RelojLocal()` por defecto. `ahora_local()` se conserva como wrapper porque `api/espacios.py` y `api/recursos.py` lo importan.
- **Guard de horario vacío**: un `horario_atencion` totalmente vacío devuelve `[]`/`False` (comportamiento actual conservado). Un horario con horas fuera de 0..22 se deja propagar como error de configuración (no se oculta).
- **`.value` en comparaciones y mensajes**: `str(miembro_de_enum)` difiere entre Python 3.10 (imagen Docker) y 3.11+ (local), así que los mensajes de error y las comparaciones contra columnas de la DB usan siempre `.value`.
- **Adaptador de auditoría**: el protocolo del dominio solo maneja primitivas; `AuditoriaSesion` crea la fila `ControlCambio` y el commit sigue siendo responsabilidad del flujo, igual que antes.

### Fase 12B — `validar_acceso_ps`

- **RN-009**: 403 si `recurso.es_prestacion_servicio` es verdadero y `usuario.rol == Rol.USUARIO.value`. `gestor`/`admin` no están restringidos en esta fase (no hay todavía un tipo de reserva "servicio de ensayo" que condicione su acceso, ver Fase 12D).
- **Punto de extensión explícito para la Fase 12D**: la función queda documentada en su propio docstring como el lugar donde 12D debe agregar el chequeo de tipo de reserva ("servicio de ensayo"), como una validación adicional — sin tocar ni duplicar este gate de rol.
- **Reutilizada en dos flujos**: `validar_creacion` (creación de reserva, `POST /reservas`) y `actualizar_reserva` (edición, `PATCH /reservas/{id}`, cuando el cambio incluye un nuevo `recurso_id`) — una sola función, sin duplicar la regla.

### Fase 12C-4d — Doble escritura controlada de `reserva_recursos`

- **Alcance**: `reserva_recursos` se escribe desde `services/reservas.py` **únicamente** para reservas singulares (una fila por reserva, sincronizando `recurso_id`, `fecha`, `hora_inicio`, `hora_fin` y `estado`). Los consumidores siguen leyendo desde el esquema histórico (`Reserva.recurso`/`Reserva.recurso_id`). NO se habilita multi-recurso ni reservas solo por zona; `reserva_zonas` no se escribe. Sin cambios en schemas, rutas, OpenAPI, models, migraciones ni frontend.
- **Puntos de escritura**: `crear_reserva` (tras el `flush` de `preparar_reserva`, para tener el id), `actualizar_reserva`, `cambiar_estado` y `cancelar_reserva_usuario` (siempre antes de `confirmar_cambios_reserva`). `eliminar_reserva` no requiere cambio: `reserva_recursos.reserva_id` lleva `ON DELETE CASCADE`.
- **Quién es dueño de commit/rollback**: el flujo de servicio, exactamente igual que antes — `preparar_reserva`/`confirmar_cambios_reserva` hacen flush/commit y `_traducir_error_integridad` hace `rollback` + `HTTPException(409)`. `_sincronizar_reserva_recurso` **nunca** hace commit ni rollback: ante un `IntegrityError` en el commit (p. ej. la constraint `reserva_recursos_sin_solapamiento`), la transacción se revierte completa — reserva y fila asociada como una sola unidad, sin filas parciales.
- **Invariante de unicidad**: `_sincronizar_reserva_recurso` consulta primero por `reserva_id`; si la fila ya existe (p. ej. reserva histórica backfillada en 12C-4b) la actualiza, nunca la duplica. Una reserva con `recurso_id` siempre tiene exactamente una fila en `reserva_recursos`.
- **Solapamientos**: el 409 clásico lo sigue produciendo la validación de servicio contra `reservas` y/o la constraint histórica `reservas_sin_solapamiento`. La constraint nueva `reserva_recursos_sin_solapamiento` (12C-4c) queda activa y su `IntegrityError` también se traduce a 409 (ampliación de `_es_conflicto_solapamiento`), cubriendo los casos en que el conflicto existe solo en la tabla de asociación (p. ej. una fila manual sin equivalente en `reservas`).

### Fase 12C-5 — Lectura interna desde la asociación

- **`validar_solapamiento`** sigue siendo la misma (delega en `crud::get_reservas_bloqueantes`, que ya hace JOIN contra `reserva_recursos`), así que al crear, actualizar o aprobar una reserva el solapamiento se valida contra la asociación, no contra la columna histórica.
- **`_recurso_id_reserva(db, reserva)` (nuevo)**: resuelve el recurso actual desde `reserva_recursos` para los flujos que necesitan saber en qué recurso vive la reserva (chequeo de solapamiento al aprobar en `cambiar_estado`; recurso actual en `actualizar_reserva` cuando el payload no incluye `recurso_id`). Exige exactamente una fila/recurso (invariante de 12C-4d): si la invariante está rota (ninguna fila o varias con recursos distintos), falla de forma ruidosa (`RuntimeError`) en vez de leer la columna histórica.
- **La doble escritura se mantiene intacta** (`_sincronizar_reserva_recurso` sigue escribiendo la asociación desde `reserva.recurso_id`): solo cambia la *lectura* interna. El dueño de commit/rollback no cambia (el flujo de servicio).
- **Actualizado en 12C-6**: `_recurso_id_reserva` (la función de esta subfase) **fue retirada** — la resolución pasa a llamar directo a `crud::get_recurso_ids_reserva` (y el nuevo `get_zona_ids_reserva` para zonas). `validar_solapamiento` queda sin referencias (era el punto de entrada del flujo singular, reemplazado por `_validar_solapamiento_efectivos`); `validar_recurso_activo`/`validar_capacidad` se conservan solo por los tests unitarios que las ejercitan directamente.

### Fase 12C-6 — Servicio de reservas plural (ejes y efectivos)

- **`_resolver_objetivo` (nuevo)**: resuelve y valida el conjunto objetivo de una reserva en un solo lugar. Aplica el **gate de modalidad** (`equipos` rechaza `zona_ids` con 400; `zonas` rechaza `recurso_ids`; `mixto` admite ambos), exige que **todos los recursos y zonas pertenezcan al mismo espacio** (en edición, `espacio_id_fijo=reserva.espacio_id` valida pertenencia — 403 para gestor/admin, 400 para el resto), valida **actividad** de zonas, recursos directos y recursos efectivos, y aplica `validar_acceso_ps` a cada recurso efectivo.
- **Materialización zona → recursos efectivos**: los efectivos son la unión de los recursos directos y los miembros de cada zona (`_miembros_zona` vía `zona_recursos`), sin duplicados y en orden estable por id. Toda reserva de zona materializa sus recursos en `reserva_recursos` — por eso el cruce zona↔recurso queda cubierto por la misma tabla en el solapamiento.
- **Zona sin recursos permitida**: una zona sin miembros produce cero recursos efectivos y es válida como objetivo. Para conservar la columna `NOT NULL` `Reserva.recurso_id` (migraciones congeladas), el **ancla** (`_recurso_ancla`) es el recurso efectivo de menor id; si no hay efectivos, el recurso de menor id del espacio; si el espacio no tiene recursos, la reserva es irrepresentable y responde 400. **Riesgo residual documentado**: la EXCLUDE histórica (`reservas_sin_solapamiento` sobre la columna ancla) puede, en ese caso extremo, chocar con una reserva directa del recurso ancla — verificado y documentado en `tests/test_reservas_zonas.py`.
- **Capacidad efectiva** = `min(espacio, zonas definidas, recursos efectivos)` (decisión aprobada), verificada contra `asistentes` en `_validar_objetivo` (400 si la supera).
- **Solapamiento transitivo** (`_validar_solapamiento_efectivos`): cada recurso efectivo contra `reserva_recursos` (`get_reservas_bloqueantes`) y cada zona contra `reserva_zonas` (`get_zonas_bloqueantes`), con `exclude_id` en edición y al aprobar. La transitividad explícita zona↔recurso no se necesita: una zona reservada ya materializó sus efectivos.
- **`_reescribir_asociaciones`**: borra y recrea las filas de `reserva_zonas`/`reserva_recursos` de la reserva dentro de la misma transacción. Nunca hace commit/rollback (el flujo es dueño, igual que 12C-4d) — sin filas parciales ante un fallo de integridad.
- **`_sincronizar_campos_asociaciones`**: cuando NO cambia el conjunto objetivo (cambiar/cancelar estado), actualiza `fecha`/`hora_inicio`/`hora_fin`/`estado` en las filas existentes de ambas tablas.
- **`_etiqueta_objetivo`**: zona-aware para los mensajes de auditoría ("la zona X y los recursos Y"); `validar_creacion` dejó de existir — los flujos llaman directo a `_resolver_objetivo` (para edición con `espacio_id_fijo`) + `_validar_objetivo`.
- **`actualizar_reserva` con ejes**: un eje ausente conserva su conjunto (`get_recurso_ids_reserva`/`get_zona_ids_reserva`); uno presente lo reemplaza entero. El conjunto recién resuelto no puede quedar vacío (400). La creación sigue auto-aprobando por las dos rutas de RN-021 (flag del espacio o gestor en su espacio), y la aprobación (`cambiar_estado`) re-valida el solapamiento transitivo con los efectivos recién resueltos.

## Pruebas

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest tests/test_reloj.py tests/test_horarios.py tests/test_reservas_validaciones.py tests/test_auditoria_dominio.py -v
.\.venv\Scripts\python.exe -m pytest tests/test_api_reservas.py::TestRecursosPS -v   # Fase 12B
.\.venv\Scripts\python.exe -m pytest tests/test_doble_escritura_reserva_recursos.py -v   # Fase 12C-4d
.\.venv\Scripts\python.exe -m pytest tests/test_crud_reservas_lectura_asociaciones.py -v   # Fase 12C-5
.\.venv\Scripts\python.exe -m pytest tests/test_reservas_zonas.py tests/test_dashboard_recursos_efectivos.py -v   # Fase 12C-6
```

Resultado esperado: verde. El test de anticipación usa `_RelojFijo` en lugar de `monkeypatch`. Fase 12C-6: suite completa **482/482**.

## Impacto y compatibilidad

- API, mensajes, estados y OpenAPI sin cambios (snapshot `openapi.json` verificado byte-idéntico en Fase 3).
- Sin cambios en `api/`, `schemas/`, migraciones ni frontend.
- Fase 12B: `validar_acceso_ps` es aditiva; ninguna reserva de recurso no-PS cambia de comportamiento (`test_reserva_normal_sin_cambios`, ver `backend/tests/test_api_reservas.py`).
- Fase 12C-4d: persistencia aditiva hacia `reserva_recursos`; el contrato de `ReservaCreate`/`ReservaUpdate`/`ReservaResponse` y todo lo que lee desde `Reserva.recurso` quedan sin cambios.
- Fase 12C-5: lectura interna del recurso desde `reserva_recursos`; para datos legítimos (doble escritura/backfill) el resultado es idéntico — sin cambio de comportamiento observable ni de contrato.
- Fase 12C-6: la entrada pasa a ejes plurales (`recurso_ids`/`zona_ids`; `recurso_id` 422) y la respuesta es aditiva — ruptura de contrato aprobada. El 409 del solapamiento puede provenir de cualquiera de las tres constraints EXCLUDE (`_CONSTRAINTS_SOLAPAMIENTO`), todas traducidas al mismo mensaje.

## Riesgos

- Si el dominio cambia la semántica de horarios vacíos o transiciones, esta capa debe re-verificarse (tests de contrato cubren ambos lados).

## Pendientes

- ~~Fase 12C-6: ruptura de contrato de `Reserva`/dashboard/notificaciones~~ **Hecho** — implementado en 12C-6; suite completa 482/482.
- ~~Fase 12C-4e-schemas: retiro del singular (`recurso_id`/`recurso`) de `ReservaResponse`~~ **Hecho** — cambio de contrato en `app/schemas/reserva.py`/`app/crud/reservas.py`, ver `backend/app/api/README.md` y `backend/app/crud/README.md`. Esta capa (`services/reservas.py`) no se tocó: `_recurso_ancla()`, `validar_solapamiento`, `validar_recurso_activo` y `validar_capacidad` siguen sin cambios, igual que `reservas.recurso_id` (columna) y `Reserva.recurso` (relación ORM).
- **Retiro de la columna `reservas.recurso_id` (no iniciado)**: solo al cierre de toda la transición, requiere aprobación explícita y ejecución de DDL.
- **Rollback endurecido de `migrations.py` (pendiente desde 12C-4b)**: script que aborte ante reservas multi-recurso o asociadas solo por zona, en una única transacción, con verificación del esquema final — sigue sin escribirse.
- Limpieza opcional: `validar_solapamiento` quedó sin referencias tras 12C-6 (solo definición); `validar_recurso_activo`/`validar_capacidad` solo las ejercitan los tests unitarios.
- Fase 12D (no iniciada): extender `validar_acceso_ps` (o agregar una validación hermana) con el condicionamiento de tipo de reserva "servicio de ensayo" para recursos PS.

## Fase de implementación

Fase 3 (integración de la capa de dominio). Fase 12B (`validar_acceso_ps`, RN-009). Fase 12C-4d (doble escritura controlada de `reserva_recursos`). Fase 12C-5 (lectura interna desde las asociaciones). Fase 12C-6 (servicio plural: ejes, efectivos, capacidad, solapamiento transitivo).
