# Pruebas — Auth

Qué debe verificarse en sesión, credenciales, invitaciones y autorización. Convenciones en [testing.md](../../docs/testing.md).

Es el único módulo donde **el tiempo de respuesta forma parte del resultado**: varias reglas exigen que dos casos distintos sean indistinguibles desde fuera, y una diferencia de milisegundos los distingue.

---

## Token y sesión

### T-AUTH-01 — El token no lleva rol ni permisos

- **Nivel:** servicio
- **Cubre:** `SEC-JWT-04`
- **Caso:** se emite un token para una cuenta con permisos administrativos y se inspeccionan sus claims.
- **Esperado:** contiene `iss`, `aud`, `sub`, `sid`, `typ`, `iat` y `exp`, y **ningún rol ni permiso**. Si estuvieran, revocar un permiso no surtiría efecto hasta que el token expirase.

### T-AUTH-02 — Un token manipulado se rechaza

- **Nivel:** servicio
- **Cubre:** `SEC-JWT-01`, `SEC-JWT-02`, `SEC-JWT-05`
- **Caso:** se presentan tokens con `alg: none`, con un algoritmo distinto al esperado, con `aud` ajena y con `typ` incorrecto.
- **Esperado:** los cuatro se rechazan.

### T-AUTH-03 — Una sesión revocada o vencida no sirve

- **Nivel:** contrato
- **Cubre:** `SEC-SES-07`, `SEC-SES-09`
- **Caso:** se usa la cookie de una sesión revocada, de una vencida por vigencia máxima y de una vencida por inactividad.
- **Esperado:** `401` en los tres casos, aunque la firma del token siga siendo válida.

### T-AUTH-04 — El token no viaja en el cuerpo

- **Nivel:** contrato
- **Cubre:** `SEC-SES-03`, `SEC-SES-05`
- **Caso:** se inicia sesión correctamente y se inspecciona la respuesta completa.
- **Esperado:** el cuerpo no contiene el token. Las cookies son `HttpOnly` y `Secure`, y la de renovación limita su `Path`.

### T-AUTH-05 — El identificador de sesión se regenera

- **Nivel:** servicio
- **Cubre:** `SEC-SES-13`, `SEC-REAUTH-04`
- **Caso:** se inicia sesión teniendo una previa, y después se reautentica.
- **Esperado:** el identificador cambia en ambos momentos.

---

## CSRF y autorización

### T-AUTH-06 — Una escritura sin CSRF se rechaza

- **Nivel:** contrato
- **Cubre:** `SEC-CSRF-01`, `SEC-CSRF-02`
- **Caso:** se envía un `POST` con sesión válida pero sin `X-CSRF-Token`, y otro con un valor que no coincide con la cookie.
- **Esperado:** `403` en ambos. `GET /api/auth/csrf` emite la cookie **sin exigir sesión previa**.

### T-AUTH-07 — Sin poder comprobar el permiso, deniega

- **Nivel:** servicio
- **Cubre:** `SEC-AUTZ-02`, `SEC-AUTZ-04`
- **Caso:** se evalúa una operación protegida cuando la información de permisos no puede consultarse.
- **Esperado:** deniega. **El fallo abierto no es una opción**, y esta prueba es la que lo acredita.

### T-AUTH-08 — El ámbito del Técnico es su unidad vigente

- **Nivel:** servicio
- **Cubre:** `RN-AUTH-ROL-05`, `RN-AUTH-ROL-06`, `SEC-AUTZ-01`
- **Caso:** un Técnico con asignaciones en dos unidades, de las cuales solo una corresponde a su cargo vigente, opera sobre ambas.
- **Esperado:** procede únicamente en la del cargo vigente. `unidades_autorizadas` **no es la unión** de sus asignaciones.

### T-AUTH-09 — La identidad no viene del cliente

- **Nivel:** contrato
- **Cubre:** `SEC-AUTZ-03`
- **Caso:** se envía una operación incluyendo un identificador de cuenta distinto al de la sesión.
- **Esperado:** se ignora el enviado y se usa el de la sesión.

---

## No enumeración

### T-AUTH-10 — El inicio de sesión no distingue la causa

