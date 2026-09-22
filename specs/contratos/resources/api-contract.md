# Contrato de API — Resources

Contrato de comunicación del módulo `resources`. Traduce a superficie HTTP los 12 flujos de [user-flow.md](../../modules/resources/user-flow.md), las reglas de [business-rules.md](../../modules/resources/business-rules.md) y las entidades de [data-model.md](../../modules/resources/data-model.md).

Aplica las [convenciones transversales](../README.md). Aquí solo se documenta lo propio de resources.

| Aspecto | Valor |
|---|---|
| Base path | `/api/recursos` para el catálogo; `/api/laboratorios` para la configuración de unidad |
| Permiso administrativo | `recursos.administrar` sobre la unidad para mobiliarios y otros recursos; equipos existentes: `recursos.editar_equipos` sobre la unidad para el Técnico y `recursos.administrar_equipos` global para el Administrador; crear equipos requiere `recursos.administrar_equipos` global |

Códigos de error propios:

| HTTP | `codigo` | Uso |
|---|---|---|
| 409 | `TIPO_INCOMPATIBLE` | La especialización enviada no corresponde al `tipo` del recurso |
| 409 | `UNIDAD_INCOMPATIBLE` | La unidad del recurso y la de una especialización que mantenga `id_unidad` propio no coinciden |

El catálogo raíz es `recursos.recursos`, con una especialización 1:1 por tipo: equipos, mobiliarios y otros. La creación del recurso y su especialización es **atómica**: o se escriben ambas o ninguna. No se ofrece eliminación física de equipos; para impedir su uso futuro se deshabilitan, conservando su historial.

**El Técnico no crea ni elimina físicamente equipos.** Puede editar equipos existentes de su unidad y cambiar tanto su habilitación (`recursos.recursos.habilitado`) como su estado operativo (`recursos.equipos.estado`). El Administrador gestiona equipos con alcance global.

---

## 1. Catálogo de recursos

### 1.1 `POST /api/recursos`

Registra un recurso con su especialización. Flujos `UF-REC-01` (mobiliario), `UF-REC-02` (otro) y `UF-REC-03` (equipo).

```json
{
  "id_unidad": 7,
  "tipo": "MOBILIARIO",
  "especializacion": {
    "nombre": "Mesa de trabajo",
    "descripcion": "Mesa metálica de 2 m"
  }
}
```

Para `tipo: "EQUIPO"`, la especialización corresponde a `recursos.equipos` y comparte el `id` del recurso como PK/FK; su creación requiere el permiso global `recursos.administrar_equipos`.

**`201 Created`**

```json
{ "id": 41, "tipo": "MOBILIARIO", "id_unidad": 7, "habilitado": true }
```

**Errores:** `409 TIPO_INCOMPATIBLE`, `409 UNIDAD_INCOMPATIBLE`, `403 NO_AUTORIZADO` si el actor no cuenta con el permiso requerido; el Técnico no puede crear equipos.

### 1.2 `GET /api/recursos`

Listado paginado. Flujo `UF-REC-04`. Filtros: `id_unidad`, `tipo`, `habilitado`, `busqueda` sobre nombre y placa. Orden admitido: `nombre`, `tipo`.

El listado ofrecido para **reservar** excluye los equipos con `acreditado = true`, que no son reservables aunque estén habilitados y operativos (`RN-REC-11`). El filtro `reservable=true` aplica esa exclusión; sin él, el listado administrativo los incluye.

### 1.3 `GET /api/recursos/{id}`

Detalle con la especialización correspondiente al tipo. Flujo `UF-REC-05`. Para equipos incluye placa, serial, calibración, `requiere_apoyo` y `acreditado`.

### 1.4 `PATCH /api/recursos/{id}`

Actualiza la especialización. Flujos `UF-REC-06`, `UF-REC-07` y `UF-REC-12`. Los campos admitidos dependen del tipo. Para equipos, el Técnico requiere `recursos.editar_equipos` en la unidad del equipo y puede actualizar los datos del equipo y `recursos.equipos.estado`; el Administrador requiere `recursos.administrar_equipos` global. Los cambios de equipo no admiten crear ni eliminar el registro ni modificar su unidad responsable. El campo común `recursos.recursos.habilitado` se modifica mediante el endpoint `/estado`.

### 1.5 `PATCH /api/recursos/{id}/estado`

Habilita o deshabilita el campo común `recursos.recursos.habilitado`. Flujos `UF-REC-08` y `UF-REC-09`. Para equipos se exige `recursos.editar_equipos` en la unidad del equipo al Técnico o `recursos.administrar_equipos` global al Administrador; para otros recursos se exige el permiso correspondiente a su tipo. Este endpoint no modifica `recursos.equipos.estado`, que se actualiza con `PATCH /api/recursos/{id}`.

```json
{ "habilitado": false, "confirmado": true }
```

Al deshabilitar, el sistema **advierte antes** cuántas reservas futuras se cancelarán y exige confirmación explícita (`RN-DES-06`). La advertencia solo aparece cuando la desactivación cancelará reservas, es decir cuando el recurso participa como `PRINCIPAL`; si solo participa como `ADICIONAL`, se retira de esas reservas sin confirmación (`RN-DES-07`).

