# Wireframes — Auth

## Alcance, fuentes y lectura

Nueve wireframes de baja fidelidad, uno por cada pantalla existente de [screens.md](screens.md). Fuentes revisadas: [user-flow.md](user-flow.md), [screen-flow.md](screen-flow.md), [business-rules.md](business-rules.md), [security.md](security.md) y [contrato API de Auth](../../contratos/auth/api-contract.md). Las variantes son estados de la misma pantalla, no pantallas nuevas.

Los bloques ASCII representan agrupación y orden de contenido, sin fijar dimensiones, estilos, tipografía, colores ni componentes. Para trasladarlos a Figma, conservar el identificador del wireframe y nombrar sus variantes por estado. Los nombres técnicos y referencias que aparecen fuera de los bloques son anotaciones de trazabilidad, no texto de interfaz.

Convenciones:

- `[campo: ______]` es una entrada; `[Acción]` es una acción respaldada por la Screen; `(dato)` es información de solo lectura. Las contraseñas se representan enmascaradas, sin un control adicional para revelarlas.
- `{mensaje}` es una región de respuesta en la misma pantalla, ausente cuando no hay mensaje. En validación puede acompañar al campo afectado. Las redacciones no fijadas por el contrato son textos de trabajo, sujetos a las mismas restricciones de seguridad.
- `→ destino` es una anotación de navegación, no un botón. Una zona marcada «pendiente» fuera de los bloques no inventa un selector ni un endpoint.
- La variación de carga conserva la estructura de la pantalla, sustituye la región de respuesta por el progreso textual y no representa un resultado antes de recibirlo. La variación bloqueada muestra la restricción y no permite completar la operación denegada; no fija duración local del bloqueo.
- Los campos y acciones que no cambian entre estados se conservan en el mismo lugar lógico. No se añaden botones de cancelar, volver, reintentar, confirmar contraseña, recordar sesión ni acciones de autoservicio.

### Estados y seguridad comunes

| Situación | Representación en la pantalla existente | Respaldo |
|---|---|---|
| Procesamiento | Región de mensaje: «Procesando…», concretada por operación; sin mensaje de éxito anticipado | Estados de screens.md |
| Validación de entradas | Mensaje junto al campo correspondiente; corrección y envío mediante la acción existente | `422 VALIDACION`, cuando el endpoint lo contempla |
| Operación no autorizada | «No se puede realizar esta operación.» en la región de respuesta; sin convertir la denegación en una explicación de permisos o datos privados | `SEC-AUTZ-01`, `SEC-AUTZ-02`, `SEC-AUTZ-04` |
| CSRF rechazado | Mismo estado de operación rechazada, sin campo, panel ni instrucciones técnicas para el usuario | Contrato §2; `SEC-CSRF-01`, `SEC-CSRF-02` |
| Limitación de intentos | «La operación está temporalmente limitada.»; sin contador, CAPTCHA o duración inventada | `SEC-ABU-01`, `SEC-ABU-03`; contrato §2 |
| Sesión no válida en una operación autenticada | Se interrumpe la operación y se conduce a SCR-AUTH-01; no se sustituye por reautenticación de una sesión inválida | `UF-AUTH-05`, `SEC-SES-07` |
| Autenticación reciente insuficiente | Se conduce a SCR-AUTH-07 y, tras éxito, se continúa en la operación pendiente | `UF-AUTH-09`, `SEC-REAUTH-01` |

Los códigos HTTP son anotaciones de compatibilidad, no mensajes para mostrar literalmente. No se muestran SQL, trazas, variables de entorno, hashes, secretos, tokens ni cookies (`SEC-INF-04`, `SEC-PWD-04`, `SEC-TOK-02`). Cookies, CSRF, auditoría y revocación son comportamiento interno, sin controles visuales propios. La autorización depende del servidor y del permiso concreto con su alcance, nunca de que un botón sea visible ni del nombre del rol.

La ayuda de nueva contraseña indica «Mínimo 8 caracteres, sin combinación obligatoria de mayúsculas, números o símbolos» (`SEC-PWD-07`). El contrato §3.1 concreta un máximo admitido de 64 para registro; no se inventa un máximo adicional para los demás formularios. Las contraseñas actuales de acceso y reautenticación no reciben validaciones nuevas de composición o longitud.

## WF-AUTH-01 — Iniciar sesión

Origen:

- SCR-AUTH-01.
- UF-AUTH-04; recibe las continuaciones de UF-AUTH-01, UF-AUTH-05, UF-AUTH-08 y UF-AUTH-11.

**Objetivo:** autenticar la cuenta y continuar según la condición de perfil. **Actor:** Usuario, Técnico o Administrador.

