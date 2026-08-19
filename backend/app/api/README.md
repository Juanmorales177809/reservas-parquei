# api

## Propósito

Routers FastAPI: endpoints HTTP. Esta capa orquesta la validación de entrada (schemas), la autorización (deps) y delega la lógica de negocio en `services/`. No contiene reglas de negocio propias.

## Cambios realizados

| Archivo | Acción | Descripción |
|---|---|---|
| espacios.py | Modificado | `GET /espacios` aplica RN-005 con autenticación opcional: anónimos y rol `usuario` ven solo espacios `activo`; admin/gestor ven todos. El docstring del endpoint se conservó EXACTO para mantener el OpenAPI byte-idéntico |
| admin_dashboard.py | Modificado | El cálculo de ocupación usa el `horario_atencion` real de cada espacio (`HorarioAtencion`) en lugar del rango fijo 7-20; el grid del heatmap conserva el rango 7..19 del contrato del gráfico |
| auth.py | Modificado (Fase 9F-A, luego 9G) | 9F-A: `POST /auth/login` además de devolver `TokenResponse` fijaba una cookie HttpOnly con el mismo token; nuevo `POST /auth/logout` (borra la cookie, `204`, idempotente, no exige autenticación). **9G (cookie-only)**: `POST /auth/login` pasa a `response_model=LoginResponse` (`{user}`) — ya no devuelve `access_token` ni `token_type`; la cookie se conserva con los mismos atributos. `logout` sin cambios |
| recursos.py | Modificado (Fase 12B) | `GET /recursos` y `GET /recursos/{id}/disponibilidad` filtran/bloquean recursos PS (`es_prestacion_servicio`) para `usuario` y anónimos; `POST /recursos` propaga el campo. `GET /recursos/gestion` no requirió cambios (ya restringido a gestor/admin) |
| zonas.py | Nuevo (Fase 12C-2) | Router `/zonas`: `GET ""` (público, criterio RN-005-like), `POST ""`, `PUT "/{zona_id}"`, `DELETE "/{zona_id}"` (`require_resource_manager` + `get_managed_space_id`, mismo patrón que `recursos.py`). Sin `GET "/{zona_id}"` — Recurso tampoco tiene ese endpoint |
| zonas.py | Modificado (Fase 12C-3) | Nuevo `PUT "/{zona_id}/recursos"` (reemplazo completo de la asociación Zona↔Recurso); `DELETE "/{zona_id}"` ahora bloquea con 409 si la zona tiene asociaciones |
| admin_dashboard.py | Modificado (Fase 12C-6) | `recursos_mas_reservados` cuenta **por recurso efectivo**: JOIN contra `reserva_recursos` (`func.count(ReservaRecurso.id)` en select/group_by/ORDER BY) — una reserva de zona con N recursos efectivos cuenta N veces |
| notificaciones.py | Modificado (Fase 12C-6) | `_etiqueta_objetivo` zona-aware: si la reserva tiene zonas, el mensaje las nombra; si no, el recurso ancla singular. `_query_usuario` precarga `Reserva.zonas` |
| recursos.py | Modificado (Fase 12C-6) | Guares de mover/eliminar migrados a `_recurso_tiene_reservas`: consulta `reserva_recursos` (conjuntos efectivos) **y** la columna histórica `Reserva.recurso_id` (ancla de zona sin recursos) |
| notificaciones.py | Modificado (Fase 12C-4e-lectores) | `_etiqueta_objetivo` nombra TODOS los recursos asociados (vía `recursos_asociados`), no solo el ancla singular, cuando la reserva no tiene zona; `_query_usuario` precarga `Reserva.recursos_asociados`→`ReservaRecurso.recurso` en vez de `Reserva.recurso` |
| recursos.py | Modificado (Fase 12C-4e-lectores) | `_recurso_tiene_reservas` deja de consultar `Reserva.recurso_id` como fallback (solo `reserva_recursos`); `eliminar_recurso` gana `try/except IntegrityError` → 409, necesario porque el ancla de una zona sin recursos ya no lo detecta el guard de aplicación y ahora depende de la FK real de `reservas.recurso_id` (sin retirar) |

