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

- **RN-USR-01:** El Administrador con el permiso global correspondiente puede crear, consultar, modificar, habilitar o deshabilitar usuarios. Estas operaciones no tienen alcance por unidad y un Técnico no puede ejecutarlas.

- **RN-USR-02:** La modificación de información de un usuario no debe alterar retroactivamente las reservas, acciones o registros históricos asociados.

- **RN-USR-03:** Deshabilitar un usuario impide nuevas operaciones que requieran una identidad activa, sin eliminar su información histórica.

- **RN-USR-04:** La eliminación física de usuarios con información histórica asociada no debe utilizarse como mecanismo ordinario de administración.

- **RN-USR-05:** La información administrativa de un usuario debe mantenerse separada de sus credenciales de autenticación cuando dichas responsabilidades pertenezcan a estructuras distintas del sistema.
- **RN-USR-06:** El alta y la edición administrativa de Usuarios aplican RN-DAT del módulo Usuarios. Para invitar una cuenta de tipo `USUARIO`, debe existir previamente una identidad con esos datos obligatorios y válidos; la invitación y el alta administrativa no completan la actualización inicial por el Usuario.
- **RN-USR-07:** Antes de invitar una cuenta de tipo `PERSONAL`, Administración debe registrar o verificar una ficha activa y completa en `personal.personal` conforme a RN-PRS-05 de Usuarios. Después solicita la invitación a Auth con el correo de esa ficha y la unidad de su cargo; Auth resuelve y vincula el `id_persona`. Administración no crea credenciales ni duplica la identidad en Auth.

---

## Cuentas — RN-CUE

- **RN-CUE-01:** La administración de cuentas debe preservar la relación entre la cuenta y la identidad funcional asociada.

- **RN-CUE-02:** Una cuenta habilitada debe cumplir las reglas de identidad y autenticación definidas por el módulo correspondiente.

- **RN-CUE-03:** Deshabilitar una cuenta impide nuevas operaciones autenticadas realizadas mediante dicha cuenta.

- **RN-CUE-04:** Deshabilitar una cuenta no elimina reservas, auditorías, notificaciones ni otros registros históricos previamente asociados.

- **RN-CUE-05:** Las credenciales, hashes, tokens, sesiones y secretos no deben exponerse mediante funciones administrativas ordinarias.

- **RN-CUE-06:** El módulo de administración no modifica directamente mecanismos criptográficos ni reglas de validación de tokens.

---

## Perfiles académicos e investigativos

Los perfiles académicos o investigativos pertenecen a [Researchs](../researchs/business-rules.md), que define su catálogo, su asociación con usuarios y su desactivación en `RN-INV-12` a `RN-INV-16`. Administration no los administra ni redefine sus reglas.

La autorización aplicable es la general de este módulo: gestionar el catálogo exige alcance global conforme a `RN-INV-15` de Researchs y `RN-AUTH-ROL-03` de Auth.


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

- **RN-AUD-06:** Un cambio de cargo, unidad organizacional o permisos vigentes de una cuenta vinculada a `personal.personal` debe quedar registrado en auditoría.

- **RN-AUD-07:** La auditoría no crea duplicados de `usuarios.usuarios`, `personal.personal` ni `auth.cuentas`. El actor se identifica mediante `actor_cuenta_id`, y su representación histórica se conserva porque esas identidades no se eliminan físicamente conforme a `RN-USR-04` y `RN-HAB-01`.

---

## Integridad administrativa — RN-INT

- **RN-INT-01:** Una operación administrativa que afecte varias entidades relacionadas debe preservar la consistencia de los datos.

- **RN-INT-02:** Si una operación no puede completarse correctamente, no debe dejar cambios parciales que contradigan las reglas del sistema.

- **RN-INT-03:** Antes de modificar o deshabilitar una entidad, deben validarse las restricciones y dependencias aplicables.

- **RN-INT-04:** El módulo de administración no debe eludir restricciones definidas por otros módulos mediante actualizaciones directas de datos.

---

## Importación masiva de catálogos — RN-IMP

