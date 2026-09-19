# Contrato de API — Reservations

Contrato de comunicación del módulo `reservations`. Traduce a superficie HTTP los flujos de [user-flows.md](../../modules/reservations/user-flows.md), las reglas de [business-rules.md](../../modules/reservations/business-rules.md) y las entidades de [data-model.md](../../modules/reservations/data-model.md).

Aplica las [convenciones transversales](../README.md): formato, fechas, errores, autenticación, paginación y concurrencia. Aquí solo se documenta lo propio de reservas.

| Aspecto | Valor |
|---|---|
| Base path | `/api/reservas` |
| Identificadores | `id` entero de la reserva; `reserva_recurso_id` entero de la asignación |

Códigos de error propios, adicionales al catálogo común:

| HTTP | `codigo` | Uso |
|---|---|---|
| 409 | `SOLAPAMIENTO` | El espacio o recurso ya está ocupado en el periodo solicitado (`RN-TIP-PE-03`, `RN-TIP-RI-04`) |
| 409 | `ESTADO_INCOMPATIBLE` | La operación no aplica al estado actual de la reserva (`RN-EST`) |
| 409 | `FUERA_DE_HORARIO` | La fecha u horario quedan fuera del horario de atención de la unidad (`RN-HOR`) |
| 409 | `CAPACIDAD_EXCEDIDA` | Los asistentes superan la capacidad del espacio (`RN-TIP-PE-05`) |

---

## 1. Creación

### 1.1 `POST /api/reservas`

Crea una solicitud de reserva de cualquier tipo. Flujos por tipo: [UF-RES-01](../../modules/reservations/user-flows.md) para espacio, `UF-RES-02` para recurso interno, `UF-RES-03` para campus, `UF-RES-04` para externo y `UF-RES-05` para lista de espera. `UF-RES-08` cubre la creación por un Técnico.

El cuerpo tiene una parte común y un bloque `detalle` cuya forma depende del tipo:

```json
{
  "id_unidad": 7,
  "tipo_reserva": "ESPACIO",
  "observacion": "Requiere mesa adicional",
  "requiere_apoyo": false,
  "contexto": {
    "proyecto_id": 12,
    "semillero_id": null,
    "pasantia_id": null,
    "trabajo_grado_id": null,
    "actividad_institucional_id": null
  },
  "detalle": {
    "espacio_id": 3,
    "fecha": "2026-10-14",
    "hora_inicio": "08:00",
    "hora_fin": "12:00",
    "asistentes": 8
  },
  "recursos": [{ "recurso_id": 41, "rol": "ADICIONAL" }],
  "acompanantes": [1099, 1104],
  "campos_adicionales": [{ "campo_id": 5, "valor_texto": "Ensayo de tracción" }]
}
```

Forma de `detalle` por tipo:

| `tipo_reserva` | Campos de `detalle` |
|---|---|
| `ESPACIO` | `espacio_id`, `fecha`, `hora_inicio`, `hora_fin`, `asistentes` |
| `RECURSO_INTERNO` | `fecha`, `hora_inicio`, `hora_fin` |
| `RECURSO_CAMPUS`, `RECURSO_EXTERNO` | `fecha_salida`, `fecha_devolucion`, `razon_solicitud`, `lugar_nombre`, `lugar_direccion`, `nombre_actividad_evento` |
| `LISTA_ESPERA` | `descripcion_necesidad` |

`recursos` es obligatorio salvo en `ESPACIO`, donde es opcional y solo admite rol `ADICIONAL`. En `RECURSO_INTERNO`, `RECURSO_CAMPUS` y `RECURSO_EXTERNO` debe incluir exactamente un `PRINCIPAL` (`RN-RES-12`).

**`201 Created`**

```json
{
  "id": 1042,
  "estado": "SOLICITADA",
  "tipo_reserva": "ESPACIO",
  "id_unidad": 7,
  "requiere_apoyo": true,
  "created_at": "2026-09-19T14:03:11Z"
}
```

El estado inicial es `SOLICITADA` o `APROBADA` según la aprobación automática de la unidad (`RN-EST-01`, `RN-APR-03`). `requiere_apoyo` puede volver `true` aunque se haya enviado `false`, si algún equipo lo exige (`RN-RES-09`).

La cabecera, el detalle, las asignaciones, el contexto y los valores de campos se escriben en una única transacción: si algo falla, no queda nada escrito (`RN-INT-01` de administration).

**Errores:** `403 PERFIL_INICIAL_PENDIENTE` y `403 VINCULACION_REQUERIDA` (`RN-RES-11`), `409 SOLAPAMIENTO`, `409 FUERA_DE_HORARIO`, `409 CAPACIDAD_EXCEDIDA`, `409 CONFLICTO` si el tipo no está habilitado para el laboratorio (`RN-TIP-05`), `422 VALIDACION`.

### 1.2 `GET /api/reservas/tipos?id_unidad=7`

Tipos de reserva habilitados para un laboratorio (`RN-TIP-02`, `RN-TIP-03`).

**`200 OK`**