**Información visible:** petición de credenciales y resultado; necesidad de nueva autenticación cuando corresponda. **Entradas:** correo y contraseña. **Principal:** iniciar sesión. **Secundarias:** autorregistrarse y recuperar contraseña. Todos estos controles proceden de las entradas y acciones de SCR-AUTH-01.

### Estado principal

```text
+--------------------------------------------------+
| Iniciar sesión                                   |
|                                                  |
| Correo electrónico [________________________]    |
| Contraseña         [************************]    |
|                                                  |
| {Mensaje de validación o resultado}               |
| [Iniciar sesión]                                 |
|                                                  |
| [Autorregistrarse]   [Recuperar contraseña]       |
+--------------------------------------------------+
```

### Estados alternos

| Estado | Variación visual | Compatibilidad API |
|---|---|---|
| Carga | Mensaje: «Iniciando sesión…» | Espera de `POST /api/auth/sesiones`, §3.2 |
| Validación | Mensaje en las entradas afectadas por datos no válidos | `422 VALIDACION`; no aplicar reglas de contraseña nueva |
| Error | «No se pudo iniciar sesión con las credenciales proporcionadas.»; mismo formulario | `401 CREDENCIALES_INVALIDAS`: idéntico para correo inexistente, contraseña incorrecta, cuenta o identidad inactiva |
| Bloqueado | Mensaje común de limitación; no completa acceso | `429 DEMASIADOS_INTENTOS` |
| Sesión vencida/revocada | Antes de las entradas: «Debes iniciar sesión nuevamente.» | `UF-AUTH-05`; no revela por qué se desactivó una cuenta |
| Éxito | Mensaje transitorio «Inicio de sesión correcto.» y continuación; no añade botón ni pantalla de bienvenida | `201 Created`; condición `actualizacion_inicial_pendiente` |

### Navegación

- **Entrada:** opción de acceso; continuidad desde registro; restablecimiento/cambio de contraseña; exigencia de nueva autenticación.
- **Salida secundaria:** autorregistro → SCR-AUTH-02; recuperación → SCR-AUTH-05.
- **Salida correcta:** `USUARIO` pendiente → módulo usuarios / completar o reanudar perfil; `USUARIO` completado o `PERSONAL` → módulo propietario / operaciones autorizadas. No se dibuja el destino externo ni se inventa una página inicial (`RN-AUTH-SES-04`).
- **Errores:** permanecen en esta pantalla; no distinguen existencia de cuenta (`SEC-ABU-02`). No se garantiza retorno automático a una operación anterior tras iniciar sesión.

## WF-AUTH-02 — Autorregistrarse

Origen:

- SCR-AUTH-02.
- UF-AUTH-01.

**Objetivo:** solicitar el alta conjunta de perfil obligatorio y cuenta `USUARIO`. **Actor:** Persona sin cuenta.

**Información visible:** datos obligatorios, ayuda de contraseña, validaciones y respuesta pública. **Entradas:** correo, contraseña, nombre, documento, teléfono, institución y dependencia. **Principal:** enviar registro. **Secundarias tras la respuesta:** continuar al inicio de sesión y acceder a recuperación. No se permite elegir rol, tipo de cuenta o permisos.

### Estado principal

```text
+--------------------------------------------------+
| Autorregistrarse                                 |
| Todos los datos solicitados son obligatorios.     |
|                                                  |
| Correo electrónico [________________________]    |
| Contraseña         [************************]    |
| 8 a 64 caracteres. Sin composición obligatoria.   |
|                                                  |
| Nombre             [________________________]    |
| Documento          [________________________]    |
| Teléfono           [________________________]    |
| Institución        [________________________]    |
| Dependencia        [________________________]    |
|                                                  |
| {Mensajes de validación}                          |
| [Enviar registro]                                |
+--------------------------------------------------+
```

Los campos de perfil corresponden a cadenas en §3.1: nombre hasta 150 caracteres; documento y teléfono hasta 20; institución y dependencia hasta 255. No se dibujan catálogos, opciones ni máscaras de formato adicionales. Esas longitudes son restricciones de datos, no tamaños visuales.

### Estados alternos

```text
+--------------------------------------------------+
| Autorregistrarse — respuesta                     |
|                                                  |
| Si el correo puede registrarse, la cuenta         |
| quedará disponible para iniciar sesión.           |
|                                                  |
| [Continuar al inicio de sesión]                   |
| [Recuperar contraseña]                            |
+--------------------------------------------------+
```

Este resultado es el mismo ante alta creada y ante duplicado de correo, documento o teléfono: el `202` no permite dibujar una confirmación de cuenta creada. La orientación a recuperación se ofrece de forma equivalente, no solo cuando internamente hay duplicados (`SEC-ABU-02`, `SEC-REC-01`). Los dos controles corresponden a las acciones secundarias de SCR-AUTH-02.

