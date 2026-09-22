# Flujos de usuario — Reservas

Este documento describe los flujos de interacción del dominio de reservas. Las reglas de negocio asociadas se definen en [business-rules.md](business-rules.md).

## Condición común para crear reservas

En todos los flujos de creación, el sistema determina primero el tipo de cuenta. Para `USUARIO`, aplica RN-RES-11 al iniciar la solicitud y nuevamente al guardarla; si la persona no cumple la actualización inicial o ya no conserva una vinculación activa y válida, informa del bloqueo y dirige a actualizar las vinculaciones según RN-USR-11. Si la última vinculación deja de ser válida durante el diligenciamiento, rechaza la creación. Para `PERSONAL`, no aplica el requisito de actualización inicial ni de vinculación académica mínima: limita la unidad receptora al laboratorio asociado a su cargo vigente, conforme a RN-RES-15. Si necesita reservar en otra unidad, debe iniciar la solicitud con una cuenta de tipo `USUARIO`.

Todos los flujos, incluidos espacio, recurso interno, recurso de campus, recurso externo y lista de espera, requieren seleccionar un contexto antes de enviar. Una cuenta `USUARIO` elige sus contextos conforme a RN-CTX-05; una cuenta `PERSONAL` puede elegir uno o más proyectos y semilleros activos del catálogo general sin vinculación propia, pero no puede elegir pasantías, trabajos de grado ni actividades institucionales, conforme a RN-CTX-08. Si no hay un contexto permitido, el sistema no permite continuar. Esta validación se reejecuta al guardar.

Cada flujo captura el periodo y los datos específicos en el detalle de su tipo. La cabecera solo recibe los datos comunes de la reserva.

## Condición común de acompañantes

Cuando el contexto de una reserva incluye proyecto o semillero, el reservista (cuenta `USUARIO` o `PERSONAL`) puede registrar cero o más acompañantes. El sistema ofrece únicamente cuentas existentes con vinculación activa al proyecto o semillero; si ambos están presentes, combina la unión de las cuentas vinculadas activamente a cualquiera de los dos. Las reservas de lista de espera no permiten acompañantes.

## Condición común de composición y ejecución de recursos

La composición de recursos de cada tipo sigue RN-RES-12. Una reserva por espacio puede continuar sin recursos complementarios y no solicita un recurso principal.

