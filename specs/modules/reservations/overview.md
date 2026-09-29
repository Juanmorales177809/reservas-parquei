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

### Transiciones por tipo

Todos los tipos conservan los estados globales anteriores. La aprobación, rechazo y cancelación admitidos se rigen por las reglas del módulo, incluida `SOLICITADA → CANCELADA`.

| Tipo | Inicio | Fin |
|---|---|---|
| `ESPACIO` | `APROBADA → EN_EJECUCION` en `hora_inicio`. Puede seguir `SOLICITADA` durante la franja; si se aprueba dentro de ella, pasa inmediatamente a `EN_EJECUCION` | En `hora_fin`: `SOLICITADA → CANCELADA`; `APROBADA` o `EN_EJECUCION → FINALIZADA` |
| `RECURSO_INTERNO` | `APROBADA → EN_EJECUCION` automáticamente en `hora_inicio` | `EN_EJECUCION → FINALIZADA` automáticamente en `hora_fin` |
| `RECURSO_CAMPUS`, `RECURSO_EXTERNO` | Entrega física tras aprobación | Devolución física completa y cierre |
| `LISTA_ESPERA` | Inicio de fabricación/prestación tras aprobación | Registro de horas y finalización |

`RECHAZADA` y `CANCELADA` no cambian automáticamente. Desde `EN_EJECUCION`, interno no puede cancelarse. Espacio e interno controlan disponibilidad por franja, sin registros de entrega/devolución; la exclusividad física solo aplica a campus y externo.

## Responsibilities

- gestionar reservas;
- controlar estados;
- validar horarios;
- validar disponibilidad;
- coordinar aprobación y cancelación;
- conservar el historial de estados y los registros históricos exigidos expresamente por las reglas; el retiro manual del Técnico no genera historial específico y la auditoría general queda fuera del alcance actual.

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
- [espacios](../espacios/overview.md): espacios, capacidad, configuración y recursos asociados;
- resources: inventario y estado operativo de los recursos;
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

- [Reglas de negocio](business-rules.md)
- [Especificación del producto](../../docs/spec.md)
- [Arquitectura general](../../docs/architecture.md)
- [Modelo de datos general](../../docs/data-model.md)
- [Especificación de pantallas](screens.md), [wireframes](wireframes.md) y [navegación funcional](screen-flow.md): las cuatro superficies de reservas.

## Modelo persistente

[Modelo de datos del módulo](data-model.md): tablas propias, relaciones y diferencias pendientes respecto al inventario principal.