| Estado | Variación visual | Compatibilidad API |
|---|---|---|
| Carga | Formulario con «Procesando registro…» | `POST /api/auth/registro`, §3.1 |
| Validación | Campo afectado y mensaje sobre ausencia, vacío, longitud o formato de correo; misma acción de envío | `422 VALIDACION` |
| Error de unicidad / alta correcta | Una sola variante pública, la representada arriba; no identifica el campo duplicado | `202 Accepted` idéntico |
| Bloqueado | Formulario con mensaje común de limitación | `429 DEMASIADOS_INTENTOS` |

### Navegación

- **Entrada:** opción de registro desde SCR-AUTH-01.
- **Salida:** continuar → SCR-AUTH-01; recuperación → SCR-AUTH-05. No inicia sesión automáticamente.
- **Posterior al acceso:** módulo usuarios / revisión y vinculaciones; la fuente de autorregistro cita UF-USR-01, sin diseñar su pantalla.
- **Errores:** corrección en esta pantalla; los conflictos de unicidad no producen una variante pública distinguible. El registro no completa la actualización inicial (`RN-AUTH-ID-06`).

## WF-AUTH-03 — Invitar o reenviar una invitación

Origen:

- SCR-AUTH-03.
- UF-AUTH-02.

**Objetivo:** emitir o reenviar una invitación de alta admitida. **Actor:** Administrador con `cuentas.administrar` global, identidad destinataria previamente creada.

**Información visible:** correo destino, tipo, unidad para `PERSONAL` y resultado. **Entradas:** correo, tipo de cuenta y unidad cuando corresponde. **Principal:** emitir invitación. **Secundaria contextual:** reenviar una invitación no completada. Corregir entradas usa el mismo formulario; no requiere otro botón.

### Estado principal

```text
+--------------------------------------------------+
| Invitar una cuenta                               |
|                                                  |
| Correo destino     [________________________]    |
| Tipo de cuenta     [USUARIO / PERSONAL]           |
|                                                  |
| Solo para PERSONAL:                              |
| Unidad del cargo   [________________________]    |
|                                                  |
| {Validación o resultado de emisión}               |
| [Emitir invitación]                              |
+--------------------------------------------------+
```

La entrada de unidad es una zona funcional sin decidir si será selección u otro mecanismo; no prescribe un catálogo. El servidor resuelve la identidad por correo y comprueba la unidad de su cargo, no la del emisor global (`RN-AUTH-ID-07`).

### Estados alternos

Variante de la misma Screen cuando el contexto ya identifica una invitación no completada:

```text
+--------------------------------------------------+
| Reenviar invitación                              |
|                                                  |
| Correo destino: (correo de la invitación)          |
| Tipo de cuenta: (USUARIO o PERSONAL)               |
| Unidad: (cuando corresponde)                      |
|                                                  |
| {Resultado de nueva emisión}                      |
| [Reenviar invitación]                            |
+--------------------------------------------------+
```

No se dibuja un listado ni un buscador para llegar a este contexto. El identificador de invitación procede del contexto, no de un campo adicional. El reenvío no vuelve a enviar los datos del formulario de emisión.

| Estado | Variación visual | Compatibilidad API |
|---|---|---|
| Carga | «Emitiendo invitación…» o «Reenviando invitación…» | Espera de §4.1 o §4.2 |
| Validación | Mensaje de corrección sobre correo, identidad previa o unidad según respuesta | `422 VALIDACION` de emisión |
| Éxito | «Invitación emitida.» / «Invitación reenviada.» en la misma vista; no afirma recepción del correo ni activación | `201 Created` de emisión; `200 OK` de reenvío |
| Conflicto | «No se puede emitir esta invitación.»; en cuenta administrativamente desactivada, orientación textual a reactivación administrativa | `409 CONFLICTO`, tanto emisión como reenvío; `RN-AUTH-ID-10` |
| No encontrada | «No se puede acceder a la invitación.»; no completa reenvío | `404 NO_ENCONTRADO` de reenvío |
| Acceso denegado | Mensaje común de operación no autorizada | `403 NO_AUTORIZADO` |
| Limitación, cuando aplique | Mensaje común de limitación, sin imponer duración | SCR-AUTH-03 y `SEC-ABU-01`; §4.1–§4.2 no concretan `429` propio ni marcan estas rutas como limitadas |

### Navegación

- **Entrada:** opción de invitar en el contexto de administración de cuentas; reenvío desde el contexto de invitación no completada. Localización pendiente de definición.
- **Salida correcta:** permanece en esta pantalla. Módulo notifications / entrega de correo; su apertura por la persona invitada inicia SCR-AUTH-04, no redirige al Administrador.
- **Errores:** permanecen en origen. La orientación a UF-AUTH-12 / SCR-AUTH-09 es texto, no un enlace o acceso nuevo inventado.
- **Dependencias:** usuarios para identidad `USUARIO`; administration para ficha `PERSONAL`, cargo, unidad y permisos. No se diseñan sus formularios.

