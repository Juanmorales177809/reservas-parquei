# Estrategia de pruebas

Cómo se verifica que lo construido corresponde a lo especificado. Es el paso que cierra el ciclo: sin él, `tasks.md` produce código y nadie comprueba que cumpla las reglas.

`architecture.md` §18 establece que cada módulo define sus pruebas. Este documento fija cómo se escriben; el `tests.md` de cada módulo dice cuáles.

---

## La regla que ordena todo

**Cada garantía se prueba en la capa que la ofrece.**

| La garantía la da | Se prueba contra | Por qué no basta lo otro |
|---|---|---|
| Una restricción de la base | La base, con SQL | Un servicio que consulta antes de escribir pasa la prueba y pierde la carrera |
| Una regla de negocio | El servicio, sin HTTP | Probarla por la API mezcla el fallo de la regla con el del enrutado |
| El contrato | La API, con una petición real | Un servicio correcto tras una ruta mal declarada sigue siendo un contrato incumplido |

Probar una exclusión de solapamiento llamando al endpoint y comprobando que devuelve `409` **no prueba nada sobre concurrencia**: prueba que la comprobación previa funciona cuando no hay nadie más. La prueba real abre dos transacciones.

---

## Los tres niveles

### Base de datos

Verifican restricciones, índices únicos parciales, CHECK y exclusiones. Se ejecutan con SQL sobre una base real, **sin pasar por el backend**.

Es el único nivel que puede acreditar la protección contra doble reserva. Ya existe un precedente en [`backend/tests/sql/`](../../backend/tests/sql/): las consultas que verificaron el ajuste de septiembre comprobando tablas esperadas y retiradas, columnas exactas, claves foráneas sin cascadas y rechazo de horarios inválidos.

### Servicio

Verifican las reglas de negocio con la base real pero sin HTTP: se llama a la capa de servicios directamente. Es donde vive la mayoría de las `RN`.

### Contrato

Verifican la superficie HTTP con una petición completa: ruta, cuerpo, código de estado, forma de la respuesta y **el caso de error**. Una prueba de contrato que solo comprueba el camino feliz no cubre el contrato, porque cada endpoint declara sus errores.

---

## Cómo se escribe una prueba

```markdown
### T-RES-01 — Título en una línea

- **Nivel:** base de datos | servicio | contrato
- **Cubre:** `RN-DIS-05`, `SEC-SES-07`
- **Caso:** el estado de partida y lo que se hace.
- **Esperado:** lo observable, incluido lo que **no** debe pasar.
```

Los identificadores son `T-<PREFIJO>-<NN>`, con el mismo prefijo que los flujos del módulo: `AUTH`, `USR`, `ADM`, `RES`, `ESP`, `REC`, `INV`, `NOT`, `REP`.

**`Cubre:` es lo que lee la trazabilidad.** Se citan reglas por su identificador completo, nunca por familia: `RN-DIS-05`, no `RN-DIS`. Una cita por familia no dice cuál de las reglas se probó, y once familias se repiten entre módulos con significados distintos.

**`Esperado:` describe lo observable, no la implementación.** «Devuelve `409 SOLAPAMIENTO`» sirve; «llama a `verificar_solapamiento`» no, porque deja de valer al refactorizar.

---

## El entorno de pruebas

**Base aislada, nunca la de desarrollo.** Las pruebas escriben, y la base de desarrollo es la única línea base que existe: ningún script reconstruye el esquema desde cero.

**El esquema se aplica con las mismas migraciones.** Si una prueba necesita una tabla que ninguna migración crea, la que falta es la migración. No se crea desde el código de pruebas, por la misma razón por la que no se crea desde el backend.

**Cada prueba deja la base como la encontró.** Lo normal es abrir una transacción y deshacerla al terminar. Las pruebas de concurrencia son la excepción —necesitan dos transacciones de verdad— y limpian explícitamente.

**Los catálogos se cargan con los mismos `seeds/` que producción.** Un catálogo distinto en pruebas convierte la prueba en ficción.

---

## Cuándo una tarea está probada

Una tarea de `tasks.md` no se cierra hasta que su criterio de aceptación tiene una prueba que lo ejecuta. Los criterios ya están escritos como petición y respuesta esperada, así que la prueba es su traducción directa.

Tres casos que se olvidan y cuestan caro:

**El caso de error.** Cada endpoint declara los suyos en el contrato. Un contrato con cinco códigos de error y pruebas de uno solo está probado en un quinto.

**La denegación.** «Si el permiso no puede comprobarse, deniega» es una regla, y sin prueba es una intención. Lo mismo con el ámbito: un Técnico sobre una unidad ajena.

**La no enumeración.** Registro, recuperación e inicio de sesión deben responder igual exista o no el correo, **sin diferencias observables de cuerpo ni de tiempo**. Es la única familia de pruebas donde el tiempo de respuesta forma parte del resultado.

---

## Qué no cubre esta estrategia

- **La interfaz de usuario.** No hay frontend todavía ni plan para él.
- **Carga y rendimiento.** El sistema es de uso institucional y acotado; si aparece un requisito de carga, se decide entonces.
- **Seguridad ofensiva.** Los controles `SEC` se prueban como comportamiento esperado, no mediante intentos de intrusión.

---

## Estado

Ninguna prueba está implementada: no hay código que probar. Los `tests.md` de cada módulo fijan qué debe verificarse, y [`trazabilidad.md`](trazabilidad.md) muestra cuánto de la especificación tiene ya una prueba declarada.

El orden es el de `tasks.md`: las pruebas de un módulo se escriben con el módulo, no después de todos.
