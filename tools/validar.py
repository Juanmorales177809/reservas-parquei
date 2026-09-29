"""Comprueba que la especificacion sea internamente coherente.

    python tools/validar.py

Devuelve 0 si todo pasa y 1 si algo falla. Lo que comprueba:

  1. Ningun enlace de markdown apunta a un archivo que no existe.
  2. Ninguna cita a una regla, control, flujo, pregunta o ADR queda colgada.
  3. Toda tarea definida aparece en el plan general, con fase y carril.
  4. Toda regla tiene camino hacia el codigo: contrato, tarea o prueba.

La 4 avisa pero no falla, porque una regla sin prueba es trabajo pendiente,
no un error del documento. Las tres primeras si fallan: son incoherencias.
"""

import re
import sys
import urllib.parse

import spec_index as ix

ERRORES = 0
AVISOS = 0


def fallo(mensaje):
    global ERRORES
    ERRORES += 1
    print(f"  FALLA  {mensaje}")


def aviso(mensaje):
    global AVISOS
    AVISOS += 1
    print(f"  aviso  {mensaje}")


def titulo(texto):
    print(f"\n{texto}")


def enlaces():
    titulo("1. Enlaces")
    revisados = 0
    for doc in ix.documentos():
        for _, enlace in re.findall(r"\[([^\]]*)\]\(([^)]+)\)", ix.leer(doc)):
            if enlace.startswith(("http://", "https://", "mailto:")):
                continue
            ruta = enlace.partition("#")[0]
            if not ruta:
                continue
            revisados += 1
            destino = doc.parent / urllib.parse.unquote(ruta)
            if not destino.exists():
                fallo(f"{doc.relative_to(ix.RAIZ).as_posix()} -> {enlace}")
    print(f"  {revisados} enlaces relativos revisados")


def referencias():
    titulo("2. Referencias a identificadores")
    definidos = ix.ids_de_regla() | set(ix.flujos()) | set(ix.pruebas())

    # Las preguntas abiertas y los ADR se definen fuera de modules/.
    oq = ix.RAIZ / "specs" / "docs" / "decisions" / "open-questions.md"
    if oq.exists():
        definidos |= set(re.findall(r"\bOQ-\d{2}\b", ix.leer(oq)))
    for adr in (ix.RAIZ / "specs" / "docs" / "decisions").glob("adr-*.md"):
        definidos.add(adr.stem.split("-")[0].upper() + "-" + adr.stem.split("-")[1])

    # Lo retirado a proposito se cita legitimamente para explicar que ya no esta.
    retirados = ix.identificadores_retirados()
    definidos |= retirados

    patron = re.compile(
        r"\b(" + ix.ID_REGLA + r"|" + ix.ID_FLUJO + r"|" + ix.ID_PRUEBA + r"|OQ-\d{2}|ADR-\d{3})\b"
    )
    colgadas = {}
    for doc in ix.documentos():
        for ident in patron.findall(ix.leer(doc)):
            if ident not in definidos:
                colgadas.setdefault(ident, set()).add(doc.relative_to(ix.RAIZ).as_posix())
    for ident in sorted(colgadas):
        fallo(f"{ident} se cita pero no esta definido: {', '.join(sorted(colgadas[ident]))}")
    print(f"  {len(definidos) - len(retirados)} definidos, {len(retirados)} retirados a proposito")


def cobertura_de_tareas():
    titulo("3. Tareas en el plan general")
    tareas = ix.tareas()
    # La convencion de cada plan incluye un ejemplo con XX; no es una tarea.
    reales = {k: v for k, v in tareas.items() if not k.endswith("XX")}

    general = ix.leer(ix.PLANES["general"]).replace("`", "").replace("~", "")

    def expandir(texto):
        vistos = set(re.findall(r"\b(?:DB|API|BK|FE)-\d{2}\b", texto))
        for pre, a, b in re.findall(r"\b(DB|API|BK|FE)-(\d{2})\s+a\s+(?:DB|API|BK|FE)-(\d{2})\b", texto):
            for n in range(int(a), int(b) + 1):
                vistos.add(f"{pre}-{n:02d}")
        return vistos

    # Las tareas del plan de auth viven dentro de BK-09; no se listan una a una.
    esperadas = [k for k, v in reales.items() if v["plan"] != "auth"]
    # API-01..API-05 son BK-04..BK-07 y BK-09 vistas desde el otro plan.
    equivalentes = {"API-01", "API-02", "API-03", "API-04", "API-05"}

    mencionadas = expandir(general)
    for ident in esperadas:
        if ident not in mencionadas and ident not in equivalentes:
            fallo(f"{ident} no se menciona en tasks.md")

    if "## Reparto para dos personas" in general:
        carriles = expandir(general.split("## Reparto para dos personas")[1])
        for ident in esperadas:
            if ident not in carriles and ident not in equivalentes:
                fallo(f"{ident} no esta asignada a ningun carril")

    if "## Fase 0" in general and "## Los dos riesgos" in general:
        fases = expandir(general.split("## Fase 0")[1].split("## Los dos riesgos")[0])
        for ident in esperadas:
            if ident not in fases and ident not in equivalentes:
                fallo(f"{ident} no esta ubicada en ninguna fase")

    print(f"  {len(reales)} tareas definidas en {len(ix.PLANES)} planes")


def camino_a_codigo():
    titulo("4. Reglas con camino hacia el codigo")
    reglas = ix.reglas()
    ids_c, fam_c = ix.reglas_en_contratos()

    ids_t, fam_t = set(), set()
    for t in ix.tareas().values():
        ids_t |= t["reglas"]
        fam_t |= t["familias"]

    ids_p, fam_p = set(), set()
    for p in ix.pruebas().values():
        ids_p |= p["reglas"]
        fam_p |= p["familias"]

    # Las pruebas se cuentan solo por identificador exacto: es lo que exige
    # testing.md, y contar por familia inflaria la cobertura.
    sin_nada = [
        r for r in reglas
        if not ix.cubierta(r["id"], ids_c, fam_c)
        and not ix.cubierta(r["id"], ids_t, fam_t)
        and not ix.cubierta_exacta(r["id"], ids_p)
    ]
    sin_prueba = [r for r in reglas if not ix.cubierta_exacta(r["id"], ids_p)]

    total = len(reglas)
    repetidas = ix.familias_repetidas()
    print(f"  {total} reglas y controles definidos en los nueve modulos")
    print(f"  {len(repetidas)} familias se repiten entre modulos con distinto significado")
    print(f"  en contrato: {sum(ix.cubierta(r['id'], ids_c, fam_c) for r in reglas)}")
    print(f"  en tarea:    {sum(ix.cubierta(r['id'], ids_t, fam_t) for r in reglas)}")
    print(f"  en prueba:   {total - len(sin_prueba)}  (solo por identificador exacto)")

    if sin_nada:
        aviso(f"{len(sin_nada)} reglas sin contrato, ni tarea, ni prueba")
        por_modulo = {}
        for r in sin_nada:
            por_modulo.setdefault(r["modulo"], []).append(r["id"])
        for modulo in sorted(por_modulo):
            print(f"           {modulo}: {len(por_modulo[modulo])}")
    if sin_prueba:
        aviso(f"{len(sin_prueba)} reglas sin prueba declarada")
    print("  el detalle esta en specs/docs/trazabilidad.md")


def main():
    print("Validacion de la especificacion")
    enlaces()
    referencias()
    cobertura_de_tareas()
    camino_a_codigo()
    print(f"\n{ERRORES} fallas, {AVISOS} avisos")
    return 1 if ERRORES else 0


if __name__ == "__main__":
    sys.exit(main())
