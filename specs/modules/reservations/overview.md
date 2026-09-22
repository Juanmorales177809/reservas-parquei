# Reservations

## Purpose

Gestionar el ciclo de vida de las reservas institucionales.

## Scope

El módulo cubre creación, consulta, modificación, aprobación,
rechazo, cancelación y validación de disponibilidad temporal.

## States

Todas los tipos de reservas utilizan un conjunto común de estados.

-  SOLICITADA;
-  APROBADA;
-  RECHAZADA;
-  EN_EJECUCION;
-  FINALIZADA;
-  CANCELADA;

### Transiciones generales

- SOLICITADA -> APROBADA;
- SOLICITADA -> RECHAZADA;
- APROBADA -> EN_EJECUCION;
- EN_EJECUCION -> FINALIZADA;
- APROBADA -> CANCELADA

## Responsibilities

- gestionar reservas;
- controlar estados;
- validar horarios;
- validar disponibilidad;
- coordinar aprobación y cancelación;
- mantener trazabilidad de las operaciones de reserva.

## Owned Concepts

- reserva;
- estado de reserva;
- horario;
- disponibilidad;
- composición de la reserva.
- contexto obligatorio de la reserva.

## Dependencies

- auth: identidad y autorización;
- [researchs](../researchs/overview.md): contexto académico/investigativo y vinculaciones válidas del usuario;
- resources: espacios y recursos;
- notifications: comunicación de eventos.

## Provides

- creación y gestión de reservas;
- consulta de estado;
- información de disponibilidad;
- eventos derivados del ciclo de vida de una reserva.

## Out of Scope

- autenticación;
- administración de cuentas;
- gestión estructural de recursos;
- generación de reportes.

## Related Documentation

- `business-rules.md`
- `../../docs/product-spec.md`
- `../../docs/architecture.md`
- `../../docs/data-model.md`

## Modelo persistente

[Modelo de datos del módulo](data-model.md): tablas propias, relaciones y diferencias pendientes respecto al inventario principal.
