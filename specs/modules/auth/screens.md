# Especificación funcional de pantallas — Auth

## Alcance y fuentes

Derivado exclusivamente de [user-flow.md](user-flow.md), [business-rules.md](business-rules.md), [security.md](security.md), [data-model.md](data-model.md) y [overview.md](overview.md). La navegación se detalla en [screen-flow.md](screen-flow.md). Los identificadores corresponden a superficies funcionales; no prescriben páginas independientes, rutas HTTP ni componentes.

No se amplían reglas, datos, contratos ni flujos. Los estados de procesamiento describen la espera del resultado de una acción existente, no operaciones nuevas. Una respuesta de éxito solo representa el resultado confirmado por el servidor. No se especifican estilos, disposición visual, textos literales de error ni códigos API.

## Criterios comunes

- **Interfaz:** recoge las entradas descritas por cada flujo y comunica validaciones, resultados y restricciones. Los errores se presentan en la superficie de origen; no requieren pantallas independientes.
- **Backend:** valida identidad, estado, sesión, permiso, ámbito y pertenencia de recursos en cada operación. El rol Administrador no concede permisos por sí mismo: una asignación global permite ejecutar ese permiso globalmente; una asignación por unidad conserva su alcance y la coincidencia con la unidad del cargo vigente, aunque otro permiso sea global. Ocultar una acción no autoriza ni protege la operación (`RN-AUTH-ID-08`, `RN-AUTH-ROL-05`, `RN-AUTH-ROL-07`, `SEC-AUTZ-01`, `SEC-AUTZ-02`, `SEC-AUTZ-03`, `SEC-AUTZ-04`, `SEC-AUTZ-05`, `SEC-AUTZ-06`).
- **Seguridad:** contraseñas, hashes, secretos de sesión, tokens y auditoría no son datos de consulta de estas pantallas. Los enlaces de invitación y recuperación aportan el token al proceso; no se crea un campo para copiarlo ni una vista para mostrarlo. Se respetan `SEC-PWD-04`, `SEC-PWD-05`, `SEC-TOK-01`, `SEC-TOK-02`, `SEC-AUD-03` y `SEC-INF-04`.
- **Nueva contraseña:** mínimo 8 caracteres y admisión de al menos 64, sin reglas obligatorias de composición ni expiración periódica forzada (`SEC-PWD-07`). No se interpreta 64 como máximo. No se añade confirmación de contraseña ni otro campo no solicitado por los flujos.
- **Respuestas públicas:** no distinguir existencia de cuenta, correo, documento o teléfono cuando el flujo exige respuesta genérica (`UF-AUTH-01`, `SEC-ABU-02`, `SEC-REC-01`). Una restricción por abuso comunica que la operación está limitada; no se inventan umbrales, plazos, contadores ni CAPTCHA (`SEC-ABU-01`, `SEC-ABU-03`).
- **Controles sin representación visual:** derivación y almacenamiento de contraseñas, cookies, HTTPS, CSRF, regeneración y revocación de sesiones, validación criptográfica y auditoría siguen siendo controles técnicos. Aplican `SEC-PWD-01`, `SEC-PWD-02`, `SEC-PWD-03`, `SEC-PWD-06`, `SEC-SES-01`, `SEC-SES-02`, `SEC-SES-03`, `SEC-SES-04`, `SEC-SES-05`, `SEC-SES-06`, `SEC-SES-11`, `SEC-SES-12`, `SEC-SES-13`, `SEC-CSRF-01`, `SEC-CSRF-02`, `SEC-CSRF-03`, `SEC-INF-01`, `SEC-INF-02`, `SEC-INF-03`, `SEC-TOK-03` y `SEC-AUD-01`. JWT permanece condicional al diseño, como en `security.md`; no origina ninguna pantalla.

## SCR-AUTH-01 — Iniciar sesión

