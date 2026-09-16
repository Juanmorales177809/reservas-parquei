# Identidad y autorización

La estructura persistente está en [data-model](../core/data-model.md) y las reglas del dominio de reservas en [bookings](bookings.md).

La autenticación pertenece al schema `auth`. Las identidades funcionales se representan mediante `usuarios.usuarios` y `personal.personal`. La autorización administrativa del personal se determina a partir de su cargo, unidad organizacional y permisos vigentes.

---

## Cuentas e identidades — RN-ID

- **RN-ID-01:** Toda operación que requiera autenticación debe realizarse mediante una cuenta activa registrada en `auth.cuentas`.

- **RN-ID-02:** Una cuenta de tipo `USUARIO` debe estar asociada a un único registro de `usuarios.usuarios`.

- **RN-ID-03:** Una cuenta de tipo `PERSONAL` debe estar asociada a un único registro de `personal.personal`.

- **RN-ID-04:** Una cuenta no puede estar asociada simultáneamente a `usuarios.usuarios` y `personal.personal`.

- **RN-ID-05:** El tipo de cuenta solo identifica la clase de identidad asociada; no concede por sí mismo permisos administrativos.

- **RN-ID-06:** Una cuenta inactiva no puede iniciar nuevas operaciones autenticadas. Su desactivación no elimina ni modifica información histórica asociada.

- **RN-ID-07:** La identidad autenticada se determina exclusivamente a partir de una cuenta validada. No se identifica a una persona por nombre, correo enviado por el cliente u otro dato no verificado.

---

## Usuarios — RN-USR

- **RN-USR-01:** `usuarios.usuarios` representa personas que utilizan el sistema principalmente para realizar y gestionar sus propias reservas.

- **RN-USR-02:** Un usuario autenticado puede crear reservas conforme a las reglas establecidas en [bookings](bookings.md).

- **RN-USR-03:** Un usuario puede consultar sus propias reservas y sus estados.

- **RN-USR-04:** Un usuario puede editar o cancelar únicamente sus propias reservas y únicamente cuando las reglas de negocio lo permitan.

- **RN-USR-05:** Una cuenta de tipo `USUARIO` no dispone de permisos administrativos sobre reservas de terceros.

- **RN-USR-06:** Los perfiles académicos o investigativos, semilleros, proyectos y modalidades de vinculación no forman parte de la autenticación y se gestionan en el dominio de investigación.

---

## Personal — RN-PER

- **RN-PER-01:** `personal.personal` representa personal o contratistas vinculados a las unidades organizacionales del laboratorio.

- **RN-PER-02:** El ámbito organizacional del personal se obtiene mediante la relación `personal -> cargo -> unidad_organizacional`.

- **RN-PER-03:** El cargo determina las acciones que pueden ser autorizadas y la unidad organizacional determina el ámbito donde pueden ejercerse.

- **RN-PER-04:** Pertenecer a una unidad organizacional no concede automáticamente todas las acciones administrativas disponibles en dicha unidad.

- **RN-PER-05:** Una cuenta asociada a personal solo puede ejercer permisos administrativos cuando la cuenta esté activa, el registro de personal esté activo y la relación de cargo y unidad organizacional que sustenta la autorización sea válida.

- **RN-PER-06:** Personal inactivo no puede realizar nuevas operaciones administrativas. Las acciones históricas realizadas anteriormente se conservan.

- **RN-PER-07:** Una cuenta de tipo `PERSONAL` puede realizar reservas propias además de las operaciones administrativas que le hayan sido autorizadas.

---

## Autenticación — RN-AUT

- **RN-AUT-01:** Las credenciales de acceso se almacenan exclusivamente en el dominio `auth` y no en `usuarios.usuarios` ni en `personal.personal`.

- **RN-AUT-02:** Las contraseñas nunca se almacenan en texto plano.

- **RN-AUT-03:** Toda autenticación válida genera una identidad verificable asociada a `auth.cuentas`.

- **RN-AUT-04:** Los tokens de acceso deben validarse por firma, vigencia y tipo antes de aceptar una operación autenticada.

- **RN-AUT-05:** Los secretos, hashes de contraseñas, refresh tokens y claves privadas no se exponen al frontend ni mediante endpoints de consulta.

- **RN-AUT-06:** Las sesiones se administran mediante `auth.sesiones`.

- **RN-AUT-07:** Una sesión revocada o vencida no puede utilizarse para obtener nuevos tokens de acceso.

- **RN-AUT-08:** La autenticación confirma quién realiza una operación, pero no determina por sí sola qué operaciones están autorizadas.

---

## Autorización — RN-AUTZ

- **RN-AUTZ-01:** Toda acción administrativa requiere una cuenta activa asociada a `personal.personal`.

- **RN-AUTZ-02:** La autorización debe comprobar como mínimo cuenta, estado del personal, cargo, unidad organizacional, permiso requerido y ámbito de actuación.

- **RN-AUTZ-03:** La autorización administrativa se evalúa con información vigente al momento de ejecutar la operación.

- **RN-AUTZ-04:** El cargo no debe evaluarse mediante comparaciones de nombres hardcodeadas en la aplicación; las acciones permitidas deben derivarse del modelo de permisos definido para el sistema.

- **RN-AUTZ-05:** El personal autorizado solo puede ejercer una operación dentro de las unidades comprendidas en su ámbito de autorización.

- **RN-AUTZ-06:** Una cuenta de tipo `PERSONAL` sin el permiso requerido se comporta como una cuenta sin autorización administrativa para dicha operación.

- **RN-AUTZ-07:** Las reglas específicas de quién puede consultar, editar, aprobar, rechazar o cancelar reservas se establecen en [bookings](bookings.md).

---

## Auditoría de identidad y autorización — RN-AUD

- **RN-AUD-01:** Toda operación administrativa sensible debe identificar la cuenta autenticada que la ejecutó.

- **RN-AUD-02:** La auditoría debe conservar actor, acción y momento de ejecución, además de la información necesaria para representar históricamente al actor.

- **RN-AUD-03:** La auditoría no crea duplicados de `usuarios.usuarios` ni de `personal.personal`.

- **RN-AUD-04:** La desactivación posterior de una cuenta, usuario, persona, cargo o unidad no elimina ni altera el historial de auditoría.

---

## Separación de responsabilidades

- `auth.cuentas` responde: **quién puede autenticarse**.
- `auth.sesiones` responde: **qué sesiones están vigentes**.
- `usuarios.usuarios` responde: **quién es el usuario reservista**.
- `personal.personal` responde: **quién es el personal institucional**.
- `cargos.cargo` y el modelo de permisos responden: **qué acciones administrativas puede realizar el personal**.
- `unidadOrganizacional.unidad_organizacional` responde: **en qué ámbito puede ejercer dichas acciones**.
- `investigacion.*` describe el contexto académico o investigativo del usuario y no concede permisos administrativos.