## WF-AUTH-04 — Activar una cuenta invitada

Origen:

- SCR-AUTH-04.
- UF-AUTH-03.

**Objetivo:** completar una invitación válida definiendo contraseña. **Actor:** Persona invitada.

**Información visible:** posibilidad de activar, ayuda de contraseña y resultado. **Entrada:** contraseña. **Principal:** activar cuenta. **Secundarias:** ninguna acción adicional; la orientación a solicitar otra invitación es texto. No hay campo de token, selección de identidad ni selección de tipo.

### Estado principal

Tras validación del enlace:

```text
+--------------------------------------------------+
| Activar una cuenta invitada                       |
|                                                  |
| Define la contraseña de tu cuenta.                |
| Contraseña         [************************]    |
| Mínimo 8 caracteres. Sin composición obligatoria. |
|                                                  |
| {Validación o resultado}                          |
| [Activar cuenta]                                  |
+--------------------------------------------------+
```

### Estados alternos

```text
+--------------------------------------------------+
| Activar una cuenta invitada                       |
|                                                  |
| Esta invitación no puede utilizarse.              |
| Solicita una nueva invitación.                    |
+--------------------------------------------------+
```

La variante anterior representa `410`; no contiene un botón de reenvío. Para `409`, sustituir ambos mensajes por «No se puede completar la activación.», sin identificar una cuenta desactivada ni orientar a repetir invitaciones.

| Estado | Variación visual | Compatibilidad API |
|---|---|---|
| Inicial / validando enlace | Solo título y «Validando invitación…»; todavía sin formulario de contraseña | `GET /api/auth/invitaciones/{token}`, §4.3 |
| Enlace válido | Formulario principal; la validez del enlace no garantiza la posterior activación | `200 OK` |
| Procesamiento | «Activando cuenta…» | `POST /api/auth/invitaciones/{token}/activacion`, §4.4 |
| Contraseña corregible | Mensaje junto al campo; misma acción | `422 VALIDACION` |
| Identidad no válida | Mensaje seguro de rechazo y orientación a corregir la ficha mediante gestión administrativa y emitir invitación válida, sin mostrar detalles internos ni enlace público a administración | Validación de identidad de §4.1/§4.4 y SCR-AUTH-04; no confundir con conflicto de cuenta desactivada |
| Invitación no utilizable | Variante sin formulario de activación utilizable | `410 TOKEN_NO_VIGENTE` |
| Estado incompatible de cuenta | Mensaje genérico de conflicto; no activa ni inicia sesión | `409 CONFLICTO`; `RN-AUTH-ID-10` |
| Bloqueado | Mensaje común de limitación | `429 DEMASIADOS_INTENTOS` en activación |
| Éxito | «Cuenta activada.» y continuación, sin pedir de nuevo la contraseña | `201 Created`, sesión iniciada |

### Navegación

- **Entrada:** enlace recibido mediante notifications.
- **Salida correcta:** `USUARIO` → módulo usuarios / UF-USR-02; `PERSONAL` → módulo propietario / operaciones autorizadas. Ningún botón adicional para iniciar sesión.
- **Errores:** se muestran aquí; no se concede acceso público a SCR-AUTH-03 o SCR-AUTH-09. El estado incompatible de cuenta no se rotula como token vencido (`SEC-ABU-02`).
- **Abandono:** no completa la activación; destino de salida no definido, sin botón nuevo.

## WF-AUTH-05 — Solicitar recuperación de contraseña

Origen:

- SCR-AUTH-05.
- UF-AUTH-07.

**Objetivo:** solicitar recuperación sin revelar si existe cuenta. **Actor:** Persona con o sin cuenta; no requiere sesión.

**Información visible:** petición de correo y respuesta equivalente. **Entrada:** correo. **Principal:** solicitar recuperación. **Secundarias:** ninguna definida en SCR-AUTH-05.

### Estado principal

```text
+--------------------------------------------------+
| Recuperar contraseña                             |
|                                                  |
| Correo electrónico [________________________]    |
|                                                  |
| {Validación o respuesta}                          |
| [Solicitar recuperación]                          |
+--------------------------------------------------+
```

### Estados alternos

```text
+--------------------------------------------------+
| Recuperar contraseña — respuesta                  |
|                                                  |
| Si existe una cuenta asociada, se enviarán        |
| las instrucciones de recuperación.                |
+--------------------------------------------------+
```

