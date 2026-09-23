# Pruebas — Notifications

Qué debe verificarse en eventos, bandeja, correos y preferencias. Convenciones en [testing.md](../../docs/testing.md).

El riesgo propio de este módulo es **que la entrega arrastre al negocio**: si un correo que no sale deshace una aprobación, el sistema se vuelve frágil por su parte menos fiable.

---

## Eventos y ocurrencias

### T-NOT-01 — La misma ocurrencia no se registra dos veces

- **Nivel:** base de datos
- **Cubre:** `RN-NOT-05`
- **Caso:** se registra dos veces el mismo evento sobre la misma entidad, con la misma clave de ocurrencia.
- **Esperado:** el índice único lo impide. **No se genera una segunda notificación**, aunque el productor reintente.

### T-NOT-02 — Los once eventos notificables existen

- **Nivel:** base de datos
- **Cubre:** `RN-EVT-01`, `RN-EVT-11`
- **Caso:** se consultan los tipos de evento cargados.
- **Esperado:** están los once, cada uno con su código, y una preferencia puede referenciarlos.

---

## Entrega de correo

### T-NOT-03 — Un fallo de entrega no invalida la operación

- **Nivel:** servicio
- **Cubre:** `RN-INT-04`
- **Caso:** se aprueba una reserva con el envío de correo fallando.
- **Esperado:** la reserva queda aprobada. El envío queda pendiente de reintento, no revierte nada.

### T-NOT-04 — Los reintentos se agotan y se detienen

- **Nivel:** servicio
- **Cubre:** `RN-COR-03`, `RN-COR-04`
- **Caso:** un envío falla repetidamente hasta agotar los reintentos previstos.
- **Esperado:** queda en `FALLIDO` y **deja de reintentarse**. No entra en un ciclo indefinido.

### T-NOT-05 — La consulta de reintento usa su índice

- **Nivel:** base de datos
- **Cubre:** `RN-COR-03`
- **Caso:** se examina el plan de la consulta que selecciona envíos pendientes por estado y próximo intento.
- **Esperado:** utiliza el índice `(estado, proximo_intento_at)`. Sin él, la tarea programada recorre la tabla entera en cada ciclo.

---

## Bandeja

### T-NOT-06 — Una notificación ajena no existe

- **Nivel:** contrato
- **Cubre:** `RN-CON-01`
- **Caso:** se consulta el detalle de una notificación de otra cuenta.
- **Esperado:** `404 NO_ENCONTRADO`. Un `403` revelaría que existe.

### T-NOT-07 — Marcar como leída no toca nada más

- **Nivel:** servicio
- **Cubre:** `RN-EST-04`
- **Caso:** se marca como leída la notificación de una reserva aprobada cuyo correo sigue pendiente.
- **Esperado:** cambia solo el estado de lectura. Ni la reserva ni el envío se alteran.

---

## Preferencias

### T-NOT-08 — La preferencia se aplica por tipo de evento

- **Nivel:** servicio
- **Cubre:** `RN-PREF-04`
- **Caso:** una cuenta desactiva un tipo de evento y ocurren dos eventos, el desactivado y otro.
- **Esperado:** solo se entrega el segundo.

### T-NOT-09 — Los correos de seguridad ignoran las preferencias

- **Nivel:** servicio
- **Cubre:** `RN-PREF-03`
- **Caso:** una cuenta desactiva todas sus preferencias y después recibe una invitación y una recuperación de contraseña.
- **Esperado:** ambos correos salen. **Una preferencia no puede dejar a alguien sin poder recuperar su cuenta.**
