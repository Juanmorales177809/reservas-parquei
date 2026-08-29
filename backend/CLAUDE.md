# backend/CLAUDE.md

## Stack

FastAPI + SQLAlchemy + Pydantic v2 + Uvicorn ([requirements.txt](requirements.txt)). `bcrypt==3.2.2` está pineado a propósito: passlib no funciona con bcrypt≥4; no subir esa versión.

## Lifespan

`app/main.py` usa `lifespan` (`asynccontextmanager`), no `on_event`. Orden obligatorio en el arranque:

1. `Base.metadata.create_all`
2. `migrate_resource_reservations()` (instala `btree_gist` y la exclusión `reservas_sin_solapamiento`)
3–4. `seed_admin_user()` — una única llamada desde `main.py`. Internamente:
   - ejecuta `init_espacios(db)` para sembrar los espacios iniciales;
   - si no existe un usuario con rol admin y están configuradas las variables `INITIAL_ADMIN_*`, crea el administrador inicial (las tres variables deben definirse juntas, password ≥ 12 caracteres).
5. `engine.dispose()` al cierre

Orden real: `create_all` → migraciones → `seed_admin_user()`. No describir `init_espacios()` como una segunda llamada independiente del lifespan.

## PostgreSQL real para tests

La suite usa PostgreSQL 13 real, nunca SQLite: la exclusión `reservas_sin_solapamiento` y `btree_gist` son específicas de PostgreSQL. Base `reservas_test` en `localhost:5433` vía `docker-compose.test.yml` (raíz del repo).

```bash
docker compose -f docker-compose.test.yml up -d --wait   # desde la raíz del repo
cd backend
pytest -v
docker compose -f docker-compose.test.yml down -v         # limpieza manual, opcional
```

## Estructura por capas

- `api/`: routers FastAPI (`auth.py`, `espacios.py`, `recursos.py`, `reservas.py`, `usuarios.py`, `notificaciones.py`, `admin_dashboard.py`, `control_cambios.py`).
- `domain/`: capa tipada — `enums.py` (`EstadoReserva`, `EstadoEntidad`, `EstadoSlot`, `Rol`), `valor.py` (`FranjaHoraria`, `HorarioAtencion`), `protocols.py` (`Reloj`, `RegistroAuditoria`).
- `services/`: reglas de negocio — `reservas.py`, `horarios.py`, `reloj.py`, `auditoria.py`.
- `crud/`: acceso SQLAlchemy (`espacios.py`, `reservas.py`, `usuarios.py`).
- `models/`: modelos SQLAlchemy (`espacio.py`, `recurso.py`, `reserva.py`, `usuario.py`, `usuario_espacio.py`, `notificacion.py`, `control_cambio.py`).
- `schemas/`: contratos Pydantic, uno por entidad + `admin_dashboard.py`, `disponibilidad.py`.
- `auth/auth.py`: hash de contraseñas y JWT. `deps.py`: dependencias de autorización.
- `config.py`, `db.py`, `main.py`, `migrations.py` en la raíz de `app/`.

## Enums de dominio

`EstadoReserva`: `ESPERANDO`, `APROBADA`, `RECHAZADA`, `CANCELADA` (`app/domain/enums.py`). `RECHAZADA` y `CANCELADA` son terminales. Transiciones válidas: `esperando → aprobada | rechazada | cancelada`, `aprobada → cancelada`.

## HorarioAtencion y FranjaHoraria

Value objects tipados en `app/domain/valor.py` que envuelven la columna JSONB `horario_atencion` de `Espacio` (día → horas). Validados por `app/services/horarios.py` (`horas_atencion_dia`, `horario_cubre_reserva`). Las horas deben ser bloques completos (`minute == 0`).

## RelojLocal y reloj inyectable

`app/services/reloj.py` define el protocolo `Reloj` y `RelojLocal`; devuelve `datetime` naive a propósito, en `APP_TIMEZONE` (por defecto `America/Bogota`). No "arreglar" añadiendo `tzinfo`. Los tests inyectan un reloj fijo (`_RelojFijo`) en vez de usar `monkeypatch` sobre funciones sueltas.

## AuditoriaSesion

Adaptador de auditoría en `app/services/auditoria.py` que implementa el protocolo `RegistroAuditoria` de `app/domain/protocols.py`; registra cambios administrativos consultables vía `GET /admin/control-cambios`.

## Roles y dependencias de autorización

Definidas en `app/deps.py`:

- `get_current_user`: decodifica el JWT de Supabase de la cookie `access_token` vía `deps.decode_token` (`sub`=UUID de `auth.users`, resuelto al `Usuario` vía `supabase_id` — ver "Migración a Supabase Auth" más abajo), 401 si no hay cookie, el token es inválido o el usuario no existe. `decode_token` verifica según el `alg` que el propio token declara: **ES256** contra el JWKS público de Supabase (`app/services/supabase_jwks.py`, lo que emite un proyecto real hoy) o **HS256** contra `SUPABASE_JWT_SECRET` (solo lo usan los tests, que firman localmente y nunca le pegan a la red — ver `tests/conftest.py::token_supabase_para`). Confirmado en producción el 2026-08-27: un proyecto de Supabase real firma ES256, no HS256 — verificar solo contra el secreto compartido rechazaba TODO login real con 401 pese a credenciales correctas.
- `require_admin`: 403 si `rol != admin`.
- `require_resource_manager`: 403 si `rol not in {admin, gestor}`.
- `get_managed_space_id`: para gestores, resuelve su único espacio en `usuarios_espacios`; 403 si no tiene espacio asignado. Para admin devuelve `None` (sin restricción).
- `get_current_user_optional`: lee la cookie `access_token` manualmente vía `Request` (sin `Depends(cookie_auth)`) para no exigir esquema de seguridad en endpoints públicos como `GET /espacios` (RN-005); un token inválido se trata como acceso anónimo, nunca como error. Fase 9G: ya no acepta `Authorization`.

## Migración a Supabase Auth (corte total, 2026-08-26)

El login clásico username/password propio (`SECRET_KEY`, `hashed_password`) **se retiró por completo** — Supabase Auth es el único mecanismo de autenticación. `POST /auth/login`, `/auth/cambiar-password`, `/auth/recuperar`, `/auth/restablecer` ya no existen; solo quedan `POST /auth/logout` (sin cambios) y `POST /auth/supabase/sesion`.

- **Quién crea la identidad en Supabase, y cuándo**: el admin sigue siendo el único que crea usuarios (`POST /usuarios`, `require_admin`). El alta son 2 pasos, no 3 — no hay un paso separado de "enviar correo":

  ```
  Admin crea usuario (form: username, email, rol, espacio?)
          │
          ▼
  POST /usuarios ──► invitar_usuario(email) ──► Supabase: crea auth.users
                          │                       Y manda el correo de
                          │                       invitación en la MISMA
                          │                       llamada (/auth/v1/invite)
                          ▼ (UUID devuelto)
                 create_usuario(db, payload, supabase_id)
                 -- crea la fila en `usuarios` con ese supabase_id
  ```

  Si `invitar_usuario` falla, no se crea nada en nuestra tabla (`502` al admin) — no hay usuario "a medias" sin `supabase_id`. El correo no lleva ninguna credencial: es un link de Supabase donde la persona elige su propia contraseña, nunca el admin. Login después: la app llama `signInWithPassword` **directo contra Supabase** (no contra este backend) y recién el JWT resultante se intercambia en `POST /auth/supabase/sesion`.
