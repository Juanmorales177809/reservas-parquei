# Contrato de API — Auth

Contrato de comunicación del módulo `auth`. Define endpoints, solicitudes, respuestas y códigos HTTP derivados de los flujos de [user-flow.md](../../modules/auth/user-flow.md), las reglas de [business-rules.md](../../modules/auth/business-rules.md), los controles de [security.md](../../modules/auth/security.md) y las entidades de [data-model.md](../../modules/auth/data-model.md).

Este documento no redefine reglas de negocio ni controles de seguridad: los traduce a la superficie HTTP. Ante cualquier conflicto prevalecen los documentos del módulo y la [arquitectura central](../../docs/architecture.md).

---

## 1. Convenciones generales

| Aspecto | Definición |
|---|---|
| Base path | `/api/auth` |
| Formato | `application/json` en solicitudes y respuestas |
| Fechas | ISO 8601 en UTC (`2026-09-18T14:03:11Z`) |
| Identificadores | `id_cuenta` entero de 64 bits; `id_sesion` UUID |
| Transporte | HTTPS obligatorio en toda ruta autenticada (`SEC-INF-01`, `SEC-SES-06`) |
| Caché | Las respuestas que establecen o contienen información de sesión declaran `Cache-Control: no-store` (`SEC-SES-11`) |

Las operaciones que modifican estado nunca se exponen mediante `GET` (`SEC-CSRF-03`).

### Envolvente de error

Toda respuesta de error usa la misma estructura (`architecture.md` §12):

```json
{
  "error": {
    "codigo": "CREDENCIALES_INVALIDAS",
    "mensaje": "No fue posible iniciar sesión con los datos suministrados.",
    "detalles": []
  }
}
```

`detalles` se usa solo para errores de validación de campos y nunca contiene trazas internas, SQL, secretos ni variables de entorno (`SEC-INF-04`).

### Catálogo de códigos de error

| HTTP | `codigo` | Uso |
|---|---|---|
| 400 | `SOLICITUD_INVALIDA` | Cuerpo malformado o parámetros incompatibles |
| 401 | `NO_AUTENTICADO` | Falta sesión válida, o venció o fue revocada (`SEC-SES-07`) |
| 401 | `CREDENCIALES_INVALIDAS` | Autenticación fallida, sin distinguir la causa (`SEC-ABU-02`) |
| 401 | `REAUTENTICACION_REQUERIDA` | Operación sensible sin autenticación reciente (`SEC-REAUTH-01`) |
| 403 | `NO_AUTORIZADO` | Permiso ausente, fuera de ámbito o recurso ajeno (`SEC-AUTZ-02`, `SEC-AUTZ-04`, `SEC-AUTZ-06`) |
| 403 | `PERFIL_INICIAL_PENDIENTE` | La operación requiere haber completado la actualización inicial del Usuario (`RN-USR-08`) |
| 404 | `NO_ENCONTRADO` | Recurso inexistente dentro del ámbito visible del actor |
| 409 | `CONFLICTO` | Conflicto de negocio, por ejemplo correo ya registrado |
| 410 | `TOKEN_NO_VIGENTE` | Token vencido, ya utilizado o revocado (`SEC-TOK-05`, `SEC-INV-02`) |
| 422 | `VALIDACION` | Campos inválidos según el esquema |
| 429 | `DEMASIADOS_INTENTOS` | Límite contra abuso superado (`SEC-ABU-01`) |
| 500 | `ERROR_INTERNO` | Error no controlado, sin detalle interno |

`403 NO_AUTORIZADO` no distingue entre "sin permiso", "fuera de ámbito" y "recurso ajeno", para no facilitar enumeración. Un recurso existente pero fuera del ámbito del actor responde `404 NO_ENCONTRADO` cuando revelar su existencia constituya una fuga.

---

## 2. Autenticación y transporte

La arquitectura fija JWT como mecanismo de autenticación (`architecture.md` §11.1) y `security.md` exige que el secreto del navegador viaje exclusivamente por cookie `HttpOnly` (`SEC-SES-03`, `SEC-SES-05`). El contrato combina ambos: **JWT de acceso de vida corta transportado en cookie, y refresco respaldado por `auth.sesiones`**. El cliente nunca lee ni almacena tokens.

