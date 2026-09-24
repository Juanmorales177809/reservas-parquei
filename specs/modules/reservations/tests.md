# Pruebas — Reservations

Qué debe verificarse en el módulo con más reglas del sistema. Convenciones en [testing.md](../../docs/testing.md).

Lo que más importa aquí no es que una reserva se cree, sino **que dos no puedan ocupar lo mismo**. Esa garantía no la da el servicio, la da la base, así que se prueba contra la base.

---

## Concurrencia y disponibilidad

### T-RES-01 — Dos reservas simultáneas sobre el mismo espacio

- **Nivel:** base de datos
- **Cubre:** `RN-DIS-05`
- **Caso:** dos transacciones abiertas a la vez solicitan el mismo espacio en periodos que se solapan; ninguna confirma antes de que la otra escriba.
- **Esperado:** una confirma y la otra falla por la restricción de exclusión. **Nunca quedan dos filas.** Si esta prueba pasa consultando antes de escribir, está mal escrita.

### T-RES-02 — El intervalo contiguo no se considera solapamiento

- **Nivel:** base de datos
- **Cubre:** `RN-DIS-05`
- **Caso:** una reserva termina exactamente cuando empieza la siguiente sobre el mismo espacio.
- **Esperado:** ambas se escriben. Un rango semiabierto no colisiona en su extremo.

### T-RES-03 — Detener el proceso automático no bloquea la disponibilidad

- **Nivel:** servicio
- **Cubre:** `RN-DIS-11`, `RN-TIP-PE-26`
- **Caso:** el proceso de transiciones automáticas está detenido y existe una reserva `ESPACIO` en `APROBADA`, con complementarios sin entrega física, cuya hora ya pasó.
- **Esperado:** se puede reservar un intervalo posterior que no se solapa. El espacio y esos complementarios bloquean por periodo; un estado sin actualizar no ocupa la franja siguiente. Este caso no se aplica a compromisos físicos, que siguen RN-DIS-06.

### T-RES-04 — Un recurso deshabilitado no entra en reservas nuevas

- **Nivel:** servicio
- **Cubre:** `RN-RES-05`, `RN-DIS-04`
- **Caso:** se solicita una reserva con un recurso deshabilitado después de haber sido reservado antes; se repite tras devolución y cierre con un recurso deshabilitado o no operativo.
- **Esperado:** se rechaza, y las reservas anteriores que lo incluían no se alteran.

---

## Transiciones automáticas

### T-RES-05 — La reserva de espacio inicia y finaliza sola

- **Nivel:** servicio
- **Cubre:** `RN-TIP-PE-25`, `RN-TIP-PE-27`
- **Caso:** una reserva de tipo `ESPACIO` en estado `APROBADA` alcanza su `hora_inicio` y después su `hora_fin`.
- **Esperado:** pasa a `EN_EJECUCION` y luego a `FINALIZADA` sin intervención. El inicio automático **no registra asistencia**, y solo ocurre desde `APROBADA`: una `SOLICITADA` que alcanza su hora no arranca.

### T-RES-06 — El recurso interno inicia y finaliza por horario

- **Nivel:** servicio
- **Cubre:** `RN-TIP-RI-07`, `RN-TIP-RI-08`, `RN-TIP-RI-09`, `RN-TIP-RI-13`
- **Caso:** una reserva `RECURSO_INTERNO` en `APROBADA` alcanza `hora_inicio` y después `hora_fin`, sin registros de entrega/devolución.
- **Esperado:** pasa automáticamente a `EN_EJECUCION` y luego a `FINALIZADA`; el historial registra ambas transiciones. No exige ni crea registros de entrega/devolución y permite franjas posteriores no solapadas.

### T-RES-07 — Las transiciones automáticas no se pueden forzar por la API

- **Nivel:** contrato
- **Cubre:** `RN-TIP-PE-25`, `RN-TIP-PE-27`
- **Caso:** se intenta finalizar e iniciar por API una reserva de tipo `ESPACIO`; repetir con `RECURSO_INTERNO`.
- **Esperado:** `409 TIPO_NO_ADMITIDO` tanto al finalizar como al iniciar. Ambas transiciones son del sistema.

---

## Contexto y acompañantes

### T-RES-08 — Sin vinculación activa no hay reserva

- **Nivel:** contrato
- **Cubre:** `RN-CTX-01`, `RN-PRO-05`
- **Caso:** un Usuario sin ninguna vinculación activa solicita una reserva.
- **Esperado:** `403 VINCULACION_REQUERIDA`.

### T-RES-09 — Los acompañantes exigen proyecto o semillero

- **Nivel:** servicio
- **Cubre:** `RN-ACO-01`, `RN-ACO-05`
- **Caso:** se añade un acompañante a una reserva cuyo contexto es una pasantía, y a otra de lista de espera.
- **Esperado:** ambas se rechazan. Los acompañantes solo aplican con proyecto o semillero, y la lista de espera nunca los admite.

### T-RES-10 — El acompañante se elige de la lista válida, no se escribe

- **Nivel:** contrato
- **Cubre:** `RN-ACO-02`, `RN-ACO-03`, `RN-ACO-04`
- **Caso:** se consultan las opciones de acompañante de una reserva con proyecto y semillero, y se intenta añadir una cuenta no vinculada a ninguno de los dos.
- **Esperado:** las opciones son la **unión** de las cuentas vinculadas activamente a ambos; la cuenta ajena se rechaza. No existe ningún campo de texto libre para el acompañante, y `asistentes` resulta del número de seleccionados.

### T-RES-11 — La asociación del acompañante sobrevive a su desvinculación