- **`POST /auth/supabase/sesion`** verifica el JWT de Supabase (reusa `deps.decode_token`, ver arriba — antes tenía su propia verificación duplicada, siempre HS256, corregido el 2026-08-27) y busca el `Usuario` **solo** por `supabase_id` ya existente — 403 si no hay fila con ese UUID. **Nunca crea ni vincula una cuenta por email.** Esto es deliberado: cierra un hueco de auto-apropiación de cuenta que tuvo una implementación previa (nunca llegó a este estado del código, revertida antes de mergear). No reintroducir esa lógica.
- **Un admin ya existente en `reservas_db` de antes del corte a Supabase bloquea el auto-seed de `seed_admin_user()`**, aunque ese admin nunca haya tenido (ni pueda tener) un `supabase_id` real — el chequeo solo mira "¿existe alguien con rol admin?", no si esa cuenta puede efectivamente loguearse. Encontrado en el primer despliegue real post-corte (2026-08-27): quedó un admin huérfano, sin forma de entrar, y sin ningún camino automático para arreglarlo. Solución aplicada a mano esa vez: `UPDATE usuarios SET email=..., supabase_id=... WHERE id=...` vinculando la fila existente a una identidad de Supabase real. No hay fix de código para esto todavía — si vuelve a pasar (otro entorno con un admin pre-Supabase), mismo camino manual.
- **Puente `usuarios.supabase_id`** (UUID, nullable, índice único en `usuarios`): evita migrar el PK entero de `Usuario` (y sus 8 relaciones de FK) a UUID. `hashed_password` y `debe_cambiar_password` quedan como columnas vestigiales (nunca se hace `DROP COLUMN` en este proyecto) — ya no se leen para autenticar.
- **`SUPABASE_URL`, `SUPABASE_JWT_SECRET`, `SUPABASE_SERVICE_ROLE_KEY`** son obligatorias (`config.py::validate()` levanta `RuntimeError` si falta alguna) — no hay flag de "hybrid", no hay camino que funcione sin Supabase configurado.
- **`seed_admin_user`**: el admin inicial (`INITIAL_ADMIN_*`) también se crea en Supabase, vía `crear_usuario_confirmado` (con contraseña ya puesta, sin correo — a diferencia de `invitar_usuario`, es la única vía que fija una contraseña desde el backend, reservada al bootstrap).
- **Recuperación de contraseña self-service** (2026-08-27): sin cambios de backend — es 100% cliente. `AuthRepository.solicitarRecuperacion` (Flutter) llama `Supabase.instance.client.auth.resetPasswordForEmail(email)` directo contra Supabase; el link que llega por correo dispara el mismo evento `passwordRecovery` que un link de invitación y termina en la misma `CompletarCuentaScreen` (`updateUser` + canje de sesión, ver `app_flutter/CLAUDE.md`). Reenviar una invitación desde el admin sigue siendo un camino aparte (ver el bullet de `reenviar-invitacion` más abajo) — ese es para cuentas que nunca completaron el alta, este es para quien ya tiene cuenta y olvidó la contraseña.
- **`DELETE /usuarios/{id}` borra también la identidad de Supabase** (`eliminar_usuario` en `supabase_admin.py`, llamada ANTES de borrar la fila local — en el orden inverso, un fallo a mitad de camino deja una identidad huérfana). Bug real encontrado en producción el 2026-08-27: antes de este fix, borrar un usuario solo tocaba `reservas_db`, y reinvitar el mismo email fallaba después con 422 `email_exists` contra una cuenta que ya no existía de nuestro lado.
- **`POST /usuarios/{id}/reenviar-invitacion`** (admin-only): genera un link de invitación fresco vía `generar_link_invitacion` (`/auth/v1/admin/generate_link`, no `/auth/v1/invite` — este último rechaza con `email_exists` cualquier email ya registrado, aunque la invitación original nunca se haya confirmado; probado contra el proyecto real). Ese endpoint de Supabase no manda el correo por su cuenta: se encola vía el outbox propio (`app/services/email.py`) y la respuesta (`ReenviarInvitacionResponse`) siempre incluye el `link` crudo además de `correo_enviado`, para que el admin lo entregue a mano mientras el SMTP del ITM sigue pendiente (ver memoria de sesión `smtp_itm_pendiente`).

## Fase A — perfil de usuario, recursos por zona, descripción de reserva (2026-08-27)

Primera fase de un plan más grande motivado por el formulario real de solicitud de laboratorios del ITM (ver `~/.claude/plans/ya-tenemos-el-ci-calm-octopus.md`, fases B/C/D todavía no implementadas). Esta fase es aditiva, sin romper ningún contrato existente.

- **`PUT /usuarios/me`** (nuevo, `app/api/usuarios.py`): self-service, cualquier rol autenticado (`get_current_user`, no `require_admin`) edita su propio perfil vía `PerfilUpdate` (`schemas/usuario.py`, `extra="forbid"`) — solo `documento_identificacion`/`telefono`/`institucion`/`vinculacion`/`dependencia`. Deliberadamente NO reusa `UsuarioUpdate`: con un schema separado, mandar `{"rol": "admin"}` a este endpoint es un 422 de validación, no un campo ignorado en silencio — la escalada de privilegios es estructuralmente imposible, no depende de que el handler se acuerde de filtrar. Registrada ANTES de `PUT /usuarios/{usuario_id}` en el archivo (mismo motivo que `GET /me` antes de cualquier ruta con `{usuario_id}`): si quedara después, FastAPI intentaría parsear `"me"` como el `int` de esa ruta.
- **`Usuario` gana 5 columnas de perfil**, todas nullable (sin backfill posible): `documento_identificacion`, `telefono`, `institucion` (texto libre, sin CHECK — la lista de facultades del ITM puede reestructurarse administrativamente), `vinculacion` (`CheckConstraint` con 5 valores del enum `VinculacionUsuario`, `IS NULL OR ...` obligatorio para no romper las filas existentes), `dependencia` (texto libre).
- **`ZonaResponse` gana `recurso_ids`** — cierra un gap real: `PUT /zonas/{id}/recursos` existía desde la Fase 12C-3 pero ninguna pantalla de Flutter lo llamaba nunca; la UI nueva (`GestionZonasScreen`, ver `app_flutter/CLAUDE.md`) necesita ver la selección actual antes de dejarla reemplazar por completo.
- **`Reserva.descripcion`** (texto libre opcional, "Actividad a realizar" del formulario real) — eje simple en `ReservaUpdate`, mismo criterio que `tipo` (ausente en el PATCH conserva, `null` explícito limpia).
- `openapi.snapshot.json` regenerado (endpoint nuevo + campos aditivos en 4 schemas) y revisado a mano — puramente aditivo, ninguna ruta ni campo existente cambió de forma.

## Fase B — motivo de la solicitud (2026-08-27)

Segunda fase del mismo plan. Agrega las 2 ramas del formulario real que sí encajan en el modelo actual de `Reserva` (franja horaria de un día) — las otras 2 (orden de salida, mano de obra) quedan para la Fase C, en una tabla aparte (ver la sección "Hoja de ruta" del plan).

