# Reservas

Contrato funcional del dominio de reservas.

El modelo persistente se define en [data-model](../core/data-model.md), los espacios en [business-rules.md](../docs/modules/espacios/business-rules.md), los recursos en [business-rules.md](../docs/modules/resources/business-rules.md), la autenticación y autorización en [business-rules.md](../docs/modules/auth/business-rules.md), y las relaciones académicas e investigativas en el módulo correspondiente de investigación.

---

## Creación y composición — RN-RES

- **RN-RES-01:** El usuario debe completar la información requerida de su perfil antes de crear una reserva.
- **RN-RES-02:** Toda reserva debe ser creada por una cuenta autenticada y activa.
- **RN-RES-03:** Toda reserva debe estar asociada a una unidad organizacional receptora mediante `id_unidad`.
- **RN-RES-04:** Los datos y elementos requeridos para crear una reserva dependen del tipo de reserva seleccionado.
- **RN-RES-05:** Todo espacio, recurso, servicio, proyecto, semillero u otro elemento asociado a la reserva debe existir y encontrarse habilitado cuando aplique.
- **RN-RES-06:** Los elementos asociados a una reserva deben pertenecer o estar disponibles para la unidad organizacional receptora, según corresponda.
- **RN-RES-07:** Una misma cuenta puede mantener varias reservas simultáneas siempre que no exista una restricción específica del tipo de reserva ni conflicto sobre los elementos reservados.
- **RN-RES-08:** Crear o modificar una reserva debe revalidar las reglas aplicables a su tipo de reserva.

---

## Catálogo de tipos de reserva — RN-TIP

- **RN-TIP-01:** `tipo_reserva_id` es obligatorio y debe referir un tipo de reserva existente y habilitado.
- **RN-TIP-02:** Si solo existe un tipo de reserva habilitado para el laboratorio, este se asigna automáticamente.
- **RN-TIP-03:** Si existen varios tipos de reserva habilitados para el laboratorio, el usuario debe seleccionar uno.
- **RN-TIP-04:** Cada tipo de reserva debe registrar `nombre`, `descripcion` y `habilitado`. Un tipo deshabilitado no podrá utilizarse en nuevas reservas, pero deberá conservarse para mantener las referencias y el historial de las reservas existentes.
- **RN-TIP-05:** Cada laboratorio debe tener definidos los tipos de reserva que ofrece. Una reserva solo puede utilizar un tipo habilitado para el laboratorio seleccionado.
- **RN-TIP-06:** Si un laboratorio no tiene ningún tipo de reserva habilitado, no se podrá crear una nueva reserva para ese laboratorio.

Los tipos de reserva contemplados actualmente son:

- Reserva por espacio.
- Recurso para uso dentro del laboratorio.
- Recurso para uso dentro del campus y fuera del laboratorio.
- Recurso fuera del campus.
- Lista de espera.
- Servicio.

---

## Reserva por espacio — RN-TIP-PE

- **RN-TIP-PE-01:** La reserva requiere seleccionar una fecha y un horario de inicio y finalización.
- **RN-TIP-PE-02:** La fecha y el horario solicitados deben encontrarse dentro de la disponibilidad definida para el espacio.
- **RN-TIP-PE-03:** No se podrá crear una reserva que se solape con otra reserva bloqueante para el mismo espacio.
- **RN-TIP-PE-04:** La reserva debe estar asociada a un espacio habilitado para reservas.
- **RN-TIP-PE-05:** La cantidad de personas asociadas a la reserva no podrá superar la capacidad habilitada del espacio.
- **RN-TIP-PE-06:** Toda reserva por espacio debe registrar al menos un contexto de uso: proyecto, semillero o actividad institucional.
- **RN-TIP-PE-07:** El usuario solo puede asociar proyectos y semilleros en los que tenga una vinculación activa registrada en su perfil.
- **RN-TIP-PE-08:** Cuando el usuario seleccione proyecto o semillero y exista una única opción disponible, esta se selecciona automáticamente.
- **RN-TIP-PE-09:** Cuando existan varias opciones disponibles para el contexto seleccionado, el usuario debe seleccionar una.
- **RN-TIP-PE-10:** Una reserva puede asociarse simultáneamente a un proyecto y a un semillero.
- **RN-TIP-PE-11:** Cuando la reserva no se asocie a proyecto ni semillero, debe registrarse una actividad institucional.
- **RN-TIP-PE-12:** Al seleccionar un espacio, el sistema debe cargar los recursos asociados y los campos adicionales configurados para ese espacio.
- **RN-TIP-PE-13:** El sistema debe indicar cuáles recursos asociados al espacio se encuentran disponibles y cuáles no están disponibles para la fecha y horario solicitados.
- **RN-TIP-PE-14:** La falta de disponibilidad de uno o más recursos asociados al espacio no impide crear la reserva del espacio.
- **RN-TIP-PE-15:** La reserva por espacio debe permitir registrar una observación para comunicar al gestor necesidades, restricciones o información adicional relacionada con los recursos requeridos.
- **RN-TIP-PE-16:** Al revisar la solicitud, el gestor debe visualizar la disponibilidad de los recursos asociados al espacio y la observación registrada por el usuario.
- **RN-TIP-PE-17:** Antes de aprobar la reserva, el gestor puede modificar los recursos asociados a la solicitud para ajustarla según la disponibilidad existente, sin alterar el espacio solicitado salvo que el flujo de gestión lo permita expresamente.
- **RN-TIP-PE-18:** Cuando el espacio tenga campos adicionales configurados como obligatorios, el usuario debe diligenciarlos antes de enviar la solicitud.
- **RN-TIP-PE-19:** Si el espacio no tiene campos adicionales configurados, la reserva continúa sin solicitar información adicional.
- **RN-TIP-PE-20:** Los valores diligenciados en los campos adicionales deben conservarse asociados a la reserva como parte de su información histórica.

