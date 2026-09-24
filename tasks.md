# Plan de implementación — Reservas Parquei

Une los cuatro planes de trabajo y fija el orden entre ellos. El **qué** y el **cómo** están antes: [`plan.md`](plan.md) fija stack, estructura del código, límites y criterios de cierre; aquí está el orden, el reparto y el criterio de aceptación de cada tarea.

| Plan | Qué cubre |
|---|---|
| [Base de datos](specs/docs/tasks/base-de-datos.md) | 15 tareas `DB-XX`: identidad, schemas, referencias externas, datos iniciales, concurrencia y gobierno del esquema |
| [Contratos de API](specs/docs/tasks/contratos.md) | 19 tareas `API-XX`: convenciones transversales y los nueve contratos |
| [Backend nuevo](specs/docs/tasks/backend.md) | 10 tareas `BK-XX`: dónde vive el proyecto, con qué estructura y cómo se levanta antes de la primera ruta de negocio |
| [Auth en detalle](specs/modules/auth/tasks.md) | 12 tareas `AUTH-XX`: el primer módulo completo, construido a dos carriles |

**Dos parejas de tareas son la misma cosa vista desde dos planes.** `BK-04` a `BK-07` son `API-01` a `API-04`, y `BK-09` es `API-05`, que a su vez se desglosa en el plan de auth. No se cuentan ni se cierran dos veces: manda la `BK-XX`, que nombra los archivos.

La especificación está cerrada: nueve módulos con reglas, modelo, flujos y contrato, y las quince preguntas abiertas resueltas. **Lo que queda es construir.**

---

## La regla que ordena todo

**Una tarea de API no se cierra antes que la tarea de base de datos que la sostiene.** No por método, sino porque un endpoint sobre una tabla que no existe no se puede probar, y uno que "funciona" sin su restricción da una falsa sensación de terminado.

El caso que más importa es la concurrencia: `API-13` crea reservas y `DB-12` instala la exclusión temporal y la garantía de un único compromiso físico por recurso, incluso con periodos distintos, junto con el retiro atómico de complementarios. **Se puede crear reservas sin `DB-12`, y ahí está el peligro**: todo parece correcto en una prueba manual y falla con dos usuarios simultáneos.

---

## Fase 0 — Desbloqueo inmediato

Sin esto nada más puede probarse contra la base ajustada.

| Tarea | Por qué ahora |
|---|---|
| ~~`BK-00`~~ | **Cerrada.** Las migraciones están rescatadas y verificadas |
| `BK-01` a `BK-03` | Levantar el proyecto. `backend/app/` está vacío |
| `DB-14` | **Las cinco tablas de `auth` no existen.** Sin ellas no hay sesión, ni invitación, ni permiso que comprobar |
| `DB-08` | Los catálogos de tipos y estados están vacíos: ninguna reserva puede crearse |
| `DB-09` | Sin el catálogo de permisos no hay autorización posible |
| `BK-04` a `BK-07` | Las convenciones transversales, que son `API-01` a `API-04`. Reimplementarlas por módulo produce nueve APIs distintas |

**`DB-14` va antes que `DB-09`**: una carga el catálogo en la tabla que la otra crea. Y `BK-06` y `BK-07` dependen de las dos, así que son el primer punto donde los planes se tocan.

**La base no se borró.** Conserva sus 28 tablas y el volumen sigue montado, así que el proyecto nuevo arranca contra un esquema que ya tiene la forma correcta. Existen las tablas de `reservas`, pero faltan las garantías y atributos objetivo de DB-12, además de las incorporaciones pendientes en los schemas compartidos.

**El siguiente paso es `BK-01`**: escribir el primer archivo de `backend/app/`. No depende de la base ni de auth, así que puede arrancar mientras `DB-14` se prepara en paralelo.

---

## Fase 1 — Los schemas que faltan

Los cuatro schemas son independientes entre sí y pueden ir en paralelo.

`DB-01` recursos · `DB-02` investigación · `DB-03` administration · `DB-04` notificaciones

