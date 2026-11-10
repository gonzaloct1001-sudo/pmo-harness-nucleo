#!/usr/bin/env python3
"""Integridad del núcleo: todo contra todo, antes de publicar una versión. Lo corre el mantenedor (y la batería).

Uso:
    python herramientas/integridad.py [--nombres-viejos a,b,c]

Revisa:
1. Rutas citadas en la documentación (`.claude/skills/...`, `herramientas/...py`, `reglas/...md`, `arquetipos/...`,
   `plantilla-*`, `biblioteca/...`, `ejemplos/...`, `NUBE.md`, etc.) que no existen.
2. Cada SKILL.md: frontmatter con name igual a su carpeta, descripción de 60 palabras o menos, línea de reglas con
   archivos que existen; cada subagente con descripción de 45 palabras o menos y `model:`.
3. Índice de skills (`.claude/skills/LEEME.md`) y catálogo (`ayuda/catalogo.yaml`) contra las carpetas reales.
4. `NUCLEO.txt`: cada ruta existe. `.claude/settings.json`: JSON válido y cada hook apunta a un script que existe.
5. `herramientas/LEEME.md` nombra cada script de `herramientas/` (salvo los privados `_x.py`).
6. Nombres viejos de skills fuera de la tabla de alias, el CHANGELOG y MEJORAS.md.
7. Compila cada .py del núcleo.
Termina con código 1 si hay problemas.
"""
import argparse
import json
import py_compile
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DOCS_EXT = {".md", ".yaml"}
EXCLUIR_PARTES = {".git", "__pycache__", ".venv", "_procesado", "respaldo-nucleo", ".harness", "_crudo"}
PREFIJOS = ("\\.claude/", "herramientas/", "reglas/", "arquetipos/", "plantilla-proyecto/", "plantilla-subproyecto/",
            "plantilla-empresa/", "biblioteca/", "pruebas/", "ejemplos/", "\\.githooks/")
RUTA_RE = re.compile(r"`((?:" + "|".join(PREFIJOS) + r")[\w./<>\-\[\]*]+)`")
MAX_SKILL, MAX_AGENTE = 60, 45


def archivos(ext):
    for x in RAIZ.rglob("*"):
        if x.is_file() and x.suffix.lower() in ext and not (set(x.relative_to(RAIZ).parts) & EXCLUIR_PARTES):
            yield x


def frontmatter(texto):
    m = re.match(r"\A---\n(.*?)\n---\n", texto, re.S)
    return m.group(1) if m else ""


