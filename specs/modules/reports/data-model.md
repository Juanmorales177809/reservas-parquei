# Modelo de datos — Reports

## Fuente y alcance

El [modelo principal](../../docs/data-model.md) no define tablas persistentes propias de reportes. El módulo consulta y agrega datos de otros dominios conforme a sus [reglas de negocio](business-rules.md); no se crean tablas nuevas por disponer de este documento.

## Fuentes de consulta

| Fuente | Datos utilizados | Modelo propietario |
|---|---|---|
| Reservas y sus detalles | Estados, fechas, horarios, asistentes, asignaciones y contexto histórico | [Reservations](../reservations/data-model.md) |
| Equipos, mobiliarios, otros y configuración e historial de horarios de laboratorios | Inventario, unidades, habilitación y horario vigente en cada periodo | [Resources](../resources/data-model.md) |
| Espacios | Capacidad, nombre y pertenencia organizacional | [Espacios](../espacios/data-model.md) |
| Proyectos, semilleros, pasantías y trabajos de grado | Dimensiones académicas/investigativas | [Researchs](../researchs/data-model.md) |
| Usuarios y personal | Identidades funcionales | [Usuarios](../usuarios/data-model.md) |
| Cuentas | Identidad autenticada y ámbito autorizado de consulta | [Auth](../auth/data-model.md) |
| Unidades, cargos y control de cambios | Estructura institucional y trazabilidad | [Administration](../administration/data-model.md) |

## Integridad de las consultas

Los reportes deben utilizar una versión coherente del modelo: el inventario actual o el objetivo una vez migrado. No deben unir tablas objetivo como si ya existieran en la base actual. Los identificadores de cuenta, usuario y personal se relacionan mediante las FK de Auth, no por igualdad implícita.

El contexto histórico registrado por reservas determina la clasificación de reservas pasadas; cambiar una vinculación de investigación no reclasifica ese historial. Las consultas respetan el ámbito autorizado y no modifican datos fuente.

## Pendientes

No se han definido vistas, vistas materializadas, tablas de agregación ni almacenamiento de exportaciones. Si se requieren, deberán especificarse sus columnas, fuentes, reglas de actualización y conservación. Las fórmulas de indicadores pertenecen a las reglas del módulo.
