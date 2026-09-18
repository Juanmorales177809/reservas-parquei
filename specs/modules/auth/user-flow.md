# User Flows — Auth

Este documento define los flujos de usuario del módulo `auth`. Las reglas funcionales se definen en [business-rules.md](business-rules.md), los controles técnicos en [security.md](security.md) y las entidades persistentes en [data-model.md](data-model.md).

El módulo `auth` administra cuenta, credenciales, sesión y decisiones de autorización. No administra el perfil funcional del reservista (módulo `usuarios`), ni la configuración institucional de personas, unidades y permisos (módulo `administration`), ni las reglas de ningún dominio operativo.

Roles funcionales usados en este documento (`RN-AUTH-ROL-01`):

- **Usuario:** cuenta vinculada a `usuarios.usuarios`. No posee permisos administrativos por el hecho de tener cuenta o vinculación académica (`RN-AUTH-ROL-04`).
- **Técnico:** cuenta vinculada a `personal.personal`. Solo puede ejecutar operaciones administrativas sobre su propia unidad organizacional (`RN-AUTH-ROL-02`).
- **Administrador:** alcance global sobre las unidades organizacionales (`RN-AUTH-ROL-03`).

En todos los flujos, la autenticación y la autorización se resuelven en el servidor; ocultar controles en el cliente no constituye un control de acceso (`SEC-AUTZ-01`).

---

## UF-AUTH-01 — Autorregistrarse

**Rol principal:** Persona sin cuenta

**Precondiciones:**
- La persona no tiene una cuenta asociada al correo que va a registrar.
- El autorregistro no requiere invitación previa.

**Flujo principal:**

1. La persona accede a la opción de registro.
2. El sistema solicita correo electrónico, contraseña y los datos obligatorios de Usuario definidos en RN-DAT: nombre, documento, teléfono, institución y dependencia.
3. La persona diligencia los datos.
4. El sistema valida el formato del correo y que la contraseña cumpla la longitud admitida, sin imponer reglas de composición (`SEC-PWD-07`); delega en `usuarios` la validación de los datos del perfil y la unicidad de documento y teléfono conforme a RN-DAT.
5. El sistema verifica que el correo no corresponda a una cuenta existente (`RN-AUTH-ID-02`).
6. El sistema deriva el hash de la contraseña mediante la función de almacenamiento definida y nunca conserva la contraseña en texto plano (`SEC-PWD-01`, `SEC-PWD-02`, `SEC-PWD-03`).
7. El sistema crea, en una única transacción, la identidad funcional en `usuarios.usuarios` con los datos obligatorios y su cuenta de tipo `USUARIO` (`RN-AUTH-ID-03`, `RN-AUTH-ID-04`). Si falla una validación o restricción única, no crea ninguno de los dos registros.
8. La cuenta queda activa y sin permisos administrativos (`RN-AUTH-ROL-04`).
9. El sistema registra el evento de creación de cuenta para trazabilidad (`SEC-AUD-01`).
10. La persona continúa con el inicio de sesión (`UF-AUTH-04`) y con la revisión de datos y el completado de vinculaciones del módulo `usuarios` (`UF-USR-01`); el alta no establece `perfil_actualizado_at`.

**Flujos alternos:**

- Si el correo ya corresponde a una cuenta, el sistema responde sin revelar que la cuenta existe y orienta a recuperar la contraseña (`SEC-ABU-02`, `SEC-REC-01`).
- Si la contraseña no cumple la longitud mínima admitida, el sistema solicita corregirla.
- Si falta algún dato obligatorio o está vacío, el sistema solicita corregirlo. Si documento o teléfono ya están registrados, no crea el alta y mantiene la respuesta pública genérica para no revelar identidades existentes.
- Si se superan los límites de intentos definidos contra abuso automatizado, el sistema restringe temporalmente la operación (`SEC-ABU-01`).

---

## UF-AUTH-02 — Invitar una cuenta

**Rol principal:** Administrador

**Precondiciones:**
- El Administrador está autenticado y autorizado para administrar cuentas (`RN-ADM-01`, `RN-PER-03`).
- Existe o se define la identidad funcional que se asociará a la cuenta invitada.
- Para invitar un Usuario, su identidad se registra previamente en Usuarios con los datos obligatorios de RN-DAT; la invitación no utiliza datos ficticios para completar el perfil.

