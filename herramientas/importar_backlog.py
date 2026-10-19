#!/usr/bin/env python3
"""Importa o actualiza el backlog del proyecto desde GitHub Issues o desde una exportación CSV (Jira u otra).

Uso:
    python herramientas/importar_backlog.py <ruta-proyecto> --desde github --repo dueño/repositorio [--simular]
    python herramientas/importar_backlog.py <ruta-proyecto> --desde csv --archivo export.csv [--simular]

GitHub: usa la CLI `gh` (debe estar instalada y autenticada). Mapeo por etiquetas:
  tipo (bug, enhancement/feature/historia, task/tarea, epic/epica, tech-debt/deuda), prioridad
  (prioridad:alta|media|baja o P0–P3), puntos ("pts:3", "points:3", "sp:3"), estado ("in progress",
  "en progreso", "review", "en revisión"); cerrado = hecho. Sprint = milestone.
CSV (Jira u otra): reconoce columnas habituales (Issue key, Summary, Issue Type, Status, Priority, Sprint,
  Story Points / Custom field (Story Points), Assignee, Created, Resolved, Labels, Epic Link / Parent).
  Los estados se traducen con `equivalencias` de agil/estados.yaml.
Los ítems existentes se actualizan por id; los nuevos se agregan; nunca se borra nada. Con --simular solo
muestra lo que haría.
"""
import argparse
import csv
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import yaml

COLUMNAS = ["id", "tipo", "titulo", "epica", "prioridad", "puntos", "estado", "sprint", "responsable",
            "fecha_creacion", "fecha_inicio", "fecha_cierre", "etiquetas", "requisito", "comentario"]
ALIAS = {
    "id": ["issue key", "key", "id", "clave"],
    "titulo": ["summary", "title", "titulo", "título", "resumen"],
    "tipo": ["issue type", "type", "tipo"],
    "estado": ["status", "estado"],
    "prioridad": ["priority", "prioridad"],
    "sprint": ["sprint", "iteration", "milestone"],
    "puntos": ["story points", "custom field (story points)", "story point estimate", "puntos", "estimate"],
    "responsable": ["assignee", "asignado", "responsable"],
    "fecha_creacion": ["created", "creado", "fecha_creacion"],
    "fecha_cierre": ["resolved", "resolution date", "closed", "fecha_cierre"],
    "etiquetas": ["labels", "etiquetas"],
    "epica": ["epic link", "parent", "epic", "epica", "épica", "parent summary"],
}
TIPOS = {"bug": "bug", "story": "historia", "historia": "historia", "task": "tarea", "sub-task": "tarea", "subtask": "tarea",
         "tarea": "tarea", "epic": "epica", "épica": "epica", "epica": "epica", "spike": "spike", "enhancement": "historia",
         "feature": "historia", "tech-debt": "deuda", "technical debt": "deuda", "deuda": "deuda"}
FORMATOS_FECHA = ["%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%d %H:%M", "%Y-%m-%d", "%d/%b/%y %I:%M %p",
                  "%d/%m/%Y %H:%M", "%d/%m/%Y", "%m/%d/%Y %H:%M", "%m/%d/%Y"]


def normalizar_fecha(v):
    v = (v or "").strip()
    if not v:
        return ""
    for f in FORMATOS_FECHA:
        try:
            return datetime.strptime(v, f).strftime("%Y-%m-%d")
        except ValueError:
            continue
    m = re.match(r"(\d{4}-\d{2}-\d{2})", v)
    return m.group(1) if m else v


def desde_github(repo):
    try:
        r = subprocess.run(["gh", "issue", "list", "--repo", repo, "--state", "all", "--limit", "1000", "--json",
                            "number,title,state,labels,assignees,milestone,createdAt,closedAt"],
                           capture_output=True, text=True, timeout=120)
    except FileNotFoundError:
        sys.exit("No encuentro la CLI de GitHub (gh). Instálala desde https://cli.github.com/ y ejecuta 'gh auth login'.")
    if r.returncode != 0:
        sys.exit(f"Error de gh: {r.stderr.strip()}")
    items = []
    for i in json.loads(r.stdout):
        etiquetas = [l["name"] for l in i.get("labels") or []]
        low = [e.lower() for e in etiquetas]
        tipo = next((TIPOS[e] for e in low if e in TIPOS), "historia")
        prio = next((e.split(":", 1)[1] for e in low if e.startswith("prioridad:")), "")
        prio = prio or next(({"p0": "alta", "p1": "alta", "p2": "media", "p3": "baja"}[e] for e in low if e in ("p0", "p1", "p2", "p3")), "")
        pts = next((re.sub(r"^(pts|points|sp):", "", e) for e in low if re.match(r"^(pts|points|sp):\d+", e)), "")
        if i["state"].upper() == "CLOSED":
            estado = "hecho"
        elif any(e in ("in progress", "en progreso", "doing") for e in low):
            estado = "en_progreso"
        elif any(e in ("review", "in review", "en revisión", "en revision") for e in low):
            estado = "en_revision"
        else:
            estado = "por_hacer"
        items.append({"id": f"GH-{i['number']}", "tipo": tipo, "titulo": i["title"], "prioridad": prio, "puntos": pts,
                      "estado": estado, "sprint": (i.get("milestone") or {}).get("title", ""),
                      "responsable": (i.get("assignees") or [{}])[0].get("login", "") if i.get("assignees") else "",
                      "fecha_creacion": normalizar_fecha(i.get("createdAt")), "fecha_cierre": normalizar_fecha(i.get("closedAt")),
                      "etiquetas": ";".join(etiquetas)})
    return items


