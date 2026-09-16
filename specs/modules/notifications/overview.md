# Notifications

## Purpose

Gestionar el registro, consulta y estado de las notificaciones generadas por eventos relevantes de Reservas Parquei.

El módulo comunica eventos producidos por otros módulos, pero no decide la validez ni el resultado de las operaciones que los originan.

## Scope

El módulo cubre:

- creación de notificaciones a partir de eventos válidos del sistema;
- identificación de destinatarios;
- almacenamiento de notificaciones;
- consulta de notificaciones;
- estado de lectura;
- conservación histórica;
- asociación entre una notificación y el evento o entidad relacionada.

## Responsibilities

El módulo es responsable de:

- registrar notificaciones derivadas de eventos relevantes;
- identificar el destinatario correspondiente;
- conservar la referencia al evento o entidad relacionada;
- evitar duplicados cuando corresponda;
- mantener el estado de lectura;
- permitir la consulta de notificaciones;
- preservar el historial de notificaciones;
- mantener coherencia entre el evento ocurrido y el contenido registrado;
- evitar exposición de información sensible en el contenido de las notificaciones.

## Owned Concepts

El módulo es propietario funcional de los siguientes conceptos:

- notificación;
- destinatario de notificación;
- tipo de evento notificable;
- estado de lectura;
- referencia funcional al evento relacionado.

Las entidades persistentes concretas asociadas a estos conceptos se definen en `docs/data-model.md`.

## Dependencies

### Reservations

El módulo depende de Reservations para conocer eventos válidos relacionados con:

- creación de solicitudes;
- aprobación;
- rechazo;
- modificación;
- cancelación;
- afectación de reservas.

Notifications no determina si una reserva puede ejecutar dichas transiciones.

### Resources

El módulo depende de Resources cuando un cambio sobre laboratorios, espacios o recursos debe producir una notificación para personas afectadas.

Notifications no determina si un recurso puede habilitarse, deshabilitarse o utilizarse.

### Auth

El módulo utiliza Auth para identificar cuentas autenticadas y destinatarios cuando la notificación depende de identidad, permisos o ámbito organizacional.

Notifications no autentica usuarios ni evalúa permisos administrativos.

### Administration

El módulo puede utilizar información administrativa necesaria para resolver destinatarios institucionales cuando corresponda.

Notifications no administra usuarios, cuentas, perfiles, unidades organizacionales ni permisos.

## Provides

El módulo proporciona al resto del sistema:

- registro de notificaciones;
- consulta de notificaciones por destinatario;
- estado leído/no leído;
- asociación con eventos o entidades relacionadas;
- historial de comunicaciones generadas por el sistema.

## Out of Scope

No pertenece a este módulo:

- decidir si una reserva puede crearse;
- aprobar o rechazar reservas;
- cancelar reservas;
- modificar estados de reservas;
- determinar disponibilidad de espacios o recursos;
- autenticar usuarios;
- evaluar permisos;
- administrar recursos;
- generar reportes;
- sustituir registros de auditoría o historial de cambios;
- actuar como fuente de verdad del estado de una reserva o recurso.

## Module Boundary

Notifications responde principalmente a las siguientes preguntas:

- ¿Qué evento debe comunicarse?
- ¿Quién debe recibir la notificación?
- ¿Qué contenido debe registrarse?
- ¿La notificación fue leída?
- ¿Con qué evento o entidad está relacionada?

No responde preguntas como:

- ¿La reserva puede aprobarse?
- ¿La reserva puede cancelarse?
- ¿El recurso está disponible?
- ¿El usuario tiene permiso para ejecutar una operación?
- ¿Cuál es el estado oficial de una reserva?

Estas decisiones pertenecen a los módulos propietarios correspondientes.

## Related Documentation

- `business-rules.md`
- `../../docs/product-spec.md`
- `../../docs/architecture.md`
- `../../docs/data-model.md`

Los contratos API específicos para consulta y gestión de notificaciones deben mantenerse en la documentación central de API.
