# Plan de implementación — Reservas Parquei

Une los dos planes de trabajo y fija el orden entre ellos.

| Plan | Qué cubre |
|---|---|
| [Base de datos](specs/docs/tasks/base-de-datos.md) | 13 tareas `DB-XX`: schemas, referencias externas, datos iniciales, concurrencia y retirada del modelo anterior |
| [Contratos de API](specs/docs/tasks/contratos.md) | 19 tareas `API-XX`: convenciones transversales y los nueve contratos |
| [Backend nuevo](specs/docs/tasks/backend.md) | 9 tareas `BK-XX`: dónde vive el proyecto, con qué estructura y cómo se levanta antes de la primera ruta de negocio |
| [Auth en detalle](specs/modules/auth/tasks.md) | Desglose de la brecha entre el módulo implementado y su contrato |

La especificación está cerrada: nueve módulos con reglas, modelo, flujos y contrato, y las quince preguntas abiertas resueltas. **Lo que queda es construir.**

---

## La regla que ordena todo

**Una tarea de API no se cierra antes que la tarea de base de datos que la sostiene.** No por método, sino porque un endpoint sobre una tabla que no existe no se puede probar, y uno que "funciona" sin su restricción da una falsa sensación de terminado.

El caso que más importa es la concurrencia: `API-13` crea reservas y `DB-12` instala la garantía de que dos no ocupen el mismo espacio. **Se puede crear reservas sin `DB-12`, y ahí está el peligro**: todo parece correcto en una prueba manual y falla con dos usuarios simultáneos.

---

## Fase 0 — Desbloqueo inmediato

Sin esto nada más puede probarse contra la base ajustada.

| Tarea | Por qué ahora |
|---|---|
| `BK-01` a `BK-03` | Levantar el proyecto nuevo. El backend actual se conserva como referencia y no se extiende |
| `DB-08` | Los catálogos de tipos y estados están vacíos: ninguna reserva puede crearse |
| `DB-09` | Sin el catálogo de permisos no hay autorización posible |
| `BK-04` a `BK-07` | Las convenciones transversales, que son `API-01` a `API-04`. Reimplementarlas por módulo produce nueve APIs distintas |

`BK-07` depende de `DB-09`: es el primer punto donde los dos planes se tocan.

`DB-13` —desconectar el arranque heredado— deja de ser urgente al construir aparte: el backend nuevo nunca crea tablas, así que el riesgo solo existe si se levanta el antiguo. Se cierra al retirarlo.

---

## Fase 1 — Los schemas que faltan

Las cuatro son independientes entre sí y pueden ir en paralelo.

`DB-01` recursos · `DB-02` investigación · `DB-03` administration · `DB-04` notificaciones

Después, `DB-05` ejecuta el script de referencias externas que ya está escrito. **Aborta si falta algún destino**, así que exige `DB-01` y `DB-02` cerradas. Hasta entonces, `reserva_recursos` y `espacio_recursos` **no admiten ninguna inserción**: sus CHECK temporales exigen `NULL` en una columna obligatoria.

En paralelo: `DB-06` y `DB-07`, que ajustan `personal.personal.estado` y el estado de las unidades.

---

## Fase 2 — Identidad y estructura

| Orden | Tareas |
|---|---|
| 1 | `API-05` auth |
| 2 | `API-06` identidades y fichas de Personal |
| 3 | `API-07` unidades, cargos y permisos · `API-08` auditoría |

`API-06` **bloquea la invitación de cuentas `PERSONAL`**: auth exige una ficha activa antes de invitar, y esa ficha se crea en `/api/personal`.

---

## Fase 3 — Catálogos e inventario

`API-09` recursos → `API-10` espacios, que necesita recursos para asociarlos.

`API-11` investigación en paralelo.

`API-12` importaciones al final de esta fase: escribe en recursos y en investigación, así que las necesita a ambas.

---

## Fase 4 — Reservas

Aquí convergen los dos planes.

| Orden | Tareas | Bloqueo |
|---|---|---|
| 1 | `DB-11` | Resolver la contradicción del ADR sobre el periodo del recurso |
| 2 | `DB-12` | Instalar exclusiones y disparadores |
| 3 | `API-13` | Creación y consulta |
| 4 | `API-14` | Gestión, propuestas y ejecución |
| 5 | `API-15` · `API-16` | Órdenes, calendario y transiciones automáticas |

`DB-11` es una decisión, no código: el ADR dice que la entrega física abre el rango temporal y el modelo dice que entrega y devolución no alteran el periodo planificado. Resolverla cuesta una conversación; implementarla mal cuesta rehacer los disparadores.

---

## Fase 5 — Notificaciones y reportes

`API-17` bandeja → `API-18` generación y entrega.

`API-19` reportes, que necesita reservas reales para tener qué reportar.

---

## Los dos riesgos que conviene no perder de vista

**La concurrencia no está garantizada.** `database-status.md` lo advierte expresamente: que existan las columnas `periodo` y `bloqueante` y algunos índices **no equivale** a la protección. Mientras `DB-12` siga abierta, la funcionalidad de crear reserva no puede darse por correcta bajo carga, aunque funcione en todas las pruebas manuales.

**El backend sigue en el modelo anterior.** Sus consultas ya no son compatibles con las 28 tablas aplicadas. `DB-13` no es limpieza: es lo que impide que un arranque recree estructuras retiradas.

---

## Reparto para dos personas

Los carriles se reparten por propiedad de archivos, no por capas, para que dos personas no toquen el mismo archivo.

| Carril | Fases 0–1 | Fases 2–3 | Fases 4–5 |
|---|---|---|---|
| **A** | `DB-01`, `DB-02`, `DB-05`, `BK-08` | `API-05`, `API-06`, `API-09`, `API-10` | `DB-11`, `DB-12`, `API-13`, `API-14` |
| **B** | `BK-01` a `BK-07`, `DB-08`, `DB-09` | `DB-03`, `DB-04`, `API-07`, `API-08`, `API-11`, `API-12` | `API-15` a `API-19` |

Puntos de sincronización obligatorios: al cerrar `BK-07`, porque todo lo demás depende del núcleo transversal; al cerrar `DB-05`, porque desbloquea las inserciones de recursos; y antes de `API-13`, para confirmar que `DB-12` está instalada y probada.

El carril B construye el proyecto nuevo y su núcleo mientras el A prepara los schemas que faltan. Convergen en `BK-08`, que solo puede modelar lo que ya existe.

---

## Qué no está en ningún plan

- **La interfaz de usuario.** Los contratos definen la superficie HTTP; ninguna tarea cubre el cliente.
- **El despliegue.** No hay entorno desplegado: todo esto es desarrollo sobre una base local.
- **La carga de datos reales.** Los catálogos de proyectos, semilleros y equipos llegan por importación, y esa importación necesita `API-12`.
