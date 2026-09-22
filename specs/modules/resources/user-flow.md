# User Flows — Recursos

Este documento define los flujos de usuario del módulo `recursos`.

El módulo `recursos` administra el catálogo común de elementos reservables en `recursos.recursos` y sus especializaciones `recursos.equipos`, `recursos.mobiliarios` y `recursos.otros_recursos`. La fila especializada de cada tipo comparte el mismo `id` del registro raíz como PK/FK.

En todos los flujos administrativos, el Técnico solo puede operar sobre elementos de su propia unidad organizacional. El Administrador tiene alcance global. El Técnico no crea ni elimina equipos, pero puede editar equipos existentes de su unidad y cambiar su habilitación y su estado operativo; sí puede crear y administrar mobiliario y otros recursos de su unidad.

---

## UF-REC-01 — Registrar un mobiliario

**Rol principal:** Técnico de la unidad o Administrador

**Precondiciones:**
- El actor está autenticado.
- El actor es Técnico de la unidad correspondiente o Administrador.

**Flujo principal:**

1. El actor accede a la administración de recursos.
2. Selecciona la opción para registrar un nuevo recurso.
3. Selecciona el tipo `MOBILIARIO`.
4. El sistema solicita la información general y específica del mobiliario.
5. El actor diligencia los datos obligatorios.
6. El sistema valida la información.
7. El sistema crea el registro en `recursos.recursos`.
8. El sistema crea el registro asociado en `recursos.mobiliarios` usando el mismo `id` del recurso como PK/FK, en una única transacción con el paso anterior; ante un fallo revierte ambos registros.
9. El recurso queda disponible en el catálogo de la unidad.

**Flujos alternos:**

- Si faltan datos obligatorios, el sistema no crea el recurso.
- Si el actor no tiene autorización sobre la unidad, el sistema rechaza la operación.

---

## UF-REC-02 — Registrar otro recurso

**Rol principal:** Técnico de la unidad o Administrador

**Precondiciones:**
- El actor está autenticado.
- El actor es Técnico de la unidad correspondiente o Administrador.

**Flujo principal:**

1. El actor accede a la administración de recursos.
2. Selecciona la opción para registrar un nuevo recurso.
3. Selecciona el tipo `OTRO`.
4. El sistema solicita la información general y específica requerida.
5. El actor diligencia los datos.
6. El sistema valida la información.
7. El sistema crea el registro en `recursos.recursos`.
8. El sistema crea el registro asociado en `recursos.otros_recursos` usando el mismo `id` del recurso como PK/FK, en una única transacción con el paso anterior; ante un fallo revierte ambos registros.
9. El recurso queda disponible en el catálogo de la unidad.

**Flujos alternos:**

- Si la información obligatoria es incompleta o inválida, el sistema no crea el recurso.
- Si el actor no tiene autorización sobre la unidad, el sistema rechaza la operación.

---

## UF-REC-03 — Registrar un equipo como recurso

**Rol principal:** Administrador o proceso de importación autorizado

**Precondiciones:**
- El actor es Administrador o un proceso de importación autorizado.
- Se cuenta con la información general del recurso y los datos especializados obligatorios del equipo.
- Cuando el origen es una carga masiva, la orquesta Administration conforme a `UF-ADM-04`; este flujo describe el registro de un equipo y se ejecuta una vez por cada fila confirmada.

**Flujo principal:**

1. El Administrador o el proceso de importación autorizado inicia el registro del equipo.
2. El sistema crea una fila en `recursos.recursos` con tipo `EQUIPO`, unidad responsable y estado de habilitación.
3. El sistema crea `recursos.equipos` con el mismo `id` como PK/FK y guarda los datos especializados del equipo, incluida su categoría y los datos de inventario.
4. La creación de ambas filas se realiza en una sola transacción; si una validación o escritura falla, no se conserva ninguna de las dos.
5. El equipo queda disponible para los procesos que consumen el catálogo de recursos, sujeto a su habilitación, condición operativa y reglas de reservabilidad.

**Flujos alternos:**

- El Técnico no puede ejecutar este flujo. Puede editar equipos existentes de su unidad mediante `UF-REC-12`, pero no crearlos ni eliminarlos.
- Si la placa ya existe, la importación actualiza el registro correspondiente en lugar de crear un duplicado, conforme a `RN-IMP-02` de este módulo.
- Si la fila no trae placa o su placa es inválida, el equipo no se registra y la fila se reporta en error conforme a `RN-IMP-03` de este módulo.
- Si falla la creación de cualquiera de las dos filas, la transacción se revierte completa.

