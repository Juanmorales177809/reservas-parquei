# Modelo de datos de LIA

## Propósito

Este documento describe el modelo relacional actualmente desplegado en la base de datos `lia_db`. El modelo organiza unidades institucionales, cargos, personal y equipos en esquemas separados.

## Estado observado

- Base de datos: `lia_db`
- Motor: PostgreSQL 13
- Esquemas funcionales: `unidadOrganizacional`, `cargos`, `personal` y `equipos`
- Tablas: 4
- Datos actuales: las cuatro tablas están vacías
- Las relaciones se implementan mediante claves foráneas, sin tablas intermedias

## Relación lógica con `reservas_db`

`personal.personal` pertenece exclusivamente a `lia_db`. `reservas_db` no replica esta tabla ni crea una tabla local sustituta.

El contexto organizacional del personal se determina mediante:

```text
personal.personal → cargos.cargo → "unidadOrganizacional".unidad_organizacional
```

La relación con Reservas se establece lógicamente mediante:

```text
lia_db."unidadOrganizacional".unidad_organizacional.id_unidad
↔ reservas_db.laboratorios.lia_unidad_id
```

No existe ni se define una FK física entre las dos bases de datos.

La cardinalidad es:

```text
LIA unidad_organizacional 1 ─── 0..1 reservas.laboratorios
```

Una unidad de LIA puede no participar en Reservas. Una unidad de LIA reservable puede corresponder como máximo a un laboratorio de Reservas. Cada laboratorio de Reservas corresponde obligatoriamente a una unidad de LIA mediante `laboratorios.lia_unidad_id`, que es único.

Las unidades organizacionales que solo agrupan otras unidades o laboratorios no deben tener una fila correspondiente en `reservas_db.laboratorios`.

`unidad_organizacional.nombre` es la fuente maestra del nombre del laboratorio. `reservas_db.laboratorios.nombre` es únicamente una caché local, no editable desde Reservas, que se actualiza cuando cambia el nombre en LIA. Su finalidad es acelerar consultas y permitir que Reservas continúe operando si LIA está temporalmente no disponible.

## Diagrama lógico

```text
unidadOrganizacional.unidad_organizacional
        ├──< cargos.cargo
        │       └──< personal.personal
        └──< equipos.equipos
```

Una unidad organizacional puede tener varios cargos y equipos. Cada persona pertenece a un cargo. La unidad organizacional también admite jerarquía mediante una referencia a otra unidad padre. No todas las unidades participan en Reservas; solo las que representan laboratorios reservables se vinculan lógicamente con `reservas_db.laboratorios`.

## Esquemas y tablas

### `unidadOrganizacional.unidad_organizacional`

Catálogo jerárquico de unidades organizacionales.

| Columna | Tipo | Nulo | Default | Descripción |
|---|---|---:|---|---|
| `id_unidad` | `integer` | No | Identity | Identificador único de la unidad. |
| `nombre` | `varchar(100)` | No | — | Nombre de la unidad. |
| `tipo` | `varchar(50)` | No | — | Tipo o clasificación de la unidad. |
| `id_unidad_padre` | `integer` | Sí | — | Unidad superior; permite construir la jerarquía. |

Restricciones:

- PK: `pk_unidad_organizacional` sobre `id_unidad`.
- Única: `uq_unidad_organizacional_nombre` sobre `nombre`.
- FK: `fk_unidad_organizacional_padre`, `id_unidad_padre` → `unidadOrganizacional.unidad_organizacional(id_unidad)`.

### `cargos.cargo`

Catálogo de cargos asociados a una unidad organizacional.

| Columna | Tipo | Nulo | Default | Descripción |
|---|---|---:|---|---|
| `id_cargo` | `integer` | No | Identity | Identificador único del cargo. |
| `nombre_cargo` | `varchar(50)` | No | — | Nombre del cargo. |
| `id_unidad` | `integer` | No | — | Unidad organizacional a la que pertenece. |

Restricciones:

- PK: `pk_cargo` sobre `id_cargo`.
- FK: `fk_cargo_unidad`, `id_unidad` → `unidadOrganizacional.unidad_organizacional(id_unidad)`.

### `personal.personal`

Directorio de personas vinculadas a un cargo.

| Columna | Tipo | Nulo | Default | Descripción |
|---|---|---:|---|---|
| `id_persona` | `integer` | No | Identity | Identificador único de la persona. |
| `nombre` | `varchar(50)` | No | — | Nombre completo o nombre de presentación. |
| `id_cargo` | `integer` | No | — | Cargo asignado a la persona. |
| `documento` | `varchar(20)` | No | — | Documento de identificación. |
| `correo` | `varchar(150)` | No | — | Correo electrónico. |
| `supabase_id` | `uuid` | Sí | — | Identificador Supabase; único cuando esté informado. |
| `telefono` | `varchar(20)` | No | — | Teléfono de contacto. |
| `estado` | `boolean` | Sí | — | Estado de la persona; su semántica debe definirse en la lógica de negocio. |

