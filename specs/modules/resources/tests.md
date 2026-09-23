# Pruebas — Resources

Qué debe verificarse en laboratorios, equipos, mobiliarios y otros recursos. Convenciones en [testing.md](../../docs/testing.md).

Dos cosas concentran el riesgo: **el ámbito por unidad**, porque un Técnico que opera fuera de la suya es una fuga, y **la deshabilitación**, porque arrastra reservas futuras.

---

## Ámbito y permisos

### T-REC-01 — El Técnico administra solo su unidad

- **Nivel:** contrato
- **Cubre:** `RN-ROL-01`, `RN-ROL-02`
- **Caso:** un Técnico crea y edita mobiliario y otros recursos en su unidad, y lo intenta en una ajena.
- **Esperado:** procede en la propia; en la ajena recibe `403`, o `404` cuando revelar la existencia sea una fuga.

### T-REC-02 — El Administrador tiene alcance global

- **Nivel:** contrato
- **Cubre:** `RN-ROL-03`
- **Caso:** un Administrador opera sobre recursos de varias unidades distintas.
- **Esperado:** procede en todas, sin necesidad de una asignación por unidad.

### T-REC-03 — El Técnico edita equipos pero no los crea

- **Nivel:** contrato
- **Cubre:** `RN-EQP-09`
- **Caso:** un Técnico con `recursos.editar_equipos` edita un equipo de su unidad, intenta crear uno y cambiar la unidad responsable de otro.
- **Esperado:** la edición procede; la creación y el cambio de unidad se deniegan. Son de `recursos.administrar_equipos` y `recursos.reasignar_unidad`, ambos globales.

---

## Mobiliarios y otros recursos

### T-REC-04 — Cada elemento es un registro individual

- **Nivel:** base de datos
- **Cubre:** `RN-MOB-01`, `RN-OTR-01`
- **Caso:** se registran tres sillas idénticas y dos elementos de otros recursos iguales.
- **Esperado:** cinco filas independientes. **No hay cantidad**: la exclusividad temporal se evalúa por elemento, y un contador no se puede reservar.

### T-REC-05 — Todo elemento pertenece a una unidad

- **Nivel:** base de datos
- **Cubre:** `RN-MOB-02`, `RN-OTR-02`
- **Caso:** se intenta insertar un mobiliario y otro recurso sin `id_unidad`.
- **Esperado:** la base lo rechaza. Sin unidad no hay ámbito que comprobar.

### T-REC-06 — Solo lo habilitado entra en reservas nuevas

- **Nivel:** servicio
- **Cubre:** `RN-MOB-03`, `RN-OTR-03`
- **Caso:** se solicita una reserva que incluye un mobiliario y otro recurso con `habilitado = false`.
- **Esperado:** se rechaza por ambos.

### T-REC-07 — La exclusividad se evalúa por elemento

- **Nivel:** base de datos
- **Cubre:** `RN-MOB-04`, `RN-OTR-04`
- **Caso:** dos reservas solapadas piden el mismo mobiliario; otras dos piden mobiliarios distintos del mismo tipo.
- **Esperado:** las primeras colisionan, las segundas no.

### T-REC-08 — Deshabilitar conserva el historial

- **Nivel:** servicio
- **Cubre:** `RN-MOB-05`, `RN-OTR-05`
- **Caso:** se deshabilita un mobiliario y un elemento de otros recursos que participaron en reservas pasadas.
- **Esperado:** el registro, sus relaciones y su historial siguen ahí. Deshabilitar no es borrar.

---

## Deshabilitación con reservas futuras

### T-REC-09 — Deshabilitar un recurso principal avisa antes

- **Nivel:** contrato
- **Cubre:** `RN-DES-06`
- **Caso:** se deshabilita un recurso `PRINCIPAL` con reservas futuras sin enviar `confirmado`.
- **Esperado:** `409 CONFLICTO` con el número de reservas en `detalles`, y **ninguna reserva modificada**.

### T-REC-10 — Sin reservas futuras no hay advertencia

- **Nivel:** contrato
- **Cubre:** `RN-DES-07`
- **Caso:** se deshabilita un recurso sin reservas futuras, y otro que solo participa como `ADICIONAL`.
- **Esperado:** procede directamente en ambos casos, sin exigir confirmación.

---

## Configuración del laboratorio

### T-REC-11 — El cambio de horario conserva la versión anterior

- **Nivel:** servicio
- **Cubre:** `RN-LAB-04`, `RN-LAB-08`
- **Caso:** se cambia el horario de atención de una unidad que ya tenía uno.
- **Esperado:** la configuración anterior queda en el histórico con su vigencia cerrada, y no se solapan dos vigencias.

### T-REC-12 — Una unidad sin tipos habilitados no acepta reservas

- **Nivel:** servicio
- **Cubre:** `RN-LAB-03`
- **Caso:** se deshabilitan las reservas de una unidad que tiene reservas históricas.
- **Esperado:** no admite nuevas y el historial no se altera.

---

## Importación de equipos

### T-REC-13 — Las columnas de la planilla son las reales

- **Nivel:** servicio
- **Cubre:** `RN-IMP-06`
- **Caso:** se carga la planilla institucional con sus columnas `PLACA`, `DESCRIPCIÓN`, `CODIGO BODEGA`, `CENTRO DE COSTOS`, `FECHA INICIO` y `COSTO`.
- **Esperado:** se mapean a `placa`, `nombre_equipo`, `bodega`, `centro_costo` y `fecha_compra`. **`COSTO` no se persiste.** Un `nombre_equipo` de hasta 100 caracteres entra sin truncarse.

### T-REC-14 — La importación no deshabilita nada

- **Nivel:** servicio
- **Cubre:** `RN-IMP-05`
- **Caso:** se importa una planilla que omite equipos existentes.
- **Esperado:** los omitidos siguen habilitados. La ausencia en la planilla no es una orden de baja.