def desde_csv(archivo, equivalencias):
    with open(archivo, encoding="utf-8-sig", newline="") as f:
        filas = list(csv.DictReader(f))
    if not filas:
        return []
    cols = {c.lower().strip(): c for c in filas[0].keys()}
    mapa = {}
    for destino, alias in ALIAS.items():
        for al in alias:
            if al in cols:
                mapa[destino] = cols[al]
                break
    if "id" not in mapa or "titulo" not in mapa:
        sys.exit(f"No encuentro columnas de id y título. Columnas del archivo: {', '.join(filas[0].keys())}")
    print("Mapeo de columnas: " + ", ".join(f"{k} ← {v}" for k, v in mapa.items()))
    eq = {k.lower(): v for k, v in (equivalencias or {}).items()}
    items = []
    for r in filas:
        it = {k: (r.get(v) or "").strip() for k, v in mapa.items()}
        it["tipo"] = TIPOS.get(it.get("tipo", "").lower(), it.get("tipo", "").lower() or "historia")
        est = it.get("estado", "")
        it["estado"] = eq.get(est.lower(), est.lower().replace(" ", "_") or "por_hacer")
        it["prioridad"] = {"highest": "alta", "high": "alta", "medium": "media", "low": "baja", "lowest": "baja"}.get(
            it.get("prioridad", "").lower(), it.get("prioridad", "").lower())
        for campo in ("fecha_creacion", "fecha_cierre"):
            it[campo] = normalizar_fecha(it.get(campo, ""))
        items.append(it)
    return items


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("proyecto")
    ap.add_argument("--desde", choices=["github", "csv"], required=True)
    ap.add_argument("--repo")
    ap.add_argument("--archivo")
    ap.add_argument("--simular", action="store_true")
    a = ap.parse_args()
    raiz = Path(a.proyecto)
    ruta = raiz / "agil" / "backlog.csv"
    cfg = yaml.safe_load((raiz / "agil" / "estados.yaml").read_text(encoding="utf-8")) if (raiz / "agil" / "estados.yaml").exists() else {}
    if a.desde == "github":
        if not a.repo:
            sys.exit("Indica --repo dueño/repositorio")
        nuevos = desde_github(a.repo)
    else:
        if not a.archivo:
            sys.exit("Indica --archivo con la exportación CSV")
        nuevos = desde_csv(a.archivo, cfg.get("equivalencias"))

    existentes = []
    if ruta.exists():
        with open(ruta, encoding="utf-8-sig", newline="") as f:
            existentes = list(csv.DictReader(f))
    columnas = list(existentes[0].keys()) if existentes else COLUMNAS
    por_id = {e["id"]: e for e in existentes}
    agregados, actualizados, sin_cambio = 0, 0, 0
    for it in nuevos:
        if it["id"] in por_id:
            e = por_id[it["id"]]
            cambios = {k: v for k, v in it.items() if k in columnas and v and e.get(k) != v}
            if cambios:
                if cambios.get("estado") in ("en_progreso", "en_revision") and not e.get("fecha_inicio"):
                    e["fecha_inicio"] = datetime.now().strftime("%Y-%m-%d")
                e.update(cambios)
                actualizados += 1
            else:
                sin_cambio += 1
        else:
            fila = {c: it.get(c, "") for c in columnas}
            existentes.append(fila)
            por_id[it["id"]] = fila
            agregados += 1
    print(f"Ítems leídos: {len(nuevos)} · nuevos: {agregados} · actualizados: {actualizados} · sin cambios: {sin_cambio}")
    faltantes = [c for c in ("puntos", "sprint") if not any(it.get(c) for it in nuevos)]
    if faltantes:
        print(f"Aviso: ningún ítem trae {', '.join(faltantes)}; las métricas de sprint quedarán incompletas.")
    if a.simular:
        print("Simulación: no se escribió nada.")
        return
    with open(ruta, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columnas, extrasaction="ignore")
        w.writeheader()
        w.writerows(existentes)
    print(f"Backlog actualizado: {ruta}")


if __name__ == "__main__":
    import _consola
    _consola.preparar()
    main()
