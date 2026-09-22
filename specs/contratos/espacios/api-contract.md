# Contrato de API — Espacios

Contrato de comunicación del módulo `espacios`. Traduce a superficie HTTP los 14 flujos de [user-flow.md](../../modules/espacios/user-flow.md), las reglas de [business-rules.md](../../modules/espacios/business-rules.md) y las entidades de [data-model.md](../../modules/espacios/data-model.md).

Aplica las [convenciones transversales](../README.md). Aquí solo se documenta lo propio de espacios.

| Aspecto | Valor |
|---|---|
| Base path | `/api/espacios` |
| Permiso administrativo | `espacios.administrar` sobre la unidad; el Administrador lo tiene con alcance global (`RN-ESP-03` de espacios) |

Códigos de error propios:

| HTTP | `codigo` | Uso |
|---|---|---|
| 409 | `NOMBRE_DUPLICADO` | Ya existe un espacio con ese nombre en la unidad (`uq_espacios_unidad_nombre`) |
| 409 | `CAMPO_SIN_OPCIONES` | Un campo de selección no puede habilitarse sin al menos una opción habilitada (`RN-ESP-CAM-03`) |

**Un espacio no tiene horario propio.** El horario aplicable es el de atención de su unidad y se administra en el contrato de [resources](../resources/api-contract.md), no aquí (`RN-ESP-DIS-02`). Este contrato no expone ningún endpoint de horario.

---

## 1. Espacios

### 1.1 `POST /api/espacios`

Registra un espacio. Flujo `UF-ESP-01`.

```json
{
  "id_unidad": 7,
  "nombre": "Laboratorio de Metrología",
  "ubicacion": "Bloque 4, piso 2",
  "capacidad": 25,
  "descripcion": "Sala con bancos de ensayo",
  "recursos": [41, 55],
  "campos": [
    {
      "nombre": "Ensayo a realizar",
      "tipo": "TEXTO",
      "obligatorio": true,
      "orden": 0,
      "opciones": []
    }
  ]
}
```

`capacidad` es obligatoria y mayor que cero (`RN-ESP-02`). `recursos` y `campos` son opcionales; el espacio puede crearse sin ninguno.

**`201 Created`** con el espacio creado, sus recursos asociados y sus campos.

**Errores:** `409 NOMBRE_DUPLICADO`, `403 NO_AUTORIZADO` si el actor no administra esa unidad, `422 VALIDACION`.

### 1.2 `PATCH /api/espacios/{id}`

Actualiza la información general. Flujo `UF-ESP-02`. Admite `nombre`, `ubicacion`, `capacidad` y `descripcion`.

`capacidad` no puede quedar vacía ni en cero (`RN-ESP-02`). La modificación no altera reservas históricas (`UF-ESP-02`, flujo alterno).

**`200 OK`** con el espacio actualizado.

### 1.3 `GET /api/espacios`

Listado paginado. Flujo `UF-ESP-12`. Filtros: `id_unidad`, `habilitado`, `capacidad_minima`. Orden admitido: `nombre`, `capacidad`.

Un Usuario solo ve espacios habilitados; un Técnico ve también los deshabilitados de su unidad.

### 1.4 `GET /api/espacios/{id}`

Detalle. Flujo `UF-ESP-13`.

```json
{
  "id": 3,
  "id_unidad": 7,
  "nombre": "Laboratorio de Metrología",
  "capacidad": 25,
  "habilitado": true,
  "horario_unidad": { "dias_atencion": [1,2,3,4,5], "hora_apertura": "07:00", "hora_cierre": "19:00" },
  "recursos": [{ "recurso_id": 41, "nombre": "Durómetro", "habilitado": true }],
  "campos": [{ "id": 5, "nombre": "Ensayo a realizar", "tipo": "TEXTO", "obligatorio": true, "orden": 0, "opciones": [] }]
}
```

`horario_unidad` se devuelve por conveniencia del cliente y es una lectura de la configuración de la unidad, no un atributo del espacio.

### 1.5 `PATCH /api/espacios/{id}/estado`

Habilita o deshabilita. Flujos `UF-ESP-10` y `UF-ESP-11`.

```json
{ "habilitado": false }
```

Al deshabilitar, el sistema **debe advertir antes** cuántas reservas futuras se cancelarán y exigir confirmación explícita (`RN-ESP-HAB-05`, `RN-DES-06` de resources). El cliente obtiene ese número con el endpoint siguiente y lo confirma enviando `confirmado: true`.

```json
{ "habilitado": false, "confirmado": true }
```