- **`TipoSolicitud`** (`app/domain/enums.py`), 3 valores: `reserva_en_laboratorio` (default), `reserva_fuera_laboratorio`, `orden_salida`. Concepto DISTINTO de `TipoReserva` (académico) y de `modalidad_reserva` de `Espacio` — nombres parecidos, no relacionados.
- **`Reserva` gana 3 columnas**: `tipo_solicitud` (NOT NULL, default `reserva_en_laboratorio`, backfill vía `UPDATE ... WHERE ... IS NULL` mismo molde que `modalidad_reserva` de `Espacio`), `ubicacion_uso` (nullable, solo aplica a `reserva_fuera_laboratorio`), `requiere_apoyo_auxiliar` (NOT NULL, default `false`).
- **El `CheckConstraint` de `tipo_solicitud` está acotado a 2 valores** (`reserva_en_laboratorio`, `reserva_fuera_laboratorio`) — **no a los 3 del enum**. `orden_salida` existe en `TipoSolicitud` porque el enum se declaró completo desde ya (para no reabrir el CHECK en la Fase C), pero la base de datos todavía lo rechaza: es la garantía estructural de que un bug de ruteo en la Fase C no pueda colar una fila de ese tipo en `reservas` sin que PostgreSQL la rechace. Ver `tests/test_reserva_tipo_solicitud.py::test_orden_salida_rechazado_por_check_constraint`.
- **`ReservaCreate`/`ReservaUpdate` rechazan `tipo_solicitud=orden_salida` con 422** (`field_validator`), redundante a propósito con el CHECK de base de datos — el endpoint público jamás debe aceptar ese valor; solo lo materializará internamente `services/solicitudes.py` en la Fase C.
- **`tipo_solicitud`/`requiere_apoyo_auxiliar` en `ReservaUpdate` NO llevan `| None`** (a diferencia de `descripcion`/`ubicacion_uso`, que sí son nullable de verdad): son columnas NOT NULL, así que mandar `null` explícito debe dar 422 de validación, no un intento silencioso de romper la constraint en el servicio. `exclude_unset` sigue distinguiendo "ausente" (conserva) de "presente" (reemplaza) sin necesidad de que el tipo permita `None` — el valor por default declarado en el schema nunca se usa para nada, solo habilita que el campo sea opcional en el JSON de entrada.
- **`ubicacion_uso` se valida cruzado con `tipo_solicitud`**: en `ReservaCreate`, un `model_validator` rechaza con 422 si `ubicacion_uso` viene sin `tipo_solicitud == reserva_fuera_laboratorio`. En `ReservaUpdate` esa validación NO puede vivir en el schema (un PATCH no ve el estado actual de la reserva) — vive en `actualizar_reserva` (`services/reservas.py`), comparando el `tipo_solicitud` ya mergeado (`cambios.get(...) or reserva.tipo_solicitud`) contra el `ubicacion_uso` ya mergeado, 400 si la combinación final es inválida.
- `openapi.snapshot.json` regenerado (3 campos aditivos en 3 schemas + enum `TipoSolicitud` nuevo) y revisado a mano.

## Fase D — import del inventario institucional real (2026-08-27)

Tercera fase del mismo plan (`~/.claude/plans/ya-tenemos-el-ci-calm-octopus.md`). La Fase C (orden de salida / mano de obra) quedó bloqueada por motivos de negocio ajenos al código (falta el formato estandarizado de orden de salida y la especificación de "mano de obra") — el usuario pidió saltar directo a cargar el inventario real de los 20 laboratorios del ITM.

- **`backend/scripts/importar_inventario.py`** (script de carga única, no una feature de producto — no tiene pantalla ni endpoint). Lee `LABORATORIOS PARQUE I.xlsx` (20 hojas = 20 laboratorios reales, 1814 filas de inventario plano) y hace *get-or-create* de un `Espacio` por hoja y un `Recurso` por fila con placa no vacía. `openpyxl==3.1.5` vive en `requirements-dev.txt` (utilería de desarrollo, nunca corre en producción).
- **Los 20 `Espacio` no existían en ninguna base antes de esta fase** — el script los crea con placeholders explícitos para lo que el Excel no trae (`ubicacion`, `capacidad`, `correo`; el dominio de correo usado, `pendiente.itm.edu.co`, es deliberadamente falso para que nadie lo confunda con un correo real entregable). Corregir a mano después desde `GestionEspaciosScreen`.
- **`Recurso.placa`** (nueva columna, `String(50)` nullable, `CREATE UNIQUE INDEX IF NOT EXISTS uq_recursos_placa`): identificador de activo físico del inventario real (ej. `"05087964"`), `null` para un recurso creado a mano desde la UI. Es la clave de idempotencia del import — confirmado por análisis completo del Excel real que las ~1814 placas son únicas dentro y entre las 20 hojas, a diferencia de las descripciones (hay duplicados reales, ej. "MICRÓFONO DINÁMICO SM 57" se repite en un mismo laboratorio). Expuesta en `RecursoResponse` como campo aditivo nullable.
- El script no asume una fila fija de encabezado: escanea las primeras filas buscando "PLACA"/"DESCRIPCIÓN" por posición (`enumerate`, no `cell.column` — en modo `read_only=True` de openpyxl las celdas vacías son `EmptyCell`, que no expone ese atributo). Confirmado necesario contra el Excel real: 19/20 hojas tienen el encabezado en la fila 3, una en la fila 4.
- Las Zonas de cada laboratorio (sub-áreas del formulario real, ej. "Estudio de Grabación y Mezcla 5.1") no están en el Excel — se crean a mano después con `GestionZonasScreen` (Fase A1) y los recursos importados se les asocian ahí.
- Dry-run por defecto (dos consultas por fila, un `rollback()` al final); `--confirmar` para escribir de verdad. Ejecutado solo contra `reservas_test` durante el desarrollo — el comando final para `reservas_db`/producción se entrega al usuario, nunca se corre desde este asistente contra esas bases.
- `openapi.snapshot.json` regenerado (un campo aditivo, `RecursoResponse.placa`) y revisado a mano.

## Equipos adicionales en una reserva (2026-08-27)

Dos features chicas, fuera del plan de fases (`~/.claude/plans/ya-tenemos-el-ci-calm-octopus.md`), pedidas directo por el usuario y documentadas primero en `HANDOFF-opencode-equipos-reserva.md` (raíz del repo) para que las implementara OpenCode; Claude Code revisó el resultado, corrigió tres problemas reales y agregó la cobertura de test que faltaba antes de aprobarlas.

- **Feature A (solo Flutter, sin cambios de backend)**: la pantalla de reserva ya permitía elegir cualquier `Recurso` del espacio además de las zonas (`recurso_ids`/`zona_ids` son ejes independientes desde la Fase 12C-6) — el gap era puramente de UI, sin ninguna indicación visual de que un equipo ya viene incluido en una zona marcada. Ver `app_flutter/CLAUDE.md`.
- **Feature B — el gestor agrega equipo a una reserva ya aprobada, sin resetear su estado**: el mecanismo ya existía (`actualizar_reserva`, `backend/app/services/reservas.py`, no tiene gate de `estado` para `gestor`/`admin` — a diferencia de un `usuario` común, que solo puede editar mientras `esperando`). Lo nuevo es la **notificación al dueño de la reserva** cuando se le agrega algo:
  - **`TipoNotificacion.ACTUALIZADA`** (`app/domain/enums.py`), quinto valor del enum — cambio de contrato aprobado explícitamente (ver `AskUserQuestion` en la sesión): `notificaciones_tipo_check` pasa a aceptar `'Actualizada'` además de los 4 valores previos, mismo patrón `DROP CONSTRAINT IF EXISTS` + `ADD CONSTRAINT` de `migrations.py`. `openapi.snapshot.json` regenerado (diff de 5 líneas, solo el enum `TipoNotificacion` en components).
  - `actualizar_reserva` compara `recurso_ids`/`zona_ids` antes/después del PATCH; si el conjunto resultante tiene algo nuevo, **y** quien edita es `gestor`/`admin` (no el propio dueño editando su reserva), crea una `Notificacion(tipo=ACTUALIZADA)` + encola un correo (`encolar_correo`, mismo patrón que `crear_reserva`/`cambiar_estado`) con el detalle de qué se agregó (nombres de recursos/zonas). Si no hay nada nuevo (solo se editó fecha/asistentes, por ejemplo) o el gestor edita su propia reserva, no notifica — ver `tests/test_api_reservas.py::TestNotificacionAlAgregarRecursos`.
  - **Sin cambios en `ReservaCreate`/`ReservaUpdate`/`ReservaResponse`**: `PATCH /reservas/{id}` ya aceptaba `recurso_ids`/`zona_ids` desde antes; esta feature solo le agrega un efecto secundario (notificar), no un campo nuevo.

