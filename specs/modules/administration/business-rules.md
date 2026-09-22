# Administración

Contrato funcional del módulo de administración.

El módulo de administración permite gestionar la configuración institucional necesaria para operar Reservas Parquei, incluyendo usuarios, cuentas, perfiles, unidades organizacionales, permisos y configuraciones globales. El Técnico opera únicamente dentro de su propia unidad; el Administrador tiene alcance global.

Las reglas específicas de autenticación y autorización pertenecen al módulo correspondiente. Las reglas de reservas, recursos, notificaciones y reportes permanecen bajo responsabilidad de sus respectivos módulos.

---

## Gestión administrativa — RN-ADM

- **RN-ADM-01:** Toda operación administrativa requiere una cuenta autenticada y autorizada para la acción correspondiente.

- **RN-ADM-02:** Las operaciones administrativas deben respetar el ámbito de autorización asociado a la cuenta que las ejecuta.

- **RN-ADM-03:** El módulo de administración no puede otorgar capacidades que contradigan las restricciones globales definidas para autenticación, autorización o seguridad.

- **RN-ADM-04:** Las operaciones administrativas relevantes deben quedar registradas para efectos de trazabilidad.

- **RN-ADM-05:** La desactivación de un elemento administrado no debe eliminar información histórica asociada.

---

## Usuarios — RN-USR

- **RN-USR-01:** El administrador institucional puede crear, consultar, modificar, habilitar o deshabilitar usuarios cuando disponga del permiso correspondiente.

- **RN-USR-02:** La modificación de información de un usuario no debe alterar retroactivamente las reservas, acciones o registros históricos asociados.

- **RN-USR-03:** Deshabilitar un usuario impide nuevas operaciones que requieran una identidad activa, sin eliminar su información histórica.

- **RN-USR-04:** La eliminación física de usuarios con información histórica asociada no debe utilizarse como mecanismo ordinario de administración.

- **RN-USR-05:** La información administrativa de un usuario debe mantenerse separada de sus credenciales de autenticación cuando dichas responsabilidades pertenezcan a estructuras distintas del sistema.
- **RN-USR-06:** El alta y la edición administrativa de Usuarios aplican RN-DAT del módulo Usuarios. Para invitar una cuenta de tipo `USUARIO`, debe existir previamente una identidad con esos datos obligatorios y válidos; la invitación y el alta administrativa no completan la actualización inicial por el Usuario.
- **RN-USR-07:** Antes de invitar una cuenta de tipo `PERSONAL`, Administración debe registrar o verificar una ficha activa y completa en `personal.personal` conforme a RN-PER-11 de Usuarios. Después solicita la invitación a Auth con el correo de esa ficha y la unidad de su cargo; Auth resuelve y vincula el `id_persona`. Administración no crea credenciales ni duplica la identidad en Auth.

---

## Cuentas — RN-CUE

- **RN-CUE-01:** La administración de cuentas debe preservar la relación entre la cuenta y la identidad funcional asociada.

- **RN-CUE-02:** Una cuenta habilitada debe cumplir las reglas de identidad y autenticación definidas por el módulo correspondiente.

- **RN-CUE-03:** Deshabilitar una cuenta impide nuevas operaciones autenticadas realizadas mediante dicha cuenta.

- **RN-CUE-04:** Deshabilitar una cuenta no elimina reservas, auditorías, notificaciones ni otros registros históricos previamente asociados.

- **RN-CUE-05:** Las credenciales, hashes, tokens, sesiones y secretos no deben exponerse mediante funciones administrativas ordinarias.

- **RN-CUE-06:** El módulo de administración no modifica directamente mecanismos criptográficos ni reglas de validación de tokens.

---

## Perfiles — RN-PRF

- **RN-PRF-01:** Los perfiles utilizados para clasificar o caracterizar usuarios deben gestionarse mediante identificadores persistentes y no mediante valores hardcodeados en la aplicación.

- **RN-PRF-02:** La asignación o retiro de un perfil no debe modificar retroactivamente el contexto registrado en operaciones históricas.

- **RN-PRF-03:** Un perfil no concede permisos administrativos por sí mismo salvo que exista una regla explícita de autorización que lo establezca.

- **RN-PRF-04:** Los perfiles deshabilitados no deben asignarse en nuevas operaciones mientras permanezcan inactivos.

- **RN-PRF-05:** Deshabilitar un perfil conserva las relaciones históricas existentes.

---

## Unidades organizacionales — RN-UNI

- **RN-UNI-01:** El administrador institucional puede gestionar las unidades organizacionales conforme a los permisos definidos para su cuenta.

- **RN-UNI-02:** Una unidad organizacional debe mantener un identificador persistente independiente de su nombre visible.

