# Reservas

Contrato funcional del dominio de reservas.

El modelo persistente se define en [data-model](data-model.md), los espacios en [business-rules.md](../espacios/business-rules.md), los recursos en [business-rules.md](../resources/business-rules.md), la autenticación y autorización en [business-rules.md](../auth/business-rules.md), y las relaciones académicas e investigativas en el módulo `researchs`.

---

## Creación y composición — RN-RES

- **RN-RES-01:** El Usuario debe cumplir las validaciones aplicables a la creación de la reserva.
- **RN-RES-02:** Toda reserva debe ser creada por una cuenta autenticada y activa.
- **RN-RES-03:** Toda reserva debe estar asociada a una unidad organizacional receptora mediante `id_unidad`.
- **RN-RES-04:** Los datos y elementos requeridos para crear una reserva dependen del tipo de reserva seleccionado.
- **RN-RES-05:** Todo espacio, recurso, proyecto, semillero u otro elemento asociado a la reserva debe existir y encontrarse habilitado cuando aplique.
- **RN-RES-06:** Los elementos asociados a una reserva deben pertenecer o estar disponibles para la unidad organizacional receptora, según corresponda.
- **RN-RES-07:** Una misma cuenta puede mantener varias reservas simultáneas siempre que cumpla las restricciones de cada tipo. Un recurso sujeto a entrega y devolución física no admite más de un compromiso vigente, aunque los periodos no se solapen (`RN-DIS-06`).
- **RN-RES-08:** Crear o modificar una reserva debe revalidar las reglas aplicables a su tipo de reserva.
- **RN-RES-09:** Cuando un equipo incluido en la reserva tenga `requiere_apoyo = true`, la reserva debe persistir `requiere_apoyo = true` automáticamente y el Usuario no puede desmarcar la opción “requiere técnico”.
- **RN-RES-10:** Cuando ningún equipo incluido exija apoyo, el Usuario puede solicitar voluntariamente apoyo técnico; el valor efectivo se persiste en `reservas.reservas.requiere_apoyo`.
- **RN-RES-11:** Para crear una reserva con una cuenta de tipo `USUARIO`, su titular debe haber completado la actualización inicial del perfil conforme a RN-USR-07 y RN-USR-08, y conservar al menos una vinculación activa y válida conforme a RN-USR-11. El backend revalida ambas condiciones al registrar cada nueva reserva. Las vinculaciones seleccionadas como contexto se validan además conforme a RN-CTX-05. Esta condición de perfil y vinculación mínima no aplica a cuentas de tipo `PERSONAL`.
- **RN-RES-12:** Una reserva por espacio admite cero o más recursos complementarios y no exige un recurso principal. Las reservas de recurso interno, campus y externo requieren un recurso principal y admiten adicionales conforme a sus reglas específicas. `LISTA_ESPERA` no selecciona ni registra recursos, por lo que no tiene recursos `PRINCIPAL` ni `ADICIONAL`.
- **RN-RES-13:** `reservas.reservas` solo contiene datos comunes. El espacio, el periodo, los asistentes y la ubicación se registran exclusivamente en el detalle correspondiente al tipo de reserva; no se duplican en la cabecera.
- **RN-RES-14:** Los recursos sujetos a entrega y devolución física no admiten más de un compromiso vigente. Desde su incorporación efectiva a una reserva, no pueden incorporarse a otra solicitud mientras el compromiso anterior siga vigente, aunque los periodos solicitados no se solapen. No se permite prorrogar la fecha estimada de devolución. Cuando exista entrega física, la liberación exige registrar la devolución y completar el cierre de la reserva. Una nueva solicitud requiere además verificar que el recurso permanece habilitado y operativo. La fecha estimada de devolución no garantiza disponibilidad futura: el recurso puede regresar tarde, dañado, requerir mantenimiento, perderse o continuar indisponible por otra condición. La vigencia y liberación se definen en `RN-DIS-06`. La exclusividad física corresponde a asignaciones de `RECURSO_CAMPUS` y `RECURSO_EXTERNO`; los complementarios de `ESPACIO` se rigen por `RN-TIP-PE-28`.
- **RN-RES-15:** Una cuenta de tipo `PERSONAL` solo puede crear reservas para la unidad organizacional (laboratorio) asociada a su registro de personal mediante su cargo vigente. Si necesita reservar en otra unidad, debe hacerlo mediante una cuenta de tipo `USUARIO`; una cuenta `PERSONAL` no puede seleccionar otra unidad como receptora.

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
- **RN-TIP-PE-02:** La fecha y el horario solicitados deben encontrarse dentro del horario de atención de la unidad a la que pertenece el espacio, conforme a `RN-ESP-DIS-02`. El espacio no define un horario propio.
- **RN-TIP-PE-03:** No se podrá crear una reserva que se solape con otra reserva bloqueante para el mismo espacio.
- **RN-TIP-PE-04:** La reserva debe estar asociada a un espacio habilitado para reservas.
- **RN-TIP-PE-05:** La reserva puede tener cero o más `asistentes`. El valor representa la cantidad de cuentas seleccionadas como acompañantes y no puede superar la capacidad habilitada del espacio. Si se registran acompañantes, el valor debe coincidir con el número de filas de `reserva_acompanantes`.
- **RN-TIP-PE-06:** Toda reserva por espacio debe registrar un contexto de uso conforme a `RN-CTX`: uno o más elementos académicos/investigativos, o una actividad institucional independiente.
- **RN-TIP-PE-07:** La selección de contexto se valida según el tipo de cuenta conforme a `RN-CTX-05` y `RN-CTX-08`; una cuenta `PERSONAL` puede seleccionar proyectos y semilleros activos del catálogo general sin tener una vinculación propia.
- **RN-TIP-PE-08:** Para una cuenta `USUARIO`, cuando al seleccionar un tipo de contexto académico/investigativo exista una única vinculación válida, el sistema la selecciona automáticamente. Esta regla no aplica a cuentas `PERSONAL`, que eligen directamente entre los proyectos y semilleros activos del catálogo general.
- **RN-TIP-PE-09:** Para una cuenta `USUARIO`, cuando existan varias vinculaciones válidas para el tipo de contexto seleccionado, debe elegir la que justifica la reserva. No se exige una vinculación propia a las cuentas `PERSONAL` para elegir proyectos o semilleros del catálogo general.
- **RN-TIP-PE-10:** Una reserva puede asociarse simultáneamente a un proyecto, un semillero, una pasantía y un trabajo de grado, conforme a `RN-CTX-03`.
- **RN-TIP-PE-11:** Para una cuenta `USUARIO`, cuando la reserva no se asocie a ningún elemento académico/investigativo, debe registrarse una actividad institucional habilitada. Esta no puede coexistir con los demás elementos de contexto, conforme a `RN-CTX-04`. Una cuenta `PERSONAL` debe seleccionar al menos un proyecto o semillero conforme a `RN-CTX-08`.
- **RN-TIP-PE-12:** Al seleccionar un espacio, el sistema debe cargar los recursos asociados y los campos adicionales configurados para ese espacio.
- **RN-TIP-PE-13:** El sistema debe indicar cuáles recursos asociados al espacio se encuentran disponibles y cuáles no están disponibles para la fecha y horario solicitados.
- **RN-TIP-PE-14:** La falta de disponibilidad de uno o más recursos complementarios asociados al espacio no impide crear la reserva del espacio; esos recursos no pueden quedar asignados durante el periodo incompatible. Un recurso con compromiso físico vigente no puede incluirse en la nueva solicitud, ni siquiera como fila `NO_DISPONIBLE`; el Usuario puede continuar sin él. La conservación como `NO_DISPONIBLE` se limita a incompatibilidades temporales de complementarios sin compromiso físico. Un préstamo posterior puede provocar el retiro de un complementario ya asignado según `RN-TIP-PE-28`, sin cancelar el espacio.
- **RN-TIP-PE-15:** La reserva por espacio debe permitir registrar una observación para comunicar al Técnico  necesidades, restricciones o información adicional relacionada con los recursos requeridos.
- **RN-TIP-PE-16:** Al revisar la solicitud, el Técnico  debe visualizar la disponibilidad de los recursos asociados al espacio y la observación registrada por el usuario.
- **RN-TIP-PE-17:** Antes de aprobar la reserva, el Técnico  puede modificar los recursos asociados a la solicitud para ajustarla según la disponibilidad existente, sin alterar el espacio solicitado salvo que el flujo de gestión lo permita expresamente.
- **RN-TIP-PE-18:** Cuando el espacio tenga campos adicionales configurados como obligatorios, el usuario debe diligenciarlos antes de enviar la solicitud.
- **RN-TIP-PE-19:** Si el espacio no tiene campos adicionales configurados, la reserva continúa sin solicitar información adicional.
- **RN-TIP-PE-20:** Los valores diligenciados en los campos adicionales deben conservarse asociados a la reserva como parte de su información histórica.
- **RN-TIP-PE-21:** El Técnico puede agregar o retirar recursos complementarios de `ESPACIO` en `SOLICITADA`, `APROBADA` o `EN_EJECUCION`, revalidando disponibilidad de la composición resultante. El retiro manual solo actualiza la composición vigente, sin historial específico ni metadatos de retiro. Las operaciones genéricas de agregar/retirar recursos no aplican a `RECURSO_CAMPUS`, `RECURSO_EXTERNO` ni `LISTA_ESPERA`. El retiro automático por préstamo conserva el historial exigido por `RN-TIP-PE-28`; las demás obligaciones expresas de historial mantienen su ámbito.
- **RN-TIP-PE-22:** Todo recurso agregado debe encontrarse habilitado, operativo y disponible durante el periodo de uso requerido por la reserva. No puede tener un compromiso físico vigente en otra reserva (`RN-DIS-06`).
- **RN-TIP-PE-23:** Cuando se agregue un recurso a una reserva en estado `EN_EJECUCION`, el sistema debe registrar automáticamente el instante de incorporación y validar su disponibilidad desde ese instante hasta la finalización prevista de la reserva.
- **RN-TIP-PE-24:** Los recursos complementarios asignados a una reserva por espacio se utilizan exclusivamente durante la franja horaria de `reservas.reserva_espacio`. No requieren entrega ni devolución física y no generan registros en `reservas.reserva_ejecucion_recursos`. Su periodo de asignación termina con la franja de la reserva, sin ninguna acción física de cierre. Un préstamo posterior puede provocar el retiro de un complementario ya asignado según `RN-TIP-PE-28`, sin cancelar el espacio.
- **RN-TIP-PE-25:** Al alcanzar `hora_fin`, una reserva `ESPACIO` todavía `SOLICITADA` pasa automáticamente a `CANCELADA`; si está `APROBADA` o `EN_EJECUCION`, pasa a `FINALIZADA`. `RECHAZADA`, `CANCELADA` y `FINALIZADA` no se modifican automáticamente. El sistema registra la transición y, en la cancelación, el motivo de vencimiento sin aprobación. No requiere ni admite cierre manual ni devolución física (`UF-RES-21`).
- **RN-TIP-PE-26:** Las transiciones automáticas de `RN-TIP-PE-25` y `RN-TIP-PE-27` no son el mecanismo que libera ni que ocupa la disponibilidad del espacio ni de sus recursos complementarios. La disponibilidad se determina siempre por el periodo reservado y el solapamiento temporal, conforme a `RN-DIS-01`, `RN-DIS-06` y `RN-DIS-11`. Un retraso o una falla del proceso automático no puede impedir que se reserve un intervalo posterior que no se solapa.
- **RN-TIP-PE-27:** Una reserva `ESPACIO` en `APROBADA` pasa automáticamente a `EN_EJECUCION` al alcanzar `hora_inicio` (`UF-RES-22`). Una reserva puede permanecer `SOLICITADA` durante su franja. Si se aprueba cuando `hora_inicio <= ahora < hora_fin`, la aprobación y el paso inmediato a `EN_EJECUCION` se registran en la misma operación, con sus transiciones e instantes; no espera otra ejecución del proceso automático. Al alcanzar `hora_fin` se aplica `RN-TIP-PE-25`, no una aprobación tardía. No se registra entrega física ni asistencia; el Técnico no inicia manualmente la reserva.


