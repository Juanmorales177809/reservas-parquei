# Contrato de API — Notifications

Contrato de comunicación del módulo `notifications`. Traduce a superficie HTTP los 3 flujos de [user-flow.md](../../modules/notifications/user-flow.md), las reglas de [business-rules.md](../../modules/notifications/business-rules.md) y las entidades de [data-model.md](../../modules/notifications/data-model.md).

---

## 1. Convenciones

Aplica las [convenciones transversales](../README.md). Aquí solo se documenta lo propio de notifications.

| Aspecto | Valor |
|---|---|
| Base path | `/api/notificaciones` |
| Permiso administrativo | Ninguno. Todas las rutas operan sobre la cuenta de la sesión: una cuenta consulta y marca únicamente sus propias notificaciones (`RN-CON-01`) |
| Identificadores | `id` entero de 64 bits de la notificación; `tipo_evento_id` entero del catálogo de eventos |

**Este contrato no define códigos de error propios.** Todos los que usa pertenecen al [catálogo común](../README.md#catálogo-común-de-códigos).

**La generación de notificaciones no se expone.** Ningún endpoint crea, edita ni elimina una notificación. Se producen como efecto de operaciones de otros módulos, conforme a la correspondencia entre eventos y flujos productores de [business-rules.md](../../modules/notifications/business-rules.md#correspondencia-entre-eventos-y-flujos-productores). Este contrato solo cubre lo que el destinatario hace con lo que ya se le comunicó.

---

## 2. Bandeja

### 2.1 `GET /api/notificaciones`

Listado paginado con la envolvente completa de las notificaciones in-app de la cuenta de la sesión. Flujo `UF-NOT-01`.

El ámbito no es configurable: devuelve siempre y solo las notificaciones cuya cuenta destinataria es la del actor (`RN-CON-01`). El cliente nunca envía un identificador de cuenta (`SEC-AUTZ-03`).

Filtros: `leida` con valores `true` o `false`, y `tipo_evento` con el código del catálogo. Orden admitido: `created_at`, descendente por defecto (`RN-CON-03`).

**`200 OK`**

```json
{
  "datos": [
    {
      "id": 8841,
      "tipo_evento": { "codigo": "RESERVA_APROBADA", "nombre": "Reserva aprobada" },
      "titulo": "Tu reserva fue aprobada",
      "cuerpo": "La reserva del 14 de octubre en el Laboratorio de Metrología quedó aprobada.",
      "reserva_id": 1042,
      "leida_at": null,
      "created_at": "2026-10-09T15:20:11Z"
    }
  ],
  "paginacion": { "pagina": 1, "tamano": 20, "total": 37, "paginas": 2 }
}
```

`titulo` y `cuerpo` son el texto tal como se comunicó y **no se recalculan al consultar**, aunque la reserva haya cambiado después (`RN-HIS-03`, `RN-CNT-04`). `reserva_id` procede del evento y puede ser `null` cuando la notificación no se refiere a una reserva. `leida_at` en `null` significa no leída (`RN-EST-02`).

Una notificación cuya entidad relacionada se desactivó después sigue apareciendo (`RN-HIS-02`). No existe purga de historial: el volumen se gestiona con paginación y filtros (`RN-HIS-01`).

Consultar no modifica el estado de ninguna notificación (`RN-CON-04`).

### 2.2 `POST /api/notificaciones/{id}/lectura`

Marca como leída una notificación propia. Flujo `UF-NOT-01`.

Sin cuerpo de solicitud.

**`200 OK`**

```json
{ "id": 8841, "leida_at": "2026-10-09T16:02:44Z" }
```

El marcado registra el instante de lectura y **no altera el estado de la reserva, del recurso, de la operación relacionada ni del envío de correo asociado al mismo evento** (`RN-EST-04`, `RN-COR-05`). Repetir la operación sobre una notificación ya leída conserva el instante original y responde igual.

**Errores:** `404 NO_ENCONTRADO` si la notificación no existe **o no pertenece a la cuenta de la sesión**. No se distingue entre ambos casos, para no revelar la existencia de notificaciones ajenas (`RN-CON-01`).

---

## 3. Preferencias de correo

### 3.1 `GET /api/notificaciones/preferencias`

Preferencias de envío por correo de la cuenta de la sesión. Paso 2 de `UF-NOT-02`.

**`200 OK`**

```json
{
  "general": { "correo_habilitado": true },
  "por_evento": [
    { "tipo_evento": { "codigo": "RESERVA_RECORDATORIO", "nombre": "Recordatorio de reserva" }, "correo_habilitado": false }
  ]
}
```

`general` puede no existir todavía; en ese caso se devuelve con el valor por defecto. `por_evento` contiene únicamente los tipos para los que la cuenta fijó una preferencia explícita: los demás se rigen por la general (`RN-PREF-04`).

### 3.2 `PUT /api/notificaciones/preferencias`

Establece las preferencias. Flujo `UF-NOT-02`. Reemplaza el conjunto completo: un tipo de evento que no venga en `por_evento` queda sin preferencia propia y pasa a regirse por la general.

```json
{
  "general": { "correo_habilitado": true },
  "por_evento": [{ "tipo_evento_id": 7, "correo_habilitado": false }]
}
```

**`200 OK`** con las preferencias vigentes, en el mismo formato de la sección anterior.

La preferencia más específica prevalece: la del tipo de evento y, en su ausencia, la general (`RN-PREF-04`). **Afecta únicamente al canal de correo**: la notificación in-app se sigue generando y consultando igual (`RN-PREF-01`).

**Errores:** `404 NO_ENCONTRADO` si un `tipo_evento_id` no existe o está deshabilitado; `422 VALIDACION` si un tipo aparece repetido en `por_evento`.

### 3.3 `GET /api/notificaciones/tipos-evento`

Catálogo de eventos notificables, necesario para que el cliente pueda ofrecer la configuración por tipo de la sección anterior. **Catálogo cerrado**: devuelve solo `datos`, sin paginación. Solo se devuelven los tipos habilitados.

```json
{ "datos": [{ "id": 7, "codigo": "RESERVA_RECORDATORIO", "nombre": "Recordatorio de reserva", "descripcion": "Aviso previo al inicio de una reserva" }] }
```

Un tipo deshabilitado deja de generar notificaciones nuevas, pero se conserva para interpretar las históricas, por lo que puede aparecer en la bandeja aunque no figure aquí.

---

## 4. Lo que este contrato no expone

- **La generación de notificaciones.** Ningún endpoint las crea. Cada evento lo produce el flujo del módulo propietario de la operación, y este módulo lo registra y lo presenta (`RN-NOT-02`).
- **La entrega de correo** (`UF-NOT-03`). La ejecuta una tarea programada del sistema, no una solicitud HTTP. El estado de un envío, sus intentos y su anulación se administran dentro de ese proceso conforme a `RN-COR`.
- **El estado de los correos.** No se consulta desde aquí. Es independiente del estado de lectura in-app (`RN-COR-05`) y no forma parte de lo que el destinatario gestiona.
- **La habilitación de correo por unidad.** Es `notificar_por_correo` de la configuración del laboratorio y pertenece a [resources](../resources/api-contract.md) conforme a `RN-LAB-07`. Se aplica **antes** que la preferencia individual: si está deshabilitada para la unidad, no se genera correo aunque la cuenta lo tenga habilitado (`RN-PREF-02`).
- **Los correos de autenticación.** Invitación y recuperación de contraseña los origina [auth](../auth/api-contract.md) y ninguna preferencia los afecta (`RN-PREF-03`).
- **Una bandeja administrativa.** `RN-CON-01` admite una función administrativa expresamente autorizada, pero ninguna regla la define hoy. Mientras no exista, ninguna cuenta puede consultar notificaciones ajenas.
