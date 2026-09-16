# Reservas

Contrato funcional del dominio de reservas.

El modelo persistente se define en [data-model](../core/data-model.md), los espacios y recursos en [spaces-and-resources](spaces-and-resources.md), la identidad y autorización en [identity](identity.md), y las relaciones académicas e investigativas en el modelo correspondiente de investigación.

---

## Catálogos — RN-TIP

- **RN-TIP-01:** `tipo_reserva_id` es obligatorio y debe referir un tipo de reserva habilitado al crear una reserva.

- **RN-TIP-02:** Los tipos de reserva y motivos de solicitud tienen `nombre`, `descripcion` y `habilitado`. Deshabilitar un registro conserva su historial y no elimina las referencias existentes.

- **RN-TIP-03:** `motivo_solicitud_id` es opcional salvo que una política específica exija su diligenciamiento. Los tipos o motivos utilizados por reservas existentes no se eliminan físicamente.

---

## Creación y composición — RN-RES

- **RN-RES-01:** Toda reserva debe ser creada por una cuenta autenticada y activa. La reserva identifica la cuenta reservista mediante `id_cuenta` y la unidad organizacional receptora mediante `id_unidad`.

- **RN-RES-02:** Una reserva puede contener solo espacio, solo equipo, solo mobiliario, solo otro recurso, varios recursos o una combinación de espacio y recursos.

- **RN-RES-03:** No puede crearse ni aprobarse una reserva sin al menos un espacio o recurso asociado.

- **RN-RES-04:** `espacio_id` es opcional. Todo espacio o recurso asociado a la reserva debe pertenecer a la unidad indicada por `id_unidad`.

- **RN-RES-05:** `asistentes >= 0`. Cuando exista un espacio reservado, el número de asistentes no puede superar la capacidad habilitada del espacio.

- **RN-RES-06:** `tipo_uso` admite únicamente `ESPACIO_RESERVADO`, `DENTRO_CAMPUS` y `FUERA_CAMPUS`.

- **RN-RES-07:** `ESPACIO_RESERVADO` exige `espacio_id`. `DENTRO_CAMPUS` permite omitir el espacio, pero en ese caso exige `ubicacion_uso` no vacía. `FUERA_CAMPUS` exige `espacio_id IS NULL` y `ubicacion_uso` no vacía.

- **RN-RES-08:** Una misma cuenta puede mantener reservas simultáneas siempre que no exista conflicto sobre los espacios o recursos asociados.

- **RN-RES-09:** Crear o modificar una reserva revalida composición, habilitación, pertenencia a la unidad, capacidad, estado operativo y disponibilidad de todos los elementos asociados.

---

## Horario — RN-HOR

- **RN-HOR-01:** `hora_inicio` debe ser menor que `hora_fin`.

- **RN-HOR-02:** Una reserva no puede cruzar medianoche.

- **RN-HOR-03:** La reserva debe encontrarse dentro del horario habilitado para la unidad o laboratorio correspondiente.

- **RN-HOR-04:** No se aceptan fechas pasadas.

- **RN-HOR-05:** `horas_antelacion` se valida al crear una reserva y al reprogramarla. No se vuelve a exigir al momento de aprobarla.

- **RN-HOR-06:** La validación de horario debe utilizar la configuración vigente de la unidad al momento de crear, modificar o aprobar la reserva.

---

## Estados — RN-EST

Los únicos estados válidos son:

- `PENDIENTE`
- `APROBADA`
- `RECHAZADA`
- `CANCELADA`

No existe el estado `FINALIZADA`.

- **RN-EST-01:** Una reserva se crea en `PENDIENTE`, salvo que la política de aprobación automática o una acción administrativa autorizada permita crearla directamente como `APROBADA`.

- **RN-EST-02:** Las reservas `PENDIENTE` y `APROBADA` bloquean disponibilidad de los espacios y recursos asociados.

- **RN-EST-03:** Las reservas `RECHAZADA` y `CANCELADA` no bloquean disponibilidad.

- **RN-EST-04:** Una reserva `RECHAZADA` o `CANCELADA` conserva su información histórica y no se elimina físicamente por causa del cambio de estado.

---

## Disponibilidad — RN-DIS

- **RN-DIS-01:** Los intervalos de reserva se interpretan como `[hora_inicio, hora_fin)`. Dos reservas contiguas no se consideran solapadas cuando una termina exactamente a la hora en que inicia la otra.

- **RN-DIS-02:** La disponibilidad se valida de forma independiente para el espacio y para cada recurso individual asociado.

- **RN-DIS-03:** Un equipo debe encontrarse operativo según la información vigente del sistema de origen correspondiente al momento de crear o aprobar la reserva.

