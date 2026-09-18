# Flujos de usuario — Reservas

Este documento describe los flujos de interacción del dominio de reservas. Las reglas de negocio asociadas se definen en [business-rules.md](business-rules.md).

## Condición común para crear reservas

En todos los flujos de creación, el sistema aplica RN-RES-11 al iniciar la solicitud y nuevamente al guardarla. Si el Usuario completó su actualización inicial pero ya no tiene ninguna vinculación activa y válida, informa del bloqueo y lo dirige a actualizar sus vinculaciones en el perfil conforme a RN-USR-11. Solo permite continuar cuando `investigacion` confirma al menos una válida. Si la última vinculación deja de ser válida durante el diligenciamiento, rechaza la creación y solicita actualizarla. Esta condición también aplica a reservas con actividad institucional o sin contexto obligatorio.

## Condición común de acompañantes

Cuando el contexto de una reserva incluye proyecto o semillero, el Usuario puede registrar cero o más acompañantes. El sistema ofrece únicamente cuentas existentes con vinculación activa al proyecto o semillero; si ambos están presentes, combina la unión de las cuentas vinculadas activamente a cualquiera de los dos. Las reservas de lista de espera y servicio no permiten acompañantes.

## Condición común de composición y ejecución de recursos

La composición de recursos de cada tipo sigue RN-RES-12. Una reserva por espacio puede continuar sin recursos complementarios y no solicita un recurso principal.

