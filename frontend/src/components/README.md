# components

## Propósito

Componentes compartidos de la interfaz: protección de rutas, indicadores de carga y gráficos del dashboard.

## Cambios realizados

| Archivo | Acción | Descripción |
|---|---|---|
| ProtectedRoute.tsx | Modificado | Soporta `roles` (con `adminOnly` como azúcar), `redirectNoAuth` y `redirectForbidden` (string o función); reemplaza los guards manuales de 10 páginas. La autorización real sigue en el backend |
| LoadingSpinner.tsx | Modificado | `role="status"`, `aria-live="polite"` y texto `sr-only` accesible |
| AdminDashboardCharts.tsx | Modificado | Leyenda del heatmap: "Heatmap visual: 07:00–19:00. El porcentaje global considera el horario completo configurado." — sin cambios de datos ni del grid |
| ProtectedRoute.test.tsx | Modificado (Fase 9F-B) | El mock de `useAuth` ya no incluye un campo `token` (retirado de `AuthContextValue` — la sesión vive en cookie HttpOnly, sin valor de token accesible en JS). `ProtectedRoute.tsx` en sí no cambió: ya consumía `isAuthenticated`/`loading`/`user`, agnóstico al mecanismo de sesión |

## Reglas de negocio relacionadas

- Contrato del heatmap (grid 7..19) conservado; `ocupacion_global` no se presenta como equivalente a las celdas.

## Decisiones técnicas

- `rolesRequeridos` memoizado con `useMemo` para evitar el warning de `exhaustive-deps`.
- Sin loops de redirección: los redirects solo se disparan cuando no se cumple la condición y el componente devuelve `null` mientras tanto.

## Pruebas

- `ProtectedRoute.test.tsx` (Vitest, contexto mockeado controlable): redirecciones, roles, adminOnly, redirectNoAuth, redirectForbidden string/función, hidratación, ausencia de loops y de peticiones de red.
- `AdminDashboardCharts.test.tsx`: grid exacto 07:00–19:00, leyenda exacta, intensidades, estado vacío y tipos del esquema.
- `npm run test`, `npm run type-check`, `npm run lint` y `npm run build` verdes.

## Impacto y compatibilidad

- Login/logout y redirecciones conservados; rutas públicas sin protección.

## Pendientes

- Tests E2E (Playwright) fuera del alcance de la fase actual.

## Fase de implementación

Fase 5A/5B.
