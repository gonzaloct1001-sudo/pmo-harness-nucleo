#!/usr/bin/env python3
"""Hook PreToolUse (Edit, Write, MultiEdit): en una carpeta de empresa, impide editar los archivos del núcleo.

Un archivo del núcleo se reemplaza al actualizar: lo que la empresa cambie ahí puede perderse. Lo propio va aparte,
donde ninguna actualización lo toca (principio 8): herramientas, hooks y pruebas en `empresa/extensiones/`; skills
propias en `.claude/skills/<nombre>/`; reglas en `empresa/estilo.md` o en el `CLAUDE.md` del proyecto. Lo que al
núcleo le falta o le falla se anota con `mejoras.py --anotar`.

No aplica en la carpeta donde se mantiene el núcleo (no tiene registro de instalación), ni a los archivos propios que
viven dentro de carpetas del núcleo, ni a los tres que se fusionan al actualizar (`.claude/settings.json`,
`.gitignore`, `requirements.txt`).
"""
import csv
import os
import sys
from pathlib import Path

from _comun import bloquear, leer_evento, preparar_salida

RAIZ = Path(__file__).resolve().parent.parent.parent
SE_FUSIONAN = {".claude/settings.json", ".gitignore", "requirements.txt"}


def main():
    preparar_salida()
    ev = leer_evento()
    ruta = (ev.get("tool_input") or {}).get("file_path") or (ev.get("tool_input") or {}).get("notebook_path") or ""
    registro = RAIZ / ".harness" / "nucleo-instalado.csv"
    if not ruta or not registro.is_file():
        return
    try:
        rel = Path(os.path.abspath(ruta)).relative_to(Path(os.path.abspath(RAIZ))).as_posix()
    except ValueError:
        return
    if rel in SE_FUSIONAN:
        return
    with open(registro, encoding="utf-8", newline="") as f:
        del_nucleo = {r["ruta"] for r in csv.DictReader(f)}
    comparar = (lambda x: x.lower()) if os.name == "nt" else (lambda x: x)
    if comparar(rel) not in {comparar(x) for x in del_nucleo}:
        return
    sys.path.insert(0, str(RAIZ / "herramientas"))
    import _nucleo
    if _nucleo.es_mantenedor(RAIZ):
        return
    bloquear(f"BLOQUEADO por el harness: `{rel}` es del núcleo y una actualización lo reemplaza; lo que cambies ahí puede "
             "perderse. Lo propio va aparte, donde ninguna actualización lo toca:\n"
             "- una herramienta, un hook o una prueba propia → `empresa/extensiones/` (lee su LEEME.md);\n"
             "- una skill propia → `.claude/skills/<nombre-propio>/SKILL.md`;\n"
             "- una regla o preferencia propia → `empresa/estilo.md` o el `CLAUDE.md` del proyecto.\n"
             "Si al núcleo le falta algo o tiene un error, no lo arregles aquí: anótalo con "
             "`python herramientas/mejoras.py --anotar --tipo cambiar --donde " + rel + " --que \"...\" --evidencia \"...\"` "
             "y, si hace falta ya, resuélvelo con una extensión.")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        sys.exit(0)