- **RN-TIP-PE-28:** Los complementarios de `ESPACIO` no constituyen un compromiso físico exclusivo frente a préstamos posteriores. Al crear una reserva de `RECURSO_CAMPUS` o `RECURSO_EXTERNO`, o incorporar un recurso a un préstamo mediante una operación permitida, el sistema resuelve las asignaciones efectivas de ese recurso en reservas de espacio: si están en `SOLICITADA` o `APROBADA`, las retira automáticamente en la misma transacción que establece el compromiso físico, aunque las fechas sean distintas; si alguna está en `EN_EJECUCION`, rechaza la operación completa con `409 CONFLICTO`, sin retiros ni escrituras parciales. Las asignaciones de reservas terminadas no se modifican. Cada retiro conserva la fila y su historial, el instante, la causa `PRESTAMO_FISICO` y la referencia a la reserva de préstamo causante. No cancela ni cambia el estado, espacio, franja o demás asignaciones de la reserva de espacio; tampoco genera entrega o devolución física para ella. Si falla cualquier parte, se revierte el conjunto. Cancelar el préstamo no restaura automáticamente los complementarios retirados; una eventual reincorporación sigue el flujo permitido y revalida disponibilidad. Esta causa es independiente de la deshabilitación regulada por `RN-CAN-05` y `RN-CAN-06`.

---

## Recurso para uso dentro del laboratorio — RN-TIP-RI

