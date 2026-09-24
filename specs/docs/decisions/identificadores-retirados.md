# Identificadores retirados

Reglas, controles y flujos que existieron y dejaron de estar definidos. **Su número no se reasigna nunca**: reasignarlo haría que una referencia antigua apuntara en silencio a una regla distinta, que es peor que una referencia rota.

Esta tabla es la fuente que lee [`tools/validar.py`](../../../tools/validar.py) para no denunciar como colgada una cita a algo retirado a propósito.

| Identificador | Módulo | Retirado porque | Qué mirar en su lugar |
|---|---|---|---|
| `RN-ESP-HAB-03` | espacios | Enunciaba de forma genérica el mismo comportamiento que otra regla define completo, con la regla de cancelación citada, la advertencia previa y el efecto de no confirmar | `RN-ESP-HAB-05` de espacios |
| `RN-APR-09` | reservations | Retirado el 2026-09-24 por la decisión del hallazgo 1: un recurso sujeto a préstamo admite un solo compromiso vigente; no existe una solicitud posterior válida esperando su devolución para aprobarse automáticamente | `RN-RES-14` y `RN-DIS-06` de reservations |

## Lo que no entra en esta tabla

**Lo trasladado a otro módulo no está retirado.** `UF-RES-18` sigue definido en reservations con la marca *(trasladado)* y apunta a `UF-REP-02` de reports, que es donde vive ahora. Un flujo trasladado conserva su encabezado precisamente para que las referencias antiguas lleguen a alguna parte.

**Lo que nunca llegó a definirse tampoco entra.** Esta tabla registra identificadores que existieron, no numeraciones saltadas.

**Las tablas de base de datos retiradas no son identificadores.** `motivos_solicitud`, `control_cambios`, `mobiliarios` y las demás que el ajuste de septiembre retiró están documentadas en [`database-status.md`](../../modules/reservations/database-status.md).

## Cómo retirar un identificador

1. Borrar su definición del documento donde vivía.
2. Dejar en ese mismo punto una línea que explique por qué y a qué regla mirar.
3. Añadir la fila aquí.
4. Ejecutar `python tools/validar.py` y comprobar que no aparecen citas colgadas: si alguna sigue apuntando al identificador retirado sin explicación, hay que corregirla.
