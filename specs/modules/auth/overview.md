# Auth

## Purpose

Gestionar la identidad autenticada, la autenticación, las sesiones y la autorización de las operaciones protegidas de Reservas Parquei.

El módulo establece quién puede autenticarse, cómo se representa la identidad asociada a una cuenta y bajo qué condiciones una cuenta puede ejecutar operaciones administrativas.

## Scope

El módulo cubre:

- cuentas de autenticación;
- asociación entre cuentas e identidades funcionales;
- autenticación;
- sesiones;
- validación de tokens;
- autorización;
- permisos administrativos;
- ámbito organizacional de autorización;
- identificación del actor autenticado;
- trazabilidad relacionada con identidad y autorización.

## Responsibilities

El módulo es responsable de:

- validar que una operación autenticada provenga de una cuenta activa;
- asociar cada cuenta con la identidad funcional correspondiente;
- autenticar credenciales;
- emitir y validar tokens de acceso;
- gestionar sesiones;
- determinar la identidad autenticada;
- evaluar permisos administrativos;
- evaluar el ámbito organizacional en el que puede ejercerse una operación;
- impedir operaciones realizadas por cuentas, sesiones o identidades inactivas cuando corresponda;
- suministrar a otros módulos la identidad y autorización necesarias para ejecutar operaciones protegidas;
- preservar la trazabilidad de las decisiones de autenticación y autorización cuando corresponda.

## Owned Concepts

El módulo es propietario funcional de los siguientes conceptos:

- cuenta;
- identidad autenticada;
- sesión;
- token de acceso;
- autenticación;
- autorización;
- permiso;
- ámbito organizacional de autorización.

Las entidades persistentes concretas asociadas a estos conceptos se definen en `docs/data-model.md`.

## Dependencies

### Administration

El módulo depende de la información administrativa vigente necesaria para determinar:

- estado de cuentas e identidades;
- cargos;
- unidades organizacionales;
- permisos;
- relaciones utilizadas para autorización.

Administration gestiona estos elementos; Auth los utiliza para tomar decisiones de autenticación y autorización.

### Reservations

El módulo de reservas utiliza Auth para determinar:

- quién realiza una operación;
- si la cuenta está autenticada;
- si puede consultar o modificar reservas de terceros;
- si puede aprobar, rechazar o cancelar reservas dentro de su ámbito autorizado.

Auth no define las reglas del ciclo de vida de una reserva.

### Resources

El módulo de recursos utiliza Auth cuando una operación de creación, modificación, habilitación o deshabilitación requiere permisos administrativos.

Auth no determina las reglas funcionales de laboratorios, espacios, equipos, mobiliarios u otros recursos.

### Reports

El módulo de reportes utiliza Auth para determinar el ámbito de información que una cuenta puede consultar.

Auth no define los criterios, cálculos o dimensiones de los reportes.

## Provides

El módulo proporciona al resto del sistema:

- identidad de la cuenta autenticada;
- estado de autenticación;
- validación de tokens;
- estado de sesión;
- evaluación de permisos;
- ámbito autorizado de actuación;
- identificación del actor que ejecuta una operación protegida.

## Out of Scope

No pertenece a este módulo:

- crear, modificar, aprobar, rechazar o cancelar reservas;
- determinar disponibilidad de espacios o recursos;
- administrar laboratorios, espacios, equipos, mobiliarios u otros recursos;
- generar reportes;
- definir reglas de ocupación;
- generar notificaciones;
- decidir las reglas funcionales específicas de otros módulos;
- almacenar credenciales en entidades que no pertenezcan al dominio de autenticación;
- conceder permisos únicamente por el nombre de un cargo, perfil o tipo de cuenta.

## Module Boundary

Auth responde principalmente a las siguientes preguntas:

- ¿Quién está autenticado?
- ¿La cuenta y la sesión siguen siendo válidas?
- ¿Qué identidad funcional está asociada a la cuenta?
- ¿Qué operación está autorizada?
- ¿En qué ámbito puede ejecutarse?

No responde preguntas como:

- ¿La reserva está disponible?
- ¿La reserva puede cancelarse por su estado?
- ¿El recurso está operativo?
- ¿Qué debe aparecer en un reporte?
- ¿Qué notificación debe generarse?

Estas decisiones pertenecen a los módulos propietarios correspondientes.

## Related Documentation

- `business-rules.md`
- `../../docs/product-spec.md`
- `../../docs/architecture.md`
- `../../docs/data-model.md`

Los contratos API específicos relacionados con autenticación y autorización deben mantenerse en la documentación central de API.


## Modelo persistente

[Modelo de datos del módulo](data-model.md): tablas propias, relaciones y diferencias pendientes respecto al inventario principal.