- **User Flows de origen:** `UF-AUTH-04`; destino de nueva autenticación de `UF-AUTH-01`, `UF-AUTH-05` y `UF-AUTH-08`.
- **Actores:** Usuario, Técnico o Administrador.
- **Objetivo:** autenticar la cuenta y continuar según su tipo y condición de perfil.
- **Precondiciones:** existe una cuenta con credenciales definidas; su existencia no se confirma públicamente mediante errores.
- **Información visible:** solicitud de correo y contraseña; resultado de autenticación; necesidad de autenticarse nuevamente cuando la sesión dejó de ser válida.
- **Entradas:** correo y contraseña.
- **Acciones:** iniciar sesión; acceder a las opciones de autorregistro y recuperación descritas en `UF-AUTH-01` y `UF-AUTH-07`.
- **Validaciones visibles:** resultado genérico de credenciales no aceptadas. No se aplica la política de definición de nueva contraseña como una regla adicional para iniciar sesión.
- **Estados:** captura, autenticación en curso, rechazo, limitación de intentos y autenticación correcta con continuación.
- **Errores y respuestas:** credenciales inválidas o cuenta/identidad inactiva no abren sesión; el mensaje no distingue correo, contraseña o existencia de cuenta. La limitación de intentos impide continuar mientras corresponda.
- **Resultado/navegación:** `USUARIO` con actualización inicial pendiente → módulo `usuarios`, completar o reanudar perfil; `USUARIO` con actualización completada o `PERSONAL` → operaciones autorizadas del módulo de destino. La fuente no fija una pantalla de inicio de la aplicación.
- **Backend:** verifica hash y estados; crea y regenera la sesión; consulta en Usuarios la condición de perfil. No toma roles ni permisos del formulario.
- **RN/SEC relacionadas:** `RN-AUTH-ID-01`, `RN-AUTH-ID-05`, `RN-AUTH-ROL-08`, `RN-AUTH-SES-04`, `SEC-PWD-04`, `SEC-PWD-05`, `SEC-SES-01`, `SEC-SES-03`, `SEC-SES-04`, `SEC-SES-09`, `SEC-SES-13`, `SEC-ABU-01`, `SEC-ABU-02`, `SEC-ABU-03`, `SEC-AUD-02` y criterios comunes.
- **Dependencias:** `usuarios` para perfil pendiente; módulos operativos para las operaciones posteriores. El perfil pendiente sigue restringido por `RN-USR-07` y `RN-USR-08` de `usuarios`, también en backend.

## SCR-AUTH-02 — Autorregistrarse

- **User Flow de origen:** `UF-AUTH-01`.
- **Actor:** Persona sin cuenta.
- **Objetivo:** crear conjuntamente el perfil obligatorio y la cuenta `USUARIO`, sin invitación ni aprobación previa.
- **Precondiciones:** la persona no tiene una cuenta asociada al correo que va a registrar.
- **Información visible:** datos obligatorios solicitados, política de longitud de contraseña, correcciones necesarias y resultado público del registro.
- **Entradas:** correo electrónico, contraseña, nombre, documento, teléfono, institución y dependencia.
- **Acciones:** enviar el registro; corregir datos; continuar al inicio de sesión después del alta; acceder a recuperación cuando la respuesta pública orienta a ello.
- **Validaciones visibles:** formato del correo, longitud de contraseña, datos obligatorios presentes y no vacíos; las validaciones del perfil corresponden a `usuarios`. No se inventan formatos de documento/teléfono ni opciones de institución/dependencia.
- **Estados:** captura, validación/procesamiento, corrección requerida, respuesta pública genérica, limitación temporal y alta completada.
- **Errores y respuestas:** correo existente → respuesta sin revelar existencia y orientación a recuperación; documento o teléfono registrado → respuesta pública genérica sin alta; datos ausentes o longitud inválida → solicitar corrección; abuso → restringir temporalmente.
- **Resultado/navegación:** alta → `SCR-AUTH-01`; después de autenticarse, revisión de datos y vinculaciones en `usuarios` (`UF-USR-01`, citado por la fuente). El registro no establece `perfil_actualizado_at`.
- **Backend:** Usuarios valida/persiste el perfil y Auth crea la cuenta en una única transacción; un fallo no deja ninguno de los dos registros. Se genera el hash y se audita el alta. No se ofrece elegir `PERSONAL`, identidad ajena, rol ni permisos.
- **RN/SEC relacionadas:** `RN-AUTH-ID-02`, `RN-AUTH-ID-03`, `RN-AUTH-ID-04`, `RN-AUTH-ID-06`, `RN-AUTH-ID-09`, `RN-AUTH-ROL-04`, `SEC-PWD-01`, `SEC-PWD-02`, `SEC-PWD-03`, `SEC-PWD-07`, `SEC-ABU-01`, `SEC-ABU-02`, `SEC-REC-01`, `SEC-AUD-01`.
- **Dependencias:** `usuarios`, propietario de los datos obligatorios, su validación, unicidad y actualización inicial. La fuente cita la familia RN-DAT de `usuarios` sin detallar sus identificadores individuales; no se reconstruyen aquí.

