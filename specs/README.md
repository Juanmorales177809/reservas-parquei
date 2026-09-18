# Especificaciones del sistema (SDD)

Esta carpeta contiene la documentación funcional y técnica del sistema usando la metodología SDD.

## Estructura

- [`docs/`](docs/): documentación transversal — [especificación de producto](docs/spec.md), [arquitectura](docs/architecture.md), [modelo de datos general](docs/data-model.md) y [decisiones pendientes](docs/decisions/open-questions.md).
- [`modules/`](modules/): un directorio por módulo, con su overview, reglas de negocio, modelo de datos y flujos de usuario.
- [`contratos/`](contratos/): contratos de API por módulo, que traducen reglas y flujos a la superficie HTTP.

## Módulos

| Módulo | Reglas | Modelo | Flujos |
|---|---|---|---|
| [auth](modules/auth/overview.md) | [RN-AUTH](modules/auth/business-rules.md) y [controles SEC](modules/auth/security.md) | [modelo](modules/auth/data-model.md) | [flujos](modules/auth/user-flow.md) |
| [usuarios](modules/usuarios/business-rules.md) | RN-USR, RN-DAT | [modelo](modules/usuarios/data-model.md) | [flujos](modules/usuarios/user-flow.md) |
| [administration](modules/administration/overview.md) | [RN-ADM, RN-UNI, RN-PER, RN-IMP](modules/administration/business-rules.md) | [modelo](modules/administration/data-model.md) | [flujos](modules/administration/user-flow.md) |
| [reservations](modules/reservations/overview.md) | [RN-RES, RN-TIP, RN-CTX, RN-EST, RN-APR, RN-CAN](modules/reservations/business-rules.md) | [modelo](modules/reservations/data-model.md) | [flujos](modules/reservations/user-flows.md) |
| [espacios](modules/espacios/overview.md) | [RN-ESP](modules/espacios/business-rules.md) | [modelo](modules/espacios/data-model.md) | [flujos](modules/espacios/user-flow.md) |
| [resources](modules/resources/overview.md) | [RN-REC, RN-EQP, RN-DES, RN-IMP](modules/resources/business-rules.md) | [modelo](modules/resources/data-model.md) | [flujos](modules/resources/user-flow.md) |
| [researchs](modules/researchs/overview.md) | [RN-INV, RN-ACT](modules/researchs/business-rules.md) | [modelo](modules/researchs/data-model.md) | — |
| [notifications](modules/notifications/overview.md) | [RN-NOT, RN-EVT, RN-COR, RN-PREF](modules/notifications/business-rules.md) | [modelo](modules/notifications/data-model.md) | — |
| [reports](modules/reports/overview.md) | [RN-OCU, RN-EXP](modules/reports/business-rules.md) | [modelo](modules/reports/data-model.md) | — |

## Contratos de API

- [auth](contratos/auth/api-contract.md): endpoints de sesión, credenciales, invitaciones y administración de cuentas, más el contrato interno que auth ofrece a los demás módulos.

Los contratos de los módulos restantes se escriben en `contratos/<módulo>/` cuando su superficie HTTP se defina.

## Convenciones

Las reglas RN son obligatorias, incluso cuando utilizan valores configurables. Las propuestas no aprobadas se identifican como recomendaciones o decisiones pendientes. Las referencias cruzadas remiten al documento que define cada regla. La documentación objetivo no acredita su implementación en las bases o el backend actuales.

Cada regla pertenece a un único módulo propietario. Cuando otro módulo necesita su efecto, lo referencia en lugar de repetirlo, para que no existan dos versiones de la misma regla.

**Los identificadores de regla son únicos dentro de su módulo, no en todo el sistema.** Varias familias se repiten con significados distintos: `RN-DES` es "Desactivación" en resources y "Destinatarios" en notifications; `RN-REC` es "Recordatorios" en reservations y "Recursos" en resources; `RN-AUD`, `RN-EST`, `RN-HIS`, `RN-IMP`, `RN-INT`, `RN-PER` y `RN-USR` también aparecen en más de un módulo. Por eso, **toda cita a una regla de otro módulo debe nombrarlo** —por ejemplo `RN-PER-02` de administration—, y una cita sin calificar se entiende siempre referida al módulo del propio documento.

LIA y Reservas comparten una única PostgreSQL con separación lógica por schemas. Reservas puede referenciar las tablas maestras de LIA mediante FK dentro de la misma base; LIA no conoce ni referencia tablas de Reservas. No existe una capa de sincronización ni proyecciones persistentes.