Después, `DB-05` ejecuta el script de referencias externas que ya está escrito. **Aborta si falta algún destino**, así que exige `DB-01` y `DB-02` cerradas. Hasta entonces, `reserva_recursos` y `espacio_recursos` **no admiten ninguna inserción**: sus CHECK temporales exigen `NULL` en una columna obligatoria.

`DB-10` carga los once tipos de evento notificables y sigue a `DB-04`.

En paralelo, los tres ajustes de identidad: `DB-06` (`personal.personal.estado`), `DB-07` (estado de las unidades) y `DB-15` (columnas objetivo de `usuarios.usuarios`). **Las tres escriben el mismo archivo**, `008_identidades.sql`, así que van a la misma persona.

También en paralelo, `BK-08`, que modela las tablas existentes. Solo puede modelar lo que ya esté creado, así que se cierra al final de la fase.

Y `DB-13`, el gobierno del esquema. No la empuja ninguna otra tarea, pero cada migración que se escriba sin ella es una más de la que nadie sabrá si se aplicó. Esta fase escribe seis archivos.

---

## Fase 2 — Identidad y estructura

| Orden | Tareas |
|---|---|
| 1 | `BK-09` auth de punta a punta, que es `API-05` y se desglosa en el [plan de auth](specs/modules/auth/tasks.md) |
| 2 | `API-06` identidades y fichas de Personal |
| 3 | `API-07` unidades, cargos y permisos · `API-08` auditoría |

`API-06` **bloquea la invitación de cuentas `PERSONAL`**: auth exige una ficha activa antes de invitar, y esa ficha se crea en `/api/personal`. Es la única dependencia circular aparente del plan, y no lo es: `AUTH-B3` se implementa y se prueba con fichas cargadas a mano, y `API-06` las hace administrables después.

Auth se construye a dos carriles: sesión y credenciales por un lado, altas e invitaciones por otro. Al cerrarlo, **queda como la referencia de estilo** de los ocho módulos restantes.

---

## Fase 3 — Catálogos e inventario

`API-09` recursos → `API-10` espacios, que necesita recursos para asociarlos.

`API-11` investigación en paralelo.

`API-12` importaciones al final de esta fase: escribe en recursos y en investigación, así que las necesita a ambas.

---

## Fase 4 — Reservas

Aquí convergen el plan de base de datos y el de contratos.

| Orden | Tareas | Bloqueo |
|---|---|---|
| 1 | `DB-11` | Decisión documental cerrada: zona horaria, proyección temporal y alcance físico |
| 2 | `DB-12` | Diseñar, instalar y probar exclusiones temporales, compromiso físico único y retiro por préstamo |
| 3 | `API-13` | Context/Strategy/policies, creación, edición, consulta, preparación de lista de espera y FGL en autoaprobación |
| 4 | `API-14` | Gestión por tipo, propuestas, aprobación/FGL, recepción de material y ejecución |
| 5 | `API-15` · `API-16` | Consulta/exportación de orden inmutable, calendario y transiciones automáticas de espacio/interno |

`DB-11` está cerrada documentalmente: `America/Bogota`, proyección física solo en campus/externo y compromiso único desde incorporación; no implica que DB-12 esté instalada. No se reabren los hallazgos funcionales cerrados.

La [arquitectura de Reservations](specs/modules/reservations/architecture.md) se implementa dentro de API-13 a API-16: `router → service → Reserva/Strategy → repository`, con el servicio como dueño de la transacción. `Reserva` es Context y delega en las cinco estrategias mediante `ReservationStrategy`; las policies comunes se separan por responsabilidad y `prestamo_fisico` no es una Strategy adicional.

Se conserva el orden API-13 → API-14 → API-15/API-16. El componente de generación de FGL se prepara en API-13 para la creación autoaprobada y se reutiliza al aprobar en API-14; API-15 solo consulta/exporta. Así la creación no depende de una tarea posterior. Los criterios incluyen lista de espera sin nuevos estados ni tablas, FGL inmutable, interno por franja, retiro manual sin historial y retiro automático por préstamo con la trazabilidad exigida.

