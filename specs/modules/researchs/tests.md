# Pruebas — Researchs

Qué debe verificarse en proyectos, semilleros, pasantías, trabajos de grado y actividades institucionales. Convenciones en [testing.md](../../docs/testing.md).

El riesgo propio de este módulo es **la vinculación duplicada**: si reactivar se implementa como crear, una persona acumula filas y el conteo de vinculaciones activas deja de significar nada.

---

## Vinculaciones

### T-INV-01 — Reactivar no duplica

- **Nivel:** servicio
- **Cubre:** `RN-INV-14`
- **Caso:** se vincula una cuenta a un proyecto, se desactiva la vinculación y se vuelve a vincular la misma cuenta al mismo proyecto.
- **Esperado:** **se reactiva la fila existente**, no se crea otra. La tabla conserva una sola vinculación por par.

### T-INV-02 — Desactivar la última no bloquea

- **Nivel:** contrato
- **Cubre:** `RN-INV-16`
- **Caso:** se desactiva la última vinculación activa de una cuenta.
- **Esperado:** la operación procede y la respuesta incluye `sin_vinculaciones_activas: true`. Es un aviso, no un error: quien administra decide.

### T-INV-03 — Sin vinculación activa no se reserva

- **Nivel:** servicio
- **Cubre:** `RN-INV-05`
- **Caso:** una cuenta sin ninguna vinculación activa intenta crear una reserva con contexto.
- **Esperado:** se rechaza. La vinculación se comprueba **en el momento de la operación**, no al crear la cuenta.

### T-INV-04 — Los proyectos no restringen dónde se reserva

- **Nivel:** servicio
- **Cubre:** `RN-INV-04`
- **Caso:** una cuenta vinculada a un proyecto reserva en una unidad distinta de la que administra ese proyecto.
- **Esperado:** procede. Los proyectos y semilleros se asocian a **personas**, nunca a laboratorios, y no limitan dónde puede reservar el usuario.

---

## Catálogos

### T-INV-05 — Los identificadores institucionales no se repiten

- **Nivel:** base de datos
- **Cubre:** `RN-INV-02`
- **Caso:** se registran dos proyectos con el mismo código institucional.
- **Esperado:** la base lo rechaza por unicidad.

### T-INV-06 — Deshabilitar conserva el historial

- **Nivel:** servicio
- **Cubre:** `RN-INV-15`
- **Caso:** se deshabilita un proyecto que ya fue contexto de reservas.
- **Esperado:** las reservas conservan su referencia; el proyecto deja de ofrecerse como contexto nuevo.

---

## Actividades institucionales

### T-INV-07 — La actividad institucional tiene su propio contexto

- **Nivel:** contrato
- **Cubre:** `RN-ACT-01`, `RN-ACT-02`
- **Caso:** se crea una reserva con contexto de actividad institucional.
- **Esperado:** se acepta sin exigir proyecto ni semillero, y la actividad queda referenciada.

### T-INV-08 — Un contexto incompatible se rechaza

- **Nivel:** base de datos
- **Cubre:** `RN-ACT-04`
- **Caso:** se intenta registrar un contexto de reserva con dos tipos a la vez, y otro sin ninguno cuando el tipo lo exige.
- **Esperado:** el CHECK rechaza ambos.

---

## Perfil propio

### T-INV-09 — Cada quien administra sus vinculaciones

- **Nivel:** contrato
- **Cubre:** `RN-INV-12`
- **Caso:** una cuenta consulta y modifica sus vinculaciones bajo `/api/perfil`, y después intenta modificar las de otra persona.
- **Esperado:** lo propio procede; lo ajeno exige permiso administrativo y se deniega sin él.
