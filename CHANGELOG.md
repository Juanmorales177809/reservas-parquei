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

Serie de sub-fases (9A–9E) sobre `feature/soV0.1`, sin cambiar métodos,
rutas ni payloads de la API salvo aprobación explícita caso por caso (Fase
9E). Punto de partida: 187 tests de backend, 45 de frontend, suite E2E con
1 flaky conocido.

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
- **Auditoría**: `npm audit` pasó de 19 a 18 vulnerabilidades (3 moderate, 14→13 high, 2 critical). Las 18 restantes son preexistentes, no relacionadas con axios, clasificadas en el reporte de la fase (runtime vs. dev-only, con/sin salto mayor de versión) — sin acción en esta fase.
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

## Riesgos aceptados y limitaciones conocidas (vigentes tras Fase 9E)

- **CSP con `'unsafe-inline'` en `script-src`** (frontend, Fase 9A): necesario porque el App Router de Next.js 14 no soporta nonces sin `middleware.ts` adicional (no implementado, fuera de alcance). Reduce la protección contra XSS por script inline, aunque la CSP sigue bloqueando fuentes externas, `object-src`, `frame-ancestors` y fija `base-uri`/`form-action`.
- **Rate limiting no distribuido** (Fase 9C): en memoria de proceso, válido mientras el backend corra como un único proceso (confirmado hoy). Requiere Redis u otro backend compartido si se despliega con múltiples workers o réplicas.
- **Riesgo de IP compartida en el rate limiter** (Fase 9C): ver detalle en la sección de Fase 9C — un atacante detrás del mismo proxy que la víctima puede bloquearla temporalmente.
- **Timing side-channel preexistente en `POST /auth/login`** (identificado en la revisión de seguridad de la Fase 9C, no introducido por ninguna fase de esta serie ni corregido): `verify_password` (bcrypt) solo se ejecuta cuando el usuario existe, dando una diferencia de tiempo medible entre "usuario no existe" y "usuario existe, password incorrecta".
- **Sin infraestructura de request ID** (Fase 9D): no existe en el proyecto; el log de errores no controlados no incluye un identificador de correlación por falta de esa infraestructura.
- **`next`/`postcss` con advisories de `npm audit`** (Fase 9B): requieren un salto mayor de Next 14 a Next 16 (breaking change) para resolverse; fuera de alcance de esta serie.
- **`frontend/services/espacioService.js`** (hallazgo de la Fase 9B): archivo legado con `import axios from 'axios'`, fuera de `src/`, no importado por nada, no compilado ni linteado. No se eliminó (fuera de alcance); si alguna vez se importa, fallaría al resolver `axios` (ya no instalado).
- **E2E cubre solo Chromium**: Firefox/WebKit quedan como trabajo futuro (limitación preexistente a esta serie, no cambiada).

## Fases pendientes (no aprobadas ni iniciadas)

Del roadmap original (`handoff-casa.md`), quedan sin iniciar tras esta serie:

- Fase 10 (imágenes base de Docker EOL).
- Deuda técnica de frontend adicional a lo ya resuelto en esta serie.
- Backlog de negocio (reglas RN-006 en adelante).
- Decidir si se actualiza `next`/`postcss` (salto mayor, ver riesgos arriba).
- Decidir si se implementa un backend de rate limiting distribuido (Redis) si el despliegue pasa a múltiples workers/réplicas.
- Decidir si se agrega infraestructura de request ID.
