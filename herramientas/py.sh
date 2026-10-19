#!/bin/sh
# Ejecuta un script de Python con el primer intérprete disponible (3.9 o superior):
# la .venv del harness (Mac), python3, python o el lanzador py de Windows.
# Uso: sh herramientas/py.sh <script.py> [argumentos]
dir="$(cd "$(dirname "$0")/.." 2>/dev/null && pwd)"
for c in "$dir/.venv/bin/python" "$dir/.venv/Scripts/python.exe"; do
  if [ -n "$dir" ] && [ -x "$c" ]; then exec "$c" "$@"; fi
done
for c in python3 python; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)" >/dev/null 2>&1; then
    exec "$c" "$@"
  fi
done
if command -v py >/dev/null 2>&1; then exec py -3 "$@"; fi
echo "PMO Harness: no se encontró Python 3.9 o superior. Ejecuta el instalador (INSTALAR-WINDOWS.bat o INSTALAR-MAC.command) y vuelve a intentar." >&2
exit 1