## SCR-AUTH-03 — Invitar o reenviar una invitación

- **User Flow de origen:** `UF-AUTH-02`.
- **Actor:** Administrador.
- **Objetivo:** emitir una invitación para una identidad existente o reenviar una invitación no completada.
- **Precondiciones:** actor autenticado y autorizado; identidad `USUARIO` previamente registrada con los datos obligatorios o ficha `PERSONAL` activa y completa.
- **Información visible:** correo destino, tipo de cuenta, unidad para `PERSONAL`, resultado de la emisión o de su rechazo. No se muestra el token.
- **Entradas:** correo destino, tipo `USUARIO` o `PERSONAL` y, para `PERSONAL`, unidad asociada al cargo vigente (`id_unidad`). Para reenviar, contexto de la invitación no completada; las fuentes no definen cómo se localiza.
- **Acciones:** emitir invitación; solicitar nueva emisión para un alta no completada; corregir los datos que impidan emitirla.
- **Validaciones visibles:** resultado de validación de correo frente a cuenta activa existente o cuenta de alta completada posteriormente desactivada administrativamente (`RN-AUTH-ID-10`), identidad previa y, para `PERSONAL`, coincidencia exacta de correo, ficha completa/activa y unidad del cargo dentro del ámbito permitido. No se especifica texto de error ni se amplía la información pública revelada.
- **Estados:** captura, emisión en curso, emisión realizada, rechazo de validación, acceso denegado y limitación por abuso cuando aplique.
- **Errores y respuestas:** si no se cumplen las validaciones no se presenta la invitación como emitida; tipo o ámbito no autorizado → denegación; cuenta de alta completada posteriormente desactivada administrativamente → rechazar invitación e indicar al Administrador que la reactivación corresponde a `UF-AUTH-12` en `SCR-AUTH-09`. No se define recuperación ante fallos de entrega de correo, ausente en las fuentes.
- **Resultado/navegación:** resultado de emisión en esta superficie; el enlace recibido abre `SCR-AUTH-04` en el recorrido de la persona invitada, no redirige al Administrador. No se confunde emisión con activación.
- **Backend:** resuelve la identidad por correo, liga la invitación a ella sin duplicarla, genera el token y audita. Reenviar invalida el token anterior y sigue permitido para altas incompletas; no permite reactivar cuentas cuyo alta se completó y que luego fueron desactivadas administrativamente (`RN-AUTH-ID-10`).
- **RN/SEC relacionadas:** `RN-AUTH-ID-02`, `RN-AUTH-ID-07`, `RN-AUTH-ID-10`, `RN-AUTH-ROL-04`, `SEC-INV-01`, `SEC-INV-03`, `SEC-INV-04`, `SEC-TOK-04`, `SEC-AUTZ-02`, `SEC-AUTZ-04`, `SEC-ABU-01`, `SEC-AUD-02`; `RN-ADM-01` y `RN-PER-03` de `administration`.
- **Dependencias:** `usuarios` para la identidad `USUARIO`; `administration` para ficha de Personal, cargo, unidad y permisos; `notificaciones` para entrega. La creación/corrección de identidades y la asignación de permisos permanecen en sus módulos, sin un formulario nuevo en Auth.

