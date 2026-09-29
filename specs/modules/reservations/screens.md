# Especificación funcional de pantallas — Reservations

## Alcance y fuentes

Derivado exclusivamente de [user-flows.md](user-flows.md), [business-rules.md](business-rules.md), [data-model.md](data-model.md) y [overview.md](overview.md). La navegación se detalla en [screen-flow.md](screen-flow.md). Los identificadores corresponden a superficies funcionales; no prescriben páginas independientes, rutas HTTP ni componentes.

No se amplían reglas, datos, contratos ni flujos. Los estados de procesamiento describen la espera del resultado de una acción existente, no operaciones nuevas. No se especifican estilos, disposición visual, textos literales de error ni códigos API.

**Fuera de alcance de este documento:** la disponibilidad como garantía (se consulta en `UF-RES-19`, se confirma solo al guardar; la exclusión la aplica `DB-12` en el servidor); los flujos de sistema sin actor (`UF-RES-12`, `UF-RES-16`, `UF-RES-17`, `UF-RES-21`, `UF-RES-22`); la exportación de reportes (`UF-RES-18`, trasladado a `UF-REP-02` de reports); la visibilidad de disponibilidad (`UF-RES-20`, configuración de `resources`).

## Criterios comunes

- **Actor y ámbito:** el Usuario crea y consulta lo propio; el Técnico gestiona su unidad; el Administrador, cualquiera. Cada acción sensible se revalida contra el backend.
- **Backend:** valida propiedad, estado, campos inmutables, contexto, capacidad, horario, periodo y recursos en cada operación; una reserva `APROBADA` no se edita directo (solo reprogramación por propuesta en espacio/interno).
- **Estados:** los seis del catálogo, sin etapas internas por tipo salvo incorporadas expresamente.
- **Cinco estrategias, cinco flujos:** espacio, recurso interno, recurso de campus, recurso externo y lista de espera se especifican como flujos de pantalla distintos, no como una sola pantalla genérica con campos condicionales sin documentar.
- **Selección, nunca texto libre:** espacios, recursos, proyectos y semilleros se seleccionan de catálogos; pasantías y trabajos se crean con sus datos obligatorios.

## SCR-RES-01 — Solicitar una reserva

- **User Flows de origen:** `UF-RES-01`, `UF-RES-02`, `UF-RES-03`, `UF-RES-04`, `UF-RES-05`, `UF-RES-08`, `UF-RES-19`, `UF-RES-24`.
- **Actores:** Usuario (con actualización inicial completa y al menos una vinculación activa y válida, `RN-USR-08`, `RN-USR-11` de usuarios); Técnico en su unidad (nace `APROBADA`, salvo lista de espera).
- **Objetivo:** registrar una solicitud del tipo elegido con su detalle, contexto y asociaciones.
- **Precondiciones:** cuenta autenticada; tipo habilitado para el laboratorio; sin compromiso vigente ni entrega abierta incompatible (`RN-DIS-06`).
- **Información visible:** tipos ofrecidos; espacios con capacidad, horario heredado, asociados y campos; recursos habilitados y operativos; catálogos de contexto; disponibilidad consultada sin garantía de asignación.
- **Entradas:** tipo; espacio o recurso `PRINCIPAL` con adicionales; fechas y horarios o salida y devolución estimada; razón y lugar para campus/externo; contexto; acompañantes; campos obligatorios; descripción de necesidad para lista de espera.
- **Acciones:** consultar disponibilidad; guardar la solicitud; editar en `SOLICITADA` solo los campos del tipo.
- **Validaciones visibles:** reglas del tipo, capacidad, horario, antelación, unicidad de `PRINCIPAL`, contexto con vinculación vigente para `USUARIO`.
- **Estados:** captura por estrategia, validando, guardando, corrección requerida, solicitud registrada; edición con revalidación completa sin aprobar.
- **Errores y respuestas:** `409 SOLAPAMIENTO`, `409 FUERA_DE_HORARIO`, `409 CAPACIDAD_EXCEDIDA`, `409 CONFLICTO` (tipo no habilitado, compromiso o entrega incompatible, recurso de espacio en ejecución), `403 VINCULACION_REQUERIDA` o `403 PERFIL_INICIAL_PENDIENTE`, `422 VALIDACION`. Todo fallo revierte sin escrituras parciales.
- **Resultado/navegación:** permanece con la confirmación y el estado inicial (aprobación automática o `SOLICITADA`); el préstamo retira complementarios previos con causa y trazabilidad (`RN-TIP-PE-28`, `UF-RES-23`).
- **Backend:** crea cabecera, detalle, contexto y asociaciones en una transacción; registra el historial inicial.
- **RN/SEC relacionadas:** `RN-RES`, `RN-TIP`, `RN-CTX`, `RN-DIS-05`, `RN-DIS-06`, `RN-HOR-06`, `RN-TIP-PE-28`; `RN-USR-08`, `RN-USR-11` de usuarios.
- **Dependencias:** `usuarios` (perfil y vinculaciones), `espacios` (selector de `FE-14`), `recursos` (selector de `FE-12`), `investigacion` (contextos).

