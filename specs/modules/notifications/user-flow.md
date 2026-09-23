# User Flows — Notificaciones

Este documento describe únicamente los comportamientos de Notifications que tienen un iniciador propio: la interacción del destinatario con su bandeja y sus preferencias, y la entrega del correo saliente.

**La generación de notificaciones no se documenta aquí.** Cada evento notificable lo produce otro módulo, y su secuencia ya está descrita en el flujo de ese módulo. La correspondencia entre las reglas `RN-EVT` y el flujo que las origina está en [business-rules.md](business-rules.md#correspondencia-entre-eventos-y-flujos-productores). Repetirla en este documento duplicaría once reglas y sus flujos.

Las reglas de este módulo están en [business-rules.md](business-rules.md) y su estructura persistente en [data-model.md](data-model.md).

---

## UF-NOT-01 — Consultar la bandeja de notificaciones y marcarlas leídas

**Actor principal:** cualquier cuenta autenticada.

**Precondiciones:**

- La cuenta está autenticada y activa.

**Flujo principal:**

1. El destinatario abre su bandeja de notificaciones.
2. El sistema devuelve únicamente las notificaciones in-app cuya cuenta destinataria es la suya (`RN-CON-01`), ordenadas cronológicamente (`RN-CON-03`).
3. Cada notificación presenta el tipo de evento, la fecha y hora, el estado de lectura y la referencia al elemento relacionado cuando exista (`RN-CON-02`). El contenido es el que se comunicó en su momento y no se recalcula aunque la reserva haya cambiado después (`RN-HIS-03`).
4. El destinatario distingue las leídas de las no leídas (`RN-EST-05`) y puede filtrar por ese estado.
5. Consultar la bandeja no modifica el estado de ninguna notificación (`RN-CON-04`).
6. El destinatario marca como leída una notificación propia; el sistema registra el instante de lectura (`RN-EST-03`).
7. El marcado no altera el estado de la reserva, del recurso, de la operación relacionada ni del envío de correo asociado al mismo evento (`RN-EST-04`, `RN-COR-05`).

**Flujos alternos:**

- Si la notificación no pertenece a la cuenta autenticada, la operación se deniega y no se revela su existencia (`RN-CON-01`).
- Una notificación cuya entidad relacionada fue desactivada o eliminada después sigue apareciendo en la bandeja (`RN-HIS-02`).
- El volumen de la bandeja se gestiona con paginación y filtros; no existe purga de historial (`RN-HIS-01`).

**Fuera de alcance:** la bandeja no es el registro oficial del estado de una reserva (`RN-HIS-04`). Para conocerlo, el destinatario consulta la reserva.

---

## UF-NOT-02 — Configurar las preferencias de correo

**Actor principal:** cualquier cuenta autenticada.

**Precondiciones:**

- La cuenta está autenticada y activa.

**Flujo principal:**

1. El destinatario abre sus preferencias de notificación.
2. El sistema muestra su preferencia general de correo y, si las tiene, las preferencias por tipo de evento.
3. El destinatario habilita o deshabilita el correo de forma general o para un tipo de evento determinado (`RN-PREF-01`).
4. El sistema guarda la preferencia. La más específica prevalece: la del tipo de evento y, en su ausencia, la general (`RN-PREF-04`).
5. La preferencia afecta únicamente al canal de correo. La notificación in-app se sigue generando y consultando igual (`RN-PREF-01`).

**Flujos alternos:**

- Si el correo está deshabilitado para la unidad en `reservas.laboratorios_config.notificar_por_correo`, no se generan correos para esos eventos aunque la preferencia individual esté habilitada (`RN-PREF-02`). Notifications no administra esa configuración: pertenece a Resources conforme a `RN-LAB-07`.
- Las comunicaciones de autenticación —invitación y recuperación de contraseña— no se ven afectadas por ninguna preferencia (`RN-PREF-03`).
- Las preferencias son individuales. Notifications no admite preferencias por unidad (`RN-PREF-04`).

---

## UF-NOT-03 — Entregar un correo saliente

**Actor principal:** el sistema. Una **tarea programada** revisa periódicamente los envíos pendientes; ninguna persona la inicia.

**Disparador:** existe un envío en estado `PENDIENTE` cuyo `proximo_intento_at` ya venció, o que aún no ha tenido ningún intento.

**Precondiciones:**

- El envío fue creado por el proceso que originó el evento, con su contenido ya resuelto como snapshot (`RN-COR-01`).

**Flujo principal:**

1. La tarea programada selecciona los envíos elegibles mediante el índice `(estado, proximo_intento_at)` de `notificaciones.envios_correo`. La frecuencia con que se ejecuta debe ser menor que la espera más corta de `RN-COR-03`, que es de un minuto.
2. Transmite el correo con el `titulo`, el `cuerpo` y los adjuntos persistidos. Un reintento usa exactamente las mismas versiones de los adjuntos (`RN-COR-06`).
3. Si el mecanismo de entrega confirma la transmisión, el envío pasa a `ENVIADO` y se registra el instante (`RN-COR-02`).
4. Si la transmisión no puede completarse, se registra el error sin credenciales ni trazas internas, se incrementa el número de intentos y se programa el siguiente (`RN-COR-02`).
5. La política de reintento es de hasta cinco intentos con espera creciente de 1, 5, 15, 60 y 240 minutos. No requiere una nueva operación sobre el evento que lo originó (`RN-COR-03`).
6. Agotados los intentos, el envío queda en `FALLIDO` definitivo y sin reintento programado (`RN-COR-03`).

**Flujos alternos:**

- **Anulación.** Si desaparece la condición que justificaba el envío antes de su transmisión —por ejemplo, la reserva se reprograma o se cancela conforme a `UF-RES-16`—, el envío `PENDIENTE` pasa a `ANULADO` con su instante y motivo. No se marca como enviado ni se reintenta (`RN-COR-07`). Un correo ya transmitido no se altera.
- **Envío sin cuenta asociada.** Un correo puede dirigirse a una dirección persistida y verificable aunque todavía no exista una cuenta, como en una invitación de `auth`. Esa condición no crea una notificación in-app (`RN-DES-06`).

**Lo que este flujo no hace:**

- **No invalida la operación de negocio.** Que se agoten los reintentos no revierte ni cuestiona la reserva, la aprobación o la invitación que originó el evento (`RN-COR-04`, `RN-INT-04`).
- **No modifica la notificación in-app.** Ambos canales derivan del mismo evento pero tienen ciclos de vida independientes (`RN-COR-05`).
- **No decide destinatarios ni contenido.** Ambos quedaron resueltos al crear el envío, conforme a `RN-DES` y `RN-CNT`.

**Mecanismo.** Lo ejecuta una tarea programada del propio sistema, no una cola de trabajos externa (`OQ-15`). La consecuencia es que **la política de reintento vive en este dominio**: `intentos` y `proximo_intento_at` de `notificaciones.envios_correo` son la fuente de verdad, y `RN-COR-03` la gobierna. Si la tarea deja de ejecutarse, los envíos permanecen en `PENDIENTE` con su reintento vencido y ninguno se pierde; el retraso es visible consultando esa tabla.

---

## Separación de responsabilidades

- El módulo productor decide **cuándo** ocurre un evento y con qué clave de ocurrencia; Notifications registra y comunica.
- Notifications no decide si una reserva puede crearse, aprobarse, rechazarse, modificarse o cancelarse (`RN-NOT-02`).
- La habilitación de correo por unidad pertenece a Resources; las preferencias individuales, a este módulo (`RN-PREF-02`, `RN-PREF-04`).
- El estado oficial de una reserva pertenece a Reservations; la bandeja no lo sustituye (`RN-HIS-04`).
