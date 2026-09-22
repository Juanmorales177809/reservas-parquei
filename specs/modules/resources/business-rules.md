# Laboratorios, espacios y recursos

Contrato funcional del dominio de laboratorios, espacios y recursos.

La estructura persistente se define en [data-model](data-model.md), las reglas de reservas y disponibilidad en [business-rules.md](../reservations/business-rules.md) y las reglas de identidad y autorización en [business-rules.md](../auth/business-rules.md).

---

## Laboratorios — RN-LAB

- **RN-LAB-01:** `reservas.laboratorios_config` representa la configuración de Reservas asociada a una unidad organizacional. `id_unidad` es obligatorio, único y referencia `unidadOrganizacional.unidad_organizacional`.

- **RN-LAB-02:** El nombre y la identidad institucional de la unidad se obtienen de `unidadOrganizacional.unidad_organizacional`; no se duplican ni se administran desde `laboratorios_config`.

- **RN-LAB-03:** `habilitado_reservas` determina si la unidad acepta nuevas reservas. Deshabilitar las reservas no elimina ni modifica el historial existente.

- **RN-LAB-04:** Horario de atención, días habilitados, anticipación mínima, modalidad de reserva y aprobación automática son configuraciones propias del dominio de Reservas.

- **RN-LAB-05:** La configuración vigente de la unidad se utiliza para validar las operaciones de reserva conforme a [reservations](../reservations/business-rules.md).

- **RN-LAB-06:** Una unidad organizacional puede existir sin tener habilitado el servicio de Reservas. La existencia de la unidad no implica que pueda recibir reservas.

- **RN-LAB-07:** `notificar_por_correo` es la única configuración general por unidad que determina si se habilita el envío de correo saliente para las notificaciones asociadas a sus reservas y recursos. Se aplica antes de la preferencia individual que cada persona pueda configurar en Notifications. Deshabilitarla no afecta la generación de notificaciones in-app.

- **RN-LAB-08:** La creación inicial del horario de una unidad y cada modificación posterior deben conservar una versión en `reservas.laboratorios_config_historico`, con su intervalo de vigencia. Las versiones de una misma unidad no pueden solaparse. Las validaciones de nuevas reservas usan la configuración vigente; Reports usa la versión vigente en cada periodo analizado para indicadores históricos.

---

## Espacios

Los espacios pertenecen al módulo [espacios](../espacios/business-rules.md), propietario funcional de `reservas.espacios`. Sus reglas de pertenencia a una unidad, capacidad, unicidad del nombre, habilitación, recursos asociados y campos adicionales se definen allí; resources no las duplica.

Lo que sí pertenece a resources es la **configuración de la unidad** a la que pertenece el espacio —horario de atención, antelación, aprobación automática y visibilidad—, definida en `RN-LAB` y en `reservas.laboratorios_config`. Un espacio no tiene horario propio: hereda el de su unidad conforme a `RN-ESP-DIS-02` de espacios.

