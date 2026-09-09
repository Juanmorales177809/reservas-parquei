# Modelo de datos — LIA

## Alcance

LIA y Reservas comparten una única base PostgreSQL, pero mantienen responsabilidades y schemas lógicos separados. Este documento describe únicamente las tablas maestras de LIA. LIA no contiene FK, tablas ni reglas que dependan de Reservas.

## Tablas maestras

### `unidadOrganizacional.unidad_organizacional`

Fuente maestra de identidad y nombre de las unidades organizacionales. Sus campos principales incluyen `id_unidad` PK y `nombre`. Una unidad puede representar un laboratorio, agrupar otras unidades o cumplir otra función institucional.

### `cargos.cargo`

Catálogo de cargos. Cada cargo se relaciona con su unidad organizacional mediante la FK propia de LIA y define las acciones que puede ejercer el personal dentro de ese ámbito.

### `personal.personal`

Fuente maestra de personal, identidad institucional y relación con cargo/unidad. Incluye `id_persona` PK, `supabase_id UUID NULL UNIQUE` cuando aplique, `correo VARCHAR(150)` y las FK de cargo/unidad correspondientes. Reservas consulta directamente esta tabla para autenticación, ámbito y autorización; no conserva una proyección.

### `equipos.equipos`

Fuente maestra de equipos. `id_equipo` es la identidad referenciada por `reservas.reserva_equipos`. La unidad actual y `estado_operativo` se consultan directamente en LIA. Reservas no copia equipos ni administra su traslado, estado o identidad.

## Relación con Reservas

La relación es unidireccional en términos de dominio: las tablas de Reservas pueden referenciar `unidad_organizacional`, `personal`, `cargo` y `equipos` mediante FK PostgreSQL porque viven en la misma base; ninguna tabla de LIA referencia tablas del schema `reservas`.

LIA no decide qué unidades tienen configuración de reservas ni crea filas de Reservas. La existencia de una fila en `reservas.laboratorios_config` es responsabilidad de Reservas y no altera el significado de la unidad en LIA.

## Fuente de verdad

Nombre, identidad, cargo, unidad y estado operativo pertenecen a LIA. Configuración de reservas, espacios, recursos locales, solicitudes, disponibilidad, notificaciones y auditoría pertenecen a Reservas. No se mantienen duplicados ni mecanismos de sincronización entre dominios.
