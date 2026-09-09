# Reservas

Contrato funcional. El modelo persistente está en [data-model](../core/data-model.md); los elementos en [spaces and resources](spaces-and-resources.md) y los permisos en [identity](identity.md).

## Catálogos — RN-TIP

- **RN-TIP-01:** `tipo_reserva_id` es obligatorio y debe referir un tipo habilitado al crear.
- **RN-TIP-02:** Tipos y motivos tienen `nombre`, `descripcion` y `habilitado`; deshabilitar conserva historial.
- **RN-TIP-03:** `motivo_solicitud_id` es opcional salvo política específica y no se eliminan físicamente registros usados.

## Creación y composición — RN-RES

- **RN-RES-01:** Toda reserva tiene reservista autenticado e `id_unidad` obligatorio.
- **RN-RES-02:** Se admite solo espacio, solo equipo, solo mobiliario, solo otro recurso, varios recursos o espacio con recursos.
- **RN-RES-03:** No puede confirmarse una reserva sin al menos un espacio o recurso.
- **RN-RES-04:** `espacio_id` es opcional; todo elemento debe pertenecer a la unidad de la reserva.
- **RN-RES-05:** `asistentes >= 0`; si hay espacio, asistentes no supera su capacidad.
- **RN-RES-06:** `tipo_uso` admite `ESPACIO_RESERVADO`, `DENTRO_CAMPUS` y `FUERA_CAMPUS`.
- **RN-RES-07:** El primer tipo exige espacio; el segundo permite omitirlo pero exige `ubicacion_uso` si se omite; el tercero exige espacio nulo y ubicación.
- **RN-RES-08:** Un usuario puede tener reservas simultáneas sobre elementos distintos.

## Horario — RN-RES

- **RN-RES-09:** Se usan horas enteras, `hora_inicio < hora_fin`, sin cruce de medianoche y dentro del horario del laboratorio.
- **RN-RES-10:** No se aceptan fechas pasadas. `horas_antelacion` se exige al crear o reprogramar, no al aprobar.
- **RN-RES-11:** Editar, crear y aprobar revalidan composición, habilitación, pertenencia, horario, capacidad, estado operativo y disponibilidad según el modelo.

## Estados — RN-EST

Solo existen `PENDIENTE`, `APROBADA`, `RECHAZADA` y `CANCELADA`. PENDIENTE y APROBADA bloquean; RECHAZADA y CANCELADA no bloquean. No existe FINALIZADA.

## Disponibilidad — RN-DIS

- **RN-DIS-01:** Los intervalos son `[hora_inicio, hora_fin)`; bloques contiguos no se solapan.
- **RN-DIS-02:** Se valida por espacio y por cada recurso individual.
- **RN-DIS-03:** Un equipo debe estar operativo según LIA al crear o aprobar.
- **RN-DIS-04:** Crear, editar horario, agregar/cambiar elementos y aprobar usan la garantía transaccional obligatoria de [data-model](../core/data-model.md#4-garantia-transaccional); consultar antes de guardar no basta.

## Aprobación — RN-APR

- **RN-APR-01:** La autorización se deriva directamente de `personal -> cargo -> unidad` en LIA.
- **RN-APR-02:** La aprobación automática nunca omite disponibilidad, horario, capacidad, estado operativo, habilitación o pertenencia.
- **RN-APR-03:** Un gestor autorizado dentro de su propio ámbito puede crear directamente APROBADA si la política lo permite; fuera de él sigue la política del laboratorio receptor.
- **RN-APR-04:** Aprobar revalida disponibilidad y no exige una nueva anticipación mínima.
- **RN-APR-05:** Rechazar conserva la información histórica y registra motivo cuando sea requerido.

## Cancelación — RN-CAN

- **RN-CAN-01:** Cancelar conserva la reserva y libera sus elementos.
- **RN-CAN-02:** Se permite cancelar hasta la fecha y hora de inicio inclusive; después no.
- **RN-CAN-03:** Se registra actor y momento. Deshabilitar un espacio o recurso conserva reservas futuras y notifica a sus afectados.

## Auditoría — RN-AUD

- **RN-AUD-01:** Crear, modificar, aprobar, rechazar y cancelar generan auditoría.
- **RN-AUD-02:** El registro incluye actor, acción, entidad, identificador y fecha/hora.
- **RN-AUD-03:** La trazabilidad no crea una copia de personal; usa el actor disponible en la misma base y conserva su representación histórica.
