# Wireframes — Reports

## Alcance, fuentes y lectura

Tres wireframes de baja fidelidad, uno por cada pantalla de [screens.md](screens.md). Fuentes revisadas: [user-flow.md](user-flow.md), [screen-flow.md](screen-flow.md), [business-rules.md](business-rules.md), [data-model.md](data-model.md) y el [contrato API de Reports](../../contratos/reports/api-contract.md). Las variantes son estados de la misma pantalla, no pantallas nuevas.

Los bloques ASCII representan agrupación y orden de contenido, sin fijar dimensiones, estilos, tipografía, colores ni componentes. Para trasladarlos a Figma, conservar el identificador del wireframe y nombrar sus variantes por estado. Los nombres técnicos y referencias que aparecen fuera de los bloques son anotaciones de trazabilidad, no texto de interfaz.

Convenciones: las mismas de [wireframes.md de auth](../auth/wireframes.md) — `[campo: ______]` es una entrada; `[Acción]` es una acción; `(dato)` es información de solo lectura; `{mensaje}` es una región de respuesta, ausente cuando no hay mensaje; `→ destino` es una anotación de navegación, no un botón. `▇▇▇` representa una barra del gráfico.

### Estados y seguridad comunes

| Situación | Representación en la pantalla existente | Respaldo |
|---|---|---|
| Consulta en curso | Región de mensaje: «Consultando…» | Estados de screens.md |
| Sin permiso | «No tienes acceso a los reportes.» | `RN-AMB-03`, `SEC-AUTZ-01` de auth |
| Sesión no válida | Interrumpe la operación y conduce a `SCR-AUTH-01` de auth | `UF-AUTH-05`, `SEC-SES-07` de auth |
| Sin información | «Sin información para los criterios seleccionados.» | `RN-REP-05`, `RN-VIS-04` |

No se muestran SQL, trazas, variables de entorno, hashes, secretos ni tokens (`RN-PRI-02`).

## WF-REP-01 — Reporte de ocupación

Origen:

- SCR-REP-01.
- UF-REP-01 y UF-REP-02.

**Objetivo:** ver el uso de laboratorios, espacios y recursos, o las horas por proyecto o semillero. **Actor:** Técnico o Administrador.

**Información visible:** resumen de la consulta, tabla, gráfico de una medida, paginación. **Entradas:** dimensión, periodo, unidad, entidad. **Principal:** consultar. **Secundaria:** exportar.

### Estado principal

```text
+----------------------------------------------------------------+
| Reportes · Ocupación                                             |
|                                                                |
| Dimensión  [espacio v]   Unidad  [Laboratorio de Metrología v]  |
| Desde [2026-09-01]  Hasta [2026-09-30]   Espacio [Todos v]      |
| [Consultar]                                                     |
|                                                                |
| Espacios · 1 sep 2026 – 30 sep 2026 · Unidad: Metrología        |
| (Solo cuentan reservas aprobadas, en ejecución y finalizadas)   |
|                                                                |
| Ocupación por espacio                                           |
| Sala de ensayos   ▇▇▇▇▇▇▇▇▇▇▇▇▇▇  38.4 %                        |
| Sala de cómputo   ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇  61.0 %                |
| Sin porcentaje: Bodega (sin horario de atención definido)       |
|                                                                |
| Espacio          Horas reservadas  Horas disponibles  Ocupación |
| Sala de ensayos          84.5           220.0          38.4 %   |
| Sala de cómputo         134.2           220.0          61.0 %   |
| Bodega                    3.0             —              —      |
|                                                                |
| [Anterior]  Página 1 de 1 · 3 espacios  [Siguiente]             |
| Exportar: [CSV]  [Excel]                                        |
|                                                                |
| {Resultado}                                                     |
+----------------------------------------------------------------+
```

### Estados alternos

| Estado | Variación visual | Compatibilidad API |
|---|---|---|
| Sin consultar | Solo el formulario; sin tabla, gráfico ni exportar | — |
| Consultando | «Consultando…» | `GET /api/reportes/ocupacion`, §3.1 |
| Resultado | Resumen, gráfico, tabla y exportar | `200 OK` |
| Proyecto o semillero | Sin columna de porcentaje ni de horas disponibles; el gráfico usa horas reservadas | `dimension=proyecto`/`semillero` |
| Recurso | Columna de horas de uso; el gráfico usa porcentaje | `dimension=recurso` |
| Sin información | «Sin información para los criterios seleccionados.» sin gráfico ni exportar | `200 OK` con `datos: []` |
| Periodo inválido | Mensaje junto a las fechas | `422 VALIDACION` |
| Denegado | «No tienes acceso a los reportes.» | `403 NO_AUTORIZADO` |
| Exportando | «Preparando el archivo…» | `GET .../ocupacion/exportacion`, §4.1 |
| Filtros cambiados sin volver a consultar | El resultado sigue mostrando el resumen de su consulta; exportar usa esa consulta | `RN-EXP-02` |