## Reglas de negocio relacionadas

- **RN-005** (solo espacios disponibles son visibles): aplicada en `GET /espacios`. Un token de usuario NO permite recuperar espacios no disponibles mediante `skip`/`limit` ni ningún parámetro.
- **RN-028** (información consolidada): la ocupación refleja ahora el horario real configurado por espacio.
- Reglas adicionales del código: convención de franjas [inicio, fin) y días sin atención.
- **RN-011 / RN-016** (Fase 12C-2, parcial): superficie HTTP de `Zona` — CRUD y autorización. La asociación con `Recurso` y la integración con `Reserva` quedan para 12C-3/12C-4.
- **RN-011 / RN-016** (Fase 12C-3): superficie HTTP de la asociación `Zona`↔`Recurso` (reemplazo completo) y guard de eliminación. La integración con `Reserva` sigue en 12C-4.

## Decisiones técnicas

- **Autenticación opcional sin cambio de OpenAPI**: la dependencia `get_current_user_optional` (en `app/deps.py`) lee el header Authorization manualmente vía `Request`, sin `OAuth2PasswordBearer` — verificado con Context7 que `OAuth2PasswordBearer` (hereda de `SecurityBase`) sí añadiría un esquema de seguridad al OpenAPI del endpoint. Un token inválido se trata como acceso anónimo.
- **Compatibilidad con la gestión admin**: `GET /espacios` alimenta también el panel admin del frontend; por eso admin/gestor siguen viendo todos los espacios (sin cambios de frontend).
- **Fuente única del horario**: la ocupación precarga los `horario_atencion` por espacio (sin N+1) y reutiliza `HorarioAtencion` del dominio; un horario vacío/inválido (dato legacy) aporta cero horas habilitadas.
- **Límites de franjas**: inicio inclusivo, fin exclusivo (convención vigente).
- **Denominador cero**: cuando no hay horas atendidas, `porcentaje` es 0 (guard existente conservado).

### Fase 12B — Visibilidad y autorización de recursos PS

- **RN-009**: recursos marcados `es_prestacion_servicio=True` no son visibles ni reservables por el rol `usuario` (investigador). `gestor` (laboratorista) y `admin` (administrador técnico) sí.
- **Reutilización del patrón RN-005**: `_puede_ver_ps(usuario)` sigue exactamente el mismo criterio ya usado en `listar_espacios` (`usuario is None or usuario.rol == Rol.USUARIO.value` → sin acceso), aplicado ahora a `listar_recursos` y `obtener_disponibilidad_recurso`, ambos antes públicos sin ninguna dependencia de autenticación.
- **`get_current_user_optional` reutilizado sin cambiar el esquema de seguridad en OpenAPI**: mismo mecanismo ya verificado en la Fase 4 para `GET /espacios` (lee el header manualmente, sin `Depends(oauth2_scheme)`) — confirmado que el diff del snapshot no agrega ningún nuevo requisito de seguridad a estos endpoints.
- **`GET /recursos/gestion` sin cambios**: ya requería `require_resource_manager` (solo gestor/admin), así que cualquiera que llegue a ese endpoint ya está autorizado a ver PS por diseño previo — no hizo falta ningún filtro adicional.
- **Respuesta 403, no 404, para el intento directo de disponibilidad de un recurso PS por un rol no autorizado**: es una restricción de rol (igual que "Solo puedes gestionar recursos de tu espacio"), no una cuestión de existencia del recurso.

### Fase 12C-2 — CRUD y API de `Zona`

