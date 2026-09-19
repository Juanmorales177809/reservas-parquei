# ADR-001 — Mecanismo contra la doble reserva concurrente

- **Estado:** propuesto, pendiente de aprobación
- **Fecha:** 2026-09-19
- **Resuelve:** [OQ-06](open-questions.md)
- **Afecta a:** `architecture.md` §10, modelo de reservas, contrato de reservations

## Contexto

La exclusividad temporal es la restricción central del dominio: dos solicitudes concurrentes no pueden ocupar el mismo espacio o recurso en periodos incompatibles.

La especificación de producto ya acota la decisión. `spec.md` exige la garantía **"a nivel de base de datos, no solo de aplicación"**, y `architecture.md` §10 advierte que validar disponibilidad antes de escribir no garantiza nada bajo concurrencia: entre la consulta y el `INSERT` otra transacción puede haber escrito. Lo que falta decidir no es el nivel, sino el mecanismo.

`RN-DIS-06` define cuándo un elemento bloquea, y exige **tres** condiciones simultáneas:

1. está efectivamente asignado a la reserva;
2. tiene un periodo definido;
3. la reserva está en un estado bloqueante (`SOLICITADA`, `APROBADA` o `EN_EJECUCION`, conforme a `RN-EST-02`).

Esa tercera condición es la que complica el diseño: el estado vive en `reservas.reservas`, mientras que el periodo vive en `reserva_espacio` y en `reserva_recursos`.

## Alternativas consideradas

### A. Restricción de exclusión de PostgreSQL

`EXCLUDE USING gist` sobre el elemento y un rango temporal. La base rechaza el solape aunque el backend tenga un error o aparezca una ruta de escritura nueva que olvide validar.

Requiere la extensión `btree_gist`, una columna de rango por tabla y denormalizar la condición de bloqueo, porque una restricción parcial solo puede referirse a columnas de su propia tabla.

### B. Bloqueo pesimista sobre el elemento

`SELECT ... FOR UPDATE` sobre la fila del espacio o recurso antes de validar y escribir, dentro de la misma transacción. No cambia el esquema.

La garantía depende de que **todo** camino de escritura tome el bloqueo. Una ruta nueva, una importación o una corrección manual que lo omita reabren el problema sin que nada lo señale. No satisface la exigencia de `spec.md`, porque la garantía sigue viviendo en la aplicación.

### C. Aislamiento `SERIALIZABLE`

PostgreSQL detecta el conflicto y aborta una de las transacciones. Es correcto y no cambia el esquema, pero obliga a implementar reintentos en todas las operaciones de escritura del sistema, no solo en reservas, y degrada el rendimiento bajo concurrencia alta. Es una decisión global del backend para resolver un problema local.

### D. Franjas discretas con índice único

Funciona si el tiempo se modela en bloques fijos. No es el caso: `RN-TIP-PE-01` admite cualquier hora de inicio y fin, y campus y externo trabajan por fechas completas. Descartada.

## Decisión

Se adopta la **alternativa A, restricción de exclusión**, por ser la única que cumple literalmente `spec.md`: la garantía queda en la base y no depende de que el backend recuerde aplicarla.

La validación en la aplicación **se conserva**. No es redundante: es la que produce un `409 SOLAPAMIENTO` con un mensaje útil. La restricción es la última línea, para el caso en que dos transacciones pasen la validación a la vez.

### Estructura

Sobre `reserva_espacio`, para la exclusividad de espacios:

```sql
CREATE EXTENSION IF NOT EXISTS btree_gist;

ALTER TABLE reservas.reserva_espacio
  ADD COLUMN periodo tsrange
    GENERATED ALWAYS AS (tsrange(fecha + hora_inicio, fecha + hora_fin, '[)')) STORED,
  ADD COLUMN bloqueante boolean NOT NULL DEFAULT true,
  ADD CONSTRAINT ex_reserva_espacio_solape
    EXCLUDE USING gist (espacio_id WITH =, periodo WITH &&)
    WHERE (bloqueante);
```

Sobre `reserva_recursos`, para la exclusividad de recursos:

