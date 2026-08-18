# schemas

## Propósito

Contratos Pydantic de la API FastAPI: modelos de entrada (creación/actualización), de respuesta y de configuración. Tras la Fase 2, los valores de estado y rol están tipados con los enums de `app/domain/enums.py`, conservando exactamente los JSON que ya consumía el frontend.

## Cambios realizados

| Archivo | Acción | Descripción |
|---|---|---|
| usuario.py | Modificado | `rol` pasa de `str`+pattern a `Rol` en `AdminUsuarioCreate`, `UsuarioUpdate` y `UsuarioResponse`. El validador manual de email se conserva |
| reserva.py | Modificado | `estado` pasa de `Literal`+validator manual a `EstadoReserva`; `nuevo_estado` pasa a `Literal[EstadoReserva.APROBADA, RECHAZADA, CANCELADA]` (sigue sin permitir `esperando`); `rol`/`estado` de los sub-modelos de respuesta pasan a `Rol`/`EstadoEntidad`; se eliminó el alias `ReservaEstado` y el validator duplicado `validar_estado` |
| espacio.py | Modificado | `estado` pasa a `EstadoEntidad` en Create/Update/Response; el validador de `horario_atencion` conserva su contrato exacto y agrega validación de respaldo con `HorarioAtencion` (opción A) |
| recurso.py | Modificado | `estado` pasa a `EstadoEntidad` en Create/Update/Response. `TipoRecursoResponse.activo` se conserva como `str` (columna de otro significado, fuera del alcance) |
| notificacion.py | Modificado | `tipo` pasa de `Literal` a `TipoNotificacion` |
| disponibilidad.py | Modificado | `estado` pasa de `str` a `EstadoSlot` |
| espacio.py | Modificado (Fase 12B) | `EspacioCreate`/`Update`/`Response` ganan `modalidad_reserva: ModalidadEspacio` y `correo: str` (obligatorio en Create, opcional en Update/Response); validador manual de formato de correo (mismo patrón que `usuario.py`) |
| recurso.py | Modificado (Fase 12B) | `RecursoCreate`/`Update`/`Response` ganan `es_prestacion_servicio: bool` (default `False`) |
| zona.py | Nuevo (Fase 12C-2) | `ZonaCreate` (`nombre`, `espacio_id` obligatorio, `descripcion`, `capacidad` opcional `>0`, `estado` default `activo`), `ZonaUpdate` (todo opcional, sin `created_by`/`updated_by`), `ZonaResponse` (incluye timestamps y auditoría; sin `recursos` todavía) |
| zona.py | Modificado (Fase 12C-3) | Agrega `ZonaRecursosUpdate` (`recurso_ids: list[int]`, reemplazo completo) y `ZonaRecursosResponse` (`zona_id`, `recurso_ids` resultantes) — deliberadamente separados de `ZonaResponse`, sin ampliar ese contrato |
| reserva.py | Modificado (Fase 12C-6) | Contrato plural aprobado 12C-6: `ReservaCreate`/`ReservaUpdate` pasan a ejes `recurso_ids`/`zona_ids` con `extra="forbid"` — el legacy `recurso_id` se rechaza con 422, no se acepta como alias; `ReservaResponse` aditiva (`recurso_ids`, `zona_ids`, `zonas`), conservando `recurso_id`/`recurso` como forma singular temporal; nuevo `ZonaReservaResponse` |

## Reglas de negocio relacionadas

- RN-003 / RN-004: roles válidos (`usuario`/`gestor`/`admin`) → `Rol`.
- RN-005 / RN-008 (análogos): estados de espacio/recurso → `EstadoEntidad`.
- RN-017 / RN-019..RN-021: estados de reserva y cambios de estado permitidos (sin `esperando` como destino) → `EstadoReserva` + `Literal` de subconjunto.
- Reglas adicionales del código: disponibilidad (`EstadoSlot`), notificaciones (`TipoNotificacion`), horario de atención por día validado con `HorarioAtencion`.

## Decisiones técnicas

