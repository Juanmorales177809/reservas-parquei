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