## SCR-RES-02 — Gestionar reservas (Técnico)

- **User Flows de origen:** `UF-RES-07`, `UF-RES-09`, `UF-RES-10`, `UF-RES-11`, `UF-RES-13`, `UF-RES-14`, `UF-RES-15`.
- **Actor:** Técnico de la unidad.
- **Objetivo:** aprobar, rechazar, agregar o retirar recursos, proponer periodos, ejecutar, finalizar y cancelar.
- **Precondiciones:** reserva en el estado que cada acción exige.
- **Información visible:** datos, usuario, tipo, elementos, disponibilidad, observaciones y propuestas con su estado.
- **Entradas:** motivo de rechazo o cancelación; recursos a agregar o retirar; periodo y motivo de propuesta; entregas y devoluciones físicas; horas de lista de espera.
- **Acciones:** aprobar (con recepción de material en lista de espera); rechazar con motivo; agregar o retirar recursos según tipo y estado (`PRINCIPAL` de interno no se retira); proponer, aceptar, rechazar o contraproponer periodo; ejecutar campus/externo/lista de espera; finalizar con devolución completa u horas; cancelar antes del inicio.
- **Validaciones visibles:** revalidación al aprobar; sin FGL no hay cambios de periodo en campus/externo; sin devolución completa no hay cierre; espacio/interno no se ejecutan ni finalizan a mano (`409 TIPO_NO_ADMITIDO`).
- **Estados:** revisión, aprobando, rechazando, gestionando recursos, negociando periodo, en ejecución, finalizando, cancelando.
- **Errores y respuestas:** `409 ESTADO_INCOMPATIBLE` fuera de estado; `409 SOLAPAMIENTO` si lo propuesto dejó de estar disponible; `409 TIPO_NO_ADMITIDO` en transiciones manuales de espacio/interno; la propuesta aceptada reprograma conservando estado y aprobación.
- **Resultado/navegación:** permanece con la confirmación; cada transición queda en el historial con actor y motivo.
- **Backend:** cada operación es transaccional; la entrega abre el rango del recurso hasta su devolución (`DB-11`).
- **RN/SEC relacionadas:** `RN-APR`, `RN-PROP`, `RN-TIP-PE-21`, `RN-TIP-PE-25`, `RN-TIP-PE-27`, `RN-TIP-RI-08`, `RN-TIP-RI-09`, `RN-TIP-RC-10`, `RN-TIP-RE-10`, `RN-CAN-02`.
- **Dependencias:** `notifications`, que comunica cada transición.

## SCR-RES-03 — Lista de espera

- **User Flows de origen:** `UF-RES-05` (más viabilidad, formulario, adjuntos y horas en sus flujos de preparación y cierre).
- **Actores:** Usuario (solicita, diligencia, adjunta); Técnico (evalúa, revisa, inicia, finaliza).
- **Objetivo:** solicitar sin fecha ni horario, completar el requerimiento técnico y cerrar con horas.
- **Precondiciones:** cuenta autenticada; para el Usuario, perfil y vinculación como en `SCR-RES-01`.
- **Información visible:** descripción de necesidad; viabilidad; formulario por partes; adjuntos; horas registradas.
- **Entradas:** descripción; viabilidad con motivo; datos de Usuario y de Técnico por partes; archivo técnico; horas de ejecución.
- **Acciones:** solicitar; declarar viabilidad (negativa rechaza en la misma transacción); diligenciar cada parte del formulario; adjuntar; ejecutar sin recursos; finalizar con horas finitas no negativas.
- **Validaciones visibles:** formulario por partes sin mezclar actores; adjunto con formato y tamaño admitidos; horas obligatorias al cerrar.
- **Estados:** solicitada, en evaluación, viable o rechazada, formulario parcial o revisado, en ejecución, finalizada con horas.
- **Errores y respuestas:** `409` sin viabilidad o formulario incompleto; `422` por horas ausentes o inválidas; nada parcial ante fallo.
- **Resultado/navegación:** permanece; las horas agregan por unidad en reports sin atribuirse a recursos.
- **Backend:** exige detalle y contexto compatibles con el tipo; registra historial y notifica.
- **RN/SEC relacionadas:** `RN-TIP-PLE`, `RN-PROP` (no admite propuestas).
- **Dependencias:** `notifications` (avisos de estado); sin recursos asociados.

## SCR-RES-04 — Consultar, calendario y órdenes

