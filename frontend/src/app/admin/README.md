# admin

## Propósito

Panel de administración y gestión (admin/gestor).

## Cambios realizados

| Archivo | Acción | Descripción |
|---|---|---|
| page.tsx | Modificado | Guard manual reemplazado por `<ProtectedRoute roles={['admin','gestor']} redirectForbidden="/dashboard">`; carga de datos conservada |
| espacios/page.tsx | Modificado | Guard → `<ProtectedRoute adminOnly>`; badges de estado centralizados en `utils/estados` |
| espacios/page.tsx | Modificado (Fase 12B) | Nuevo campo "Correo" (`type="email"`, obligatorio) en el formulario de creación — el backend exige `EspacioCreate.correo` desde RN-007; sin este campo, la creación de espacios fallaba con 422 |
| recursos/page.tsx | Modificado | Guard → `<ProtectedRoute roles={['admin','gestor']} redirectForbidden="/dashboard">`; cast mínimo en el select de estado; `aria-label` en inputs inline |
| reservas/page.tsx | Modificado | Guard → `<ProtectedRoute roles={['admin','gestor']} redirectForbidden="/">`; badges centralizados; `aria-label` en inputs inline |
| configuracion/page.tsx | Modificado | Guard → `<ProtectedRoute roles={['gestor']} redirectForbidden={usuario => usuario.rol === 'admin' ? '/admin' : '/dashboard'}>` (conserva el redirect dinámico previo) |
| control-cambios/page.tsx | Modificado | Guard → `<ProtectedRoute adminOnly redirectForbidden="/admin">` |

## Reglas de negocio relacionadas

- Autorización de UI por rol (la autoridad real es el backend, sin cambios).
- **RN-007** (Fase 12B): correo propio del espacio, ahora recolectado en el formulario de creación.

## Decisiones técnicas

- Semántica de redirects conservada exactamente por página (push→replace unificado; comportamiento equivalente documentado).

### Fase 12B — Campo "Correo" en la creación de espacios

- **Solo el formulario de creación**, no el de edición: `EspacioUpdate.correo` ya era opcional en el backend antes de esta corrección y no formaba parte de la regresión reportada; ampliar la edición queda fuera del alcance mínimo autorizado.
- `type="email"` para validación nativa del navegador además de la validación del backend — no reemplaza ni relaja la validación real, que sigue viviendo en `EspacioCreate` (`backend/app/schemas/espacio.py`).
- Corrección de una regresión real: sin este campo, `POST /espacios` desde este formulario fallaba con 422 (`correo` obligatorio desde RN-007) — confirmado con `frontend/e2e/tests/smoke/03-admin.spec.ts` en rojo antes del cambio, verde después.

## Pruebas

- `npm run type-check`, `npm run lint`, `npm run build` verdes.
- Fase 12B: `npx playwright test e2e/tests/smoke/03-admin.spec.ts --project=admin` — 2/2 verde (antes: 1 fallo determinista por `correo` ausente).

## Impacto y compatibilidad

- Login/logout, redirecciones y permisos de UI intactos; sin cambios de endpoints.
- Fase 12B: el tipo `EspacioCreate` (`frontend/src/types/espacio.ts`) ahora declara `correo` como obligatorio, reflejando el contrato real del backend desde la Fase 12B.

## Pendientes

- Tests de componentes (infraestructura pendiente de aprobación).
- Fase 12B: el formulario no recolecta `modalidad_reserva` (queda con el default `equipos` del backend) — fuera del alcance de esta corrección, que se limitó a resolver la regresión de `correo`.

## Fase de implementación

Fase 5A. Fase 12B (campo "Correo" en creación de espacios).