---

## Recurso para uso dentro del laboratorio — RN-TIP-RI

- **RN-TIP-RI-01:** La reserva corresponde a un único recurso que será utilizado dentro de las instalaciones del laboratorio.
- **RN-TIP-RI-02:** La reserva requiere seleccionar una fecha de inicio de uso y una fecha de finalización de uso.
- **RN-TIP-RI-03:** El recurso debe estar disponible durante todo el periodo solicitado.
- **RN-TIP-RI-04:** No se podrá crear una reserva que se solape con otra reserva bloqueante para el mismo recurso durante el periodo solicitado.
- **RN-TIP-RI-05:** La reserva de un recurso para uso dentro del laboratorio no requiere asociarlo a una reserva de espacio.
- **RN-TIP-RI-06:** El recurso reservado puede corresponder a un equipo con placa de identificación o a un recurso sin placa, según su clasificación en el inventario.
- **RN-TIP-RI-07:** La entrega del recurso al usuario requiere la aprobación previa del gestor.
- **RN-TIP-RI-08:** Al entregar físicamente el recurso al usuario, la reserva debe pasar al estado `EN_EJECUCION`.
- **RN-TIP-RI-09:** Al recibir nuevamente el recurso o finalizar su uso dentro del laboratorio, el gestor debe registrar la devolución o finalización y la reserva debe pasar al estado `FINALIZADA`.

---

## Recurso para uso dentro del campus — RN-TIP-RC

- **RN-TIP-RC-01:** La reserva corresponde a un único recurso que saldrá del laboratorio, pero permanecerá dentro del campus autorizado.
- **RN-TIP-RC-02:** La reserva requiere seleccionar una fecha de salida y una fecha de devolución del recurso.
- **RN-TIP-RC-03:** El recurso debe estar disponible durante todo el periodo comprendido entre la fecha de salida y la fecha de devolución solicitadas.
- **RN-TIP-RC-04:** No se podrá crear una reserva que se solape con otra reserva bloqueante para el mismo recurso durante el periodo solicitado.
- **RN-TIP-RC-05:** El recurso reservado puede corresponder a un equipo con placa de identificación o a un recurso sin placa, según su clasificación en el inventario.
- **RN-TIP-RC-06:** La entrega del recurso al usuario requiere la aprobación previa del gestor.
- **RN-TIP-RC-07:** El sistema debe generar la orden de salida correspondiente al uso del recurso dentro del campus y fuera del laboratorio.
- **RN-TIP-RC-08:** La orden de salida debe registrar la aprobación del gestor y la recepción del recurso por parte del usuario.
- **RN-TIP-RC-09:** Al entregar físicamente el recurso al usuario, la reserva debe pasar al estado `EN_EJECUCION`.
- **RN-TIP-RC-10:** Al recibir nuevamente el recurso, el gestor debe registrar su devolución y la reserva debe pasar al estado `FINALIZADA`.

---

## Recurso fuera del campus — RN-TIP-RE