## SCR-AUTH-04 — Activar una cuenta invitada

- **User Flow de origen:** `UF-AUTH-03`.
- **Actor:** Persona invitada.
- **Objetivo:** definir la contraseña y completar la activación asociada a una invitación válida.
- **Precondiciones:** invitación emitida; acceso mediante su enlace. El formulario solo continúa tras validar el token.
- **Información visible:** posibilidad de definir contraseña cuando el enlace es válido, política de longitud, rechazo de activación y orientación a solicitar nueva invitación cuando corresponda.
- **Entradas:** contraseña. El enlace aporta el token; tipo e identidad proceden de la invitación almacenada y no son elecciones del invitado.
- **Acciones:** definir/enviar contraseña; corregir su longitud. Ante invitación vencida, usada o revocada, seguir la orientación a solicitar otra; no se inventa una solicitud automática de reenvío.
- **Validaciones visibles:** longitud de contraseña y posibilidad de completar la activación según la validación del enlace, de la identidad vinculada y de la restricción de `RN-AUTH-ID-10`.
- **Estados:** validación del enlace, definición de contraseña, activación en curso, contraseña corregible, invitación no utilizable, identidad no válida y activación completada.
- **Errores y respuestas:** token inválido/vencido/usado/revocado → no completar alta; ficha de Personal desactivada, eliminada o con otro correo → rechazar y orientar a corregir la ficha y emitir invitación válida. Si el alta se completó y la cuenta fue desactivada administrativamente, la invitación no la reactiva: se rechaza el proceso sin iniciar sesión y sin revelar innecesariamente datos de la cuenta (`RN-AUTH-ID-10`, `SEC-ABU-02`). La reactivación corresponde exclusivamente a `UF-AUTH-12`; no se ofrece acceso público a `SCR-AUTH-09`. Abandonar no deja utilizable la cuenta sin activar. No se fija un destino al abandonar.
- **Resultado/navegación:** activación correcta inicia sesión sin pedir otra vez la contraseña; `USUARIO` → módulo `usuarios` / `UF-USR-02`; `PERSONAL` → operaciones autorizadas, sin actualización inicial.
- **Backend:** revalida invitación e identidad y rechaza la activación de cuentas de alta completada posteriormente desactivadas administrativamente; para las altas admitidas, crea o activa cuenta con exclusividad de identidad, consume token, crea/regenera sesión y audita. Los controles no se sustituyen con validar el enlace en el cliente.
- **RN/SEC relacionadas:** `RN-AUTH-ID-03`, `RN-AUTH-ID-05`, `RN-AUTH-ID-07`, `RN-AUTH-ID-10`, `RN-AUTH-SES-04`, `SEC-TOK-01`, `SEC-TOK-04`, `SEC-TOK-05`, `SEC-INV-02`, `SEC-PWD-02`, `SEC-PWD-07`, `SEC-SES-13`, `SEC-ABU-01`, `SEC-AUD-02`.
- **Dependencias:** `notificaciones` como origen del enlace; `usuarios` para actualización inicial; `administration` para corregir la ficha de Personal cuando corresponda. No se prescribe navegación automática a la gestión administrativa desde un enlace público.

## SCR-AUTH-05 — Solicitar recuperación de contraseña