- **User Flows de origen:** `UF-RES-19` (disponibilidad consultada en `SCR-RES-01`, sin superficie propia adicional); detalle, `.ics` y FGL de solo lectura.
- **Actores:** Usuario (lo propio); Técnico (su unidad).
- **Objetivo:** ver el detalle con su historial, descargar el calendario y consultar la orden de salida.
- **Precondiciones:** reserva visible en el ámbito del actor.
- **Información visible:** cabecera, detalle por tipo, contexto con snapshots, asignaciones, historial con actor y motivo; orden FGL con snapshots, actividades e ítems; archivo `.ics` para espacio/interno aprobadas.
- **Entradas:** filtros y paginación del listado; ninguna escritura.
- **Acciones:** filtrar, paginar, ver detalle, descargar `.ics`, consultar orden y PDF.
- **Validaciones visibles:** fuera de ámbito no existe (`404`); `.ics` solo espacio/interno aprobadas; orden solo campus/externo generada.
- **Estados:** consultando, listado, detalle, descarga.
- **Errores y respuestas:** `404 NO_ENCONTRADO` fuera de ámbito; `409 TIPO_NO_ADMITIDO` donde no aplica; `409 ESTADO_INCOMPATIBLE` sin aprobación para `.ics`.
- **Resultado/navegación:** permanece; la orden nunca se regenera ni versiona desde aquí; las firmas son en papel.
- **Backend:** lectura con ámbito; snapshots inmutables; `.ics` generado sin sincronizar calendarios externos.
- **RN/SEC relacionadas:** `RN-CAL`, `RN-TIP-RC-11` a `RN-TIP-RC-14`, `RN-TIP-RE-11` a `RN-TIP-RE-14`, `RN-CTX-07`.
- **Dependencias:** ninguna escritura; `reports` exporta agregados, no este detalle.

## Cobertura de todos los User Flows

| User Flow revisado | Superficie |
|---|---|
| UF-RES-01 | SCR-RES-01 |
| UF-RES-02 | SCR-RES-01 |
| UF-RES-03 | SCR-RES-01 |
| UF-RES-04 | SCR-RES-01 |
| UF-RES-05 | SCR-RES-01, SCR-RES-03 |
| UF-RES-07 | SCR-RES-02 |
| UF-RES-08 | SCR-RES-01 |
| UF-RES-09 | SCR-RES-02 |
| UF-RES-10 | SCR-RES-02 |
| UF-RES-11 | SCR-RES-02 |
| UF-RES-12 | Sin pantalla propia: efecto automático del sistema |
| UF-RES-13 | SCR-RES-02 |
| UF-RES-14 | SCR-RES-02 |
| UF-RES-15 | SCR-RES-02 |
| UF-RES-16 | Sin pantalla propia: tarea del sistema (recordatorio) |
| UF-RES-17 | Sin pantalla propia: adjunto del correo de confirmación |
| UF-RES-18 | Trasladado a `UF-REP-02` de reports |
| UF-RES-19 | SCR-RES-01 (consulta previa, sin garantía) |
| UF-RES-20 | Sin pantalla propia: configuración de `resources` |
| UF-RES-21 | Sin pantalla propia: tarea del sistema (API-16) |
| UF-RES-22 | Sin pantalla propia: tarea del sistema (API-16) |
| UF-RES-23 | Sin pantalla propia: efecto atómico al crear el préstamo |
| UF-RES-24 | SCR-RES-01 |

## Ambigüedades y límites de las fuentes

1. **Presentación del periodo por estrategia:** cada tipo muestra fechas/horas o salida/devolución según su detalle; no se unifica en un formato común inventado.
2. **Destino tras guardar o confirmar:** ningún flujo lo fija. No se decide aquí.
3. **Retornos y cancelaciones:** ninguna fuente define botones de volver o cancelar en estas superficies; no se agregan.
4. **Orden de secciones en gestión:** la fuente no fija el orden de aprobación, recursos, propuestas y ejecución; no se prescribe uno.

## Decisiones aplicadas a las ambigüedades de prioridad alta

- Las cinco estrategias se especifican como flujos de pantalla distintos dentro de `SCR-RES-01` (solicitud) y `SCR-RES-02` (gestión), no como una pantalla genérica con campos condicionales sin documentar — exigencia explícita de la aceptación de `FE-18`.
- Los seis estados se cubren como estados de esas superficies, no como pantallas por estado.
- Los flujos de sistema quedan explícitamente sin superficie en vez de omitirse en silencio.

## Documentos relacionados

- [Flujos de usuario](user-flows.md): los veinticuatro flujos (uno trasladado) que originan estas pantallas.
- [Reglas de negocio](business-rules.md): `RN-RES`, `RN-TIP`, `RN-CTX`, `RN-DIS`, `RN-APR`, `RN-PROP`, `RN-CAN`, `RN-CAL`.
- [Modelo de datos](data-model.md): cabecera, detalles por tipo, asignaciones, contexto y órdenes.
- [Navegación funcional](screen-flow.md): cómo se conectan estas cuatro superficies entre sí y con usuarios, espacios, recursos, notifications y reports.
