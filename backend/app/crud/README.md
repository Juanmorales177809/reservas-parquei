# crud

## Propósito

Consultas de persistencia SQLAlchemy. La lógica de negocio vive en `services/`; esta capa solo construye, lee y actualiza filas.

## Cambios realizados

| Archivo | Acción | Descripción |
|---|---|---|
| espacios.py | Modificado | `create_espacio` construye el horario por defecto con `HorarioAtencion` (validación de dominio) y lo serializa al formato exacto que ya se persistía: `{"0": [7..19], ..., "5": [7..19]}` |
| espacios.py | Modificado (Fase 12B) | `create_espacio` propaga `modalidad_reserva` y `correo` del payload al modelo |
| zonas.py | Nuevo (Fase 12C-2) | `get_zona`, `create_zona` (fija `created_by`/`updated_by` desde el usuario autenticado), `update_zona` (aplica un dict de cambios ya validado/filtrado por `api/zonas.py` y refresca `updated_by`). Sin función de listado — ver `backend/app/api/README.md`, Fase 12C-2 |
| zonas.py | Modificado (Fase 12C-3) | Agrega `reemplazar_recursos_de_zona`: diff completo (quitar/agregar) de `zona_recursos` para una zona, con `try/except IntegrityError` que traduce un conflicto de la `UniqueConstraint` a `HTTPException(409)` — red de seguridad ante condición de carrera, mismo patrón que `services/reservas.py::_traducir_error_integridad` |
| reservas.py | Modificado (Fase 12C-5) | `get_reservas_bloqueantes` pasa a hacer JOIN contra `reserva_recursos` (consulta por recurso, con `distinct`); nuevo `get_recurso_ids_reserva` para resolver los recursos de una reserva desde la asociación |
| reservas.py | Modificado (Fase 12C-6) | Nuevos `get_zona_ids_reserva` y `get_zonas_bloqueantes` (espejo de los de recurso contra `reserva_zonas`); los getters de listado/individual (`get_reservas`, `get_reservas_gestion`, `get_mis_reservas`, `get_reserva`) enriquecen la respuesta con los conjuntos desde las asociaciones (`_enriquecer_con_asociaciones` + `_OPTIONS_CARGA`) |
| reservas.py | Modificado (Fase 12C-4e-lectores/schemas) | `_OPTIONS_CARGA` cambia `joinedload(Reserva.recurso)` por `joinedload(Reserva.recursos_asociados).joinedload(ReservaRecurso.recurso)`; `_enriquecer_con_asociaciones` deja de resolver/asignar el ancla singular (`reserva.recurso`) y solo puebla `reserva.recursos` (lista de `Recurso` completos) además de `recurso_ids`/`zona_ids` |

## Reglas de negocio relacionadas

- ➕ Horario de atención por día: el espacio nuevo nace con atención 07:00–19:00 de lunes a sábado (mismo valor que antes).
- RN-006 / RN-007 (Fase 12B): modalidad y correo del espacio, persistidos al crear.
- RN-011 / RN-016 (Fase 12C-2, parcial): persistencia de `Zona` aislada.
- RN-011 / RN-016 (Fase 12C-3): persistencia del reemplazo de `zona_recursos`.

## Decisiones técnicas

- El value object del dominio valida el horario antes de persistirlo; la serialización `{str(dia): list}` conserva el formato de la DB (claves string del JSON).
- Fase 12B: `update_espacio` no requirió cambios — ya usa `data.model_dump(exclude_unset=True)` genérico, que recoge `modalidad_reserva`/`correo` automáticamente cuando el schema los valida.
- Fase 12C-2: `update_zona` recibe un `dict` de cambios ya filtrado (no el schema `ZonaUpdate` directo), a diferencia de `update_espacio`. Motivo: `api/zonas.py` necesita eliminar `espacio_id` de los cambios cuando quien edita es un gestor (no puede mover una zona fuera de su espacio) antes de aplicar nada — esa decisión de autorización vive en la capa de API, no en `crud/`, así que `update_zona` recibe el resultado ya resuelto.
- Fase 12C-3: `reemplazar_recursos_de_zona` calcula el diff (`actuales - recurso_ids` para quitar, `recurso_ids - actuales` para agregar) en Python, no en SQL — el volumen esperado por zona es pequeño y la legibilidad del diff explícito pesó más que optimizar una consulta de conjunto en la base. Todas las validaciones de negocio (existencia, pertenencia al espacio, conflicto con otra zona) ya se resolvieron en `api/zonas.py` antes de llamar a esta función; el `try/except IntegrityError` aquí es puramente una red de seguridad ante una condición de carrera real, no la vía principal de validación.

### Fase 12C-5 — Lectura interna desde las asociaciones

