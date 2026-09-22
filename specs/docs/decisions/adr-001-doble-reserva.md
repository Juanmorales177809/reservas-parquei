# ADR-001 — Mecanismo contra la doble reserva concurrente

- **Estado:** seleccionado a nivel de diseño; pendiente de aprobación formal e implementación
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

El estado vive en `reservas.reservas`. El periodo de espacios está en `reserva_espacio`; el de recursos está en los detalles por tipo. La restricción de exclusión necesita que el periodo de cada fila sea consultable desde la misma fila que contiene el recurso o espacio, por lo que el periodo del recurso se proyecta técnicamente en `reserva_recursos` y se sincroniza con sus detalles dentro de la misma transacción.

## Alternativas consideradas

### A. Restricción de exclusión de PostgreSQL

`EXCLUDE USING gist` sobre el elemento y un rango temporal. La base rechaza el solape aunque el backend tenga un error o aparezca una ruta de escritura nueva que olvide validar.

Requiere la extensión `btree_gist`, una columna de rango por tabla y denormalizar la condición de bloqueo, porque una restricción parcial solo puede referirse a columnas de su propia tabla. En recursos, una columna generada no sirve para leer fechas de las tablas de detalle; se requiere una columna derivada mantenida transaccionalmente por disparadores.

### B. Bloqueo pesimista sobre el elemento

`SELECT ... FOR UPDATE` sobre la fila del espacio o recurso antes de validar y escribir, dentro de la misma transacción. No cambia el esquema.

La garantía depende de que **todo** camino de escritura tome el bloqueo. Una ruta nueva, una importación o una corrección manual que lo omita reabren el problema sin que nada lo señale. No satisface la exigencia de `spec.md`, porque la garantía sigue viviendo en la aplicación.

### C. Aislamiento `SERIALIZABLE`

PostgreSQL detecta el conflicto y aborta una de las transacciones. Es correcto y no cambia el esquema, pero obliga a implementar reintentos en todas las operaciones de escritura del sistema, no solo en reservas, y degrada el rendimiento bajo concurrencia alta. Es una decisión global del backend para resolver un problema local.

### D. Franjas discretas con índice único

Funciona si el tiempo se modela en bloques fijos. No es el caso: `RN-TIP-PE-01` admite cualquier hora de inicio y fin, y campus y externo trabajan por fechas completas. Descartada.

## Decisión propuesta

La propuesta selecciona la **alternativa A, restricción de exclusión**, por ser la única que cumple literalmente `spec.md`: la garantía quedaría en la base y no dependería de que el backend recuerde aplicarla. Esta selección de diseño aún requiere aprobación formal e implementación.

La validación en la aplicación **se conserva**. No es redundante: es la que produce un `409 SOLAPAMIENTO` con un mensaje útil. La restricción es la última línea, para el caso en que dos transacciones pasen la validación a la vez.

### Estructura

Los siguientes fragmentos describen la estructura objetivo. La migración debe crear las columnas y disparadores, inicializar las proyecciones de las filas existentes y solo después habilitar las restricciones de exclusión.

Para espacios, los extremos están en la misma fila, por lo que `periodo` puede ser generado. El `CASE` devuelve un **NULL SQL** si falta cualquiera de los extremos; no pasa `NULL` al constructor de rangos.

```sql
CREATE EXTENSION IF NOT EXISTS btree_gist;

ALTER TABLE reservas.reserva_espacio
  ADD COLUMN periodo tsrange
    GENERATED ALWAYS AS (
      CASE
        WHEN fecha IS NOT NULL
         AND hora_inicio IS NOT NULL
         AND hora_fin IS NOT NULL
        THEN tsrange(fecha + hora_inicio, fecha + hora_fin, '[)')
        ELSE NULL::tsrange
      END
    ) STORED,
  ADD COLUMN bloqueante boolean NOT NULL DEFAULT false;
```

Después de instalar el disparador de estado y sincronizar las filas existentes, se agrega la restricción:

```sql
ALTER TABLE reservas.reserva_espacio
  ADD CONSTRAINT ex_reserva_espacio_solape
    EXCLUDE USING gist (espacio_id WITH =, periodo WITH &&)
    WHERE (bloqueante AND periodo IS NOT NULL);
```

Para recursos, `periodo` no es una columna generada: un disparador lo calcula desde el detalle compatible con el tipo de reserva y lo guarda como proyección técnica en `reserva_recursos`. Las fechas de negocio permanecen en su detalle y no se agregan `fecha_inicio_uso` ni `fecha_fin_uso` a la tabla de asociación.

```sql
ALTER TABLE reservas.reserva_recursos
  ADD COLUMN periodo tstzrange NULL,
  ADD COLUMN bloqueante boolean NOT NULL DEFAULT false;
```

Después de instalar los disparadores de sincronización y completar las filas existentes, se agrega la restricción:

```sql
ALTER TABLE reservas.reserva_recursos
  ADD CONSTRAINT ex_reserva_recursos_solape
    EXCLUDE USING gist (recurso_id WITH =, periodo WITH &&)
    WHERE (bloqueante AND periodo IS NOT NULL);
```

El disparador de sincronización de recursos debe:

