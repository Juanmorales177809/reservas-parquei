# admin

## Propósito

Panel de administración y gestión (admin/gestor).

## Cambios realizados

| Archivo | Acción | Descripción |
|---|---|---|
| page.tsx | Modificado | Guard manual reemplazado por `<ProtectedRoute roles={['admin','gestor']} redirectForbidden="/dashboard">`; carga de datos conservada |
| espacios/page.tsx | Modificado | Guard → `<ProtectedRoute adminOnly>`; badges de estado centralizados en `utils/estados` |
| recursos/page.tsx | Modificado | Guard → `<ProtectedRoute roles={['admin','gestor']} redirectForbidden="/dashboard">`; cast mínimo en el select de estado; `aria-label` en inputs inline |
| reservas/page.tsx | Modificado | Guard → `<ProtectedRoute roles={['admin','gestor']} redirectForbidden="/">`; badges centralizados; `aria-label` en inputs inline |
| configuracion/page.tsx | Modificado | Guard → `<ProtectedRoute roles={['gestor']} redirectForbidden={usuario => usuario.rol === 'admin' ? '/admin' : '/dashboard'}>` (conserva el redirect dinámico previo) |
| control-cambios/page.tsx | Modificado | Guard → `<ProtectedRoute adminOnly redirectForbidden="/admin">` |

## Reglas de negocio relacionadas

- Autorización de UI por rol (la autoridad real es el backend, sin cambios).

## Decisiones técnicas

- Semántica de redirects conservada exactamente por página (push→replace unificado; comportamiento equivalente documentado).

## Pruebas

- `npm run type-check`, `npm run lint`, `npm run build` verdes.

## Impacto y compatibilidad

- Login/logout, redirecciones y permisos de UI intactos; sin cambios de endpoints.

## Pendientes

- Tests de componentes (infraestructura pendiente de aprobación).

## Fase de implementación

Fase 5A.
