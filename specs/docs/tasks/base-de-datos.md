# Plan de tareas — Base de datos

Traduce el [modelo de datos general](../data-model.md), los modelos por módulo y el [estado verificado de PostgreSQL](../../modules/reservations/database-status.md) a tareas de migración. Cada tarea declara objetivo, archivos afectados, dependencias, criterio de aceptación y las reglas que la sustentan.

Plan general y dependencias entre planes: [`tasks.md`](../../../tasks.md) de la raíz.

---

## Punto de partida

El ajuste `002_reservas_objetivo.sql` se aplicó el 23 de septiembre de 2026 sobre el schema `reservas`: 28 tablas, todas vacías, en una transacción. **Lo que sigue es todo lo que ese ajuste dejó fuera.**

| Estado | Qué |
|---|---|
| Aplicado | Las 28 tablas de `reservas`, con sus CHECK, índices y los índices únicos parciales de propuesta vigente y entrega abierta |
| Aplicado | Los cinco tipos de campo de `espacio_campos` y los tres tipos de `reserva_adjuntos`, conforme a `OQ-02` y `OQ-14` |
| Aplicado | La retirada de `motivos_solicitud`, `control_cambios`, `notificaciones`, `mobiliarios`, `otros` y las tres tablas de asociación heredadas |
| **Pendiente** | Las cinco tablas objetivo de `auth`: sesiones, invitaciones, tokens de recuperación, permisos y sus asignaciones |
| **Pendiente** | Las columnas objetivo de `usuarios.usuarios` |
| **Pendiente** | Los schemas `recursos`, `administration` y `notificaciones`, y la parte de `investigacion` que no existe |
| **Pendiente** | Las cinco FK externas, hoy sustituidas por CHECK temporales `pendiente_fk_*` |
| **Pendiente** | Los datos iniciales de los catálogos, que están vacíos |
| **Pendiente** | Los disparadores y exclusiones de ADR-001 |

**La base sobrevivió al borrado del backend anterior y sus scripts se rescataron** en `BK-00`: `002`, `003`, el respaldo estructural y las pruebas SQL están de vuelta en `backend/`, idénticos al original.

### Los schemas que este plan no crea

`auth`, `personal`, `cargos`, `unidadOrganizacional` e `investigacion` ya existen en la base, pero **ningún script de este repositorio los crea**: `002` solo los referencia por clave foránea. Son anteriores al proyecto y se comparten con otros sistemas del ITM.

Lo que sí crea este plan es lo que falta **dentro** de ellos: las cinco tablas objetivo de `auth` (`DB-14`) y las columnas objetivo de `usuarios.usuarios` (`DB-15`). Eso es lo que `auth/data-model.md` y `usuarios/data-model.md` llaman «incorporaciones objetivo».

---

## Convención de tarea

```markdown
### DB-XX — Título

- **Objetivo:** qué queda distinto al terminar.
- **Afectados:** archivos de migración concretos.
- **Dependencias:** qué debe cerrarse antes; qué desbloquea.
- **Aceptación:** condición verificable sobre la base, no "quedó creado".
- **Modelo:** documento que define la estructura.
- **RN:** reglas que sostiene.
```

Toda migración se ejecuta en una transacción, comprueba que las tablas de origen estén vacías antes de tocarlas y conserva un respaldo de estructura. Ninguna usa `DROP ... CASCADE`.

**El número del archivo es un identificador estable, no el orden de aplicación.** El orden lo fijan las fases del [plan general](../../../tasks.md) y las dependencias declaradas en cada tarea. `003` ya lo demuestra: está escrito desde septiembre y se aplica después de `004` y `005`, porque aborta si sus destinos no existen.

---

## 1. Identidad

Lo que falta dentro de los schemas compartidos. **Bloquea la autenticación entera**, así que va antes que todo lo demás.

### DB-14 — Crear las tablas objetivo de `auth`

