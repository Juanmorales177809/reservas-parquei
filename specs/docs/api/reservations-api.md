# API de reservas

Plantilla para definir los endpoints de reservas.

Operaciones pendientes: crear, consultar propias, consultar detalle, modificar, aprobar, rechazar, cancelar y consultar disponibilidad.

Aprobar, rechazar y cancelar deben tratarse como operaciones de negocio, no como simples actualizaciones CRUD. Para cada operación deben quedar definidos request, response, estados válidos, permisos, errores y concurrencia.

Referencias: [reservas](../domains/bookings.md), [transacciones](../core/transactions.md) y [errores](../core/errors.md).
