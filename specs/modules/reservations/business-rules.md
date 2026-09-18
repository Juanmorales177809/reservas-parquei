# Reservas

Contrato funcional del dominio de reservas.

El modelo persistente se define en [data-model](data-model.md), los espacios en [business-rules.md](../espacios/busines-rules.md), los recursos en [business-rules.md](../resources/business-rules.md), la autenticación y autorización en [business-rules.md](../auth/business-rules.md), y las relaciones académicas e investigativas en el módulo `researchs`.

---

## Creación y composición — RN-RES

- **RN-RES-01:** El Usuario debe cumplir las validaciones aplicables a la creación de la reserva.
- **RN-RES-02:** Toda reserva debe ser creada por una cuenta autenticada y activa.
- **RN-RES-03:** Toda reserva debe estar asociada a una unidad organizacional receptora mediante `id_unidad`.
- **RN-RES-04:** Los datos y elementos requeridos para crear una reserva dependen del tipo de reserva seleccionado.
- **RN-RES-05:** Todo espacio, recurso, proyecto, semillero u otro elemento asociado a la reserva debe existir y encontrarse habilitado cuando aplique.
- **RN-RES-06:** Los elementos asociados a una reserva deben pertenecer o estar disponibles para la unidad organizacional receptora, según corresponda.
- **RN-RES-07:** Una misma cuenta puede mantener varias reservas simultáneas siempre que no exista una restricción específica del tipo de reserva ni conflicto sobre los elementos reservados.
- **RN-RES-08:** Crear o modificar una reserva debe revalidar las reglas aplicables a su tipo de reserva.
- **RN-RES-09:** Cuando un equipo incluido en la reserva tenga `requiere_apoyo = true`, la reserva debe persistir `requiere_apoyo = true` automáticamente y el Usuario no puede desmarcar la opción “requiere técnico”.
- **RN-RES-10:** Cuando ningún equipo incluido exija apoyo, el Usuario puede solicitar voluntariamente apoyo técnico; el valor efectivo se persiste en `reservas.reservas.requiere_apoyo`.
- **RN-RES-11:** Para crear una reserva, la cuenta Usuario debe haber completado la actualización inicial de su perfil conforme a RN-USR-07 y RN-USR-08, y conservar al menos una vinculación activa y válida conforme a RN-USR-11. El backend revalida ambas condiciones al registrar cada nueva reserva. Las vinculaciones seleccionadas como contexto se validan además conforme a RN-CTX-05.
- **RN-RES-12:** Una reserva por espacio admite cero o más recursos complementarios y no exige un recurso principal. Las reservas de recurso interno, campus y externo requieren un recurso principal y admiten adicionales conforme a sus reglas específicas. No se impone un recurso principal a lista de espera por una regla global; su composición corresponde a sus reglas específicas.

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

---

## Reserva por espacio — RN-TIP-PE

