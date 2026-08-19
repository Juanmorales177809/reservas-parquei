# frontend/CLAUDE.md

## Stack

Next.js 14 (App Router, código activo en `src/`), React 18, TypeScript estricto, Tailwind 4, Recharts, Axios ([package.json](package.json)).

## API proxy mediante rewrites

`next.config.js` reescribe `/api/:path*`, `/docs` y `/openapi.json` hacia `BACKEND_URL` (`http://backend:8000` en Docker, `http://localhost:8000` en local). El frontend siempre llama rutas relativas `/api`; no introducir URLs absolutas al backend en el cliente.

## BACKEND_URL

Variable de entorno consumida por `next.config.js` en build/runtime del servidor Next.js; no confundir con una variable de cliente (`NEXT_PUBLIC_*`), no está expuesta al navegador.

## AuthContext (Fase 9G: sesión por cookie HttpOnly, única vía — cookie-only)

`src/context/AuthContext.tsx`: expone `user`, `isAdmin` (`rol === 'admin'`), `canManageResources` (`rol === 'admin' | 'gestor'`), `isAuthenticated` (`Boolean(user)`), `loading`, `login`, `logout`. Ya no expone `token` (no hay valor de JWT visible en JS: vive en una cookie HttpOnly que fija el backend).

- **Al montar**: llama `GET /usuarios/me` (`authService.getProfile()`) para determinar la sesión — 200 = autenticado (`setUser`), 401/error = anónimo (`setUser(null)`), siempre `loading=false` al terminar. Es asíncrono: `loading` empieza en `true` y solo pasa a `false` cuando la consulta resuelve (antes de esta fase era síncrono, leyendo `localStorage`).
- **`login(username, password)`**: llama `authService.login`, que hace `POST /auth/login` (el backend fija la cookie vía `Set-Cookie`) y devuelve `user` del body de la respuesta. Desde la Fase 9G el body es `LoginResponse{user}` — ya no incluye `access_token` ni `token_type`. `setUser(usuario)` en éxito; el error se propaga al llamador (`login/page.tsx` lo captura y muestra).
- **`logout()`**: llama `authService.logout()` (`POST /auth/logout`, borra la cookie en el backend) y siempre hace `setUser(null)` al final (`finally`), incluso si la llamada de red falla — el fallo de red se traga silenciosamente (`catch` vacío) porque `Navbar.tsx` llama `logout()` sin `await`; dejar que el error se propagara produciría un unhandled rejection.

## Sin localStorage para la sesión (ya no es deuda XSS de la misma forma)

Desde la Fase 9F-B, ni el JWT ni el usuario se guardan en `localStorage`. El JWT vive en una cookie `access_token` HttpOnly (`backend/app/api/auth.py`, Fase 9F-A): JavaScript de página no puede leerla ni escribirla, lo que reduce (no elimina) el riesgo de robo de token por XSS respecto al modelo anterior. Sigue vigente evitar scripts de terceros. `frontend/src/services/api.ts`/`auth.ts`/`context/AuthContext.tsx` no deben volver a introducir `window.localStorage.setItem('token', ...)` ni equivalente — sería una fuente de verdad paralela a la cookie.

## apiFetch

`src/services/api.ts`. Ya no añade `Authorization` (no hay token accesible en JS y el backend ya no lo acepta desde la Fase 9G); envía `credentials: 'same-origin'` en cada `fetch` para que el navegador adjunte la cookie `access_token` en peticiones al mismo origen (el proxy `/api` de Next.js).

Interceptor 401: si `response.status === 401` y la ruta no está en `RUTAS_SIN_REDIRECT_401`, redirige a `/login` lanzando `Error('Sesión expirada...')`. Ya no limpia `localStorage` (no hay nada que limpiar) ni intenta borrar la cookie HttpOnly (no es posible ni el objetivo — el backend la expira por `Max-Age` o la borra en `POST /auth/logout`).

## Rutas excluidas del interceptor global de 401 (`RUTAS_SIN_REDIRECT_401` en `api.ts`)

