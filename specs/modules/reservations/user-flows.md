# Flujos de usuario — Reservas

Este documento describe los flujos de interacción del dominio de reservas. Las reglas de negocio asociadas se definen en [business-rules.md](business-rules.md).

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
10. La falta de disponibilidad de recursos asociados no impide continuar con la reserva del espacio.
11. El usuario diligencia los campos adicionales obligatorios, cuando existan.
12. El usuario selecciona uno o más elementos de contexto académico/investigativo (proyecto, semillero, pasantía y trabajo de grado), o una actividad institucional independiente. El sistema impide combinar la actividad institucional con los demás elementos, conforme a `RN-CTX`.
13. Para cada elemento académico/investigativo seleccionado, el sistema consulta las vinculaciones válidas del usuario en el dominio responsable y, si existe una única opción válida, la selecciona automáticamente.
14. Si existen varias opciones válidas para un elemento seleccionado, el usuario selecciona una para ese elemento.
15. Cuando el contexto seleccionado sea un proyecto o semillero, el sistema muestra únicamente las cuentas asociadas a ese proyecto o semillero como opciones válidas de acompañante, conforme a `RN-ACO`.
16. El usuario selecciona uno o más acompañantes de esa lista.
17. El usuario puede registrar una observación para el Técnico .
18. El usuario envía la solicitud.
19. El sistema revalida las reglas aplicables.
20. Si la aprobación automática está habilitada, la reserva queda en `APROBADA`.
21. Si no está habilitada, la reserva queda en `SOLICITADA`.
22. El sistema genera las notificaciones correspondientes.

---

## UF-RES-02 — Crear reserva de recurso para uso dentro del laboratorio

### Actor principal
Usuario.

### Flujo
1. El usuario selecciona el laboratorio o unidad organizacional.
2. Selecciona `Recurso para uso dentro del laboratorio`.
3. El sistema muestra los recursos habilitados.
4. El usuario selecciona uno o varios recursos.
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
3. La orden registra la aprobación del Técnico  y la recepción del recurso por parte del usuario.
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
3. La orden registra la aprobación del Técnico  y la recepción del recurso por parte del usuario.
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
1. El Técnico  consulta las reservas de las unidades organizacionales autorizadas.
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
1. El Técnico  selecciona una unidad organizacional dentro de su ámbito autorizado.
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

## UF-RES-17 — Enviar, actualizar o cancelar la invitación de calendario

### Actor principal
Sistema.

### Disparador
Una reserva pasa a `APROBADA`, se reprograma estando `APROBADA` o `EN_EJECUCION`, o pasa a `RECHAZADA`/`CANCELADA` teniendo una invitación previa.

### Flujo
1. Cuando la reserva queda `APROBADA`, el sistema genera y envía una invitación de calendario a los interesados, con opción de aceptar o rechazar desde su propio cliente de correo.
2. Si la reserva se reprograma, el sistema actualiza la invitación conservando el mismo identificador de evento.
3. Si la reserva se cancela o rechaza teniendo una invitación previamente enviada, el sistema envía la cancelación de esa invitación.

---

## UF-RES-18 — Exportar reportes

### Actor principal
Técnico  o administrador.

### Flujo
1. El Técnico  o administrador consulta el reporte que necesita, con los filtros aplicables a su ámbito.
2. Selecciona la opción de exportar y el formato (CSV o Excel).
3. El sistema genera el archivo con exactamente los datos visibles según el filtro aplicado, sin exceder el ámbito autorizado del actor.
4. El sistema entrega el archivo para su descarga.

---

## Estados utilizados en los flujos

- `SOLICITADA`
- `APROBADA`
- `RECHAZADA`
- `EN_EJECUCION`
- `FINALIZADA`
- `CANCELADA`

Las etapas internas propias de un tipo de reserva no constituyen estados globales salvo que se incorporen expresamente al catálogo de estados.