- **RN-TIP-PE-01:** La reserva requiere seleccionar una fecha y un horario de inicio y finalización.
- **RN-TIP-PE-02:** La fecha y el horario solicitados deben encontrarse dentro de la disponibilidad definida para el espacio.
- **RN-TIP-PE-03:** No se podrá crear una reserva que se solape con otra reserva bloqueante para el mismo espacio.
- **RN-TIP-PE-04:** La reserva debe estar asociada a un espacio habilitado para reservas.
- **RN-TIP-PE-05:** La cantidad de personas asociadas a la reserva no podrá superar la capacidad habilitada del espacio.
- **RN-TIP-PE-06:** Toda reserva por espacio debe registrar un contexto de uso conforme a `RN-CTX`: uno o más elementos académicos/investigativos, o una actividad institucional independiente.
- **RN-TIP-PE-07:** El usuario solo puede asociar proyectos, semilleros, pasantías y trabajos de grado para los que tenga una vinculación válida conforme a `RN-CTX-05`.
- **RN-TIP-PE-08:** Cuando el usuario seleccione un elemento de contexto académico/investigativo y exista una única opción válida disponible, esta se selecciona automáticamente.
- **RN-TIP-PE-09:** Cuando existan varias opciones válidas para un elemento de contexto seleccionado, el usuario debe seleccionar una para ese elemento.
- **RN-TIP-PE-10:** Una reserva puede asociarse simultáneamente a un proyecto, un semillero, una pasantía y un trabajo de grado, conforme a `RN-CTX-03`.
- **RN-TIP-PE-11:** Cuando la reserva no se asocie a ningún elemento académico/investigativo, debe registrarse una actividad institucional habilitada. Esta no puede coexistir con los demás elementos de contexto, conforme a `RN-CTX-04`.
- **RN-TIP-PE-12:** Al seleccionar un espacio, el sistema debe cargar los recursos asociados y los campos adicionales configurados para ese espacio.
- **RN-TIP-PE-13:** El sistema debe indicar cuáles recursos asociados al espacio se encuentran disponibles y cuáles no están disponibles para la fecha y horario solicitados.
- **RN-TIP-PE-14:** La falta de disponibilidad de uno o más recursos complementarios asociados al espacio no impide crear la reserva del espacio; esos recursos no pueden quedar asignados durante el periodo incompatible.
- **RN-TIP-PE-15:** La reserva por espacio debe permitir registrar una observación para comunicar al Técnico  necesidades, restricciones o información adicional relacionada con los recursos requeridos.
- **RN-TIP-PE-16:** Al revisar la solicitud, el Técnico  debe visualizar la disponibilidad de los recursos asociados al espacio y la observación registrada por el usuario.
- **RN-TIP-PE-17:** Antes de aprobar la reserva, el Técnico  puede modificar los recursos asociados a la solicitud para ajustarla según la disponibilidad existente, sin alterar el espacio solicitado salvo que el flujo de gestión lo permita expresamente.
- **RN-TIP-PE-18:** Cuando el espacio tenga campos adicionales configurados como obligatorios, el usuario debe diligenciarlos antes de enviar la solicitud.
- **RN-TIP-PE-19:** Si el espacio no tiene campos adicionales configurados, la reserva continúa sin solicitar información adicional.
- **RN-TIP-PE-20:** Los valores diligenciados en los campos adicionales deben conservarse asociados a la reserva como parte de su información histórica.
- **RN-TIP-PE-21:** El Técnico  puede agregar recursos asociados a una reserva en estado `SOLICITADA`, `APROBADA` o `EN_EJECUCION`.
- **RN-TIP-PE-22:** Todo recurso agregado debe encontrarse habilitado, operativo y disponible durante el periodo de uso requerido por la reserva.
- **RN-TIP-PE-23:** Cuando se agregue un recurso a una reserva en estado `EN_EJECUCION`, la disponibilidad debe validarse desde el momento de su incorporación hasta la finalización prevista de la reserva.

---

## Recurso para uso dentro del laboratorio — RN-TIP-RI

- **RN-TIP-RI-01:** La reserva corresponde a un único recurso que será utilizado dentro de las instalaciones del laboratorio.
- **RN-TIP-RI-02:** La reserva requiere seleccionar una fecha de inicio de uso y una fecha de finalización de uso.
- **RN-TIP-RI-03:** El recurso debe estar disponible durante todo el periodo solicitado.
- **RN-TIP-RI-04:** No se podrá crear una reserva que se solape con otra reserva bloqueante para el mismo recurso durante el periodo solicitado.
- **RN-TIP-RI-05:** La reserva de un recurso para uso dentro del laboratorio no requiere asociarlo a una reserva de espacio.
- **RN-TIP-RI-06:** El recurso reservado puede corresponder a un equipo con placa de identificación o a un recurso sin placa, según su clasificación en el inventario.
- **RN-TIP-RI-07:** La entrega del recurso al usuario requiere la aprobación previa del Técnico .
- **RN-TIP-RI-08:** Al entregar físicamente el recurso al usuario, la reserva debe pasar al estado `EN_EJECUCION`.
- **RN-TIP-RI-09:** Al recibir nuevamente el recurso o finalizar su uso dentro del laboratorio, el Técnico  debe registrar la devolución o finalización y la reserva debe pasar al estado `FINALIZADA`.
- **RN-TIP-RI-10:** El Técnico  puede agregar recursos adicionales a una reserva en estado `SOLICITADA`, `APROBADA` o `EN_EJECUCION`.
- **RN-TIP-RI-11:** Todo recurso agregado debe encontrarse habilitado, operativo y disponible durante el periodo de uso requerido por la reserva.
- **RN-TIP-RI-12:** Cuando se agregue un recurso a una reserva en estado `EN_EJECUCION`, la disponibilidad debe validarse desde el momento de su incorporación hasta la finalización prevista de la reserva.

