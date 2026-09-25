# Seguridad de autenticación y autorización

Este documento define los controles técnicos de seguridad del módulo `auth`. Las reglas funcionales de identidad, autenticación y autorización se encuentran en [business-rules.md](business-rules.md).

Los controles aquí definidos complementan las reglas de negocio y deben aplicarse en backend, infraestructura y cliente cuando corresponda.

---

## Contraseñas — SEC-PWD

- **SEC-PWD-01:** Las contraseñas nunca deben almacenarse en texto plano ni mediante cifrado reversible.

- **SEC-PWD-02:** Las contraseñas deben almacenarse mediante una función de derivación diseñada para almacenamiento de contraseñas. Para nuevas implementaciones se debe preferir `Argon2id`. Si la implementación utiliza `bcrypt`, debe emplear un factor de trabajo adecuado a la capacidad del servidor y respetar las limitaciones de longitud propias del algoritmo.

- **SEC-PWD-03:** Cada contraseña debe utilizar un `salt` único generado de forma segura. Cuando el algoritmo seleccionado administre el `salt` internamente, no debe implementarse un mecanismo paralelo manual.

- **SEC-PWD-04:** Los hashes de contraseñas nunca deben exponerse al frontend, incluirse en respuestas de API, registros de aplicación ni mensajes de error.

- **SEC-PWD-05:** El sistema no debe registrar contraseñas, tokens de recuperación, secretos de sesión ni otras credenciales en logs.

- **SEC-PWD-06:** Cuando se utilice `Argon2id`, la configuración mínima debe ser 19 MiB de memoria, 2 iteraciones y paralelismo de 1. Cuando se utilice `bcrypt`, el factor de trabajo mínimo debe ser 10. Estos valores son mínimos y deben incrementarse según la capacidad del servidor sin degradar el tiempo de respuesta aceptable para el usuario.

- **SEC-PWD-07:** La contraseña debe aceptar un mínimo de 8 caracteres y permitir al menos 64 caracteres, sin imponer reglas obligatorias de composición como mayúsculas, símbolos o números, ni expiración periódica forzada sin evidencia de compromiso.

---

## Sesiones — SEC-SES

- **SEC-SES-01:** Las sesiones autenticadas deben estar representadas y controladas por `auth.sesiones`.

- **SEC-SES-02:** El identificador o secreto de sesión debe generarse mediante un generador criptográficamente seguro y no debe contener información personal, permisos, identificadores internos interpretables ni otros datos sensibles.

- **SEC-SES-03:** El secreto de sesión del navegador debe transportarse exclusivamente mediante una cookie configurada con `HttpOnly` y `Secure`.

- **SEC-SES-04:** La cookie de sesión debe declarar explícitamente una política `SameSite` compatible con el flujo funcional de la aplicación. `Lax` puede utilizarse como valor por defecto cuando sea compatible; `Strict` debe utilizarse únicamente cuando no interfiera con navegaciones legítimas requeridas por la aplicación.

- **SEC-SES-05:** La cookie de sesión no debe almacenarse ni replicarse en `localStorage`, `sessionStorage`, IndexedDB u otro almacenamiento accesible desde JavaScript.

- **SEC-SES-06:** Toda comunicación autenticada debe utilizar HTTPS. El identificador de sesión nunca debe transmitirse mediante HTTP sin cifrar.

- **SEC-SES-07:** Una sesión vencida, revocada o cerrada debe rechazarse en el servidor aunque el cliente conserve una cookie previa.

- **SEC-SES-08:** Cerrar sesión debe invalidar la sesión correspondiente en `auth.sesiones` y eliminar la cookie de sesión del cliente sin esperar su vencimiento natural.

- **SEC-SES-09:** Las sesiones deben tener tiempo máximo de vigencia y tiempo máximo de inactividad definidos por configuración. Al superar cualquiera de los límites aplicables, se debe exigir una nueva autenticación.

- **SEC-SES-10:** Después de un cambio de contraseña exitoso, el sistema debe revocar todas las sesiones activas de la cuenta, incluida la sesión actual. No crea automáticamente una nueva sesión; la persona debe iniciar sesión nuevamente con la nueva contraseña. Ante otros eventos que comprometan la confianza en las credenciales, debe revocar las sesiones activas según la política aplicable.

- **SEC-SES-11:** Las respuestas que establezcan o contengan información sensible de sesión deben utilizar controles de caché que impidan su almacenamiento cuando corresponda.

- **SEC-SES-12:** El identificador de sesión debe generarse con al menos 128 bits aleatorios obtenidos mediante un generador criptográficamente seguro.

- **SEC-SES-13:** El identificador de sesión debe regenerarse tras un inicio de sesión exitoso y tras cualquier elevación del nivel de privilegio de la cuenta, invalidando el identificador anterior para prevenir fijación de sesión.

---

## Protección contra CSRF — SEC-CSRF

- **SEC-CSRF-01:** El uso de cookies para autenticación requiere protección contra solicitudes falsificadas entre sitios en las operaciones que modifican estado.