- **RN-TIP-RI-01:** La reserva corresponde a uno o varios recursos (un `PRINCIPAL` y, opcionalmente, `ADICIONAL`es) que serán utilizados dentro de las instalaciones del laboratorio, conforme a la cardinalidad por tipo de `RN-RES-12`.
- **RN-TIP-RI-02:** La reserva requiere seleccionar una fecha y un horario de inicio y finalización de uso, comprendidos dentro de un mismo día. Aplican a todos los recursos de la reserva.
- **RN-TIP-RI-03:** Cada recurso debe estar habilitado, operativo y disponible durante la franja solicitada. `RECURSO_INTERNO` no crea un compromiso físico exclusivo: admite reservas sucesivas con franjas no solapadas. Un compromiso físico vigente de campus o externo no se elude reservando el recurso como interno (`RN-DIS-06`).
- **RN-TIP-RI-04:** No se puede crear o modificar una reserva que se solape con otra asignación temporal bloqueante de alguno de sus recursos. Los periodos no solapados se admiten; crear una reserva interna no retira complementarios de espacio mediante `RN-TIP-PE-28`, porque no es un préstamo físico.
- **RN-TIP-RI-05:** La reserva de un recurso para uso dentro del laboratorio no requiere asociarlo a una reserva de espacio.
- **RN-TIP-RI-06:** Cada recurso reservado puede corresponder a un equipo con placa de identificación o a un recurso sin placa, según su clasificación en el inventario.
- **RN-TIP-RI-07:** El uso dentro del laboratorio requiere aprobación de la reserva. No se registra entrega ni devolución física para `RECURSO_INTERNO`; esas operaciones no condicionan sus estados.
- **RN-TIP-RI-08:** Una reserva `RECURSO_INTERNO` en `APROBADA` pasa automáticamente a `EN_EJECUCION` al alcanzar `hora_inicio`, sin intervención del Técnico ni registro de entrega física (`UF-RES-22`).
- **RN-TIP-RI-09:** Una reserva `RECURSO_INTERNO` en `EN_EJECUCION` pasa automáticamente a `FINALIZADA` al alcanzar `hora_fin`, sin devolución física ni cierre manual (`UF-RES-21`).
- **RN-TIP-RI-10:** El Técnico puede agregar o retirar solo recursos `ADICIONAL`es de `RECURSO_INTERNO` en `SOLICITADA`, `APROBADA` o `EN_EJECUCION`, revalidando disponibilidad de la composición resultante. El `PRINCIPAL` no puede retirarse mediante estas operaciones. El retiro manual solo actualiza la composición vigente, sin historial específico ni metadatos de retiro.
- **RN-TIP-RI-11:** Todo recurso incorporado debe estar habilitado, operativo y disponible durante la franja aplicable. Se validan solapamientos y compromisos físicos ajenos de campus o externo, pero la incorporación a interno solo crea una asignación temporal (`RN-DIS-06`).
- **RN-TIP-RI-12:** Cuando se agregue un recurso a una reserva en estado `EN_EJECUCION`, el sistema debe registrar automáticamente el instante de incorporación y validar su disponibilidad desde ese instante hasta la finalización prevista de la reserva.
- **RN-TIP-RI-13:** La disponibilidad de `RECURSO_INTERNO` se controla por franja horaria, conforme a `RN-DIS-01` y `RN-DIS-11`. Sus asignaciones no abren rangos físicos ni generan filas en `reserva_ejecucion_recursos`. Vencer la franja permite evaluar intervalos posteriores no solapados, sin depender de devolución ni de retrasos del proceso automático. Desde `EN_EJECUCION` no puede cancelarse.

---

## Recurso para uso dentro del campus — RN-TIP-RC

- **RN-TIP-RC-01:** La reserva corresponde a uno o varios recursos (un `PRINCIPAL` y, opcionalmente, `ADICIONAL`es) que saldrán del laboratorio, pero permanecerán dentro del campus autorizado. Todos los recursos de la reserva comparten la misma fecha de salida y de devolución estimada.
- **RN-TIP-RC-02:** La reserva requiere seleccionar una fecha de salida y una fecha estimada de devolución, aplicable a todos sus recursos. La fecha estimada sirve para planificar el periodo solicitado; no acredita que el recurso haya regresado al laboratorio.
- **RN-TIP-RC-03:** Al crear o modificar la solicitud, cada recurso debe encontrarse habilitado y operativo, tener un periodo compatible con las asignaciones temporales existentes y estar libre de otro compromiso vigente (`RN-DIS-06`). La aprobación y la entrega revalidan esas condiciones excluyendo el compromiso de la propia reserva. Una solicitud no puede crearse para esperar la liberación de un recurso comprometido. Las asignaciones complementarias previas de espacio se resuelven conforme a `RN-TIP-PE-28`; no se equiparan a otro compromiso físico.
- **RN-TIP-RC-04:** No se podrá crear una reserva que se solape con otra reserva bloqueante para alguno de sus recursos. Tampoco se permiten compromisos pendientes sobre el mismo recurso con periodos distintos (`RN-DIS-06`). Las asignaciones complementarias previas de espacio se resuelven conforme a `RN-TIP-PE-28`; no se equiparan a otro compromiso físico.
- **RN-TIP-RC-05:** Cada recurso reservado puede corresponder a un equipo con placa de identificación o a un recurso sin placa, según su clasificación en el inventario.
- **RN-TIP-RC-06:** La entrega de los recursos al usuario requiere la aprobación previa del Técnico .
- **RN-TIP-RC-07:** El sistema debe generar la orden de salida correspondiente al uso de los recursos dentro del campus y fuera del laboratorio, listando todos los recursos de la reserva. La aprobación, la generación de la FGL 030 y el inicio de ejecución forman parte del mismo proceso de salida. La FGL 030 se genera al pasar a `APROBADA`, incluida la autoaprobación; el proceso continúa con la entrega física y el paso a `EN_EJECUCION`, sin una etapa posterior de retiro automático por deshabilitación. Desde la salida, la composición queda fija hasta la devolución. Desde ese momento sus datos quedan inmutables: no se modifica, regenera ni versiona. No se permiten modificaciones posteriores de fechas, recursos ni otros datos que formen parte de la orden, tampoco mediante propuestas o contrapropuestas.
- **RN-TIP-RC-08:** La orden de salida debe registrar la aprobación del Técnico  y la recepción de los recursos por parte del usuario.
- **RN-TIP-RC-09:** Al entregar físicamente los recursos al usuario, la reserva debe pasar al estado `EN_EJECUCION`.
- **RN-TIP-RC-10:** Al recibir nuevamente los recursos, el Técnico debe registrar en la misma operación la devolución de todos los recursos entregados. No se permite una devolución parcial durante la ejecución; solo entonces la reserva pasa a `FINALIZADA`. La devolución y el cierre no declaran operativo ni habilitado el recurso; una nueva solicitud revalida `RN-DIS-04` y `RN-DIS-06`.
- **RN-TIP-RC-11:** La orden de salida (`RN-TIP-RC-07`) debe poder exportarse prellenada en el formato institucional "FGL 030 Orden de salida equipos y herramientas".
- **RN-TIP-RC-12:** Al crear la reserva, el usuario debe registrar en `reserva_datos_salida` la razón de la solicitud, el nombre y dirección del lugar al cual serán desplazados los equipos o herramientas, y el nombre de la actividad o evento cuando aplique según el contexto. Estos datos se conservan asociados a la reserva antes de generar la orden.
- **RN-TIP-RC-13:** Los siguientes datos se prellenan a partir de información ya existente en la reserva, sin solicitarse nuevamente: dependencia solicitante, entendida como la afiliación de quien solicita y no como la unidad receptora de la reserva, fecha de retiro y fecha de regreso, actividad o actividades asociadas, que pueden marcarse varias a la vez sobre las ocho casillas del formato según el contexto registrado en `RN-CTX`; pasantía y trabajo de grado se marcan como «otro» y se detallan en el nombre de la actividad, código del proyecto de investigación cuando corresponda, y nombre, cédula, correo y teléfono del responsable de la solicitud, tomados del perfil de la identidad asociada a la cuenta: `usuarios.usuarios` para cuentas de Usuario y `personal.personal` para cuentas de Personal. Los datos técnicos se copian como snapshot desde Resources: para equipos, `descripcion_snapshot` toma `recursos.equipos.nombre_equipo`, `placa_snapshot` toma `recursos.equipos.placa` y bodega, centro de costo y fecha de compra toman `recursos.equipos.bodega`, `centro_costo` y `fecha_compra`; para mobiliarios y otros recursos, la descripción toma su campo `nombre` y los datos exclusivos de equipos quedan nulos.
- **RN-TIP-RC-14:** Las firmas, cargos de los autorizantes y los registros de entrega o devolución física de los recursos no se prellenan; se diligencian manualmente o se registran en el momento correspondiente del flujo de aprobación y ejecución.

