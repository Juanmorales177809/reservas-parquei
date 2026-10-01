# Plan de implementación — Reservas Parquei

Une los cuatro planes de trabajo y fija el orden entre ellos. El **qué** y el **cómo** están antes: [`plan.md`](plan.md) fija stack, estructura del código, límites y criterios de cierre; aquí está el orden, el reparto y el criterio de aceptación de cada tarea.

| Plan | Qué cubre |
|---|---|
| [Base de datos](specs/docs/tasks/base-de-datos.md) | 15 tareas `DB-XX`: identidad, schemas, referencias externas, datos iniciales, concurrencia y gobierno del esquema |
| [Contratos de API](specs/docs/tasks/contratos.md) | 19 tareas `API-XX`: convenciones transversales y los nueve contratos |
| [Backend nuevo](specs/docs/tasks/backend.md) | 10 tareas `BK-XX`: dónde vive el proyecto, con qué estructura y cómo se levanta antes de la primera ruta de negocio |
| [Auth en detalle](specs/modules/auth/tasks.md) | 12 tareas `AUTH-XX`: el primer módulo completo, construido a dos carriles |
| [Frontend](specs/docs/tasks/frontend.md) | 23 tareas `FE-XX`: cimientos, componentes compartidos y, módulo por módulo, la especificación de pantalla que falta seguida de su implementación en Next.js |

**Dos parejas de tareas son la misma cosa vista desde dos planes.** `BK-04` a `BK-07` son `API-01` a `API-04`, y `BK-09` es `API-05`, que a su vez se desglosa en el plan de auth. No se cuentan ni se cierran dos veces: manda la `BK-XX`, que nombra los archivos.

La especificación está cerrada: nueve módulos con reglas, modelo, flujos y contrato, y las quince preguntas abiertas resueltas. **Lo que queda es construir.**

---

## La regla que ordena todo

**Una tarea de API no se cierra antes que la tarea de base de datos que la sostiene.** No por método, sino porque un endpoint sobre una tabla que no existe no se puede probar, y uno que "funciona" sin su restricción da una falsa sensación de terminado.

El caso que más importa es la concurrencia: `API-13` crea reservas y `DB-12` instala la exclusión temporal y la garantía de un único compromiso físico por recurso, incluso con periodos distintos, junto con el retiro atómico de complementarios. **Se puede crear reservas sin `DB-12`, y ahí está el peligro**: todo parece correcto en una prueba manual y falla con dos usuarios simultáneos.

---

## Fase 0 — Desbloqueo inmediato · **cerrada**

Sin esto nada más podía probarse contra la base ajustada.

| Tarea | Por qué |
|---|---|
| ~~`BK-00`~~ | Las migraciones rescatadas y verificadas |
| ~~`BK-01`~~ a ~~`BK-03`~~ | El proyecto levanta, con `/health` respondiendo desde el contenedor |
| ~~`DB-14`~~ | Las cinco tablas de `auth` existen |
| ~~`DB-08`~~ | Los cinco tipos y seis estados de reservas están cargados |
| ~~`DB-09`~~ | Los catorce permisos están cargados |
| ~~`BK-04`~~ a ~~`BK-07`~~ | Las convenciones transversales: envolvente de error, paginación, sesión/CSRF y `exigir_permiso` |

Cada tarea quedó verificada contra `reservas_db` real, no solo escrita: peticiones HTTP de verdad contra el contenedor, y para `BK-07`, datos de prueba sembrados y revertidos en una transacción. El detalle de cada una está en [`backend.md`](specs/docs/tasks/backend.md) y [`base-de-datos.md`](specs/docs/tasks/base-de-datos.md).

**El proyecto deniega por defecto.** `authz.py` deniega ante cualquier permiso que no pueda comprobarse, no solo ante uno explícitamente denegado — es el criterio de cierre de esta fase en `plan.md` §5.

**La base no se borró.** Conserva sus 28 tablas de `reservas` y el volumen sigue montado. Faltan las garantías y atributos objetivo de `DB-12`, además de las incorporaciones pendientes en los schemas compartidos que cubre la Fase 1.

---

## Fase 1 — Los schemas que faltan · **cerrada**

Los cuatro schemas se crearon en orden pero eran independientes entre sí:

