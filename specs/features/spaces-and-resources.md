# Laboratorios, espacios y recursos

Contrato funcional. La estructura está en [data-model](../core/data-model.md), reservas en [bookings](bookings.md) y permisos en [identity](identity.md).

## Laboratorios — RN-LAB

- **RN-LAB-01:** `laboratorios_config` representa la configuración de Reservas para una unidad de LIA; `id_unidad` es FK obligatoria y única.
- **RN-LAB-02:** El nombre se obtiene directamente de `unidadOrganizacional.unidad_organizacional`; no se duplica ni edita en Reservas.
- **RN-LAB-03:** `habilitado_reservas` es configuración local. Si es falso, no se crean nuevas reservas; se conserva el historial.
- **RN-LAB-04:** Horario, anticipación, modalidad y aprobación automática son configuración de Reservas y se validan en cada operación aplicable.

## Espacios — RN-ESP

- **RN-ESP-01:** Cada espacio pertenece a una unidad/laboratorio configurado.
- **RN-ESP-02:** Solo espacios habilitados pueden usarse en nuevas solicitudes.
- **RN-ESP-03:** `capacidad > 0`; limita asistentes cuando se selecciona el espacio.
- **RN-ESP-04:** El nombre es único por laboratorio: `UNIQUE (id_unidad, nombre)`.
- **RN-ESP-05:** Deshabilitar conserva historial y reservas; notifica reservas futuras PENDIENTE o APROBADA.
- **RN-ESP-06:** La exclusividad temporal sigue RN-DIS; el espacio puede omitirse conforme a RN-RES y `tipo_uso`.

## Recursos — RN-REC

- **RN-REC-01:** Cada recurso es una fila individual y pertenece a una unidad/laboratorio.
- **RN-REC-02:** Al crear, modificar o aprobar, todo recurso coincide con la unidad de la reserva.
- **RN-REC-03:** Un recurso no se repite dentro de la misma reserva y su disponibilidad se evalúa individualmente.
- **RN-REC-04:** Los nombres pueden repetirse; la identidad es la PK, no el nombre.
- **RN-REC-05:** Deshabilitar impide nuevas reservas, conserva asociaciones y notifica reservas futuras afectadas.

## Equipos — RN-EQP

- **RN-EQP-01:** Los equipos se referencian directamente mediante `equipos.equipos.id_equipo`; no existe copia en Reservas.
- **RN-EQP-02:** LIA es la fuente del estado operativo y de la unidad actual.
- **RN-EQP-03:** Solo equipos operativos pueden incluirse en nuevas solicitudes o aprobarse.
- **RN-EQP-04:** Estado operativo y disponibilidad temporal son validaciones independientes.
- **RN-EQP-05:** Un cambio posterior de unidad en LIA no reescribe el historial; las nuevas operaciones consultan el dato actual.
- **RN-EQP-06:** El equipo puede reservarse sin espacio y dentro o fuera del campus según RN-RES.

## Mobiliarios — RN-MOB

- **RN-MOB-01:** Cada elemento físico tiene registro individual en `reservas.mobiliarios`.
- **RN-MOB-02:** Solo elementos habilitados se incluyen en nuevas solicitudes; su exclusividad sigue RN-DIS.

## Otros recursos — RN-OTR

- **RN-OTR-01:** Cada elemento se identifica individualmente en `reservas.otros`.
- **RN-OTR-02:** Solo elementos habilitados se incluyen en nuevas solicitudes; su exclusividad sigue RN-DIS.

La desactivación es lógica y no cancela ni elimina reservas existentes.