**Flujo principal:**

1. El Administrador accede a la administración de cuentas.
2. Selecciona la opción de invitar y registra el correo destino y el tipo de cuenta que corresponderá (`USUARIO` o `PERSONAL`).
3. El sistema valida que el correo no corresponda a una cuenta activa existente (`RN-AUTH-ID-02`).
4. El sistema genera un token de invitación impredecible, de vigencia limitada y de un solo uso (`SEC-INV-01`, `SEC-TOK-04`).
5. El sistema almacena la invitación con el alcance que le corresponde; el token no puede conceder permisos superiores a los definidos en la invitación almacenada (`SEC-INV-04`).
6. El módulo `notificaciones` entrega el enlace de invitación al correo destino.
7. El sistema registra la emisión para trazabilidad (`SEC-AUD-02`).

**Flujos alternos:**

- **Reenviar invitación no completada:** el Administrador solicita una nueva emisión; el sistema genera un token nuevo e invalida el anterior (`SEC-INV-03`).
- Si el Administrador no está autorizado para el tipo de cuenta o ámbito solicitado, la operación se deniega (`SEC-AUTZ-02`, `SEC-AUTZ-04`).
- Los permisos asociados a la cuenta invitada se gestionan en `administration`; la invitación por sí sola no los concede.

---

## UF-AUTH-03 — Activar una cuenta invitada

**Rol principal:** Persona invitada

**Precondiciones:**
- Existe una invitación emitida para el correo de la persona.

**Flujo principal:**

1. La persona abre el enlace de invitación recibido.
2. El sistema valida el token completamente antes de continuar: vigencia, estado de uso y correspondencia con la invitación almacenada (`SEC-TOK-01`, `SEC-INV-02`).
3. El sistema solicita definir la contraseña de la cuenta.
4. La persona define su contraseña.
5. El sistema valida la longitud admitida y deriva el hash correspondiente (`SEC-PWD-02`, `SEC-PWD-07`).
6. El sistema crea o activa la cuenta con el tipo y la identidad definidos en la invitación, respetando la exclusividad de identidad (`RN-AUTH-ID-03`).
7. El sistema marca el token como utilizado; un intento posterior con el mismo token se rechaza (`SEC-TOK-05`).
8. El sistema registra el evento de activación (`SEC-AUD-02`).
9. La persona continúa con el inicio de sesión y el completado de perfil (`UF-USR-02`).

**Flujos alternos:**

- Si la invitación está vencida, ya fue utilizada o fue revocada, el proceso de alta no se completa y el sistema orienta a solicitar una nueva invitación (`SEC-INV-02`).
- Si la persona abandona el proceso, la cuenta no queda utilizable hasta completar la activación.

---

## UF-AUTH-04 — Iniciar sesión

**Rol principal:** Usuario, Técnico o Administrador

**Precondiciones:**
- Existe una cuenta con credenciales definidas.

**Flujo principal:**

1. La persona accede al inicio de sesión y registra correo y contraseña.
2. El sistema verifica las credenciales contra el hash almacenado, sin exponerlo en respuestas, registros ni mensajes de error (`SEC-PWD-04`, `SEC-PWD-05`).
3. El sistema verifica que la cuenta esté activa (`RN-AUTH-ID-01`) y que la identidad funcional asociada también lo esté (`RN-AUTH-ID-05`).
4. El sistema crea la sesión en `auth.sesiones`, con vigencia máxima y límite de inactividad definidos por configuración (`SEC-SES-01`, `SEC-SES-09`).
5. El sistema genera el secreto de sesión mediante un generador criptográficamente seguro, sin incluir datos personales ni permisos interpretables (`SEC-SES-02`, `SEC-SES-12`).
6. El sistema regenera el identificador de sesión tras la autenticación exitosa, invalidando cualquier identificador previo (`SEC-SES-13`).
7. El sistema entrega el secreto de sesión exclusivamente mediante cookie `HttpOnly` y `Secure`, con política `SameSite` declarada explícitamente (`SEC-SES-03`, `SEC-SES-04`).
8. El sistema registra el inicio de sesión exitoso (`SEC-AUD-02`).
9. Para una cuenta `USUARIO`, el sistema consulta en Usuarios si la actualización inicial está pendiente, conforme a RN-AUTH-SES-04. Si está pendiente, conduce al flujo de completar o reanudar el perfil; si está completada, permite continuar. Para `PERSONAL`, esta condición no aplica.
10. Cada operación protegida aplica `UF-AUTH-10`, incluyendo la restricción de perfil pendiente; la redirección de la interfaz no sustituye ese control.

