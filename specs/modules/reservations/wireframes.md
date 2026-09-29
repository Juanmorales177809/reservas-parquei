# Wireframes — Reservations

## Alcance, fuentes y lectura

Cuatro wireframes de baja fidelidad, uno por cada pantalla de [screens.md](screens.md). Fuentes revisadas: [user-flows.md](user-flows.md), [screen-flow.md](screen-flow.md), [business-rules.md](business-rules.md), [data-model.md](data-model.md) y el [contrato API de Reservations](../../contratos/reservations/api-contract.md). Las variantes son estados de la misma pantalla, no pantallas nuevas.

Los bloques ASCII representan agrupación y orden de contenido, sin fijar dimensiones, estilos, tipografía, colores ni componentes. Para trasladarlos a Figma, conservar el identificador del wireframe y nombrar sus variantes por estado. Los nombres técnicos y referencias que aparecen fuera de los bloques son anotaciones de trazabilidad, no texto de interfaz.

Convenciones: las mismas de [wireframes.md de auth](../auth/wireframes.md) — `[campo: ______]` es una entrada; `[Acción]` es una acción; `(dato)` es información de solo lectura; `{mensaje}` es una región de respuesta, ausente cuando no hay mensaje; `→ destino` es una anotación de navegación, no un botón.

### Estados y seguridad comunes

| Situación | Representación en la pantalla existente | Respaldo |
|---|---|---|
| Procesamiento | Región de mensaje: «Procesando…», concretada por operación | Estados de screens.md |
| Validación de entradas | Mensaje junto al campo correspondiente; corrección mediante la acción existente | `422 VALIDACION`, contrato §1 |
| Conflicto de disponibilidad | Mensaje de no disponibilidad sin revelar datos ajenos | `409 SOLAPAMIENTO`, `409 CONFLICTO` |
| Operación no autorizada | «No se puede realizar esta operación.» | `SEC-AUTZ-01`, `SEC-AUTZ-02`, `SEC-AUTZ-04` de auth |
| Sesión no válida | Interrumpe la operación y conduce a `SCR-AUTH-01` de auth | `UF-AUTH-05`, `SEC-SES-07` de auth |
| Perfil o vinculación faltante | Orientación a `SCR-USR-01` o `SCR-USR-05` | `403 PERFIL_INICIAL_PENDIENTE`, `403 VINCULACION_REQUERIDA` |

No se muestran SQL, trazas, variables de entorno, hashes, secretos ni tokens (`SEC-INF-04` de auth, por la misma disciplina transversal).

## WF-RES-01 — Solicitar una reserva

Origen:

- SCR-RES-01.
- UF-RES-01, UF-RES-02, UF-RES-03, UF-RES-04, UF-RES-05, UF-RES-08, UF-RES-19, UF-RES-24.

**Objetivo:** registrar una solicitud del tipo elegido. **Actores:** Usuario o Técnico.

**Información visible:** tipos, espacios/recursos, contexto, disponibilidad consultada. **Entradas:** detalle por estrategia y contexto. **Principal:** guardar solicitud. **Secundarias:** consultar disponibilidad, editar en solicitada.

### Estado principal

```text
+--------------------------------------------------+
| Nueva reserva                                      |
|                                                  |
| Tipo       [espacio | interno | campus |        |
|              externo | lista de espera]             |
| Unidad             [seleccionar]                  |
|                                                  |
| (detalle según estrategia:                        |
|  espacio y franja / recurso y horario /           |
|  salida y devolución / necesidad)                 |
|                                                  |
| Contexto   [proyecto | semillero | ...]           |
| [Consultar disponibilidad]  {franjas}             |
|                                                  |
| [Guardar solicitud]                               |
|                                                  |
| {Resultado}                                       |
+--------------------------------------------------+
```

### Estados alternos

