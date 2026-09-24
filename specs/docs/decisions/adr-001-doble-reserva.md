# ADR-001 — Mecanismo contra la doble reserva concurrente

- **Estado:** diseño temporal aprobado el 2026-09-23; ampliación funcional aprobada el 2026-09-24 (hallazgo 1). Pendientes diseño de integridad del compromiso físico único, migración e implementación y pruebas; DB-12 no acredita todavía la garantía ampliada.
- **Fecha:** 2026-09-19
- **Resuelve:** [OQ-06](open-questions.md)
- **Afecta a:** `architecture.md` §10, modelo de reservas, contrato de reservations

## Contexto

La exclusividad temporal es la restricción central del dominio: dos solicitudes concurrentes no pueden ocupar el mismo espacio o recurso en periodos incompatibles.

La especificación de producto ya acota la decisión. `spec.md` exige la garantía **"a nivel de base de datos, no solo de aplicación"**, y `architecture.md` §10 advierte que validar disponibilidad antes de escribir no garantiza nada bajo concurrencia: entre la consulta y el `INSERT` otra transacción puede haber escrito. Lo que falta decidir no es el nivel, sino el mecanismo.

`RN-DIS-06` de reservations distingue dos garantías:

1. **Planificación temporal:** espacios, recursos internos y complementarios sin entrega física bloquean su periodo efectivamente asignado en un estado bloqueante.
2. **Compromiso físico único:** cada recurso incorporado efectivamente a `RECURSO_CAMPUS` o `RECURSO_EXTERNO` queda comprometido desde `SOLICITADA` (o desde su creación en `APROBADA`). No puede incorporarse a otra solicitud mientras siga vigente el compromiso, aunque sus fechas sean distintas. Aplica a principales y adicionales, entre tipos y solicitantes, y no se elude asignándolo como complementario de espacio.

La fecha estimada de devolución no garantiza disponibilidad: puede existir retraso, daño, mantenimiento, pérdida u otra causa. Vencer el periodo no libera el compromiso. Cancelación o rechazo válidos antes de entrega permiten terminarlo sin devolución; si hubo entrega, se exige devolución y cierre único. Un retiro permitido antes de entrega conserva el historial; retirar una asignación entregada no la libera. Cada solicitud posterior revalida habilitación y operatividad; devolver un recurso dañado permite cerrar el préstamo, pero no reservarlo otra vez.

El estado vive en `reservas.reservas`; los periodos de negocio viven en los detalles. La proyección temporal en `reserva_recursos` permite excluir solapamientos, pero no representa por sí sola la exclusividad del compromiso desde la solicitud.

## Alternativas consideradas para la garantía temporal (decisión original)

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

## Decisión y revisión funcional

La propuesta selecciona la **alternativa A, restricción de exclusión**, por ser la única que cumple literalmente `spec.md`: la garantía quedaría en la base y no dependería de que el backend recuerde aplicarla. Aprobada 2026-09-23 con la decisión DB-11: ante la contradicción con el modelo, rige el ADR —la entrega física abre el rango— y se corrige el modelo.

La validación en la aplicación **se conserva**. Produce `409 SOLAPAMIENTO` ante incompatibilidad temporal y `409 CONFLICTO` ante compromiso físico vigente, con mensajes útiles. La restricción es la última línea, para el caso en que dos transacciones pasen la validación a la vez.

### Revisión del 2026-09-24 — un solo compromiso físico vigente

La decisión original de abrir el rango al entregar se conserva como antecedente y componente temporal, pero es insuficiente para el comportamiento aprobado del hallazgo 1. A para el 1–3 de octubre ya impide crear B para el 5–6 desde que A incorpora el recurso, antes de cualquier entrega. B no se crea en `SOLICITADA` para esperar su liberación. Se retira `RN-APR-09` de reservations, que presuponía esa solicitud posterior.

La base debe garantizar un único compromiso físico vigente por `recurso_id`, con independencia del periodo, del tipo de préstamo y del rol principal/adicional. El mecanismo concreto requiere diseño y una tarea de migración nueva: no se afirma que baste un índice sobre las columnas actuales. Debe coordinarse con las asignaciones temporales de complementarios de espacio, sin cambiar su planificación por franjas ni permitir eludir un compromiso físico. También debe impedir liberar compromisos con entregas abiertas mediante cambios de estado o asignación. No se implementa DDL en esta revisión documental.

Reprogramar, aprobar o entregar la misma reserva conserva su compromiso y lo excluye de la comparación. Una nueva solicitud solo puede admitirse tras la terminación válida del compromiso anterior y la verificación vigente de habilitación y operatividad. Registrar devolución y cierre no restablece esas condiciones ni aprueba otra solicitud automáticamente.

### Estructura temporal original — insuficiente para el compromiso único



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