---

## UF-REC-04 — Consultar recursos

**Actor principal:** Usuario autenticado, Técnico o Administrador

**Precondiciones:**
- El actor está autenticado.
- La consulta corresponde a un contexto permitido.

**Flujo principal:**

1. El actor accede al catálogo de recursos.
2. El sistema obtiene los recursos correspondientes al ámbito de consulta.
3. El sistema identifica el tipo de cada recurso.
4. Cuando se requiere información especializada:
   - consulta `recursos.equipos` para recursos tipo `EQUIPO`;
   - consulta `recursos.mobiliarios` para tipo `MOBILIARIO`;
   - consulta `recursos.otros_recursos` para tipo `OTRO`.
5. El sistema presenta la información consolidada.
6. El actor puede aplicar los filtros habilitados.

---

## UF-REC-05 — Consultar detalle de un recurso

**Actor principal:** Usuario autenticado, Técnico o Administrador

**Precondiciones:**
- El recurso existe.
- El actor puede consultar el recurso dentro de su contexto de uso.

**Flujo principal:**

1. El actor selecciona un recurso.
2. El sistema consulta la información común en `recursos.recursos`.
3. El sistema identifica el tipo del recurso.
4. El sistema obtiene la información especializada del módulo o tabla correspondiente.
5. El sistema presenta el detalle consolidado.

**Flujos alternos:**

- Si el recurso está deshabilitado, el sistema puede mostrarlo para consulta histórica, pero debe identificarlo como no disponible para nuevas operaciones.

---

## UF-REC-06 — Actualizar un mobiliario

**Rol principal:** Técnico de la unidad o Administrador

**Precondiciones:**
- El mobiliario existe.
- El actor tiene permiso para administrarlo dentro de su unidad.

**Flujo principal:**

1. El actor consulta el mobiliario.
2. Selecciona la opción de edición.
3. El sistema muestra la información editable.
4. El actor modifica los datos.
5. El sistema valida la información.
6. El sistema actualiza `recursos.mobiliarios` y, cuando corresponda, los atributos comunes de `recursos.recursos`.
7. El sistema confirma la actualización.

**Flujos alternos:**

- Si los datos son inválidos, no se guardan los cambios.
- Si el actor carece de autorización, la operación se rechaza.

---

## UF-REC-07 — Actualizar otro recurso

**Rol principal:** Técnico de la unidad o Administrador

**Precondiciones:**
- El recurso existe.
- El actor tiene permiso para administrarlo dentro de su unidad.

**Flujo principal:**

1. El actor consulta el recurso.
2. Selecciona la opción de edición.
3. El sistema muestra los datos editables.
4. El actor realiza los cambios.
5. El sistema valida la información.
6. El sistema actualiza `recursos.otros_recursos` y, cuando corresponda, `recursos.recursos`.
7. El sistema confirma la actualización.

---

## UF-REC-08 — Habilitar un recurso

**Rol principal:** Técnico de la unidad o Administrador

**Precondiciones:**
- El recurso existe y se encuentra deshabilitado.
- Para equipos, el Técnico tiene `recursos.editar_equipos` en la unidad del equipo; el Administrador tiene `recursos.administrar_equipos` con alcance global.
- Para los demás recursos, el actor tiene el permiso administrativo correspondiente en la unidad.

**Flujo principal:**

1. El actor consulta el recurso.
2. Selecciona la opción de habilitar.
3. El sistema valida que el recurso pueda volver a utilizarse.
4. El sistema cambia su estado a habilitado.
5. El recurso vuelve a estar disponible para nuevas operaciones que lo admitan.

---

## UF-REC-09 — Deshabilitar un recurso

**Rol principal:** Técnico de la unidad o Administrador

**Precondiciones:**
- El recurso existe y está habilitado.
- Para equipos, el Técnico tiene `recursos.editar_equipos` en la unidad del equipo; el Administrador tiene `recursos.administrar_equipos` con alcance global.
- Para los demás recursos, el actor tiene el permiso administrativo correspondiente en la unidad.

**Flujo principal:**

