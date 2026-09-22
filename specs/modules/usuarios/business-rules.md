# Usuarios y personal

La estructura persistente está en [data-model](data-model.md) y las reglas del dominio de reservas en [business-rules.md](../reservations/business-rules.md).

Este módulo es propietario de las **identidades funcionales**: `usuarios.usuarios` representa a quien reserva y `personal.personal` al personal institucional. Define sus datos obligatorios, su estado y su relación con el cargo.

No define credenciales, autenticación, sesiones, roles, permisos ni autorización: esos conceptos pertenecen a [Auth](../auth/business-rules.md), que resuelve qué cuenta actúa y qué puede hacer. La auditoría administrativa pertenece a [Administration](../administration/business-rules.md). Las reglas sobre quién puede consultar, editar, aprobar, rechazar o cancelar reservas pertenecen a [Reservations](../reservations/business-rules.md).
---

## Identidad de cuenta y autenticación

La relación entre una cuenta y su identidad funcional la define Auth: `RN-AUTH-ID-01` a `RN-AUTH-ID-12` cubren la cuenta activa, la exclusividad entre `usuarios.usuarios` y `personal.personal`, la inmutabilidad y coincidencia del correo, las vías de alta y la conservación del historial. Las sesiones se rigen por `RN-AUTH-SES` y la autorización administrativa por `RN-AUTH-ROL`.

Este módulo no repite esas reglas. Aporta únicamente las identidades que Auth referencia.
---

## Usuarios — RN-USR

- **RN-USR-01:** `usuarios.usuarios` representa personas que utilizan el sistema principalmente para realizar y gestionar sus propias reservas.

- **RN-USR-02:** Un Usuario autenticado puede crear reservas conforme a las reglas establecidas en [business-rules.md](../reservations/business-rules.md).

- **RN-USR-03:** Un usuario puede consultar sus propias reservas y sus estados.

- **RN-USR-04:** Un usuario puede editar o cancelar únicamente sus propias reservas y únicamente cuando las reglas de negocio del dominio de reservas lo permitan.

- **RN-USR-05:** La vinculación con `usuarios.usuarios` no concede permisos administrativos sobre reservas de terceros.

- **RN-USR-06:** Los perfiles académicos o investigativos, semilleros, proyectos, pasantías, trabajos de grado y modalidades de vinculación no forman parte de la autenticación y se gestionan en el dominio de investigación. El Usuario gestiona únicamente sus propias vinculaciones; las intervenciones sobre vínculos ajenos y las actividades institucionales corresponden al Administrador global conforme a Researchs.
- **RN-USR-07:** En el primer ingreso autenticado, el Usuario debe completar la actualización inicial de sus datos personales y contar con al menos una vinculación académica o investigativa activa y válida a un proyecto, semillero, pasantía o trabajo de grado.
- **RN-USR-08:** Mientras la actualización inicial esté pendiente, el Usuario solo puede acceder a las operaciones necesarias para completar su perfil, seleccionar o mantener sus vinculaciones y cerrar sesión; no puede crear reservas ni ejecutar otras operaciones de negocio que requieran el perfil completo.
- **RN-USR-09:** La actualización inicial puede cumplirse con una o más vinculaciones de cualquier tipo admitido; no exige tener una vinculación de cada tipo. Una actividad institucional no cuenta como vinculación académica o investigativa.
- **RN-USR-10:** Los proyectos y semilleros deben seleccionarse desde los catálogos existentes de `investigacion`; el Usuario no puede crearlos ni ingresar sus nombres o códigos libremente.
- **RN-USR-11:** Después de completar la actualización inicial, el Usuario debe conservar al menos una vinculación académica o investigativa activa y válida de los tipos definidos en RN-USR-07 para crear nuevas reservas. Si no conserva ninguna, se bloquea la creación de nuevas reservas hasta que actualice sus vinculaciones y `investigacion` confirme al menos una activa y válida. Esta condición se verifica con información vigente al crear cada reserva, incluso si su contexto es una actividad institucional o el tipo no requiere contexto. No se reinicia la actualización inicial ni se bloquea el inicio de sesión por esta causa; el Usuario puede actualizar sus vinculaciones y consultar o gestionar reservas existentes conforme a sus reglas, sin alteración automática de su estado o historial.


---

## Datos obligatorios del Usuario — RN-DAT

- **RN-DAT-01:** Toda alta de Usuario debe registrar nombre, documento, teléfono, institución y dependencia. Los cinco campos son obligatorios y no admiten valores vacíos ni compuestos únicamente por espacios. Se solicitan en el autorregistro o en el alta administrativa de la identidad que se invita; se revisan durante la actualización inicial y deben mantenerse completos en posteriores modificaciones.
- **RN-DAT-02:** Documento y teléfono deben ser únicos, cada uno por separado, entre los registros de `usuarios.usuarios`, incluidos los inactivos. El backend valida la unicidad al crear y modificar, excluyendo el propio registro en una edición; la base de datos la garantiza mediante restricciones `UNIQUE`. Un conflicto rechaza la operación y no debe sobrescribir ni fusionar identidades.
- **RN-DAT-03:** Institución y dependencia describen la afiliación del Usuario y se almacenan en su perfil. No conceden permisos administrativos ni sustituyen una vinculación académica o investigativa. Sus valores no son únicos.

