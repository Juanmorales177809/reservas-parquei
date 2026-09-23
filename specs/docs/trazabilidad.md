# Trazabilidad

> **Generado.** Lo produce `python tools/trazabilidad.py` leyendo la especificación.
> No se edita a mano: cualquier cambio se pierde en la siguiente ejecución.

Responde una sola pregunta, para cada regla y control definido: **¿hay un contrato que lo exponga, una tarea que lo construya y una prueba que lo verifique?**

Distingue dos fuerzas de evidencia, porque no son lo mismo:

| Se lee | Significa |
|---|---|
| `4/6` | Cuatro de las seis reglas de la familia se citan **por su identificador**. Evidencia directa |
| `familia` | Ninguna se cita por su identificador, pero el documento nombra la familia. Solo indica intención |
| `—` | No aparece |

**La cita por familia es evidencia débil.** Once familias se repiten entre módulos con significados distintos, así que una tarea que cita `RN-IMP` podría referirse a la de administration o a la de resources. Están listadas al final.

---

## Resumen

| Módulo | Reglas | En contrato | En tarea | En prueba | Sin ningún camino |
|---|---:|---:|---:|---:|---:|
| administration | 62 | 62 | 57 | 23 | — |
| auth | 89 | 85 | 89 | 39 | — |
| espacios | 22 | 22 | 15 | 11 | — |
| notifications | 60 | 49 | 50 | 12 | — |
| reports | 58 | 58 | 23 | 17 | — |
| researchs | 20 | 20 | 20 | 10 | — |
| reservations | 180 | 168 | 124 | 29 | — |
| resources | 57 | 33 | 44 | 23 | — |
| usuarios | 19 | 19 | 19 | 10 | — |
| **total** | **567** | **516** | **441** | **174** | **—** |

---

## Detalle por familia

### administration

| Familia | Reglas | Contrato | Tarea | Prueba |
|---|---:|---|---|---|
| `RN-ADM` | 5 | 1/5 | — | — |
| `RN-AUD` | 7 | 6/7 | 2/7 | 5/7 |
| `RN-CUE` | 6 | 1/6 | 1/6 | — |
| `RN-HAB` | 5 | 3/5 | 1/5 | — |
| `RN-IMP` ⚠ | 12 | 10/12 | 5/12 | 7/12 |
| `RN-INT` ⚠ | 4 | 1/4 | 1/4 | 1/4 |
| `RN-PER` | 9 | 8/9 | 4/9 | 7/9 |
| `RN-UNI` | 7 | 7/7 | 2/7 | 2/7 |
| `RN-USR` ⚠ | 7 | 5/7 | 1/7 | 1/7 |

### auth

| Familia | Reglas | Contrato | Tarea | Prueba |
|---|---:|---|---|---|
| `RN-AUTH-ID` | 12 | 5/12 | 4/12 | 3/12 |
| `RN-AUTH-ROL` | 9 | 7/9 | 4/9 | 3/9 |
| `RN-AUTH-SES` | 5 | 3/5 | 2/5 | — |
| `SEC-ABU` | 3 | 3/3 | 3/3 | 3/3 |
| `SEC-AUD` | 4 | 3/4 | 2/4 | — |
| `SEC-AUTZ` | 6 | 5/6 | 4/6 | 4/6 |
| `SEC-CSRF` | 3 | 2/3 | 2/3 | 2/3 |
| `SEC-INF` | 4 | — | 1/4 | — |
| `SEC-INV` | 4 | 3/4 | 4/4 | 4/4 |
| `SEC-JWT` | 5 | 4/5 | 4/5 | 4/5 |
| `SEC-PWD` | 7 | 1/7 | 1/7 | 3/7 |
| `SEC-REAUTH` | 4 | 4/4 | 2/4 | 3/4 |
| `SEC-REC` | 5 | 5/5 | 2/5 | 2/5 |
| `SEC-SES` | 13 | 9/13 | 6/13 | 6/13 |
| `SEC-TOK` | 5 | 4/5 | 2/5 | 2/5 |

### espacios

| Familia | Reglas | Contrato | Tarea | Prueba |
|---|---:|---|---|---|
| `RN-ESP` | 3 | 2/3 | — | — |
| `RN-ESP-CAM` | 5 | 3/5 | 2/5 | 4/5 |
| `RN-ESP-DIS` | 3 | 1/3 | 1/3 | 1/3 |
| `RN-ESP-HAB` | 4 | 2/4 | — | 4/4 |
| `RN-ESP-REC` | 7 | 5/7 | 1/7 | 2/7 |

### notifications

| Familia | Reglas | Contrato | Tarea | Prueba |
|---|---:|---|---|---|
| `RN-CAL` ⚠ | 3 | 2/3 | familia | — |
| `RN-CNT` | 6 | 1/6 | — | — |
| `RN-CON` ⚠ | 4 | 4/4 | 1/4 | 1/4 |
| `RN-COR` | 7 | 1/7 | 2/7 | 2/7 |
| `RN-DES` ⚠ | 6 | 1/6 | 1/6 | 1/6 |
| `RN-EST` ⚠ | 5 | 3/5 | 1/5 | 2/5 |
| `RN-EVT` | 11 | — | 2/11 | 2/11 |
| `RN-HIS` ⚠ | 4 | 4/4 | — | — |
| `RN-INT` ⚠ | 4 | 1/4 | 1/4 | 1/4 |
| `RN-NOT` | 6 | 1/6 | 1/6 | 1/6 |
| `RN-PREF` | 4 | 4/4 | 2/4 | 2/4 |

