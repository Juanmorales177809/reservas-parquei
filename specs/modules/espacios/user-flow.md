# User Flows — Espacios

Este documento define los flujos de usuario del módulo `espacios`.

Roles funcionales usados en este documento:

- **Técnico:** administra espacios únicamente dentro de su propia unidad organizacional.
- **Usuario:** consulta y utiliza espacios disponibles dentro de los procesos permitidos.
- **Administrador:** puede intervenir sobre cualquier unidad organizacional.

El módulo `espacios` administra la configuración propia de los espacios: información general, capacidad, recursos asociados y campos adicionales. El módulo `reservas` consume esta configuración, pero no la administra.

Un espacio **no tiene horario propio**: el horario aplicable es el de atención de su unidad, definido en `reservas.laboratorios_config` y configurado desde [Resources](../resources/user-flow.md). Por eso no existe un flujo de configuración de horario en este módulo.

---

## UF-ESP-01 — Registrar un espacio

**Rol principal:** Técnico 

**Precondiciones:**
- El Técnico  está autenticado.
- Tiene autorización para administrar espacios en la unidad correspondiente.

**Flujo principal:**

1. El Técnico  accede a la administración de espacios.
2. Selecciona la opción para crear un nuevo espacio.
3. El sistema solicita la información general del espacio.
4. El Técnico  diligencia los datos obligatorios.
5. Define la capacidad, obligatoria y mayor que cero (`RN-ESP-02`).
6. Puede asociar recursos existentes.
7. Puede configurar cero o más campos adicionales.
8. El sistema valida la configuración.
9. El sistema crea el espacio.
10. El espacio queda disponible según su estado de habilitación y el horario de atención de su unidad.

**Flujos alternos:**

- Si faltan datos obligatorios, el espacio no se crea.
- Si el Técnico  no tiene autorización sobre la unidad, la operación se rechaza.
- Si no se configuran campos adicionales, el espacio se crea sin ellos.

---

## UF-ESP-02 — Actualizar información general de un espacio

**Rol principal:** Técnico 

**Precondiciones:**
- El espacio existe.
- El Técnico  tiene autorización sobre la unidad del espacio.

**Flujo principal:**

1. El Técnico  consulta el espacio.
2. Selecciona la opción de edición.
3. El sistema muestra los datos editables.
4. El Técnico  modifica la información general permitida.
5. Puede modificar la capacidad, que debe seguir siendo mayor que cero y no puede quedar vacía (`RN-ESP-02`).
6. El sistema valida los cambios.
7. El sistema guarda la actualización.
8. Las nuevas operaciones utilizan la configuración vigente.

**Flujos alternos:**

- Si los datos son inválidos, el sistema no guarda los cambios.
- La modificación no elimina ni altera información histórica de reservas.

---

## UF-ESP-03 — Asociar recursos a un espacio

**Rol principal:** Técnico 

**Precondiciones:**
- El espacio existe.
- Los recursos existen en el módulo `recursos`.
- El Técnico  tiene autorización sobre el espacio.

**Flujo principal:**

1. El Técnico  accede al detalle del espacio.
2. Selecciona la administración de recursos asociados.
3. El sistema consulta los recursos disponibles para asociación.
4. El Técnico  selecciona uno o más recursos.
5. El sistema valida que los recursos existan y puedan asociarse.
6. El sistema registra las asociaciones.
7. Los recursos quedan visibles como recursos asociados al espacio.

**Flujos alternos:**

- La asociación con el espacio no implica disponibilidad temporal.
- La disponibilidad para una reserva se valida en el módulo `reservas`.

---

## UF-ESP-04 — Retirar un recurso asociado

**Rol principal:** Técnico 

**Precondiciones:**
- Existe una asociación entre el espacio y el recurso.
- El Técnico  tiene autorización sobre el espacio.

**Flujo principal:**

1. El Técnico  accede a los recursos asociados.
2. Selecciona el recurso que desea retirar.
3. El sistema solicita confirmación.
4. El Técnico  confirma.
5. El sistema elimina o deshabilita la asociación según el modelo definido.
6. El recurso deja de mostrarse como asociado para nuevas reservas.
7. Las reservas históricas conservan sus referencias.

---

