# Preguntas abiertas

Este documento registra ambigüedades, decisiones pendientes y comportamientos que todavía no tienen una regla de negocio confirmada.

Cada pregunta incluye contexto, alternativas consideradas, impacto y, cuando se resuelva, la decisión y su fecha. Una pregunta resuelta se conserva con su decisión, no se borra.

---

## OQ-01 — Catálogo de permisos administrativos

**Contexto.** `auth.permisos` y `auth.cuenta_permisos` están definidos, pero no la lista de códigos concretos: qué operaciones administrativas se controlan y con qué granularidad.

**Alternativas.** Un permiso por operación, frente a permisos agrupados por área funcional.

**Impacto.** Bloquea la implementación de `exigir_permiso` del contrato de auth y la administración de asignaciones. Afecta a `RN-PER-01`, `RN-PER-03` de administration y `SEC-AUTZ-04`.

**Estado.** Abierta. Conviene resolverla al implementar el primer módulo administrativo, no en abstracto.

---

## OQ-02 — Tipos admitidos en los campos adicionales de espacios

**Contexto.** `reservas.espacio_campos.tipo` acepta un catálogo de tipos que incluye `SELECCION`, pero el resto no está definido: texto, número, fecha u otros.

**Alternativas.** Un conjunto cerrado y pequeño, frente a un catálogo extensible por configuración.

**Impacto.** Determina la validación de `reserva_campos_valores` y el formulario de reserva. Afecta a `RN-ESP-CAM-02` y `RN-TIP-PE-18`.

**Estado.** Abierta.

---

## OQ-03 — Composición de la línea de contacto del FGL 030

**Contexto.** El formato físico imprime una sola línea de contacto que contempla ubicación, correo electrónico, teléfono y celular. El perfil almacena `correo` y `telefono` por separado, y no registra ubicación ni celular como campos distintos.

**Alternativas.** Concatenar correo y teléfono en `responsable_contacto_snapshot`, frente a ampliar el perfil con los datos que faltan.

**Impacto.** Afecta el prellenado exigido por `RN-TIP-RC-13` y `RN-TIP-RE-13`.

**Estado.** Abierta.

---

## OQ-04 — Contenido de las notificaciones por tipo de evento

**Contexto.** `notificaciones.notificaciones` guarda `titulo` y `cuerpo` como contenido histórico, pero no está definido qué texto corresponde a cada uno de los once eventos de `RN-EVT`.

**Alternativas.** Plantillas por evento en configuración, frente a texto construido en código.

**Impacto.** Afecta a `RN-CNT` y a la conservación histórica de `RN-HIS-03` de notifications. También queda por fijar qué eventos admiten una sola notificación por reserva, que es lo que sostiene la restricción única de la tabla.

**Estado.** Abierta.

---

## OQ-05 — Representación persistente de la configuración global

**Contexto.** `RN-CFG-02` exige que toda configuración cuente con representación persistente, pero el modelo no define una tabla de configuración global.

**Alternativas.** Tabla clave-valor tipada, frente a variables de entorno para lo que no cambia en caliente.

**Impacto.** Afecta a `RN-CFG-01` a `RN-CFG-07` y a cualquier parámetro que hoy se describe como configurable sin decir dónde vive.

**Estado.** Abierta.

---

## OQ-06 — Mecanismo transaccional contra doble reserva

**Contexto.** El modelo exige impedir que dos solicitudes concurrentes ocupen el mismo espacio o recurso en periodos incompatibles, pero el mecanismo concreto no está elegido.

**Alternativas.** Restricción de exclusión de PostgreSQL sobre rangos, bloqueo pesimista por elemento, o serialización de la transacción.

**Impacto.** Es la garantía central de integridad del dominio. Los índices ordinarios y una consulta previa no la sustituyen. Requiere un ADR conforme a `architecture.md` §17. La especificación de producto ya acota la decisión: exige la garantía **a nivel de base de datos, no solo de aplicación**, por lo que un bloqueo resuelto únicamente en el backend no satisface el requisito. Lo que queda por elegir es el mecanismo de PostgreSQL, no el nivel.

**Estado.** Abierta. Bloquea dar por correcta la funcionalidad [001 — Crear una reserva](../../features/001-create-reservation/spec.md) bajo concurrencia.

---

## OQ-07 — Destino de `motivos_solicitud`

**Contexto.** `reservas.motivos_solicitud` existe en el inventario y `reservas.reservas.motivo_solicitud_id` lo referencia, pero el diseño objetivo no lo contempla: el "por qué" de una reserva pasó a resolverse con el contexto de `RN-CTX`.

**Alternativas.** Retirarlo por quedar superado por el contexto, frente a conservarlo como catálogo complementario e independiente del contexto académico.

**Impacto.** Afecta la migración del inventario y la lista de diferencias pendientes del modelo de reservations. Mientras no se decida, el catálogo queda sin propietario en el diseño objetivo.

**Estado.** Abierta.
