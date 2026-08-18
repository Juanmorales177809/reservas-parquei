# frontend/e2e/CLAUDE.md

## Versión y entorno

`@playwright/test` **1.61.0** exacta (sin rango), Node v24.19.0, npm 11. Browsers: `npx playwright install chromium` (solo Chromium por ahora; Firefox/WebKit son trabajo futuro).

## Puertos y stack

- Frontend Next.js: `:3000`.
- Backend FastAPI: `:8000`.
- PostgreSQL de pruebas: `:5433`, base `reservas_test`.

## Base reservas_test

Única base permitida para E2E. Nunca desarrollo ni producción.

```bash
docker compose -f docker-compose.test.yml up -d --wait   # desde la raíz del repo
```

El lifespan del backend crea el esquema, ejecuta migraciones y aplica el seed determinista (6 espacios, horario 07:00–19:00 lunes a sábado) y el admin de pruebas vía `INITIAL_ADMIN_*`.

## Limpieza manual con down -v

```bash
docker compose -f docker-compose.test.yml down -v
```

Siempre manual y explícita. **Nunca ejecutar `down -v` automáticamente desde Playwright ni desde ningún test.**

## webServer

`playwright.config.ts` define dos `webServer`: backend (`..\backend\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000`, cwd `../backend`, con env de prueba) y frontend (`npm run dev`, con `BACKEND_URL=http://localhost:8000`). Playwright los arranca automáticamente; `reuseExistingServer: !process.env.CI` permite reutilizarlos en local.

## Global setup

`e2e/global-setup.ts` crea los usuarios `gestor` y `usuario` vía la API del admin (asignando espacio al gestor) y genera `storageState` por rol en `e2e/.auth/`.

### Cookies reales desde la Fase 9F-B (antes: localStorage simulado)

`guardarStorageState(rol)` hace login real contra `POST /auth/login` con un `APIRequestContext` de Playwright; el backend fija la cookie HttpOnly `access_token` en la respuesta y Playwright la captura sola en el cookie-jar de ese contexto (comportamiento estándar de `APIRequestContext`, sin código adicional). `await ctx.storageState()` vuelca ese cookie-jar directamente al archivo — ya no se construye `origins[].localStorage` a mano. La cookie se obtiene contra el backend en `:8000` sin `Domain` explícito, pero las cookies no se distinguen por puerto (RFC 6265): la misma cookie autentica igual cuando el navegador visita el frontend en `:3000` (`baseURL` de `playwright.config.ts`).

Antes de escribir el archivo, `guardarStorageState` hace un `GET /usuarios/me` sin header `Authorization` como verificación de humo — si eso falla, la cookie no sirve y el setup se detiene ahí en vez de generar un `storageState` inválido en silencio.

## Usuarios admin/gestor/usuario

- **admin**: creado por el lifespan del backend con `INITIAL_ADMIN_*`.
- **gestor**: creado por `global-setup.ts`, con un espacio asignado.
- **usuario**: creado por `global-setup.ts`, sin espacio asignado.

## Credenciales ficticias solo por variables de entorno

Definidas en `playwright.config.ts`: `SECRET_KEY`, `INITIAL_ADMIN_USERNAME=e2e-admin`, `INITIAL_ADMIN_EMAIL=e2e-admin@test.com`, `INITIAL_ADMIN_PASSWORD=E2e-Admin-123!`. Son ficticias y exclusivas del proceso E2E local; nunca deben usarse en desarrollo ni producción, y nunca deben sustituirse por credenciales reales.

## storageState bajo .auth/ ignorado

`e2e/.auth/*.json` se genera en `global-setup.ts` y está ignorado por git (`**/.auth/` en `.gitignore`). No commitear su contenido ni copiarlo a otra ubicación versionada.

## Contextos nuevos por test

Proyectos por rol (`anonimo`, `usuario`, `gestor`, `admin`) definidos en `playwright.config.ts`, cada uno con su propio `storageState`; cada test corre en un contexto nuevo, sin estado mutable compartido entre tests.

## Workers, retries, traces

- `workers: 1` (la base de datos es compartida entre tests, ejecución secuencial determinista).
- `retries: 1` en local, `2` en CI (`process.env.CI`).
- `trace: 'retain-on-failure'`, `screenshot: 'only-on-failure'`, `video: 'off'`. Artefactos en `test-results/` y `playwright-report/` (ambos ignorados por git).

## Comandos smoke/regresión/all

- `npm run test:e2e`: smoke.
- `npm run test:e2e:regresion`: smoke + regresión.
- `npm run test:e2e:all`: conjunto completo configurado.
- `npm run test:e2e:report`: reporte HTML (`playwright-report/`).

Para obtener el conteo real vigente, usar `npx playwright test --list`; no mantener números manuales en esta documentación (pueden desactualizarse respecto al código).

Los 4 proyectos por rol (`anonimo`, `usuario`, `gestor`, `admin`) pueden producir, por diseño, tests aplicables solo a algunos roles y skips en el resto; un skip esperado no es un fallo.

## No usar producción

Ningún test E2E debe apuntar a un `BACKEND_URL`, `DATABASE_URL` o dominio de producción. Los valores están fijos a `localhost` en `playwright.config.ts`.

## No incluir secretos, tokens ni storageState en commits

No añadir a git ningún archivo bajo `e2e/.auth/`, tokens capturados en traces, ni credenciales reales en `data/usuarios.ts` u otros fixtures.

## Fechas deterministas

`fechaFutura(dias)` evita domingo y respeta la anticipación mínima de 24 h; cada test de reserva usa un offset de días distinto (8, 9, 10, 11, 12, 13, 14, 15) para no solapar reservas entre tests. Las horas se calculan a mediodía para evitar falsos positivos por huso horario.

## Datos únicos

`sufijoUnico()` genera nombres únicos por test; los tests no dependen del orden de ejecución ni hacen cleanup destructivo dentro del propio test (la recreación de la base es manual, vía `down -v`).

## Reglas de clasificación de fallos

- La autoridad de autorización es el backend: los escenarios de 403/409 se validan contra la API, no solo contra la UI.
- Un fallo en un test de rol (401/403) debe primero descartarse contra el backend directamente antes de asumir un bug de frontend.
- "Reserva fuera de horario no cuenta en ocupación" es una limitación conocida no cubierta por E2E (el contrato actual la bloquea con 400 en API/UI); está cubierta solo por tests de integración del backend con inserción directa en la base.

## No modificar backend para hacer pasar un test sin aprobación

Si un test E2E falla por un comportamiento real del backend (no por un bug del test), no cambiar código de `backend/` para forzar que el test pase sin señalarlo y pedir aprobación explícita primero.
