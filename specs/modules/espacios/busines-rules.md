# Espacios

## Creación y configuración — RN-ESP

- **RN-ESP-01:** Todo espacio debe pertenecer a una unidad organizacional.

- **RN-ESP-02:** Un espacio debe definir su capacidad máxima cuando esta aplique.

- **RN-ESP-03:** Solo el Técnico de la unidad correspondiente puede crear, modificar o deshabilitar espacios; el Administrador puede hacerlo sobre cualquier unidad.

---

## Recursos asociados — RN-ESP-REC

- **RN-ESP-REC-01:** Un espacio puede tener cero o más recursos asociados.

- **RN-ESP-REC-02:** Los recursos asociados deben existir previamente en el catálogo de recursos; asociar un recurso a un espacio no crea un nuevo recurso.

- **RN-ESP-REC-03:** Un recurso puede asociarse o desasociarse de un espacio por el Técnico de la unidad o por el Administrador.

- **RN-ESP-REC-04:** La asociación de un recurso a un espacio no implica que el recurso esté disponible en todos los horarios en los que el espacio pueda reservarse.

- **RN-ESP-REC-05:** La disponibilidad de cada recurso asociado se determina de manera independiente a la disponibilidad del espacio.

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

- **RN-ESP-DIS-02:** La disponibilidad de un espacio debe considerar su horario configurado y las reservas bloqueantes existentes.

- **RN-ESP-DIS-03:** La capacidad habilitada del espacio limita el número de asistentes permitido en las reservas que utilicen dicho espacio.

---

## Deshabilitación — RN-ESP-HAB

- **RN-ESP-HAB-01:** Deshabilitar un espacio impide utilizarlo en nuevas reservas.

- **RN-ESP-HAB-02:** Deshabilitar un espacio no elimina su información ni su historial.

- **RN-ESP-HAB-03:** Cuando se deshabilite un espacio, las reservas futuras que dependan de él deben ser tratadas conforme a las reglas de cancelación del dominio de reservas.

- **RN-ESP-HAB-04:** La deshabilitación de un espacio debe conservar sus asociaciones históricas con reservas, recursos y campos adicionales.
