# AGENTS.md

Instrucciones para agentes que trabajen en este repositorio.

Es un proyecto **spec-driven**: la especificación está cerrada y el código está por escribir. Eso invierte el reflejo habitual —leer el código para entender el sistema— porque **no hay código que leer**. La fuente de verdad son los documentos.

---

## Antes de tocar nada

Lee en este orden, y solo lo que necesites:

| Si vas a… | Lee |
|---|---|
| Entender el producto | [`specs/docs/spec.md`](specs/docs/spec.md) |
| Entender cómo se construye | [`plan.md`](plan.md) |
| Saber qué hacer a continuación | [`tasks.md`](tasks.md) |
| Implementar un endpoint | El contrato del módulo en [`specs/contratos/`](specs/contratos/) |
| Implementar una regla | `business-rules.md` del módulo propietario |
| Tocar el esquema | [`specs/docs/tasks/base-de-datos.md`](specs/docs/tasks/base-de-datos.md) y [`database-status.md`](specs/modules/reservations/database-status.md) |
| Escribir una prueba | [`specs/docs/testing.md`](specs/docs/testing.md) y el `tests.md` del módulo |

**No empieces a escribir código sin la tarea correspondiente de `tasks.md` delante.** Cada una declara objetivo, archivos afectados, dependencias y criterio de aceptación verificable. Si lo que te piden no está en ninguna tarea, eso es la señal de que falta abrirla, no de que sobre el plan.

---

## Las reglas que no se cruzan

**1. El backend nunca crea ni modifica tablas.** No hay `create_all`, ni creación al arrancar, ni `ALTER` desde un servicio. El esquema lo gobiernan las migraciones de `backend/migrations/`. Si al implementar descubres que falta una columna o una tabla, **abre una tarea `DB-XX`**; no la creas desde el código.

**2. El contrato manda sobre el código.** Cada ruta, cada campo del cuerpo y cada código de error ya están escritos. Si necesitas algo que el contrato no contempla, **corrige el contrato primero y después implementa**. Nunca al revés: un contrato que se actualiza para describir lo que ya se hizo deja de servir para nada.

**3. Los módulos no se llaman entre sí por HTTP.** Comparten proceso y base. Un módulo que necesita algo de otro usa su capa de servicios, respetando la propiedad de cada tabla.

**4. Cada regla pertenece a un módulo.** Cuando otro la necesita, la referencia en lugar de repetirla. Un módulo no redefine una regla global.

**5. Lo que garantiza la base, lo garantiza la base.** Unicidad, no solapamiento e integridad referencial se comprueban con restricciones, no con una consulta previa desde el servicio. Una consulta previa no protege de una carrera.

---

## Convenciones que cuesta caro ignorar

### Los identificadores de regla no son únicos en todo el sistema

`RN-IMP-06` existe en **administration** y en **resources**, con significados distintos. Hay once familias así. **Toda cita a una regla de otro módulo nombra su módulo.** La tabla completa está en [`specs/README.md`](specs/README.md).

Los prefijos: `RN-` reglas de negocio, `SEC-` controles de seguridad, `UF-` flujos de usuario, `OQ-` preguntas abiertas —las quince están resueltas—, `ADR-` decisiones arquitectónicas.

### PostgreSQL es la 13, no una posterior

- La unicidad condicional se resuelve con **índices únicos parciales**, no con `NULLS NOT DISTINCT`.
- La exclusión de solapamientos exige `btree_gist`, que ya está instalada.
- `gen_random_uuid()` sí pertenece al núcleo en la 13; no hace falta `pgcrypto`.

### La sesión vive en una cookie

El token viaja en una cookie `HttpOnly`, nunca en el cuerpo de la respuesta ni en `localStorage`, y **no contiene rol ni permisos**: se revalidan en el servidor en cada operación. Toda escritura exige CSRF de doble envío.

### Los errores tienen una sola forma

`{"error": {"codigo", "mensaje", "detalles"}}`, con el catálogo común de [`specs/contratos/README.md`](specs/contratos/README.md). Nunca el `detail` de FastAPI. `detalles` **jamás** contiene trazas, SQL ni variables de entorno.

### El idioma