| Estado | Variación visual | Compatibilidad API |
|---|---|---|
| Carga | «Procesando solicitud…» en el formulario | `POST /api/auth/recuperacion`, §3.6 |
| Validación | Mensaje sobre el correo enviado según error de entrada; no valida existencia visualmente | `422 VALIDACION`; no se añade una regla de formato propia |
| Respuesta / éxito público | Variante genérica anterior, igual exista o no cuenta; no anuncia «Correo enviado» | `202 Accepted`; `SEC-REC-01` |
| Bloqueado | Mensaje común de limitación | `429 DEMASIADOS_INTENTOS` |

### Navegación

- **Entrada:** recuperación desde SCR-AUTH-01 o respuesta de SCR-AUTH-02.
- **Salida:** permanece la respuesta en esta vista. Solo abrir el enlace recibido por correo inicia SCR-AUTH-06; no hay salto directo ni botón que sustituya ese enlace.
- **Errores:** validación/limitación en origen; inexistencia de cuenta no es una variante de error visible.
- **Dependencia:** notifications entrega el correo cuando corresponde. No se diseña bandeja, seguimiento o reenvío.

## WF-AUTH-06 — Restablecer la contraseña

Origen:

- SCR-AUTH-06.
- UF-AUTH-08.

**Objetivo:** establecer nueva contraseña mediante enlace válido. **Actor:** Persona titular de la cuenta.

**Información visible:** petición de nueva contraseña, validación del enlace y resultado. **Entrada:** nueva contraseña. **Principal:** restablecer contraseña. **Secundaria tras éxito:** iniciar sesión. No se solicita contraseña anterior.

### Estado principal

```text
+--------------------------------------------------+
| Restablecer la contraseña                         |
|                                                  |
| Nueva contraseña   [************************]    |
| Mínimo 8 caracteres. Sin composición obligatoria. |
|                                                  |
| {Validación o resultado}                          |
| [Restablecer contraseña]                          |
+--------------------------------------------------+
```

### Estados alternos

```text
+--------------------------------------------------+
| Restablecer la contraseña — resultado              |
|                                                  |
| Contraseña restablecida.                          |
| Debes iniciar sesión con la nueva contraseña.     |
|                                                  |
| [Iniciar sesión]                                  |
+--------------------------------------------------+
```

| Estado | Variación visual | Compatibilidad API |
|---|---|---|
| Inicial / validación del enlace | Solo título y «Validando enlace…»; no muestra aún entrada de contraseña | `GET /api/auth/recuperacion/{token}`, §3.7 |
| Enlace válido | Formulario principal | `200 OK` |
| Carga de cambio | «Restableciendo contraseña…» | `POST /api/auth/recuperacion/{token}`, §3.8 |
| Validación | Mensaje junto a contraseña para corregir longitud | `422 VALIDACION` |
| Enlace rechazado / bloqueado | Reemplaza formulario por «Este enlace no puede utilizarse. La contraseña no se ha cambiado.»; sin reenvío ni retorno adicional | `410 TOKEN_NO_VIGENTE` |
| Limitación | Mensaje común de limitación | `429 DEMASIADOS_INTENTOS` |
| Éxito | Variante de resultado anterior | `204 No Content`; mensaje local tras confirmación, no campo adicional del API |

### Navegación

- **Entrada:** apertura del enlace de recuperación entregado por notifications.
- **Salida:** acción «Iniciar sesión» → SCR-AUTH-01. Se revocan las sesiones y no se inicia otra automáticamente (`SEC-REC-05`).
- **Errores:** permanecen aquí; token inválido no se corrige con una entrada manual ni se renueva automáticamente.
- **Dependencia:** notifications informa del cambio, sin condición de confirmar recepción para continuar.

## WF-AUTH-07 — Reautenticarse para una operación sensible

Origen:

- SCR-AUTH-07.
- UF-AUTH-09; utilizado por UF-AUTH-11 y operaciones sensibles documentadas.

**Objetivo:** validar la contraseña actual para continuar la operación pendiente. **Actor:** Cuenta autenticada con sesión válida cuya autenticación reciente no satisface la ventana configurada.

**Información visible:** necesidad de reautenticarse y su resultado. **Entrada:** únicamente contraseña actual. **Principal:** validar contraseña y continuar. **Secundarias:** ninguna definida. No hay correo, recuperación, OTP, MFA, selector de cuenta ni cancelación añadida.

### Estado principal

```text
+--------------------------------------------------+
| Reautenticarse                                    |
|                                                  |
| Introduce tu contraseña actual para continuar.    |
| Contraseña actual  [************************]    |
|                                                  |
| {Resultado de la validación}                      |
| [Validar y continuar]                             |
+--------------------------------------------------+
```

### Estados alternos

