# Especificaciones del sistema (SDD)

Esta carpeta contiene la documentación funcional y técnica del sistema usando la metodología SDD.

## Estructura

- [`core/`](core/): contratos técnicos, modelo de datos y configuración global.
- [`features/`](features/): reglas funcionales por capacidad del sistema.
- [`decisions/`](decisions/): preguntas abiertas y decisiones pendientes.
- [`lia/`](lia/): documentación del modelo maestro de LIA, en la misma PostgreSQL y con responsabilidad independiente.

## Contratos de Reservas

- [Reservas](features/bookings.md): RN-TIP, RN-RES, RN-EST, RN-DIS, RN-APR, RN-CAN y RN-AUD.
- [Laboratorios, espacios y recursos](features/spaces-and-resources.md): RN-LAB, RN-ESP, RN-REC, RN-EQP, RN-MOB y RN-OTR.
- [Identidad](features/identity.md): RN-USR, autenticación y autorización.
- [Modelo de datos](core/data-model.md): estructura e invariantes transaccionales del modelo objetivo.
- [Modelo de datos LIA](lia/data-model-lia.md): tablas maestras de LIA y límites de responsabilidad.

LIA y Reservas comparten una única PostgreSQL. Reservas puede referenciar las tablas maestras de LIA mediante FK dentro de la misma base; LIA no conoce ni referencia tablas de Reservas. No existe una capa de sincronización ni proyecciones persistentes.

Las reglas RN son obligatorias, incluso cuando utilizan valores configurables. Las propuestas no aprobadas se identifican como recomendaciones o decisiones pendientes. Las referencias cruzadas remiten al documento que define cada regla. La documentación objetivo no acredita su implementación en las bases o el backend actuales.
