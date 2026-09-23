# Plan técnico — Reservas Parquei

Cómo se construye lo que la especificación describe. Cierra la cadena de SDD entre el qué y el cuándo:

| Documento | Responde |
|---|---|
| [`specs/docs/spec.md`](specs/docs/spec.md) | Qué hace el producto y para quién |
| [`specs/docs/architecture.md`](specs/docs/architecture.md) | Cómo está diseñado el sistema |
| **`plan.md`** | **Cómo se construye: stack, estructura, límites, fases y criterios de cierre** |
| [`tasks.md`](tasks.md) | En qué orden, quién y con qué criterio de aceptación por tarea |

**Aquí no hay tareas.** Si buscas qué hacer a continuación, es `tasks.md`.

---

## 1. De dónde parte

La especificación está cerrada: nueve módulos con reglas, modelo, flujos y contrato, y las quince preguntas abiertas resueltas. Lo que no existe es el código.

| Componente | Estado |
|---|---|
| Especificación y contratos | Completos y cotejados entre sí. 122 rutas documentadas |
| Base de datos | El schema `reservas` aplicado: 28 tablas, vacías. Faltan cuatro schemas, cinco tablas de `auth` y las columnas objetivo de `usuarios.usuarios` |
| Backend | Vacío. El anterior se retiró entero porque respondía a un contrato distinto |
| Frontend | Vacío. Sin plan todavía |

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

Auth es la única excepción a la forma de cuatro archivos: se construye a dos manos y parte su router y su servicio para que dos personas no editen el mismo archivo.

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
| **2 — Identidad** | Auth funciona de punta a punta contra el contrato nuevo, y **queda como referencia de estilo**: cualquier módulo posterior que se estructure distinto se corrige, no se justifica |
| **3 — Catálogos e inventario** | Existen recursos, espacios y contextos reales, creados por la API y no insertados a mano |
| **4 — Reservas** | Dos transacciones concurrentes sobre el mismo espacio y periodo terminan con **una sola reserva escrita**, verificado contra la base y no contra el backend |
| **5 — Notificaciones y reportes** | Repetir una ocurrencia no genera una segunda notificación, y un fallo de entrega **no invalida la operación de negocio** que lo originó |

Una fase no se da por cerrada porque sus tareas estén marcadas, sino porque su criterio se comprueba.

---

## 6. Las decisiones técnicas que siguen abiertas

Tres, y **las tres bloquean código**. Ninguna es una tarea de escribir: son acuerdos que cuestan una conversación y, mal resueltos, cuestan rehacer.

**La zona horaria operativa.** `architecture.md` §15 exige fijar la convención de fechas y horas **antes** de implementar módulos que comparen tiempos, y ADR-001 lo repite: convertir los periodos locales a `tstzrange` exige una zona horaria explícita y uniforme, **nunca la implícita de cada conexión**. Sin esto, los disparadores de solapamiento se construyen sobre arena. Es prerrequisito de `DB-12`.

**Si la entrega física abre el rango temporal.** ADR-001 propone que sí; el modelo de datos de reservations dice que entrega y devolución no alteran el periodo planificado. `database-status.md` lo señala como pendiente de resolver antes de tocar los disparadores. Es `DB-11`.

**El mecanismo de migraciones.** `architecture.md` §15 exige reproducibilidad y versionado, no una herramienta concreta. Hoy los scripts están en el repositorio pero **nada registra cuáles se han aplicado** salvo un documento escrito a mano. Es `DB-13`.

ADR-001 sigue **pendiente de aprobación formal**. Implementarlo antes de aprobarlo es asumir que se aprobará.

---

## 7. Los riesgos

**La protección contra doble reserva no está instalada.** Que existan las columnas `periodo` y `bloqueante` y algunos índices ordinarios **no equivale** a la garantía. Hasta instalarla, crear una reserva funciona en toda prueba manual y falla con dos usuarios simultáneos. Es el riesgo más caro del proyecto porque no se manifiesta hasta que hay usuarios.

**El esquema no se puede reconstruir desde cero.** El ajuste que produjo las 28 tablas transforma un esquema anterior en vez de crearlo, y los schemas compartidos con otros sistemas del ITM no los crea ningún script de aquí. Perder el volumen de PostgreSQL no se arregla volviendo a ejecutar las migraciones.

**La especificación puede envejecer al implementar.** El límite 2 dice que el contrato manda, pero un contrato que nadie corrige cuando la realidad lo contradice deja de ser útil. Corregirlo es parte del trabajo, no una interrupción.

---

## 8. Qué queda fuera

- **El frontend.** Su stack está fijado, pero no tiene plan. Construirlo exige antes una API contra la que trabajar: el orden natural es después de que auth funcione de punta a punta y haya una sesión real que consumir.
- **El despliegue.** No hay entorno desplegado. Todo esto es desarrollo sobre una base local.
- **La carga de datos reales.** Proyectos, semilleros y equipos llegan por importación masiva, que es superficie de API y no un paso de instalación.