- **User Flow de origen:** `UF-AUTH-07`.
- **Actor:** Persona con o sin cuenta.
- **Objetivo:** solicitar el envío de un enlace sin revelar cuentas registradas.
- **Precondiciones:** ninguna; no requiere autenticación.
- **Información visible:** solicitud del correo y respuesta equivalente exista o no una cuenta.
- **Entradas:** correo.
- **Acciones:** enviar solicitud de recuperación.
- **Validaciones visibles:** correo como dato solicitado; la fuente no especifica validaciones adicionales de formato para este flujo. No se informa si existe una cuenta.
- **Estados:** captura, procesamiento, respuesta genérica y limitación de solicitudes.
- **Errores y respuestas:** inexistencia de cuenta no produce un error distinguible; exceso de solicitudes → limitación contra abuso. La respuesta no asegura que se haya enviado un correo a una cuenta existente.
- **Resultado/navegación:** permanece el resultado genérico en esta superficie. La apertura posterior del enlace recibido inicia `SCR-AUTH-06`; no hay salto automático al restablecimiento ni consulta de estado del envío.
- **Backend:** solo si existe cuenta genera token asociado, temporal y de un uso; solicita entrega y registra el evento sin token completo.
- **RN/SEC relacionadas:** `RN-AUTH-ID-02` como identificación por correo; `SEC-REC-01`, `SEC-REC-02`, `SEC-TOK-04`, `SEC-ABU-01`, `SEC-AUD-02`, `SEC-AUD-03`.
- **Dependencias:** `notificaciones` entrega el enlace cuando corresponde; no requiere pantalla de ese módulo.

## SCR-AUTH-06 — Restablecer la contraseña

- **User Flow de origen:** `UF-AUTH-08`.
- **Actor:** Persona titular de la cuenta.
- **Objetivo:** establecer una nueva contraseña mediante el enlace de recuperación.
- **Precondiciones:** enlace recibido; token validado antes de permitir el cambio.
- **Información visible:** solicitud de nueva contraseña, política de longitud, resultado del restablecimiento o rechazo del enlace y necesidad de iniciar sesión tras el éxito.
- **Entradas:** nueva contraseña; token aportado por el enlace.
- **Acciones:** enviar nueva contraseña, corregirla si no cumple la longitud e iniciar sesión después del éxito.
- **Validaciones visibles:** longitud admitida; enlace utilizable. No se pide una contraseña anterior ni se exige sesión.
- **Estados:** validación del enlace, captura, procesamiento, corrección requerida, enlace rechazado y contraseña restablecida.
- **Errores y respuestas:** token vencido/usado/revocado o inválido → rechazo sin cambiar contraseña; longitud no admitida → solicitar corrección. No se añade renovación automática del enlace.
- **Resultado/navegación:** éxito → `SCR-AUTH-01`, nueva autenticación obligatoria; no inicia sesión automáticamente.
- **Backend:** valida token/cuenta, almacena nuevo hash, consume token, revoca sesiones, solicita notificación y audita.
- **RN/SEC relacionadas:** `RN-AUTH-SES-01`, `RN-AUTH-SES-05`, `SEC-TOK-01`, `SEC-TOK-05`, `SEC-REC-03`, `SEC-REC-04`, `SEC-REC-05`, `SEC-PWD-02`, `SEC-PWD-03`, `SEC-PWD-07`, `SEC-SES-10`, `SEC-AUD-02`.
- **Dependencias:** `notificaciones` entrega el enlace e informa del cambio; no se necesita vista de notificaciones para completar el restablecimiento.

## SCR-AUTH-07 — Reautenticarse para una operación sensible