- Para una reserva `SOLICITADA` o `APROBADA`, derivar el periodo solicitado del detalle: intervalo horario para `RECURSO_INTERNO` y días completos desde `fecha_salida` hasta el inicio del día siguiente a `fecha_devolucion` para `RECURSO_CAMPUS` y `RECURSO_EXTERNO`. La conversión a `tstzrange` debe usar una zona horaria operativa explícita y uniforme, no la zona implícita de cada conexión.
- Al pasar a `EN_EJECUCION`, mantener ocupado cada recurso entregado hasta que se registre su devolución física. Si no existe todavía `devuelto_at`, el rango efectivo es `[inicio, )`, con extremo superior sin límite; cuando se registra `devuelto_at`, se actualiza a `[inicio, devuelto_at)`. Así, el recurso puede volver a reservarse desde el momento de su devolución, aunque otros recursos de la misma reserva sigan en ejecución.
- Dejar `periodo` como **NULL SQL** cuando no exista un periodo aplicable o falte un extremo necesario para definirlo. La ausencia de fecha no se representa pasando límites NULL a `tstzrange`, porque eso construiría un rango sin límite. Una ejecución abierta sin devolución es un caso distinto: tiene inicio y un rango intencionalmente abierto, no un periodo ausente.
- Recalcular la proyección cuando se inserte o modifique el detalle por tipo, la asociación o `estado_asignacion`, el estado de la reserva, o el registro de entrega/devolución. La actualización ocurre en la misma transacción.

`bloqueante` es una proyección técnica, no un dato editable desde la aplicación. En espacios refleja que la reserva está en estado bloqueante; en recursos requiere además `estado_asignacion = 'ASIGNADO'`. Se inicializa en `false` y se sincroniza al insertar o cambiar una reserva o asignación. `periodo IS NOT NULL` también forma parte del predicado de exclusión. La restricción solo indexa filas que satisfacen ambas condiciones.

El rango es semiabierto `[)`: una reserva que termina a las 12:00 no choca con otra que empieza a las 12:00. Un extremo superior sin límite se usa exclusivamente mientras un recurso entregado sigue sin devolución registrada; no equivale a `NULL` SQL.

### Cómo se cumplen las tres condiciones de `RN-DIS-06`

| Condición | Cómo se satisface |
|---|---|
| Asignado efectivamente | En espacios, la fila de `reserva_espacio` contiene el espacio asignado. En recursos, la fila debe tener `estado_asignacion = 'ASIGNADO'`; `SOLICITADO`, `NO_DISPONIBLE` y `RETIRADO` no bloquean. |
| Periodo definido | `periodo` es un NULL SQL si no hay periodo aplicable o falta un extremo requerido. En ejecución, un recurso todavía no devuelto tiene un periodo abierto `[inicio, )` porque sigue ocupado. |
| Estado bloqueante | `bloqueante` refleja las transiciones de `reservas.reservas.estado_id`; para recursos también incorpora el estado de la asignación. El disparador lo mantiene en ambos tipos de cambio. |

El registro de devolución física se conserva en `reserva_ejecucion_recursos.devuelto_at`. La actualización de ese dato cierra el rango efectivo del recurso en esa marca de tiempo. La finalización global de la reserva no debe retrasar la disponibilidad de un recurso que ya fue devuelto.

### Lista de espera

`LISTA_ESPERA` no crea filas en `reserva_recursos` ni tiene espacio (`RN-TIP-PLE-01`); por tanto, no crea rangos ni bloquea recursos. Si una reserva obtiene un periodo posteriormente, la asignación se sincroniza y valida dentro de la misma transacción antes de confirmar el cambio.

## Consecuencias

**A favor:**

- La garantía es real y no depende del código de la aplicación, que es lo que exige `spec.md`.
- El índice GiST que crea la restricción sirve además para las consultas de disponibilidad por elemento y periodo.
- Los periodos ausentes se representan mediante NULL SQL y quedan fuera del índice; una ejecución abierta se representa con un límite superior sin acotar mientras el recurso siga sin devolución.

**En contra, y hay que asumirlo:**

- Requiere `btree_gist`, una extensión estándar pero que debe existir en el entorno de despliegue.
- Introduce las columnas técnicas `periodo` y `bloqueante` en las tablas de asignación, además de disparadores para mantenerlas. Son proyecciones derivadas: si no se sincronizan correctamente desde todos los cambios de estado, asociación, detalle y ejecución, la restricción puede proteger de menos o de más. Deben inicializarse y probarse antes de habilitar las restricciones.
- La violación llega al backend como un error de restricción de PostgreSQL, que hay que traducir a `409 SOLAPAMIENTO` en lugar de dejar escapar un `500`.
- La exclusividad de espacios y la de recursos viven en tablas distintas, así que son dos restricciones, no una.

## Verificación

La decisión se considera implementada cuando existan pruebas que, con dos transacciones concurrentes sobre el mismo elemento y periodos solapados, demuestren que:

1. exactamente una de las dos confirma y la otra falla;
2. la que falla devuelve `409 SOLAPAMIENTO` y no un error interno;
3. una reserva sin periodo definido no impide otra sobre el mismo elemento;
4. cancelar o rechazar una reserva libera la franja de inmediato;
5. un recurso entregado sigue bloqueado hasta registrar su devolución, y queda disponible desde `devuelto_at`;
6. una asociación `SOLICITADO`, `NO_DISPONIBLE` o `RETIRADO` no bloquea aunque la reserva tenga estado bloqueante;
7. una reserva que termina a la misma hora en que otra empieza no se considera solape.

Mientras esas pruebas no existan, `architecture.md` §10 y el contrato de reservations siguen describiendo un requisito, no una garantía satisfecha.

## Pendiente de esta decisión

El diseño de periodos y predicados queda definido aquí. Antes de declarar la garantía implementada faltan aprobar el ADR, definir en la migración la zona horaria operativa explícita para convertir los periodos locales a `tstzrange`, instalar y verificar los disparadores, inicializar las proyecciones existentes y ejecutar las pruebas de concurrencia de esta decisión.
