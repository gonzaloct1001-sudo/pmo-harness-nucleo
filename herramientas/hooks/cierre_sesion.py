#!/usr/bin/env python3
"""Hook Stop de Claude Code: no dejar un proyecto a medias al terminar.

Si hay cambios sin guardar en proyectos/ y el traspaso del proyecto tocado no se actualizó en esta sesión, pide una
sola vez (stop_hook_active evita el bucle) cerrar bien: traspaso al día (regla 17) y ofrecer guardar-cambios.
Si no hay nada pendiente, no dice nada.
"""
import json
import subprocess
import sys
import time
from pathlib import Path

from _comun import leer_evento, preparar_salida

RAIZ = Path(__file__).resolve().parent.parent.parent
HORAS_TRASPASO = 3


def main():
    preparar_salida()
    ev = leer_evento()
    if ev.get("stop_hook_active"):
        return
    r = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all", "--", "proyectos"], cwd=RAIZ, capture_output=True,
                       text=True, encoding="utf-8", errors="replace", timeout=20)
    if r.returncode != 0:
        return
    cambiados = [l[3:].strip().strip('"') for l in r.stdout.splitlines() if l.strip()]
    tocados = sorted({c.split("/")[1] for c in cambiados if c.startswith("proyectos/") and c.count("/") >= 2
                      and "/_entrada/" not in c})
    sin_traspaso = []
    for slug in tocados:
        traspaso = RAIZ / "proyectos" / slug / "seguimiento" / "traspaso.md"
        if not (traspaso.exists() and time.time() - traspaso.stat().st_mtime < HORAS_TRASPASO * 3600):
            sin_traspaso.append(slug)  # el traspaso no se tocó en las últimas horas: la sesión cambió cosas y no lo dijo
    if sin_traspaso:
        print(json.dumps({"decision": "block", "reason":
                          "Antes de terminar: hay cambios sin guardar en " + ", ".join(sin_traspaso) + " y su traspaso no se actualizó. "
                          "Actualiza proyectos/<slug>/seguimiento/traspaso.md (regla 17: hecho, próximo paso, comprobado, no comprobado, "
                          "tuve que adivinar) y ofrece `guardar-cambios` en una línea. Si el usuario ya lo decidió, termina."},
                         ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
