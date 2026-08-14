# app

## Propósito

Páginas del App Router de Next.js y estilos globales.

## Cambios realizados

| Archivo | Acción | Descripción |
|---|---|---|
| espacios/page.tsx | Modificado | Modal de reserva accesible: `role="dialog"`, `aria-modal`, `aria-labelledby`, cierre con Escape, foco inicial en el botón Cerrar y retorno de foco al elemento previo |
| globals.css | Modificado | Estilos `:focus-visible` visibles para `.btn`, `.input`, botones, enlaces, selects y checkboxes |

## Reglas de negocio relacionadas

- RN-005 (Fase 4): la página ya filtraba espacios activos en cliente; sin cambios funcionales.

## Decisiones técnicas

- El foco se gestiona con `useRef` sin dependencias nuevas (sin librería de focus-trap).

## Pruebas

- `espacios/page.test.tsx` (Vitest + RTL + user-event): listado público (loading, vacío, defensa cliente, error), modal accesible (dialog, aria-modal, foco, Escape y restauración), selección consecutiva, términos, payload completo y error de reserva.
- `npm run test`, `npm run type-check`, `npm run lint`, `npm run build` verdes.

## Impacto y compatibilidad

- Flujo de reserva sin cambios; solo accesibilidad.

## Pendientes

- Focus-trap completo dentro del modal (Tab cíclico) si se aprueba una dependencia en el futuro.

## Fase de implementación

Fase 5A.
