# Revisión global — especificaciones y contratos

**Rama:** `feature/v0.1.1` · **Último commit revisado:** `1e652a5` · **Fecha:** 23 de septiembre de 2026

Esta revisión cierra los siete bloques de corrección ejecutados sobre `specs/`, añade el cotejo de los cinco contratos de API contra los modelos de datos, las reglas de negocio y los flujos de usuario, y recoge las correcciones ya aplicadas tras ese cotejo.

**Alcance verificado:** 51 documentos, 509 reglas de negocio, 80 flujos de usuario y 77 endpoints repartidos en 5 contratos.

---

## 1. Resumen

Las comprobaciones mecánicas salen limpias y las inconsistencias de contrato que no requerían decisión funcional ya están corregidas. Lo que queda son **dos asuntos que necesitan autorización**, **un cotejo pendiente** y **diez decisiones funcionales sin tomar**.

| Comprobación | Resultado |
|---|---|
| Enlaces y anclas rotas | **0** |
| Referencias de sección rotas dentro de los contratos | **0** |
| Tablas citadas sin definición en ningún modelo | **0** |
| Referencias a reglas o flujos inexistentes | **1**, y es una nota de retiro deliberada |
| Valores de enumeración usados en contratos sin respaldo | **0** |
| Permisos usados fuera del catálogo de `auth.permisos` | **0** |
| Códigos de error usados sin declarar | **0** |
| Endpoints `GET` que modifiquen estado | **0** |
| Flujos cubiertos por algún endpoint | **73 de 80** |

Los 7 flujos sin endpoint pertenecen a administration, notifications, reports y researchs —que todavía no tienen contrato— más `UF-RES-18`, que se trasladó a reports como `UF-REP-02`.

---

## 2. Correcciones completadas

### Bloque 1 — Identidad, autenticación y permisos (`3d09c23`)

Se retiraron 30 reglas duplicadas de `usuarios` (familias `RN-ID`, `RN-AUT`, `RN-AUTZ`, `RN-AUD`), sustituidas por remisiones a Auth y Administration. `RN-PER` de usuarios pasó a `RN-PRS` para no colisionar con los permisos de administration. Auth ganó 8 reglas, entre ellas `RN-AUTH-ROL-09`, que protege la última cuenta con permisos globales enumerando las cuatro vías por las que podría perderse.

### Bloque 2 — Perfiles académicos e investigativos (`4f6be6b`)

La familia `RN-PRF` de administration desapareció: los perfiles académicos pertenecen a researchs, que sumó `RN-INV-12` a `RN-INV-16`. `RN-PRF-03` se retiró en lugar de trasladarse, porque sus dos citas usaban «perfil» en el sentido de rol de cuenta y se redirigieron a `RN-AUTH-ROL-04`.

### Bloque 3 — Importaciones (`ae502d6`)

El modelo ya admitía el catálogo `EQUIPOS`, pero `RN-IMP-01` de administration lo excluía. Ahora administration orquesta las tres importaciones y `RN-IMP-10` delega en cada módulo propietario la identificación y las validaciones. Nuevo flujo `UF-ADM-04`.

### Bloque 4 — Finalización de reservas por espacio (`d2f0e98`)

`RN-TIP-PE-24` escondía la finalización automática dentro de una regla sobre recursos y afirmaba que esa transición «libera el espacio». Se separó en `RN-TIP-PE-25` y `RN-TIP-PE-26`, se añadió `RN-DIS-11` —el bloqueo pertenece al periodo, no al cambio de estado— y `RN-TIP-RI-13`, que excluye expresamente a `RECURSO_INTERNO` de la finalización por tiempo. Nuevo flujo de sistema `UF-RES-21`.

### Bloque 5 — Modelo de datos y nomenclatura (`4b141b9`)

Once apariciones de `espacios_campos` y `espacios_campos_opciones` pasaron a los nombres aprobados. `reserva_adjuntos` y `reserva_historial_estado` dejaron de estar en prosa y tienen tabla de campos completa. `personal.personal.estado` pasó de admitir `NULL` a `NOT NULL DEFAULT true`.

### Bloque 6 — Limpieza documental (`3eaa1cf`)

`UF-USR-04` declara el correo como no editable. `RN-ESP-HAB-03` se retiró por estar contenida en `RN-ESP-HAB-05`. Las cuatro preguntas locales de usuarios se cerraron nombrando la regla que resolvió cada una. Reports dejó de citar `control_cambios` como fuente.

