# Notificaciones

Contrato funcional del módulo de notificaciones.

Las notificaciones informan a los usuarios sobre eventos relevantes generados por otros módulos. Este módulo no decide si una reserva puede crearse, aprobarse, rechazarse, modificarse o cancelarse; únicamente registra y presenta las notificaciones derivadas de dichas operaciones.

Las reglas que determinan cuándo ocurre un evento pertenecen al módulo propietario correspondiente.

---

## Creación de notificaciones — RN-NOT

- **RN-NOT-01:** Toda notificación debe estar asociada a un evento identificable generado por una operación válida del sistema.

- **RN-NOT-02:** La creación de una notificación no puede modificar el resultado de la operación que la originó.

- **RN-NOT-03:** Una notificación debe identificar como mínimo el destinatario, el tipo de evento, la fecha y hora de generación y la referencia al elemento relacionado cuando corresponda.

- **RN-NOT-04:** El contenido de una notificación debe corresponder al evento que la originó y no debe inferir estados o resultados distintos de los registrados por el módulo propietario.

- **RN-NOT-05:** Una misma operación no debe generar notificaciones duplicadas para el mismo destinatario, evento y referencia funcional.

---

## Destinatarios — RN-DES

- **RN-DES-01:** Toda notificación debe tener al menos un destinatario identificable por el sistema.

- **RN-DES-02:** El destinatario debe determinarse a partir de información persistente y verificable del sistema, no de datos de identidad suministrados libremente por el cliente.

- **RN-DES-03:** Una notificación destinada al reservista debe asociarse a la cuenta responsable de la reserva correspondiente.

- **RN-DES-04:** Cuando una operación administrativa requiera notificar a personal autorizado, los destinatarios deben determinarse mediante las reglas vigentes de autorización y ámbito organizacional definidas por el módulo correspondiente.

- **RN-DES-05:** La existencia de una notificación histórica no depende de que el destinatario permanezca activo posteriormente.

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

---

## Estado de las notificaciones — RN-EST

- **RN-EST-01:** Una notificación debe conservar su estado de lectura de manera independiente del estado del elemento que la originó.

- **RN-EST-02:** Una notificación nueva se registra inicialmente como no leída.

- **RN-EST-03:** El destinatario puede marcar una notificación propia como leída.

- **RN-EST-04:** Marcar una notificación como leída no modifica el estado de la reserva, recurso u operación relacionada.

- **RN-EST-05:** El sistema debe permitir distinguir entre notificaciones leídas y no leídas.

---

## Consulta — RN-CON

- **RN-CON-01:** Una cuenta autenticada puede consultar únicamente las notificaciones destinadas a dicha cuenta, salvo que exista una función administrativa expresamente autorizada.

- **RN-CON-02:** Las consultas deben permitir identificar como mínimo el tipo de evento, la fecha y hora, el estado de lectura y la referencia relacionada cuando exista.

- **RN-CON-03:** Las notificaciones deben poder ordenarse cronológicamente.

- **RN-CON-04:** La consulta de notificaciones no modifica su estado salvo que la operación solicitada implique explícitamente marcarla como leída.

---

## Contenido — RN-CNT

- **RN-CNT-01:** El contenido de una notificación debe ser comprensible sin requerir acceso a información interna de implementación.

- **RN-CNT-02:** Una notificación no debe contener credenciales, tokens, hashes de contraseñas, secretos ni información técnica sensible.

- **RN-CNT-03:** La notificación debe utilizar información suficiente para identificar el evento sin duplicar innecesariamente toda la información de la entidad relacionada.

- **RN-CNT-04:** Cuando el contenido incluya datos que puedan cambiar posteriormente, la notificación debe conservar la información necesaria para representar correctamente el evento ocurrido.

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

- **RN-INT-04:** Si el mecanismo de entrega o visualización falla, la operación de negocio original no debe considerarse inválida únicamente por dicha falla, salvo que una regla global establezca lo contrario.

---

## Separación de responsabilidades

- El módulo de reservas determina cuándo una reserva se crea, aprueba, rechaza, modifica o cancela.

- El módulo de recursos determina el estado, habilitación y disponibilidad estructural de espacios y recursos.

- El módulo de autenticación y autorización determina la identidad de la cuenta y los permisos aplicables.

- El módulo de notificaciones determina qué mensaje se registra, quién lo recibe y cuál es su estado de lectura.

- El módulo de notificaciones no modifica estados de reservas, permisos, recursos ni identidades.

---

## Dependencias funcionales

Las reglas de este documento dependen de otros módulos únicamente en los siguientes aspectos:

- **Reservas:** determina los eventos válidos relacionados con creación, aprobación, rechazo, modificación, cancelación y afectación de reservas.

- **Recursos:** determina cuándo un espacio o recurso ha sido deshabilitado o cambia de condición.

- **Autenticación y autorización:** determina la identidad de las cuentas y, cuando corresponda, qué personal se encuentra autorizado dentro de un ámbito organizacional.

- **Modelo persistente:** define las claves, relaciones y restricciones utilizadas para asociar una notificación con su destinatario y con el elemento relacionado.

---

## Principios del módulo

1. Una notificación comunica un evento; no lo decide.

2. El módulo propietario del proceso es la fuente de verdad sobre el estado de la operación.

3. Las notificaciones no sustituyen auditoría ni historial de cambios.

4. Una notificación debe conservar suficiente contexto para representar históricamente el evento comunicado.

5. El estado de lectura pertenece exclusivamente a la notificación y no modifica la entidad relacionada.

6. La generación de notificaciones debe evitar duplicados y mantener consistencia con la operación que las origina.