- **RN-TIP-RE-01:** La reserva corresponde a un único recurso autorizado para salir del campus.
- **RN-TIP-RE-02:** La reserva requiere seleccionar una fecha de salida y una fecha de devolución.
- **RN-TIP-RE-03:** El recurso debe estar disponible durante todo el periodo comprendido entre la fecha de salida y la fecha de devolución solicitadas.
- **RN-TIP-RE-04:** No se podrá crear una reserva que se solape con otra reserva bloqueante para el mismo recurso durante el periodo solicitado.
- **RN-TIP-RE-05:** El recurso reservado puede corresponder a un equipo con placa de identificación o a un recurso sin placa, según su clasificación en el inventario.
- **RN-TIP-RE-06:** La salida del recurso requiere la aprobación previa del gestor.
- **RN-TIP-RE-07:** El sistema debe generar la orden de salida externa correspondiente al retiro del recurso fuera del campus.
- **RN-TIP-RE-08:** La orden de salida externa debe registrar la aprobación del gestor y la recepción del recurso por parte del usuario.
- **RN-TIP-RE-09:** Al entregar físicamente el recurso al usuario, la reserva debe pasar al estado `EN_EJECUCION`.
- **RN-TIP-RE-10:** Al recibir nuevamente el recurso, el gestor debe registrar su devolución y la reserva debe pasar al estado `FINALIZADA`.

---

## Lista de espera — RN-TIP-PLE

- **RN-TIP-PLE-01:** La reserva no requiere seleccionar fecha ni horario de ejecución al momento de la solicitud.
- **RN-TIP-PLE-02:** La solicitud debe incluir una descripción de la necesidad y podrá incluir un archivo CAD, una imagen u otro archivo técnico asociado cuando corresponda.
- **RN-TIP-PLE-03:** El formulario complementario solo se habilita después de que el gestor determine que la solicitud es viable.
- **RN-TIP-PLE-04:** La evaluación de viabilidad y la aprobación del formulario complementario forman parte del flujo interno de revisión y no constituyen estados globales de la reserva.
- **RN-TIP-PLE-05:** La reserva pasa al estado `APROBADA` cuando se han completado las aprobaciones requeridas y el gestor registra la recepción del material necesario para su ejecución.
- **RN-TIP-PLE-06:** Las reservas de tipo lista de espera en estado `APROBADA` no siguen un orden cronológico obligatorio. El gestor selecciona la siguiente reserva a ejecutar según la prioridad o los criterios operativos aplicables.
- **RN-TIP-PLE-07:** Cuando el gestor inicia la fabricación o prestación correspondiente, la reserva debe pasar al estado `EN_EJECUCION`.
- **RN-TIP-PLE-08:** Al finalizar la ejecución, el gestor debe registrar las horas empleadas y la reserva debe pasar al estado `FINALIZADA`.

---

## Reserva por servicio — RN-TIP-SER

Las reglas específicas de este tipo de reserva se definirán cuando se establezca su flujo funcional. Hasta entonces, le aplican únicamente las reglas generales del dominio que sean compatibles con su naturaleza.

---

## Horario para reservas con franja horaria — RN-HOR

- **RN-HOR-01:** Estas reglas aplican únicamente a los tipos de reserva que utilizan `hora_inicio` y `hora_fin`.
- **RN-HOR-02:** `hora_inicio` debe ser menor que `hora_fin`.
- **RN-HOR-03:** Una reserva con franja horaria no puede cruzar medianoche.
- **RN-HOR-04:** La reserva debe encontrarse dentro del horario habilitado para la unidad, laboratorio o espacio correspondiente.
- **RN-HOR-05:** No se aceptan fechas pasadas al crear o reprogramar una reserva con franja horaria.
- **RN-HOR-06:** `horas_antelacion` se valida al crear una reserva y al reprogramarla. No se vuelve a exigir al momento de aprobarla.
- **RN-HOR-07:** La validación de horario debe utilizar la configuración vigente de la unidad al momento de crear, modificar o aprobar la reserva.

---

## Estados — RN-EST

Los únicos estados globales válidos son:

- `SOLICITADA`
- `APROBADA`
- `RECHAZADA`
- `EN_EJECUCION`
- `FINALIZADA`
- `CANCELADA`

- **RN-EST-01:** Una reserva puede iniciar en `SOLICITADA` o `APROBADA` según las reglas de aprobación definidas en `RN-APR`.
- **RN-EST-02:** `SOLICITADA`, `APROBADA` y `EN_EJECUCION` se consideran estados bloqueantes para la disponibilidad de los espacios o recursos que formen parte efectiva de la reserva, cuando aplique.
- **RN-EST-03:** `RECHAZADA`, `FINALIZADA` y `CANCELADA` no bloquean disponibilidad futura.
- **RN-EST-04:** Una reserva `RECHAZADA`, `FINALIZADA` o `CANCELADA` conserva su información histórica y no se elimina físicamente por causa del cambio de estado.
- **RN-EST-05:** Las acciones intermedias propias de un tipo de reserva, como evaluación de viabilidad, diligenciamiento de formularios o recepción de material, no constituyen estados globales salvo que se incorporen expresamente al catálogo de estados.