- **RN-UNI-03:** El nombre de una unidad puede modificarse sin cambiar su identidad interna.

- **RN-UNI-04:** Deshabilitar una unidad no elimina automáticamente usuarios, personal, reservas, recursos ni información histórica asociada.

- **RN-UNI-05:** Una unidad deshabilitada no debe utilizarse para nuevas configuraciones u operaciones cuando estas requieran una unidad activa.

- **RN-UNI-06:** La existencia de una unidad organizacional no implica por sí sola que pueda recibir reservas.

- **RN-UNI-07:** Las condiciones específicas para habilitar reservas sobre una unidad pertenecen al módulo responsable de recursos y configuración de reservas.

---

## Permisos — RN-PER

- **RN-PER-01:** Los permisos administrativos deben representarse explícitamente mediante el modelo de autorización definido por el sistema.

- **RN-PER-02:** Los permisos no deben determinarse mediante comparaciones hardcodeadas de nombres de cargos, perfiles o usuarios.

- **RN-PER-03:** Asignar un permiso requiere autorización suficiente para administrar dicho permiso.

- **RN-PER-04:** Retirar un permiso afecta nuevas decisiones de autorización desde el momento en que el cambio entra en vigencia.

- **RN-PER-05:** La modificación de permisos no altera retroactivamente la validez histórica de acciones ejecutadas cuando la autorización era válida.

- **RN-PER-06:** La existencia de un permiso no amplía automáticamente su ámbito organizacional.

- **RN-PER-07:** El ámbito en que puede ejercerse un permiso debe evaluarse conjuntamente con la identidad y contexto organizacional definidos por el módulo de autorización.

- **RN-PER-08:** Solo pueden recibir permisos administrativos las cuentas activas de tipo `PERSONAL`, vinculadas a un registro activo de `personal.personal`. Las cuentas de tipo `USUARIO` no pueden recibir asignaciones de `auth.cuenta_permisos`.

- **RN-PER-09:** Al asignar un permiso acotado a unidad a una cuenta `PERSONAL`, la unidad debe coincidir con la asociada a su cargo vigente. El sistema debe rechazar asignaciones para otra unidad. Una asignación global debe registrarse explícitamente con `id_unidad NULL`; su evaluación se rige por `RN-AUTH-ROL-03` y no puede usarse para ampliar tácitamente el alcance de un Técnico.

---

## Configuración global — RN-CFG

- **RN-CFG-01:** Solo usuarios autorizados pueden modificar configuraciones globales del sistema.

- **RN-CFG-02:** Toda configuración debe contar con una representación persistente o mecanismo de configuración claramente definido cuando su modificación afecte el comportamiento del sistema.

- **RN-CFG-03:** Una configuración global no debe utilizarse para reemplazar reglas de negocio que pertenecen a módulos específicos.

- **RN-CFG-04:** Los cambios de configuración deben validarse antes de entrar en vigencia.

- **RN-CFG-05:** Una configuración inválida no debe dejar el sistema en un estado parcialmente actualizado.

- **RN-CFG-06:** Cuando una configuración afecte nuevas operaciones, su modificación no debe reinterpretar automáticamente registros históricos.

- **RN-CFG-07:** Las configuraciones que afecten seguridad, autenticación o autorización deben respetar las restricciones definidas por dichos módulos.

---

## Habilitación y desactivación — RN-HAB

- **RN-HAB-01:** Siempre que el modelo lo permita, la desactivación debe preferirse sobre la eliminación física de elementos con relaciones históricas.

- **RN-HAB-02:** Un elemento deshabilitado no debe utilizarse en nuevas operaciones que requieran que dicho elemento se encuentre activo.

- **RN-HAB-03:** La desactivación conserva identificadores, relaciones e información histórica.

- **RN-HAB-04:** La reactivación de un elemento no debe crear una nueva identidad cuando corresponda al mismo registro persistente.

- **RN-HAB-05:** La desactivación de una entidad no debe propagarse automáticamente a otras entidades salvo que exista una regla explícita que lo establezca.

---

## Auditoría administrativa — RN-AUD

- **RN-AUD-01:** Las operaciones administrativas relevantes deben registrar la cuenta que ejecutó la acción.

- **RN-AUD-02:** El registro debe incluir como mínimo actor, acción, entidad afectada, identificador y fecha/hora.

- **RN-AUD-03:** Cuando una operación cambie información administrativa relevante, el registro debe permitir identificar el cambio realizado cuando corresponda.

- **RN-AUD-04:** La auditoría debe conservarse aunque posteriormente se desactive la cuenta o entidad relacionada.