| Estado | Variación visual | Compatibilidad API |
|---|---|---|
| Carga / validación | «Validando contraseña…» | `POST /api/auth/reautenticacion`, §3.9 |
| Error | «No se pudo validar la contraseña.»; operación pendiente sin ejecutar | `401 CREDENCIALES_INVALIDAS` |
| Bloqueado | Mensaje común de limitación; no continúa operación sensible | `429 DEMASIADOS_INTENTOS` |
| Sesión inválida | Interrumpe esta vista y requiere inicio de sesión | `401 NO_AUTENTICADO` → SCR-AUTH-01 |
| Éxito | «Validación completada.» y retorno al origen; sin un segundo botón | `200 OK`; no muestra identificadores, cookies ni cuenta regresiva de la ventana |

### Navegación

- **Entrada:** desde cambio de contraseña o una operación sensible de SCR-AUTH-09 / módulo propietario, solo cuando se requiere reautenticación explícita.
- **Salida correcta:** continúa a SCR-AUTH-08, retorna a SCR-AUTH-09 o al módulo propietario que originó la operación; administration es un origen externo documentado para gestión de permisos.
- **Condición de omisión:** si la autenticación reciente satisface la ventana configurada, esta vista no aparece (`SEC-REAUTH-01`).
- **Errores:** credenciales y límite permanecen aquí; sesión inválida requiere SCR-AUTH-01. La validación correcta no concede permisos ni ejecuta automáticamente una operación sin sus comprobaciones.

## WF-AUTH-08 — Cambiar la contraseña estando autenticado

Origen:

- SCR-AUTH-08.
- UF-AUTH-11, con UF-AUTH-09 cuando corresponde.

**Objetivo:** cambiar contraseña tras satisfacer la autenticación reciente exigida. **Actor:** Cuenta autenticada.

**Información visible:** petición de nueva contraseña, ayuda y resultado. **Entrada:** únicamente nueva contraseña. **Principal:** cambiar contraseña. **Secundaria condicional:** continuar por reautenticación mediante SCR-AUTH-07; es una transición, no un formulario duplicado ni un botón adicional.

### Estado principal

```text
+--------------------------------------------------+
| Cambiar contraseña                               |
|                                                  |
| Nueva contraseña   [************************]    |
| Mínimo 8 caracteres. Sin composición obligatoria. |
|                                                  |
| {Validación o resultado}                          |
| [Cambiar contraseña]                              |
+--------------------------------------------------+
```

### Estados alternos

```text
+--------------------------------------------------+
| Cambiar contraseña — resultado                    |
|                                                  |
| Contraseña actualizada.                           |
| Debes iniciar sesión con la nueva contraseña.     |
+--------------------------------------------------+
             → SCR-AUTH-01
```

La salida anterior no crea una décima pantalla ni agrega un botón a SCR-AUTH-08. Es el resultado seguido de la navegación documentada al acceso.

| Estado | Variación visual | Compatibilidad API |
|---|---|---|
| Pendiente de reautenticación | «Debes reautenticarte para continuar.» y transición a SCR-AUTH-07 antes de continuar el formulario | Consulta de condición en §3.4; `401 REAUTENTICACION_REQUERIDA` en §5.1 si deja de satisfacerse |
| Carga | «Cambiando contraseña…» | `PUT /api/auth/cuentas/actual/contrasena`, §5.1 |
| Validación | Mensaje junto a la nueva contraseña; misma acción de cambio | `422 VALIDACION` |
| Reautenticación fallida | El rechazo se representa en SCR-AUTH-07; no se modifica contraseña | `UF-AUTH-09`, `UF-AUTH-11` |
| Sesión inválida | Interrupción y SCR-AUTH-01 | `401 NO_AUTENTICADO` |
| Éxito | Resultado anterior y salida a inicio de sesión | `204 No Content`; todas las sesiones revocadas, incluida la actual; no crea sesión nueva (`SEC-SES-10`) |

### Navegación

- **Entrada:** opción de cambio desde contexto autenticado; si la ventana ya se cumple, acceso directo al formulario. Si no, SCR-AUTH-07 antes de continuar aquí.
- **Salida correcta:** SCR-AUTH-01; la nueva autenticación usa la nueva contraseña. La obtención de CSRF y eliminación de cookies del contrato son invisibles para el usuario.
- **Errores:** validación permanece aquí; falta de autenticación reciente → SCR-AUTH-07 → esta pantalla; sesión inválida → SCR-AUTH-01, sin prometer retorno automático.
- **Dependencia:** notifications informa del cambio; no se añade confirmación de correo.

## WF-AUTH-09 — Gestionar estado y tipo de identidad de una cuenta

Origen:

- SCR-AUTH-09.
- UF-AUTH-12 y UF-AUTH-13; UF-AUTH-09 para la operación sensible cuando corresponde.

**Objetivo:** cambiar estado o tipo de identidad de la cuenta objetivo conservando identificador e historial. **Actor:** Administrador con permiso global `cuentas.administrar`.

