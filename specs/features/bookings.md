# Reservas

## Propósito

Una reserva representa la solicitud de uso de un recurso dentro de un espacio, durante una fecha y un intervalo horario determinados.

La reserva siempre pertenece a:

- un usuario;
- un espacio;
- un recurso;
- una fecha;
- una hora de inicio y una hora de finalización.

## Clasificación de reglas

- `Constraint`: regla obligatoria que debe cumplirse para aceptar o modificar una reserva.
- `Suggestion`: comportamiento recomendado o configurable que puede cambiarse mediante una decisión de negocio.
- `Open question`: comportamiento aún no definido y que requiere decisión.

## Constraint: autenticación y propiedad

1. Solo un usuario autenticado puede crear una reserva.
2. Un usuario normal solo puede editar sus propias reservas.
3. Un usuario normal solo puede editar una reserva cuyo estado sea `esperando`.
4. Un usuario normal solo puede cancelar sus propias reservas.
5. Un usuario normal solo puede cancelar reservas en estado `aprobada`.
6. Un usuario normal no puede eliminar reservas.
7. Un administrador puede gestionar reservas de cualquier espacio.
8. Un gestor solo puede gestionar reservas del espacio que tiene asignado.
9. Un gestor no puede aprobar, rechazar, cancelar, editar o eliminar reservas de otro espacio.

## Constraint: datos obligatorios

Una reserva debe contener:

- `recurso_id` válido;
- `fecha` válida;
- `hora_inicio`;
- `hora_fin`;
- `asistentes` mayor o igual que cero.

La cantidad de asistentes no puede ser menor que cero ni superar la capacidad configurada para el recurso.

> Nota de implementación: actualmente el schema y la base de datos exigen `asistentes > 0`; deben ajustarse a `asistentes >= 0`.

## Constraint: recurso y espacio

1. El recurso debe existir.
2. El espacio asociado al recurso debe existir.
3. El recurso debe estar en estado `activo`.
4. El espacio debe estar en estado `activo`.
5. La reserva se asocia automáticamente al espacio al que pertenece el recurso.
6. No se permite reservar directamente un espacio sin seleccionar un recurso.

## Constraint: horario

1. `hora_inicio` debe ser menor que `hora_fin`.
2. Las horas deben estar alineadas a horas exactas; actualmente no se permiten minutos ni segundos distintos de cero.
3. Cada hora incluida en el intervalo debe estar habilitada en el horario del espacio.
4. Una reserva no puede cruzar medianoche.
5. La duración debe estar contenida dentro del horario de apertura del laboratorio o espacio.
6. Las reservas solo pueden utilizar los bloques horarios habilitados por el laboratorio o espacio.
7. La fecha se interpreta usando la zona horaria de negocio configurada en `APP_TIMEZONE`.

Ejemplo válido:

```text
08:00 - 10:00
```

Ejemplos inválidos:

```text
10:00 - 09:00   # El inicio es posterior al final
08:30 - 09:30   # No está permitido el bloque parcial actualmente
18:00 - 02:00   # No se permite cruzar medianoche
```

## Constraint: anticipación

La reserva debe crearse con una anticipación mínima igual a `espacio.horas_antelacion`.

La comparación se realiza entre la fecha y hora de inicio de la reserva y la hora local actual del sistema.

Si el inicio de la reserva es anterior al límite permitido, la solicitud debe rechazarse.

## Constraint: solapamiento

Un recurso no puede tener dos reservas bloqueantes que se solapen en la misma fecha.

Un mismo usuario sí puede tener varias reservas simultáneas, incluso sobre recursos diferentes. La validación de solapamiento se aplica por recurso, no globalmente por usuario.

Los estados bloqueantes son:

- `esperando`;
- `aprobada`.

Las reservas `rechazada` y `cancelada` no bloquean disponibilidad.

Dos intervalos se consideran solapados cuando:

```text
reserva_existente.hora_inicio < nueva.hora_fin
AND reserva_existente.hora_fin > nueva.hora_inicio
```

La validación se realiza antes de guardar y también existe una protección a nivel de base de datos para evitar carreras entre solicitudes concurrentes.

## Máquina de estados

Los estados permitidos son:

| Estado | Descripción |
|---|---|
| `esperando` | Solicitud creada y pendiente de decisión. |
| `aprobada` | Reserva confirmada y bloquea disponibilidad. |
| `rechazada` | Solicitud no aprobada. No bloquea disponibilidad. |
| `cancelada` | Reserva cancelada. No bloquea disponibilidad. |

Transiciones permitidas:

```text
esperando -> aprobada
esperando -> rechazada
esperando -> cancelada
aprobada  -> cancelada
```

No se permiten las siguientes transiciones:

- `rechazada` → cualquier estado;
- `cancelada` → cualquier estado;
- `aprobada` → `esperando`;
- `aprobada` → `rechazada`.