### Cookies

| Cookie | Contenido | Atributos | Vigencia |
|---|---|---|---|
| `rp_access` | JWT de acceso | `HttpOnly`, `Secure`, `SameSite=Lax`, `Path=/api` | Corta, por configuración |
| `rp_refresh` | Secreto de refresco; su hash se persiste en `auth.sesiones.refresh_token_hash` | `HttpOnly`, `Secure`, `SameSite=Lax`, `Path=/api/auth/sesiones` | Hasta `expires_at` de la sesión |
| `rp_csrf` | Token CSRF de doble envío | `Secure`, `SameSite=Lax`, legible por JavaScript | Igual que la sesión |

`rp_csrf` es intencionalmente legible por el cliente: no es el secreto de sesión y su exposición no contradice `SEC-SES-05`.

### Claims del JWT de acceso

```json
{
  "iss": "reservas-parquei",
  "aud": "reservas-parquei-api",
  "sub": "1042",
  "sid": "8f2c1b6e-5a71-4f0c-9a3a-2c9f1d0b7e44",
  "typ": "access",
  "iat": 1789660991,
  "exp": 1789661891
}
```

El servidor fija explícitamente el algoritmo esperado y rechaza `alg: none` o cualquier algoritmo distinto (`SEC-JWT-01`). Valida firma, `iss`, `aud`, `exp` y `typ` (`SEC-JWT-02`).

El token **no transporta rol, permisos ni ámbito**: esos datos se evalúan en cada operación con información vigente (`SEC-JWT-04`, `RN-AUTH-ROL-05`). Un JWT con firma válida se rechaza igualmente si su sesión (`sid`) fue revocada o venció (`SEC-JWT-05`, `SEC-SES-07`).

### CSRF

Toda operación que modifica estado exige el encabezado `X-CSRF-Token` con el valor de la cookie `rp_csrf` (`SEC-CSRF-01`, `SEC-CSRF-02`). Su ausencia o discrepancia responde `403 NO_AUTORIZADO`.

### Limitación de intentos

Los endpoints marcados como **limitado** aplican control contra abuso automatizado (`SEC-ABU-01`) y responden `429 DEMASIADOS_INTENTOS` con encabezado `Retry-After`. Superar el límite no implica autorización (`SEC-ABU-03`).

---

## 3. Endpoints públicos de sesión y credenciales

### 3.1 `POST /api/auth/registro` — limitado

Autorregistro sin invitación. Flujo [UF-AUTH-01](../../modules/auth/user-flow.md).

```json
{
  "nombre": "Persona de ejemplo",
  "documento": "1000000001",
  "telefono": "+573000000001",
  "institucion": "Institución de ejemplo",
  "dependencia": "Facultad de ejemplo",
  "correo": "persona@correo.itm.edu.co",
  "contrasena": "una frase larga de paso"
}
```

`contrasena`: mínimo 8 y máximo admitido 64 caracteres, sin reglas de composición obligatorias (`SEC-PWD-07`).

Los cinco campos del perfil son obligatorios conforme a RN-DAT de Usuarios: `nombre` hasta 150 caracteres; `documento` y `telefono` hasta 20 cada uno; `institucion` y `dependencia` hasta 255 cada uno. Son cadenas no vacías ni compuestas solo por espacios; documento y teléfono son únicos por separado en Usuarios. Auth delega la validación y persistencia del perfil en ese módulo. La identidad y la cuenta se crean atómicamente y `perfil_actualizado_at` permanece NULL hasta completar el flujo inicial.

**`202 Accepted`**

```json
{
  "mensaje": "Si el correo puede registrarse, la cuenta quedará disponible para iniciar sesión."
}
```

La respuesta es idéntica exista o no una cuenta con ese correo, para no revelar cuentas registradas (`SEC-ABU-02`). También se conserva esta respuesta genérica ante un documento o teléfono duplicado, sin crear la cuenta ni revelar la identidad con la que existe el conflicto. Cuando la cuenta se crea, queda activa, de tipo `USUARIO`, vinculada a una única identidad (`RN-AUTH-ID-03`) y sin permisos administrativos (`RN-AUTH-ROL-04`).

