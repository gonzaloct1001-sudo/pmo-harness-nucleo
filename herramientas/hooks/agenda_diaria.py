#!/usr/bin/env python3
"""Hook UserPromptSubmit de Claude Code: en la primera interacción del día entrega la agenda (herramientas/agenda.py).

Lo vencido, lo de hoy, lo que viene en 14 días y los reportes que tocan hoy, de todos los proyectos. Una sola vez por
día y por computador (marca en .harness/agenda-vista.txt); el resto del día no dice nada. Los demás asistentes la piden
con `python herramientas/agenda.py --una-vez` al recibir el primer pedido del día.
"""
import json
import sys
from pathlib import Path

from _comun import leer_evento, preparar_salida

RAIZ = Path(__file__).resolve().parent.parent.parent


def main():
    preparar_salida()
    leer_evento()
    if not (RAIZ / ".harness" / "estado.yaml").exists():
        return  # sin instalar todavía no hay proyectos que agendar
    sys.path.insert(0, str(RAIZ / "herramientas"))
    import _nucleo
    import agenda
    if _nucleo.es_mantenedor(RAIZ):
        return
    texto = agenda.del_dia(RAIZ, una_vez=True)
    if texto:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext":
                          "[Agenda del día del PMO Harness] Es la primera interacción de hoy. Antes de atender el pedido, "
                          "muéstrale al usuario esta agenda en pocas líneas (lo vencido primero, después lo de hoy y lo que viene); "
                          "no la repitas más tarde y no actúes sobre ella sin que lo pida.\n" + texto}}, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
