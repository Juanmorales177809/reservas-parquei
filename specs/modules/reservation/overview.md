# Reservations

## Purpose

Gestionar el ciclo de vida de las reservas institucionales.

## Scope

El módulo cubre creación, consulta, modificación, aprobación,
rechazo, cancelación y validación de disponibilidad temporal.

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

## Dependencies

- auth: identidad y autorización;
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