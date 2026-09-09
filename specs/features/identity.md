# Identidad y autorización

La estructura está en [data-model](../core/data-model.md); las reglas de reservas en [bookings](bookings.md). La identidad administrativa pertenece a LIA y se consulta directamente en la misma PostgreSQL.

## Usuarios y personal — RN-USR

- **RN-USR-01:** Un reservista autenticado puede crear solicitudes según las opciones disponibles.
- **RN-USR-02:** Solo puede solicitar elementos habilitados.
- **RN-USR-03:** Debe aportar fecha, horario, tipo de reserva, tipo de uso y datos requeridos.
- **RN-USR-04:** Puede consultar sus solicitudes y estados.
- **RN-USR-05:** Las acciones administrativas requieren personal autorizado para la unidad correspondiente.
- **RN-USR-06:** Reservas no tiene copia de personal; usa directamente `personal.personal`.
- **RN-USR-07:** El ámbito se obtiene por `personal -> cargo -> unidad_organizacional`.
- **RN-USR-08:** El cargo define acciones permitidas y la unidad define el ámbito; la unidad por sí sola no concede todas las acciones.
- **RN-USR-09:** Personal inactivo no realiza nuevas operaciones administrativas; el historial se conserva.

## Autenticación

- **RN-USR-10:** La identidad autenticada debe vincularse verificablemente con `personal.personal.supabase_id` (o el identificador autenticado definido por LIA). No se identifica por nombre ni por un identificador no verificado.
- **RN-USR-11:** Credenciales y tokens deben validarse por vigencia; no se exponen secretos.
- **RN-USR-12:** La autorización consulta el estado actual de personal, cargo y unidad; no depende de caché, proyección ni vigencia de sincronización.

La tabla `reservas.usuarios` representa reservistas y no sustituye a `personal.personal`. Una persona puede tener ambas identidades si el flujo de autenticación así lo requiere.

## Autorización y auditoría

La matriz cargo-acción debe definir, como mínimo, administrar configuración, aprobar, rechazar, cancelar administrativamente y editar reservas. Un gestor autorizado en su unidad puede crear APROBADA si la política del laboratorio lo permite. Toda acción sensible debe comprobar identidad, actividad, cargo, unidad y operación solicitada en la misma transacción de negocio.

La auditoría conserva actor, acción y momento sin crear una copia de personal. LIA no referencia tablas ni roles de Reservas.
