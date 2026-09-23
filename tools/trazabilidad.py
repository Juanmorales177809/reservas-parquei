"""Genera specs/docs/trazabilidad.md: el camino de cada regla hacia el codigo.

    python tools/trazabilidad.py

Responde a una sola pregunta, para cada una de las reglas y controles
definidos: existe un contrato que la exponga, una tarea que la construya y
una prueba que la verifique?

Distingue dos fuerzas de evidencia, porque no son lo mismo:

  por identificador  el documento nombra `RN-REC-04`. Evidencia directa.
  por familia        el documento nombra `RN-REC`, sin decir cual. Es lo que
                     hacen casi todas las tareas, y solo indica intencion.

La distincion importa porque once familias se repiten entre modulos con
significados distintos: una tarea que cita `RN-IMP` podria referirse a la de
administration o a la de resources.
"""

import sys
from collections import defaultdict

import spec_index as ix

SALIDA = ix.RAIZ / "specs" / "docs" / "trazabilidad.md"


def recolectar():
    ids_c, fam_c = ix.reglas_en_contratos()

    ids_t, fam_t = set(), set()
    for t in ix.tareas().values():
        ids_t |= t["reglas"]
        fam_t |= t["familias"]

    ids_p, fam_p = set(), set()
    for p in ix.pruebas().values():
        ids_p |= p["reglas"]
        fam_p |= p["familias"]

    return {
        "contrato": (ids_c, fam_c),
        "tarea": (ids_t, fam_t),
        "prueba": (ids_p, fam_p),
    }


def celda(reglas_familia, ids, familias):
    """Como se ve una familia en una columna: n/m, 'familia' o guion."""
    exactas = sum(1 for r in reglas_familia if r["id"] in ids)
    if exactas:
        return f"{exactas}/{len(reglas_familia)}"
    if reglas_familia[0]["familia"] in familias:
        return "familia"
    return "—"


