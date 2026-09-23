# Preguntas abiertas

Este documento registra ambigüedades, decisiones pendientes y comportamientos que todavía no tienen una regla de negocio confirmada.

Cada pregunta incluye contexto, alternativas consideradas, impacto y, cuando se resuelva, la decisión y su fecha. Una pregunta resuelta se conserva con su decisión, no se borra.

---

## OQ-01 — Catálogo de permisos administrativos

**Contexto.** `auth.permisos` y `auth.cuenta_permisos` están definidos, pero no la lista de códigos concretos: qué operaciones administrativas se controlan y con qué granularidad.

**Alternativas.** Un permiso por operación, frente a permisos agrupados por área funcional.

**Impacto.** Bloquea la implementación de `exigir_permiso` del contrato de auth y la administración de asignaciones. Afecta a `RN-PER-01`, `RN-PER-03` de administration y `SEC-AUTZ-04`.

**Estado.** Resuelta. Se adopta un código por área funcional distinguiendo el verbo solo donde hay un caso real de separarlo; el catálogo inicial de catorce códigos está en [auth/data-model.md](../../modules/auth/data-model.md#authpermisos) y los contratos ya citan el código que exige cada operación. La granularidad responde a que la asignación es directa y sin roles: dar de alta a un Técnico son cinco asignaciones, no una por endpoint.

---

## OQ-02 — Tipos admitidos en los campos adicionales de espacios

**Contexto.** `reservas.espacio_campos.tipo` acepta un catálogo de tipos que incluye `SELECCION`, pero el resto no está definido: texto, número, fecha u otros.

**Alternativas.** Un conjunto cerrado y pequeño, frente a un catálogo extensible por configuración.

**Decisión.** Resuelta el 23 de septiembre de 2026: **conjunto cerrado de cinco tipos** —`TEXTO`, `TEXTO_LARGO`, `NUMERO`, `BOOLEANO` y `SELECCION`—, que es el que el modelo ya contemplaba y el contrato de espacios ya publicaba. Se descartó el catálogo ampliable porque cada tipo nuevo necesita su propia validación y su forma de presentarse en el formulario, de modo que añadirlo por configuración no evitaría tocar el código.

**Impacto.** `RN-ESP-CAM-02` enumera los cinco y declara el catálogo cerrado; el CHECK sobre `espacio_campos.tipo_campo` lo garantiza. Añadir un tipo exige modificar la regla, el CHECK y la validación del formulario.

**Estado.** Resuelta.

---

## OQ-03 — Contacto del responsable en FGL 030

**Contexto.** La concatenación de correo y teléfono en un único campo podía truncar valores válidos.

**Decisión.** Resuelta. La orden conserva `responsable_correo_snapshot` y `responsable_telefono_snapshot` como campos independientes, cada uno con la longitud de su fuente.

**Impacto.** Afecta el prellenado exigido por `RN-TIP-RC-13` y `RN-TIP-RE-13`.

**Estado.** Resuelta.

---

## OQ-04 — Contenido de las notificaciones por tipo de evento

**Contexto.** `notificaciones.notificaciones` guarda `titulo` y `cuerpo` como contenido histórico, pero no está definido qué texto corresponde a cada uno de los once eventos de `RN-EVT`.

**Alternativas.** Plantillas por evento en configuración, frente a texto construido en código.

**Decisión.** Resuelta el 23 de septiembre de 2026: **el texto vive en el código**, no en un catálogo de plantillas administrable. Queda en `RN-CNT-06` de notifications. Cambiar una redacción es un cambio de código y un despliegue; a cambio, no hay que construir una pantalla de administración de plantillas ni decidir quién puede editarlas.

La conservación histórica no depende de esta decisión: `titulo` y `cuerpo` guardan el texto tal como se comunicó, así que una redacción nueva nunca reinterpreta una notificación ya generada.

**La segunda parte de esta pregunta no requería decisión.** Qué eventos admiten una sola notificación por reserva ya lo resuelve `RN-NOT-05`: la unicidad se determina por la clave de ocurrencia que define el proceso que origina el evento, no por el tipo de evento ni por la reserva. Es esa clave la que sostiene la restricción única de `notificaciones.eventos`, y `UF-RES-16` la usa para impedir un segundo recordatorio.

**Impacto.** Afecta a `RN-CNT` y al modelo de notificaciones, que deja de declarar el contenido como pendiente.

**Estado.** Resuelta.

---

## OQ-05 — Configuración global genérica

**Contexto.** Se había planteado `RN-CFG` sin identificar una configuración global concreta ni un propietario funcional.

**Decisión.** Resuelta. La configuración global genérica queda fuera de alcance: se elimina `RN-CFG` y no se crea una tabla ni otro mecanismo genérico. Cada configuración necesaria debe definirse en su módulo propietario antes de incorporarse.

**Impacto.** No existe una configuración global que diseñar o administrar en esta iteración.

**Estado.** Resuelta.

---

## OQ-06 — Mecanismo transaccional contra doble reserva

**Contexto.** El modelo exige impedir que dos solicitudes concurrentes ocupen el mismo espacio o recurso en periodos incompatibles. Esta pregunta se abrió antes de seleccionar la restricción de exclusión documentada en ADR-001.

**Alternativas.** Restricción de exclusión de PostgreSQL sobre rangos, bloqueo pesimista por elemento, o serialización de la transacción.

**Impacto.** Es la garantía central de integridad del dominio. Los índices ordinarios y una consulta previa no la sustituyen. La selección del mecanismo debe formalizarse mediante un ADR conforme a `architecture.md` §17. La especificación de producto ya acota la decisión: exige la garantía **a nivel de base de datos, no solo de aplicación**, por lo que un bloqueo resuelto únicamente en el backend no satisface el requisito. ADR-001 selecciona una restricción de exclusión de PostgreSQL a nivel de diseño; queda pendiente su aprobación formal, no elegir otra alternativa.

**Estado.** Resuelta a nivel de diseño por [ADR-001](adr-001-doble-reserva.md), que selecciona como propuesta el uso de restricciones de exclusión de PostgreSQL con periodos y predicados de bloqueo sincronizados en base de datos. La aprobación formal, la implementación y las pruebas de concurrencia siguen pendientes; hasta completarlas, la funcionalidad [001 — Crear una reserva](../../features/001-create-reservation/spec.md) no puede darse por correcta bajo concurrencia.

---

## OQ-07 — Destino de `motivos_solicitud`

**Contexto.** `reservas.motivos_solicitud` existe en el inventario y `reservas.reservas.motivo_solicitud_id` lo referencia, pero el diseño objetivo no lo contempla: el "por qué" de una reserva pasó a resolverse con el contexto de `RN-CTX`.

**Alternativas.** Retirarlo por quedar superado por el contexto, frente a conservarlo como catálogo complementario e independiente del contexto académico.

**Decisión.** Resuelta el 23 de septiembre de 2026: **se retira**, junto con la columna `reservas.reservas.motivo_solicitud_id` que lo referencia.

El porqué de una reserva ya tiene dos respuestas en el diseño objetivo, y ninguna es este catálogo: `reserva_contexto` registra el proyecto, semillero, pasantía, trabajo de grado o actividad institucional que la justifica, y `reserva_datos_salida.razon_solicitud` captura, de forma obligatoria para `RECURSO_CAMPUS` y `RECURSO_EXTERNO`, por qué sale el equipo del campus. Además, «sacar un equipo fuera del laboratorio» no es un motivo sino un tipo de reserva. Conservar el catálogo habría dejado dos lugares respondiendo la misma pregunta.

La columna siempre admitió NULL, así que ni siquiera en la base actual era obligatoria y ninguna reserva depende de su valor.

**Impacto.** Afecta la migración del inventario y la lista de diferencias pendientes del modelo de reservations, que ahora indica retirarlos en lugar de decidir su destino.

**Estado.** Resuelta.

---

## OQ-08 — Superficie de administration, notifications, reports y researchs

**Contexto.** Esos cuatro módulos suman 191 reglas y solo 2 flujos de usuario. Los contratos de auth, reservations, espacios, usuarios y resources se derivaron de sus flujos; para estos cuatro no hay de dónde derivar, y redactar su contrato exigiría inventar la superficie en lugar de traducirla.

**Alternativas.** Escribir primero su `user-flow.md` y derivar después, frente a derivar el contrato directamente de las reglas asumiendo el riesgo de inventar endpoints que nadie pidió.

**Impacto.** Sin contrato, esos módulos no son implementables por un equipo distinto al que escribió sus reglas. Afecta especialmente a notifications, del que ya dependen reservations (recordatorios y confirmaciones) y auth (invitaciones y recuperación).

**Estado.** Abierta, pero el bloqueo original quedó levantado y **notifications ya está escrito**. Los cuatro módulos tienen flujos de usuario de los que derivar su superficie: `UF-ADM-01` a `UF-ADM-04` en administration, `UF-INV-01` en researchs, `UF-NOT-01` a `UF-NOT-03` en notifications y `UF-REP-01` y `UF-REP-02` en reports.

El [contrato de notifications](../../contratos/notifications/api-contract.md) se escribió primero por dependencia: reservations y auth ya lo citaban para recordatorios, confirmaciones, invitaciones y recuperación de contraseña. Expone la bandeja del destinatario y sus preferencias de correo; la generación y la entrega no tienen superficie HTTP. Quedan `administration`, `reports` y `researchs`.

---

## OQ-09 — Derivación del periodo de uso de un recurso

**Contexto.** `reserva_recursos` no contiene fechas de inicio o fin; el periodo de negocio reside en el detalle de cada tipo. Una columna generada en la tabla de asociación no puede leer esas tablas ni representar por sí sola el periodo de una ejecución cuyo recurso aún no se ha devuelto.

**Alternativas.** Copiar fechas de inicio y fin como datos de negocio, frente a mantener una sola proyección técnica del rango desde los detalles y el registro de ejecución.

**Impacto.** La restricción de exclusión requiere comparar el periodo del recurso junto con su asignación en la misma tabla, y debe conservar la indisponibilidad de un recurso en ejecución hasta registrar la devolución física.

**Estado.** Resuelta a nivel de diseño por la propuesta de [ADR-001](adr-001-doble-reserva.md): el periodo se mantiene como rango técnico en `reserva_recursos`, sincronizado transaccionalmente desde el detalle del tipo y `reserva_ejecucion_recursos.devuelto_at`; un recurso en ejecución sin devolución tiene rango superior abierto. La aprobación formal, la migración, los disparadores y las pruebas siguen pendientes.

---

## OQ-10 — Columnas de la planilla de importación de equipos

**Contexto.** `RN-IMP-02` de administration fija las columnas `codigo`, `nombre` y `estado` para los catálogos de investigación. Esas columnas no aplican al equipo, cuya identidad es la placa (`RN-IMP-02` de resources), y no existe un conjunto de columnas aprobado para la planilla de equipos. `UF-ADM-04` describe la carga sin presuponerlas.

**Alternativas.** Reutilizar la estructura de los catálogos de investigación sustituyendo `codigo` por `placa`, frente a definir una planilla propia con los datos especializados que `UF-REC-03` exige al registrar un equipo.

**Decisión.** Resuelta el 23 de septiembre de 2026 a partir de la planilla real que se usa hoy, en lugar de diseñar un formato nuevo. Son seis columnas: `PLACA`, `DESCRIPCIÓN`, `CODIGO BODEGA`, `CENTRO DE COSTOS`, `FECHA INICIO` y `COSTO`. Quedan en `RN-IMP-11` de administration, con su correspondencia persistente en `RN-IMP-06` de resources.

Tres consecuencias de esa planilla real:

- **`COSTO` no se conserva.** Es un dato contable del inventario institucional y ninguna regla de reservas lo necesita. Se lee y se descarta, sin error.
- **No trae unidad organizacional.** El Administrador la selecciona al iniciar la carga y se aplica solo a los equipos que la carga cree (`RN-IMP-12`). Importar varias unidades exige una carga por unidad.
- **`DESCRIPCIÓN` alimenta `nombre_equipo`**, que se amplió de `varchar(50)` a `varchar(100)`. Las descripciones reales siguen el patrón «tipo, marca, modelo y capacidad» y desbordaban el ancho anterior; con el rechazo total de `OQ-11`, una sola descripción larga habría frenado la carga entera.

**Impacto.** Afecta a `RN-IMP-11` y `RN-IMP-12` de administration, `RN-IMP-06` de resources, `UF-ADM-04` y `recursos.equipos.nombre_equipo`.

**Estado.** Resuelta.

---

## OQ-11 — Tratamiento de una importación con filas en error

**Contexto.** `RN-IMP-06` de administration exige que una importación con errores no deje cambios parciales y que el Administrador revise el resultado antes de confirmar. No queda claro si eso significa que la carga completa se rechaza cuando alguna fila falla, o que la escritura es atómica y las filas válidas sí se confirman. La redacción anterior de `RN-IMP-03` de resources afirmaba lo segundo para equipos, lo que contradecía la primera lectura; esa afirmación se retiró y la decisión quedó centralizada aquí.

**Alternativas.** Rechazo total cuando exista al menos una fila en error, frente a confirmación de las filas válidas reportando las erróneas.

**Decisión.** Resuelta el 23 de septiembre de 2026: **rechazo total**. Una carga con al menos una fila en error no se confirma en ninguna de sus filas. El Administrador corrige el archivo y vuelve a cargarlo. No existe confirmación parcial.

El resultado por fila se conserva igualmente, para que el Administrador sepa exactamente qué corregir sin volver a procesar el archivo. Así, una importación confirmada nunca convive con filas `ERROR`: sus totales describen una carga íntegra.

**Impacto.** Fija el paso de confirmación de `UF-ADM-01` y `UF-ADM-04`. `RN-IMP-06` de administration quedó redactada sin ambigüedad y `RN-IMP-03` de resources se alineó con ella, retirando la afirmación contraria que la originó.

**Estado.** Resuelta.

---

## OQ-12 — Desactivación de equipos por importación

**Contexto.** `RN-IMP-09` de administration permite desactivar un proyecto o semillero incluyéndolo con estado `INACTIVO`, y `administration.importaciones` cuenta `registros_desactivados`. Resources no define si la planilla de equipos puede deshabilitar un equipo, y hacerlo tendría el efecto de `RN-DES-03`: afectar reservas futuras que dependan de él.

**Alternativas.** Admitir la desactivación masiva con la advertencia y confirmación que exige `RN-DES-06`, frente a restringir la importación a altas y actualizaciones y dejar la desactivación al flujo individual.

**Decisión.** Resuelta el 23 de septiembre de 2026: **la importación de equipos no deshabilita**. Solo crea y actualiza por placa.

La planilla real de `OQ-10` no tiene columna de estado, así que no puede expresar una baja. Y aunque la tuviera, una desactivación masiva cancelaría reservas futuras sin la confirmación explícita que `RN-DES-06` exige antes de cada cancelación. Deshabilitar un equipo sigue siendo una acción individual.

**Impacto.** `RN-IMP-07` y `RN-IMP-09` de administration y `RN-IMP-07` de resources lo declaran. El contador de registros desactivados de una carga de `EQUIPOS` es siempre cero.

**Estado.** Resuelta.

---

## OQ-13 — Entrada de una reserva por espacio al estado `EN_EJECUCION`

**Contexto.** `RN-TIP-PE-25` y `UF-RES-21` documentan la salida de una reserva por espacio: alcanza `hora_fin` y pasa a `FINALIZADA`. La entrada a `EN_EJECUCION` nunca se definió. `RN-TIP-PE-21` y `RN-TIP-PE-23` presuponen que una reserva por espacio puede encontrarse en ese estado, y `UF-RES-13` no la excluye, pero su contrapartida en el contrato describe la operación como el registro de una entrega física, que en una reserva por espacio no existe.

**Alternativas.** Transición automática al alcanzar `hora_inicio`, registro manual por el Técnico al abrir el espacio, o que `ESPACIO` nunca pase por `EN_EJECUCION` y transite de `APROBADA` directamente a `FINALIZADA`.

**Decisión.** Resuelta el 23 de septiembre de 2026: **transición automática al alcanzar `hora_inicio`**, simétrica con la finalización. Queda en `RN-TIP-PE-27` y `UF-RES-22`.

Se descartó que el Técnico la marcara, porque una reserva por espacio no tiene entrega física que registrar y, si se olvidara de marcarla, la reserva saltaría de `APROBADA` a `FINALIZADA` sin pasar por el estado que `RN-TIP-PE-21` y `RN-TIP-PE-23` necesitan para agregar recursos en curso. Se descartó eliminar el estado por la misma razón: habría obligado a reescribir esas dos reglas.

Solo transita una reserva `APROBADA`; una `SOLICITADA` que llega a su hora de inicio permanece como está. `EN_EJECUCION` significa aquí que la franja está en curso, no que el Usuario se haya presentado: el sistema no registra asistencia.

**Impacto.** `UF-RES-13` y `POST /api/reservas/{id}/ejecucion` excluyen el tipo `ESPACIO`. No afecta la disponibilidad, que se evalúa por intervalo conforme a `RN-DIS-11`.

**Estado.** Resuelta.

---

## OQ-14 — Tipos de adjunto admitidos en una reserva

**Contexto.** `reservas.reserva_adjuntos.tipo_adjunto` clasifica el archivo que el Usuario carga con su requerimiento, pero no existe un catálogo aprobado de valores. La única fuente es [spec.md](../spec.md), que menciona «un archivo CAD, imagen u otro archivo técnico» sin cerrar la lista, y `UF-RES-05`, que la repite. Por eso la columna se documentó sin `CHECK`.

**Alternativas.** Un catálogo cerrado en `CHECK` o en una tabla de tipos, frente a dejar la clasificación abierta y validar únicamente `content_type` y tamaño.

**Decisión.** Resuelta el 23 de septiembre de 2026: **planos, imágenes y PDF**. `tipo_adjunto` admite `PLANO` (DWG, DXF, STEP, STL), `IMAGEN` (PNG, JPG) y `DOCUMENTO` (PDF), y cada uno acota los tipos MIME válidos en `content_type`.

Se descartó admitir cualquier archivo salvo ejecutables, porque el Técnico debe poder abrir el adjunto para evaluar el requerimiento. Y se descartó limitarlo a PDF e imagen, porque obligaría al Usuario a exportar su plano y el Técnico perdería el archivo CAD original, que es justamente el que necesita para valorar la pieza.

**Impacto.** `reservas.reserva_adjuntos.tipo_adjunto` lleva CHECK sobre los tres valores, y el backend valida que el contenido corresponda al tipo declarado en lugar de confiar en la extensión. El límite de 5 MB no cambia.

**Estado.** Resuelta.

---

## OQ-15 — Mecanismo que ejecuta la entrega y el reintento de correo

**Contexto.** `RN-COR-03` fija la política de reintento —hasta cinco intentos con espera de 1, 5, 15, 60 y 240 minutos— y `notificaciones.envios_correo` la soporta con `intentos`, `proximo_intento_at` y un índice `(estado, proximo_intento_at)` descrito como «para el proceso que reintenta». `UF-NOT-03` documenta la secuencia, pero ninguna decisión aprobada nombra el mecanismo que la ejecuta.

**Alternativas.** Una tarea programada que consulta periódicamente los envíos vencidos, una cola de trabajos con reintento propio, o un worker dedicado. La elección afecta a quién pertenece el control del reintento: si lo lleva la cola, `intentos` y `proximo_intento_at` pasan a ser un reflejo y no la fuente.

**Decisión.** Resuelta el 23 de septiembre de 2026: **una tarea programada del propio sistema**, no una cola de trabajos externa.

La consecuencia importante es de propiedad, no de tecnología: la política de reintento de `RN-COR-03` permanece en este dominio. `intentos` y `proximo_intento_at` de `notificaciones.envios_correo` son la fuente de verdad y no el reflejo de lo que decida una infraestructura ajena. Si la tarea se retrasa o se detiene, los envíos permanecen en `PENDIENTE` con su reintento vencido y siguen siendo visibles en esa tabla; no se pierde ninguno.

La tarea debe ejecutarse con una frecuencia menor que la espera más corta de la política, que es de un minuto.

**Impacto.** `UF-NOT-03` documenta el mecanismo y el modelo de notificaciones explica para qué sirve el índice `(estado, proximo_intento_at)`. Al no delegarse a infraestructura, la decisión no requiere un ADR propio.

**Estado.** Resuelta.