**Flujos alternos:**

- Si las credenciales no son válidas, el sistema responde con un mensaje que no revela si falló el correo, la contraseña o la existencia de la cuenta (`SEC-ABU-02`), y registra el intento fallido relevante (`SEC-AUD-02`).
- Si la cuenta o la identidad están inactivas, el sistema no inicia sesión y conserva el historial asociado (`RN-AUTH-ID-05`).
- Si se superan los límites de intentos, el sistema aplica la limitación definida; superarla no implica que la operación esté autorizada (`SEC-ABU-01`, `SEC-ABU-03`).
- El cliente no almacena el secreto de sesión en `localStorage`, `sessionStorage` ni otro almacenamiento accesible desde JavaScript (`SEC-SES-05`).

---

## UF-AUTH-05 — Mantener y renovar la sesión

**Rol principal:** Cuenta autenticada

**Precondiciones:**
- Existe una sesión registrada en `auth.sesiones` que no ha sido revocada ni ha vencido.

**Flujo principal:**

1. La persona continúa operando en la aplicación.
2. En cada operación autenticada, el sistema valida en el servidor que la sesión exista, esté vigente y no esté revocada (`SEC-SES-07`).
3. El sistema verifica que no se hayan superado la vigencia máxima ni el tiempo máximo de inactividad aplicables (`SEC-SES-09`).
4. Cuando el diseño lo contemple, el sistema renueva el acceso validando el secreto de renovación almacenado en `auth.sesiones` (`SEC-TOK-01`).
5. El sistema verifica que la cuenta y la identidad continúen activas (`RN-AUTH-ID-01`).
6. La operación continúa con la identidad obtenida de la sesión, nunca con identificadores enviados por el cliente (`SEC-AUTZ-03`).

**Flujos alternos:**

- Si la sesión venció, fue cerrada o revocada, el sistema la rechaza aunque el cliente conserve una cookie previa y exige nueva autenticación (`SEC-SES-07`, `UF-AUTH-04`).
- Si la cuenta o identidad fueron desactivadas, las operaciones autenticadas dejan de permitirse (`RN-AUTH-ID-05`).
- Los cambios de permisos o de unidad aplican a las nuevas decisiones de autorización, sin alterar la trazabilidad histórica (`RN-AUTH-SES-03`, `SEC-AUTZ-05`).

---

## UF-AUTH-06 — Cerrar sesión

**Rol principal:** Cuenta autenticada

**Precondiciones:**
- Existe una sesión activa.

**Flujo principal:**

1. La persona selecciona cerrar sesión.
2. El sistema invalida la sesión correspondiente en `auth.sesiones` sin esperar su vencimiento natural (`RN-AUTH-SES-02`, `SEC-SES-08`).
3. El sistema elimina la cookie de sesión del cliente (`SEC-SES-08`).
4. El sistema registra el cierre de sesión (`SEC-AUD-02`).
5. Cualquier intento posterior con el secreto anterior se rechaza en el servidor (`SEC-SES-07`).

**Flujos alternos:**

- Si la sesión ya estaba vencida o revocada, el resultado para la persona es equivalente: queda sin sesión válida.

---

## UF-AUTH-07 — Solicitar recuperación de contraseña

**Rol principal:** Persona con o sin cuenta

**Precondiciones:**
- Ninguna. La persona no necesita estar autenticada.

**Flujo principal:**

