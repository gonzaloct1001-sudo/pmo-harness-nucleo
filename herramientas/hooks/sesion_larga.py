#!/usr/bin/env python3
"""Hook PostToolUse (todas las herramientas) de Claude Code: cuenta las acciones de la sesión y avisa cuando son muchas.

La calidad del contexto baja mucho antes de que la ventana se llene (entre el 20 y el 40 %). A las AVISO acciones, y
cada AVISO después, le recuerda a Claude guardar, actualizar el traspaso y abrir una sesión nueva. Nunca bloquea.
El conteo vive en .harness/sesiones/<id de sesión>.txt (local, fuera de Git).
"""
import json
import sys
from pathlib import Path

from _comun import leer_evento, preparar_salida

RAIZ = Path(__file__).resolve().parent.parent.parent
AVISO = 120


def main():
    preparar_salida()
    ev = leer_evento()
    sesion = str(ev.get("session_id") or "sin-id")[:40]
    carpeta = RAIZ / ".harness" / "sesiones"
    if not (RAIZ / ".harness").exists():
        return
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta = carpeta / (sesion + ".txt")
    try:
        n = int(ruta.read_text(encoding="utf-8").strip() or 0)
    except (OSError, ValueError):
        n = 0
    n += 1
    ruta.write_text(str(n), encoding="utf-8")
    if n % AVISO == 0:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext":
                          f"[Harness] Esta sesión lleva {n} acciones: la calidad del contexto baja antes de llenarse. Cierra el hito en "
                          "curso, actualiza el traspaso (regla 17), ofrece `guardar-cambios` y sugiere al usuario seguir en una sesión "
                          "nueva (`/clear` o cerrar y abrir): retomará desde el traspaso sin perder nada."}}, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
