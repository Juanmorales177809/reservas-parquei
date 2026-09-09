# Espacios y recursos

## Propósito

Este documento define las reglas de negocio para administrar espacios y recursos reservables.

- Un `espacio` representa una ubicación o área administrable.
- Un `recurso` representa un elemento concreto que puede utilizarse dentro de un espacio.
- Un recurso pertenece exactamente a un espacio.

## Clasificación

- `Constraint`: regla obligatoria de validación, integridad o autorización.
- `Suggestion`: comportamiento configurable o recomendación.
- `Open question`: decisión de negocio aún pendiente.

## Espacios

### Constraint: datos básicos

Un espacio debe tener:

- `nombre`, entre 1 y 100 caracteres;
- `ubicacion`, con máximo de 200 caracteres;
- `capacidad`, mayor que cero;
- `estado` válido.

Los estados permitidos son:

| Estado | Significado |
|---|---|
| `activo` | El espacio está operativo y puede participar en la disponibilidad. |
| `inactivo` | El espacio no está disponible para operación normal. |

El nombre del espacio debe ser único. No se permiten espacios duplicados. La unicidad debe estar protegida en la aplicación y en la base de datos.

### Constraint: permisos

- Solo un administrador puede crear espacios.
- Solo un administrador puede actualizar espacios.
- Solo un administrador puede eliminar espacios.
- Un gestor puede consultar y configurar las reglas operativas de su espacio asignado.
- Un gestor no puede configurar un espacio que no tenga asignado.
- La eliminación requiere que el espacio no tenga reservas, recursos ni gestores asociados.

Cuando existen dependencias, el espacio debe conservarse y cambiarse a un estado no operativo en lugar de eliminarse.

### Constraint: capacidad

La capacidad del espacio debe ser mayor que cero.

La capacidad del espacio representa el límite general del área. La capacidad efectiva de una reserva se valida contra la capacidad del recurso seleccionado.

Debe evitarse que un recurso tenga una capacidad superior a la capacidad del espacio, salvo que el negocio defina explícitamente que ambas capacidades representan conceptos diferentes.

## Recursos

### Constraint: datos básicos

Un recurso debe tener:

- `nombre`, entre 1 y 100 caracteres;
- `espacio_id` válido;
- `tipo_recurso_id` válido;
- `capacidad`, mayor que cero;
- `estado` válido.

Los estados permitidos son:

- `activo`;
- `inactivo`;

No se utiliza un estado `mantenimiento` para espacios ni recursos.

Un recurso no puede crearse sin un espacio existente ni sin un tipo de recurso existente.

### Constraint: permisos y alcance

- Administradores pueden gestionar recursos de cualquier espacio.
- Gestores pueden crear, actualizar y eliminar recursos únicamente dentro de su espacio asignado.
- Un gestor no puede cambiar un recurso a otro espacio.
- Un gestor no puede manipular un recurso perteneciente a otro espacio.
- Los recursos pueden consultarse públicamente.
- La gestión de recursos requiere autenticación y rol de administrador o gestor.

### Constraint: integridad de recursos

1. No se puede mover un recurso que tenga reservas asociadas a otro espacio.
2. No se puede eliminar un recurso que tenga reservas asociadas.
3. El espacio del recurso debe mantenerse sincronizado cuando el recurso cambia.
4. El tipo de recurso debe existir antes de crear o actualizar el recurso.
5. Los recursos inactivos no deben considerarse disponibles para nuevas reservas.
6. Los nombres de recursos pueden repetirse, incluso dentro del mismo espacio.

## Horarios del espacio

### Constraint: configuración

La configuración de atención debe contener al menos una franja horaria.

Los días se representan con valores de `0` a `6`:

```text
0 = lunes
1 = martes
2 = miércoles
3 = jueves
4 = viernes
5 = sábado
6 = domingo
```

Las horas configurables deben estar entre `0` y `22` inclusive. Las horas se almacenan como números enteros y representan bloques de una hora.

El espacio debe mantener:

- `horario_atencion`;
- `dias_atencion`;
- `hora_apertura`;
- `hora_cierre`.

La hora de apertura debe ser menor que la hora de cierre.

Al actualizar el horario:

1. Se eliminan los días sin horas seleccionadas.
2. Se actualiza la lista de días de atención.
3. La apertura se calcula con la hora mínima configurada.
4. El cierre se calcula como una hora después de la hora máxima configurada.
5. Se actualiza el usuario responsable y la fecha de modificación.

### Suggestion

Se recomienda mantener una única fuente de verdad para el horario. `dias_atencion`, `hora_apertura` y `hora_cierre` pueden derivarse de `horario_atencion` para evitar inconsistencias.

## Anticipación y aprobación

### Constraint

`horas_antelacion` debe ser un valor entre `0` y `8760` horas.

El valor define cuánto tiempo antes del inicio de una reserva puede solicitarse el uso del espacio.

### Suggestion

El espacio puede configurar `aprobacion_automatica` para decidir si las reservas se aprueban inmediatamente o requieren revisión.

La aprobación automática aplica a las reservas de gestores sobre sus propios espacios y recursos. Las reservas sobre otros espacios o recursos requieren aprobación.

## Disponibilidad

La disponibilidad del espacio y sus recursos se calcula en bloques de una hora según:

- el día de la semana;
- el horario de atención;
- el estado del espacio;
- el estado del recurso;
- la anticipación mínima;
- las reservas bloqueantes existentes.

Un espacio o recurso que no esté `activo` debe mostrarse como no disponible y no debe ofrecerse para nuevas reservas.

Los endpoints de disponibilidad son públicos actualmente.

## Tipos de recurso

Los recursos deben pertenecer a un tipo existente.

Solo los tipos cuyo estado sea `activo` deben aparecer en el catálogo público de tipos.

El tipo de recurso contiene:

- nombre;
- descripción;
- estado.

El campo `activo` de `tipos_recursos` actualmente es un string. Los estados operativos de espacios y recursos son únicamente `activo` e `inactivo`.

## Desactivación de recursos con reservas futuras

### Constraint

Cuando un recurso se cambia a `inactivo` y tiene reservas futuras activas, el sistema debe informar a los usuarios propietarios, identificar las reservas afectadas, conservarlas y bloquear nuevas reservas sobre el recurso.

La desactivación no debe eliminar automáticamente las reservas existentes.

### Suggestion

El aviso debería generarse mediante una notificación persistente y, si está habilitado, también por correo electrónico.

## Auditoría

Las siguientes operaciones deben registrar auditoría:

- crear espacio;
- actualizar espacio;
- eliminar espacio;
- configurar horario o reglas del espacio;
- crear recurso;
- actualizar recurso;
- eliminar recurso.

La auditoría debe incluir el usuario responsable, la entidad, el identificador, la acción y una descripción.

## Reglas pendientes de decisión

1. ¿La capacidad del recurso puede superar la capacidad del espacio?
2. ¿Debe bloquearse la desactivación de un espacio con reservas futuras?
3. ¿Se debe permitir eliminar físicamente espacios y recursos o solo desactivarlos?
4. ¿La configuración de horario debe permitir minutos distintos de cero?
5. ¿La hora máxima configurable debe ser `22` o debe permitirse `23`?
6. ¿La aprobación automática debe configurarse también por recurso?
7. ¿Los tipos de recurso deben tener un catálogo administrable por usuarios?
8. ¿La capacidad del espacio debe validarse al crear y actualizar recursos?
