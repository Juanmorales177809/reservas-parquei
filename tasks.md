# Plan de adecuación al modelo SDD

Este plan traduce el SDD aprobado al estado actual del repositorio. No implementa cambios. Las tareas parten de que actualmente existen una base `reservas_db` separada, modelos SQLAlchemy sobre tablas `public` heredadas y una migración incremental en `backend/app/migrations.py`.

## 1. Migraciones de base de datos y schemas

### DB-01 — Definir la base PostgreSQL compartida

- **Objetivo:** ajustar el despliegue para que LIA y Reservas vivan en una sola PostgreSQL, separados por schemas lógicos.
- **Afectados:** `docker-compose.yml`, `.env`, `backend/app/config.py`, scripts/backups SQL.
- **Dependencias:** ninguna; bloquea DB-02 y todas las FK cruzadas.
- **Aceptación:** una instalación limpia crea una sola base con los schemas de LIA y Reservas, y el backend puede resolver las tablas de ambos dominios con una única `DATABASE_URL`.
- **RN:** arquitectura documentada en `specs/README.md`, `specs/core/data-model.md` y `specs/lia/data-model-lia.md`.

### DB-02 — Crear schemas y ubicar las tablas objetivo

- **Objetivo:** crear `reservas` y ubicar las tablas maestras existentes de LIA (`unidadOrganizacional`, `personal`, `cargos`, `equipos`) en la misma base, eliminando la dependencia del `public` heredado.
- **Afectados:** migraciones nuevas; `backend/reservas_db_backup.sql`, `backend/lia_db_backup.sql` como fuentes de datos, no como migración automática.
- **Dependencias:** DB-01.
- **Aceptación:** el catálogo resultante contiene las tablas documentadas en ambos `data-model.md`, con nombres y schemas calificables desde PostgreSQL.
- **RN:** modelo de datos; dependencia unidireccional LIA → Reservas solo en forma de referencias desde Reservas.

### DB-03 — Sustituir tablas obsoletas de Reservas

- **Objetivo:** eliminar `personal`, `usuarios_laboratorios`, `lista_espera`, `laboratorios` y recursos genéricos heredados; crear `laboratorios_config`, `mobiliarios`, `otros` y las asociaciones objetivo.
- **Afectados:** migraciones y datos existentes; `backend/reservas_db_backup.sql` contiene actualmente dichas tablas y asociaciones antiguas.
- **Dependencias:** DB-02; definir estrategia de conservación histórica antes de eliminar datos.
- **Aceptación:** no existen tablas/columnas eliminadas por el SDD y sí existen `usuarios`, `laboratorios_config`, `espacios`, `mobiliarios`, `otros`, `reservas`, `reserva_equipos`, `reserva_mobiliarios`, `reserva_otros`, `reserva_acompanantes`, catálogos, notificaciones, colas y auditoría.
- **RN:** RN-LAB, RN-REC, RN-EQP, RN-RES y ausencia de lista de espera.

### DB-04 — Aplicar constraints, índices y estados objetivo

- **Objetivo:** llevar a base las FK, `NOT NULL`, `UNIQUE`, `CHECK` y estados del `data-model`.
- **Afectados:** migraciones de Reservas y LIA; constraints actuales visibles en `backend/reservas_db_backup.sql` no coinciden, por ejemplo `asistentes > 0` y estados en minúscula.
- **Dependencias:** DB-02 y DB-03.
- **Aceptación:** `PENDIENTE`/`APROBADA` bloquean, `RECHAZADA`/`CANCELADA` no; capacidad es `> 0`; nombres de espacios son únicos por unidad; `tipo_reserva_id` es obligatorio; no existe `FINALIZADA`.
- **RN:** RN-RES, RN-EST, RN-DIS, RN-ESP y RN-TIP.

## 2. Ajustes de modelos/ORM

### ORM-01 — Remapear Base y schemas

- **Objetivo:** hacer que SQLAlchemy use los schemas reales y una sola conexión PostgreSQL.
- **Afectados:** `backend/app/db.py`, `backend/app/config.py`, `backend/app/models/__init__.py`, todos los modelos ORM.
- **Dependencias:** DB-01 y DB-02.
- **Aceptación:** las consultas ORM generan nombres de schema correctos y usan la única conexión PostgreSQL configurada para ambos dominios.
- **RN:** modelo de datos compartido.

### ORM-02 — Reemplazar modelos heredados

- **Objetivo:** eliminar de ORM `UsuarioEspacio`, `Recurso`, `TipoRecurso` y entidades locales que no existen en el SDD, e introducir configuración, recursos locales y asociaciones objetivo.
- **Afectados:** `backend/app/models/usuario_espacio.py`, `recurso.py`, `espacio.py`, `reserva.py`, `usuario.py`, `models/__init__.py`; nuevos modelos para `laboratorios_config`, `mobiliarios`, `otros` y asociaciones.
- **Dependencias:** DB-03.
- **Aceptación:** cada tabla documentada tiene modelo o representación ORM equivalente; no quedan relaciones a `laboratorio_id`, `recurso_id` único ni asignaciones `usuarios_espacios`.
- **RN:** RN-LAB, RN-REC, RN-RES.

