#!/usr/bin/env python3
"""Consolida la evaluación de propuestas: admisibilidad, puntajes ponderados, umbrales, ranking y presupuesto.

Uso:
    python herramientas/puntaje_pauta.py <ruta-proyecto> [--fecha AAAA-MM-DD] [--salida ranking.md] [--no-registrar]

Lee evaluacion/pauta.yaml, evaluacion/admisibilidad.csv, evaluacion/puntajes.csv e items/items.csv.
- Admisible: cumple (si / na) todos los requisitos excluyentes. Los no excluyentes incumplidos quedan como "subsanable".
- Por criterio: promedio de los evaluadores; si la diferencia entre evaluadores supera `discrepancia_maxima`, se alerta.
- Puntaje ponderado = Σ promedio del criterio × ponderación (se exige que las ponderaciones sumen 1).
- Cumple umbrales: admisible, con todos los criterios puntuados, sobre el puntaje mínimo y los mínimos por criterio.
- Ranking entre las que cumplen umbrales (desempate según la pauta) y acumulado de montos vs presupuesto.
Registra los resultados en metricas/mediciones.csv (salvo --no-registrar) y muestra el ranking.
"""
import argparse
import csv
from collections import defaultdict
from datetime import date
from pathlib import Path

import yaml

import _mediciones  # noqa: E402  (escritura segura de mediciones.csv)

FUENTE = "herramientas/puntaje_pauta.py"