**Información visible:** cuenta objetivo, correo inmutable, estado, tipo e identidad asociada; resultado. **Entradas:** acción de estado, tipo destino e identidad destino. **Principales por operación:** desactivar/reactivar y aplicar cambio de tipo. **Secundarias:** ninguna adicional; permisos se administran fuera de Auth, sin botón inventado.

### Estado principal

```text
+--------------------------------------------------+
| Gestionar cuenta                                 |
|                                                  |
| Cuenta:            (cuenta objetivo)              |
| Correo:            (correo inmutable)             |
| Estado:            (activa / inactiva)            |
| Tipo:              (USUARIO / PERSONAL)           |
| Identidad:         (identidad asociada)           |
|                                                  |
| Estado de cuenta                                 |
| [Desactivar cuenta]                              |
|   Si está inactiva: [Reactivar cuenta]             |
| {Resultado de modificación de estado}             |
|                                                  |
| Cambiar tipo de identidad                         |
| Tipo destino       [USUARIO / PERSONAL]           |
| Identidad destino  [zona de entrada por definir]  |
| {Validación de identidad destino}                 |
| [Aplicar cambio de tipo]                          |
| {Resultado del cambio de tipo}                    |
+--------------------------------------------------+
```

La acción de estado se representa alternativamente según el estado actual, no como dos operaciones simultáneas. No hay «Guardar todo»: estado y tipo son operaciones separadas. La zona de identidad es un espacio funcional pendiente, no un buscador, catálogo ni campo de identificador manual decidido aquí. Solo admite la identidad correspondiente al tipo destino; el envío de `id_usuario` o `id_persona`, nunca ambos, pertenece al contrato §6.2.

### Estados alternos

| Estado | Variación visual | Compatibilidad API |
|---|---|---|
| Contexto inicial | Datos de la cuenta objetivo suministrados por el contexto existente; no se añade una llamada de consulta no documentada | Precondiciones de SCR-AUTH-09; mecanismo de acceso pendiente |
| Carga de modificación | Mensaje de progreso en el grupo de estado o de identidad que se está modificando | `PATCH /api/auth/cuentas/{id_cuenta}/estado` o `PUT /api/auth/cuentas/{id_cuenta}/identidad` |
| Éxito de estado | «Estado de cuenta actualizado.» y nuevo estado; cambia la acción de estado disponible | `200 OK`, §6.1; no añade listado de sesiones |
| Éxito de tipo | «Tipo de identidad actualizado.» y nuevo tipo/identidad; no anuncia permisos concedidos | `200 OK`, §6.2 |
| Validación de identidad | Mensaje junto a la zona de destino por correo incompatible, exclusividad o campos inválidos; no cambia el correo de la cuenta | `422 VALIDACION`, §6.2 |
| Cuenta/identidad no encontrada | Mensaje de rechazo sin mostrar datos inexistentes o fuera de acceso; no aplica el cambio | `404 NO_ENCONTRADO`, §6.1/§6.2 |
| Identidad inactiva u ocupada | «No se puede vincular la identidad seleccionada.»; conserva datos previos | `409 CONFLICTO`, §6.2 |
| Protección de última cuenta administrativa | «No se puede aplicar el cambio: debe conservarse al menos una cuenta administrativa válida.»; operación bloqueada | `409 CONFLICTO`; `RN-AUTH-ROL-09` |
| Acceso denegado | Mensaje común; no concede acceso ni deduce permisos del rol | `403 NO_AUTORIZADO`; `SEC-AUTZ-04` |
| Reautenticación | Operación pendiente → SCR-AUTH-07 → retorno a esta vista | `401 REAUTENTICACION_REQUERIDA` para cambio de identidad, §6.2; aplicar UF-AUTH-09 cuando corresponda, sin clasificar nuevas operaciones |

### Navegación

- **Entrada:** acceso administrativo a la cuenta objetivo; mecanismo de localización no definido. La orientación desde invitaciones no se convierte en un enlace directo nuevo.
- **Salida correcta:** permanece en esta vista con los valores confirmados. Si la sesión del propio actor deja de ser válida, rige UF-AUTH-05 y se conduce a SCR-AUTH-01.
- **Retorno de reautenticación:** SCR-AUTH-07 → SCR-AUTH-09 para continuar la operación pendiente.
- **Errores:** en el grupo correspondiente, sin ejecutar el cambio. La cuenta desactivada después de completar alta solo se reactiva aquí, no mediante invitación (`RN-AUTH-ID-10`).
- **Dependencias:** usuarios / identidades `USUARIO`; administration / identidad `PERSONAL`, permisos y auditoría. No se diseñan pantallas de selección externas ni gestión de permisos.

## Dependencias y límites del cierre visual