### Navegación

- **Entrada:** destino «Reportes» de la navegación.
- **Salida correcta:** permanece; conserva los filtros consultados.
- **Errores:** en esta misma pantalla, sin revelar datos fuera del ámbito.

## WF-REP-02 — Reporte de solicitudes

Origen:

- SCR-REP-02.
- UF-REP-01 y UF-REP-02.

**Objetivo:** ver la demanda por estado y laboratorio. **Actor:** Técnico o Administrador.

**Información visible:** resumen, tabla con una columna por estado, paginación. **Entradas:** periodo (opcional), unidad. **Principal:** consultar. **Secundaria:** exportar.

### Estado principal

```text
+----------------------------------------------------------------+
| Reportes · Solicitudes                                          |
|                                                                |
| Desde [2026-09-01]  Hasta [2026-09-30]   Unidad [Todas v]       |
| [Consultar]                                                     |
|                                                                |
| Laboratorios · 1 sep 2026 – 30 sep 2026                         |
| (Incluye todos los estados: mide demanda, no uso)               |
|                                                                |
| Laboratorio   Solic. Aprob. Rechaz. En ejec. Finaliz. Cancel.   |
| Metrología      12     40      3       1       35       5       |
| Cómputo          4     18      0       0       20       2       |
|                                                                |
| [Anterior]  Página 1 de 1 · 2 laboratorios  [Siguiente]         |
| Exportar: [CSV]  [Excel]                                        |
|                                                                |
| {Resultado}                                                     |
+----------------------------------------------------------------+
```

### Estados alternos

| Estado | Variación visual | Compatibilidad API |
|---|---|---|
| Sin consultar | Solo el formulario | — |
| Consultando | «Consultando…» | `GET /api/reportes/solicitudes`, §3.2 |
| Resultado | Resumen, tabla y exportar | `200 OK` |
| Sin periodo | El resumen dice «todo lo registrado» | Periodo omitido |
| Periodo incompleto o invertido | Mensaje junto a las fechas | `422 VALIDACION` |
| Sin información | «Sin información para los criterios seleccionados.» | `200 OK` con `datos: []` |
| Denegado | «No tienes acceso a los reportes.» | `403 NO_AUTORIZADO` |

### Navegación

- **Entrada:** destino «Reportes» de la navegación.
- **Salida correcta:** permanece.
- **Errores:** en esta misma pantalla.

## WF-REP-03 — Horas de lista de espera

Origen:

- SCR-REP-03.
- UF-REP-01 y UF-REP-02.

**Objetivo:** ver reservas y horas de lista de espera por unidad. **Actor:** Técnico o Administrador.

**Información visible:** resumen, tabla, paginación. **Entradas:** periodo (obligatorio), unidad. **Principal:** consultar. **Secundaria:** exportar.

### Estado principal

```text
+----------------------------------------------------------------+
| Reportes · Lista de espera                                      |
|                                                                |
| Desde [2026-09-01]  Hasta [2026-09-30]   Unidad [Todas v]       |
| [Consultar]                                                     |
|                                                                |
| Lista de espera · 1 sep 2026 – 30 sep 2026                      |
| (Horas por unidad; no se atribuyen a ningún recurso)            |
|                                                                |
| Laboratorio      Reservas     Horas de ejecución                |
| Metrología           9              46.5                        |
|                                                                |
| [Anterior]  Página 1 de 1 · 1 laboratorio  [Siguiente]          |
| Exportar: [CSV]  [Excel]                                        |
|                                                                |
| {Resultado}                                                     |
+----------------------------------------------------------------+
```

### Estados alternos

| Estado | Variación visual | Compatibilidad API |
|---|---|---|
| Sin consultar | Solo el formulario | — |
| Consultando | «Consultando…» | `GET /api/reportes/lista-espera`, §3.3 |
| Resultado | Resumen, tabla y exportar | `200 OK` |
| Periodo ausente o invertido | Mensaje junto a las fechas | `422 VALIDACION` |
| Sin información | «Sin información para los criterios seleccionados.» | `200 OK` con `datos: []` |
| Denegado | «No tienes acceso a los reportes.» | `403 NO_AUTORIZADO` |

### Navegación

- **Entrada:** destino «Reportes» de la navegación.
- **Salida correcta:** permanece.
- **Errores:** en esta misma pantalla.