---

## Recurso para uso dentro del campus — RN-TIP-RC

- **RN-TIP-RC-01:** La reserva corresponde a uno o varios recursos (un `PRINCIPAL` y, opcionalmente, `ADICIONAL`es) que saldrán del laboratorio, pero permanecerán dentro del campus autorizado. Todos los recursos de la reserva comparten la misma fecha de salida y de devolución.
- **RN-TIP-RC-02:** La reserva requiere seleccionar una fecha de salida y una fecha de devolución, aplicable a todos sus recursos.
- **RN-TIP-RC-03:** Cada recurso debe estar disponible durante todo el periodo comprendido entre la fecha de salida y la fecha de devolución solicitadas.
- **RN-TIP-RC-04:** No se podrá crear una reserva que se solape con otra reserva bloqueante para alguno de sus recursos durante el periodo solicitado.
- **RN-TIP-RC-05:** Cada recurso reservado puede corresponder a un equipo con placa de identificación o a un recurso sin placa, según su clasificación en el inventario.
- **RN-TIP-RC-06:** La entrega de los recursos al usuario requiere la aprobación previa del Técnico .
- **RN-TIP-RC-07:** El sistema debe generar la orden de salida correspondiente al uso de los recursos dentro del campus y fuera del laboratorio, listando todos los recursos de la reserva.
- **RN-TIP-RC-08:** La orden de salida debe registrar la aprobación del Técnico  y la recepción de los recursos por parte del usuario.
- **RN-TIP-RC-09:** Al entregar físicamente los recursos al usuario, la reserva debe pasar al estado `EN_EJECUCION`.
- **RN-TIP-RC-10:** Al recibir nuevamente los recursos, el Técnico  debe registrar su devolución y la reserva debe pasar al estado `FINALIZADA`.
- **RN-TIP-RC-11:** La orden de salida (`RN-TIP-RC-07`) debe poder exportarse prellenada en el formato institucional "FGL 030 Orden de salida equipos y herramientas".
- **RN-TIP-RC-12:** Al crear la reserva, el usuario debe registrar adicionalmente: razón de la solicitud, nombre y dirección del lugar al cual serán desplazados los equipos o herramientas, y el nombre de la actividad o evento cuando aplique según el contexto.
- **RN-TIP-RC-13:** Los siguientes datos se prellenan a partir de información ya existente en la reserva, sin solicitarse nuevamente: dependencia solicitante (unidad receptora), fecha de retiro y fecha de regreso, actividad asociada (proyecto de investigación, semillero, proyecto académico, servicio de extensión, docencia, calibración, mantenimiento u otro, según el contexto registrado en `RN-CTX`), código del proyecto de investigación cuando corresponda, y nombre, cédula y contacto del responsable de la solicitud, tomados del perfil de la cuenta usuario. Los datos técnicos de cada recurso (placa, descripción, bodega, centro de costo y fecha de compra) se prellenan a partir del inventario de recursos.
- **RN-TIP-RC-14:** Las firmas, cargos de los autorizantes y los registros de entrega o devolución física de los recursos no se prellenan; se diligencian manualmente o se registran en el momento correspondiente del flujo de aprobación y ejecución.
- **RN-TIP-RC-15:** Cuando la reserva se reprograme extendiendo su fecha de devolución, la orden de salida debe reflejar la fecha de prórroga de los recursos.