---

## Recurso fuera del campus — RN-TIP-RE

- **RN-TIP-RE-01:** La reserva corresponde a uno o varios recursos (un `PRINCIPAL` y, opcionalmente, `ADICIONAL`es) autorizados para salir del campus. Todos los recursos de la reserva comparten la misma fecha de salida y de devolución estimada.
- **RN-TIP-RE-02:** La reserva requiere seleccionar una fecha de salida y una fecha estimada de devolución, aplicable a todos sus recursos. La fecha estimada sirve para planificar el periodo solicitado; no acredita que el recurso haya regresado al laboratorio.
- **RN-TIP-RE-03:** Al crear o modificar la solicitud, cada recurso debe encontrarse habilitado y operativo, tener un periodo compatible con las asignaciones temporales existentes y estar libre de otro compromiso vigente (`RN-DIS-06`). La aprobación y la entrega revalidan esas condiciones excluyendo el compromiso de la propia reserva. Una solicitud no puede crearse para esperar la liberación de un recurso comprometido. Las asignaciones complementarias previas de espacio se resuelven conforme a `RN-TIP-PE-28`; no se equiparan a otro compromiso físico.
- **RN-TIP-RE-04:** No se podrá crear una reserva que se solape con otra reserva bloqueante para alguno de sus recursos. Tampoco se permiten compromisos pendientes sobre el mismo recurso con periodos distintos (`RN-DIS-06`). Las asignaciones complementarias previas de espacio se resuelven conforme a `RN-TIP-PE-28`; no se equiparan a otro compromiso físico.
- **RN-TIP-RE-05:** Cada recurso reservado puede corresponder a un equipo con placa de identificación o a un recurso sin placa, según su clasificación en el inventario.
- **RN-TIP-RE-06:** La salida de los recursos requiere la aprobación previa del Técnico .
- **RN-TIP-RE-07:** El sistema debe generar la orden de salida externa correspondiente al retiro de los recursos fuera del campus, listando todos los recursos de la reserva. La aprobación, la generación de la FGL 030 y el inicio de ejecución forman parte del mismo proceso de salida. La FGL 030 se genera al pasar a `APROBADA`, incluida la autoaprobación; el proceso continúa con la entrega física y el paso a `EN_EJECUCION`, sin una etapa posterior de retiro automático por deshabilitación. Desde la salida, la composición queda fija hasta la devolución. Desde ese momento sus datos quedan inmutables: no se modifica, regenera ni versiona. No se permiten modificaciones posteriores de fechas, recursos ni otros datos que formen parte de la orden, tampoco mediante propuestas o contrapropuestas.
- **RN-TIP-RE-08:** La orden de salida externa debe registrar la aprobación del Técnico  y la recepción de los recursos por parte del usuario.
- **RN-TIP-RE-09:** Al entregar físicamente los recursos al usuario, la reserva debe pasar al estado `EN_EJECUCION`.
- **RN-TIP-RE-10:** Al recibir nuevamente los recursos, el Técnico debe registrar en la misma operación la devolución de todos los recursos entregados. No se permite una devolución parcial durante la ejecución; solo entonces la reserva pasa a `FINALIZADA`. La devolución y el cierre no declaran operativo ni habilitado el recurso; una nueva solicitud revalida `RN-DIS-04` y `RN-DIS-06`.
- **RN-TIP-RE-11:** La orden de salida externa (`RN-TIP-RE-07`) debe poder exportarse prellenada en el formato institucional "FGL 030 Orden de salida equipos y herramientas".
- **RN-TIP-RE-12:** Al crear la reserva, el usuario debe registrar en `reserva_datos_salida` la razón de la solicitud, el nombre y dirección del lugar al cual serán desplazados los equipos o herramientas, y el nombre de la actividad o evento cuando aplique según el contexto. Estos datos se conservan asociados a la reserva antes de generar la orden.
- **RN-TIP-RE-13:** Los siguientes datos se prellenan a partir de información ya existente en la reserva, sin solicitarse nuevamente: dependencia solicitante, entendida como la afiliación de quien solicita y no como la unidad receptora de la reserva, fecha de retiro y fecha de regreso, actividad o actividades asociadas, que pueden marcarse varias a la vez sobre las ocho casillas del formato según el contexto registrado en `RN-CTX`; pasantía y trabajo de grado se marcan como «otro» y se detallan en el nombre de la actividad, código del proyecto de investigación cuando corresponda, y nombre, cédula, correo y teléfono del responsable de la solicitud, tomados del perfil de la identidad asociada a la cuenta: `usuarios.usuarios` para cuentas de Usuario y `personal.personal` para cuentas de Personal. Los datos técnicos se copian como snapshot desde Resources: para equipos, `descripcion_snapshot` toma `recursos.equipos.nombre_equipo`, `placa_snapshot` toma `recursos.equipos.placa` y bodega, centro de costo y fecha de compra toman `recursos.equipos.bodega`, `centro_costo` y `fecha_compra`; para mobiliarios y otros recursos, la descripción toma su campo `nombre` y los datos exclusivos de equipos quedan nulos.
- **RN-TIP-RE-14:** Las firmas, cargos de los autorizantes y los registros de entrega o devolución física de los recursos no se prellenan; se diligencian manualmente o se registran en el momento correspondiente del flujo de aprobación y ejecución.

## Casillas del FGL 030 — RN-SAL

- **RN-SAL-01:** `orden_salida_actividades` representa únicamente las casillas del formato FGL 030; no es un catálogo alternativo de contextos ni una entidad administrada por Researchs.
- **RN-SAL-02:** Al generar una orden, el sistema copia el contexto registrado en `reserva_contexto` a las casillas del formato, sin crear ni modificar contextos.
- **RN-SAL-03:** `proyecto_id` se representa como `PROYECTO_INVESTIGACION` y `semillero_id` como `SEMILLERO_INVESTIGACION`. Pasantía, trabajo de grado y `actividad_institucional_id` se representan como `OTRO`, con su detalle en `nombre_actividad_evento` cuando corresponda.
- **RN-SAL-04:** Las casillas `CALIBRACION`, `DOCENCIA`, `MANTENIMIENTO` y `SERVICIO_EXTENSION` solo se marcan cuando correspondan al formato y no se derivan de una entidad adicional de Researchs.

---

## Lista de espera — RN-TIP-PLE