Los efectos de deshabilitar un espacio sobre las reservas futuras los determinan `RN-CAN-04` a `RN-CAN-08` de [reservations](../reservations/business-rules.md#cancelación--rn-can); la advertencia previa y la confirmación explícita se rigen por `RN-DES-06` y `RN-DES-07` de este módulo.

---

## Recursos — RN-REC

Para efectos de Reservas, se consideran recursos reservables los equipos, mobiliarios y otros elementos individualizables. Los espacios se gestionan como una categoría independiente.

- **RN-REC-01:** Todo recurso reservable representa un elemento individual identificable mediante su clave primaria.

- **RN-REC-02:** Todo recurso pertenece a una unidad organizacional.

- **RN-REC-03:** Al crear, modificar o aprobar una reserva, cada recurso asociado debe pertenecer a la misma unidad indicada por `reservas.reservas.id_unidad`.

- **RN-REC-04:** Un mismo recurso no puede aparecer más de una vez dentro de una misma reserva.

- **RN-REC-05:** La disponibilidad temporal se evalúa individualmente para cada recurso conforme a [reservations](../reservations/business-rules.md).

- **RN-REC-06:** El nombre de un recurso no constituye su identidad y puede repetirse. La identificación se realiza mediante su clave primaria.

- **RN-REC-07:** Solo recursos habilitados y, cuando corresponda, operativos pueden incorporarse a nuevas reservas.

- **RN-REC-08:** Deshabilitar un recurso conserva su registro, sus relaciones y el historial de reservas.

- **RN-REC-09:** Cuando un recurso sea deshabilitado, las reservas futuras `SOLICITADA` o `APROBADA` que lo utilicen deben tratarse conforme a las reglas de cancelación de [reservas](../reservations/business-rules.md#cancelación--rn-can), `RN-CAN-04` a `RN-CAN-08`, que distinguen el recurso `PRINCIPAL` del `ADICIONAL`. Resources no define ese efecto.

- **RN-REC-10:** `requiere_apoyo` es un atributo propio de `recursos.equipos`, obligatorio y configurado por la unidad organizacional responsable. Indica si el equipo exige acompañamiento técnico durante su uso.

- **RN-REC-11:** El listado de recursos disponibles para una reserva se limita a los recursos que pertenecen a la unidad organizacional correspondiente. Los equipos con `recursos.equipos.acreditado = true` se excluyen de dicho listado y no son reservables, con independencia de su estado u operatividad, por estar destinados a ensayos certificados. La acreditación es un atributo exclusivo de equipos: mobiliarios y otros recursos no se filtran por esta condición.

---

## Equipos — RN-EQP

- **RN-EQP-01:** Los equipos reservables se identifican mediante `recursos.equipos.id`, que coincide con `recursos.recursos.id`; Reservas no mantiene una segunda copia del mismo equipo.

- **RN-EQP-02:** `recursos.recursos.id_unidad` determina la unidad organizacional del equipo y `recursos.equipos.estado` contiene su condición operativa vigente para las validaciones de Reservations.

- **RN-EQP-03:** Solo equipos con `recursos.recursos.habilitado = true` y `recursos.equipos.estado = true` pueden incorporarse a nuevas reservas o aprobarse.

- **RN-EQP-04:** Estado operativo y disponibilidad temporal son condiciones independientes. Un equipo puede estar operativo y no estar disponible por encontrarse reservado.

- **RN-EQP-05:** Un cambio posterior en la unidad, estado u otros datos del equipo no modifica retroactivamente las reservas históricas.

- **RN-EQP-06:** Las nuevas operaciones utilizan la información vigente del equipo al momento de realizar la validación.

- **RN-EQP-07:** Un equipo puede reservarse sin espacio cuando la composición y el `tipo_uso` de la reserva lo permitan.
- **RN-EQP-08:** Todo equipo debe indicar mediante `requiere_apoyo` si exige acompañamiento técnico durante su uso.
- **RN-EQP-09:** El Técnico puede editar los datos de equipos existentes pertenecientes a su unidad organizacional y modificar tanto `recursos.recursos.habilitado` como `recursos.equipos.estado`, con el permiso `recursos.editar_equipos` asignado a esa unidad. No puede crear ni eliminar físicamente equipos, ni cambiar su unidad responsable. El Administrador puede realizar estas operaciones con alcance global y el permiso `recursos.administrar_equipos`.
- **RN-EQP-11:** La eliminación física de un equipo no está permitida; para retirarlo de nuevas operaciones se cambia su habilitación (`recursos.recursos.habilitado`) y se conserva su historial. El estado operativo (`recursos.equipos.estado`) expresa si el equipo está en condiciones de uso y también puede actualizarse sin borrar el registro.
- **RN-EQP-10:** Un equipo puede utilizarse dentro o fuera del campus cuando las reglas de reserva y las políticas aplicables lo permitan.

---

## Mobiliarios — RN-MOB

- **RN-MOB-01:** Cada elemento de mobiliario reservable tiene un registro individual en `recursos.mobiliarios`.

- **RN-MOB-02:** Cada mobiliario pertenece a una unidad organizacional mediante `id_unidad`.

- **RN-MOB-03:** Solo mobiliarios con `habilitado = true` pueden incorporarse a nuevas reservas.

- **RN-MOB-04:** La exclusividad temporal de cada mobiliario se evalúa individualmente conforme a las reglas de disponibilidad de [reservations](../reservations/business-rules.md).

- **RN-MOB-05:** Deshabilitar un mobiliario conserva su registro, relaciones e historial.

---

## Otros recursos — RN-OTR

- **RN-OTR-01:** Cada elemento clasificado como otro recurso tiene un registro individual en `recursos.otros_recursos`.

- **RN-OTR-02:** Cada elemento pertenece a una unidad organizacional mediante `id_unidad`.

- **RN-OTR-03:** Solo elementos con `habilitado = true` pueden incorporarse a nuevas reservas.

- **RN-OTR-04:** Su exclusividad temporal se evalúa individualmente conforme a las reglas de disponibilidad de [reservations](../reservations/business-rules.md).

- **RN-OTR-05:** Deshabilitar un elemento conserva su registro, relaciones e historial.

## Administración por rol — RN-ROL

- **RN-ROL-01:** El Técnico solo administra elementos pertenecientes a su unidad organizacional.
- **RN-ROL-02:** El Técnico puede crear y administrar mobiliario y otros recursos de su unidad.
- **RN-ROL-03:** El Administrador tiene alcance global y puede realizar las operaciones administrativas definidas sobre cualquier unidad organizacional.

---

## Desactivación y conservación histórica — RN-DES

- **RN-DES-01:** La desactivación de laboratorios, espacios o recursos es lógica y no elimina registros históricos.

- **RN-DES-02:** Deshabilitar un laboratorio, espacio o recurso impide su utilización en nuevas reservas mientras permanezca deshabilitado.

- **RN-DES-03:** La desactivación de un laboratorio, espacio o recurso afecta las reservas futuras `SOLICITADA` o `APROBADA` que dependan de él, que se tratan conforme a `RN-CAN-04` a `RN-CAN-08` de [reservas](../reservations/business-rules.md#cancelación--rn-can). No afecta reservas ya finalizadas, rechazadas o canceladas.

- **RN-DES-04:** La notificación a los usuarios afectados y el registro de la desactivación como motivo corresponden a las reglas de cancelación de [reservas](../reservations/business-rules.md#cancelación--rn-can), que determinan además si la reserva se cancela o si únicamente se retira el elemento desactivado.

- **RN-DES-05:** Las reservas históricas conservan la referencia al espacio o recurso utilizado aunque posteriormente este sea deshabilitado.

- **RN-DES-06:** Cuando una desactivación vaya a cancelar reservas futuras conforme a `RN-CAN-04` del dominio de reservas —por tratarse de un espacio o de un recurso con rol `PRINCIPAL`—, el sistema debe advertirlo antes de ejecutarla. La advertencia indica la cantidad de reservas futuras que se cancelarán y exige una confirmación explícita del actor; si este no confirma, la desactivación no se ejecuta y no se modifica ninguna reserva.

- **RN-DES-07:** La advertencia de `RN-DES-06` no se presenta cuando la desactivación no cancela reservas, es decir, cuando el elemento no tiene reservas futuras o cuando solo participa como recurso `ADICIONAL` y únicamente será retirado conforme a `RN-CAN-05`.

---

## Importación masiva de inventario — RN-IMP

- **RN-IMP-01:** El sistema permite importar equipos institucionales de forma masiva a partir de una planilla.

- **RN-IMP-02:** La importación es idempotente por placa: un registro cuya placa ya exista se actualiza con los datos de la planilla en lugar de duplicarse; un registro con placa nueva se crea.

- **RN-IMP-03:** Un registro de la planilla sin placa, o con una placa inválida, no se importa y debe reportarse como error de la importación sin afectar el resto de los registros válidos.

- **RN-IMP-04:** La importación no modifica retroactivamente las reservas históricas asociadas a un equipo actualizado (ver RN-EQP-05).