## WF-REP-04 — Panel de inicio

Origen:

- SCR-REP-04.
- UF-REP-01 (sin UF-REP-02: el inicio no se exporta).

**Objetivo:** ver el agregado del periodo y llegar a los reportes. **Actor:** los tres roles (el Usuario solo ve accesos, sin sección de reportes).

**Información visible:** periodo con su previo, tarjetas de indicadores, tabla de estados, serie por fecha, barras por laboratorio y recursos, mapa de calor, enlaces a las tres pantallas. **Entradas:** periodo y unidad. **Principal:** consultar. **Secundaria:** ninguna (sin exportar).

### Estado principal

```text
+----------------------------------------------------------------+
| Inicio                                                         |
|                                                                |
| Desde [2026-09-01]  Hasta [2026-09-30]  Unidad [Todas v]        |
| [Consultar]                                                    |
|                                                                |
| 1 sep 2026 – 30 sep 2026 · previo 2 ago – 31 ago 2026           |
|                                                                |
| (Reservas 96, antes 80) (Solicitadas 12)                       |
| (Horas 412.5, antes 350.0) (Ocupación 38.4 %, antes —)          |
|                                                                |
| Por estado                                                     |
| Solic. Aprob. Rechaz. En ejec. Finaliz. Cancel.                 |
|   12     40      3       1       35       5                     |
|                                                                |
| Reservas por día                                               |
| 1 sep ▇▇▇▇ 4 ···                                               |
|                                                                |
| Por laboratorio          Recursos más reservados               |
| Metrología 96 · 38.4 %   Osciloscopio 14 ···                   |
|                                                                |
| Mapa de calor (cantidad, 7–19)                                  |
| lun 9h ▇▇▇ 6 ···                                               |
|                                                                |
| Ver: [Ocupación] [Solicitudes] [Lista de espera]                |
|                                                                |
| {Resultado}                                                     |
+----------------------------------------------------------------+
```

### Estados alternos

| Estado | Variación visual | Compatibilidad API |
|---|---|---|
| Al entrar | Consulta automática del mes en curso, con los periodos rápidos a la vista; «Consultando…» mientras tanto | `GET /api/reportes/resumen`, §3.4 |
| Consultando | «Consultando…» | `GET /api/reportes/resumen`, §3.4 |
| Resultado | Indicadores, tablas, gráficos y enlaces | `200 OK` |
| Usuario sin permiso | Accesos a «Mis reservas» y «Nueva reserva», sin sección de reportes ni llamada al endpoint | — (`FE-41`) |
| Sin información | «Sin información para los criterios seleccionados.» sin gráficos | `200 OK` con secciones vacías |
| Periodo inválido | Mensaje junto a las fechas | `422 VALIDACION` |
| Denegado | «No tienes acceso a los reportes.» | `403 NO_AUTORIZADO` |

### Navegación

- **Entrada:** primer destino del menú tras el login (los tres roles).
- **Salida correcta:** permanece; los enlaces llevan a cada reporte.
- **Errores:** en esta misma pantalla, sin revelar datos fuera del ámbito.

## Dependencias y límites del cierre visual

| Pantallas | Información pendiente o límite | Tratamiento en los wireframes |
|---|---|---|
| Todas | Periodo prefijado | Se puede proponer el mes en curso como valor inicial; no es regla |
| WF-REP-01 | Gráfico de una página con más páginas | El gráfico dibuja la página a la vista y lo dice; no se pide otro conjunto |
| WF-REP-02 | Dimensión distinta de laboratorio | No se ofrece: el servidor solo admite `laboratorio` |
| Todas | Totales | Ausentes a propósito: sumarían solo la página a la vista |
| Todas | Retornos al abandonar no fijados por las fuentes | No se agregan botones de retorno o cancelación |

## Matriz de cobertura y estados

| Wireframe | Screen | User Flow | Estados representados |
|---|---|---|---|
| WF-REP-01 | SCR-REP-01 | UF-REP-01, UF-REP-02 | Sin consultar, consultando, resultado por dimensión, sin información, periodo inválido, denegado, exportando |
| WF-REP-02 | SCR-REP-02 | UF-REP-01, UF-REP-02 | Sin consultar, consultando, resultado, sin periodo, periodo inválido, sin información, denegado |
| WF-REP-03 | SCR-REP-03 | UF-REP-01, UF-REP-02 | Sin consultar, consultando, resultado, periodo inválido, sin información, denegado |
| WF-REP-04 | SCR-REP-04 | UF-REP-01 | Consulta automática al entrar, consultando, resultado, usuario sin permiso, sin información, periodo inválido, denegado |