```sql
ALTER TABLE reservas.reserva_recursos
  ADD COLUMN periodo tstzrange
    GENERATED ALWAYS AS (tstzrange(fecha_inicio_uso, fecha_fin_uso, '[)')) STORED,
  ADD COLUMN bloqueante boolean NOT NULL DEFAULT true,
  ADD CONSTRAINT ex_reserva_recursos_solape
    EXCLUDE USING gist (recurso_id WITH =, periodo WITH &&)
    WHERE (bloqueante);
```

El rango es semiabierto `[)`: una reserva que termina a las 12:00 no choca con otra que empieza a las 12:00.

### Cómo se cumplen las tres condiciones de `RN-DIS-06`

| Condición | Cómo se satisface |
|---|---|
| Asignado efectivamente | La fila existe en `reserva_recursos` y no está retirada; se refleja en `bloqueante` |
| Periodo definido | Si `fecha_inicio_uso` o `fecha_fin_uso` son `NULL`, el rango generado es `NULL` y la restricción **no aplica a esa fila**. Es exactamente lo que pide `RN-DIS-06`: una solicitud sin periodo no bloquea franjas |
| Estado bloqueante | Denormalizado en `bloqueante`, mantenido por disparador desde las transiciones de `reservas.reservas.estado_id` |

`bloqueante` no es un dato nuevo del dominio: es una proyección del estado de la reserva y del retiro de la asignación. Se mantiene en el mismo disparador que ya registra las transiciones en `reserva_historial_estado`, y nunca se escribe desde la aplicación.

### Reservas por fechas completas

Campus y externo se definen por `fecha_salida` y `fecha_devolucion`, sin hora. Al derivar `fecha_inicio_uso` y `fecha_fin_uso` para `reserva_recursos`, el periodo abarca **hasta el final del día de devolución**: el equipo no queda disponible ese mismo día para otra reserva. Es decir, `[fecha_salida 00:00, fecha_devolucion + 1 día 00:00)`.

### Lista de espera

No tiene periodo (`RN-TIP-PLE-01`), así que su rango es `NULL` y la restricción no le aplica. Es coherente con `RN-DIS-06` y no requiere tratamiento especial.

## Consecuencias

**A favor:**

- La garantía es real y no depende del código de la aplicación, que es lo que exige `spec.md`.
- El índice GiST que crea la restricción sirve además para las consultas de disponibilidad por elemento y periodo.
- Los rangos `NULL` resuelven sin excepciones los casos sin periodo definido.

**En contra, y hay que asumirlo:**

- Requiere `btree_gist`, una extensión estándar pero que debe existir en el entorno de despliegue.
- Introduce dos columnas derivadas y un disparador. `bloqueante` es denormalización: si el disparador falla, la restricción protege de menos o de más. Debe cubrirse con pruebas.
- La violación llega al backend como un error de restricción de PostgreSQL, que hay que traducir a `409 SOLAPAMIENTO` en lugar de dejar escapar un `500`.
- La exclusividad de espacios y la de recursos viven en tablas distintas, así que son dos restricciones, no una.

## Verificación

La decisión se considera implementada cuando existan pruebas que, con dos transacciones concurrentes sobre el mismo elemento y periodos solapados, demuestren que:

1. exactamente una de las dos confirma y la otra falla;
2. la que falla devuelve `409 SOLAPAMIENTO` y no un error interno;
3. una reserva sin periodo definido no impide otra sobre el mismo elemento;
4. cancelar o rechazar una reserva libera la franja de inmediato;
5. una reserva que termina a la misma hora en que otra empieza no se considera solape.

Mientras esas pruebas no existan, `architecture.md` §10 y el contrato de reservations siguen describiendo un requisito, no una garantía satisfecha.

## Pendiente de esta decisión

Falta definir cómo se derivan `fecha_inicio_uso` y `fecha_fin_uso` de `reserva_recursos` a partir del detalle de cada tipo de reserva. Hoy son nulables y el modelo no dice quién las escribe ni cuándo; sin esa regla, la restricción de recursos no protege nada porque el rango sería siempre `NULL`.
