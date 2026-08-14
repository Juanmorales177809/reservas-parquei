# reservas

## Propósito

Flujo de reservas del usuario.

## Cambios realizados

| Archivo | Acción | Descripción |
|---|---|---|
| mis-reservas/page.tsx | Modificado | Guard manual → `<ProtectedRoute>`; badges centralizados en `utils/estados`; `aria-label` en inputs inline (fecha, horas, asistentes) |
| nueva/page.tsx | Modificado | Guard manual → `<ProtectedRoute>` dentro del formulario |

## Reglas de negocio relacionadas

- Estados de reserva y edición solo de reservas propias (backend conserva la autoridad).

## Decisiones técnicas

- El wrapper se coloca dentro de `NuevaReservaForm` para que el formulario no consulte datos sin sesión.

## Pruebas

- `npm run type-check`, `npm run lint`, `npm run build` verdes.

## Impacto y compatibilidad

- Sin cambios de flujo; redirección a `/login` equivalente (replace).

## Pendientes

- N/A.

## Fase de implementación

Fase 5A.
