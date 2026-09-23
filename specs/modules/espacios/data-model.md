# Modelo de datos — Espacios

## Fuente y alcance

Este documento define el modelo persistente completo del módulo `espacios`.

Se conserva la ubicación actual de las tablas de espacios dentro del schema `reservas`, aunque la responsabilidad funcional pertenece al módulo `espacios`.

El módulo administra:

- información general del espacio;
- pertenencia a una unidad organizacional;
- capacidad;
- recursos asociados;
- campos adicionales configurables;
- opciones de campos de selección.

El módulo `reservas` consume esta configuración al crear una reserva, pero no administra la definición del espacio.

Convenciones:

- `PK`: clave primaria.
- `FK`: clave foránea.
- `UQ`: restricción única.
- `NN`: `NOT NULL`.
- Las FK sin acción explícita usan `NO ACTION`.
- Las identidades usan el mismo tipo de la PK referenciada.
- Los registros utilizados históricamente no deben eliminarse físicamente cuando su eliminación impida interpretar reservas existentes.

---

# 1. Espacios

## `reservas.espacios`

Representa un espacio reservable perteneciente a una unidad organizacional.

| Campo | Tipo | Null | Restricción / descripción |
|---|---|---:|---|
| `id` | integer | No | PK; identity |
| `id_unidad` | integer | No | FK → `unidadOrganizacional.unidad_organizacional(id_unidad)` |
| `nombre` | varchar(100) | No | Nombre del espacio |
| `ubicacion` | varchar(255) | Sí | Ubicación física |
| `capacidad` | integer | No | Capacidad máxima del espacio; debe ser mayor que cero |
| `descripcion` | text | Sí | Descripción del espacio |
| `habilitado` | boolean | No | DEFAULT `true` |
| `created_at` | timestamptz | No | Fecha de creación |
| `updated_at` | timestamptz | No | Última actualización |

### Restricciones

```sql
UNIQUE (id_unidad, nombre)
```

```sql
CHECK (capacidad > 0)
```

### Reglas de integridad

- Todo espacio pertenece a una única unidad organizacional.
- Un espacio deshabilitado no puede utilizarse en nuevas reservas.
- Deshabilitar un espacio no elimina su historial.
- `capacidad` siempre debe estar declarada y ser mayor que cero.

### Índices recomendados

```text
(id_unidad, habilitado)
(nombre)
```

---

# 2. Horario compartido de la unidad