def leer(ruta):
    if not ruta.exists():
        return []
    with open(ruta, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def num(v):
    try:
        return float(str(v).replace(",", ".").strip())
    except (TypeError, ValueError):
        return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("proyecto")
    ap.add_argument("--fecha", default=date.today().isoformat())
    ap.add_argument("--salida")
    ap.add_argument("--no-registrar", action="store_true")
    a = ap.parse_args()
    raiz = Path(a.proyecto)
    pauta = yaml.safe_load((raiz / "evaluacion" / "pauta.yaml").read_text(encoding="utf-8")) or {}
    criterios = pauta.get("criterios") or []
    escala = pauta.get("escala") or {}
    emin, emax = num(escala.get("minimo")) or 1, num(escala.get("maximo")) or 5
    umbr = pauta.get("umbrales") or {}
    pmin = num(umbr.get("puntaje_minimo")) or 0
    min_crit = umbr.get("minimo_por_criterio") or {}
    disc_max = num(pauta.get("discrepancia_maxima")) or 2
    conv = pauta.get("convocatoria") or {}
    presupuesto = num(conv.get("presupuesto_total")) or 0
    alertas = []

    suma_w = sum(num(c.get("ponderacion")) or 0 for c in criterios)
    if criterios and abs(suma_w - 1) > 0.001:
        alertas.append(f"Las ponderaciones suman {suma_w:.3f}, no 1. Revisar la pauta.")
    excluyentes = {r["id"] for r in pauta.get("admisibilidad") or [] if r.get("excluyente", True)}
    requisitos = {r["id"] for r in pauta.get("admisibilidad") or []}

    items = {r["id"]: r for r in leer(raiz / "items" / "items.csv")}
    adm = defaultdict(dict)
    for r in leer(raiz / "evaluacion" / "admisibilidad.csv"):
        adm[r["postulacion"]][r["requisito"]] = (r.get("cumple") or "").strip().lower()
    punt = defaultdict(lambda: defaultdict(list))
    for r in leer(raiz / "evaluacion" / "puntajes.csv"):
        v = num(r.get("puntaje"))
        if v is None:
            continue
        if not emin <= v <= emax:
            alertas.append(f"{r['postulacion']} {r['criterio']}: puntaje {v} fuera de la escala {emin:g}–{emax:g}.")
        punt[r["postulacion"]][r["criterio"]].append((v, r.get("evaluador", "")))

    filas = []
    for pid in sorted(set(items) | set(adm) | set(punt)):
        it = items.get(pid, {})
        faltan_req = [q for q in requisitos if q not in adm[pid]]
        incumple_excl = [q for q in excluyentes if adm[pid].get(q) not in ("si", "sí", "na", "")]
        incumple_sub = [q for q in requisitos - excluyentes if adm[pid].get(q) == "no"]
        revisada_adm = bool(adm[pid]) and not faltan_req
        admisible = revisada_adm and not incumple_excl
        prom, faltantes = {}, []
        for c in criterios:
            vals = punt[pid].get(c["id"], [])
            if not vals:
                faltantes.append(c["id"])
                continue
            vs = [v for v, _ in vals]
            prom[c["id"]] = sum(vs) / len(vs)
            if len(vs) > 1 and max(vs) - min(vs) >= disc_max:
                detalle = ", ".join("%s=%g" % (e or "?", v) for v, e in vals)
                alertas.append(f"{pid} {c['id']}: discrepancia entre evaluadores ({detalle}). Revisar.")
        completa = bool(criterios) and not faltantes
        pond = sum(prom[c["id"]] * (num(c.get("ponderacion")) or 0) for c in criterios if c["id"] in prom) if prom else None
        bajo_min = [c for c, m in min_crit.items() if c in prom and prom[c] < float(m)]
        cumple = admisible and completa and pond is not None and pond >= pmin and not bajo_min
        filas.append({"id": pid, "nombre": it.get("nombre", ""), "monto": num(it.get("monto_solicitado")),
                      "revisada_adm": revisada_adm, "admisible": admisible, "excl": incumple_excl, "sub": incumple_sub,
                      "prom": prom, "faltan": faltantes, "pond": pond if completa else None, "parcial": pond,
                      "bajo_min": bajo_min, "cumple": cumple})

    orden_desempate = pauta.get("desempate") or []
    ranking = sorted([f for f in filas if f["cumple"]],
                     key=lambda f: [-f["pond"]] + [-f["prom"].get(c, 0) for c in orden_desempate] + [f["id"]])
    acum = 0.0
    for k, f in enumerate(ranking, 1):
        f["rank"] = k
        if f["monto"] is not None:
            acum += f["monto"]
        f["acum"] = acum
        f["dentro"] = (not presupuesto) or acum <= presupuesto

    # ----- informe -----
    out = [f"# Evaluación — {conv.get('nombre', raiz.name)}", "", f"Fecha: {a.fecha}", "",
           f"Postulaciones: {len(filas)} · con admisibilidad revisada: {sum(f['revisada_adm'] for f in filas)} · "
           f"admisibles: {sum(f['admisible'] for f in filas)} · evaluación completa: {sum(f['pond'] is not None for f in filas)} · "
           f"cumplen umbrales: {len(ranking)}", ""]
    if ranking:
        cab = "| # | Id | Nombre | Puntaje | " + " | ".join(c["id"] for c in criterios) + " | Monto | Acumulado | Presupuesto |"
        out += ["## Ranking (cumplen umbrales)", "", cab, "|" + "---|" * (8 + len(criterios) - 1)]
        for f in ranking:
            out.append(f"| {f['rank']} | {f['id']} | {f['nombre']} | {f['pond']:.2f} | "
                       + " | ".join(f"{f['prom'].get(c['id'], 0):.1f}" for c in criterios)
                       + f" | {f['monto'] or 0:,.0f} | {f['acum']:,.0f} | {'Dentro' if f['dentro'] else 'Fuera'} |".replace(",", "."))
        out.append("")
    otras = [f for f in filas if not f["cumple"]]
    if otras:
        out += ["## No cumplen umbrales o están incompletas", "", "| Id | Nombre | Motivo |", "|---|---|---|"]
        for f in otras:
            mot = []
            if not f["revisada_adm"]:
                mot.append("admisibilidad sin revisar o incompleta")
            if f["excl"]:
                mot.append("no admisible: incumple " + ", ".join(f["excl"]))
            if f["faltan"]:
                mot.append("faltan criterios: " + ", ".join(f["faltan"]))
            if f["pond"] is not None and f["pond"] < pmin:
                mot.append(f"puntaje {f['pond']:.2f} bajo el mínimo {pmin:g}")
            if f["bajo_min"]:
                mot.append("bajo el mínimo en " + ", ".join(f["bajo_min"]))
            out.append(f"| {f['id']} | {f['nombre']} | {'; '.join(mot)} |")
        out.append("")
    sub = [f for f in filas if f["sub"]]
    if sub:
        out += ["## Requisitos subsanables pendientes", ""] + [f"- {f['id']}: {', '.join(f['sub'])}" for f in sub] + [""]
    out += [f"## Alertas ({len(alertas)})", ""] + ([f"- {x}" for x in alertas] or ["- Sin alertas."]) + [""]
    texto = "\n".join(out)

    if not a.no_registrar:
        med = [(f["id"], "admisible", 1 if f["admisible"] else 0) for f in filas if f["revisada_adm"]]
        for f in filas:
            for c, v in f["prom"].items():
                med.append((f["id"], f"crit_{c}", v))
            if f["pond"] is not None:
                med.append((f["id"], "puntaje_ponderado", f["pond"]))
            med.append((f["id"], "cumple_umbrales", 1 if f["cumple"] else 0))
            if f.get("rank"):
                med.append((f["id"], "ranking", f["rank"]))
        med += [("PROYECTO", "n_postulaciones", len(filas)), ("PROYECTO", "n_admisibles", sum(f["admisible"] for f in filas)),
                ("PROYECTO", "n_evaluadas", sum(f["pond"] is not None for f in filas)),
                ("PROYECTO", "monto_seleccionable", sum(f["monto"] or 0 for f in ranking if f["dentro"]))]
        ruta = raiz / "metricas" / "mediciones.csv"
        nuevas = [{"fecha": a.fecha, "entidad": e, "metrica": m, "valor": f"{v:.10g}", "fuente": FUENTE, "comentario": ""} for e, m, v in med]
        _mediciones.registrar(ruta, nuevas, FUENTE, a.fecha)
    if a.salida:
        Path(a.salida).write_text(texto, encoding="utf-8")
    print(texto)


if __name__ == "__main__":
    import _consola
    _consola.preparar()
    main()
