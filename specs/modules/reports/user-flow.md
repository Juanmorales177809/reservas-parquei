# User Flows — Reportes

Este documento describe los dos comportamientos de Reports que una persona inicia y conduce: consultar un reporte y descargarlo. Las reglas están en [business-rules.md](business-rules.md) y las fuentes de consulta en [data-model.md](data-model.md).

Reports no tiene tablas persistentes propias ni flujos de sistema: toda su actividad es una consulta iniciada por un actor autenticado, que no modifica ninguna entidad fuente (`RN-REP-02`).

---

## UF-REP-01 — Consultar un reporte de ocupación

**Actor principal:** Técnico de la unidad o Administrador.

**Precondiciones:**

- La cuenta está autenticada y activa.
- La cuenta tiene permiso de consulta de reportes con un ámbito vigente: el Técnico sobre su propia unidad, el Administrador sobre cualquiera (`RN-AMB-01`, `RN-AMB-02`).

**Flujo principal:**

1. El actor abre los reportes y elige la dimensión de análisis: laboratorio, espacio, recurso, proyecto o semillero (`RN-DIM-01` a `RN-DIM-05`).
2. Indica el periodo y los filtros que necesite. Cuando el reporte depende de información temporal, el periodo es obligatorio (`RN-FIL-01`).
3. El sistema valida el ámbito autorizado con información vigente al momento de la consulta (`RN-AMB-03`). Los filtros solicitados no pueden ampliarlo (`RN-AMB-05`); la ausencia de un filtro opcional se interpreta como el conjunto permitido por ese ámbito, no como acceso sin restricciones (`RN-FIL-05`).
4. El sistema consulta los módulos propietarios y calcula los indicadores conforme a `RN-OCU-05`, contabilizando como ocupación únicamente las reservas `APROBADA`, `EN_EJECUCION` y `FINALIZADA` (`RN-OCU-04`).
5. Las dimensiones se resuelven por los identificadores y relaciones persistentes de las fuentes, nunca por coincidencia de nombres (`RN-DIM-07`, `RN-CON-02`, `RN-CON-03`).
6. El sistema presenta el resultado con los mismos datos y filtros utilizados para generarlo, identificando el criterio de agrupación (`RN-VIS-01`, `RN-VIS-03`).
7. El resultado expone únicamente la información necesaria para el objetivo de la consulta (`RN-PRI-01`, `RN-PRI-03`).

**Flujos alternos:**

- Si la fecha inicial es posterior a la final, el sistema rechaza la consulta (`RN-FIL-02`).
- Si ningún registro cumple los criterios, el sistema devuelve un resultado vacío identificable; la ausencia de datos no es un error (`RN-REP-05`, `RN-VIS-04`).
- Si un filtro referencia una entidad inexistente o fuera del ámbito autorizado, la consulta no produce acceso a información no permitida (`RN-FIL-04`).
- Cuando el modelo no contiene la información necesaria para un porcentaje —por ejemplo, un elemento sin horario de atención definido—, el sistema devuelve el total de horas reservadas y no estima el porcentaje (`RN-OCU-06`, `RN-CON-04`).
- El contexto académico o investigativo se usa como dimensión y no altera la autorización de la consulta (`RN-CTX-04`). Una reserva sin proyecto ni semillero no se asigna artificialmente a uno (`RN-CTX-03`).

**Fuera de alcance:** la consulta no modifica ninguna entidad fuente ni el estado de una reserva para alterar su inclusión en el resultado (`RN-REP-02`, `RN-EST-04`). La trazabilidad disponible se limita a la descrita en [data-model.md](data-model.md#alcance-de-la-trazabilidad-disponible).

---

## UF-REP-02 — Exportar un reporte

**Actor principal:** Técnico de la unidad o Administrador.

**Precondiciones:**

- El actor consultó previamente un reporte conforme a `UF-REP-01`, con sus filtros aplicados.

**Flujo principal:**

1. El actor selecciona la opción de exportar sobre el reporte que tiene a la vista.
2. Elige uno de los formatos admitidos: CSV o Excel (`RN-EXP-05`).
3. El sistema genera el archivo con exactamente los mismos filtros y criterios del reporte consultado (`RN-EXP-02`).
4. El archivo incluye la información necesaria para identificar el periodo y los criterios principales utilizados (`RN-EXP-04`).
5. El sistema entrega el archivo para su descarga (`RN-EXP-01`).

**Flujos alternos:**

- La exportación no incluye información fuera del ámbito autorizado del actor (`RN-EXP-03`). El filtrado, el ordenamiento y la exportación no pueden utilizarse para evadir las restricciones de autorización (`RN-PRI-04`).
- El archivo no incluye credenciales, tokens, hashes ni otra información técnica sensible (`RN-PRI-02`).
- Un reporte sin datos se exporta como ausencia de información para los criterios seleccionados, no con valores ficticios (`RN-VIS-04`).

**Nota de propiedad.** Este flujo sustituye a `UF-RES-18`, que documentaba la exportación dentro de Reservations pese a citar `RN-EXP-05` de este módulo. La superficie HTTP correspondiente sigue expuesta en el [contrato de reservations](../../contratos/reservations/api-contract.md), porque exporta el listado de reservas; Reports no tiene contrato propio todavía (`OQ-08`).

---

## Separación de responsabilidades

- Reports consulta y presenta; los módulos propietarios registran y modifican (`RN-REP-06`, `RN-CON-01`).
- El significado de cada estado de reserva pertenece a Reservations y no se redefine aquí (`RN-EST-02`).
- El ámbito autorizado lo determina Auth mediante los permisos vigentes de la cuenta; Reports lo aplica, no lo define (`RN-AMB-03`).
- Los formatos de exportación admitidos son propiedad de este módulo; los demás lo referencian (`RN-EXP-05`).