- **RN-TIP-PLE-01:** La reserva no requiere seleccionar fecha ni horario de ejecución al momento de la solicitud.
- **RN-TIP-PLE-02:** La solicitud debe incluir una descripción de la necesidad. El reservista puede adjuntar uno o varios archivos técnicos a su reserva mientras esté `SOLICITADA`, antes o después de la evaluación de viabilidad. Cada archivo debe cumplir los formatos, validación de contenido y límite de 5 MB definidos en `reserva_adjuntos` del [modelo](data-model.md#reservasreserva_adjuntos). La lista de espera no permite asociar espacio ni recursos. Cargar un archivo no cambia el estado; si falla la carga, no se registra ese adjunto ni se elimina la reserva.
- **RN-TIP-PLE-03:** El Técnico de la unidad registra la viabilidad mediante una acción explícita sobre la reserva `SOLICITADA`. Registra `viable` y `fecha_evaluacion_viabilidad`; si es viable, la reserva permanece `SOLICITADA` y se habilita el formulario complementario. Si no es viable, registra el motivo y la reserva pasa a `RECHAZADA` en la misma transacción, conservando sus datos y adjuntos. No se introduce un estado global de viabilidad. El formulario se persiste en `reserva_lista_espera_formulario`.
- **RN-TIP-PLE-04:** Con la reserva `SOLICITADA` y declarada viable, el reservista diligencia su parte del formulario y el Técnico de la unidad la revisa y completa la parte técnica. Cada actor solo modifica su parte; la parte técnica requiere que exista la del reservista. Los datos de cada parte son un objeto no vacío; el Técnico acredita su revisión completando la parte técnica y su registro de revisión. Si el reservista modifica su parte después de esa revisión, se invalida la parte técnica y su revisión y deben completarse nuevamente antes de aprobar. El formulario no tiene aprobación independiente ni introduce estados globales.
- **RN-TIP-PLE-05:** Una única operación del Técnico registra la recepción del material y cambia la reserva de `SOLICITADA` a `APROBADA`. Exige viabilidad positiva, parte del reservista registrada, parte técnica completada y revisión vigente, además de confirmación expresa de recepción del material. El sistema registra `fecha_recepcion_material`, `fecha_aprobacion` y la transición de estado en la misma transacción. Si falta una condición o falla una escritura, no se registra la recepción ni se aprueba. No existe una operación separada de recepción ni autoaprobación para este tipo.
- **RN-TIP-PLE-06:** Las reservas de tipo lista de espera en estado `APROBADA` no siguen un orden cronológico obligatorio. El Técnico  selecciona la siguiente reserva a ejecutar según la prioridad o los criterios operativos aplicables.
- **RN-TIP-PLE-07:** El Técnico de la unidad inicia la fabricación o prestación de una reserva `APROBADA` mediante la acción de ejecución, que cambia a `EN_EJECUCION` y registra la transición. No corresponde a una entrega de recursos ni crea filas en `reserva_ejecucion_recursos`; no requiere ni admite recursos en el cuerpo de esa operación.
- **RN-TIP-PLE-08:** El Técnico de la unidad finaliza una reserva `EN_EJECUCION` registrando obligatoriamente las horas empleadas (`horas_ejecucion`, número finito mayor o igual a cero conforme al modelo) y cambiándola a `FINALIZADA` en la misma transacción. No requiere ni admite recursos o devoluciones. Si faltan las horas o son inválidas, no se registra el cierre ni se cambia el estado.
- **RN-TIP-PLE-09:** Si se modifica efectivamente `descripcion_necesidad` de una lista de espera `SOLICITADA` después de evaluar viabilidad, la evaluación anterior deja de ser válida. En la misma transacción se limpian `viable` y `fecha_evaluacion_viabilidad`; la reserva sigue `SOLICITADA` y exige nueva acción de evaluación antes de habilitar el formulario o aprobar. Se conservan los adjuntos y la parte del reservista del formulario si existe, pero se invalidan la parte técnica y su revisión. Después de nueva viabilidad positiva, el Técnico debe revisar y completar otra vez su parte. Enviar la misma descripción sin cambios no invalida la evaluación. Una reserva `RECHAZADA` no se reabre mediante edición.

---

## Horario para reservas con franja horaria — RN-HOR

- **RN-HOR-01:** Estas reglas aplican únicamente a los tipos de reserva que utilizan `hora_inicio` y `hora_fin`.
- **RN-HOR-02:** `hora_inicio` debe ser menor que `hora_fin`.
- **RN-HOR-03:** Una reserva con franja horaria no puede cruzar medianoche.
- **RN-HOR-04:** La reserva debe encontrarse dentro del horario de atención habilitado para la unidad o laboratorio correspondiente. Los espacios y recursos de esa unidad heredan ese horario y no definen uno propio (`RN-ESP-DIS-02`).
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
- **RN-EST-02:** `SOLICITADA`, `APROBADA` y `EN_EJECUCION` son estados bloqueantes. En espacios, recursos internos y complementarios sin entrega física bloquean el periodo efectivamente asignado. En `RECURSO_CAMPUS` y `RECURSO_EXTERNO`, cada asignación efectiva mantiene además un compromiso exclusivo sobre el recurso desde su incorporación, incluso en `SOLICITADA`, independientemente de sus fechas (`RN-DIS-06`). La exclusividad física corresponde a asignaciones de `RECURSO_CAMPUS` y `RECURSO_EXTERNO`; los complementarios de `ESPACIO` se rigen por `RN-TIP-PE-28`.
- **RN-EST-03:** `RECHAZADA`, `FINALIZADA` y `CANCELADA` no bloquean disponibilidad futura tras una transición válida. No se permite terminar el compromiso de un recurso dejando una entrega física abierta; la devolución y el cierre deben cumplir `RN-DIS-06`. Terminar el compromiso no acredita habilitación ni operatividad.
- **RN-EST-04:** Una reserva `RECHAZADA`, `FINALIZADA` o `CANCELADA` conserva su información histórica y no se elimina físicamente por causa del cambio de estado.
- **RN-EST-05:** Las acciones intermedias propias de un tipo de reserva, como evaluación de viabilidad, diligenciamiento de formularios o recepción de material, no constituyen estados globales salvo que se incorporen expresamente al catálogo de estados.

---

## Disponibilidad — RN-DIS

- **RN-DIS-01:** Para reservas con franja horaria, los intervalos se interpretan como `[hora_inicio, hora_fin)`. Dos reservas contiguas no se consideran solapadas cuando una termina exactamente a la hora en que inicia la otra.
- **RN-DIS-02:** Para reservas de recursos por días, el periodo solicitado comprende la fecha de salida o inicio y la fecha estimada de devolución o finalización. Dos reservas se consideran solapadas cuando comparten al menos una fecha del periodo solicitado.
- **RN-DIS-03:** El sistema debe impedir crear o modificar una reserva cuando su espacio o un recurso obligatorio se solape con otra asignación temporal bloqueante, o cuando exista un compromiso físico incompatible conforme a `RN-DIS-06`, aunque los periodos sean distintos. Aprobar o entregar revalida las condiciones vigentes. La validación es independiente por elemento y excluye la asignación y el compromiso de la propia reserva al modificarla, reprogramarla o aprobarla. La excepción de `RN-TIP-PE-14` no autoriza incluir recursos comprometidos en un préstamo. Las asignaciones complementarias previas de espacio se resuelven conforme a `RN-TIP-PE-28`; no se equiparan a otro compromiso físico.
- **RN-DIS-04:** Un equipo debe encontrarse operativo según la información vigente del módulo propietario al crear, incorporar, aprobar o entregar el recurso. Al solicitarlo nuevamente después de una devolución se revalidan habilitación y operatividad: registrar la devolución no las restablece automáticamente. Un recurso devuelto dañado, en mantenimiento o deshabilitado puede cerrar su préstamo, pero no es elegible para una nueva solicitud mientras no cumpla las condiciones aplicables.
- **RN-DIS-05:** Validar disponibilidad y registrar la reserva y sus asignaciones debe realizarse en una misma transacción con protección en base de datos frente a concurrencia. La garantía cubre creación, modificación de periodos, incorporación o cambio de elementos, aprobación, entrega, devolución y liberación del compromiso. Dos solicitudes de préstamo sobre el mismo recurso no pueden confirmar ambas aunque sus periodos no se solapen. También se protege la concurrencia entre una entrega o liberación y otra solicitud o incorporación. Una consulta previa o la exclusión temporal por sí sola no acreditan la exclusividad física de `RN-DIS-06`; véase el [data-model](data-model.md). El establecimiento del compromiso, los retiros de complementarios y su trazabilidad son atómicos; se protege también la carrera con el inicio de ejecución del espacio (`RN-TIP-PE-28`).
- **RN-DIS-06:** La disponibilidad distingue asignación temporal y compromiso físico. Los espacios, los recursos internos y los complementarios sin entrega física bloquean únicamente su periodo efectivamente asignado en estados bloqueantes; una solicitud sin periodo ni elementos asignados no ocupa franjas. En `RECURSO_CAMPUS` y `RECURSO_EXTERNO`, una asignación efectiva de un recurso `PRINCIPAL` o `ADICIONAL` en `SOLICITADA`, `APROBADA` o `EN_EJECUCION` constituye un compromiso vigente exclusivo sobre `recurso_id`. Comienza al incorporar el recurso y no permite otro compromiso, aunque cambien el tipo de reserva, el solicitante o las fechas. Tampoco permite incluirlo como recurso interno o complementario en otra nueva solicitud o incorporación por espacio. La planificación por franjas de espacios y complementarios sin préstamo se conserva; sus complementarios no constituyen compromisos físicos. Al establecer un préstamo se aplica `RN-TIP-PE-28`: retiro automático en `SOLICITADA` o `APROBADA`, o rechazo si el espacio está `EN_EJECUCION`. Vencer el periodo o la devolución estimada no termina el compromiso. Una cancelación o rechazo válidos antes de la entrega lo terminan sin exigir una devolución inexistente; un retiro permitido antes de entrega termina la asignación conservando su historial. Si hubo entrega, retirarla o cambiar el estado no sustituye la devolución: deben registrarse la devolución de todos los recursos entregados y el cierre único de la reserva. Solo después puede evaluarse una nueva solicitud, verificando habilitación, operatividad y las restantes condiciones vigentes. No se aprueba ni entrega un recurso con otra entrega abierta. Las revalidaciones de la misma reserva excluyen su propio compromiso.
- **RN-DIS-07:** El Usuario siempre puede consultar el horario de atención de la unidad y las franjas disponibles del espacio o recurso; las opciones de visibilidad no pueden ocultar esa información.
- **RN-DIS-08:** Cada unidad puede configurar de forma independiente `mostrar_estado_reserva` y `mostrar_reservista`, ambas desactivadas por defecto, para mostrar al Usuario el estado y el nombre del reservista de la reserva que ocupa una franja no disponible.
- **RN-DIS-09:** El Técnico solo puede modificar estas opciones para su propia unidad organizacional. El Administrador puede modificarlas para cualquier unidad, conforme a los permisos de `auth`.
- **RN-DIS-10:** Las opciones de visibilidad solo determinan la información presentada al Usuario; no modifican la disponibilidad ni las reglas de bloqueo, ni permiten consultar el detalle completo de reservas ajenas. El backend aplica estas opciones al responder las consultas de disponibilidad.
- **RN-DIS-11:** Para espacios, recursos internos y complementarios sin entrega física, el bloqueo corresponde al periodo asignado: un periodo terminado no bloquea intervalos posteriores aunque el proceso automático no haya actualizado el estado. Dos franjas consecutivas se evalúan conforme a `RN-DIS-01`. Esta liberación por tiempo no aplica a compromisos físicos de `RN-DIS-06`: siguen vigentes hasta su terminación válida y, si hubo entrega, hasta registrar devolución y cierre, aunque haya vencido el periodo solicitado.

---

## Propiedad y acceso — RN-PRO

- **RN-PRO-01:** La cuenta usuario puede consultar sus propias reservas independientemente de su estado.
- **RN-PRO-02:** El reservista puede editar directamente sus propias reservas únicamente en `SOLICITADA`, conforme a `RN-PRO-06`. Toda edición revalida las reglas aplicables y se guarda atómicamente; conserva `SOLICITADA` y no activa autoaprobación. En `APROBADA` no hay edición directa por el reservista: solo en espacio e interno el periodo puede negociarse mediante propuestas y contrapropuestas (`RN-PROP-01`, `RN-PROP-05`). Estas no autorizan cambiar espacio ni recursos. `RECHAZADA`, `EN_EJECUCION`, `FINALIZADA` y `CANCELADA` no son editables directamente por el reservista.
- **RN-PRO-03:** Una cuenta sin permisos administrativos no puede consultar el detalle completo, modificar, aprobar, rechazar ni cancelar reservas pertenecientes a terceros. La consulta de disponibilidad puede mostrar únicamente la información de terceros autorizada por `RN-DIS-08` y `RN-DIS-10`.
- **RN-PRO-04:** El Técnico puede consultar y gestionar reservas de terceros únicamente dentro de su propia unidad organizacional. El Administrador puede hacerlo dentro de cualquier unidad organizacional.
- **RN-PRO-05:** La autenticación y la validación de permisos se rigen por las reglas definidas en el módulo `auth`. Las reglas de este dominio determinan qué acciones requieren dichos permisos y sobre qué unidad organizacional deben aplicarse.


- **RN-PRO-06:** En `SOLICITADA`, son editables por el reservista: `observacion`, contexto y solicitud voluntaria de apoyo, sin desactivar el apoyo obligatorio. En `ESPACIO`: espacio, fecha, horario, acompañantes, complementarios y valores de campos adicionales; `asistentes` se deriva del número de acompañantes. En `RECURSO_INTERNO`: fecha, horario y recursos, manteniendo exactamente un principal. En `RECURSO_CAMPUS` y `RECURSO_EXTERNO`: fechas, recursos y datos de salida (razón, lugar y actividad/evento). En `LISTA_ESPERA`: descripción de la necesidad; adjuntos y parte del formulario se gestionan por sus operaciones específicas. No son editables mediante esta operación el tipo, unidad receptora, titular, estado, datos técnicos de evaluación, recepción, aprobación, ejecución, horas, historial ni snapshots generados. Se revalidan las relaciones y el detalle resultantes; al cambiar recursos se conserva la historia de asignación y se aplican `RN-DIS-06` y `RN-TIP-PE-28`. Ningún fallo deja modificaciones parciales.


---

## Aprobación — RN-APR

- **RN-APR-01:** Solo una cuenta autenticada con permiso para gestionar reservas de la unidad receptora puede aprobar o rechazar una reserva.
- **RN-APR-02:** La aprobación automática de reservas creadas por Usuarios puede habilitarse o deshabilitarse por el Técnico desde la configuración de su propia unidad organizacional.
- **RN-APR-03:** Cuando la aprobación automática esté habilitada para la unidad, la reserva creada por un Usuario inicia en `APROBADA` si cumple todas las validaciones. Si un recurso tiene otro compromiso vigente o una entrega abierta, la solicitud con ese recurso se rechaza; no se crea en espera de su liberación (`RN-DIS-06`). Esta vía no aplica a `LISTA_ESPERA`, que siempre inicia en `SOLICITADA` conforme a `RN-TIP-PLE-05`.
- **RN-APR-04:** Cuando la aprobación automática no esté habilitada, la reserva creada por un usuario se registra en estado `SOLICITADA` y requiere revisión del Técnico .
- **RN-APR-05:** Las reservas creadas por un Técnico dentro de su propia unidad se registran directamente en `APROBADA` si cumplen todas las validaciones, excepto `LISTA_ESPERA`, que siempre inicia en `SOLICITADA` y solo se aprueba conforme a `RN-TIP-PLE-05`. Un compromiso vigente o una entrega abierta impiden crear otra solicitud con ese recurso; el Técnico no puede eludir `RN-DIS-06` ni crear una solicitud pendiente de su liberación.
- **RN-APR-06:** La aprobación automática, tanto para usuarios como para Técnico es, no omite las validaciones aplicables al tipo de reserva, incluyendo disponibilidad, horario o fechas, capacidad, estado operativo, habilitación y pertenencia a la unidad cuando correspondan.
- **RN-APR-07:** Aprobar manualmente revalida las condiciones vigentes del tipo, incluida habilitación, operatividad y disponibilidad física cuando corresponda. Se excluye el compromiso de la propia reserva, pero no otros compromisos ni entregas abiertas incompatibles (`RN-DIS-06`).
- **RN-APR-08:** Rechazar una reserva conserva toda su información histórica y debe registrar el motivo del rechazo.
`RN-APR-09` retirado el 2026-09-24: no se admiten solicitudes posteriores pendientes de liberación del mismo recurso. Véanse `RN-RES-14`, `RN-DIS-06` y el [registro de identificadores retirados](../../docs/decisions/identificadores-retirados.md).

---

## Propuesta y contrapropuesta de horario — RN-PROP

- **RN-PROP-01:** El Técnico puede proponer un periodo alternativo con motivo para una reserva temporal en `SOLICITADA` o `APROBADA`. El reservista puede responder o contraproponer conforme a `RN-PROP-03`. Aplica a `ESPACIO`, `RECURSO_INTERNO`, `RECURSO_CAMPUS` y `RECURSO_EXTERNO`; `LISTA_ESPERA` no admite propuestas. La negociación modifica exclusivamente el periodo, no espacio, recursos ni otros datos. En campus y externo solo puede proponerse o contraproponerse antes de generar la FGL 030 al aprobar (`RN-TIP-RC-07`, `RN-TIP-RE-07`).
- **RN-PROP-02:** Una propuesta de periodo notifica a la cuenta usuario y no cambia el estado de la reserva.
- **RN-PROP-03:** La cuenta usuario puede aceptar la propuesta, rechazarla, o presentar una contrapropuesta con su propio motivo.
- **RN-PROP-04:** Ante una contrapropuesta, únicamente el Técnico  puede aceptarla o rechazarla.
- **RN-PROP-05:** En campus y externo, una FGL 030 ya generada impide aceptar cambios de periodo, incluso si la propuesta se creó antes de aprobar; se conserva íntegra la reserva, la orden y la propuesta. Aceptar una propuesta o contrapropuesta exige que la reserva siga en `SOLICITADA` o `APROBADA` y revalida todas las reglas aplicables a la reprogramación: fecha y horario para `ESPACIO` y `RECURSO_INTERNO`; salida y devolución estimada para `RECURSO_CAMPUS` y `RECURSO_EXTERNO`, además de disponibilidad, habilitación, operatividad, capacidad, contexto y demás condiciones que correspondan. Se aplica la antelación de reprogramación de `RN-HOR-06`. Si cumple, periodo y resolución de la propuesta se guardan atómicamente y se conserva el estado vigente: una `APROBADA` permanece `APROBADA`, sin nueva aprobación ni transición ficticia. Se conserva su `fecha_aprobacion`. Si falla cualquier validación o escritura, no se modifica periodo, estado, asignaciones ni resolución de la propuesta, que permanece `VIGENTE`. El compromiso físico propio se conserva y se excluye de la comparación (`RN-DIS-06`).
- **RN-PROP-06:** Rechazar una propuesta o contrapropuesta conserva el periodo y el estado vigente de la reserva (`SOLICITADA` o `APROBADA`), sin generar otra solicitud. Solo se registra la resolución de la propuesta como `RECHAZADA`; no se revoca una aprobación existente.
- **RN-PROP-07:** Solo puede existir una propuesta o contrapropuesta vigente a la vez por reserva.

---

## Cancelación — RN-CAN

- **RN-CAN-01:** Una cancelación válida conserva el registro y libera las asignaciones temporales y los compromisos anteriores a la entrega conforme a `RN-DIS-06`. No sustituye el registro de devolución de un recurso entregado ni restablece su habilitación u operatividad.
- **RN-CAN-02:** Una reserva puede cancelarse mientras no haya iniciado su ejecución. Para `ESPACIO`, el límite corresponde al inicio de su franja; la cancelación automática de una solicitud al vencer `hora_fin` es el caso específico de `RN-TIP-PE-25`. Para `RECURSO_INTERNO`, no se admite cancelación desde `EN_EJECUCION`, cuyo inicio es automático por horario (`RN-TIP-RI-08`). Para campus y externo, el límite corresponde a la entrega física; para lista de espera, al inicio de fabricación o prestación. La cancelación no sustituye la devolución de los préstamos físicos.
- **RN-CAN-03:** Toda cancelación registra el actor, el momento de la acción y el motivo cuando corresponda.
- **RN-CAN-04:** La deshabilitación de un espacio o recurso solo cancela automáticamente la reserva cuando desaparece el objeto de esta: el espacio en una reserva por espacio, o el recurso con rol `PRINCIPAL` en una reserva de recurso interno, campus o externo, conforme a `RN-RES-12`.
- **RN-CAN-05:** Cuando el elemento deshabilitado sea un recurso con rol `ADICIONAL`, la reserva no se cancela: el recurso se retira de la reserva, conserva su historial de asignación y la reserva continúa vigente. Esto es coherente con `RN-TIP-PE-14`, según el cual la falta de recursos complementarios no impide la reserva de un espacio.
- **RN-CAN-06:** Tanto la cancelación automática como el retiro automático de un recurso aplican únicamente a reservas cuya ejecución aún no haya iniciado. En campus y externo, el retiro automático por deshabilitación solo aplica antes del proceso de aprobación, generación de FGL 030 y salida (`RN-TIP-RC-07`, `RN-TIP-RE-07`); no retira recursos de una orden ya generada. Desde la salida, la composición queda fija hasta la devolución.
- **RN-CAN-07:** El sistema debe notificar a los usuarios afectados, distinguiendo si la reserva fue cancelada o si únicamente se retiró un recurso complementario, conforme a las reglas y canales definidos en [business-rules.md](../notifications/business-rules.md).
- **RN-CAN-08:** La cancelación o el retiro automáticos deben registrar como motivo la deshabilitación del espacio o recurso y conservar la trazabilidad histórica de la reserva.

---

## Recordatorios — RN-REC

- **RN-REC-01:** El sistema envía un recordatorio automático a la cuenta usuario antes del inicio previsto de una reserva `ESPACIO` o `RECURSO_INTERNO` en estado `APROBADA`. La anticipación es configurable por unidad en `reservas.laboratorios_config.recordatorio_horas_antes`, y la generación y entrega de la notificación se rigen por [RN-EVT-11](../notifications/business-rules.md) del módulo de notificaciones. `RECURSO_CAMPUS`, `RECURSO_EXTERNO` y `LISTA_ESPERA` no generan este recordatorio, porque no tienen una hora de inicio prevista que permita calcularlo.
- **RN-REC-02:** El recordatorio se genera una única vez por reserva y no se repite. La constancia es la ocurrencia de evento de recordatorio y sus canales registrados en Notifications; reservas no almacena un indicador duplicado.
- **RN-REC-03:** Reprogramar o cancelar la reserva antes de la transmisión del recordatorio anula los envíos de correo pendientes de esa ocurrencia conforme a RN-COR-07. No se registra el recordatorio como enviado ni se altera el resultado histórico de un envío ya transmitido.

---

## Archivo de calendario — RN-CAL

- **RN-CAL-01:** Cuando se apruebe una reserva de tipo `ESPACIO` o `RECURSO_INTERNO` para uso dentro de la unidad organizacional, el sistema debe generar un archivo de calendario iCalendar (`.ics`). Las reservas `RECURSO_CAMPUS`, `RECURSO_EXTERNO` y `LISTA_ESPERA` no generan `.ics`.
- **RN-CAL-02:** El archivo `.ics` debe incluir la fecha, hora de inicio y hora de finalización de la reserva. Para `ESPACIO`, debe incluir el espacio o ubicación cuando aplique; para `RECURSO_INTERNO`, debe incluir la ubicación de uso cuando esté definida. En ambos casos debe incluir una descripción de la reserva.
- **RN-CAL-03:** Cuando corresponda enviar el correo de confirmación de una reserva `ESPACIO` o `RECURSO_INTERNO`, el archivo `.ics` debe adjuntarse a ese correo.
- **RN-CAL-04:** Si una reserva `ESPACIO` o `RECURSO_INTERNO` es modificada y se envía una nueva confirmación, el sistema debe generar un nuevo archivo `.ics` con la información vigente.
- **RN-CAL-05:** No se requiere sincronización directa con calendarios externos ni persistencia de identificadores de eventos externos.

---

## Contexto de la reserva — RN-CTX

El módulo [Researchs](../researchs/overview.md), propietario del dominio `investigacion`, administra el contexto académico/investigativo, las actividades institucionales, los catálogos y las vinculaciones de cuentas Usuario. `reservas` registra cuál de esos contextos justifica cada reserva y conserva su información histórica. Las cuentas `USUARIO` y `PERSONAL` tienen reglas distintas de selección, definidas aquí; la disponibilidad de actividades institucionales para nuevas reservas se rige por RN-ACT de Researchs.

- **RN-CTX-01:** Toda reserva, sin importar su tipo (`ESPACIO`, `RECURSO_INTERNO`, `RECURSO_CAMPUS`, `RECURSO_EXTERNO` o `LISTA_ESPERA`), debe estar asociada al menos a un contexto académico/investigativo o a una actividad institucional.
- **RN-CTX-02:** El contexto académico/investigativo puede incluir como máximo un proyecto, un semillero, una pasantía y un trabajo de grado.
- **RN-CTX-03:** Semillero, proyecto, pasantía y trabajo de grado pueden coexistir dentro de una misma reserva.
- **RN-CTX-04:** Una actividad institucional constituye un contexto independiente y no puede coexistir en la misma reserva con semillero, proyecto, pasantía ni trabajo de grado.
- **RN-CTX-05:** Para una cuenta `USUARIO`, solo pueden seleccionarse proyectos, semilleros, pasantías y trabajos de grado con vinculación activa y válida de su titular, conforme a `investigacion`. Esta validación se realiza usando el `id_usuario` asociado a la cuenta.
- **RN-CTX-08:** Una cuenta `PERSONAL` solo puede utilizar como contexto máximo un proyecto y máximo un semillero activos del catálogo general de `investigacion`; no requiere ni se le consulta una vinculación propia con ellos. No puede utilizar pasantías, trabajos de grado ni actividades institucionales como contexto.
- **RN-CTX-09:** La selección del contexto no amplía el ámbito de reserva de una cuenta `PERSONAL`: esta solo puede reservar en el laboratorio de su unidad organizacional asociada, conforme a `RN-RES-15`.
- **RN-CTX-06:** El contexto académico, investigativo o institucional de una reserva no otorga por sí mismo permisos administrativos sobre reservas.
- **RN-CTX-07:** El contexto asociado a una reserva debe conservarse históricamente aunque posteriormente cambien los proyectos, semilleros, pasantías, trabajos de grado, actividades institucionales o vinculaciones del usuario.

---

## Acompañante — RN-ACO

- **RN-ACO-01:** Los acompañantes solo aplican cuando la reserva tiene un proyecto o un semillero como contexto.
- **RN-ACO-02:** Cada acompañante debe ser una cuenta existente vinculada activamente al proyecto o al semillero registrado en la reserva.
- **RN-ACO-03:** Una reserva puede registrar de cero a N acompañantes; no es obligatorio registrar uno. El sistema no solicita datos libres del acompañante: el Usuario selecciona cuentas de la lista válida de vinculaciones del proyecto o semillero, y el número de seleccionados determina `asistentes`.
- **RN-ACO-04:** Si la reserva tiene proyecto y semillero, las opciones de acompañante son la unión de las cuentas vinculadas activamente a cualquiera de los dos.
- **RN-ACO-05:** Las reservas de lista de espera no admiten acompañantes.
- **RN-ACO-06:** Ser acompañante no otorga por sí mismo permisos administrativos sobre la reserva; la autorización se determina en `auth`.
- **RN-ACO-07:** La asociación del acompañante se conserva históricamente aunque posteriormente se desactive su vinculación con el proyecto o semillero.

---

## Auditoría — pendiente de diseño

La auditoría de Reservations está fuera del alcance funcional actual. Esta iteración no registra una tabla `reserva_auditoria`, no define snapshots del actor ni exige datos de auditoría para las operaciones de reserva. Su diseño se tratará en una decisión futura.

---

## Reportes — RN-REP

- **RN-REP-01:** Solo el Técnico dentro de su unidad y el Administrador con alcance global pueden generar y exportar reportes de reservas. El Usuario no tiene acceso a esta funcionalidad.
- **RN-REP-02:** El Técnico puede exportar reservas de su unidad; el Administrador puede exportar información de cualquier unidad. Los formatos admitidos son los que define [RN-EXP-05](../reports/business-rules.md) del módulo de reportes, propietario de esa decisión.
- **RN-REP-03:** Un reporte exportado contiene exactamente los datos visibles según el filtro aplicado por quien lo solicita, sin exceder su ámbito de acceso.

---

## Dependencias funcionales

Las reglas de este documento dependen de otros dominios únicamente en los siguientes aspectos:

- **Autenticación y autorización:** [business-rules.md](../auth/business-rules.md) determina autenticación, cuentas activas y validación de permisos.
- **Espacios:** [business-rules.md](../espacios/business-rules.md) determina existencia, habilitación, capacidad, configuración, campos adicionales y recursos asociados a los espacios.
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
7. Se conserva únicamente el historial exigido expresamente por las reglas del módulo, incluidas las transiciones de estado y los retiros automáticos. El retiro manual del Técnico no genera historial específico ni metadatos adicionales. La auditoría general queda fuera del alcance actual.
