# Investigación — Researchs

Contrato funcional del dominio `investigacion`, alojado en el módulo `researchs`.

`investigacion` es dueño del contexto académico/investigativo y de las vinculaciones del usuario. `reservas` únicamente registra cuáles de esos contextos justificaron la reserva y conserva su información histórica.

## Reglas de investigación — RN-INV

- **RN-INV-01:** Un usuario puede estar vinculado a múltiples proyectos y semilleros.
- **RN-INV-02:** Una pasantía debe registrar universidad de procedencia, nombre del docente responsable en el ITM y correo del docente.
- **RN-INV-03:** Un trabajo de grado debe registrar nombre y correo del director.
- **RN-INV-04:** Las vinculaciones de usuarios con proyectos, semilleros, pasantías y trabajos de grado pueden estar activas o inactivas.
- **RN-INV-05:** La desactivación de una vinculación no elimina su historial.

## Relación con reservas

Las reglas [RN-CTX](../reservations/business-rules.md#contexto-de-la-reserva--rn-ctx) determinan qué combinaciones de contexto admite una reserva. Researchs proporciona las entidades y las vinculaciones activas y válidas del usuario para su selección. Una vinculación académica o investigativa no concede permisos administrativos sobre reservas.

Desactivar una vinculación conserva su registro y las referencias históricas existentes; no modifica retroactivamente el contexto de reservas anteriores.

## Documentación relacionada

- [Overview del módulo](overview.md).
- [Modelo de datos de investigación](data-model.md).
- [Modelo general](../../docs/data-model.md#schema-investigacion).