- **User Flows de origen:** `UF-AUTH-09`; utilizado por `UF-AUTH-11`.
- **Actor:** Cuenta autenticada.
- **Objetivo:** aportar autenticación reciente para continuar una operación sensible pendiente.
- **Precondiciones:** sesión activa y operación sensible que requiere reautenticación explícita según evaluación del servidor.
- **Información visible:** necesidad de reautenticación para continuar y resultado de la validación.
- **Entradas:** únicamente contraseña actual de la cuenta identificada por la sesión; no se solicita correo ni se incorporan OTP, MFA u otros factores (`SEC-REAUTH-03`).
- **Acciones:** presentar la contraseña actual para continuar la operación solicitada.
- **Validaciones visibles:** aceptación o rechazo de la reautenticación; no basta con tener una sesión antigua activa.
- **Estados:** contraseña actual requerida, validación en curso, fallo, limitación de intentos y reautenticación correcta.
- **Errores y respuestas:** fallo o límite de intentos → la operación sensible no se ejecuta. No se fija una cancelación ni un retorno alternativo no descritos por la fuente.
- **Resultado/navegación:** éxito → continuar la operación que la originó (`SCR-AUTH-08` para cambio de contraseña, o módulo propietario). Si ya existe autenticación suficientemente reciente, este formulario no es necesario.
- **Backend:** evalúa la ventana de autenticación reciente definida por la configuración y valida la contraseña actual contra el hash de la cuenta identificada por la sesión cuando se exige reautenticación; mantiene la condición de autenticación reciente, regenera sesión cuando corresponde y registra el evento. La reautenticación no concede permisos ni omite `UF-AUTH-10`.
- **RN/SEC relacionadas:** `RN-AUTH-ROL-08`, `RN-AUTH-SES-01`, `SEC-REAUTH-01`, `SEC-REAUTH-02`, `SEC-REAUTH-03`, `SEC-REAUTH-04`, `SEC-SES-13`, `SEC-ABU-01`, `SEC-AUD-02`.
- **Dependencias:** `administration` para operaciones sensibles de permisos mencionadas por `UF-AUTH-09`; otros destinos solo cuando el módulo propietario haya definido la operación sensible.

## SCR-AUTH-08 — Cambiar la contraseña estando autenticado

- **User Flow de origen:** `UF-AUTH-11`.
- **Actor:** Cuenta autenticada.
- **Objetivo:** definir una contraseña nueva desde una sesión válida, cumpliendo la reautenticación exigida.
- **Precondiciones:** sesión válida y evaluación de `UF-AUTH-09` antes de continuar con el cambio. Si la autenticación reciente satisface la ventana configurada, no se solicita reautenticación adicional; en caso contrario se completa `SCR-AUTH-07` antes de continuar a `SCR-AUTH-08`.
- **Información visible:** necesidad de reautenticación si procede, solicitud de nueva contraseña, política de longitud y resultado del cambio.
- **Entradas:** nueva contraseña; la contraseña actual para reautenticación se recoge, cuando se exige, en `SCR-AUTH-07`, sin duplicarlo como campo adicional aquí.
- **Acciones:** continuar mediante reautenticación cuando se exija; definir/enviar nueva contraseña; corregir longitud.
- **Validaciones visibles:** autenticación reciente o reautenticación explícita satisfecha conforme a `UF-AUTH-09`, y longitud admitida.
- **Estados:** pendiente de reautenticación, captura de nueva contraseña, procesamiento, corrección requerida, cambio rechazado y cambio completado.
- **Errores y respuestas:** reautenticación fallida → no modifica contraseña; longitud no admitida → solicitar corrección.
- **Resultado/navegación:** cambio completado con todas las sesiones activas revocadas, incluida la actual. No se crea automáticamente una nueva sesión; la persona debe continuar a `SCR-AUTH-01` e iniciar sesión nuevamente con la nueva contraseña (`SEC-SES-10`, `UF-AUTH-04`).
- **Backend:** comprueba autenticación reciente o reautenticación explícita conforme a `UF-AUTH-09`, deriva hash, revoca todas las sesiones activas incluida la actual, solicita notificación y audita. No crea automáticamente una nueva sesión.
- **RN/SEC relacionadas:** `RN-AUTH-SES-01`, `RN-AUTH-SES-05`, `SEC-REAUTH-01`, `SEC-REAUTH-02`, `SEC-PWD-02`, `SEC-PWD-07`, `SEC-SES-07`, `SEC-SES-10`, `SEC-REC-04`, `SEC-AUD-02`.
- **Dependencias:** `notificaciones` informa del cambio. No se crea una pantalla de confirmación de correo.

## SCR-AUTH-09 — Gestionar estado y tipo de identidad de una cuenta