- **Nivel:** servicio
- **Cubre:** `RN-ACO-07`
- **Caso:** se desactiva la vinculación de un acompañante al proyecto después de registrado en la reserva.
- **Esperado:** la reserva conserva la asociación. El histórico no se reescribe.

### T-RES-12 — Ser acompañante no otorga permisos

- **Nivel:** contrato
- **Cubre:** `RN-ACO-06`, `RN-PRO-03`
- **Caso:** un acompañante intenta consultar el detalle completo y cancelar la reserva en la que figura.
- **Esperado:** se le deniega igual que a cualquier tercero.

---

## Propiedad y acceso

### T-RES-13 — El Usuario ve sus reservas en cualquier estado

- **Nivel:** contrato
- **Cubre:** `RN-PRO-01`
- **Caso:** un Usuario lista sus reservas teniendo alguna en cada estado.
- **Esperado:** aparecen todas, incluidas `CANCELADA` y `FINALIZADA`.

### T-RES-14 — La edición directa depende del estado

- **Nivel:** servicio
- **Cubre:** `RN-PRO-02`
- **Caso:** el reservista intenta cambiar fecha, horario, espacio y recursos con la reserva en `SOLICITADA`, `APROBADA`, `RECHAZADA`, `EN_EJECUCION`, `FINALIZADA` y `CANCELADA`.
- **Esperado:** solo procede en `SOLICITADA`, y los cambios que afectan disponibilidad se revalidan. En `APROBADA` solo espacio e interno pueden negociar el periodo por propuesta; esta no permite cambiar espacio ni recursos. Los demás estados no admiten edición directa.

### T-RES-15 — El Técnico no sale de su unidad

- **Nivel:** contrato
- **Cubre:** `RN-PRO-04`
- **Caso:** un Técnico consulta y aprueba una reserva de otra unidad; un Administrador hace lo mismo.
- **Esperado:** el Técnico recibe `403`, o `404` cuando revelar la existencia sea una fuga. El Administrador procede en cualquier unidad.

### T-RES-16 — La disponibilidad ajena se muestra recortada

- **Nivel:** contrato
- **Cubre:** `RN-PRO-03`, `RN-DIS-08`, `RN-DIS-10`
- **Caso:** un Usuario consulta la disponibilidad de un espacio ocupado por la reserva de otra persona.
- **Esperado:** ve que el intervalo está ocupado y **nada más**: ni titular, ni contexto, ni detalle.

---

## Cancelación y órdenes

### T-RES-17 — Deshabilitar con reservas futuras avisa antes de cancelar

- **Nivel:** contrato
- **Cubre:** `RN-CAN-04`
- **Caso:** se deshabilita un elemento con reservas futuras sin enviar confirmación.
- **Esperado:** `409 CONFLICTO` con el número de reservas afectadas en `detalles`. Sin confirmación, **nada se cancela**.

### T-RES-18 — La orden de salida no lleva firma

- **Nivel:** contrato
- **Cubre:** `RN-TIP-RC-11`, `RN-SAL-01`
- **Caso:** se genera la orden de salida prellenada.
- **Esperado:** no contiene ningún campo de firma. Los jefes firman sobre el documento impreso.

---

## Compromiso físico único — decisión del hallazgo 1 (2026-09-24)

Pruebas documentadas, todavía no implementadas ni ejecutadas.

### T-RES-19 — Un compromiso físico impide otro aunque cambien las fechas

- **Nivel:** servicio
- **Cubre:** `RN-RES-14`, `RN-DIS-06`, `RN-EST-02`
- **Caso:** A incorpora un recurso para el 1–3 de octubre; se intenta crear B para el 5–6. Repetir con A en SOLICITADA, APROBADA y EN_EJECUCION, para cada tipo de préstamo y roles PRINCIPAL y ADICIONAL.
- **Esperado:** B no se crea y A conserva su compromiso. No se requiere que A haya sido entregada; vencer sus fechas tampoco permite B.

### T-RES-20 — El contrato rechaza el segundo compromiso sin escrituras parciales

- **Nivel:** contrato
- **Cubre:** `RN-DIS-03`, `RN-DIS-05`, `RN-DIS-06`, `RN-APR-03`, `RN-APR-05`
- **Caso:** POST /api/reservas con contexto y detalle válidos y varios recursos, uno comprometido en A para otras fechas. Repetir como Usuario y Técnico y con autoaprobación activada y desactivada.
- **Esperado:** 409 CONFLICTO con envolvente error y detalles vacíos. No quedan cabecera, detalle, contexto ni asociaciones de B; no se devuelve 201 SOLICITADA.

### T-RES-21 — La exclusividad atraviesa tipos de préstamo

- **Nivel:** servicio
- **Cubre:** `RN-RES-14`, `RN-DIS-06`
- **Caso:** Crear A con un recurso en RECURSO_CAMPUS y RECURSO_EXTERNO; intentar B con el mismo recurso en los otros tipos y periodos distintos.
- **Esperado:** Se rechaza B en todas las combinaciones, también con otra cuenta o rol de asignación.

### T-RES-22 — Incorporar recursos no elude el compromiso

- **Nivel:** contrato
- **Cubre:** `RN-TIP-PE-22`, `RN-TIP-RI-11`, `RN-DIS-05`, `RN-DIS-06`
- **Caso:** POST /api/reservas/{id}/recursos sobre ESPACIO y RECURSO_INTERNO con un lote que contiene un recurso comprometido en otra reserva y uno libre.
- **Esperado:** 409 CONFLICTO; no se incorpora ninguno del lote ni se altera el compromiso existente.

### T-RES-23 — Un complementario comprometido no se incluye como no disponible