- **SEC-CSRF-02:** La protección CSRF debe implementarse en el servidor mediante un mecanismo explícito compatible con la arquitectura de la aplicación. `SameSite` se considera una defensa adicional y no sustituye por sí solo la protección CSRF cuando esta sea necesaria.

- **SEC-CSRF-03:** Las operaciones que modifican estado no deben ejecutarse mediante métodos HTTP destinados únicamente a lectura, como `GET`.

---

## Tokens de acceso y secretos — SEC-TOK

- **SEC-TOK-01:** Todo token utilizado para autenticar, autorizar temporalmente o restablecer una sesión debe validarse completamente antes de aceptar la operación correspondiente.

- **SEC-TOK-02:** Los secretos, claves privadas, refresh tokens, hashes de contraseñas y credenciales de infraestructura no deben exponerse al frontend ni mediante endpoints de consulta.

- **SEC-TOK-03:** Las claves criptográficas y secretos de infraestructura deben suministrarse mediante mecanismos de configuración segura y no deben almacenarse directamente en el código fuente ni incluirse en el repositorio.

- **SEC-TOK-04:** Los tokens temporales de invitación y recuperación deben generarse de forma criptográficamente segura, tener vigencia limitada y ser de un solo uso.

- **SEC-TOK-05:** Un token temporal utilizado, vencido o revocado debe rechazarse en intentos posteriores.

---

## JWT — SEC-JWT

Estas reglas aplican únicamente cuando el sistema utilice JWT para tokens firmados.

- **SEC-JWT-01:** La validación de un JWT debe fijar explícitamente en el servidor el algoritmo de firma esperado. Un token que declare `alg: none` o un algoritmo distinto al configurado debe rechazarse.

- **SEC-JWT-02:** La validación debe comprobar la firma y, cuando correspondan al diseño del token, el emisor (`iss`), la audiencia (`aud`), la expiración (`exp`) y el propósito o tipo esperado.

- **SEC-JWT-03:** El payload de un JWT no debe considerarse confidencial. No debe incluir contraseñas, secretos, información sensible ni datos personales que no sean estrictamente necesarios.

- **SEC-JWT-04:** El servidor no debe confiar en permisos, roles o ámbitos incluidos en un JWT cuando las reglas de autorización requieran validar información vigente en el sistema.

- **SEC-JWT-05:** Un JWT vencido, revocado o asociado a una sesión inválida debe rechazarse aunque su firma sea válida.

---

## Recuperación y cambio de contraseña — SEC-REC

- **SEC-REC-01:** La solicitud de recuperación de contraseña debe responder de forma equivalente exista o no una cuenta asociada al identificador proporcionado, evitando revelar qué cuentas están registradas.

- **SEC-REC-02:** El proceso de recuperación debe utilizar un token temporal asociado a una cuenta específica, con vigencia limitada y de un solo uso.

- **SEC-REC-03:** La nueva contraseña solo podrá establecerse después de validar correctamente el token de recuperación.

- **SEC-REC-04:** Un cambio de contraseña exitoso debe generar una notificación a la cuenta afectada conforme a las reglas y canales definidos en el módulo de notificaciones.

- **SEC-REC-05:** Una recuperación de contraseña exitosa debe revocar las sesiones activas existentes de la cuenta y exigir nueva autenticación.

---

## Invitaciones — SEC-INV

- **SEC-INV-01:** Los enlaces de invitación deben utilizar tokens impredecibles, de vigencia limitada y de un solo uso.

- **SEC-INV-02:** Una invitación vencida, utilizada o revocada no puede completar el proceso de alta.

- **SEC-INV-03:** Emitir una nueva invitación debe invalidar cualquier invitación anterior que no deba continuar siendo válida para el mismo proceso de alta.

- **SEC-INV-04:** El token de invitación no debe conceder permisos superiores a los definidos por la invitación almacenada y validada en el servidor.

---

## Reautenticación para operaciones sensibles — SEC-REAUTH

- **SEC-REAUTH-01:** Las operaciones sensibles deben requerir una autenticación reciente o una reautenticación explícita cuando el nivel de riesgo lo justifique.

- **SEC-REAUTH-02:** Como mínimo, deben considerarse operaciones sensibles el cambio de contraseña, la asignación o modificación de permisos administrativos y otras acciones que puedan alterar el control de la cuenta.

- **SEC-REAUTH-03:** La reautenticación debe validar únicamente la contraseña actual de la cuenta identificada por la sesión. No solicita nuevamente correo ni incorpora OTP, MFA u otros factores. La existencia de una sesión activa antigua no sustituye esta validación.

- **SEC-REAUTH-04:** Después de una reautenticación exitosa que implique elevación de privilegios o cambio sensible de seguridad, el identificador de sesión debe regenerarse conforme a `SEC-SES-13`.

---

## Protección contra abuso — SEC-ABU

- **SEC-ABU-01:** Los endpoints de inicio de sesión, recuperación de contraseña, validación de invitaciones y otras operaciones de autenticación sensibles deben aplicar limitación de intentos o mecanismos equivalentes contra abuso automatizado.