1. La persona accede a la opción de recuperación e indica su correo.
2. El sistema responde de forma equivalente exista o no una cuenta asociada, sin revelar qué cuentas están registradas (`SEC-REC-01`).
3. Si la cuenta existe, el sistema genera un token de recuperación asociado a esa cuenta, de vigencia limitada y de un solo uso (`SEC-REC-02`, `SEC-TOK-04`).
4. El módulo `notificaciones` entrega el enlace de recuperación al correo de la cuenta.
5. El sistema registra la solicitud para trazabilidad, sin almacenar el token completo (`SEC-AUD-02`, `SEC-AUD-03`).

**Flujos alternos:**

- Si el correo no corresponde a ninguna cuenta, el sistema no envía enlace y la respuesta visible no difiere de la anterior (`SEC-REC-01`).
- Si se superan los límites de solicitudes definidos, el sistema aplica la limitación contra abuso (`SEC-ABU-01`).

---

## UF-AUTH-08 — Restablecer la contraseña

**Rol principal:** Persona titular de la cuenta

**Precondiciones:**
- La persona recibió un enlace de recuperación.

**Flujo principal:**

1. La persona abre el enlace de recuperación.
2. El sistema valida completamente el token antes de permitir cualquier cambio: vigencia, estado de uso y cuenta asociada (`SEC-TOK-01`, `SEC-REC-03`).
3. El sistema solicita la nueva contraseña.
4. La persona define la nueva contraseña y el sistema valida la longitud admitida (`SEC-PWD-07`).
5. El sistema deriva y almacena el nuevo hash (`SEC-PWD-02`, `SEC-PWD-03`).
6. El sistema marca el token como utilizado; no puede reutilizarse (`SEC-TOK-05`).
7. El sistema revoca las sesiones activas de la cuenta y exige nueva autenticación (`SEC-REC-05`, `SEC-SES-10`).
8. El módulo `notificaciones` informa a la cuenta afectada que su contraseña fue actualizada (`SEC-REC-04`).
9. El sistema registra el evento (`SEC-AUD-02`).
10. La persona inicia sesión con la nueva contraseña (`UF-AUTH-04`).

**Flujos alternos:**

- Si el token está vencido, ya fue utilizado o fue revocado, el sistema rechaza el intento y la contraseña no cambia (`SEC-TOK-05`).
- Si la nueva contraseña no cumple la longitud admitida, el sistema solicita corregirla.

---

## UF-AUTH-09 — Reautenticarse para una operación sensible

**Rol principal:** Cuenta autenticada

**Precondiciones:**
- Existe una sesión activa.
- La operación solicitada está clasificada como sensible: cambio de contraseña, cambio de correo de la cuenta, asignación o modificación de permisos administrativos u otra acción que pueda alterar el control de la cuenta (`SEC-REAUTH-02`).

**Flujo principal:**

1. La persona solicita una operación sensible.
2. El sistema determina si existe una autenticación suficientemente reciente (`SEC-REAUTH-01`).
3. Si no la hay, el sistema solicita reautenticación explícita.
4. La persona presenta nuevamente un factor de autenticación aceptado; la existencia de una sesión activa antigua no sustituye esta validación (`SEC-REAUTH-03`).
5. El sistema valida el factor presentado.
6. Cuando la operación implique elevación de privilegios o un cambio sensible de seguridad, el sistema regenera el identificador de sesión (`SEC-REAUTH-04`, `SEC-SES-13`).
7. El sistema permite continuar con la operación solicitada.
8. El sistema registra la reautenticación (`SEC-AUD-02`).

**Flujos alternos:**

- Si la reautenticación falla, la operación sensible no se ejecuta.
- Si se superan los límites de intentos, el sistema aplica la limitación definida (`SEC-ABU-01`).

---

## UF-AUTH-10 — Ejecutar una operación protegida

**Rol principal:** Usuario, Técnico o Administrador

**Precondiciones:**
- Existe una sesión válida.

**Flujo principal:**

