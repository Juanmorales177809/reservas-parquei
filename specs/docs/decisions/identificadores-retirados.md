# Identificadores retirados

Reglas, controles y flujos que existieron y dejaron de estar definidos. **Su número no se reasigna nunca**: reasignarlo haría que una referencia antigua apuntara en silencio a una regla distinta, que es peor que una referencia rota.

Esta tabla es la fuente que lee [`tools/validar.py`](../../../tools/validar.py) para no denunciar como colgada una cita a algo retirado a propósito.

| Identificador | Módulo | Retirado porque | Qué mirar en su lugar |
|---|---|---|---|
| `RN-ESP-HAB-03` | espacios | Enunciaba de forma genérica el mismo comportamiento que otra regla define completo, con la regla de cancelación citada, la advertencia previa y el efecto de no confirmar | `RN-ESP-HAB-05` de espacios |
| `RN-APR-09` | reservations | Retirado el 2026-09-24 por la decisión del hallazgo 1: un recurso sujeto a préstamo admite un solo compromiso vigente; no existe una solicitud posterior válida esperando su devolución para aprobarse automáticamente | `RN-RES-14` y `RN-DIS-06` de reservations |
| `RN-ID-01` | usuarios | Retirada la familia `RN-ID` de `usuarios`: la identidad la define `auth` | `RN-AUTH-ID-01` de auth |
| `RN-ID-04` | usuarios | Retirada la familia `RN-ID` de `usuarios`: la identidad la define `auth` | `RN-AUTH-ID-03` de auth |
| `RN-ID-05` | usuarios | Retirada la familia `RN-ID` de `usuarios`: la identidad la define `auth` | `RN-AUTH-ID-03` de auth |
| `RN-ID-07` | usuarios | Retirada la familia `RN-ID` de `usuarios`: la identidad la define `auth` | `RN-AUTH-ID-05` de auth |
| `RN-ID-12` | usuarios | Retirada la familia `RN-ID` de `usuarios`: la identidad la define `auth` | `RN-AUTH-ID-02` de auth |
| `RN-AUT-03` | usuarios | Retirada la familia `RN-AUT` de `usuarios`: las sesiones las define `auth` | `RN-AUTH-SES-01` de auth |
| `RN-AUT-04` | usuarios | Retirada la familia `RN-AUT` de `usuarios`: las sesiones las define `auth` | `RN-AUTH-SES-01` de auth |
| `RN-AUT-06` | usuarios | Retirada la familia `RN-AUT` de `usuarios`: las sesiones las define `auth` | `RN-AUTH-SES-02` de auth |
| `RN-AUTZ-01` | usuarios | Retirada la familia `RN-AUTZ` de `usuarios`: la autorización la define `auth` | `RN-AUTH-ROL-02` y `RN-AUTH-ROL-07` de auth |
| `RN-AUTZ-02` | usuarios | Retirada la familia `RN-AUTZ` de `usuarios`: la autorización la define `auth` | `RN-AUTH-ROL-05` y `RN-AUTH-ROL-07` de auth |
| `RN-AUTZ-03` | usuarios | Retirada la familia `RN-AUTZ` de `usuarios`: la autorización la define `auth` | `RN-AUTH-ROL-05` y `RN-AUTH-ROL-07` de auth |
| `RN-PRF-01` | administration | Trasladados los perfiles académicos a `researchs`, que los define en `RN-INV` | `RN-INV-12` a `RN-INV-16` de researchs |
| `RN-PRF-03` | administration | Retirado: sus citas usaban «perfil» como rol de cuenta | `RN-AUTH-ROL-04` de auth |
| `RN-PRF-04` | administration | Trasladados los perfiles académicos a `researchs`, que los define en `RN-INV` | `RN-INV-12` a `RN-INV-16` de researchs |
| `RN-PRF-05` | administration | Trasladados los perfiles académicos a `researchs`, que los define en `RN-INV` | `RN-INV-12` a `RN-INV-16` de researchs |

## Lo que no entra en esta tabla

**Lo trasladado a otro módulo no está retirado.** `UF-RES-18` sigue definido en reservations con la marca *(trasladado)* y apunta a `UF-REP-02` de reports, que es donde vive ahora. Un flujo trasladado conserva su encabezado precisamente para que las referencias antiguas lleguen a alguna parte.

**Lo que nunca llegó a definirse tampoco entra.** Esta tabla registra identificadores que existieron, no numeraciones saltadas.

**Las tablas de base de datos retiradas no son identificadores.** `motivos_solicitud`, `control_cambios`, `mobiliarios` y las demás que el ajuste de septiembre retiró están documentadas en [`database-status.md`](../../modules/reservations/database-status.md).

## Cómo retirar un identificador

1. Borrar su definición del documento donde vivía.
2. Dejar en ese mismo punto una línea que explique por qué y a qué regla mirar.
3. Añadir la fila aquí.
4. Ejecutar `python tools/validar.py` y comprobar que no aparecen citas colgadas: si alguna sigue apuntando al identificador retirado sin explicación, hay que corregirla.