- **`GET /zonas` público, criterio RN-005-like**: mismo patrón exacto que `listar_espacios` (`usuario is None or usuario.rol == Rol.USUARIO.value` → solo `estado='activo'`), extendido con un `JOIN` a `Espacio` para exigir también `Espacio.estado == 'activo'` — así una zona activa de un espacio inactivo/mantenimiento no se filtra por accidente. `gestor`/`admin` ven todo, sin restricción a su propio espacio (igual que `GET /recursos`, no `GET /recursos/gestion`); el filtro por `?espacio_id=` es un `WHERE` adicional, sin validar que el espacio exista (mismo criterio que `GET /recursos`).
- **Sin `GET /zonas/{zona_id}` de un solo elemento**: decisión deliberada, no un olvido — `Recurso` tampoco tiene un `GET /recursos/{id}` (solo listado, `/gestion` y `/{id}/disponibilidad`). Una petición a esa ruta responde **405** (el path existe para `PUT`/`DELETE`, no para `GET` — comportamiento estándar de Starlette, no un handler propio), verificado con test explícito.
- **`POST /zonas` con `espacio_id` obligatorio en el schema** (a diferencia de `RecursoCreate.espacio_id`, opcional con fallback silencioso al espacio del gestor): como aquí siempre viene explícito, la autorización es un **403 explícito** si un gestor manda un `espacio_id` distinto al suyo, en vez del "override silencioso" que usa `crear_recurso`. Mismo criterio de fondo (gestor limitado a su espacio), forma de aplicarlo adaptada al contrato pedido.
- **`PUT /zonas/{zona_id}` ignora `espacio_id` para un gestor** (lo elimina de `cambios` antes de persistir, igual que `actualizar_recurso`): un gestor no puede mover una zona fuera de su espacio ni leyendo ni escribiendo ese campo.
- **`created_by`/`updated_by` nunca vienen del payload**: `ZonaCreate`/`ZonaUpdate` no declaran esos campos (Pydantic v2 ignora por defecto cualquier campo extra no declarado), así que un cliente que los incluya en el JSON no tiene ningún efecto — se fijan siempre desde `current_user.id` en el router.
- **Sin guard de dependencias en `DELETE /zonas/{zona_id}`**: a diferencia de `eliminar_recurso`/`eliminar_espacio` (que bloquean el borrado si hay reservas/recursos asociados), `Zona` no tiene todavía ninguna asociación real que consultar (`zona_recursos` es 12C-3, `reserva_zonas` es 12C-4) — inventar esa consulta ahora sería contra una tabla que no existe. El guard se agregará cuando esas asociaciones existan.
- **`crud/zonas.py` deliberadamente sin una función de listado**: a diferencia de `crud/espacios.py`, el listado de `GET /zonas` requiere el `JOIN` condicional con `Espacio` según el rol — mismo patrón que `listar_espacios` en `api/espacios.py`, que tampoco delega el listado a `crud/espacios.py`. `crud/zonas.py` se mantiene con `get_zona`/`create_zona`/`update_zona`, sin una abstracción de listado que ningún caller usaría.

### Fase 12C-3 — Asociación Zona↔Recurso

- **Validación completa antes de escribir, no incremental**: `PUT /zonas/{zona_id}/recursos` resuelve existencia (404), pertenencia al mismo espacio (400) y conflicto de unicidad con otra zona (409) **antes** de llamar a `reemplazar_recursos_de_zona` — así, si cualquier recurso de la lista falla una validación, ninguna fila se modifica (atomicidad "por construcción", verificada con test explícito: una lista mixta de un recurso válido y uno conflictivo no deja ni siquiera el válido asociado).
- **Precedencia de errores**: 404 (existencia) → 400 (espacio distinto al de la zona) → 409 (ya asociado a otra zona) → 403 (autorización, resuelto antes que cualquiera de los anteriores, junto con el 404 de la zona misma). Ningún precedente exacto de "dos entidades deben compartir el mismo padre" existía en el código; se eligió 400 por ser una violación de regla de dominio sobre el payload, no un problema de existencia (404) ni de permisos (403) ni de conflicto con otro recurso (409).
- **`espacio_id` obligatorio en el schema, sin validar estado del espacio**: igual que en `crear_zona`/`crear_recurso`, la asociación no exige que el espacio esté `activo` — esa restricción es propia de la reserva (fuera de alcance aquí), no de la gestión de catálogo.
- **Lista vacía permitida sin excepción**: `PUT /zonas/{zona_id}/recursos` con `recurso_ids: []` desasocia todo — no hay ninguna regla existente que exija que una zona tenga al menos un recurso.
- **`DELETE /zonas/{zona_id}` ahora bloquea con 409 si tiene asociaciones**: mismo patrón que `eliminar_recurso`/`eliminar_espacio` (bloquear en vez de cascada silenciosa cuando la eliminación es una acción explícita del usuario vía API). Distinto del comportamito a nivel de BD (`ondelete="CASCADE"` en `zona_recursos`, ver `backend/app/models/README.md`): ese cascade es una red de seguridad para el caso en que la fila se elimine por otra vía, no el camino esperado desde este endpoint (que nunca debería llegar a ejecutar el `DELETE FROM zonas` mientras existan asociaciones, gracias al guard).
- **Sin guard equivalente en `api/recursos.py`**: fuera de alcance de 12C-3 (no listado en los archivos autorizados). `PUT /recursos/{id}` sigue sin impedir mover un recurso asociado a una zona a otro espacio, y `DELETE /recursos/{id}` sigue sin bloquear por asociación de zona (solo por reservas). Riesgo aceptado y documentado, no silenciado — ver `backend/app/models/README.md`.