El espacio utiliza el horario de atención de su unidad, conforme a RN-ESP-DIS-02. La configuración se almacena una sola vez por unidad en [`reservas.laboratorios_config`](../resources/data-model.md#reservaslaboratorios_config), administrada por Resources, y aplica tanto a espacios como a recursos.

Al crear un espacio, `reservas.espacios.id_unidad` determina la configuración que se consulta mediante `laboratorios_config.id_unidad`. No se crean filas de horario ni se copian días o franjas al espacio. El módulo Espacios no tiene una tabla de horarios ni permite sobrescribir el horario de la unidad.

Reservations consulta esta configuración compartida y las reservas bloqueantes para calcular la disponibilidad de cada espacio o recurso. Las fechas y horas de una reserva siguen perteneciendo a Reservations y no constituyen una configuración de horario independiente.

---

# 3. Recursos asociados al espacio

## `reservas.espacio_recursos`

Relaciona un espacio con los recursos que forman parte de su configuración habitual.

| Campo | Tipo | Null | Restricción / descripción |
|---|---|---:|---|
| `espacio_id` | integer | No | PK/FK → `reservas.espacios(id)` |
| `recurso_id` | integer | No | PK/FK → `recursos.recursos(id)` |
| `habilitado` | boolean | No | DEFAULT `true` |
| `created_at` | timestamptz | No | Fecha de asociación |
| `updated_at` | timestamptz | No | Última actualización |

### Clave primaria

```sql
PRIMARY KEY (espacio_id, recurso_id)
```

### Reglas de integridad

- El recurso debe existir previamente en `recursos.recursos`.
- El espacio y el recurso deben pertenecer a la misma unidad organizacional.
- Un recurso solo puede tener una asociación habilitada con un espacio. Para asociarlo a otro espacio, primero debe deshabilitarse su asociación vigente.
- Asociar un recurso a un espacio no crea el recurso.
- La asociación indica que el recurso puede formar parte del uso habitual del espacio.
- La asociación no garantiza disponibilidad temporal.
- La disponibilidad para una reserva concreta se valida en `reservas`.
- Un recurso asociado que no esté disponible no impide reservar el espacio.
- Si una asociación deja de ser válida, debe deshabilitarse cuando sea necesario conservar trazabilidad histórica.

### Índices recomendados

```text
(recurso_id, habilitado)
(espacio_id, habilitado)
```

La unicidad de la asociación activa se garantiza con un índice único parcial:

```sql
CREATE UNIQUE INDEX uq_espacio_recursos_recurso_activo
    ON reservas.espacio_recursos (recurso_id)
    WHERE habilitado = true;
```

---

# 4. Campos adicionales configurables

## `reservas.espacio_campos`

Define campos dinámicos que el Usuario debe o puede diligenciar al reservar un espacio.

| Campo | Tipo | Null | Restricción / descripción |
|---|---|---:|---|
| `id` | integer | No | PK; identity |
| `espacio_id` | integer | No | FK → `reservas.espacios(id)` |
| `nombre` | varchar(150) | No | Etiqueta visible |
| `tipo_campo` | varchar(30) | No | Tipo funcional; CHECK sobre los cinco valores admitidos |
| `obligatorio` | boolean | No | DEFAULT `false` |
| `orden` | integer | No | Orden de presentación |
| `habilitado` | boolean | No | DEFAULT `true` |
| `created_at` | timestamptz | No | Fecha de creación |
| `updated_at` | timestamptz | No | Última actualización |

### Tipos de campo admitidos

```text
TEXTO
TEXTO_LARGO
NUMERO
BOOLEANO
SELECCION
```

El catálogo es cerrado y lo fija `RN-ESP-CAM-02`. Añadir un tipo exige modificar esa regla, el CHECK y la validación del formulario de reserva, porque cada tipo necesita saber cómo se presenta y cómo se valida lo diligenciado.

### Restricciones

```sql
CHECK (
    tipo_campo IN (
        'TEXTO',
        'TEXTO_LARGO',
        'NUMERO',
        'BOOLEANO',
        'SELECCION'
    )
)
```

```sql
CHECK (orden >= 0)
```

```sql
UNIQUE (espacio_id, nombre)
```

### Reglas de integridad

- Un espacio puede tener cero o más campos adicionales.
- Los campos adicionales complementan el tipo de reserva `ESPACIO`; no modifican sus reglas estructurales.
- Un campo no puede eliminar la obligación de fecha, hora, disponibilidad o cualquier otra regla propia de la reserva por espacio.
- Los campos obligatorios deben tener valor antes de enviar la reserva.
- Los campos usados históricamente no deben eliminarse físicamente si eso impide interpretar reservas anteriores.
- Un campo deshabilitado no se muestra en nuevas reservas.

### Índice recomendado

```text
(espacio_id, habilitado, orden)
```

---

# 5. Opciones de campos de selección

## `reservas.espacio_campo_opciones`

Define las opciones disponibles para campos `SELECCION`.

| Campo | Tipo | Null | Restricción / descripción |
|---|---|---:|---|
| `id` | integer | No | PK; identity |
| `campo_id` | integer | No | FK → `reservas.espacio_campos(id)` |
| `valor` | varchar(255) | No | Valor visible |
| `orden` | integer | No | Orden de presentación |
| `habilitado` | boolean | No | DEFAULT `true` |
| `created_at` | timestamptz | No | Fecha de creación |
| `updated_at` | timestamptz | No | Última actualización |

### Restricciones

```sql
CHECK (orden >= 0)
```

```sql
UNIQUE (campo_id, valor)
```

### Reglas de integridad

- Solo los campos `SELECCION` pueden tener opciones.
- Un campo `SELECCION` habilitado debe tener al menos una opción habilitada.
- Una opción solo puede pertenecer a un campo.
- Una opción deshabilitada no puede seleccionarse en nuevas reservas.
- Las opciones utilizadas históricamente deben conservarse para interpretar reservas anteriores.

### Índice recomendado

```text
(campo_id, habilitado, orden)
```

---

# 6. Respuestas de una reserva

Las respuestas no pertenecen al módulo `espacios`.

Se almacenan en:

```text
reservas.reserva_campos_valores
```

definida en el módulo `reservas`.

Relación conceptual:

```text
reservas.espacio_campos
        |
        +---- reservas.espacio_campo_opciones
        |
        v
reservas.reserva_campos_valores
```

El módulo `reservas` debe garantizar que:

- `campo_id` pertenezca al espacio reservado;
- los campos obligatorios tengan respuesta;
- si se utiliza `opcion_id`, la opción pertenezca al campo;
- una opción deshabilitada no pueda utilizarse para una nueva reserva;
- la interpretación histórica se conserve mediante los snapshots definidos en el modelo de reservas.

---

# 7. Relación conceptual completa

```text
unidadOrganizacional.unidad_organizacional
    |
    +--> reservas.laboratorios_config (horario compartido; Resources)
    |
    +--> reservas.espacios
             |
             +--> espacio_recursos --> recursos.recursos
             |
             +--> espacio_campos
                       |
                       +--> espacio_campo_opciones
                       |
                       +--> reserva_campos_valores
```

---

# 8. Cardinalidades

```text
unidad_organizacional 1 ─── N espacios

unidad_organizacional 1 ─── 0..1 laboratorios_config (Resources)

espacios 1 ─── N espacio_recursos
recursos 1 ─── 0..1 asociación habilitada
        mediante espacio_recursos

espacios 1 ─── N espacio_campos

espacio_campos 1 ─── N espacio_campo_opciones

espacio_campos 1 ─── N reserva_campos_valores
```

---

# 9. Ciclo de configuración de un espacio

El modelo permite que el Técnico de la unidad construya dinámicamente la configuración del espacio:

```text
Crear espacio
    |
    +--> información general
    |
    +--> capacidad máxima (obligatoria y mayor que cero)
    |
    +--> consulta del horario compartido mediante id_unidad
    |
    +--> asociar 0..N recursos existentes
    |
    +--> crear 0..N campos adicionales
              |
              +--> tipo
              +--> obligatorio/opcional
              +--> orden
              +--> habilitado
              |
              +--> 0..N opciones si tipo = SELECCION
```

Esta configuración se consume posteriormente desde el flujo de reserva por espacio.

---

# 10. Separación de responsabilidades

## Espacios

Es responsable de:

- existencia y configuración del espacio;
- capacidad;
- asociación con recursos;
- definición de campos adicionales;
- definición de opciones.

## Recursos

Es responsable de:

- identidad del recurso;
- tipo de recurso;
- estado general;
- información especializada del recurso.

También administra la configuración de atención de la unidad en `reservas.laboratorios_config`, incluido el horario compartido que consumen todos sus espacios y recursos.

## Reservas

Es responsable de:

- fecha y hora solicitadas;
- disponibilidad temporal;
- solapamientos;
- asignación efectiva de recursos;
- respuestas diligenciadas para los campos del espacio;
- aprobación;
- ejecución;
- cancelación;
- historial.

---

# 11. Decisiones de integridad

1. `capacidad` es obligatoria y debe ser mayor que cero.
2. Un espacio puede existir sin recursos asociados.
3. Un espacio puede existir sin campos adicionales.
4. Un espacio puede tener varios recursos asociados.
5. Un espacio puede tener múltiples campos dinámicos.
6. Un campo `SELECCION` utiliza opciones almacenadas de forma independiente.
7. Los recursos deben existir antes de ser asociados al espacio.
8. La asociación espacio–recurso no representa una asignación en una reserva.
9. La disponibilidad temporal no se almacena en `espacio_recursos`; se determina desde el dominio de reservas.
10. Campos y opciones utilizados históricamente deben conservarse aunque posteriormente se deshabiliten.
11. Las operaciones de configuración administrativa deben respetar el ámbito de autorización:
    - el Técnico administra únicamente espacios de su unidad;
    - el Administrador puede administrar espacios de cualquier unidad.
12. El horario se consulta desde la configuración de la unidad; crear o editar un espacio no crea ni modifica un horario propio.
13. Un recurso solo puede tener una asociación habilitada con un espacio y debe pertenecer a la misma unidad organizacional del espacio. Para cambiarlo de espacio, se deshabilita primero la asociación vigente.

---

# 12. Puntos todavía no definidos

No se agregan al modelo hasta contar con una regla funcional explícita:

- excepciones de horario por fechas especiales o festivos;
- bloqueos manuales temporales del espacio por mantenimiento;
- eliminación física de espacios nunca utilizados;
- versionado completo de configuraciones de campos.

Si estas funcionalidades se requieren posteriormente, deben definirse primero en las reglas de negocio.
