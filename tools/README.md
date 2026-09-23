# tools

Dos scripts que comprueban que la especificación sea coherente consigo misma. Sin dependencias: solo Python 3 y `git`.

```bash
python tools/validar.py       # comprueba; devuelve 1 si algo falla
python tools/trazabilidad.py  # genera specs/docs/trazabilidad.md
```

## Por qué existen

La especificación son ~60 documentos que se citan entre sí: reglas que referencian reglas de otro módulo, contratos que citan reglas, tareas que citan contratos. **Nada de eso lo comprueba un compilador.** Un identificador que se renombra deja referencias colgadas que nadie ve hasta que alguien implementa la regla equivocada.

Estos scripts son el paso de análisis del ciclo. Se ejecutan antes de dar por cerrado un cambio en `specs/`.

## Qué comprueba `validar.py`

| # | Comprobación | Falla |
|---|---|---|
| 1 | Ningún enlace de markdown apunta a un archivo inexistente | Sí |
| 2 | Ninguna cita a una regla, control, flujo, pregunta o ADR queda colgada | Sí |
| 3 | Toda tarea aparece en el plan general, con fase y carril | Sí |
| 4 | Toda regla tiene camino hacia el código | Solo avisa |

La 4 avisa en vez de fallar porque una regla sin prueba es trabajo pendiente, no una incoherencia del documento.

Solo mira archivos **versionados**: se los pide a `git ls-files`. Un borrador local sin versionar no debe hacer fallar la validación del repositorio.

## Qué genera `trazabilidad.py`

[`specs/docs/trazabilidad.md`](../specs/docs/trazabilidad.md), que responde para cada regla si hay un contrato que la exponga, una tarea que la construya y una prueba que la verifique.

Distingue dos fuerzas de evidencia. Un contrato o una tarea pueden citar una **familia** —`RN-REC`— porque describen de qué tratan sin enumerar cada regla. Una **prueba no**: tiene que citar `RN-REC-04`, porque si no, no dice cuál verificó. Por eso la columna de pruebas solo cuenta identificadores exactos.

## Los tres archivos

| Archivo | Qué hace |
|---|---|
| `spec_index.py` | Lee la especificación y devuelve índices. No decide nada ni imprime |
| `validar.py` | Las cuatro comprobaciones |
| `trazabilidad.py` | La matriz |

`spec_index.py` devuelve las reglas como **lista, no como diccionario por identificador**. Los identificadores son únicos dentro de su módulo, no en todo el sistema: once familias se repiten entre módulos con significados distintos, así que indexar por identificador perdería silenciosamente las repetidas. Es el error que cometió la primera versión de este script, que contaba 513 reglas donde hay 567.

## Si añades un documento

Los scripts reconocen los formatos tal como los escriben los documentos actuales:

```text
regla    - **RN-REC-04:** texto        en modules/<m>/business-rules.md
control  - **SEC-SES-01:** texto       en modules/<m>/security.md
flujo    ## UF-REC-01 — Título         en modules/<m>/user-flow*.md
tarea    ### DB-14 — Título            en los planes de tareas
prueba   ### T-REC-01 — Título         en modules/<m>/tests.md
         - **Cubre:** `RN-REC-04`, ...
```

Si escribes una regla con otro formato, no se contará. Conviene ejecutar `validar.py` después de añadir documentos y comprobar que los totales suben como esperas.