La documentación y los identificadores del dominio están **en español**, con acentos. Los nombres de tabla, columna y campo de API son los de la especificación: `reserva_recursos`, `id_unidad`, `hora_inicio`. No los traduzcas ni los normalices.

Los mensajes de commit están en inglés.

---

## Qué no se toca

**La base de datos viva.** Es la única línea base que existe: ningún script de este repositorio reconstruye el esquema desde cero. No ejecutes migraciones destructivas ni `DROP ... CASCADE`. El volumen de PostgreSQL contiene las 28 tablas aplicadas.

**`backend/migrations/002_reservas_objetivo.sql` y `003_reservas_referencias_externas.sql`.** Ya se escribieron y `002` ya se aplicó. `003` está escrito y **nunca ejecutado**, a propósito: aborta si sus destinos no existen. No los edites; si algo falta, escribe una migración nueva.

**Los contratos cerrados**, salvo por la regla 2: se corrigen deliberadamente, no de paso.

---

## Cómo se valida un cambio

Antes de darlo por cerrado:

- **Documentación:** ejecuta `python tools/validar.py`. Comprueba enlaces, referencias colgadas y que toda tarea tenga fase y carril. Devuelve `1` si algo falla. Si tocaste reglas o pruebas, regenera la matriz con `python tools/trazabilidad.py`.
- **Tarea de base de datos:** el criterio de aceptación se comprueba **contra la base**, no contra el backend. Toda migración corre en una transacción, verifica que las tablas de origen estén vacías antes de tocarlas y no usa `DROP ... CASCADE`.
- **Tarea de API:** el criterio está escrito como una petición y su respuesta esperada, **incluido el caso de error**. «Quedó implementado» no es un criterio.
- **Prueba:** cita las reglas que cubre **por su identificador completo**, nunca por familia. `RN-DIS-05`, no `RN-DIS`: si no, no se sabe cuál se verificó, y la trazabilidad no la cuenta.

**Retirar un identificador es una decisión.** Si una regla o un flujo deja de existir, su número **no se reasigna** y la retirada se anota en [`identificadores-retirados.md`](specs/docs/decisions/identificadores-retirados.md). Reasignarlo haría que una referencia antigua apuntara en silencio a otra regla.

**Una tarea de API no se cierra antes que la tarea de base de datos que la sostiene.** Un endpoint sobre una tabla que no existe no se puede probar, y uno que «funciona» sin su restricción da una falsa sensación de terminado.

---

## Dos cosas que conviene no dar por supuestas

**La protección contra doble reserva está instalada, y sigue siendo la base quien la da.** Las exclusiones `ex_reserva_espacio_solape` (`reservas.reserva_espacio`) y `ex_reserva_recursos_solape` (`reservas.reserva_recursos`) existen en la base viva (verificado el 2026-09-29: un solape parcial desde la interfaz devuelve `409 SOLAPAMIENTO` y no inserta fila). No las sustituyas por una consulta previa desde el servicio ni las quites en una migración. Si una base nueva no las tiene, la reserva "funciona" con un solo usuario y falla con dos simultáneos.

**Los catálogos deben estar cargados.** Sin tipos de reserva, estados ni permisos no puede crearse ninguna reserva ni autorizarse ninguna operación (en la base viva ya lo están; una base nueva no los trae). Si algo falla con una clave foránea sin resolver, probablemente sea esto y no tu código. Al cargar una semilla usa un cliente en UTF-8: una carga con otra codificación guardó `??` en lugar de los acentos (repara `013_corregir_textos_tipos_evento.sql`).

---

## Si algo se contradice

Pasa, y es información: significa que un documento envejeció. **Señálalo en vez de elegir en silencio.** El orden de precedencia cuando dos documentos discrepan:

1. `specs/docs/architecture.md` para restricciones técnicas
2. El contrato del módulo para la superficie HTTP
3. `business-rules.md` del módulo propietario para el comportamiento
4. `data-model.md` para la estructura

Una contradicción entre un ADR y un modelo de datos no la resuelve el que implementa: se registra como decisión, con su fecha. Hay una abierta ahora mismo, sobre si la entrega física de un recurso abre su rango temporal.
