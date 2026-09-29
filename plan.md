# Plan técnico — Reservas Parquei

Cómo se construye lo que la especificación describe. Cierra la cadena de SDD entre el qué y el cuándo:

| Documento | Responde |
|---|---|
| [`specs/docs/spec.md`](specs/docs/spec.md) | Qué hace el producto y para quién |
| [`specs/docs/architecture.md`](specs/docs/architecture.md) | Cómo está diseñado el sistema |
| **`plan.md`** | **Cómo se construye: stack, estructura, límites, fases y criterios de cierre** |
| [`tasks.md`](tasks.md) | En qué orden, quién y con qué criterio de aceptación por tarea |
| [`specs/docs/testing.md`](specs/docs/testing.md) | Cómo se verifica que lo construido corresponde a lo especificado |
| [`specs/docs/trazabilidad.md`](specs/docs/trazabilidad.md) | Si cada regla tiene ya contrato, tarea y prueba. Generado |

**Aquí no hay tareas.** Si buscas qué hacer a continuación, es `tasks.md`.

---

## 1. De dónde parte

La especificación está cerrada: nueve módulos con reglas, modelo, flujos y contrato, y las quince preguntas abiertas resueltas. Lo que no existe es el código.

| Componente | Estado |
|---|---|
| Especificación y contratos | Completos y cotejados entre sí. 122 rutas documentadas |
| Base de datos | Completa: los cinco schemas y las 51+ tablas aplicados, con las garantías de concurrencia de `DB-12` instaladas y probadas |
| Backend | Completo: 56 tareas de base de datos, contratos y backend cerradas, `auth` incluida |
| Frontend | Vacío. Con plan: [`specs/docs/tasks/frontend.md`](specs/docs/tasks/frontend.md), 23 tareas `FE-XX` |

El backend anterior autenticaba por `username`, devolvía el token en el cuerpo y metía el rol dentro del JWT. No eran defectos de implementación sino de contrato, así que se retiró en vez de adaptarse pieza a pieza.

**La base no se borró.** Es la única línea base que existe, porque ningún script de este repositorio reconstruye el esquema desde cero.

---

## 2. Lo que ya está decidido

Fijado en `architecture.md` §3 y §16. **No se renegocia al implementar.**

| Capa | Tecnología |
|---|---|
| Frontend | Next.js 14, React 18, TypeScript, Tailwind CSS y Recharts |
| Backend | FastAPI, Python, SQLAlchemy, Pydantic y Uvicorn |
| Base de datos | PostgreSQL 13 |
| Autenticación | JWT en cookie `HttpOnly` con CSRF de doble envío; contraseñas con bcrypt |
| Contenedores | Docker y Docker Compose |

Tres consecuencias que condicionan el código:

**PostgreSQL 13, no 14 ni 15.** La unicidad condicional se resuelve con índices únicos parciales, no con `NULLS NOT DISTINCT`. La exclusión de solapamientos exige `btree_gist`, que ya está instalada. `gen_random_uuid()` sí es del núcleo en la 13.

**La sesión vive en una cookie, no en el cliente.** El token nunca viaja en el cuerpo ni se guarda en `localStorage`, y **no contiene rol ni permisos**: se revalidan en el servidor en cada operación. Esto obliga a CSRF de doble envío en toda escritura.

**Un solo proceso y una sola base.** Los nueve módulos comparten ambos; no hay servicios separados ni cola de mensajes.

---

## 3. Cómo se organiza el código

```text
backend/
  app/
    core/          errores, paginación, sesión, CSRF, autorización
    db/            sesión de SQLAlchemy y modelos por schema
    modules/       los nueve módulos de la especificación
    main.py
  migrations/      el esquema, versionado
  tests/
docker-compose.yml
```

Cada módulo tiene la misma forma interna —`router.py`, `schemas.py`, `service.py`, `repository.py`— para que la capa donde vive una regla sea evidente:

| Capa | Responsabilidad | Lo que **no** hace |
|---|---|---|
| `router.py` | Traducir HTTP: rutas, cuerpos, códigos de estado | Aplicar reglas de negocio |
| `schemas.py` | Forma de entrada y salida, validación sintáctica | Consultar la base |
| `service.py` | Aplicar las `RN`, orquestar la transacción | Hablar SQL |
| `repository.py` | Hablar con la base | Decidir nada |

