# Pruebas — Usuarios

Qué debe verificarse en identidades funcionales y fichas de Personal. Convenciones en [testing.md](../../docs/testing.md).

El riesgo propio de este módulo es **la identidad partida**: si el correo de una identidad puede cambiar mientras su cuenta conserva el anterior, la persona deja de ser una sola a ojos del sistema.

---

## Datos de identidad

### T-USR-01 — El documento es único

- **Nivel:** contrato
- **Cubre:** `RN-DAT-02`
- **Caso:** se crea una identidad con un documento ya registrado.
- **Esperado:** `409 DOCUMENTO_DUPLICADO`, **por la restricción de la base** y no por una consulta previa del servicio.

### T-USR-02 — El alta pide los cinco datos

- **Nivel:** contrato
- **Cubre:** `RN-DAT-01`
- **Caso:** se crea una identidad omitiendo cada uno de los datos obligatorios por turno.
- **Esperado:** `422 VALIDACION` en cada caso.

### T-USR-03 — El correo es inmutable con cuenta asociada

- **Nivel:** contrato
- **Cubre:** `RN-USR-08`, `RN-USR-09`
- **Caso:** se modifica el correo de una identidad que ya tiene cuenta.
- **Esperado:** `409 CONFLICTO`. En `GET /api/perfil` el correo se devuelve **como solo lectura**.

### T-USR-04 — El perfil queda marcado hasta completarse

- **Nivel:** servicio
- **Cubre:** `RN-USR-07`
- **Caso:** se crea una cuenta por autorregistro y se consulta su identidad antes de la revisión inicial.
- **Esperado:** `perfil_actualizado_at` es nulo. Se sella al completar los datos y las vinculaciones, no al crear la cuenta.

---

## Fichas de Personal

### T-USR-05 — La ficha nace activa

- **Nivel:** base de datos
- **Cubre:** `RN-PRS-04`
- **Caso:** se inserta una ficha sin indicar estado, y otra con estado nulo.
- **Esperado:** la primera queda activa; la segunda se rechaza. **No existe un tercer valor indeterminado.**

### T-USR-06 — Invitar Personal exige ficha activa

- **Nivel:** contrato
- **Cubre:** `RN-PRS-02`
- **Caso:** se invita una cuenta `PERSONAL` para un correo sin ficha, y para uno con ficha inactiva.
- **Esperado:** ambas se rechazan. La ficha se crea antes, en `/api/personal`.

### T-USR-07 — Desactivar una ficha no borra su historial

- **Nivel:** servicio
- **Cubre:** `RN-PRS-05`
- **Caso:** se desactiva una ficha que tiene cargo, permisos y operaciones auditadas.
- **Esperado:** el registro y su historial permanecen; la cuenta asociada deja de resolver rol administrativo.

---

## Relación con la cuenta

### T-USR-08 — Una cuenta tiene exactamente una identidad

- **Nivel:** base de datos
- **Cubre:** `RN-USR-10`
- **Caso:** se intenta vincular una cuenta a una identidad de Usuario y a una ficha de Personal a la vez, y después a ninguna.
- **Esperado:** el CHECK rechaza ambos. Es `USUARIO` o `PERSONAL`, nunca las dos ni ninguna.

### T-USR-09 — El correo coincide entre identidad y cuenta

- **Nivel:** servicio
- **Cubre:** `RN-USR-11`
- **Caso:** se compara el correo de una identidad con el de su cuenta asociada.
- **Esperado:** son el mismo, y ambos inmutables.