| Estado | Variación visual | Compatibilidad API |
|---|---|---|
| Consultando disponibilidad | «Consultando…» más franjas sin garantía | `GET /api/reservas/disponibilidad`, §3.3 |
| Guardando | «Guardando…» | `POST /api/reservas`, §2.1 |
| Conflicto o validación | Mensaje de corrección | `409` / `422` de §2.1 |
| Perfil/vinculación faltante | Orientación a usuarios | `403` de `RN-USR-08` / `RN-USR-11` |
| Editando solicitada | Campos del tipo, revalidación completa | `PATCH /api/reservas/{id}`, §2.8 |
| Registrada | Confirmación con estado inicial | `201 Created` |

### Navegación

- **Entrada:** navegación del módulo.
- **Salida correcta:** permanece con la confirmación.
- **Errores:** corrección en esta misma pantalla, sin escrituras parciales.

## WF-RES-02 — Gestionar reservas

Origen:

- SCR-RES-02.
- UF-RES-07, UF-RES-09, UF-RES-10, UF-RES-11, UF-RES-13, UF-RES-14, UF-RES-15.

**Objetivo:** aprobar, gestionar recursos, negociar periodo, ejecutar, finalizar y cancelar. **Actor:** Técnico.

**Información visible:** datos, usuario, tipo, elementos, propuestas, historial. **Entradas:** motivos, recursos, periodos, entregas, devoluciones, horas. **Principal:** la acción del estado (aprobar, ejecutar, finalizar…). **Secundarias:** las demás según tipo y estado.

### Estado principal

```text
+--------------------------------------------------+
| Reserva #___ (estado)                             |
| (datos, usuario, tipo, elementos, contexto)       |
|                                                  |
| Propuestas                                        |
| (vigente, historial)   [Proponer] [Aceptar]       |
|                        [Rechazar] [Contraproponer]|
|                                                  |
| Recursos      [Agregar]              [Retirar]    |
| Ejecución     [Iniciar] [Finalizar] [Cancelar]    |
| [Aprobar] [Rechazar]                              |
|                                                  |
| Historial (transiciones con actor y motivo)       |
|                                                  |
| {Resultado}                                       |
+--------------------------------------------------+
```

### Estados alternos

| Estado | Variación visual | Compatibilidad API |
|---|---|---|
| Revisando | Detalle completo antes de actuar | `GET /api/reservas/{id}`, §3.2 |
| Aprobando/rechazando | «Guardando…», motivo donde aplica | `POST .../aprobacion`, `POST .../rechazo`, §4.1/§4.2 |
| Negociando periodo | Vigente visible; aceptar revalida | `POST .../propuestas...`, §5.1–§5.3 |
| Ejecutando/finalizando | Entregas o devoluciones u horas | `POST .../ejecucion`, `POST .../finalizacion`, §6.1/§6.2 |
| Cancelando | Motivo y confirmación | `POST .../cancelacion`, §6.3 |
| Transición manual no admitida | Mensaje de no aplica | `409 TIPO_NO_ADMITIDO` |
| Fuera de estado | Mensaje de incompatibilidad | `409 ESTADO_INCOMPATIBLE` |

### Navegación

- **Entrada:** listado del módulo o aviso de notifications.
- **Salida correcta:** permanece con la confirmación y el historial actualizado.
- **Errores:** corrección en esta misma pantalla, sin cambios parciales.

## WF-RES-03 — Lista de espera

Origen:

- SCR-RES-03.
- UF-RES-05 y sus flujos de preparación y cierre.

**Objetivo:** solicitar sin fecha, completar el requerimiento y cerrar con horas. **Actores:** Usuario y Técnico.

**Información visible:** necesidad, viabilidad, formulario por partes, adjuntos, horas. **Entradas:** descripción, viabilidad, datos por parte, archivo, horas. **Principal:** según actor y estado (solicitar, evaluar, diligenciar, finalizar).

### Estado principal

```text
+--------------------------------------------------+
| Lista de espera                                   |
|                                                  |
| Necesidad          [________________________]    |
| Viabilidad         (evaluación del Técnico)       |
| Formulario         (parte del Usuario / Técnico) |
| Adjuntos           [elegir archivo]  [Subir]     |
| Horas de ejecución [________]                    |
| [Guardar / Evaluar / Finalizar]                   |
|                                                  |
| {Resultado}                                       |
+--------------------------------------------------+
```

