# types

## Propósito

Tipos TypeScript que espejan los contratos JSON del backend. No contienen lógica de negocio.

## Cambios realizados

| Archivo | Acción | Descripción |
|---|---|---|
| espacio.ts | Modificado | `Espacio.estado` pasó de `'activo'\|'inactivo'\|'mantenimiento'\|string` a la unión estricta (el `\|string` anulaba el narrowing) |
| recurso.ts | Modificado | `Recurso.estado` idem. `TipoRecurso.activo` se conserva como `string`: el backend envía valores arbitrarios de esa columna (no forma parte de los enums del dominio) |
| reserva.ts | Modificado | `ReservaEspacio.estado` idem |

## Reglas de negocio relacionadas

- Valores JSON del backend conservados exactamente (sin cambios de campos, endpoints ni payloads).

## Decisiones técnicas

- El único cast introducido (`admin/recursos/page.tsx`) es el mínimo necesario al leer un `<select>` cuyo valor tipado es `string`.

## Pruebas

- `npm run type-check` verde.

## Impacto y compatibilidad

- Sin cambios en requests/responses; solo tipado más estricto en tiempo de compilación.

## Pendientes

- `TipoRecurso.activo` sigue como `string` por contrato del backend.

## Fase de implementación

Fase 5A.
