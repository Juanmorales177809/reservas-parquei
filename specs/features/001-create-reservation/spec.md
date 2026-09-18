# 001 — Crear una reserva

Primera funcionalidad a implementar. Recorta el alcance a la creación de una solicitud: no incluye aprobación, ejecución, cancelación ni reprogramación.

El comportamiento completo vive en los módulos; este documento solo delimita el alcance de la entrega y enumera lo que debe cumplirse para darla por terminada.

## Objetivo

Permitir que una cuenta autenticada registre una solicitud de reserva que cumpla todas las reglas aplicables a su tipo.

## Alcance

Incluye:

- selección de laboratorio o unidad organizacional;
- selección del tipo de reserva habilitado para ese laboratorio;
- los datos temporales que exija el tipo seleccionado;
- selección de espacio o de recursos, según el tipo;
- número de asistentes y acompañantes cuando el tipo lo admita;
- contexto académico, investigativo o institucional;
- campos adicionales configurados para el espacio;
- validación y registro de la solicitud con su estado inicial.

No incluye: aprobación, propuestas de horario, ejecución, devolución, cancelación, órdenes de salida ni notificaciones más allá de la confirmación de creación.

## Reglas aplicables

| Ámbito | Reglas |
|---|---|
| Composición general | `RN-RES-01` a `RN-RES-12` |
| Tipo de reserva | `RN-TIP-01` a `RN-TIP-06` |
| Reglas del tipo elegido | `RN-TIP-PE`, `RN-TIP-RI`, `RN-TIP-RC`, `RN-TIP-RE` o `RN-TIP-PLE` |
| Horario | `RN-HOR-01` a `RN-HOR-07` |
| Disponibilidad | `RN-DIS` |
| Contexto | `RN-CTX-01` a `RN-CTX-07` |
| Acompañantes | `RN-ACO-01` a `RN-ACO-06` |
| Estado inicial y aprobación automática | `RN-EST` y `RN-APR-03` a `RN-APR-06` |
| Perfil del solicitante | `RN-RES-11`, que exige `RN-USR-07`, `RN-USR-08` y `RN-USR-11` de usuarios |

Salvo donde se indique otro módulo, las reglas citadas son de reservations. El flujo de referencia es [`UF-RES-01`](../../modules/reservations/user-flows.md) para reserva por espacio, y `UF-RES-02` a `UF-RES-05` para los demás tipos.

## Criterios de aceptación

- Una solicitud válida se registra con el estado inicial que corresponda según la aprobación automática de su unidad.
- Una solicitud que incumpla cualquier regla de su tipo no se crea, y ninguna de sus partes queda escrita.
- Un conflicto de disponibilidad impide completar la operación, incluso si aparece entre la validación y el guardado.
- Una cuenta con la actualización inicial pendiente, o sin vinculación activa y válida, no puede crear reservas.
- El contexto seleccionado se valida contra las vinculaciones vigentes del usuario al guardar, no solo al abrir el formulario.

## Dependencia bloqueante

El tercer criterio de aceptación depende de **OQ-06**: el mecanismo transaccional que impide la doble reserva concurrente todavía no está elegido. Sin él, esta funcionalidad puede implementarse pero no puede darse por correcta bajo concurrencia.