**Errores:** `422 VALIDACION` (datos obligatorios ausentes, vacíos o fuera de longitud; correo con formato inválido o contraseña fuera del rango admitido), `429 DEMASIADOS_INTENTOS`.

El completado de perfil pertenece a `usuarios`. Auth consulta su condición para aplicar RN-AUTH-SES-04 y RN-USR-08; no duplica sus campos ni valida por su cuenta las vinculaciones.

### Condición de actualización inicial

Las respuestas de inicio de sesión (§3.2), renovación (§3.3), sesión actual (§3.4) y activación con sesión (§4.4) incluyen `actualizacion_inicial_pendiente`: `true` si la cuenta es `USUARIO` y `usuarios.usuarios.perfil_actualizado_at` es NULL, `false` si ya completó el proceso y `null` para `PERSONAL` (no aplica).

El cliente conduce al Usuario pendiente al flujo de completar o reanudar el perfil. El servidor consulta la condición vigente al autorizar cada operación; no la toma del cliente ni de un claim del JWT. Mientras esté pendiente permite las operaciones necesarias de perfil, catálogos y vinculaciones, la consulta/renovación de sesión para ese fin y el cierre de sesión. Las demás operaciones de negocio responden `403 PERFIL_INICIAL_PENDIENTE`. Los procesos públicos de recuperación de credenciales mantienen sus controles propios.

---

### 3.2 `POST /api/auth/sesiones` — limitado

Inicio de sesión. Flujo [UF-AUTH-04](../../modules/auth/user-flow.md).

```json
{
  "correo": "persona@correo.itm.edu.co",
  "contrasena": "una frase larga de paso"
}
```

**`201 Created`** — establece `rp_access`, `rp_refresh` y `rp_csrf`.

```json
{
  "id_cuenta": 1042,
  "tipo_cuenta": "USUARIO",
  "rol": "USUARIO",
  "actualizacion_inicial_pendiente": true,
  "correo": "persona@correo.itm.edu.co",
  "id_sesion": "8f2c1b6e-5a71-4f0c-9a3a-2c9f1d0b7e44",
  "expira_en": "2026-09-18T22:03:11Z"
}
```

El identificador de sesión se regenera en cada inicio exitoso e invalida el anterior (`SEC-SES-13`). El secreto se genera con al menos 128 bits de un generador criptográficamente seguro (`SEC-SES-02`, `SEC-SES-12`).

**Errores:** `401 CREDENCIALES_INVALIDAS` —respuesta única para contraseña incorrecta, correo inexistente, cuenta inactiva e identidad inactiva (`SEC-ABU-02`, `RN-AUTH-ID-01`, `RN-AUTH-ID-05`)—, `422 VALIDACION`, `429 DEMASIADOS_INTENTOS`.

Se registran el inicio exitoso y los intentos fallidos relevantes, sin secretos (`SEC-AUD-02`, `SEC-AUD-03`).

---

### 3.3 `POST /api/auth/sesiones/renovacion`

Renovación del acceso. Flujo [UF-AUTH-05](../../modules/auth/user-flow.md). Requiere cookie `rp_refresh`; no requiere `rp_access` vigente.

Sin cuerpo de solicitud.

**`200 OK`** — reemplaza `rp_access` y rota `rp_refresh`.

```json
{
  "id_sesion": "8f2c1b6e-5a71-4f0c-9a3a-2c9f1d0b7e44",
  "expira_en": "2026-09-18T22:33:11Z",
  "actualizacion_inicial_pendiente": true
}
```

Antes de renovar, el servidor verifica que la sesión exista, no esté revocada, no haya superado su vigencia máxima ni el tiempo máximo de inactividad (`SEC-SES-07`, `SEC-SES-09`), y que la cuenta e identidad sigan activas (`RN-AUTH-ID-01`).

**Errores:** `401 NO_AUTENTICADO` cuando la sesión venció, fue revocada o la cuenta quedó inactiva; el cliente debe reautenticarse.

---

### 3.4 `GET /api/auth/sesiones/actual`