1. El actor consulta el recurso.
2. Selecciona la opción de deshabilitar.
3. El sistema consulta a `reservas` en cuántas reservas futuras el recurso participa con rol `PRINCIPAL`, es decir, cuántas se cancelarán conforme a `RN-CAN-04`.
4. Si esa cantidad es mayor que cero, el sistema la advierte y solicita confirmación explícita (`RN-DES-06`); en caso contrario solicita una confirmación simple (`RN-DES-07`).
5. El actor confirma la operación.
6. El sistema cambia el recurso a estado deshabilitado.
7. El recurso deja de estar disponible para nuevas operaciones.
8. Los registros históricos que lo referencian conservan su relación.
9. Si existen reservas futuras afectadas, el módulo `reservas` aplica sus reglas correspondientes: cancela aquellas donde el recurso era `PRINCIPAL` y lo retira de aquellas donde era `ADICIONAL` (`RN-CAN-04`, `RN-CAN-05`).

**Flujos alternos:**

- Si el actor no confirma, el recurso permanece habilitado y ninguna reserva se modifica.
- Si la operación no está autorizada, el recurso permanece sin cambios.

---

## UF-REC-10 — Cambiar la unidad responsable de un recurso

**Rol principal:** Técnico de la unidad o Administrador

**Precondiciones:**
- El recurso existe.
- El actor tiene autorización suficiente para modificar su unidad responsable.
- La nueva unidad existe.

**Flujo principal:**

1. El actor consulta el recurso.
2. Selecciona la opción para cambiar su unidad responsable.
3. El sistema muestra las unidades permitidas.
4. El actor selecciona la nueva unidad.
5. El sistema valida la operación.
6. El sistema actualiza la unidad asociada al recurso.
7. El sistema conserva trazabilidad del cambio.

**Flujos alternos:**

- Si existen condiciones que impiden el cambio, el sistema rechaza la operación y mantiene la unidad actual.

---

## UF-REC-12 — Actualizar un equipo existente

**Rol principal:** Técnico de la unidad o Administrador

**Precondiciones:**
- El equipo existe en `recursos.recursos` y tiene su especialización en `recursos.equipos`.
- El Técnico cuenta con `recursos.editar_equipos` asignado a la unidad del equipo; el Administrador cuenta con `recursos.administrar_equipos` de alcance global.

**Flujo principal:**

1. El actor consulta un equipo existente y selecciona la opción de edición.
2. El sistema presenta los datos generales y especializados editables, incluidos `recursos.recursos.habilitado` y `recursos.equipos.estado`.
3. El actor modifica los datos requeridos y, si corresponde, uno o ambos estados.
4. El sistema valida el permiso, la pertenencia del equipo a la unidad autorizada y las restricciones de los campos. No permite cambiar `id_unidad` mediante este flujo.
5. El sistema actualiza los datos comunes y especializados en una única operación coherente.
6. El sistema confirma el cambio y conserva el registro y las relaciones históricas.

**Flujos alternos:**

- Si la validación falla, no se aplica ningún cambio.
- Si el actor intenta crear o eliminar físicamente el equipo, la operación se rechaza.
- Si se cambia `habilitado` a `false`, se aplica el flujo `UF-REC-09` y sus efectos sobre reservas futuras. Cambiar el estado operativo no sustituye la validación de disponibilidad temporal de `reservas`.

---

## UF-REC-11 — Consultar disponibilidad desde otro módulo

**Actor principal:** Otro módulo del sistema

**Precondiciones:**
- El recurso existe.
- El módulo consumidor tiene permitido consultar su información.

**Flujo principal:**

1. El módulo consumidor solicita información del recurso.
2. `recursos` valida que el recurso exista y esté habilitado.
3. `recursos` retorna su identidad, tipo y unidad responsable.
4. El módulo consumidor aplica sus propias reglas de disponibilidad y uso.

**Nota:**

La disponibilidad temporal de un recurso para una reserva pertenece al módulo `reservas`. El módulo `recursos` administra la existencia, clasificación y estado general del recurso.

---

## Separación entre módulos

- `recursos` administra la identidad común de los elementos reservables, su tipo, unidad responsable y estado general.
- `recursos.equipos` conserva los atributos especializados y el estado operativo de los equipos.
- `reservas` administra la asignación, disponibilidad temporal, uso, entrega y devolución de recursos dentro de una reserva.
- `auth` determina la identidad autenticada y autorización del actor.
- `unidadOrganizacional` proporciona el ámbito organizacional al que pertenece el recurso.

Un flujo de `recursos` no debe duplicar procesos propios de `reservas`, como reservar, aprobar una reserva, entregar un recurso reservado o registrar su devolución.
