# Autenticación y autorización

El módulo `auth` administra las cuentas, credenciales, sesiones y decisiones de autorización. Las identidades funcionales se encuentran en `usuarios.usuarios` y `personal.personal`; una cuenta corresponde exactamente a una de ellas.

## Cuentas e identidades — RN-AUTH-ID

- **RN-AUTH-ID-01:** Toda operación autenticada requiere una cuenta activa.
- **RN-AUTH-ID-02:** El correo electrónico es único, identifica la cuenta y coincide con el correo de su identidad funcional asociada. Después de crear la cuenta no puede modificarse.
- **RN-AUTH-ID-03:** Una cuenta debe estar vinculada a `usuarios.usuarios` o a `personal.personal`, nunca a ambas, y el correo de la identidad vinculada debe coincidir con el correo inmutable de la cuenta.
- **RN-AUTH-ID-04:** La restricción de exclusividad se conserva mediante `ck_auth_cuentas_identidad` y las restricciones únicas de las referencias de identidad.
- **RN-AUTH-ID-05:** Desactivar una cuenta o identidad impide nuevas operaciones autenticadas, sin eliminar su historial.
- **RN-AUTH-ID-06:** El autorregistro solicita los datos obligatorios definidos en RN-DAT de Usuarios junto con correo y contraseña. Usuarios valida y persiste el perfil; Auth crea su cuenta en la misma transacción. El registro no completa por sí solo la actualización inicial ni las vinculaciones obligatorias.
- **RN-AUTH-ID-07:** Antes de emitir una invitación para `PERSONAL`, debe existir una identidad activa y completa en `personal.personal`. Auth la resuelve por coincidencia exacta del correo único, guarda su `id_persona` en `auth.invitaciones` y valida que `id_unidad` coincida con la unidad derivada de su cargo y esté dentro del ámbito autorizado del emisor. Auth no crea ni completa la ficha de Personal. Al activar la invitación, vuelve a verificar que la identidad siga activa y que el correo coincida.
- **RN-AUTH-ID-08:** La identidad autenticada se determina exclusivamente a partir de una cuenta validada. No se identifica a una persona por nombre, correo enviado por el cliente u otro dato no verificado.
- **RN-AUTH-ID-09:** Una cuenta se crea por una de dos vías: invitación emitida por una cuenta autorizada, o autorregistro abierto sin aprobación previa. El autorregistro solo crea cuentas de tipo `USUARIO`; nunca permite autoasignarse permisos administrativos ni vincularse a `personal.personal`.
- **RN-AUTH-ID-10:** Una cuenta cuyo proceso de alta no se completó puede recibir una nueva invitación sin que ello duplique su identidad funcional ni impida reintentar el alta. Una invitación no puede reactivar una cuenta cuyo alta fue completada y que posteriormente fue desactivada administrativamente; su reactivación corresponde exclusivamente a `UF-AUTH-12`.
- **RN-AUTH-ID-11:** El historial de reservas, notificaciones y auditoría se mantiene asociado a la misma cuenta aunque su identidad funcional quede inactiva.
- **RN-AUTH-ID-12:** Mientras la identidad no tenga una cuenta asociada, su correo puede corregirse mediante la gestión administrativa aplicable. Una vez creada la cuenta, el correo de ambas es el mismo valor inmutable conforme a `RN-AUTH-ID-02`.

## Roles y alcance — RN-AUTH-ROL