**Problemas reales encontrados en la revisión y corregidos antes de aprobar** (ninguno los introdujo el diseño del handoff, todos de la implementación de OpenCode):
1. `app_flutter/pubspec.yaml` tenía el SDK debilitado a `^3.12.0` — exactamente el error que `app_flutter/CLAUDE.md:499` ya documentaba como resuelto (una imagen Docker con Dart 3.12 rompe `pubspec.yaml`, que exige `^3.13.1`). Revertido al valor correcto.
2. `test_domain_enums.py::test_tipo_notificacion_conserva_valores_actuales` — el nuevo valor del enum lo rompía (es exactamente el tripwire que ese test existe para atrapar); actualizado junto con el snapshot de OpenAPI.
3. **Cero cobertura de test para el comportamiento nuevo** (notificar al agregar equipo) — contradice la regla del proyecto "todo cambio de comportamiento en un endpoint debe ir acompañado de la prueba correspondiente" (`backend/tests/CLAUDE.md`). Se agregó `TestNotificacionAlAgregarRecursos` (3 casos: notifica con el correo correcto, no notifica si no se agregó nada nuevo, un gestor editando su propia reserva no se autonotifica).

**Verificado**: backend 639/639 contra `reservas_test`; Flutter `flutter analyze` limpio, `flutter test` 40/40 (incluye los 7 tests nuevos de `espacio_reserva_sheet_test.dart` que ya traía la implementación de OpenCode para la Feature A). **No se hizo verificación manual interactiva contra un backend real corriendo** (E2E Web sigue bloqueado por el gap de CORS/`--use-existing-app` ya documentado en `app_flutter/CLAUDE.md`, y montar el harness nativo Windows solo para esto no se justificó en esta sesión) — la cobertura automatizada es inusualmente específica (un test por estado/interacción visual en Feature A, un test por rama de la lógica de notificación en Feature B), pero sigue siendo análisis estático + tests, no el flujo real corriendo. Queda como riesgo residual conocido, no verificado en vivo.

## Correo por Microsoft Graph (puente temporal, 2026-08-28)

SMTP clásico contra `smtp.office365.com` no funciona en el tenant M365 del ITM: primero se confirmó `535 5.7.139 ... disabled for the Tenant` (SMTP AUTH apagado a nivel de todo el tenant, cuenta `reservaslabparquei@correo.itm.edu.co`), y después, con `sgc-lia@itm.edu.co`, un error de credenciales que probablemente sea Conditional Access bloqueando autenticación heredada. Se armó un ticket a Sistemas (`ticket-sistemas-graph-mail.html`, raíz del repo) pidiendo un App Registration con `Mail.Send` de aplicación — la solución correcta y permanente — pero mientras se resuelve, `app/services/email_graph.py` es un **puente temporal** que sí funciona hoy.

- **Token DELEGADO, no de aplicación**: usa `PublicClientApplication` de `msal` con el `CLIENT_ID` público bien conocido de "Microsoft Graph Command Line Tools" (`14d82eec-204b-4c2f-b7e8-296a70dab67e`, el mismo que usa `Connect-MgGraph` de PowerShell por defecto) — **no requiere que Sistemas cree ni apruebe nada** para arrancar, porque es una app de primera parte de Microsoft ya pre-consentida en la mayoría de los tenants.
- **Login único, interactivo, fuera del backend**: `python -m scripts.graph_login` (nuevo, `backend/scripts/graph_login.py`) lo corre a mano quien tenga la contraseña de `GRAPH_MAIL_SENDER` — device code flow, no hace falta que el navegador se abra en el servidor, solo visitar una URL e ingresar un código desde cualquier dispositivo. Deja el token (y su refresh token) cacheado en `GRAPH_TOKEN_CACHE_PATH`.
- **El backend NUNCA dispara un login interactivo por su cuenta**: `procesar_pendientes()` solo intenta `acquire_token_silent` (renovación silenciosa desde la caché). Si el token cacheado venció o el refresh token quedó inválido (cambio de contraseña, revocación de sesión, política de Conditional Access), el envío falla con un `RuntimeError` explícito — mismo contrato que `_enviar_smtp`, la fila del outbox queda `pendiente`/`fallido` según corresponda. Hace falta correr `graph_login` de nuevo a mano; **esto se rompe solo, sin aviso, es un riesgo aceptado del carácter temporal de este puente** — no reemplaza la necesidad del App Registration real.
- **`EMAIL_TRANSPORT`** (`smtp` default | `graph_delegado`) decide el transporte real dentro de `procesar_pendientes`; `smtp` no cambia nada del comportamiento existente. `GRAPH_MAIL_SENDER` es el buzón que manda el correo (`sgc-lia@itm.edu.co`).
- **`graph_token_cache` — volumen Docker nuevo**, montado en `backend` en `/data/graph`: el token cacheado tiene que sobrevivir cada reconvergencia del agente de CD (`deploy/README.md`, ~10 min de ciclo) — sin un volumen persistente, cada redeploy borraría la sesión y obligaría a repetir el login interactivo.
- **`msal==1.38.0`** — única dependencia nueva de producción (no dev-only, a diferencia de `openpyxl` de la Fase D) — ver el comentario en `requirements.txt` sobre por qué es temporal.
- **Reemplazar, no extender, cuando llegue el App Registration real**: el flujo `client_credentials` (app-only, sin sesión de usuario) es una implementación distinta — otro `ConfidentialClientApplication`, sin device flow, sin cache de sesión de usuario. `email_graph.py` está aislado detrás de una única función (`enviar_graph`) para que el reemplazo sea acotado.
- Tests: `tests/test_email_graph.py` (token silencioso con/sin cuenta cacheada, token vencido, payload/headers del `sendMail`, error HTTP) y `tests/test_correo_saliente.py::test_procesar_pendientes_usa_graph_si_transport_es_graph_delegado` (confirma que con `graph_delegado` no se toca SMTP en absoluto). Todos mockean `PublicClientApplication`/`httpx.post` — nunca le pegan a Graph ni a MSAL real. **Sin verificar en vivo contra Graph todavía** — falta que alguien con la contraseña de `sgc-lia@itm.edu.co` corra `graph_login.py` una vez para poblar la caché real y probar un envío de punta a punta.

## Plantillas HTML institucionales en el outbox (2026-08-28)

`CorreoSaliente` gana `es_html` (`Boolean NOT NULL DEFAULT false`) — solo las plantillas de `app/services/email_templates.py` mandan HTML; cualquier notificación futura que no pase por ahí sigue en texto plano por default. `_enviar_smtp`/`enviar_graph` (`app/services/email_graph.py`) ya aceptan `es_html` y lo traducen a `MIMEText(..., "html")`/`contentType: "HTML"` de Graph respectivamente; `procesar_pendientes` lo pasa desde la fila del outbox sin que quien encola tenga que saber nada del transporte.

Identidad visual compartida por todas las plantillas (HTML de correo real: tablas + estilos inline, sin CSS externo). Los colores de estado de reserva (`_COLORES_ESTADO` en el módulo) son los mismos hex que ya usa `notificaciones_sheet.dart::_NotificacionTile` — un correo y su notificación in-app se ven del mismo sistema.

> **Desactualizado, ver "Rediseño con identidad real del ITM" más abajo**: esta primera versión usaba azul académico `#1E3A8A` + esmeralda `#10B981` (inventados para `app_flutter/` en la Fase 6) y un masthead con degradé CSS. Se reemplazó el mismo día por los colores reales de la Facultad de Ingenierías y un logo real extraído del manual de marca del ITM.

