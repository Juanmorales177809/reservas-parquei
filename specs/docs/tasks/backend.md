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
  migrations/               <- se rescatan 002 y 003 del commit 2b32ea2
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

### BK-02 — Conectar a PostgreSQL sin crear nada

- **Objetivo:** hay una sesión de SQLAlchemy configurada por variable de entorno.
- **Afectados:** `backend/app/db/session.py`, `backend/app/core/config.py`.
- **Dependencias:** BK-01.
- **Aceptación:** `GET /health` informa si la base responde. **Arrancar dos veces seguidas no crea ni altera ninguna tabla**: el conteo de tablas de `reservas` sigue siendo 28.

### BK-03 — Añadir el servicio a Docker Compose

- **Objetivo:** el backend corre junto a `db` y `pgadmin`.
- **Afectados:** `docker-compose.yml`.
- **Dependencias:** BK-01.
- **Aceptación:** `docker compose up` levanta la base y el backend. El servicio ya existe y construye `./backend`; hay que revisar sus variables de entorno, que hoy incluyen las del arranque anterior (`INITIAL_ADMIN_*`, `ALGORITHM`). El servicio `frontend` apunta a una carpeta que seguirá siendo la antigua hasta que se rehaga.

---

## Hito 1 — El núcleo transversal

Es lo que hace que los nueve módulos se comporten igual. Implementa las tareas `API-01` a `API-04` del plan de contratos, y **ninguna ruta de negocio se escribe antes de cerrarlo**.

### BK-04 — Envolvente de error y catálogo común

- **Objetivo:** toda excepción sale como `{"error": {"codigo", "mensaje", "detalles"}}`.
- **Afectados:** `backend/app/core/errors.py`, manejadores en `main.py`.
- **Dependencias:** BK-01. Cubre `API-01`.
- **Aceptación:** una ruta inexistente devuelve `404 NO_ENCONTRADO` con esa forma, no el `detail` de FastAPI. Una excepción no controlada devuelve `500 ERROR_INTERNO` **sin traza en la respuesta**.

### BK-05 — Paginación, filtros y orden

- **Objetivo:** una dependencia reutilizable que todo listado usa.
- **Afectados:** `backend/app/core/pagination.py`.
- **Dependencias:** BK-04. Cubre `API-02`.
- **Aceptación:** un listado devuelve `datos` + `paginacion`; un filtro desconocido devuelve `400 SOLICITUD_INVALIDA`; un catálogo cerrado devuelve solo `datos` y rechaza `pagina`.

### BK-06 — Sesión por cookie y CSRF

- **Objetivo:** identidad desde la sesión y doble envío obligatorio en toda escritura.
- **Afectados:** `backend/app/core/security.py`, `backend/app/modules/auth/`.
- **Dependencias:** BK-04. Cubre `API-03`.
- **Aceptación:** un `POST` sin `X-CSRF-Token` devuelve `403` aunque la sesión sea válida. El JWT **no contiene rol ni permisos**. `GET /api/auth/csrf` emite la cookie sin sesión previa.

### BK-07 — `exigir_permiso` con ámbito

- **Objetivo:** una dependencia que resuelve permiso y unidad en cada operación.
- **Afectados:** `backend/app/core/authz.py`.
- **Dependencias:** BK-06 y **DB-09**, que carga el catálogo de permisos.
- **Aceptación:** un Técnico sobre una unidad ajena recibe `403`, o `404` cuando revelar la existencia sea una fuga. Si el permiso no puede comprobarse, **deniega**.

---

## Hito 2 — Los modelos

### BK-08 — Modelar las tablas que existen

- **Objetivo:** modelos SQLAlchemy de `reservas` (28 tablas), `auth`, `usuarios`, `personal`, `cargos`, `unidadOrganizacional` e `investigacion` en lo que ya existe.
- **Afectados:** `backend/app/db/models/`.
- **Dependencias:** BK-02.
- **Aceptación:** una consulta a cada tabla se ejecuta sin error. **Ningún modelo declara una tabla que la base no tenga**, y ninguno se marca como creable.
- **Nota:** `recursos`, `administration`, `notificaciones` y el resto de `investigacion` **no se modelan todavía**: no existen hasta `DB-01` a `DB-04`. Modelarlos antes produce código que no se puede probar.

---

## Hito 3 — El primer módulo completo

### BK-09 — Auth de punta a punta

- **Objetivo:** los 17 endpoints del contrato de auth, funcionando.
- **Afectados:** `backend/app/modules/auth/`.
- **Dependencias:** Hito 1 y BK-08. Desarrolla `API-05`; el desglose está en [modules/auth/tasks.md](../../modules/auth/tasks.md).
- **Aceptación:** la del plan de auth. Además, **auth queda como la referencia de estilo**: cualquier módulo posterior que se estructure distinto se corrige, no se justifica.

Al cerrar este hito hay un módulo entero contra el contrato nuevo, y las decisiones difíciles —sesiones, CSRF, ámbito, forma del error— ya están tomadas en código, no solo en documento.

---

## Hito 4 en adelante

El orden es el del [plan general](../../../tasks.md): identidad, estructura institucional, catálogos, reservas, y por último notificaciones y reportes. Cada módulo es una tarea `API-XX` y no necesita una `BK-XX` propia: a partir de aquí el plan de contratos manda.

Lo único que este documento añade para esa etapa es la condición de entrada: **un módulo no empieza hasta que existan sus tablas**. Resources no se implementa antes de `DB-01`, researchs antes de `DB-02`, administration antes de `DB-03` ni notifications antes de `DB-04`.

---

## El frontend

Se borró con el backend y **no tiene plan todavía**. Construirlo exige antes tener API contra la que trabajar: el orden natural es después de `BK-09`, cuando auth funcione de punta a punta y haya una sesión real que consumir.

`architecture.md` §3 fija su stack —Next.js 14, React 18, TypeScript, Tailwind y Recharts—, así que esa parte tampoco se decidirá entonces.