- `/auth/login`: un 401 ahí son credenciales inválidas, debe llegar al formulario de `login/page.tsx` sin redirect. (Sin cambios respecto a antes de la Fase 9F-B; corregido originalmente en el commit `914cf36`.)
- `/usuarios/me` (Fase 9F-B): `AuthContext` lo usa como sondeo pasivo de sesión al montar. Un visitante anónimo en una página pública (`/`, `/espacios`, `/terminos`) SIEMPRE recibe 401 aquí — es el resultado normal de "no hay sesión", no una sesión vencida. Si este 401 disparara el interceptor global, redirigiría a `/login` a cualquier visitante anónimo de una página pública, rompiendo la navegación anónima. `ProtectedRoute` ya se encarga de redirigir a `/login` en rutas protegidas cuando `isAuthenticated` es `false`, así que ese caso queda cubierto igual, solo que sin el mensaje "Sesión expirada" (que sigue apareciendo para un 401 real en cualquier otro endpoint protegido, p. ej. una acción disparada desde una página ya autenticada cuya cookie expiró).

No quitar ninguna de las dos exclusiones sin entender el efecto: quitar `/auth/login` rompe el mensaje de credenciales inválidas; quitar `/usuarios/me` rompe la navegación anónima en páginas públicas.

## Tratamiento de 403

No hay interceptor global para 403 en `apiFetch`; cada vista/página debe capturar el error y mostrar el mensaje adecuado según su contexto (por ejemplo, gestor sin espacio asignado, o usuario intentando una acción de admin).

## Rutas públicas y protegidas

- Públicas: `/`, `/espacios`, `/login`, `/terminos`.
- Protegidas — requieren sesión; algunas requieren rol:
  - `/dashboard`
  - `/admin`
  - `/reservas/mis-reservas`
  - `/reservas/nueva`
  - `/usuarios`
  - `/admin/espacios`
  - `/admin/recursos`
  - `/admin/reservas`
  - `/admin/configuracion`
  - `/admin/control-cambios`

## Vitest/RTL

Config en `vitest.config.ts`: entorno `jsdom`, setup en `src/test/setupTests.ts`, alias `@/*` → `src/`, cobertura v8 informativa sobre `src/utils/**` y `src/components/**`. Detalle de mocks y límites en `src/test/README.md`.

## Playwright

E2E en `frontend/e2e/`; ver [frontend/e2e/CLAUDE.md](e2e/CLAUDE.md) para el detalle completo.

## Comandos

```bash
npm run type-check   # tsc --noEmit
npm run lint         # ESLint 8, next/core-web-vitals
npm run build        # next build (output: 'standalone')
npm run test         # Vitest (unitarias y de componentes)
npm run test:coverage
```

## Prohibición de tocar backend desde tareas frontend

No modificar archivos bajo `backend/` como parte de una tarea etiquetada como frontend, salvo aprobación explícita separada. Si un cambio de frontend requiere un cambio de contrato en el backend, se debe señalar y pedir confirmación antes de tocarlo.

## Heatmap 07:00–19:00

El dashboard de ocupación (`ocupacion_por_dia_hora`) usa un grid fijo de 7 días × horas 07–19. El backend expone además `ocupacion_global`, que incluye horas fuera de ese rango pero no se refleja en el heatmap (ver [CLAUDE.md](../CLAUDE.md) raíz).

## Porcentaje global basado en horario real

El porcentaje de ocupación mostrado en el dashboard debe calcularse sobre el horario real configurado por espacio (`horario_atencion`), no sobre un horario fijo asumido; el backend ya hace este cálculo — el frontend solo debe consumir y renderizar `ocupacion_global`/`ocupacion_por_dia_hora` tal como los entrega la API, sin recalcular porcentajes en el cliente.

## Selectores accesibles antes que data-testid

Al escribir tests (Vitest/RTL o Playwright), preferir selectores por rol/label/texto accesible (`getByRole`, `getByLabelText`, `getByText`) antes que `data-testid`. Usar `data-testid` solo cuando no exista un selector accesible razonable.
