# frontend/CLAUDE.md

## Stack

Next.js 14 (App Router, código activo en `src/`), React 18, TypeScript estricto, Tailwind 4, Recharts, Axios ([package.json](package.json)).

## API proxy mediante rewrites

`next.config.js` reescribe `/api/:path*`, `/docs` y `/openapi.json` hacia `BACKEND_URL` (`http://backend:8000` en Docker, `http://localhost:8000` en local). El frontend siempre llama rutas relativas `/api`; no introducir URLs absolutas al backend en el cliente.

## BACKEND_URL

Variable de entorno consumida por `next.config.js` en build/runtime del servidor Next.js; no confundir con una variable de cliente (`NEXT_PUBLIC_*`), no está expuesta al navegador.

## AuthContext

`src/context/AuthContext.tsx`: expone `user`, `token`, `isAdmin` (`rol === 'admin'`), `canManageResources` (`rol === 'admin' | 'gestor'`), `isAuthenticated`, `login`, `logout`. En el montaje inicial lee `token`/`user` de `localStorage`. `login` llama `authService.login` y persiste `access_token`/`user` en `localStorage`. `logout` los limpia.

## localStorage como deuda XSS conocida

El JWT y el usuario se guardan en `localStorage` (claves `token`, `user`). Es una deuda técnica conocida y aceptada por ahora: evitar scripts de terceros y revisar con cuidado cualquier cambio que pueda introducir XSS.

## apiFetch

`src/services/api.ts`. Añade `Authorization: Bearer <token>` a cada request. Interceptor 401: si `response.status === 401` y la ruta no es `/auth/login`, limpia `token`/`user` de `localStorage` y redirige a `/login` lanzando `Error('Sesión expirada...')`.

## Diferencia entre 401 de login y 401 protegido

- `POST /auth/login` está excluido del interceptor global (`RUTA_LOGIN` en `api.ts`): un 401 ahí son credenciales inválidas y debe llegar al formulario de `login/page.tsx` sin redirect ni limpieza de `localStorage`.
- Cualquier otro endpoint: un 401 dispara el interceptor global (sesión expirada) — limpieza + redirect a `/login`.

No revertir esta exclusión sin entender que rompe el mensaje de error de credenciales inválidas (corregido en el commit `914cf36`).

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
