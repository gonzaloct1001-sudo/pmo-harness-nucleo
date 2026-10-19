#!/usr/bin/env python3
"""Genera cronograma/gantt.md (diagrama Mermaid) desde cronograma/cronograma.csv.

Uso:
    python herramientas/gantt_mermaid.py proyectos/<slug> [--hoy AAAA-MM-DD]

En VS Code se visualiza con la vista previa de Markdown (extensión
"Markdown Preview Mermaid Support"). En GitHub se ve directamente.
Marcas: terminadas = done, en curso = active, atrasadas = crit, hitos = milestone.
"""
import argparse
import csv
import re
from datetime import date, datetime
from pathlib import Path

import _config  # noqa: E402  (proyecto.yaml con herencia de programa)


def f(v):
    try:
        return datetime.strptime((v or "").strip(), "%Y-%m-%d").date()
    except ValueError:
        return None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("proyecto")
    p.add_argument("--hoy")
    p.add_argument("--cronograma", help="archivo de cronograma (por defecto cronograma/cronograma.csv del proyecto)")
    p.add_argument("--salida", help="archivo de salida (por defecto cronograma/gantt.md del proyecto)")
    p.add_argument("--titulo", default="Carta Gantt")
    a = p.parse_args()
    hoy = f(a.hoy) if a.hoy else date.today()
    raiz = Path(a.proyecto)
    origen = Path(a.cronograma) if a.cronograma else raiz / "cronograma" / "cronograma.csv"
    with open(origen, encoding="utf-8-sig", newline="") as fh:
        tareas = list(csv.DictReader(fh))

    lineas = [f"# {a.titulo}", "", f"Generada el {hoy.isoformat()} desde `{origen.name}`. No editar a mano.", "",
              "```mermaid", "gantt", "    dateFormat YYYY-MM-DD", "    axisFormat %b %y", "    todayMarker on"]
    grupos = {}
    for t in tareas:
        grupos.setdefault((t.get("subproyecto") or "Sin subproyecto").strip(), []).append(t)
    for sp, lista in grupos.items():
        lineas.append(f"    section {sp}")
        for t in lista:
            ini, fin = f(t.get("inicio_plan")), f(t.get("fin_plan"))
            if not ini or not fin:
                continue
            av = float((t.get("avance_pct") or "0").replace(",", ".") or 0)
            marcas = []
            if av >= 100:
                marcas.append("done")
            elif fin < hoy:
                marcas.append("crit")
            elif ini <= hoy:
                marcas.append("active")
            nombre = re.sub(r"[:#;]", " ", t.get("tarea", "")).strip()
            tid = re.sub(r"\W", "", t.get("id", ""))
            if (t.get("es_hito") or "").strip().lower() in ("si", "sí"):
                marcas.append("milestone")
                lineas.append(f"    {nombre} :{', '.join(marcas + [tid])}, {fin.isoformat()}, 0d")
            else:
                etiqueta = f"{nombre} ({av:.0f}%)"
                lineas.append(f"    {etiqueta} :{', '.join(marcas + [tid])}, {ini.isoformat()}, {fin.isoformat()}")
    lineas += ["```", ""]
    destino = Path(a.salida) if a.salida else raiz / "cronograma" / "gantt.md"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text("\n".join(lineas), encoding="utf-8")
    print(f"Gantt generado: {destino.as_posix()}")


if __name__ == "__main__":
    import _consola
    _consola.preparar()
    main()
