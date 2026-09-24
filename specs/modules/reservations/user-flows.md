# Flujos de usuario — Reservas

Este documento describe los flujos de interacción del dominio de reservas. Las reglas de negocio asociadas se definen en [business-rules.md](business-rules.md).

## Condición común para crear reservas

En todos los flujos de creación, el sistema determina primero el tipo de cuenta. Para `USUARIO`, aplica RN-RES-11 al iniciar la solicitud y nuevamente al guardarla; si la persona no cumple la actualización inicial o ya no conserva una vinculación activa y válida, informa del bloqueo y dirige a actualizar las vinculaciones según RN-USR-11. Si la última vinculación deja de ser válida durante el diligenciamiento, rechaza la creación. Para `PERSONAL`, no aplica el requisito de actualización inicial ni de vinculación académica mínima: limita la unidad receptora al laboratorio asociado a su cargo vigente, conforme a RN-RES-15. Si necesita reservar en otra unidad, debe iniciar la solicitud con una cuenta de tipo `USUARIO`.

Todos los flujos, incluidos espacio, recurso interno, recurso de campus, recurso externo y lista de espera, requieren seleccionar un contexto antes de enviar. Una cuenta `USUARIO` elige sus contextos conforme a RN-CTX-05; una cuenta `PERSONAL` puede elegir como máximo un proyecto y un semillero activos del catálogo general sin vinculación propia, pero no puede elegir pasantías, trabajos de grado ni actividades institucionales, conforme a RN-CTX-08. Si no hay un contexto permitido, el sistema no permite continuar. Esta validación se reejecuta al guardar.

Cada flujo captura el periodo y los datos específicos en el detalle de su tipo. La cabecera solo recibe los datos comunes de la reserva.

## Condición común de acompañantes

Cuando el contexto de una reserva incluye proyecto o semillero, el reservista (cuenta `USUARIO` o `PERSONAL`) puede registrar cero o más acompañantes. El sistema ofrece únicamente cuentas existentes con vinculación activa al proyecto o semillero; si ambos están presentes, combina la unión de las cuentas vinculadas activamente a cualquiera de los dos. Las reservas de lista de espera no permiten acompañantes.

## Condición común de composición y ejecución de recursos

La composición de recursos de cada tipo sigue RN-RES-12. Una reserva por espacio puede continuar sin recursos complementarios y no solicita un recurso principal.