- **Nivel:** contrato
- **Cubre:** `RN-TIP-PE-14`, `RN-DIS-06`
- **Caso:** POST /api/reservas de ESPACIO incluyendo un recurso comprometido físicamente; repetir sin ese recurso y con los demás datos válidos.
- **Esperado:** La primera petición responde 409 CONFLICTO sin filas, tampoco NO_DISPONIBLE. La segunda responde 201 y conserva la reserva de espacio sin el recurso.

### T-RES-24 — Dos préstamos concurrentes con periodos distintos

- **Nivel:** base de datos
- **Cubre:** `RN-DIS-05`, `RN-DIS-06`
- **Caso:** Dos transacciones intentan incorporar efectivamente el mismo recurso en reservas físicas de periodos distintos, antes de que cualquiera confirme; repetir entre tipos de préstamo.
- **Esperado:** Solo una confirma; la otra falla por la garantía de integridad en base de datos. No se acredita con consultas previas ni solo con exclusión temporal.

### T-RES-25 — Aprobación reprogramación y entrega conservan el compromiso propio

- **Nivel:** servicio
- **Cubre:** `RN-DIS-06`, `RN-APR-07`, `RN-PROP-05`
- **Caso:** Crear A, aceptar una propuesta válida de otro periodo, aprobarla y registrar su entrega. Intentar crear B antes y después de cada operación.
- **Esperado:** A no colisiona consigo misma y conserva un solo compromiso; B siempre se rechaza. La entrega de A no queda impedida por un segundo préstamo futuro, porque B nunca pudo crearse.

### T-RES-26 — Cancelación y rechazo válidos anteriores a entrega liberan el compromiso

- **Nivel:** servicio
- **Cubre:** `RN-CAN-01`, `RN-EST-03`, `RN-DIS-06`
- **Caso:** Cancelar o rechazar válidamente A antes de la entrega; intentar después una solicitud B con el mismo recurso habilitado y operativo.
- **Esperado:** A conserva su historia, no se inventa devolución y B puede crearse si satisface las demás reglas.

### T-RES-27 — Devolución y cierre permiten evaluar una nueva solicitud

- **Nivel:** contrato
- **Cubre:** `RN-RES-14`, `RN-DIS-04`, `RN-DIS-06`
- **Caso:** Finalizar por POST /api/reservas/{id}/finalizacion devolviendo todos los recursos de A; después crear B con un recurso habilitado y operativo y datos válidos.
- **Esperado:** El cierre responde 200 FINALIZADA y la creación 201 con estado según aprobación aplicable. No hay aprobación automática de una solicitud que esperara devolución.

### T-RES-28 — Devolver un recurso dañado no lo hace reservable

- **Nivel:** contrato
- **Cubre:** `RN-DIS-04`, `RN-DIS-06`
- **Caso:** Registrar devolución completa y cierre de A con recurso dañado, en mantenimiento o deshabilitado según el módulo propietario; intentar POST /api/reservas con ese recurso.
- **Esperado:** El cierre responde 200 FINALIZADA. La nueva solicitud responde 409 CONFLICTO sin escrituras. La devolución permanece registrada y no modifica habilitación ni operatividad.

### T-RES-29 — Una entrega abierta no se libera mediante retiro o cambio de estado

- **Nivel:** contrato
- **Cubre:** `RN-DIS-06`, `RN-EST-03`, `RN-CAN-01`
- **Caso:** Con A entregada, intentar DELETE de su asignación, cancelación, rechazo o finalización que omita un recurso entregado pendiente de devolución.
- **Esperado:** 409 ESTADO_INCOMPATIBLE; no se altera la entrega ni se libera el compromiso, y otra solicitud sigue impedida.

### T-RES-30 — La disponibilidad no promete liberación en la fecha estimada

- **Nivel:** contrato
- **Cubre:** `RN-DIS-06`, `RN-DIS-10`, `RN-DIS-11`
- **Caso:** GET /api/reservas/disponibilidad para un recurso comprometido y fechas posteriores a su devolución estimada; repetir tras devolución con recurso no operativo.
- **Esperado:** Las franjas consultadas del recurso tienen disponible=false. No se revela identidad ajena sin autorización ni se marca ocupado el espacio completo por ese recurso.

### T-RES-31 — Las franjas de espacios conservan su planificación

- **Nivel:** base de datos
- **Cubre:** `RN-DIS-01`, `RN-DIS-05`, `RN-TIP-PE-24`
- **Caso:** Registrar dos reservas de ESPACIO con el mismo complementario sin préstamo físico en franjas contiguas y no solapadas.
- **Esperado:** Ambas se admiten. No se aplica exclusividad global de préstamo a esos complementarios ni al espacio; se mantiene la protección contra solapamientos.

### T-RES-32 — Concurrencia de entrega liberación e incorporación

- **Nivel:** base de datos
- **Cubre:** `RN-DIS-05`, `RN-DIS-06`
- **Caso:** Competir entrega de A con incorporación del mismo recurso en B; repetir con devolución y cierre válidos de A frente a creación de B.
- **Esperado:** Mientras A mantenga su compromiso B no confirma. Tras cierre confirmado B solo puede confirmar conforme a las condiciones vigentes; nunca hay dos compromisos ni entrega abierta desprotegida.

### T-RES-33 — El retiro automático por deshabilitación antes de entrega conserva el historial

- **Nivel:** servicio
- **Cubre:** `RN-DIS-06`, `RN-CAN-05`
- **Caso:** Deshabilitar un adicional aún no entregado de un préstamo y ejecutar su retiro automático; comprobar el historial y evaluar una nueva solicitud. No se utiliza el DELETE genérico.
- **Esperado:** La asignación retirada conserva su historia y ya no mantiene ese compromiso. La nueva solicitud exige habilitación, operatividad y las demás condiciones; la retirada no las restablece.

---

## Caso mixto — cierre funcional del hallazgo 1