---

## Recurso fuera del campus — RN-TIP-RE

- **RN-TIP-RE-01:** La reserva corresponde a uno o varios recursos (un `PRINCIPAL` y, opcionalmente, `ADICIONAL`es) autorizados para salir del campus. Todos los recursos de la reserva comparten la misma fecha de salida y de devolución.
- **RN-TIP-RE-02:** La reserva requiere seleccionar una fecha de salida y una fecha de devolución, aplicable a todos sus recursos.
- **RN-TIP-RE-03:** Cada recurso debe estar disponible durante todo el periodo comprendido entre la fecha de salida y la fecha de devolución solicitadas.
- **RN-TIP-RE-04:** No se podrá crear una reserva que se solape con otra reserva bloqueante para alguno de sus recursos durante el periodo solicitado.
- **RN-TIP-RE-05:** Cada recurso reservado puede corresponder a un equipo con placa de identificación o a un recurso sin placa, según su clasificación en el inventario.
- **RN-TIP-RE-06:** La salida de los recursos requiere la aprobación previa del Técnico .
- **RN-TIP-RE-07:** El sistema debe generar la orden de salida externa correspondiente al retiro de los recursos fuera del campus, listando todos los recursos de la reserva.
- **RN-TIP-RE-08:** La orden de salida externa debe registrar la aprobación del Técnico  y la recepción de los recursos por parte del usuario.
- **RN-TIP-RE-09:** Al entregar físicamente los recursos al usuario, la reserva debe pasar al estado `EN_EJECUCION`.
- **RN-TIP-RE-10:** Al recibir nuevamente los recursos, el Técnico  debe registrar su devolución y la reserva debe pasar al estado `FINALIZADA`.
- **RN-TIP-RE-11:** La orden de salida externa (`RN-TIP-RE-07`) debe poder exportarse prellenada en el formato institucional "FGL 030 Orden de salida equipos y herramientas".
- **RN-TIP-RE-12:** Al crear la reserva, el usuario debe registrar adicionalmente: razón de la solicitud, nombre y dirección del lugar al cual serán desplazados los equipos o herramientas, y el nombre de la actividad o evento cuando aplique según el contexto.
- **RN-TIP-RE-13:** Los siguientes datos se prellenan a partir de información ya existente en la reserva, sin solicitarse nuevamente: dependencia solicitante (unidad receptora), fecha de retiro y fecha de regreso, actividad asociada (proyecto de investigación, semillero, proyecto académico, servicio de extensión, docencia, calibración, mantenimiento u otro, según el contexto registrado en `RN-CTX`), código del proyecto de investigación cuando corresponda, y nombre, cédula y contacto del responsable de la solicitud, tomados del perfil de la cuenta usuario. Los datos técnicos de cada recurso (placa, descripción, bodega, centro de costo y fecha de compra) se prellenan a partir del inventario de recursos.
- **RN-TIP-RE-14:** Las firmas, cargos de los autorizantes y los registros de entrega o devolución física de los recursos no se prellenan; se diligencian manualmente o se registran en el momento correspondiente del flujo de aprobación y ejecución.
- **RN-TIP-RE-15:** Cuando la reserva se reprograme extendiendo su fecha de devolución, la orden de salida debe reflejar la fecha de prórroga de los recursos.

---

## Lista de espera — RN-TIP-PLE