---

## Disponibilidad — RN-DIS

- **RN-DIS-01:** Para reservas con franja horaria, los intervalos se interpretan como `[hora_inicio, hora_fin)`. Dos reservas contiguas no se consideran solapadas cuando una termina exactamente a la hora en que inicia la otra.
- **RN-DIS-02:** Para reservas de recursos por días, el periodo comprende la fecha de salida o inicio y la fecha de devolución o finalización. Dos reservas se consideran solapadas cuando comparten al menos una fecha del periodo reservado.
- **RN-DIS-03:** La disponibilidad se valida de forma independiente para el espacio y para cada recurso individual asociado, salvo los recursos complementarios de una reserva por espacio cuya falta de disponibilidad no bloquee la reserva según `RN-TIP-PE-14`.
- **RN-DIS-04:** Un equipo debe encontrarse operativo según la información vigente del sistema de origen correspondiente al momento de crear o aprobar la reserva.
- **RN-DIS-05:** Crear, modificar horario o fechas, agregar o cambiar elementos y aprobar una reserva deben utilizar la garantía transaccional definida en [data-model](../core/data-model.md#4-garantia-transaccional). Consultar disponibilidad antes de guardar no constituye por sí solo una garantía suficiente.
- **RN-DIS-06:** La validación de disponibilidad debe considerar como bloqueantes únicamente las reservas en estados definidos como bloqueantes por `RN-EST-02`.

---

## Propiedad y acceso — RN-PRO

- **RN-PRO-01:** La cuenta usuario puede consultar sus propias reservas independientemente de su estado.
- **RN-PRO-02:** La cuenta usuario puede editar sus propias reservas únicamente cuando el estado de la reserva y las reglas de negocio permitan la modificación.
- **RN-PRO-03:** Una cuenta sin permisos administrativos no puede consultar, modificar, aprobar, rechazar ni cancelar reservas pertenecientes a terceros.
- **RN-PRO-04:** El personal autorizado puede consultar y gestionar reservas de terceros únicamente dentro de las unidades organizacionales incluidas en su ámbito de autorización.
- **RN-PRO-05:** La autenticación y la validación de permisos se rigen por las reglas definidas en el módulo `auth`. Las reglas de este dominio determinan qué acciones requieren dichos permisos y sobre qué unidad organizacional deben aplicarse.

---

## Aprobación — RN-APR

- **RN-APR-01:** Solo una cuenta autenticada con permiso para gestionar reservas de la unidad receptora puede aprobar o rechazar una reserva.
- **RN-APR-02:** La aprobación automática de reservas creadas por usuarios puede habilitarse o deshabilitarse por el gestor desde la configuración de su unidad organizacional.
- **RN-APR-03:** Cuando la aprobación automática esté habilitada para la unidad organizacional, la reserva creada por un usuario se registra directamente en estado `APROBADA`, siempre que cumpla las validaciones aplicables a su tipo.
- **RN-APR-04:** Cuando la aprobación automática no esté habilitada, la reserva creada por un usuario se registra en estado `SOLICITADA` y requiere revisión del gestor.
- **RN-APR-05:** Las reservas creadas por un gestor dentro de una unidad organizacional en la que tenga permiso de gestión se registran directamente en estado `APROBADA`.
- **RN-APR-06:** La aprobación automática, tanto para usuarios como para gestores, no omite las validaciones aplicables al tipo de reserva, incluyendo disponibilidad, horario o fechas, capacidad, estado operativo, habilitación y pertenencia a la unidad cuando correspondan.
- **RN-APR-07:** Aprobar una reserva manualmente debe revalidar las condiciones aplicables a su tipo.
- **RN-APR-08:** Rechazar una reserva conserva toda su información histórica y debe registrar el motivo del rechazo.

---

## Cancelación — RN-CAN

- **RN-CAN-01:** Cancelar una reserva conserva el registro y libera inmediatamente los espacios y recursos asociados para efectos de disponibilidad futura.
- **RN-CAN-02:** Una reserva puede cancelarse mientras no haya iniciado su ejecución. Para reservas con horario, el límite corresponde al inicio de la franja reservada. Para reservas de recursos, el límite corresponde a la entrega física del recurso o al registro de inicio de ejecución, según aplique.
- **RN-CAN-03:** Toda cancelación registra el actor, el momento de la acción y el motivo cuando corresponda.
- **RN-CAN-04:** Cuando se deshabilite un espacio o recurso, todas las reservas futuras que dependan de ese elemento deben pasar automáticamente al estado `CANCELADA`.
- **RN-CAN-05:** La cancelación automática por deshabilitación aplica únicamente a reservas cuya ejecución aún no haya iniciado.
- **RN-CAN-06:** El sistema debe notificar a los usuarios afectados que la reserva fue cancelada por la deshabilitación del espacio o recurso asociado, conforme a las reglas y canales definidos en [business-rules.md](../docs/modules/notifications/business-rules.md).
- **RN-CAN-07:** La cancelación automática debe registrar como motivo la deshabilitación del espacio o recurso y conservar la trazabilidad histórica de la reserva.

---

## Contexto académico e institucional — RN-CTX

- **RN-CTX-01:** Una reserva puede asociarse al contexto académico, investigativo o institucional bajo el cual se realiza.
- **RN-CTX-02:** Cuando se asocie un perfil, semillero o proyecto, la cuenta usuario debe estar relacionada válidamente con dicho elemento al momento de crear la reserva.
- **RN-CTX-03:** Cuando el tipo de reserva exija un contexto y el usuario no esté vinculado a un proyecto ni a un semillero, la reserva podrá asociarse a una actividad institucional habilitada.
- **RN-CTX-04:** El contexto asociado a una reserva debe conservarse históricamente aunque posteriormente cambien los perfiles, proyectos, semilleros, actividades institucionales o modalidades de vinculación del usuario.
- **RN-CTX-05:** Una reserva no requiere simultáneamente perfil, semillero, proyecto y modalidad. Solo se registran los elementos que correspondan al contexto real y a las reglas de su tipo de reserva.
- **RN-CTX-06:** El contexto académico, investigativo o institucional de una reserva no otorga por sí mismo permisos administrativos sobre reservas.

---

## Auditoría — RN-AUD

- **RN-AUD-01:** Crear, modificar, aprobar, rechazar, iniciar ejecución, finalizar y cancelar una reserva genera un registro de auditoría.
- **RN-AUD-02:** El registro de auditoría incluye como mínimo actor, acción, entidad, identificador de la entidad y fecha/hora.
- **RN-AUD-03:** Toda acción auditada debe identificar la cuenta autenticada que la ejecutó y conservar una representación histórica suficiente del actor, independientemente de que la cuenta corresponda a un usuario o a personal.
- **RN-AUD-04:** La trazabilidad histórica no debe depender de que el usuario, personal, cargo, proyecto, semillero, actividad institucional o modalidad permanezcan activos posteriormente.

---

## Dependencias funcionales

Las reglas de este documento dependen de otros dominios únicamente en los siguientes aspectos:

- **Autenticación y autorización:** [business-rules.md](../docs/modules/auth/business-rules.md) determina autenticación, cuentas activas y validación de permisos.
- **Espacios:** [business-rules.md](../docs/modules/espacios/business-rules.md) determina existencia, habilitación, capacidad, configuración, campos adicionales y recursos asociados a los espacios.
- **Recursos:** [business-rules.md](../docs/modules/resources/business-rules.md) determina existencia, habilitación, clasificación y estado operativo de los recursos.
- **Notificaciones:** [business-rules.md](../docs/modules/notifications/business-rules.md) determina canales, mecanismos y reglas de entrega de las notificaciones generadas por el dominio de reservas.
- **Modelo persistente:** [data-model](../core/data-model.md) define claves, relaciones, constraints y garantías transaccionales.
- **Investigación y contexto institucional:** perfiles, semilleros, proyectos, actividades institucionales y modalidades de vinculación son datos de contexto y no sustituyen las reglas de autorización.

---

## Principios del dominio

1. Una reserva siempre tiene una cuenta usuario y una unidad receptora.
2. Toda reserva debe contener los datos y elementos obligatorios definidos para su tipo de reserva.
3. La disponibilidad se protege tanto por reglas de negocio como por garantía transaccional.
4. El acceso a reservas de terceros depende de autorización, no del tipo de usuario por sí solo.
5. Las relaciones académicas, investigativas e institucionales contextualizan la reserva, pero no conceden permisos administrativos.
6. Los tipos de reserva comparten estados globales, pero pueden tener acciones y etapas internas propias que no constituyen nuevos estados.
7. Las acciones relevantes conservan trazabilidad histórica.
