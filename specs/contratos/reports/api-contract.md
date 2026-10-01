# Contrato de API — Reports

Contrato de comunicación del módulo `reports`. Traduce a superficie HTTP los 2 flujos de [user-flow.md](../../modules/reports/user-flow.md), las reglas de [business-rules.md](../../modules/reports/business-rules.md) y las fuentes de consulta de [data-model.md](../../modules/reports/data-model.md).

---

## 1. Convenciones

Aplica las [convenciones transversales](../README.md). Aquí solo se documenta lo propio de reports.

| Aspecto | Valor |
|---|---|
| Base path | `/api/reportes` |
| Permiso administrativo | `reportes.consultar`, con el alcance de su asignación vigente: global permite consultar cualquier unidad; por unidad permite consultar únicamente esa unidad, aunque la cuenta tenga rol Administrador por otro permiso. El rol no concede el permiso ni amplía su alcance (`RN-AUTH-ROL-03`, `RN-AUTH-ROL-07` de auth) |
| Identificadores | `id_unidad`, `espacio_id`, `recurso_id`, `proyecto_id` y `semillero_id`, enteros de sus módulos propietarios |

**Este contrato no define códigos de error propios.** Todos los que usa pertenecen al [catálogo común](../README.md#catálogo-común-de-códigos).

**Todas las operaciones son de solo lectura.** Ninguna modifica el estado de las entidades que consulta (`RN-REP-02`), ni el estado de una reserva para alterar su inclusión en un resultado (`RN-EST-04`).

---

## 2. Parámetros comunes de un reporte

Los endpoints de la sección 3 comparten esta solicitud (§3.4 solo usa el periodo y `id_unidad`).

| Parámetro | Valor |
|---|---|
| `dimension` | `laboratorio`, `espacio`, `recurso`, `proyecto` o `semillero` (`RN-DIM-01` a `RN-DIM-05`) |
| `desde`, `hasta` | Periodo analizado, obligatorio cuando el reporte depende de información temporal (`RN-FIL-01`) |
| `id_unidad` | Limita a una unidad. Sin él, el reporte abarca el conjunto permitido por el ámbito del actor, no todo el sistema (`RN-FIL-05`) |
| `espacio_id`, `recurso_id`, `proyecto_id`, `semillero_id` | Filtros opcionales por entidad concreta |

**El ámbito no se negocia.** Los filtros no pueden ampliar la información autorizada para la cuenta (`RN-AMB-05`), y se evalúan con información de autorización vigente al momento de la consulta (`RN-AMB-03`). Poder consultar una entidad individual no implica poder consultar reportes agregados sobre ella (`RN-AMB-04`).

Las dimensiones se resuelven por los identificadores y relaciones persistentes de las fuentes, nunca por coincidencia de nombres (`RN-DIM-07`, `RN-CON-02`, `RN-CON-03`).

**Errores comunes a los tres:** `422 VALIDACION` si `desde` es posterior a `hasta` (`RN-FIL-02`) o si falta el periodo en un reporte temporal; `403 NO_AUTORIZADO` si la cuenta carece del permiso; `400 SOLICITUD_INVALIDA` si `dimension` no es uno de los cinco valores admitidos.

Un filtro que referencie una entidad inexistente o fuera del ámbito autorizado **no produce acceso a información no permitida** (`RN-FIL-04`): el reporte se resuelve dentro del ámbito del actor.

Cuando ningún registro cumple los criterios, la respuesta es un resultado vacío con su envolvente y su resumen. **No es un error** (`RN-REP-05`, `RN-VIS-04`).

---

## 3. Reportes

### 3.1 `GET /api/reportes/ocupacion`

Ocupación y uso por la dimensión seleccionada. Flujo `UF-REP-01`. Listado paginado con la envolvente completa. Permiso: `reportes.consultar`.

Cuenta como ocupación **únicamente** lo reservado en estado `APROBADA`, `EN_EJECUCION` y `FINALIZADA`. Las reservas `SOLICITADA`, `RECHAZADA` y `CANCELADA` se excluyen, porque no representan uso efectivo (`RN-OCU-04`).

**`200 OK`**

```json
{
  "resumen": {
    "dimension": "espacio",
    "desde": "2026-09-01",
    "hasta": "2026-09-30",
    "filtros": { "id_unidad": 7 }
  },
  "datos": [
    {
      "espacio_id": 3,
      "nombre": "Laboratorio de Metrología",
      "id_unidad": 7,
      "horas_reservadas": 84.5,
      "horas_disponibles": 220.0,
      "porcentaje_ocupacion": 38.4
    }
  ],
  "paginacion": { "pagina": 1, "tamano": 20, "total": 6, "paginas": 1 }
}
```

Los indicadores se calculan conforme a `RN-OCU-05`:

| Dimensión | Qué devuelve |
|---|---|
| `espacio` | Horas reservadas sobre las horas de atención de su unidad en el mismo periodo, tomadas de las versiones de horario vigentes entonces (`RN-LAB-08` de resources) |
| `recurso` | `porcentaje_ocupacion` sobre la duración del periodo analizado, y `horas_uso` con las horas acumuladas de uso efectivo de sus asignaciones |
| `laboratorio` | Los mismos indicadores agregados por unidad organizacional |
| `proyecto`, `semillero` | Horas reservadas atribuidas al contexto registrado en cada reserva |

**`porcentaje_ocupacion` es `null` cuando no puede calcularse.** Un elemento sin horario de atención definido devuelve el total de horas reservadas y ningún porcentaje: el sistema no lo estima (`RN-OCU-06`, `RN-CON-04`).

Un mismo elemento no se contabiliza más de una vez dentro de la misma unidad de análisis cuando corresponde al mismo registro de reserva y al mismo criterio de agrupación (`RN-OCU-03`).

**`horas_uso` no incluye horas de lista de espera**, que nunca se atribuyen a un recurso y se consultan en §3.3 (`RN-OCU-05`).

### 3.2 `GET /api/reportes/solicitudes`

Conteo de reservas agrupadas por estado, por laboratorio, para el periodo seleccionado. Flujo `UF-REP-01`. Listado paginado con la envolvente completa. Permiso: `reportes.consultar`.

`dimension` solo admite `laboratorio` (su valor por omisión); cualquier otra responde `400 SOLICITUD_INVALIDA`. A diferencia de los otros dos reportes, **el periodo es opcional**, pero `desde` y `hasta` viajan juntos o ninguno: sin periodo se cuenta todo lo registrado.

**No aplica el filtro de ocupación de `RN-OCU-04`**: incluye todos los estados, porque su objeto es la demanda, no el uso efectivo (`RN-OCU-05`).

**`200 OK`**

```json
{
  "resumen": { "dimension": "laboratorio", "desde": "2026-09-01", "hasta": "2026-09-30", "filtros": {} },
  "datos": [
    {
      "id_unidad": 7,
      "nombre": "Laboratorio de Metrología",
      "solicitada": 12,
      "aprobada": 40,
      "rechazada": 3,
      "en_ejecucion": 1,
      "finalizada": 35,
      "cancelada": 5
    }
  ],
  "paginacion": { "pagina": 1, "tamano": 20, "total": 6, "paginas": 1 }
}
```

Los estados son los del catálogo de reservations y **su significado no se redefine aquí** (`RN-EST-01`, `RN-EST-02`).

### 3.3 `GET /api/reportes/lista-espera`

Horas empleadas en reservas de tipo `LISTA_ESPERA`. Flujo `UF-REP-01`. Listado paginado con la envolvente completa. Permiso: `reportes.consultar`.

Las horas proceden de `horas_ejecucion`, que el Técnico registra al finalizar cada reserva (`RN-TIP-PLE-08` de reservations). **Se agregan por unidad y nunca se atribuyen a un recurso** (`RN-OCU-05`).

**`200 OK`**

```json
{
  "resumen": { "desde": "2026-09-01", "hasta": "2026-09-30", "filtros": { "id_unidad": 7 } },
  "datos": [{ "id_unidad": 7, "nombre": "Laboratorio de Metrología", "reservas": 9, "horas_ejecucion": 46.5 }],
  "paginacion": { "pagina": 1, "tamano": 20, "total": 1, "paginas": 1 }
}
```

Este endpoint no admite `dimension`: la agregación es siempre por unidad.

### 3.4 `GET /api/reportes/resumen`

Panel de inicio: los indicadores y distribuciones principales del periodo en una sola consulta (pantalla «Inicio», `FE-47`/`FE-48`, visible para los tres roles; la sección de reportes solo la consulta quien tiene el permiso). **No introduce reglas ni cálculos propios**: cada cifra es la que ya dan los reportes anteriores, agregada para el conjunto del ámbito del actor (`RN-AMB-01`, `RN-AMB-02`). Solo lectura. Permiso: `reportes.consultar`. Parámetros: `desde` y `hasta`, obligatorios (`RN-FIL-01`), e `id_unidad`, opcional (`RN-FIL-05`). Un periodo inválido responde igual que en §2. La pantalla «Inicio» del `USUARIO` no llama a este endpoint (no ejerce ningún permiso, `FE-41`): muestra accesos a sus reservas.

Cuentan como **demanda** todas las reservas cuya franja cruza el periodo, en cualquier estado (como `solicitudes`, `RN-OCU-05`). Cuentan como **uso** —horas, ocupación, mapa de calor y recursos más reservados— únicamente `APROBADA`, `EN_EJECUCION` y `FINALIZADA` (`RN-OCU-04`).

Las **horas de lista de espera** también suman en las horas, pero no en la ocupación: las `horas_ejecucion` de las reservas `LISTA_ESPERA` en `FINALIZADA` cuentan como horas de uso (`RN-OCU-05`, como en §3.3) y se atribuyen al periodo donde cae su fecha de creación, que es la única fecha que tienen. La ocupación sigue midiéndose solo con franjas sobre el horario de atención —las horas de lista no usan el horario y darían más del 100 %—. La lista de espera sigue sin franja con fecha (no aparece en `por_fecha`), sin recursos atribuidos (`recursos_mas_reservados`) y sin horas de reloj (`ocupacion_dia_hora`).

El **periodo previo** es el de igual duración que termina el día anterior a `desde`; sirve para comparar y se calcula con los mismos criterios.

**`200 OK`**

```json
{
  "resumen": {
    "desde": "2026-09-01", "hasta": "2026-09-30",
    "desde_previo": "2026-08-02", "hasta_previo": "2026-08-31",
    "filtros": { "id_unidad": 7 }
  },
  "indicadores": {
    "reservas": { "actual": 96, "previo": 80 },
    "solicitadas": 12,
    "horas_reservadas": { "actual": 412.5, "previo": 350.0 },
    "porcentaje_ocupacion": { "actual": 38.4, "previo": null }
  },
  "por_estado": { "solicitada": 12, "aprobada": 40, "rechazada": 3, "en_ejecucion": 1, "finalizada": 35, "cancelada": 5 },
  "por_fecha": [{ "fecha": "2026-09-01", "reservas": 4 }],
  "por_laboratorio": [
    { "id_unidad": 7, "nombre": "Laboratorio de Metrología", "reservas": 96, "horas_reservadas": 412.5, "porcentaje_ocupacion": 38.4 }
  ],
  "recursos_mas_reservados": [{ "recurso_id": 42, "nombre": "Osciloscopio", "reservas": 14 }],
  "ocupacion_dia_hora": [{ "dia": 1, "hora": 9, "cantidad": 6 }]
}
```

| Campo | Qué es |
|---|---|
| `indicadores.solicitadas` | Reservas del periodo todavía en `SOLICITADA`: lo que espera una decisión |
| `indicadores.horas_reservadas` | Horas de uso del periodo: franjas de espacio e interno, días de campus y externo, más `horas_ejecucion` de lista de espera `FINALIZADA` creada en el periodo |
| `indicadores.porcentaje_ocupacion` | Horas de uso sobre las horas de atención de las unidades del ámbito que tienen horario en el periodo. **`null` si ninguna lo tiene**, nunca un cero (`RN-OCU-06`) |
| `por_estado` | Los seis estados del catálogo de reservations, siempre presentes, con cero cuando no hay (`RN-EST-01`) |
| `por_fecha` | Reservas por día de su franja (la salida, en las de campus y externas), ordenadas por fecha; los días sin reservas se omiten. La lista de espera no tiene fecha y no aparece aquí |
| `por_laboratorio` | Una fila por unidad del ámbito, con su demanda, sus horas de uso y su ocupación (`null` sin horario) |
| `recursos_mas_reservados` | Hasta cinco recursos con más reservas de uso, de mayor a menor; en empate, por `recurso_id`. Cuenta por asignación (`reserva_recursos`): una reserva con N recursos suma N, como el panel anterior |
| `ocupacion_dia_hora` | Reservas de uso por día de la semana (`0` domingo a `6` sábado, el mismo criterio que `dias_atencion`) y hora del día (`7` a `19`, el grid del panel anterior); solo las horas dentro del horario de atención de cada laboratorio. Se omiten las celdas en cero; las horas fuera del grid cuentan en la ocupación global pero no se dibujan |

---

## 4. Exportación

### 4.1 `GET /api/reportes/{tipo}/exportacion`

Descarga el reporte consultado. Flujo `UF-REP-02`. Permiso: `reportes.consultar`.

`tipo` admite `ocupacion`, `solicitudes` y `lista-espera`. Acepta **los mismos parámetros** que el endpoint correspondiente de la sección 3, más `formato`.

| Parámetro | Valor |
|---|---|
| `formato` | `csv` o `excel` (`RN-EXP-05`). Este módulo es el propietario de esa definición |

El archivo contiene exactamente los mismos datos que devolvería la consulta con esos filtros (`RN-EXP-02`, `RN-VIS-01`) e incluye el periodo y los criterios principales utilizados, de modo que pueda interpretarse fuera del sistema (`RN-EXP-04`).

**`200 OK`** con `Content-Type: text/csv` o el del libro de Excel, y `Content-Disposition: attachment`. No lleva envolvente de paginación: exporta el resultado completo del ámbito consultado.

**El archivo no incluye información fuera del ámbito autorizado** (`RN-EXP-03`), ni credenciales, tokens, hashes u otra información técnica sensible (`RN-PRI-02`). Los datos personales se limitan a los necesarios para la función autorizada (`RN-PRI-03`).

El filtrado, el ordenamiento y la exportación **no pueden utilizarse para evadir las restricciones de autorización** (`RN-PRI-04`).

Un reporte sin datos se exporta como ausencia de información para los criterios seleccionados, no con valores ficticios (`RN-VIS-04`).

**Errores:** los comunes de la sección 2, más `400 SOLICITUD_INVALIDA` si `tipo` o `formato` no son admitidos.

---

## 5. Lo que este contrato no expone

- **Escritura de cualquier clase.** Reports consulta y presenta; los módulos propietarios registran y modifican (`RN-REP-06`, `RN-CON-01`).
- **Exportación del listado de reservas.** `GET /api/reservas/exportacion` pertenece a [reservations](../reservations/api-contract.md), porque exporta las reservas en bruto y no un reporte agregado. Comparte con este contrato las reglas `RN-EXP`.
- **Trazabilidad de operaciones.** `administration.auditoria` registra únicamente operaciones administrativas y el historial de una reserva se limita a sus transiciones de estado. Un reporte no puede atribuir a esas fuentes información que no registran (`RN-HIS-04`); el alcance real está en [data-model.md](../../modules/reports/data-model.md#alcance-de-la-trazabilidad-disponible).
- **Vistas materializadas, tablas de agregación y exportaciones almacenadas.** No están definidas. Si se requieren, deben especificarse antes sus columnas, fuentes y reglas de actualización.
- **Reclasificación histórica.** Una modificación posterior de la vinculación de un usuario con un proyecto o semillero no altera el contexto registrado en una reserva pasada (`RN-CTX-02`), y una reserva sin contexto no se asigna artificialmente a uno (`RN-CTX-03`).
