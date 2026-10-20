#!/bin/bash
# Instalador del PMO Harness para Mac: doble clic para dejar listo el computador.
# Si macOS no lo deja abrir: clic derecho > Abrir. No instala VS Code ni el asistente de IA.
cd "$(dirname "$0")" || exit 1
bash herramientas/preparar_pc.sh --doble-clic "$@"
echo
# Deja leer el resultado en la ventana del doble clic, sin esperar para siempre (y nunca si lo ejecuta un asistente)
if [ -t 0 ] && [ "${TERM_PROGRAM:-}" != "vscode" ]; then
  read -t 600 -n 1 -s -r -p "Presiona una tecla para cerrar esta ventana..." || true
  echo
fi
