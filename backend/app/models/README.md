# models

## Propósito

Modelos SQLAlchemy (ORM) que mapean el esquema de PostgreSQL. Las columnas y constraints son la fuente de verdad del esquema; las migraciones idempotentes de `app/migrations.py` las refuerzan en arranques posteriores.

## Cambios realizados

| Archivo | Acción | Descripción |
|---|---|---|
| reserva.py | Modificado | `ESTADOS_RESERVA` y `ESTADOS_BLOQUEANTES` pasan de tuplas literales a **alias derivados de los enums del dominio** (`EstadoReserva`, `ESTADOS_RESERVA_BLOQUEANTES`) vía `.value` |

## Reglas de negocio relacionadas

- ➕ Estados de reserva (`esperando/aprobada/rechazada/cancelada`) y estados bloqueantes de disponibilidad/solapamiento.
- RN-017 / RN-019..RN-021: ciclo de aprobación (los estados persisten sin cambios).

## Decisiones técnicas

- **Alias, no enum SQLAlchemy**: las columnas siguen siendo `String` con sus `CheckConstraint` actuales. Esto garantiza **cero cambios de SQL y cero migraciones**: los valores persistidos son exactamente los mismos strings de antes.
- Los consumidores existentes (`api/espacios.py`, `crud/reservas.py`) importan `ESTADOS_BLOQUEANTES` sin cambios.

## Pruebas

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

Resultado esperado: suite completa verde (los tests de integración validan el comportamiento de las constantes sin cambios).

## Impacto y compatibilidad

- Sin cambios de esquema, SQL ni datos. OpenAPI sin cambios.

## Riesgos

- Ninguno en esta fase (cambio puramente aditivo de origen de los literales).

## Pendientes

- N/A para esta fase.

## Fase de implementación

Fase 3 (integración de la capa de dominio).
