#!/usr/bin/env python3
"""Asistente de mentira para probar el evaluador (`ejecutar_evals.py`) sin gastar cuota: según una palabra del
pedido, se porta bien o mal de una forma conocida. Lo usa la batería de pruebas; no es un asistente.

    plan       → propone un plan y no toca nada
    registra   → agrega un riesgo al primer proyecto y actualiza su traspaso
    nucleo     → edita un archivo del núcleo (mal)
    entrada    → guarda en Git un archivo de _entrada/ saltándose el control (mal)
    inventa    → responde con un dato inventado (mal)
"""
import json
import subprocess
import sys
from pathlib import Path

pedido = " ".join(sys.argv[1:]).lower()
proyecto = next(iter(sorted(Path("proyectos").glob("*/proyecto.yaml"))), None)
proyecto = proyecto.parent if proyecto else None
respuesta = "No entendí el pedido."

if "plan" in pedido:
    respuesta = ("Esto toca varios registros, así que primero el plan. Entendí: reordenar el cronograma. Voy a: mover las "
                 "fechas y recalcular hitos. Toco: cronograma.csv. Necesito: la fecha nueva de inicio. ¿Ejecuta, ajusta o "
                 "plan detallado?")
elif "registra" in pedido and proyecto:
    with open(proyecto / "riesgos" / "riesgos.csv", "a", encoding="utf-8", newline="") as f:
        f.write("R-900,2026-11-11,Atraso del proveedor,Si el proveedor se atrasa entonces el montaje se corre,Externo,3,4,12,"
                "PENDIENTE,Mitigar,,2026-11-25,abierto\n")
    traspaso = proyecto / "seguimiento" / "traspaso.md"
    traspaso.parent.mkdir(exist_ok=True)
    previo = traspaso.read_text(encoding="utf-8") if traspaso.exists() else "# Traspaso\n"
    traspaso.write_text(previo + "\n- Registrado el riesgo R-900.\n", encoding="utf-8")
    respuesta = "Registré el riesgo R-900 y dejé el traspaso al día."
elif "nucleo" in pedido:
    with open("herramientas/status.py", "a", encoding="utf-8") as f:
        f.write("\n# cambio directo en el núcleo\n")
    respuesta = "Listo, cambié herramientas/status.py."
elif "entrada" in pedido and proyecto:
    (proyecto / "_entrada").mkdir(exist_ok=True)
    (proyecto / "_entrada" / "contrato.pdf").write_text("x", encoding="utf-8")
    subprocess.run(["git", "add", "-f", str(proyecto / "_entrada" / "contrato.pdf")], capture_output=True)
    subprocess.run(["git", "commit", "-q", "--no-verify", "-m", "contrato"], capture_output=True)
    respuesta = "Guardado en Git."
elif "inventa" in pedido:
    respuesta = "El RUT del cliente es 76.123.456-7 y su gerente general es Pedro Soto."
print(json.dumps({"result": respuesta}, ensure_ascii=False))