En UF-RES-02, UF-RES-03 y UF-RES-04, el sistema registra por recurso la entrega y la devolución físicas con fecha, responsable y observaciones cuando correspondan, según [el registro de ejecución](data-model.md#reservasreserva_ejecucion_recursos). Asignar un recurso a la reserva o retirarlo de su composición no acredita su entrega ni su devolución. Los cambios de estado siguen las reglas de ejecución del tipo.

## Condición común de disponibilidad

Los flujos de creación, modificación, asignación de elementos y aprobación aplican RN-DIS. Al confirmar la operación, el sistema revalida disponibilidad y guarda de forma transaccional con protección frente a concurrencia; si otra reserva bloquea un elemento obligatorio, informa del conflicto y no confirma los cambios. Al modificar o aprobar se excluye la propia reserva de la comparación. El mecanismo técnico está pendiente de implementación según el data-model.

Solo las asignaciones con periodo definido y un estado bloqueante conforme a RN-EST-02 y RN-EST-03 ocupan disponibilidad. Una solicitud sin periodo, como lista de espera, no ocupa franjas futuras; al asignarle un periodo se aplica la misma validación. Los recursos complementarios no disponibles siguen la excepción RN-TIP-PE-14.

---

## UF-RES-01 — Crear reserva por espacio

### Actor principal
Usuario.

### Flujo
1. El usuario selecciona el laboratorio o unidad organizacional.
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
14. El usuario selecciona uno o más elementos de contexto académico/investigativo (proyecto, semillero, pasantía y trabajo de grado), o una actividad institucional independiente. El sistema impide combinar la actividad institucional con los demás elementos, conforme a `RN-CTX`.
15. Para cada elemento académico/investigativo seleccionado, el sistema consulta las vinculaciones válidas del usuario en el dominio responsable y, si existe una única opción válida, la selecciona automáticamente.
16. Si existen varias opciones válidas para un elemento seleccionado, el usuario selecciona una para ese elemento.
17. El Usuario aplica la condición común de acompañantes; puede continuar sin seleccionar ninguno.
18. El usuario puede registrar una observación para el Técnico.
19. El usuario envía la solicitud.
20. El sistema revalida las reglas aplicables.
21. Si la aprobación automática está habilitada, la reserva queda en `APROBADA`.
22. Si no está habilitada, la reserva queda en `SOLICITADA`.
23. El sistema genera las notificaciones correspondientes.

---

## UF-RES-02 — Crear reserva de recurso para uso dentro del laboratorio

### Actor principal
Usuario.

### Flujo
1. El usuario selecciona el laboratorio o unidad organizacional.
2. Selecciona `Recurso para uso dentro del laboratorio`.
3. El sistema muestra los recursos habilitados.
4. El usuario selecciona uno o varios recursos.
5. Si un equipo seleccionado tiene `requiere_apoyo = true`, el sistema selecciona “requiere técnico” y bloquea su desactivación; si ninguno lo exige, el usuario puede solicitarlo voluntariamente.
5. Selecciona fecha y hora de inicio y fecha y hora de finalización de uso.
6. El sistema valida disponibilidad durante todo el periodo.
7. El usuario envía la solicitud.
8. La reserva queda en `SOLICITADA` o `APROBADA` según la configuración de aprobación automática.

### Ejecución
1. El Técnico  entrega físicamente el recurso.
2. La reserva pasa a `EN_EJECUCION`.
3. El Técnico  puede agregar recursos adicionales si están habilitados, operativos y disponibles durante el periodo aplicable.
4. Al devolver el recurso o finalizar su uso, el Técnico  registra la finalización.
5. La reserva pasa a `FINALIZADA`.

---

## UF-RES-03 — Crear reserva de recurso para uso dentro del campus

### Actor principal
Usuario.

### Flujo
1. El usuario selecciona el laboratorio o unidad organizacional.
2. Selecciona `Recurso para uso dentro del campus`.
3. El sistema muestra los recursos habilitados.
4. El usuario selecciona un recurso.
5. Selecciona fecha de salida y fecha de devolución.
6. El sistema valida disponibilidad durante todo el periodo.
7. El usuario envía la solicitud.
8. La reserva queda en `SOLICITADA` o `APROBADA` según la configuración aplicable.

### Entrega y devolución
1. El Técnico  aprueba la entrega.
2. El sistema genera la orden de salida para uso dentro del campus.
3. Las firmas de aprobación y recepción se diligencian físicamente en la orden; el seguimiento digital de entrega y devolución sigue la condición común de ejecución.
4. Al entregar físicamente el recurso, la reserva pasa a `EN_EJECUCION`.
5. Al devolverlo, el Técnico  registra la devolución.
6. La reserva pasa a `FINALIZADA`.

---

## UF-RES-04 — Crear reserva de recurso fuera del campus

### Actor principal
Usuario.

### Flujo
1. El usuario selecciona el laboratorio o unidad organizacional.
2. Selecciona `Recurso fuera del campus`.
3. El sistema muestra los recursos autorizados para este tipo de salida.
4. El usuario selecciona un recurso.
5. Selecciona fecha de salida y fecha de devolución.
6. El sistema valida disponibilidad durante todo el periodo.
7. El usuario envía la solicitud.
8. La reserva queda en `SOLICITADA` o `APROBADA` según la configuración aplicable.

### Entrega y devolución
1. El Técnico  aprueba la salida.
2. El sistema genera la orden de salida externa.
3. Las firmas de aprobación y recepción se diligencian físicamente en la orden; el seguimiento digital de entrega y devolución sigue la condición común de ejecución.
4. Al entregar físicamente el recurso, la reserva pasa a `EN_EJECUCION`.
5. Al devolverlo, el Técnico  registra la devolución.
6. La reserva pasa a `FINALIZADA`.

---

## UF-RES-05 — Crear reserva tipo lista de espera

### Actor principal
Usuario.

### Flujo
1. El usuario selecciona el laboratorio o unidad organizacional.
2. Selecciona `Lista de espera`.
3. Registra la descripción de la necesidad.
4. Cuando corresponda, adjunta un archivo CAD, imagen u otro archivo técnico.
5. Envía la solicitud.
6. La reserva queda en `SOLICITADA`.
7. El Técnico  revisa la solicitud y determina si es viable.
8. Si no es viable, la reserva pasa a `RECHAZADA`.
9. Si es viable, el sistema habilita el formulario complementario.
10. El usuario diligencia y envía el formulario.
11. El Técnico  revisa la información.
12. Cuando se completan las aprobaciones requeridas, el usuario entrega el material.
13. El Técnico  registra la recepción del material.
14. La reserva pasa a `APROBADA`.
15. Las reservas aprobadas permanecen disponibles para selección del Técnico  sin orden cronológico obligatorio.
16. El Técnico  selecciona la siguiente según prioridad o criterio operativo.
17. Al iniciar la fabricación o prestación, la reserva pasa a `EN_EJECUCION`.
18. Al finalizar, el Técnico  registra las horas empleadas.
19. La reserva pasa a `FINALIZADA`.

---

## UF-RES-06 — Crear reserva por servicio

### Estado
Pendiente de definición funcional.

Este flujo se completará cuando se establezcan las reglas específicas de la reserva por servicio.

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
2. Excluye las reservas cuya ejecución ya haya iniciado.
3. Las reservas afectadas pasan automáticamente a `CANCELADA`.
4. El sistema registra como motivo la deshabilitación del espacio o recurso.
5. Se libera la disponibilidad asociada.
6. El sistema notifica a los usuarios afectados.
7. La acción queda registrada en auditoría.

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
Una reserva pasa a `APROBADA`, o se modifica y requiere el envío de una nueva confirmación.

### Flujo
1. Cuando la reserva queda `APROBADA`, el sistema genera un archivo `.ics` con la fecha, horario, ubicación o espacio cuando aplique y descripción de la reserva.
2. El sistema adjunta el archivo `.ics` al correo de confirmación de la reserva.
3. Si la reserva es modificada y se envía una nueva confirmación, el sistema genera un nuevo archivo `.ics` con la información vigente y lo adjunta a ese correo.
4. El flujo no sincroniza directamente calendarios externos ni persiste identificadores de eventos externos.

---

## UF-RES-18 — Exportar reportes

### Roles participantes
Técnico de la unidad o Administrador.

### Flujo
1. El Técnico consulta el reporte de su unidad o el Administrador consulta el reporte global que necesita.
2. Selecciona la opción de exportar y el formato (CSV o Excel).
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