### Bloque 7 — Flujos de notifications y reports (`f99013f`)

Cinco flujos nuevos en lugar de uno por familia de reglas: `UF-REP-01`, `UF-REP-02`, `UF-NOT-01`, `UF-NOT-02` y `UF-NOT-03`. No se crearon flujos de evento: los once eventos `RN-EVT` ya los produce otro módulo y se cerraron con una tabla de correspondencia.

### Reorganización de contratos (`1b8970f`)

Los cinco contratos comparten forma: abren con `## 1. Convenciones` y cierran con «Lo que este contrato no expone». `UNIDAD_INCOMPATIBLE`, que significaba dos cosas distintas en espacios y resources, subió al catálogo común con una sola definición. `TIPO_NO_ADMITIDO` quedó declarado donde ya se usaba y `TOKEN_NO_VIGENTE` dejó de estar declarado dos veces.

### Correcciones del cotejo de contratos (`1e652a5`)

Las cuatro que no dependían de ninguna decisión funcional:

- **El contrato de auth auditaba un evento imposible.** Su tabla de auditoría incluía «Cambio de contraseña **y de correo** — §5.1, §5.2». No existe §5.2 y no puede existir: el correo es inmutable una vez creada la cuenta conforme a `RN-AUTH-ID-02`, `RN-AUTH-ID-03` y `RN-AUTH-ID-12`. Se retiró la referencia y la mención al correo.
- **El parámetro de invitaciones no coincidía con su columna.** El contrato exponía `{id_invitacion}` mientras la clave primaria del modelo es `auth.invitaciones.id`. Renombrado a `{id}` en la ruta y en las dos respuestas, conforme a la convención de conservar el nombre de la columna.
- **La envolvente de colección se declaraba de cuatro formas distintas.** Ahora hay una regla única en `contratos/README.md`: un catálogo de tamaño acotado y no paginable devuelve solo `datos`; todo listado cuyo volumen dependa de los datos lleva `datos` + `paginacion`. Cada endpoint indica cuál de los dos es y ningún contrato repite la forma.
- **La advertencia sobre identificadores repetidos estaba incompleta.** `specs/README.md` enumeraba ocho familias repetidas entre módulos cuando hay once. Faltaban `RN-CAL`, `RN-CON`, `RN-CTX` y `RN-REP`, y sobraba `RN-AUD`, que tras el bloque 1 solo existe en administration. Sustituida por una tabla con las once y el significado de cada una en cada módulo.

---

## 3. Inconsistencias pendientes

### C4 — Tres endpoints sin flujo que los origine

**Severidad: media. Requiere autorización.**

`GET` y `PATCH /api/laboratorios/{id_unidad}/configuracion` y `PUT /api/laboratorios/{id_unidad}/tipos-reserva` existen en el contrato de resources y están respaldados por reglas (`RN-LAB`, `RN-TIP-05`), pero **ningún flujo de usuario los describe**. `resources/user-flow.md` cubre doce flujos de recursos y ninguno de configuración de laboratorio.

Es el único caso en que la superficie HTTP va por delante de los flujos; los demás contratos se derivaron de flujos existentes.

**Corrección propuesta.** Escribir el flujo de configuración del laboratorio en `resources/user-flow.md`, con el Técnico de la unidad como actor principal y el Administrador con alcance global.

**¿Requiere decisión funcional?** Sí. Crear un flujo nuevo excede el encargo de «solo contratos, sin nuevas reglas, flujos ni entidades» y necesita autorización expresa.

### M2 — `espacios/overview.md` está prácticamente vacío

**Severidad: baja. Requiere autorización.**

Cinco líneas, sin título y con un único enlace al modelo de datos. Los demás overviews van de 49 a 164 líneas. Ningún control automático lo detecta porque no rompe ninguna referencia.

**¿Requiere decisión funcional?** No en cuanto al contenido, que sería descriptivo, pero sí autorización para escribirlo por la misma razón que C4.

### M3 — La especificación de la funcionalidad 001 no se ha cotejado

**Severidad: media. No requiere autorización para revisarla.**