- **RN-DIS-04:** Crear, modificar horario, agregar o cambiar elementos y aprobar una reserva deben utilizar la garantía transaccional definida en [data-model](../core/data-model.md#4-garantia-transaccional). Consultar disponibilidad antes de guardar no constituye por sí solo una garantía suficiente.

- **RN-DIS-05:** La validación de disponibilidad debe considerar como bloqueantes únicamente las reservas en estado `PENDIENTE` o `APROBADA`.

---

## Propiedad y acceso — RN-PRO

- **RN-PRO-01:** La cuenta reservista puede consultar sus propias reservas independientemente de su estado.

- **RN-PRO-02:** La cuenta reservista puede editar sus propias reservas únicamente cuando el estado de la reserva y las reglas de negocio permitan la modificación.

- **RN-PRO-03:** Una cuenta sin permisos administrativos no puede consultar, modificar, aprobar, rechazar ni cancelar reservas pertenecientes a terceros.

- **RN-PRO-04:** El personal autorizado puede consultar y gestionar reservas de terceros únicamente dentro de las unidades organizacionales incluidas en su ámbito de autorización.

- **RN-PRO-05:** La determinación de si una cuenta corresponde a personal autorizado, así como sus permisos y ámbito organizacional, se rige por [identity](identity.md).

---

## Aprobación — RN-APR

- **RN-APR-01:** Solo una cuenta autorizada conforme a [identity](identity.md) puede aprobar o rechazar reservas de terceros.

- **RN-APR-02:** La aprobación automática nunca omite las validaciones de disponibilidad, horario, capacidad, estado operativo, habilitación o pertenencia a la unidad.

- **RN-APR-03:** El personal con permiso para gestionar reservas puede crear una reserva directamente en estado `APROBADA` cuando actúe dentro de su ámbito autorizado y la política de la unidad lo permita. Fuera de dicho ámbito se aplica la política de la unidad receptora.

- **RN-APR-04:** Aprobar una reserva revalida disponibilidad, horario, capacidad, habilitación, pertenencia y estado operativo. La aprobación no exige nuevamente la anticipación mínima.

- **RN-APR-05:** Rechazar una reserva conserva toda su información histórica y registra el motivo cuando la política aplicable lo requiera.

---

## Cancelación — RN-CAN

- **RN-CAN-01:** Cancelar una reserva conserva el registro y libera inmediatamente los espacios y recursos asociados para efectos de disponibilidad.

- **RN-CAN-02:** La cancelación se permite hasta la fecha y hora de inicio inclusive. Después del inicio no se permite cancelar la reserva.

- **RN-CAN-03:** Toda cancelación registra el actor y el momento de la acción.

- **RN-CAN-04:** Deshabilitar un espacio o recurso no elimina reservas futuras existentes. El sistema debe conservarlas y generar la notificación o tratamiento definido para las personas afectadas.

---

## Contexto académico e investigativo — RN-CTX

- **RN-CTX-01:** Una reserva puede asociarse al contexto académico o investigativo bajo el cual se realiza.

- **RN-CTX-02:** Cuando se asocie un perfil, semillero o proyecto, la cuenta reservista debe estar relacionada válidamente con dicho elemento al momento de crear la reserva.

- **RN-CTX-03:** La asociación con semillero o proyecto es opcional cuando la modalidad de vinculación permita realizar reservas sin pertenecer a ellos, por ejemplo pasantía internacional, apropiación social del conocimiento, movilidad, visitante, convenio u otra modalidad habilitada.

- **RN-CTX-04:** El contexto asociado a una reserva debe conservarse históricamente aunque posteriormente cambien los perfiles, proyectos, semilleros o modalidades de vinculación del usuario.

- **RN-CTX-05:** Una reserva no requiere simultáneamente perfil, semillero, proyecto y modalidad. Solo se registran los elementos que correspondan al contexto real de la reserva.

- **RN-CTX-06:** El contexto académico o investigativo de una reserva no otorga por sí mismo permisos administrativos sobre reservas.

---

## Auditoría — RN-AUD

- **RN-AUD-01:** Crear, modificar, aprobar, rechazar y cancelar una reserva genera un registro de auditoría.

- **RN-AUD-02:** El registro de auditoría incluye como mínimo actor, acción, entidad, identificador de la entidad y fecha/hora.

- **RN-AUD-03:** Toda acción auditada debe identificar la cuenta autenticada que la ejecutó y conservar una representación histórica suficiente del actor, independientemente de que la cuenta corresponda a un usuario o a personal.

- **RN-AUD-04:** La trazabilidad histórica no debe depender de que el usuario, personal, cargo, proyecto, semillero o modalidad permanezcan activos posteriormente.

---

## Dependencias funcionales

Las reglas de este documento dependen de otros dominios únicamente en los siguientes aspectos:

- **Identidad y autorización:** [identity](identity.md) determina autenticación, tipo de cuenta, permisos administrativos y ámbito organizacional.
- **Espacios y recursos:** [spaces-and-resources](spaces-and-resources.md) determina existencia, habilitación, capacidad, pertenencia y estado operativo de espacios y recursos.
- **Modelo persistente:** [data-model](../core/data-model.md) define claves, relaciones, constraints y garantías transaccionales.
- **Investigación:** perfiles, semilleros, proyectos y modalidades de vinculación son datos de contexto y no sustituyen las reglas de autorización.

---

## Principios del dominio

1. Una reserva siempre tiene una cuenta reservista y una unidad receptora.
2. Toda reserva debe tener al menos un espacio o recurso.
3. La disponibilidad se protege tanto por reglas de negocio como por garantía transaccional.
4. El acceso a reservas de terceros depende de autorización, no del tipo de usuario por sí solo.
5. Las relaciones académicas e investigativas contextualizan la reserva, pero no conceden permisos administrativos.
6. Las acciones relevantes conservan trazabilidad histórica.