- **User Flows de origen:** `UF-AUTH-12` y `UF-AUTH-13`.
- **Actor:** Administrador.
- **Objetivo:** desactivar/reactivar la cuenta objetivo o cambiar su tipo de identidad, conservando identificador e historial.
- **Precondiciones:** actor autenticado con el permiso requerido y su alcance efectivo, sin atribuir permisos al rol por sí mismo; cuenta objetivo existente; para cambiar tipo, identidad destino existente y activa.
- **Información visible:** cuenta objetivo, correo inmutable, estado y tipo de cuenta, identidad asociada y resultado de la operación. Solo se muestra el contexto necesario para estas acciones; no se añade un listado de reservas, auditorías o sesiones.
- **Entradas:** acción de desactivar/reactivar; para cambio de tipo, tipo destino e identidad destino a vincular. El mecanismo de localización o selección de cuenta/identidad no está concretado; no se inventan buscadores, catálogos ni campos API.
- **Acciones:** desactivar, reactivar, promover a personal administrativo o degradar a reservista conforme al flujo. No se añaden edición de correo, borrado de cuenta ni asignación de permisos dentro de Auth.
- **Validaciones visibles:** permiso/ámbito, identidad destino existente y activa, coincidencia de correo y exclusividad de identidad; protección de la última cuenta que cumple `RN-AUTH-ROL-09`.
- **Estados:** cuenta en consulta, modificación en curso, estado/tipo actualizado, cambio rechazado y acceso denegado. Las operaciones sensibles siguen `UF-AUTH-09` cuando corresponda; la clasificación concreta no se amplía aquí.
- **Errores y respuestas:** identidad inexistente/inactiva, correo incompatible o exclusividad incumplida → cambio no aplicado; fuera de ámbito → denegación; desactivación o cambio que deje sin la última cuenta administrativa válida → rechazo. Los errores se comunican en la misma superficie.
- **Resultado/navegación:** permanece la cuenta objetivo con su estado/tipo resultante. Reactivar conserva identificador y relaciones, sin crear identidad nueva. El cambio de tipo no concede permisos: su gestión corresponde a `administration`.
- **Backend:** valida y actualiza estado o vínculo exclusivo, preserva historial, revoca sesiones de la cuenta desactivada y registra el cambio. Cambios de tipo/identidad/permisos afectan nuevas decisiones, no reinterpretan acciones anteriores.
- **RN/SEC relacionadas:** `RN-AUTH-ID-01`, `RN-AUTH-ID-02`, `RN-AUTH-ID-03`, `RN-AUTH-ID-04`, `RN-AUTH-ID-05`, `RN-AUTH-ID-11`, `RN-AUTH-ROL-04`, `RN-AUTH-ROL-09`, `RN-AUTH-SES-03`, `SEC-AUTZ-04`, `SEC-SES-10`; `RN-ADM-01`, `RN-PER-03`, `RN-PER-05`, `RN-CUE-01`, `RN-CUE-03`, `RN-CUE-04`, `RN-USR-02`, `RN-HAB-04`, `RN-AUD-01`, `RN-AUD-02` y `RN-AUD-04` de `administration`, citadas por los flujos de origen.
- **Dependencias:** `usuarios` y `administration` para las identidades destino; `administration` para permisos y auditoría; `reservations` y `notificaciones` conservan sus referencias históricas. No se infiere una transición a esos historiales.

## Cobertura de todos los User Flows

