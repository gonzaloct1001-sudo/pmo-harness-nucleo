"""Utilidades comunes de consola para los scripts de herramientas/.

En Windows la consola usa por defecto cp1252 y los caracteres como "−", "★" o "→" hacen caer el script
cuando la salida se redirige (pipe). preparar() fuerza UTF-8 en stdout y stderr.
"""
import sys


def preparar():
    for flujo in (sys.stdout, sys.stderr):
        try:
            flujo.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
