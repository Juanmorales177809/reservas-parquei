# utils

## Propósito

Utilidades de presentación compartidas (fechas, etiquetas y variantes visuales de estados).

## Cambios realizados

| Archivo | Acción | Descripción |
|---|---|---|
| estados.ts | Creado | Centraliza badges y labels de estados de reserva y de entidad (antes duplicados en 4+1 páginas). Fallback seguro para valores desconocidos (`badge-neutral` y el valor crudo) |

## Reglas de negocio relacionadas

- Estados de reserva (`esperando/aprobada/rechazada/cancelada`) y estados de entidad (`activo/inactivo/mantenimiento`) — textos visibles y variantes conservados exactamente.

## Decisiones técnicas

- API de funciones (`badgeEstadoReserva`, `labelEstadoReserva`, `badgeEstadoEntidad`) con `Record` tipado por las uniones de `types/`; el estado desconocido no rompe la UI.

## Pruebas

- Verificación por `npm run type-check` y `npm run lint` (no existe infraestructura de tests unitarios aprobada).

## Impacto y compatibilidad

- Sin cambios visuales ni de datos; elimina duplicación.

## Pendientes

- N/A.

## Fase de implementación

Fase 5A.
