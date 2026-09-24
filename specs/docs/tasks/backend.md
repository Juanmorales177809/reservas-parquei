# Plan de tareas — Backend nuevo

Cómo se construye el backend desde cero. Las tareas de superficie HTTP están en el [plan de contratos](contratos.md) como `API-XX`; este documento cubre lo anterior a ellas: dónde vive el proyecto, con qué estructura y en qué orden se levanta.

Plan general: [`tasks.md`](../../../tasks.md) de la raíz.

---

## Punto de partida

| Qué | Estado |
|---|---|
| El código anterior de `backend/` y `frontend/` | **Borrado.** 109 archivos, contra un contrato que ya no rige |
| `backend/migrations/` | **Rescatado.** `002`, `003` y el respaldo estructural, idénticos al original |
| `backend/tests/sql/` | **Rescatado.** Las consultas que verifican el ajuste |
| La base `reservas_db` | **Intacta**, con sus 28 tablas en el schema `reservas`, todas vacías |
| `docker-compose.yml` | Conserva `db` y `pgadmin`; los servicios de aplicación se reintroducen en `BK-03` |
| Los nueve contratos | Escritos y cotejados contra modelos, reglas y flujos |

El backend anterior implementaba un contrato distinto: credencial por `username`, token en el cuerpo de la respuesta, `rol` dentro del JWT, sin sesiones ni CSRF. Se retiró entero en lugar de adaptarlo pieza a pieza.

**Se conservó lo que no es código de aplicación**: las migraciones que gobiernan el esquema y las consultas que verifican que se aplicó bien. `001_shared_postgres.sql` no se rescató: pertenecía al arranque anterior, que es justamente lo que no se repite.

Por tanto **el punto de partida para escribir código es `backend/app/`, que está vacío**, contra una base que ya tiene la forma correcta.

**El stack no se decide aquí.** `architecture.md` §3 lo fija: FastAPI, Python, SQLAlchemy, Pydantic, Uvicorn, PostgreSQL 13, JWT con bcrypt y Docker Compose.

---

## Tres reglas de construcción

**1. El backend nunca crea ni modifica tablas.** El esquema lo gobiernan las migraciones versionadas de `backend/migrations/`, conforme a `architecture.md` §15. No hay `create_all` ni creación al arrancar. Era el defecto del backend anterior, que `DB-13` señalaba: su arranque podía recrear tablas que el ajuste había retirado.

**2. La superficie se deriva del contrato, no al revés.** Cada ruta, cada campo del cuerpo y cada código de error ya están escritos. Si al implementar aparece algo que el contrato no contempla, se corrige el contrato primero y se implementa después; no se añade al código y se documenta luego.

**3. Los módulos no se llaman entre sí por HTTP.** Comparten proceso y base. Un módulo que necesita algo de otro usa su capa de servicios, respetando la propiedad de cada tabla. El contrato interno de auth (`exigir_permiso`, contexto autenticado) es el ejemplo a seguir.

---

## Dónde vive

```text
backend/
  app/
    core/                   <- lo transversal: errores, paginación, sesión, permisos
    db/                     <- sesión de SQLAlchemy y modelos por schema
    modules/
      auth/                 <- router, esquemas, servicios y repositorio
      usuarios/
      administration/
      researchs/
      resources/
      espacios/
      reservations/
      notifications/
      reports/
    main.py
  migrations/               <- 002 y 003, rescatados en BK-00
  tests/
  Dockerfile
  requirements.txt
```

La misma ruta que antes, ahora vacía. `docker-compose.yml` volverá a construir `./backend` en `BK-03`.

Cada módulo tiene la misma forma interna —`router.py`, `schemas.py`, `service.py`, `repository.py`— para que la capa donde vive una regla sea evidente: el router traduce HTTP, el servicio aplica las `RN` y el repositorio habla con la base.

**Los módulos son los nueve de las especificaciones**, con sus mismos nombres. Un módulo del backend que no corresponda a uno documentado es señal de que la superficie se está inventando.

---

## Convención de tarea

```markdown
### BK-XX — Título

- **Objetivo:** qué queda distinto al terminar.
- **Afectados:** archivos concretos.
- **Dependencias:** qué debe cerrarse antes.
- **Aceptación:** condición verificable, escrita como comando o petición.
```

---

## Hito 0 — Que arranque

Al cerrarlo existe un servicio que responde y se conecta a la base, sin lógica de negocio.

### BK-00 — Rescatar las migraciones · **cerrada**