**`200 OK`**

```json
{ "id": 41, "habilitado": false, "reservas_canceladas": 2, "reservas_afectadas": 5 }
```

`reservas_canceladas` son aquellas donde el recurso era `PRINCIPAL`; `reservas_afectadas` incluye además aquellas donde solo se retiró. El efecto lo determinan `RN-CAN-04` y `RN-CAN-05` de reservations; resources no reimplementa esa lógica.

**Errores:** `409 CONFLICTO` si hay cancelaciones pendientes de confirmar.

### 1.6 `GET /api/recursos/{id}/impacto-deshabilitacion`

Conteo previo para poblar la confirmación, sin ejecutar nada.

```json
{ "reservas_a_cancelar": 2, "reservas_a_retirar": 3 }
```

### 1.7 `PATCH /api/recursos/{id}/unidad`

Cambia la unidad responsable. Flujo `UF-REC-10`. Permiso: `recursos.reasignar_unidad`.

```json
{ "id_unidad": 12 }
```

La unidad del recurso y la de su especialización deben quedar coincidentes. Las reservas históricas conservan la referencia al recurso con independencia del cambio.

**Errores:** `403 NO_AUTORIZADO` si el actor no tiene alcance global, `409 UNIDAD_INCOMPATIBLE`.

---

## 2. Configuración del laboratorio

Es la configuración por unidad en `reservas.laboratorios_config`. Incluye el horario de atención, que **es el horario aplicable a todos los espacios y recursos de esa unidad** (`RN-ESP-DIS-02` de espacios).

### 2.1 `GET /api/laboratorios/{id_unidad}/configuracion`

```json
{
  "id_unidad": 7,
  "habilitado_reservas": true,
  "dias_atencion": [1, 2, 3, 4, 5],
  "hora_apertura": "07:00",
  "hora_cierre": "19:00",
  "horas_antelacion": 24,
  "aprobacion_automatica": false,
  "recordatorio_horas_antes": 24,
  "mostrar_estado_reserva": false,
  "mostrar_reservista": false,
  "tipos_reserva": ["ESPACIO", "RECURSO_INTERNO"]
}
```

La lectura del horario es pública para cualquier cuenta autenticada: el Usuario siempre puede consultarlo y las opciones de visibilidad no pueden ocultarlo (`RN-DIS-07` de reservations).

### 2.2 `PATCH /api/laboratorios/{id_unidad}/configuracion`

Modifica la configuración. Permiso: `laboratorios.configurar` sobre la unidad.

Cambiar el horario **cambia el de todos los espacios de la unidad**, porque ninguno define uno propio. La validación de reservas futuras usa la configuración vigente al crear, modificar o aprobar (`RN-HOR-07` de reservations); un cambio de horario no reinterpreta automáticamente las reservas ya aprobadas.

`recordatorio_horas_antes` debe ser mayor que cero y define la anticipación del recordatorio automático (`RN-REC-01` de reservations).

### 2.3 `PUT /api/laboratorios/{id_unidad}/tipos-reserva`

Define qué tipos de reserva ofrece el laboratorio (`RN-TIP-05` de reservations).

```json
{ "tipos": ["ESPACIO", "RECURSO_INTERNO", "RECURSO_CAMPUS"] }
```

Una lista vacía deja el laboratorio sin reservas posibles (`RN-TIP-06` de reservations). Los tipos deshabilitados se conservan para mantener las referencias históricas.

### 2.4 `PATCH /api/laboratorios/{id_unidad}/visibilidad`

Opciones de visibilidad de la disponibilidad. Flujo `UF-RES-20` de reservations, cuya configuración pertenece a este módulo.

```json
{ "mostrar_estado_reserva": true, "mostrar_reservista": false }
```

Ninguna de las dos puede ocultar el horario ni las franjas ocupadas (`RN-DIS-07` de reservations).

---

## 3. Contrato interno hacia otros módulos

Resources no expone un endpoint para que otros módulos consulten disponibilidad: la disponibilidad temporal depende de las reservas y la resuelve reservations (`RN-ESP-REC-05` de espacios). Flujo `UF-REC-11`.

Lo que resources sí provee internamente:

| Operación | Responsabilidad |
|---|---|
| `obtener_recurso(id)` | Datos del recurso y su especialización, para los snapshots del FGL 030 |
| `es_reservable(id)` | Habilitado, operativo y no acreditado (`RN-REC-11`) |
| `configuracion_unidad(id_unidad)` | Horario, antelación, aprobación automática y recordatorio |

---

## 4. Lo que este contrato no expone

- **Importación masiva de equipos**: pertenece a administration (`RN-IMP`), pendiente de contrato.
- **Disponibilidad**: la resuelve [reservations](../reservations/api-contract.md).
- **Espacios**: tienen su propio [contrato](../espacios/api-contract.md); resources administra la configuración de la unidad a la que pertenecen.
