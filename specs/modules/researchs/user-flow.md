# User Flows — Researchs

Este documento describe únicamente la gestión administrativa propia de `investigacion`. Los flujos mediante los cuales un Usuario crea, desactiva o reactiva sus propias vinculaciones se encuentran en [Usuarios](../usuarios/user-flow.md).

## UF-INV-01 — Administrar vinculaciones ajenas y actividades institucionales

**Actor principal:** Administrador con alcance global.

**Precondiciones:**

- La cuenta del actor es `PERSONAL`, está activa y posee una asignación global vigente.
- La vinculación o actividad que se va a gestionar existe, cuando la operación no sea una creación.

**Flujo principal:**

1. El Administrador selecciona un Usuario o una actividad institucional.
2. El sistema verifica el alcance global del actor y rechaza la operación de un Técnico.
3. Para una vinculación, el Administrador puede crearla, desactivarla o reactivarla según RN-INV. Si ya existe una relación inactiva para el mismo Usuario y entidad, el sistema reactiva esa fila.
4. Para una actividad institucional, el Administrador puede crearla, modificar sus datos obligatorios, activarla o desactivarla según RN-ACT.
5. El sistema conserva las relaciones y referencias históricas; no elimina físicamente vinculaciones ni actividades.
6. El sistema registra la operación administrativa.

**Flujos alternos:**

- Si el actor no tiene alcance global, el sistema no revela ni modifica el registro solicitado.
- Si se intenta crear una segunda vinculación para la misma pareja Usuario-entidad, el sistema rechaza la duplicación o reactiva la fila existente si estaba inactiva.