1. La persona solicita una operación protegida de cualquier módulo.
2. El sistema determina la identidad autenticada a partir de la sesión, no de datos enviados por el cliente (`SEC-AUTZ-03`).
3. El sistema verifica que la cuenta y la identidad funcional estén activas (`RN-AUTH-ID-01`, `RN-AUTH-ID-05`).
4. El sistema evalúa el permiso requerido con información vigente, sin derivarlo del nombre del cargo ni de valores enviados por el cliente (`RN-AUTH-ROL-05`, `RN-PER-02`).
5. El sistema evalúa el ámbito organizacional aplicable: el Técnico solo sobre su unidad (`RN-AUTH-ROL-02`), el Administrador sobre cualquier unidad (`RN-AUTH-ROL-03`).
6. Cuando la operación recae sobre un recurso identificado por el cliente —una reserva, un perfil, un archivo—, el sistema verifica además que dicho recurso pertenezca o esté explícitamente permitido para la identidad autenticada (`SEC-AUTZ-06`).
7. Si la cuenta es `USUARIO`, el sistema consulta la condición vigente de actualización inicial en Usuarios. Mientras esté pendiente, solo autoriza las operaciones necesarias para completar el perfil y sus vinculaciones, mantener la sesión para ese fin o cerrarla, conforme a RN-USR-08. Las demás se rechazan aunque el cliente omita la redirección.
8. Si el permiso, el ámbito y la condición de perfil lo permiten, `auth` entrega al módulo propietario la identidad y la autorización, y este aplica sus propias reglas funcionales.
9. El módulo propietario ejecuta la operación y registra el actor cuando corresponda (`RN-AUD-01`).

**Flujos alternos:**

- Si el permiso requerido no puede comprobarse de forma válida, el sistema deniega por defecto (`SEC-AUTZ-02`).
- Si la operación queda fuera del ámbito organizacional autorizado, se deniega aunque el permiso exista (`RN-PER-06`, `SEC-AUTZ-04`).
- Si el recurso solicitado no pertenece a la identidad autenticada ni le está explícitamente permitido, se deniega aunque posea el permiso general (`SEC-AUTZ-06`).
- Las operaciones que modifican estado no se ejecutan mediante métodos destinados únicamente a lectura y requieren protección contra solicitudes falsificadas entre sitios (`SEC-CSRF-01`, `SEC-CSRF-03`).

---

## UF-AUTH-11 — Cambiar la contraseña estando autenticado

**Rol principal:** Cuenta autenticada

**Precondiciones:**
- Existe una sesión válida.

**Flujo principal:**

1. La persona accede a la opción de cambio de contraseña.
2. El sistema exige reautenticación por tratarse de una operación sensible (`UF-AUTH-09`, `SEC-REAUTH-02`).
3. La persona define la nueva contraseña.
4. El sistema valida la longitud admitida y deriva el nuevo hash (`SEC-PWD-02`, `SEC-PWD-07`).
5. El sistema revoca las sesiones activas de la cuenta según la política aplicable (`SEC-SES-10`).
6. El módulo `notificaciones` informa a la cuenta afectada del cambio (`SEC-REC-04`).
7. El sistema registra el evento (`SEC-AUD-02`).

**Flujos alternos:**

- Si la reautenticación falla, la contraseña no se modifica.
- Si la nueva contraseña no cumple la longitud admitida, el sistema solicita corregirla.

---

## UF-AUTH-12 — Cambiar el correo de la cuenta

**Rol principal:** Cuenta autenticada, o Administrador autorizado

**Precondiciones:**
- Existe una sesión válida.
- El correo es el identificador funcional único de la cuenta (`RN-AUTH-ID-02`).

**Flujo principal:**

1. El actor accede a la opción de cambio de correo.
2. El sistema exige reautenticación por tratarse de una operación sensible (`SEC-REAUTH-02`).
3. El actor registra el nuevo correo.
4. El sistema valida el formato y la unicidad del correo (`RN-AUTH-ID-02`).
5. El sistema aplica el cambio conservando la identidad funcional y el historial de la cuenta (`RN-CUE-01`, `RN-USR-02`).
6. El módulo `notificaciones` informa del cambio a la cuenta afectada.
7. El sistema registra el evento (`SEC-AUD-02`).

**Flujos alternos:**

- Si el correo ya pertenece a otra cuenta, el cambio se rechaza.
- Si el actor es un Administrador, la operación debe estar dentro de su ámbito autorizado (`SEC-AUTZ-04`).

---

## UF-AUTH-13 — Desactivar o reactivar una cuenta

**Rol principal:** Administrador

**Precondiciones:**
- El Administrador está autenticado y autorizado para administrar cuentas (`RN-ADM-01`).
- La cuenta objetivo existe.