- **RN-TIP-PLE-01:** La reserva no requiere seleccionar fecha ni horario de ejecución al momento de la solicitud.
- **RN-TIP-PLE-02:** La solicitud debe incluir una descripción de la necesidad y podrá incluir un archivo CAD, una imagen u otro archivo técnico asociado cuando corresponda.
- **RN-TIP-PLE-03:** El formulario complementario solo se habilita después de que el Técnico  determine que la solicitud es viable.
- **RN-TIP-PLE-04:** La evaluación de viabilidad y la aprobación del formulario complementario forman parte del flujo interno de revisión y no constituyen estados globales de la reserva.
- **RN-TIP-PLE-05:** La reserva pasa al estado `APROBADA` cuando se han completado las aprobaciones requeridas y el Técnico  registra la recepción del material necesario para su ejecución.
- **RN-TIP-PLE-06:** Las reservas de tipo lista de espera en estado `APROBADA` no siguen un orden cronológico obligatorio. El Técnico  selecciona la siguiente reserva a ejecutar según la prioridad o los criterios operativos aplicables.
- **RN-TIP-PLE-07:** Cuando el Técnico  inicia la fabricación o prestación correspondiente, la reserva debe pasar al estado `EN_EJECUCION`.
- **RN-TIP-PLE-08:** Al finalizar la ejecución, el Técnico  debe registrar las horas empleadas y la reserva debe pasar al estado `FINALIZADA`.

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
- **RN-DIS-03:** El sistema debe impedir crear, modificar o aprobar una reserva cuando su espacio o un recurso obligatorio se solape con otra reserva bloqueante. La disponibilidad se valida de forma independiente para cada elemento y excluye la propia reserva al modificarla o aprobarla. Para recursos complementarios de una reserva por espacio se aplica la excepción de `RN-TIP-PE-14`.
- **RN-DIS-04:** Un equipo debe encontrarse operativo según la información vigente del sistema de origen correspondiente al momento de crear o aprobar la reserva.
- **RN-DIS-05:** La validación de disponibilidad y el registro de la reserva y sus asignaciones deben realizarse en una misma transacción con protección contra solicitudes concurrentes incompatibles. Esta garantía aplica al crear, modificar horario o fechas, agregar o cambiar elementos y aprobar una reserva, conforme al [data-model](data-model.md). Consultar disponibilidad antes de guardar no constituye por sí solo una garantía suficiente.
- **RN-DIS-06:** Un espacio o recurso solo bloquea disponibilidad cuando está efectivamente asignado a la reserva, tiene un periodo definido y la reserva se encuentra en un estado bloqueante conforme a `RN-EST-02` y `RN-EST-03`. Una solicitud sin periodo definido no bloquea franjas futuras por su estado solamente.
- **RN-DIS-07:** El Usuario siempre puede consultar los horarios configurados y las franjas disponibles del espacio o recurso; las opciones de visibilidad no pueden ocultar esa información.
- **RN-DIS-08:** Cada unidad puede configurar de forma independiente `mostrar_estado_reserva` y `mostrar_reservista`, ambas desactivadas por defecto, para mostrar al Usuario el estado y el nombre del reservista de la reserva que ocupa una franja no disponible.
- **RN-DIS-09:** El Técnico solo puede modificar estas opciones para su propia unidad organizacional. El Administrador puede modificarlas para cualquier unidad, conforme a los permisos de `auth`.
- **RN-DIS-10:** Las opciones de visibilidad solo determinan la información presentada al Usuario; no modifican la disponibilidad ni las reglas de bloqueo, ni permiten consultar el detalle completo de reservas ajenas. El backend aplica estas opciones al responder las consultas de disponibilidad.

---

## Propiedad y acceso — RN-PRO

- **RN-PRO-01:** La cuenta usuario puede consultar sus propias reservas independientemente de su estado.
- **RN-PRO-02:** La cuenta usuario puede editar sus propias reservas únicamente cuando el estado de la reserva y las reglas de negocio permitan la modificación.
- **RN-PRO-03:** Una cuenta sin permisos administrativos no puede consultar el detalle completo, modificar, aprobar, rechazar ni cancelar reservas pertenecientes a terceros. La consulta de disponibilidad puede mostrar únicamente la información de terceros autorizada por `RN-DIS-08` y `RN-DIS-10`.
- **RN-PRO-04:** El Técnico puede consultar y gestionar reservas de terceros únicamente dentro de su propia unidad organizacional. El Administrador puede hacerlo dentro de cualquier unidad organizacional.
- **RN-PRO-05:** La autenticación y la validación de permisos se rigen por las reglas definidas en el módulo `auth`. Las reglas de este dominio determinan qué acciones requieren dichos permisos y sobre qué unidad organizacional deben aplicarse.