### Estados alternos

| Estado | Variación visual | Compatibilidad API |
|---|---|---|
| Evaluando | «Guardando…» | `POST .../viabilidad`, §2.4 |
| Diligenciando | Una parte por petición | `PUT .../formulario`, §2.3 |
| Subiendo adjunto | «Subiendo…» | `POST .../adjuntos`, §2.5 |
| Finalizando | Horas finitas no negativas | `POST .../finalizacion`, §6.2 |
| Incompleto | Mensaje de lo que falta | `409` sin parciales |

### Navegación

- **Entrada:** navegación del módulo.
- **Salida correcta:** permanece con la confirmación.
- **Errores:** corrección en esta misma pantalla.

## WF-RES-04 — Consultar, calendario y órdenes

Origen:

- SCR-RES-04.
- Detalle, `.ics` y FGL de solo lectura.

**Objetivo:** ver, descargar calendario y consultar la orden. **Actores:** Usuario y Técnico.

**Información visible:** cabecera, detalle, contexto con snapshots, asignaciones, historial, orden, calendario. **Entradas:** filtros y paginación. **Principal:** ninguna acción propia; filtrar y descargar.

### Estado principal

```text
+--------------------------------------------------+
| Mis reservas / Reservas                           |
|                                                  |
| Filtros: estado, tipo, fechas                     |
| [Filtrar]                                         |
| (lista con estado)                                |
|                                                  |
| Detalle                                          |
| (cabecera, detalle, contexto, historial)          |
| [Descargar calendario]  [Ver orden de salida]     |
|                                                  |
+--------------------------------------------------+
```

### Estados alternos

| Estado | Variación visual | Compatibilidad API |
|---|---|---|
| Carga | «Cargando…» | `GET /api/reservas`, §3.1 |
| Detalle | Consolidado con historial | `GET /api/reservas/{id}`, §3.2 |
| Fuera de ámbito | Ausencia indistinguible | `404 NO_ENCONTRADO` |
| Calendario no admitido | Mensaje de no aplica | `409 TIPO_NO_ADMITIDO` / `409 ESTADO_INCOMPATIBLE` |
| Orden inexistente | Mensaje de aún no generada | `404 NO_ENCONTRADO` |

### Navegación

- **Entrada:** navegación del módulo o aviso de notifications.
- **Salida correcta:** permanece; descargas aparte.
- **Errores:** corrección o denegación en esta misma pantalla.

## Dependencias y límites del cierre visual

| Pantallas | Información pendiente o límite | Tratamiento en los wireframes |
|---|---|---|
| WF-RES-01 | Presentación del periodo por estrategia | Un bloque de detalle por estrategia, sin formato común inventado |
| WF-RES-02 | Orden de secciones de gestión | Sin orden prescrito; no se prescribe uno |
| WF-RES-01 | Destino tras guardar o confirmar | Se representa la confirmación; la navegación externa no se resuelve aquí |
| Todas | Retornos al abandonar no fijados por las fuentes | No se agregan botones de retorno o cancelación |

## Matriz de cobertura y estados

| Wireframe | Screen | User Flow | Estados representados |
|---|---|---|---|
| WF-RES-01 | SCR-RES-01 | UF-RES-01/02/03/04/05/08/19/24 | Consultando, guardando, conflicto/validación, perfil, editando, registrada |
| WF-RES-02 | SCR-RES-02 | UF-RES-07/09/10/11/13/14/15 | Revisando, aprobando, negociando, ejecutando, cancelando, no admitida |
| WF-RES-03 | SCR-RES-03 | UF-RES-05 + preparación/cierre | Evaluando, diligenciando, adjuntando, finalizando, incompleto |
| WF-RES-04 | SCR-RES-04 | Detalle/.ics/FGL | Carga, detalle, fuera de ámbito, calendario, orden |