- **Enums del dominio** (`str, Enum`, Python 3.10): reemplazan `pattern` y `Literal` donde el resultado JSON/OpenAPI es equivalente. Verificado con snapshot de `openapi.json` antes/después (diff limitado a pattern→enum y Literal→enum).
- **Opción A (compatibilidad de contrato)**: el validador de `ConfiguracionEspacioUpdate.horario_atencion` conserva EXACTAMENTE la salida actual, incluidas las claves de días vacíos con listas `[]` (`{1: [], 2: [9]}` sigue devolviendo `{1: [], 2: [9]}`). `HorarioAtencion` se usa solo como respaldo de invariantes de dominio (claves 0–6, horas 0–22, al menos una franja, orden/dedupe) y NO reemplaza la salida pública: el dominio elimina días vacíos solo en su normalización interna, y `api/espacios.py` filtra posteriormente las listas vacías. La normalización del dominio nunca debe cambiar silenciosamente los JSON de la API.
- **Mensajes de validación**: los 3 mensajes de horario se conservan exactos; los mensajes 422 de rol/estado cambian de "pattern" a "Input should be..." (propio del cambio pattern→enum, documentado).
- **EmailStr descartado en esta fase**: no se añadió la dependencia `email-validator`; el validador manual actual se conserva (ver Pendientes).

### Fase 12B — `Espacio.correo` y `Recurso.es_prestacion_servicio`

- **`EspacioCreate.correo` obligatorio, `EspacioUpdate.correo` opcional**: mismo criterio que RN-007 (correo obligatorio para altas nuevas, decisión 2 de la Fase 12A) sin romper espacios sembrados antes de esta fase (ver `backend/app/models/README.md`).
- **Validador reutilizado, no una dependencia nueva**: `_validar_formato_correo` replica exactamente el patrón ya usado en `UsuarioCreate`/`UsuarioUpdate` (`"@" in value and "." in value.split("@")[-1]`) — mismo criterio "EmailStr descartado" de la Fase 2, no se añadió `email-validator`.
- **`RecursoCreate.es_prestacion_servicio` con default `False`**: compatible con payloads existentes que no incluyen el campo (Fase 12D deberá condicionar su reserva a un tipo de reserva "servicio de ensayo", sin tocar este schema).

### Fase 12C-2 — `schemas/zona.py` (nuevo)

- **`ZonaCreate.espacio_id` obligatorio, sin fallback silencioso**: a diferencia de `RecursoCreate.espacio_id` (opcional, con fallback automático al espacio del gestor en `api/recursos.py`), el contrato de `Zona` exige el campo siempre explícito — la autorización de "gestor limitado a su espacio" se aplica como 403 explícito en `api/zonas.py`, no como sustitución silenciosa.
- **`capacidad: int | None = Field(default=None, gt=0)`**: mismo patrón exacto que `RecursoCreate.capacidad`/`RecursoUpdate.capacidad`, adaptado a nullable porque `Zona.capacidad` es opcional (a diferencia de `Espacio.capacidad`/`Recurso.capacidad`, que son obligatorias) — ver `backend/app/models/README.md`, Fase 12C-1.
- **`created_by`/`updated_by` fuera de `ZonaCreate`/`ZonaUpdate` por diseño**: no se declaran en ningún schema de entrada — Pydantic v2 ignora por defecto cualquier campo extra no declarado en el modelo, así que un payload que los incluya no tiene ningún efecto. Se fijan siempre en `api/zonas.py` desde `current_user.id`.
- **`ZonaResponse` sí expone `created_at`/`updated_at`/`created_by`/`updated_by`**: a diferencia de `EspacioResponse`/`RecursoResponse` (que no exponen ningún campo de auditoría), aquí se incluyen explícitamente por instrucción directa de esta subfase — es una decisión nueva para `Zona`, no un calco de un patrón de respuesta ya existente en el proyecto (no había ninguno idéntico que copiar). `created_by`/`updated_by` se exponen como enteros (FK), sin anidar el objeto `Usuario`.
- **`ZonaResponse` no incluye `recursos` todavía**: `zona_recursos` no existe hasta la Fase 12C-3.

### Fase 12C-3 — `ZonaRecursosUpdate` / `ZonaRecursosResponse`

- **Schemas propios, no una extensión de `ZonaResponse`**: `PUT /zonas/{zona_id}/recursos` responde `ZonaRecursosResponse` (`zona_id`, `recurso_ids`), no `ZonaResponse` con un campo `recursos` agregado — evita ampliar un contrato ya aprobado (12C-2) sin necesidad; el endpoint tiene su propia forma de entrada/salida.
- **`ZonaRecursosUpdate.recurso_ids: list[int] = Field(default_factory=list)`**: lista vacía es un valor válido por defecto (desasocia todo), sin validación de mínimo — coherente con la decisión aprobada "lista vacía permitida".
- **Sin validación de duplicados en la lista de entrada**: el endpoint trata `recurso_ids` como un conjunto (`set(payload.recurso_ids)`) antes de procesar — un cliente que envíe duplicados no obtiene error, simplemente se deduplican. No se invierte en detectar y rechazar esto porque no aporta ninguna protección real (el resultado es idéntico con o sin duplicados).