Restricciones:

- PK: `pk_personal` sobre `id_persona`.
- Única: `uq_personal_documento` sobre `documento`.
- Única: `uq_personal_correo` sobre `correo`.
- Única: `uq_personal_telefono` sobre `telefono`.
- Única: `uq_personal_supabase_id` sobre `supabase_id`.
- FK: `fk_personal_cargo`, `id_cargo` → `cargos.cargo(id_cargo)`.

### `equipos.equipos`

Inventario de equipos asociados a una unidad organizacional.

| Columna | Tipo | Nulo | Default | Descripción |
|---|---|---:|---|---|
| `id_equipo` | `integer` | No | Sequence | Identificador único del equipo. |
| `id_unidad` | `integer` | No | — | Unidad organizacional responsable. |
| `nombre_equipo` | `varchar(50)` | No | — | Nombre del equipo. |
| `placa` | `varchar(40)` | Sí | — | Placa o identificador patrimonial. |
| `serial` | `varchar(50)` | Sí | — | Número serial del equipo. |
| `marca` | `varchar(50)` | Sí | — | Marca. |
| `modelo` | `varchar(50)` | Sí | — | Modelo. |
| `image_path` | `varchar(100)` | Sí | — | Ruta de la imagen. |
| `manual_operacion` | `varchar(100)` | Sí | — | Ruta del manual de operación. |
| `requiere_calibracion` | `boolean` | Sí | — | Indica si requiere calibración. |
| `guia_rapida` | `varchar(100)` | Sí | — | Ruta de la guía rápida. |
| `instalador` | `varchar(100)` | Sí | — | Ruta o referencia del instalador. |
| `estado` | `boolean` | Sí | — | Estado operativo del equipo. |
| `id_categoria` | `integer` | Sí | — | Identificador de categoría; actualmente no tiene FK declarada. |
| `proxima_fecha_calibracion` | `date` | Sí | — | Próxima fecha de calibración. |
| `proxima_fecha_mantenimiento` | `date` | Sí | — | Próxima fecha de mantenimiento. |
| `frecuencia_calibracion` | `integer` | Sí | — | Frecuencia de calibración, en unidad pendiente de definir. |
| `frecuencia_mantenimiento` | `integer` | Sí | — | Frecuencia de mantenimiento, en unidad pendiente de definir. |

Restricciones:

- PK: `pk_equipos` sobre `id_equipo`.
- Única: `uq_equipos_placa` sobre `placa`.
- Única: `uq_equipos_serial` sobre `serial`.
- FK: `fk_equipos_unidad`, `id_unidad` → `unidadOrganizacional.unidad_organizacional(id_unidad)`.

## Reglas e implicaciones para la lógica de SDD

1. No se puede crear un cargo sin una unidad organizacional existente.
2. No se puede registrar personal sin un cargo existente.
3. No se puede registrar un equipo sin una unidad organizacional existente.
4. `nombre` de unidad, documento, correo, teléfono, placa y serial deben tratarse como valores únicos.
5. `id_categoria` en equipos es actualmente un identificador sin entidad referenciada; debe definirse antes de implementar validaciones de categoría.
6. Las columnas `estado` aceptan `NULL`; la lógica de SDD debe decidir si `NULL` representa un estado desconocido o si deben agregarse valores por defecto y restricciones `NOT NULL`.
7. Las columnas de frecuencia no documentan su unidad de medida; debe establecerse si representan días, meses u otra unidad.
8. La eliminación de una unidad, cargo o persona debe considerar las referencias existentes. No hay reglas `ON DELETE` explícitas en el modelo actual.

## Secuencias e identidad

- `unidadOrganizacional.unidad_organizacional_id_unidad_seq`
- `cargos.cargo_id_cargo_seq`
- `personal.personal_id_persona_seq`
- `equipos.equipos_id_equipo_seq`

Las tres primeras claves usan columnas `IDENTITY`; `equipos.id_equipo` usa una secuencia explícita como valor por defecto.

## Convenciones de acceso

Desde otro contenedor conectado a la red de base de datos:

```text
Host: lia_db
Puerto: 5432
Base de datos: lia_db
```

Desde fuera de Docker, usando el puerto publicado por el servidor:

```text
Host: IP_DEL_SERVIDOR
Puerto: 5433
Base de datos: lia_db
```
