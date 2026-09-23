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
| [researchs](modules/researchs/overview.md) | [RN-INV, RN-ACT](modules/researchs/business-rules.md) | [modelo](modules/researchs/data-model.md) | [flujos](modules/researchs/user-flow.md) |
| [notifications](modules/notifications/overview.md) | [RN-NOT, RN-EVT, RN-COR, RN-PREF](modules/notifications/business-rules.md) | [modelo](modules/notifications/data-model.md) | [flujos](modules/notifications/user-flow.md) |
| [reports](modules/reports/overview.md) | [RN-OCU, RN-EXP](modules/reports/business-rules.md) | [modelo](modules/reports/data-model.md) | [flujos](modules/reports/user-flow.md) |

## Contratos de API

Las [convenciones transversales](contratos/README.md) definen formato, errores, autenticación, paginación y concurrencia. Cada contrato de módulo las referencia y solo documenta lo suyo.

| Módulo | Contrato |
|---|---|
| auth | [sesión, credenciales, invitaciones y administración de cuentas](contratos/auth/api-contract.md) |
| reservations | [ciclo completo de la reserva](contratos/reservations/api-contract.md) |
| espacios | [espacios, recursos asociados y campos adicionales](contratos/espacios/api-contract.md) |
| usuarios | [perfil del reservista y vinculaciones](contratos/usuarios/api-contract.md) |
| resources | [catálogo de recursos y configuración del laboratorio](contratos/resources/api-contract.md) |
| notifications | [bandeja del destinatario y preferencias de correo](contratos/notifications/api-contract.md) |

Faltan `administration`, `reports` y `researchs`. Los tres ya tienen flujos de usuario de los que derivar su superficie, así que el bloqueo original de **OQ-08** quedó levantado; escribir los contratos sigue pendiente. Ver [decisiones pendientes](docs/decisions/open-questions.md).

## Convenciones

Las reglas RN son obligatorias, incluso cuando utilizan valores configurables. Las propuestas no aprobadas se identifican como recomendaciones o decisiones pendientes. Las referencias cruzadas remiten al documento que define cada regla. La documentación objetivo no acredita su implementación en las bases o el backend actuales.

Cada regla pertenece a un único módulo propietario. Cuando otro módulo necesita su efecto, lo referencia en lugar de repetirlo, para que no existan dos versiones de la misma regla.

**Los identificadores de regla son únicos dentro de su módulo, no en todo el sistema.** Once familias se repiten, varias con significados distintos:

| Familia | Módulos | Significados cuando difieren |
|---|---|---|
| `RN-CAL` | notifications, reservations | Quién genera el `.ics` frente a quién lo adjunta |
| `RN-CON` | notifications, reports | "Consulta" de la bandeja frente a "Consistencia de datos" |
| `RN-CTX` | reports, reservations | El contexto como dimensión de análisis frente al contexto de la reserva |
| `RN-DES` | notifications, resources | "Destinatarios" frente a "Desactivación" |
| `RN-EST` | notifications, reports, reservations | Estado de lectura, estados en reportes y estados de la reserva |
| `RN-HIS` | notifications, reports | Persistencia de notificaciones frente a datos históricos de reportes |
| `RN-IMP` | administration, resources | Orquestación de la carga frente a validaciones del equipo |
| `RN-INT` | administration, notifications | "Integridad" en ambos, sobre operaciones distintas |
| `RN-REC` | reservations, resources | "Recordatorios" frente a "Recursos" |
| `RN-REP` | reports, reservations | "Generación de reportes" frente a las reglas de reserva que los alimentan |
| `RN-USR` | administration, usuarios | Administración de identidades frente a reglas del Usuario |

`RN-PER` identifica únicamente los permisos de `administration`; las reglas de personal de `usuarios` usan `RN-PRS`. `RN-AUD` existe solo en `administration`.

Por eso, **toda cita a una regla de otro módulo debe nombrarlo** —por ejemplo `RN-PER-02` de administration—, y una cita sin calificar se entiende siempre referida al módulo del propio documento.

LIA y Reservas comparten una única PostgreSQL con separación lógica por schemas. Reservas puede referenciar las tablas maestras de LIA mediante FK dentro de la misma base; LIA no conoce ni referencia tablas de Reservas. No existe una capa de sincronización ni proyecciones persistentes.
