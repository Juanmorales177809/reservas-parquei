# Resources

## Purpose

Gestionar los laboratorios, espacios, equipos, mobiliarios y otros recursos reservables utilizados por Reservas Parquei.

El módulo define la identidad, pertenencia, capacidad, habilitación y estado operativo de los elementos reservables. Las reglas sobre disponibilidad temporal, conflictos de horario y ciclo de vida de las reservas pertenecen al módulo Reservations.

## Scope

El módulo cubre:

- configuración de laboratorios habilitados para reservas;
- gestión de espacios;
- gestión de equipos reservables;
- gestión de mobiliarios;
- gestión de otros recursos reservables;
- pertenencia de espacios y recursos a unidades organizacionales;
- capacidad de espacios;
- habilitación o deshabilitación;
- estado operativo cuando corresponda;
- conservación histórica de los elementos deshabilitados.

## Responsibilities

El módulo es responsable de:

- identificar los laboratorios, espacios y recursos disponibles para el sistema;
- mantener la pertenencia de cada espacio o recurso a una unidad organizacional;
- gestionar la configuración de laboratorios habilitados para reservas;
- mantener la capacidad de los espacios;
- mantener el estado de habilitación de espacios y recursos;
- mantener o consultar el estado operativo de los equipos cuando corresponda;
- impedir que elementos deshabilitados se utilicen en nuevas operaciones;
- conservar la identidad y relaciones históricas de elementos deshabilitados;
- proporcionar a otros módulos la información vigente necesaria para validar operaciones sobre reservas.

## Owned Concepts

El módulo es propietario funcional de los siguientes conceptos:

- laboratorio habilitado para reservas;
- espacio;
- recurso reservable;
- equipo;
- mobiliario;
- otro recurso;
- capacidad;
- pertenencia a unidad organizacional;
- habilitación;
- estado operativo.

Las entidades persistentes concretas asociadas a estos conceptos se definen en `docs/data-model.md`.

## Dependencies

### Administration

El módulo depende de Administration para la información institucional y administrativa necesaria para relacionar recursos con unidades organizacionales y gestionar configuraciones autorizadas.

Resources no administra usuarios, cuentas, perfiles ni permisos.

### Auth

El módulo utiliza Auth para determinar si una cuenta puede ejecutar operaciones administrativas sobre laboratorios, espacios o recursos.

Resources no autentica usuarios ni evalúa por sí mismo la identidad de una cuenta.

### Reservations

Reservations utiliza Resources para conocer:

- existencia de espacios y recursos;
- pertenencia a una unidad;
- capacidad;
- estado de habilitación;
- estado operativo cuando corresponda.

Resources no determina:

- disponibilidad temporal;
- conflictos entre reservas;
- estados de reserva;
- aprobación;
- rechazo;
- cancelación.

### Notifications

El módulo puede originar eventos relacionados con la deshabilitación o cambio de condición de un espacio o recurso.

Notifications determina cómo se registran y presentan las comunicaciones derivadas de dichos eventos.

### Reports

Reports utiliza información de laboratorios, espacios y recursos para generar consultas y agregaciones.

Resources no define criterios ni cálculos de reportes.

## Provides

El módulo proporciona al resto del sistema:

- identificación de laboratorios configurados para reservas;
- espacios disponibles como entidades reservables;
- equipos, mobiliarios y otros recursos;
- unidad organizacional asociada;
- capacidad de espacios;
- estado de habilitación;
- estado operativo cuando corresponda;
- información necesaria para validar si un elemento puede participar en una nueva reserva.

## Out of Scope

No pertenece a este módulo:

- crear reservas;
- aprobar o rechazar reservas;
- cancelar reservas;
- gestionar estados de reserva;
- determinar solapamientos de horario;
- calcular disponibilidad temporal;
- autenticar usuarios;
- evaluar permisos;
- generar notificaciones;
- generar reportes;
- administrar cuentas, perfiles o unidades organizacionales como entidades institucionales.

## Module Boundary

Resources responde principalmente a las siguientes preguntas:

- ¿Qué laboratorios están configurados para recibir reservas?
- ¿Qué espacios existen?
- ¿Qué recursos reservables existen?
- ¿A qué unidad organizacional pertenece cada elemento?
- ¿Cuál es la capacidad de un espacio?
- ¿El elemento está habilitado?
- ¿El equipo está operativo cuando esa condición aplica?

No responde preguntas como:

- ¿El recurso está libre en una fecha y hora determinadas?
- ¿Existe otra reserva que lo bloquee?
- ¿La reserva puede aprobarse?
- ¿La reserva puede cancelarse?
- ¿El usuario tiene permiso para ejecutar una operación?
- ¿Qué notificación debe generarse?

Estas decisiones pertenecen a los módulos propietarios correspondientes.

## Related Documentation

- `business-rules.md`
- `../../docs/product-spec.md`
- `../../docs/architecture.md`
- `../../docs/data-model.md`

Los contratos API específicos para laboratorios, espacios y recursos deben mantenerse en la documentación central de API.


## Modelo persistente

[Modelo de datos del módulo](data-model.md): tablas propias, relaciones y diferencias pendientes respecto al inventario principal.
