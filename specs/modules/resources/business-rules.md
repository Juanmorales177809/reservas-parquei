# Laboratorios, espacios y recursos

Contrato funcional del dominio de laboratorios, espacios y recursos.

La estructura persistente se define en [data-model](../core/data-model.md), las reglas de reservas y disponibilidad en [bookings](bookings.md) y las reglas de identidad y autorización en [identity](identity.md).

---

## Laboratorios — RN-LAB

- **RN-LAB-01:** `reservas.laboratorios_config` representa la configuración de Reservas asociada a una unidad organizacional. `id_unidad` es obligatorio, único y referencia `unidadOrganizacional.unidad_organizacional`.

- **RN-LAB-02:** El nombre y la identidad institucional de la unidad se obtienen de `unidadOrganizacional.unidad_organizacional`; no se duplican ni se administran desde `laboratorios_config`.

- **RN-LAB-03:** `habilitado_reservas` determina si la unidad acepta nuevas reservas. Deshabilitar las reservas no elimina ni modifica el historial existente.

- **RN-LAB-04:** Horario de atención, días habilitados, anticipación mínima, modalidad de reserva y aprobación automática son configuraciones propias del dominio de Reservas.

- **RN-LAB-05:** La configuración vigente de la unidad se utiliza para validar las operaciones de reserva conforme a [bookings](bookings.md).

- **RN-LAB-06:** Una unidad organizacional puede existir sin tener habilitado el servicio de Reservas. La existencia de la unidad no implica que pueda recibir reservas.

- **RN-LAB-07:** `notificar_por_correo` determina si la unidad tiene habilitado el envío de correo saliente para las notificaciones asociadas a sus reservas y recursos. Esta configuración es propia de la unidad, se aplica a todas las personas relacionadas con ella y es independiente de la preferencia de correo que cada persona pueda configurar individualmente (ver [notifications](../business-rules%20(1).md)). Deshabilitarla no afecta la generación de notificaciones in-app.

---

## Espacios — RN-ESP

- **RN-ESP-01:** Cada espacio pertenece a una única unidad organizacional mediante `id_unidad`.

- **RN-ESP-02:** Solo los espacios con `habilitado = true` pueden incorporarse a nuevas reservas o agregarse durante una modificación.

- **RN-ESP-03:** `capacidad` debe ser mayor que cero. Cuando una reserva utilice un espacio, el número de asistentes no puede superar su capacidad.

- **RN-ESP-04:** El nombre del espacio es único dentro de cada unidad mediante `UNIQUE (id_unidad, nombre)`.

- **RN-ESP-05:** Deshabilitar un espacio conserva el registro, sus relaciones y el historial de reservas.

- **RN-ESP-06:** Cuando un espacio sea deshabilitado y existan reservas futuras `PENDIENTE` o `APROBADA` que lo utilicen, dichas reservas deben cancelarse automáticamente y notificarse a los usuarios afectados, conforme a las reglas de cancelación definidas en [bookings].

- **RN-ESP-07:** La exclusividad temporal del espacio se rige por las reglas de disponibilidad definidas en [bookings](bookings.md).

- **RN-ESP-08:** Una reserva puede no contener espacio cuando su composición y `tipo_uso` lo permitan conforme a [bookings](bookings.md).

---

## Recursos — RN-REC

Para efectos de Reservas, se consideran recursos reservables los equipos, mobiliarios y otros elementos individualizables. Los espacios se gestionan como una categoría independiente.

- **RN-REC-01:** Todo recurso reservable representa un elemento individual identificable mediante su clave primaria.

- **RN-REC-02:** Todo recurso pertenece a una unidad organizacional.

- **RN-REC-03:** Al crear, modificar o aprobar una reserva, cada recurso asociado debe pertenecer a la misma unidad indicada por `reservas.reservas.id_unidad`.

- **RN-REC-04:** Un mismo recurso no puede aparecer más de una vez dentro de una misma reserva.

- **RN-REC-05:** La disponibilidad temporal se evalúa individualmente para cada recurso conforme a [bookings](bookings.md).

- **RN-REC-06:** El nombre de un recurso no constituye su identidad y puede repetirse. La identificación se realiza mediante su clave primaria.

- **RN-REC-07:** Solo recursos habilitados y, cuando corresponda, operativos pueden incorporarse a nuevas reservas.

- **RN-REC-08:** Deshabilitar un recurso conserva su registro, sus relaciones y el historial de reservas.

- **RN-REC-09:** Cuando un recurso sea deshabilitado y existan reservas futuras `PENDIENTE` o `APROBADA` que lo utilicen, dichas reservas deben cancelarse automáticamente y notificarse a los usuarios afectados, conforme a las reglas de cancelación definidas en [bookings].