def generar():
    reglas = ix.reglas()
    fuentes = recolectar()
    repetidas = ix.familias_repetidas()

    por_modulo = defaultdict(list)
    for r in reglas:
        por_modulo[r["modulo"]].append(r)

    def cubre(r, clave):
        # Las pruebas solo cuentan por identificador exacto; los contratos y
        # las tareas citan familias de forma legitima.
        if clave == "prueba":
            return ix.cubierta_exacta(r["id"], fuentes["prueba"][0])
        return ix.cubierta(r["id"], *fuentes[clave])

    L = []
    L.append("# Trazabilidad")
    L.append("")
    L.append("> **Generado.** Lo produce `python tools/trazabilidad.py` leyendo la especificación.")
    L.append("> No se edita a mano: cualquier cambio se pierde en la siguiente ejecución.")
    L.append("")
    L.append("Responde una sola pregunta, para cada regla y control definido: **¿hay un contrato "
             "que lo exponga, una tarea que lo construya y una prueba que lo verifique?**")
    L.append("")
    L.append("Distingue dos fuerzas de evidencia, porque no son lo mismo:")
    L.append("")
    L.append("| Se lee | Significa |")
    L.append("|---|---|")
    L.append("| `4/6` | Cuatro de las seis reglas de la familia se citan **por su identificador**. "
             "Evidencia directa |")
    L.append("| `familia` | Ninguna se cita por su identificador, pero el documento nombra la "
             "familia. Solo indica intención |")
    L.append("| `—` | No aparece |")
    L.append("")
    L.append("**La cita por familia es evidencia débil.** Once familias se repiten entre módulos "
             "con significados distintos, así que una tarea que cita `RN-IMP` podría referirse a "
             "la de administration o a la de resources. Están listadas al final.")
    L.append("")
    L.append("---")
    L.append("")

    total = len(reglas)
    L.append("## Resumen")
    L.append("")
    L.append("| Módulo | Reglas | En contrato | En tarea | En prueba | Sin ningún camino |")
    L.append("|---|---:|---:|---:|---:|---:|")
    for modulo in sorted(por_modulo):
        rs = por_modulo[modulo]
        sin = sum(1 for r in rs if not any(cubre(r, k) for k in fuentes))
        L.append(f"| {modulo} | {len(rs)} | {sum(cubre(r, 'contrato') for r in rs)} | "
                 f"{sum(cubre(r, 'tarea') for r in rs)} | {sum(cubre(r, 'prueba') for r in rs)} | "
                 f"{sin or '—'} |")
    sin_total = sum(1 for r in reglas if not any(cubre(r, k) for k in fuentes))
    L.append(f"| **total** | **{total}** | **{sum(cubre(r, 'contrato') for r in reglas)}** | "
             f"**{sum(cubre(r, 'tarea') for r in reglas)}** | "
             f"**{sum(cubre(r, 'prueba') for r in reglas)}** | **{sin_total or '—'}** |")
    L.append("")
    L.append("---")
    L.append("")

    L.append("## Detalle por familia")
    L.append("")
    for modulo in sorted(por_modulo):
        familias = defaultdict(list)
        for r in por_modulo[modulo]:
            familias[r["familia"]].append(r)
        L.append(f"### {modulo}")
        L.append("")
        L.append("| Familia | Reglas | Contrato | Tarea | Prueba |")
        L.append("|---|---:|---|---|---|")
        for f in sorted(familias):
            rs = familias[f]
            marca = " ⚠" if f in repetidas else ""
            # En la columna de pruebas no se admite "familia": o hay identificador o no hay.
            L.append(f"| `{f}`{marca} | {len(rs)} | {celda(rs, *fuentes['contrato'])} | "
                     f"{celda(rs, *fuentes['tarea'])} | {celda(rs, fuentes['prueba'][0], set())} |")
        L.append("")

    L.append("---")
    L.append("")
    sin_camino = [r for r in reglas if not any(cubre(r, k) for k in fuentes)]
    L.append("## Reglas sin ningún camino")
    L.append("")
    if sin_camino:
        L.append(f"{len(sin_camino)} reglas no aparecen en ningún contrato, ni en ninguna tarea, "
                 "ni en ninguna prueba. **No significa que sobren**: significa que nada indica "
                 "dónde se implementan ni cómo se comprobará que lo están.")
        L.append("")
        L.append("| Regla | Módulo | Definida en |")
        L.append("|---|---|---|")
        for r in sorted(sin_camino, key=lambda x: (x["modulo"], x["id"])):
            # El documento vive en specs/docs/, asi que specs/X se alcanza con ../X
            relativa = "../" + r["archivo"].split("/", 1)[1]
            L.append(f"| `{r['id']}` | {r['modulo']} | "
                     f"[{r['archivo']}:{r['linea']}]({relativa}#L{r['linea']}) |")
    else:
        L.append("Ninguna. Toda regla aparece al menos en un contrato, una tarea o una prueba.")
    L.append("")
    L.append("---")
    L.append("")

    L.append("## Familias repetidas entre módulos")
    L.append("")
    L.append("Mismo nombre de familia, significados distintos. **Toda cita a una de estas desde "
             "fuera de su módulo tiene que nombrar el módulo**, o no se sabe a cuál se refiere.")
    L.append("")
    L.append("| Familia | Módulos que la definen |")
    L.append("|---|---|")
    for f in sorted(repetidas):
        L.append(f"| `{f}` | {', '.join(sorted(repetidas[f]))} |")
    L.append("")

    return "\n".join(L) + "\n"


def main():
    SALIDA.write_text(generar(), encoding="utf-8")
    reglas = ix.reglas()
    fuentes = recolectar()
    sin = sum(1 for r in reglas
              if not any(ix.cubierta(r["id"], *fuentes[k]) for k in fuentes))
    print(f"{SALIDA.relative_to(ix.RAIZ).as_posix()} generado")
    print(f"  {len(reglas)} reglas y controles")
    print(f"  {sin} sin ningun camino hacia el codigo")
    return 0


if __name__ == "__main__":
    sys.exit(main())