- **Objetivo:** existen `auth.sesiones`, `auth.invitaciones`, `auth.tokens_recuperacion`, `auth.permisos` y `auth.cuenta_permisos`. `auth.cuentas` ya existe y no se toca.
- **Afectados:** `backend/migrations/010_auth_objetivo.sql`.
- **Dependencias:** ninguna. **Bloquea `DB-09`, `BK-06`, `BK-07` y el plan de auth entero.**
- **Aceptación:**
  - `auth.sesiones` rechaza `expires_at <= created_at`, y borrar una cuenta borra sus sesiones por `ON DELETE CASCADE`.
  - El índice único parcial de `auth.invitaciones` impide dos invitaciones utilizables para el mismo correo; una usada o revocada deja de estorbar.
  - `auth.tokens_recuperacion.token_hash` es único.
  - Los dos índices únicos parciales de `auth.cuenta_permisos` impiden repetir un permiso en la misma unidad y repetir la asignación global, **y `id_unidad` admite `NULL`**.
- **Modelo:** [auth/data-model.md](../../modules/auth/data-model.md).
- **RN:** `SEC-SES-01`, `SEC-SES-09`, `SEC-INV-02`, `SEC-INV-03`, `SEC-TOK-05`, `RN-PER-01`, `RN-PER-06`.
- **Nota:** `gen_random_uuid()` es parte del núcleo desde PostgreSQL 13, así que `auth.sesiones` no necesita `pgcrypto`. Conviene comprobarlo antes de asumirlo: la base es exactamente 13.

---

## 2. Tablas de los módulos propietarios

Estas tablas **bloquean** la instalación de las cinco FK externas y, con ellas, la posibilidad de insertar en `reserva_recursos` y `espacio_recursos`.

### DB-01 — Crear el schema `recursos`

- **Objetivo:** existen `recursos.recursos`, `recursos.equipos`, `recursos.categorias_equipos`, `recursos.mobiliarios` y `recursos.otros_recursos`.
- **Afectados:** `backend/migrations/004_recursos.sql`.
- **Dependencias:** ninguna. **Bloquea DB-05.**
- **Aceptación:** `reserva_recursos` y `espacio_recursos` admiten una inserción con `recurso_id` válido una vez ejecutado DB-05; antes no.
- **Modelo:** [resources/data-model.md](../../modules/resources/data-model.md).
- **RN:** `RN-REC`, `RN-EQP`.
- **Nota:** `nombre_equipo` es `varchar(100)`, no 50. El ancho se amplió al fijar la planilla real de importación (`OQ-10`).

### DB-02 — Completar el schema `investigacion`

- **Objetivo:** existen `pasantias`, `trabajos_grado`, `actividades_institucionales`, `perfiles`, `modalidades_vinculacion` y las seis tablas de vinculación con usuarios. `proyectos` y `semilleros` ya existen.
- **Afectados:** `backend/migrations/005_investigacion.sql`.
- **Dependencias:** ninguna. **Bloquea DB-05.**
- **Aceptación:** `reserva_contexto` admite un valor en `pasantia_id`, `trabajo_grado_id` y `actividad_institucional_id` una vez ejecutado DB-05.
- **Modelo:** [researchs/data-model.md](../../modules/researchs/data-model.md).
- **RN:** `RN-INV`, `RN-ACT`.

### DB-03 — Crear el schema `administration`

- **Objetivo:** existen `administration.auditoria`, `administration.importaciones` y `administration.importacion_resultados`.
- **Afectados:** `backend/migrations/006_administration.sql`.
- **Dependencias:** ninguna.
- **Aceptación:** una operación administrativa deja una fila en `auditoria` con `actor_cuenta_id` resoluble por FK; el CHECK de `importaciones.catalogo` rechaza un valor distinto de `PROYECTOS`, `SEMILLEROS` o `EQUIPOS`.
- **Modelo:** [administration/data-model.md](../../modules/administration/data-model.md).
- **RN:** `RN-AUD-01` a `RN-AUD-07`, `RN-IMP-08`.

### DB-04 — Crear el schema `notificaciones`

- **Objetivo:** existen `tipos_evento`, `eventos`, `notificaciones`, `envios_correo`, `envio_correo_adjuntos` y `preferencias`.
- **Afectados:** `backend/migrations/007_notificaciones.sql`.
- **Dependencias:** ninguna.
- **Aceptación:** el índice único de `eventos.ocurrencia_clave` impide registrar dos veces la misma ocurrencia; el índice `(estado, proximo_intento_at)` de `envios_correo` existe y lo usa el plan de la consulta de reintento.
- **Modelo:** [notifications/data-model.md](../../modules/notifications/data-model.md).
- **RN:** `RN-NOT-05`, `RN-COR-03`, `RN-PREF-04`.

---

## 3. Cierre de las referencias externas

