# Plan de tareas — Backend nuevo

Cómo se construye el backend desde cero, sin tocar el actual. Las tareas de superficie HTTP están en el [plan de contratos](contratos.md) como `API-XX`; este documento cubre lo anterior a ellas: dónde vive el proyecto, con qué estructura y en qué orden se levanta.

Plan general: [`tasks.md`](../../../tasks.md) de la raíz.

---

## Punto de partida

| Qué | Estado |
|---|---|
| `backend/app/` | El backend actual. **Se conserva**, no se modifica y no se extiende |
| `backend/migrations/` | Las migraciones de la base, incluida `003` sin ejecutar. **Se conservan y se siguen usando** |
| La base `reservas_db` | 28 tablas aplicadas en el schema `reservas`, todas vacías |
| Los nueve contratos | Escritos y cotejados contra modelos, reglas y flujos |

El backend actual implementa un contrato anterior: credencial por `username`, token en el cuerpo de la respuesta, `rol` dentro del JWT, sin sesiones ni CSRF. Adaptarlo pieza a pieza obliga a mantener dos comportamientos a la vez en los mismos archivos. Por eso se construye uno nuevo al lado y el viejo queda como referencia hasta que el nuevo lo sustituya.

**El stack no se decide aquí.** `architecture.md` §3 lo fija: FastAPI, Python, SQLAlchemy, Pydantic, Uvicorn, PostgreSQL 13, JWT con bcrypt y Docker Compose.

---

## Tres reglas de construcción

**1. El backend nunca crea ni modifica tablas.** El esquema lo gobiernan las migraciones versionadas de `backend/migrations/`, conforme a `architecture.md` §15. No hay `create_all` ni creación al arrancar. Es exactamente lo que `DB-13` señala como defecto del backend actual: su arranque puede intentar recrear tablas que el ajuste retiró.

**2. La superficie se deriva del contrato, no al revés.** Cada ruta, cada campo del cuerpo y cada código de error ya están escritos. Si al implementar aparece algo que el contrato no contempla, se corrige el contrato primero y se implementa después; no se añade al código y se documenta luego.

**3. Los módulos no se llaman entre sí por HTTP.** Comparten proceso y base. Un módulo que necesita algo de otro usa su capa de servicios, respetando la propiedad de cada tabla. El contrato interno de auth (`exigir_permiso`, contexto autenticado) es el ejemplo a seguir.

---

## Dónde vive

```text
api/                        <- el backend nuevo
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
  tests/
  Dockerfile
  requirements.txt
backend/                    <- el actual, intacto
  migrations/               <- las migraciones siguen aquí
```

Carpeta hermana, no una subcarpeta de `backend/`, para que ningún import cruce entre el viejo y el nuevo por accidente. Las migraciones se quedan donde están: son de la base, no de la aplicación, y `003` está pendiente de ejecutar.

Cada módulo tiene la misma forma interna —`router.py`, `schemas.py`, `service.py`, `repository.py`— para que la capa donde vive una regla sea evidente: el router traduce HTTP, el servicio aplica las `RN` y el repositorio habla con la base.

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

### BK-01 — Crear el proyecto

- **Objetivo:** `api/` existe, instala sus dependencias y expone `GET /health`.
- **Afectados:** `api/requirements.txt`, `api/app/main.py`, `api/Dockerfile`.
- **Dependencias:** ninguna.
- **Aceptación:** `uvicorn app.main:app` levanta y `GET /health` devuelve `200`. **No abre conexión a la base.**

### BK-02 — Conectar a PostgreSQL sin crear nada

- **Objetivo:** hay una sesión de SQLAlchemy configurada por variable de entorno.
- **Afectados:** `api/app/db/session.py`, `api/app/core/config.py`.
- **Dependencias:** BK-01.
- **Aceptación:** `GET /health` informa si la base responde. **Arrancar dos veces seguidas no crea ni altera ninguna tabla**: el conteo de tablas de `reservas` sigue siendo 28.

### BK-03 — Añadir el servicio a Docker Compose

- **Objetivo:** el backend nuevo corre junto a `db` y `pgadmin`.
- **Afectados:** `docker-compose.yml`.
- **Dependencias:** BK-01.
- **Aceptación:** `docker compose up` levanta la base y el backend nuevo. El servicio `backend` antiguo sigue definido pero **no se levanta por defecto**.

---

## Hito 1 — El núcleo transversal

Es lo que hace que los nueve módulos se comporten igual. Implementa las tareas `API-01` a `API-04` del plan de contratos, y **ninguna ruta de negocio se escribe antes de cerrarlo**.