---

## Aprobación — RN-APR

- **RN-APR-01:** Solo una cuenta autenticada con permiso para gestionar reservas de la unidad receptora puede aprobar o rechazar una reserva.
- **RN-APR-02:** La aprobación automática de reservas creadas por Usuarios puede habilitarse o deshabilitarse por el Técnico desde la configuración de su propia unidad organizacional.
- **RN-APR-03:** Cuando la aprobación automática esté habilitada para la unidad organizacional, la reserva creada por un usuario se registra directamente en estado `APROBADA`, siempre que cumpla las validaciones aplicables a su tipo. Esta vía no aplica a lista de espera, que siempre inicia en `SOLICITADA` conforme a RN-TIP-PLE-05.
- **RN-APR-04:** Cuando la aprobación automática no esté habilitada, la reserva creada por un usuario se registra en estado `SOLICITADA` y requiere revisión del Técnico .
- **RN-APR-05:** Las reservas creadas por un Técnico dentro de su propia unidad organizacional se registran directamente en estado `APROBADA`, excepto lista de espera. El Técnico no puede autoaprobar una lista de espera al crearla; esta siempre inicia en `SOLICITADA` y solo pasa a `APROBADA` conforme a RN-TIP-PLE-05.
- **RN-APR-06:** La aprobación automática, tanto para usuarios como para Técnico es, no omite las validaciones aplicables al tipo de reserva, incluyendo disponibilidad, horario o fechas, capacidad, estado operativo, habilitación y pertenencia a la unidad cuando correspondan.
- **RN-APR-07:** Aprobar una reserva manualmente debe revalidar las condiciones aplicables a su tipo.
- **RN-APR-08:** Rechazar una reserva conserva toda su información histórica y debe registrar el motivo del rechazo.

---

## Propuesta y contrapropuesta de horario — RN-PROP

- **RN-PROP-01:** En lugar de rechazar una reserva en estado `SOLICITADA`, el Técnico  puede proponer un horario o fecha alternativa, indicando un motivo.
- **RN-PROP-02:** Una propuesta de horario notifica a la cuenta usuario y no cambia el estado de la reserva.
- **RN-PROP-03:** La cuenta usuario puede aceptar la propuesta, rechazarla, o presentar una contrapropuesta con su propio motivo.
- **RN-PROP-04:** Ante una contrapropuesta, únicamente el Técnico  puede aceptarla o rechazarla.
- **RN-PROP-05:** Aceptar cualquier propuesta o contrapropuesta revalida las reglas aplicables al tipo de reserva (disponibilidad, horario o fechas, capacidad) antes de reprogramarla.
- **RN-PROP-06:** Rechazar una propuesta o contrapropuesta conserva la reserva en estado `SOLICITADA` con su horario original, sin generar una nueva solicitud.
- **RN-PROP-07:** Solo puede existir una propuesta o contrapropuesta vigente a la vez por reserva.

---

## Cancelación — RN-CAN