Identidad autenticada vigente. Sustenta el paso 2 de [UF-AUTH-10](../../modules/auth/user-flow.md) en el cliente.

**`200 OK`**

```json
{
  "id_cuenta": 1042,
  "tipo_cuenta": "PERSONAL",
  "rol": "TECNICO",
  "correo": "tecnico@itm.edu.co",
  "actualizacion_inicial_pendiente": null,
  "id_sesion": "8f2c1b6e-5a71-4f0c-9a3a-2c9f1d0b7e44",
  "unidades_autorizadas": [7],
  "autenticacion_reciente": false
}
```

`unidades_autorizadas` contiene las unidades sobre las que el actor puede ejercer operaciones administrativas: una lista para `TECNICO` (`RN-AUTH-ROL-02`) y `"GLOBAL"` para `ADMINISTRADOR` (`RN-AUTH-ROL-03`). Para `USUARIO` es una lista vacía (`RN-AUTH-ROL-04`).

Esta respuesta sirve para adaptar la interfaz, **nunca como control de autorización**: el servidor revalida permiso y ámbito en cada operación (`SEC-AUTZ-01`).

**Errores:** `401 NO_AUTENTICADO`.

---

### 3.5 `DELETE /api/auth/sesiones/actual`

Cierre de sesión. Flujo [UF-AUTH-06](../../modules/auth/user-flow.md).

**`204 No Content`** — invalida la sesión en `auth.sesiones` sin esperar su vencimiento y elimina `rp_access`, `rp_refresh` y `rp_csrf` del cliente (`RN-AUTH-SES-02`, `SEC-SES-08`).

Si la sesión ya estaba vencida o revocada, la respuesta es igualmente `204`: el resultado para el cliente es el mismo.

---

### 3.6 `POST /api/auth/recuperacion` — limitado

Solicitud de recuperación de contraseña. Flujo [UF-AUTH-07](../../modules/auth/user-flow.md).

```json
{ "correo": "persona@correo.itm.edu.co" }
```

**`202 Accepted`**

```json
{
  "mensaje": "Si existe una cuenta asociada, se enviarán las instrucciones de recuperación."
}
```

La respuesta y su tiempo de proceso son equivalentes exista o no la cuenta (`SEC-REC-01`). Cuando existe, se genera un token de vigencia limitada y un solo uso (`SEC-REC-02`, `SEC-TOK-04`) y `notificaciones` entrega el enlace.

**Errores:** `422 VALIDACION`, `429 DEMASIADOS_INTENTOS`.

---

### 3.7 `GET /api/auth/recuperacion/{token}`

Validación previa del token, para que el cliente muestre el formulario solo si procede. Paso 2 de [UF-AUTH-08](../../modules/auth/user-flow.md).

**`200 OK`**

```json
{ "vigente": true }
```

**Errores:** `410 TOKEN_NO_VIGENTE` si está vencido, ya utilizado o revocado. La respuesta no revela a qué cuenta pertenece el token.

---

### 3.8 `POST /api/auth/recuperacion/{token}` — limitado

Restablecimiento efectivo. Flujo [UF-AUTH-08](../../modules/auth/user-flow.md).

```json
{ "contrasena": "una nueva frase larga de paso" }
```

**`204 No Content`**

El token se valida por completo antes de aplicar cualquier cambio (`SEC-TOK-01`, `SEC-REC-03`) y queda marcado como utilizado (`SEC-TOK-05`). La operación revoca todas las sesiones activas de la cuenta (`SEC-REC-05`, `SEC-SES-10`) y `notificaciones` informa del cambio a la cuenta afectada (`SEC-REC-04`).

**Errores:** `410 TOKEN_NO_VIGENTE`, `422 VALIDACION`, `429 DEMASIADOS_INTENTOS`.

---

### 3.9 `POST /api/auth/reautenticacion` — limitado

Reautenticación para operaciones sensibles. Flujo [UF-AUTH-09](../../modules/auth/user-flow.md). Requiere sesión válida.

```json
{ "contrasena": "una frase larga de paso" }
```

**`200 OK`** — regenera el identificador de sesión (`SEC-REAUTH-04`, `SEC-SES-13`).

```json
{ "autenticacion_reciente_hasta": "2026-09-18T14:18:11Z" }
```