### T-RES-34 — Préstamo posterior retira complementarios sin cancelar el espacio

- **Nivel:** contrato
- **Cubre:** `RN-TIP-PE-28`, `RN-DIS-06`
- **Caso:** POST /api/reservas de préstamo con recurso previamente ASIGNADO como complementario de ESPACIO. Repetir en SOLICITADA y APROBADA, con fechas solapadas y distintas y en los dos tipos de préstamo físico (campus y externo).
- **Esperado:** 201 con el estado de aprobación aplicable. La asignación previa pasa a RETIRADO; el espacio conserva estado, franja y demás recursos. No se registra entrega física del espacio.

### T-RES-35 — Historial causa y reserva causante se conservan

- **Nivel:** contrato
- **Cubre:** `RN-TIP-PE-28`, `RN-PRO-03`
- **Caso:** Tras el retiro automático, consultar GET /api/reservas/{id} del espacio con actores con y sin acceso al préstamo causante.
- **Esperado:** Se conserva la fila retirada y se muestran retirado_at y causa_retiro=PRESTAMO_FISICO; reserva_causante_id identifica el préstamo solo para el actor autorizado, y es null para los demás. La referencia se mantiene internamente y no se concede acceso al préstamo.

### T-RES-36 — Espacio en ejecución impide el préstamo posterior

- **Nivel:** contrato
- **Cubre:** `RN-TIP-PE-28`, `RN-DIS-05`
- **Caso:** Intentar crear un préstamo de RECURSO_CAMPUS o RECURSO_EXTERNO cuando ese recurso es complementario efectivo de ESPACIO en EN_EJECUCION; incluir otro recurso cuyo complemento pertenece a un espacio APROBADA.
- **Esperado:** 409 CONFLICTO con detalles vacíos. No se establece el préstamo ni se asigna el lote; tampoco se retira el otro complementario. Ambos espacios conservan sus asignaciones.

### T-RES-37 — Préstamo retiros y trazabilidad son atómicos

- **Nivel:** base de datos
- **Cubre:** `RN-TIP-PE-28`, `RN-DIS-05`
- **Caso:** La operación afecta varias asignaciones complementarias y establece un compromiso físico; provocar fallo de integridad antes de confirmar.
- **Esperado:** Rollback completo: sin préstamo nuevo, sin incorporación, sin retiros ni trazabilidad parcial. Las asignaciones previas siguen vigentes.

### T-RES-38 — Cancelar el préstamo no restaura complementarios

- **Nivel:** servicio
- **Cubre:** `RN-TIP-PE-28`, `RN-CAN-01`
- **Caso:** Crear un préstamo que retire complementarios y cancelarlo válidamente antes de entrega.
- **Esperado:** Las filas siguen RETIRADO con causa y referencia causante intactas. Reincorporar requiere una operación permitida y revalidación, y crea una nueva asignación sin sobrescribir la historia.

### T-RES-39 — Inicio del espacio concurrente con préstamo

- **Nivel:** base de datos
- **Cubre:** `RN-TIP-PE-28`, `RN-DIS-05`, `RN-TIP-PE-27`
- **Caso:** Competir el inicio automático del espacio APROBADA con un préstamo que requiere uno de sus complementarios.
- **Esperado:** Si el inicio confirma primero, el préstamo falla sin retiros. Si el préstamo retira primero, el espacio inicia sin ese complementario. Nunca se retira a un espacio ya EN_EJECUCION ni se confirma una combinación incompatible.

### T-RES-40 — Incorporación complementaria concurrente con préstamo

- **Nivel:** base de datos
- **Cubre:** `RN-TIP-PE-28`, `RN-DIS-05`, `RN-DIS-06`
- **Caso:** Competir la incorporación de un complementario a un espacio SOLICITADA o APROBADA con la creación de un préstamo del mismo recurso.
- **Esperado:** Si el préstamo confirma primero, la incorporación se rechaza. Si el complementario se incorpora primero, el préstamo lo retira atómicamente con causa y reserva causante. No quedan ambas asignaciones efectivas incompatibles.

---

## Lista de espera — cierre documental del hallazgo 2

Casos especificados; no implican pruebas implementadas ni ejecutadas.

### T-RES-41 — Viabilidad explícita positiva y negativa

- **Nivel:** contrato
- **Cubre:** `RN-TIP-PLE-03`, `RN-EST-05`
- **Caso:** POST /api/reservas/{id}/lista-espera/viabilidad sobre LISTA_ESPERA SOLICITADA con viable=true; repetir en otra reserva con viable=false y motivo no vacío.
- **Esperado:** 200: la positiva persiste evaluación y mantiene SOLICITADA; la negativa persiste evaluación, motivo e historial y queda RECHAZADA. Sin motivo requerido: 422 VALIDACION sin cambios. No se crean estados globales.

### T-RES-42 — Permisos y ámbito de acciones de lista de espera

- **Nivel:** contrato
- **Cubre:** `RN-PRO-03`, `RN-PRO-04`, `RN-TIP-PLE-03`, `RN-TIP-PLE-04`, `RN-TIP-PLE-05`, `RN-TIP-PLE-07`, `RN-TIP-PLE-08`
- **Caso:** Un reservista sin permisos técnicos y un Técnico de otra unidad intentan evaluar viabilidad, escribir parte técnica, aprobar, iniciar y finalizar. El Técnico intenta escribir la parte del reservista de una reserva ajena.
- **Esperado:** 403 NO_AUTORIZADO o 404 NO_ENCONTRADO cuando corresponda ocultar existencia, sin cambios ni archivos expuestos. El reservista propietario puede cargar archivos y escribir únicamente su parte; un permiso administrativo no permite suplantarla.

