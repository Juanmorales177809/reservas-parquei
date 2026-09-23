# Reservas Parquei

Sistema de reservas de espacios, equipos y recursos de laboratorio para el ITM.

**Estado: la especificación está cerrada y la base de datos aplicada. El backend y el frontend están por construir.**

---

## Dónde está cada cosa

| Carpeta | Contenido |
|---|---|
| [`specs/`](specs/) | La especificación completa: nueve módulos con reglas de negocio, modelo de datos, flujos de usuario y contrato de API |
| [`backend/migrations/`](backend/migrations/) | Las migraciones que gobiernan el esquema de PostgreSQL |
| [`plan.md`](plan.md) | El plan técnico: stack, estructura del código, límites y criterios de cierre de cada fase |
| [`tasks.md`](tasks.md) | El plan de implementación, que une los planes de base de datos, contratos y backend |
| [`AGENTS.md`](AGENTS.md) | Cómo trabajar en este repositorio: qué documento manda, qué no se toca y cómo se valida un cambio |
| [`tools/`](tools/) | Los scripts que comprueban que la especificación sea coherente y generan la matriz de trazabilidad |
| `docker-compose.yml` | Levanta PostgreSQL y pgAdmin |

La cadena es **`spec.md` → `architecture.md` → `plan.md` → `tasks.md`**: qué hace el producto, cómo está diseñado, cómo se construye y en qué orden.

## Estado real

| Componente | Estado |
|---|---|
| Especificación | **Completa.** 504 reglas de negocio, 63 controles de seguridad, 82 flujos y 9 contratos con 122 rutas, cotejados entre sí. Las 15 preguntas abiertas están resueltas |
| Pruebas | **Especificadas, ninguna implementada.** 111 pruebas descritas en los nueve `tests.md`; no hay código que probar |
| Base de datos | **Aplicada parcialmente.** El schema `reservas` tiene sus 28 tablas; faltan los schemas `recursos`, `administration` y `notificaciones`, parte de `investigacion` y cinco tablas dentro de `auth` |
| Backend | **Por construir.** El anterior se retiró: implementaba un contrato distinto |
| Frontend | **Por construir** |

Tres cosas conviene saberlas antes de tocar nada:

**Las tablas de sesión y permisos no existen.** `auth.cuentas` sí, pero `auth.sesiones`, `auth.invitaciones`, `auth.tokens_recuperacion`, `auth.permisos` y `auth.cuenta_permisos` están definidas en la especificación y nunca se aplicaron. Sin ellas no hay inicio de sesión ni autorización posible. Es `DB-14`, la primera tarea de base de datos.

**La protección contra doble reserva no está instalada.** Que existan las columnas `periodo` y `bloqueante` no equivale a la garantía. Es la tarea `DB-12`, y hasta cerrarla crear una reserva no es correcto bajo concurrencia.

**Los catálogos están vacíos.** Sin tipos de reserva, estados ni permisos cargados, no puede crearse ninguna reserva ni autorizarse ninguna operación. Son `DB-08` y `DB-09`.

## Tecnologías

Fijadas en [`specs/docs/architecture.md`](specs/docs/architecture.md) §3.

| Capa | Tecnología |
|---|---|
| Frontend | Next.js 14, React 18, TypeScript, Tailwind CSS y Recharts |
| Backend | FastAPI, Python, SQLAlchemy, Pydantic y Uvicorn |
| Base de datos | PostgreSQL 13 |
| Autenticación | JWT en cookie `HttpOnly`, con bcrypt |
| Contenedores | Docker y Docker Compose |

## Cómo empezar

```bash
docker compose up -d db          # levanta PostgreSQL con el esquema ya aplicado
```

A partir de ahí, el orden está en [`tasks.md`](tasks.md). La primera tarea de código es `BK-01`: crear el proyecto del backend.

## Cómo leer la especificación

Empieza por [`specs/README.md`](specs/README.md), que indexa los nueve módulos y sus contratos.

Cada módulo tiene cuatro documentos —`overview`, `business-rules`, `data-model` y `user-flow`— y un contrato de API en [`specs/contratos/`](specs/contratos/).

Dos convenciones que evitan errores al leer:

- **Cada regla pertenece a un único módulo.** Cuando otro la necesita, la referencia en lugar de repetirla.
- **Los identificadores de regla son únicos dentro de su módulo, no en todo el sistema.** Once familias se repiten con significados distintos, así que toda cita a una regla ajena nombra su módulo. La tabla completa está en [`specs/README.md`](specs/README.md).