`specs/features/001-create-reservation/spec.md` no se toca desde antes de los siete bloques. Sus referencias a reglas siguen resolviendo, pero nadie ha verificado que su contenido siga siendo coherente con lo que cambió en reservations, usuarios y espacios — en particular con `RN-DIS-11`, `RN-TIP-PE-25` y `RN-TIP-PE-26`, que son posteriores.

---

## 4. Decisiones pendientes

Diez de las quince preguntas del registro central siguen abiertas.

### Bloquean trabajo concreto

| | Qué decide | Qué frena |
|---|---|---|
| `OQ-04` | El texto de cada uno de los once eventos notificables | Todo el módulo de notificaciones |
| `OQ-02` | Los tipos admitidos en los campos adicionales de espacios | El formulario de reserva y el catálogo del contrato de espacios |
| `OQ-10` | Las columnas de la planilla de importación de equipos | `UF-ADM-04` |
| `OQ-11` | Si una carga con filas en error se confirma parcialmente o se rechaza entera | `UF-ADM-01` y `UF-ADM-04` |
| `OQ-13` | Cómo entra una reserva por espacio en `EN_EJECUCION` | `UF-RES-13` para ese tipo |

`OQ-11` merece atención: **era una contradicción real entre módulos**, no una omisión. `RN-IMP-06` de administration exigía no dejar cambios parciales mientras `RN-IMP-03` de resources afirmaba que las filas válidas se importan igual. La afirmación de resources se retiró y la decisión quedó centralizada, pero sigue sin tomarse.

### Acotadas

- `OQ-07` — destino de `reservas.motivos_solicitud`, que el diseño objetivo no contempla.
- `OQ-12` — si la importación puede deshabilitar equipos, lo que tendría el efecto de `RN-DES-03` sobre reservas futuras.
- `OQ-14` — catálogo de tipos de adjunto admitidos.

### De arquitectura

- `OQ-15` — el mecanismo que ejecuta la entrega y el reintento de correo. El modelo aporta el índice que lo soporta y `UF-NOT-03` describe la secuencia, pero nadie ha elegido entre tarea programada, cola de trabajos o worker. La elección determina si la política de `RN-COR-03` vive en la aplicación o en la infraestructura. Merece un ADR.
- `OQ-08` — los contratos de administration, notifications, reports y researchs. **El bloqueo original quedó levantado**: los cuatro módulos ya tienen flujos de los que derivar su superficie. Solo falta escribirlos, y `contratos/README.md` ya documenta la forma común que deben seguir.

---

## 5. Archivos modificados por bloque

| Bloque | Commit | Archivos |
|---|---|---|
| 1 — Identidad y permisos | `3d09c23` | 7 |
| 2 — Perfiles académicos | `4f6be6b` | 6 |
| 3 — Importaciones | `ae502d6` | 7 |
| 4 — Finalización por espacio | `d2f0e98` | 4 |
| 5 — Modelo y nomenclatura | `4b141b9` | 4 |
| 6 — Limpieza documental | `3eaa1cf` | 5 |
| 7 — Flujos de notifications y reports | `f99013f` | 7 |
| Reorganización de contratos | `1b8970f` | 6 |
| Correcciones del cotejo | `1e652a5` | 7 |

Cada commit contiene únicamente su bloque. Ningún cambio se coló entre bloques.

---

## 6. Lo que requiere revisión posterior

**ADR-001 sigue sin aprobación formal.** Selecciona una restricción de exclusión de PostgreSQL contra la doble reserva concurrente, pero la migración, los disparadores y las pruebas de concurrencia están pendientes. Hasta completarlas, la funcionalidad 001 no puede darse por correcta bajo concurrencia, como el propio ADR advierte.

**Los cuatro contratos faltantes**, cuya forma ya está documentada.

**Nada está construido.** Todo lo anterior es especificación. Las comprobaciones de este informe verifican coherencia documental, no implementación.

---

## 7. Orden sugerido

1. **Las cinco preguntas bloqueantes** con el responsable funcional, empezando por `OQ-11` y `OQ-04`, que desatascan importaciones y notificaciones enteras. Es lo único que impide avanzar de verdad.
2. **C4 y M2**, en cuanto haya autorización para crear un flujo y un overview.
3. **M3**, cotejar la funcionalidad 001 contra las reglas posteriores a los siete bloques.
4. **Los cuatro contratos** que faltan.
5. **El ADR del mecanismo de reintento de correo** (`OQ-15`) y la aprobación formal de ADR-001.