## UF-ESP-05 — Configurar un campo adicional

**Rol principal:** Técnico 

**Precondiciones:**
- El espacio existe o está en proceso de creación.
- El Técnico  tiene autorización para administrarlo.

**Flujo principal:**

1. El Técnico  accede a la configuración de campos adicionales.
2. Selecciona la opción para agregar un campo.
3. El sistema solicita:
   - nombre;
   - tipo de campo;
   - condición de obligatorio u opcional;
   - orden de presentación;
   - estado de habilitación.
4. El Técnico  diligencia la configuración.
5. Si el campo es de selección, configura sus opciones.
6. El sistema valida la definición.
7. El sistema guarda el campo asociado al espacio.
8. El campo queda disponible para futuras reservas.

**Flujos alternos:**

- Si el campo requiere opciones y no tiene ninguna válida, no puede quedar habilitado.
- Si el campo es obligatorio, el módulo `reservas` exigirá valor antes de enviar la solicitud.
- Si el campo es opcional, puede quedar sin valor en la reserva.

---

## UF-ESP-06 — Configurar opciones de un campo de selección

**Rol principal:** Técnico 

**Precondiciones:**
- Existe un campo adicional de tipo selección.
- El Técnico  tiene autorización sobre el espacio.

**Flujo principal:**

1. El Técnico  selecciona el campo.
2. Accede a la administración de opciones.
3. Agrega una o más opciones.
4. Define el orden de presentación.
5. Habilita o deshabilita cada opción según corresponda.
6. El sistema valida la configuración.
7. El sistema guarda las opciones.

**Flujos alternos:**

- Una opción deshabilitada deja de estar disponible para nuevas reservas.
- Las reservas históricas conservan la interpretación de la opción utilizada.

---

## UF-ESP-07 — Editar un campo adicional

**Rol principal:** Técnico 

**Precondiciones:**
- El campo existe.
- El Técnico  tiene autorización sobre el espacio.

**Flujo principal:**

1. El Técnico  selecciona el campo.
2. El sistema muestra su configuración actual.
3. El Técnico  modifica los atributos permitidos.
4. El sistema valida los cambios.
5. El sistema guarda la nueva configuración.
6. Las nuevas reservas utilizan la configuración actualizada.

**Flujos alternos:**

- Si el campo ya fue utilizado en reservas, la modificación no puede impedir interpretar los valores históricos.
- Si se modifican opciones, debe conservarse la información necesaria para interpretar las selecciones anteriores.

---

## UF-ESP-08 — Deshabilitar un campo adicional

**Rol principal:** Técnico 

**Precondiciones:**
- El campo existe y está habilitado.
- El Técnico  tiene autorización sobre el espacio.

**Flujo principal:**

1. El Técnico  selecciona el campo.
2. Solicita deshabilitarlo.
3. El sistema solicita confirmación.
4. El Técnico  confirma.
5. El sistema cambia el campo a estado deshabilitado.
6. El campo deja de mostrarse en nuevas reservas.
7. Los valores históricos permanecen disponibles.

---

## UF-ESP-09 — Reordenar campos adicionales

**Rol principal:** Técnico 

**Precondiciones:**
- El espacio tiene dos o más campos adicionales configurados.

**Flujo principal:**

1. El Técnico  accede a la configuración de campos.
2. Modifica el orden de presentación.
3. El sistema valida el nuevo orden.
4. El sistema guarda la configuración.
5. Las nuevas reservas presentan los campos según el nuevo orden.

**Nota:**
El cambio de orden no modifica los valores históricos de reservas anteriores.

---

## UF-ESP-10 — Habilitar un espacio

**Rol principal:** Técnico 

**Precondiciones:**
- El espacio existe.
- El espacio está deshabilitado.
- El Técnico  tiene autorización sobre la unidad.

**Flujo principal:**

1. El Técnico  consulta el espacio.
2. Selecciona la opción de habilitar.
3. El sistema valida que la configuración mínima requerida sea válida.
4. El Técnico  confirma.
5. El sistema habilita el espacio.
6. El espacio vuelve a estar disponible para nuevas reservas.

---

## UF-ESP-11 — Deshabilitar un espacio

**Rol principal:** Técnico 