- **Objetivo:** `backend/migrations/` vuelve a contener el script que produjo el esquema vivo y el que queda pendiente.
- **Resultado:** rescatados de `2b32ea2` y verificados idénticos por hash: `002_reservas_objetivo.sql`, `003_reservas_referencias_externas.sql`, el respaldo `20260923_reservas_antes.sql` y las pruebas `tests/sql/reservas_objetivo.sql`. No se rescató `001_shared_postgres.sql`.
- **Queda pendiente de esta tarea:** nada. `003` sigue sin ejecutarse, que es `DB-05`, y el mecanismo de migraciones sigue sin fijarse, que es `DB-13`.

### BK-01 — Crear el proyecto

- **Objetivo:** `backend/` expone `GET /health` e instala sus dependencias.
- **Afectados:** `backend/requirements.txt`, `backend/app/main.py`, `backend/Dockerfile`.
- **Dependencias:** ninguna.
- **Aceptación:** `uvicorn app.main:app` levanta y `GET /health` devuelve `200`. **No abre conexión a la base.**

### BK-02 — Conectar a PostgreSQL sin crear nada · **cerrada**

- **Objetivo:** hay una sesión de SQLAlchemy configurada por variable de entorno.
- **Afectados:** `backend/app/db/session.py`, `backend/app/core/config.py`, `backend/app/main.py`, `backend/requirements.txt`.
- **Dependencias:** BK-01.
- **Aceptación:** `GET /health` informa si la base responde. **Arrancar dos veces seguidas no crea ni altera ninguna tabla**: el conteo de tablas de `reservas` sigue siendo 28.
- **Resultado:** verificado contra `reservas_db` real, en su red de Docker, dos arranques consecutivos: `{"estado":"ok","base_de_datos":"conectada"}` ambas veces y 28 tablas antes y después. Sin base alcanzable responde `200` con `"sin_conexion"`, nunca un error sin controlar. `DATABASE_URL` se construye desde `POSTGRES_*` y admite anularse.

### BK-03 — Añadir el servicio a Docker Compose · **cerrada**

- **Objetivo:** el backend corre junto a `db` y `pgadmin`.
- **Afectados:** `docker-compose.yml`.
- **Dependencias:** BK-01.
- **Aceptación:** `docker compose up` levanta la base y el backend, y `GET /health` responde desde el contenedor. **El servicio hay que crearlo**: se retiró al borrar el código anterior, porque apuntaba a una carpeta inexistente y rompía `docker compose up`. Se declara con lo que el backend necesita hoy —la cadena de conexión y poco más— **sin arrastrar las variables del arranque anterior** (`INITIAL_ADMIN_*`, `ALGORITHM`), que pertenecían a un modelo retirado. El servicio `frontend` tampoco existe y no se reintroduce aquí.
- **Resultado:** verificado con `docker compose up -d --build backend`: construye, arranca junto a `db` ya saludable, y `curl http://localhost:8000/health` desde el host devuelve `{"estado":"ok","base_de_datos":"conectada"}`. Puerto `8000` expuesto, configurable por `BACKEND_HOST_PORT`.

---

## Hito 1 — El núcleo transversal

Es lo que hace que los nueve módulos se comporten igual, y **ninguna ruta de negocio se escribe antes de cerrarlo**.

`BK-04` a `BK-07` **son** `API-01` a `API-04`: el mismo trabajo visto desde el proyecto en vez de desde el contrato. No son dos tareas cada una. **Manda la `BK-XX`**, que nombra los archivos; la `API-XX` aporta el criterio de aceptación escrito como petición y se cierra con ella.

### BK-04 — Envolvente de error y catálogo común · **cerrada**

- **Objetivo:** toda excepción sale como `{"error": {"codigo", "mensaje", "detalles"}}`.
- **Afectados:** `backend/app/core/errors.py`, manejadores en `main.py`.
- **Dependencias:** BK-01. Cubre `API-01`.
- **Aceptación:** una ruta inexistente devuelve `404 NO_ENCONTRADO` con esa forma, no el `detail` de FastAPI. Una excepción no controlada devuelve `500 ERROR_INTERNO` **sin traza en la respuesta**.
- **Resultado:** `DomainError` y una subclase por cada uno de los catorce códigos comunes de `contratos/README.md` §2, más manejadores para `RequestValidationError` (422 `VALIDACION`, con `detalles` de campo/motivo sin el valor enviado) y `StarletteHTTPException` (404/405 → `NO_ENCONTRADO`). Verificado con peticiones reales contra el contenedor: 404 en ruta inexistente, 500 sin traza ni el mensaje original de una excepción con datos sensibles, 422 con dos campos inválidos. `DemasiadosIntentos` añade el encabezado `Retry-After` cuando se indica.

### BK-05 — Paginación, filtros y orden · **cerrada**