### ORM-03 — Modelar invariantes de reserva

- **Objetivo:** representar `id_unidad`, espacio opcional, `tipo_uso`, catálogos, estados y asociaciones múltiples.
- **Afectados:** `backend/app/models/reserva.py`, schemas Pydantic bajo `backend/app/schemas/`.
- **Dependencias:** ORM-02 y DB-04.
- **Aceptación:** el modelo permite solo espacio, solo recurso, espacio + recursos y préstamo externo; impide una reserva sin elementos y valida las condiciones de `tipo_uso`.
- **RN:** RN-RES-02–07 y RN-EST.

## 3. Relaciones directas con tablas maestras de LIA

### LIA-01 — FK a unidad organizacional

- **Objetivo:** referenciar directamente `unidadOrganizacional.unidad_organizacional.id_unidad` desde `laboratorios_config`, `reservas` y entidades locales que deban pertenecer a un laboratorio.
- **Afectados:** migraciones, modelos, CRUD y schemas.
- **Dependencias:** DB-02/03 y ORM-01.
- **Aceptación:** una unidad inexistente no puede usarse; el nombre mostrado se obtiene por join y no se almacena en Reservas.
- **RN:** RN-LAB-01/02, RN-RES-01/04.

### LIA-02 — FK directa a personal, cargo y unidad para autorización

- **Objetivo:** resolver el ámbito y las acciones administrativas con `personal -> cargo -> unidad`, sin tabla local de personal ni caché de autorización.
- **Afectados:** `backend/app/auth/auth.py`, `backend/app/deps.py`, `backend/app/api/auth.py`, `backend/app/api/usuarios.py`, modelos y consultas de autorización.
- **Dependencias:** LIA-01, ORM-01 y DB-02.
- **Aceptación:** aprobación, configuración y acciones administrativas consultan las tablas maestras actuales de LIA y rechazan personal inactivo, sin depender de `Usuario.rol` local como única fuente.
- **RN:** RN-USR-05–12, RN-APR-01/03.

### LIA-03 — FK directa de equipos

- **Objetivo:** reemplazar `recursos`/`recurso_id` por `reserva_equipos.id_equipo -> equipos.equipos.id_equipo`.
- **Afectados:** modelos, CRUD y APIs de recursos/reservas; `backend/app/api/recursos.py`, `backend/app/services/reservas.py`, schemas y frontend consumidor.
- **Dependencias:** DB-03, ORM-02 y LIA-01.
- **Aceptación:** Reservas no crea ni actualiza equipos; una operación consulta nombre, unidad y `estado_operativo` actuales de LIA y rechaza equipos no operativos.
- **RN:** RN-EQP-01–06, RN-REC-02.

## 4. Laboratorios, espacios y recursos

### RES-01 — Implementar `laboratorios_config`

- **Objetivo:** trasladar horario, anticipación, modalidad, habilitación, aprobación y correo desde campos dispersos/locales a la tabla de configuración por unidad.
- **Afectados:** `backend/app/models/espacio.py`, `backend/app/api/espacios.py`, `backend/app/services/horarios.py`, schemas y pantallas admin correspondientes.
- **Dependencias:** LIA-01 y ORM-02.
- **Aceptación:** la configuración se administra por unidad; `habilitado_reservas` controla nuevas solicitudes; los nombres se leen de LIA.
- **RN:** RN-LAB-01–04.

### RES-02 — Rediseñar espacios

- **Objetivo:** asociar espacios a unidad, aplicar capacidad positiva y unicidad del nombre.
- **Afectados:** `backend/app/models/espacio.py`, `backend/app/crud/espacios.py`, `backend/app/api/espacios.py`, schemas y frontend de espacios.
- **Dependencias:** RES-01 y DB-04.
- **Aceptación:** no se acepta capacidad cero/negativa ni nombres repetidos dentro de una unidad; la desactivación es lógica y conserva historial.
- **RN:** RN-ESP-01–06.

### RES-03 — Separar equipos, mobiliarios y otros

- **Objetivo:** mantener equipos en LIA y crear recursos locales solo para mobiliarios y otros.
- **Afectados:** `backend/app/api/recursos.py`, `backend/app/models/recurso.py`, schemas, servicios y frontend `frontend/src/services/recursos.ts`/tipos.
- **Dependencias:** LIA-03 y ORM-02.
- **Aceptación:** los nombres locales pueden repetirse, los recursos se identifican por PK, y deshabilitar no elimina reservas históricas.
- **RN:** RN-REC, RN-EQP, RN-MOB, RN-OTR.

