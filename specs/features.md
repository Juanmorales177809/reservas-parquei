# Índice de features

Las reglas funcionales de Reservas se distribuyen así:

- [Bookings](features/bookings.md): RN-TIP, RN-RES, RN-EST, RN-DIS, RN-APR, RN-CAN y RN-AUD.
- [Spaces and resources](features/spaces-and-resources.md): RN-LAB, RN-ESP, RN-REC, RN-EQP, RN-MOB y RN-OTR.
- [Identity](features/identity.md): RN-USR, autenticación y autorización.
- [Modelo de datos de Reservas](core/data-model.md): tablas, FK, restricciones e invariantes transaccionales.
- [Modelo de datos de LIA](lia/data-model-lia.md): fuentes maestras y límites de dependencia.

La arquitectura usa una única PostgreSQL con separación lógica por schemas. No hay reglas de sincronización entre bases ni copias persistentes de entidades de LIA.