- Para una reserva `SOLICITADA` o `APROBADA`, derivar el periodo solicitado del detalle: intervalo horario para `RECURSO_INTERNO` y días completos desde `fecha_salida` hasta el inicio del día siguiente a `fecha_devolucion_estimada` para `RECURSO_CAMPUS` y `RECURSO_EXTERNO`. La conversión a `tstzrange` debe usar una zona horaria operativa explícita y uniforme, no la zona implícita de cada conexión.
- Solo para campus y externo, al pasar a `EN_EJECUCION`, mantener ocupados los recursos entregados hasta el cierre único de la reserva. La finalización registra la devolución de todos los recursos entregados en la misma operación; entonces se actualizan sus rangos efectivos y termina el compromiso. Su elegibilidad posterior requiere comprobar habilitación y operatividad.
- Dejar `periodo` como **NULL SQL** cuando no exista un periodo aplicable o falte un extremo necesario para definirlo. La ausencia de fecha no se representa pasando límites NULL a `tstzrange`, porque eso construiría un rango sin límite. Una ejecución abierta sin devolución es un caso distinto: tiene inicio y un rango intencionalmente abierto, no un periodo ausente.
- Recalcular la proyección cuando se inserte o modifique el detalle por tipo, la asociación o `estado_asignacion`, el estado de la reserva, o el registro de entrega/devolución. La actualización ocurre en la misma transacción.

`bloqueante` es una proyección técnica, no un dato editable desde la aplicación. En espacios refleja que la reserva está en estado bloqueante; en recursos requiere además `estado_asignacion = 'ASIGNADO'`. Se inicializa en `false` y se sincroniza al insertar o cambiar una reserva o asignación. `periodo IS NOT NULL` también forma parte del predicado de exclusión. La restricción solo indexa filas que satisfacen ambas condiciones.

El rango temporal es semiabierto `[)`: dos franjas que se tocan a las 12:00 no se solapan. Esto no permite dos compromisos físicos simultáneamente vigentes con fechas contiguas. Un extremo superior sin límite se usa exclusivamente mientras un recurso entregado sigue sin devolución registrada; no equivale a `NULL` SQL.

### Alcance de las proyecciones temporales

`periodo` y `bloqueante` protegen los intervalos de las asignaciones efectivas. Un rango abierto durante una entrega impide solapamientos futuros, pero no impide dos solicitudes con periodos distintos antes de entregar. Por eso la estructura temporal anterior necesita la garantía adicional de compromiso único desde la incorporación. La base debe verificar ambas condiciones en la misma transacción.

El registro de devolución física se conserva en `reserva_ejecucion_recursos.devuelto_at`. En reservas que requieren devolución, esos valores se registran conjuntamente al cierre: la finalización global y la devolución de todos los recursos entregados ocurren en la misma operación.

### Lista de espera

`LISTA_ESPERA` no crea filas en `reserva_recursos` ni tiene espacio (`RN-TIP-PLE-01`); por tanto, no crea rangos ni bloquea recursos. Si una reserva obtiene un periodo posteriormente, la asignación se sincroniza y valida dentro de la misma transacción antes de confirmar el cambio.

## Consecuencias

**A favor, una vez implementadas ambas garantías:**

- La exclusión temporal y el compromiso físico único se protegen en base de datos, sin depender de que la aplicación recuerde hacer una consulta previa.
- El índice GiST que crea la restricción sirve además para las consultas de disponibilidad por elemento y periodo.
- Los periodos ausentes se representan mediante NULL SQL y quedan fuera del índice; una ejecución abierta se representa con un límite superior sin acotar mientras el recurso siga sin devolución.

**En contra, y hay que asumirlo:**

- Requiere `btree_gist`, una extensión estándar pero que debe existir en el entorno de despliegue.
- Introduce las columnas técnicas `periodo` y `bloqueante` en las tablas de asignación, además de disparadores para mantenerlas. Son proyecciones derivadas: si no se sincronizan correctamente desde todos los cambios de estado, asociación, detalle y ejecución, la restricción puede proteger de menos o de más. Deben inicializarse y probarse antes de habilitar las restricciones.
- La violación llega al backend como un error de restricción de PostgreSQL, que hay que traducir a `409 SOLAPAMIENTO` si es temporal o `409 CONFLICTO` si afecta al compromiso físico, sin exponer SQL ni devolver un `500`.
- La exclusividad temporal de espacios y recursos vive en tablas distintas. A esas exclusiones debe añadirse la garantía de compromiso físico único; no se presupone que las dos restricciones temporales basten.

## Verificación

La decisión se considera implementada cuando existan pruebas de integridad contra la base y pruebas de contrato para traducir sus errores. Incluyen transacciones concurrentes con periodos solapados y, para préstamos, también distintos:

1. exactamente una de las dos confirma y la otra falla;
2. el contrato traduce el fallo temporal a `409 SOLAPAMIENTO` y el compromiso físico incompatible a `409 CONFLICTO`, sin error interno;
3. una solicitud sin periodo ni asignación efectiva, como lista de espera, no bloquea recursos;
4. cancelar o rechazar válidamente antes de entrega libera la asignación y el compromiso; no habilita ni declara operativo el recurso;
5. los recursos entregados siguen bloqueados hasta el cierre único que registra la devolución de todos ellos;
6. una asociación temporal `NO_DISPONIBLE` o retirada válidamente no bloquea; no se permite retirar una asignación entregada para eludir la devolución;
7. dos reservas de espacio o complementarios sin préstamo que se tocan en un extremo no se consideran solapadas;
8. dos solicitudes concurrentes de préstamo del mismo recurso con periodos distintos no pueden confirmar ambas, incluso entre tipos diferentes;
9. el compromiso empieza en `SOLICITADA`, se conserva en aprobación, reprogramación y entrega, y no se libera al vencer la fecha estimada;
10. una nueva incorporación, incluso como complementario de espacio, no elude un compromiso físico vigente;
11. cancelar o rechazar válidamente antes de entregar permite terminar el compromiso sin devolución; retirar o cambiar el estado de una asignación entregada no lo libera;
12. la devolución permite cerrar un préstamo de un recurso dañado, pero una nueva solicitud se rechaza hasta recuperar habilitación y operatividad;
13. la concurrencia entre incorporación, entrega y liberación no deja dos compromisos ni una entrega abierta sin protección. La convivencia de préstamos y franjas se verifica en ambos órdenes de creación.

Mientras esas pruebas no existan, `architecture.md` §10 y el contrato de reservations siguen describiendo un requisito, no una garantía satisfecha.

## Corrección de alcance — hallazgo 4

`RECURSO_INTERNO` no es un préstamo con entrega/devolución física: mantiene un periodo horario acotado también en `EN_EJECUCION`, admite franjas no solapadas y no abre rangos físicos. La exclusividad del hallazgo 1 y el retiro de complementarios de `RN-TIP-PE-28` de reservations corresponden solo a campus y externo. El inicio y fin automáticos de interno no crean registros de entrega/devolución. Las restricciones temporales deben proteger sus franjas independientemente de la puntualidad del proceso automático.

## Pendiente de esta decisión

El diseño temporal original se conserva, pero el mecanismo adicional de compromiso físico único y su coordinación con asignaciones por franjas requieren diseño y migración nuevos antes de implementar. La zona horaria operativa es `America/Bogota` (DB-11). Faltan instalar y verificar todas las restricciones y disparadores, inicializar las proyecciones y ejecutar las pruebas ampliadas contra una base aislada. Ningún fragmento SQL anterior acredita por sí solo la decisión del 2026-09-24.

### Caso mixto — decisión final del 2026-09-24

Los complementarios de `ESPACIO` no constituyen compromisos físicos exclusivos. Al establecer un préstamo (creación o incorporación permitida), se retiran automáticamente las asignaciones complementarias efectivas del recurso en espacios `SOLICITADA` o `APROBADA`, sin cancelar el espacio ni alterar su franja o demás recursos. Si alguna está `EN_EJECUCION`, se rechaza la operación completa con `409 CONFLICTO`, sin retiros parciales (`RN-TIP-PE-28` de reservations). Los periodos distintos no exceptúan estas condiciones y las asignaciones de reservas terminadas permanecen históricas.

El compromiso, todos los retiros y su trazabilidad se confirman atómicamente. Se conserva la fila original, instante de retiro, causa `PRESTAMO_FISICO` y referencia a la reserva causante, conforme al modelo objetivo de reservations; su persistencia todavía requiere migración. No se generan entregas físicas para espacios. Cancelar el préstamo no restaura complementarios; una reincorporación permitida exige revalidar y conservar la fila retirada.

La integridad debe coordinar la exclusión temporal con el retiro previo de las asignaciones afectadas y la exclusividad entre préstamos. También protege la carrera con el inicio automático del espacio: si este inicia primero, se rechaza el préstamo; si el préstamo retira primero el complementario, el espacio inicia con su composición vigente. El caso mixto queda cerrado funcionalmente; permanece pendiente el diseño e implementación de las restricciones y de la trazabilidad objetivo.

Pruebas adicionales requeridas: retiro en ambos estados permitidos; rechazo en ejecución; rollback del conjunto ante fallo; preservación de la reserva de espacio y del historial; causa y reserva causante persistidas; ausencia de restauración al cancelar; concurrencia con inicio del espacio e incorporación de complementarios.