### T-RES-43 — Formulario habilitado solo tras viabilidad

- **Nivel:** contrato
- **Cubre:** `RN-TIP-PLE-03`, `RN-TIP-PLE-04`
- **Caso:** PUT /api/reservas/{id}/lista-espera/formulario antes de evaluar; repetir tras viable=true; intentar parte técnica sin parte del reservista y cuerpos vacíos o con ambas partes.
- **Esperado:** 409 CONFLICTO antes de viabilidad o sin parte previa del reservista. Tras viable=true, cada parte válida responde 200 sin aprobar. Cuerpo inválido responde 422 VALIDACION; no cambia el formulario.

### T-RES-44 — Modificar la parte del reservista exige nueva revisión

- **Nivel:** servicio
- **Cubre:** `RN-TIP-PLE-04`, `RN-TIP-PLE-05`
- **Caso:** Con formulario revisado y reserva SOLICITADA, el reservista modifica datos_usuario; después se intenta recepción y aprobación.
- **Esperado:** La modificación invalida datos_tecnico, revisado_por y revisado_at conjuntamente. La aprobación se rechaza hasta completar una nueva revisión; no registra recepción.

### T-RES-45 — Carga y consulta de adjuntos técnicos

- **Nivel:** contrato
- **Cubre:** `RN-TIP-PLE-02`, `RN-PRO-01`, `RN-PRO-03`
- **Caso:** Crear LISTA_ESPERA y cargar por multipart archivos de cada formato permitido, antes y después de viabilidad mientras siga SOLICITADA. Consultar listado paginado y descargar como propietario y Técnico autorizado; intentar descarga ajena y un adjunto de otra reserva.
- **Esperado:** 201 por archivo válido con metadatos sin storage_key; listado y descarga autorizados responden 200 y conservan archivos al terminar la reserva. Acceso fuera de ámbito o adjunto de otra reserva: 404. Las cargas no cambian estado ni habilitan formulario.

### T-RES-46 — Adjuntos inválidos y fallo de almacenamiento

- **Nivel:** contrato
- **Cubre:** `RN-TIP-PLE-02`
- **Caso:** Cargar archivo vacío, mayor de 5242880 bytes, formato prohibido o contenido distinto del MIME; repetir con tamaño límite válido y simular fallo de almacenamiento.
- **Esperado:** 422 VALIDACION para archivos inválidos; el límite válido se acepta si cumple el formato. Fallo de almacenamiento: 500 ERROR_INTERNO sin detalles internos. No queda adjunto incompleto ni se elimina la reserva SOLICITADA; se permite reintentar.

### T-RES-47 — Recepción y aprobación en una sola operación

- **Nivel:** contrato
- **Cubre:** `RN-TIP-PLE-05`, `RN-APR-01`
- **Caso:** POST /api/reservas/{id}/aprobacion con material_recibido=true y reserva SOLICITADA viable con ambas partes completas y revisión vigente. Repetir sin confirmación, con false, sin viabilidad o con formulario incompleto.
- **Esperado:** 200 APROBADA con fecha_aprobacion y detalle.fecha_recepcion_material registradas conjuntamente. Confirmación ausente o false: 422 VALIDACION; precondiciones de negocio ausentes: 409 CONFLICTO. Ningún fallo deja recepción registrada.

### T-RES-48 — Rollback de recepción aprobación e historial

- **Nivel:** servicio
- **Cubre:** `RN-TIP-PLE-05`
- **Caso:** Con condiciones válidas, provocar fallo de persistencia durante la operación de recepción/aprobación.
- **Esperado:** La transacción revierte fecha_recepcion_material, fecha_aprobacion y transición/historial; permanece SOLICITADA y conserva el formulario previo. No hay recepción independiente confirmada.

### T-RES-49 — Inicio de prestación sin entrega física

- **Nivel:** contrato
- **Cubre:** `RN-TIP-PLE-07`, `RN-RES-12`
- **Caso:** POST /api/reservas/{id}/ejecucion con {} sobre LISTA_ESPERA APROBADA. Repetir fuera de APROBADA y con recursos, incluso [].
- **Esperado:** 200 EN_EJECUCION con transición e historial, sin filas en reserva_recursos ni reserva_ejecucion_recursos. Estado inválido: 409 ESTADO_INCOMPATIBLE; recursos enviados: 422 VALIDACION. Ningún error altera estado.

### T-RES-50 — Finalización exige horas y no admite recursos

- **Nivel:** contrato
- **Cubre:** `RN-TIP-PLE-08`
- **Caso:** POST /api/reservas/{id}/finalizacion sobre LISTA_ESPERA EN_EJECUCION con horas_ejecucion=6.5; repetir con cero, horas ausentes, null, negativas, no numéricas o no finitas y con recursos. Probar además en SOLICITADA y APROBADA.
- **Esperado:** Horas válidas, incluido cero: 200 FINALIZADA con horas persistidas. Datos inválidos: 422 VALIDACION; estado incompatible: 409 ESTADO_INCOMPATIBLE. Sin filas de entrega/devolución. Fallos no persisten horas ni cierre parcialmente.

### T-RES-51 — Ciclo completo sin nuevas tablas ni estados

- **Nivel:** servicio
- **Cubre:** `RN-TIP-PLE-02`, `RN-TIP-PLE-03`, `RN-TIP-PLE-04`, `RN-TIP-PLE-05`, `RN-TIP-PLE-07`, `RN-TIP-PLE-08`, `RN-EST-05`
- **Caso:** Crear solicitud, cargar adjuntos, declarar viabilidad positiva, completar ambas partes, recibir material y aprobar, iniciar prestación y finalizar con horas.
- **Esperado:** Solo usa SOLICITADA, APROBADA, EN_EJECUCION y FINALIZADA y las estructuras existentes de lista de espera, formulario, adjuntos e historial. No crea estados de formulario/material ni asignaciones o ejecuciones físicas de recursos.