**Flujo principal:**

1. El Administrador accede a la cuenta objetivo.
2. El sistema verifica permiso y ámbito aplicables (`SEC-AUTZ-04`).
3. El Administrador solicita desactivar la cuenta.
4. El sistema marca la cuenta como inactiva sin eliminar su historial (`RN-AUTH-ID-05`, `RN-CUE-04`).
5. El sistema revoca las sesiones activas de esa cuenta (`SEC-SES-10`).
6. La cuenta no puede iniciar sesión ni ejecutar operaciones autenticadas (`RN-AUTH-ID-01`, `RN-CUE-03`).
7. Las reservas, auditorías y notificaciones previas conservan su referencia e interpretación (`RN-CUE-04`, `RN-AUD-04`).
8. El sistema registra el cambio administrativo (`RN-AUD-01`).

**Flujos alternos:**

- **Reactivación:** el Administrador reactiva la cuenta; esta conserva su identificador y relaciones previas, sin crear una identidad nueva (`RN-HAB-04`).
- El sistema no permite desactivar ni degradar la última cuenta con permisos de administrador.
- Si la operación queda fuera del ámbito autorizado, se deniega (`SEC-AUTZ-04`).

---

## UF-AUTH-14 — Cambiar el tipo de identidad de una cuenta

**Rol principal:** Administrador

**Precondiciones:**
- El Administrador está autenticado y autorizado (`RN-ADM-01`, `RN-PER-03`).
- Existe la identidad destino en `usuarios.usuarios` o en `personal.personal`.

**Flujo principal:**

1. El Administrador accede a la cuenta objetivo.
2. Solicita promoverla a personal administrativo o degradarla a reservista.
3. El sistema valida que la cuenta quede vinculada a exactamente una identidad, nunca a ambas (`RN-AUTH-ID-03`, `RN-AUTH-ID-04`).
4. El sistema actualiza el tipo de cuenta y la identidad asociada conservando el historial de la persona (`RN-CUE-01`, `RN-USR-02`).
5. Los permisos y el ámbito resultantes se administran explícitamente en `administration`; el cambio de tipo no los concede por sí solo (`RN-AUTH-ROL-04`, `RN-PRF-03`).
6. El cambio aplica a las nuevas decisiones de autorización y no reinterpreta la trazabilidad histórica (`RN-AUTH-SES-03`, `RN-PER-05`).
7. El sistema registra el cambio administrativo (`RN-AUD-02`).

**Flujos alternos:**

- Si el cambio dejaría al sistema sin ninguna cuenta con permisos de administrador, la operación se rechaza.
- Si la identidad destino no existe o está inactiva, el cambio no se aplica.
- Si la operación queda fuera del ámbito autorizado, se deniega (`SEC-AUTZ-04`).

---

## Separación entre módulos

Los flujos anteriores pueden desencadenar operaciones de otros módulos, pero no trasladan su responsabilidad funcional:

- `auth` administra cuenta, credenciales, sesión, tokens y la decisión de autorización.
- `administration` administra personas, unidades organizacionales, cargos, perfiles y la asignación de permisos que `auth` evalúa.
- `usuarios` administra el perfil funcional del reservista después del alta de la cuenta.
- `notificaciones` entrega los correos de invitación, recuperación y confirmación de cambios; `auth` define cuándo deben generarse, no cómo se entregan.
- Los módulos operativos —`reservations`, `resources`, `espacios`, `reports`— aplican sus propias reglas una vez `auth` confirma identidad, permiso y ámbito.

`auth` no decide si una reserva está disponible, si un recurso está operativo ni qué debe aparecer en un reporte.

## Estructura persistente pendiente

Los flujos de invitación (`UF-AUTH-02`, `UF-AUTH-03`), recuperación de contraseña (`UF-AUTH-07`, `UF-AUTH-08`) y evaluación de permisos (`UF-AUTH-10`) requieren entidades persistentes que el modelo principal aún no define: tokens de invitación, tokens de recuperación, permisos y sus asignaciones. Conforme a [data-model.md](data-model.md), su estructura queda pendiente de especificar y no se deduce del nombre del cargo ni del tipo de cuenta.
