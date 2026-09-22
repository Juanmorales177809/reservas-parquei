# Notificaciones

Contrato funcional del módulo de notificaciones.

Las notificaciones informan a los usuarios sobre eventos relevantes generados por otros módulos. Este módulo no decide si una reserva puede crearse, aprobarse, rechazarse, modificarse o cancelarse; únicamente registra y presenta las notificaciones derivadas de dichas operaciones.

Las reglas que determinan cuándo ocurre un evento pertenecen al módulo propietario correspondiente.

Un mismo evento puede dar lugar a dos registros independientes: una notificación in-app (ver RN-EST) y un envío de correo saliente (ver RN-COR). Ambos se derivan del mismo evento, pero cada uno tiene su propio ciclo de vida — la existencia, el contenido o el estado de uno no condiciona la existencia, el contenido o el estado del otro.

---

## Creación de notificaciones — RN-NOT

- **RN-NOT-01:** Toda notificación debe estar asociada a un evento identificable, generado ya sea por una operación válida del sistema o por una condición temporal verificada por un proceso automático (por ejemplo, un recordatorio previo al inicio de una reserva).

- **RN-NOT-02:** La creación de una notificación no puede modificar el resultado de la operación o condición que la originó.

- **RN-NOT-03:** Una notificación debe identificar como mínimo el destinatario, el tipo de evento, la fecha y hora de generación y la referencia al elemento relacionado cuando corresponda.

- **RN-NOT-04:** El contenido de una notificación debe corresponder al evento que la originó y no debe inferir estados o resultados distintos de los registrados por el módulo propietario.

- **RN-NOT-05:** Una misma ocurrencia de evento no debe generar notificaciones duplicadas para el mismo destinatario y canal. La ocurrencia se identifica mediante una clave estable definida por el proceso que la origina, no solo por el tipo de evento o la reserva relacionada.

- **RN-NOT-06:** Un evento puede originar, según corresponda, una notificación in-app, un envío de correo, ambos o ninguno. La determinación de qué canales aplican para cada tipo de evento pertenece a la configuración del sistema y a las preferencias vigentes del destinatario (ver RN-PREF).

---

## Destinatarios — RN-DES

- **RN-DES-01:** Toda notificación debe tener al menos un destinatario identificable por el sistema.

- **RN-DES-02:** El destinatario debe determinarse a partir de información persistente y verificable del sistema, no de datos de identidad suministrados libremente por el cliente.

- **RN-DES-03:** Una notificación destinada al reservista debe asociarse a la cuenta responsable de la reserva correspondiente.

- **RN-DES-04:** Cuando una operación administrativa requiera notificar a un Técnico o Administrador, los destinatarios deben determinarse mediante las reglas vigentes de autorización y alcance organizacional.

- **RN-DES-05:** La existencia de una notificación histórica no depende de que el destinatario permanezca activo posteriormente.

- **RN-DES-06:** Un correo puede destinarse a una dirección persistida y verificable aunque todavía no exista una cuenta asociada, cuando el proceso propietario lo autorice, como en una invitación de `auth`. Esta condición no crea una notificación in-app.

---

## Eventos de reserva — RN-EVT

Las siguientes reglas definen eventos notificables asociados al ciclo de vida de una reserva. La validez de la operación que genera cada evento se determina en el módulo de reservas.

- **RN-EVT-01:** La creación de una solicitud de reserva genera una notificación para el reservista confirmando que la solicitud fue registrada.

- **RN-EVT-02:** La aprobación de una reserva genera una notificación para el reservista indicando el nuevo estado.

- **RN-EVT-03:** El rechazo de una reserva genera una notificación para el reservista indicando el nuevo estado.

- **RN-EVT-04:** Cuando el rechazo tenga un motivo registrado, dicho motivo puede incorporarse al contenido de la notificación.

- **RN-EVT-05:** La cancelación de una reserva genera una notificación para las personas que deban ser informadas conforme a las reglas del proceso correspondiente.

- **RN-EVT-06:** Cuando una reserva futura resulte afectada por la deshabilitación de un espacio o recurso, el sistema debe generar el tratamiento de notificación definido para dicho caso.

- **RN-EVT-07:** La modificación de una reserva solo genera una nueva notificación cuando el cambio corresponda a un evento definido como notificable.

- **RN-EVT-08:** El registro de una propuesta de horario alternativo, y el registro de una contrapropuesta, generan cada uno una notificación para la contraparte del intercambio.

- **RN-EVT-09:** La incorporación de un recurso adicional a una reserva ya aprobada genera una notificación para el reservista indicando el recurso agregado.

- **RN-EVT-10:** Las reservas de tipo lista de espera generan las notificaciones de cambios de estado definidas en este módulo. Su ejecución se rige por RN-TIP-PLE de Reservations; no se generan avisos de liberación de cupo, turnos ni vencimientos de confirmación.