- **`plantilla_invitacion(link, nombre_saludo)`** — usada por `reenviar_invitacion_endpoint` y (desde el cambio de abajo) por `create_usuario_admin`.
- **`plantilla_reserva_pendiente(...)`** — nueva reserva esperando aprobación, al gestor (`crear_reserva`).
- **`plantilla_reserva_estado(..., estado, motivo=None)`** — aprobada/rechazada/cancelada al solicitante (`cambiar_estado`); tarjeta con acento de color por estado, bloque de motivo solo si `estado == "rechazada" and motivo`.
- **`plantilla_reserva_actualizada(...)`** — Feature B (equipos agregados a una reserva aprobada), al dueño (`actualizar_reserva`).
- Todo texto controlado por el usuario (`nombre_saludo`, `motivo`, `detalle`) se escapa (`html.escape`) antes de insertarse.

**Actualización (2026-08-28, mismo día): la invitación inicial también se movió a nuestro outbox.** El plan original de arriba (dejar `POST /usuarios` con `invitar_usuario`/`/auth/v1/invite` intacto, sin verificar contra el proyecto real si `generate_link` crea usuarios nuevos) se reemplazó a pedido explícito del usuario, que no quería depender de un SMTP de terceros para Supabase. `create_usuario_admin` ahora usa `crear_usuario_y_generar_link` (nueva, `app/services/supabase_admin.py`) — mismo endpoint `/auth/v1/admin/generate_link` `type=invite` que ya usaba `generar_link_invitacion` para el reenvío, pero devolviendo también el `id` de usuario que trae la respuesta (documentado por Supabase como el mismo mecanismo interno que `/auth/v1/invite`, solo que sin mandar el correo). Si la respuesta no trajera ese `id` contra el proyecto real, la función falla fuerte (`SupabaseAdminError`, 502) en vez de guardar una fila local sin `supabase_id` — fallo ruidoso, no silencioso, y así quedó de hecho verificado en producción el mismo día (usuario "Prueba" creado con éxito). `invitar_usuario`/`/auth/v1/invite` queda sin uso en el código (no se borró, por si hiciera falta volver atrás) pero ya no es el camino real.

Con esto, `supabase-template-invitacion.html` (raíz del repo, pensado originalmente para pegar en el dashboard de Supabase) queda sin uso real para la invitación inicial -- se mantiene igual solo por si en algún momento se vuelve a depender de que Supabase mande el correo. `supabase-template-recuperacion-password.html` **quedó obsoleto el mismo día** (ver "Recuperación de contraseña también por nuestro outbox" más abajo) -- la frase original de este párrafo ("sigue siendo el único lugar...") ya no es cierta.

**Hallazgo real en producción, mismo día**: `EMAIL_ENABLED` nunca se activó en el `.env` del servidor al armar el puente de Graph -- se configuraron `EMAIL_TRANSPORT`/`GRAPH_MAIL_SENDER` pero no ese flag, así que `procesar_pendientes` cortaba antes de intentar cualquier envío (la fila quedaba `pendiente`, la UI mostraba el fallback de "copiá el link a mano"). La prueba directa de `enviar_graph(...)` de la sesión anterior no lo detectó porque llama la función directo, sin pasar por ese chequeo. Corregido a mano en el servidor (`EMAIL_ENABLED=true` + recrear el backend) -- confirmar que quede así en cualquier entorno nuevo que reciba este puente.

Tests: `tests/test_email_templates.py` (una clase por plantilla — HTML válido, colores de estado correctos, escape de texto controlado por usuario, bloque de motivo condicional), `test_correo_saliente.py`/`test_api_reservas.py`/`test_api_usuarios.py` extendidos para confirmar `es_html=True` en cada punto de enganche real (crear reserva, cambiar estado, Feature B, reenviar invitación, crear usuario).

**Rediseño con identidad real del ITM (2026-08-28, mismo día, reemplaza la identidad "inventada" descrita arriba):** a pedido explícito, se reemplazó el azul académico/esmeralda de la app (Fase 6 de `app_flutter/`) por los colores REALES de la Facultad de Ingenierías, verificados swatch por swatch contra `Manual-ITM-V-2025.pdf` (el usuario lo compartió, página 7 "Colores secundarios para las facultades"): `#102D69` (navy), `#00A0B7` (teal), `#56ACDE` (celeste) — no relacionados con `_COLORES_ESTADO` (ese sigue siendo el sistema semántico de `notificaciones_sheet.dart`, ver arriba).

- **Logo real, no una recreación**: `_LOGO_ITM_B64` es un recorte de la página 2 del mismo manual (extraído con PyMuPDF, no una interpretación mía), reescalado y convertido a PNG paleta (~6.5KB) para no inflar el peso del correo.
- **Ícono de "bienvenida" en `plantilla_invitacion`**: ilustración plana genérica (figuras humanas simples, sin rostro ni fotografía real de nadie) tomada de un archivo de referencia (`reserva-parque-i-email-v2.html`) que el usuario ya tenía armado — deliberadamente NO se generó ninguna foto de una persona real: no hay forma de verificar ni generar de forma auténtica una foto de alguien del ITM.
- **Estructura HTML adoptada del mismo archivo de referencia**, más robusta que el primer intento de esta misma fecha: bloque condicional `<!--[if mso]>` (densidad de píxel para Outlook), texto de preheader oculto (`mso-hide:all`), `@media` de achicado a mobile (apila el header en una columna), tipografía Montserrat (la que el manual exige como corporativa obligatoria, página 5).
- **`SOPORTE_EMAIL = "reservaslabparquei@correo.itm.edu.co"`** — la cuenta real ya usada en el resto del proyecto (SMTP/Graph), no un placeholder.
- **Los botones/links de CTA solo los tiene `plantilla_invitacion`** (que ya tenía un link real, el de Supabase) — las plantillas de reserva (`pendiente`/`estado`/`actualizada`) NO ganaron un botón "Ingresá aquí": no hay una URL pública estable de la app configurada (`APP_BASE_URL` no existe como setting), así que agregar un botón ahí habría significado hardcodear la IP privada del bastión o inventar una dependencia nueva fuera del alcance de este pedido. Siguen con el mismo cierre de texto plano que ya tenían ("Ingresá al sistema de reservas para más detalles").
- **Peso final**: ambas imágenes juntas (~10-11KB) más el HTML de tablas (~15-20KB) quedan bien por debajo del límite de recorte de Gmail (~102KB) — el primer intento de este mismo día (con degradé CSS y sin logo real) pesaba menos pero se descartó por no usar assets reales.

## Autoregistro abierto (2026-08-28)

A pedido explícito del usuario del proyecto, confirmado tras advertirle que revertía (parcialmente) el diseño "solo un admin invita" ya documentado arriba: se agrega `POST /auth/registro` (público, sin autenticación) que crea una cuenta con rol `usuario` sin ninguna aprobación ni invitación de por medio. **No es lo mismo que el hueco de seguridad cerrado en `supabase_sesion`**: ese endpoint seguía prohibido de vincular o crear una cuenta a partir de un JWT ajeno; `POST /auth/registro` sigue sin tocar esa regla — solo agrega un camino nuevo, explícito y auditable para crear una cuenta **nueva** (username/email únicos, mismas validaciones 409 que `create_usuario_admin`), nunca vincula con una cuenta existente.

