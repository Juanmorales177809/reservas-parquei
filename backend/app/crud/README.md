# crud

## Propósito

Consultas de persistencia SQLAlchemy. La lógica de negocio vive en `services/`; esta capa solo construye, lee y actualiza filas.

## Cambios realizados

| Archivo | Acción | Descripción |
|---|---|---|
| espacios.py | Modificado | `create_espacio` construye el horario por defecto con `HorarioAtencion` (validación de dominio) y lo serializa al formato exacto que ya se persistía: `{"0": [7..19], ..., "5": [7..19]}` |
| espacios.py | Modificado (Fase 12B) | `create_espacio` propaga `modalidad_reserva` y `correo` del payload al modelo |

## Reglas de negocio relacionadas

- ➕ Horario de atención por día: el espacio nuevo nace con atención 07:00–19:00 de lunes a sábado (mismo valor que antes).
- RN-006 / RN-007 (Fase 12B): modalidad y correo del espacio, persistidos al crear.

## Decisiones técnicas

- El value object del dominio valida el horario antes de persistirlo; la serialización `{str(dia): list}` conserva el formato de la DB (claves string del JSON).
- Fase 12B: `update_espacio` no requirió cambios — ya usa `data.model_dump(exclude_unset=True)` genérico, que recoge `modalidad_reserva`/`correo` automáticamente cuando el schema los valida.

## Pruebas

- Cubierto por `tests/test_api_espacios.py` (creación de espacios) y `tests/test_schemas_contrato.py`.
- Fase 12B: `tests/test_api_espacios.py::TestModalidadYCorreo`.

## Impacto y compatibilidad

- Ningún cambio observable: el dict persistido es idéntico al anterior.
- Fase 12B: espacios creados antes de esta fase no se ven afectados (columnas nuevas con default/backfill, ver `backend/app/models/README.md`).

## Riesgos

- Ninguno.

## Pendientes

- N/A para esta fase.

## Fase de implementación

Fase 3 (integración de la capa de dominio). Fase 12B (`modalidad_reserva`, `correo`).
