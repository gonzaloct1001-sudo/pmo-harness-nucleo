#!/bin/bash
# Instalador del PMO Harness para Mac: doble clic para revisar e instalar (con tu permiso) lo necesario.
# Si macOS no lo deja abrir: clic derecho > Abrir. No instala VS Code ni el asistente de IA.
cd "$(dirname "$0")" || exit 1
bash herramientas/preparar_pc.sh "$@"
echo
read -n 1 -s -r -p "Listo. Presiona una tecla para cerrar..."
echo