**Errores:** `409 CONFLICTO` si hay reservas futuras que se cancelarían y falta `confirmado`. La respuesta incluye el número en `detalles`, para que el cliente pueda mostrarlo sin una consulta extra.

**`200 OK`**

```json
{ "id": 3, "habilitado": false, "reservas_canceladas": 4 }
```

Deshabilitar cancela las reservas futuras que dependan del espacio, conforme a `RN-CAN-04` de reservations, y conserva las asociaciones históricas (`RN-ESP-HAB-04`).

### 1.6 `GET /api/espacios/{id}/impacto-deshabilitacion`

Cuántas reservas futuras se verían afectadas, para poblar la confirmación de `1.5` sin ejecutar nada.

**`200 OK`**

```json
{ "reservas_a_cancelar": 4 }
```

El conteo lo resuelve reservations aplicando `RN-CAN-04`; espacios no reimplementa esa lógica.

---

## 2. Recursos asociados

### 2.1 `POST /api/espacios/{id}/recursos`

Asocia recursos existentes. Flujo `UF-ESP-03`.

```json
{ "recursos": [41, 55] }
```

Asociar no crea recursos ni implica disponibilidad temporal (`RN-ESP-REC-02`, `RN-ESP-REC-04`). Cada recurso debe pertenecer a la misma unidad del espacio y no puede tener otra asociación habilitada (`RN-ESP-REC-06`, `RN-ESP-REC-07`).

**`201 Created`** con las asociaciones. **Errores:** `409 CONFLICTO` si la asociación ya existe o el recurso ya está asociado activamente a otro espacio; `409 UNIDAD_INCOMPATIBLE` si el recurso pertenece a otra unidad.

### 2.2 `DELETE /api/espacios/{id}/recursos/{recurso_id}`

Retira la asociación. Flujo `UF-ESP-04`. **`204 No Content`**.

No borra la fila: la deshabilita, para que las reservas históricas conserven su referencia.

---

## 3. Campos adicionales

### 3.1 `POST /api/espacios/{id}/campos`

Configura un campo. Flujo `UF-ESP-05`.

```json
{
  "nombre": "Tipo de probeta",
  "tipo": "SELECCION",
  "obligatorio": true,
  "orden": 1,
  "opciones": [{ "valor": "Metálica", "orden": 0 }, { "valor": "Polimérica", "orden": 1 }]
}
```

**`201 Created`**. **Errores:** `409 CAMPO_SIN_OPCIONES` si `tipo` es `SELECCION` y no llega ninguna opción habilitada, `409 CONFLICTO` si el nombre ya existe en ese espacio.

### 3.2 `PATCH /api/espacios/{id}/campos/{campo_id}`

Edita el campo. Flujo `UF-ESP-07`. La modificación no puede impedir interpretar los valores históricos ya registrados (`RN-ESP-CAM-05`).

### 3.3 `PATCH /api/espacios/{id}/campos/{campo_id}/estado`

Deshabilita o habilita el campo. Flujo `UF-ESP-08`. Un campo utilizado en reservas **nunca se elimina**: se deshabilita y sus valores históricos permanecen consultables.

### 3.4 `PUT /api/espacios/{id}/campos/orden`

Reordena. Flujo `UF-ESP-09`.

```json
{ "orden": [{ "campo_id": 5, "orden": 0 }, { "campo_id": 9, "orden": 1 }] }
```

El cambio de orden no modifica los valores históricos de reservas anteriores.

### 3.5 `POST /api/espacios/{id}/campos/{campo_id}/opciones`

Agrega opciones a un campo de selección. Flujo `UF-ESP-06`.

### 3.6 `PATCH /api/espacios/{id}/campos/{campo_id}/opciones/{opcion_id}`

Edita el valor, el orden o la habilitación de una opción. Una opción usada en una reserva se deshabilita, nunca se borra: las reservas históricas conservan la interpretación de la opción utilizada.

---

## 4. Lo que este contrato no expone

- **Horarios del espacio**: no existen. El horario es de la unidad y se administra en [resources](../resources/api-contract.md).
- **Disponibilidad temporal**: la resuelve reservations en `GET /api/reservas/disponibilidad`, porque depende de las reservas, no de la configuración del espacio (`RN-ESP-REC-05`).
- **Uso del espacio durante una reserva** (`UF-ESP-14`): es un flujo de reservations.

## 5. Catálogo de tipos de campo

Los valores admitidos para `tipo` son `TEXTO`, `TEXTO_LARGO`, `NUMERO`, `BOOLEANO` y `SELECCION`. El valor `SELECCION` identifica un campo cuyas opciones se administran mediante el endpoint de opciones.