### T-RES-52 — Operaciones de lista de espera rechazan tipo o estado incorrectos

- **Nivel:** contrato
- **Cubre:** `RN-TIP-PLE-02`, `RN-TIP-PLE-03`, `RN-TIP-PLE-04`
- **Caso:** Invocar viabilidad, formulario y adjuntos sobre ESPACIO; escribirlos sobre LISTA_ESPERA APROBADA o terminada.
- **Esperado:** 409 TIPO_NO_ADMITIDO para otro tipo; 409 ESTADO_INCOMPATIBLE para escrituras fuera de SOLICITADA. Consultar los adjuntos históricos de una lista terminada sigue permitido dentro del ámbito autorizado.

---

## Edición y negociación — cierre documental del hallazgo 3

Pruebas especificadas; pendientes de implementación.

### T-RES-53 — Edición directa por tipo en solicitada

- **Nivel:** contrato
- **Cubre:** `RN-PRO-02`, `RN-PRO-06`
- **Caso:** PATCH /api/reservas/{id} como propietario sobre SOLICITADA con campos comunes y específicos válidos de cada tipo; enviar fragmentos de detalle y selecciones completas de asociaciones.
- **Esperado:** 200 con cambios resultantes y estado SOLICITADA, incluso con autoaprobación habilitada. Campos omitidos conservan valor. No se crean transiciones ficticias.

### T-RES-54 — Campos inmutables y acceso a edición

- **Nivel:** contrato
- **Cubre:** `RN-PRO-02`, `RN-PRO-03`, `RN-PRO-06`
- **Caso:** PATCH con tipo, unidad, titular, estado, evaluación, recepción, horas, snapshots o asistentes manuales; repetir como no propietario y en estados distintos de SOLICITADA.
- **Esperado:** 422 VALIDACION para campos prohibidos; 403 NO_AUTORIZADO o 404 NO_ENCONTRADO según ámbito para otro actor; 409 ESTADO_INCOMPATIBLE fuera de SOLICITADA. Sin modificaciones.

### T-RES-55 — Edición deriva asistentes apoyo y contexto válido

- **Nivel:** servicio
- **Cubre:** `RN-PRO-06`, `RN-RES-09`, `RN-TIP-PE-05`, `RN-CTX-04`
- **Caso:** Cambiar acompañantes, contexto, espacio y recursos; solicitar requiere_apoyo=false con un equipo que exige apoyo. Probar capacidad excedida, contexto incompatible y campos del espacio anterior incompatibles.
- **Esperado:** Asistentes corresponde a acompañantes y el apoyo obligatorio sigue true. Solo se aceptan datos resultantes válidos; un fallo conserva todas las selecciones y valores originales.

### T-RES-56 — Cambio de recursos conserva compromiso e historial

- **Nivel:** servicio
- **Cubre:** `RN-PRO-06`, `RN-DIS-06`, `RN-TIP-PE-28`
- **Caso:** Editar composición en SOLICITADA, retirando y añadiendo recursos; repetir con uno comprometido físicamente y con complementario de espacio en EN_EJECUCION.
- **Esperado:** Cambio válido conserva asignaciones retiradas y crea las nuevas, incluidos retiros automáticos permitidos e historial. Conflicto revierte toda la edición y no libera compromisos anteriores.

### T-RES-57 — Cambiar descripción invalida viabilidad y revisión

- **Nivel:** contrato
- **Cubre:** `RN-PRO-06`, `RN-TIP-PLE-09`, `RN-TIP-PLE-05`
- **Caso:** PATCH de descripcion_necesidad sobre LISTA_ESPERA SOLICITADA viable y revisada, con adjuntos y formulario; intentar después PUT de formulario y aprobación.
- **Esperado:** 200 SOLICITADA con viable y fecha_evaluacion_viabilidad null y revisión técnica invalidada; conserva adjuntos y parte del reservista. Formulario y aprobación responden 409 CONFLICTO hasta nueva viabilidad positiva y revisión requerida. No reabre una RECHAZADA.

### T-RES-58 — Descripción idéntica o edición fallida conserva evaluación

- **Nivel:** servicio
- **Cubre:** `RN-TIP-PLE-09`, `RN-PRO-06`
- **Caso:** Enviar la descripción actual; después intentar cambiarla junto con contexto inválido.
- **Esperado:** La primera operación no invalida evaluación. La segunda falla sin cambiar descripción, evaluación, formulario ni adjuntos.

### T-RES-59 — Aceptación de propuesta conserva aprobación

- **Nivel:** contrato
- **Cubre:** `RN-PROP-01`, `RN-PROP-05`, `RN-HOR-06`
- **Caso:** En ESPACIO y RECURSO_INTERNO APROBADA, crear propuesta técnica y aceptarla como propietario; repetir con contrapropuesta del propietario aceptada por Técnico, cumpliendo todas las reglas.
- **Esperado:** 200 con periodo nuevo y APROBADA, misma fecha_aprobacion, propuesta ACEPTADA con resolución. No se crea APROBADA→APROBADA ni nueva aprobación. SOLICITADA permanece SOLICITADA en el caso equivalente.

### T-RES-60 — Revalidación fallida no aplica el periodo ni resuelve propuesta

- **Nivel:** contrato
- **Cubre:** `RN-PROP-05`, `RN-DIS-05`
- **Caso:** Aceptar propuesta vigente de ESPACIO o RECURSO_INTERNO APROBADA cuando cambió horario, operatividad, capacidad, contexto o disponibilidad, o el nuevo periodo incumple antelación; provocar también fallo de persistencia.
- **Esperado:** Error de contrato correspondiente; estado APROBADA, periodo original, asignaciones y fecha_aprobacion intactos. Propuesta sigue VIGENTE sin resolución parcial. El fallo de persistencia revierte el conjunto.