### DB-05 — Ejecutar `003_reservas_referencias_externas.sql`

- **Objetivo:** las cinco FK quedan instaladas y desaparecen los CHECK temporales `pendiente_fk_*`.
- **Afectados:** `backend/migrations/003_reservas_referencias_externas.sql`, escrito y **nunca ejecutado**.
- **Dependencias:** **DB-01** y **DB-02**. El script aborta si falta algún destino.
- **Aceptación:** no queda ninguna constraint cuyo nombre empiece por `pendiente_fk_`, y una inserción con `recurso_id` inexistente falla por FK, no por CHECK.
- **Modelo:** [database-status.md](../../modules/reservations/database-status.md), sección de referencias externas pendientes.

---

## 4. Ajustes a schemas ya existentes

Las tres comparten el archivo `008_identidades.sql`, así que **van al mismo carril**: repartirlas entre dos personas es un conflicto garantizado.

### DB-06 — `personal.personal.estado` como `NOT NULL DEFAULT true`

- **Objetivo:** la ficha está activa o inactiva, sin un tercer valor indeterminado.
- **Afectados:** `backend/migrations/008_identidades.sql`.
- **Dependencias:** ninguna.
- **Aceptación:** una inserción sin `estado` produce `true`; `NULL` se rechaza.
- **Modelo:** [usuarios/data-model.md](../../modules/usuarios/data-model.md).
- **RN:** `RN-PRS-04`.
- **Nota de migración:** fijar en `true` las filas existentes con `NULL` **antes** de aplicar la restricción, sin deducir el valor de otros campos. Desactivar personal activo por una inferencia es peor que el `NULL`.

### DB-07 — `unidad_organizacional.estado`

- **Objetivo:** la unidad admite baja lógica.
- **Afectados:** `backend/migrations/008_identidades.sql`.
- **Dependencias:** ninguna.
- **Aceptación:** deshabilitar una unidad no elimina ni modifica usuarios, personal, reservas ni recursos asociados.
- **Modelo:** [administration/data-model.md](../../modules/administration/data-model.md).
- **RN:** `RN-UNI-04`, `RN-UNI-05`.

### DB-15 — Columnas objetivo de `usuarios.usuarios`

- **Objetivo:** la identidad funcional de Usuario tiene `documento`, `telefono`, `institucion` y `dependencia` con sus restricciones, y el CHECK de nombre.
- **Afectados:** `backend/migrations/008_identidades.sql`.
- **Dependencias:** ninguna. **Bloquea `API-06`**, que exige el documento único y responde `409 DOCUMENTO_DUPLICADO`.
- **Aceptación:** insertar un documento ya registrado falla **por la restricción de unicidad de la base**, no por una comprobación del backend. Ninguna fila existente pierde datos al aplicar la migración.
- **Modelo:** [usuarios/data-model.md](../../modules/usuarios/data-model.md).
- **RN:** `RN-DAT`.
- **Nota de migración:** el modelo exige **completar los faltantes y resolver los duplicados antes** de imponer las restricciones, y hacerlo **sin inventar valores**. Si quedan filas irresolubles, se documentan y se decide explícitamente; no se rellenan por deducción.

---

## 5. Datos iniciales

### DB-08 — Cargar los catálogos de reservas

- **Objetivo:** `tipos_reserva` y `estados_reserva` dejan de estar vacíos.
- **Afectados:** `backend/migrations/seeds/catalogos_reservas.sql`.
- **Dependencias:** ninguna. **Bloquea cualquier prueba funcional de reservas.**
- **Aceptación:** existen los cinco tipos (`ESPACIO`, `RECURSO_INTERNO`, `RECURSO_CAMPUS`, `RECURSO_EXTERNO`, `LISTA_ESPERA`) y los seis estados; crear una reserva resuelve `tipo_reserva_id` y `estado_id` sin insertar catálogo.
- **Modelo:** [reservations/data-model.md](../../modules/reservations/data-model.md).
- **RN:** `RN-TIP-01`, `RN-EST`.

### DB-09 — Cargar el catálogo de permisos