**Precondiciones:**
- El espacio existe.
- El espacio está habilitado.
- El Técnico  tiene autorización sobre la unidad.

**Flujo principal:**

1. El Técnico  consulta el espacio.
2. Selecciona la opción de deshabilitar.
3. El sistema consulta a `reservas` cuántas reservas futuras se cancelarán por esta deshabilitación.
4. El sistema advierte esa cantidad y solicita confirmación explícita (`RN-ESP-HAB-05`, `RN-DES-06`).
5. El Técnico  confirma.
6. El sistema deshabilita el espacio.
7. El espacio deja de estar disponible para nuevas reservas.
8. El módulo `reservas` identifica las reservas futuras afectadas.
9. `reservas` aplica sus reglas de cancelación y notificación.
10. La información histórica permanece disponible.

**Flujos alternos:**

- Si el Técnico  no confirma, el espacio permanece habilitado y ninguna reserva se modifica.
- Si el espacio no tiene reservas futuras, el sistema solicita una confirmación simple, sin advertencia de cancelaciones (`RN-DES-07`).
- Las reservas en `EN_EJECUCION` no se cancelan automáticamente por este flujo.
- Si el Técnico  no está autorizado, la operación se rechaza.

---

## UF-ESP-12 — Consultar espacios

**Rol principal:** Usuario

**Precondiciones:**
- El usuario está autenticado.

**Flujo principal:**

1. El usuario accede al listado de espacios.
2. El sistema obtiene los espacios disponibles según el contexto de consulta.
3. El sistema muestra información general, capacidad, estado y unidad.
4. El usuario puede aplicar los filtros disponibles.
5. El usuario selecciona un espacio para consultar su detalle.

---

## UF-ESP-13 — Consultar detalle de un espacio

**Rol principal:** Usuario

**Precondiciones:**
- El espacio existe.

**Flujo principal:**

1. El usuario selecciona un espacio.
2. El sistema consulta la información general.
3. Consulta la capacidad.
4. Consulta el horario de atención heredado de su unidad.
5. Consulta los recursos asociados.
6. Consulta los campos adicionales habilitados.
7. El sistema presenta la información consolidada.

---

## UF-ESP-14 — Utilizar un espacio durante una reserva

**Rol principal:** Usuario

**Precondiciones:**
- El usuario inició una reserva de tipo espacio.
- El espacio existe y está habilitado.

**Flujo principal:**

1. El usuario selecciona un espacio.
2. El módulo `reservas` consulta la configuración del espacio.
3. El sistema obtiene:
   - capacidad;
   - horario de atención heredado de su unidad;
   - recursos asociados;
   - campos adicionales habilitados;
   - obligatoriedad y opciones de cada campo.
4. El usuario selecciona fecha y horario conforme al flujo de reservas.
5. El sistema muestra los recursos asociados y su disponibilidad para el periodo solicitado.
6. Si uno o más recursos asociados no están disponibles, el usuario puede continuar con la reserva del espacio.
7. Si existen campos adicionales, el sistema los presenta.
8. El usuario diligencia los campos obligatorios y los opcionales que correspondan.
9. El sistema valida los valores.
10. El módulo `reservas` almacena los valores ingresados junto con la reserva.
11. El flujo continúa en el módulo `reservas`.

**Flujos alternos:**

- Si un campo obligatorio no tiene valor, la reserva no puede enviarse.
- Si una opción seleccionada ya no está habilitada, el sistema solicita una opción válida.
- La falta de disponibilidad de un recurso asociado no bloquea la reserva del espacio.

---

## Separación de responsabilidades

- `espacios` administra espacios, capacidad, recursos asociados y campos adicionales. No administra horarios: el aplicable es el de atención de la unidad, que pertenece a `recursos`.
- `recursos` administra la identidad y estado general de los recursos.
- `reservas` administra disponibilidad temporal, solicitud, aprobación, asignación, ejecución y cancelación de reservas.
- `auth` determina la identidad autenticada y la autorización.
- `unidadOrganizacional` determina el ámbito institucional al que pertenece el espacio.

La asociación de un recurso con un espacio indica que puede formar parte de su configuración, pero no constituye una asignación automática ni garantiza disponibilidad para una reserva concreta.