### T-RES-61 — Rechazar una propuesta no revoca aprobación

- **Nivel:** contrato
- **Cubre:** `RN-PROP-06`
- **Caso:** POST rechazo de propuesta vigente de una reserva APROBADA; repetir para SOLICITADA.
- **Esperado:** 200; propuesta RECHAZADA. Se conserva periodo y estado previo, sin nueva solicitud ni transición de reserva.

### T-RES-62 — Negociación restringida al periodo y estados admitidos

- **Nivel:** contrato
- **Cubre:** `RN-PROP-01`, `RN-PROP-05`
- **Caso:** Proponer o aceptar fuera de SOLICITADA/APROBADA; enviar espacio o recursos en una propuesta; intentarlo en LISTA_ESPERA.
- **Esperado:** 409 ESTADO_INCOMPATIBLE por estado, 422 VALIDACION por campos ajenos al periodo/motivo y 409 TIPO_NO_ADMITIDO para lista de espera, sin cambios.

### T-RES-63 — Aceptación concurrente con cambio de estado

- **Nivel:** servicio
- **Cubre:** `RN-PROP-05`, `RN-DIS-05`
- **Caso:** Competir aceptación de periodo con cancelación o inicio de ejecución de la reserva.
- **Esperado:** No se confirma una reprogramación sobre un estado ya incompatible. Si el cambio de estado confirma primero, la aceptación se rechaza sin modificar periodo ni resolver propuesta. Si acepta primero, la transición posterior evalúa los datos vigentes.

---

## Transiciones horarias — hallazgo 4

### T-RES-64 — Espacio solicitado puede aprobarse durante la franja

- **Nivel:** contrato
- **Cubre:** `RN-TIP-PE-27`, `RN-HOR-06`
- **Caso:** Mantener ESPACIO en SOLICITADA después de hora_inicio; aprobarlo mediante POST /api/reservas/{id}/aprobacion antes de hora_fin con las condiciones vigentes satisfechas.
- **Esperado:** 200 EN_EJECUCION inmediatamente, con fecha_aprobacion e historial SOLICITADA→APROBADA→EN_EJECUCION en una operación. No exige entrega ni espera al proceso temporal; la antelación no se vuelve a exigir al aprobar.

### T-RES-65 — Espacio solicitado vence a cancelado

- **Nivel:** servicio
- **Cubre:** `RN-TIP-PE-25`, `RN-EST-04`
- **Caso:** Alcanzar hora_fin de ESPACIO todavía SOLICITADA.
- **Esperado:** Transición automática a CANCELADA con origen sistema, fecha y motivo de vencimiento sin aprobación. Conserva historia y no pasa a FINALIZADA.

### T-RES-66 — Espacio aprobado o en ejecución finaliza al vencer

- **Nivel:** servicio
- **Cubre:** `RN-TIP-PE-25`
- **Caso:** Alcanzar hora_fin con ESPACIO en APROBADA o EN_EJECUCION; repetir con RECHAZADA, CANCELADA y FINALIZADA.
- **Esperado:** Los dos primeros pasan a FINALIZADA; los estados terminales permanecen intactos, sin transiciones duplicadas.

### T-RES-67 — Aprobación de espacio en el límite final

- **Nivel:** contrato
- **Cubre:** `RN-TIP-PE-25`, `RN-TIP-PE-27`
- **Caso:** Intentar aprobar ESPACIO SOLICITADA cuando ahora es igual o posterior a hora_fin.
- **Esperado:** 409 ESTADO_INCOMPATIBLE; no se registra aprobación ni inicio. El proceso de vencimiento aplica SOLICITADA→CANCELADA, conservando el historial.

### T-RES-68 — Interno admite franjas sucesivas y rechaza solapamientos

- **Nivel:** base de datos
- **Cubre:** `RN-TIP-RI-03`, `RN-TIP-RI-04`, `RN-TIP-RI-13`, `RN-DIS-01`, `RN-DIS-05`
- **Caso:** Crear dos reservas RECURSO_INTERNO con el mismo recurso y franjas contiguas; repetir con franjas solapadas.
- **Esperado:** Ambas franjas contiguas se admiten sin esperar cierre de la primera. Las solapadas no pueden confirmar ambas. No se aplica unicidad de compromiso físico al interno.

### T-RES-69 — Interno en ejecución no admite cancelación

- **Nivel:** contrato
- **Cubre:** `RN-CAN-02`, `RN-TIP-RI-08`, `RN-TIP-RI-13`
- **Caso:** Tras el inicio automático de RECURSO_INTERNO, invocar POST /api/reservas/{id}/cancelacion sin que exista entrega física.
- **Esperado:** 409 ESTADO_INCOMPATIBLE sin cambio de estado. La denegación depende de EN_EJECUCION, no de entrega/devolución.

### T-RES-70 — Interno no retira complementarios como préstamo físico

- **Nivel:** servicio
- **Cubre:** `RN-TIP-RI-04`, `RN-TIP-PE-28`, `RN-DIS-06`
- **Caso:** Crear RECURSO_INTERNO con un recurso complementario previamente asignado a ESPACIO; probar franja distinta y franja solapada.
- **Esperado:** La franja distinta se admite y conserva el complementario; la solapada se rechaza conforme a disponibilidad temporal. No hay retiros con causa PRESTAMO_FISICO ni registros de entrega/devolución.


### T-RES-71 — Operaciones del Técnico sobre complementarios y adicionales

