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

**Impacto.** Determina la validación de `reserva_campos_valores` y el formulario de reserva. Afecta a `RN-ESP-CAM-02` y `RN-TIP-PE-18`.

**Estado.** Abierta.

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

**Impacto.** Afecta a `RN-CNT` y a la conservación histórica de `RN-HIS-03` de notifications. También queda por fijar qué eventos admiten una sola notificación por reserva, que es lo que sostiene la restricción única de la tabla.

**Estado.** Abierta.

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

**Impacto.** Afecta la migración del inventario y la lista de diferencias pendientes del modelo de reservations. Mientras no se decida, el catálogo queda sin propietario en el diseño objetivo.

**Estado.** Abierta.

---

## OQ-08 — Superficie de administration, notifications, reports y researchs

**Contexto.** Esos cuatro módulos suman 191 reglas y solo 2 flujos de usuario. Los contratos de auth, reservations, espacios, usuarios y resources se derivaron de sus flujos; para estos cuatro no hay de dónde derivar, y redactar su contrato exigiría inventar la superficie en lugar de traducirla.

**Alternativas.** Escribir primero su `user-flow.md` y derivar después, frente a derivar el contrato directamente de las reglas asumiendo el riesgo de inventar endpoints que nadie pidió.

**Impacto.** Sin contrato, esos módulos no son implementables por un equipo distinto al que escribió sus reglas. Afecta especialmente a notifications, del que ya dependen reservations (recordatorios y confirmaciones) y auth (invitaciones y recuperación).

**Estado.** Abierta. Decidido en su momento posponerlos; el orden sugerido por dependencia es notifications, administration, reports y researchs.

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

**Impacto.** Sin ella no puede implementarse la validación del paso 3 de `UF-ADM-04` ni determinarse qué datos del equipo actualiza una reimportación. Afecta a `RN-IMP-02` de administration y a `RN-IMP-02` de resources.

**Estado.** Abierta.

---

## OQ-11 — Tratamiento de una importación con filas en error

**Contexto.** `RN-IMP-06` de administration exige que una importación con errores no deje cambios parciales y que el Administrador revise el resultado antes de confirmar. No queda claro si eso significa que la carga completa se rechaza cuando alguna fila falla, o que la escritura es atómica y las filas válidas sí se confirman. La redacción anterior de `RN-IMP-03` de resources afirmaba lo segundo para equipos, lo que contradecía la primera lectura; esa afirmación se retiró y la decisión quedó centralizada aquí.

**Alternativas.** Rechazo total cuando exista al menos una fila en error, frente a confirmación de las filas válidas reportando las erróneas.

**Impacto.** Determina el paso 6 de `UF-ADM-01` y de `UF-ADM-04`, el significado de los totales de `administration.importaciones` y si una carga confirmada puede convivir con filas `ERROR` en `importacion_resultados`. Afecta a `RN-IMP-06` de administration y a `RN-IMP-03` de resources.

**Estado.** Abierta.

---

## OQ-12 — Desactivación de equipos por importación

**Contexto.** `RN-IMP-09` de administration permite desactivar un proyecto o semillero incluyéndolo con estado `INACTIVO`, y `administration.importaciones` cuenta `registros_desactivados`. Resources no define si la planilla de equipos puede deshabilitar un equipo, y hacerlo tendría el efecto de `RN-DES-03`: afectar reservas futuras que dependan de él.

**Alternativas.** Admitir la desactivación masiva con la advertencia y confirmación que exige `RN-DES-06`, frente a restringir la importación a altas y actualizaciones y dejar la desactivación al flujo individual.

**Impacto.** Una desactivación masiva silenciosa podría cancelar reservas futuras sin la confirmación explícita que `RN-DES-06` exige. Afecta a `RN-IMP-07` y `RN-IMP-09` de administration, a `RN-DES-03` y `RN-DES-06` de resources, y al contador `registros_desactivados`.

**Estado.** Abierta.
