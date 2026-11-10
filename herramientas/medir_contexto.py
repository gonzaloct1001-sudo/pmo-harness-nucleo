#!/usr/bin/env python3
"""Cuánto contexto (tokens aproximados) consume cada pieza del harness.

Uso:
    python herramientas/medir_contexto.py [--techo] [--skill <nombre>] [--todo]

- Carga fija de cada sesión: AGENTS.md (vía CLAUDE.md o GEMINI.md), el archivo de entrada y la salida del estado de
  inicio. Es lo que paga cada conversación antes de empezar.
- Skills: cada SKILL.md (carga cuando se usa) y sus references (cargan solo en la fase que las usa).
- Subagentes: su instrucción (carga en el contexto propio del subagente, no en el principal).
La estimación es caracteres ÷ 4 (en español suele quedar algo por debajo del conteo real; sirve para comparar y
vigilar el crecimiento). Con --techo termina con código 1 si la carga fija supera el límite (TECHO_FIJO), que es lo
que la batería de pruebas controla para que el núcleo no engorde sin que se note.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
TECHO_FIJO = 2800       # tokens aprox. del texto fijo del núcleo (AGENTS.md como mapa + puerta de entrada); el detalle vive en reglas/
TECHO_SKILL = 5000      # aviso si una skill supera esto sin references


def tokens(ruta):
    try:
        return len(Path(ruta).read_text(encoding="utf-8", errors="replace")) // 4
    except OSError:
        return 0


def carga_fija():
    partes = [("AGENTS.md", tokens(RAIZ / "AGENTS.md")), ("CLAUDE.md (puerta de entrada)", tokens(RAIZ / "CLAUDE.md"))]
    try:
        r = subprocess.run([sys.executable, "herramientas/estado.py"], cwd=RAIZ, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=120)
        partes.append(("salida de estado.py (hook de inicio)", len(r.stdout) // 4))
    except (OSError, subprocess.TimeoutExpired):
        partes.append(("salida de estado.py (hook de inicio)", 0))
    return partes


def skills():
    salida = []
    for d in sorted((RAIZ / ".claude" / "skills").iterdir()):
        s = d / "SKILL.md"
        if not s.exists():
            continue
        refs = sum(tokens(r) for r in (d / "references").rglob("*") if r.is_file()) if (d / "references").exists() else 0
        salida.append((d.name, tokens(s), refs))
    return salida


def agentes():
    salida = []
    for a in sorted((RAIZ / ".claude" / "agents").glob("*.md")):
        fm = a.read_text(encoding="utf-8", errors="replace").split("---")
        m = re.search(r"^model:\s*(\S+)", fm[1] if len(fm) > 1 else "", re.M)
        salida.append((a.stem, tokens(a), m.group(1) if m else "(hereda)"))
    return salida


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--techo", action="store_true", help="código 1 si la carga fija supera el techo")
    ap.add_argument("--skill", help="detalle de una skill")
    ap.add_argument("--todo", action="store_true", help="listar todas las skills (por defecto, las 10 más pesadas)")
    a = ap.parse_args()

    fija = carga_fija()
    total = sum(t for _, t in fija)
    estatica = sum(t for n, t in fija if not n.startswith("salida de estado.py"))
    print("# Contexto del harness (tokens aproximados)\n")
    print("## Carga fija por sesión")
    for nombre, t in fija:
        print(f"- {nombre}: ~{t}")
    print(f"- **Total: ~{total}** · texto fijo del núcleo (sin el estado): ~{estatica} (techo {TECHO_FIJO}: "
          f"{'bajo el techo' if estatica <= TECHO_FIJO else 'SUPERADO'})")

    lista = skills()
    if a.skill:
        lista = [x for x in lista if x[0] == a.skill]
        if not lista:
            sys.exit(f"No existe la skill {a.skill}.")
    print("\n## Skills (cargan solo cuando se usan)")
    mostrar = sorted(lista, key=lambda x: -(x[1] + x[2]))
    if not a.todo and not a.skill:
        mostrar = mostrar[:10]
    for nombre, t, refs in mostrar:
        aviso = "  ← pesada: parte de su contenido podría ir a references/" if t > TECHO_SKILL else ""
        print(f"- {nombre}: SKILL.md ~{t}" + (f" + references ~{refs}" if refs else "") + aviso)
    if not a.todo and not a.skill and len(lista) > 10:
        print(f"- … {len(lista) - 10} más (--todo). Suma de todas: ~{sum(t for _, t, _ in lista)} en SKILL.md, ~{sum(r for _, _, r in lista)} en references")

    print("\n## Subagentes (contexto propio; el modelo es su nivel de capacidad)")
    for nombre, t, modelo in agentes():
        print(f"- {nombre}: ~{t} · model {modelo}")
    print("\nRegla 21 de AGENTS.md: no releer lo que ya está en contexto; resúmenes por script; lotes de documentos al lector-documental.")
    return 1 if a.techo and estatica > TECHO_FIJO else 0


if __name__ == "__main__":
    import _consola
    _consola.preparar()
    sys.exit(main())