En UF-RES-02, UF-RES-03 y UF-RES-04, el sistema registra por recurso la entrega y la devolución físicas con fecha, responsable y observaciones cuando correspondan, según [el registro de ejecución](data-model.md#reservasreserva_ejecucion_recursos). Asignar un recurso a la reserva o retirarlo de su composición no acredita su entrega ni su devolución. Los cambios de estado siguen las reglas de ejecución del tipo.

## Condición común de disponibilidad

Los flujos de creación, modificación, asignación de elementos y aprobación aplican RN-DIS. Al confirmar la operación, el sistema revalida disponibilidad y guarda de forma transaccional con protección frente a concurrencia; si otra reserva bloquea un elemento obligatorio, informa del conflicto y no confirma los cambios. Al modificar o aprobar se excluye la propia reserva de la comparación. El mecanismo técnico está pendiente de implementación según el data-model.

Solo las asignaciones con periodo definido y un estado bloqueante conforme a RN-EST-02 y RN-EST-03 ocupan disponibilidad. Una solicitud sin periodo, como lista de espera, no ocupa franjas futuras; al asignarle un periodo se aplica la misma validación. Los recursos complementarios no disponibles siguen la excepción RN-TIP-PE-14.

---

## UF-RES-01 — Crear reserva por espacio

### Actor principal
Reservista con cuenta de tipo `USUARIO` o `PERSONAL`.

### Flujo
1. Si la cuenta es `PERSONAL`, el sistema asigna como unidad receptora su laboratorio asociado al cargo vigente y no permite cambiarlo. Si la cuenta es `USUARIO`, selecciona el laboratorio o unidad organizacional permitidos.
2. El sistema muestra los tipos de reserva habilitados para el laboratorio.
3. El usuario selecciona `Reserva por espacio`.
4. El sistema muestra los espacios habilitados para reservas.
5. El usuario selecciona un espacio.
6. El sistema carga capacidad, horario disponible, recursos asociados y campos adicionales configurados.
7. El usuario selecciona fecha, hora de inicio y hora de finalización.
8. El sistema valida disponibilidad del espacio.
9. El sistema muestra la disponibilidad de los recursos asociados.
10. Los recursos complementarios no disponibles quedan sin asignar para ese periodo y se muestran como no disponibles, conforme a RN-TIP-PE-14; el usuario puede continuar con la reserva del espacio.
11. Si entre los equipos seleccionados alguno tiene `requiere_apoyo = true`, el sistema selecciona automáticamente “requiere técnico” y el usuario no puede desmarcarlo.
12. Si ningún equipo exige apoyo, el usuario puede seleccionar voluntariamente “requiere técnico”.
13. El usuario diligencia los campos adicionales obligatorios, cuando existan.
14. El sistema presenta las opciones de contexto según el tipo de cuenta. `USUARIO` puede seleccionar sus contextos válidos y una actividad institucional independiente conforme a `RN-CTX`; `PERSONAL` solo puede seleccionar uno o más proyectos y semilleros activos del catálogo general, sin consulta de vinculación personal.
15. Para `USUARIO`, el sistema consulta las vinculaciones válidas en `investigacion`; cuando existan varias opciones para el tipo de contexto, el Usuario selecciona las que justifican la reserva. Para `PERSONAL`, el sistema valida que cada proyecto o semillero seleccionado exista y esté activo, sin exigir una fila en las tablas de vinculación de usuarios.
17. Si la reserva tiene proyecto o semillero, el sistema muestra las cuentas vinculadas activamente a cualquiera de esos contextos.
18. El usuario selecciona opcionalmente cero o más cuentas de esa lista; el sistema calcula `asistentes` con el número seleccionado y valida que no supere la capacidad del espacio.
19. El usuario puede registrar una observación para el Técnico.
20. El usuario envía la solicitud.
21. El sistema revalida las reglas aplicables.
22. Si la aprobación automática está habilitada, la reserva queda en `APROBADA`.
23. Si no está habilitada, la reserva queda en `SOLICITADA`.
24. El sistema genera las notificaciones correspondientes.

---

## UF-RES-02 — Crear reserva de recurso para uso dentro del laboratorio

### Actor principal
Reservista con cuenta de tipo `USUARIO` o `PERSONAL`.

### Flujo
1. Si la cuenta es `PERSONAL`, el sistema asigna como unidad receptora su laboratorio asociado al cargo vigente y no permite cambiarlo. Si la cuenta es `USUARIO`, selecciona el laboratorio o unidad organizacional permitidos.
2. Selecciona `Recurso para uso dentro del laboratorio`.
3. El sistema muestra los recursos habilitados.
4. El usuario selecciona uno o varios recursos: un `PRINCIPAL` y, opcionalmente, `ADICIONAL`es (`RN-TIP-RI-01`, `RN-RES-12`).
5. Si un equipo seleccionado tiene `requiere_apoyo = true`, el sistema selecciona “requiere técnico” y bloquea su desactivación; si ninguno lo exige, el usuario puede solicitarlo voluntariamente.
6. Selecciona la fecha y el horario de inicio y finalización de uso, dentro de un mismo día y aplicables a todos los recursos (`RN-TIP-RI-02`).
7. El sistema valida la disponibilidad de cada recurso durante todo el periodo.
8. El usuario envía la solicitud.
9. La reserva queda en `SOLICITADA` o `APROBADA` según la configuración de aprobación automática.

### Ejecución
1. El Técnico  entrega físicamente el recurso.
2. La reserva pasa a `EN_EJECUCION`.
3. El Técnico  puede agregar recursos adicionales si están habilitados, operativos y disponibles durante el periodo aplicable.
4. Al devolver el recurso o finalizar su uso, el Técnico  registra la finalización.
5. La reserva pasa a `FINALIZADA`.

---

## UF-RES-03 — Crear reserva de recurso para uso dentro del campus

### Actor principal
Reservista con cuenta de tipo `USUARIO` o `PERSONAL`.

### Flujo
1. Si la cuenta es `PERSONAL`, el sistema asigna como unidad receptora su laboratorio asociado al cargo vigente y no permite cambiarlo. Si la cuenta es `USUARIO`, selecciona el laboratorio o unidad organizacional permitidos.
2. Selecciona `Recurso para uso dentro del campus`.
3. El sistema muestra los recursos habilitados.
4. El usuario selecciona uno o varios recursos (un `PRINCIPAL` y, opcionalmente, `ADICIONAL`es).
5. Selecciona fecha de salida y fecha de devolución, aplicables a todos los recursos.
6. El sistema valida disponibilidad de cada recurso durante todo el periodo.
7. El usuario envía la solicitud.
8. La reserva queda en `SOLICITADA` o `APROBADA` según la configuración aplicable.

### Entrega y devolución
1. El Técnico  aprueba la entrega.
2. El sistema genera la orden de salida para uso dentro del campus, listando todos los recursos y copiando las casillas del FGL 030 desde `reserva_contexto` conforme a RN-SAL.
3. Las firmas de aprobación y recepción se diligencian físicamente en la orden; el seguimiento digital de entrega y devolución sigue la condición común de ejecución.
4. Al entregar físicamente los recursos, la reserva pasa a `EN_EJECUCION`.
5. Al devolverlos, el Técnico  registra la devolución.
6. La reserva pasa a `FINALIZADA`.
7. Si el Usuario necesita usar los recursos por un periodo posterior, debe crear una nueva reserva conforme a `RN-RES-14`; el sistema valida disponibilidad y aplica las aprobaciones correspondientes.

---

## UF-RES-04 — Crear reserva de recurso fuera del campus

### Actor principal
Reservista con cuenta de tipo `USUARIO` o `PERSONAL`.

### Flujo
1. Si la cuenta es `PERSONAL`, el sistema asigna como unidad receptora su laboratorio asociado al cargo vigente y no permite cambiarlo. Si la cuenta es `USUARIO`, selecciona el laboratorio o unidad organizacional permitidos.
2. Selecciona `Recurso fuera del campus`.
3. El sistema muestra los recursos autorizados para este tipo de salida.
4. El usuario selecciona uno o varios recursos (un `PRINCIPAL` y, opcionalmente, `ADICIONAL`es).
5. Selecciona fecha de salida y fecha de devolución, aplicables a todos los recursos.
6. El sistema valida disponibilidad de cada recurso durante todo el periodo.
7. El usuario envía la solicitud.
8. La reserva queda en `SOLICITADA` o `APROBADA` según la configuración aplicable.

### Entrega y devolución
1. El Técnico  aprueba la salida.
2. El sistema genera la orden de salida externa, listando todos los recursos y copiando las casillas del FGL 030 desde `reserva_contexto` conforme a RN-SAL.
3. Las firmas de aprobación y recepción se diligencian físicamente en la orden; el seguimiento digital de entrega y devolución sigue la condición común de ejecución.
4. Al entregar físicamente los recursos, la reserva pasa a `EN_EJECUCION`.
5. Al devolverlos, el Técnico  registra la devolución.
6. La reserva pasa a `FINALIZADA`.
7. Si el Usuario necesita usar los recursos por un periodo posterior, debe crear una nueva reserva conforme a `RN-RES-14`; el sistema valida disponibilidad y aplica las aprobaciones correspondientes.

---

## UF-RES-05 — Crear reserva tipo lista de espera

### Actor principal
Reservista con cuenta de tipo `USUARIO` o `PERSONAL`.

### Flujo
1. Si la cuenta es `PERSONAL`, el sistema asigna como unidad receptora su laboratorio asociado al cargo vigente y no permite cambiarlo. Si la cuenta es `USUARIO`, selecciona el laboratorio o unidad organizacional permitidos.
2. Selecciona `Lista de espera`.
3. El sistema no solicita espacio ni recursos para este tipo de reserva.
4. Registra la descripción de la necesidad.
5. Cuando corresponda, adjunta un archivo CAD, imagen u otro archivo técnico.
6. Envía la solicitud.
7. La reserva queda en `SOLICITADA`.
8. El Técnico  revisa la solicitud y determina si es viable.
9. Si no es viable, la reserva pasa a `RECHAZADA`.
10. Si es viable, el sistema habilita el formulario complementario.
11. El usuario diligencia y envía el formulario.
12. El Técnico  revisa la información.
13. Cuando se completan las aprobaciones requeridas, el usuario entrega el material.
14. El Técnico  registra la recepción del material.
15. La reserva pasa a `APROBADA`.
16. Las reservas aprobadas permanecen disponibles para selección del Técnico  sin orden cronológico obligatorio.
17. El Técnico  selecciona la siguiente según prioridad o criterio operativo.
18. Al iniciar la fabricación o prestación, la reserva pasa a `EN_EJECUCION`.
19. Al finalizar, el Técnico  registra las horas empleadas.
20. La reserva pasa a `FINALIZADA`.

---

## UF-RES-07 — Revisar y aprobar una reserva

### Actor principal
Técnico .

### Flujo
1. El Técnico consulta las reservas de su propia unidad organizacional.
2. Selecciona una reserva en estado `SOLICITADA`.
3. El sistema muestra datos de la reserva, usuario, tipo, elementos asociados, disponibilidad, observaciones e información adicional aplicable.
4. El Técnico  revisa la solicitud.
5. El sistema revalida las condiciones aplicables al tipo de reserva.
6. El Técnico  puede ajustar los elementos permitidos por las reglas del tipo.
7. Si aprueba, la reserva pasa a `APROBADA`.
8. Si rechaza, registra el motivo y la reserva pasa a `RECHAZADA`.
9. El sistema genera las notificaciones correspondientes.

---

## UF-RES-08 — Crear reserva como Técnico 

### Actor principal
Técnico .

### Flujo
1. El Técnico selecciona su propia unidad organizacional.
2. Crea la reserva correspondiente.
3. El sistema valida las reglas aplicables al tipo.
4. Si las validaciones se cumplen, la reserva se registra directamente en `APROBADA`.
5. La acción queda registrada en auditoría.

---

## UF-RES-09 — Agregar recursos a una reserva por espacio

### Actor principal
Técnico .

### Precondición
La reserva debe estar en `SOLICITADA`, `APROBADA` o `EN_EJECUCION`.

### Flujo
1. El Técnico  abre la reserva.
2. Selecciona la opción para gestionar recursos asociados.
3. El sistema muestra recursos habilitados y su disponibilidad.
4. El Técnico  selecciona uno o más recursos.
5. El sistema valida habilitación, estado operativo, disponibilidad y pertenencia o disponibilidad para la unidad.
6. Si la reserva está en `EN_EJECUCION`, la disponibilidad se valida desde el momento de incorporación hasta la finalización prevista.
7. El sistema agrega el recurso a la reserva.
8. La acción queda registrada en auditoría.

---

## UF-RES-10 — Agregar recursos a una reserva de uso dentro del laboratorio

### Actor principal
Técnico .

### Precondición
La reserva debe estar en `SOLICITADA`, `APROBADA` o `EN_EJECUCION`.

### Flujo
1. El Técnico  abre la reserva.
2. Selecciona la opción para agregar recursos.
3. El sistema muestra recursos habilitados y disponibles.
4. El Técnico  selecciona recursos adicionales.
5. El sistema valida las condiciones aplicables.
6. Si la reserva está en `EN_EJECUCION`, la disponibilidad se valida desde el momento de incorporación hasta la finalización prevista.
7. Los recursos se agregan a la reserva.
8. La acción queda registrada en auditoría.

---

## UF-RES-11 — Cancelar una reserva

### Actor principal
Usuario.

### Flujo
1. El usuario consulta sus reservas.
2. Selecciona una reserva cuya ejecución no haya iniciado.
3. Selecciona cancelar.
4. El sistema valida que la cancelación esté permitida.
5. El usuario confirma.
6. La reserva pasa a `CANCELADA`.
7. Los espacios y recursos asociados dejan de bloquear disponibilidad futura.
8. La cancelación queda registrada en auditoría.
9. El sistema genera las notificaciones correspondientes.

---

## UF-RES-12 — Cancelación automática por deshabilitación

### Actor principal
Sistema.

### Disparador
Se deshabilita un espacio o recurso.

### Flujo
1. El sistema identifica las reservas futuras que dependan del elemento deshabilitado.
2. Excluye las reservas cuya ejecución ya haya iniciado (`RN-CAN-06`).
3. El sistema determina, para cada reserva, si el elemento deshabilitado es el objeto de la reserva: el espacio en una reserva por espacio, o el recurso con rol `PRINCIPAL` en una reserva de recurso (`RN-CAN-04`).
4. Si lo es, la reserva pasa automáticamente a `CANCELADA`.
5. Si el elemento es un recurso con rol `ADICIONAL`, el sistema lo retira de la reserva conservando su historial de asignación y la reserva continúa vigente (`RN-CAN-05`).
6. El sistema registra como motivo la deshabilitación del espacio o recurso (`RN-CAN-08`).
7. Se libera la disponibilidad asociada al elemento retirado o a la reserva cancelada.
8. El sistema notifica a los usuarios afectados, distinguiendo cancelación de retiro de un recurso complementario (`RN-CAN-07`).
9. La acción queda registrada en auditoría.

---

## UF-RES-13 — Iniciar ejecución

### Actor principal
Técnico .

### Flujo
1. El Técnico  selecciona una reserva `APROBADA`.
2. Verifica las condiciones requeridas para iniciar.
3. Ejecuta la acción de inicio.
4. La reserva pasa a `EN_EJECUCION`.
5. El sistema registra actor, fecha y hora.
6. La acción queda registrada en auditoría.

---

## UF-RES-14 — Finalizar reserva

### Actor principal
Técnico .

### Flujo
1. El Técnico  selecciona una reserva en `EN_EJECUCION`.
2. Registra la información requerida por el tipo de reserva.
3. Cuando aplique, registra devolución de recursos, horas empleadas u observaciones de cierre.
4. Confirma la finalización.
5. La reserva pasa a `FINALIZADA`.
6. La acción queda registrada en auditoría.
7. El sistema genera las notificaciones correspondientes cuando aplique.

---

## UF-RES-15 — Proponer y resolver un horario alternativo

### Actor principal
Técnico .

### Precondición
La reserva debe estar en `SOLICITADA`.

### Flujo
1. El Técnico  abre una reserva en `SOLICITADA` y, en vez de rechazarla, selecciona proponer un horario alternativo.
2. Registra el horario o fecha propuesta y un motivo.
3. El sistema notifica al usuario; la reserva permanece en `SOLICITADA`.
4. El usuario revisa la propuesta y elige aceptarla, rechazarla o contraproponer otro horario con su propio motivo.
5. Si contrapropone, el sistema notifica al Técnico .
6. El Técnico  revisa la contrapropuesta y elige aceptarla o rechazarla.
7. Al aceptarse cualquiera de las dos propuestas, el sistema revalida las reglas aplicables al tipo de reserva (disponibilidad, horario o fechas, capacidad) y reprograma la reserva con el nuevo horario.
8. Al rechazarse una propuesta o contrapropuesta, la reserva conserva su horario original y permanece en `SOLICITADA`.
9. La acción queda registrada en auditoría.

---

## UF-RES-16 — Enviar recordatorio automático

### Actor principal
Sistema.

### Disparador
Se acerca la fecha/hora de inicio de una reserva en estado `APROBADA`.

### Flujo
1. El sistema identifica las reservas `APROBADA` cuyo inicio se aproxima dentro del margen configurado.
2. Excluye las reservas que ya recibieron el recordatorio.
3. El sistema envía el recordatorio a la cuenta usuario responsable de la reserva.
4. El sistema marca la reserva como recordada, para no enviarlo nuevamente.
5. Si la reserva se reprograma o cancela antes del envío, el recordatorio pendiente para ese horario queda anulado.

---

## UF-RES-17 — Generar y adjuntar el archivo de calendario

### Actor principal
Sistema.

### Disparador
Una reserva `ESPACIO` o `RECURSO_INTERNO` para uso dentro de la unidad organizacional pasa a `APROBADA`, o se modifica y requiere el envío de una nueva confirmación.

### Flujo
1. Cuando una reserva `ESPACIO` o `RECURSO_INTERNO` queda `APROBADA`, el sistema genera un archivo `.ics` con la fecha, hora de inicio, hora de finalización, ubicación cuando aplique y descripción. Las reservas de campus, externas y de lista de espera no generan este archivo.
2. El sistema adjunta el archivo `.ics` al correo de confirmación de la reserva.
3. Si la reserva es modificada y se envía una nueva confirmación, el sistema genera un nuevo archivo `.ics` con la información vigente y lo adjunta a ese correo.
4. El flujo no sincroniza directamente calendarios externos ni persiste identificadores de eventos externos.

---

## UF-RES-18 — Exportar reportes

### Roles participantes
Técnico de la unidad o Administrador.

### Flujo
1. El Técnico consulta el reporte de su unidad o el Administrador consulta el reporte global que necesita.
2. Selecciona la opción de exportar y uno de los formatos admitidos por `RN-EXP-05` de reportes (CSV o Excel).
3. El sistema genera el archivo con exactamente los datos visibles según el filtro aplicado, sin exceder el ámbito autorizado del actor.
4. El sistema entrega el archivo para su descarga.

---

## UF-RES-19 — Consultar disponibilidad

### Roles participantes

Usuario.

### Flujo

1. El Usuario selecciona la unidad, el espacio o recurso y el periodo que desea consultar.
2. El sistema muestra los horarios configurados y las franjas disponibles conforme a RN-DIS-07.
3. Para las franjas ocupadas, el sistema consulta las opciones de visibilidad de la unidad y muestra el estado o el nombre del reservista únicamente cuando la opción correspondiente está habilitada.
4. Si ambas opciones están desactivadas, la franja sigue apareciendo como no disponible, sin estado ni nombre del reservista. Esta consulta no permite abrir el detalle completo de reservas ajenas.
5. El Usuario selecciona un periodo y continúa con el flujo del tipo de reserva. La consulta no garantiza la asignación hasta confirmar la operación según la condición común de disponibilidad.

---

## UF-RES-20 — Configurar visibilidad de disponibilidad

### Roles participantes

Técnico de la unidad o Administrador.

### Flujo

1. El Técnico abre la configuración de su propia unidad o el Administrador selecciona la unidad que desea configurar.
2. El sistema muestra las opciones «Mostrar estado de la reserva» y «Mostrar reservista», inicialmente desactivadas.
3. El Técnico o Administrador activa o desactiva cada opción de forma independiente y guarda los cambios.
4. El backend valida los permisos y el ámbito de la unidad conforme a RN-DIS-09, guarda la configuración y registra el cambio para trazabilidad.
5. Las siguientes consultas del Usuario aplican la configuración vigente conforme a RN-DIS-10.

---

## Estados utilizados en los flujos

- `SOLICITADA`
- `APROBADA`
- `RECHAZADA`
- `EN_EJECUCION`
- `FINALIZADA`
- `CANCELADA`

Las etapas internas propias de un tipo de reserva no constituyen estados globales salvo que se incorporen expresamente al catálogo de estados.
