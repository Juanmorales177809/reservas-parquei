# Espacios

## Propósito

Administrar los espacios físicos reservables de cada unidad organizacional: su identidad, capacidad, habilitación, los recursos que quedan asociados a ellos y los campos adicionales que el Usuario debe diligenciar al reservarlos.

Un espacio es el objeto de una reserva de tipo `ESPACIO`. Este módulo define **qué es** un espacio y **cómo se configura**; cuándo está libre y quién puede ocuparlo lo determina [Reservations](../reservations/business-rules.md).

## Alcance y responsabilidades

- Registrar espacios con su nombre, ubicación, capacidad y descripción, únicos por nombre dentro de su unidad.
- Habilitar y deshabilitar un espacio, advirtiendo antes cuántas reservas futuras se cancelarían y exigiendo confirmación explícita.
- Asociar recursos existentes a un espacio y retirar esa asociación sin borrar su historial.
- Configurar los campos adicionales del espacio, sus opciones cuando son de selección, su obligatoriedad y su orden de presentación.
- Conservar la interpretación histórica: un campo o una opción utilizados en una reserva se deshabilitan, nunca se eliminan.

## Conceptos propios

El módulo es propietario de `reservas.espacios`, `reservas.espacio_recursos`, `reservas.espacio_campos` y `reservas.espacio_campo_opciones`. Sus campos y restricciones están en [data-model.md](data-model.md).

**Un espacio no tiene horario propio.** El horario aplicable es el de atención de su unidad organizacional, que se configura en Resources (`RN-ESP-DIS-02`). Cambiar el horario de la unidad cambia el de todos sus espacios, y este módulo no expone ninguna operación de horario.

Un **campo adicional** es información que el espacio pide al reservarlo —el ensayo a realizar, el tipo de probeta—. Admite cinco tipos cerrados: texto, texto largo, número, sí o no, y lista de opciones (`RN-ESP-CAM-02`). Los valores que el Usuario diligencia pertenecen a la reserva, no al espacio, y se conservan con su interpretación histórica.

## Dependencias y límites

| Módulo | Relación |
|---|---|
| [Resources](../resources/overview.md) | Proporciona los recursos asociables y **configura el horario de atención de la unidad**, que es el que rige para todos los espacios de esa unidad. |
| [Reservations](../reservations/business-rules.md) | Determina la disponibilidad temporal, el solapamiento y el efecto de deshabilitar un espacio sobre las reservas futuras. Conserva los valores diligenciados en los campos adicionales. |
| [Auth](../auth/overview.md) | Evalúa el permiso `espacios.administrar` y su ámbito organizacional en cada operación. |
| [Administration](../administration/overview.md) | Aporta la unidad organizacional a la que pertenece cada espacio. |

## Fuera de alcance

- **Disponibilidad temporal.** Saber si un espacio está libre en una franja depende de las reservas, no de la configuración del espacio (`RN-ESP-REC-05`).
- **Horario de atención.** Pertenece a la unidad y se administra en Resources.
- **Cancelación de reservas.** Deshabilitar un espacio las cancela, pero el efecto lo definen las reglas de cancelación de Reservations (`RN-CAN-04`); este módulo no reimplementa esa lógica.
- **Uso del espacio durante una reserva.** Es un flujo de Reservations.

## Estado y decisiones pendientes

Las reglas están en `RN-ESP`, `RN-ESP-DIS`, `RN-ESP-HAB`, `RN-ESP-REC` y `RN-ESP-CAM`. `RN-ESP-HAB-03` quedó retirada por estar contenida en `RN-ESP-HAB-05`, y su identificador no se reasignó.

El catálogo de tipos de campo quedó cerrado en cinco valores. Esta documentación describe el diseño objetivo y no acredita su implementación en la base de datos ni en el backend.

## Documentación relacionada

- [Reglas de negocio](business-rules.md).
- [Modelo de datos del módulo](data-model.md): tablas propias, relaciones y diferencias pendientes respecto al inventario principal.
- [Flujos de usuario](user-flow.md).
- [Contrato de API](../../contratos/espacios/api-contract.md).
- [Especificación de pantallas](screens.md), [wireframes](wireframes.md) y [navegación funcional](screen-flow.md): las cuatro superficies de espacios.
