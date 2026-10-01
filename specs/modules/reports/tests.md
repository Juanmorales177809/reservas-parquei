# Pruebas — Reports

Qué debe verificarse en los informes de ocupación y uso. Convenciones en [testing.md](../../docs/testing.md).

El riesgo propio de este módulo es **el número que miente**: un cero donde debería haber un «no se puede calcular» se lee como un dato y se decide sobre él.

---

## Cálculo

### T-REP-01 — Sin horario definido no hay porcentaje

- **Nivel:** servicio
- **Cubre:** `RN-OCU-04`, `RN-OCU-05`
- **Caso:** se pide la ocupación de un elemento que no tiene horario de atención definido.
- **Esperado:** `porcentaje_ocupacion: null` junto a su total de horas. **Nunca un cero**, que se leería como «no se usó».

### T-REP-02 — Un resultado vacío no es un error

- **Nivel:** contrato
- **Cubre:** `RN-REP-05`
- **Caso:** se consulta un reporte con criterios que no coinciden con ningún registro.
- **Esperado:** `200` con un resultado vacío identificable, no un `404` ni un error.

### T-REP-03 — Los mismos datos dan el mismo resultado

- **Nivel:** servicio
- **Cubre:** `RN-REP-04`
- **Caso:** se ejecuta dos veces el mismo reporte sin que cambien los datos fuente.
- **Esperado:** resultados idénticos.

### T-REP-04 — Cada reporte incluye los estados que le corresponden

- **Nivel:** servicio
- **Cubre:** `RN-OCU-06`, `RN-EST-01`
- **Caso:** se comparan el reporte de solicitudes y el de ocupación sobre el mismo conjunto de reservas.
- **Esperado:** `solicitudes` incluye todos los estados; `ocupacion` solo los tres que representan uso real. Confundirlos infla la ocupación con reservas canceladas.

---

## Aislamiento

### T-REP-05 — Un reporte no modifica nada

- **Nivel:** servicio
- **Cubre:** `RN-REP-02`, `RN-REP-06`
- **Caso:** se generan todos los reportes y se compara el estado de reservas, recursos, usuarios y configuraciones antes y después.
- **Esperado:** nada cambió. La generación es consulta.

---

## Ámbito y visibilidad

### T-REP-06 — El Técnico solo ve su unidad

- **Nivel:** contrato
- **Cubre:** `RN-AMB-01`
- **Caso:** un Técnico pide un reporte de otra unidad y uno sin filtrar.
- **Esperado:** el primero se deniega; el segundo llega acotado a su unidad, **no vacío ni global**.

### T-REP-07 — El Administrador ve cualquier unidad

- **Nivel:** contrato
- **Cubre:** `RN-AMB-02`
- **Caso:** un Administrador pide reportes de varias unidades.
- **Esperado:** los obtiene todos.

### T-REP-08 — Los datos personales no se exponen por agregación

- **Nivel:** contrato
- **Cubre:** `RN-PRI-01`
- **Caso:** se consulta un reporte agregado por tipo de usuario o por semillero.
- **Esperado:** devuelve totales, no identidades individuales que el actor no podría consultar de otro modo.

---

## Filtros y exportación

### T-REP-09 — Un filtro desconocido no se ignora

- **Nivel:** contrato
- **Cubre:** `RN-FIL-01`
- **Caso:** se envía un filtro que no existe.
- **Esperado:** `400 SOLICITUD_INVALIDA`. Ignorarlo en silencio devolvería un reporte que no es el pedido, con aspecto de serlo.

### T-REP-10 — La exportación contiene lo mismo que la consulta

- **Nivel:** contrato
- **Cubre:** `RN-EXP-01`, `RN-EXP-05`
- **Caso:** se consulta un reporte con filtros y se exporta con los mismos.
- **Esperado:** el archivo contiene exactamente las filas de la consulta, con el mismo ámbito aplicado.

---

## Resumen para el inicio

### T-REP-11 — El resumen trae las seis secciones y los seis estados

- **Nivel:** contrato
- **Cubre:** `RN-EST-01`, `RN-OCU-05`
- **Caso:** se pide `GET /api/reportes/resumen` con un periodo válido y reservas en dos estados.
- **Esperado:** `200` con `resumen` (con su periodo previo), `indicadores`, `por_estado` con las seis claves siempre, `por_fecha`, `por_laboratorio`, `recursos_mas_reservados` y `ocupacion_dia_hora`.

### T-REP-12 — El Técnico solo ve su unidad en el resumen

- **Nivel:** contrato
- **Cubre:** `RN-AMB-01`, `RN-AMB-05`
- **Caso:** un Técnico pide el resumen sin filtro y con el `id_unidad` de otra unidad.
- **Esperado:** el primero llega acotado a su unidad; el segundo se deniega con `403 NO_AUTORIZADO`.

### T-REP-13 — El resumen exige un periodo válido

- **Nivel:** contrato
- **Cubre:** `RN-FIL-01`, `RN-FIL-02`
- **Caso:** se pide el resumen sin periodo y con `desde` posterior a `hasta`.
- **Esperado:** `422 VALIDACION` en ambos casos.

### T-REP-14 — Sin permiso no hay resumen

- **Nivel:** contrato
- **Cubre:** `RN-AMB-03`
- **Caso:** una cuenta sin `reportes.consultar` pide el resumen.
- **Esperado:** `403 NO_AUTORIZADO`, sin revelar datos.

### T-REP-15 — El resumen no inventa porcentajes

- **Nivel:** servicio
- **Cubre:** `RN-OCU-06`, `RN-CON-04`
- **Caso:** se pide el resumen de una unidad sin horario de atención definido y con una reserva de uso.
- **Esperado:** sus horas aparecen y `porcentaje_ocupacion` es `null`, nunca cero, también en los indicadores.

### T-REP-16 — Las horas de lista de espera finalizada suman en el resumen

- **Nivel:** servicio
- **Cubre:** `RN-OCU-05`
- **Caso:** se pide el resumen de un periodo que contiene la creación de una lista de espera `FINALIZADA` con `horas_ejecucion`, y de otro que no.
- **Esperado:** las horas aparecen en `indicadores.horas_reservadas` y en su laboratorio solo en el primer periodo, con la ocupación en 0 (las horas de lista no usan el horario); en otro estado no suman; `por_fecha`, `recursos_mas_reservados` y el mapa no cambian.
