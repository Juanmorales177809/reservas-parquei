# Contrato de API — Resources

Contrato de comunicación del módulo `resources`. Traduce a superficie HTTP los 13 flujos de [user-flow.md](../../modules/resources/user-flow.md), las reglas de [business-rules.md](../../modules/resources/business-rules.md) y las entidades de [data-model.md](../../modules/resources/data-model.md).

---

## 1. Convenciones

Aplica las [convenciones transversales](../README.md). Aquí solo se documenta lo propio de resources.

| Aspecto | Valor |
|---|---|
| Base path | `/api/recursos` para el catálogo; `/api/laboratorios` para la configuración de unidad |
| Permiso administrativo | `recursos.administrar` sobre la unidad para mobiliarios y otros recursos; equipos existentes: `recursos.editar_equipos` sobre la unidad o `recursos.administrar_equipos` global, según la asignación vigente del permiso requerido, no el nombre del rol; crear equipos requiere `recursos.administrar_equipos` global; reasignar la unidad de un recurso requiere `recursos.reasignar_unidad` global; la configuración del laboratorio requiere `laboratorios.configurar` sobre la unidad |
| Identificadores | `id` entero del recurso, compartido con su especialización; `id_unidad` entero de la unidad organizacional |

Códigos de error propios, adicionales al catálogo común:

| HTTP | `codigo` | Uso |
|---|---|---|
| 409 | `TIPO_INCOMPATIBLE` | La especialización enviada no corresponde al `tipo` del recurso |

`409 UNIDAD_INCOMPATIBLE` pertenece al catálogo común; aquí significa que la unidad del recurso y la de una especialización que mantenga `id_unidad` propio no coinciden, o que el recurso no pertenece a la unidad de destino al reasignarlo.

El catálogo raíz es `recursos.recursos`, con una especialización 1:1 por tipo: equipos, mobiliarios y otros. La creación del recurso y su especialización es **atómica**: o se escriben ambas o ninguna. No se ofrece eliminación física de equipos; para impedir su uso futuro se deshabilitan, conservando su historial.

**El Técnico no crea ni elimina físicamente equipos.** Puede editar equipos existentes de su unidad y cambiar tanto su habilitación (`recursos.recursos.habilitado`) como su estado operativo (`recursos.equipos.estado`). La gestión global de equipos requiere una asignación global de `recursos.administrar_equipos`; el rol Administrador no la concede por sí mismo. Una cuenta con rol Administrador por otro permiso global puede ejercer `recursos.editar_equipos` únicamente dentro de la unidad de su asignación, coincidente con la de su cargo vigente (`RN-AUTH-ROL-03`, `RN-AUTH-ROL-07` de auth). Ese permiso no permite crear ni eliminar equipos, administrarlos globalmente o reasignar su unidad; se mantienen las restricciones y los permisos específicos de cada operación.

---

## 2. Catálogo de recursos

### 2.1 `POST /api/recursos`

Registra un recurso con su especialización. Flujos `UF-REC-01` (mobiliario), `UF-REC-02` (otro) y `UF-REC-03` (equipo).

**Origen externo ([decisión 2026-09-30](../../docs/decisions/origen-externo-estructura-institucional.md)).** Los **equipos** vienen de LIA: la interfaz no los registra, solo mobiliario y otros recursos. Con `tipo` `EQUIPO` este endpoint se conserva como vía de carga hasta que se diseñe la integración.

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

### 2.2 `GET /api/recursos`

Listado paginado con la envolvente completa. Flujo `UF-REC-04`. Filtros: `id_unidad`, `tipo`, `habilitado`, `busqueda` sobre nombre y placa. Orden admitido: `nombre`, `tipo`. Cada elemento de `datos` incluye `nombre` (el de su especialización) para que las pantallas ofrezcan el recurso por nombre y no por su identificador: `{ "id": 41, "tipo": "MOBILIARIO", "nombre": "Mesa de trabajo", "id_unidad": 7, "habilitado": true }`.

El listado ofrecido para **reservar** excluye los equipos con `acreditado = true`, que no son reservables aunque estén habilitados y operativos (`RN-REC-11`). El filtro `reservable=true` aplica esa exclusión; sin él, el listado administrativo los incluye.

### 2.3 `GET /api/recursos/{id}`

Detalle con la especialización correspondiente al tipo. Flujo `UF-REC-05`. Para equipos incluye placa, serial, calibración, `requiere_apoyo` y `acreditado`.

### 2.4 `PATCH /api/recursos/{id}`

Actualiza la especialización. Flujos `UF-REC-06`, `UF-REC-07` y `UF-REC-12`. Los campos admitidos dependen del tipo. Para equipos, se requiere `recursos.editar_equipos` con alcance sobre la unidad del equipo o `recursos.administrar_equipos` global. La primera vía permite actualizar los datos del equipo y `recursos.equipos.estado` dentro de su unidad también cuando la cuenta sea Administrador por otro permiso global; este rol no amplía el alcance de edición. Los cambios de equipo no admiten crear ni eliminar el registro ni modificar su unidad responsable. El campo común `recursos.recursos.habilitado` se modifica mediante el endpoint `/estado`.

### 2.5 `PATCH /api/recursos/{id}/estado`

Habilita o deshabilita el campo común `recursos.recursos.habilitado`. Flujos `UF-REC-08` y `UF-REC-09`. Para equipos se exige `recursos.editar_equipos` con alcance sobre la unidad del equipo o `recursos.administrar_equipos` global, también para cuentas con permisos de distintos alcances según §1; para otros recursos se exige el permiso correspondiente a su tipo. Este endpoint no modifica `recursos.equipos.estado`, que se actualiza con `PATCH /api/recursos/{id}`.

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