Dentro de esa ventana, las operaciones sensibles de §5 y §6 no vuelven a exigir reautenticación. La sola existencia de una sesión antigua nunca la sustituye (`SEC-REAUTH-03`).

**Errores:** `401 CREDENCIALES_INVALIDAS`, `401 NO_AUTENTICADO`, `429 DEMASIADOS_INTENTOS`.

---

## 4. Invitaciones

### 4.1 `POST /api/auth/invitaciones`

Emisión de invitación. Flujo [UF-AUTH-02](../../modules/auth/user-flow.md). Requiere permiso administrativo sobre cuentas y ámbito aplicable.

```json
{
  "correo": "nuevo@itm.edu.co",
  "tipo_cuenta": "PERSONAL",
  "id_unidad": 7
}
```

`id_unidad` es obligatorio para `tipo_cuenta = "PERSONAL"` y debe estar dentro del ámbito del emisor (`SEC-AUTZ-04`).

Para `tipo_cuenta = "USUARIO"`, debe existir una identidad creada previamente mediante el alta administrativa de Usuarios conforme a RN-DAT. El servidor la resuelve por el correo único del destinatario y valida sus datos obligatorios antes de emitir la invitación. La activación utiliza esa identidad existente, sin duplicar el perfil ni crear una identidad con campos vacíos.

**`201 Created`**

```json
{
  "id_invitacion": 55,
  "correo": "nuevo@itm.edu.co",
  "tipo_cuenta": "PERSONAL",
  "expira_en": "2026-09-25T14:03:11Z",
  "estado": "PENDIENTE"
}
```

La respuesta **nunca incluye el token**: se entrega únicamente por correo a través de `notificaciones` (`SEC-TOK-02`). La invitación no concede permisos administrativos por sí misma; estos se administran en `administration` (`SEC-INV-04`).

**Errores:** `401 NO_AUTENTICADO`, `403 NO_AUTORIZADO`, `409 CONFLICTO` si el correo ya corresponde a una cuenta activa, `422 VALIDACION`.

---

### 4.2 `POST /api/auth/invitaciones/{id_invitacion}/reenvio`

Reenvío de una invitación no completada. Flujo alterno de [UF-AUTH-02](../../modules/auth/user-flow.md).

**`200 OK`**

```json
{
  "id_invitacion": 55,
  "expira_en": "2026-10-02T09:15:00Z",
  "estado": "PENDIENTE"
}
```

Emite un token nuevo e invalida el anterior (`SEC-INV-03`).

**Errores:** `403 NO_AUTORIZADO`, `404 NO_ENCONTRADO`, `409 CONFLICTO` si la invitación ya fue utilizada.

---

### 4.3 `GET /api/auth/invitaciones/{token}`

Validación previa del token, público. Paso 2 de [UF-AUTH-03](../../modules/auth/user-flow.md).

**`200 OK`**

```json
{
  "vigente": true,
  "correo": "nuevo@itm.edu.co"
}
```

Se devuelve el correo destino porque quien posee el token ya lo recibió en ese buzón.

**Errores:** `410 TOKEN_NO_VIGENTE` cuando está vencida, utilizada o revocada (`SEC-INV-02`).

---

### 4.4 `POST /api/auth/invitaciones/{token}/activacion` — limitado

Activación de la cuenta invitada. Flujo [UF-AUTH-03](../../modules/auth/user-flow.md).

```json
{ "contrasena": "una frase larga de paso" }
```

**`201 Created`** — establece las cookies de sesión, igual que un inicio de sesión.

```json
{
  "id_cuenta": 1109,
  "tipo_cuenta": "PERSONAL",
  "rol": "TECNICO",
  "correo": "nuevo@itm.edu.co",
  "actualizacion_inicial_pendiente": null,
  "id_sesion": "0d5b1a44-92f7-4c33-b0f5-6e0a2c7d1f10",
  "expira_en": "2026-10-02T17:15:00Z"
}
```

La cuenta se crea o activa con el tipo e identidad definidos en la invitación almacenada, respetando la exclusividad de identidad (`RN-AUTH-ID-03`), y el token queda marcado como utilizado (`SEC-TOK-05`).