| Pantallas | Información pendiente o límite | Tratamiento en los wireframes |
|---|---|---|
| SCR-AUTH-03 | Localización de invitación para reenvío; mecanismo de captura de unidad; datos de contexto que alimentan la variante de reenvío | La estructura está representada, pero esos controles/contextos no están cerrados para detalle en Figma. No se inventa un listado ni un endpoint de consulta |
| SCR-AUTH-09 | Acceso a cuenta objetivo, fuente de sus datos y mecanismo de selección de identidad destino; el contrato Auth no expone aquí una consulta de cuenta ajena | Zona funcional pendiente. No puede cerrarse por completo la interacción de selección con estas fuentes |
| SCR-AUTH-01 y SCR-AUTH-04; continuidad de SCR-AUTH-02 | Destino concreto de la aplicación y referencias distintas de perfil: UF-USR-01 desde autorregistro, UF-USR-02 desde activación | El formulario Auth puede cerrarse; la navegación externa conserva los destinos funcionales existentes, sin resolver su correspondencia silenciosamente |
| SCR-AUTH-04 | Canal concreto para pedir nueva invitación y gestión de corrección de ficha | Orientación textual; no autoservicio ni enlace público a administración |
| SCR-AUTH-03, SCR-AUTH-05, SCR-AUTH-06 y SCR-AUTH-08 | Entrega de correo por notifications | No se representa recepción garantizada, seguimiento ni interfaz de correo |
| SCR-AUTH-03 | screens.md contempla limitación «cuando aplique», pero emisión/reenvío no están marcados como limitados en el contrato | Variante condicional documentada; no afirmar un `429` propio como respuesta ya fijada para estas rutas |
| Todas | Retornos al abandonar no fijados por las fuentes | No se agregan botones de retorno o cancelación |

El registro puede representarse con entradas de texto gracias a los tipos y longitudes de §3.1 del contrato; no se inventan catálogos de institución o dependencia. Su estado de éxito visible se unifica con el resultado público genérico, aunque internamente exista una rama de alta creada en el flujo. Esta distinción evita revelar duplicados y no cambia las fuentes.

UF-AUTH-05 (mantener sesión), UF-AUTH-06 (cerrar sesión) y UF-AUTH-10 (autorizar) no reciben wireframe propio. Sus efectos son continuidad, interrupción, retorno a acceso o rechazo en la vista solicitante. El cierre sigue siendo la acción del contexto autenticado documentado, sin diseñar un contenedor de aplicación o una pantalla adicional.

## Matriz de cobertura y estados

| Wireframe | Screen | User Flow | Estados representados |
|---|---|---|---|
| WF-AUTH-01 | SCR-AUTH-01 | UF-AUTH-04; entradas de UF-AUTH-01, UF-AUTH-05, UF-AUTH-08 y UF-AUTH-11 | Inicial, carga, validación, credenciales rechazadas, bloqueo por intentos, sesión inválida, éxito y salida externa |
| WF-AUTH-02 | SCR-AUTH-02 | UF-AUTH-01 | Inicial, carga, corrección, respuesta genérica compartida por alta y duplicados, bloqueo, continuación a acceso/recuperación |
| WF-AUTH-03 | SCR-AUTH-03 | UF-AUTH-02 | Emisión, reenvío contextual, carga, validación, conflicto, no encontrada, denegación, limitación condicional, éxito |
| WF-AUTH-04 | SCR-AUTH-04 | UF-AUTH-03 | Validación inicial de enlace, captura, carga, corrección, identidad no válida, enlace rechazado, conflicto genérico, limitación, éxito con sesión y salida externa |
| WF-AUTH-05 | SCR-AUTH-05 | UF-AUTH-07 | Inicial, carga, validación, respuesta genérica, limitación; entrada posterior por correo separada |
| WF-AUTH-06 | SCR-AUTH-06 | UF-AUTH-08 | Validación de enlace, captura, carga, corrección, enlace bloqueado, limitación, éxito y nuevo inicio de sesión |
| WF-AUTH-07 | SCR-AUTH-07 | UF-AUTH-09; uso por UF-AUTH-11 y UF-AUTH-13 | Contraseña actual requerida, validación/carga, error, limitación, sesión inválida, éxito y retorno al origen; omisión por autenticación reciente |
| WF-AUTH-08 | SCR-AUTH-08 | UF-AUTH-11; UF-AUTH-09 | Entrada directa o reautenticación previa, captura, carga, validación, rechazo, sesión inválida, éxito con revocación total y salida a acceso |
| WF-AUTH-09 | SCR-AUTH-09 | UF-AUTH-12, UF-AUTH-13; UF-AUTH-09 | Consulta contextual, carga, validación, conflicto, no encontrado, bloqueo de última cuenta administrativa, denegación, reautenticación, éxito de estado/tipo |