- **`RegistroRequest`** (`schemas/usuario.py`): `username`, `email`, `password` (`min_length=8`) — a diferencia de `UsuarioCreate` (sin `password`, porque la crea un admin vía invitación de Supabase), acá la persona elige su propia contraseña en el mismo formulario.
- **`registro()`** (`api/auth.py`) valida username/email únicos (409, mismo mensaje que `create_usuario_admin`), y llama `crear_usuario_confirmado(email, password)` (`services/supabase_admin.py`) — función que YA existía, hasta ahora reservada solo al bootstrap del admin inicial (`seed_admin_user`): crea la identidad de Supabase con la contraseña ya puesta y `email_confirm: True`, sin correo de invitación. Un fallo de Supabase da 502 y no crea la fila local (mismo orden que `create_usuario_admin`: primero Supabase, después la fila local, para no dejar cuentas locales sin `supabase_id`).
- **Rol fijo `usuario`, sin `espacio_id`**: `create_usuario(db, UsuarioCreate(...), supabase_id)` reutiliza el mismo `crud.create_usuario` que ya usa `create_usuario_admin`, con el default de `rol="usuario"` — no hay forma de autoregistrarse como `gestor` ni `admin`.
- **Sin restricción de dominio de correo** (decisión explícita: "autoregistro abierto, sin aprobación", ver `AskUserQuestion` de la sesión) — cualquier email con formato válido puede crear una cuenta. Si en el futuro se quiere acotar a `@itm.edu.co` o similar, es un `field_validator` adicional en `RegistroRequest`, no reabre ningún otro contrato.
- **El perfil (documento/teléfono/institución/vinculación/dependencia) sigue obligatorio** antes de poder usar el resto de la app — eso lo exige el guard ya existente de `app_router.dart` (Flutter, ver `app_flutter/CLAUDE.md`), no este endpoint: una cuenta recién autoregistrada aterriza igual en `/perfil`, igual que una invitada por un admin.
- Tests: `tests/test_api_auth.py` — éxito con rol `usuario`, 409 username duplicado, 409 email duplicado, 422 password corta (<8), 422 email inválido, 502 si falla Supabase (y no queda fila local huérfana). `openapi.snapshot.json` regenerado (endpoint + schema nuevos, puramente aditivo).

## Recuperación de contraseña también por nuestro outbox (2026-08-28)

A pedido explícito ("necesito que todo se envíe por Graph"): el único correo que hasta ahora seguía sin pasar por el outbox propio era la recuperación de contraseña, disparada 100% client-side por `AuthRepository.solicitarRecuperacion` (`resetPasswordForEmail` de Supabase) — ver "Migración a Supabase Auth" en `app_flutter/CLAUDE.md`. Se reemplaza por el mismo patrón ya usado para la invitación inicial (`crear_usuario_y_generar_link`): generar el link vía Supabase Admin API sin que Supabase mande su propio correo, y encolarlo nosotros mismos.

- **`generar_link_recuperacion(email)`** (`app/services/supabase_admin.py`) — mismo endpoint `/auth/v1/admin/generate_link` que `generar_link_invitacion`, pero `type=recovery`. A diferencia de `type=invite`, Supabase rechaza `recovery` para un email sin cuenta -- acá esa condición (y cualquier error de red/HTTP) se traduce a `None`, nunca a una excepción: el invariante de privacidad (misma respuesta exista o no la cuenta) tiene que sobrevivir intacto, y una excepción sin capturar lo rompería.
- **`POST /auth/recuperar`** (`app/api/auth.py`, público, sin autenticación) — `RecuperarPasswordRequest{email}` → siempre `204` sin body, exista o no la cuenta. Si `generar_link_recuperacion` devuelve `None`, o si el email no tiene un `Usuario` local (mismo caso raro que ya cubre `reenviar_invitacion_solo_admin`, cuenta de Supabase sin fila local), corta con `db.rollback()` antes del `return` -- defensivo, no hay ninguna escritura pendiente en ese punto, pero deja la sesión en un estado conocido en vez de depender del cierre implícito de `get_db`.
- **`plantilla_recuperacion_password(link, nombre_saludo="")`** (`app/services/email_templates.py`) -- mismo esqueleto que `plantilla_invitacion` (header/logo/footer compartidos, botón CTA vía `_boton`) pero sin el ícono de bienvenida (no aplica a este contexto) y con copy propio ("Restablecé tu contraseña").
- **Flutter**: `AuthRepository.solicitarRecuperacion` pasó de `Supabase.instance.client.auth.resetPasswordForEmail(email)` a `_dio.post('/auth/recuperar', data: {'email': email})` -- misma firma, mismo comportamiento observable desde `_RecuperarPasswordDialog` (que ya usaba `apiErrorMessage`/`on Object catch`, listo para un `DioException` sin cambios). El link que llega por correo sigue estableciendo la misma sesión temporal `passwordRecovery` que un link de invitación y termina en `CompletarCuentaScreen` -- ese mecanismo no cambió, solo quién dispara el envío del correo.
- **`supabase-template-recuperacion-password.html` (raíz del repo) queda obsoleto** -- Supabase ya no manda ningún correo de recuperación por su cuenta, así que esa plantilla (pensada para pegarse en su dashboard) no tiene ningún efecto. Se deja en el repo sin borrar, mismo criterio que `supabase-template-invitacion.html`.
- Tests: `tests/test_api_auth.py` (cuenta existente encola con `es_html=True`; cuenta inexistente responde 204 igual sin encolar nada; email con formato inválido da 422), `tests/test_email_templates.py::TestPlantillaRecuperacionPassword`.

## Confirmación por correo al crear una reserva (2026-08-28)

Gap real encontrado auditando los puntos de notificación existentes (`grep -rn "Notificacion(\|encolar_correo(" app/`): `crear_reserva` ya avisaba al gestor cuando una reserva quedaba pendiente (`plantilla_reserva_pendiente`), pero nunca le confirmaba nada a quien la creó -- ni en el caso pendiente ni en el de aprobación automática.

- **Caso pendiente** (`aprobacion_automatica=False`): además del correo al gestor, `crear_reserva` ahora encola `plantilla_reserva_recibida(...)` al propio solicitante -- contraparte textual de la de gestor ("Recibimos tu solicitud" en vez de "Tenés una reserva por aprobar"), mismo acento de color "pendiente" (`#d97706`, `_COLORES_ESTADO`).
- **Caso aprobación automática** (`aprobacion_automatica=True`, ya sea porque el espacio la tiene activada o porque un gestor reserva su propio espacio): no hay nada "pendiente" que confirmar, así que se reusa directamente `plantilla_reserva_estado(estado="aprobada")` -- la misma plantilla que ya usa `cambiar_estado` cuando un gestor aprueba a mano.
- **Deliberadamente sin `Notificacion` in-app nueva**: solo se agregó el correo, no un nuevo valor de `TipoNotificacion` ni una fila nueva en la campanita -- pedido explícito fue "correo al usuario", y agregar un tipo de notificación nuevo habría sido un cambio de contrato/UI fuera de lo pedido.
- Tests: `tests/test_correo_saliente.py` -- `test_crear_reserva_esperando_tambien_confirma_al_solicitante` y `test_crear_reserva_con_aprobacion_automatica_confirma_directamente_aprobada`; los dos tests preexistentes que asumían un único `CorreoSaliente` por reserva creada se ajustaron para filtrar por destinatario (ahora hay dos filas: gestor + solicitante).

**Gap adicional encontrado en la misma auditoría, ya resuelto (mismo día, confirmado con el usuario)**: `cancelar_reserva_usuario` (cuando el dueño cancela su propia reserva ya aprobada) no generaba ninguna `Notificacion` ni correo hacia el/la gestor/a que la había aprobado -- a diferencia de `cambiar_estado` (gestor → usuario), que sí cubre los tres estados en ese sentido.

