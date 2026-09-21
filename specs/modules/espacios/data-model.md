# Modelo de datos — Espacios

## Fuente y alcance

Este documento define el modelo persistente completo del módulo `espacios`.

Se conserva la ubicación actual de las tablas de espacios dentro del schema `reservas`, aunque la responsabilidad funcional pertenece al módulo `espacios`.

El módulo administra:

- información general del espacio;
- pertenencia a una unidad organizacional;
- capacidad;
- disponibilidad horaria;
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
| `capacidad` | integer | Sí | Capacidad cuando aplique |
| `descripcion` | text | Sí | Descripción del espacio |
| `habilitado` | boolean | No | DEFAULT `true` |
| `created_at` | timestamptz | No | Fecha de creación |
| `updated_at` | timestamptz | No | Última actualización |

### Restricciones

```sql
UNIQUE (id_unidad, nombre)
```

```sql
CHECK (capacidad IS NULL OR capacidad > 0)
```

### Reglas de integridad

- Todo espacio pertenece a una única unidad organizacional.
- Un espacio deshabilitado no puede utilizarse en nuevas reservas.
- Deshabilitar un espacio no elimina su historial.
- `capacidad` puede ser `NULL` cuando no aplique al espacio.

### Índices recomendados

```text
(id_unidad, habilitado)
(nombre)
```

---

# 2. Disponibilidad horaria del espacio

## `reservas.espacio_horarios`

Permite definir una o varias franjas de disponibilidad por día de la semana.

| Campo | Tipo | Null | Restricción / descripción |
|---|---|---:|---|
| `id` | integer | No | PK; identity |
| `espacio_id` | integer | No | FK → `reservas.espacios(id)` |
| `dia_semana` | smallint | No | Día de la semana |
| `hora_inicio` | time | No | Inicio de la franja |
| `hora_fin` | time | No | Fin de la franja |
| `habilitado` | boolean | No | DEFAULT `true` |
| `created_at` | timestamptz | No | Fecha de creación |
| `updated_at` | timestamptz | No | Última actualización |

### Restricciones

```sql
CHECK (dia_semana BETWEEN 1 AND 7)
```

Convención:

```text
1 = lunes
2 = martes
3 = miércoles
4 = jueves
5 = viernes
6 = sábado
7 = domingo
```

```sql
CHECK (hora_inicio < hora_fin)
```

```sql
UNIQUE (espacio_id, dia_semana, hora_inicio, hora_fin)
```

### Reglas de integridad

- Un espacio puede tener cero o más franjas configuradas.
- Puede existir más de una franja para el mismo día.
- Las nuevas reservas por espacio deben encontrarse dentro de alguna franja habilitada.
- La validación de solapamientos entre reservas pertenece al módulo `reservas`.
- Deshabilitar una franja no elimina las reservas históricas.

### Índice recomendado

```text
(espacio_id, dia_semana, habilitado)
```

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

---

# 4. Campos adicionales configurables

## `reservas.espacios_campos`

Define campos dinámicos que el Usuario debe o puede diligenciar al reservar un espacio.

| Campo | Tipo | Null | Restricción / descripción |
|---|---|---:|---|
| `id` | integer | No | PK; identity |
| `espacio_id` | integer | No | FK → `reservas.espacios(id)` |
| `nombre` | varchar(150) | No | Etiqueta visible |
| `tipo_campo` | varchar(30) | No | Tipo funcional |
| `obligatorio` | boolean | No | DEFAULT `false` |
| `orden` | integer | No | Orden de presentación |
| `habilitado` | boolean | No | DEFAULT `true` |
| `created_at` | timestamptz | No | Fecha de creación |
| `updated_at` | timestamptz | No | Última actualización |

### Tipos de campo iniciales

```text
TEXTO
TEXTO_LARGO
NUMERO
BOOLEANO
SELECT
```

No deben agregarse nuevos tipos sin necesidad funcional.

### Restricciones

```sql
CHECK (
    tipo_campo IN (
        'TEXTO',
        'TEXTO_LARGO',
        'NUMERO',
        'BOOLEANO',
        'SELECT'
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

## `reservas.espacios_campos_opciones`

Define las opciones disponibles para campos `SELECT`.

| Campo | Tipo | Null | Restricción / descripción |
|---|---|---:|---|
| `id` | integer | No | PK; identity |
| `campo_id` | integer | No | FK → `reservas.espacios_campos(id)` |
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

- Solo los campos `SELECT` pueden tener opciones.
- Un campo `SELECT` habilitado debe tener al menos una opción habilitada.
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
reservas.espacios_campos
        |
        +---- reservas.espacios_campos_opciones
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
                    v
            reservas.espacios
              /      |      \
             /       |       \
            v        v        v
 espacio_horarios  espacio_recursos  espacios_campos
                       |                  |
                       v                  v
             recursos.recursos   espacios_campos_opciones
                                          |
                                          v
                              reserva_campos_valores
```

---

# 8. Cardinalidades

```text
unidad_organizacional 1 ─── N espacios

espacios 1 ─── N espacio_horarios

espacios N ─── N recursos
        mediante espacio_recursos

espacios 1 ─── N espacios_campos

espacios_campos 1 ─── N espacios_campos_opciones

espacios_campos 1 ─── N reserva_campos_valores
```

---

# 9. Ciclo de configuración de un espacio

El modelo permite que el Técnico de la unidad construya dinámicamente la configuración del espacio:

```text
Crear espacio
    |
    +--> información general
    |
    +--> capacidad, cuando aplique
    |
    +--> disponibilidad horaria
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
              +--> 0..N opciones si tipo = SELECT
```

Esta configuración se consume posteriormente desde el flujo de reserva por espacio.

---

# 10. Separación de responsabilidades

## Espacios

Es responsable de:

- existencia y configuración del espacio;
- capacidad;
- horario;
- asociación con recursos;
- definición de campos adicionales;
- definición de opciones.

## Recursos

Es responsable de:

- identidad del recurso;
- tipo de recurso;
- estado general;
- información especializada del recurso.

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

1. `capacidad` es opcional y, cuando exista, debe ser mayor que cero.
2. Un espacio puede existir sin recursos asociados.
3. Un espacio puede existir sin campos adicionales.
4. Un espacio puede tener varios recursos asociados.
5. Un espacio puede tener múltiples campos dinámicos.
6. Un campo `SELECT` utiliza opciones almacenadas de forma independiente.
7. Los recursos deben existir antes de ser asociados al espacio.
8. La asociación espacio–recurso no representa una asignación en una reserva.
9. La disponibilidad temporal no se almacena en `espacio_recursos`; se determina desde el dominio de reservas.
10. Campos y opciones utilizados históricamente deben conservarse aunque posteriormente se deshabiliten.
11. Las operaciones de configuración administrativa deben respetar el ámbito de autorización:
    - el Técnico administra únicamente espacios de su unidad;
    - el Administrador puede administrar espacios de cualquier unidad.

---

# 12. Puntos todavía no definidos

No se agregan al modelo hasta contar con una regla funcional explícita:

- excepciones de horario por fechas especiales o festivos;
- bloqueos manuales temporales del espacio por mantenimiento;
- eliminación física de espacios nunca utilizados;
- versionado completo de configuraciones de campos.

Si estas funcionalidades se requieren posteriormente, deben definirse primero en las reglas de negocio.
