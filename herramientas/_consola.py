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
    sys.excepthook = _anotar_y_seguir


def _anotar_y_seguir(tipo, valor, tb):
    """Un error no previsto de un script del núcleo (traceback) queda anotado en el registro de mejoras de la carpeta de
    empresa, para el mantenedor. Luego el error se muestra como siempre. SystemExit no pasa por aquí."""
    try:
        from pathlib import Path
        raiz = Path(__file__).resolve().parent.parent
        script = Path(sys.argv[0]).name if sys.argv else ""
        if tipo is not KeyboardInterrupt and script and script != "mejoras.py":
            import _nucleo
            import mejoras
            if not _nucleo.es_mantenedor(raiz):
                mejoras.anotar(raiz, "fallo", script, f"{script} falló con un error no previsto ({tipo.__name__})",
                               f"{tipo.__name__}: {str(valor)[:200]} · comando: {' '.join(sys.argv[1:])[:120]}", quien="sistema")
    except Exception:
        pass
    sys.__excepthook__(tipo, valor, tb)
