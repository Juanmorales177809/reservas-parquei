# User Flows — Administration

Este documento describe los flujos administrativos del módulo `administration`. La importación masiva se orquesta aquí, pero escribe siempre en el módulo propietario: `investigacion` para proyectos y semilleros, `recursos` para equipos. Researchs y Resources conservan la propiedad de sus entidades, de sus validaciones y de las vinculaciones.

## UF-ADM-01 — Importar proyectos o semilleros mediante Excel

**Actor principal:** Administrador

**Precondiciones:**

- La cuenta está autenticada, activa y tiene alcance global.
- El archivo corresponde a un catálogo de proyectos o de semilleros.

**Flujo principal:**

1. El Administrador selecciona «Importar catálogo de investigación».
2. Selecciona el tipo de catálogo: `proyectos` o `semilleros`.
3. Carga un archivo Excel con las columnas `codigo`, `nombre` y `estado`.
4. El sistema valida el formato, las columnas, los campos obligatorios, los estados permitidos y los códigos duplicados dentro del archivo.
5. El sistema compara los códigos con el catálogo correspondiente de `investigacion` y muestra un resumen de registros nuevos, actualizados y desactivados, junto con los errores encontrados.
6. El Administrador revisa el resultado y confirma la importación. Si hay al menos una fila en error, el sistema no permite confirmar (`RN-IMP-06`).
7. El sistema crea los códigos nuevos y actualiza los códigos existentes en la tabla de `investigacion` correspondiente.
8. El sistema conserva las identidades, vinculaciones y referencias históricas; no crea ni modifica vinculaciones de usuarios.
9. El sistema registra el resultado de validación por cada fila procesada. Al confirmar, registra además la operación, el Administrador, la fecha, el catálogo, la referencia del archivo y sus totales.

**Flujos alternos:**

- Si el archivo no cumple el formato o contiene errores, el sistema rechaza la confirmación y muestra los errores sin guardar cambios parciales.
- Si un código ya existe, se actualiza ese registro; no se crea un duplicado.
- Si el archivo contiene nombres parecidos con códigos diferentes, el sistema puede advertir la coincidencia, pero no fusiona registros automáticamente.
- Si la cuenta no tiene alcance global, el sistema rechaza la operación.

## UF-ADM-02 — Registrar o actualizar la identidad de un Usuario

**Rol:** Administrador con permiso global de gestión de usuarios.

1. El Administrador abre el alta o la edición de un Usuario.
2. El sistema solicita los datos obligatorios de RN-DAT de Usuarios y el correo de la identidad.
3. Usuarios valida obligatoriedad y unicidad conforme a sus reglas; al editar, excluye el propio registro de la comprobación de duplicados.
4. El sistema guarda la identidad y registra la acción administrativa. Si hay datos faltantes, inválidos o duplicados, rechaza la operación sin guardar cambios parciales.
5. Para un alta nueva, el Administrador puede continuar con UF-AUTH-02 para invitar la cuenta usando el correo de esa identidad. El Usuario revisará sus datos y completará las vinculaciones en su primer ingreso; el alta administrativa no marca la actualización inicial como completada.

## UF-ADM-03 — Registrar la identidad de Personal e invitar su cuenta

**Actor principal:** Administrador con permiso global `usuarios.administrar` y autorización global para invitar cuentas conforme a Auth.

**Precondiciones:**

- El cargo existe y pertenece a la unidad que se asignará a la persona.
- La ficha de Personal no está ya registrada, o el Administrador puede localizar y verificar la ficha existente.

**Flujo principal:**

1. El Administrador abre la gestión de identidades de Personal.
2. Para una ficha nueva, registra nombre, documento, correo, teléfono y cargo. Si la ficha ya existe, la localiza por su correo y verifica los datos; no crea un duplicado.
3. El dominio de Usuarios valida los campos obligatorios, la unicidad de documento, correo y teléfono, la existencia del cargo y su unidad organizacional, y guarda o actualiza la ficha en `personal.personal` (`RN-PRS-05`). La ficha queda activa para recibir la invitación.
4. El Administrador elige invitar la cuenta y proporciona el correo de la ficha y la unidad derivada del cargo.
5. Auth resuelve la ficha por correo único, confirma que el correo y la unidad coincidan, almacena `id_persona` en la invitación y envía el enlace conforme a `UF-AUTH-02`.
6. La persona invitada define su contraseña al activar la cuenta. La ficha de Personal ya existente no se vuelve a crear ni se reemplaza.
7. La asignación de permisos administrativos, si corresponde, se realiza por separado en Administration; la invitación no concede permisos.

