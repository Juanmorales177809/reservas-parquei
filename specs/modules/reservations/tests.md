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
- **Caso:** el proceso de transiciones automáticas está detenido y existe una reserva `APROBADA` cuya hora ya pasó.
- **Esperado:** se puede reservar un intervalo posterior que no se solapa. **El bloqueo pertenece al periodo, no al estado**, así que un estado sin actualizar no ocupa el recurso.

### T-RES-04 — Un recurso deshabilitado no entra en reservas nuevas

- **Nivel:** servicio
- **Cubre:** `RN-DIS-01`, `RN-REC-01`
- **Caso:** se solicita una reserva con un recurso deshabilitado después de haber sido reservado antes.
- **Esperado:** se rechaza, y las reservas anteriores que lo incluían no se alteran.

---

## Transiciones automáticas

### T-RES-05 — La reserva de espacio inicia y finaliza sola

- **Nivel:** servicio
- **Cubre:** `RN-TIP-PE-25`, `RN-TIP-PE-27`
- **Caso:** una reserva de tipo `ESPACIO` en estado `APROBADA` alcanza su `hora_inicio` y después su `hora_fin`.
- **Esperado:** pasa a `EN_EJECUCION` y luego a `FINALIZADA` sin intervención. El inicio automático **no registra asistencia**, y solo ocurre desde `APROBADA`: una `SOLICITADA` que alcanza su hora no arranca.

### T-RES-06 — El recurso interno nunca finaliza por tiempo

- **Nivel:** servicio
- **Cubre:** `RN-TIP-RI-13`
- **Caso:** una reserva `RECURSO_INTERNO` sobrepasa su hora de fin sin devolución registrada.
- **Esperado:** sigue abierta. Cerrarla exige la devolución, no el reloj.

### T-RES-07 — Las transiciones automáticas no se pueden forzar por la API

- **Nivel:** contrato
- **Cubre:** `RN-TIP-PE-25`, `RN-TIP-PE-27`
- **Caso:** se intenta finalizar e iniciar por API una reserva de tipo `ESPACIO`.
- **Esperado:** `409 CONFLICTO` al finalizar y `409 TIPO_NO_ADMITIDO` al iniciar. Ambas transiciones son del sistema.

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
- **Caso:** el reservista intenta cambiar fecha, horario, espacio y recursos con la reserva en `SOLICITADA`, `APROBADA`, `EN_EJECUCION`, `FINALIZADA` y `CANCELADA`.
- **Esperado:** solo procede en `SOLICITADA`, y los cambios que afectan disponibilidad se revalidan. En `APROBADA` la vía es la propuesta; las tres últimas no son editables.

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