**Errores:** `410 TOKEN_NO_VIGENTE`, `422 VALIDACION`, `429 DEMASIADOS_INTENTOS`.

---

## 5. Cuenta propia

### 5.1 `PUT /api/auth/cuentas/actual/contrasena`

Cambio de contraseña autenticado. Flujo [UF-AUTH-11](../../modules/auth/user-flow.md). Operación sensible (`SEC-REAUTH-02`).

```json
{ "contrasena": "otra frase larga de paso" }
```

**`204 No Content`** — revoca las sesiones activas según la política aplicable (`SEC-SES-10`) y `notificaciones` informa del cambio (`SEC-REC-04`).

**Errores:** `401 REAUTENTICACION_REQUERIDA` cuando no hay autenticación reciente, `401 NO_AUTENTICADO`, `422 VALIDACION`.

---

### 5.2 `PUT /api/auth/cuentas/actual/correo`

Cambio del correo de la cuenta. Flujo [UF-AUTH-12](../../modules/auth/user-flow.md). Operación sensible (`SEC-REAUTH-02`).

```json
{ "correo": "nuevo.correo@itm.edu.co" }
```

**`200 OK`**

```json
{
  "id_cuenta": 1042,
  "correo": "nuevo.correo@itm.edu.co"
}
```

Conserva la identidad funcional y el historial de la cuenta (`RN-CUE-01`). El correo permanece único (`RN-AUTH-ID-02`).

**Errores:** `401 REAUTENTICACION_REQUERIDA`, `409 CONFLICTO` si el correo pertenece a otra cuenta, `422 VALIDACION`.

---

## 6. Administración de cuentas

Requieren permiso administrativo sobre cuentas y ámbito aplicable (`RN-ADM-01`, `SEC-AUTZ-04`).

### 6.1 `PATCH /api/auth/cuentas/{id_cuenta}/estado`

Desactivación o reactivación. Flujo [UF-AUTH-13](../../modules/auth/user-flow.md).

```json
{ "estado": false }
```

**`200 OK`**

```json
{
  "id_cuenta": 1042,
  "estado": false,
  "sesiones_revocadas": 3
}
```

Desactivar marca la cuenta inactiva sin eliminar historial (`RN-AUTH-ID-05`, `RN-CUE-04`) y revoca sus sesiones activas (`SEC-SES-10`). Reactivar conserva el identificador y las relaciones previas, sin crear una identidad nueva (`RN-HAB-04`).

**Errores:** `403 NO_AUTORIZADO`, `404 NO_ENCONTRADO`, `409 CONFLICTO` cuando la operación dejaría al sistema sin ninguna cuenta con permisos de administrador.

---

### 6.2 `PUT /api/auth/cuentas/{id_cuenta}/identidad`

Promoción o degradación entre reservista y personal administrativo. Flujo [UF-AUTH-14](../../modules/auth/user-flow.md). Operación sensible (`SEC-REAUTH-02`).

```json
{
  "tipo_cuenta": "PERSONAL",
  "id_persona": 314
}
```

Se envía `id_persona` para `tipo_cuenta = "PERSONAL"` o `id_usuario` para `"USUARIO"`, nunca ambos (`RN-AUTH-ID-03`, `RN-AUTH-ID-04`).

**`200 OK`**

```json
{
  "id_cuenta": 1042,
  "tipo_cuenta": "PERSONAL",
  "id_persona": 314,
  "id_usuario": null
}
```

El cambio conserva el historial de la persona y aplica solo a decisiones de autorización posteriores (`RN-AUTH-SES-03`, `RN-PER-05`). No concede permisos por sí mismo: se administran en `administration` (`RN-PRF-03`).

**Errores:** `401 REAUTENTICACION_REQUERIDA`, `403 NO_AUTORIZADO`, `404 NO_ENCONTRADO` si la identidad destino no existe, `409 CONFLICTO` si la identidad destino está inactiva, ya pertenece a otra cuenta, o el cambio dejaría al sistema sin administradores, `422 VALIDACION`.

---

## 7. Contrato interno hacia otros módulos

