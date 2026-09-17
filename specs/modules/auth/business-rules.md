# Identidad y autorización

La estructura persistente está en [data-model](../core/data-model.md) y las reglas del dominio de reservas en [business-rules.md](../modules/reservas/business-rules.md).

La autenticación pertenece al schema `auth`. Las identidades funcionales se representan mediante `usuarios.usuarios` y `personal.personal`. Una misma cuenta puede estar vinculada a ambas entidades cuando la persona cumple simultáneamente ambas condiciones dentro del sistema. La autorización administrativa del personal se determina a partir de su cargo, unidad organizacional y permisos vigentes.

---

## Cuentas e identidades — RN-ID

- **RN-ID-01:** Toda operación que requiera autenticación debe realizarse mediante una cuenta activa registrada en `auth.cuentas`.

- **RN-ID-02:** Una cuenta puede estar asociada a un único registro de `usuarios.usuarios`.

- **RN-ID-03:** Una cuenta puede estar asociada a un único registro de `personal.personal`.

- **RN-ID-04:** Una misma cuenta puede estar vinculada simultáneamente a `usuarios.usuarios` y `personal.personal` cuando la misma persona cumple ambas condiciones dentro del sistema.

- **RN-ID-05:** La existencia de una vinculación con `usuarios.usuarios` o `personal.personal` no elimina ni reemplaza la otra vinculación existente.

- **RN-ID-06:** La vinculación de una cuenta con `usuarios.usuarios` o `personal.personal` no concede por sí misma permisos administrativos.

- **RN-ID-07:** Una cuenta inactiva no puede iniciar nuevas operaciones autenticadas. Su desactivación no elimina ni modifica información histórica asociada.

- **RN-ID-08:** La identidad autenticada se determina exclusivamente a partir de una cuenta validada. No se identifica a una persona por nombre, correo enviado por el cliente u otro dato no verificado.

- **RN-ID-09:** Una cuenta se crea por una de dos vías: invitación emitida por una cuenta con permiso de administración, o autorregistro abierto sin aprobación previa. El autorregistro solo permite crear una cuenta vinculada inicialmente como usuario y nunca permite autoasignarse permisos administrativos ni una vinculación como personal.

- **RN-ID-10:** Una cuenta que no completó su proceso de alta puede recibir una nueva invitación sin que eso duplique su identidad ni impida reintentar el alta.

- **RN-ID-11:** El historial de reservas, notificaciones y auditoría debe mantenerse asociado a la misma cuenta, independientemente de que esta tenga vinculación con `usuarios.usuarios`, `personal.personal` o ambas.

---

## Usuarios — RN-USR

- **RN-USR-01:** `usuarios.usuarios` representa personas que utilizan el sistema principalmente para realizar y gestionar sus propias reservas.

- **RN-USR-02:** Un usuario autenticado puede crear reservas conforme a las reglas establecidas en [business-rules.md](../modules/reservas/business-rules.md).

- **RN-USR-03:** Un usuario puede consultar sus propias reservas y sus estados.

- **RN-USR-04:** Un usuario puede editar o cancelar únicamente sus propias reservas y únicamente cuando las reglas de negocio del dominio de reservas lo permitan.

- **RN-USR-05:** La vinculación con `usuarios.usuarios` no concede permisos administrativos sobre reservas de terceros.

- **RN-USR-06:** Los perfiles académicos o investigativos, semilleros, proyectos y modalidades de vinculación no forman parte de la autenticación y se gestionan en el dominio de investigación.

- **RN-USR-07:** Una cuenta vinculada a `usuarios.usuarios` debe completar los datos mínimos de perfil requeridos antes de poder crear una reserva.

---

## Personal — RN-PER

- **RN-PER-01:** `personal.personal` representa personal o contratistas vinculados a las unidades organizacionales correspondientes.

- **RN-PER-02:** El ámbito organizacional del personal se obtiene mediante la relación `personal -> cargo -> unidad_organizacional`, salvo que el modelo persistente defina una relación adicional explícita.

- **RN-PER-03:** El cargo determina las acciones que pueden ser autorizadas y la unidad organizacional determina el ámbito donde pueden ejercerse.

- **RN-PER-04:** Pertenecer a una unidad organizacional no concede automáticamente todas las acciones administrativas disponibles en dicha unidad.

- **RN-PER-05:** Una cuenta vinculada a `personal.personal` solo puede ejercer permisos administrativos cuando la cuenta esté activa, el registro de personal esté activo y la relación de cargo, unidad organizacional y permisos que sustenta la autorización sea válida.

- **RN-PER-06:** Personal inactivo no puede realizar nuevas operaciones administrativas. Las acciones históricas realizadas anteriormente se conservan.

- **RN-PER-07:** Una cuenta vinculada a `personal.personal` puede realizar reservas propias además de las operaciones administrativas que le hayan sido autorizadas.

- **RN-PER-08:** La vinculación simultánea con `usuarios.usuarios` y `personal.personal` representa una única cuenta con dos relaciones funcionales; no crea cuentas duplicadas ni identidades independientes.