Los archivos compartidos del servicio, estrategias y repositorio se entregan del carril A al B al cerrar API-14. API-15 y API-16 se secuencian cuando modifiquen esos mismos archivos; no se crean tareas adicionales ni se cambian los carriles existentes.

---

## Fase 5 — Notificaciones y reportes

`API-17` bandeja → `API-18` generación y entrega. Ambas se apoyan en `DB-04` y `DB-10`, cerradas en la fase 1: sin los once tipos de evento cargados no hay ocurrencia que registrar.

`API-19` reportes, que necesita reservas reales para tener qué reportar.

---

## Los dos riesgos que conviene no perder de vista

**La concurrencia no está garantizada.** `database-status.md` lo advierte expresamente: que existan las columnas `periodo` y `bloqueante` y algunos índices **no equivale** a la protección. Mientras `DB-12` siga abierta, la funcionalidad de crear reserva no puede darse por correcta bajo carga, aunque funcione en todas las pruebas manuales.

**El esquema no se puede reconstruir desde cero.** `002` no crea el schema `reservas`, lo transforma: exige el esquema anterior, que producía un script deliberadamente no rescatado. Y los schemas compartidos —`auth`, `personal`, `cargos`, `unidadOrganizacional`, `investigacion`— no los crea ningún script de este repositorio. **La única línea base es la base viva**, más el respaldo de `snapshots/`. Perder el volumen de PostgreSQL no se arregla volviendo a ejecutar las migraciones. Es lo que `DB-13` tiene que resolver, y por eso conviene cerrarla temprano, antes de que se acumulen más migraciones sin registro de cuáles se aplicaron.

---

## Reparto para dos personas

Los carriles se reparten por propiedad de archivos, no por capas, para que dos personas no toquen el mismo archivo.

El corte es limpio: **A es la base de datos, B es el proyecto.** Ningún archivo pertenece a los dos.

| Carril | Fases 0–1 | Fases 2–3 | Fases 4–5 |
|---|---|---|---|
| **A** | `DB-14`, `DB-01` a `DB-10`, `DB-15`, `DB-13` | `BK-09` carril A, `API-09`, `API-10` | `DB-11` (cerrada), `DB-12`, `API-13`, `API-14` |
| **B** | `BK-01` a `BK-07`, `BK-08` | `BK-09` carril B, `API-06`, `API-07`, `API-08`, `API-11`, `API-12` | `API-15` a `API-19` |

`BK-00` está cerrada y no entra en el reparto. `BK-09` aparece en los dos carriles porque auth se construye a dos manos: el [plan de auth](specs/modules/auth/tasks.md) reparte sus doce tareas por archivo.

**Puntos de sincronización obligatorios:**

1. Al cerrar **`DB-14`**, porque `BK-06` y `BK-07` no pueden terminarse sin las tablas de `auth`. Es el primer punto donde B espera a A.
2. Al cerrar **`BK-07`**, porque todo lo demás depende del núcleo transversal.
3. Al cerrar **`DB-05`**, porque desbloquea las inserciones de recursos.
4. Antes de **`API-13`**, para confirmar que `DB-12` está instalada y probada.

El carril B construye el proyecto nuevo y su núcleo mientras el A prepara lo que falta en la base. Convergen en `BK-08`, que solo puede modelar lo que ya existe, y vuelven a separarse dentro de auth.

---

## Qué no está en ningún plan

- **La interfaz de usuario.** `frontend/` se borró entero y no tiene plan todavía. El orden natural es después de `BK-09`, cuando auth funcione y haya una sesión real que consumir. Su stack ya está fijado en `architecture.md` §3.
- **El despliegue.** No hay entorno desplegado: todo esto es desarrollo sobre una base local.
- **La carga de datos reales.** Los catálogos de proyectos, semilleros y equipos llegan por importación, y esa importación necesita `API-12`.