### Fase 12C-6 — Contrato plural de reserva

- **`ReservaCreate` con `extra="forbid"`**: `recurso_id` y cualquier campo fuera de los ejes se rechazan con **422** (`extra_forbidden`), nunca se aceptan como alias silencioso. Los ejes son `recurso_ids`/`zona_ids` (`list[int]`, default `[]`), con el validator `_al_menos_un_recurso_o_zona` que exige al menos uno. El contrato público deja de aceptar el payload singular histórico.
- **`ReservaUpdate` por ejes de reemplazo completo** (`extra="forbid"`, todo opcional): un eje ausente conserva su conjunto actual; un eje presente reemplaza el conjunto completo de ese eje. La combinación final (ambos ejes, fecha, horas, asistentes) se valida en el servicio (`services/reservas.py::_validar_objetivo`), no en el schema — un payload que deje el conjunto vacío según el estado recién resuelto responde 400 desde el servicio.
- **`ReservaResponse` aditiva, no ruptura**: se agregan `recurso_ids`, `zona_ids` y `zonas` (lista de `ZonaReservaResponse`), poblados desde las tablas de asociación (`crud/reservas.py::_enriquecer_con_asociaciones`). `recurso_id`/`recurso` se conservan como forma singular temporal (ancla) hasta 12C-4e.
- **`ZonaReservaResponse` (nuevo)**: misma base mínima que `ZonaResponse` (`id`, `nombre`, `espacio_id`, `descripcion`, `capacidad`, `estado`) sin timestamps ni auditoría — suficiente para la respuesta de la reserva y los mensajes de notificación.