~~`DB-01`~~ recursos · ~~`DB-02`~~ investigación · ~~`DB-03`~~ administration · ~~`DB-04`~~ notificaciones

~~`DB-05`~~ ejecutó el script de referencias externas que llevaba escrito desde septiembre sin correr. Las cinco FK están instaladas; `reserva_recursos` y `espacio_recursos` ya admiten inserciones con `recurso_id` real.

~~`DB-10`~~ cargó el catálogo de eventos notificables: **nueve códigos, no once** — dos reglas de `RN-EVT` no definen un evento propio o comparten el de otra, según la propia tabla de correspondencia del módulo. Verificado en [`base-de-datos.md`](specs/docs/tasks/base-de-datos.md).

~~`DB-06`~~, ~~`DB-07`~~ y ~~`DB-15`~~, los tres ajustes de identidad que comparten `008_identidades.sql`, están cerrados.

~~`BK-08`~~ modeló las 51 tablas de `reservas`, `auth`, `usuarios`, `personal`, `cargos`, `unidadOrganizacional` e `investigacion` — generadas por introspección de la base real, no transcritas a mano, y verificadas con una consulta a cada una. `recursos`, `administration` y `notificaciones` existen pero **no se modelan todavía**: se modelan con el primer `API-XX` de su propio módulo.

`~~DB-13~~` ya estaba cerrada desde antes de esta fase: el ledger de `public.schema_migrations` existe y cada migración de la fase siguió su convención, insertando su propia fila al terminar.

**El siguiente paso es la Fase 2**: `BK-09`, auth de punta a punta.

---

## Fase 2 — Identidad y estructura · **cerrada**

| Orden | Tareas |
|---|---|
| 1 | ~~`BK-09`~~ auth de punta a punta, que es `API-05` y se desglosa en el [plan de auth](specs/modules/auth/tasks.md) |
| 2 | ~~`API-06`~~ identidades y fichas de Personal |
| 3 | ~~`API-07`~~ unidades, cargos y permisos · ~~`API-08`~~ auditoría |

`API-06` **bloqueaba la invitación de cuentas `PERSONAL`**: auth exige una ficha activa antes de invitar, y esa ficha se crea en `/api/personal`. Era la única dependencia circular aparente del plan, y no lo era: `AUTH-B3` se implementó y se probó con fichas cargadas a mano, y `API-06` las hizo administrables después.

Auth se construyó a dos carriles: sesión y credenciales por un lado, altas e invitaciones por otro. Al cerrarlo, **quedó como la referencia de estilo** de los ocho módulos restantes.

Con `API-06` a `API-08` cerradas, `backend/tests/` tiene 38 pruebas formales en verde contra `reservas_test` —una base PG13 aislada, construida con la misma cadena de migraciones—, cubriendo auth, administration y usuarios. **El siguiente paso es la Fase 3.**

---

## Fase 3 — Catálogos e inventario · **cerrada**

~~`API-09`~~ recursos → ~~`API-10`~~ espacios, que necesita recursos para asociarlos.

~~`API-11`~~ investigación en paralelo.

~~`API-12`~~ importaciones al final de esta fase: escribe en recursos y en investigación, así que las necesita a ambas.

Fase 3 cerrada.

---

## Fase 4 — Reservas · **cerrada**

Aquí convergen el plan de base de datos y el de contratos.

| Orden | Tareas | Bloqueo |
|---|---|---|
| 1 | ~~`DB-11`~~ | Decisión documental cerrada: zona horaria, proyección temporal y alcance físico |
| 2 | ~~`DB-12`~~ | Diseñar, instalar y probar exclusiones temporales, compromiso físico único y retiro por préstamo |
| 3 | ~~`API-13`~~ | Context/Strategy/policies, creación, edición, consulta, preparación de lista de espera y FGL en autoaprobación |
| 4 | ~~`API-14`~~ | Gestión por tipo, propuestas, aprobación/FGL, recepción de material y ejecución |
| 5 | ~~`API-15`~~ · ~~`API-16`~~ | Consulta/exportación de orden inmutable, calendario y transiciones automáticas de espacio/interno |