- **RN-AUTH-ROL-01:** Los únicos roles funcionales son Usuario, Técnico y Administrador.
- **RN-AUTH-ROL-02:** El Técnico es una cuenta activa de tipo `PERSONAL`, vinculada a un registro activo de `personal.personal` cuyo cargo pertenece a un laboratorio. Gestiona únicamente ese laboratorio, el de su cargo vigente. No requiere ninguna asignación de permisos: el conjunto de lo que puede hacer lo fija el rol. *(Redefinida el 2026-09-30: los roles son fijos y los permisos los define el rol; ver [la decisión](../../docs/decisions/origen-externo-estructura-institucional.md#los-permisos-los-define-el-rol-2026-09-30).)*
- **RN-AUTH-ROL-03:** El Administrador es una cuenta activa de tipo `ADMINISTRADOR`: propia de Reservas, sin ficha en `personal.personal` ni identidad asociada (no viene de LIA). Su ámbito es global y puede ejecutar todo permiso habilitado del catálogo. El rol lo da el tipo de cuenta; no se otorga ni se retira por asignaciones. *(Redefinida el 2026-09-30: los roles son fijos y los permisos los define el rol; ver [la decisión](../../docs/decisions/origen-externo-estructura-institucional.md#los-permisos-los-define-el-rol-2026-09-30).)*
- **RN-AUTH-ROL-04:** Una cuenta de tipo `USUARIO` no puede recibir ni ejercer permisos administrativos. La cuenta o una vinculación académica no conceden permisos por sí mismas.
- **RN-AUTH-ROL-05:** Los permisos y el alcance deben validarse en el servidor con información vigente; no se derivan únicamente del nombre del cargo ni de datos enviados por el cliente.
- **RN-AUTH-ROL-06:** El ámbito del Técnico sale siempre de su cargo vigente (`personal.personal -> cargos.cargo -> laboratorio`). Nada enviado por el cliente ni ninguna asignación puede ampliarlo a otro laboratorio. *(Redefinida el 2026-09-30: los roles son fijos y los permisos los define el rol; ver [la decisión](../../docs/decisions/origen-externo-estructura-institucional.md#los-permisos-los-define-el-rol-2026-09-30).)*
- **RN-AUTH-ROL-07:** La autorización comprueba el tipo y el estado de la cuenta, el estado de la ficha `personal.personal` (para el Técnico) y que el rol admita el permiso requerido. El Técnico solo ejerce los permisos de ámbito de laboratorio (`reservas.administrar`, `reservas.exportar`, `espacios.administrar`, `recursos.administrar`, `recursos.editar_equipos`, `laboratorios.configurar`, `reportes.consultar`) y únicamente sobre el laboratorio de su cargo; lo demás es del Administrador. Si las condiciones no se cumplen o no pueden comprobarse, se deniega la operación. *(Redefinida el 2026-09-30: los roles son fijos y los permisos los define el rol; ver [la decisión](../../docs/decisions/origen-externo-estructura-institucional.md#los-permisos-los-define-el-rol-2026-09-30).)*
- **RN-AUTH-ROL-08:** La autenticación confirma qué cuenta realiza una operación, pero no determina por sí sola qué operaciones están autorizadas.
- **RN-AUTH-ROL-09:** Siempre debe existir al menos una cuenta activa de tipo `ADMINISTRADOR`. Ninguna operación puede dejar al sistema sin ella: no puede desactivarse la última, ni cambiarse su tipo. La primera se crea con `python -m app.scripts.crear_administrador`, porque para entrar a la interfaz ya hace falta una. *(Redefinida el 2026-09-30: los roles son fijos y los permisos los define el rol; ver [la decisión](../../docs/decisions/origen-externo-estructura-institucional.md#los-permisos-los-define-el-rol-2026-09-30).)*

## Sesiones — RN-AUTH-SES

- **RN-AUTH-SES-01:** Las sesiones se registran en `auth.sesiones` y una sesión revocada o vencida no puede continuar operaciones.
- **RN-AUTH-SES-02:** Cerrar sesión revoca la sesión correspondiente.
- **RN-AUTH-SES-03:** Los cambios de cuenta, identidad o permisos aplican a nuevas decisiones de autorización y no alteran la trazabilidad histórica.
- **RN-AUTH-SES-04:** Después de autenticar una cuenta de Usuario, el sistema debe consultar si la actualización inicial del perfil está pendiente y dirigirla al flujo obligatorio de `usuarios`; la autenticación por sí sola no habilita operaciones de negocio restringidas por RN-USR-07 y RN-USR-08.
- **RN-AUTH-SES-05:** Una sesión revocada o vencida no puede utilizarse para continuar una operación autenticada ni para establecer una sesión nueva.

Las entidades persistentes se detallan en [data-model.md](data-model.md). Los controles técnicos de seguridad se detallan en [security.md](security.md).
