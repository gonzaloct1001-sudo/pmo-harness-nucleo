#!/usr/bin/env python3
"""Hook PostToolUse (herramienta Skill) de Claude Code: anota qué skill se usó y cuándo en .harness/uso-skills.csv.

Es el dato con que entropia.py encuentra skills sin uso (candidatas a fusionarse o retirarse). Local, fuera de Git.
"""
import sys
from datetime import date
from pathlib import Path

from _comun import leer_evento, preparar_salida

RAIZ = Path(__file__).resolve().parent.parent.parent


def main():
    preparar_salida()
    ev = leer_evento()
    entrada = ev.get("tool_input") or {}
    skill = str(entrada.get("skill") or entrada.get("name") or entrada.get("command") or "").strip().lstrip("/").split(" ")[0]
    if not skill or not (RAIZ / ".harness").exists():
        return
    ruta = RAIZ / ".harness" / "uso-skills.csv"
    nuevo = not ruta.exists()
    with open(ruta, "a", encoding="utf-8", newline="") as f:
        if nuevo:
            f.write("fecha,skill\n")
        f.write(f"{date.today().isoformat()},{skill}\n")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