- **Nivel:** contrato
- **Cubre:** `RN-AUTH-ID-01`, `SEC-ABU-02`
- **Caso:** se intenta iniciar sesión con contraseña incorrecta, correo inexistente, cuenta inactiva e identidad inactiva.
- **Esperado:** el mismo `401 CREDENCIALES_INVALIDAS` en los cuatro, **sin diferencias observables de cuerpo ni de tiempo**.

### T-AUTH-11 — Registro y recuperación responden igual

- **Nivel:** contrato
- **Cubre:** `SEC-REC-01`, `SEC-ABU-02`
- **Caso:** se registra y se solicita recuperación con un correo existente y con uno que no lo está.
- **Esperado:** respuestas idénticas. La ausencia de filas para un correo no se expone de ninguna forma.

### T-AUTH-12 — El límite de intentos no concede acceso

- **Nivel:** contrato
- **Cubre:** `SEC-ABU-01`, `SEC-ABU-03`
- **Caso:** se superan los intentos permitidos en un endpoint limitado y luego se envían credenciales correctas.
- **Esperado:** `429 DEMASIADOS_INTENTOS` con `Retry-After`; **superar el límite no autoriza nada**.

---

## Tokens de un solo uso

### T-AUTH-13 — El token de recuperación se gasta

- **Nivel:** contrato
- **Cubre:** `SEC-TOK-05`, `SEC-REC-03`
- **Caso:** se restablece la contraseña con un token válido y se reutiliza el mismo token.
- **Esperado:** el segundo intento responde `410`. El restablecimiento **revoca todas las sesiones** de la cuenta.

### T-AUTH-14 — Reenviar una invitación invalida la anterior

- **Nivel:** contrato
- **Cubre:** `SEC-INV-02`, `SEC-INV-03`
- **Caso:** se emite una invitación, se reenvía, y se intenta activar con el primer token.
- **Esperado:** el primero ya no sirve. Una invitación vencida, usada o revocada tampoco completa el alta.

### T-AUTH-15 — El token nunca aparece en una respuesta

- **Nivel:** contrato
- **Cubre:** `SEC-TOK-02`, `SEC-INV-01`
- **Caso:** se emite una invitación y se solicita una recuperación, inspeccionando ambas respuestas completas.
- **Esperado:** ninguna contiene el token. Viaja solo por correo y se almacena como hash.

### T-AUTH-16 — La activación usa los datos almacenados

- **Nivel:** servicio
- **Cubre:** `SEC-INV-04`, `RN-AUTH-ID-03`
- **Caso:** se activa una invitación enviando un tipo de cuenta y una identidad distintos a los que guarda la invitación.
- **Esperado:** se aplican los almacenados. El cliente no elige su propio tipo de cuenta.

---

## Operaciones sensibles y administración

### T-AUTH-17 — Sin autenticación reciente no hay operación sensible

- **Nivel:** contrato
- **Cubre:** `SEC-REAUTH-01`, `SEC-REAUTH-02`
- **Caso:** se cambia la contraseña y la identidad de una cuenta con una sesión válida pero antigua.
- **Esperado:** `401 REAUTENTICACION_REQUERIDA` hasta reautenticarse.

### T-AUTH-18 — Desactivar una cuenta corta sus sesiones

- **Nivel:** servicio
- **Cubre:** `SEC-SES-10`, `RN-AUTH-ID-05`
- **Caso:** se desactiva una cuenta con sesiones abiertas y después se reactiva.
- **Esperado:** las sesiones quedan revocadas, el historial se conserva y reactivar **no crea una identidad nueva**.

### T-AUTH-19 — El sistema no se queda sin administradores

- **Nivel:** contrato
- **Cubre:** `RN-AUTH-ROL-09`
- **Caso:** se desactiva o degrada la última cuenta con permiso global vigente.
- **Esperado:** `409 CONFLICTO`.

### T-AUTH-20 — Las contraseñas no se guardan ni se registran en claro

- **Nivel:** servicio
- **Cubre:** `SEC-PWD-01`, `SEC-PWD-04`, `SEC-PWD-05`
- **Caso:** se crea una cuenta y se inspeccionan la base, la respuesta y los registros de aplicación.
- **Esperado:** la contraseña no aparece en ninguno de los tres, ni su hash en la respuesta.
