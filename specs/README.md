# Especificaciones del sistema (SDD)

Esta carpeta contiene la documentación funcional y técnica del sistema usando la metodología SDD.

## Estructura

- [`core/`](core/): contratos técnicos, modelo de datos y configuración global.
- [`features/`](features/): reglas funcionales por capacidad del sistema.
- [`decisions/`](decisions/): preguntas abiertas y decisiones pendientes.
- [`lia/`](lia/): documentación del modelo maestro de LIA, en la misma PostgreSQL y con responsabilidad independiente.

## Módulo Researchs — Investigación

El módulo [Researchs](modules/researchs/overview.md) administra el contexto académico/investigativo y las vinculaciones del usuario en el schema `investigacion`.

- [Reglas de negocio RN-INV](modules/researchs/business-rules.md).
- [Modelo de datos](modules/researchs/data-model.md), alineado con el [modelo general](docs/data-model.md#schema-investigacion).

## Contratos de Reservas

- [Reservas](features/bookings.md): RN-TIP, RN-RES, RN-EST, RN-DIS, RN-APR, RN-CAN y RN-AUD.
- [Laboratorios, espacios y recursos](features/spaces-and-resources.md): RN-LAB, RN-ESP, RN-REC, RN-EQP, RN-MOB y RN-OTR.
- [Identidad](features/identity.md): RN-USR, autenticación y autorización.
- [Modelo de datos](core/data-model.md): estructura e invariantes transaccionales del modelo objetivo.
- [Modelo de datos LIA](lia/data-model-lia.md): tablas maestras de LIA y límites de responsabilidad.

LIA y Reservas comparten una única PostgreSQL. Reservas puede referenciar las tablas maestras de LIA mediante FK dentro de la misma base; LIA no conoce ni referencia tablas de Reservas. No existe una capa de sincronización ni proyecciones persistentes.

Las reglas RN son obligatorias, incluso cuando utilizan valores configurables. Las propuestas no aprobadas se identifican como recomendaciones o decisiones pendientes. Las referencias cruzadas remiten al documento que define cada regla. La documentación objetivo no acredita su implementación en las bases o el backend actuales.


## Modelos de datos por módulo

- [auth](modules/auth/data-model.md).
- [usuarios](modules/usuarios/data-model.md).
- [administration](modules/administration/data-model.md).
- [espacios](modules/espacios/data-model.md).
- [resources](modules/resources/data-model.md).
- [notifications](modules/notifications/data-model.md).
- [reservations](modules/reservations/data-model.md).
- [researchs](modules/researchs/data-model.md).
- [reports](modules/reports/data-model.md).