def campo(fm, nombre):
    m = re.search(rf"^{nombre}:\s*(.+)$", fm, re.M)
    return m.group(1).strip() if m else ""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--nombres-viejos", default="", help="nombres de skills retiradas, separados por coma")
    a = ap.parse_args()
    problemas = []

    # 1. rutas citadas
    for x in archivos(DOCS_EXT):
        rel = x.relative_to(RAIZ).as_posix()
        if rel in ("CHANGELOG.md", "MEJORAS.md"):
            continue
        for m in RUTA_RE.finditer(x.read_text(encoding="utf-8", errors="replace")):
            ruta = m.group(1).rstrip("/").rstrip(".")
            if any(c in ruta for c in "<>*[") or ruta.endswith(("/...", "...")):
                continue
            if not (RAIZ / ruta).exists():
                problemas.append(f"ruta citada que no existe · {rel}: `{ruta}`")

    # 2. skills y subagentes
    reales = set()
    for s in sorted((RAIZ / ".claude" / "skills").glob("*/SKILL.md")):
        reales.add(s.parent.name)
        t = s.read_text(encoding="utf-8", errors="replace")
        fm = frontmatter(t)
        if campo(fm, "name") != s.parent.name:
            problemas.append(f"skill {s.parent.name}: name del frontmatter «{campo(fm, 'name')}» distinto de la carpeta")
        n = len(campo(fm, "description").split())
        if n > MAX_SKILL:
            problemas.append(f"skill {s.parent.name}: descripción de {n} palabras (máximo {MAX_SKILL})")
        m = re.search(r"^> Reglas que aplican.*$", t, re.M)
        if not m:
            problemas.append(f"skill {s.parent.name}: sin línea «Reglas que aplican»")
        else:
            for r in re.findall(r"`(reglas/[\w-]+\.md)`", m.group(0)):
                if not (RAIZ / r).exists():
                    problemas.append(f"skill {s.parent.name}: regla citada que no existe {r}")
    for ag in sorted((RAIZ / ".claude" / "agents").glob("*.md")):
        fm = frontmatter(ag.read_text(encoding="utf-8", errors="replace"))
        n = len(campo(fm, "description").split())
        if n > MAX_AGENTE:
            problemas.append(f"subagente {ag.stem}: descripción de {n} palabras (máximo {MAX_AGENTE})")
        if not campo(fm, "model"):
            problemas.append(f"subagente {ag.stem}: sin `model:`")

    # 3. índice y catálogo
    idx = (RAIZ / ".claude" / "skills" / "LEEME.md").read_text(encoding="utf-8", errors="replace")
    en_idx = set(re.findall(r"^\| `([a-z-]+)` \| .* \| `\.claude/skills/[a-z-]+/SKILL\.md` \|$", idx, re.M))
    for s in sorted(reales - en_idx):
        problemas.append(f"índice de skills: falta la fila de {s}")
    for s in sorted(en_idx - reales):
        problemas.append(f"índice de skills: fila de {s} sin carpeta")
    cat = (RAIZ / ".claude" / "skills" / "ayuda" / "catalogo.yaml").read_text(encoding="utf-8", errors="replace")
    ids = re.findall(r"\{id: ([a-z-]+),", cat)
    for s in sorted(set(ids) - reales):
        problemas.append(f"catálogo: skill {s} sin carpeta")
    for s in sorted(reales - set(ids)):
        problemas.append(f"catálogo: falta la skill {s}")
    for s in sorted({i for i in ids if ids.count(i) > 1}):
        problemas.append(f"catálogo: skill {s} repetida")

    # 4. NUCLEO.txt y settings.json
    for linea in (RAIZ / "NUCLEO.txt").read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if linea and not linea.startswith("#") and not linea.startswith("http") and not (RAIZ / linea).exists():
            problemas.append(f"NUCLEO.txt: no existe {linea}")
    try:
        cfg = json.loads((RAIZ / ".claude" / "settings.json").read_text(encoding="utf-8"))
        for evento, entradas in (cfg.get("hooks") or {}).items():
            for e in entradas:
                for h in e.get("hooks", []):
                    for m in re.finditer(r"herramientas/[\w/]+\.(?:py|sh)", h.get("command", "")):
                        if not (RAIZ / m.group(0)).exists():
                            problemas.append(f"settings.json: hook {evento} apunta a {m.group(0)} que no existe")
    except (OSError, ValueError) as e:
        problemas.append(f"settings.json: {e}")

    # 5. herramientas/LEEME.md
    leeme = (RAIZ / "herramientas" / "LEEME.md").read_text(encoding="utf-8", errors="replace")
    for p in sorted((RAIZ / "herramientas").glob("*.py")):
        if not p.name.startswith("_") and p.name not in leeme:
            problemas.append(f"herramientas/LEEME.md: no nombra {p.name}")

    # 6. nombres viejos
    viejos = [v.strip() for v in a.nombres_viejos.split(",") if v.strip()]
    if viejos:
        for x in archivos({".md", ".py", ".yaml", ".txt"}):
            rel = x.relative_to(RAIZ).as_posix()
            if rel in ("CHANGELOG.md", "MEJORAS.md"):
                continue
            t = x.read_text(encoding="utf-8", errors="replace")
            if rel == ".claude/skills/LEEME.md":
                t = t.split("## Nombres anteriores")[0]
            for v in viejos:
                if re.search(r"(?<!references/)" + re.escape(v) + r"(?![\w-])", t):
                    problemas.append(f"nombre viejo «{v}» en {rel}")

    # 7. compila
    for p in archivos({".py"}):
        try:
            py_compile.compile(str(p), doraise=True)
        except py_compile.PyCompileError as e:
            problemas.append(f"no compila {p.relative_to(RAIZ).as_posix()}: {str(e)[:120]}")

    print(f"# Integridad del núcleo · {len(reales)} skills · {len(problemas)} problema(s)")
    for p in problemas:
        print("- " + p)
    if not problemas:
        print("Todo cuadra: rutas, skills, subagentes, índice, catálogo, NUCLEO.txt, hooks, herramientas y compilación.")
    return 1 if problemas else 0


if __name__ == "__main__":
    import _consola
    _consola.preparar()
    sys.exit(main())