- **Objetivo:** `auth.permisos` contiene los catorce códigos.
- **Afectados:** `backend/migrations/seeds/permisos.sql`.
- **Dependencias:** **DB-14**, que crea la tabla. **Bloquea toda autorización real.**
- **Aceptación:** `exigir_permiso` resuelve los catorce códigos; asignar uno inexistente falla por FK.
- **Modelo:** [auth/data-model.md](../../modules/auth/data-model.md#catálogo-inicial).
- **RN:** `RN-PER-01`, `RN-AUTH-ROL`.

### DB-10 — Cargar los tipos de evento notificables

- **Objetivo:** `notificaciones.tipos_evento` contiene los once eventos de `RN-EVT`.
- **Afectados:** `backend/migrations/seeds/tipos_evento.sql`.
- **Dependencias:** **DB-04**.
- **Aceptación:** cada evento de `RN-EVT-01` a `RN-EVT-11` tiene un código en la tabla, y la preferencia por tipo de `RN-PREF-04` puede referenciarlos.
- **Modelo:** [notifications/data-model.md](../../modules/notifications/data-model.md).

---

## 6. Concurrencia

### DB-11 — Resolver la contradicción sobre el periodo de un recurso

- **Objetivo:** existe una única respuesta a si la entrega física abre el rango temporal de la asignación.
- **Afectados:** [ADR-001](../decisions/adr-001-doble-reserva.md) y [reservations/data-model.md](../../modules/reservations/data-model.md).
- **Dependencias:** ninguna. **Bloquea DB-12.**
- **Aceptación:** el ADR y el modelo dicen lo mismo, y la diferencia queda registrada como decisión con su fecha.
- **Contexto:** el ADR propone que la entrega física abra el rango; el modelo indica que entrega y devolución no alteran el periodo planificado. `database-status.md` lo señala expresamente como pendiente de resolver **antes** de implementar los disparadores.

### DB-12 — Instalar las exclusiones y disparadores de ADR-001

- **Objetivo:** la base impide que dos reservas ocupen el mismo espacio o recurso en periodos incompatibles.
- **Afectados:** `backend/migrations/009_concurrencia.sql`.
- **Dependencias:** **DB-11** y **DB-05**.
- **Aceptación:** dos transacciones concurrentes que soliciten el mismo espacio en periodos solapados terminan con una sola reserva escrita y un error de exclusión en la otra. La prueba se ejecuta contra la base, no contra el backend.
- **Modelo:** [ADR-001](../decisions/adr-001-doble-reserva.md).
- **RN:** `RN-DIS-05`, `OQ-06`, `OQ-09`.
- **Aviso:** `database-status.md` advierte que **la presencia de las columnas `periodo` y `bloqueante` y de índices ordinarios no equivale a la garantía**. Hasta cerrar esta tarea, la funcionalidad de crear reserva no puede darse por correcta bajo concurrencia.

---

## 7. Gobierno del esquema

### DB-13 — Fijar el mecanismo de migraciones

- **Objetivo:** existe una forma reproducible y versionada de evolucionar el esquema, conforme a `architecture.md` §15.
- **Afectados:** `backend/migrations/`, y la herramienta que se elija.
- **Dependencias:** ninguna.
- **Aceptación:** el estado aplicado es consultable sin inspeccionar la base a mano, y aplicar las migraciones pendientes **sobre el esquema actual** deja un resultado idéntico en dos entornos distintos.
- **Contexto:** el ajuste `002` se ejecutó manualmente y nunca formó parte de un arranque. Al borrarse el backend anterior desapareció el riesgo que originó esta tarea —un arranque que recreaba tablas retiradas—, pero no la necesidad: los scripts están en el repositorio, pero **nada registra cuáles se han aplicado** salvo `database-status.md`, escrito a mano.
- **Por qué la aceptación no habla de una base vacía:** no se puede partir de una. `002` no crea el esquema, lo transforma: empieza en `DROP TABLE reservas.reserva_equipos` y `ALTER TABLE reservas.reservas`, y exige el esquema anterior que producía `001_shared_postgres.sql`, deliberadamente no rescatado. Y los schemas compartidos —`auth`, `personal`, `cargos`, `unidadOrganizacional`, `investigacion`— no los crea ningún script de este repositorio. **La línea base es el esquema vivo**, descrito en `database-status.md` y respaldado en `snapshots/`.
- **Decisión pendiente:** si se adopta una herramienta de migraciones o se mantiene la ejecución manual documentada. `architecture.md` exige reproducibilidad y versionado, no una herramienta concreta. Si se quisiera además poder construir desde cero, haría falta una tarea aparte que genere una línea base completa a partir del esquema vivo; hoy no está en el plan.