- **RN-EVT-11:** El vencimiento del plazo de un recordatorio automático previo al inicio de una reserva genera una notificación para el reservista, sin que esto constituya una operación sobre la reserva.

---

## Estado de las notificaciones in-app — RN-EST

- **RN-EST-01:** Una notificación in-app debe conservar su estado de lectura de manera independiente del estado del elemento que la originó.

- **RN-EST-02:** Una notificación in-app nueva se registra inicialmente como no leída.

- **RN-EST-03:** El destinatario puede marcar una notificación in-app propia como leída.

- **RN-EST-04:** Marcar una notificación in-app como leída no modifica el estado de la reserva, recurso, operación relacionada ni de un envío de correo asociado al mismo evento.

- **RN-EST-05:** El sistema debe permitir distinguir entre notificaciones in-app leídas y no leídas.

---

## Correo saliente — RN-COR

- **RN-COR-01:** Un envío de correo asociado a un evento notificable se registra inicialmente en estado pendiente.

- **RN-COR-02:** Un envío de correo pasa a estado enviado cuando el mecanismo de entrega confirma su transmisión, o a estado fallido cuando la transmisión no puede completarse.

- **RN-COR-03:** Un envío de correo en estado fallido debe reintentarse automáticamente, sin requerir una nueva operación sobre el evento que lo originó. La política es de hasta cinco intentos con espera creciente de 1, 5, 15, 60 y 240 minutos; agotados, el envío queda en estado fallido definitivo. Su representación persistente se define en [data-model.md](data-model.md).

- **RN-COR-04:** El agotamiento de los reintentos de un envío de correo no invalida la operación de negocio que originó el evento (ver RN-INT-04) ni el registro histórico de la notificación asociada.

- **RN-COR-05:** El estado de un envío de correo se conserva y consulta de forma independiente del estado de lectura de la notificación in-app asociada al mismo evento, cuando ambas existan.

- **RN-COR-06:** Un envío de correo puede incluir uno o más archivos adjuntos cuando el tipo de evento lo requiera (por ejemplo, un archivo de calendario `.ics`), conforme a lo definido en RN-CAL y RN-CNT. Cada reintento utiliza las mismas versiones persistidas de los adjuntos.

- **RN-COR-07:** Un envío en estado `PENDIENTE` puede anularse antes de su transmisión cuando desaparezca la condición que lo justificaba. Se registra como `ANULADO`, con momento y motivo; no se marca como enviado ni se reintenta.

---

## Consulta — RN-CON

- **RN-CON-01:** Una cuenta autenticada puede consultar únicamente las notificaciones destinadas a dicha cuenta, salvo que exista una función administrativa expresamente autorizada.

- **RN-CON-02:** Las consultas deben permitir identificar como mínimo el tipo de evento, la fecha y hora, el estado de lectura y la referencia relacionada cuando exista.

- **RN-CON-03:** Las notificaciones deben poder ordenarse cronológicamente.

- **RN-CON-04:** La consulta de notificaciones no modifica su estado salvo que la operación solicitada implique explícitamente marcarla como leída.

---

## Contenido — RN-CNT

- **RN-CNT-01:** El contenido de una notificación debe ser comprensible sin requerir acceso a información interna de implementación.

- **RN-CNT-02:** Una notificación no debe contener credenciales, hashes de contraseñas, secretos de sesión ni información técnica sensible. Esta restricción no aplica a un token de un solo uso incluido intencionalmente en un correo para completar un flujo específico (por ejemplo, invitación inicial o recuperación de contraseña, ver RN-CAL y dependencias de autenticación), siempre que dicho token no otorgue acceso más allá del flujo para el que fue emitido.

- **RN-CNT-03:** La notificación debe utilizar información suficiente para identificar el evento sin duplicar innecesariamente toda la información de la entidad relacionada.

- **RN-CNT-04:** Cuando el contenido incluya datos que puedan cambiar posteriormente, la notificación debe conservar la información necesaria para representar correctamente el evento ocurrido.

- **RN-CNT-05:** Un envío de correo puede incluir uno o más archivos adjuntos cuando el tipo de evento lo requiera. El adjunto está sujeto a las mismas restricciones de contenido que el resto de la notificación (RN-CNT-01, RN-CNT-02).

---

## Archivos de calendario — RN-CAL

- **RN-CAL-01:** Reservations determina cuándo debe generarse el archivo `.ics` y qué información vigente debe contener, conforme a sus reglas RN-CAL.
- **RN-CAL-02:** Cuando corresponda enviar el correo de confirmación, Notifications adjunta el archivo `.ics` generado para la aprobación o modificación de la reserva.
- **RN-CAL-03:** El envío del archivo `.ics` no implica sincronización directa con calendarios externos ni exige persistir identificadores de eventos externos.

