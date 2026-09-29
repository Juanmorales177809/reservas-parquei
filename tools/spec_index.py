"""Lee la especificacion y devuelve un indice de reglas, flujos, contratos, tareas y pruebas.

Lo usan validar.py y trazabilidad.py. No imprime nada ni decide nada: solo lee.

Formatos que reconoce, tal como los escriben los documentos:

    regla      - **RN-REC-04:** texto          en modules/<m>/business-rules.md
    control    - **SEC-SES-01:** texto         en modules/<m>/security.md
    flujo      ## UF-REC-01 - Titulo           en modules/<m>/user-flow*.md
    tarea      ### DB-14 - Titulo              en los planes de tareas
    prueba     ### T-REC-01 - Titulo           en modules/<m>/tests.md
               - **Cubre:** `RN-REC-04`, ...
"""

import re
import subprocess
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
MODULOS = RAIZ / "specs" / "modules"
CONTRATOS = RAIZ / "specs" / "contratos"

PLANES = {
    "general": RAIZ / "tasks.md",
    "tecnico": RAIZ / "plan.md",
    "base-de-datos": RAIZ / "specs" / "docs" / "tasks" / "base-de-datos.md",
    "contratos": RAIZ / "specs" / "docs" / "tasks" / "contratos.md",
    "backend": RAIZ / "specs" / "docs" / "tasks" / "backend.md",
    "auth": MODULOS / "auth" / "tasks.md",
    "frontend": RAIZ / "specs" / "docs" / "tasks" / "frontend.md",
}

# Un identificador de regla o control: RN-TIP-PE-25, RN-REC-04, SEC-SES-01.
ID_REGLA = r"(?:RN|SEC)-[A-Z]+(?:-[A-Z]+)?-\d{2}"
ID_FLUJO = r"UF-[A-Z]+-\d{2}"
ID_TAREA = r"(?:DB|API|BK|AUTH|FE)-[A-Z]?\d{1,2}"
ID_PRUEBA = r"T-[A-Z]+-\d{2}"


def leer(ruta):
    return ruta.read_text(encoding="utf-8")


def documentos():
    """Los .md *versionados*.

    Se piden a git en vez de recorrer el disco porque un borrador local sin
    versionar no debe hacer fallar la validacion del repositorio. Si git no
    esta disponible, se recorre el disco y se avisa de la diferencia.
    """
    try:
        salida = subprocess.run(
            ["git", "ls-files", "-z", "*.md"],
            cwd=RAIZ, capture_output=True, text=True, check=True,
        ).stdout
        rutas = [RAIZ / p for p in salida.split("\0") if p]
        if rutas:
            return [p for p in rutas if p.exists()]
    except (OSError, subprocess.CalledProcessError):
        pass
    return [p for p in RAIZ.rglob("*.md") if ".git" not in p.parts]


def familia(id_regla):
    """RN-TIP-PE-25 -> RN-TIP-PE. Quita solo el numero final."""
    return id_regla.rsplit("-", 1)[0]


def reglas():
    """Las reglas *definidas*, no las citadas.

    Devuelve una lista, no un diccionario por identificador: los
    identificadores son unicos dentro de su modulo, no en todo el sistema.
    Once familias se repiten entre modulos con significados distintos, asi
    que indexar por id solo perderia silenciosamente las repetidas.
    """
    encontradas = []
    for carpeta in sorted(MODULOS.iterdir()):
        if not carpeta.is_dir():
            continue
        for archivo in ("business-rules.md", "security.md"):
            ruta = carpeta / archivo
            if not ruta.exists():
                continue
            for n, linea in enumerate(leer(ruta).splitlines(), 1):
                m = re.match(r"- \*\*(" + ID_REGLA + r"):\*\*", linea)
                if m:
                    encontradas.append({
                        "id": m.group(1),
                        "modulo": carpeta.name,
                        "familia": familia(m.group(1)),
                        "tipo": m.group(1)[:3].rstrip("-"),
                        "archivo": ruta.relative_to(RAIZ).as_posix(),
                        "linea": n,
                    })
    return encontradas


def ids_de_regla():
    """Solo los identificadores definidos, para comprobar citas colgadas."""
    return {r["id"] for r in reglas()}


def familias_repetidas():
    """Familias definidas en mas de un modulo, con significados distintos."""
    por_familia = {}
    for r in reglas():
        por_familia.setdefault(r["familia"], set()).add(r["modulo"])
    return {f: m for f, m in por_familia.items() if len(m) > 1}