`DB-11` está cerrada documentalmente: `America/Bogota`, proyección física solo en campus/externo y compromiso único desde incorporación. `DB-12` instaló y verificó el mecanismo de integridad —incluida concurrencia real— en `backend/migrations/009_concurrencia.sql`. `API-13` está cerrada: implementa la arquitectura completa y verifica por HTTP real, incluida la protección de `DB-12` en la ruta completa. `API-14` a `API-16` están cerradas y verificadas con pruebas formales; el siguiente paso es la Fase 5.

La [arquitectura de Reservations](specs/modules/reservations/architecture.md) se implementa dentro de API-13 a API-16: `router → service → Reserva/Strategy → repository`, con el servicio como dueño de la transacción. `Reserva` es Context y delega en las cinco estrategias mediante `ReservationStrategy`; las policies comunes se separan por responsabilidad y `prestamo_fisico` no es una Strategy adicional.

Se conserva el orden API-13 → API-14 → API-15/API-16. El componente de generación de FGL se prepara en API-13 para la creación autoaprobada y se reutiliza al aprobar en API-14; API-15 solo consulta/exporta. Así la creación no depende de una tarea posterior. Los criterios incluyen lista de espera sin nuevos estados ni tablas, FGL inmutable, interno por franja, retiro manual sin historial y retiro automático por préstamo con la trazabilidad exigida.

Los archivos compartidos del servicio, estrategias y repositorio se entregan del carril A al B al cerrar API-14. API-15 y API-16 se secuencian cuando modifiquen esos mismos archivos; no se crean tareas adicionales ni se cambian los carriles existentes.

---

## Fase 5 — Notificaciones y reportes · **cerrada**

~~`API-17`~~ bandeja → ~~`API-18`~~ generación y entrega. Ambas se apoyan en `DB-04` y `DB-10`, cerradas en la fase 1: sin los doce tipos de evento cargados (nueve de reservas más tres de auth) no hay ocurrencia que registrar.

`API-19` reportes, que necesita reservas reales para tener qué reportar. Cerrada: `/api/reportes` completo (ocupación, solicitudes, lista de espera y exportación csv/excel), verificado con 81 pruebas y por HTTP real.

`API-20` resumen para el panel de inicio. Cerrada: `GET /api/reportes/resumen` con indicadores, periodo previo y distribuciones en una sola consulta, verificado con 5 pruebas nuevas (suite 129/129).

`API-21` horas de lista de espera en el resumen. Las `horas_ejecucion` de lista `FINALIZADA` suman en horas y ocupación, atribuidas por fecha de creación.

**Con las fases 0 a 5 cerradas, el backend está completo.** El siguiente paso es la Fase 6.

---

## Fase 6 — Frontend

`frontend/` se borró y no tenía plan (`plan.md` §8). Ya no aplica el motivo por el que se aplazó: **el backend está completo**, con sesión real que consumir y los 19 contratos cerrados. Lo que falta no es API — es la especificación de pantalla de ocho de los nueve módulos, que solo existe hoy para auth, y después el código. El desglose completo, con esa distinción entre especificación e implementación, está en el [plan de frontend](specs/docs/tasks/frontend.md).

| Orden | Tareas | Qué cierra |
|---|---|---|
| 1 | `FE-01` a `FE-04` | Proyecto Next.js 14, tokens de diseño en Tailwind, cliente HTTP con sesión/CSRF y el componente `Button` completo |
| 2 | `FE-05`, `FE-06` | Completar `specs/ui/layout.md` (hoy solo fija una regla) y el shell de navegación autenticado |
| 3 | `FE-07` | Las nueve pantallas de auth, cuya especificación ya está cerrada — queda como referencia de estilo del resto, igual que auth lo fue para el backend |
| 4 | `FE-08` a `FE-19` | Especificación e implementación, módulo por módulo: usuarios, administration, resources, espacios, researchs y reservations, en ese orden |
| 5 | `FE-20` a `FE-23` | Especificación e implementación de notifications y reports |
| 6 | `FE-24` a `FE-46` | Brechas frente a las reglas: navegación, reserva conforme a reglas, lista de espera, sesión, gestión de reservas, formularios completos y E2E |
| 7 | `FE-47` a `FE-50` | Especificación (`SCR-REP-04`/`WF-REP-04`) e implementación de la pantalla «Inicio» con el resumen del periodo, y el último mes ya consultado al entrar |

