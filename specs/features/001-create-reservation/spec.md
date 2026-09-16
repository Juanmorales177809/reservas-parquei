# Create Reservation

## Objective

Permitir que una cuenta autenticada cree una solicitud de reserva.

## Scope

Incluye:
- selección de Laboratorio
- selección de fecha y horario;
- selecciona tipo de reserva;
- selección de espacios y/o recursos;
- selección de asistentes;
- contexto asociado;
- validación;
- creación de la solicitud.

## Applicable Business Rules

- RN-RES-01
- RN-RES-02
- RN-RES-03
- RN-HOR-01
- RN-HOR-04
- RN-DIS-01
- RN-EST-01

## Acceptance Criteria

- Una solicitud válida se registra correctamente.
- Una solicitud inválida no se crea.
- Un conflicto de disponibilidad impide completar la operación.