### Fase 12C-6 — Dashboard, notificaciones y guards por recurso efectivo

- **Dashboard cuenta por recurso efectivo** (`admin_dashboard.py`): `recursos_mas_reservados` hace JOIN contra `reserva_recursos` y cuenta `ReservaRecurso.id` — una reserva de zona con N recursos efectivos aporta N al ranking de ese recurso, mismo criterio que la ocupación (que ya leía desde la asociación vía el servicio). Reemplaza el conteo por la columna histórica `Reserva.recurso_id`.
- **Notificaciones zona-aware** (`notificaciones.py`): `_etiqueta_objetivo` nombra la/s zona/s cuando la reserva las tiene ("Nueva reserva pendiente para la zona X"); si no, el recurso ancla singular (compatibilidad). `_query_usuario` precarga `Reserva.zonas` (joinedload) para evitar N+1.
- **Guard de mover/eliminar recurso migrado** (`recursos.py::_recurso_tiene_reservas`): consulta `reserva_recursos` (fuente de los conjuntos, incluye recursos reclamados por reservas de zona que no son el ancla) **y** la columna histórica `Reserva.recurso_id` (el ancla de una zona sin recursos, que conserva el FK) — un recurso con reservas no puede moverse a otro espacio ni eliminarse, con 409 en ambos endpoints.

### Fase 12C-4e-lectores/schemas — Retiro del singular en la respuesta

- **`notificaciones.py::_etiqueta_objetivo` lista todos los recursos**: cuando la reserva no tiene zona, el mensaje ahora nombra todos los recursos asociados (`", ".join`), no solo el ancla — una reserva de dos recursos directos mencionaba antes solo uno.
- **`recursos.py::_recurso_tiene_reservas` consulta solo `reserva_recursos`**: se retira el fallback a la columna histórica `Reserva.recurso_id`. Caso límite real: el recurso "ancla" de una reserva de zona **sin** recursos asociados no tiene fila en `reserva_recursos` y este guard ya no lo detecta — pero `reservas.recurso_id` sigue siendo `NOT NULL` con FK real (sin retirar en esta subfase), así que la base de datos igual rechaza el borrado. `eliminar_recurso` ganó un `try/except IntegrityError` → 409 (mismo mensaje que el guard explícito) para no dejar escapar ese caso límite como un 500 crudo — necesario para completar el pedido literal ("guard consulta solo `reserva_recursos`") sin introducir una regresión.
- **`ReservaResponse` retira `recurso_id`/`recurso`, agrega `recursos`** (`app/schemas/reserva.py`, detalle completo en `backend/app/schemas/README.md`): la forma singular temporal (ancla) que 12C-6 dejó pendiente se retira; `crud/reservas.py::_enriquecer_con_asociaciones` deja de resolver/asignar el ancla y solo puebla `recursos`/`recurso_ids`/`zona_ids` (ver `backend/app/crud/README.md`).
- **`reservas.recurso_id` (columna), `Reserva.recurso` (relación ORM), `reservas_sin_solapamiento`, índices históricos, `migrations.py` y el rollback documentado no se tocan**: el retiro es solo del contrato de respuesta pública; nada del modelo ni de la base de datos cambió, sin DDL ejecutado.

