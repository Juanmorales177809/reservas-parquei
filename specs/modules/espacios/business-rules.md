# Espacios

## Creación y configuración — RN-ESP

- **RN-ESP-01:** Todo espacio debe pertenecer a una unidad organizacional.

- **RN-ESP-02:** Todo espacio debe definir su capacidad máxima, que es obligatoria y mayor que cero. No se admite un espacio sin capacidad declarada.

- **RN-ESP-03:** Solo el Técnico de la unidad correspondiente puede crear, modificar o deshabilitar espacios; el Administrador puede hacerlo sobre cualquier unidad.

---

## Recursos asociados — RN-ESP-REC

- **RN-ESP-REC-01:** Un espacio puede tener cero o más recursos asociados.

- **RN-ESP-REC-02:** Los recursos asociados deben existir previamente en el catálogo de recursos; asociar un recurso a un espacio no crea un nuevo recurso.

- **RN-ESP-REC-03:** Un recurso puede asociarse o desasociarse de un espacio por el Técnico de la unidad o por el Administrador.

- **RN-ESP-REC-04:** La asociación de un recurso a un espacio no implica que el recurso esté disponible en todos los horarios en los que el espacio pueda reservarse.

- **RN-ESP-REC-05:** La disponibilidad de cada recurso asociado se determina de manera independiente a la disponibilidad del espacio.

- **RN-ESP-REC-06:** El espacio y el recurso asociado deben pertenecer a la misma unidad organizacional.

- **RN-ESP-REC-07:** Un recurso solo puede estar asociado activamente a un espacio. Para asociarlo a otro espacio, el Técnico debe retirar primero la asociación vigente; el retiro deshabilita la fila y conserva el historial.

---

## Campos adicionales — RN-ESP-CAM

- **RN-ESP-CAM-01:** Un espacio puede tener cero o más campos adicionales configurados para recopilar información específica durante su reserva.

- **RN-ESP-CAM-02:** Cada campo adicional debe definir como mínimo nombre, tipo de campo, obligatoriedad, orden y estado de habilitación.

- **RN-ESP-CAM-03:** Los campos de tipo selección pueden tener una o más opciones configuradas.

- **RN-ESP-CAM-04:** Los campos adicionales pertenecen a la configuración del espacio y no forman parte fija de la estructura general de una reserva.

- **RN-ESP-CAM-05:** Un campo adicional utilizado previamente en reservas no debe eliminarse de forma que se pierda la interpretación histórica de los valores registrados.

---

## Disponibilidad — RN-ESP-DIS

- **RN-ESP-DIS-01:** Un espacio solo puede ofrecerse para nuevas reservas cuando se encuentre habilitado.

- **RN-ESP-DIS-02:** Un espacio no tiene horario propio: su disponibilidad debe considerar el horario de atención de su unidad, definido en `reservas.laboratorios_config`, y las reservas bloqueantes existentes. Cambiar el horario de la unidad cambia el de todos sus espacios.

- **RN-ESP-DIS-03:** La capacidad habilitada del espacio limita el número de asistentes permitido en las reservas que utilicen dicho espacio.

---

## Deshabilitación — RN-ESP-HAB

- **RN-ESP-HAB-01:** Deshabilitar un espacio impide utilizarlo en nuevas reservas.

- **RN-ESP-HAB-02:** Deshabilitar un espacio no elimina su información ni su historial.

- **RN-ESP-HAB-04:** La deshabilitación de un espacio debe conservar sus asociaciones históricas con reservas, recursos y campos adicionales.

- **RN-ESP-HAB-05:** Deshabilitar un espacio con reservas futuras cancela esas reservas conforme a `RN-CAN-04` del dominio de reservas. Antes de ejecutarla, el sistema debe advertir la cantidad de reservas futuras que se cancelarán y exigir una confirmación explícita del actor, conforme a `RN-DES-06` de recursos. Si el actor no confirma, el espacio permanece habilitado y ninguna reserva se modifica.

El identificador `RN-ESP-HAB-03` quedó retirado: enunciaba de forma genérica el mismo comportamiento que `RN-ESP-HAB-05` define completo, con la regla de cancelación citada, la advertencia previa y el efecto de no confirmar. La numeración no se reasigna, para que las referencias vigentes a `RN-ESP-HAB-04` y `RN-ESP-HAB-05` sigan apuntando a la misma regla.
