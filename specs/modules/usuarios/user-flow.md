# User Flows — Usuarios

Este documento define los flujos de usuario del módulo `usuarios`.

El módulo `usuarios` orquesta la gestión del perfil funcional del reservista. Cuando el flujo requiere información académica o investigativa, consume las entidades y reglas del módulo `investigacion` sin duplicar su lógica de negocio.

---

## UF-USR-01 — Completar perfil después del autorregistro

**Actor principal:** Usuario

**Precondiciones:**
- La cuenta fue creada mediante autorregistro.
- La cuenta está activa y autenticada.
- El usuario aún no ha completado la información mínima de perfil.

**Flujo principal:**

1. El usuario inicia sesión.
2. El sistema detecta que el perfil funcional está incompleto.
3. El sistema dirige al usuario a completar su perfil.
4. El usuario diligencia los datos personales obligatorios.
5. El usuario selecciona su perfil o perfiles académicos/investigativos cuando corresponda.
6. El sistema consulta al módulo `investigacion` las opciones y relaciones disponibles.
7. El usuario registra o selecciona, según corresponda:
   - proyectos;
   - semilleros;
   - pasantías;
   - trabajos de grado.
8. El módulo `investigacion` valida y almacena las vinculaciones académicas o investigativas.
9. El usuario selecciona las unidades o laboratorios en los que espera realizar reservas, cuando esta información forme parte del perfil funcional.
10. El sistema valida que los datos obligatorios estén completos.
11. El sistema marca el perfil como completo.
12. El usuario puede continuar hacia las funcionalidades que exigen perfil completo.

**Flujos alternos:**

- Si faltan datos obligatorios, el sistema informa cuáles deben completarse y no marca el perfil como completo.
- Si una vinculación académica o investigativa no es válida, el módulo `investigacion` rechaza su registro o selección.
- Si el usuario abandona el proceso antes de finalizar, el perfil permanece incompleto.

---

## UF-USR-02 — Completar perfil después de una invitación

**Actor principal:** Usuario invitado

**Precondiciones:**
- Existe una invitación válida asociada a una cuenta.
- El usuario completó el proceso de activación de la cuenta.
- El perfil funcional aún está incompleto.

**Flujo principal:**

1. El usuario completa la activación de su cuenta.
2. El sistema autentica al usuario.
3. El sistema identifica que el perfil funcional está incompleto.
4. El sistema solicita completar los datos personales obligatorios.
5. El usuario diligencia la información requerida.
6. El usuario registra o selecciona sus perfiles y vinculaciones académicas o investigativas cuando corresponda.
7. El módulo `investigacion` valida y almacena dichas vinculaciones.
8. El usuario completa las demás asociaciones funcionales requeridas por el perfil.
9. El sistema valida la integridad de la información.
10. El perfil queda completo.

**Flujos alternos:**

- Si la invitación ya no es válida, el flujo de activación se resuelve en el dominio `auth`.
- Si el usuario no completa el perfil, puede autenticarse, pero no puede ejecutar operaciones que exijan perfil completo.

---

## UF-USR-03 — Consultar perfil propio

**Actor principal:** Usuario

**Precondiciones:**
- El usuario está autenticado.

**Flujo principal:**

1. El usuario accede a su perfil.
2. El sistema obtiene la información funcional del módulo `usuarios`.
3. El sistema consulta al módulo `investigacion` las vinculaciones académicas e investigativas que deban mostrarse.
4. El sistema presenta la información consolidada del perfil.
5. El usuario puede revisar sus datos y acceder a las opciones de actualización permitidas.

---

## UF-USR-04 — Actualizar datos personales

**Actor principal:** Usuario

**Precondiciones:**
- El usuario está autenticado.
- Existe un perfil funcional asociado a su cuenta.

**Flujo principal:**

1. El usuario accede a la edición de su perfil.
2. El sistema muestra los datos personales editables.
3. El usuario modifica uno o más datos.
4. El sistema valida formato y obligatoriedad.
5. El sistema guarda los cambios.
6. El sistema recalcula si el perfil continúa cumpliendo los requisitos mínimos.
7. El sistema confirma la actualización.

**Flujos alternos:**

- Si un dato obligatorio queda vacío o inválido, el sistema rechaza la actualización.
- Si el cambio afecta la condición de perfil completo, el sistema actualiza su estado funcional.

---

## UF-USR-05 — Actualizar perfiles académicos o investigativos

**Actor principal:** Usuario

**Precondiciones:**
- El usuario está autenticado.
- El usuario tiene un perfil funcional existente.

**Flujo principal:**

1. El usuario accede a la sección académica o investigativa de su perfil.
2. El sistema consulta al módulo `investigacion` los perfiles disponibles.
3. El usuario selecciona uno o más perfiles que correspondan a su situación.
4. El módulo `investigacion` valida las opciones seleccionadas.
5. El sistema actualiza las vinculaciones correspondientes.
6. El perfil consolidado del usuario refleja los cambios.

**Flujos alternos:**

- Si una combinación no está permitida por las reglas de `investigacion`, el sistema rechaza el cambio.
- Si una vinculación deja de estar vigente, se conserva su historial cuando corresponda.

---

## UF-USR-06 — Asociar un proyecto

**Actor principal:** Usuario

**Precondiciones:**
- El usuario está autenticado.
- El proyecto existe en el módulo `investigacion`.

**Flujo principal:**

1. El usuario accede a la sección de proyectos de su perfil.
2. El sistema consulta los proyectos disponibles o vinculables.
3. El usuario selecciona el proyecto correspondiente.
4. El módulo `investigacion` valida la vinculación.
5. El sistema registra la relación entre usuario y proyecto.
6. El proyecto queda disponible como contexto en procesos que lo permitan, como reservas.

**Flujos alternos:**

