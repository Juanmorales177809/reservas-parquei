# app

## Propósito

Paquete raíz de la aplicación FastAPI: punto de entrada (`main.py`), configuración (`config.py`), acceso a datos (`db.py`), dependencias de autorización (`deps.py`) y migraciones idempotentes (`migrations.py`).

## Cambios realizados

| Archivo | Acción | Descripción |
|---|---|---|
| main.py | Modificado | `@app.on_event("startup"/"shutdown")` (deprecado) migrado a `lifespan` con `asynccontextmanager`; orden conservado: `create_all` → `migrate_resource_reservations()` → `seed_admin_user()`; `engine.dispose()` al cierre |
| deps.py | Modificado (Fase 9F-A, luego 9G) | 9F-A: `get_current_user`, `get_current_user_optional` y `require_admin_dashboard` aceptaban cookie `access_token` o header `Authorization: Bearer` (prioridad al header; `oauth2_scheme` con `auto_error=False`). **9G (cookie-only)**: se elimina `OAuth2PasswordBearer` y toda lectura de `Authorization`; los dependientes leen únicamente `request.cookies["access_token"]` vía `cookie_auth` (`APIKeyCookie` `auto_error=False`, scheme name `cookieAuth`); se elimina el header `WWW-Authenticate: Bearer` de los 401; los mensajes de 401/403 se conservan |

## Reglas de negocio relacionadas

- Arranque idempotente: creación de esquema, instalación de `btree_gist` y exclusión `reservas_sin_solapamiento`, seed de espacios iniciales y creación opcional del primer admin (`INITIAL_ADMIN_*`).

## Decisiones técnicas

- **Lifespan**: patrón actual de FastAPI (verificado en docs oficiales vía Context7). Los warnings de deprecación de `on_event` desaparecieron; el único warning restante de la suite es el shim de `httpx` (externo al proyecto).
- **`engine.dispose()` seguro**: solo cierra conexiones ociosas del pool; el engine global de `app.db` sigue siendo utilizable después (se reabren conexiones al usarlo). Verificado: el fixture `db` y otros tests abren conexiones nuevas sin problema tras el lifespan.
- **Tests**: el fixture `client` de `tests/conftest.py` usa `TestClient` SIN context manager, por lo que el lifespan NO se ejecuta en la suite normal (sin seeding). `tests/test_lifespan_arranque.py` lo ejercita explícitamente con `with TestClient(app)` y comprueba idempotencia con dos ciclos.

### Fase 9F-A — `deps.py`: cookie o header, con precedencia documentada

- **Un único punto de fallback**: `get_current_user` calcula `token_efectivo = token or request.cookies.get(NOMBRE_COOKIE_ACCESO)` (constante importada de `app.auth.auth`); el resto de la función (decodificación, búsqueda del usuario, excepción 401) no cambió. Mismo patrón aplicado a `require_admin_dashboard`.
- **`get_current_user_optional` mantiene su restricción de no añadir esquema de seguridad al OpenAPI** (RN-005 en `GET /espacios`, decisión de la Fase 4 documentada arriba): sigue leyendo el header manualmente vía `Request` en vez de `Depends(oauth2_scheme)`; solo se le agregó el mismo fallback a cookie cuando el header no trae `Bearer `.
- **`oauth2_scheme` con `auto_error=False`**: antes, la ausencia del header interrumpía la resolución de dependencias con un 401 automático de FastAPI antes de que el código de `get_current_user` se ejecutara. Ahora esa interrupción automática se desactiva para poder revisar la cookie primero; `get_current_user`/`require_admin_dashboard` lanzan el mismo `HTTPException 401` manualmente si no hay ni header ni cookie, preservando el status code observable (no hay test en la suite que dependiera del mensaje `"Not authenticated"` por defecto de FastAPI, verificado antes de este cambio).
- **`require_admin_dashboard` es código sin uso** (verificado: ningún router lo importa) pero se actualizó por consistencia, ya que comparte la misma instancia de `oauth2_scheme`; sin test dedicado, igual que antes de esta fase.

