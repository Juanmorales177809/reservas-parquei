# dashboard

## Propósito

Panel del usuario autenticado con sus reservas.

## Cambios realizados

| Archivo | Acción | Descripción |
|---|---|---|
| page.tsx | Modificado | Guard manual → `<ProtectedRoute>`; badges centralizados en `utils/estados` |

## Reglas de negocio relacionadas

- Consulta de reservas propias (sin cambios de comportamiento).

## Pruebas

- `npm run type-check`, `npm run lint`, `npm run build` verdes.

## Impacto y compatibilidad

- Sin cambios funcionales.

## Pendientes

- Comparación de fechas naive existente (registrada como deuda en Fase 5; sin tocar en 5A).

## Fase de implementación

Fase 5A.