- **RN-CAN-01:** Cancelar una reserva conserva el registro y libera inmediatamente los espacios y recursos asociados para efectos de disponibilidad futura.
- **RN-CAN-02:** Una reserva puede cancelarse mientras no haya iniciado su ejecución. Para reservas con horario, el límite corresponde al inicio de la franja reservada. Para reservas de recursos, el límite corresponde a la entrega física del recurso o al registro de inicio de ejecución, según aplique.
- **RN-CAN-03:** Toda cancelación registra el actor, el momento de la acción y el motivo cuando corresponda.
- **RN-CAN-04:** Cuando se deshabilite un espacio o recurso, todas las reservas futuras que dependan de ese elemento deben pasar automáticamente al estado `CANCELADA`.
- **RN-CAN-05:** La cancelación automática por deshabilitación aplica únicamente a reservas cuya ejecución aún no haya iniciado.
- **RN-CAN-06:** El sistema debe notificar a los usuarios afectados que la reserva fue cancelada por la deshabilitación del espacio o recurso asociado, conforme a las reglas y canales definidos en [business-rules.md](../notifications/business-rules.md).
- **RN-CAN-07:** La cancelación automática debe registrar como motivo la deshabilitación del espacio o recurso y conservar la trazabilidad histórica de la reserva.

---

## Recordatorios — RN-REC

- **RN-REC-01:** El sistema envía un recordatorio automático a la cuenta usuario antes del inicio previsto de una reserva en estado `APROBADA` segun las reglas establecidas en [].
- **RN-REC-02:** El recordatorio se envía una única vez por reserva y no se repite si ya fue enviado.
- **RN-REC-03:** Reprogramar o cancelar la reserva antes del envío del recordatorio anula el envío pendiente para ese horario.

---

## Archivo de calendario — RN-CAL

- **RN-CAL-01:** Cuando una reserva sea aprobada, el sistema debe generar un archivo de calendario en formato iCalendar (`.ics`), excepto lista de espera, que no tiene periodo y no genera `.ics`.
- **RN-CAL-02:** El archivo `.ics` debe incluir como mínimo la fecha, hora de inicio, hora de finalización, ubicación o espacio cuando aplique y una descripción de la reserva.
- **RN-CAL-03:** Cuando corresponda enviar el correo de confirmación de la reserva, el archivo `.ics` debe adjuntarse a ese correo.
- **RN-CAL-04:** Si una reserva es modificada y se envía una nueva confirmación, el sistema debe generar un nuevo archivo `.ics` con la información vigente.
- **RN-CAL-05:** No se requiere sincronización directa con calendarios externos ni persistencia de identificadores de eventos externos.

---

## Contexto de la reserva — RN-CTX

El módulo [Researchs](../researchs/overview.md), propietario del dominio `investigacion`, es dueño del contexto académico/investigativo, de las actividades institucionales y de las vinculaciones del usuario. `reservas` únicamente registra cuáles de esos contextos justificaron la reserva y conserva su información histórica; la disponibilidad de una actividad para nuevas reservas se rige por RN-ACT del módulo Researchs.

- **RN-CTX-01:** Toda reserva que requiera contexto deberá estar asociada al menos a un contexto académico/investigativo o a una actividad institucional.
- **RN-CTX-02:** El contexto académico/investigativo puede estar compuesto por uno o más de los siguientes elementos: semillero, proyecto, pasantía y trabajo de grado.
- **RN-CTX-03:** Semillero, proyecto, pasantía y trabajo de grado pueden coexistir dentro de una misma reserva.
- **RN-CTX-04:** Una actividad institucional constituye un contexto independiente y no puede coexistir en la misma reserva con semillero, proyecto, pasantía ni trabajo de grado.
- **RN-CTX-05:** Solo pueden seleccionarse vinculaciones académicas o investigativas activas y válidas del usuario, conforme al dominio `investigacion`, responsable de dicha información.
- **RN-CTX-06:** El contexto académico, investigativo o institucional de una reserva no otorga por sí mismo permisos administrativos sobre reservas.
- **RN-CTX-07:** El contexto asociado a una reserva debe conservarse históricamente aunque posteriormente cambien los proyectos, semilleros, pasantías, trabajos de grado, actividades institucionales o vinculaciones del usuario.

---

## Acompañante — RN-ACO