- Ahora notifica (in-app + correo) a todos los gestores del espacio de la reserva, mismo patrón de consulta que ya usa `crear_reserva` para avisar de una reserva pendiente (`join` `UsuarioEspacio` filtrando `rol == gestor` y `espacio_id`).
- **No se reutilizó `TipoNotificacion.CANCELADA` a ciegas**: ese tipo ya existía para el sentido opuesto (gestor cancela → avisa al usuario dueño, `cambiar_estado`), y el mensaje in-app (`api/notificaciones.py::_mensaje`) estaba hardcodeado en segunda persona ("Tu reserva de X fue cancelada") -- mandárselo tal cual a un gestor que no es dueño de la reserva habría sido un mensaje engañoso. Se corrigió `_mensaje` para distinguir por destinatario (`notificacion.usuario_id != reserva.usuario_id` → "Se canceló la reserva de X", sin el "Tu"), reutilizando el mismo valor de enum -- no hizo falta un `TipoNotificacion` nuevo ni tocar el `CHECK` de la base.
- **Correo con plantilla propia**, `plantilla_reserva_cancelada_por_usuario` -- no se reutilizó `plantilla_reserva_estado` (misma razón: esa está redactada en segunda persona para el propio solicitante).
- Tests: `tests/test_correo_saliente.py::test_cancelar_reserva_usuario_notifica_al_gestor` (in-app + correo, mensaje sin "Tu"), `tests/test_api_notificaciones.py` para el caso de `_mensaje` con destinatario ≠ dueño.

## Correos faltantes: bienvenida, confirmación de contraseña, reserva eliminada (2026-08-29)

Auditoría a pedido explícito del usuario ("qué más correos necesitamos") sobre todos los puntos `encolar_correo(...)` existentes -- ver `email_templates.py` para el inventario completo. Se implementaron 3 de los 5 gaps encontrados (el usuario descartó "aviso de cambio de rol" y "aviso al eliminar una cuenta"):

- **`plantilla_bienvenida_autoregistro`**: `POST /auth/registro` (autoregistro abierto) no mandaba ningún correo -- a diferencia del alta por admin (`plantilla_invitacion`), quien se autoregistra no recibía ninguna confirmación de que su cuenta se creó.
- **`plantilla_password_actualizada` + `POST /auth/confirmar-cambio-password`** (nuevo endpoint, autenticado): el cambio de contraseña en sí es 100% client-side contra Supabase (`AuthRepository.completarCuenta` en Flutter, tanto para completar una invitación como una recuperación), así que este backend no tenía ningún hook para enterarse de que ocurrió. El cliente ya autenticado (tras `_intercambiarSesion`) llama a este endpoint nuevo para disparar la confirmación -- práctica de seguridad estándar (detectar un cambio que uno no hizo). Falla en modo best-effort del lado de Flutter: si el correo falla, no bloquea el login (la sesión ya es válida en ese punto).
- **`plantilla_reserva_eliminada`**: `DELETE /reservas/{id}` (`services/reservas.py::eliminar_reserva`, distinto de cancelar -- solo gestor/admin puede llamarlo) no notificaba a nadie. Ahora avisa al dueño de la reserva (`reserva.actor`) SOLO si quien elimina no es el propio dueño (un gestor borrando su propia reserva no se autonotifica).

**Bug real preexistente encontrado en el camino, corregido**: al escribir el test de `DELETE /reservas/{id}` -- **el primero que existe para ese endpoint en toda la suite**, nunca se había probado antes -- el borrado de una reserva con recursos/zonas asociados reventaba con `IntegrityError: NotNullViolation` en `reserva_recursos.reserva_id`. Causa: `Reserva.recursos_asociados`/`zonas_asociadas` (`app/models/reserva.py`, Fase 12C-6) tenían `passive_deletes=True` pero les faltaba `cascade="all, delete-orphan"` -- sin el cascade, SQLAlchemy intenta poner `reserva_id=NULL` en las filas asociadas al borrar la reserva en vez de dejar que la base de datos cascadee (la FK real ya tenía `ondelete="CASCADE"` desde siempre). `Reserva.acompanantes` ya tenía el patrón correcto (`cascade` + `passive_deletes` juntos) -- se alineó `recursos_asociados`/`zonas_asociadas` al mismo patrón. Sin cambio de esquema (la FK ya cascadeaba a nivel de base de datos), solo corrige la configuración de la ORM.

Tests: `tests/test_api_auth.py` (bienvenida al registrarse, `confirmar-cambio-password` para usuario y personal, 401 sin sesión), `tests/test_correo_saliente.py` (gestor elimina la reserva de otro → notifica; gestor elimina la propia → no se autonotifica). `openapi.snapshot.json` regenerado (solo `POST /auth/confirmar-cambio-password` nuevo). 705/705 en verde.

## Separación `personal`/`usuarios` en tablas SQL reales (2026-08-28)

A pedido explícito del usuario del proyecto ("al momento de registrar un gestor va a la tabla de personal y al momento que se registre un usuario de reserva va a una tabla de usuario") -- confirmado vía `AskUserQuestion` que era separación real en la base de datos, no solo visual en la UI. Diseño completo y decisiones no obvias en `~/.claude/plans/dazzling-wobbling-zebra.md` (fuera del repo). Reemplaza toda mención anterior en este archivo de "`usuarios` con rol admin/gestor/usuario" para roles `admin`/`gestor`: esos ahora viven en `personal`.

