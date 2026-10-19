"""Escritura segura de metricas/mediciones.csv, compartida por los scripts que registran mediciones.

- Conserva el orden de las filas y las columnas extra que el usuario haya agregado al final (CLAUDE.md, principio 7).
- Reemplaza solo las mediciones de la misma fecha y fuente (volver a ejecutar un cálculo no duplica filas).
- Escribe en un archivo temporal y lo reemplaza al final: si algo falla, el archivo original queda intacto.
"""
import csv
from pathlib import Path

BASE = ["fecha", "entidad", "metrica", "valor", "fuente", "comentario"]


def registrar(ruta, nuevas, fuente, fecha):
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    filas, campos = [], list(BASE)
    if ruta.exists():
        with open(ruta, encoding="utf-8-sig", newline="") as f:
            lector = csv.DictReader(f)
            campos = list(lector.fieldnames or BASE)
            filas = list(lector)
        campos += [c for c in BASE if c not in campos]
    previas = [x for x in filas if not (x.get("fecha") == fecha and x.get("fuente") == fuente)]
    tmp = ruta.with_name(ruta.name + ".tmp")
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore", restval="")
        w.writeheader()
        w.writerows(previas + list(nuevas))
    tmp.replace(ruta)
    return len(list(nuevas))