- **RN-AUD-05:** Los registros de auditoría no deben modificarse para reflejar valores actuales cuando ello altere la representación histórica de la acción ejecutada.

---

## Integridad administrativa — RN-INT

- **RN-INT-01:** Una operación administrativa que afecte varias entidades relacionadas debe preservar la consistencia de los datos.

- **RN-INT-02:** Si una operación no puede completarse correctamente, no debe dejar cambios parciales que contradigan las reglas del sistema.

- **RN-INT-03:** Antes de modificar o deshabilitar una entidad, deben validarse las restricciones y dependencias aplicables.

- **RN-INT-04:** El módulo de administración no debe eludir restricciones definidas por otros módulos mediante actualizaciones directas de datos.

---

## Importación de catálogos de investigación — RN-IMP

- **RN-IMP-01:** Solo el Administrador puede importar proyectos y semilleros mediante un archivo Excel, con autorización global vigente.
- **RN-IMP-02:** El archivo debe identificar cada registro mediante `codigo`, incluir `nombre` y `estado`, y señalar el tipo de catálogo que se importa. La columna `estado` admite únicamente los valores `ACTIVO` e `INACTIVO`, sin distinguir mayúsculas y recortando los espacios circundantes; cualquier otro valor, incluido el vacío, invalida la fila.
- **RN-IMP-03:** Antes de guardar, el sistema debe validar columnas, campos obligatorios, estados permitidos, códigos duplicados dentro del archivo y el formato del archivo.
- **RN-IMP-04:** El `codigo` se normaliza recortando espacios y convirtiendo a mayúsculas, tanto para comparar como para almacenar. Un código existente actualiza el registro correspondiente; un código nuevo crea un registro en `investigacion`, cuya clave primaria genera la base de datos. Reimportar el mismo archivo no crea duplicados, y dos filas cuyo código normalizado coincida se rechazan como duplicadas conforme a `RN-IMP-03`.
- **RN-IMP-05:** La importación no crea ni modifica vinculaciones de usuarios y no permite al Administrador reemplazar las reglas de Researchs sobre dichas vinculaciones.
- **RN-IMP-06:** Una importación con errores no debe dejar cambios parciales; el Administrador debe revisar el resultado de validación antes de confirmar.
- **RN-IMP-07:** Desactivar un proyecto o semillero conserva su registro, sus vinculaciones y las referencias históricas de reservas.
- **RN-IMP-08:** Cada importación confirmada registra Administrador, fecha, catálogo, archivo o referencia de carga y registros creados, actualizados o desactivados.
- **RN-IMP-09:** La importación es incremental: un registro existente que no aparezca en el archivo permanece sin cambios. Desactivar un proyecto o semillero requiere incluirlo expresamente con estado `INACTIVO`; la ausencia de una fila nunca desactiva registros.

---

## Separación de responsabilidades

- El módulo de administración gestiona usuarios, cuentas, perfiles, unidades organizacionales, permisos, configuración global e importaciones autorizadas de catálogos de investigación.

- El módulo de autenticación y autorización determina cómo se autentica una cuenta y cómo se evalúa si puede ejecutar una operación.

- El módulo de reservas determina las reglas del ciclo de vida de las reservas.

- El módulo de recursos determina las reglas de laboratorios, espacios y recursos reservables.

- El módulo de notificaciones determina la generación y gestión de notificaciones.

- El módulo de reportes determina las reglas de consulta, consolidación y exportación de información.

- El módulo de administración no redefine las reglas funcionales pertenecientes a otros módulos.

---

## Dependencias funcionales

Las reglas de este documento dependen de otros módulos únicamente en los siguientes aspectos:

- **Autenticación y autorización:** determina identidad autenticada, permisos y ámbito de actuación.

- **Reservas:** determina las restricciones que deben respetarse cuando una acción administrativa afecta una reserva.

- **Recursos:** determina las restricciones asociadas a laboratorios, espacios y recursos.

- **Modelo persistente:** define claves, relaciones, restricciones y dependencias entre las entidades administradas.
- **Researchs:** conserva la propiedad de proyectos, semilleros y sus vinculaciones; Administration solo ejecuta la importación autorizada.

---

## Principios del módulo

1. Administrar una entidad no implica ignorar las reglas del módulo propietario.

2. La autorización debe verificarse antes de ejecutar cualquier operación administrativa protegida.

3. Las entidades con información histórica asociada deben conservar su identidad aun cuando sean deshabilitadas.

4. Los cambios administrativos afectan operaciones futuras desde su entrada en vigencia y no reinterpretan automáticamente información histórica.

5. Los permisos deben ser explícitos y no depender de nombres hardcodeados.

6. La administración debe preservar consistencia, trazabilidad y separación de responsabilidades.
