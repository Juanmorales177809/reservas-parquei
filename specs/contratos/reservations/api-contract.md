# Contrato de API — Reservations

Contrato de comunicación del módulo `reservations`. Traduce a superficie HTTP los flujos de [user-flows.md](../../modules/reservations/user-flows.md), las reglas de [business-rules.md](../../modules/reservations/business-rules.md) y las entidades de [data-model.md](../../modules/reservations/data-model.md).

---

## 1. Convenciones

Aplica las [convenciones transversales](../README.md): formato, fechas, errores, autenticación, paginación y concurrencia. Aquí solo se documenta lo propio de reservas.

| Aspecto | Valor |
|---|---|
| Base path | `/api/reservas` |
| Permiso administrativo | `reservas.administrar` sobre la unidad de la reserva para aprobar, rechazar, gestionar recursos, ejecutar y finalizar; `reservas.exportar` para la exportación. Crear y consultar las propias reservas no exige permiso administrativo |
| Identificadores | `id` entero de la reserva; `reserva_recurso_id` entero de la asignación |

Códigos de error propios y uso específico del código común `CONFLICTO`:

| HTTP | `codigo` | Uso |
|---|---|---|
| 409 | `CONFLICTO` | El recurso tiene otro compromiso físico vigente o una entrega abierta; aplica aunque el nuevo periodo no se solape (`RN-RES-14`, `RN-DIS-06`). También aplica si el recurso está asignado como complementario de un espacio `EN_EJECUCION` (`RN-TIP-PE-28`). Usa el código común sin redefinirlo |
| 409 | `SOLAPAMIENTO` | El espacio o recurso ya está ocupado en el periodo solicitado (`RN-TIP-PE-03`, `RN-TIP-RI-04`) |
| 409 | `ESTADO_INCOMPATIBLE` | La operación no aplica al estado actual de la reserva (`RN-EST`) |
| 409 | `FUERA_DE_HORARIO` | La fecha u horario quedan fuera del horario de atención de la unidad (`RN-HOR`) |
| 409 | `CAPACIDAD_EXCEDIDA` | Los asistentes superan la capacidad del espacio (`RN-TIP-PE-05`) |
| 409 | `TIPO_NO_ADMITIDO` | La operación no aplica al tipo de la reserva (`RN-TIP`, `RN-CAL-01`) |

---

## 2. Creación

### 2.1 `POST /api/reservas`