### Fase 9F-A — Autenticación dual por cookie HttpOnly

- **Fase dual aprobada explícitamente**: `POST /auth/login` conserva `TokenResponse.access_token` en el body (sin cambio de contrato) y además fija una cookie HttpOnly con el mismo token, vía los helpers de `app/auth/auth.py` (`atributos_cookie_acceso()`, `max_age_cookie_acceso()`). Objetivo: permitir migrar el frontend a cookie en una fase posterior sin romper clientes existentes (E2E, frontend actual, que siguen usando `Authorization: Bearer`).
- **`POST /auth/logout` nuevo, sin autenticación**: borra la cookie (`response.delete_cookie`) y responde `204 No Content` siempre, exista o no una cookie previa, y con o sin `Authorization` válido. Diseño intencional: un cliente con sesión inválida/expirada debe poder limpiar su cookie igual.
- **Precedencia documentada cuando hay ambos mecanismos**: `app/deps.py` (`get_current_user`, `get_current_user_optional`, `require_admin_dashboard`) da prioridad al header `Authorization` sobre la cookie cuando ambos están presentes — el header es la señal explícita de un cliente que declara sus propias credenciales por request; la cookie es un fallback ambiental para clientes de navegador. Probado en `tests/test_api_auth_cookie.py::TestPrecedenciaCuandoHayAmbosMecanismos`.
- **`oauth2_scheme` con `auto_error=False`**: necesario para que `get_current_user`/`require_admin_dashboard` puedan evaluar la cookie antes de decidir que no hay credenciales. Verificado que no cambia el esquema de seguridad generado en OpenAPI (el snapshot solo ganó la ruta `/auth/logout`, nada más).
- **Sin cambios de CORS/rate limiting**: el navegador real solo llega al backend vía el proxy de Next.js (`frontend/next.config.js`, `/api/:path*`), por lo que la fase dual no requiere tocar `allow_credentials` de CORS ni el limitador de intentos de login — ambos quedan fuera de alcance de esta fase, sin cambios.

### Fase 9G — `auth.py` y `deps.py`: corte cookie-only

- **`POST /auth/login` → `LoginResponse{user}`**: el response_model pasa de `TokenResponse` a `LoginResponse` (`app/schemas/usuario.py`, únicamente `user`). La cookie `access_token` se sigue fijando con los mismos atributos (9F-A, `app/auth/auth.py`), con el mismo `Max-Age`. **Contrato de login**: ya no hay `access_token` ni `token_type` en el body; el frontend solo leía `data.user` desde 9F-B.
- **Authorization/Bearer ya no se acepta**: los dependientes de `app/deps.py` leen únicamente la cookie; un Bearer sin cookie devuelve 401 (sin `WWW-Authenticate: Bearer`). Con cookie y Bearer a la vez, **solo la cookie decide**. Probado en `test_api_auth_cookie.py::TestBearerRechazado`/`TestSoloLaCookieDecide`.
- **OpenAPI = mecanismo real**: `securitySchemes.cookieAuth` (`apiKey`, `in: cookie`, `name: access_token`) exigido en los endpoints protegidos; `GET /espacios` (RN-005, `get_current_user_optional`), `/auth/login` y `/auth/logout` siguen públicos sin security. El snapshot aún no está regenerado (diff generado en `tests/openapi.generado.json`).
- **CORS**: `allow_headers` → `["Content-Type"]` en `app/main.py` (se retira `Authorization`); origins y `allow_credentials=False` sin cambios (el navegador solo cruza orígenes vía proxy same-origin de Next.js).

