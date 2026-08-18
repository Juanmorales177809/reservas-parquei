# models

## Propósito

Modelos SQLAlchemy (ORM) que mapean el esquema de PostgreSQL. Las columnas y constraints son la fuente de verdad del esquema; las migraciones idempotentes de `app/migrations.py` las refuerzan en arranques posteriores.

## Cambios realizados

| Archivo | Acción | Descripción |
|---|---|---|
| reserva.py | Modificado | `ESTADOS_RESERVA` y `ESTADOS_BLOQUEANTES` pasan de tuplas literales a **alias derivados de los enums del dominio** (`EstadoReserva`, `ESTADOS_RESERVA_BLOQUEANTES`) vía `.value` |
| espacio.py | Modificado (Fase 12B) | Nuevas columnas `modalidad_reserva` (`String(20)`, NOT NULL, default `'equipos'`, `CheckConstraint` `ck_espacios_modalidad_reserva`) y `correo` (`String(255)`, nullable) |
| recurso.py | Modificado (Fase 12B) | Nueva columna `es_prestacion_servicio` (`Boolean`, NOT NULL, default `false`) |

## Reglas de negocio relacionadas

- ➕ Estados de reserva (`esperando/aprobada/rechazada/cancelada`) y estados bloqueantes de disponibilidad/solapamiento.
- RN-017 / RN-019..RN-021: ciclo de aprobación (los estados persisten sin cambios).
- **RN-006** (Fase 12B): modalidad de reserva del espacio (`equipos`/`zonas`/`mixto`) → `Espacio.modalidad_reserva`.
- **RN-007** (Fase 12B): correo propio del espacio para aprobaciones/notificaciones → `Espacio.correo`.
- **RN-009** (Fase 12B): recurso de prestación de servicios (PS) → `Recurso.es_prestacion_servicio`.

## Decisiones técnicas

- **Alias, no enum SQLAlchemy**: las columnas siguen siendo `String` con sus `CheckConstraint` actuales. Esto garantiza **cero cambios de SQL y cero migraciones**: los valores persistidos son exactamente los mismos strings de antes.
- Los consumidores existentes (`api/espacios.py`, `crud/reservas.py`) importan `ESTADOS_BLOQUEANTES` sin cambios.

### Fase 12B — Columnas nuevas de `Espacio` y `Recurso`

- **`modalidad_reserva`**: `String(20)` en vez de un `Enum` nativo de PostgreSQL — mismo patrón que `estado` en ambos modelos (string validado por `CheckConstraint`, no tipo enumerado de BD), para no introducir una migración de tipo de columna distinta al resto del esquema. Default `'equipos'`, backfill idempotente en `migrations.py`.
- **`correo`**: `nullable=True` a propósito — obligatorio en el schema `EspacioCreate` para altas nuevas (RN-007, decisión 2 de la Fase 12A), pero la columna en BD no fabrica datos falsos para espacios ya sembrados antes de esta fase. `EspacioUpdate.correo` permite completarlo después.
- **`es_prestacion_servicio`**: `Boolean` NOT NULL, default `false` — ningún recurso existente cambia de comportamiento (decisión 5 de las nueve decisiones de 12B, "recursos PS existentes").
- Nombre del campo **`modalidad_reserva`**, no `tipo_reserva`: evita colisión con el futuro campo de tipo de reserva académica en `Reserva` (RN-012, Fase 12D) — ver `app/domain/README.md`.

## Pruebas

```powershell
.\.venv\Scripts\python.exe -m pytest -v
.\.venv\Scripts\python.exe -m pytest tests/test_api_espacios.py tests/test_api_recursos.py tests/test_api_reservas.py -v   # Fase 12B
```

Resultado esperado: suite completa verde (los tests de integración validan el comportamiento de las constantes sin cambios). Fase 12B: 318/318.

## Impacto y compatibilidad

- Sin cambios de esquema, SQL ni datos. OpenAPI sin cambios.
- Fase 12B: cambio de esquema (3 columnas nuevas) vía migración idempotente aprobada explícitamente (ver `backend/app/migrations.py` y `CHANGELOG.md`, Fase 12B). Cambio de OpenAPI aprobado (ver `backend/app/schemas/README.md`).

## Riesgos

- Ninguno en esta fase (cambio puramente aditivo de origen de los literales).
- Fase 12B: el frontend admin (`frontend/src/app/admin/espacios/page.tsx`) crea espacios sin enviar `correo` — con `correo` ahora obligatorio en `EspacioCreate`, esa creación falla con 422. **No corregido en esta fase** (fuera del alcance backend-only de 12B); ver riesgo detallado en `CHANGELOG.md` (Fase 12B) y en el resultado de E2E.

## Pendientes

- N/A para esta fase.
- Fase 12B: decidir y aprobar por separado el ajuste de `frontend/src/app/admin/espacios/page.tsx` (y del payload de `frontend/e2e/tests/smoke/03-admin.spec.ts`) para incluir `correo` al crear un espacio.

## Fase de implementación

Fase 3 (integración de la capa de dominio). Fase 12B (`modalidad_reserva`, `correo`, `es_prestacion_servicio`).
