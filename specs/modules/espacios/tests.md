# Pruebas — Espacios

Qué debe verificarse en espacios, sus recursos asociados y sus campos adicionales. Convenciones en [testing.md](../../docs/testing.md).

El riesgo propio de este módulo es **el formulario imposible**: un campo obligatorio sin opciones válidas deja al Usuario sin poder completar una reserva, y el defecto no se ve hasta que alguien lo intenta.

---

## Campos adicionales

### T-ESP-01 — Un campo de selección sin opciones no se habilita

- **Nivel:** contrato
- **Cubre:** `RN-ESP-CAM-02`, `RN-ESP-CAM-03`
- **Caso:** se habilita un campo de tipo `SELECCION` que no tiene ninguna opción habilitada.
- **Esperado:** `409 CAMPO_SIN_OPCIONES`. Tampoco se permite deshabilitar la última opción de un campo ya habilitado.

### T-ESP-02 — Los tipos de campo son un catálogo cerrado

- **Nivel:** base de datos
- **Cubre:** `RN-ESP-CAM-01`
- **Caso:** se intenta crear un campo adicional con un tipo fuera de los cinco definidos.
- **Esperado:** el CHECK lo rechaza. El catálogo no se amplía desde el código.

### T-ESP-03 — Los valores capturados sobreviven al cambio del campo

- **Nivel:** servicio
- **Cubre:** `RN-ESP-CAM-05`
- **Caso:** se deshabilita un campo adicional que ya tenía valores registrados en reservas.
- **Esperado:** las reservas conservan lo capturado. El campo deja de pedirse en las nuevas.

---

## Recursos asociados

### T-ESP-04 — No se asocia un recurso de otra unidad

- **Nivel:** contrato
- **Cubre:** `RN-ESP-REC-06`
- **Caso:** se asocia a un espacio un recurso que pertenece a otra unidad organizacional.
- **Esperado:** `409 UNIDAD_INCOMPATIBLE`.

### T-ESP-05 — Un recurso está asociado a un solo espacio a la vez

- **Nivel:** base de datos
- **Cubre:** `RN-ESP-REC-03`
- **Caso:** se asocia un recurso ya asociado y habilitado en otro espacio.
- **Esperado:** el índice único parcial lo rechaza. Liberarlo del primero permite asociarlo al segundo.

---

## Disponibilidad y horario

### T-ESP-06 — El horario no es de este módulo

- **Nivel:** contrato
- **Cubre:** `RN-ESP-DIS-02`
- **Caso:** se buscan endpoints de horario de atención bajo `/api/espacios`.
- **Esperado:** **no existe ninguno**. El horario es de la unidad y se configura en resources. Un espacio no tiene horario propio.

### T-ESP-07 — Un espacio deshabilitado no admite reservas nuevas

- **Nivel:** servicio
- **Cubre:** `RN-ESP-HAB-01`, `RN-ESP-HAB-02`
- **Caso:** se deshabilita un espacio con reservas históricas y se intenta reservarlo.
- **Esperado:** la reserva nueva se rechaza; la información y el historial permanecen intactos.

### T-ESP-08 — Deshabilitar con reservas futuras exige confirmación

- **Nivel:** contrato
- **Cubre:** `RN-ESP-HAB-05`
- **Caso:** se deshabilita un espacio con reservas futuras sin confirmar, y después confirmando.
- **Esperado:** sin confirmación, se advierte la cantidad que se cancelaría y **el espacio sigue habilitado con todas sus reservas intactas**. Con confirmación, se cancelan conforme a la regla de cancelación de reservations.

### T-ESP-09 — Las asociaciones históricas se conservan

- **Nivel:** servicio
- **Cubre:** `RN-ESP-HAB-04`
- **Caso:** se deshabilita un espacio con recursos asociados, campos adicionales y reservas pasadas.
- **Esperado:** las tres asociaciones siguen consultables.