- **RN-REC-10:** `requiere_apoyo_auxiliar` es un atributo propio del catálogo del recurso, configurado por la unidad organizacional responsable. Determina si el recurso exige acompañamiento técnico y su efecto sobre la reserva se rige por las reglas definidas en [bookings](bookings.md).

- **RN-REC-11:** El listado de recursos disponibles para una reserva se limita a los recursos que pertenecen a la unidad organizacional correspondiente. Los recursos con `acreditado = true` se excluyen de dicho listado y no son reservables, con independencia de su estado `boolean = true` u operativo.

---

## Equipos — RN-EQP

- **RN-EQP-01:** Los equipos reservables se identifican mediante `equipos.equipos.id_equipo`; Reservas no mantiene una segunda copia del mismo equipo.

- **RN-EQP-02:** `equipos.equipos` contiene la información vigente necesaria para determinar la unidad organizacional y el estado del equipo utilizado por Reservas.

- **RN-EQP-03:** Solo equipos habilitados para uso y en estado operativo pueden incorporarse a nuevas reservas o aprobarse.

- **RN-EQP-04:** Estado operativo y disponibilidad temporal son condiciones independientes. Un equipo puede estar operativo y no estar disponible por encontrarse reservado.

- **RN-EQP-05:** Un cambio posterior en la unidad, estado u otros datos del equipo no modifica retroactivamente las reservas históricas.

- **RN-EQP-06:** Las nuevas operaciones utilizan la información vigente del equipo al momento de realizar la validación.

- **RN-EQP-07:** Un equipo puede reservarse sin espacio cuando la composición y el `tipo_uso` de la reserva lo permitan.

- **RN-EQP-08:** Un equipo puede utilizarse dentro o fuera del campus cuando las reglas de reserva y las políticas aplicables lo permitan.

---

## Mobiliarios — RN-MOB

- **RN-MOB-01:** Cada elemento de mobiliario reservable tiene un registro individual en `reservas.mobiliarios`.

- **RN-MOB-02:** Cada mobiliario pertenece a una unidad organizacional mediante `id_unidad`.

- **RN-MOB-03:** Solo mobiliarios con `habilitado = true` pueden incorporarse a nuevas reservas.

- **RN-MOB-04:** La exclusividad temporal de cada mobiliario se evalúa individualmente conforme a las reglas de disponibilidad de [bookings](bookings.md).

- **RN-MOB-05:** Deshabilitar un mobiliario conserva su registro, relaciones e historial.

---

## Otros recursos — RN-OTR

- **RN-OTR-01:** Cada elemento clasificado como otro recurso tiene un registro individual en `reservas.otros`.

- **RN-OTR-02:** Cada elemento pertenece a una unidad organizacional mediante `id_unidad`.

- **RN-OTR-03:** Solo elementos con `habilitado = true` pueden incorporarse a nuevas reservas.

- **RN-OTR-04:** Su exclusividad temporal se evalúa individualmente conforme a las reglas de disponibilidad de [bookings](bookings.md).

- **RN-OTR-05:** Deshabilitar un elemento conserva su registro, relaciones e historial.

---

## Desactivación y conservación histórica — RN-DES

- **RN-DES-01:** La desactivación de laboratorios, espacios o recursos es lógica y no elimina registros históricos.

- **RN-DES-02:** Deshabilitar un laboratorio, espacio o recurso impide su utilización en nuevas reservas mientras permanezca deshabilitado.

- **RN-DES-03:** La desactivación de un laboratorio, espacio o recurso cancela automáticamente las reservas futuras `PENDIENTE` o `APROBADA` que dependan de él, conforme a las reglas de cancelación definidas en [bookings]. No afecta reservas ya finalizadas, rechazadas o canceladas.

- **RN-DES-04:** Las reservas futuras afectadas por una desactivación se cancelan automáticamente y se notifican a los usuarios afectados, registrando la desactivación como motivo, conforme a las reglas de cancelación definidas en [bookings].

- **RN-DES-05:** Las reservas históricas conservan la referencia al espacio o recurso utilizado aunque posteriormente este sea deshabilitado.

---

## Importación masiva de inventario — RN-IMP

- **RN-IMP-01:** El sistema permite importar equipos institucionales de forma masiva a partir de una planilla.

- **RN-IMP-02:** La importación es idempotente por placa: un registro cuya placa ya exista se actualiza con los datos de la planilla en lugar de duplicarse; un registro con placa nueva se crea.

- **RN-IMP-03:** Un registro de la planilla sin placa, o con una placa inválida, no se importa y debe reportarse como error de la importación sin afectar el resto de los registros válidos.

- **RN-IMP-04:** La importación no modifica retroactivamente las reservas históricas asociadas a un equipo actualizado (ver RN-EQP-05).