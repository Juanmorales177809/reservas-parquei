# Especificación funcional de pantallas — Reports

## Alcance y fuentes

Derivado de [user-flow.md](user-flow.md), [business-rules.md](business-rules.md), [data-model.md](data-model.md), [overview.md](overview.md) y el [contrato de reports](../../contratos/reports/api-contract.md). La navegación se detalla en [screen-flow.md](screen-flow.md). Los identificadores corresponden a superficies funcionales; no prescriben páginas independientes, rutas HTTP ni componentes.

No se amplían reglas, datos, contratos ni flujos. Reports no escribe nada: toda superficie es una consulta (`RN-REP-02`). No se especifican estilos, disposición visual ni textos literales de error.

**Fuera de alcance de este documento:** la exportación del **listado de reservas en bruto** (pertenece a [reservations](../../contratos/reservations/api-contract.md) §8.2); la trazabilidad de operaciones (`RN-HIS-04`; el alcance real está en [data-model.md](data-model.md#alcance-de-la-trazabilidad-disponible)); las vistas materializadas y las exportaciones almacenadas (no están definidas).

## Criterios comunes

- **Actor y ámbito:** Técnico sobre su unidad, Administrador sobre cualquiera (`RN-AMB-01`, `RN-AMB-02`). Quien tiene alcance por unidad ve ofrecidas solo sus unidades (dato de la sesión); el servidor sigue siendo quien acota y el filtro nunca amplía el ámbito (`RN-AMB-03`, `RN-AMB-05`). Un Usuario no tiene reportes en su navegación; si llega por otra vía, la denegación aparece en la misma pantalla.
- **Selección, nunca texto libre:** unidad, espacio, recurso, proyecto y semillero se eligen **por nombre** de catálogos; el identificador no se teclea.
- **Consulta explícita:** se consulta con una acción, no al teclear cada filtro. El resultado corresponde a los filtros con que se pidió (`RN-VIS-01`); cambiar un filtro no cambia el resultado a la vista hasta volver a consultar.
- **Resumen visible:** todo resultado muestra la dimensión de agrupación, el periodo y los filtros aplicados (`RN-VIS-03`, `RN-EXP-04`).
- **Sin transformar lo devuelto:** las cifras se muestran tal como las entrega el servidor; no se redondean, suman, promedian ni estiman en la pantalla (`RN-VIS-02`, `RN-CON-04`). Por eso no hay filas de total: en un listado paginado, la suma de la página no es el total.
- **Vacío no es error:** sin registros se muestra la ausencia de información para los criterios elegidos, sin valores ficticios (`RN-REP-05`, `RN-VIS-04`).
- **Tabla siempre, gráfico solo donde la forma lo justifica:** la tabla es el dato y su alternativa accesible; el gráfico es una lectura complementaria (ver «Decisiones aplicadas»).

## SCR-REP-01 — Reporte de ocupación

- **User Flows de origen:** `UF-REP-01`, `UF-REP-02`.
- **Actores:** Técnico de la unidad; Administrador.
- **Objetivo:** ver cuánto se usan los laboratorios, espacios y recursos, o cuántas horas se atribuyen a un proyecto o semillero, en un periodo.
- **Precondiciones:** cuenta autenticada y activa con `reportes.consultar` y un ámbito vigente.
- **Información visible:** resumen (dimensión, periodo, filtros); tabla con una fila por elemento; gráfico de barras de una medida; paginación.
  - `laboratorio` y `espacio`: nombre, horas reservadas, horas disponibles, porcentaje de ocupación.
  - `recurso`: nombre, horas reservadas, horas de uso, porcentaje de ocupación.
  - `proyecto` y `semillero`: nombre, horas reservadas.
- **Entradas:** dimensión (una de cinco); periodo (`desde`, `hasta`, ambos obligatorios); unidad; el filtro por entidad que corresponde a la dimensión (espacio, recurso, proyecto o semillero).
- **Acciones:** consultar; paginar; exportar a CSV o Excel el resultado consultado.
- **Validaciones visibles:** periodo completo y `desde` no posterior a `hasta` (`RN-FIL-01`, `RN-FIL-02`); un elemento sin porcentaje calculable (sin horario de atención) muestra sus horas y **ningún** porcentaje (`RN-OCU-06`); solo cuentan las reservas `APROBADA`, `EN_EJECUCION` y `FINALIZADA` (`RN-OCU-04`), y así se indica junto al resultado.
- **Estados:** sin consultar, consultando, resultado, vacío, denegado, periodo inválido, error, exportando.
- **Errores y respuestas:** `422` por periodo ausente o invertido → corrección en el formulario; `403` → «no tienes acceso» sin revelar datos; `400` por dimensión no admitida no debería ocurrir (se elige de una lista cerrada).
- **Resultado/navegación:** permanece; conserva los filtros de la consulta.
- **Backend:** consulta módulos propietarios, resuelve dimensiones por identificadores (`RN-DIM-07`, `RN-CON-02`) y calcula con las versiones de horario vigentes en cada periodo (`RN-LAB-08` de resources).
- **RN/SEC relacionadas:** `RN-REP`, `RN-AMB`, `RN-DIM`, `RN-FIL`, `RN-OCU`, `RN-CTX`, `RN-HIS`, `RN-VIS`, `RN-EXP`, `RN-PRI`.
- **Dependencias:** `reservations`, `resources`, `espacios`, `researchs` (fuentes); `auth` (ámbito).

## SCR-REP-02 — Reporte de solicitudes

- **User Flows de origen:** `UF-REP-01`, `UF-REP-02`.
- **Actores:** Técnico de la unidad; Administrador.
- **Objetivo:** ver la demanda: cuántas reservas hay en cada estado, por laboratorio, en un periodo.
- **Precondiciones:** las de `SCR-REP-01`.
- **Información visible:** resumen; tabla con una fila por laboratorio y una columna por estado, en el orden del catálogo (solicitada, aprobada, rechazada, en ejecución, finalizada, cancelada); paginación. **Sin gráfico.**
- **Entradas:** periodo (`desde` y `hasta` juntos u omitidos ambos: sin periodo se cuenta todo lo registrado); unidad.
- **Acciones:** consultar; paginar; exportar.
- **Validaciones visibles:** incluye todos los estados, sin el filtro de ocupación, porque mide demanda y no uso (`RN-OCU-05`); el significado de cada estado es el de reservations y no se redefine (`RN-EST-01` a `RN-EST-04`).
- **Estados, errores, resultado/navegación, backend:** como `SCR-REP-01`.
- **RN/SEC relacionadas:** `RN-REP`, `RN-AMB`, `RN-FIL`, `RN-EST`, `RN-OCU-05`, `RN-VIS`, `RN-EXP`, `RN-PRI`.
- **Dependencias:** `reservations` (estados), `auth` (ámbito).

## SCR-REP-03 — Horas de lista de espera

- **User Flows de origen:** `UF-REP-01`, `UF-REP-02`.
- **Actores:** Técnico de la unidad; Administrador.
- **Objetivo:** ver cuántas reservas de lista de espera hubo y cuántas horas se emplearon, por unidad, en un periodo.
- **Precondiciones:** las de `SCR-REP-01`.
- **Información visible:** resumen; tabla con laboratorio, reservas y horas de ejecución; paginación. **Sin dimensión y sin gráfico.**
- **Entradas:** periodo (obligatorio, `desde` y `hasta`); unidad.
- **Acciones:** consultar; paginar; exportar.
- **Validaciones visibles:** las horas se agregan por unidad y nunca se atribuyen a un recurso (`RN-OCU-05`); proceden de las horas que el Técnico registra al finalizar cada reserva.
- **Estados, errores, resultado/navegación, backend:** como `SCR-REP-01`.
- **RN/SEC relacionadas:** `RN-REP`, `RN-AMB`, `RN-FIL`, `RN-OCU-05`, `RN-VIS`, `RN-EXP`, `RN-PRI`.
- **Dependencias:** `reservations` (`horas_ejecucion`), `auth` (ámbito).

## SCR-REP-04 — Panel de inicio

- **User Flows de origen:** `UF-REP-01` (la consulta agregada; sin `UF-REP-02`: el inicio no se exporta).
- **Actores:** los tres roles. Técnico y Administrador ven el resumen del periodo (`GET /api/reportes/resumen`, contrato §3.4); el Usuario ve accesos a sus reservas y nunca llama a ese endpoint (no ejerce ningún permiso, `FE-41`).
- **Objetivo:** ver de un vistazo la demanda y el uso del periodo, con su comparación contra el periodo previo, y llegar a los reportes de detalle.
- **Precondiciones:** cuenta autenticada y activa. La sección de reportes exige `reportes.consultar` con ámbito vigente; sin él solo se muestran los accesos.
- **Información visible:** periodo consultado con su previo; tarjetas de indicadores (reservas actual/previo, solicitadas, horas actual/previo, ocupación actual/previo con `null` sin horario); tabla de estados (seis columnas); serie por fecha; barras por laboratorio y recursos más reservados; mapa de calor día×hora (cantidad, grid 7–19); enlaces a las tres pantallas de detalle.
- **Entradas:** periodo (`desde`, `hasta`, ambos obligatorios) y unidad (quien tiene alcance por unidad ve ofrecida solo la suya). El periodo propone el mes calendario anterior y **se consulta solo al entrar**; cambiar un filtro exige volver a consultar.
- **Acciones:** consultar. Sin paginación (el resumen no pagina) y sin exportar.
- **Validaciones visibles:** periodo completo y `desde` no posterior a `hasta` (`RN-FIL-01`, `RN-FIL-02`); `porcentaje_ocupacion` ausente sin horario (`RN-OCU-06`); el mapa cuenta por asignación y solo dibuja celdas con valor.
- **Estados:** sin consultar, consultando, resultado, vacío, denegado, periodo inválido, error.
- **Errores y respuestas:** `422` por periodo ausente o invertido → corrección en el formulario; `403` → «no tienes acceso» sin revelar datos.
- **Resultado/navegación:** permanece; conserva los filtros de la consulta. Es el aterrizaje tras el login (los tres roles).
- **Backend:** una sola consulta agregada del ámbito del actor (`RN-AMB-01`, `RN-AMB-02`); sin cálculos propios.
- **RN/SEC relacionadas:** `RN-REP`, `RN-AMB`, `RN-FIL`, `RN-EST-01`, `RN-OCU-04`, `RN-OCU-05`, `RN-OCU-06`, `RN-VIS`, `RN-PRI`.
- **Dependencias:** `reservations`, `resources`, `espacios`, `researchs` (fuentes); `auth` (ámbito).
- **Gráficos:** los de barras/serie usan una sola medida y un solo color (`--color-primary-1`); el mapa de calor usa una sola tinta con intensidad; `por_estado` es tabla, no torta de seis colores (la paleta de tokens no da seis series distinguibles, ver «Decisiones aplicadas»).

## Cobertura de todos los User Flows

| User Flow revisado | Superficie |
|---|---|
| UF-REP-01 | SCR-REP-01, SCR-REP-02, SCR-REP-03 (un reporte por superficie: cambian los parámetros y las columnas), SCR-REP-04 (agregado del periodo) |
| UF-REP-02 | Acción «exportar» de cada una de las tres superficies (no tiene pantalla propia: parte del reporte que se tiene a la vista; el inicio no se exporta) |

## Ambigüedades y límites de las fuentes

1. **Periodo prefijado:** las fuentes exigen periodo pero no fijan uno por defecto. La pantalla puede proponer el mes en curso como valor inicial editable; es una decisión de presentación, no una regla, y la consulta sigue siendo explícita.
2. **`dimension` en solicitudes:** el contrato habla de «la dimensión seleccionada», pero solo `laboratorio` está implementado y documentado con ejemplo. Esta especificación no ofrece selector de dimensión en `SCR-REP-02`. Se corrige la redacción del contrato (§3.2) en lugar de dejar una capacidad que el servidor rechaza.
3. **Periodo en solicitudes:** a diferencia de los otros dos reportes, el periodo es opcional (todo o nada). No se hace obligatorio aquí: no lo exige ninguna fuente.
4. **Paginación y gráfico:** el gráfico representa **las filas de la página a la vista**, los mismos datos que la tabla (`RN-VIS-01`), y lo dice cuando hay más páginas. No se pide al servidor un conjunto distinto para dibujarlo.
5. **Destino tras exportar y retornos:** ninguna fuente los fija. No se agregan botones de retorno.
6. **Orden del listado:** el que entrega el servidor; no se ofrece otro.

## Decisiones aplicadas a las ambigüedades de prioridad alta

**Qué informe es gráfico y cuál es tabla** (exigencia de `FE-22`). Criterio: la forma la decide el trabajo del dato, y el color, que viene después, tiene que caber en los tokens de [design-tokens.md](../../ui/design-tokens.md) (`FE-23` prohíbe salirse de ellos).

| Informe | Representación | Por qué |
|---|---|---|
| Ocupación | **Tabla exportable + gráfico de barras horizontales de una sola medida y un solo color** | Comparar magnitudes entre elementos es el trabajo de una barra. Una sola serie: sin leyenda, con el valor rotulado en cada barra. Una sola medida: `porcentaje_ocupacion` en laboratorio, espacio y recurso; `horas_reservadas` en proyecto y semillero (que no tienen porcentaje). Mezclar horas y porcentajes en un eje sería engañoso |
| Solicitudes | **Solo tabla exportable** | Seis estados son seis categorías con identidad propia. La paleta de tokens no da seis colores distinguibles: al validarla con el script de la guía de visualización como paleta categórica falla en banda de luminosidad (el ámbar), en croma (el gris) y en contraste (turquesa y ámbar bajo 3:1). Inventar tonos fuera de los tokens está prohibido; seis columnas de cifras son legibles y exportables tal cual |
| Lista de espera | **Solo tabla exportable** | Tres cifras por unidad y ninguna comparación que una forma mejore. Las tarjetas con totales quedan descartadas: sumarían solo la página a la vista (`RN-VIS-02`) |

**El color del gráfico** es el verde de marca (`--color-primary-1`), validado con el script de la guía como serie única en claro (contraste ≥ 3:1 sobre la superficie clara) y en oscuro (≥ 3:1 sobre la oscura). Es la única tinta de datos; el texto, los ejes y las etiquetas usan los tokens de texto.

**Reglas del gráfico de ocupación**

- Título que nombra la medida y la agrupación: «Ocupación por espacio», «Horas reservadas por proyecto» (`RN-VIS-03`).
- Una barra por fila con valor calculable. Una fila **sin porcentaje** no dibuja barra —nunca una barra en cero (`RN-OCU-06`, `RN-VIS-04`)— y se enumera bajo el gráfico con el motivo («sin horario de atención definido»); sigue apareciendo en la tabla con sus horas.
- Valores rotulados tal como llegan, sin más redondeo que el del servidor (`RN-VIS-02`); el eje de porcentaje parte de 0 y no se trunca.
- Cada barra tiene su dato en un aviso al pasar o enfocar, y el gráfico no es la única vía: la tabla contiene todo lo que él muestra.
- Sin resultado, no se dibuja un gráfico vacío: se muestra la ausencia de información.

## Documentos relacionados

- [Flujos de usuario](user-flow.md): los dos flujos que originan estas pantallas.
- [Reglas de negocio](business-rules.md): `RN-REP`, `RN-AMB`, `RN-DIM`, `RN-FIL`, `RN-OCU`, `RN-VIS`, `RN-EXP`, `RN-PRI`.
- [Contrato de reports](../../contratos/reports/api-contract.md): la superficie HTTP.
- [Navegación funcional](screen-flow.md) y [wireframes](wireframes.md).
- [Tokens de diseño](../../ui/design-tokens.md): la paleta a la que se limita el gráfico.