- **Tabla nueva `personal`** (`app/models/personal.py`): mismas columnas de perfil que `Usuario`, sin las vestigiales de Supabase (`hashed_password`, `debe_cambiar_password` -- tabla nueva, no arrastra ese vestigio). `rol` con `CheckConstraint` propio (`admin`/`gestor` únicamente). `Usuario`/`usuarios` se queda tal cual (mismo id space, mismas columnas) pero desde esta separación solo contiene rol `usuario` -- no se le dropea la columna `rol` (nunca se hace DROP COLUMN en este proyecto), queda redundante.
- **9 FK repuntadas de `usuarios.id` a `personal.id`**: `usuarios_espacios.usuario_id`, `recursos.created_by`/`update_by`, `zonas.created_by`/`updated_by`, `ensayos.created_by`/`updated_by`, `espacios.created_by`/`updated_by` -- todas gateadas por `require_admin`/`require_resource_manager`, nunca las toca un rol `usuario`.
- **3 tablas polimórficas** (`reservas`, `notificaciones`, `control_cambios`): un gestor también reserva su propio espacio, recibe notificaciones de su espacio, y aparece en la auditoría -- por eso `usuario_id` pasó a nullable y cada una ganó `personal_id` nullable + `CHECK` de "exactamente una llena" (`control_cambios` admite además las dos en NULL, ya lo permitía su `ondelete=SET NULL` previo). `Reserva.actor`/`Notificacion.actor`/`ControlCambio.actor` (`@property`) devuelven `self.usuario or self.personal`. `app/services/actores.py` centraliza `columnas_actor(actor)` (qué columna llenar al crear) y `es_actor(entidad, actor)`/`mismo_actor(a, b)` (comparar identidad sin ambigüedad de tabla) -- reusado en `services/reservas.py`, `services/auditoria.py`, `api/notificaciones.py`.
- **Migración** (`app/migrations.py`, al final de `migrate_resource_reservations()`): copia admin/gestor de `usuarios` a `personal` preservando el mismo `id` (`INSERT ... id` explícito + `setval` -- solo es seguro acá porque `personal` arranca vacía; ver el punto siguiente para por qué NO se repite ese truco en runtime), repunta las 9 FK, habilita el polimorfismo + backfill + `CHECK` en las 3 tablas, borra de `usuarios` al final. Todo dentro de la misma transacción de siempre, idempotente (verificado corriendo la suite completa varias veces seguidas contra la misma `reservas_test`).
- **Cambio de rol que cruza la frontera** (`usuario` -> `gestor`/`admin` o viceversa) NO es un `UPDATE`: `app/services/migrar_actor.py::promover_a_personal`/`degradar_a_usuario` insertan en la tabla destino y repuntan reservas/notificaciones/auditoría existentes. **A diferencia de la migración inicial, acá NO se preserva el mismo `id`** -- `personal`/`usuarios` tienen secuencias `SERIAL` independientes que arrancan igual en 1, 2, 3... y ya pueden tener filas propias en el momento de la promoción/degradación (a diferencia de la migración inicial, que mueve hacia una tabla todavía vacía); reusar el id viejo colisionaría. Se deja que la tabla destino asigne uno nuevo (`RETURNING id`) y se repuntan las referencias a ese id nuevo. Bug real encontrado y corregido durante el desarrollo de esta misma fase (test `test_promover_usuario_existente_a_gestor` lo cubre).
- **`GET/POST/PUT/DELETE /usuarios`** ahora es rol `usuario` únicamente (sin `rol`/`espacio_id`, que ya no aplican -- `AdminUsuarioCreate` se retiró, `POST /usuarios` reusa directamente `UsuarioCreate`). **`/personal` es un router nuevo** (`app/api/personal.py`) con la misma forma de CRUD que antes tenía `/usuarios` para admin/gestor, más `POST /personal/promover/{usuario_id}` (asciende una cuenta `usuario` existente). `PUT /usuarios/{id}` con `rol=usuario` en el body es la señal de degradación (`schemas/personal.py::PersonalUpdate.rol` doc). `degradar_a_usuario` puede fallar con 409 si la persona todavía figura como `created_by`/`updated_by` de algún recurso/zona/ensayo/espacio -- no se detecta a mano, se deja que la FK real (sin `ON DELETE`) lo rechace y se traduce el `IntegrityError`.
- **Unicidad de `username`/`email` cruzada**: PostgreSQL solo la garantiza dentro de cada tabla por separado -- `app/crud/identidad.py` (`buscar_por_username`/`buscar_por_email`/`buscar_por_supabase_id`, consultan ambas tablas) reemplaza los checks 409 que antes solo miraban `usuarios`. `actualizar_perfil` (mismo módulo) también quedó compartido: `PUT /usuarios/me` funciona igual para `Personal` que para `Usuario`, los 5 campos de perfil tienen el mismo nombre en los dos modelos.
- **`app/deps.py::_usuario_por_sub`** prueba `personal` antes que `usuarios` al resolver la sesión (`crud/identidad.py::buscar_por_supabase_id`); `get_current_user`/`require_admin`/`require_resource_manager`/`get_managed_space_id` devuelven/reciben `Personal | Usuario` según corresponda.
- **`UsuarioResponse` no cambió de forma** y se reusa tal cual para las respuestas de `/personal` (misma forma exacta: `id`/`username`/`email`/`rol`/`espacio`/campos de perfil) -- no se creó un `PersonalResponse` aparte, sería una duplicación sin beneficio. `ReservaResponse`/`NotificacionResponse` tampoco cambiaron: la resolución "¿esta fila es de `personal` o `usuarios`?" se hace del lado del servidor (`_ReservaConActorNormalizado`, proxy de solo lectura en `schemas/reserva.py` que resuelve `usuario_id`/`usuario` desde `Reserva.actor` sin tocar el resto de los campos).
- Tests: `tests/conftest.py::crear_usuario` cambia de implementación (no de firma) -- `rol="admin"|"gestor"` crea en `Personal`, cualquier otro valor en `Usuario`; los ~330 sitios que ya lo llaman no se tocaron, solo leen atributos que ambos modelos exponen igual. `crear_recurso`/`crear_zona` (mismo archivo) ganan `_personal_para_fk`: si el `usuario` que reciben no es `Personal` (muchos tests pasan cómodamente el mismo objeto que usan como dueño de la reserva), crean/reusan un admin de pruebas dedicado -- evita tener que tocar los ~150 sitios que llaman a esos dos helpers. `tests/test_api_usuarios.py` se acotó a rol `usuario`; `tests/test_api_personal.py` (nuevo) cubre admin/gestor, incluida la promoción/degradación. Suite completa: 701/701 contra `reservas_test`.
- `openapi.snapshot.json` regenerado: rutas nuevas bajo `/personal`, `AdminUsuarioCreate` retirado, `UsuarioUpdate` sin `rol`/`espacio_id` -- sin cambios en `/reservas`, `/notificaciones`, `/admin/control-cambios`, `/auth/*`.

**Bug crítico real encontrado y corregido antes de cerrar esta fase**: `app/api/auth.py` (login, autoregistro, recuperación de contraseña) importaba `get_usuario_by_email`/`get_usuario_by_username`/`get_usuario_by_supabase_id` directo de `crud/usuarios.py` -- funciones que SOLO miran la tabla `usuarios`, nunca `personal`. Como `POST /auth/supabase/sesion` es el endpoint de intercambio de sesión que usa TODO login real (Flutter, tras `signInWithPassword`), esto significaba que **ningún admin ni gestor real podía iniciar sesión** tras la separación -- 403 "cuenta no asociada" para cualquiera de ellos. Los 697 tests de la suite completa pasaban igual porque los ~10 tests de `test_supabase_sesion_*` preexistentes usaban `crear_usuario(...)` con el rol default (`usuario`), ninguno ejercitaba un login de personal a través de este endpoint específico -- la cobertura de `deps.py`/`get_current_user` (que sí se había corregido) enmascaraba el problema en el resto de la suite, porque esas pruebas fijan la cookie a mano (`cookies_para`) sin pasar por `/auth/supabase/sesion`. Corregido reemplazando esos tres imports por `crud/identidad.py::buscar_por_email/buscar_por_username/buscar_por_supabase_id` (cross-table) en los tres endpoints de `api/auth.py` (login, `/auth/registro`, `/auth/recuperar` -- los tres tenían el mismo gap). Cobertura nueva agregada específicamente para este caso: `test_supabase_sesion_exitosa_con_personal_admin_o_gestor`, `test_registro_username_duplicado_contra_personal_da_409`, `test_registro_email_duplicado_contra_personal_da_409`, `test_recuperar_password_cuenta_de_personal_tambien_encola_el_correo` (`tests/test_api_auth.py`). Lección: cuando una entidad se divide en dos tablas, hay que auditar TODOS los `import` directos de funciones "por tabla" en el código, no solo el más obvio (`deps.py`) -- un grep de `get_usuario_by_` tras terminar el cambio es lo que lo encontró.

## Reglas de autorización

Un gestor solo puede estar asignado a un espacio. No se puede eliminar ni degradar la propia cuenta administrativa, y siempre debe quedar al menos un `admin` en el sistema (protegido con advisory lock en `proteger_administradores`).

## Migraciones SQL idempotentes sin Alembic

No hay Alembic. El esquema evoluciona en `app/migrations.py` mediante SQL idempotente (`ADD COLUMN IF NOT EXISTS`, bloques `DO $$`), ejecutado en cada arranque después de `Base.metadata.create_all`. Cualquier cambio de esquema nuevo debe seguir ese mismo patrón.

## Compatibilidad de constraints

La exclusión `reservas_sin_solapamiento` (extensión `btree_gist`, estados `esperando`/`aprobada`) la aplica PostgreSQL. El servicio valida antes de escribir; un `IntegrityError` de esa constraint se traduce a HTTP 409 (`_traducir_error_integridad`), nunca debe propagarse crudo al cliente.

## Comandos pytest

```bash
cd backend
pytest -v                              # suite completa
pytest tests/test_lifespan_arranque.py -v   # solo lifespan
```

Orden crítico si se ejecuta manualmente fuera de la suite: fijar `DATABASE_URL`/`SECRET_KEY` → importar `app` → `create_all` → `migrate_resource_reservations()` → ejecutar. Importar `app.*` antes de fijar el entorno apuntaría al motor de la base de desarrollo.

## No modificar schemas/OpenAPI sin aprobación

Ningún cambio en `app/schemas/`, en los routers de `app/api/` ni en el OpenAPI generado debe hacerse sin aprobación explícita del usuario, dado que el frontend y los E2E dependen del contrato actual.

## No cambiar endpoints sin pruebas de contrato

Todo cambio de comportamiento en un endpoint debe ir acompañado de la actualización o creación del test correspondiente en `backend/tests/` (ver [backend/tests/CLAUDE.md](tests/CLAUDE.md)) antes de darse por terminado.