```json
{ "datos": [{ "codigo": "ESPACIO", "nombre": "Reserva por espacio" }] }
```

Si la lista trae un solo elemento, el cliente lo selecciona automáticamente (`RN-TIP-02`). Una lista vacía significa que el laboratorio no admite reservas (`RN-TIP-06`).

---

## 2. Consulta

### 2.1 `GET /api/reservas`

Listado paginado conforme a las [convenciones](../README.md). El ámbito lo determina el rol: un Usuario ve solo las suyas, un Técnico las de su unidad y un Administrador las de cualquier unidad.

Filtros: `estado`, `tipo_reserva`, `id_unidad`, `desde`, `hasta`, `espacio_id`, `recurso_id`. Orden admitido: `created_at`, `fecha`, `estado`.

**`200 OK`** — envolvente `datos` + `paginacion`, con una fila resumida por reserva.

### 2.2 `GET /api/reservas/{id}`

Detalle completo: cabecera, detalle del tipo, recursos asignados con su rol y estado, contexto con sus snapshots, acompañantes, campos adicionales, propuesta vigente si existe e historial de estados.

**Errores:** `404 NO_ENCONTRADO` si está fuera del ámbito del actor.

### 2.3 `GET /api/reservas/disponibilidad`

Consulta de disponibilidad. Flujo `UF-RES-19`.

Parámetros: `id_unidad` obligatorio, `espacio_id` o `recurso_id`, `desde` y `hasta`.

**`200 OK`**

```json
{
  "horario_unidad": { "dias_atencion": [1,2,3,4,5], "hora_apertura": "07:00", "hora_cierre": "19:00" },
  "franjas": [{ "fecha": "2026-10-14", "hora_inicio": "08:00", "hora_fin": "12:00", "disponible": false }]
}
```

El horario proviene de la unidad, no del espacio (`RN-ESP-DIS-02` de espacios). Solo bloquean franja las reservas en estado bloqueante con periodo definido (`RN-DIS-06`). Lo que el actor ve de cada franja ocupada depende de la configuración de visibilidad de la unidad (`RN-DIS`), pero el horario y la ocupación nunca se ocultan (`RN-DIS-07`).

Esta consulta **no reserva ni garantiza nada**: la disponibilidad se revalida al guardar.

---

## 3. Gestión por el Técnico

### 3.1 `POST /api/reservas/{id}/aprobacion`

Aprueba una reserva. Flujo `UF-RES-07`. Permiso: `reservas.administrar` sobre la unidad de la reserva.

```json
{ "observacion": "Aprobada con el equipo sustituido" }
```

**`200 OK`** — devuelve la reserva con `estado: "APROBADA"` y `fecha_aprobacion`.

Aprobar revalida disponibilidad, horario y capacidad (`RN-APR-06`). Para lista de espera, la aprobación exige además viabilidad y recepción del material (`RN-TIP-PLE-05`).

**Errores:** `409 ESTADO_INCOMPATIBLE`, `409 SOLAPAMIENTO`, `403 NO_AUTORIZADO`.

### 3.2 `POST /api/reservas/{id}/rechazo`

```json
{ "motivo": "El laboratorio estará en mantenimiento" }
```

`motivo` es obligatorio. **`200 OK`** con `estado: "RECHAZADA"`.

### 3.3 `POST /api/reservas/{id}/recursos`

Agrega recursos a una reserva ya creada. Flujos `UF-RES-09` y `UF-RES-10`. Permiso: `reservas.administrar` sobre la unidad de la reserva.

```json
{ "recursos": [{ "recurso_id": 55, "rol": "ADICIONAL" }] }
```

Admitido en `SOLICITADA`, `APROBADA` y `EN_EJECUCION` (`RN-TIP-PE-21`). En `EN_EJECUCION` la disponibilidad se valida desde el momento de la incorporación hasta la finalización prevista (`RN-TIP-PE-23`).

**`201 Created`** con las asignaciones creadas.

### 3.4 `DELETE /api/reservas/{id}/recursos/{reserva_recurso_id}`

Retira un recurso de la reserva. **`204 No Content`**. No borra la asignación: la marca como retirada y conserva el historial (`reserva_recursos.retirado_at`).

---

## 4. Propuestas de horario

### 4.1 `POST /api/reservas/{id}/propuestas`

Propone un horario alternativo. Flujo `UF-RES-15`. Lo usa el Técnico para proponer y el Usuario para contraproponer; `origen` se deriva del rol del actor, no del cuerpo.

```json
{
  "fecha_propuesta": "2026-10-16",
  "hora_inicio": "14:00",
  "hora_fin": "18:00",
  "motivo": "El espacio está ocupado esa mañana"
}
```

**`201 Created`** con la propuesta en estado `VIGENTE`. Si ya existía una vigente, queda `SUSTITUIDA` (`RN-PROP-07`). La reserva no cambia de estado (`RN-PROP-02`).

### 4.2 `POST /api/reservas/{id}/propuestas/vigente/aceptacion`

**`200 OK`** — revalida las reglas del tipo y reprograma la reserva (`RN-PROP-05`). Solo puede aceptar la contraparte de quien propuso (`RN-PROP-04`).

