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
| Unidades, cargos y auditoría administrativa | Estructura institucional y trazabilidad de las operaciones administrativas registradas en `administration.auditoria` | [Administration](../administration/data-model.md) |

## Integridad de las consultas

Los reportes deben utilizar una versión coherente del modelo: el inventario actual o el objetivo una vez migrado. No deben unir tablas objetivo como si ya existieran en la base actual. Los identificadores de cuenta, usuario y personal se relacionan mediante las FK de Auth, no por igualdad implícita.

El contexto histórico registrado por reservas determina la clasificación de reservas pasadas; cambiar una vinculación de investigación no reclasifica ese historial. Las consultas respetan el ámbito autorizado y no modifican datos fuente.

## Alcance de la trazabilidad disponible

`administration.auditoria` registra **únicamente operaciones administrativas** (`RN-AUD-01` a `RN-AUD-07`): altas, modificaciones, cambios de cargo, unidad o permisos, y desactivaciones. No registra el ciclo de vida de una reserva. La auditoría de Reservations está fuera del alcance funcional actual, y `reservas.control_cambios` es una tabla del inventario heredado que `administration.auditoria` sustituye; no se consulta como fuente.

La trazabilidad de una reserva se limita por tanto a `reservas.reserva_historial_estado`, que conserva sus transiciones de estado con el actor cuando lo hubo, el motivo y el instante. Un reporte de trazabilidad no puede atribuir a estas fuentes información que no registran, conforme a `RN-HIS-04`.

## Pendientes

No se han definido vistas, vistas materializadas, tablas de agregación ni almacenamiento de exportaciones. Si se requieren, deberán especificarse sus columnas, fuentes, reglas de actualización y conservación. Las fórmulas de indicadores pertenecen a las reglas del módulo.
