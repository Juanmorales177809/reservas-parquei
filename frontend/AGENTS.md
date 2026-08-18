# Frontend Agent Instructions

Scope: `frontend/` (Next.js 14, App Router). Las reglas de `AGENTS.md` (raíz) aplican también aquí; en caso de conflicto sobre seguridad, la raíz tiene precedencia. Para contexto y convenciones detalladas ver `frontend/CLAUDE.md` y `frontend/e2e/CLAUDE.md` — este archivo no repite ese contenido.

Última revisión: 2026-08-18. Commit de referencia: `f73b9c3e8f17c9d49d2715411ff9021c76b5c12e`.

## Exact commands

```bash
cd frontend
npm run test         # Vitest (unitarias y de componentes)
npm run type-check   # tsc --noEmit
npm run lint         # next lint
npm run build        # next build (standalone)
```

E2E (requiere `reservas_test` levantada — ver `AGENTS.md` raíz):

```bash
npm run test:e2e            # smoke
npm run test:e2e:regresion  # smoke + regresión
npm run test:e2e:all        # suite completa — lo que corre CI también
```

## Structure

- `src/services/` — cliente de la API: `api.ts` (`apiFetch`, interceptor de 401), `auth.ts` (`login`, `getProfile`, `logout`).
- `src/context/` — `AuthContext.tsx` (sesión), `NotificationContext.tsx`.
- `src/components/` — componentes compartidos, incluye `ProtectedRoute.tsx` (guard de rutas por rol, client-side; la autorización real vive en el backend).
- `frontend/e2e/` — Playwright: `global-setup.ts`, `fixtures/`, `tests/smoke/`, `tests/regresion/`.

## Autenticación actual (estado confirmado en código — Fase 9F-B)

- La sesión vive en una **cookie HttpOnly** (`access_token`) gestionada por el navegador; JavaScript de página no puede leerla ni escribirla.
- `apiFetch` (`src/services/api.ts`) usa `credentials: 'same-origin'` en cada request para que el navegador adjunte esa cookie.
- **No leer ni escribir `localStorage.token`** (ni ninguna otra clave para el JWT/usuario) — es la fuente de verdad anterior, retirada. No reintroducir esa lectura/escritura.
- `AuthContext` determina la sesión con `GET /usuarios/me` (`authService.getProfile()`) al montar; es asíncrono, `loading` debe reflejarlo.
- `/usuarios/me` está exento del interceptor global de 401 en `api.ts` (`RUTAS_SIN_REDIRECT_401`, junto con `/auth/login`) — un 401 ahí en una página pública es normal (visitante anónimo), no dispara redirect. No quitar esta exención sin entender que rompe la navegación anónima.
- `logout()` llama `POST /auth/logout`; limpia el estado local siempre, incluso si la llamada de red falla.
- El backend mantiene `Authorization: Bearer <token>` como **compatibilidad dual temporal** — el frontend ya no lo genera, pero no asumir que el backend lo retiró (ver Fase 9G en `CHANGELOG.md`).

## E2E

- `storageState` con **cookies reales**: `frontend/e2e/global-setup.ts` usa `ctx.storageState()` sobre un `APIRequestContext` que hizo login real — no construir `localStorage` a mano en ningún fixture nuevo.
- Para simular una sesión inválida en un test, usar `context.addCookies()` (ver `frontend/e2e/tests/smoke/06-401.spec.ts`) — `page.evaluate` no puede tocar una cookie HttpOnly, por diseño.
- Revisar `frontend/e2e/fixtures/fixtures.ts` antes de asumir que un fixture nuevo necesita cookies: los fixtures que hablan directamente con el backend (`APIRequestContext` con header `Authorization`) siguen siendo válidos mientras el backend mantenga la compatibilidad dual.
- **No usar credenciales reales** en ningún fixture, spec, ni en `playwright.config.ts` — solo las ficticias ya definidas (`e2e-admin`, etc.), exclusivas del proceso E2E local.

## No cambiar contrato backend sin aprobación

Ningún cambio en `frontend/` debe asumir ni forzar un cambio de contrato del backend (rutas, schemas, campos de respuesta). Si una tarea de frontend parece requerirlo, señalarlo y pedir aprobación explícita antes de tocar `backend/`.

## Criterios de validación

- `npm run test`, `npm run type-check`, `npm run lint`, `npm run build` en verde.
- E2E relevante en verde (smoke como mínimo si se tocó autenticación o rutas protegidas).
- Ningún `console.log`/`console.error` con tokens, cookies o credenciales.
- `README.md`/`CLAUDE.md` de la carpeta tocada actualizado si el comportamiento documentado cambió.

## No verificado / pendiente

- No hay una política formal documentada sobre cuándo crear un `README.md` nuevo por carpeta (`src/context/`, `src/services/` no tienen uno propio hoy, a diferencia de `src/components/` o `src/app/*`) — no asumir que falta uno sin confirmarlo primero.