- Si el proyecto no puede vincularse al usuario, el sistema no crea la relación.
- Si la relación ya existe, el sistema no crea un duplicado.

---

## UF-USR-07 — Asociar un semillero

**Actor principal:** Usuario

**Precondiciones:**
- El usuario está autenticado.
- El semillero existe en el módulo `investigacion`.

**Flujo principal:**

1. El usuario accede a la sección de semilleros.
2. El sistema consulta los semilleros disponibles o vinculables.
3. El usuario selecciona el semillero correspondiente.
4. El módulo `investigacion` valida la vinculación.
5. El sistema registra la relación entre usuario y semillero.
6. El semillero queda disponible como contexto en procesos que lo permitan.

**Flujos alternos:**

- Si la relación no es válida, el sistema la rechaza.
- Si ya existe, no se crea una relación duplicada.

---

## UF-USR-08 — Registrar una pasantía

**Actor principal:** Usuario

**Precondiciones:**
- El usuario está autenticado.
- El módulo `investigacion` permite registrar la pasantía para el usuario.

**Flujo principal:**

1. El usuario accede a la sección de pasantías.
2. El sistema solicita:
   - universidad de procedencia;
   - nombre del docente responsable en el ITM;
   - correo del docente responsable en el ITM.
3. El usuario diligencia la información.
4. El sistema valida los campos obligatorios.
5. El módulo `investigacion` registra la pasantía.
6. El módulo `investigacion` vincula la pasantía con el usuario.
7. La pasantía queda disponible como contexto en procesos que la admitan.

**Flujos alternos:**

- Si falta información obligatoria, el registro no se completa.
- Si el correo no cumple el formato requerido, el sistema solicita corrección.

---

## UF-USR-09 — Registrar un trabajo de grado

**Actor principal:** Usuario

**Precondiciones:**
- El usuario está autenticado.
- El módulo `investigacion` permite registrar el trabajo de grado para el usuario.

**Flujo principal:**

1. El usuario accede a la sección de trabajo de grado.
2. El sistema solicita:
   - nombre del director;
   - correo del director.
3. El usuario diligencia la información.
4. El sistema valida los campos obligatorios.
5. El módulo `investigacion` registra el trabajo de grado.
6. El módulo `investigacion` vincula el trabajo de grado con el usuario.
7. El trabajo de grado queda disponible como contexto en procesos que lo admitan.

**Flujos alternos:**

- Si falta información obligatoria, el registro no se completa.
- Si el correo no cumple el formato requerido, el sistema solicita corrección.

---

## UF-USR-10 — Desactivar una vinculación académica o investigativa

**Actor principal:** Usuario o personal autorizado, según las reglas del módulo `investigacion`

**Precondiciones:**
- Existe una vinculación vigente entre el usuario y una entidad de investigación.

**Flujo principal:**

1. El actor accede a la vinculación.
2. El sistema verifica si la operación está permitida.
3. El actor solicita desactivar la vinculación.
4. El módulo `investigacion` conserva el historial de la relación.
5. La vinculación deja de estar disponible para nuevas operaciones que requieran una relación activa.
6. Las reservas históricas que la utilizaron mantienen su referencia e interpretación.

**Flujos alternos:**

- Si la operación no está autorizada, el sistema no modifica la vinculación.
- Si la relación ya está inactiva, no se crea una nueva desactivación.

---

## UF-USR-11 — Seleccionar unidades o laboratorios de interés

**Actor principal:** Usuario

**Precondiciones:**
- El usuario está autenticado.
- Las unidades o laboratorios disponibles existen y están habilitados para el uso correspondiente.

**Flujo principal:**

1. El usuario accede a la configuración de su perfil.
2. El sistema muestra las unidades o laboratorios disponibles.
3. El usuario selecciona aquellos con los que tendrá interacción.
4. El sistema valida que las selecciones sean válidas.
5. El sistema guarda las asociaciones del perfil.
6. Las selecciones quedan disponibles para facilitar procesos posteriores, sin conceder permisos administrativos.

**Flujos alternos:**

- Si una unidad o laboratorio deja de estar disponible, no puede seleccionarse para nuevas asociaciones.
- La asociación funcional no implica autorización administrativa.

---

## UF-USR-12 — Verificar perfil antes de iniciar una reserva

**Actor principal:** Usuario

**Precondiciones:**
- El usuario está autenticado.
- El usuario intenta iniciar una reserva.

**Flujo principal:**

1. El usuario selecciona la opción para crear una reserva.
2. El sistema consulta el estado del perfil funcional.
3. Si el perfil está completo, el sistema permite continuar con el flujo del módulo `reservas`.
4. El módulo `reservas` continúa con la selección de tipo, unidad y contexto correspondiente.

**Flujo alterno — perfil incompleto:**

1. El sistema detecta que el perfil no cumple los requisitos mínimos.
2. El sistema informa que debe completar su perfil.
3. El usuario es dirigido al flujo `UF-USR-01` o a la edición correspondiente.
4. La creación de la reserva no continúa hasta que se cumpla la condición de perfil completo.

---

## Separación entre módulos

Los flujos anteriores pueden consumir información de otros módulos, pero no trasladan su responsabilidad funcional:

- `auth` administra cuenta, autenticación y sesión.
- `usuarios` administra y orquesta el perfil funcional del reservista.
- `investigacion` administra perfiles académicos/investigativos, proyectos, semilleros, pasantías, trabajos de grado y sus vinculaciones.
- `reservas` utiliza el perfil y las vinculaciones válidas para crear y gestionar reservas.

Cuando un flujo del perfil requiere crear o modificar una entidad de investigación, `usuarios` actúa como orquestador de la experiencia y `investigacion` conserva la responsabilidad sobre la validación y persistencia de dicha entidad.