## Pruebas

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest tests/test_schemas_contrato.py -v
.\.venv\Scripts\python.exe -m pytest -v
```

Resultado esperado: 21 tests de contrato + suite completa en verde (157 en Fase 2). Fase 12B: 318/318 (3 tests de contrato preexistentes actualizados para incluir `correo` en `EspacioCreate`/`EspacioResponse`, ver `tests/test_schemas_contrato.py`). Fase 12C-2: 364/364 (snapshot ya aprobado y regenerado). Fase 12C-3: 382/382 salvo `test_openapi_contrato.py` (rojo esperado, snapshot de esta subfase pendiente de aprobación) — validaciones de `ZonaRecursosUpdate`/`Response` cubiertas indirectamente vía `tests/test_api_zonas_recursos.py`. Fase 12C-6: `tests/test_schemas_contrato.py` extendido al payload plural (`extra="forbid"` + ejes), `tests/test_reservas_zonas.py` (nuevo, cubre el contrato vía API) y suite completa **482/482** (incluye `test_openapi_contrato.py` en verde con el snapshot aprobado y regenerado).

## Impacto y compatibilidad

- JSON de respuestas y peticiones idénticos para datos válidos; sin cambios de campos, rutas ni defaults.
- OpenAPI: `pattern`→`$ref` de enums y nuevos schemas de componentes (`Rol`, `EstadoEntidad`, `EstadoReserva`, `EstadoSlot`, `TipoNotificacion`). Verificado por diff de snapshot.
- Sin cambios en services, models, api, migraciones ni frontend.
- Fase 12B: cambio de OpenAPI aprobado explícitamente — diff del snapshot limitado a `correo`, `modalidad_reserva` (+ el nuevo componente `ModalidadEspacio`) y `es_prestacion_servicio`; ninguna ruta, método ni otro schema tocado (verificado con diff explícito antes de regenerar).
- **Fase 12C-2 — cambio de OpenAPI aprobado y regenerado**: diff limitado a `ZonaCreate`/`ZonaUpdate`/`ZonaResponse` + paths `/zonas`, `/zonas/{zona_id}` (376 líneas insertadas, 0 eliminadas). `tests/openapi.snapshot.json` ya refleja este cambio.
- **Fase 12C-3 — cambio de OpenAPI aprobado y regenerado**: diff limitado a `ZonaRecursosUpdate`/`ZonaRecursosResponse` + path `/zonas/{zona_id}/recursos` (94 líneas insertadas, 0 eliminadas). `tests/openapi.snapshot.json` ya refleja este cambio.
- **Fase 12C-6 — cambio de OpenAPI aprobado y regenerado**: diff verificado antes/después y limitado a los cambios aprobados — `ReservaCreate`/`ReservaUpdate` (`+ additionalProperties: false`, `recurso_id` → ejes `recurso_ids`/`zona_ids`), `ReservaResponse` (+ `recurso_ids`, `zona_ids`, `zonas`; conserva `recurso_id`/`recurso`), nuevo `ZonaReservaResponse`. **Ninguna ruta, método, esquema de seguridad ni otro schema tocado** (578 líneas insertadas, 7 eliminadas). `tests/openapi.snapshot.json` ya refleja este cambio; `test_openapi_contrato.py` verde.

## Riesgos

- Textos de error 422 para valores inválidos de rol/estado cambian de texto (documentado arriba).
- `ReservaResponse.estado` con `EstadoReserva`: si la DB contuviera un valor corrupto, la serialización fallaría (protegido por el CheckConstraint de DB).
- Fase 12B: `EspacioCreate.correo` obligatorio rompe cualquier cliente que cree espacios sin ese campo — confirmado real en `frontend/src/app/admin/espacios/page.tsx` y en `frontend/e2e/tests/smoke/03-admin.spec.ts` (ver Riesgos en `backend/app/models/README.md` y `CHANGELOG.md`).
- Fase 12C-2: ninguno funcional. `ZonaResponse` expone `created_by`/`updated_by` como enteros crudos, sin nombre/username del usuario — si en una fase posterior se necesita mostrar quién creó/editó una zona en la UI, requerirá un `join` adicional o un cambio de schema (fuera de alcance de esta subfase).
- Fase 12C-3: ninguno funcional. `ZonaRecursosResponse` no expone la zona completa, solo `zona_id` y la lista resultante — suficiente para el propósito del endpoint (confirmar el resultado del reemplazo).
- Fase 12C-6: el singular `recurso_id`/`recurso` de `ReservaResponse` es **compatibilidad temporal** (ancla) hasta 12C-4e; los clientes nuevos deben leer `recurso_ids`/`zonas`. El 422 de entrada por `recurso_id` es deliberado (ruptura aprobada). El `ZonaReservaResponse` no expone timestamps — si una fase futura necesita quién creó/editó una zona en el detalle de la reserva, requerirá un cambio de schema.

## Pendientes

- **EmailStr + `email-validator`**: reemplazo del validador manual de email en una fase posterior (requiere añadir la dependencia a `requirements.txt` y aprobación). Aplica también al validador nuevo de `Espacio.correo` (Fase 12B).
- Fuente única del horario de atención (Fase 4).
- Limpieza de tipos TypeScript del frontend con `| string` (Fase 5).
- Fase 12B: actualizar el formulario de creación de espacios del frontend admin para enviar `correo` (y opcionalmente `modalidad_reserva`) — pendiente de aprobación separada, fuera de alcance backend-only.
- ~~Fase 12C-2: aprobar y regenerar `tests/openapi.snapshot.json`~~ **Hecho** — snapshot regenerado y verde.
- ~~Fase 12C-3: aprobar y regenerar `tests/openapi.snapshot.json`~~ **Hecho** — snapshot regenerado y verde.
- ~~Fase 12C-6: aprobar y regenerar `tests/openapi.snapshot.json`~~ **Hecho** — snapshot regenerado y verde.
- **Fase 12C-4e (no iniciada)**: retiro de `Reserva.recurso_id`/`recurso` (columna, constraint histórica `reservas_sin_solapamiento` y singular de la respuesta) — solo al cierre de toda la transición, requiere aprobación explícita.
- Evaluar en una fase posterior si `RecursoResponse` debe exponer su `zona_id` (simetría inversa) — no pedido en 12C-3, no implementado.

## Fase de implementación

Fase 2 (alineación de schemas con el dominio). Fase 12B (`Espacio.correo`/`modalidad_reserva`, `Recurso.es_prestacion_servicio`). Fase 12C-2 (`schemas/zona.py`). Fase 12C-3 (`ZonaRecursosUpdate`/`ZonaRecursosResponse`). Fase 12C-6 (contrato plural de reserva).