def flujos():
    """Los flujos definidos por su encabezado. id -> datos."""
    encontrados = {}
    for carpeta in sorted(MODULOS.iterdir()):
        if not carpeta.is_dir():
            continue
        for ruta in sorted(carpeta.glob("user-flow*.md")):
            for n, linea in enumerate(leer(ruta).splitlines(), 1):
                m = re.match(r"#{2,3} (" + ID_FLUJO + r")\b", linea)
                if m:
                    encontrados[m.group(1)] = {
                        "modulo": carpeta.name,
                        "archivo": ruta.relative_to(RAIZ).as_posix(),
                        "linea": n,
                    }
    return encontrados


def tareas():
    """Las tareas definidas en los planes. id -> datos, con las reglas que cita."""
    encontradas = {}
    for nombre, ruta in PLANES.items():
        if not ruta.exists():
            continue
        texto = leer(ruta)
        # Cada tarea va desde su encabezado hasta el siguiente encabezado.
        partes = re.split(r"^(#{3,4} (" + ID_TAREA + r")\b.*)$", texto, flags=re.M)
        for i in range(1, len(partes) - 2, 3):
            cabecera, ident, cuerpo = partes[i], partes[i + 1], partes[i + 2]
            if ident in encontradas:  # la convencion de ejemplo usa DB-XX, no colisiona
                continue
            encontradas[ident] = {
                "plan": nombre,
                "titulo": cabecera.lstrip("# ").strip(),
                "archivo": ruta.relative_to(RAIZ).as_posix(),
                "reglas": set(re.findall(ID_REGLA, cuerpo)),
                "familias": set(re.findall(r"\b((?:RN|SEC)-[A-Z]+(?:-[A-Z]+)?)\b", cuerpo)),
            }
    return encontradas


def pruebas():
    """Las pruebas definidas por modulo, con las reglas que declaran cubrir."""
    encontradas = {}
    for carpeta in sorted(MODULOS.iterdir()):
        ruta = carpeta / "tests.md"
        if not ruta.exists():
            continue
        texto = leer(ruta)
        partes = re.split(r"^(#{3,4} (" + ID_PRUEBA + r")\b.*)$", texto, flags=re.M)
        for i in range(1, len(partes) - 2, 3):
            cabecera, ident, cuerpo = partes[i], partes[i + 1], partes[i + 2]
            encontradas[ident] = {
                "modulo": carpeta.name,
                "titulo": cabecera.lstrip("# ").strip(),
                "archivo": ruta.relative_to(RAIZ).as_posix(),
                "reglas": set(re.findall(ID_REGLA, cuerpo)),
                "familias": set(re.findall(r"\b((?:RN|SEC)-[A-Z]+(?:-[A-Z]+)?)\b", cuerpo)),
            }
    return encontradas


def identificadores_retirados():
    """Los que existieron y dejaron de estar definidos, con su numero sin reasignar.

    Se leen de la tabla del registro en vez de deducirse de la prosa: retirar
    un identificador es una decision, y una decision se anota.
    """
    ruta = RAIZ / "specs" / "docs" / "decisions" / "identificadores-retirados.md"
    if not ruta.exists():
        return set()
    patron = r"^\| *`(" + ID_REGLA + r"|" + ID_FLUJO + r")` *\|"
    return set(re.findall(patron, leer(ruta), flags=re.M))


def texto_contratos():
    """Todo el texto de los nueve contratos, por modulo."""
    return {
        c.parent.name: leer(c)
        for c in sorted(CONTRATOS.glob("*/api-contract.md"))
    }


def reglas_en_contratos():
    """Identificadores y familias de regla citados por algun contrato."""
    ids, fams = set(), set()
    for texto in texto_contratos().values():
        ids |= set(re.findall(ID_REGLA, texto))
        fams |= set(re.findall(r"\b((?:RN|SEC)-[A-Z]+(?:-[A-Z]+)?)\b", texto))
    return ids, fams


def cubierta(id_regla, ids, familias):
    """Cubierta por identificador o por familia.

    Vale para contratos y tareas, que citan familias legitimamente: una tarea
    dice de que trata, no enumera cada regla.
    """
    return id_regla in ids or familia(id_regla) in familias


def cubierta_exacta(id_regla, ids, familias=None):
    """Cubierta solo por su identificador completo.

    Es lo que se exige a las pruebas: citar `RN-DIS-05`, no `RN-DIS`. Una
    prueba que nombra la familia no dice cual de las reglas verifica, y
    contarla como cobertura de todas convierte la matriz en optimismo.
    """
    return id_regla in ids