## Pruebas

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_api_espacios.py tests/test_admin_dashboard_ocupacion.py -v
.\.venv\Scripts\python.exe -m pytest tests/test_api_auth_cookie.py -v
.\.venv\Scripts\python.exe -m pytest tests/test_api_recursos.py tests/test_api_espacios.py::TestModalidadYCorreo -v   # Fase 12B
.\.venv\Scripts\python.exe -m pytest tests/test_api_zonas.py -v   # Fase 12C-2
.\.venv\Scripts\python.exe -m pytest tests/test_api_zonas_recursos.py -v   # Fase 12C-3
.\.venv\Scripts\python.exe -m pytest tests/test_dashboard_recursos_efectivos.py -v   # Fase 12C-6
.\.venv\Scripts\python.exe -m pytest tests/test_api_notificaciones.py tests/test_api_recursos.py tests/test_reserva_response_sin_singular.py -v   # Fase 12C-4e-lectores/schemas
```

Resultado esperado: verde (8 tests de RN-005 + 7 de ocupación; suite de autenticación por cookie de la Fase 9G reescrita a cookie-only). Suite completa del backend: **516/516** salvo `test_openapi_contrato.py` en rojo a propósito hasta aprobar la regeneración del snapshot de 9G. Fase 12B: 318/318. Fase 12C-2: 364 en total. Fase 12C-3: 382 en total. Fase 12C-6: 482/482. Fase 12C-4e-lectores/schemas: suite completa **525/525** (incluye `test_openapi_contrato.py` verde, snapshot regenerado); E2E completo contra `reservas_test` recreada en limpio: **27 passed / 0 failed / 81 skipped**.

## Impacto y compatibilidad

- OpenAPI **byte-idéntico** para Fase 4 (SHA256 verificado antes/después). Fase 9F-A cambia el OpenAPI de forma aprobada: solo agrega la ruta `/auth/logout` (verificado con diff explícito del snapshot regenerado — 15 líneas insertadas, 0 eliminadas, ningún otro path/schema tocado).
- Sin cambios de rutas, métodos, campos, schemas, migraciones ni frontend en Fase 4. Fase 9F-A no toca `TokenResponse`, ni ningún schema existente, ni frontend, ni Docker, ni CI, ni migraciones, ni rate limiting.
- Cambio de comportamiento intencional (Fase 4): la lista pública ya no expone espacios `inactivo`/`mantenimiento` (corrección de RN-005).
- Cambio de comportamiento intencional (Fase 9F-A): los endpoints protegidos aceptaron además una cookie `access_token` válida como alternativa al header `Authorization`. Cambio de comportamiento intencional (Fase 9G): el header `Authorization` **deja de aceptarse** (401 sin cookie válida) y el login deja de exponer `access_token`/`token_type`; códigos de estado 401/403/422/429 sin cambios salvo el header `WWW-Authenticate`, verificado con tests explícitos.
- Cambio de comportamiento intencional (Fase 12B): `GET /recursos` y `GET /recursos/{id}/disponibilidad` dejan de ser completamente públicos en su resultado — un anónimo o `usuario` ya no ve/consulta recursos PS (antes visibles a cualquiera). Sin cambios de OpenAPI en estas dos rutas (no se agregó esquema de seguridad); el cambio es de comportamiento, verificado con tests explícitos.
- **Fase 12C-2 — cambio de OpenAPI puramente aditivo, aprobado y regenerado**: nuevos paths `/zonas` y `/zonas/{zona_id}`, nuevos componentes `ZonaCreate`/`ZonaUpdate`/`ZonaResponse`. Ningún path/schema existente fue tocado (376 líneas insertadas, 0 eliminadas). `tests/openapi.snapshot.json` ya refleja este cambio; `test_openapi_contrato.py` verde.
- **Fase 12C-3 — cambio de OpenAPI puramente aditivo, aprobado y regenerado**: nuevo path `/zonas/{zona_id}/recursos` (`PUT`), nuevos componentes `ZonaRecursosUpdate`/`ZonaRecursosResponse`. Ningún path/schema existente fue tocado (94 líneas insertadas, 0 eliminadas; el guard nuevo de `DELETE /zonas/{zona_id}` es un cambio de comportamiento, no de contrato — FastAPI no documenta automáticamente cada código de error posible de un `HTTPException` inline, mismo criterio que el resto de 403/404 de este router). `tests/openapi.snapshot.json` ya refleja este cambio; `test_openapi_contrato.py` verde.
- **Fase 12C-6 — cambio de OpenAPI aprobado y regenerado**: cambios solo a nivel de schemas de reserva (`ReservaCreate`/`ReservaUpdate`: `additionalProperties: false` + ejes `recurso_ids`/`zona_ids`; `ReservaResponse`: + `recurso_ids`/`zona_ids`/`zonas`; nuevo `ZonaReservaResponse`). **Ninguna ruta ni esquema de seguridad modificado** (verificado por script estructural y por diff antes de regenerar). `test_openapi_contrato.py` verde.
- **Fase 12C-4e-schemas — cambio de OpenAPI aprobado y regenerado, único schema afectado**: `ReservaResponse` quita `recurso`/`recurso_id` de `properties`/`required`, agrega `recursos` (array de `RecursoReservaResponse`). Cambio de comportamiento en `notificaciones.py`/`recursos.py` (12C-4e-lectores) sin cambio de OpenAPI (mismos paths, mismos códigos de estado documentados). **Ninguna ruta, método, request body ni esquema de seguridad tocado** — ver detalle del diff en `backend/app/schemas/README.md`. `test_openapi_contrato.py` verde.

## Riesgos

- El heatmap `ocupacion_por_dia_hora` mantiene su grid 7..19 (contrato del gráfico): horas atendidas fuera de ese rango se cuentan en `ocupacion_global` pero no aparecen en el gráfico. Limitación documentada, no bloqueante.
- **CSRF (riesgo aceptado, mitigado, no eliminado)**: al aceptar cookie, el navegador la adjunta automáticamente en peticiones same-origin; desde la Fase 9F-B `frontend/src/services/api.ts` envía `credentials: 'same-origin'` en cada request. `SameSite=Lax` bloquea el envío de la cookie en peticiones state-changing disparadas por `fetch`/XHR desde otro origen, pero no hay token CSRF de doble envío ni otra defensa adicional — la Fase 9G retiró la vía `Authorization` (que SameSite no podía mitigar) y **seguimos dependiendo** de `SameSite=Lax` + cookie host-only + proxy same-origin de Next.js (`frontend/next.config.js`). **No se afirma que el riesgo esté resuelto, solo mitigado**; el token de doble envío queda como fase separada (Pendientes).
- **`require_admin_dashboard` no tiene cobertura de test propia** (ni antes ni después de esta fase): función sin uso en ningún router actual (verificado); se actualizó por consistencia con `oauth2_scheme`, pero queda sin ejercitar directamente.
- **Fase 12B — regresión real de E2E confirmada**: `frontend/e2e/tests/smoke/03-admin.spec.ts:12-14` crea un espacio vía API directa sin `correo`, ahora obligatorio — falla con 422 de forma determinista (no flaky, reproducido en 2 intentos). Requiere ajuste del payload del test (y del formulario admin real, `frontend/src/app/admin/espacios/page.tsx`), fuera del alcance backend-only de esta fase.
- **Fase 12C-2**: ninguno funcional. `Zona` sigue sin asociación con `Recurso` ni `Reserva` — el `DELETE /zonas/{id}` no tiene guard de dependencias porque no hay ninguna que consultar todavía (ver Decisiones técnicas). El rollback de `Reserva.recurso_id` (decisión 11 del análisis de 12C) sigue pendiente — corresponde a 12C-4, no a esta subfase.
- **Fase 12C-3**: ninguno funcional en el alcance implementado. `PUT /recursos/{id}` y `DELETE /recursos/{id}` no conocían la asociación de zona (riesgo aceptado y documentado en `backend/app/models/README.md`) — **resuelto en 12C-6** con `_recurso_tiene_reservas` (asociación + columna histórica). El rollback de `Reserva.recurso_id` sigue pendiente — corresponde a 12C-4e.
- **Fase 12C-6**: el mensaje de notificación de una reserva que antes se construía con `reserva.recurso.nombre` ahora es zona-aware — una reserva solo de zona ya no muestra el recurso ancla en el texto. Riesgo residual del ancla (zona sin recursos → recurso de menor id del espacio) documentado en `services/README.md` y `tests/test_reservas_zonas.py`.
- **Fase 12C-4e-lectores/schemas**: ruptura de contrato aprobada explícitamente en `ReservaResponse` (retira `recurso_id`/`recurso`) — cualquier cliente externo no migrado a `recurso_ids`/`recursos`/`zonas` se rompe; el frontend propio de este repo ya migró en la misma subfase. `_recurso_tiene_reservas` (`recursos.py`) ya no detecta por sí solo el recurso ancla de una zona sin recursos — ese caso límite queda cubierto por la FK real de `reservas.recurso_id` (traducida a 409), no por el guard de aplicación; riesgo residual documentado, no bloqueante mientras la columna histórica exista.

## Pendientes

- Si el frontend del panel admin migrara a un endpoint propio de gestión, el filtro podría volverse incondicional (sin distinción por rol).
- Limpiar el docstring/descripción del endpoint requeriría aprobación explícita (cambia OpenAPI).
- ~~Fase 9F-B: migrar `AuthContext`, `api.ts`, `localStorage` y los fixtures E2E para dejar de depender del header como mecanismo primario.~~ **Hecho** — commit `13c341d3c93ae86deb709aad1f5f659cdc74c9bf`, local, pendiente de push.
- ~~Fase 9G: retirar `access_token` del body de `TokenResponse` y el soporte de `Authorization`.~~ **Implementada en el working tree** (sin commit ni push): falta aprobar el diff del OpenAPI (`tests/openapi.generado.json` vs snapshot) y regenerar el snapshot.
- **CSRF de doble envío (fase separada, no iniciada)**: 9G dejó explícitamente fuera de alcance agregar un token CSRF u otra defensa adicional (origin/referer); evaluar como fase propia.
- **Fase 12B**: aprobar por separado el ajuste de `frontend/src/app/admin/espacios/page.tsx` y `frontend/e2e/tests/smoke/03-admin.spec.ts` para incluir `correo` (ver Riesgos arriba).
- **Fase 12D** (pendiente, no iniciada): agregar el condicionamiento de "PS solo reservable en tipo servicio de ensayo" en `services/reservas.py::validar_acceso_ps` (ver `backend/app/services/README.md`).
- ~~Fase 12C-2: aprobar y regenerar `tests/openapi.snapshot.json`~~ **Hecho.**
- ~~Fase 12C-3: aprobar y regenerar `tests/openapi.snapshot.json`~~ **Hecho.**
- ~~Fase 12C-6: aprobar y regenerar `tests/openapi.snapshot.json`~~ **Hecho.**
- ~~Fase 12C-4e-lectores: migrar lectores de `notificaciones.py`/`recursos.py` a las asociaciones.~~ **Hecho.**
- ~~Fase 12C-4e-schemas: retirar `recurso_id`/`recurso` de `ReservaResponse`, agregar `recursos`; aprobar y regenerar `tests/openapi.snapshot.json`.~~ **Hecho.**
- **Retiro de la columna `reservas.recurso_id`, `Reserva.recurso` (relación ORM), `reservas_sin_solapamiento` e índices históricos (no iniciado)**: solo al cierre de toda la transición, requiere aprobación explícita y ejecución de DDL. El **rollback endurecido** de `migrations.py` (abortar ante reservas no representables, única transacción, verificación del esquema) sigue sin escribirse (pendiente desde 12C-4b).

## Fase de implementación

Fase 4 (RN-005 y ocupación real). Fase 9F-A (autenticación dual por cookie HttpOnly). Fase 9G (cookie-only, corte de `access_token`/`Authorization`). Fase 12B (visibilidad/autorización de recursos PS). Fase 12C-2 (CRUD/API de `Zona`). Fase 12C-3 (asociación Zona↔Recurso). Fase 12C-6 (dashboard/notificaciones/guards por recurso efectivo). Fase 12C-4e-lectores/schemas (retiro del singular en la respuesta).