- **Objetivo:** una dependencia reutilizable que todo listado usa.
- **Afectados:** `backend/app/core/pagination.py`.
- **Dependencias:** BK-04. Cubre `API-02`.
- **Aceptación:** un listado devuelve `datos` + `paginacion`; un filtro desconocido devuelve `400 SOLICITUD_INVALIDA`; un catálogo cerrado devuelve solo `datos` y rechaza `pagina`.
- **Resultado:** `paginacion_para(filtros_admitidos, ordenes_admitidos)` y `catalogo_cerrado_para(filtros_admitidos)`, dos fábricas de dependencia que cada endpoint instancia con lo suyo. Verificado con peticiones reales: 137 elementos con `tamano=20` dan `paginas: 7`; filtro desconocido, campo de orden no admitido, `pagina=0` y `tamano=500` responden los cuatro `400 SOLICITUD_INVALIDA`; el catálogo cerrado devuelve solo `datos` y rechaza tanto `pagina` como un filtro no declarado.

### BK-06 — Sesión por cookie y CSRF · **cerrada**

- **Objetivo:** identidad desde la sesión y doble envío obligatorio en toda escritura.
- **Afectados:** `backend/app/core/security.py`, `backend/app/modules/auth/`.
- **Dependencias:** BK-04. Cubre `API-03`.
- **Aceptación:** un `POST` sin `X-CSRF-Token` devuelve `403` aunque la sesión sea válida. El JWT **no contiene rol ni permisos**. `GET /api/auth/csrf` emite la cookie sin sesión previa.
- **Resultado:** `security.py` trae `emitir_token_acceso`/`verificar_token_acceso` (HS256 fijo, `iss`/`aud`/`typ` validados, claims exactos del contrato), las cookies `rp_access`/`rp_refresh`/`rp_csrf` con sus atributos y rutas del contrato §2, y `exigir_csrf` de doble envío. `GET /api/auth/csrf` es el primer endpoint real del módulo auth.
  Verificado con peticiones reales: `rp_csrf` se conserva entre llamadas (sin `Set-Cookie` si ya existe) y se emite si falta; `POST` sin encabezado, con valor incorrecto y con el valor correcto dan `403`, `403` y `200`; los claims del JWT no traen rol ni permisos; `alg:none`, algoritmo distinto, `aud` ajena, `typ` incorrecto y un token vencido se rechazan los cinco. **No verifica revocación de sesión**: eso exige `auth.sesiones` y es de `BK-07`/`AUTH-A3` en adelante — está anotado en el propio módulo, no se presenta como hecho.
  - **`JWT_SECRET`** se añadió a `docker-compose.yml` y `.env.example`, sin valor por defecto real; `security.py` aborta al firmar si falta, no Compose al arrancar, para no romper `docker compose up -d db`.

### BK-07 — `exigir_permiso` con ámbito · **cerrada**

- **Objetivo:** una dependencia que resuelve permiso y unidad en cada operación, y deriva rol y unidades autorizadas.
- **Afectados:** `backend/app/core/authz.py`.
- **Dependencias:** BK-06, **DB-14**, que crea `auth.permisos` y `auth.cuenta_permisos`, y **DB-09**, que carga el catálogo.
- **Aceptación:** un Técnico sobre una unidad ajena recibe `403`, o `404` cuando revelar la existencia sea una fuga. Si el permiso no puede comprobarse, **deniega**. `unidades_autorizadas` de un Técnico contiene **solo la unidad vigente de su cargo**, nunca la unión de sus asignaciones; la de un Administrador es `"GLOBAL"`.
- **Resultado:** `resolver_rol(sesion, id_cuenta)` deriva `ADMINISTRADOR`/`TECNICO`/`USUARIO` conforme a `auth/data-model.md`, y `exigir_permiso(sesion, id_cuenta, codigo, id_unidad=None)` evalúa un código concreto. Recibe `id_cuenta` ya resuelto: conectarlo con la cookie de sesión es `AUTH-A6` (`BK-09`), que construye sobre esto.
  Verificado contra `reservas_db` real con datos de prueba sembrados y revertidos en una sola transacción (0 filas remanentes al terminar), nueve casos: rol y `unidades_autorizadas` de Técnico, Administrador y Usuario; Técnico con permiso en su unidad permite; Técnico sobre unidad ajena deniega **sin comprobar el permiso**; cuenta sin ningún permiso, código no asignado y cuenta inexistente deniegan sin excepción sin controlar; Administrador con asignación global permite en cualquier unidad.
  - **`404` cuando revelar la existencia sea una fuga** no es de esta capa: `exigir_permiso` solo sabe de permiso y unidad, nunca de si un recurso concreto existe. Esa conversión 403→404 la decide el servicio propietario del recurso (`SEC-AUTZ-06`), cuando lo construya.

