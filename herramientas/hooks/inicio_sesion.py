#!/usr/bin/env python3
"""Hook SessionStart de Claude Code: entrega el resumen de estado del harness (herramientas/estado.py).

Los demás asistentes ejecutan `python herramientas/estado.py --remoto` como paso 0 (ver AGENTS.md).
"""
import sys
from pathlib import Path

from _comun import preparar_salida

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def main():
    preparar_salida()
    import estado
    print(estado.resumen(remoto=True))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