- **RN-ACO-01:** Los acompañantes solo aplican cuando la reserva tiene un proyecto o un semillero como contexto.
- **RN-ACO-02:** Cada acompañante debe ser una cuenta existente vinculada activamente al proyecto o al semillero registrado en la reserva.
- **RN-ACO-03:** Una reserva puede registrar de cero a N acompañantes; no es obligatorio registrar uno.
- **RN-ACO-04:** Si la reserva tiene proyecto y semillero, las opciones de acompañante son la unión de las cuentas vinculadas activamente a cualquiera de los dos.
- **RN-ACO-05:** Las reservas de lista de espera no admiten acompañantes.
- **RN-ACO-06:** Ser acompañante no otorga por sí mismo permisos administrativos sobre la reserva; la autorización se determina en `auth`.
- **RN-ACO-07:** La asociación del acompañante se conserva históricamente aunque posteriormente se desactive su vinculación con el proyecto o semillero.

---

## Auditoría — RN-AUD

- **RN-AUD-01:** Crear, modificar, aprobar, rechazar, iniciar ejecución, finalizar y cancelar una reserva genera un registro de auditoría.
- **RN-AUD-02:** El registro de auditoría incluye como mínimo actor, acción, entidad, identificador de la entidad y fecha/hora.
- **RN-AUD-03:** Toda acción auditada debe identificar la cuenta autenticada que la ejecutó y conservar una representación histórica suficiente del actor, independientemente de que la cuenta corresponda a un usuario o a personal.
- **RN-AUD-04:** La trazabilidad histórica no debe depender de que el usuario, personal, cargo, proyecto, semillero, actividad institucional o modalidad permanezcan activos posteriormente.

---

## Reportes — RN-REP

- **RN-REP-01:** Solo el Técnico dentro de su unidad y el Administrador con alcance global pueden generar y exportar reportes de reservas. El Usuario no tiene acceso a esta funcionalidad.
- **RN-REP-02:** El Técnico puede exportar reservas y su historial de auditoría de su unidad; el Administrador puede exportar información de cualquier unidad, en formato CSV o Excel.
- **RN-REP-03:** Un reporte exportado contiene exactamente los datos visibles según el filtro aplicado por quien lo solicita, sin exceder su ámbito de acceso.

---

## Dependencias funcionales

Las reglas de este documento dependen de otros dominios únicamente en los siguientes aspectos:

- **Autenticación y autorización:** [business-rules.md](../auth/business-rules.md) determina autenticación, cuentas activas y validación de permisos.
- **Espacios:** [business-rules.md](../espacios/busines-rules.md) determina existencia, habilitación, capacidad, configuración, campos adicionales y recursos asociados a los espacios.
- **Recursos:** [business-rules.md](../resources/business-rules.md) determina existencia, habilitación, clasificación y estado operativo de los recursos.
- **Notificaciones:** [business-rules.md](../notifications/business-rules.md) determina canales, mecanismos y reglas de entrega de las notificaciones generadas por el dominio de reservas.
- **Modelo persistente:** [data-model](data-model.md) define claves, relaciones, constraints y garantías transaccionales.
- **Investigación y contexto institucional:** perfiles, semilleros, proyectos, actividades institucionales y modalidades de vinculación son datos de contexto y no sustituyen las reglas de autorización. También determina qué cuentas pertenecen a cada proyecto o semillero, base para ofrecerlas como opciones válidas de acompañante (`RN-ACO`).

---

## Principios del dominio

1. Una reserva siempre tiene una cuenta usuario y una unidad receptora.
2. Toda reserva debe contener los datos y elementos obligatorios definidos para su tipo de reserva.
3. La disponibilidad se protege tanto por reglas de negocio como por garantía transaccional.
4. El acceso a reservas de terceros depende de autorización, no del tipo de usuario por sí solo.
5. Las relaciones académicas, investigativas e institucionales contextualizan la reserva, pero no conceden permisos administrativos.
6. Los tipos de reserva comparten estados globales, pero pueden tener acciones y etapas internas propias que no constituyen nuevos estados.
7. Las acciones relevantes conservan trazabilidad histórica.