---

## Hito 2 — Los modelos

### BK-08 — Modelar las tablas que existen · **cerrada**

- **Objetivo:** modelos SQLAlchemy de `reservas` (28 tablas), `auth`, `usuarios`, `personal`, `cargos`, `unidadOrganizacional` e `investigacion` en lo que ya existe.
- **Afectados:** `backend/app/db/models/`.
- **Dependencias:** BK-02 y **DB-14**, que añade las cinco tablas de `auth` que hoy faltan.
- **Aceptación:** una consulta a cada tabla se ejecuta sin error. **Ningún modelo declara una tabla que la base no tenga**, y ninguno se marca como creable.
- **Alcance de `auth`:** las **seis** tablas, es decir `auth.cuentas`, que ya existía, y las cinco que crea `DB-14`. El plan de auth las consume, no las modela. (Corrección: el texto original de esta tarea decía «siete»; `1 + 5 = 6`.)
- **Nota:** `recursos`, `administration` y `notificaciones` **existen desde `DB-01` a `DB-04`, cerradas en esta misma fase, pero deliberadamente no se modelan aquí**: no estaban en el alcance original de esta tarea, y modelarlas sin que ningún endpoint las use todavía es exactamente el riesgo que esta nota advertía. Se modelan con el primer `API-XX` de su propio módulo (`API-09`, `API-07`/`API-08`, `API-17`/`API-18`).
- **Resultado:** 51 clases declarativas de SQLAlchemy 2.0, generadas por introspección directa de `reservas_db` (no transcritas a mano) para garantizar que ningún modelo describe una columna, tipo o FK que la base no tenga exactamente así. Cuatro archivos: `reservas.py` (28), `auth.py` (6), `investigacion.py` (13), `identidad.py` (`usuarios`, `personal`, `cargos`, `unidadOrganizacional`: 1 cada uno). Verificado con una consulta real a las 51 tablas —cero fallos— y una comparación explícita contra `information_schema`: cero mapeadas que no existan, cero existentes sin mapear. Las columnas técnicas `periodo`/`bloqueante` de `reserva_espacio`/`reserva_recursos` quedan anotadas como proyecciones que ningún servicio debe escribir directamente. Ningún `Base.metadata.create_all` en ningún sitio.

---

## Hito 3 — El primer módulo completo

### BK-09 — Auth de punta a punta · **en progreso**

- **Objetivo:** los 17 endpoints del contrato de auth, funcionando. Dieciséis se construyen aquí; `GET /api/auth/csrf` ya lo entregó `BK-06`.
- **Afectados:** `backend/app/modules/auth/`.
- **Dependencias:** Hito 1, BK-08 y **DB-14**. Desarrolla `API-05`; el desglose está en [modules/auth/tasks.md](../../modules/auth/tasks.md), que es el documento que manda al implementarlo.
- **Aceptación:** la del plan de auth. Además, **auth queda como la referencia de estilo**: cualquier módulo posterior que se estructure distinto se corrige, no se justifica.
- **Avance:** Fase 1 del plan de auth cerrada (`AUTH-A1` a `AUTH-B5`, 9 tareas) y `AUTH-C1` (auditoría) también: los 16 endpoints funcionan y dejan su registro en `administration.auditoria`, verificados con peticiones reales contra `reservas_db`. Solo faltan `AUTH-T1`/`AUTH-T2` —pruebas formales, sin framework instalado todavía— para cerrar este hito.

Al cerrar este hito hay un módulo entero contra el contrato nuevo, y las decisiones difíciles —sesiones, CSRF, ámbito, forma del error— ya están tomadas en código, no solo en documento.

---

## Hito 4 en adelante

El orden es el del [plan general](../../../tasks.md): identidad, estructura institucional, catálogos, reservas, y por último notificaciones y reportes. Cada módulo es una tarea `API-XX` y no necesita una `BK-XX` propia: a partir de aquí el plan de contratos manda.

Lo único que este documento añade para esa etapa es la condición de entrada: **un módulo no empieza hasta que existan sus tablas**. Resources no se implementa antes de `DB-01`, researchs antes de `DB-02`, administration antes de `DB-03` ni notifications antes de `DB-04`.

---

## El frontend

Se borró con el backend y **no tiene plan todavía**. Construirlo exige antes tener API contra la que trabajar: el orden natural es después de `BK-09`, cuando auth funcione de punta a punta y haya una sesión real que consumir.

`architecture.md` §3 fija su stack —Next.js 14, React 18, TypeScript, Tailwind y Recharts—, así que esa parte tampoco se decidirá entonces.