- **`get_reservas_bloqueantes` migrada a JOIN contra `reserva_recursos`**: la consulta por recurso filtra por las columnas desnormalizadas de la asociación (`ReservaRecurso.recurso_id/fecha/hora_inicio/hora_fin/estado`) — exactamente los mismos campos y estados que las constraints `reservas_sin_solapamiento` y `reserva_recursos_sin_solapamiento` — y aplica `distinct()` para no duplicar una reserva con varias filas asociadas. Ya no depende de `Reserva.recurso_id`. El `exclude_id` conserva su contrato.
- **`get_recurso_ids_reserva(reserva_id)` (nuevo)**: resuelve los recursos de una reserva desde `reserva_recursos` (con `distinct`), para que `services/reservas.py` lea el recurso actual de una reserva desde la asociación y no desde la columna histórica.
- **Compatibilidad**: para los flujos legítimos (doble escritura 12C-4d y backfill 12C-4b) columna y asociación son idénticas, así que los resultados son los mismos que antes. Las respuestas públicas siguen construyéndose con `Reserva.recurso` (forma singular) — los getters de listado/individual (`get_reservas`, `get_reservas_gestion`, `get_mis_reservas`, `get_reserva`) no se tocan.
- **Impacto colateral esperado**: `api/recursos.py::obtener_disponibilidad_recurso` delega en `get_reservas_bloqueantes`, así que migra automáticamente (por recurso) sin tocar `api/`. El dashboard (`api/admin_dashboard.py`) y las notificaciones (`api/notificaciones.py`) siguen leyendo la columna/relación histórica — fuera de alcance de esta subfase, coherentes para datos singulares.

### Fase 12C-6 — Lectura de los conjuntos desde las asociaciones

- **`_enriquecer_con_asociaciones`**: adjunta `reserva.recurso_ids`/`reserva.zona_ids` como atributos de instancia (no columnas), ordenados de forma estable, para que `ReservaResponse` los serialice — la respuesta es **aditiva**: el singular `Reserva.recurso`/`recurso_id` sigue leyéndose de la columna ancla.
- **`get_zona_ids_reserva`/`get_zonas_bloqueantes` (nuevos)**: espejo de `get_recurso_ids_reserva`/`get_reservas_bloqueantes` contra `reserva_zonas` (la misma tabla de la constraint `reserva_zonas_sin_solapamiento`), con `distinct()` para reservas multi-zona. El servicio los usa para validar el solapamiento de zonas y resolver las zonas actuales de una reserva.
- **Listados con `joinedload`**: `_OPTIONS_CARGA` precarga `recursos_asociados`, `zonas_asociadas` y la relación many-to-many `zonas` (más la cadena `recurso.espacio`) para evitar N+1 al construir la respuesta enriquecida.

### Fase 12C-4e-lectores/schemas — Retiro del singular en la respuesta

- **`_OPTIONS_CARGA` deja de precargar `Reserva.recurso`**: la cadena `joinedload(Reserva.recursos_asociados).joinedload(ReservaRecurso.recurso).joinedload(Recurso.espacio)` reemplaza a `joinedload(Reserva.recurso).joinedload(Recurso.espacio)` — la misma fuente (`reserva_recursos`) que ya alimentaba `recurso_ids` ahora también resuelve los objetos completos de `recursos`.
- **`_enriquecer_con_asociaciones` simplificada**: ya no resuelve ni asigna `reserva.recurso` (el ancla) — ese paso quedó sin consumidor tras retirar `recurso_id`/`recurso` de `ReservaResponse` (12C-4e-schemas, ver `backend/app/schemas/README.md` y `backend/app/api/README.md`). Solo puebla `reserva.recurso_ids`, `reserva.recursos` (lista de `Recurso`, no solo el ancla) y `reserva.zona_ids`.
- **`Reserva.recurso` (relación ORM) y `Reserva.recurso_id` (columna) no se tocan** a nivel de modelo — siguen intactos para el ancla histórica, la EXCLUDE `reservas_sin_solapamiento` y un eventual rollback; simplemente esta capa deja de leerlos para la respuesta pública.

## Pruebas

