# Changelog

Registro cronológico y factual de los cambios del proyecto. Formato: una
sección por fase, en el orden en que se implementó y publicó. Los hashes de
commit, resultados de CI y conteos de pruebas son los reales observados en
este repositorio (`git log`, GitHub Actions) al momento de cada fase, no
estimaciones.

Convención de commits de esta serie: `<tipo>: <resumen>` (`security:`,
`test:`), rama `feature/soV0.1`, base `feature/v0.1`. Workflow de CI:
`.github/workflows/ci.yml` (`name: CI`), tres jobs — `Backend (pytest)`,
`Frontend (lint, type-check, test, build)`, `E2E (Playwright)`.

## Fase 9 — Hardening de seguridad (2026-08-18)

Serie de sub-fases (9A–9F-B) sobre `feature/soV0.1`, sin cambiar métodos,
rutas ni payloads de la API salvo aprobación explícita caso por caso (Fases
9E, 9F-A). Punto de partida: 187 tests de backend, 45 de frontend, suite
E2E con 1 flaky conocido.

Las Fases 9F-A y 9F-B (migración del JWT de `localStorage` a cookie
HttpOnly) son commits **locales en `feature/soV0.1`, todavía sin `git
push`** al momento de escribir estas dos secciones — a diferencia de
9A–9E, no hay ejecución de CI que reportar para ellas todavía.

### Fase 9A — Cabeceras de seguridad, CORS y contenedor no root