**Los módulos del backend son los nueve de las especificaciones, con sus mismos nombres.** Un módulo que no corresponda a uno documentado es señal de que la superficie se está inventando.

Auth divide su router y servicio conforme a su plan. Reservations conserva las cuatro capas y añade el dominio, las estrategias y las políticas de su [arquitectura aprobada](specs/modules/reservations/architecture.md).

### Reservations

Flujo lógico: `router → service → Reserva/Strategy → repository`. El servicio carga y persiste mediante el repositorio; Context y estrategias no acceden directamente a SQL. El servicio conserva autorización, orquestación y transacciones. `Reserva` es el Context que delega comportamiento específico mediante `ReservationStrategy`, sin sustituir al servicio.

`API-13` establece `domain/reserva.py`, `strategies/reservation_strategy.py`, el selector y las cinco estrategias: `EspacioStrategy`, `RecursoInternoStrategy`, `RecursoCampusStrategy`, `RecursoExternoStrategy` y `ListaEsperaStrategy`. Sus operaciones se completan en API-14 y API-16 según el contrato. Las policies se separan por acceso, contexto, apoyo, horario, disponibilidad y propuestas. `PrestamoFisicoPolicy` es un componente compartido por campus y externo, no una sexta Strategy.

El retiro manual del Técnico no genera historial específico. Los retiros automáticos por préstamo conservan únicamente la trazabilidad exigida y se coordinan entre reservas en una transacción. Las garantías de base de DB-12 no se sustituyen con validaciones en Strategy.

Lista de espera conserva viabilidad explícita, adjuntos y formulario tras viabilidad; recepción y aprobación atómicas; ejecución sin entrega de recursos y finalización con horas. Campus y externo generan la FGL 030 al aprobar dentro del proceso de salida y mantienen sus datos inmutables, sin regeneración ni versiones. Espacio e interno conservan sus transiciones automáticas por franja, con las diferencias definidas en sus reglas.

### Frontend

```text
frontend/
  app/
    (auth)/        rutas publicas: login, registro, activacion, recuperacion
    (app)/         rutas autenticadas, una carpeta por modulo
  src/
    components/ui/ componentes compartidos, empezando por Button
    lib/           cliente HTTP y hooks de datos
    styles/        tokens.css, generado desde specs/ui/design-tokens.md
  tests/
```

Next.js 14 con **App Router**, no Pages Router: Server Components por defecto para las vistas de solo lectura, `'use client'` solo donde hay estado o interacción. El detalle completo de esta arquitectura —por qué App Router, cómo se maneja la sesión en el cliente, dónde vive TanStack Query— está en el [plan de frontend](specs/docs/tasks/frontend.md), porque no estaba fijado en `architecture.md` y se decide ahí por primera vez. Anotado en [`decisiones_pendientes_para_revision.md`](decisiones_pendientes_para_revision.md) para revisión del equipo.

Un directorio por módulo dentro de `app/(app)/`, con los mismos nueve nombres que el backend — la misma regla del límite 4: un directorio que no corresponda a un módulo documentado es señal de que la superficie se está inventando.

---

## 4. Los cinco límites que no se cruzan

**1. El backend nunca crea ni modifica tablas.** El esquema lo gobiernan las migraciones versionadas de `backend/migrations/`, conforme a `architecture.md` §15. No hay `create_all` ni creación al arrancar. Cuando falte estructura, se abre una tarea de base de datos; no se resuelve desde el código.

**2. La superficie se deriva del contrato, no al revés.** Cada ruta, cada campo y cada código de error ya están escritos. Si al implementar aparece algo que el contrato no contempla, **se corrige el contrato primero**; no se añade al código y se documenta después.

**3. Los módulos no se llaman entre sí por HTTP.** Comparten proceso y base. Un módulo que necesita algo de otro usa su capa de servicios, respetando la propiedad de cada tabla. El contrato interno de auth es el ejemplo a seguir.

**4. Cada regla pertenece a un módulo.** Cuando otro la necesita, la referencia. Un módulo no redefine una regla global (`architecture.md` §16.9). Los identificadores de regla son únicos **dentro** de su módulo, no en todo el sistema: once familias se repiten con significados distintos, así que toda cita a una regla ajena nombra su módulo.

**5. Lo que garantiza la base, lo garantiza la base.** Unicidad, no solapamiento y referencias válidas se comprueban con restricciones, no con una consulta previa desde el servicio. Una consulta previa no es una garantía bajo concurrencia; es una carrera con mejor cara.