### reports

| Familia | Reglas | Contrato | Tarea | Prueba |
|---|---:|---|---|---|
| `RN-AMB` | 5 | 5/5 | — | 2/5 |
| `RN-CON` ⚠ | 4 | 4/4 | 1/4 | 1/4 |
| `RN-CTX` ⚠ | 4 | 2/4 | familia | 1/4 |
| `RN-DIM` | 7 | 3/7 | — | — |
| `RN-EST` ⚠ | 4 | 3/4 | 1/4 | 2/4 |
| `RN-EXP` | 5 | 4/5 | familia | 2/5 |
| `RN-FIL` | 5 | 4/5 | — | 1/5 |
| `RN-HIS` ⚠ | 4 | 4/4 | — | — |
| `RN-OCU` | 6 | 4/6 | 3/6 | 3/6 |
| `RN-PRI` | 4 | 3/4 | — | 1/4 |
| `RN-REP` ⚠ | 6 | 4/6 | — | 4/6 |
| `RN-VIS` | 4 | 2/4 | — | — |

### researchs

| Familia | Reglas | Contrato | Tarea | Prueba |
|---|---:|---|---|---|
| `RN-ACT` | 4 | 4/4 | familia | 3/4 |
| `RN-INV` | 16 | 8/16 | 3/16 | 7/16 |

### reservations

| Familia | Reglas | Contrato | Tarea | Prueba |
|---|---:|---|---|---|
| `RN-ACO` | 7 | — | — | 7/7 |
| `RN-APR` | 9 | 2/9 | familia | — |
| `RN-CAL` ⚠ | 5 | 2/5 | familia | — |
| `RN-CAN` | 8 | 4/8 | — | 1/8 |
| `RN-CTX` ⚠ | 9 | 3/9 | familia | 1/9 |
| `RN-DIS` | 11 | 2/11 | 2/11 | 5/11 |
| `RN-EST` ⚠ | 5 | 3/5 | 1/5 | 2/5 |
| `RN-HOR` | 7 | 1/7 | — | — |
| `RN-PRO` | 5 | — | — | 5/5 |
| `RN-PROP` | 7 | 5/7 | familia | — |
| `RN-REC` ⚠ | 3 | 1/3 | familia | 1/3 |
| `RN-REP` ⚠ | 3 | 2/3 | — | 1/3 |
| `RN-RES` | 15 | 3/15 | familia | — |
| `RN-SAL` | 4 | familia | — | 1/4 |
| `RN-TIP` | 6 | 4/6 | 1/6 | — |
| `RN-TIP-PE` | 27 | 6/27 | 3/27 | 3/27 |
| `RN-TIP-PLE` | 8 | 3/8 | — | — |
| `RN-TIP-RC` | 14 | 1/14 | 2/14 | 1/14 |
| `RN-TIP-RE` | 14 | 1/14 | — | — |
| `RN-TIP-RI` | 13 | 1/13 | 1/13 | 1/13 |

### resources

| Familia | Reglas | Contrato | Tarea | Prueba |
|---|---:|---|---|---|
| `RN-DES` ⚠ | 7 | 2/7 | 1/7 | 2/7 |
| `RN-EQP` | 11 | — | 1/11 | 1/11 |
| `RN-IMP` ⚠ | 7 | 5/7 | 1/7 | 3/7 |
| `RN-LAB` | 8 | 2/8 | 1/8 | 3/8 |
| `RN-MOB` | 5 | — | — | 5/5 |
| `RN-OTR` | 5 | — | — | 5/5 |
| `RN-REC` ⚠ | 11 | 2/11 | familia | 1/11 |
| `RN-ROL` | 3 | — | — | 3/3 |

### usuarios

| Familia | Reglas | Contrato | Tarea | Prueba |
|---|---:|---|---|---|
| `RN-DAT` | 3 | 2/3 | familia | 2/3 |
| `RN-PRS` | 5 | 4/5 | 1/5 | 3/5 |
| `RN-USR` ⚠ | 11 | 8/11 | 2/11 | 5/11 |

---

## Reglas sin ningún camino

Ninguna. Toda regla aparece al menos en un contrato, una tarea o una prueba.

---

## Familias repetidas entre módulos

Mismo nombre de familia, significados distintos. **Toda cita a una de estas desde fuera de su módulo tiene que nombrar el módulo**, o no se sabe a cuál se refiere.

| Familia | Módulos que la definen |
|---|---|
| `RN-CAL` | notifications, reservations |
| `RN-CON` | notifications, reports |
| `RN-CTX` | reports, reservations |
| `RN-DES` | notifications, resources |
| `RN-EST` | notifications, reports, reservations |
| `RN-HIS` | notifications, reports |
| `RN-IMP` | administration, resources |
| `RN-INT` | administration, notifications |
| `RN-REC` | reservations, resources |
| `RN-REP` | reports, reservations |
| `RN-USR` | administration, usuarios |