---

## Preferencias de envío — RN-PREF

- **RN-PREF-01:** Un destinatario puede configurar si desea recibir por correo las notificaciones de un tipo de evento determinado. Esta preferencia no afecta la generación ni la consulta de la notificación in-app correspondiente.

- **RN-PREF-02:** La habilitación general del correo para los eventos de una unidad se consulta exclusivamente en `reservas.laboratorios_config.notificar_por_correo`, conforme a RN-LAB-07 de Resources. Si está deshabilitada, no se generan correos para esos eventos, pero las notificaciones in-app permanecen independientes.

- **RN-PREF-03:** Las preferencias de envío no aplican a comunicaciones de autenticación (invitación, recuperación de contraseña) definidas por el módulo correspondiente.

- **RN-PREF-04:** Cuando el correo esté habilitado para la unidad, la preferencia individual más específica de la cuenta —por tipo de evento y, en su ausencia, general— determina si se crea el envío. Las preferencias por unidad no existen en Notifications.

---

## Persistencia e historial — RN-HIS

- **RN-HIS-01:** Las notificaciones se conservan como registros históricos de los eventos comunicados.

- **RN-HIS-02:** La eliminación o desactivación posterior de la entidad relacionada no debe invalidar el registro histórico de la notificación.

- **RN-HIS-03:** Una modificación posterior de una reserva, recurso o usuario no debe modificar retroactivamente el significado de una notificación ya generada.

- **RN-HIS-04:** Las notificaciones no constituyen el registro oficial del estado de una reserva ni sustituyen el historial o auditoría del módulo propietario.

---

## Integridad — RN-INT

- **RN-INT-01:** La generación de una notificación debe producirse únicamente después de que la operación que la origina haya sido aceptada por el sistema.

- **RN-INT-02:** Una notificación no debe comunicar como completada una operación que posteriormente sea revertida por un error de la misma transacción.

- **RN-INT-03:** La estrategia técnica utilizada para coordinar la operación principal y la generación de la notificación debe preservar la consistencia entre ambos registros.

- **RN-INT-04:** Si el mecanismo de entrega o visualización falla, la operación de negocio original no debe considerarse inválida únicamente por dicha falla, salvo que una regla global establezca lo contrario. Para el canal de correo, el comportamiento esperado ante la falla es el reintento automático definido en RN-COR-03, no la invalidación de la operación.

---

## Separación de responsabilidades

- El módulo de reservas determina cuándo una reserva se crea, aprueba, rechaza, modifica o cancela.

- El módulo de recursos determina el estado, habilitación y disponibilidad estructural de espacios y recursos.

- El módulo de autenticación y autorización determina la identidad de la cuenta y los permisos aplicables.

- El módulo de notificaciones determina qué mensaje se registra, quién lo recibe, por qué canal (in-app y/o correo) se entrega, y cuál es el estado de lectura o de envío correspondiente.

- El módulo de notificaciones no modifica estados de reservas, permisos, recursos ni identidades.

---

## Dependencias funcionales

Las reglas de este documento dependen de otros módulos únicamente en los siguientes aspectos:

- **Reservas:** determina los eventos válidos relacionados con creación, aprobación, rechazo, modificación, cancelación y afectación de reservas.

- **Recursos:** determina cuándo un espacio o recurso ha sido deshabilitado o cambia de condición.

- **Autenticación y autorización:** determina la identidad de las cuentas, qué personal se encuentra autorizado dentro de un ámbito organizacional, y los eventos notificables propios de identidad (invitación inicial, reenvío de invitación, recuperación de contraseña, confirmación de cambio de contraseña). El módulo de notificaciones registra y entrega estas comunicaciones bajo las mismas reglas de contenido e integridad que el resto, pero no determina cuándo ocurren.

- **Modelo persistente:** define las claves, relaciones y restricciones utilizadas para asociar una notificación con su destinatario y con el elemento relacionado.

---

## Principios del módulo

1. Una notificación comunica un evento; no lo decide.

2. El módulo propietario del proceso es la fuente de verdad sobre el estado de la operación.

3. Las notificaciones no sustituyen auditoría ni historial de cambios.

4. Una notificación debe conservar suficiente contexto para representar históricamente el evento comunicado.

5. El estado de lectura pertenece exclusivamente a la notificación y no modifica la entidad relacionada.

6. La generación de notificaciones debe evitar duplicados y mantener consistencia con la operación que las origina.

7. La notificación in-app y el envío de correo son registros independientes derivados de un mismo evento; ninguno sustituye ni condiciona al otro.