- **Commit**: `3a9e67721ee0841cbe1b29ccc3b9123e69cf12a3` — "security: harden headers CORS and backend container".
- **Push y CI**: publicado en `origin/feature/soV0.1`. Run de GitHub Actions [`32092032893`](https://github.com/Juanmorales177809/reservas-parquei/actions/runs/32092032893) — `completed` / `success`.
- **Archivos**: `.github/workflows/ci.yml`, `backend/Dockerfile`, `backend/app/config.py`, `backend/app/main.py`, `frontend/next.config.js`, `backend/tests/test_cors.py`, `backend/tests/test_security_headers.py`, `frontend/src/test/next-config-security-headers.test.ts`.
- **Cabeceras de seguridad** (backend vía middleware ASGI, frontend vía `next.config.js` `headers()`): `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy` en todas las respuestas. `Content-Security-Policy` restrictiva (`default-src 'none'` en backend salvo `/docs`/`/redoc`, que la excluyen porque Swagger UI carga script/CSS externos e inline; `default-src 'self'` en frontend). `Strict-Transport-Security` y `Cross-Origin-Opener-Policy` **solo** cuando `ENVIRONMENT=production` está explícitamente configurado — no se fuerzan en desarrollo ni en el `docker-compose.yml` actual (que fija `NODE_ENV=production` para el stack local sobre HTTP simple, sin TLS documentado en este repo).
  - Decisión documentada: la CSP del frontend incluye `'unsafe-inline'` en `script-src` porque el App Router de Next.js 14 inyecta `<script>` inline para hidratar Server Components (`self.__next_f.push(...)`); verificado manualmente en navegador que sin ese permiso la app no hidrata. También en `style-src`, por los estilos inline de Recharts y del heatmap del dashboard.
- **CORS** (`backend/app/main.py`): `allow_credentials=False` (el JWT viaja en `Authorization`, nunca en cookies), `allow_methods` acotado a `GET/POST/PUT/PATCH/DELETE` (los únicos que emite el frontend), `allow_headers` acotado a `Content-Type`/`Authorization`. `allow_origins` sin cambios (ya venía parametrizado por variable de entorno).
- **Docker**: `backend/Dockerfile` agrega usuario no root `appuser` (UID 1000, GID 0 — mismo grupo que el patrón OpenShift `chgrp -R 0` ya existente). Verificado con contenedor real: `id` → `uid=1000(appuser) gid=0(root)`, `/health` responde 200, migraciones y seed corren sin error.
- **Auditoría de dependencias**: step informativo `npm audit --audit-level=high` agregado a `ci.yml` con `continue-on-error: true` — no bloquea el pipeline, solo da visibilidad.
- **Resultados**: backend 204/204 (187 previos + 7 de cabeceras + 10 de CORS); frontend 53/53 + type-check/lint/build limpios; E2E 25 passed + 1 flaky conocido + 78 skipped.
- **OpenAPI**: sin cambios (verificado contra `tests/openapi.snapshot.json`).
- **Hallazgo corregido antes de publicar**: la primera versión enviaba `Cross-Origin-Opener-Policy` siempre, no solo con `ENVIRONMENT=production` como el resto de cabeceras condicionadas a HTTPS real; se corrigió antes del commit y quedó agrupada con `Strict-Transport-Security` bajo el mismo condicional.

### Fase 9A.1 — Estabilización del flaky de E2E

- **Commit**: `118031c2df126d0f371142b1b1b02b9803ecde2c` — "test: remove deterministic E2E date collision".
- **Push y CI**: publicado en `origin/feature/soV0.1`. Run [`32093344703`](https://github.com/Juanmorales177809/reservas-parquei/actions/runs/32093344703) — `completed` / `cancelled` (cancelado por la política `concurrency: cancel-in-progress: true` de `ci.yml` al llegar el push de la fase siguiente antes de terminar; no es un fallo de los tests). Las corridas de CI de los commits posteriores, que incluyen este cambio, sí completaron en verde.
- **Archivo**: `frontend/e2e/tests/regresion/05-notificaciones.spec.ts` (offset de fecha 14→22) y `frontend/e2e/README.md` (documenta la regla de separación mínima de offsets).
- **Causa raíz**: `frontend/e2e/tests/smoke/08-disponibilidad.spec.ts` (offset 13) y `05-notificaciones.spec.ts` (offset 14) reservaban el mismo recurso y horario; `fechaFutura()` salta al lunes cuando el offset crudo cae domingo, así que dos offsets separados por solo 1 día podían converger a la misma fecha efectiva según el día de ejecución, disparando un `409` real de la constraint `reservas_sin_solapamiento` entre specs.
- **Fix**: separar los offsets en al menos 2 días — matemáticamente imposible que colisionen sin importar el día de la semana en que se ejecute la suite (el salto de domingo nunca desplaza más de 1 día).
- **Validación local**: combinación conflictiva (`usuario`+`gestor`, `--retries=0`) 3/3 corridas sin fallos; suite completa (`test:e2e:all`) 3/3 corridas con DB reiniciada entre cada una, siempre 26 passed / 0 failed / 0 flaky / 78 skipped.

### Fase 9B — Eliminación de dependencia axios no usada

- **Commit**: `7dbd2f91e861e8fe09821af3f375d2cbd031d441` — "security: remove unused axios dependency".
- **Push y CI**: publicado. Run [`32094212014`](https://github.com/Juanmorales177809/reservas-parquei/actions/runs/32094212014) — `completed` / `success`.
- **Archivos**: `frontend/package.json`, `frontend/package-lock.json`.
- **Hallazgo**: `axios@0.27.2` era dependencia directa con múltiples CVEs altos/críticos, pero **no se usaba en ningún código activo** — el único `import axios` real estaba en `frontend/services/espacioService.js`, fuera de `src/`, nunca importado por nada, no compilado (`tsconfig.json` solo incluye `**/*.ts`/`**/*.tsx`), no linteado (fuera del alcance por defecto de `next lint`). Se dejó ese archivo huerto sin tocar (legado, fuera de alcance de esta fase).
- **Cambio**: `npm uninstall axios` eliminó exactamente 2 paquetes (`axios` y su única dependencia `follow-redirects`); ninguna otra versión cambió (Next, React, TypeScript, Tailwind, ESLint, Vitest, Playwright intactos).
- **Auditoría** (estado histórico registrado en esta fase, no vigente): `npm audit` pasó de 19 a 18 vulnerabilidades (3 moderate, 14→13 high, 2 critical) al retirar `axios`. Las 18 restantes eran preexistentes, no relacionadas con axios, clasificadas en el reporte de la fase (runtime vs. dev-only, con/sin salto mayor de versión) — sin acción en esta fase.
- **Nota (Fase 9G, auditoría posterior — 2026-08-18)**: la cifra de arriba es una fotografía del momento de la Fase 9B, **no el estado actual** — el conjunto de paquetes con advisories cambia con el tiempo a medida que se publican nuevos CVEs, independientemente de que el código de la app no cambie. El run de CI [`32104289551`](https://github.com/Juanmorales177809/reservas-parquei/actions/runs/32104289551) (commit `e26231e`) observó advisories en un conjunto de paquetes distinto al de esta fase (transitivos de `devDependencies`: herramientas de lint/test/build), **no corregidos** en esa auditoría ni en ninguna posterior. Según esa misma auditoría, ninguno de esos paquetes se compila en el bundle `standalone` de producción (`next build`), por lo que no llegan al artefacto desplegado — pero siguen sin resolverse en el árbol de dependencias.
- **Resultados**: backend sin cambios (204/204, no tocado); frontend 53/53 + type-check/lint/build limpios; E2E 26 passed / 0 failed / 0 flaky / 78 skipped.
- **OpenAPI**: sin cambios (cambio frontend-only).

### Fase 9C — Rate limiting en `POST /auth/login`

- **Commit**: `b9065c905e038a642b292cd00ff0eea2121f735b` — "security: rate limit authentication attempts".
- **Push y CI**: publicado. Run [`32096276168`](https://github.com/Juanmorales177809/reservas-parquei/actions/runs/32096276168) — `completed` / `success`.
- **Archivos**: `backend/app/api/auth.py`, `backend/app/services/rate_limit.py` (nuevo), `backend/tests/test_rate_limit.py` (nuevo), `backend/tests/test_api_auth_rate_limit.py` (nuevo).
- **Diseño**: memoria del proceso, sin dependencia nueva (se evaluaron slowapi y Redis; con un solo worker de Uvicorn confirmado — sin `--workers` en `Dockerfile`, sin réplicas en `docker-compose.yml`, CI arranca un único proceso — memoria de proceso es adecuada y slowapi no aportaría nada que memoria no diera ya).
- **Parámetros**: **5 intentos fallidos por ventana deslizante de 15 minutos**. Cuentan como intento: usuario inexistente y password incorrecta (las dos ramas 401 actuales); no cuentan errores no relacionados (422 de validación, excepciones internas).
- **Clave de limitación**: `IP + username`, sin normalizar. La IP es **exclusivamente** `request.client.host` (la conexión TCP directa) — **nunca se confía en `X-Forwarded-For`**, porque no existe ningún proxy confiable configurado en este despliegue; verificado con un test que envía ese header y confirma que no tiene efecto alguno sobre el bloqueo.
- **Comportamiento del bloqueo**: al superar el límite, `429` con mensaje genérico idéntico exista o no el usuario (sin enumeración). El chequeo de bloqueo ocurre antes de tocar la base y sin registrar nada nuevo — un cliente ya bloqueado no puede extender su propio bloqueo reintentando. Login exitoso reinicia el contador de esa clave. Cota dura de memoria (`MAX_CLAVES_RASTREADAS = 10_000`) con expulsión de la clave más antigua, para evitar crecimiento ilimitado.
- **Limitación por proceso** (documentada explícitamente en el código y aquí): **no es una solución distribuida**. Si en el futuro el backend corre con `--workers N` o múltiples réplicas, cada proceso mantiene su propio conteo y el límite efectivo se multiplica por esa cantidad de procesos. Migrar a un backend compartido (Redis u otro) queda fuera de alcance de esta fase.
- **Riesgo de IP compartida** (aceptado, documentado): `docker-compose.yml` no expone el puerto 8000 del backend al host — el backend solo es alcanzable vía el proxy de Next.js. En el despliegue Docker real, todos los usuarios comparten la IP aparente del contenedor `frontend` desde la perspectiva del backend. Un atacante que falle 5 veces contra el username de una víctima real, pasando por el mismo proxy, podría bloquear temporalmente (≤15 min) el login de esa víctima. Es consecuencia directa de la topología actual (sin proxy confiable configurado), no resoluble sin tocar infraestructura.
- **Revisión de seguridad dedicada** (sub-agente especializado): sin hallazgos HIGH/MEDIUM explotables.
- **Resultados**: backend 226/226 (204 previos + 11 unitarios + 11 de integración); frontend 53/53 (sin cambios); E2E 26 passed / 0 failed / 0 flaky / 78 skipped.
- **OpenAPI**: sin cambios — confirmado que ni `request: Request` ni el `429` nuevo se documentan (el `401` ya existente tampoco estaba documentado antes).

### Fase 9D — Handler global de excepciones no controladas

- **Commit**: `9c81fdaf9d19dcd8b824b7414f928391c4d01a7b` — "security: add global exception handler".
- **Push y CI**: publicado. Run [`32097309764`](https://github.com/Juanmorales177809/reservas-parquei/actions/runs/32097309764) — `completed` / `success`.
- **Archivos**: `backend/app/main.py`, `backend/tests/test_exception_handler.py` (nuevo).
- **Comportamiento previo** (confirmado antes de implementar, no documentado hasta ahora): el 500 por defecto de FastAPI/Starlette ya era genérico (sin traceback, sin rutas internas), pero era **texto plano** (`"Internal Server Error"`, no JSON) y **no se registraba nada en ningún log**.
- **Handler nuevo** (`@app.exception_handler(Exception)`): responde siempre `500` en JSON con un mensaje genérico y estable (`"Ha ocurrido un error interno. Inténtalo de nuevo más tarde."`), idéntico sin importar el tipo real de excepción — nunca incluye `str(exc)`, el nombre del tipo de excepción, traceback, rutas de archivo, SQL ni variables de entorno en la respuesta al cliente.
- **Logging server-side**: registra método HTTP, ruta y tipo de excepción en el mensaje, más el **traceback completo vía `exc_info`** — todo queda solo en el log del servidor, nunca en la respuesta HTTP. No se registra el cuerpo de la petición, headers, `Authorization` ni ninguna credencial (verificado con test que envía un token y un password ficticios y confirma que no aparecen en el log).
- **Request ID**: no existe infraestructura de request ID en el proyecto (verificado explícitamente antes de implementar); no se agregó una nueva para esta fase, tal como se acordó.
- **HTTPException y validaciones preservadas**: FastAPI ya registra handlers propios y más específicos para `HTTPException` y `RequestValidationError` (401/403/404/409/422/429 entre otros); esos siguen resolviéndose con su handler original, nunca con el nuevo — verificado con tests explícitos de 401 y 422 sin cambios de comportamiento.
- **Resultados**: backend 236/236 (226 previos + 10 nuevos); frontend 53/53 (sin cambios); E2E 26 passed / 0 failed / 0 flaky / 78 skipped.
- **OpenAPI**: sin cambios (un `exception_handler` no se documenta en el schema).

### Fase 9E — Refuerzo de validaciones de seguridad en schemas de usuario/auth

- **Commit**: `32db67c0d4f0717943c5b3f5e3aaced2801ac5ae` — "security: harden user schema validation". **Pendiente de push** al momento de escribir este changelog (sin ejecución de CI todavía para este commit).
- **Archivos**: `backend/app/schemas/usuario.py`, `backend/tests/openapi.snapshot.json` (regenerado), `backend/tests/test_usuario_schemas_seguridad.py` (nuevo).
- **Análisis previo**: `UsuarioResponse` no declara `password` ni `hashed_password` (ya seguro por omisión de campo, sin cambios). `UsuarioCreate` nunca se usa como body de ninguna ruta (solo como base de `AdminUsuarioCreate`); `UsuarioLogin` no tenía ninguna restricción de longitud documentada.
- **Cambios implementados** (los 4 aprobados explícitamente, con estos valores finales):
  - `UsuarioLogin.username`: `min_length=1, max_length=80` (80 = mismo máximo ya usado para username en Create/Update).
  - `UsuarioLogin.password`: `min_length=1, max_length=72` (72 = límite real de bcrypt; `passlib`+`bcrypt` trunca en silencio pasado ese byte — ver pin de `bcrypt==3.2.2` en `backend/CLAUDE.md`).
  - `UsuarioCreate.password` y `UsuarioUpdate.password`: `+ max_length=72` (mismo motivo, ambos ya tenían `min_length=6`, sin tocar ese mínimo).
  - `UsuarioCreate.email`: mismo validador de formato (`@` y `.` después de `@`) que ya tenían `AdminUsuarioCreate`/`UsuarioUpdate` — implementado moviendo el validador a la clase base `UsuarioCreate` (que `AdminUsuarioCreate` hereda), en vez de duplicar el código; comportamiento idéntico al propuesto.
- **Efecto de contrato aprobado explícitamente**: `POST /auth/login` con `username` o `password` vacíos pasa de responder `401` a responder `422` (falla la validación del schema antes de llegar a la lógica de negocio). Verificado que esos `422` **no consumen** el rate limit de la Fase 9C (los 422 nunca cuentan como intento, por diseño de ambas fases).
- **Cambios exactos en OpenAPI** (snapshot regenerado con el mecanismo documentado en `backend/tests/test_openapi_contrato.py`, nunca editado a mano): 3 cambios, correspondientes uno a uno con los 4 puntos de arriba —
  - `AdminUsuarioCreate.password`: `+ "maxLength": 72`.
  - `UsuarioLogin.username`: `+ "maxLength": 80, "minLength": 1`; `UsuarioLogin.password`: `+ "maxLength": 72, "minLength": 1`.
  - `UsuarioUpdate.password`: `+ "maxLength": 72`.
  - El validador de formato de email de `UsuarioCreate` **no genera ningún cambio en OpenAPI**: los `field_validator` de Pydantic nunca se reflejan en JSON Schema, ni antes ni ahora.
- **No implementado** (explícitamente fuera de alcance de esta fase): normalización de username, complejidad de contraseña, cambios de mensajes existentes, cambios a rate limiting/auth/cookies/JWT/frontend/Docker/CI/migraciones.
- **Resultados**: backend 267/267 (236 previos + 31 nuevos); `test_openapi_contrato.py` verde con el snapshot regenerado; frontend 53/53 + type-check/lint/build limpios (sin cambios de código, backend-only); E2E 26 passed / 0 failed / 0 flaky / 78 skipped.

### Fase 9F-A — Backend dual de autenticación (cookie HttpOnly)

- **Commit**: `49bf9f393dc80ac10c2c0498c57c0ad393247112` — "security: add dual JWT cookie authentication". **Local en `feature/soV0.1`, pendiente de push** al momento de escribir esta entrada — sin ejecución de CI todavía para este commit.
- **Archivos**: `backend/app/auth/auth.py`, `backend/app/api/auth.py`, `backend/app/deps.py`, `backend/tests/test_api_auth_cookie.py` (nuevo), `backend/tests/openapi.snapshot.json` (regenerado), `backend/app/auth/README.md` (nuevo), `backend/app/api/README.md`, `backend/app/README.md`.
- **Decisión de producto aprobada explícitamente — fase dual, no reemplazo**: `POST /auth/login` conserva `access_token` en el body (`TokenResponse` sin cambios de contrato) y además fija una cookie HttpOnly `access_token` con el mismo token, para no romper clientes existentes (frontend previo a la migración, E2E) mientras dura la transición. Los endpoints protegidos aceptan cookie **o** header `Authorization: Bearer`; cuando ambos están presentes, **el header tiene prioridad** (`app/deps.py`) — es la señal explícita de un cliente que declara sus propias credenciales por request, la cookie es un fallback ambiental para clientes de navegador.
- **Atributos de la cookie** (`app/auth/auth.py`, `atributos_cookie_acceso()`/`max_age_cookie_acceso()`): `HttpOnly=true`; `SameSite=Lax`; `Path=/`; `Domain` **no fijado** explícitamente (el navegador la asocia al host de la respuesta); `Secure=true` **solo** cuando `ENVIRONMENT=production` está confirmado explícitamente (mismo gate que HSTS/COOP desde la Fase 9A — no se activa solo por desplegar con Docker Compose); `Max-Age` igual a `ACCESS_TOKEN_EXPIRE_MINUTES * 60`, el mismo tiempo de vida que ya tenía el JWT.
- **`SameSite=Lax` es suficiente porque el navegador nunca cruza orígenes**: `frontend/next.config.js` reescribe `/api/:path*` hacia el backend en el propio servidor de Next.js; el navegador solo ve el origen del frontend. No hizo falta `SameSite=None` ni fijar `Domain` manualmente.
- **`POST /auth/logout` (nuevo)**: borra la cookie (`response.delete_cookie`), responde `204 No Content`, **no exige autenticación** y es **idempotente** (no falla si no existe cookie previa) — un cliente con sesión inválida o expirada debe poder limpiar su cookie igual.
- **Sin cambios de CORS ni de rate limiting**: el navegador real solo llega al backend vía el proxy `/api` de Next.js (mismo origen visible desde el navegador), así que la fase dual no requirió tocar `allow_credentials` de CORS (Fase 9A) ni el limitador de intentos de login (Fase 9C) — ambos quedaron explícitamente fuera de alcance y sin cambios.
- **RED → GREEN**: `backend/tests/test_api_auth_cookie.py` (22 tests) escrito primero contra el backend sin modificar (10 fallos esperados, confirmados antes de implementar), implementado hasta verde.
- **Resultados**: backend **289/289** (267 previos + 22 nuevos); frontend 53/53 + type-check/lint/build limpios (sin cambios de código, backend-only); E2E 26 passed / 0 failed / 0 flaky / 78 skipped (baseline sin cambios, fase backend-only).
- **OpenAPI**: cambio de contrato **aprobado explícitamente**. Snapshot regenerado con el mecanismo documentado en `test_openapi_contrato.py`; diff exacto verificado: **15 líneas insertadas, 0 eliminadas** — solo agrega la ruta `/auth/logout`. `TokenResponse` y el resto de paths/schemas quedaron byte-idénticos.

### Fase 9F-B — Migración de frontend y E2E a cookie HttpOnly

- **Commit**: `13c341d3c93ae86deb709aad1f5f659cdc74c9bf` — "security: migrate frontend auth to httpOnly cookie". **Local en `feature/soV0.1`, pendiente de push** al momento de escribir esta entrada — sin ejecución de CI todavía para este commit.
- **Archivos**: `frontend/src/services/api.ts`, `frontend/src/services/auth.ts`, `frontend/src/context/AuthContext.tsx`, `frontend/src/app/login/page.tsx`, `frontend/src/services/api.test.ts`, `frontend/src/context/AuthContext.test.tsx` (nuevo), `frontend/src/app/espacios/page.test.tsx`, `frontend/src/components/ProtectedRoute.test.tsx`, `frontend/e2e/global-setup.ts`, `frontend/e2e/tests/smoke/06-401.spec.ts`, `frontend/CLAUDE.md`, `frontend/e2e/CLAUDE.md`, `frontend/src/app/README.md`, `frontend/src/components/README.md`.
- **`apiFetch` (`api.ts`)**: deja de leer `localStorage.token` y de generar el header `Authorization`; envía `credentials: 'same-origin'` en cada `fetch` para que el navegador adjunte la cookie `access_token` (vía el mismo proxy `/api` de Next.js). El interceptor de 401 ya no limpia `localStorage` (no queda nada que limpiar) ni intenta manipular la cookie HttpOnly — no es posible desde JS ni es el objetivo; el backend la expira por `Max-Age` o la borra en `POST /auth/logout`.
- **Exención de `/usuarios/me` del redirect global de 401** (`RUTAS_SIN_REDIRECT_401`, junto con `/auth/login`): `AuthContext` usa `GET /usuarios/me` como sondeo pasivo de sesión al montar; un visitante anónimo en una página pública recibe 401 ahí normalmente. Sin esta exención, el interceptor global habría redirigido a `/login` a cualquier visitante anónimo de una página pública, rompiendo la navegación anónima. `ProtectedRoute` sigue siendo quien redirige en rutas protegidas cuando `isAuthenticated` es falso. Documentado en `frontend/CLAUDE.md`.
- **`AuthContext.tsx`**: ya no expone `token` (no hay valor de JWT accesible en JS). Determina la sesión con `getProfile()` (`GET /usuarios/me`) al montar, con `loading` correcto durante la consulta asíncrona (antes era síncrono, vía `localStorage`). `login()` guarda solo el `user` de la respuesta y **descarta `access_token` sin almacenarlo**. `logout()` llama `authService.logout()` (`POST /auth/logout`) y limpia el estado local siempre, incluso si la llamada de red falla (`catch` vacío + `setUser(null)` en `finally`) — bug real encontrado y corregido durante GREEN: sin ese `catch`, un fallo de red producía un *unhandled rejection* porque `Navbar.tsx` llama `logout()` sin `await`.
- **`ProtectedRoute.tsx` sin cambios**: cero diff en el componente — ya consumía `isAuthenticated`/`loading`/`user` de forma agnóstica al mecanismo de sesión subyacente; solo se ajustó el mock de su test (campo `token` retirado, ya no existe en el tipo `AuthContextValue`).
- **E2E — cookies reales, no simuladas**: `global-setup.ts` genera `storageState` con `ctx.storageState()`, que captura la cookie real que el backend fija en `POST /auth/login` (Playwright la retiene sola en el cookie-jar del `APIRequestContext`), en vez de construir `localStorage` a mano. `06-401.spec.ts` usa `context.addCookies()` en vez de `page.evaluate(() => localStorage...)` para simular una sesión inválida (una cookie HttpOnly no es accesible desde `page.evaluate`, por diseño). `frontend/e2e/fixtures/fixtures.ts` revisado, **sin cambios**: llama al backend directamente con `Authorization`, mecanismo que el backend sigue soportando (fase dual).
- **Backend dual permanece intacto**: `git diff --stat -- backend/` vacío en este commit — ningún archivo de `backend/` tocado. `TokenResponse.access_token` y el soporte de `Authorization` en `deps.py` (Fase 9F-A) **no se retiraron**; siguen siendo la vía de compatibilidad temporal (ver Fase 9G, pendiente, en "Fases pendientes" más abajo).
- **RED → GREEN**: `api.test.ts` (reescrito) y `AuthContext.test.tsx` (nuevo, no existía) escritos primero contra el código sin modificar (10 fallos esperados, confirmados antes de implementar). Hallazgo no previsto durante la implementación: 4 tests de `espacios/page.test.tsx` sembraban `localStorage` para simular sesión y quedaron rotos por el nuevo modelo asíncrono; se adaptaron mockeando `authService.getProfile`, igual que el resto de servicios de esa página.
- **Resultados backend**: **289/289**, confirmado sin tocar (`git diff --stat -- backend/` vacío); `test_openapi_contrato.py` verde (sin cambios, fase frontend/E2E-only).
- **Resultados frontend**: Vitest **66/66** (53 previos + 13 nuevos, principalmente `AuthContext.test.tsx`); `type-check`, `lint` y `build` verdes.
- **Resultados E2E**: **26 passed, 0 failed, 1 flaky recuperado por retry, 81 skipped.** El flaky (`frontend/e2e/tests/smoke/05-heatmap.spec.ts`, escenario "una reserva dentro del horario incrementa la ocupación global", proyecto `admin`) es **preexistente y no relacionado con esta fase** — la aserción que falla crea una reserva vía API directa con header `Authorization`, sin tocar cookies ni `AuthContext`, y coincide con el "1 flaky conocido" que este changelog documenta desde la Fase 9A. Antes de la corrida final fue necesario reiniciar `reservas_test` (`docker compose -f docker-compose.test.yml down -v` + `up -d --wait`): las múltiples corridas de E2E ejecutadas en la misma sesión de trabajo (Fases 9F-A y 9F-B) habían acumulado reservas en la base persistente — los specs usan offsets de fecha fijos, diseñados para no colisionar *dentro* de una corrida, no para ser idempotentes entre corridas repetidas el mismo día sin reinicio. Es el comportamiento ya documentado de la suite (`backend/tests/CLAUDE.md`, `frontend/e2e/CLAUDE.md`), no un fallo nuevo introducido por esta fase.
- **OpenAPI**: sin cambios — cambio frontend/E2E-only, ningún archivo de `backend/` tocado.

## Riesgos aceptados y limitaciones conocidas (vigentes tras Fase 9F-B)

- **CSP con `'unsafe-inline'` en `script-src`** (frontend, Fase 9A): necesario porque el App Router de Next.js 14 no soporta nonces sin `middleware.ts` adicional (no implementado, fuera de alcance). Reduce la protección contra XSS por script inline, aunque la CSP sigue bloqueando fuentes externas, `object-src`, `frame-ancestors` y fija `base-uri`/`form-action`.
- **Rate limiting no distribuido** (Fase 9C): en memoria de proceso, válido mientras el backend corra como un único proceso (confirmado hoy). Requiere Redis u otro backend compartido si se despliega con múltiples workers o réplicas.
- **Riesgo de IP compartida en el rate limiter** (Fase 9C): ver detalle en la sección de Fase 9C — un atacante detrás del mismo proxy que la víctima puede bloquearla temporalmente.
- **Timing side-channel preexistente en `POST /auth/login`** (identificado en la revisión de seguridad de la Fase 9C, no introducido por ninguna fase de esta serie ni corregido): `verify_password` (bcrypt) solo se ejecuta cuando el usuario existe, dando una diferencia de tiempo medible entre "usuario no existe" y "usuario existe, password incorrecta".
- **Sin infraestructura de request ID** (Fase 9D): no existe en el proyecto; el log de errores no controlados no incluye un identificador de correlación por falta de esa infraestructura.
- **`next`/`postcss` con advisories de `npm audit`** (Fase 9B): requieren un salto mayor de Next 14 a Next 16 (breaking change) para resolverse; fuera de alcance de esta serie.
- **`frontend/services/espacioService.js`** (hallazgo de la Fase 9B): archivo legado con `import axios from 'axios'`, fuera de `src/`, no importado por nada, no compilado ni linteado. No se eliminó (fuera de alcance); si alguna vez se importa, fallaría al resolver `axios` (ya no instalado).
- **E2E cubre solo Chromium**: Firefox/WebKit quedan como trabajo futuro (limitación preexistente a esta serie, no cambiada).
- **CSRF sin defensa adicional más allá de `SameSite=Lax`** (Fase 9F-A/9F-B): al aceptar cookie, el navegador la adjunta automáticamente en peticiones same-origin, y desde la Fase 9F-B el frontend sí envía `credentials: 'same-origin'` en cada request. `SameSite=Lax` bloquea el envío de la cookie en peticiones state-changing disparadas desde otro origen, pero no se agregó un token CSRF de doble envío ni ningún otro mecanismo adicional — decisión explícita, fuera de alcance de ambas fases. **El riesgo está mitigado, no resuelto.**
- **Dependencia del proxy same-origin de Next.js** (Fase 9F-A/9F-B): que `SameSite=Lax` sea suficiente (sin `SameSite=None` ni CORS con credentials) depende por completo de que el navegador nunca hable directo con el backend — todo pasa por el proxy `/api` de `frontend/next.config.js`. Si en el futuro un cliente accede al backend cross-origin (app móvil, `/docs` servido con CORS directo en producción, etc.), este análisis debe revisarse desde cero.
- **`access_token` en el body y `Authorization` son compatibilidad temporal, no el estado final** (Fase 9F-A/9F-B): ambos se mantuvieron activos a propósito para no romper clientes durante la migración. Frontend y E2E ya migraron a cookie (Fase 9F-B), pero el backend todavía acepta y expone ambos mecanismos. Su retiro queda para una fase de corte futura (Fase 9G, ver abajo) — no asumir que ya están deprecados o que se van a retirar automáticamente.
- **Commits `49bf9f3` (Fase 9F-A) y `13c341d` (Fase 9F-B) sin `git push`** al momento de escribir esta entrada: ambos son commits locales en `feature/soV0.1`. No existe ejecución de CI para ninguno de los dos todavía — no inventar ni asumir un resultado de CI posterior a estos commits.

## Fase 10 — Estabilización y fijado de versiones de imágenes base (2026-08-18)

Serie de sub-fases (10-B a 10-G — no existe una "Fase 10-A" documentada; el
roadmap original (`handoff-casa.md`) solo registra "Fase 10 (imágenes base
EOL de Docker)" en bloque, sin sub-fases; la numeración B–G es la usada al
ejecutar el trabajo real) sobre imágenes base de Docker próximas a EOL,
reproducibilidad de builds y compatibilidad de dependencias tras el salto de
versión, en `feature/soV0.1`. Alcance explícito de toda la serie: nunca leer,
escribir ni migrar la base de datos de desarrollo (`reservas_db`); solo
`reservas_test` (puerto 5433) es válida para pruebas e inspección.

### Fase 10-B — PostgreSQL de la base de pruebas a la versión 17

- **Commit**: `c7f8129edac2fc14ff95c30f377479f21be61885` — "build: upgrade test database to postgres 17".
- **Archivo**: `docker-compose.test.yml` (`postgres:13` → `postgres:17`, exclusivo de `reservas_test`, puerto 5433).
- PostgreSQL real verificado en el contenedor: **17.11**.
- Extensión `btree_gist` y la restricción de exclusión `reservas_sin_solapamiento` (específicas de PostgreSQL, ver `backend/CLAUDE.md`) validadas contra el servidor 17.
- **Resultados**: backend 290 passed; `test_openapi_contrato.py` 2 passed (OpenAPI sin cambios); frontend 66 passed; `type-check`, `lint` y `build` verdes; E2E 26 passed, 0 failed, 1 flaky, 81 skipped.
- Flaky: `frontend/e2e/tests/smoke/05-heatmap.spec.ts` (proyecto `admin`, "una reserva dentro del horario incrementa la ocupación global") — preexistente, ya documentado desde la Fase 9A, recuperado en retry.
- **Alcance**: únicamente `reservas_test` fue actualizada. **La base de datos de desarrollo (`reservas_db`, `docker-compose.yml`) no se tocó y sigue en PostgreSQL 13** — su eventual migración es un trabajo aparte, pospuesto explícitamente (ver Fase 10-E).

### Fase 10-C — Imagen Docker del frontend a Node 24.19.0

- **Commit**: `80164873b6ac613927e6449eba933866a03a9bef` — "build: upgrade frontend image to node 24".
- **Archivo**: `frontend/Dockerfile` (`node:20-alpine` → `node:24.19.0-alpine` en las dos etapas `builder` y `runner`; usuario no root `node` conservado sin cambios).
- Build real ejecutado y verificado: `docker build -f frontend/Dockerfile -t reservas-frontend:node24 ./frontend` (contexto `./frontend`, no la raíz del repo — el comando con contexto `.` falla porque el Dockerfile espera `package-lock.json` en la raíz del contexto, igual que ya usa `docker-compose.yml`).
- Contenedor real: `node --version` → `v24.19.0` en ambas etapas; usuario efectivo `node` (`uid=1000`).
- Smoke test contra un backend real (alias de red `backend`, `reservas_test` como base de datos): `GET /` → 200; `GET /api/espacios` (proxy `/api` de Next.js) → 200 con datos reales; `/docs` y `/openapi.json` → 200.
- **Resultados**: backend 290 passed; frontend 66 passed; `type-check`/`lint`/`build` verdes; E2E 26 passed, 0 failed, 1 flaky, 81 skipped (mismo flaky de `05-heatmap.spec.ts`).
- No se modificó CI, `package-lock.json` ni `docker-compose.yml` en esta fase.

### Fase 10-D — Imagen Docker del backend a Python 3.12 y CI

- **Commit**: `daa4dfe60087013914b99f8196ff352540139b1c` — "build: upgrade backend to python 3.12".
- **Archivos**: `backend/Dockerfile` (`python:3.10-slim` → `python:3.12-slim-bookworm`) y `.github/workflows/ci.yml` (jobs `backend` y `e2e`: `python-version: '3.10'` → `'3.12'`).
- Python real verificado en la imagen: **3.12.14**.
- **Compatibilidad passlib/bcrypt probada explícitamente** (motivo: `bcrypt==3.2.2` está pineado en `backend/requirements.txt` porque passlib no funciona con bcrypt≥4, ver `backend/CLAUDE.md`) — flujo real de la aplicación, dentro de la imagen: hash bcrypt real vía `hash_password()`, verificación de contraseña correcta (`True`), rechazo de contraseña incorrecta (`False`), usuario de prueba real creado vía `create_usuario()` contra `reservas_test`, login real (`POST /auth/login` → 200), JWT emitido en el body y cookie `access_token` (`HttpOnly`, `SameSite=Lax`, `Path=/`) emitida. Ni la contraseña, ni el hash, ni el JWT ni la cookie se registraron en ningún log.
- `backend/requirements.txt` y `backend/requirements-dev.txt` **sin cambios** — no hizo falta actualizar bcrypt, passlib ni python-jose.
- **Resultados**: backend 290 passed; `test_openapi_contrato.py` 2 passed (OpenAPI sin cambios); frontend 66 passed; E2E 26 passed, 0 failed, 1 flaky, 81 skipped (mismo flaky de `05-heatmap.spec.ts`).
- Usuario no root `appuser` (`uid=1000, gid=0`) conservado sin cambios.

### Fase 10-E — Análisis previo de la migración de PostgreSQL de desarrollo (pospuesta)

- **Sin commit — solo análisis de solo lectura, ningún archivo modificado.**
- Hallazgo determinante: el volumen `reservas_postgres_data` **no existe** en este entorno, y el stack de desarrollo (`docker-compose.yml`) **no está levantado** (sin `.env`, sin contenedores `reservas_db`/`reservas_backend`/`reservas_frontend` activos).
- No se ejecutó `docker compose up` ni `down -v` sobre el entorno de desarrollo en ningún momento de este análisis.
- **La migración de PostgreSQL de desarrollo de 13 a 17 queda pospuesta** hasta disponer de un entorno con datos reales que migrar — `docker-compose.yml` sigue declarando `postgres:13` sin cambios.
- Procedimiento futuro documentado (a ejecutar cuando exista el entorno): backup lógico con `pg_dump --format=custom` sobre el volumen 13 original, restauración en un **volumen nuevo** para PostgreSQL 17, validación completa (conteo de filas, extensión `btree_gist`, restricción `reservas_sin_solapamiento`, migraciones idempotentes, suite completa) antes de reapuntar `docker-compose.yml`. El volumen PostgreSQL 13 original debe conservarse intacto y sin modificar hasta que esa validación termine.
- **No se afirma en ningún punto que PostgreSQL de desarrollo haya sido migrado** — sigue en 13, sin cambios, en todos los entornos donde exista.

### Fase 10-F — Análisis de pinning y reproducibilidad de imágenes

- **Sin commit — solo análisis de solo lectura, ningún archivo modificado.**
- Confirmado con `docker buildx imagetools inspect` contra el registry oficial: `node:24.19.0-alpine` y `python:3.12-slim-bookworm` ya usan **tags versionados explícitos** (patch exacto y minor+variante de Debian respectivamente), no `latest`.
- Digests multi-arquitectura reales verificados para las cinco imágenes relevantes (`node:24.19.0-alpine`, `python:3.12-slim-bookworm`, `postgres:13`, `postgres:17`, `dpage/pgadmin4:latest`) — **verificados, pero no incorporados al código**: ningún `FROM`/`image:` se reescribió a formato `imagen@sha256:...`.
- **Estrategia recomendada y adoptada: tag versionado explícito, no pin por digest** — un digest congelaría también los parches de seguridad transitivos del sistema operativo base (Alpine/Debian) que el tag versionado sí sigue recibiendo automáticamente, a cambio de una ganancia de reproducibilidad que no es el patrón que sigue el resto del proyecto (sin Alembic, sin SBOM/firma de supply chain).
- PostgreSQL de desarrollo continúa declarado en `postgres:13`, sin cambios (fuera de alcance, ver Fase 10-E).
- Hallazgo que originó la Fase 10-G: `dpage/pgadmin4:latest` era la única imagen del stack sin ningún tipo de fijación de versión — resuelta a `latest` como versión real `9.17` en el momento de la verificación.
- No se modificó ningún archivo en esta fase.

### Fase 10-G — Fijado de la versión de pgAdmin

- **Commit**: `1e53307b9d1bc61003c49db5063fe4ab8e560f69` — "build: pin pgadmin image version".
- **Archivo**: `docker-compose.yml` (`dpage/pgadmin4:latest` → `dpage/pgadmin4:9.17`, única línea modificada).
- Digest verificado contra el registry oficial: `sha256:2f4ce946ddf8360680d7eff4eaba1d91859eb6b4003e6623bad5c63a322c2f4d` — **la versión `9.17` coincide exactamente con lo que `latest` resolvía en el momento de la verificación** (Fase 10-F), no es un downgrade ni un adelanto de versión.
- `docker compose config` validado (variables ficticias, sin `.env` real disponible; salida filtrada para no exponer ningún valor de `PASSWORD`/`SECRET_KEY`) — estructura YAML correcta, los 4 servicios (`db`, `backend`, `frontend`, `pgadmin`) resueltos, `db` intacto en `postgres:13`, `backend`/`frontend` sin cambios.
- **No fue posible verificar el arranque vía `docker compose up -d pgadmin`**: ese servicio depende de `db: condition: service_healthy`, que a su vez requiere el volumen `reservas_postgres_data` — inexistente en este entorno (Fase 10-E) — y no hay `.env`/`SECRET_KEY` configurados. Levantarlo por esa vía habría creado el volumen de desarrollo, prohibido explícitamente.
- Verificación alternativa: contenedor aislado y efímero (`docker run --rm dpage/pgadmin4:9.17`, sin `docker-compose.yml`, credenciales ficticias) — arrancó correctamente, imagen y digest confirmados por `docker inspect`.
- **Hallazgo durante la verificación, corregido de inmediato**: la propia imagen `dpage/pgadmin4` declara `VOLUME /var/lib/pgadmin` en su Dockerfile, así que el contenedor aislado creó un volumen anónimo aunque no se pasó `-v`. Se detuvo el contenedor (`--rm` liberó también el volumen anónimo al detenerse) y se confirmó que no quedó ningún volumen remanente (`docker volume ls`) — sin residuos.
- **No se afirma que pgAdmin haya sido validado contra una base de datos de desarrollo real** — solo se verificó de forma aislada, sin conexión a `reservas_db`.

## Estado actual (2026-08-18, tras Fase 10-G)

- **Fase 9G cerrada**: commit `6eabc92b9cfb6719884212179146cb77c7cf1871` — "test: close security audit coverage gap" (precede a toda la serie Fase 10; agrega cobertura de test a `backend/tests/test_api_auth_cookie.py` y una nota de auditoría posterior en este changelog — no debe confundirse con el corte de `access_token`/`Authorization` descrito más abajo en "Fases pendientes", que sigue sin implementar).
- **Fase 10-B, 10-C, 10-D y 10-G implementadas**, en este orden: `c7f8129edac2fc14ff95c30f377479f21be61885`, `80164873b6ac613927e6449eba933866a03a9bef`, `daa4dfe60087013914b99f8196ff352540139b1c`, `1e53307b9d1bc61003c49db5063fe4ab8e560f69`. **Actualización posterior (Fase 12A):** estos cuatro commits, junto con `f8ac24a` (documentación de la Fase 10) y `259dc59` (informe de la Fase 12), ya tienen `git push` a `origin/feature/soV0.1` — ver "Estado actual" de la Fase 12A más abajo. No hay ejecución de CI propia de este repositorio observada todavía para ninguno de ellos (no se confirmó un run de GitHub Actions); no inventar un resultado de CI no verificado.
- **Fase 10-E pospuesta**: no existe volumen de desarrollo en este entorno; la migración de PostgreSQL de desarrollo de 13 a 17 no se ha iniciado, queda condicionada a disponer de un entorno con datos reales.
- **Fase 10-F**: análisis de pinning completado, sin cambios de archivo — su único efecto práctico fue identificar el hallazgo resuelto en la Fase 10-G.
- **Flaky E2E conocido, sin cambios en toda la serie**: `frontend/e2e/tests/smoke/05-heatmap.spec.ts` (proyecto `admin`), reproducido de forma idéntica (falla en el primer intento, pasa en retry #1) en las Fases 10-B, 10-C y 10-D — mismo patrón documentado desde la Fase 9A, no introducido ni agravado por esta serie.

## Riesgos aceptados y limitaciones conocidas (vigentes tras Fase 10-G)

- **PostgreSQL de desarrollo sigue en 13**, con una migración a 17 documentada pero no ejecutada (Fase 10-E) — no confundir con `reservas_test`, que ya corre en 17 desde la Fase 10-B.
- **Ninguna imagen base está fijada por digest**, solo por tag versionado (decisión explícita de la Fase 10-F) — un futuro rebuild de `node:24.19.0-alpine` o `python:3.12-slim-bookworm` por parte de sus mantenedores (parche de seguridad del SO base) cambiará el digest resultante sin que cambie ningún archivo de este repo.
- **`docker-compose.test.yml` (`postgres:17`) no tiene fijado el minor/patch exacto** — evaluado en la Fase 10-F como tarea separada, no decidida todavía.
- Los resultados de regresión de la Fase 10 (10-B, 10-C, 10-D, 10-G) están verificados localmente, pero **sin ejecución de CI real** (sin push) — un futuro `git push` podría revelar diferencias de entorno no visibles en las verificaciones locales de esta serie.

## Fase 12A — Cierre documental: decisiones de dominio (2026-08-18)

**Fase exclusivamente documental — ningún archivo de código, test, schema, migración, OpenAPI, Docker o CI fue modificado.** Cierra el análisis funcional previo (`Auditoria_Funcional_Fase12.pdf`, commiteado en la raíz del repositorio, commit `259dc59`) con diez decisiones aprobadas explícitamente por el usuario, que fijan el rumbo de las Fases 12B–12H.

### Contraste Word vs. repositorio (resumen — detalle completo en el PDF)

El documento `Documentacion_AppReserva_Solucion-2.docx` describe un sistema distinto ("Sistema de Reservas de Laboratorios" sobre SharePoint/Power Apps/Power Automate, roles Investigador/Laboratorista, entidades Laboratorio/Equipo/Zona/Ensayo/Proyecto/Acompañante) del dominio actual de `reservas-parquei` (espacios institucionales genéricos, roles `usuario`/`gestor`/`admin`). De sus 30 reglas de negocio (RN-001 a RN-030), el análisis encontró: 10 implementadas con equivalente funcional (vocabulario distinto: espacio↔laboratorio, recurso↔equipo), 2 parciales, 13 ausentes, 2 contradictorias (RN-018, RN-019) y 3 no verificables por depender de reglas ausentes. Detalle regla por regla, con cita de archivo y línea para cada hallazgo, en `Auditoria_Funcional_Fase12.pdf`.

### Decisiones aprobadas

1. **El Word es el sistema funcional que `reservas-parquei` debe migrar** — deja de ser "documentación histórica sin relación con el roadmap" y pasa a ser la fuente funcional primaria de las Fases 12B en adelante.
2. **`aprobacion_automatica` se mantiene para cualquier usuario** — el comportamiento actual del código (ver corrección de RN-021 abajo) queda confirmado como el diseño deseado, no como un defecto a corregir. Esto formaliza una divergencia deliberada frente a RN-019 del Word (que exige aprobación siempre para solicitudes de investigador): en `reservas-parquei`, un espacio con el flag activo auto-aprueba también a `usuario`.
3. **Se implementará historial mediante soft-delete o estado histórico** — `Reserva` dejará de permitir borrado físico (hoy `DELETE /reservas/{id}` hace `db.delete()` real, `backend/app/services/reservas.py:322`); queda pendiente para 12G decidir el mecanismo exacto (ver preguntas abiertas).
4. **Se implementarán zonas y reservas multi-recurso** — nueva entidad `Zona` (N:1 `Espacio`, N:N con `Recurso`) y ruptura de la cardinalidad actual "1 reserva = 1 recurso" (`Reserva.recurso_id`, FK simple) hacia una relación 0..N. Es el cambio estructural de mayor riesgo técnico de toda la serie: rompe el contrato de OpenAPI de `Reserva`.
5. **Se implementará `Proyecto` con alta manual por administrador** — sin dependencia de archivo externo (a diferencia de DT-004 del sistema legado, que dependía de un Excel administrado por la Dirección de Investigación); evita repetir esa deuda técnica desde el diseño.
6. **El correo real es obligatorio** — se añadirá un canal SMTP/proveedor transaccional real, hoy inexistente en el backend (sin variables `SMTP_*`/`EMAIL_*` en `config.py`, sin librería de correo en `requirements.txt`). Es infraestructura nueva, no una extensión menor de `Notificacion` (hoy 100% in-app).
7. **Los informes serán mensuales, programados y persistidos** — reemplaza el dashboard on-demand actual (`GET /admin/dashboard/summary`, calculado por request) por un mecanismo periódico que genera y guarda un artefacto. Requiere infraestructura de tareas programadas hoy inexistente en el backend (sin Celery/APScheduler/cron en `requirements.txt`).
8. **La disponibilidad se validará en todas las fechas** — al implementar reservas multi-fecha (12F), se descarta explícitamente replicar DT-003 del sistema legado (que el propio Word marca como deuda de prioridad **alta**: solo valida la primera fecha del rango).
9. **Acompañantes serán entidades relacionales identificables** — nueva tabla `Acompañante` (N:1 `Reserva`), no el campo numérico `asistentes` actual, que se conserva para aforo/capacidad.
10. **Corregir ahora la documentación de RN-021** — aplicado en este mismo commit, ver siguiente apartado.

### Mapeo de roles aprobado (resuelve la pregunta abierta 1 de este mismo cierre de Fase 12A)

Añadido al cierre de la sesión del 2026-08-18, junto con las diez decisiones de arriba:

| Rol actual (`reservas-parquei`) | Rol del Word (sistema a migrar) |
| --- | --- |
| `usuario` | Investigador |
| `gestor` | Laboratorista |
| `admin` | Administrador técnico |

Esto resuelve la pregunta abierta 1 original (mapeo exacto de roles) y desbloquea 12B (visibilidad de equipos PS por rol: restringida a `gestor`/`admin`, equivalente a "solo laboratoristas" del Word). Ningún rol nuevo se crea — el catálogo `usuario`/`gestor`/`admin` (`backend/app/domain/enums.py:19-25`) se conserva sin cambios; el mapeo es una equivalencia funcional para la migración del dominio, no una migración de esquema de roles.

### RN-021 corregida

`README.md:11` documentaba el mecanismo de auto-aprobación de forma incompleta ("Aprobación automática configurable por espacio"), describiendo solo una de las dos rutas reales. Mecanismo completo, verificado en `backend/app/services/reservas.py:126-141` (función `crear_reserva`, sin cambios en esta fase):

```python
espacio_gestionado = get_managed_space_id(db, usuario) if usuario.rol == Rol.GESTOR.value else None
aprobacion_automatica = recurso.espacio.aprobacion_automatica or espacio_gestionado == recurso.espacio_id
```

Dos rutas independientes, unidas por `OR`, ambas ahora documentadas explícitamente en `README.md`:

- **Ruta 1 — flag por espacio**: si `Espacio.aprobacion_automatica` es `True` (configurable vía `PUT /espacios/gestion/configuracion`), la reserva se auto-aprueba **sin importar el rol de quien la crea** — incluye al rol `usuario`. Confirmado como comportamiento deseado por la decisión 2.
- **Ruta 2 — gestor en su propio espacio**: si quien crea la reserva es un `gestor` y el recurso pertenece al espacio que administra (`espacio_gestionado == recurso.espacio_id`), la reserva se auto-aprueba **independientemente del valor del flag**, incluso si está en `False`. Esta ruta es la que `README.md` no mencionaba antes de esta fase.

Ambas rutas conviven: un espacio puede tener el flag en `False` y aun así auto-aprobar las reservas de su propio gestor; o tener el flag en `True` y auto-aprobar también a investigadores externos. Ninguna de las dos rutas se modificó en esta fase — es documentación alcanzando al código, no un cambio de comportamiento.

### Fases 12B–12H (aprobadas, vinculadas a reglas concretas)

Roadmap aprobado a partir de las diez decisiones de arriba. Ninguna fase de esta lista está implementada; ninguna tiene alcance de código aprobado todavía — cada una requeriría su propia aprobación explícita de cambio de contrato (OpenAPI, schemas, migraciones) antes de tocar código, igual que el resto de fases de este proyecto.

- **12B — Modalidad de espacio y equipos PS**: campo de modalidad (equipos/zonas/mixto) y correo propio en `Espacio` (RN-006, RN-007); campo booleano PS en `Recurso` con regla de visibilidad restringida a `gestor`/`admin` (equivalente a "laboratorista" tras el mapeo de roles aprobado arriba) para servicio de ensayo (RN-009).
- **12C — Entidad Zona y multi-recurso por reserva**: tabla `Zona` (N:1 `Espacio`), relación N:N `Zona`↔`Recurso`, y la ruptura de `Reserva` de "1 recurso" a "0..N recursos/zonas" (RN-011, RN-016; decisión 4). El cambio de mayor riesgo técnico — toca el contrato de OpenAPI de `Reserva`.
- **12D — Tipo de reserva académico y Proyectos**: campo de tipo (investigación/grado/servicio de ensayo) en `Reserva`; entidad `Proyecto` con alta manual por administrador, sin dependencia de archivo externo (RN-012, RN-013, RN-014, RN-015; decisión 5).
- **12E — Acompañantes y ensayos**: tabla `Acompañante` (N:1 `Reserva`, entidad relacional identificable — decisión 9); tabla `Ensayo` (N:1 `Zona`) y su selección durante la reserva (RN-015, RN-016). Depende de 12C (Zona debe existir).
- **12F — Reservas multi-fecha**: aceptar rango/lista de fechas en una sola solicitud, con validación de disponibilidad en **todas** las fechas desde el diseño (RN-025, RN-026; decisión 8, descarta replicar DT-003).
- **12G — Historial e informes mensuales**: soft-delete o estado histórico en `Reserva` (RN-018; decisión 3); mecanismo periódico de generación y persistencia de informes mensuales, con infraestructura de tareas programadas nueva (RN-027, RN-028; decisión 7).
- **12H — Canal de correo real**: implementación del canal SMTP/proveedor transaccional obligatorio (RN-022, RN-024; decisión 6), incluyendo la decisión pendiente de si sustituye o complementa las notificaciones in-app actuales.

### Riesgos y dependencias

- **Ruptura de contrato de OpenAPI en `Reserva`** (12C, 12D, 12F): agregar tipo de reserva, multi-recurso y multi-fecha cambia el schema `ReservaCreate`/`ReservaResponse` de forma incompatible con el contrato actual — cada cambio requiere aprobación explícita por separado, según la política de este repositorio (`CLAUDE.md`, "Política de cambios de API/OpenAPI").
- **Infraestructura externa nueva sin precedente en el repo**: correo real (12H) y tareas programadas (12G) no tienen ningún componente equivalente hoy — son las dos fases con mayor riesgo de introducir dependencias, variables de entorno y puntos de fallo nuevos (proveedor de correo caído, job de informe fallido) que el resto del proyecto no maneja todavía.
- **Integridad referencial de las entidades nuevas**: `Zona`, `Proyecto`, `Acompañante` y `Ensayo` deben mantener el mismo estándar que ya tiene el esquema actual (FKs reales, `CheckConstraint`, sin columnas de texto consolidado) para no reintroducir DT-006 del sistema legado (relaciones sin integridad referencial real) dentro de este propio repositorio.
- **Rendimiento de validación multi-fecha** (12F, decisión 8): validar disponibilidad en todas las fechas de un rango, en vez de solo la primera, tiene costo computacional a evaluar según el tamaño típico de rango antes de implementar.
- **Orden de dependencias entre fases**: 12C es prerrequisito de 12E (Ensayo depende de Zona). El mapeo de roles, que bloqueaba en particular a 12B (visibilidad de equipos PS por rol), ya quedó resuelto en esta misma fase (ver "Mapeo de roles aprobado" arriba).
- Ninguna de estas fases está implementada — esta fase (12A) es puramente documental.

### Cambios estructurales previstos (sin código en esta fase)

- **`Reserva`**: agregar tipo de reserva académico; romper cardinalidad 1:1 con `Recurso` hacia 1:N; agregar mecanismo de historial (soft-delete o estado); dejar de tener exactamente una `fecha`.
- **Entidades nuevas**: `Zona`, `Ensayo`, `Proyecto`, `Acompañante`.
- **`Espacio`**: nuevo campo de modalidad (equipos/zonas/mixto); nuevo campo de correo propio.
- **`Recurso`**: nuevo campo booleano PS (prestación de servicios).
- **Infraestructura nueva**: canal de correo real; mecanismo de tareas programadas para informes mensuales.
- Todo lo anterior implicará, cuando se implemente, cambios de migraciones, schemas, OpenAPI, frontend y tests — explícitamente fuera de alcance de esta fase.

### Preguntas abiertas (no resueltas por las diez decisiones)

Las diez decisiones fijan el rumbo pero dejan detalles de implementación sin resolver — no se asume ninguna respuesta:

1. ~~Mapeo exacto de roles~~ — **Resuelta** en el cierre de esta misma fase: ver "Mapeo de roles aprobado" arriba (`usuario`→Investigador, `gestor`→Laboratorista, `admin`→Administrador técnico).
2. **Alcance de "correo real obligatorio"** (decisión 6): ¿reemplaza las notificaciones in-app actuales o las complementa? ¿incluye aprobación por enlace de correo de un solo uso (RN-022/DT-005) o solo notificación informativa?
3. **Mecanismo técnico de informes programados** (decisión 7): ¿tarea programada dentro del propio backend (requiere elegir y agregar una dependencia de scheduling) o un proceso/servicio externo?
4. **Modelo exacto de soft-delete** (decisión 3): ¿un estado nuevo dentro de `EstadoReserva`, o una columna independiente (p. ej. `deleted_at`) separada del campo `estado` actual?
5. **Cardinalidad exacta de `Zona`** (decisión 4): ¿obligatoria solo para espacios de modalidad "zonas"/"mixto", o toda reserva puede tener cero zonas incluso en esa modalidad?
6. **Estructura de datos de `Acompañante`** (decisión 9): ¿qué campos lo identifican (nombre, documento, correo)? ¿tiene cuenta de usuario propia o es un registro estructurado sin cuenta?
7. **Gobernanza de `Proyecto`** (decisión 5): con alta manual por administrador, ¿el administrador vincula usuario↔proyecto al crear el proyecto, o el investigador se autoasocia a un proyecto ya existente?
8. **Orden real de implementación 12B–12H**: dado que las decisiones estructurales ya están tomadas, ¿se mantiene el orden de dependencias propuesto, o hay una prioridad de negocio distinta (por ejemplo, adelantar 12H sobre 12C)?

### Estado actual (2026-08-18, tras Fase 12A)

- **Fase 12A cerrada documentalmente y commiteada**: commit `cde3ffbe1a7f555ad59d9598d06d5605f4cb16a7` — "docs: record phase 12 domain decisions", ya en `origin/feature/soV0.1`.
- Los seis commits de la serie Fase 10 + el informe de Fase 12 (`c7f8129`, `8016487`, `daa4dfe`, `1e53307`, `f8ac24a`, `259dc59`) ya están en `origin/feature/soV0.1` — `git push` realizado.
- `Auditoria_Funcional_Fase12.pdf` (commit `259dc59`) es la fuente de evidencia detallada de todas las decisiones de esta sección.
- Además del mapeo de roles (`usuario`→Investigador, `gestor`→Laboratorista, `admin`→Administrador técnico), añadido al cierre de la sesión — ver "Mapeo de roles aprobado" arriba.
- Ninguna fase 12B–12H tenía código implementado al cierre de 12A — ver Fase 12B abajo, la primera con código real.

## Fase 12B — Modalidad del espacio, correo y equipos PS (2026-08-18)

**Backend-only**, RED → GREEN. Implementa RN-006 (modalidad de reserva del espacio), RN-007 (correo propio del espacio) y RN-009 (equipos PS), a partir de las diez decisiones aprobadas en la Fase 12A. Ningún archivo de `frontend/` fue tocado — hallazgo de compatibilidad real documentado abajo.

### Alcance y archivos

`backend/app/domain/enums.py` (nuevo `ModalidadEspacio`), `backend/app/models/espacio.py` (`modalidad_reserva`, `correo`), `backend/app/models/recurso.py` (`es_prestacion_servicio`), `backend/app/schemas/espacio.py`, `backend/app/schemas/recurso.py`, `backend/app/crud/espacios.py`, `backend/app/api/recursos.py`, `backend/app/services/reservas.py` (`validar_acceso_ps`), `backend/app/migrations.py`, `backend/tests/conftest.py`, `backend/tests/test_api_espacios.py`, `backend/tests/test_api_reservas.py`, `backend/tests/test_api_recursos.py` (nuevo), `backend/tests/test_schemas_contrato.py`, `backend/tests/openapi.snapshot.json` (regenerado), y los README de `domain/`, `models/`, `schemas/`, `api/`, `services/`, `crud/`, `tests/`.

### Las nueve decisiones de diseño (documentadas antes de codificar)

1. **Enum de modalidad**: `ModalidadEspacio` = `equipos`/`zonas`/`mixto` (minúsculas, como `EstadoEntidad`/`EstadoReserva`/`Rol` — no las mayúsculas del Word). Campo `Espacio.modalidad_reserva`, **no** `tipo_reserva`, para no colisionar con el futuro `Reserva.tipo` de la Fase 12D.
2. **Correo obligatorio para todos los espacios** de aquí en adelante (RN-007, decisión 6 de 12A) — pero la columna es `nullable` en BD para no fabricar datos falsos en espacios ya sembrados; `EspacioCreate.correo` requerido, `EspacioUpdate.correo` opcional.
3. **Formato de correo**: mismo validador manual ya usado en `UsuarioCreate`/`UsuarioUpdate`, sin añadir la dependencia `email-validator`.
4. **Nombre del campo PS**: `Recurso.es_prestacion_servicio` (booleano), descriptivo en vez de la sigla.
5. **Recursos PS existentes**: backfill `false` — ningún recurso cambia de comportamiento.
6. **Modalidad incompatible**: en 12B es solo informativa (validación de enum); sin cruce con Zona/Recurso porque Zona no existe todavía (Fase 12C) — dependencia documentada, no omitida en silencio.
7. **Respuesta no autorizado**: 401 sin sesión (ya existente); **403** para `usuario` intentando ver/reservar un recurso PS (restricción de rol, mismo criterio que "Solo puedes gestionar recursos de tu espacio").
8. **Admin (y gestor) pueden reservar PS directamente en 12B** — no hay todavía gate de "tipo de reserva" (Fase 12D). `validar_acceso_ps` queda aislada para que 12D extienda sin duplicar el gate de rol.
9. **Compatibilidad**: las tres columnas nuevas nacen con default seguro (`modalidad_reserva='equipos'`, `es_prestacion_servicio=false`, `correo` nulo) vía migración idempotente con backfill.

### RN-006 / RN-007 / RN-009 — trazabilidad

- **RN-006**: `Espacio.modalidad_reserva` (`ModalidadEspacio`), validado por `CheckConstraint ck_espacios_modalidad_reserva` a nivel de PostgreSQL, no solo en Pydantic.
- **RN-007**: `Espacio.correo`, obligatorio en `EspacioCreate`, validado con el mismo criterio de formato que `Usuario.email`.
- **RN-009**: `Recurso.es_prestacion_servicio`. Visibilidad: `GET /recursos` y `GET /recursos/{id}/disponibilidad` (antes completamente públicos) filtran/bloquean PS para `usuario`/anónimos, reutilizando `get_current_user_optional` (mismo mecanismo de RN-005, sin agregar esquema de seguridad al OpenAPI). Reserva: `validar_acceso_ps` en `services/reservas.py`, invocada desde creación (`POST /reservas`) y edición (`PATCH /reservas/{id}` al cambiar de recurso).

### Migración

Idempotente (`backend/app/migrations.py`): `ADD COLUMN IF NOT EXISTS` + backfill + `SET NOT NULL` para `espacios.modalidad_reserva` (default `'equipos'`) y `recursos.es_prestacion_servicio` (default `false`); `espacios.correo` queda nullable, sin backfill de datos falsos. `CheckConstraint ck_espacios_modalidad_reserva` agregada de forma idempotente en el mismo bloque `DO $$` que ya protege `ck_espacios_horario_atencion`/`ck_espacios_horas_antelacion`. **Verificada ejecutándola dos veces seguidas** contra el mismo esquema, sin error.

### RED → GREEN

28 tests nuevos, escritos primero contra el código sin modificar (confirmados en rojo: `TypeError: 'modalidad_reserva' is an invalid keyword argument for Espacio`), implementados hasta verde: `TestModalidadYCorreo` (10, en `test_api_espacios.py`), `test_api_recursos.py` completo (13, nuevo archivo), `TestRecursosPS` (5, en `test_api_reservas.py`). Además, 4 tests preexistentes requirieron actualización mecánica de payload/fixture para reflejar el nuevo contrato (`correo` ahora obligatorio en `EspacioCreate`): `test_crear_espacio_solo_admin` y 3 tests de `test_schemas_contrato.py`.

### Resultados

- Backend: **318/318** (290 previos + 28 nuevos).
- `test_openapi_contrato.py`: verde tras regenerar el snapshot con el mecanismo documentado. Diff revisado explícitamente: limitado a `correo`, `modalidad_reserva` (+ nuevo componente `ModalidadEspacio`) y `es_prestacion_servicio` en los schemas de `Espacio`/`Recurso` — ninguna ruta, método ni otro schema tocado.
- Frontend: Vitest 66/66, `type-check` y `lint` limpios, `build` sin cambios de output salvo el tamaño esperado de `/admin/espacios` (+0.06 kB por el campo nuevo).
- **E2E: 26 passed, 0 failed, 1 flaky (preexistente), 81 skipped.** `03-admin.spec.ts` en verde tras el ajuste de compatibilidad (ver abajo). El único flaky (`05-heatmap.spec.ts:30`, proyecto `admin`) es el mismo caso preexistente documentado desde la Fase 9A, no relacionado con esta fase.

### Compatibilidad frontend — corregida (opción A autorizada)

`frontend/src/app/admin/espacios/page.tsx:66` creaba espacios sin enviar `correo`; con `correo` obligatorio en el backend, la creación desde el panel admin real fallaba con 422. Corregido con autorización explícita separada, alcance mínimo y mecánico:

- **`frontend/src/types/espacio.ts`**: `EspacioCreate.correo: string` (obligatorio, refleja el contrato real del backend).
- **`frontend/src/app/admin/espacios/page.tsx`**: nuevo campo "Correo" (`type="email"`, `required`, `maxLength={255}`) en el formulario de creación; su valor se incluye en el payload de `crearEspacio` y se limpia tras crear con éxito. Sin cambios en edición/actualización de espacios existentes (fuera del alcance de esta corrección).
- **`frontend/e2e/tests/smoke/03-admin.spec.ts`**: el payload de creación directa vía API agrega `correo: 'espacio.e2e@example.com'` — dominio reservado para documentación/pruebas (RFC 2606), nunca un dominio institucional real.
- **RED → GREEN verificado de forma aislada**: `npx playwright test e2e/tests/smoke/03-admin.spec.ts --project=admin` — rojo antes (mismo error 422 en 2 intentos), verde después (2/2).
- **No se relajó ninguna validación backend**, no cambió la obligatoriedad de `correo` en altas nuevas, ni la compatibilidad `nullable` de espacios existentes — el ajuste es exclusivamente del lado que faltaba enviar el campo.

### Riesgos y dependencias

- El `CheckConstraint` de `modalidad_reserva` protege a nivel de PostgreSQL, no solo Pydantic — un valor inválido nunca llega a persistirse aunque se hubiera evitado la validación de schema.
- `validar_acceso_ps` queda con una responsabilidad parcial a propósito (sin el gate de tipo de reserva) — si la Fase 12D no lo extiende, un PS seguiría siendo reservable por `gestor`/`admin` sin exigir "servicio de ensayo", que es el estado intermedio esperado, no un olvido.
- **Hallazgo resuelto**: los tests de backend de esta fase (`backend/tests/test_api_espacios.py`, `backend/tests/test_schemas_contrato.py`) usaban correos ficticios con dominio `correo.itm.edu.co` — un patrón que podía coincidir con un subdominio institucional real (el dominio raíz `itm.edu.co` es el de esta institución). Se sustituyó por un dominio reservado (`example.com`, RFC 2606) en la fase de higiene de datos posterior (no se envía ningún dato real: no existe infraestructura SMTP todavía).

### Preguntas abiertas para continuar

1. Las 8 preguntas abiertas de la Fase 12A siguen sin resolver (mapeo de roles ya resuelto aparte; correo real SMTP, informes programados, soft-delete, cardinalidad de Zona, estructura de Acompañante, gobernanza de Proyecto, orden 12C–12H).
2. **Resuelto**: los dominios de prueba no reservados (`correo.itm.edu.co`, `test.com`, `ejemplo.com`) se sustituyeron por dominios reservados (`example.com`) en la fase de higiene de datos posterior (ver hallazgo arriba).

## Fase 12C — Entidad Zona y multi-recurso por reserva (en curso, 2026-08-18)

Precedida por un análisis previo de solo lectura (sin commit) que produjo el modelo propuesto, la estrategia de compatibilidad, el contrato de API objetivo, las reglas de integridad y once decisiones aprobadas explícitamente por el usuario (cardinalidad mínima de la selección, gate de modalidad, transitividad zona→recursos, unicidad funcional recurso→zona, retiro de `Reserva.recurso_id` sin alias, fórmula de capacidad efectiva, endpoint de reemplazo completo para `Zona`↔`Recurso`, visibilidad pública de `GET /zonas`, ocupación por recurso en el dashboard, y rollback de migración creado y probado). El roadmap se dividió en ocho subfases (12C-1 a 12C-8), cada una con su propio ciclo RED → GREEN y su propia aprobación de alcance.

### Fase 12C-1 — Entidad `Zona` aislada

**Backend-only, RED → GREEN.** Introduce la entidad `Zona` como tabla nueva, sin ninguna asociación con `Recurso` ni integración con `Reserva` todavía — deliberadamente aislada, para no tocar el contrato de OpenAPI ni el comportamiento de las entidades existentes en esta subfase.

**Archivos**: `backend/app/models/zona.py` (nuevo), `backend/app/models/__init__.py` (registro de `Zona`), `backend/tests/test_models_zona.py` (nuevo, 13 tests), `backend/app/models/README.md`.

**Modelo**: `id`, `nombre` (`String(100)` NOT NULL), `espacio_id` (FK `espacios.id` NOT NULL, index), `descripcion` (`Text` nullable), `capacidad` (`Integer` nullable, sin `CheckConstraint` en BD — mismo criterio que `Espacio.capacidad`/`Recurso.capacidad`, que tampoco lo tienen), `estado` (`String(20)` NOT NULL default `'activo'` + `CheckConstraint ck_zonas_estado`), `created_at`/`updated_at`, `created_by`/`updated_by` (FK `usuarios.id` NOT NULL — comportamiento real de `Recurso`, ortografía de `Espacio`). Relación `Zona.espacio` unidireccional (sin `back_populates`, ya que `app/models/espacio.py` no se modificó en esta subfase).

**Migración**: ninguna entrada manual en `app/migrations.py`. `zonas` es una tabla nueva y se crea completa (columnas + `CheckConstraint`) vía `Base.metadata.create_all()` al registrarse en `app/models/__init__.py` — mismo mecanismo ya usado por `tipos_recursos`/`usuarios_espacios` en fases anteriores. Verificado con `test_lifespan_arranque.py` (arranque idempotente en dos ciclos, sin error).

**RED → GREEN**: 13 tests nuevos en `test_models_zona.py`, escritos primero contra el código sin `Zona` (confirmados en rojo: `ModuleNotFoundError: No module named 'app.models.zona'`), implementados hasta verde: campos obligatorios (`nombre`, `espacio_id`, `created_by`, `updated_by`), `CheckConstraint` de `estado` (rechaza valores fuera de `activo/inactivo/mantenimiento`, acepta los tres válidos), `capacidad` opcional (nula, positiva, y explícitamente **no** rechazada por BD si es no-positiva — documenta la decisión de no inventar un constraint que Espacio/Recurso tampoco tienen), y la relación `Zona.espacio`.

**Resultados**: backend **331/331** (318 previos + 13 nuevos). `test_lifespan_arranque.py`: 3/3. Ningún archivo de `Reserva`, `Recurso` ni `Espacio` fue modificado — verificado por la suite completa en verde sin cambios de comportamiento en ninguno de los tres.

**Fuera de alcance de esta subfase** (confirmado explícitamente, no omitido): asociación `Zona`↔`Recurso` (12C-3), schema Pydantic/router de `Zona` (12C-2), migración de `Reserva.recurso_id` a `reserva_recursos` (12C-4), validaciones de modalidad/PS/solapamiento (12C-5), cambio de contrato de `ReservaCreate`/`ReservaResponse` (12C-6), frontend (12C-7), correo real, multi-fecha, informes.

**Riesgos**: ninguno funcional — `Zona` es una entidad huérfana desde el punto de vista de negocio hasta 12C-2. **El rollback de `Reserva.recurso_id` (decisión 11) sigue pendiente**: corresponde a la subfase 12C-4 (donde se retira esa columna), no a esta — en 12C-1 no existe ningún cambio que revertir sobre `Reserva`.

**Sin commit ni push** — pendiente de autorización explícita separada.

### Fase 12C-2 — CRUD y API de `Zona`

**Backend-only, RED → GREEN.** Expone `Zona` vía HTTP: CRUD completo (salvo `GET` de un solo elemento, deliberadamente omitido) y autorización, todavía sin asociación con `Recurso` ni integración con `Reserva`.

**Archivos**: `backend/app/schemas/zona.py` (nuevo), `backend/app/crud/zonas.py` (nuevo), `backend/app/api/zonas.py` (nuevo), `backend/app/main.py` (registro del router), `backend/tests/test_api_zonas.py` (nuevo, 33 tests), READMEs de `schemas/`, `crud/` y `api/`.

**Contrato** (pendiente de aprobación de OpenAPI, ver abajo): `ZonaCreate` (`nombre` obligatorio ≤100, `espacio_id` obligatorio, `descripcion` opcional, `capacidad` opcional `>0`, `estado` default `activo`), `ZonaUpdate` (todo opcional, sin `created_by`/`updated_by`), `ZonaResponse` (id, nombre, espacio_id, descripcion, capacidad, estado, `created_at`/`updated_at`, `created_by`/`updated_by` como enteros; sin `recursos`).

**Endpoints**: `GET /zonas?espacio_id=` (público, criterio RN-005-like: anónimo/`usuario` ven solo zonas `activo` de espacios `activo`; `gestor`/`admin` ven todo), `POST /zonas`, `PUT /zonas/{zona_id}`, `DELETE /zonas/{zona_id}` — los tres de escritura restringidos a `gestor`/`admin` (`require_resource_manager`), con `gestor` limitado a su espacio asignado (`get_managed_space_id`, mismo patrón que `Recurso`). **Deliberadamente sin `GET /zonas/{zona_id}`**: `Recurso` tampoco tiene un GET de un solo elemento; una petición a esa ruta responde 405 (el path existe para `PUT`/`DELETE`), verificado con test explícito.

**Decisiones de diseño**: `ZonaCreate.espacio_id` es obligatorio (a diferencia del opcional-con-fallback de `RecursoCreate`), así que la autorización de "gestor limitado a su espacio" se aplica como 403 explícito en vez de sustitución silenciosa. `created_by`/`updated_by` no se declaran en ningún schema de entrada (Pydantic v2 ignora campos extra no declarados) y se fijan siempre desde el usuario autenticado. `DELETE /zonas/{zona_id}` no tiene guard de dependencias — no existe todavía ninguna asociación real que consultar (`zona_recursos` es 12C-3, `reserva_zonas` es 12C-4); inventar esa consulta habría violado la instrucción explícita de no construir consultas sobre asociaciones inexistentes.

**RED → GREEN**: 33 tests nuevos en `test_api_zonas.py`, confirmados en rojo (endpoints inexistentes) antes de implementar `schemas/zona.py` + `crud/zonas.py` + `api/zonas.py` + registro en `main.py`, verde después.

**Resultados**: backend **363 passed, 1 failed** (364 tests totales: 331 previos + 33 nuevos). El único fallo es `test_openapi_contrato.py::test_openapi_coincide_con_snapshot_versionado`, **esperado y no un bug** — hay endpoints nuevos y el snapshot no se tocó. `test_models_zona.py` (13/13) y `test_lifespan_arranque.py` (3/3) sin regresión.

**Diff de OpenAPI (generado y revisado, snapshot NO sobrescrito)**: puramente aditivo — nuevos componentes `ZonaCreate`, `ZonaResponse`, `ZonaUpdate`; nuevos paths `/zonas` (`GET`, `POST`) y `/zonas/{zona_id}` (`PUT`, `DELETE`). Ningún path, método ni schema existente fue modificado. **Pendiente de aprobación explícita antes de regenerar `tests/openapi.snapshot.json`.**

**Validaciones de frontend**: no ejecutadas en esta subfase — ningún archivo de `frontend/` se modificó, y el snapshot de OpenAPI no es un artefacto que el build/type-check del frontend consuma.

**Riesgos**: ninguno funcional. El rollback de `Reserva.recurso_id` (decisión 11 del análisis de 12C) sigue pendiente — corresponde a 12C-4. La asociación `Zona`↔`Recurso` (12C-3) sigue sin implementar.

**Sin commit ni push** — pendiente de autorización explícita separada.

**Actualización posterior**: el diff de OpenAPI de esta subfase fue aprobado explícitamente por el usuario; `tests/openapi.snapshot.json` fue regenerado con el mecanismo documentado en `test_openapi_contrato.py` (376 líneas insertadas, 0 eliminadas — limitado a `ZonaCreate`/`ZonaUpdate`/`ZonaResponse` y los paths `/zonas`, `/zonas/{zona_id}`, verificado antes y después de regenerar). Backend: 364/364 (incluye `test_openapi_contrato.py` en verde).

### Fase 12C-3 — Asociación Zona↔Recurso

**Backend-only, RED → GREEN.** Introduce `zona_recursos` (asociación técnica N:N entre `Zona` y `Recurso`, con unicidad funcional que restringe cada recurso a como máximo una zona), el endpoint de reemplazo completo `PUT /zonas/{zona_id}/recursos`, y el guard de eliminación en `DELETE /zonas/{zona_id}`. Sin integración con `Reserva` todavía.

**Archivos**: `backend/app/models/zona_recurso.py` (nuevo), `backend/app/models/__init__.py` (registro), `backend/app/schemas/zona.py` (`ZonaRecursosUpdate`, `ZonaRecursosResponse`), `backend/app/crud/zonas.py` (`reemplazar_recursos_de_zona`), `backend/app/api/zonas.py` (`PUT /{zona_id}/recursos`, guard en `DELETE /{zona_id}`), `backend/tests/test_models_zona_recurso.py` (nuevo, 5 tests), `backend/tests/test_api_zonas_recursos.py` (nuevo, 12 tests), `backend/tests/test_api_zonas.py` (1 test extendido), READMEs de `models/`, `schemas/`, `crud/` y `api/`.

**Constraint aprobada**: `UniqueConstraint` sobre `recurso_id` solo (no sobre el par `zona_id`+`recurso_id`) en `zona_recursos` — la tabla sigue siendo N:N estructuralmente, pero la constraint de BD impone que un recurso pertenezca, como máximo, a una zona. Mismo patrón exacto ya usado por `UsuarioEspacio.uq_usuarios_espacios_usuario`. FKs con `ondelete="CASCADE"` en ambos lados (`zona_id`, `recurso_id`) — único patrón disponible sin modificar `app/models/zona.py` ni `app/models/recurso.py` (fuera de alcance); mismo mecanismo que ya usa `Notificacion`.

**`PUT /zonas/{zona_id}/recursos`**: recibe la lista completa de `recurso_ids` y la persiste como reemplazo total (quita las asociaciones ausentes, agrega las nuevas). Validación completa antes de escribir: 404 si algún recurso no existe, 400 si algún recurso pertenece a un espacio distinto al de la zona, 409 si algún recurso ya está asociado a **otra** zona — en los tres casos, ningún cambio se persiste (atomicidad verificada con test explícito: una lista mixta de un recurso válido y uno conflictivo no deja ni siquiera el válido asociado). Lista vacía permitida (desasocia todo). Autorización idéntica al resto del router: `require_resource_manager` + `get_managed_space_id` (gestor limitado a su espacio, admin sin restricción, `usuario` 403).

**`DELETE /zonas/{zona_id}` actualizado**: ahora responde 409 si la zona tiene asociaciones en `zona_recursos`, mismo patrón que `eliminar_recurso`/`eliminar_espacio`.

**RED → GREEN**: 18 tests nuevos (5 de modelo + 12 de API + 1 extendido), confirmados en rojo (`ModuleNotFoundError: No module named 'app.models.zona_recurso'`) antes de implementar, verde después.

**Resultados**: backend **381 passed, 1 failed** de 382 (364 previos + 18 nuevos). El único fallo es `test_openapi_contrato.py::test_openapi_coincide_con_snapshot_versionado`, **esperado, no un bug** — hay un endpoint nuevo y el snapshot de esta subfase no se tocó. `test_models_zona.py` (13/13) y `test_lifespan_arranque.py` (3/3) sin regresión.

**Diff de OpenAPI (generado y revisado, snapshot NO sobrescrito)**: puramente aditivo — nuevos componentes `ZonaRecursosUpdate`, `ZonaRecursosResponse`; nuevo path `/zonas/{zona_id}/recursos` (`PUT`). Ningún path/schema existente fue modificado (94 líneas insertadas, 0 eliminadas). El nuevo 409 de `DELETE /zonas/{zona_id}` no aparece en el diff — es un cambio de comportamiento vía `HTTPException` inline, no de contrato declarado, mismo criterio que el resto de errores de este router. **Pendiente de aprobación explícita antes de regenerar `tests/openapi.snapshot.json`.**

**Riesgo aceptado y documentado (no silenciado)**: `PUT /recursos/{id}` (fuera de alcance de 12C-3, no listado en los archivos autorizados) no valida si el recurso tiene una asociación de zona antes de permitir moverlo a otro espacio; `DELETE /recursos/{id}` tampoco bloquea por asociación de zona (solo por reservas) — si se elimina, `ondelete="CASCADE"` limpia la fila de `zona_recursos` silenciosamente. Ambos requieren un guard en `api/recursos.py` en una fase posterior.

**Sin commit ni push** — pendiente de autorización explícita separada.

**Actualización posterior**: el diff de OpenAPI de esta subfase fue aprobado explícitamente por el usuario; `tests/openapi.snapshot.json` fue regenerado (94 líneas insertadas, 0 eliminadas, verificado contra el snapshot ya aprobado de 12C-2 — limitado exactamente a `ZonaRecursosUpdate`, `ZonaRecursosResponse` y `PUT /zonas/{zona_id}/recursos`). Backend: 382/382 (incluye `test_openapi_contrato.py` en verde).

## Fase 12C-4 — Migración de `Reserva.recurso_id` (en curso)

### Análisis previo y prueba ejecutable (sin código de aplicación)

Antes de escribir cualquier modelo, se entregó un análisis con: inventario real de referencias a `Reserva.recurso_id`/`Reserva.recurso` en todo el repositorio (backend, tests, frontend — incluye un hallazgo no identificado en el análisis original de 12C: `app/api/notificaciones.py` construye el texto de cada notificación leyendo `reserva.recurso.nombre`), diseño final de `reserva_recursos`/`reserva_zonas`, el SQL exacto de backfill/gate/constraints/retiro, y una **prueba ejecutada realmente contra PostgreSQL 17** (`reservas_test`) dentro de un esquema desechable (`CREATE SCHEMA proof_12c4`, eliminado al finalizar) que demostró: idempotencia del backfill y de los bloques `DO $$` de `EXCLUDE` (ejecutados dos veces cada uno); una reserva con dos recursos simultáneos sin conflicto y detección real de solapamiento (`IntegrityError` de PostgreSQL) al intentar un tercero; una reserva de zona con el mismo comportamiento; y un ensayo de rollback que reveló el caso crítico — **una reserva con más de un recurso asociado no puede volver, sin pérdida, a una sola columna `recurso_id`** — que el script de esa primera versión señalaba explícitamente (dejando `NULL` en vez de inventar un valor) pero sin abortar la operación como tal. Verificado explícitamente que `public.reservas` (columna `recurso_id`, constraint `reservas_sin_solapamiento`, todos los índices) quedó intacto tras la prueba. Cero archivos de la aplicación creados o modificados en este análisis.

**Corrección de alcance pedida por el usuario tras revisar el análisis**: el script de rollback debe **endurecerse** antes de escribirse en `migrations.py` — no basta con señalar los casos no representables, debe **abortar** la operación completa si detecta (a) alguna reserva con más de un recurso asociado, o (b) alguna reserva asociada solo por zona (sin ningún recurso), ejecutarse dentro de una única transacción, y verificar al final que el esquema resultante coincide exactamente con el esquema anterior a la migración. Explícitamente prohibido: usar un `UPDATE` parcial seguido de `SET NOT NULL` como mecanismo para ocultar reservas no representables — el rollback debe fallar de forma ruidosa, no silenciosa, ante datos que no puede revertir sin pérdida. Este endurecimiento se implementará en `migrations.py` como parte de 12C-4b, no en esta subfase (12C-4a no toca `migrations.py`).

**Secuencia de subfases aprobada** (reemplaza la numeración informal del análisis previo): 12C-4a (modelos de asociación, sin migración) → 12C-4b (creación/verificación de tablas, backfill idempotente y gates, sin retirar columna) → 12C-4c (constraints `EXCLUDE` nuevas, sin retirar columna) → 12C-4d (doble escritura controlada, todavía leyendo desde el esquema antiguo) → 12C-5 (servicios y CRUD leen las asociaciones) → 12C-6 (ruptura de contrato, dashboard y notificaciones) → 12C-4e (retiro de `recurso_id`, solo al cierre de toda la transición).

### Fase 12C-4a — Modelos de asociación `ReservaRecurso`/`ReservaZona`, aislados

**Backend-only, RED → GREEN.** Introduce `reserva_recursos` y `reserva_zonas` como tablas nuevas, completamente aisladas — sin backfill, sin lectura ni escritura desde `services/reservas.py`, sin ningún cambio en `Reserva`, `Recurso`, `Zona`, `migrations.py`, schemas, CRUD, API, dashboard, notificaciones, OpenAPI ni frontend.

**Archivos**: `backend/app/models/reserva_recurso.py` (nuevo), `backend/app/models/reserva_zona.py` (nuevo), `backend/app/models/__init__.py` (registro), `backend/tests/test_models_reserva_asociaciones.py` (nuevo, 17 tests), `backend/app/models/README.md`.

**Modelo**: ambas tablas siguen el patrón `id` PK + FK + `fecha`/`hora_inicio`/`hora_fin`/`estado` desnormalizados (necesarios para el futuro `EXCLUDE USING gist` de 12C-4c, que no puede indexar a través de un `JOIN`). Diferencias deliberadas frente a `zona_recursos` (12C-3):
- **`UniqueConstraint` por PAR** (`reserva_id`+`recurso_id`/`zona_id`), no por columna sola — un recurso o zona puede aparecer en muchas reservas distintas; solo la fila exacta no puede repetirse.
- **`recurso_id`/`zona_id` sin `ondelete="CASCADE"`** — un recurso o zona ya referenciado en una reserva no puede eliminarse silenciosamente; la FK lo bloquea con `IntegrityError` (verificado con test que aísla este caso de la restricción NOT NULL de la columna vieja `Reserva.recurso_id`, usando un recurso "ancla" distinto para la reserva base). `reserva_id` sí mantiene `ondelete="CASCADE"` en ambas tablas.
- Relaciones `reserva`/`recurso`/`zona` unidireccionales, sin `back_populates` — `app/models/reserva.py`, `recurso.py` y `zona.py` no se modificaron.

**Migración**: ninguna entrada en `migrations.py` — mismo mecanismo que toda tabla nueva de esta serie (`create_all` al registrarse en `models/__init__.py`).

**RED → GREEN**: 17 tests nuevos en `test_models_reserva_asociaciones.py`, confirmados en rojo (`ModuleNotFoundError: No module named 'app.models.reserva_recurso'`) antes de implementar, verde después. Cubren: creación básica, FK/nulabilidad (`reserva_id`/`recurso_id`/`zona_id` obligatorios y validados contra IDs inexistentes), unicidad por par (incluye la prueba explícita de que un mismo recurso SÍ puede repetirse en reservas distintas, a diferencia de `zona_recursos`), `ON DELETE CASCADE` selectivo (cascada desde `Reserva`, rechazo sin cascada desde `Recurso`/`Zona`), y `create_all` idempotente.

**Resultados**: backend **399/399** (382 previos + 17 nuevos). Sin fallo de `test_openapi_contrato.py` — correcto, ningún schema ni endpoint cambió. `test_lifespan_arranque.py`: 3/3.

**No se afirma que 12C-4 esté migrada**: `Reserva.recurso_id` sigue siendo la única fuente de verdad real; `reserva_recursos`/`reserva_zonas` existen como tablas vacías, sin ningún consumidor todavía.

**Sin commit ni push** — pendiente de autorización explícita separada.

### Fase 12C-4b — Backfill idempotente y gate de cobertura

**Backend-only, RED → GREEN.** Puebla `reserva_recursos` con exactamente una fila por cada `Reserva` histórica con `recurso_id`, y agrega un gate que aborta la migración con una excepción real de PostgreSQL si alguna reserva queda sin fila asociada. `Reserva.recurso_id`, sus índices y `reservas_sin_solapamiento` no se tocan. Sin constraints `EXCLUDE`, sin doble escritura, sin lectura desde asociaciones, sin cambios en `models/reserva.py`.

**Verificación previa (antes de tocar `migrations.py`)**: se confirmó el comportamiento real de borrado consultando `pg_constraint.confdeltype` directamente en `reservas_test` (no solo el código Python) — `reserva_id → CASCADE`, `recurso_id → NO ACTION`, `zona_id → NO ACTION`, exactamente lo aprobado en 12C-4a. No hizo falta ajustar ni modelos ni tests.

**Archivos**: `backend/app/migrations.py` (backfill + gate), `backend/tests/test_migrations_reserva_recursos.py` (nuevo, 10 tests), `backend/app/models/README.md`.

**SQL exacto** (extraído como constantes de módulo `_BACKFILL_RESERVA_RECURSOS`/`_GATE_RESERVA_RECURSOS_COMPLETO`, a diferencia del resto de `migrations.py` que usa literales inline — para que los tests puedan ejercitar el gate de forma aislada):

```sql
INSERT INTO reserva_recursos (reserva_id, recurso_id, fecha, hora_inicio, hora_fin, estado)
SELECT id, recurso_id, fecha, hora_inicio, hora_fin, estado
FROM reservas
WHERE recurso_id IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM reserva_recursos rr WHERE rr.reserva_id = reservas.id);

DO $$
DECLARE huerfanas INTEGER;
BEGIN
    SELECT COUNT(*) INTO huerfanas FROM reservas r
    WHERE NOT EXISTS (SELECT 1 FROM reserva_recursos WHERE reserva_id = r.id);
    IF huerfanas > 0 THEN
        RAISE EXCEPTION 'Backfill de reserva_recursos incompleto: % reservas sin fila asociada', huerfanas;
    END IF;
END $$;
```

Sin guard de existencia de tabla: `reserva_recursos` ya existe (creada por `create_all` antes de `migrate_resource_reservations()`), mismo criterio que el resto del archivo, que nunca verifica la existencia de una tabla ya creada por `create_all`.

**RED → GREEN**: 10 tests nuevos en `test_migrations_reserva_recursos.py`, confirmados en rojo genuinamente — se revirtió temporalmente `migrations.py` con `git stash` a su estado anterior a esta subfase, se confirmó `ImportError: cannot import name '_GATE_RESERVA_RECURSOS_COMPLETO'`, y se restauró la implementación con `git stash pop` antes de continuar. Cubren: backfill de una reserva histórica sin asociación previa, conservación exacta de `fecha`/`hora_inicio`/`hora_fin`/`estado`, correspondencia exacta 1:1 con `Reserva`, no modificación de la tabla `reservas`, idempotencia (2 y 3 ejecuciones consecutivas sin duplicar), el gate en verde cuando el backfill está completo, el gate detectando una inconsistencia simulada, y verificación explícita de que `recurso_id`/índices/`reservas_sin_solapamiento` siguen intactos tras la migración.

**Hallazgo operativo durante el desarrollo (corregido, no un defecto de la migración)**: llamar a `migrate_resource_reservations()` desde un test mientras la sesión `db` de ese test tenía una transacción implícita abierta sobre `reservas` producía un auto-deadlock de un solo hilo (la conexión de la migración esperaba un lock `ACCESS EXCLUSIVE` para el `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` que el propio test bloqueaba sin poder liberarlo, porque ambas conexiones vivían en el mismo proceso síncrono). Diagnosticado inspeccionando `pg_stat_activity` en `reservas_test`, con dos backends `idle in transaction`/`active...Lock` reales que hubo que terminar con `pg_terminate_backend` antes de poder continuar. Corregido agregando `db.commit()` explícito antes de cada llamada a `migrate_resource_reservations()` en el archivo de test; documentado ahí y en `models/README.md` como nota de aislamiento de conexión.

**Resultados**: backend **409/409** (399 previos + 10 nuevos). `test_models_reserva_asociaciones.py` (17/17) y `test_lifespan_arranque.py` (3/3) sin regresión. Sin fallo de `test_openapi_contrato.py` — ningún schema ni endpoint cambió.

**Estado verificado de `public.reservas` tras la migración**: columna `recurso_id` sigue `NOT NULL`; índices `ix_reservas_recurso_id`, `ix_reservas_recurso_fecha_estado` presentes; constraint `reservas_sin_solapamiento` presente; 0 reservas huérfanas (sin fila en `reserva_recursos`) en cada ejecución de prueba.

**Confirmaciones explícitas**: `reserva_recursos`/`reserva_zonas` contienen únicamente filas producidas por el backfill (verificado con test dedicado) — **no hay doble escritura**, ningún archivo de `services/`, `crud/`, `api/` de reservas fue tocado. **12C-4c (constraints `EXCLUDE`) sigue pendiente**, igual que 12C-4d, 12C-5, 12C-6 y el retiro final de `recurso_id` (12C-4e).

**Rollback endurecido — pendiente, no implementado en esta subfase**: el usuario pidió que el script de rollback (a) aborte explícitamente ante reservas con más de un recurso o reservas asociadas solo por zona, (b) se ejecute dentro de una única transacción, y (c) verifique que el esquema final coincide con el esquema anterior, prohibiendo el patrón "`UPDATE` parcial + `SET NOT NULL`" para ocultar casos no representables. Este endurecimiento **no se escribió en `migrations.py`** en 12C-4b — el análisis previo ya había señalado el caso crítico (reserva multi-recurso) pero sin el mecanismo de abortar exigido ahora; queda como trabajo explícito para cuando se decida implementar el rollback ejecutable completo, no como parte automática de esta subfase.

**Sin commit ni push** — pendiente de autorización explícita separada.

### Fase 12C-4c — Constraints EXCLUDE de `reserva_recursos`/`reserva_zonas`

**Backend-only, RED → GREEN.** Agrega `reserva_recursos_sin_solapamiento` y `reserva_zonas_sin_solapamiento` (`EXCLUDE USING gist`, mismo patrón que `reservas_sin_solapamiento`), de forma idempotente. `Reserva.recurso_id`, `reservas_sin_solapamiento` y todos los índices históricos siguen intactos. Sin doble escritura, sin lectura desde las asociaciones, sin cambios en `models/reserva.py`, schemas, CRUD, servicios, APIs, dashboard, notificaciones ni frontend.

**Verificación previa**: se reconfirmó `pg_constraint.confdeltype` de 12C-4a/12C-4b sin encontrar ningún cambio necesario (ya documentado en la sección de 12C-4b).

**Archivos**: `backend/app/migrations.py` (constraints `EXCLUDE` + docstring del contrato transaccional), `backend/tests/test_migrations_reserva_recursos.py` (extendido, 9 tests nuevos en `TestConstraintsExcludeSolapamiento`), `backend/app/models/README.md`.

**SQL exacto**:

```sql
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'reserva_recursos_sin_solapamiento' AND conrelid = 'reserva_recursos'::regclass
    ) THEN
        ALTER TABLE reserva_recursos
        ADD CONSTRAINT reserva_recursos_sin_solapamiento
        EXCLUDE USING gist (
            recurso_id WITH =, fecha WITH =,
            tsrange(fecha + hora_inicio, fecha + hora_fin, '[)') WITH &&
        )
        WHERE (estado IN ('esperando', 'aprobada'));
    END IF;
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'reserva_zonas_sin_solapamiento' AND conrelid = 'reserva_zonas'::regclass
    ) THEN
        ALTER TABLE reserva_zonas
        ADD CONSTRAINT reserva_zonas_sin_solapamiento
        EXCLUDE USING gist (
            zona_id WITH =, fecha WITH =,
            tsrange(fecha + hora_inicio, fecha + hora_fin, '[)') WITH &&
        )
        WHERE (estado IN ('esperando', 'aprobada'));
    END IF;
END $$;
```

`btree_gist` reutilizada (ya se crea más arriba en la misma función); sin re-declararla.

**Documentación del contrato transaccional** (agregada al docstring de `migrate_resource_reservations()`): toda la función corre dentro de una única transacción (`engine.begin()`); cualquier fallo — `RAISE EXCEPTION` del gate, violación de `EXCLUDE`, ausencia de `btree_gist` — se propaga sin capturarse y revierte *todo* lo aplicado en esa llamada, sin excepción oculta ni reintento en bucle.

**RED → GREEN**: 9 tests nuevos, confirmados en rojo comentando temporalmente solo la línea que agrega el statement de constraints en la tupla de `migrate_resource_reservations()` (sin revertir 12C-4a/12C-4b, ya aprobados) — 7 de 9 fallaron por la razón correcta (las constraints todavía no existían); verde tras restaurar la línea. **Hallazgo corregido durante el desarrollo**: las primeras versiones de varios tests reutilizaban, para la `Reserva` ancla, el mismo recurso que el recurso bajo prueba — colisionaban con la fila que el backfill de 12C-4b ya había insertado automáticamente para esa reserva, en la `UniqueConstraint(reserva_id, recurso_id)`, antes de poder ejercitar la constraint `EXCLUDE`. Corregido usando un "recurso ancla" distinto en cada test (`reserva_zonas` no tiene este problema, nunca se backfillea).

**Resultados**: backend **418/418** (409 previos + 9 nuevos). `test_models_reserva_asociaciones.py` (17/17) y `test_lifespan_arranque.py` (3/3) sin regresión. Sin fallo de `test_openapi_contrato.py`.

**Verificación final contra `pg_constraint` real** (no solo contra el código):

| Verificación | Resultado |
|---|---|
| `reserva_recursos_sin_solapamiento` | presente, `contype = 'x'` (exclusion), sobre `reserva_recursos` |
| `reserva_zonas_sin_solapamiento` | presente, `contype = 'x'`, sobre `reserva_zonas` |
| `reservas_sin_solapamiento` | presente, sin cambios |
| `reservas.recurso_id` | `NOT NULL`, sin cambios |
| `ix_reservas_recurso_id`, `ix_reservas_recurso_fecha_estado` | presentes, sin cambios |
| Sesiones bloqueadas/`idle in transaction` tras la migración | ninguna (verificado con `pg_stat_activity`, y con test dedicado) |

**Confirmaciones explícitas**: `reserva_recursos`/`reserva_zonas` siguen sin validación cruzada entre sí (una zona y uno de sus recursos pueden reservarse en el mismo horario sin que nada lo detecte — transitividad pendiente para 12C-5, verificado con test explícito). **12C-4d (doble escritura), 12C-5 (servicios/CRUD), 12C-6 (ruptura de contrato) y 12C-4e (retiro de `recurso_id`) siguen pendientes.** El rollback endurecido sigue sin implementarse — sin cambios respecto a lo señalado en 12C-4b.

**Sin commit ni push** — pendiente de autorización explícita separada.

### Fase 12C-4d — Doble escritura controlada de `reserva_recursos`

**Backend-only, RED → GREEN.** `services/reservas.py` escribe `reserva_recursos` al crear y al modificar reservas singulares, manteniendo una única fila por reserva sincronizada con `reservas.recurso_id`, `fecha`, `hora_inicio`, `hora_fin` y `estado`. Los consumidores siguen leyendo desde el esquema histórico (`Reserva.recurso`); NO se habilita multi-recurso ni reservas solo por zona; `reserva_zonas` no se escribe. Sin cambios en `models/`, schemas, rutas, OpenAPI, `migrations.py`, dashboard, notificaciones ni frontend.

**Archivos**: `backend/app/services/reservas.py` (`_sincronizar_reserva_recurso()` nueva — crea o actualiza la única fila, nunca duplica, nunca hace commit/rollback — invocada en `crear_reserva`, `actualizar_reserva`, `cambiar_estado` y `cancelar_reserva_usuario`; `_es_conflicto_solapamiento` ampliada a `reserva_recursos_sin_solapamiento`), `backend/tests/test_doble_escritura_reserva_recursos.py` (nuevo, 16 tests), `backend/app/services/README.md`.

**Diseño**: `eliminar_reserva` no requiere cambio (`reserva_recursos.reserva_id` lleva `ON DELETE CASCADE`, 12C-4a). El flujo de servicio sigue siendo el dueño de commit/rollback (`preparar_reserva`/`confirmar_cambios_reserva` flush/commit, `_traducir_error_integridad` rollback + 409): ante un `IntegrityError` en el commit (p. ej. la constraint `reserva_recursos_sin_solapamiento` de 12C-4c), la transacción se revierte completa — reserva y fila asociada como una sola unidad, sin filas parciales. Una reserva histórica backfillada por 12C-4b actualiza su fila existente en lugar de duplicarla.

**RED → GREEN**: 16 tests nuevos (creación, recurso, fecha/hora, estados, solapamiento por la constraint histórica y por la nueva, fallo de integridad sin filas parciales, reserva histórica backfilled, invariantes exactas en cada paso del ciclo de vida, ausencia de sesiones bloqueadas/`idle in transaction`) — 15 en rojo por ausencia de doble escritura (`NoResultFound` en `reserva_recursos` y `DID NOT RAISE` en los escenarios de la constraint nueva); verde tras la implementación. Un test (guard de ausencia de bloqueos) pasa correctamente en ambos estados por diseño.

**Resultados**: backend **434/434** (418 previos + 16 nuevos). `test_openapi_contrato.py`, `test_api_reservas.py`, `test_migrations_reserva_recursos.py`, `test_models_reserva_asociaciones.py`, `test_admin_dashboard_ocupacion.py`, `test_lifespan_arranque.py` sin regresión. Verificación directa contra PostgreSQL real (`pg_constraint`, `pg_stat_activity` y doble escritura real vía servicio): invariantes exactas cumplidas, `recurso_id` NOT NULL, las tres constraints `EXCLUDE` y los dos `UNIQUE` presentes, sin sesiones bloqueadas.

**Confirmaciones explícitas**: **12C-5 (servicios/CRUD leen las asociaciones), 12C-6 (ruptura de contrato/dashboard/notificaciones) y 12C-4e (retiro de `recurso_id`) NO fueron implementadas** en esta subfase. El rollback endurecido sigue pendiente (sin cambios respecto a 12C-4b/12C-4c).

**Sin commit ni push** — pendiente de autorización explícita separada.

### Fase 12C-5 — Servicios y CRUD leen desde las asociaciones

**Backend-only, RED → GREEN.** La lectura interna de la reserva por recurso y la resolución del recurso actual de una reserva pasan a `reserva_recursos` (la misma tabla que sostiene la constraint `reserva_recursos_sin_solapamiento` y la doble escritura de 12C-4d). El contrato público sigue siendo singular (`Reserva.recurso`/`recurso_id`) y no se retira la columna histórica. Dashboard, notificaciones, frontend, OpenAPI, `migrations.py`, constraints e índices históricos intactos.

**Inventario de lectores (previo a la implementación)**: `crud/reservas.py::get_reservas_bloqueantes` (por recurso), `services/reservas.py::cambiar_estado` y `::actualizar_reserva` (recurso actual) → **migrados**. `get_reservas`/`get_reservas_gestion`/`get_mis_reservas`/`get_reserva` (construyen la respuesta singular vía `Reserva.recurso`) → **conservados**. `api/admin_dashboard.py` (ocupación por recurso), `api/notificaciones.py` (`reserva.recurso.nombre`) y el guard de mover/eliminar recurso en `api/recursos.py` (`recurso.reservas`) → **conservados, fueran de alcance** (gap conocido para 12C-6; coherentes para datos singulares por la doble escritura). La consulta de espacio de `api/espacios.py` no es por recurso y no lee `recurso_id` → intacta. Ninguna consulta migrada altera la semántica pública para datos legítimos (asociación == columna para doble escritura y backfill).

**Archivos**: `backend/app/crud/reservas.py` (`get_reservas_bloqueantes` con JOIN contra `reserva_recursos` + `distinct()`; nuevo `get_recurso_ids_reserva`), `backend/app/services/reservas.py` (nuevo `_recurso_id_reserva`, usado por `cambiar_estado` y `actualizar_reserva`), `backend/tests/test_crud_reservas_lectura_asociaciones.py` (nuevo, 10 tests), `backend/app/crud/README.md`, `backend/app/services/README.md`.

**RED → GREEN**: 10 tests nuevos. RED demostrado en dos frentes: (1) `get_reservas_bloqueantes` devolvía `[]` para un recurso presente solo en la asociación; (2) `actualizar_reserva` permitía mover una reserva a un horario que solapaba otra en el recurso de la asociación (sin 409), porque la columna histórica no coincidía. Verde tras la migración. Un efecto esperado y verificado: los 4 tests de 12C-4d que ejercitaban la constraint nueva siguen pasando — el 409 que antes producía el commit ahora lo produce la validación de servicio vía asociación (mismo HTTP, mismo "sin filas parciales").

**Resultados**: backend **444/444** (434 previos + 10 nuevos). `test_openapi_contrato.py` en verde (sin cambios de contrato). Verificación directa contra PostgreSQL real: lectura por asociación confirmada en flujo legítimo y divergente, `recurso_id` NOT NULL, tres constraints `EXCLUDE` y dos `UNIQUE` presentes, sin sesiones bloqueadas/`idle in transaction`.

**Confirmaciones explícitas**: **la doble escritura de 12C-4d se mantiene** (solo cambia la lectura); **12C-6 (ruptura de contrato/dashboard/notificaciones) y 12C-4e (retiro de `recurso_id`) NO fueron implementadas.** El rollback endurecido sigue pendiente (sin cambios).

**Sin commit ni push** — pendiente de autorización explícita separada.

### Fase 12C-6 — Ruptura de contrato de Reserva (ejes plurales) y consumidores; Fase 12C-7 — Frontend y E2E

**12C-6 backend-only y 12C-7 frontend/E2E, RED → GREEN, implementadas en la misma iteración.** 12C-6 materializa la decisión 4 de la Fase 12A: rompe el contrato de `Reserva` hacia los ejes plurales, completa la validación multi-recurso/zona y migra dashboard, notificaciones y guards a las asociaciones. 12C-7 migra los consumidores del frontend y los fixtures/specs E2E al payload nuevo. El cambio de OpenAPI de 12C-6 fue aprobado explícitamente; el snapshot se regeneró únicamente después de verificar por script estructural y por diff que no cambiaba ninguna ruta ni esquema de seguridad.

#### 12C-6 — Contrato y backend

**Archivos**: `backend/app/schemas/reserva.py`, `backend/app/crud/reservas.py`, `backend/app/services/reservas.py`, `backend/app/api/admin_dashboard.py`, `backend/app/api/notificaciones.py`, `backend/app/api/recursos.py`, `backend/app/models/reserva.py`, `backend/tests/conftest.py` (`payload_reserva_objetivos` + `crear_zona`/`asociar_zona_recurso`), `backend/tests/test_reservas_zonas.py` (nuevo), `backend/tests/test_dashboard_recursos_efectivos.py` (nuevo), `backend/tests/test_api_notificaciones.py`, `backend/tests/test_api_recursos.py`, `backend/tests/test_schemas_contrato.py`, `backend/tests/test_doble_escritura_reserva_recursos.py`, `backend/tests/test_crud_reservas_lectura_asociaciones.py`, `backend/tests/test_api_reservas.py`, `backend/tests/openapi.snapshot.json` (regenerado), READMEs de `schemas/`, `crud/`, `services/` y `api/`.

**Contrato plural (aprobado)**:
- `ReservaCreate` con `extra="forbid"`: el legacy `recurso_id` responde **422** (`extra_forbidden`), nunca como alias; ejes `recurso_ids`/`zona_ids` (`list[int]`, default `[]`) con al menos uno obligatorio.
- `ReservaUpdate` por ejes de **reemplazo completo** (`extra="forbid"`, todo opcional): un eje ausente conserva su conjunto; uno presente lo reemplaza entero; el conjunto final se valida en el servicio.
- `ReservaResponse` **aditiva**: gana `recurso_ids`/`zona_ids`/`zonas` (`ZonaReservaResponse`, nuevo); `recurso_id`/`recurso` se conservan como forma singular temporal (ancla) hasta 12C-4e.

**Servicio** (`services/reservas.py`): `validar_creacion` reemplazada por `_validar_objetivo`; nueva maquinaria `_resolver_objetivo`/`_resolver_efectivos`/`_capacidad_efectiva`/`_recurso_ancla`/`_validar_solapamiento_efectivos`/`_reescribir_asociaciones`/`_sincronizar_campos_asociaciones`/`_etiqueta_objetivo`; flujos migrados (`crear_reserva`, `actualizar_reserva`, `cambiar_estado`, `cancelar_reserva_usuario`). Reglas implementadas: gate de modalidad `equipos`/`zonas`/`mixto` (400 si incompatible), mismidad de espacio del conjunto (edición con `espacio_id_fijo`: 403 gestor/admin, 400 resto), **materialización zona → recursos efectivos** (directos ∪ miembros de zonas, sin duplicados, orden estable), **zona sin recursos permitida** (ancla = recurso de menor id del espacio; 400 si el espacio no tiene recursos — riesgo residual de la EXCLUDE histórica sobre el ancla documentado en `tests/test_reservas_zonas.py`), **capacidad efectiva = min(espacio, zonas definidas, recursos efectivos)**, **solapamiento transitivo** (cada efectivo contra `reserva_recursos`, cada zona contra `reserva_zonas`, con `exclude_id` en edición/aprobación), re-escritura de asociaciones dentro de una única transacción (sin filas parciales). La función `_recurso_id_reserva` de 12C-5 se retiró en favor de `crud::get_recurso_ids_reserva`/`get_zona_ids_reserva`; `validar_solapamiento` queda sin referencias (`validar_recurso_activo`/`validar_capacidad` solo las ejercitan tests unitarios).

**CRUD** (`crud/reservas.py`): nuevos `get_zona_ids_reserva`/`get_zonas_bloqueantes` (espejo de los de recurso contra `reserva_zonas`); getters de listado/individual enriquecidos con los conjuntos desde las asociaciones (`_enriquecer_con_asociaciones` + `_OPTIONS_CARGA` con `joinedload` de `recursos_asociados`/`zonas_asociadas`/`zonas`) — la respuesta es aditiva, el singular sigue leyéndose de la columna ancla.

**Dashboard/notificaciones/guares**: `recursos_mas_reservados` cuenta por **recurso efectivo** (JOIN `reserva_recursos`, `func.count(ReservaRecurso.id)`); `_etiqueta_objetivo` de notificaciones es **zona-aware** (`_query_usuario` precarga `Reserva.zonas`); `api/recursos.py::_recurso_tiene_reservas` consulta `reserva_recursos` + columna histórica para mover/eliminar un recurso (409).

**Modelos** (`models/reserva.py`): relaciones aditivas de lectura `recursos_asociados`/`zonas_asociadas` (`passive_deletes=True` + `overlaps="reserva"`) y `zonas` (many-to-many `viewonly`) — corrigió el cascade del ORM que rompía los tests de borrado de recurso/zona (22 fallos → 0) y eliminó los SAWarnings. Sin cambio de esquema.

**RED → GREEN**: tests nuevos/extendidos (conjunto, modalidad, capacidad efectiva, solapamiento transitivo, dashboard, notificaciones zona-aware, guards) escritos primero contra el código sin implementar. Tres fallos RED iniciales eran bugs de los **propios tests**, no del servicio: (1) zona sin recursos → el ancla (menor id del espacio) sí choca con una reserva directa de ese recurso por la EXCLUDE histórica, escenario corregido y documentado en `test_zona_sin_recursos_ancla_al_recurso_de_menor_id`; (2) el escenario de aprobación transitiva exigía modalidad `mixto`; (3) el escenario de gestor en zona de otro espacio exigía asociar el recurso a la zona. Ports de payload legacy: `test_doble_escritura_reserva_recursos.py`/`test_crud_reservas_lectura_asociaciones.py`/`test_api_reservas.py` pasan `recurso_ids`.

**Resultados backend**: **482/482** (444 previos + 38 nuevos/extendidos; 1 warning preexistente de Starlette). `test_openapi_contrato.py` verde con el snapshot regenerado.

**OpenAPI (12C-6, aprobado)**: snapshot regenerado con el mecanismo documentado del docstring de `test_openapi_contrato.py` tras aprobación explícita. Verificación estructural previa: `paths` idénticos, `security`/`securitySchemes` idénticos, ningún otro schema compartido alterado — únicamente `ReservaCreate`/`ReservaUpdate` (`+ additionalProperties: false`, ejes `recurso_ids`/`zona_ids`, sin `recurso_id`), `ReservaResponse` (+ `recurso_ids`/`zona_ids`/`zonas`, conservando `recurso_id`/`recurso`) y `ZonaReservaResponse` nuevo. Diff: 578 insertadas, 7 eliminadas.

#### 12C-7 — Frontend y E2E

**Archivos**: `frontend/src/types/reserva.ts` (ejes plurales; `Reserva` aditiva con `recurso_ids?`/`zona_ids?`/`zonas?`, conservando lectura singular `recurso_id`/`recurso`), `frontend/src/types/espacio.ts` (+ `modalidad_reserva`), `frontend/src/types/zona.ts` (nuevo), `frontend/src/services/zonas.ts` (nuevo), `frontend/src/app/espacios/page.tsx`, `frontend/src/app/reservas/nueva/page.tsx`, `frontend/src/app/espacios/page.test.tsx`, `frontend/e2e/fixtures/fixtures.ts`, las **8 specs** que creaban reservas (`smoke/05`, `smoke/08`, `regresion/02..05`, `07`, `08`), `frontend/e2e/README.md`. `frontend/src/app/admin/README.md` revisado y **no modificado** — no documenta estos flujos (panel admin, no reservas).

**UI**: el modal de `espacios` y el form de `reservas/nueva` soportan **modalidad equipos/zonas/mixto** con **selección múltiple** (checkboxes) de recursos y/o zonas; grilla de slots construida desde `horario_atencion` para las reservas de zona (no existe endpoint de disponibilidad de zona; la autoridad del solapamiento es el backend, 409); aviso "podés reservar una zona aunque no tenga recursos asociados" y estados vacíos por modalidad; payload siempre `recurso_ids`/`zona_ids` (nunca `recurso_id`); lectura singular conservada para mostrar el recurso creado.

**E2E**: `crearReservaApi` y los 8 specs migrados a `recurso_ids: [recurso.id]` (incl. el POST inline de `07-domingo`). Verificación real del contrato contra el backend: plural → **201**, `recurso_id` singular → **422** `extra_forbidden`, plural + `zona_ids` → 201.

**Hallazgo durante la validación E2E — colisión de offsets 12/13 (bug **preexistente** de la suite, no de la migración)**: al correr la suite completa aparecía un flaky determinista en `smoke/05-heatmap` (proyecto `admin`). Con BD limpia e instrumentación temporal (status + body) se confirmó la causa raíz: `fechaFutura(12)` y `fechaFutura(13)` convergen a la misma fecha efectiva cuando el día+12 cae domingo (2026-08-30 lo es), y ambos specs reservan el mismo recurso y 10:00–11:00 en proyectos distintos (admin y usuario) → 409 real de `reservas_sin_solapamiento` dejado en la base por la corrida anterior dentro de la misma suite. Es la misma clase de colisión ya documentada en `05-notificaciones` y en `e2e/README.md`. Fix mínimo en la spec autorizada: `05-heatmap` offset **12 → 20** (margen ≥2 días), con comentario que sigue el precedente. La corrida final se ejecutó sobre `reservas_test` recién creada (`docker compose -f docker-compose.test.yml down -v` + `up -d --wait`, limpieza manual según lo documentado) para medir conteos reales.

**Resultados frontend**: Vitest **70/70** (7 archivos; `espacios/page.test.tsx` 18 tests, incl. modalidades `zonas` y `mixto`); `type-check`, `lint` y `build` verdes.

**Resultados E2E** (`test:e2e:all` sobre BD limpia): **27 passed, 0 failed, 0 flaky, 81 skipped** (1.4 min, `workers=1`; los skips son por diseño `solo([rol])`).

**Sin commit ni push** — pendiente de autorización explícita separada.

### Fase 12C-4e — Rollback condicionado: procedimiento documentado, gates y pruebas (solo esquemas desechables)

**Backend-only, sin retirar nada todavía.** Documenta el procedimiento de rollback del modelo 12C-6 al esquema histórico como constante `_ROLLBACK_RESERVA_LEGACY` de `app/migrations.py` — **durmiente, NO conectada al arranque ni a `migrate_resource_reservations()`** (no hay mecanismo seguro de producción, por lo que el SQL se documenta y se prueba exclusivamente en esquemas desechables). NO retira `reservas.recurso_id`/`Reserva.recurso`, ni toca `reservas_sin_solapamiento`, los índices históricos, `reserva_recursos` ni `reserva_zonas`. Sin DDL destructivo contra `public`; sin commit ni push. El retiro final de `recurso_id` sigue pendiente de decisión separada.

**Archivos**: `backend/app/migrations.py` (constante `_ROLLBACK_RESERVA_LEGACY` — un único `DO` con DDL vía `EXECUTE`, esquema-agnóstico por `search_path` — más bloque de comentario del contrato y nota en el docstring de `migrate_resource_reservations()`), `backend/tests/test_migrations_rollback_12c4e.py` (nuevo, 14 tests), `backend/app/models/README.md`.

**Contrato del procedimiento (gates G0–G5, en orden, cada uno con `RAISE EXCEPTION` que propaga y revierte)**:
- **G0** idempotencia: si faltan `reserva_recursos`/`reserva_zonas` → `G0 ya_revertido` (second execution fails explicitly, sin tocar nada).
- **G1** más de un recurso por reserva (dataset no representable en una columna única).
- **G2** cualquier reserva con zona (solo-zona, mixta o zona con recursos efectivos — pérdida de la dimensión zona en el esquema antiguo).
- **G3** divergencia del ancla (`reservas.recurso_id` ≠ única fila de `reserva_recursos`) en reservas de exactamente un recurso.
- **G4/G4b** divergencias de fecha/hora/estado entre `reservas` y `reserva_recursos`/`reserva_zonas`.
- **G5** reservas huérfanas (sin ninguna asociación).

Una sola transacción (el bloque es UNA sentencia; los DDL van por `EXECUTE` en el mismo bloque). Nunca `UPDATE` parcial + `SET NOT NULL` para ocultar datos: el rollback solo progresa cuando el dataset es **exclusivamente reservas singulares coherentes** (reversible sin pérdida); la restauración de la columna desde la única asociación es no-op garantizada por G3. Restaura `reservas_sin_solapamiento` e índices históricos si faltan, luego elimina constraints/tablas nuevas. No deja sesiones bloqueadas ni `idle in transaction`.

**Prueba destructiva real ya ejecutada (resultado registrado)** — realizada contra bases PostgreSQL 17 desechables del contenedor `reservas_test_db`, creadas desde un backup del propio `reservas_test`:

- **Backup previo**: `pg_dump -Fc` de `reservas_test` → **SHA-256 `D596610D203053E26CD4506097C74AA7D5A896CA87905C02132C47B7B76C7B7D`** (artefacto conservado fuera del repo, `%LOCALAPPDATA%\\..\\Local\\Temp\\opencode\\backup_12c4e_pre.dump`). Restaurado con éxito en `proof_12c4e_restore` (estructura 12C-6 íntegra: 2 tablas de asociación, 3 EXCLUDE, `recurso_id` NOT NULL, 2 índices, `btree_gist`, tabla `zonas`, 0 filas).
- **Base de gates** (`proof_12c4e_gates`, dataset 9/9/3/1: reservas/rr/rz/zona_recursos, escenarios X1..X9): los gates detectaron exactamente lo esperado — **G1**: X2 (09-02) y X4 (09-04); **G2**: X3 (09-03 solo-zona), X4 (09-04 mixta) y X5 (09-07 zona con efectivos); **G3**: X6 (09-08); **G4**: X7 (09-09); **G5**: X8 (09-10). X1 y X9 (singulares coherentes) NO marcadas. La ejecución del cuerpo completo sobre ese dataset abortó en el primer gate: `ERROR: G1 multi_recurso no representable: reservas {10,12}` + `ROLLBACK`, con conteos intactos tras el aborto (9/9/3 y 3 EXCLUDE).
- **Base reversible** (`proof_12c4e_rollback`, solo X1+R y X9+R): (1) **aborto transaccional** — DO completo + `RAISE` forzado antes del COMMIT → `ROLLBACK` total: `reserva_recursos`/`reserva_zonas` presentes, 3 EXCLUDE, `recurso_id` NOT NULL, 2/2 filas coherentes, **0 sesiones `idle in transaction`/bloqueos**; (2) **rollback exitoso (COMMIT)**: 2 reservas intactas, 0 tablas de asociación, `reservas_sin_solapamiento` presente, índices históricos 2/2, `recurso_id` NOT NULL, `zonas`/`zona_recursos` permanecen; (3) **idempotencia**: segunda ejecución → `G0 ya_revertido` + `ROLLBACK`, sin alterar nada.
- **`public` intacto tras toda la prueba**: `reservas_test` siguió con 0 filas, 3 EXCLUDE, `recurso_id` NOT NULL. Bases desechables eliminadas; artefacto de backup conservado. `git status` limpio (solo el DOCX untracked ajeno), HEAD en `a5da4aa`, sin commit ni push.

**RED → GREEN**: los 14 tests del módulo (`test_migrations_rollback_12c4e.py`) ejercitan la constante real contra esquemas desechables (`CREATE/DROP SCHEMA` dentro de `reservas_test`, nunca `public`), incluyendo: G0 con `search_path` sin `public` (matiz descubierto en el desarrollo: `to_regclass('reserva_recursos')` resuelve el schema `public` real si el esquema desechable no tiene la tabla — por eso el test G0 deja `public` fuera de la ruta), G1, G2×3 (solo-zona/mixta/zona-con-efectivos), G3, G4, G5 (cada aborto verifica que el mensaje identifica gate + reservas y que NADA cambió), rollback reversible con restauración de esquema/conteos/NOT NULL, respeto de la constraint histórica ya existente, rollback transaccional ante error forzado post-DDL (todo revertido), ausencia de sesiones bloqueadas e idempotencia. Todos en rojo antes de escribir el procedimiento; **verdes tras proceder**: 14/14.

**Resultados backend**: **496/496** (482 previos + 14 nuevos). `test_openapi_contrato.py` en verde (sin cambio de contrato). `public` sigue con las 3 constraints EXCLUDE y `recurso_id` NOT NULL tras la corrida completa de la suite.

**Confirmaciones explícitas**: el procedimiento está documentado y probado, pero **el retiro de `reservas.recurso_id`/`Reserva.recurso` sigue sin implementarse** (pendiente de decisión explícita separada, 12C-4e fase de retiro), y el procedimiento NO se conecta al ciclo de vida de la app.

**Sin commit ni push** — pendiente de autorización explícita separada.

## Fases pendientes (no aprobadas ni iniciadas)

Del roadmap original (`handoff-casa.md`), quedan sin iniciar tras esta serie:

- **Fase 9G** (fase de corte, sin alcance formalmente aprobado todavía): evaluar retirar `access_token` del body de `TokenResponse` y el soporte del header `Authorization` en `backend/app/deps.py`, ahora que frontend y E2E ya no dependen de ellos (Fase 9F-B). Cambiaría el contrato de OpenAPI y requeriría aprobación explícita, igual que 9F-A/9F-B. También pendiente: evaluar si conviene agregar una defensa CSRF adicional (token de doble envío) antes o como parte de este corte.
- **Fase 10** (imágenes base de Docker EOL): 10-B, 10-C, 10-D y 10-G implementadas y ya en `origin/feature/soV0.1` (ver sección "Fase 10" y "Estado actual" arriba); **10-E** (migración de PostgreSQL de desarrollo 13→17) queda explícitamente pospuesta hasta disponer de un entorno con datos reales que migrar; 10-F (análisis de pinning por digest) completado sin cambios de archivo.
- **Fase 12** (migración funcional del dominio del Word): 12A cerrada documentalmente (diez decisiones + mapeo de roles). **12B implementada** (RN-006/007/009: modalidad, correo, PS — ver sección "Fase 12B" arriba), backend-only, 318/318 tests; el ajuste de compatibilidad frontend con `correo` al crear espacios se implementó y verificó en la propia 12B (opción A autorizada, sin relajar validaciones — ver sección "Fase 12B" arriba). **12C en curso**: análisis previo aprobado (once decisiones), **12C-1 implementada** (entidad `Zona` aislada, 331/331 tests), **12C-2 implementada** (CRUD/API de `Zona`, 364/364, snapshot aprobado y regenerado), **12C-3 implementada** (asociación Zona↔Recurso, 382/382, snapshot aprobado y regenerado), **12C-4a implementada** (modelos `ReservaRecurso`/`ReservaZona` aislados, 399/399), **12C-4b implementada** (backfill idempotente + gate de cobertura en `migrations.py`, 409/409), **12C-4c implementada** (constraints `EXCLUDE` `reserva_recursos_sin_solapamiento`/`reserva_zonas_sin_solapamiento`, 418/418, rollback endurecido pendiente — ver sección "Fase 12C-4" arriba) y **12C-4d implementada** (doble escritura controlada de `reserva_recursos` en `services/reservas.py`, 434/434, sin retirar `recurso_id`) y **12C-5 implementada** (servicios/CRUD leen desde las asociaciones, 444/444, sin ruptura de contrato), **12C-6 implementada** (ruptura de contrato plural de `Reserva` + dashboard/notificaciones/guares por recurso efectivo, 482/482, snapshot aprobado y regenerado) y **12C-7 implementada** (frontend y E2E con payload `recurso_ids`/`zona_ids`, Vitest 70/70 y E2E 27/0/0/81 en BD limpia — ver sección "Fase 12C-6 / Fase 12C-7" arriba) y **12C-4e documentada y probada en su parte de rollback** (procedimiento `_ROLLBACK_RESERVA_LEGACY` + gates G0–G5 + 14 tests solo contra esquemas desechables, 496/496 — ver sección "Fase 12C-4e" arriba); el retiro de `recurso_id` (12C-4e fase de retiro) y 12C-8 sin código todavía. 12D–12H: sin código todavía; quedan preguntas de implementación sin resolver (ver "Preguntas abiertas" de las Fases 12A/12B).
- Fase 11: sin alcance definido en ningún documento de este repositorio — no existe roadmap aprobado para ella. No inventar contenido hasta que se defina explícitamente.
- Deuda técnica de frontend adicional a lo ya resuelto en esta serie.
- Backlog de negocio (reglas RN-006 en adelante).
- Decidir si se actualiza `next`/`postcss` (salto mayor, ver riesgos arriba).
- Decidir si se implementa un backend de rate limiting distribuido (Redis) si el despliegue pasa a múltiples workers/réplicas.
- Decidir si se agrega infraestructura de request ID.
- Hacer `git push` de los commits `49bf9f3` (Fase 9F-A) y `13c341d` (Fase 9F-B) — pendiente de decisión del usuario, no ejecutado en ninguna de las dos fases.
- Hacer `git push` de los commits de la Fase 10 (`c7f8129`, `8016487`, `daa4dfe`, `1e53307`) y del commit documental que los describe — pendiente de decisión del usuario, no ejecutado en esta serie.