Crea una solicitud de reserva de cualquier tipo. Flujos por tipo: `UF-RES-01` para espacio, `UF-RES-02` para recurso interno, `UF-RES-03` para campus, `UF-RES-04` para externo y `UF-RES-05` para lista de espera. `UF-RES-08` cubre la creación por un Técnico.

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
    "asistentes": 2
  },
  "recursos": [{ "recurso_id": 41, "rol": "ADICIONAL" }],
  "acompanantes": [1099, 1104],
  "campos_adicionales": [{ "campo_id": 5, "valor_texto": "Ensayo de tracción" }]
}
```

`contexto` es obligatorio para todos los tipos de reserva, incluida `LISTA_ESPERA`. Puede contener como máximo un proyecto, un semillero, una pasantía y un trabajo de grado, o una actividad institucional independiente; no puede combinar ambos grupos. Si falta o está vacío, la API responde `422 VALIDACION`.

Forma de `detalle` por tipo:

Los campos de espacio, periodo, asistentes y ubicación se envían únicamente dentro de `detalle`; no forman parte de la cabecera común.

| `tipo_reserva` | Campos de `detalle` |
|---|---|
| `ESPACIO` | `espacio_id`, `fecha`, `hora_inicio`, `hora_fin`, `asistentes` |
| `RECURSO_INTERNO` | `fecha`, `hora_inicio`, `hora_fin` |
| `RECURSO_CAMPUS`, `RECURSO_EXTERNO` | `fecha_salida`, `fecha_devolucion_estimada`, `razon_solicitud`, `lugar_nombre`, `lugar_direccion`, `nombre_actividad_evento` |
| `LISTA_ESPERA` | `descripcion_necesidad` |

`recursos` es obligatorio en `RECURSO_INTERNO`, `RECURSO_CAMPUS` y `RECURSO_EXTERNO`, donde debe incluir exactamente un `PRINCIPAL` (`RN-RES-12`). En `ESPACIO` es opcional y solo admite rol `ADICIONAL`. En `LISTA_ESPERA` no se permite enviar `recursos`.

En una reserva por espacio, `asistentes` es opcional y por defecto es `0`. El valor debe coincidir con la cantidad de cuentas en `acompanantes` y no puede superar la capacidad del espacio. Las cuentas se seleccionan de la lista de vinculaciones activas del proyecto o semillero; no se ingresan manualmente.

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

El estado inicial es `SOLICITADA` o `APROBADA` según la aprobación automática de la unidad (`RN-EST-01`, `RN-APR-03`), excepto `LISTA_ESPERA`, que siempre inicia en `SOLICITADA` y sigue su flujo específico. `requiere_apoyo` puede volver `true` aunque se haya enviado `false`, si algún equipo lo exige (`RN-RES-09`).

En `RECURSO_CAMPUS` y `RECURSO_EXTERNO`, incorporar cada recurso (`PRINCIPAL` o `ADICIONAL`) establece su compromiso exclusivo desde la creación válida, incluso en `SOLICITADA`. Otro compromiso vigente impide crear la solicitud aunque las fechas sean distintas; no se devuelve `201` con una solicitud pendiente de liberación. La condición aplica igualmente al Técnico y a la autoaprobación. Solo después de terminar válidamente el compromiso anterior, con devolución física cuando corresponda, se admite evaluar otra solicitud verificando habilitación y operatividad (`RN-RES-14`, `RN-DIS-04`, `RN-DIS-06`).

Al crear un préstamo, las asignaciones complementarias previas del recurso en espacios `SOLICITADA` o `APROBADA` se retiran automáticamente con causa `PRESTAMO_FISICO` y referencia a la reserva de préstamo creada (`RN-TIP-PE-28`, `UF-RES-23`). No son otro compromiso físico ni producen por sí solas `409 SOLAPAMIENTO`. El préstamo, todos los retiros y su trazabilidad son atómicos; el espacio conserva su estado, franja y demás recursos. Si alguna asignación efectiva corresponde a un espacio `EN_EJECUCION`, responde `409 CONFLICTO` con `detalles: []`, sin crear el préstamo ni retirar asignaciones. No se exige confirmación ni una llamada previa a DELETE para este retiro automático.

En `RECURSO_INTERNO`, las asignaciones se controlan por franja horaria: no generan compromiso físico y se admiten periodos no solapados; la presencia de un compromiso físico ajeno de campus/externo sigue impidiendo incluir el recurso.

En `ESPACIO`, un complementario comprometido físicamente no puede incluirse, ni como `NO_DISPONIBLE`. Si se envía, se rechaza la operación completa; el cliente puede enviar una nueva solicitud del espacio sin ese recurso. La excepción temporal de `RN-TIP-PE-14` se conserva para complementarios sin compromiso físico.

Ejemplo de rechazo, tanto si la reserva anterior está `SOLICITADA` como si ya se entregó el recurso, aunque la nueva fecha sea posterior:

```json
{ "error": { "codigo": "CONFLICTO", "mensaje": "El recurso tiene un compromiso vigente y no puede incluirse en otra solicitud.", "detalles": [] } }
```

La cabecera, el detalle, las asignaciones, el contexto y los valores de campos se escriben en una única transacción: si algo falla, no queda nada escrito (`RN-INT-01` de administration).

**Errores:** `403 PERFIL_INICIAL_PENDIENTE` y `403 VINCULACION_REQUERIDA` (`RN-RES-11`), `409 SOLAPAMIENTO`, `409 FUERA_DE_HORARIO`, `409 CAPACIDAD_EXCEDIDA`, `409 CONFLICTO` si el tipo no está habilitado para el laboratorio (`RN-TIP-05`), si un recurso tiene un compromiso físico vigente o entrega abierta (`RN-DIS-06`), si el recurso es complementario de un espacio `EN_EJECUCION` (`RN-TIP-PE-28`), o si no cumple habilitación u operatividad (`RN-RES-05`, `RN-DIS-04`), `422 VALIDACION`.

### 2.2 `GET /api/reservas/tipos?id_unidad=7`

Tipos de reserva habilitados para un laboratorio. **Catálogo cerrado**: devuelve solo `datos`, sin paginación. Sustenta el paso de selección de tipo de `UF-RES-01` a `UF-RES-05` (`RN-TIP-02`, `RN-TIP-03`).

**`200 OK`**

```json
{ "datos": [{ "codigo": "ESPACIO", "nombre": "Reserva por espacio" }] }
```

Si la lista trae un solo elemento, el cliente lo selecciona automáticamente (`RN-TIP-02`). Una lista vacía significa que el laboratorio no admite reservas (`RN-TIP-06`).

### 2.3 `PUT /api/reservas/{id}/lista-espera/formulario`

Persiste el formulario de una reserva `LISTA_ESPERA` en `SOLICITADA` y con `viable = true` (`UF-RES-05`, `RN-TIP-PLE-03`, `RN-TIP-PLE-04`). El reservista autenticado puede escribir únicamente su parte de una reserva propia, sin permiso administrativo; el Técnico requiere `reservas.administrar` sobre la unidad para escribir la parte técnica. Un Técnico no sustituye la parte del reservista de una reserva ajena.

Parte del reservista:

```json
{ "datos_usuario": { "campo": "valor" } }
```

Parte técnica, una vez registrada la del reservista:

```json
{ "datos_tecnico": { "campo": "valor" } }
```

Cada petición contiene exactamente una de las dos partes, como objeto JSON no vacío. Los nombres internos son datos del formulario; no se define aquí un catálogo adicional. `diligenciado_at`, `revisado_por` y `revisado_at` se derivan de la sesión y del servidor, no del cuerpo. Si el reservista modifica su parte después de una revisión, se invalidan conjuntamente `datos_tecnico`, `revisado_por` y `revisado_at`; el Técnico debe revisarla y completar su parte de nuevo.

**`200 OK`** — devuelve `reserva_id`, ambas partes (la técnica puede ser null), `diligenciado_at`, `revisado_por` y `revisado_at`. La reserva permanece `SOLICITADA`. El formulario no tiene aprobación ni estado global propios. Cambiar la descripción mediante §2.8 invalida la viabilidad y la revisión técnica; el formulario queda bloqueado hasta nueva viabilidad positiva (`RN-TIP-PLE-09`).

**Errores:** `409 TIPO_NO_ADMITIDO` para otro tipo; `409 ESTADO_INCOMPATIBLE` fuera de `SOLICITADA`; `409 CONFLICTO` sin viabilidad positiva o si el Técnico intenta completar su parte sin la del reservista; `403 NO_AUTORIZADO` al escribir una parte no permitida; `404 NO_ENCONTRADO` fuera del ámbito visible; `422 VALIDACION` por cuerpo inválido, vacío o con ambas partes. Ningún error altera el formulario ni el estado.

### 2.4 `POST /api/reservas/{id}/lista-espera/viabilidad`

Acción explícita del Técnico, con permiso `reservas.administrar` sobre la unidad. Solo para `LISTA_ESPERA` en `SOLICITADA` (`UF-RES-05`, `RN-TIP-PLE-03`).

```json
{ "viable": true }
```

Una evaluación negativa exige motivo no vacío:

```json
{ "viable": false, "motivo": "El requerimiento no es técnicamente viable" }
```

**`200 OK`** — devuelve `id`, `viable`, `fecha_evaluacion_viabilidad` y `estado`. Si es viable, permanece `SOLICITADA` y se habilita el formulario. Si no, registra evaluación, motivo e historial y pasa a `RECHAZADA` en una sola transacción; conserva adjuntos y formulario existente. La fecha la registra el servidor. No hay estado global de viabilidad.

**Errores:** `409 TIPO_NO_ADMITIDO`, `409 ESTADO_INCOMPATIBLE`, `403 NO_AUTORIZADO`, `404 NO_ENCONTRADO` fuera del ámbito visible y `422 VALIDACION` si falta el booleano o el motivo requerido. Un fallo no deja una evaluación ni transición parcial.

### 2.5 `POST /api/reservas/{id}/lista-espera/adjuntos`

Carga un archivo técnico de una reserva propia `LISTA_ESPERA` en `SOLICITADA`, antes o después de evaluar viabilidad (`UF-RES-05`, `RN-TIP-PLE-02`). Permiso: reservista propietario, sin permiso administrativo; mantiene autenticación y CSRF. La reserva se crea primero mediante §2.1. Se pueden cargar varios archivos con peticiones sucesivas.

**Cuerpo:** excepción explícita al JSON, `multipart/form-data`, con `archivo` (un archivo) y `tipo_adjunto` (`PLANO`, `IMAGEN` o `DOCUMENTO`). Se admiten DWG, DXF, STEP y STL para `PLANO`; PNG y JPG para `IMAGEN`; PDF para `DOCUMENTO`, con los MIME definidos en [reserva_adjuntos](../../modules/reservations/data-model.md#reservasreserva_adjuntos). Cada archivo debe tener entre 1 y 5242880 bytes (5 MB). Se valida su contenido, no solo extensión o MIME declarado.

**`201 Created`** — metadatos del adjunto: `id`, `reserva_id`, `tipo_adjunto`, `nombre_original`, `content_type`, `size_bytes`, `uploaded_by` y `created_at`. No devuelve `storage_key`. No cambia el estado de la reserva.

**Errores:** `409 TIPO_NO_ADMITIDO`, `409 ESTADO_INCOMPATIBLE`, `403 NO_AUTORIZADO`, `404 NO_ENCONTRADO` fuera del ámbito visible y `422 VALIDACION` por archivo vacío, mayor de 5 MB, formato no admitido o contenido incompatible. Un fallo de almacenamiento responde `500 ERROR_INTERNO` sin datos internos. No se registra un adjunto incompleto ni se elimina la reserva por el fallo; el reservista puede reintentar la carga.

### 2.6 `GET /api/reservas/{id}/lista-espera/adjuntos`

Listado paginado de metadatos, con los campos de §2.5 y envolvente común. Permiso: acceso de lectura a la reserva (propietario o gestión dentro del ámbito autorizado). Disponible también después de terminar la reserva; conserva su historia.

**`200 OK`** — lista paginada, vacía si no hay archivos. **Errores:** `409 TIPO_NO_ADMITIDO` y `404 NO_ENCONTRADO` fuera del ámbito visible.

### 2.7 `GET /api/reservas/{id}/lista-espera/adjuntos/{adjunto_id}`

Descarga autenticada del archivo; mismo ámbito que §2.6. El adjunto debe pertenecer a esa reserva. **`200 OK`** con el contenido binario, su `Content-Type` validado y `Content-Disposition: attachment` con nombre seguro. No expone rutas internas ni URL pública de almacenamiento.

**Errores:** `409 TIPO_NO_ADMITIDO`; `404 NO_ENCONTRADO` si no existe la reserva o el adjunto en el ámbito visible, o si el adjunto pertenece a otra reserva.


### 2.8 `PATCH /api/reservas/{id}`

Edición directa por el reservista propietario, únicamente en `SOLICITADA` (`UF-RES-24`, `RN-PRO-02`, `RN-PRO-06`). Requiere sesión activa y CSRF; no exige permiso administrativo ni habilita editar reservas ajenas por esta ruta.

| Tipo | Campos editables |
|---|---|
| Todos | `observacion`, `contexto`, `requiere_apoyo` como solicitud voluntaria, sin desactivar apoyo obligatorio |
| `ESPACIO` | `detalle.espacio_id`, `detalle.fecha`, `detalle.hora_inicio`, `detalle.hora_fin`, `acompanantes`, `recursos` complementarios y `campos_adicionales` |
| `RECURSO_INTERNO` | `detalle.fecha`, `detalle.hora_inicio`, `detalle.hora_fin`, `recursos` con exactamente un principal |
| `RECURSO_CAMPUS`, `RECURSO_EXTERNO` | `detalle.fecha_salida`, `detalle.fecha_devolucion_estimada`, `detalle.razon_solicitud`, `detalle.lugar_nombre`, `detalle.lugar_direccion`, `detalle.nombre_actividad_evento` y `recursos` |
| `LISTA_ESPERA` | `detalle.descripcion_necesidad`; adjuntos y formulario se modifican únicamente por sus rutas específicas |

Ejemplo para un espacio:

```json
{
  "observacion": "Necesitamos otra franja",
  "detalle": { "hora_inicio": "10:00", "hora_fin": "12:00" },
  "acompanantes": [1099]
}
```

Los campos omitidos conservan su valor. `detalle` actualiza solo los campos enviados; `contexto`, `recursos`, `acompanantes` y `campos_adicionales`, cuando se envían, representan la selección completa resultante de ese bloque. Una colección vacía elimina su selección efectiva solo si el tipo lo permite y conserva la historia exigida; no elimina físicamente asignaciones retiradas. `contexto` no puede quedar vacío. NULL solo se admite para campos opcionales según creación/modelo, no sustituye colecciones. El cuerpo debe contener al menos un campo editable. Se validan los datos resultantes completos, no únicamente el fragmento enviado.

`detalle.asistentes` no se edita: se calcula a partir de `acompanantes`. El apoyo efectivo se recalcula; enviar false no desactiva el requerido por equipos. No se admiten `tipo_reserva`, `tipo_reserva_id`, `id_unidad`, titular, estado, viabilidad, aprobación, recepción, ejecución, horas, historial ni snapshots. Los campos no aplicables al tipo se rechazan. Cambiar espacio exige campos y acompañantes válidos para el nuevo espacio; cambiar recursos mantiene cardinalidad, compromiso único e historial y ejecuta los retiros de `UF-RES-23` atómicamente cuando corresponda.

En lista de espera, cambiar efectivamente la descripción tras una evaluación limpia `viable` y `fecha_evaluacion_viabilidad`; conserva adjuntos y parte del reservista del formulario, pero limpia parte técnica y revisión (`RN-TIP-PLE-09`). Permanece `SOLICITADA` y requiere nueva viabilidad positiva antes de habilitar formulario o aprobar. Enviar la misma descripción no invalida nada.

**`200 OK`** — detalle actualizado, con `estado: "SOLICITADA"`, asistentes/apoyo efectivos y, para lista de espera, evaluación y revisión resultantes. No activa autoaprobación. Ningún cambio directo procede en `APROBADA`: solo espacio e interno pueden negociar el periodo por §5; campus y externo tienen bloqueados los datos de la FGL 030.

**Errores:** `404 NO_ENCONTRADO` si la reserva no existe en el ámbito visible; `403 NO_AUTORIZADO` si el actor no es propietario; `409 ESTADO_INCOMPATIBLE` fuera de `SOLICITADA`; `422 VALIDACION` por campos inmutables, desconocidos, no aplicables, cuerpo vacío o datos inválidos; `409 SOLAPAMIENTO`, `409 FUERA_DE_HORARIO`, `409 CAPACIDAD_EXCEDIDA` o `409 CONFLICTO` según las reglas de creación y de disponibilidad aplicables. La edición revalida todas las condiciones correspondientes; reprogramar exige antelación (`RN-HOR-06`). Si falla, se conservan íntegros reserva, asociaciones, retiros, snapshots, viabilidad y formulario.

---

## 3. Consulta

### 3.1 `GET /api/reservas`

Listado paginado conforme a las [convenciones](../README.md). Sustenta la consulta de `UF-RES-19` y la revisión previa a `UF-RES-07`. El ámbito lo determina el rol: un Usuario ve solo las suyas, un Técnico las de su unidad y un Administrador las de cualquier unidad.

Filtros: `estado`, `tipo_reserva`, `id_unidad`, `desde`, `hasta`, `espacio_id`, `recurso_id`. Orden admitido: `created_at`, `fecha`, `estado`.

**`200 OK`** con una fila resumida por reserva.

### 3.2 `GET /api/reservas/{id}`

Detalle completo: cabecera, detalle del tipo, recursos asignados con su rol y estado, contexto con sus snapshots, acompañantes, campos adicionales, propuesta vigente si existe e historial de estados. Para `LISTA_ESPERA`, incluye evaluación de viabilidad, recepción del material, horas y formulario complementario con ambas partes y su revisión cuando exista; los archivos se consultan mediante §2.6 y §2.7.

Las asignaciones cuyo retiro exige conservar historial permanecen en el historial de recursos; el retiro manual de §4.4 no genera ese historial. Para retiros por préstamo incluyen `estado_asignacion: "RETIRADO"`, `retirado_at` (ISO 8601 UTC), `causa_retiro: "PRESTAMO_FISICO"` y `reserva_causante_id`. Se excluyen de los recursos efectivos. La referencia causante se conserva internamente, pero solo se expone su identificador si el actor tiene acceso a esa reserva; en otro caso se devuelve `reserva_causante_id: null`, sin conceder acceso ni revelar datos del préstamo ajeno. Cancelar el préstamo no borra esa relación histórica.

**Errores:** `404 NO_ENCONTRADO` si está fuera del ámbito del actor.

### 3.3 `GET /api/reservas/disponibilidad`

Consulta de disponibilidad. Flujo `UF-RES-19`.

Parámetros: `id_unidad` obligatorio, `espacio_id` o `recurso_id`, `desde` y `hasta`.

**`200 OK`**

```json
{
  "horario_unidad": { "dias_atencion": [1,2,3,4,5], "hora_apertura": "07:00", "hora_cierre": "19:00" },
  "franjas": [{ "fecha": "2026-10-14", "hora_inicio": "08:00", "hora_fin": "12:00", "disponible": false }]
}
```

El horario proviene de la unidad, no del espacio (`RN-ESP-DIS-02` de espacios). Los espacios, recursos internos y complementarios sin préstamo bloquean por franja. Un compromiso físico vigente mantiene el recurso no elegible para otra solicitud, también después de su fecha estimada de devolución (`RN-DIS-06`). Para ese recurso, las franjas consultadas se devuelven con `disponible: false`; esto no modifica las franjas del espacio. Terminar el compromiso no permite responder disponible si el recurso sigue deshabilitado o no operativo. No se expone una fecha estimada como garantía de liberación. Lo que el actor ve de cada franja ocupada depende de la configuración de visibilidad de la unidad (`RN-DIS`), pero el horario y la ocupación nunca se ocultan (`RN-DIS-07`).

Esta consulta **no reserva ni garantiza nada**: la disponibilidad se revalida al guardar.

---

## 4. Gestión por el Técnico

### 4.1 `POST /api/reservas/{id}/aprobacion`

Aprueba una reserva. Flujo `UF-RES-07`. Permiso: `reservas.administrar` sobre la unidad de la reserva.

```json
{ "observacion": "Aprobada con el equipo sustituido" }
```

Para `LISTA_ESPERA`, esta misma ruta registra recepción de material y aprobación; no existe una ruta de recepción independiente. Permiso: Técnico con `reservas.administrar` sobre la unidad. Cuerpo específico:

```json
{ "material_recibido": true, "observacion": "Material recibido y formulario revisado" }
```

`material_recibido` es una confirmación obligatoria y debe ser `true`; `observacion` es opcional. El servidor exige `SOLICITADA`, `viable = true`, parte del reservista registrada y parte técnica con revisión vigente (`RN-TIP-PLE-05`). No se exige una fecha de recepción previamente persistida. Genera `fecha_recepcion_material` y `fecha_aprobacion` con el instante de la operación y guarda ambas, el estado y su historial en una única transacción. Si falla, no registra recepción ni aprobación. El campo `material_recibido` no se admite para los otros tipos.

**`200 OK`** — devuelve `estado: "APROBADA"` y `fecha_aprobacion`, salvo `ESPACIO` aprobado durante su franja (`hora_inicio <= ahora < hora_fin`), que devuelve `estado: "EN_EJECUCION"` tras registrar aprobación e inicio inmediato en la misma transacción. Para lista de espera incluye `detalle.fecha_recepcion_material`. Un espacio puede permanecer solicitado durante la franja; al alcanzar `hora_fin` ya no se aprueba: responde `409 ESTADO_INCOMPATIBLE` y rige la cancelación automática de `UF-RES-21`.

Para `RECURSO_CAMPUS` y `RECURSO_EXTERNO`, aprobación, generación de FGL 030 e inicio de ejecución pertenecen al mismo proceso de salida: esta ruta registra la aprobación y la orden; §6.1 registra la entrega física y el paso a `EN_EJECUCION` dentro de ese proceso. No constituyen una etapa posterior para retirar recursos por deshabilitación. Desde la salida, la composición queda fija hasta la devolución. El paso a `APROBADA` genera la FGL 030 con los datos vigentes, también en la creación autoaprobada. Aprobación y generación se guardan juntas; ante fallo se revierten ambas. Desde entonces no se modifican los datos de la reserva incluidos en la orden ni sus snapshots; no se regenera ni versiona (`RN-TIP-RC-07`, `RN-TIP-RE-07`).

Aprobar revalida disponibilidad, habilitación, operatividad, horario y capacidad cuando correspondan (`RN-APR-06`). Para préstamos se excluye el compromiso propio, sin admitir otro compromiso ni entrega abierta incompatible (`RN-DIS-06`). Para lista de espera rigen la viabilidad, formulario y recepción conjunta descritos arriba; no se validan espacio, recursos ni franjas inexistentes.

**Errores:** `409 ESTADO_INCOMPATIBLE`, `409 SOLAPAMIENTO`, `409 CONFLICTO` por compromiso ajeno, entrega abierta incompatible o recurso no habilitado/operativo, `403 NO_AUTORIZADO`. Para lista de espera: `409 CONFLICTO` si falta viabilidad o formulario completo con revisión vigente; `422 VALIDACION` si falta `material_recibido`, es false o se envían campos inválidos. Todas las escrituras se revierten ante fallo.

### 4.2 `POST /api/reservas/{id}/rechazo`

```json
{ "motivo": "El laboratorio estará en mantenimiento" }
```

`motivo` es obligatorio. **`200 OK`** con `estado: "RECHAZADA"`. Un rechazo válido previo a entrega termina el compromiso sin exigir devolución. No puede usarse para liberar un recurso entregado: responde `409 ESTADO_INCOMPATIBLE` y no altera la entrega (`RN-DIS-06`).

### 4.3 `POST /api/reservas/{id}/recursos`

Agrega recursos a una reserva ya creada. Flujos `UF-RES-09` y `UF-RES-10`. Permiso: `reservas.administrar` sobre la unidad de la reserva.

```json
{ "recursos": [{ "recurso_id": 55, "rol": "ADICIONAL" }] }
```

Admitido exclusivamente para complementarios de `ESPACIO` y recursos `ADICIONAL`es de `RECURSO_INTERNO`, en `SOLICITADA`, `APROBADA` y `EN_EJECUCION` (`RN-TIP-PE-21`, `RN-TIP-RI-10`). No aplica a `RECURSO_CAMPUS`, `RECURSO_EXTERNO` ni `LISTA_ESPERA`. En `EN_EJECUCION` la disponibilidad se valida desde el momento de la incorporación hasta la finalización prevista (`RN-TIP-PE-23`).

**`201 Created`** con las asignaciones creadas. Para `ESPACIO` y `RECURSO_INTERNO`, la incorporación revalida habilitación, operatividad, disponibilidad por franja y ausencia de un compromiso físico ajeno de campus/externo. En interno crea una asignación temporal, sin entrega física, compromiso físico ni retiro automático de complementarios de otras reservas.

**Errores:** `409 TIPO_NO_ADMITIDO` para los tipos excluidos; `409 ESTADO_INCOMPATIBLE` fuera de los estados permitidos; `422 VALIDACION` si se envía un rol distinto de `ADICIONAL`; `409 CONFLICTO` si algún recurso tiene compromiso físico ajeno o no está habilitado/operativo; `409 SOLAPAMIENTO` por incompatibilidad temporal. No se incorpora parcialmente el lote.


### 4.4 `DELETE /api/reservas/{id}/recursos/{reserva_recurso_id}`

Permiso: `reservas.administrar` sobre la unidad de la reserva. Retira manualmente un complementario de `ESPACIO` o un `ADICIONAL` de `RECURSO_INTERNO`, exclusivamente en `SOLICITADA`, `APROBADA` o `EN_EJECUCION` (`RN-TIP-PE-21`, `RN-TIP-RI-10`). Revalida disponibilidad de la composición resultante. **`204 No Content`**: elimina la asociación vigente, sin conservar historial específico del retiro ni registrar causa, actor, fecha u otros metadatos. No elimina filas históricas de retiros automáticos: el retiro por préstamo sigue `RN-TIP-PE-28` y no utiliza esta operación.

**Errores:** `409 TIPO_NO_ADMITIDO` para `RECURSO_CAMPUS`, `RECURSO_EXTERNO` o `LISTA_ESPERA`; `409 ESTADO_INCOMPATIBLE` fuera de los estados permitidos; `409 CONFLICTO` al intentar retirar el `PRINCIPAL` de interno. Los conflictos de disponibilidad siguen §4.3. Un rechazo no modifica la composición. La edición del reservista en `SOLICITADA` conserva su contrato específico (§2.8).

---

## 5. Propuestas de periodo

En campus y externo, desde la generación de la FGL 030 al aprobar, crear una propuesta/contrapropuesta o aceptar una anterior responde `409 ESTADO_INCOMPATIBLE`, sin cambiar periodo, reserva, propuesta ni orden. La negociación en `APROBADA` descrita a continuación se limita a espacio e interno.

### 5.1 `POST /api/reservas/{id}/propuestas`

Propone un periodo alternativo para `ESPACIO`, `RECURSO_INTERNO`, `RECURSO_CAMPUS` o `RECURSO_EXTERNO`. No aplica a `LISTA_ESPERA`. La reserva debe estar `SOLICITADA` o `APROBADA`; únicamente se negocia el periodo, nunca espacio, recursos ni otros datos. Flujo `UF-RES-15`. Lo usa el Técnico para proponer y el Usuario para contraproponer; `origen` se deriva del rol del actor, no del cuerpo.

```json
{
  "fecha_inicio_propuesta": "2026-10-16",
  "fecha_fin_propuesta": "2026-10-16",
  "hora_inicio": "14:00",
  "hora_fin": "18:00",
  "motivo": "El espacio está ocupado esa mañana"
}
```

**`201 Created`** con la propuesta en estado `VIGENTE`. Si ya existía una vigente, queda `SUSTITUIDA` (`RN-PROP-07`). La reserva conserva su estado y periodo mientras se negocia (`RN-PROP-02`). **Errores:** `409 ESTADO_INCOMPATIBLE` fuera de `SOLICITADA` o `APROBADA`; `409 TIPO_NO_ADMITIDO` para lista de espera; `422 VALIDACION` por campos ajenos al periodo/motivo o periodo inválido; `403 NO_AUTORIZADO` o `404 NO_ENCONTRADO` según permiso y ámbito.

### 5.2 `POST /api/reservas/{id}/propuestas/vigente/aceptacion`

**`200 OK`** — devuelve la reserva con el periodo aceptado y su mismo estado (`SOLICITADA` o `APROBADA`). Revalida todas las reglas aplicables a la reprogramación, incluida antelación cuando corresponda (`RN-HOR-06`), y guarda periodo y aceptación de la propuesta atómicamente (`RN-PROP-05`). Si estaba `APROBADA`, conserva aprobación y `fecha_aprobacion`, sin transición de estado ficticia ni aprobación adicional. Conserva el compromiso físico propio y lo excluye de la comparación; no crea un nuevo compromiso (`RN-DIS-06`). Solo puede aceptar la contraparte de quien propuso (`RN-PROP-04`).

**Errores:** `409 SOLAPAMIENTO` si el periodo propuesto dejó de estar disponible; la propuesta queda vigente y la reserva sin cambios. `409 CONFLICTO` si falla habilitación/operatividad o existe un compromiso ajeno o entrega abierta incompatible; tampoco se modifica la propuesta ni la reserva. `409 FUERA_DE_HORARIO`, `409 CAPACIDAD_EXCEDIDA` o `422 VALIDACION` para las demás condiciones aplicables; `409 ESTADO_INCOMPATIBLE` si la reserva dejó de estar `SOLICITADA` o `APROBADA`. Toda revalidación usa datos vigentes y todo fallo revierte cambios: periodo, estado, asignaciones y propuesta quedan como estaban. Se revalida el estado dentro de la transacción frente a cancelación o inicio concurrentes.

### 5.3 `POST /api/reservas/{id}/propuestas/vigente/rechazo`

**`200 OK`** — registra la propuesta como `RECHAZADA`; la reserva conserva su periodo y estado actual (`SOLICITADA` o `APROBADA`), sin revocar aprobación (`RN-PROP-06`). **Errores:** `409 ESTADO_INCOMPATIBLE` fuera de esos estados; `403 NO_AUTORIZADO` o `404 NO_ENCONTRADO` según permiso y ámbito.

---

## 6. Ejecución

### 6.1 `POST /api/reservas/{id}/ejecucion`

Inicia una reserva `APROBADA` y la pasa a `EN_EJECUCION`. Solo en campus y externo registra entrega física; en `LISTA_ESPERA`, inicio de fabricación o prestación sin recursos. Flujo `UF-RES-13`. Permiso: `reservas.administrar` sobre la unidad de la reserva.

```json
{
  "recursos": [{ "reserva_recurso_id": 88, "observacion_entrega": "Entregado con estuche" }]
}
```

El cuerpo anterior corresponde solo a los tipos de préstamo. Esta operación completa el proceso de salida iniciado con la aprobación y generación de la FGL 030 (§4.1); no modifica, regenera ni versiona la orden ni cambia los recursos incluidos. El retiro automático por deshabilitación se limita a antes de ese proceso (`RN-CAN-06`). En ellos escribe en `reserva_ejecucion_recursos` con la cuenta que entrega. La ejecución física se registra separadamente del estado de asignación del recurso. El retiro de complementarios de espacio corresponde al establecimiento del compromiso (`UF-RES-23`), no se posterga hasta la entrega. En préstamos, el compromiso ya existe desde la incorporación; entregar lo conserva. Se revalidan habilitación, operatividad y ausencia de otro compromiso o entrega incompatible, excluyendo el compromiso propio. Si falla, `409 CONFLICTO` sin registrar entrega ni cambiar el estado.

**No aplica a `ESPACIO` ni `RECURSO_INTERNO`**, que inician automáticamente por horario conforme a `RN-TIP-PE-27`, `RN-TIP-RI-08` y `UF-RES-22`. Invocarlo sobre cualquiera de ellos responde `409 TIPO_NO_ADMITIDO`; no registra entrega ni cambia su estado.

Para `LISTA_ESPERA`, el cuerpo es `{}`. La operación registra únicamente la transición con actor e instante, sin asignaciones ni filas en `reserva_ejecucion_recursos` (`RN-TIP-PLE-07`). No admite `recursos`, ni siquiera un arreglo vacío.

**`200 OK`** con `estado: "EN_EJECUCION"`. **Errores para lista de espera:** `409 ESTADO_INCOMPATIBLE` si no está `APROBADA`; `422 VALIDACION` si el cuerpo contiene recursos u otros campos; `403 NO_AUTORIZADO` o `404 NO_ENCONTRADO` según ámbito. Un error no cambia el estado.

### 6.2 `POST /api/reservas/{id}/finalizacion`

Registra el cierre y pasa a `FINALIZADA`. Para una reserva de recursos que requiera devolución, el arreglo debe contener todos los recursos entregados de esa reserva; no se permite devolución parcial. Flujo `UF-RES-14`.

**No aplica a `ESPACIO` ni `RECURSO_INTERNO`**, cuyas transiciones al fin de franja son automáticas (`RN-TIP-PE-25`, `RN-TIP-RI-09`, `UF-RES-21`). Invocarlo sobre cualquiera de ellos responde `409 TIPO_NO_ADMITIDO`; no registra devolución ni cierre manual.

```json
{
  "recursos": [{ "reserva_recurso_id": 88, "observacion_devolucion": "Sin novedad" }]
}
```

El ejemplo anterior corresponde al cierre de préstamos. Para `LISTA_ESPERA`, el Técnico con `reservas.administrar` sobre la unidad envía:

```json
{ "horas_ejecucion": 6.5 }
```

Exige estado `EN_EJECUCION` y `horas_ejecucion` como número finito mayor o igual a cero; cero es válido conforme al modelo. No admite `recursos`, ni siquiera vacío. Horas, transición e historial se guardan juntos, sin devoluciones ni filas de ejecución física (`RN-TIP-PLE-08`).

**`200 OK`** con `estado: "FINALIZADA"` y `detalle.horas_ejecucion`. **Errores para lista de espera:** `422 VALIDACION` por horas ausentes, nulas, negativas, no finitas, no numéricas o presencia de recursos; `409 ESTADO_INCOMPATIBLE` fuera de `EN_EJECUCION`; `403 NO_AUTORIZADO` o `404 NO_ENCONTRADO` según ámbito. No se persisten horas ni estado parcialmente.

En préstamos, la devolución completa y el cierre son atómicos. Se permite registrar devolución y finalizar aunque el recurso regrese dañado, en mantenimiento o deshabilitado: ello no restablece su habilitación u operatividad ni aprueba otra solicitud. Toda solicitud posterior revalida esas condiciones (`RN-DIS-04`, `RN-DIS-06`). **`200 OK`** con `estado: "FINALIZADA"`; `409 ESTADO_INCOMPATIBLE` si se intenta cerrar omitiendo recursos entregados pendientes de devolución, sin cambios parciales.

### 6.3 `POST /api/reservas/{id}/cancelacion`

Cancela la reserva. Flujo `UF-RES-11`. El Usuario puede cancelar las suyas; el Técnico las de su unidad.

```json
{ "motivo": "Ya no se requiere el laboratorio" }
```

Admitida mientras la ejecución no haya iniciado (`RN-CAN-02`). Una cancelación válida termina el compromiso anterior a la entrega sin exigir una devolución inexistente (`RN-CAN-01`, `RN-DIS-06`); no habilita ni declara operativo el recurso. Cancelar el préstamo no restaura automáticamente ningún complementario retirado por `UF-RES-23`; se conserva el historial y la referencia causante.

**Errores:** `409 ESTADO_INCOMPATIBLE` si la ejecución ya inició. En `RECURSO_INTERNO`, `EN_EJECUCION` comienza automáticamente por horario y desde ese estado no se admite cancelación, sin consultar entrega/devolución física.

---

## 7. Orden de salida

### 7.1 `GET /api/reservas/{id}/orden-salida`

Datos prellenados del FGL 030 para reservas `RECURSO_CAMPUS` y `RECURSO_EXTERNO`, generados al pasar a `APROBADA`, incluida la autoaprobación, dentro de `UF-RES-03` y `UF-RES-04`. La consulta lee los snapshots originales e inmutables; no genera, actualiza ni versiona la orden. Devuelve la cabecera con sus snapshots, las actividades marcadas y los ítems técnicos, uno por recurso.

Las actividades marcadas son las casillas del FGL 030 y se generan desde `reserva_contexto` conforme a `RN-SAL`; no representan nuevos contextos ni se administran desde este endpoint.

**Errores:** `409 TIPO_NO_ADMITIDO` si el tipo de reserva no genera orden de salida; `404 NO_ENCONTRADO` si todavía no se ha generado por no haberse aprobado. Ambas consultas de orden aplican estos errores.

### 7.2 `GET /api/reservas/{id}/orden-salida.pdf`

Documento listo para imprimir, renderizado a partir de los snapshots inmutables de la sección anterior. Descargar el PDF no regenera los datos ni crea otra versión de la orden. `Content-Type: application/pdf`. Flujos `UF-RES-03` y `UF-RES-04`.

Las firmas y los recibidos a satisfacción **no** se capturan: se diligencian a mano sobre el documento impreso (`RN-TIP-RC-14`, `RN-TIP-RE-14`).

---

## 8. Calendario y exportación

### 8.1 `GET /api/reservas/{id}/calendario.ics`

Archivo iCalendar de una reserva aprobada de tipo `ESPACIO` o `RECURSO_INTERNO` para uso dentro de la unidad organizacional. Flujo `UF-RES-17`. `Content-Type: text/calendar`. Incluye el periodo con hora y la ubicación cuando aplique (`RN-CAL-01`, `RN-CAL-02`).

**Errores:** `409 ESTADO_INCOMPATIBLE` si la reserva no está aprobada; `409 TIPO_NO_ADMITIDO` para `RECURSO_CAMPUS`, `RECURSO_EXTERNO` o `LISTA_ESPERA`.

### 8.2 `GET /api/reservas/exportacion?formato=csv`

Exporta el listado con los filtros aplicados. Flujo `UF-REP-02` de reports. Permiso: `reservas.exportar`.

`formato` admite `csv` y `excel`, conforme a `RN-EXP-05` de reports, propietario de esa decisión. El archivo contiene exactamente lo visible según el filtro y el ámbito del actor (`RN-REP-03`).

---

## 9. Pendientes

1. El esquema exacto de los campos adicionales depende del catálogo de `espacio_campos.tipo`, registrado como **OQ-02**.
2. ADR-001 registra el diseño temporal aprobado el 2026-09-23 y la ampliación funcional del 2026-09-24: compromiso físico único desde la incorporación. El caso mixto se resuelve conforme a `RN-TIP-PE-28`. Faltan diseñar la integridad adicional e implementar y probar las garantías y la trazabilidad del retiro contra la base. `409 SOLAPAMIENTO` para conflictos temporales y `409 CONFLICTO` para compromiso físico describen el comportamiento esperado, no una garantía instalada.
3. `motivos_solicitud` y `motivo_solicitud_id` se retiran del modelo (**OQ-07**). Este contrato nunca los expuso: el "por qué" de la reserva se resuelve con `contexto`, y la razón de sacar un equipo del campus con `razon_solicitud` del detalle.

---

## 10. Lo que este contrato no expone

- **Cancelación automática por deshabilitación** (`UF-RES-12`): la dispara Resources al deshabilitar un elemento, no un endpoint de reservas.
- **Transiciones por franja** (`UF-RES-21`, `UF-RES-22`): espacio solicitado vence a `CANCELADA`; espacio aprobado/en ejecución vence a `FINALIZADA`; interno aprobado inicia y en ejecución finaliza automáticamente por horario. No cambian reservas rechazadas o canceladas.
- **Recordatorios** (`UF-RES-16`): los genera un proceso temporal, no una solicitud HTTP.
- **Visibilidad de disponibilidad** (`UF-RES-20`): es configuración de la unidad y pertenece al contrato de resources.
- **Historial de estados y asignaciones históricas exigidas por las reglas**: se consultan dentro del detalle de la reserva, sin endpoints de escritura directa. El retiro manual del Técnico no genera historial específico. La auditoría general queda fuera del alcance y no se expone en el detalle.