---

## 5. Las fases y cuándo una está cerrada

El orden lo detalla `tasks.md`. Lo que sigue es el criterio de salida de cada una: qué tiene que ser cierto para pasar a la siguiente.

| Fase | Cerrada cuando |
|---|---|
| **0 — Desbloqueo** | El proyecto levanta, responde `/health` y **deniega por defecto**: una operación sin permiso comprobable falla. Las tablas de `auth` existen y sus catálogos están cargados |
| **1 — Los schemas que faltan** | Las cinco claves foráneas externas están instaladas y no queda ninguna restricción `pendiente_fk_*`. Los modelos reflejan la base y ninguno declara una tabla inexistente |
| **2 — Identidad** | Auth funciona de punta a punta contra el contrato nuevo y queda como referencia de las convenciones transversales; Reservations aplica además su arquitectura Strategy aprobada |
| **3 — Catálogos e inventario** | Existen recursos, espacios y contextos reales, creados por la API y no insertados a mano |
| **4 — Reservas** | Los cinco tipos cumplen el contrato actualizado; la base impide solapamientos temporales y compromisos físicos duplicados incluso con fechas distintas, incluidos los retiros atómicos de complementarios y sus carreras con el inicio del espacio |
| **5 — Notificaciones y reportes** | Repetir una ocurrencia no genera una segunda notificación, y un fallo de entrega **no invalida la operación de negocio** que lo originó |
| **6 — Frontend** | Los nueve módulos tienen su especificación de pantalla (`screens.md`, `wireframes.md`, `screen-flow.md`) y su implementación en `frontend/`, consumiendo la API real y no una simulada; ningún componente compartido usa un color, radio o sombra fuera de [`design-tokens.md`](specs/ui/design-tokens.md) |

Una fase no se da por cerrada porque sus tareas estén marcadas, sino porque su criterio se comprueba.

Cómo se comprueba está en [`testing.md`](specs/docs/testing.md), y qué falta por comprobar en [`trazabilidad.md`](specs/docs/trazabilidad.md), que se regenera con `python tools/trazabilidad.py`.

---

## 6. Decisiones cerradas y trabajo pendiente

**Decisiones cerradas de Reservations:** DB-11 y ADR-001 fijaron `America/Bogota` y la proyección temporal; la entrega física abre el rango solo para campus y externo, sin alterar las fechas solicitadas. La ampliación funcional exige un único compromiso físico desde la incorporación, aunque los periodos no se solapen. Espacio e interno funcionan por franjas, sin entrega/devolución física. Los hallazgos funcionales y la arquitectura Strategy están cerrados documentalmente.

**Garantías pendientes — DB-12:** diseñar, instalar y probar la exclusión temporal, la integridad del compromiso físico único y los campos objetivo del retiro automático por préstamo. Los índices ordinarios y la exclusión por periodo no bastan para la exclusividad física. Aprobar el diseño funcional no significa que esas garantías estén instaladas.

**Gobierno de migraciones — DB-13:** sigue pendiente el mecanismo reproducible y versionado de aplicación sobre la base actual. No se reabren las decisiones funcionales al implementar.

---

## 7. Los riesgos

**La protección contra doble reserva no está instalada.** Que existan las columnas `periodo` y `bloqueante` y algunos índices ordinarios **no equivale** a la garantía. Hasta instalarla, crear una reserva funciona en toda prueba manual y falla con dos usuarios simultáneos. Es el riesgo más caro del proyecto porque no se manifiesta hasta que hay usuarios.

**El esquema no se puede reconstruir desde cero.** El ajuste que produjo las 28 tablas transforma un esquema anterior en vez de crearlo, y los schemas compartidos con otros sistemas del ITM no los crea ningún script de aquí. Perder el volumen de PostgreSQL no se arregla volviendo a ejecutar las migraciones.

**La especificación puede envejecer al implementar.** El límite 2 dice que el contrato manda, pero un contrato que nadie corrige cuando la realidad lo contradice deja de ser útil. Corregirlo es parte del trabajo, no una interrupción.

---

## 8. Qué queda fuera

- **El despliegue.** No hay entorno desplegado. Todo esto es desarrollo sobre una base local.
- **La carga de datos reales.** Proyectos, semilleros y equipos llegan por importación masiva, que es superficie de API y no un paso de instalación.