Dentro de cada módulo de los órdenes 4 y 5, la tarea de especificación de pantalla cierra antes que su implementación — la misma regla que impide cerrar una `API-XX` antes que su `DB-XX`.

---

## Los dos riesgos que conviene no perder de vista

**La concurrencia está garantizada por `DB-12`.** `database-status.md` advertía que columnas, periodo y bloqueante e índices ordinarios **no equivalen** a la protección: por eso se instaló la exclusión temporal con disparadores y se probó con transacciones concurrentes reales antes de dar por correcta la creación de reservas bajo carga.

**El esquema no se puede reconstruir desde cero.** `002` no crea el schema `reservas`, lo transforma: exige el esquema anterior, que producía un script deliberadamente no rescatado. Y los schemas compartidos —`auth`, `personal`, `cargos`, `unidadOrganizacional`, `investigacion`— no los crea ningún script de este repositorio. **La única línea base es la base viva**, más el respaldo de `snapshots/`. Perder el volumen de PostgreSQL no se arregla volviendo a ejecutar las migraciones. Es lo que `DB-13` tiene que resolver, y por eso conviene cerrarla temprano, antes de que se acumulen más migraciones sin registro de cuáles se aplicaron.

---

## Reparto para dos personas

Los carriles se reparten por propiedad de archivos, no por capas, para que dos personas no toquen el mismo archivo.

El corte es limpio: **A es la base de datos, B es el proyecto.** Ningún archivo pertenece a los dos.

| Carril | Fases 0–1 | Fases 2–3 | Fases 4–5 |
|---|---|---|---|
| **A** | `DB-14`, `DB-01` a `DB-10`, `DB-15`, `DB-13` | `BK-09` carril A, `API-09`, `API-10` | `DB-11` (cerrada), `DB-12`, `API-13`, `API-14` |
| **B** | `BK-01` a `BK-07`, `BK-08` | `BK-09` carril B, `API-06`, `API-07`, `API-08`, `API-11`, `API-12` | `API-15` a `API-21` |

`BK-00` está cerrada y no entra en el reparto. `BK-09` aparece en los dos carriles porque auth se construye a dos manos: el [plan de auth](specs/modules/auth/tasks.md) reparte sus doce tareas por archivo.

**Puntos de sincronización obligatorios:**

1. Al cerrar **`DB-14`**, porque `BK-06` y `BK-07` no pueden terminarse sin las tablas de `auth`. Es el primer punto donde B espera a A.
2. Al cerrar **`BK-07`**, porque todo lo demás depende del núcleo transversal.
3. Al cerrar **`DB-05`**, porque desbloquea las inserciones de recursos.
4. Antes de **`API-13`**, para confirmar que `DB-12` está instalada y probada.

El carril B construye el proyecto nuevo y su núcleo mientras el A prepara lo que falta en la base. Convergen en `BK-08`, que solo puede modelar lo que ya existe, y vuelven a separarse dentro de auth.

**Este reparto no cubre la Fase 6.** `FE-01` a `FE-23` no se dimensionaron para la pareja A/B de las fases 0–5 — se abrieron después de que ambos carriles convergieran, con el backend ya completo. El [plan de frontend](specs/docs/tasks/frontend.md) no reparte sus tareas a dos carriles por archivo; cada módulo reparte su propia especificación (`FE-08`, `FE-10`, `FE-12`, `FE-14`, `FE-16`, `FE-18`, `FE-20`, `FE-22`, `FE-47`) e implementación (`FE-09`, `FE-11`, `FE-13`, `FE-15`, `FE-17`, `FE-19`, `FE-21`, `FE-23`, `FE-48`, `FE-49`, `FE-50`) como una secuencia, no como dos personas en paralelo — repartirlo así queda para cuando se abra la Fase 6. Las brechas que se detectaron después (`FE-24` a `FE-46`, Fase 7 del [plan de frontend](specs/docs/tasks/frontend.md)) tampoco se reparten a dos carriles: van en secuencia, porque casi todas tocan `GestionReservaClient` y la página de nueva reserva.

---

## Qué no está en ningún plan

- **El despliegue.** No hay entorno desplegado: todo esto es desarrollo sobre una base local.
- **La carga de datos reales.** Los catálogos de proyectos, semilleros y equipos llegan por importación, y esa importación necesita `API-12`.