- **RN-PER-09:** Siempre debe existir al menos una cuenta vinculada a `personal.personal` con permisos de administración global vigentes. Ninguna operación puede eliminar, degradar o inhabilitar la última cuenta que los posee.

---

## Autenticación — RN-AUT

- **RN-AUT-01:** Las credenciales de acceso se administran exclusivamente en el dominio `auth` y no en `usuarios.usuarios` ni en `personal.personal`.

- **RN-AUT-02:** Toda autenticación válida establece una identidad verificable asociada a `auth.cuentas`.

- **RN-AUT-03:** Las sesiones autenticadas se administran mediante `auth.sesiones`.

- **RN-AUT-04:** Una sesión revocada o vencida no puede utilizarse para continuar una operación autenticada ni para establecer una nueva sesión válida.

- **RN-AUT-05:** La autenticación confirma qué cuenta realiza una operación, pero no determina por sí sola qué operaciones están autorizadas.

- **RN-AUT-06:** Cerrar sesión debe finalizar la sesión autenticada correspondiente en `auth.sesiones`.

---

## Autorización — RN-AUTZ

- **RN-AUTZ-01:** Toda acción administrativa requiere una cuenta activa vinculada a `personal.personal`.

- **RN-AUTZ-02:** La autorización debe comprobar como mínimo la cuenta autenticada, el estado del personal, el cargo, la unidad organizacional, el permiso requerido y el ámbito de actuación.

- **RN-AUTZ-03:** La autorización administrativa se evalúa con información vigente al momento de ejecutar la operación.

- **RN-AUTZ-04:** El cargo no debe evaluarse mediante comparaciones de nombres fijos en la aplicación; las acciones permitidas deben derivarse del modelo de permisos definido para el sistema.

- **RN-AUTZ-05:** El personal autorizado solo puede ejercer una operación dentro de las unidades comprendidas en su ámbito de autorización.

- **RN-AUTZ-06:** Una cuenta vinculada a `personal.personal` sin el permiso requerido se comporta como una cuenta sin autorización administrativa para dicha operación.

- **RN-AUTZ-07:** Las reglas específicas de quién puede consultar, editar, aprobar, rechazar o cancelar reservas se establecen en el dominio de reservas.

- **RN-AUTZ-08:** Un cambio de cargo, unidad organizacional o permisos vigentes de una cuenta vinculada a personal debe quedar registrado en auditoría.

---

## Auditoría de identidad y autorización — RN-AUD

- **RN-AUD-01:** Toda operación administrativa sensible debe identificar la cuenta autenticada que la ejecutó.

- **RN-AUD-02:** La auditoría debe conservar como mínimo actor, acción y momento de ejecución, además de la información necesaria para representar históricamente al actor.

- **RN-AUD-03:** La auditoría no crea duplicados de `usuarios.usuarios`, `personal.personal` ni `auth.cuentas`.

- **RN-AUD-04:** La desactivación posterior de una cuenta, usuario, personal, cargo o unidad organizacional no elimina ni altera el historial de auditoría.

---

## Separación de responsabilidades

- `auth.cuentas` responde: **quién puede autenticarse**.
- `auth.sesiones` responde: **qué sesiones están vigentes**.
- `usuarios.usuarios` responde: **quién es el usuario que reserva**.
- `personal.personal` responde: **quién es el personal institucional**.
- `cargos.cargo` y el modelo de permisos responden: **qué acciones administrativas puede realizar el personal**.
- `unidadOrganizacional.unidad_organizacional` responde: **en qué ámbito puede ejercer dichas acciones**.
- `investigacion.*` describe el contexto académico o investigativo del usuario y no concede permisos administrativos.

---

## Dependencias funcionales

- **Reservas:** define qué acciones sobre reservas requieren autorización y bajo qué condiciones funcionales.
- **Personal y cargos:** determinan la relación del personal con cargos, unidades organizacionales y permisos.
- **Usuarios:** contiene la información funcional del reservista que no pertenece al dominio de autenticación.
- **Investigación:** administra perfiles académicos, proyectos, semilleros y modalidades de vinculación.
- **Notificaciones:** gestiona la entrega de notificaciones derivadas de eventos del dominio de identidad y autorización.
- **Modelo persistente:** [data-model](../core/data-model.md) define claves, relaciones, restricciones e integridad referencial.

---

## Preguntas abiertas

- ¿Un registro de `personal.personal` puede tener más de un cargo o unidad organizacional vigente simultáneamente, o exactamente uno a la vez?
- ¿Cómo se relaciona el ámbito de una `unidad_organizacional` con la configuración local de reservas de un laboratorio, como horario y aprobación automática?
- ¿El dominio `investigacion.*` requiere reglas propias de autorización para administrar proyectos y semilleros?
- ¿Una cuenta vinculada a `personal.personal` inactiva conserva explícitamente su relación histórica con cargo y unidad organizacional para efectos de auditoría?
