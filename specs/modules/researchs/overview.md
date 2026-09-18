# Researchs — Investigación

## Propósito

Gestionar el contexto académico/investigativo del usuario y sus vinculaciones. El módulo se denomina `researchs` en la documentación y es propietario del dominio persistente `investigacion`.

## Alcance y responsabilidades

- Gestionar proyectos, semilleros, pasantías y trabajos de grado.
- Mantener los catálogos de proyectos y semilleros que Administration importa mediante el mecanismo autorizado.
- Gestionar actividades institucionales con su dependencia y estado.
- Gestionar perfiles académicos/investigativos y modalidades de vinculación definidos en el modelo general.
- Asociar usuarios a estas entidades y mantener el estado de sus vinculaciones.
- Exigir los datos de universidad y docente ITM para pasantías, y los datos del director para trabajos de grado.
- Proporcionar las vinculaciones activas y válidas que otros módulos pueden consultar.
- Conservar los registros de vinculación al desactivarlos y respetar las referencias históricas.

## Conceptos propios

El módulo administra las entidades del schema `investigacion`: `proyectos`, `semilleros`, `pasantias`, `trabajos_grado`, `actividades_institucionales`, `perfiles`, `modalidades_vinculacion` y sus seis tablas de vinculación con usuarios. Sus campos y restricciones se detallan en [data-model.md](data-model.md).

## Dependencias y límites

| Módulo | Relación |
|---|---|
| [Usuarios](../usuarios/business-rules.md) | Proporciona `usuarios.usuarios`; las vinculaciones utilizan `id_usuario`. |
| [Auth](../auth/overview.md) | Autentica cuentas y evalúa la autorización para operar. La pertenencia a un proyecto u otra entidad no concede permisos administrativos. |
| [Administration](../administration/overview.md) | Ejecuta la importación autorizada de proyectos y semilleros; Researchs conserva la propiedad del catálogo y sus vinculaciones. |
| [Reservations](../reservations/business-rules.md#contexto-de-la-reserva--rn-ctx) | Consulta el contexto disponible y registra las entidades que justificaron una reserva. Define la obligatoriedad, coexistencia y exclusividad de los contextos mediante RN-CTX. |
| [Reports](../reports/overview.md) | Puede utilizar el contexto como dimensión de consulta, respetando el contexto histórico conservado por reservas. |

Researchs proporciona las entidades, las actividades institucionales y sus vinculaciones; reservas conserva las referencias seleccionadas y sus copias históricas. Researchs no crea reservas ni decide su disponibilidad, aprobación o estado.

## Fuera de alcance

- Autenticación, sesiones y administración de cuentas.
- Gestión de espacios, recursos o disponibilidad temporal.
- Ciclo de vida de reservas y combinaciones permitidas de su contexto.

## Estado y decisiones pendientes

Las reglas iniciales se recogen en RN-INV-01 a RN-INV-07 y RN-ACT-01 a RN-ACT-03. Las tablas de actividades institucionales, pasantías, trabajos de grado y sus vinculaciones están documentadas como cambios pendientes de aplicar en la base de datos. Esta documentación no acredita implementación en el backend.

Quedan pendientes los permisos concretos para administrar estas entidades, sus flujos y contratos API, y el mecanismo de auditoría de cambios de vinculación. El estado actual permite conservar registros desactivados, pero por sí solo no registra cada transición histórica.

## Documentación relacionada

- [Reglas de negocio](business-rules.md).
- [Modelo de datos del módulo](data-model.md).
- [Modelo general](../../docs/data-model.md#schema-investigacion).
- [Modelo de contexto de reservas](../reservations/data-model.md#reservasreserva_contexto).