### Fase 9G — `deps.py`: cookie-only (corte del contrato)

- **`cookie_auth` (`APIKeyCookie`) como única vía de sesión**: `get_current_user` y `require_admin_dashboard` toman `Depends(cookie_auth)` (`auto_error=False`, `scheme_name="cookieAuth"`, nombre `access_token`) y lanzan el mismo 401 manual con mensaje estable cuando no hay cookie. `get_current_user_optional` sigue leyendo `request.cookies` a mano (sin el `Depends`) para **no** añadir el esquema de seguridad al OpenAPI de los públicos (RN-005); una cookie inválida se trata como anónimo.
- **La presencia de `cookie_auth` en la cadena de dependencias es lo que hace que FastAPI documente `cookieAuth` y lo exija** (`security: [{cookieAuth: []}]`) en los endpoints protegidos — mismo mecanismo que antes con `OAuth2PasswordBearer`, sin tocar el OpenAPI a mano.
- **Cero lectura de `Authorization`**: se eliminaron la precedencia header→cookie, el parseo manual del header y `WWW-Authenticate: Bearer`; 401/403 conservan sus mensajes (`"No se pudo validar la autenticación"`, `"Solo un administrador..."`, etc.).
- **`require_admin_dashboard` sigue sin uso** (ningún router lo importa) pero se mantuvo consistente con el nuevo mecanismo; `require_admin`, `require_resource_manager` y `get_managed_space_id` dependen de `get_current_user`, sin cambios de lógica.

## Pruebas

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_lifespan_arranque.py -v
.\.venv\Scripts\python.exe -m pytest tests/test_api_auth_cookie.py -v
```

Resultado esperado: 3 tests verdes de lifespan; suite de autenticación por cookie verde (Fase 9G — `test_api_auth_cookie.py` reescrito a cookie-only: login sin `access_token`, rechazo de Bearer, cookie como única vía, `cookieAuth` en OpenAPI, logout idempotente, 401 sin `WWW-Authenticate`). Suite completa: **516/516** (salvo `test_openapi_contrato.py` en rojo a propósito hasta aprobar la regeneración del snapshot de la Fase 9G).

## Impacto y compatibilidad

- Rutas y comportamiento de startup sin cambios salvo el mecanismo de ciclo de vida. OpenAPI byte-idéntico (verificado en Fase 3).
- Fase 9F-A: ningún endpoint que dependía solo de `Authorization` cambió su comportamiento cuando el cliente sigue enviando solo ese header (289/289 tests preexistentes en verde, incluidos los de CORS, cabeceras de seguridad, rate limiting y el handler de excepciones). El cambio es aditivo: agrega una vía de autenticación adicional, no quita la existente.

## Riesgos

- Ninguno identificado para el arranque en Docker (healthcheck de compose usa `/health`, que no depende del orden del lifespan).
- Fase 9F-A: ver riesgos de CSRF y de la fase dual completa en `backend/app/api/README.md` (sección Fase 9F-A) y `backend/app/auth/README.md`.

## Pendientes

- N/A para la Fase 3.
- Fase 9F-A: la migración de frontend/E2E (Fase 9F-B) ya se completó (commit `13c341d3c93ae86deb709aad1f5f659cdc74c9bf`, local, pendiente de push).
- **Fase 9G**: implementada en el working tree (sin commit ni push); pendiente aprobar el diff del OpenAPI (`backend/tests/openapi.generado.json` vs snapshot) y regenerar el snapshot; CSRF de doble envío queda como fase separada.

## Fase de implementación

Fase 3 (integración de la capa de dominio). Fase 9F-A (autenticación dual por cookie HttpOnly). Fase 9G (cookie-only, corte de `access_token`/`Authorization`, cambios en `deps.py`).