En UF-RES-03 y UF-RES-04, el sistema registra la entrega física y, al cierre, la devolución de todos los recursos entregados con fecha, responsable y observaciones cuando correspondan, según [el registro de ejecución](data-model.md#reservasreserva_ejecucion_recursos). No se permite una devolución parcial durante la ejecución. Asignar un recurso a la reserva o retirarlo de su composición no acredita su entrega ni su devolución. Los cambios de estado siguen las reglas de ejecución del tipo.

## Condición común de disponibilidad

Los flujos de creación, modificación, asignación de elementos y aprobación aplican RN-DIS. Al confirmar la operación, el sistema revalida disponibilidad y guarda de forma transaccional con protección frente a concurrencia; si otra reserva bloquea un elemento obligatorio, informa del conflicto y no confirma los cambios. Al modificar o aprobar se excluye la propia reserva de la comparación. El mecanismo técnico está pendiente de implementación según el data-model.

En espacios, recursos internos y complementarios sin entrega física, las asignaciones bloquean por periodo conforme a RN-EST-02 y RN-EST-03. En préstamos físicos, la incorporación efectiva de cada recurso crea un compromiso exclusivo desde `SOLICITADA`, sin depender del solapamiento de fechas. Lista de espera no asigna recursos ni bloquea franjas. La excepción RN-TIP-PE-14 no permite incorporar recursos con compromiso físico vigente.

En `RECURSO_CAMPUS` y `RECURSO_EXTERNO`, otro compromiso vigente o una entrega abierta impiden crear la solicitud o incorporar el recurso, aunque el nuevo periodo sea posterior. La condición aplica a Usuarios y Técnicos, con o sin autoaprobación. No se crea una solicitud pendiente de liberación. Terminado válidamente el compromiso y registrada la devolución cuando corresponda, cada nueva solicitud revalida habilitación y operatividad conforme a RN-DIS-04 y RN-DIS-06. Una fecha estimada cumplida no acredita disponibilidad. Los complementarios ya asignados a espacios se resuelven mediante `UF-RES-23` al establecer el compromiso: retiro automático en `SOLICITADA` o `APROBADA`, rechazo del préstamo en `EN_EJECUCION`. El espacio nunca se cancela por esta causa.

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
10. Los complementarios con incompatibilidad temporal siguen RN-TIP-PE-14. Los que tengan un compromiso físico vigente se muestran como no seleccionables y no se incluyen, ni como `NO_DISPONIBLE`; el usuario puede continuar con el espacio sin ellos. Si intenta enviarlos, la operación se rechaza sin escrituras parciales.
11. Si entre los equipos seleccionados alguno tiene `requiere_apoyo = true`, el sistema selecciona automáticamente “requiere técnico” y el usuario no puede desmarcarlo.
12. Si ningún equipo exige apoyo, el usuario puede seleccionar voluntariamente “requiere técnico”.
13. El usuario diligencia los campos adicionales obligatorios, cuando existan.
14. El sistema presenta las opciones de contexto según el tipo de cuenta. `USUARIO` puede seleccionar sus contextos válidos y una actividad institucional independiente conforme a `RN-CTX`; `PERSONAL` solo puede seleccionar como máximo un proyecto y un semillero activos del catálogo general, sin consulta de vinculación personal.
15. Para `USUARIO`, el sistema consulta las vinculaciones válidas en `investigacion`; cuando existan varias opciones para cada tipo de contexto, el Usuario selecciona la que justifica la reserva. Para `PERSONAL`, el sistema valida que el proyecto o semillero seleccionado exista y esté activo, sin exigir una fila en las tablas de vinculación de usuarios.
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
7. El sistema valida habilitación, operatividad, disponibilidad temporal y ausencia de otro compromiso vigente para cada recurso. Revalida al guardar; si algún recurso tiene otro compromiso físico, no crea la solicitud (`RN-DIS-06`). Se admiten franjas no solapadas. La reserva interna no genera compromiso físico ni retira complementarios de espacios.
8. El usuario envía la solicitud.
9. La reserva queda en `SOLICITADA` o `APROBADA` según la configuración de aprobación automática.

### Ejecución
1. Al alcanzar `hora_inicio`, el sistema cambia una reserva `APROBADA` a `EN_EJECUCION`.
2. Desde `EN_EJECUCION` ya no puede cancelarse.
3. El Técnico puede agregar recursos adicionales habilitados, operativos y disponibles desde su incorporación hasta el fin de la franja.
4. Al alcanzar `hora_fin`, el sistema cambia `EN_EJECUCION` a `FINALIZADA`.
5. No se registra entrega ni devolución física. La disponibilidad se controla por franja, sin depender de esos registros.

---

## UF-RES-03 — Crear reserva de recurso para uso dentro del campus

### Actor principal
Reservista con cuenta de tipo `USUARIO` o `PERSONAL`.

### Flujo
1. Si la cuenta es `PERSONAL`, el sistema asigna como unidad receptora su laboratorio asociado al cargo vigente y no permite cambiarlo. Si la cuenta es `USUARIO`, selecciona el laboratorio o unidad organizacional permitidos.
2. Selecciona `Recurso para uso dentro del campus`.
3. El sistema muestra los recursos habilitados.
4. El usuario selecciona uno o varios recursos (un `PRINCIPAL` y, opcionalmente, `ADICIONAL`es).
5. Selecciona fecha de salida y fecha estimada de devolución, aplicables a todos los recursos.
6. Registra razón de la solicitud, nombre y dirección del lugar de uso, y el nombre de la actividad o evento cuando aplique. El sistema los conserva asociados a la reserva.
7. El sistema valida habilitación, operatividad, compatibilidad temporal y ausencia de otro compromiso vigente por recurso. Revalida al guardar; otro compromiso físico impide crear la solicitud aunque las fechas sean distintas (`RN-DIS-06`). Los complementarios previos de espacio siguen `UF-RES-23`.
8. El usuario envía la solicitud.
9. Si todas las validaciones se cumplen, la reserva queda en `SOLICITADA` o `APROBADA` según la configuración y el actor. Un recurso comprometido impide crear la solicitud; no se registra una reserva pendiente de su devolución.

### Proceso de salida y devolución
La aprobación, la generación de FGL 030 y el inicio de ejecución integran el mismo proceso de salida. El retiro automático por deshabilitación solo aplica antes de este proceso. Desde la salida, la composición queda fija hasta la devolución.

1. Antes de aprobar o entregar, el sistema revalida habilitación, operatividad y disponibilidad física, excluyendo el compromiso de la propia reserva. No admite otro compromiso ni entrega abierta incompatible; el Técnico no puede continuar si falla la validación.
2. Al pasar la reserva a `APROBADA`, incluida la autoaprobación, el sistema genera la FGL 030 para uso dentro del campus, listando todos los recursos y copiando las casillas del FGL 030 desde `reserva_contexto` y los datos registrados al crear la reserva conforme a RN-SAL.
Desde la generación, la orden es inmutable, no se regenera ni versiona y no se permiten cambios de los datos que contiene.
3. Las firmas de aprobación y recepción se diligencian físicamente en la orden; el seguimiento digital de entrega y devolución sigue la condición común de ejecución.
4. Al entregar físicamente los recursos, la reserva pasa a `EN_EJECUCION`.
5. Al cerrar la reserva, el Técnico registra la devolución de todos los recursos entregados en una sola operación.
6. La reserva pasa a `FINALIZADA`.
7. Para solicitar nuevamente los recursos, primero debe terminar el compromiso anterior y registrarse su devolución cuando corresponda. La nueva solicitud exige comprobar que siguen habilitados y operativos, además de las demás condiciones (`RN-RES-14`, `RN-DIS-06`).

---

## UF-RES-04 — Crear reserva de recurso fuera del campus

### Actor principal
Reservista con cuenta de tipo `USUARIO` o `PERSONAL`.

### Flujo
1. Si la cuenta es `PERSONAL`, el sistema asigna como unidad receptora su laboratorio asociado al cargo vigente y no permite cambiarlo. Si la cuenta es `USUARIO`, selecciona el laboratorio o unidad organizacional permitidos.
2. Selecciona `Recurso fuera del campus`.
3. El sistema muestra los recursos autorizados para este tipo de salida.
4. El usuario selecciona uno o varios recursos (un `PRINCIPAL` y, opcionalmente, `ADICIONAL`es).
5. Selecciona fecha de salida y fecha estimada de devolución, aplicables a todos los recursos.
6. El sistema valida habilitación, operatividad, compatibilidad temporal y ausencia de otro compromiso vigente por recurso. Revalida al guardar; otro compromiso físico impide crear la solicitud aunque las fechas sean distintas (`RN-DIS-06`). Los complementarios previos de espacio siguen `UF-RES-23`.
7. El usuario envía la solicitud.
8. Si todas las validaciones se cumplen, la reserva queda en `SOLICITADA` o `APROBADA` según la configuración y el actor. Un recurso comprometido impide crear la solicitud; no se registra una reserva pendiente de su devolución.

### Proceso de salida y devolución
La aprobación, la generación de FGL 030 y el inicio de ejecución integran el mismo proceso de salida. El retiro automático por deshabilitación solo aplica antes de este proceso. Desde la salida, la composición queda fija hasta la devolución.

1. Antes de aprobar o entregar, el sistema revalida habilitación, operatividad y disponibilidad física, excluyendo el compromiso de la propia reserva. No admite otro compromiso ni entrega abierta incompatible; el Técnico no puede continuar si falla la validación.
2. Al pasar la reserva a `APROBADA`, incluida la autoaprobación, el sistema genera la FGL 030 externa, listando todos los recursos y copiando las casillas del FGL 030 desde `reserva_contexto` y los datos registrados al crear la reserva conforme a RN-SAL.
Desde la generación, la orden es inmutable, no se regenera ni versiona y no se permiten cambios de los datos que contiene.
3. Las firmas de aprobación y recepción se diligencian físicamente en la orden; el seguimiento digital de entrega y devolución sigue la condición común de ejecución.
4. Al entregar físicamente los recursos, la reserva pasa a `EN_EJECUCION`.
5. Al devolverlos, el Técnico  registra la devolución.
6. La reserva pasa a `FINALIZADA`.
7. Para solicitar nuevamente los recursos, primero debe terminar el compromiso anterior y registrarse su devolución cuando corresponda. La nueva solicitud exige comprobar que siguen habilitados y operativos, además de las demás condiciones (`RN-RES-14`, `RN-DIS-06`).

---

## UF-RES-05 — Crear reserva tipo lista de espera

### Actor principal
Reservista con cuenta de tipo `USUARIO` o `PERSONAL`.

### Flujo
1. Si la cuenta es `PERSONAL`, el sistema asigna como unidad receptora su laboratorio asociado al cargo vigente y no permite cambiarlo. Si la cuenta es `USUARIO`, selecciona el laboratorio o unidad organizacional permitidos.
2. Selecciona `Lista de espera`.
3. El sistema no solicita espacio ni recursos para este tipo de reserva.
4. Registra la descripción de la necesidad.
5. Envía la solicitud con su contexto y descripción; la reserva queda en `SOLICITADA`.
6. Con el identificador de la reserva, el reservista carga los archivos técnicos que correspondan mediante la operación de adjuntos. El sistema valida cada archivo; un fallo no registra ese adjunto ni elimina la reserva. Puede consultar y descargar sus archivos.
7. El Técnico consulta la solicitud y sus adjuntos y registra explícitamente la evaluación de viabilidad.
8. Si no es viable, registra el motivo; la evaluación y el paso a `RECHAZADA` se guardan juntos, conservando la información.
9. Si es viable, se registra la evaluación, permanece `SOLICITADA` y se habilita el formulario complementario.
10. Si el reservista cambia la descripción tras evaluarla, se invalida la viabilidad y la revisión técnica y se exige nueva evaluación (`RN-TIP-PLE-09`). Con viabilidad positiva vigente, el reservista diligencia y guarda su parte; el Técnico revisa y completa la suya. Una modificación posterior de la parte del reservista invalida la parte técnica y su revisión, que deben completarse de nuevo (`RN-TIP-PLE-04`).
11. El reservista entrega el material. En una sola operación, el Técnico confirma su recepción y solicita la aprobación.
12. El sistema revalida viabilidad positiva y ambas partes del formulario con revisión vigente. Registra recepción, aprobación e historial en una única transacción. Si falla, conserva `SOLICITADA` sin registrar recepción (`RN-TIP-PLE-05`).
13. Las reservas `APROBADA` permanecen disponibles para selección del Técnico, sin orden cronológico obligatorio.
14. El Técnico selecciona la siguiente según prioridad o criterio operativo e inicia la fabricación o prestación. La acción cambia a `EN_EJECUCION`, sin entrega de recursos ni filas en `reserva_ejecucion_recursos`.
15. Al finalizar, registra las horas empleadas; horas y transición a `FINALIZADA` se guardan juntas. No hay devolución de recursos.

Ninguna etapa introduce estados globales nuevos. Las acciones técnicas exigen permiso sobre la unidad; el reservista solo carga adjuntos y diligencia su parte de una reserva propia.

---

## UF-RES-07 — Revisar y aprobar una reserva

### Actor principal
Técnico .

### Flujo
1. El Técnico consulta las reservas de su propia unidad organizacional.
2. Selecciona una reserva en estado `SOLICITADA`.
3. El sistema muestra datos de la reserva, usuario, tipo, elementos asociados, disponibilidad, observaciones e información adicional aplicable.
4. El Técnico  revisa la solicitud.
5. El sistema revalida las condiciones del tipo. Para campus y externo verifica habilitación, operatividad y disponibilidad física, excluyendo el compromiso propio; no permite otro compromiso ni entrega abierta incompatible (`RN-DIS-06`).
6. El Técnico  puede ajustar los elementos permitidos por las reglas del tipo.
7. Si cumple las validaciones, aprueba y pasa a `APROBADA`. Para `ESPACIO`, si la aprobación ocurre dentro de la franja, pasa inmediatamente a `EN_EJECUCION` en la misma operación; al alcanzar `hora_fin` rige `UF-RES-21` y no se aprueba una franja vencida. Para `LISTA_ESPERA`, esta misma operación registra la recepción del material tras verificar viabilidad y formulario completo con revisión vigente (`UF-RES-05`); no hay una aprobación que omita esa recepción. Si las condiciones cambiaron desde la creación válida, rechaza la operación de aprobación sin cambios; esto no habilita crear solicitudes para esperar otra devolución.
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
4. Si las validaciones se cumplen, la reserva se registra directamente en `APROBADA`, excepto `LISTA_ESPERA`, que sigue siempre su flujo específico en `SOLICITADA`. Si existe otro compromiso vigente o entrega abierta para un recurso, no se crea la solicitud; el permiso del Técnico no exceptúa RN-DIS-06. Los retiros de complementarios previos se coordinan según `UF-RES-23`.

---

## UF-RES-09 — Agregar o retirar recursos complementarios de una reserva por espacio

### Actor principal
Técnico .

### Precondición
La reserva debe estar en `SOLICITADA`, `APROBADA` o `EN_EJECUCION`.

### Flujo de incorporación
1. El Técnico  abre la reserva.
2. Selecciona la opción para gestionar recursos asociados.
3. El sistema muestra recursos habilitados y su disponibilidad.
4. El Técnico  selecciona uno o más recursos.
5. El sistema valida habilitación, estado operativo, disponibilidad y pertenencia o disponibilidad para la unidad. Si existe un compromiso físico vigente en otra reserva, rechaza la incorporación sin cambios (`RN-DIS-06`).
6. Si la reserva está en `EN_EJECUCION`, el sistema valida la disponibilidad desde el instante actual hasta la finalización prevista.
7. El sistema agrega el recurso y, si la reserva está en `EN_EJECUCION`, registra automáticamente `incorporado_at` con ese instante en la misma transacción.

### Retiro manual
El Técnico selecciona recursos complementarios. El sistema revalida la disponibilidad de la composición resultante y retira los seleccionados de la composición vigente, sin historial específico, causa, actor, fecha ni otros metadatos de retiro. Se admiten los mismos estados de la precondición. Este retiro no modifica registros conservados por retiros automáticos ni sustituye sus flujos.

---

## UF-RES-10 — Agregar o retirar recursos adicionales de una reserva de uso dentro del laboratorio

### Actor principal
Técnico .

### Precondición
La reserva debe estar en `SOLICITADA`, `APROBADA` o `EN_EJECUCION`.

### Flujo de incorporación
1. El Técnico  abre la reserva.
2. Selecciona la opción para agregar recursos.
3. El sistema muestra recursos habilitados y disponibles.
4. El Técnico  selecciona recursos adicionales.
5. El sistema valida las condiciones aplicables, incluida la ausencia de otro compromiso vigente; incorporar un adicional a interno crea únicamente su asignación temporal por franja (`RN-DIS-06`), sin entrega física ni retiros de complementarios de otras reservas.
6. Si la reserva está en `EN_EJECUCION`, el sistema valida la disponibilidad desde el instante actual hasta la finalización prevista.
7. El sistema agrega los recursos y, si la reserva está en `EN_EJECUCION`, registra automáticamente `incorporado_at` con ese instante en la misma transacción.

### Retiro manual
El Técnico selecciona recursos adicionales; el `PRINCIPAL` no puede retirarse. El sistema revalida la disponibilidad de la composición resultante y retira los seleccionados de la composición vigente, sin historial específico, causa, actor, fecha ni otros metadatos de retiro. Se admiten los mismos estados de la precondición. Este retiro no modifica registros conservados por retiros automáticos ni sustituye sus flujos.

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
8. El sistema genera las notificaciones correspondientes.

---

## UF-RES-12 — Cancelación automática por deshabilitación

### Actor principal
Sistema.

### Disparador
Se deshabilita un espacio o recurso.

En campus y externo, el retiro automático de adicionales solo aplica antes del proceso de aprobación, generación de FGL 030 y salida (`RN-CAN-06`). Desde la salida no altera la composición, que queda fija hasta la devolución.

### Flujo
1. El sistema identifica las reservas futuras que dependan del elemento deshabilitado.
2. Excluye las reservas cuya ejecución ya haya iniciado (`RN-CAN-06`).
3. El sistema determina, para cada reserva, si el elemento deshabilitado es el objeto de la reserva: el espacio en una reserva por espacio, o el recurso con rol `PRINCIPAL` en una reserva de recurso (`RN-CAN-04`).
4. Si lo es, la reserva pasa automáticamente a `CANCELADA`.
5. Si el elemento es un recurso con rol `ADICIONAL`, el sistema lo retira de la reserva conservando su historial de asignación y la reserva continúa vigente (`RN-CAN-05`).
6. El sistema registra como motivo la deshabilitación del espacio o recurso (`RN-CAN-08`).
7. Se libera la disponibilidad asociada al elemento retirado o a la reserva cancelada.
8. El sistema notifica a los usuarios afectados, distinguiendo cancelación de retiro de un recurso complementario (`RN-CAN-07`).

---

## UF-RES-13 — Iniciar ejecución

### Actor principal
Técnico .

### Alcance
Reservas de `RECURSO_CAMPUS` y `RECURSO_EXTERNO`, cuyo inicio coincide con la entrega física, y `LISTA_ESPERA`, cuyo inicio corresponde a fabricar o prestar el servicio sin entrega de recursos. **`ESPACIO` y `RECURSO_INTERNO` quedan excluidos**: inician automáticamente por horario conforme a `RN-TIP-PE-27`, `RN-TIP-RI-08` y `UF-RES-22`.

### Flujo
1. Para campus y externo, el Técnico continúa el mismo proceso de salida en el que se aprueba y genera la FGL 030; no abre una etapa posterior de ajuste de recursos. Para `LISTA_ESPERA`, selecciona una reserva `APROBADA`.
2. Verifica las condiciones requeridas para iniciar. Para los tipos de préstamo, revalida habilitación, operatividad y ausencia de otra entrega abierta o compromiso incompatible, excluyendo el compromiso propio (`RN-DIS-06`).
3. Ejecuta la acción de inicio: entrega física para los tipos de préstamo; comienzo de fabricación o prestación para `LISTA_ESPERA`, sin registrar recursos ni entregas (`RN-TIP-PLE-07`).
4. La reserva pasa a `EN_EJECUCION`.
5. El sistema registra actor, fecha y hora.

---

## UF-RES-14 — Finalizar reserva

### Actor principal
Técnico .

### Alcance
Reservas de `RECURSO_CAMPUS`, `RECURSO_EXTERNO` y `LISTA_ESPERA`. `ESPACIO` y `RECURSO_INTERNO` quedan excluidos: sus transiciones al fin de franja son automáticas conforme a `RN-TIP-PE-25`, `RN-TIP-RI-09` y `UF-RES-21`, sin cierre manual.

### Flujo
1. El Técnico  selecciona una reserva en `EN_EJECUCION` de alguno de los tipos incluidos en el alcance.
2. Registra la información requerida por el tipo de reserva.
3. Para una reserva de recursos que requiera devolución, registra en la misma operación la devolución de todos los recursos entregados; para lista de espera, registra obligatoriamente `horas_ejecucion` finitas y no negativas, sin recursos ni devoluciones, y guarda horas y cierre en la misma transacción (`RN-TIP-PLE-08`). En campus y externo, la reserva no finaliza mientras falte devolución, aunque haya pasado la fecha estimada (`RN-TIP-RC-10`, `RN-TIP-RE-10`).
4. Confirma la finalización.
5. La reserva pasa a `FINALIZADA`.
6. El sistema genera las notificaciones correspondientes cuando aplique.
7. La devolución y el cierre terminan el préstamo, incluso si el recurso regresa dañado o no operativo. No restablecen su habilitación ni operatividad: una nueva solicitud debe revalidarlas. No se aprueba otra solicitud en espera de devolución, porque no se admite un segundo compromiso vigente (`RN-DIS-04`, `RN-DIS-06`).

---

## UF-RES-15 — Proponer y resolver un periodo alternativo

### Actor principal
Técnico .

### Precondición
La reserva debe estar en `SOLICITADA` o `APROBADA`.

### Flujo
1. El Técnico abre una reserva temporal en `SOLICITADA` o `APROBADA` y selecciona proponer un periodo alternativo. En campus y externo no se permite proponer, contraproponer ni aceptar cambios de periodo desde la generación de la FGL 030 al aprobar, aunque la propuesta sea anterior; el intento no modifica reserva, orden ni propuesta. `LISTA_ESPERA` no admite esta acción.
2. Registra el periodo propuesto y un motivo: fecha y horario para `ESPACIO` o `RECURSO_INTERNO`; fecha de salida y devolución estimada para `RECURSO_CAMPUS` o `RECURSO_EXTERNO`.
3. El sistema notifica al usuario; la reserva conserva su estado y periodo vigentes.
4. El usuario revisa la propuesta y elige aceptarla, rechazarla o contraproponer otro periodo con su propio motivo.
5. Si contrapropone, el sistema notifica al Técnico .
6. El Técnico  revisa la contrapropuesta y elige aceptarla o rechazarla.
7. Al aceptar, el sistema verifica que la reserva siga en `SOLICITADA` o `APROBADA` y revalida todas las reglas aplicables a la reprogramación. Si cumple, registra el periodo y la aceptación juntos, conservando el estado actual y, si estaba aprobada, `fecha_aprobacion`. Si falla, no cambia la reserva ni la propuesta, que sigue `VIGENTE`. En préstamos conserva el mismo compromiso, excluyéndolo de la comparación; no crea uno nuevo ni permite conflictos ajenos (`RN-DIS-06`).
8. Al rechazar, la propuesta queda `RECHAZADA` y la reserva conserva su periodo y estado actual, incluida `APROBADA` cuando corresponda. No se crea una transición de estado de reserva.

---

## UF-RES-16 — Enviar recordatorio automático

### Actor principal
Sistema.

### Disparador
Se acerca la fecha/hora de inicio de una reserva `ESPACIO` o `RECURSO_INTERNO` en estado `APROBADA`.

### Flujo
1. El sistema identifica las reservas elegibles cuyo inicio se aproxima dentro del margen configurado.
2. Excluye las que ya tengan una ocurrencia de evento de recordatorio para esa reserva.
3. El sistema crea la ocurrencia, la notificación in-app y, cuando aplique, el envío de correo al reservista conforme a Notifications.
4. La ocurrencia registrada en Notifications impide otro recordatorio; la reserva no almacena un indicador propio.
5. Si la reserva se reprograma o cancela antes de la transmisión del correo, el sistema anula el envío pendiente conforme a RN-COR-07. Los correos ya enviados no se alteran.

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

## UF-RES-18 — Exportar reportes *(trasladado)*

Este flujo se trasladó a [`UF-REP-02 — Exportar un reporte`](../reports/user-flow.md#uf-rep-02--exportar-un-reporte) de Reports, propietario de las reglas `RN-EXP` que ya citaba. El identificador se conserva sin reasignar para no desplazar `UF-RES-19` ni `UF-RES-20`.

La superficie HTTP sigue en el contrato de reservations, porque lo que se exporta es el listado de reservas.

---

## UF-RES-19 — Consultar disponibilidad

### Roles participantes

Usuario.

### Flujo

1. El Usuario selecciona la unidad, el espacio o recurso y el periodo que desea consultar.
2. El sistema muestra los horarios y franjas disponibles conforme a RN-DIS-07. Un recurso con compromiso físico vigente no se presenta elegible para otra solicitud, tampoco después de su fecha estimada de devolución. Esta condición no modifica las franjas del espacio ni revela datos ajenos fuera de RN-DIS-08 y RN-DIS-10.
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

## UF-RES-21 — Resolver automáticamente el fin de franja

### Actor y disparador

Sistema, al alcanzar `hora_fin` de `ESPACIO` o `RECURSO_INTERNO`. No interviene entrega o devolución física.

### Flujo

1. El sistema evalúa el estado vigente dentro de la operación transaccional.
2. Para `ESPACIO`, si sigue `SOLICITADA`, registra `CANCELADA` con motivo de vencimiento sin aprobación. Si está `APROBADA` o `EN_EJECUCION`, registra `FINALIZADA` (`RN-TIP-PE-25`).
3. Para `RECURSO_INTERNO` en `EN_EJECUCION`, registra `FINALIZADA` (`RN-TIP-RI-09`).
4. `RECHAZADA`, `CANCELADA` y `FINALIZADA` no cambian automáticamente. Se conserva el historial y se identifica al sistema como origen de las transiciones.
5. La disponibilidad de espacios, internos y complementarios sin préstamo se evalúa por sus intervalos: una demora del proceso no bloquea franjas posteriores no solapadas (`RN-DIS-11`). No se crean filas de entrega/devolución.

Los préstamos de campus y externo finalizan con devolución física; lista de espera con horas de prestación. Este proceso no modifica sus estados.

---

## UF-RES-22 — Iniciar automáticamente reservas por franja

### Actor y disparador

Sistema, al alcanzar `hora_inicio` de una reserva `ESPACIO` o `RECURSO_INTERNO` en `APROBADA`.

### Flujo

1. Comprueba el tipo, el estado vigente y la franja.
2. Registra `APROBADA → EN_EJECUCION` automáticamente, con origen sistema e instante (`RN-TIP-PE-27`, `RN-TIP-RI-08`). No registra entrega física ni asistencia.
3. `ESPACIO` puede permanecer `SOLICITADA` durante su franja. Si se aprueba cuando `hora_inicio <= ahora < hora_fin`, la operación de aprobación registra el paso inmediato a `EN_EJECUCION`, sin esperar este proceso.
4. Al llegar `hora_fin` se aplican las transiciones de `UF-RES-21`; un espacio vencido no se inicia por una ejecución tardía de este proceso.
5. `RECHAZADA`, `CANCELADA` y `FINALIZADA` no cambian automáticamente. Desde `EN_EJECUCION`, el recurso interno no puede cancelarse.

El estado no sustituye la evaluación de disponibilidad por franja. Campus, externo y lista de espera conservan sus acciones de inicio de `UF-RES-13`.

---

## UF-RES-23 — Retirar complementarios por un préstamo posterior

### Actor y disparador

Sistema, al establecer un compromiso físico mediante la creación válida de un préstamo o la incorporación permitida de recursos. Aplica `RN-TIP-PE-28`.

### Flujo

1. Revalida las condiciones del préstamo y la ausencia de otro compromiso físico vigente para cada recurso.
2. Identifica sus asignaciones complementarias efectivas en reservas de espacio y comprueba el estado vigente dentro de la transacción, incluyendo la concurrencia con el inicio automático del espacio.
3. Si alguna reserva de espacio afectada está `EN_EJECUCION`, rechaza la operación completa con `409 CONFLICTO`. No crea ni amplía el préstamo y no retira ningún recurso de ninguna reserva.
4. Para las reservas de espacio en `SOLICITADA` o `APROBADA`, marca las asignaciones afectadas `RETIRADO`, conservando fila e historial, instante, causa `PRESTAMO_FISICO` y reserva de préstamo causante. No modifica asignaciones de reservas terminadas.
5. Confirma los retiros, su trazabilidad y el compromiso físico en una única transacción. Cualquier fallo revierte todo el conjunto.
6. La reserva de espacio conserva su estado, espacio, franja y demás recursos; no se cancela ni se registra ejecución física para sus complementarios. Su detalle muestra los retiros con las restricciones de acceso aplicables.
7. Cancelar posteriormente el préstamo no restaura esas asignaciones. Reincorporar el recurso exige una nueva operación permitida de `UF-RES-09` y revalidación; la fila retirada conserva su historia.

---

## UF-RES-24 — Editar directamente una reserva solicitada

### Actor y precondición

Reservista propietario de una reserva `SOLICITADA`, con sesión activa. Aplica `RN-PRO-02`, `RN-PRO-06` y, para cambio de descripción de lista de espera, `RN-TIP-PLE-09`.

### Flujo

1. Consulta su reserva y modifica únicamente los campos permitidos para su tipo.
2. El sistema verifica propiedad, estado y campos inmutables. Una reserva `APROBADA` solo puede reprogramarse mediante `UF-RES-15` si es `ESPACIO` o `RECURSO_INTERNO`; campus y externo no admiten cambios del periodo de la FGL 030 generada. La edición directa se rechaza.
3. Compone los datos resultantes y revalida contexto, acompañantes, apoyo, configuración de campos, capacidad, horario, periodo y recursos según corresponda. Deriva asistentes y apoyo efectivo; el cliente no modifica snapshots ni estados.
4. Si cambian recursos, conserva las asignaciones retiradas, establece las nuevas y aplica exclusividad física y retiros de complementarios mediante `UF-RES-23`. Una reprogramación conserva el compromiso propio.
5. Si cambia la descripción de lista de espera tras una evaluación, invalida esa viabilidad y la revisión técnica dentro de la misma operación; conserva adjuntos y la parte del reservista. El formulario queda bloqueado hasta nueva viabilidad positiva.
6. Confirma los datos y sus efectos juntos, manteniendo `SOLICITADA`. Si falla cualquier condición o escritura, no cambia nada, incluidos retiros, snapshots o viabilidad. La edición no aprueba automáticamente la reserva.

---

## Estados utilizados en los flujos

- `SOLICITADA`
- `APROBADA`
- `RECHAZADA`
- `EN_EJECUCION`
- `FINALIZADA`
- `CANCELADA`

Las etapas internas propias de un tipo de reserva no constituyen estados globales salvo que se incorporen expresamente al catálogo de estados.
