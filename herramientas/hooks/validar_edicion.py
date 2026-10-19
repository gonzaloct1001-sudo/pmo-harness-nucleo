#!/usr/bin/env python3
"""Hook PostToolUse (Edit/Write/MultiEdit y Bash): valida CSV y YAML del harness justo después de editarlos.

- Con Edit/Write/MultiEdit revisa el archivo editado.
- Con Bash (por ejemplo `cat >> archivo.csv` o un script) revisa los CSV y YAML de proyectos/ modificados en
  los últimos minutos, porque un comando de consola no informa qué archivos tocó.
- CSV: todas las filas con la misma cantidad de columnas que el encabezado; fechas AAAA-MM-DD en columnas
  de fecha; sin encabezados duplicados.
- YAML: que se pueda leer; en metricas.yaml, campos obligatorios y valores permitidos.
Si encuentra problemas, se los muestra a Claude para que los corrija de inmediato.
Las reglas de validación están en _comun.py y son las mismas del control de Git (.githooks/pre-commit).
"""
import sys
import time
from pathlib import Path

from _comun import bloquear, leer_evento, preparar_salida, revisar

RAIZ = Path(__file__).resolve().parent.parent.parent
VENTANA_SEG = 120


def main():
    preparar_salida()
    ev = leer_evento()
    ruta = (ev.get("tool_input") or {}).get("file_path") or ""
    if ruta:
        rutas = [Path(ruta)] if Path(ruta).exists() else []
    elif ev.get("tool_name") in ("Bash", "PowerShell"):
        rutas = recientes(RAIZ)
    else:
        return
    mensajes = []
    for r in rutas:
        problemas = revisar(r)
        if problemas:
            mensajes.append(f"{r}:\n- " + "\n- ".join(problemas))
    if mensajes:
        bloquear("El harness detectó problemas tras la edición:\n" + "\n".join(mensajes) + "\nCorrígelos antes de continuar.")


def recientes(base, segundos=VENTANA_SEG):
    """CSV y YAML bajo base/proyectos y base/empresa modificados hace menos de `segundos` (excluye _entrada)."""
    limite = time.time() - segundos
    rutas = []
    for carpeta in (base / "proyectos", base / "empresa"):
        if carpeta.exists():
            rutas += [p for p in carpeta.rglob("*") if p.is_file() and p.suffix.lower() in (".csv", ".yaml", ".yml")
                      and "_entrada" not in p.parts and p.stat().st_mtime >= limite]
    return rutas


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        sys.exit(0)