- Cubierto por `tests/test_api_espacios.py` (creación de espacios) y `tests/test_schemas_contrato.py`.
- Fase 12B: `tests/test_api_espacios.py::TestModalidadYCorreo`.
- Fase 12C-2: `tests/test_api_zonas.py` (33 tests, cubre `crud/zonas.py` indirectamente vía la API).
- Fase 12C-3: `tests/test_api_zonas_recursos.py` (12 tests, cubre `reemplazar_recursos_de_zona` indirectamente vía la API) + `tests/test_models_zona_recurso.py` (5 tests, ejercita la `UniqueConstraint` directamente contra el modelo).
- Fase 12C-5: `tests/test_crud_reservas_lectura_asociaciones.py` (10 tests, cubre `get_reservas_bloqueantes`, `get_recurso_ids_reserva`, la re-lectura de `services/reservas.py` y la compatibilidad de listados/backfill).
- Fase 12C-6: `tests/test_reservas_zonas.py` (nuevo, cubre `get_zonas_bloqueantes` y el contrato plural vía API), `tests/test_dashboard_recursos_efectivos.py` (nuevo) y la extensión de `tests/test_crud_reservas_lectura_asociaciones.py`/`tests/test_api_reservas.py` al payload plural. Suite completa **482/482**.
- Fase 12C-4e-lectores/schemas: `tests/test_reserva_response_sin_singular.py` (integración `get_reserva()` + `ReservaResponse.model_validate()`, un recurso/varios recursos/solo-zona/mixta/no-expone-campos-singulares), `tests/test_crud_reservas_lectura_asociaciones.py::TestCompatibilidadListados` (las aserciones `.recurso.id` verifican la relación ORM directa, no la respuesta pública). Suite completa **525/525**.

## Impacto y compatibilidad

- Ningún cambio observable: el dict persistido es idéntico al anterior.
- Fase 12B: espacios creados antes de esta fase no se ven afectados (columnas nuevas con default/backfill, ver `backend/app/models/README.md`).
- Fase 12C-2: archivo nuevo, sin impacto en `crud/espacios.py`, `crud/reservas.py` ni `crud/usuarios.py`.
- Fase 12C-3: sin impacto en `crud/espacios.py`, `crud/reservas.py` ni ningún módulo de `Recurso` (no existe `crud/recursos.py` — la persistencia de `Recurso` vive inline en `api/recursos.py`, sin cambios).
- Fase 12C-5: la lectura por recurso y la resolución del recurso actual de una reserva pasan a `reserva_recursos`; sin cambio de contrato público ni de esquema.
- Fase 12C-6: `ReservaResponse` gana `recurso_ids`/`zona_ids`/`zonas` desde las asociaciones (aditivo); sin cambio de esquema, rutas ni semántica pública para datos legítimos. `Reserva.recurso_id` sigue presente como ancla (12C-4e).
- Fase 12C-4e-lectores/schemas: cambio de contrato aprobado y regenerado en `ReservaResponse` (retira `recurso_id`/`recurso`, agrega `recursos`) — ver `backend/app/api/README.md`. Sin cambio de esquema de base de datos, rutas, ni otros schemas. `reservas.recurso_id` (columna), `Reserva.recurso` (relación ORM), `reservas_sin_solapamiento` e índices históricos no se tocan.

## Riesgos

- Ninguno.
- Fase 12C-2: ninguno funcional — ver Riesgos en `backend/app/api/README.md`, Fase 12C-2.
- Fase 12C-3: ninguno funcional — ver Riesgos en `backend/app/models/README.md`, Fase 12C-3 (guard pendiente en `api/recursos.py`, fuera de alcance).
- Fase 12C-5: los guard de `api/recursos.py` (`recurso.reservas` para mover/eliminar) siguen leyendo la columna histórica — gap conocido para 12C-6; la lectura por recurso del dashboard también (fuera de alcance). Ambos coherentes para datos singulares.
- Fase 12C-6: resuelto el gap de 12C-5 — `api/recursos.py::_recurso_tiene_reservas` consulta `reserva_recursos` **y** la columna histórica (ancla de zona sin recursos). Ningún riesgo funcional nuevo en esta capa.
- Fase 12C-4e-lectores: `_recurso_tiene_reservas` deja de consultar la columna histórica como fallback — un recurso "ancla" de una zona sin recursos ya no lo detecta este guard; sigue bloqueado por la FK real de `reservas.recurso_id` (traducida a 409 en `api/recursos.py`, ver `backend/app/api/README.md`).

## Pendientes

- ~~Fase 12C-4e-lectores: lectores de CRUD/frontend migrados a las asociaciones.~~ **Hecho.**
- ~~Fase 12C-4e-schemas: retiro de `recurso_id`/`recurso` de `ReservaResponse`, adición de `recursos`.~~ **Hecho** — `tests/openapi.snapshot.json` regenerado.
- **Retiro de la columna `reservas.recurso_id`, la relación `Reserva.recurso`, `reservas_sin_solapamiento` e índices históricos (no iniciado)**: solo al cierre de toda la transición, requiere aprobación explícita y ejecución de DDL (fuera de alcance de 12C-4e-schemas).

## Fase de implementación

Fase 3 (integración de la capa de dominio). Fase 12B (`modalidad_reserva`, `correo`). Fase 12C-2 (`crud/zonas.py`). Fase 12C-3 (`reemplazar_recursos_de_zona`). Fase 12C-5 (lectura desde `reserva_recursos`). Fase 12C-6 (lectura de conjuntos desde las asociaciones). Fase 12C-4e-lectores/schemas (retiro del singular en la respuesta pública).