- **RN-IMP-01:** Solo el Administrador puede ejecutar una importación masiva, con autorización global vigente. Los catálogos importables son `PROYECTOS`, `SEMILLEROS` y `EQUIPOS`. Administration autoriza, orquesta y registra la carga en los tres casos; las entidades se escriben siempre en el módulo propietario: `investigacion` para proyectos y semilleros, `recursos` para equipos.
- **RN-IMP-02:** Para los catálogos `PROYECTOS` y `SEMILLEROS`, el archivo debe identificar cada registro mediante `codigo`, incluir `nombre` y `estado`, y señalar el tipo de catálogo que se importa. La columna `estado` admite únicamente los valores `ACTIVO` e `INACTIVO`, sin distinguir mayúsculas y recortando los espacios circundantes; cualquier otro valor, incluido el vacío, invalida la fila.
- **RN-IMP-03:** Antes de guardar, el sistema debe validar el formato del archivo, sus columnas, los campos obligatorios y los registros duplicados dentro del archivo. Para proyectos y semilleros valida además los estados permitidos y los códigos duplicados. Las validaciones propias de cada catálogo las define su módulo propietario conforme a `RN-IMP-10`.
- **RN-IMP-04:** Para proyectos y semilleros, el `codigo` se normaliza recortando espacios y convirtiendo a mayúsculas, tanto para comparar como para almacenar. Un código existente actualiza el registro correspondiente; un código nuevo crea un registro en `investigacion`, cuya clave primaria genera la base de datos. Reimportar el mismo archivo no crea duplicados, y dos filas cuyo código normalizado coincida se rechazan como duplicadas conforme a `RN-IMP-03`. Para equipos, la clave de identificación e idempotencia es la placa, conforme a `RN-IMP-02` de [Resources](../resources/business-rules.md#importación-masiva-de-inventario--rn-imp).
- **RN-IMP-05:** La importación no crea ni modifica vinculaciones de usuarios y no permite al Administrador reemplazar las reglas de Researchs sobre dichas vinculaciones.
- **RN-IMP-06:** Una carga que contenga al menos una fila con error **no se confirma en ninguna de sus filas**. El Administrador revisa el resultado de validación, corrige el archivo y vuelve a cargarlo. No existe confirmación parcial: una importación deja todas sus filas escritas o ninguna. El resultado por fila se conserva igualmente conforme a `RN-IMP-08`, para que el Administrador sepa qué corregir.
- **RN-IMP-07:** Desactivar un proyecto o semillero conserva su registro, sus vinculaciones y las referencias históricas de reservas. La importación de equipos no desactiva ni deshabilita: solo crea y actualiza, conforme a `RN-IMP-09`.
- **RN-IMP-08:** Cada carga procesada conserva el resultado de cada fila: número, identificador de la fila cuando pueda determinarse, resultado y detalle de error cuando corresponda. Cuando la importación se confirma, registra además Administrador, fecha, catálogo, archivo o referencia de carga y sus totales.
- **RN-IMP-09:** La importación es incremental: un registro existente que no aparezca en el archivo permanece sin cambios, en cualquier catálogo. Desactivar un proyecto o semillero requiere incluirlo expresamente con estado `INACTIVO`; la ausencia de una fila nunca desactiva registros. La planilla de equipos no tiene columna de estado, por lo que una carga de `EQUIPOS` nunca deshabilita un equipo: deshabilitarlo sigue siendo una acción individual sujeta a la advertencia y confirmación de `RN-DES-06` de Resources. El contador de registros desactivados de una carga de equipos es siempre cero.
- **RN-IMP-10:** Administration valida el archivo, orquesta la carga, presenta el resumen y conserva la trazabilidad; no define las reglas propias de cada catálogo. La identificación del registro, sus validaciones específicas y el efecto de la escritura corresponden al módulo propietario: `RN-INV` de [Researchs](../researchs/business-rules.md) para proyectos y semilleros, y `RN-IMP` de [Resources](../resources/business-rules.md#importación-masiva-de-inventario--rn-imp) para equipos. La importación no escribe esas entidades eludiendo sus reglas, conforme a `RN-INT-04`.
- **RN-IMP-11:** Para el catálogo `EQUIPOS`, la planilla tiene seis columnas: `PLACA`, `DESCRIPCIÓN`, `CODIGO BODEGA`, `CENTRO DE COSTOS`, `FECHA INICIO` y `COSTO`. `PLACA` y `DESCRIPCIÓN` son obligatorias; las cuatro restantes admiten valor vacío. `COSTO` se lee y se descarta: es un dato contable del inventario institucional y no se conserva en este sistema. La correspondencia con las columnas persistidas la define `RN-IMP-06` de [Resources](../resources/business-rules.md#importación-masiva-de-inventario--rn-imp).
- **RN-IMP-12:** La planilla de equipos no incluye la unidad organizacional. El Administrador la selecciona al iniciar la carga y todos los equipos de esa ejecución quedan asignados a ella. Importar equipos de varias unidades requiere una carga por unidad. La unidad seleccionada se aplica únicamente a los equipos que la carga crea; un equipo existente conserva la unidad que ya tenía, porque cambiarla exige `recursos.reasignar_unidad` conforme a `RN-EQP-09` de Resources.

---

## Separación de responsabilidades

- El módulo de administración gestiona usuarios, cuentas, perfiles, unidades organizacionales, permisos e importaciones masivas autorizadas, tanto de los catálogos de investigación como del inventario de equipos.

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
