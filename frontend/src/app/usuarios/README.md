# usuarios

## Propósito

Administración de usuarios (solo admin).

## Cambios realizados

| Archivo | Acción | Descripción |
|---|---|---|
| page.tsx | Modificado | Guard manual → `<ProtectedRoute adminOnly>`; `aria-label` en inputs inline de edición (username, email, rol, espacio y clave opcional) |

## Reglas de negocio relacionadas

- RN-002/RN-003/RN-004 (backend conserva la autoridad y validaciones).

## Pruebas

- `npm run type-check`, `npm run lint`, `npm run build` verdes.

## Impacto y compatibilidad

- Sin cambios funcionales.

## Pendientes

- N/A.

## Fase de implementación

Fase 5A.