Una reserva aprobada solo puede pasar a cancelada. Una reserva rechazada o cancelada es terminal.

## Creación de reservas

Al crear una reserva, el sistema debe ejecutar las validaciones en este orden lógico:

1. Verificar autenticación del usuario.
2. Buscar el recurso.
3. Verificar que el recurso y el espacio estén activos.
4. Validar asistentes y capacidad.
5. Validar el intervalo horario.
6. Validar el horario habilitado del espacio.
7. Validar la anticipación mínima.
8. Verificar solapamientos.
9. Determinar el estado inicial.
10. Persistir la reserva y registrar la auditoría.

## Estado inicial y aprobación

### Constraint

Una reserva nueva debe comenzar en uno de estos estados:

- `aprobada`, cuando aplica aprobación automática;
- `esperando`, cuando requiere revisión.

### Suggestion

La aprobación automática se aplica cuando un gestor reserva en su propio espacio y recurso. Si reserva en otro espacio o recurso, la solicitud requiere aprobación.

## Cambio de estado

Solo un administrador o gestor puede cambiar el estado de una reserva.

Antes de aprobar una reserva que estaba pendiente, el sistema debe volver a comprobar el solapamiento. Esto evita aprobar una reserva que quedó en conflicto mientras esperaba revisión.

Cada cambio efectivo de estado debe:

- actualizar la reserva;
- crear una notificación para el usuario propietario;
- registrar una entrada de auditoría.

Repetir el mismo estado no debe generar una transición adicional ni una nueva notificación.

## Edición de reservas

Al editar una reserva se deben volver a validar todos los datos derivados:

- recurso;
- espacio asociado;
- capacidad;
- horario;
- horario habilitado del espacio;
- anticipación mínima;
- solapamiento.

Si se cambia el recurso, el espacio de la reserva debe actualizarse al espacio del nuevo recurso.

Un gestor solo puede cambiar recursos pertenecientes a su espacio administrado.

## Cancelación y eliminación

### Cancelación

La cancelación es un cambio de estado y conserva el historial de la reserva.

- El propietario puede cancelar sus reservas aprobadas hasta la hora de inicio, inclusive.
- Un administrador o gestor puede cancelar reservas dentro de su ámbito de gestión.
- La cancelación libera el intervalo horario.
- La cancelación debe generar auditoría y notificación.

No se permite cancelar una reserva después de su hora de inicio.

### Eliminación

La eliminación es una operación física y debe restringirse a administradores y gestores autorizados.

Como recomendación, debe preferirse cancelar o desactivar una reserva para conservar trazabilidad e historial.

## Disponibilidad

La disponibilidad se calcula por bloques horarios de una hora.

Un bloque puede presentarse como:

- `libre`: no existe una reserva bloqueante;
- `ocupado`: existe una reserva `esperando` o `aprobada`;
- `no disponible`: el recurso o el espacio no están activos.

Los bloques anteriores al límite de anticipación no se muestran como disponibles.

La disponibilidad pública no requiere autenticación actualmente.

La disponibilidad se consulta por separado para espacios y recursos. La disponibilidad del espacio no sustituye la disponibilidad específica de cada recurso.

## Notificaciones

### Constraint del proceso

Cuando una reserva queda pendiente, se debe notificar a los gestores asignados al espacio.

Cuando una reserva cambia de estado, se debe notificar al propietario con el tipo correspondiente:

- `Pendiente`;
- `Aprobada`;
- `Rechazada`;
- `Cancelada`.

### Suggestion

Debe definirse si las notificaciones duplicadas deben evitarse cuando existen varios eventos consecutivos sobre la misma reserva.

## Auditoría

Las siguientes operaciones deben registrar auditoría:

- creación;
- actualización;
- aprobación;
- rechazo;
- cancelación;
- eliminación.

La auditoría debe conservar el usuario que ejecutó la operación, la entidad, el identificador de la reserva, la acción y una descripción legible.

## Integridad y concurrencia

La validación de solapamiento en aplicación es necesaria para proporcionar mensajes claros, pero no es suficiente por sí sola ante solicitudes concurrentes.

La base de datos debe mantener una restricción de exclusión para impedir dos intervalos bloqueantes simultáneos sobre el mismo recurso y fecha. Los errores de integridad de esa restricción deben traducirse a una respuesta HTTP `409 Conflict`.

## Reglas pendientes de decisión

1. ¿Debe existir una anticipación máxima para reservar?
2. ¿La edición de una reserva aprobada por un gestor debe requerir una nueva aprobación?
3. ¿Debe conservarse el historial mediante cancelación en lugar de eliminación física?
4. ¿Cuál es la unidad de `horas_antelacion`: horas naturales o horas dentro del horario de atención?
5. ¿Qué mensaje y canal se utilizarán para informar a usuarios cuando se desactive un recurso con reservas futuras?