## 5. Reservas y asociaciones

### RESV-01 — Reescribir creación y edición de reservas

- **Objetivo:** soportar composición múltiple y `tipo_uso`, con `id_unidad` obligatorio y `espacio_id` opcional.
- **Afectados:** `backend/app/services/reservas.py`, `backend/app/crud/reservas.py`, `backend/app/api/reservas.py`, `backend/app/schemas/reserva.py`, frontend de nueva reserva y tipos.
- **Dependencias:** ORM-03, RES-01/02/03 y LIA-01/03.
- **Aceptación:** pasan los cuatro escenarios soportados: solo espacio, solo equipo, espacio + recursos y préstamo externo; se rechazan asociaciones de otra unidad o reservas vacías.
- **RN:** RN-RES-01–11.

### RESV-02 — Estados y transiciones

- **Objetivo:** reemplazar `esperando/aprobada/...` por estados SDD y retirar estados inventados.
- **Afectados:** `backend/app/services/reservas.py`, `backend/app/crud/reservas.py`, schemas, APIs, notificaciones y frontend.
- **Dependencias:** DB-04 y RESV-01.
- **Aceptación:** solo las transiciones documentadas son posibles; PENDIENTE/APROBADA bloquean y RECHAZADA/CANCELADA liberan disponibilidad.
- **RN:** RN-EST-01–09.

### RESV-03 — Anticipación, horario y capacidad

- **Objetivo:** centralizar las validaciones del SDD y aplicar anticipación solo al crear/reprogramar.
- **Afectados:** `backend/app/services/horarios.py`, `reloj.py`, `reservas.py`, schemas y pruebas.
- **Dependencias:** RES-01, RESV-01 y DB-04.
- **Aceptación:** intervalos enteros `[inicio, fin)`, sin medianoche, dentro del horario configurado, sin fechas pasadas; asistentes no negativos y limitados por espacio.
- **RN:** RN-RES-05/09–11, RN-DIS-01.

## 6. Disponibilidad y concurrencia

### CON-01 — Restricciones de exclusión por espacio y recurso

- **Objetivo:** impedir solapamientos bloqueantes para cada espacio, equipo, mobiliario y otro recurso.
- **Afectados:** migraciones, índices/constraints, `backend/app/crud/reservas.py`, `backend/app/services/reservas.py`.
- **Dependencias:** DB-04, RESV-01 y asociaciones ORM.
- **Aceptación:** dos transacciones concurrentes que intentan ocupar el mismo elemento y horario no pueden confirmar ambas; elementos distintos sí pueden reservarse simultáneamente.
- **RN:** RN-DIS-01–04.

### CON-02 — Hacer atómicas las operaciones críticas

- **Objetivo:** validar y persistir en una transacción crear, editar horario, agregar/cambiar elementos y aprobar.
- **Afectados:** `backend/app/services/reservas.py`, endpoints y manejo de `IntegrityError`.
- **Dependencias:** CON-01 y RESV-02.
- **Aceptación:** un conflicto concurrente devuelve conflicto, revierte la transacción y no deja asociaciones parciales ni notificaciones huérfanas.
- **RN:** RN-DIS-04, RN-APR-02/04.

## 7. Identidad y autorización

### AUTH-01 — Separar reservistas de personal LIA

- **Objetivo:** conservar `reservas.usuarios` para reservistas y usar `personal.personal.supabase_id` para identidad administrativa.
- **Afectados:** `backend/app/auth/auth.py`, `backend/app/api/auth.py`, `backend/app/models/usuario.py`, schemas y frontend `AuthContext`.
- **Dependencias:** LIA-02.
- **Aceptación:** la identidad autenticada se vincula verificablemente con LIA; no existe modelo local `personal` ni asignación `usuarios_espacios` como autorización principal.
- **RN:** RN-USR-01–12.

### AUTH-02 — Rehacer permisos por cargo y unidad

- **Objetivo:** eliminar permisos basados exclusivamente en `Usuario.rol` y asignación directa a espacio.
- **Afectados:** `backend/app/deps.py`, APIs administrativas, CRUD de usuarios, frontend admin.
- **Dependencias:** AUTH-01 y LIA-02.
- **Aceptación:** un gestor solo opera en su unidad y acciones permitidas por cargo; puede crear APROBADA en su propio ámbito si la política lo permite.
- **RN:** RN-USR-05–09, RN-APR-01/03.

## 8. Notificaciones y auditoría

### AUD-01 — Adaptar actores y eventos