**Errores:** `409 SOLAPAMIENTO` si el horario propuesto dejó de estar disponible; la propuesta queda vigente y la reserva sin cambios.

### 4.3 `POST /api/reservas/{id}/propuestas/vigente/rechazo`

**`200 OK`** — la reserva permanece en `SOLICITADA` con su horario original (`RN-PROP-06`).

---

## 5. Ejecución

### 5.1 `POST /api/reservas/{id}/ejecucion`

Registra la entrega física y pasa la reserva a `EN_EJECUCION`. Flujo `UF-RES-13`. Permiso: `reservas.administrar` sobre la unidad de la reserva.

```json
{
  "recursos": [{ "reserva_recurso_id": 88, "observacion_entrega": "Entregado con estuche" }]
}
```

Escribe en `reserva_ejecucion_recursos` con la cuenta que entrega. **No** usa `asignado_at`, que representa asignación y no entrega.

**`200 OK`** con `estado: "EN_EJECUCION"`.

### 5.2 `POST /api/reservas/{id}/finalizacion`

Registra la devolución y pasa a `FINALIZADA`. Flujo `UF-RES-14`.

```json
{
  "recursos": [{ "reserva_recurso_id": 88, "observacion_devolucion": "Sin novedad" }],
  "horas_ejecucion": 6.5
}
```

`horas_ejecucion` es obligatorio solo para lista de espera (`RN-TIP-PLE-08`).

### 5.3 `POST /api/reservas/{id}/cancelacion`

Cancela la reserva. Flujo `UF-RES-11`. El Usuario puede cancelar las suyas; el Técnico las de su unidad.

```json
{ "motivo": "Ya no se requiere el laboratorio" }
```

Admitida mientras la ejecución no haya iniciado (`RN-CAN-02`). Libera la disponibilidad de inmediato (`RN-CAN-01`).

**Errores:** `409 ESTADO_INCOMPATIBLE` si la ejecución ya inició.

---

## 6. Orden de salida

### 6.1 `GET /api/reservas/{id}/orden-salida`

Datos prellenados del FGL 030 para reservas `RECURSO_CAMPUS` y `RECURSO_EXTERNO`. Devuelve la cabecera con sus snapshots, las actividades marcadas y los ítems técnicos, uno por recurso.

**Errores:** `409 CONFLICTO` si el tipo de reserva no genera orden de salida.

### 6.2 `GET /api/reservas/{id}/orden-salida.pdf`

Documento listo para imprimir. `Content-Type: application/pdf`.

Las firmas y los recibidos a satisfacción **no** se capturan: se diligencian a mano sobre el documento impreso (`RN-TIP-RC-14`, `RN-TIP-RE-14`).

### 6.3 `PUT /api/reservas/{id}/orden-salida/prorroga`

```json
{ "fecha_prorroga": "2026-11-02" }
```

**`200 OK`**. Registra la prórroga sin alterar `fecha_regreso_snapshot`, que conserva la fecha originalmente impresa (`RN-TIP-RC-15`).

---

## 7. Calendario y exportación

### 7.1 `GET /api/reservas/{id}/calendario.ics`

Archivo iCalendar de una reserva aprobada. Flujo `UF-RES-17`. `Content-Type: text/calendar`.

Las reservas con horario generan evento con hora; campus y externo generan evento de día completo; lista de espera no genera archivo (`RN-CAL-01`, `RN-CAL-02`).

**Errores:** `409 ESTADO_INCOMPATIBLE` si la reserva no está aprobada, `404 NO_ENCONTRADO` para lista de espera.

### 7.2 `GET /api/reservas/exportacion?formato=csv`

Exporta el listado con los filtros aplicados. Flujo `UF-RES-18`. Permiso: `reservas.exportar`.

`formato` admite `csv` y `excel`, conforme a `RN-EXP-05` de reports, propietario de esa decisión. El archivo contiene exactamente lo visible según el filtro y el ámbito del actor (`RN-REP-03`).

---

## 8. Lo que este contrato no expone

- **Cancelación automática por deshabilitación** (`UF-RES-12`): la dispara Resources al deshabilitar un elemento, no un endpoint de reservas.
- **Recordatorios** (`UF-RES-16`): los genera un proceso temporal, no una solicitud HTTP.
- **Visibilidad de disponibilidad** (`UF-RES-20`): es configuración de la unidad y pertenece al contrato de resources.
- **Auditoría e historial de estados**: se consultan dentro del detalle de la reserva; no se exponen endpoints de escritura sobre ellos.

## 9. Pendientes

1. El esquema exacto de los campos adicionales depende del catálogo de `espacio_campos.tipo`, registrado como **OQ-02**.
2. La garantía contra doble reserva concurrente está pendiente (**OQ-06**). Hasta resolverla, `409 SOLAPAMIENTO` describe el comportamiento esperado, no una garantía verificada.
3. El destino de `motivos_solicitud` está pendiente (**OQ-07**); este contrato no lo expone, porque el "por qué" de la reserva se resuelve con `contexto`.
