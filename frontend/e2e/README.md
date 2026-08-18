# e2e

## Propósito

Pruebas E2E con Playwright contra el stack real local: frontend Next.js (`:3000`), backend FastAPI (`:8000`) y PostgreSQL de pruebas (`reservas_test` en `localhost:5433`). Cubren flujo público, login, roles, RN-005, reservas, disponibilidad, errores 401/403/409, dashboard, ocupación real y heatmap 07:00–19:00.

## Versión y requisitos

- `@playwright/test` **1.61.0** (exacta, sin rango), Node v24.19.0, npm 11.
- Browsers: `npx playwright install chromium`.

## Preparación de PostgreSQL (manual, externa a Playwright)

```powershell
docker compose -f docker-compose.test.yml up -d --wait   # desde la raíz del repo
```

- Solo se usa la base exclusiva `reservas_test`; nunca desarrollo ni producción.
- El lifespan del backend crea el esquema, ejecuta migraciones y aplica el seed determinista (6 espacios 07:00–19:00 lun–sáb) y el admin de pruebas vía `INITIAL_ADMIN_*`.
- **Limpieza manual y explícita** (nunca automática desde Playwright ni los tests):

```powershell
docker compose -f docker-compose.test.yml down -v
```

## Arranque

`playwright.config.ts` define dos `webServer` (backend con env de prueba y frontend `npm run dev` con `BACKEND_URL=http://localhost:8000`). Playwright los inicia automáticamente; `reuseExistingServer` permite reutilizarlos localmente.

Variables de entorno del proceso (credenciales **ficticias**, no reales):
`SECRET_KEY` (solo proceso), `INITIAL_ADMIN_USERNAME=e2e-admin`, `INITIAL_ADMIN_EMAIL=e2e-admin@test.com`, `INITIAL_ADMIN_PASSWORD=E2e-Admin-123!`.

## Ejecución

```powershell
npm run test:e2e            # smoke (10 escenarios)
npm run test:e2e:regresion  # smoke + regresión (24 escenarios)
npm run test:e2e:all        # suite completa
npm run test:e2e:report     # reporte HTML (playwright-report/)
```

## Usuarios y autenticación

- **admin**: creado por el lifespan (`INITIAL_ADMIN_*`).
- **gestor** y **usuario**: creados por `global-setup.ts` vía API del admin (con espacio asignado al gestor).
- `global-setup.ts` genera `storageState` por rol en `e2e/.auth/` (**ignorado por git**) a partir del login por API y replica el mecanismo real de la app (token y usuario en `localStorage`).
- Proyectos por rol (`anonimo`, `usuario`, `gestor`, `admin`) con contexto nuevo por test: sin estado mutable compartido.
- Al menos un test smoke valida el login real por UI (`02-login.spec.ts`).

## Determinismo y aislamiento

- `workers: 1` (base compartida) y retries 1 (2 en CI).
- Fechas relativas fijas: `fechaFutura(dias)` evita domingo y supera la anticipación de 24 h; cada test de reserva usa un offset distinto (8, 9, 11, 12, 13, 15, 16, 18, 22) para no solaparse entre tests.
- **Regla de separación de offsets**: si dos tests usan el mismo recurso (normalmente `primerRecurso`) y el mismo rango horario, sus offsets deben diferir en **al menos 2 días** entre sí. `fechaFutura` salta al día siguiente cuando el offset crudo cae domingo, así que dos offsets consecutivos (diferencia de 1) pueden converger a la misma fecha efectiva según el día de la semana en que se ejecute la suite — nunca desplaza más de 1 día, así que una separación de 2+ lo hace imposible sin importar el día real. Incidente conocido: `smoke/08-disponibilidad.spec.ts` (offset 13) y `regresion/05-notificaciones.spec.ts` (offset 14, hoy 22) colisionaban y producían un 409 real e intermitente.
- Nombres únicos por test (`sufijoUnico()`); sin dependencia del orden; sin cleanup destructivo dentro de cada test (la recreación de la base es manual).

## Reportes y trazas

- Reporter `list` + HTML; `trace: retain-on-failure`, `screenshot: only-on-failure`, video off. Artefactos en `test-results/` y `playwright-report/` (ignorados).

## Limitaciones

- Reloj real: las fechas se calculan relativas al día de ejecución (documentado; horas a mediodía evitan falsos positivos).
- "Reserva fuera de horario no cuenta en ocupación": **pendiente** — el contrato actual impide crearla por API/UI (400); está cubierta por los tests de integración del backend con inserción directa en la base.
- Solo Chromium; Firefox/WebKit y CI (GitHub Actions con services) son trabajo futuro.
- La autoridad de autorización es el backend: los escenarios de 403/409 se validan contra la API, no solo contra la UI.
- Nota: el handler global de 401 de `apiFetch` excluye la ruta `/auth/login` para que el error de credenciales inválidas sea visible (cubierto por `src/services/api.test.ts` y el smoke `02-login.spec.ts`).

## Fase de implementación

Fase 5C.