### 2.6 `GET /api/recursos/{id}/impacto-deshabilitacion`

Conteo previo para poblar la confirmación de §2.5, sin ejecutar nada. Sustenta el paso de advertencia de `UF-REC-09`.

```json
{ "reservas_a_cancelar": 2, "reservas_a_retirar": 3 }
```

### 2.7 `PATCH /api/recursos/{id}/unidad`

Cambia la unidad responsable. Flujo `UF-REC-10`. Permiso: `recursos.reasignar_unidad`.

```json
{ "id_unidad": 12 }
```

La unidad del recurso y la de su especialización deben quedar coincidentes. Las reservas históricas conservan la referencia al recurso con independencia del cambio.

**Errores:** `403 NO_AUTORIZADO` si el actor no tiene una asignación global de `recursos.reasignar_unidad`, `409 UNIDAD_INCOMPATIBLE`.

---

## 3. Configuración del laboratorio

Es la configuración por unidad en `reservas.laboratorios_config`. Incluye el horario de atención, que **es el horario aplicable a todos los espacios y recursos de esa unidad** (`RN-ESP-DIS-02` de espacios).

### 3.0 `GET /api/laboratorios`

Catálogo de laboratorios: las unidades organizacionales activas que tienen configuración de reservas. Lo puede leer **cualquier cuenta autenticada**, sin permiso administrativo: quien va a reservar, filtrar sus reservas o consultar reportes necesita elegir la unidad por su nombre, y `GET /api/unidades` exige `unidades.administrar`. Catálogo cerrado, sin paginación, ordenado por nombre.

**`200 OK`**

```json
{ "datos": [{ "id_unidad": 7, "nombre": "Laboratorio de Metrología", "habilitado_reservas": true }] }
```

`habilitado_reservas` es el de `RN-LAB-03`: una unidad con reservas deshabilitadas sigue apareciendo (sus reservas históricas se consultan), pero no admite nuevas.

### 3.1 `GET /api/laboratorios/{id_unidad}/configuracion`

Configuración vigente de la unidad. Paso 2 de `UF-REC-13`.

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
  "notificar_por_correo": false,
  "tipos_reserva": ["ESPACIO", "RECURSO_INTERNO"]
}
```

`notificar_por_correo` es la única configuración general por unidad que habilita el correo saliente de las notificaciones de sus reservas y recursos (`RN-LAB-07`); se devuelve para poder mostrarla y modificarla. `dias_atencion` numera 0 = domingo a 6 = sábado.

La lectura del horario es pública para cualquier cuenta autenticada: el Usuario siempre puede consultarlo y las opciones de visibilidad no pueden ocultarlo (`RN-DIS-07` de reservations).

### 3.2 `PATCH /api/laboratorios/{id_unidad}/configuracion`

Modifica la configuración. Flujo `UF-REC-13`. Permiso: `laboratorios.configurar` sobre la unidad.

Cambiar el horario **cambia el de todos los espacios de la unidad**, porque ninguno define uno propio. La validación de reservas futuras usa la configuración vigente al crear, modificar o aprobar (`RN-HOR-07` de reservations); un cambio de horario no reinterpreta automáticamente las reservas ya aprobadas.

`recordatorio_horas_antes` debe ser mayor que cero y define la anticipación del recordatorio automático (`RN-REC-01` de reservations).

### 3.3 `PUT /api/laboratorios/{id_unidad}/tipos-reserva`

Define qué tipos de reserva ofrece el laboratorio. Flujo `UF-REC-13` (`RN-TIP-05` de reservations).

```json
{ "tipos": ["ESPACIO", "RECURSO_INTERNO", "RECURSO_CAMPUS"] }
```

Una lista vacía deja el laboratorio sin reservas posibles (`RN-TIP-06` de reservations). Los tipos deshabilitados se conservan para mantener las referencias históricas.

### 3.4 `PATCH /api/laboratorios/{id_unidad}/visibilidad`

Opciones de visibilidad de la disponibilidad. Flujo `UF-RES-20` de reservations, cuya configuración pertenece a este módulo.

```json
{ "mostrar_estado_reserva": true, "mostrar_reservista": false }
```

Ninguna de las dos puede ocultar el horario ni las franjas ocupadas (`RN-DIS-07` de reservations).

---

## 4. Contrato interno hacia otros módulos

Resources no expone un endpoint para que otros módulos consulten disponibilidad: la disponibilidad temporal depende de las reservas y la resuelve reservations (`RN-ESP-REC-05` de espacios). Flujo `UF-REC-11`.

Lo que resources sí provee internamente:

| Operación | Responsabilidad |
|---|---|
| `obtener_recurso(id)` | Datos del recurso y su especialización, para los snapshots del FGL 030 |
| `es_reservable(id)` | Habilitado, operativo y no acreditado (`RN-REC-11`) |
| `configuracion_unidad(id_unidad)` | Horario, antelación, aprobación automática y recordatorio |

---

## 5. Lo que este contrato no expone

- **Importación masiva de equipos**: la orquesta administration conforme a `RN-IMP-01` y `UF-ADM-04` de ese módulo, y su contrato sigue pendiente. Este módulo aporta las validaciones del equipo (`RN-IMP-02` a `RN-IMP-05`) y la escritura de `UF-REC-03`, no un endpoint de carga propio.
- **Disponibilidad**: la resuelve [reservations](../reservations/api-contract.md).
- **Espacios**: tienen su propio [contrato](../espacios/api-contract.md); resources administra la configuración de la unidad a la que pertenecen.