**Flujos alternos:**

- Si faltan datos, hay valores duplicados o el cargo no es válido para la unidad, la ficha no se guarda y no se emite la invitación.
- Si no existe una ficha activa que coincida con el correo, o la unidad no coincide con la unidad del cargo o el ámbito del emisor, Auth rechaza la invitación.
- Si la ficha está inactiva, debe reactivarse mediante la gestión administrativa correspondiente antes de invitar.

## UF-ADM-04 — Importar equipos institucionales

**Actor principal:** Administrador

**Precondiciones:**

- La cuenta está autenticada, activa y tiene alcance global (`RN-IMP-01`).
- El archivo corresponde al catálogo de equipos.

**Flujo principal:**

1. El Administrador selecciona «Importar catálogo» y elige el catálogo `EQUIPOS`.
2. **Selecciona la unidad organizacional** a la que pertenecerán los equipos que la carga cree. La planilla no la contiene (`RN-IMP-12`).
3. Carga la planilla de equipos, con las seis columnas de `RN-IMP-11`.
4. El sistema valida el formato del archivo, sus columnas y las placas duplicadas dentro de la planilla (`RN-IMP-03`).
5. Por cada fila, Resources valida la placa y la descripción conforme a `RN-IMP-02`, `RN-IMP-03` y `RN-IMP-06` de ese módulo.
6. El sistema compara las placas con el inventario existente y muestra un resumen de equipos nuevos y actualizados, junto con las filas en error.
7. El Administrador revisa el resultado y confirma la importación. **Si hay al menos una fila en error, el sistema no permite confirmar** (`RN-IMP-06`).
8. Al confirmar, Resources crea o actualiza cada equipo conforme a `UF-REC-03`, escribiendo `recursos.recursos` y `recursos.equipos` en una sola transacción por equipo (`RN-IMP-05` de Resources). Los equipos nuevos quedan en la unidad seleccionada en el paso 2; los existentes conservan la suya.
9. La importación no modifica las reservas históricas asociadas a un equipo actualizado (`RN-IMP-04` de Resources) ni deshabilita ningún equipo (`RN-IMP-07` de Resources).
10. El sistema registra el resultado de cada fila procesada. Al confirmar, registra además la operación, el Administrador, la fecha, el catálogo `EQUIPOS`, la referencia del archivo y sus totales (`RN-IMP-08`).

**Flujos alternos:**

- Si el archivo no cumple el formato, el sistema rechaza la confirmación y muestra los errores sin escribir equipos.
- Si una placa ya existe, se actualiza ese equipo; no se crea un duplicado (`RN-IMP-02` de Resources).
- Si una fila no trae placa o su placa es inválida, se reporta como fila en error y la carga completa queda sin confirmar (`RN-IMP-03` de Resources).
- Si los equipos pertenecen a varias unidades, se realiza una carga por unidad.
- Si la cuenta no tiene alcance global, el sistema rechaza la operación.

**Trazabilidad.** La unidad seleccionada en el paso 2 no se conserva en el registro de la importación, que guarda actor, catálogo, archivo y totales. La unidad de cada equipo sí queda en `recursos.recursos.id_unidad`.

---

## Separación de responsabilidades

- Administration autoriza, valida el archivo, orquesta la carga y conserva su trazabilidad, conforme a `RN-IMP-10`.
- Researchs conserva las entidades `proyectos` y `semilleros`, sus identificadores y sus vinculaciones.
- Resources conserva las entidades `recursos` y `equipos`, la identificación por placa y las validaciones del equipo.
- La importación no asigna usuarios a proyectos o semilleros, ni crea reservas o asignaciones de equipos.
- Los Usuarios seleccionan registros existentes; no crean proyectos ni semilleros desde su perfil o una reserva.
