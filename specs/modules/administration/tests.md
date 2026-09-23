# Pruebas — Administration

Qué debe verificarse en unidades, cargos, permisos, auditoría e importaciones. Convenciones en [testing.md](../../docs/testing.md).

Dos cosas concentran el riesgo: **el permiso mal otorgado**, que amplía el alcance de quien no debería tenerlo, y **la importación a medias**, que deja el catálogo en un estado que nadie pidió.

---

## Permisos y ámbito

### T-ADM-01 — Un permiso por unidad exige coincidir con el cargo

- **Nivel:** contrato
- **Cubre:** `RN-PER-08`, `RN-PER-09`
- **Caso:** se asigna un permiso por unidad a una cuenta `PERSONAL` cuyo cargo vigente pertenece a otra unidad.
- **Esperado:** `422 VALIDACION`. La asignación ni se guarda ni se considera después.

### T-ADM-02 — Una cuenta Usuario no recibe permisos administrativos

- **Nivel:** contrato
- **Cubre:** `RN-PER-02`
- **Caso:** se intenta asignar cualquier permiso administrativo a una cuenta de tipo `USUARIO`.
- **Esperado:** `422 VALIDACION`.

### T-ADM-03 — El permiso no se extiende a otras unidades

- **Nivel:** servicio
- **Cubre:** `RN-PER-06`
- **Caso:** una cuenta con un permiso otorgado sobre la unidad A opera sobre la unidad B.
- **Esperado:** se deniega. Un permiso con unidad concreta **nunca** se extiende.

### T-ADM-04 — Retirar un permiso solo afecta a lo posterior

- **Nivel:** servicio
- **Cubre:** `RN-PER-04`, `RN-PER-05`
- **Caso:** se retira un permiso y se deshabilita otro, después de que ambos autorizaran operaciones ya ejecutadas.
- **Esperado:** las operaciones anteriores siguen siendo válidas; las nuevas se deniegan.

### T-ADM-05 — No se puede quedar el sistema sin permiso global

- **Nivel:** contrato
- **Cubre:** `RN-PER-03`
- **Caso:** se retira el último permiso global vigente del sistema.
- **Esperado:** `409 CONFLICTO`.

---

## Unidades y cargos

### T-ADM-06 — Deshabilitar una unidad no borra nada

- **Nivel:** servicio
- **Cubre:** `RN-UNI-04`, `RN-UNI-05`
- **Caso:** se deshabilita una unidad con usuarios, personal, reservas y recursos asociados.
- **Esperado:** ninguno se elimina ni se modifica. La baja es lógica.

---

## Auditoría

### T-ADM-07 — Toda operación administrativa deja registro

- **Nivel:** servicio
- **Cubre:** `RN-AUD-01`, `RN-AUD-02`
- **Caso:** se asigna un permiso, se deshabilita una unidad y se cambia el estado de una cuenta.
- **Esperado:** tres filas con actor, acción, entidad, identificador y momento, y el actor resoluble por clave foránea.

### T-ADM-08 — La auditoría no se puede escribir ni corregir

- **Nivel:** contrato
- **Cubre:** `RN-AUD-05`, `RN-AUD-06`
- **Caso:** se intenta crear, modificar y borrar un registro de auditoría por la API.
- **Esperado:** **no existe ninguna ruta** que lo permita. Un registro que se puede editar no es una auditoría.

### T-ADM-09 — El registro no guarda secretos

- **Nivel:** servicio
- **Cubre:** `RN-AUD-07`
- **Caso:** se audita una operación que manejó una contraseña y un token.
- **Esperado:** ni la contraseña ni el token completo aparecen en el registro.

---

## Importaciones

### T-ADM-10 — Una sola fila con error impide confirmar toda la carga

- **Nivel:** contrato
- **Cubre:** `RN-IMP-06`, `RN-IMP-09`
- **Caso:** se valida una planilla con una única fila inválida y se intenta confirmarla.
- **Esperado:** la validación devuelve `confirmable: false`, y confirmar responde `409 CONFLICTO`. **No se confirma ninguna fila**, ni siquiera las correctas.

### T-ADM-11 — El resultado por fila se conserva sin confirmar

- **Nivel:** servicio
- **Cubre:** `RN-IMP-08`
- **Caso:** se valida una carga con errores y no se confirma.
- **Esperado:** el resultado de cada fila queda registrado y consultable, con su motivo de rechazo.

### T-ADM-12 — La unidad de los equipos se elige al cargar

- **Nivel:** contrato
- **Cubre:** `RN-IMP-11`, `RN-IMP-12`
- **Caso:** se envía una carga de `EQUIPOS` sin `id_unidad`, y otra con una unidad indicada sobre equipos que ya existen.
- **Esperado:** la primera responde `400 SOLICITUD_INVALIDA`. La unidad **solo se aplica a los equipos que la carga crea**, nunca a los preexistentes.

### T-ADM-13 — El catálogo importable es cerrado

- **Nivel:** base de datos
- **Cubre:** `RN-IMP-01`
- **Caso:** se intenta registrar una importación con un catálogo distinto de `PROYECTOS`, `SEMILLEROS` o `EQUIPOS`.
- **Esperado:** el CHECK lo rechaza.