- **Nivel:** contrato
- **Cubre:** `RN-TIP-PE-21`, `RN-TIP-PE-22`, `RN-TIP-PE-23`, `RN-TIP-RI-10`, `RN-TIP-RI-11`, `RN-TIP-RI-12`
- **Caso:** En ESPACIO y RECURSO_INTERNO, repetir POST de adicionales y DELETE de una asociación vigente en SOLICITADA, APROBADA y EN_EJECUCION. Probar incorporación disponible, solapamiento y compromiso físico ajeno; revalidar disponibilidad de la composición resultante en el retiro.
- **Esperado:** POST válido devuelve 201; DELETE válido, 204 y elimina solo la asociación vigente, sin historial específico, causa, actor, fecha ni metadatos de retiro. Se conserva el principal de interno. Las incorporaciones en ejecución mantienen incorporado_at y validación hasta el fin previsto. Los conflictos devuelven 409 SOLAPAMIENTO o CONFLICTO según corresponda, sin cambios parciales.

### T-RES-72 — Límites de las operaciones genéricas de recursos

- **Nivel:** contrato
- **Cubre:** `RN-RES-12`, `RN-TIP-PE-21`, `RN-TIP-RI-10`
- **Caso:** Intentar POST/DELETE genéricos en campus, externo y lista de espera; en espacio e interno fuera de SOLICITADA, APROBADA y EN_EJECUCION; enviar rol PRINCIPAL en POST e intentar retirar el principal vigente de interno.
- **Esperado:** Tipos excluidos: 409 TIPO_NO_ADMITIDO. Estados excluidos: 409 ESTADO_INCOMPATIBLE. Rol no admitido en POST: 422 VALIDACION. Retiro del principal de interno: 409 CONFLICTO. Ningún rechazo modifica la reserva. La edición del reservista en SOLICITADA conserva su operación y validaciones propias.

### T-RES-73 — El retiro manual no altera el historial del retiro automático

- **Nivel:** servicio
- **Cubre:** `RN-TIP-PE-21`, `RN-TIP-RI-10`, `RN-TIP-PE-28`, `RN-CAN-05`, `RN-CAN-08`
- **Caso:** En una reserva con filas históricas de retiros automáticos, retirar manualmente otro complementario vigente. Comparar con un retiro automático por préstamo conforme a T-RES-34 a T-RES-40.
- **Esperado:** El retiro manual actualiza únicamente la composición vigente y no crea historial ni metadatos. Las filas históricas previas permanecen intactas. El retiro automático por préstamo conserva fila, instante, causa y reserva causante, y sigue siendo atómico; se mantienen también las obligaciones expresas de historial por deshabilitación.


### T-RES-74 — Generación de FGL 030 al aprobar

- **Nivel:** contrato
- **Cubre:** `RN-TIP-RC-07`, `RN-TIP-RE-07`
- **Caso:** Consultar orden y PDF de campus/externo SOLICITADA; aprobar y volver a consultar. Repetir con creación autoaprobada y con fallo al guardar la orden.
- **Esperado:** Antes de aprobación, 404 NO_ENCONTRADO sin generación por GET. Al aprobar existe una única orden con cabecera, actividades e ítems de los datos vigentes. La autoaprobación también la genera. Un fallo revierte aprobación y generación juntas.

### T-RES-75 — Orden y datos bloqueados tras aprobación

- **Nivel:** contrato
- **Cubre:** `RN-TIP-RC-07`, `RN-TIP-RE-07`, `RN-PROP-01`, `RN-PROP-05`, `RN-PRO-06`
- **Caso:** Tras aprobar campus/externo, intentar editar fechas, recursos y datos de salida mediante PATCH; crear propuesta o contrapropuesta y aceptar una propuesta creada en SOLICITADA. Consultar repetidamente orden y PDF tras cambios de datos del catálogo o perfil de origen.
- **Esperado:** Los intentos de edición y negociación responden 409 ESTADO_INCOMPATIBLE sin modificar reserva, propuesta ni orden. Las consultas conservan los snapshots originales, sin regeneración ni versiones. En SOLICITADA las ediciones y propuestas permitidas siguen disponibles antes de generar la orden. Las operaciones genéricas de recursos conservan sus exclusiones actuales.

### T-RES-76 — Proceso de salida y composición fija hasta devolución

- **Nivel:** servicio
- **Cubre:** `RN-TIP-RC-07`, `RN-TIP-RC-09`, `RN-TIP-RE-07`, `RN-TIP-RE-09`, `RN-CAN-05`, `RN-CAN-06`
- **Caso:** Para campus y externo, comprobar el retiro automático de un adicional deshabilitado antes del proceso de salida. Después recorrer aprobación, generación de FGL 030 y entrega física con inicio de ejecución como un mismo proceso; comprobar composición y orden hasta la devolución.
- **Esperado:** El retiro automático por deshabilitación solo aplica antes de ese proceso. La FGL refleja los recursos con los que se aprueba la salida; no se retiran recursos de ella después de generarla. La entrega registra EN_EJECUCION dentro del mismo proceso. Desde la salida, la composición queda fija hasta la devolución y la FGL permanece inmutable, sin regeneración ni versiones.


### T-RES-77 — Tipo no admitido al consultar la orden de salida

- **Nivel:** contrato
- **Cubre:** `RN-TIP-RC-07`, `RN-TIP-RE-07`
- **Caso:** Consultar GET /api/reservas/{id}/orden-salida y su variante .pdf para ESPACIO, RECURSO_INTERNO y LISTA_ESPERA.
- **Esperado:** 409 TIPO_NO_ADMITIDO sin generar orden ni modificar la reserva. CONFLICTO se conserva para las condiciones de negocio que lo especifican, no para tipos ajenos a la operación.