`auth` no expone endpoints para autorizar operaciones ajenas: entrega a cada módulo el contexto y las decisiones que necesita (`overview.md` → Provides). Corresponde al paso 7 de [UF-AUTH-10](../../modules/auth/user-flow.md).

### Contexto autenticado

```python
ContextoAutenticado:
    id_cuenta: int
    id_sesion: UUID
    tipo_cuenta: Literal["USUARIO", "PERSONAL"]
    id_usuario: int | None
    id_persona: int | None
    rol: Literal["USUARIO", "TECNICO", "ADMINISTRADOR"]
    unidades_autorizadas: list[int] | Literal["GLOBAL"]
    autenticacion_reciente: bool
    actualizacion_inicial_pendiente: bool | None
```

La identidad proviene siempre de la sesión, nunca de identificadores enviados por el cliente (`SEC-AUTZ-03`).

### Operaciones ofrecidas

| Operación | Responsabilidad | Falla con |
|---|---|---|
| `obtener_contexto()` | Resuelve el contexto autenticado y verifica que cuenta e identidad estén activas (`RN-AUTH-ID-01`, `RN-AUTH-ID-05`) | `401 NO_AUTENTICADO` |
| `exigir_permiso(codigo, id_unidad=None)` | Evalúa permiso y ámbito con información vigente (`RN-AUTH-ROL-05`, `SEC-AUTZ-04`) | `403 NO_AUTORIZADO` |
| `exigir_autenticacion_reciente()` | Verifica la ventana de reautenticación (`SEC-REAUTH-01`) | `401 REAUTENTICACION_REQUERIDA` |
| `exigir_perfil_inicial_completo()` | Consulta la condición vigente en Usuarios; se aplica a operaciones de negocio fuera del flujo permitido de actualización inicial. Para PERSONAL no aplica | `403 PERFIL_INICIAL_PENDIENTE` |

La comprobación de que un recurso concreto pertenece al actor —una reserva, un perfil, un archivo— corresponde al módulo propietario del recurso, que la ejecuta además del permiso general (`SEC-AUTZ-06`). `auth` no conoce la propiedad de entidades ajenas.

Ante imposibilidad de comprobar el permiso requerido, la decisión es denegar (`SEC-AUTZ-02`).

---

## 8. Auditoría

Generan registro de seguridad, sin contraseñas, secretos de sesión, tokens completos ni claves (`SEC-AUD-01`, `SEC-AUD-03`):

| Evento | Origen |
|---|---|
| Inicio de sesión exitoso e intentos fallidos relevantes | §3.2 |
| Cierre de sesión | §3.5 |
| Solicitud y confirmación de recuperación | §3.6, §3.8 |
| Cambio de contraseña y de correo | §5.1, §5.2 |
| Revocación de sesiones | §3.8, §5.1, §6.1 |
| Reautenticación sensible | §3.9 |
| Emisión, reenvío y activación de invitaciones | §4.1, §4.2, §4.4 |
| Cambios administrativos de cuenta e identidad | §6.1, §6.2 |

---

## 9. Definiciones pendientes

Este contrato asume estructuras que el modelo principal todavía no define, conforme advierte [data-model.md](../../modules/auth/data-model.md):

1. **Invitaciones** (§4): no existe tabla de invitaciones ni de sus tokens. `id_invitacion`, `estado` y `expira_en` son provisionales hasta especificarla.
2. **Recuperación de contraseña** (§3.6–§3.8): no existe tabla de tokens de recuperación.
3. **Permisos y ámbito** (§3.4, §7): no existen tablas de permisos ni de asignaciones. `rol` y `unidades_autorizadas` se presentan como contrato estable, pero su derivación persistente está pendiente y no debe deducirse del nombre del cargo ni del tipo de cuenta (`RN-PER-02`).
4. **Ventana de autenticación reciente** (§3.9): su duración es configuración pendiente de definir.
5. **Vigencias de sesión** (§2): la vigencia máxima y el tiempo de inactividad son configuración (`SEC-SES-09`) y no se fijan en este documento.

Mientras estas definiciones no existan, la superficie HTTP descrita puede implementarse, pero su respaldo persistente debe acordarse antes de construir los endpoints de §4 y la evaluación de permisos de §7.