- **SEC-ABU-02:** Los mensajes de error de autenticación no deben revelar innecesariamente si falló el correo, la contraseña, la existencia de la cuenta u otro dato que facilite enumeración de usuarios.

- **SEC-ABU-03:** Los controles contra abuso no deben utilizarse como fuente de autorización. Superarlos no implica que la operación esté permitida.

---

## Autorización técnica — SEC-AUTZ

- **SEC-AUTZ-01:** Toda autorización debe validarse en el servidor. Ocultar botones, rutas o controles en el frontend no constituye un control de autorización.

- **SEC-AUTZ-02:** El backend debe denegar por defecto una operación cuando no pueda comprobar de forma válida el permiso requerido.

- **SEC-AUTZ-03:** Los identificadores enviados por el cliente nunca sustituyen la identidad obtenida de la sesión autenticada.

- **SEC-AUTZ-04:** Las operaciones sobre recursos pertenecientes a una unidad organizacional deben validar en el servidor tanto el permiso requerido como el ámbito organizacional aplicable. Para roles administrativos, la cuenta debe ser de tipo `PERSONAL` y estar vinculada a una identidad de personal activa. El alcance depende de la asignación concreta del permiso requerido: una asignación global permite ejecutarlo globalmente; una asignación por unidad exige coincidencia entre unidad asignada, unidad del recurso y unidad de la identidad mediante su cargo vigente, aunque el actor sea Administrador. El rol Administrador no concede permisos por sí mismo y una asignación global no amplía otros permisos por unidad (`RN-AUTH-ROL-02`, `RN-AUTH-ROL-03`, `RN-AUTH-ROL-06`, `RN-AUTH-ROL-07`).

- **SEC-AUTZ-05:** Los cambios de cargo, unidad, permisos o estado del personal deben reflejarse en las autorizaciones posteriores sin depender exclusivamente de información almacenada previamente en el cliente.

- **SEC-AUTZ-06:** Toda operación sobre un recurso identificado mediante un valor enviado por el cliente, como una reserva, perfil o archivo, debe verificar en el servidor que dicho recurso pertenece o está explícitamente permitido para la identidad autenticada. Contar con el permiso general de la operación no sustituye la validación de propiedad, pertenencia o vínculo específico con el recurso solicitado.

---

## Auditoría de seguridad — SEC-AUD

- **SEC-AUD-01:** Los eventos de autenticación y seguridad relevantes deben generar registros suficientes para investigación y trazabilidad sin almacenar secretos.

- **SEC-AUD-02:** Deben registrarse como mínimo los eventos de inicio de sesión exitoso, intentos fallidos relevantes, cierre de sesión, recuperación o cambio de contraseña, revocación de sesiones, reautenticaciones sensibles y cambios administrativos de permisos cuando corresponda.

- **SEC-AUD-03:** Los registros de auditoría no deben contener contraseñas, secretos de sesión, tokens completos ni claves privadas.

- **SEC-AUD-04:** El acceso a los registros de seguridad debe estar restringido a las cuentas y servicios expresamente autorizados.

---

## Transporte y configuración — SEC-INF

- **SEC-INF-01:** La aplicación debe utilizar HTTPS en producción para todas las rutas autenticadas y para cualquier operación que transporte credenciales o tokens.

- **SEC-INF-02:** La configuración de producción no debe utilizar credenciales, claves o secretos por defecto.

- **SEC-INF-03:** Los secretos de producción deben mantenerse fuera del repositorio de código y separarse de la configuración pública del frontend.

- **SEC-INF-04:** Las respuestas de error expuestas al cliente no deben incluir trazas internas, secretos, consultas SQL, variables de entorno ni información sensible de infraestructura.

---

## Decisiones que deben mantenerse consistentes

1. `auth.cuentas` representa la cuenta autenticable.
2. `auth.sesiones` mantiene el estado de las sesiones autenticadas.
3. El navegador no administra directamente secretos de autenticación mediante almacenamiento accesible desde JavaScript.
4. La autenticación y la autorización se validan en el servidor.
5. Las reglas funcionales de permisos permanecen en `business-rules.md`; este documento define los controles técnicos para hacerlas cumplir de forma segura.
6. Los controles JWT solo aplican si JWT forma parte de la arquitectura de autenticación implementada.

---

## Referencias técnicas

- OWASP Cheat Sheet Series — Password Storage Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
- OWASP Cheat Sheet Series — Session Management Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html
- OWASP Cheat Sheet Series — Authentication Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
- OWASP Cheat Sheet Series — Forgot Password Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html
- OWASP Cheat Sheet Series — Cross-Site Request Forgery Prevention Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html
- OWASP Cheat Sheet Series — JSON Web Token for Java Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html
- OWASP Cheat Sheet Series — Authorization Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html
- NIST SP 800-63B — Authentication and Authenticator Management: https://pages.nist.gov/800-63-4/sp800-63b.html