## Personal — RN-PRS

- **RN-PRS-01:** `personal.personal` representa personal o contratistas vinculados a las unidades organizacionales correspondientes.

- **RN-PRS-02:** El ámbito organizacional del personal se obtiene mediante la relación `personal -> cargo -> unidad_organizacional`, salvo que el modelo persistente defina una relación adicional explícita.

- **RN-PRS-03:** El cargo determina únicamente la unidad organizacional de pertenencia del Personal. Las acciones autorizadas se determinan exclusivamente mediante `auth.cuenta_permisos` y su alcance, conforme a `RN-AUTH-ROL` de Auth.

- **RN-PRS-04:** Personal inactivo no puede realizar nuevas operaciones administrativas. Las acciones históricas realizadas anteriormente se conservan.

- **RN-PRS-05:** Toda ficha de `personal.personal` debe registrar nombre, documento, correo, teléfono y cargo. Documento, correo y teléfono deben ser únicos en la tabla; el cargo debe existir y determina la unidad organizacional del personal. Administración captura y valida estos datos mediante este dominio antes de solicitar a Auth una invitación `PERSONAL`; Auth no crea ni completa la ficha.

Las condiciones bajo las cuales una cuenta vinculada a `personal.personal` puede ejercer permisos administrativos, el ámbito en que puede hacerlo y la exclusividad frente a `usuarios.usuarios` se definen en `RN-AUTH-ROL-02`, `RN-AUTH-ROL-06`, `RN-AUTH-ROL-07` y `RN-AUTH-ID-03` de Auth. Las condiciones bajo las cuales una cuenta `PERSONAL` puede crear reservas se definen en `RN-RES-15` de Reservations.


## Autenticación, autorización y auditoría

Ninguno de estos conceptos se define en este módulo.

- **Credenciales, autenticación y sesiones:** `RN-AUTH-ID` y `RN-AUTH-SES` de [Auth](../auth/business-rules.md). Las credenciales se administran exclusivamente en el schema `auth` y nunca en `usuarios.usuarios` ni en `personal.personal`.
- **Roles, permisos, ámbito y autorización administrativa:** `RN-AUTH-ROL` de Auth, junto con `RN-PER` de [Administration](../administration/business-rules.md), que define cómo se representan y asignan los permisos.
- **Auditoría administrativa:** `RN-AUD` de Administration.
- **Autorización sobre reservas:** `RN-RES`, `RN-APR` y `RN-CAN` de [Reservations](../reservations/business-rules.md).


## Separación de responsabilidades

- `auth.cuentas` responde: **quién puede autenticarse**.
- `auth.sesiones` responde: **qué sesiones están vigentes**.
- `usuarios.usuarios` responde: **quién es el usuario que reserva**.
- `personal.personal` responde: **quién es el personal institucional**.
- `cargos.cargo` responde: **a qué unidad organizacional pertenece el personal**, conforme a `RN-PRS-03`.
- `auth.permisos` y `auth.cuenta_permisos` responden: **qué acciones administrativas puede realizar y en qué ámbito**, conforme a `RN-AUTH-ROL` de Auth.
- `investigacion.*` describe el contexto académico o investigativo del usuario y no concede permisos administrativos.

---

## Dependencias funcionales

- **Reservas:** define qué acciones sobre reservas requieren autorización y bajo qué condiciones funcionales.
- **Personal y cargos:** determinan la relación del personal con cargos, unidades organizacionales y permisos.
- **Usuarios:** contiene la información funcional del reservista que no pertenece al dominio de autenticación.
- **Investigación:** administra perfiles académicos, proyectos, semilleros, pasantías, trabajos de grado y sus vinculaciones con el usuario, así como las modalidades de vinculación.
- **Notificaciones:** gestiona la entrega de notificaciones derivadas de eventos del dominio de identidad y autorización.
- **Modelo persistente:** [data-model](../../docs/data-model.md) define claves, relaciones, restricciones e integridad referencial.

---

## Preguntas abiertas

- ¿Un registro de `personal.personal` puede tener más de un cargo o unidad organizacional vigente simultáneamente, o exactamente uno a la vez?
- ¿Cómo se relaciona el ámbito de una `unidad_organizacional` con la configuración local de reservas de un laboratorio, como horario y aprobación automática?
- ¿El dominio `investigacion.*` requiere reglas propias de autorización para administrar proyectos y semilleros?
- ¿Una cuenta vinculada a `personal.personal` inactiva conserva explícitamente su relación histórica con cargo y unidad organizacional para efectos de auditoría?