### BK-04 — Envolvente de error y catálogo común

- **Objetivo:** toda excepción sale como `{"error": {"codigo", "mensaje", "detalles"}}`.
- **Afectados:** `api/app/core/errors.py`, manejadores en `main.py`.
- **Dependencias:** BK-01. Cubre `API-01`.
- **Aceptación:** una ruta inexistente devuelve `404 NO_ENCONTRADO` con esa forma, no el `detail` de FastAPI. Una excepción no controlada devuelve `500 ERROR_INTERNO` **sin traza en la respuesta**.

### BK-05 — Paginación, filtros y orden

- **Objetivo:** una dependencia reutilizable que todo listado usa.
- **Afectados:** `api/app/core/pagination.py`.
- **Dependencias:** BK-04. Cubre `API-02`.
- **Aceptación:** un listado devuelve `datos` + `paginacion`; un filtro desconocido devuelve `400 SOLICITUD_INVALIDA`; un catálogo cerrado devuelve solo `datos` y rechaza `pagina`.

### BK-06 — Sesión por cookie y CSRF

- **Objetivo:** identidad desde la sesión y doble envío obligatorio en toda escritura.
- **Afectados:** `api/app/core/security.py`, `api/app/modules/auth/`.
- **Dependencias:** BK-04. Cubre `API-03`.
- **Aceptación:** un `POST` sin `X-CSRF-Token` devuelve `403` aunque la sesión sea válida. El JWT **no contiene rol ni permisos**. `GET /api/auth/csrf` emite la cookie sin sesión previa.

### BK-07 — `exigir_permiso` con ámbito

- **Objetivo:** una dependencia que resuelve permiso y unidad en cada operación.
- **Afectados:** `api/app/core/authz.py`.
- **Dependencias:** BK-06 y **DB-09**, que carga el catálogo de permisos.
- **Aceptación:** un Técnico sobre una unidad ajena recibe `403`, o `404` cuando revelar la existencia sea una fuga. Si el permiso no puede comprobarse, **deniega**.

---

## Hito 2 — Los modelos

### BK-08 — Modelar las tablas que existen

- **Objetivo:** modelos SQLAlchemy de `reservas` (28 tablas), `auth`, `usuarios`, `personal`, `cargos`, `unidadOrganizacional` e `investigacion` en lo que ya existe.
- **Afectados:** `api/app/db/models/`.
- **Dependencias:** BK-02.
- **Aceptación:** una consulta a cada tabla se ejecuta sin error. **Ningún modelo declara una tabla que la base no tenga**, y ninguno se marca como creable.
- **Nota:** `recursos`, `administration`, `notificaciones` y el resto de `investigacion` **no se modelan todavía**: no existen hasta `DB-01` a `DB-04`. Modelarlos antes produce código que no se puede probar.

---

## Hito 3 — El primer módulo completo

### BK-09 — Auth de punta a punta

- **Objetivo:** los 17 endpoints del contrato de auth, funcionando.
- **Afectados:** `api/app/modules/auth/`.
- **Dependencias:** Hito 1 y BK-08. Desarrolla `API-05`; el desglose está en [modules/auth/tasks.md](../../modules/auth/tasks.md).
- **Aceptación:** la del plan de auth. Además, **auth queda como la referencia de estilo**: cualquier módulo posterior que se estructure distinto se corrige, no se justifica.

Al cerrar este hito hay un módulo entero contra el contrato nuevo, y las decisiones difíciles —sesiones, CSRF, ámbito, forma del error— ya están tomadas en código, no solo en documento.

---

## Hito 4 en adelante

El orden es el del [plan general](../../../tasks.md): identidad, estructura institucional, catálogos, reservas, y por último notificaciones y reportes. Cada módulo es una tarea `API-XX` y no necesita una `BK-XX` propia: a partir de aquí el plan de contratos manda.

Lo único que este documento añade para esa etapa es la condición de entrada: **un módulo no empieza hasta que existan sus tablas**. Resources no se implementa antes de `DB-01`, researchs antes de `DB-02`, administration antes de `DB-03` ni notifications antes de `DB-04`.

---

## Cuándo se retira el backend actual

No al empezar, sino cuando el nuevo cubra lo que el viejo hacía. La señal es `API-13`: con reservas creándose contra el contrato nuevo, el viejo deja de aportar referencia.

Hasta entonces se queda, sin tocar y sin levantarse por defecto. Retirarlo es una tarea aparte, que incluye `DB-13` —desconectar el arranque heredado— y revisar qué de `backend/migrations/` pasa a gobernar el proyecto nuevo.