| User Flow revisado | Superficie o efecto de interfaz |
|---|---|
| UF-AUTH-01 | SCR-AUTH-02; continúa a SCR-AUTH-01 y perfil en usuarios |
| UF-AUTH-02 | SCR-AUTH-03; entrega por notificaciones |
| UF-AUTH-03 | SCR-AUTH-04; transfiere a usuarios o a operaciones autorizadas |
| UF-AUTH-04 | SCR-AUTH-01 |
| UF-AUTH-05 | Sin pantalla propia: continuidad silenciosa; sesión inválida exige SCR-AUTH-01 |
| UF-AUTH-06 | Sin pantalla propia: acción «cerrar sesión» desde el contexto autenticado; termina sin sesión válida, incluso si ya estaba vencida/revocada |
| UF-AUTH-07 | SCR-AUTH-05 |
| UF-AUTH-08 | SCR-AUTH-06; exige SCR-AUTH-01 tras el éxito |
| UF-AUTH-09 | SCR-AUTH-07 solo cuando se requiere reautenticación explícita |
| UF-AUTH-10 | Sin pantalla propia: permite continuar, comunica denegación en origen o conduce a completar perfil cuando corresponde |
| UF-AUTH-11 | SCR-AUTH-07 si no se satisface la ventana de autenticación reciente; SCR-AUTH-08 para el cambio; éxito → SCR-AUTH-01 |
| UF-AUTH-12 | SCR-AUTH-09 |
| UF-AUTH-13 | SCR-AUTH-09 |

La acción de cierre no necesita diálogo de confirmación. El servidor revoca la sesión, elimina la cookie y audita (`RN-AUTH-SES-02`, `SEC-SES-07`, `SEC-SES-08`, `SEC-AUD-02`). La renovación, cuando el diseño la contemple, no necesita botón, aviso previo, cuenta regresiva ni pantalla (`UF-AUTH-05`, `SEC-SES-09`). Una denegación de autorización es un estado del contexto solicitante, no un «panel de permisos» (`UF-AUTH-10`).

## Ambigüedades y límites de las fuentes

1. **Destino de perfil:** `UF-AUTH-01` remite a `UF-USR-01` de `usuarios`; `UF-AUTH-03` remite a `UF-USR-02`; `UF-AUTH-04` habla de completar o reanudar sin identificador. Se conservan esas referencias sin decidir que sean equivalentes ni reemplazarlas. Auth no define aquí las pantallas del perfil.
2. **Regeneración de sesión tras reautenticación:** el modelo describe regeneración en toda reautenticación exitosa y seguridad la exige expresamente cuando implica elevación o cambio sensible; esa diferencia de alcance técnico no se resuelve mediante una regla visual. El factor, la condición de autenticación reciente y la salida del cambio de contraseña quedan resueltos por las decisiones recogidas abajo.
3. **Destinos y retornos no fijados:** no se especifican pantalla de inicio de aplicación, ruta tras cerrar sesión, navegación al abandonar formularios, retorno automático a una operación tras iniciar sesión ni mecanismo para localizar cuentas, identidades o invitaciones. Tampoco se define un autoservicio para pedir nueva invitación. No se añaden esas acciones.
4. **Detalle fuera de Auth:** las validaciones de perfil se remiten a la familia RN-DAT de `usuarios`; las fuentes no fijan su detalle ni opciones de captura. Los fallos de entrega, mensajes literales, límites de intentos y varias rutas de retorno tampoco están definidos. Las tablas objetivo pendientes descritas en el modelo no prueban disponibilidad actual de estas funciones.

## Decisiones aplicadas a las ambigüedades de prioridad alta

- `UF-AUTH-09` utiliza únicamente la contraseña actual de la cuenta identificada por la sesión (`SEC-REAUTH-03`).
- `UF-AUTH-11` aplica la ventana de autenticación reciente ya configurada; solo cuando no se satisface exige `SCR-AUTH-07` antes de continuar a `SCR-AUTH-08` (`SEC-REAUTH-01`).
- El cambio de contraseña exitoso revoca todas las sesiones activas, incluida la actual, no crea otra automáticamente y exige `SCR-AUTH-01` con la nueva contraseña (`SEC-SES-10`).
- Cada permiso conserva el alcance de su asignación. El rol Administrador no concede permisos ni convierte en globales las asignaciones por unidad (`RN-AUTH-ROL-03`, `RN-AUTH-ROL-07`, `SEC-AUTZ-04`).
- Las invitaciones no reactivan cuentas cuyo alta se completó y que después fueron desactivadas administrativamente. Solo `UF-AUTH-12` permite esa reactivación; las altas incompletas conservan la nueva emisión o reenvío (`RN-AUTH-ID-10`).