- **Objetivo:** usar `actor_tipo`, `actor_id`, `actor_nombre` y auditar las operaciones del SDD sin FK a personal local.
- **Afectados:** `backend/app/models/control_cambio.py`, `backend/app/services/auditoria.py`, API y schemas de control de cambios.
- **Dependencias:** DB-04 y AUTH-01.
- **Aceptación:** crear, modificar, aprobar, rechazar y cancelar dejan auditoría con actor, acción, entidad e instante.
- **RN:** RN-AUD-01–03.

### AUD-02 — Actualizar notificaciones y colas

- **Objetivo:** conservar notificaciones para reservistas/gestores y avisos por desactivación, sin referencias a `personal_id` ni lista de espera.
- **Afectados:** `backend/app/models/notificacion.py`, `backend/app/api/notificaciones.py`, servicios, colas de correo/calendario y frontend.
- **Dependencias:** RESV-02, AUTH-02 y DB-03.
- **Aceptación:** cambios de estado notifican al reservista; desactivar espacio o recurso notifica reservas futuras PENDIENTE/APROBADA; no se generan entradas de lista de espera.
- **RN:** RN-ESP-05, RN-REC-05, RN-AUD.

## 9. Pruebas

### TEST-01 — Pruebas de migración y modelo

- **Objetivo:** verificar instalación limpia, migración de datos y constraints.
- **Afectados:** suite de backend a crear, backups SQL y pipeline.
- **Dependencias:** DB-01–04.
- **Aceptación:** las pruebas confirman schemas, FK LIA, unicidad, checks, estados y ausencia de tablas obsoletas.
- **RN:** todo `data-model.md`.

### TEST-02 — Pruebas funcionales de reservas

- **Objetivo:** cubrir composición, horario, capacidad, cancelación, aprobación y recursos actuales de LIA.
- **Afectados:** `backend/app/services/`, `api/`, `schemas/` y frontend relevante.
- **Dependencias:** RESV-01–03, LIA-03 y AUTH-02.
- **Aceptación:** existe al menos una prueba verificable para cada cardinalidad y regla RN-RES/RN-APR/RN-CAN.
- **RN:** RN-RES, RN-EST, RN-APR, RN-CAN.

### TEST-03 — Pruebas de concurrencia

- **Objetivo:** demostrar ausencia de doble reserva bajo operaciones simultáneas.
- **Afectados:** suite de integración PostgreSQL y `backend/app/services/reservas.py`.
- **Dependencias:** CON-01/02.
- **Aceptación:** una sola operación gana el conflicto por elemento; la otra recibe error controlado y la base queda consistente.
- **RN:** RN-DIS-04.

## 10. Limpieza de código obsoleto

### CLEAN-01 — Retirar migración incremental heredada

- **Objetivo:** reemplazar `migrate_resource_reservations()` por migraciones versionadas del modelo objetivo y eliminar conversiones de `recurso_id`, `esperando`, recursos sintéticos y horarios por espacio.
- **Afectados:** `backend/app/migrations.py` y arranque de `backend/app/main.py`/configuración que la invoque.
- **Dependencias:** DB-01–04 y RESV-01.
- **Aceptación:** el arranque no ejecuta reparaciones destructivas o idempotencias antiguas y todas las modificaciones se trazan en migraciones versionadas.
- **RN:** modelo de datos y RN-DIS.

### CLEAN-02 — Retirar tablas y contratos heredados

- **Objetivo:** retirar del producto las entidades y contratos que pertenecen al modelo anterior: tablas locales de personal/equipos/laboratorios, `usuarios_espacios`, `recurso_id`, estados antiguos y endpoints que los exponen.
- **Afectados:** `backend/app/models/`, `backend/app/api/`, `backend/app/crud/`, `backend/app/schemas/`, `frontend/src/` y configuración de despliegue que aún apunte a la base anterior.
- **Dependencias:** DB-03, ORM-02, LIA-01–03, RESV-01/02 y AUTH-01/02.
- **Aceptación:** una búsqueda del repositorio no encuentra uso ejecutable de esas entidades o campos; las consultas administrativas y de reservas usan el modelo objetivo.
- **RN:** modelo de datos, RN-LAB, RN-EQP, RN-RES, RN-EST y RN-USR.

### CLEAN-03 — Retirar contratos frontend/backend obsoletos

- **Objetivo:** eliminar tipos, servicios, pantallas y payloads que asumen un solo recurso por reserva, `espacio_id` obligatorio, roles locales o estados antiguos.
- **Afectados:** `frontend/src/services/{reservas,recursos,espacios}.ts`, `frontend/src/types/{reserva,recurso,espacio}.ts`, páginas de reservas/admin y schemas/API backend.
- **Dependencias:** RESV-01/02 y AUTH-01/02.
- **Aceptación:** frontend y API comparten los nombres, estados, asociaciones múltiples y permisos del SDD; no quedan llamadas a endpoints eliminados.
- **RN:** RN-RES, RN-EST, RN-USR.
