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

## Fases pendientes (no aprobadas ni iniciadas)

Del roadmap original (`handoff-casa.md`), quedan sin iniciar tras esta serie:

- **Fase 9G** (fase de corte, sin alcance formalmente aprobado todavía): evaluar retirar `access_token` del body de `TokenResponse` y el soporte del header `Authorization` en `backend/app/deps.py`, ahora que frontend y E2E ya no dependen de ellos (Fase 9F-B). Cambiaría el contrato de OpenAPI y requeriría aprobación explícita, igual que 9F-A/9F-B. También pendiente: evaluar si conviene agregar una defensa CSRF adicional (token de doble envío) antes o como parte de este corte.
- Fase 10 (imágenes base de Docker EOL).
- Fase 11 y Fase 12: mencionadas como continuación numérica de la serie; **sin alcance definido en ningún documento de este repositorio** — no existe roadmap aprobado más allá de la Fase 10. No inventar contenido para ellas hasta que se definan explícitamente.
- Deuda técnica de frontend adicional a lo ya resuelto en esta serie.
- Backlog de negocio (reglas RN-006 en adelante).
- Decidir si se actualiza `next`/`postcss` (salto mayor, ver riesgos arriba).
- Decidir si se implementa un backend de rate limiting distribuido (Redis) si el despliegue pasa a múltiples workers/réplicas.
- Decidir si se agrega infraestructura de request ID.
- Hacer `git push` de los commits `49bf9f3` (Fase 9F-A) y `13c341d` (Fase 9F-B) — pendiente de decisión del usuario, no ejecutado en ninguna de las dos fases.
