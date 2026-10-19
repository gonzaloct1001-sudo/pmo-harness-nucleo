#!/usr/bin/env python3
"""Métricas de un proyecto ágil: sprints, flujo, calidad, DORA, deuda técnica y trazabilidad.

Uso:
    python herramientas/metricas_agil.py <ruta-proyecto> [--fecha AAAA-MM-DD] [--ventana-dias 30] [--no-registrar]

Lee agil/backlog.csv, agil/sprints.csv, agil/estados.yaml e ingenieria/(despliegues|deuda-tecnica|requisitos).csv.
- Sprints: velocidad y cumplimiento del compromiso (promedio de los últimos 3 cerrados) y burndown del sprint en curso.
- Flujo: trabajo en curso, bugs abiertos, tiempo de ciclo (mediana, ítems cerrados en la ventana).
- DORA (despliegues a producción en la ventana): frecuencia semanal, tiempo de entrega (mediana, horas),
  tasa de falla de cambios y tiempo de recuperación (mediana, minutos).
- Deuda técnica abierta y de prioridad alta; requisitos sin prueba o sin historia.
Registra las métricas (nivel proyecto) en metricas/mediciones.csv y muestra un informe.
"""
import argparse
import csv
import statistics
from datetime import date, datetime, timedelta
from pathlib import Path

import yaml

import _mediciones  # noqa: E402  (escritura segura de mediciones.csv)

FUENTE = "herramientas/metricas_agil.py"


def leer(ruta):
    if not ruta.exists():
        return []
    with open(ruta, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def fecha(v):
    try:
        return datetime.strptime(str(v).strip()[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def num(v, d=0.0):
    try:
        return float(str(v).replace(",", ".").strip())
    except (TypeError, ValueError):
        return d


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("proyecto")
    ap.add_argument("--fecha")
    ap.add_argument("--ventana-dias", type=int, default=30)
    ap.add_argument("--no-registrar", action="store_true")
    a = ap.parse_args()
    raiz = Path(a.proyecto)
    hoy = fecha(a.fecha) if a.fecha else date.today()
    desde = hoy - timedelta(days=a.ventana_dias)
    cfg = yaml.safe_load((raiz / "agil" / "estados.yaml").read_text(encoding="utf-8")) if (raiz / "agil" / "estados.yaml").exists() else {}
    estados = cfg.get("estados") or []
    terminados = {e["id"] for e in estados if str(e.get("categoria", "")).startswith("terminado")} or {"hecho", "descartado"}
    hechos = {e["id"] for e in estados if e.get("categoria") == "terminado"} or {"hecho"}
    en_curso = {e["id"] for e in estados if e.get("categoria") == "en_curso"} or {"en_progreso", "en_revision"}
    limite_wip = cfg.get("limite_trabajo_en_curso")

    backlog = leer(raiz / "agil" / "backlog.csv")
    sprints = leer(raiz / "agil" / "sprints.csv")
    med, out = [], [f"# Métricas ágiles — corte {hoy.isoformat()} (ventana {a.ventana_dias} días)", ""]

    # ---- Sprints ----
    def completado(sp):
        if str(sp.get("completado_pts", "")).strip():
            return num(sp["completado_pts"])
        fin = fecha(sp.get("fin"))
        return sum(num(i.get("puntos")) for i in backlog if i.get("sprint") == sp["sprint"] and i.get("estado") in hechos
                   and (not fin or (fecha(i.get("fecha_cierre")) or hoy) <= fin))

    cerrados = [s for s in sprints if s.get("estado", "").lower() == "cerrado" and fecha(s.get("fin")) and fecha(s["fin"]) <= hoy]
    cerrados.sort(key=lambda s: fecha(s["fin"]))
    ult3 = cerrados[-3:]
    if ult3:
        vel = statistics.mean(completado(s) for s in ult3)
        cumpl = statistics.mean(completado(s) / num(s.get("comprometido_pts"), 1) for s in ult3 if num(s.get("comprometido_pts")))
        med += [("velocidad_promedio", vel), ("cumplimiento_compromiso", cumpl)]
        out += ["## Sprints cerrados (últimos 3)", "", "| Sprint | Comprometido | Completado | Cumplimiento |", "|---|---|---|---|"]
        for s in ult3:
            c, p = completado(s), num(s.get("comprometido_pts"))
            out.append(f"| {s['sprint']} | {p:g} | {c:g} | {c / p:.0%} |" if p else f"| {s['sprint']} | — | {c:g} | — |")
        out += ["", f"Velocidad promedio: {vel:.1f} pts · cumplimiento promedio: {cumpl:.0%}", ""]
    actual = next((s for s in sprints if fecha(s.get("inicio")) and fecha(s.get("fin")) and fecha(s["inicio"]) <= hoy <= fecha(s["fin"])), None)
    if actual:
        ini, fin = fecha(actual["inicio"]), fecha(actual["fin"])
        items_sp = [i for i in backlog if i.get("sprint") == actual["sprint"]]
        comp = num(actual.get("comprometido_pts")) or sum(num(i.get("puntos")) for i in items_sp)
        hecho_pts = sum(num(i.get("puntos")) for i in items_sp if i.get("estado") in hechos)
        dias_tot = max((fin - ini).days, 1)
        transcurrido = min(max((hoy - ini).days, 0), dias_tot) / dias_tot
        med.append(("avance_sprint_actual", hecho_pts / comp if comp else 0))
        out += [f"## Sprint en curso: {actual['sprint']} ({ini} a {fin})", "", f"Objetivo: {actual.get('objetivo', '')}", "",
                f"Terminado {hecho_pts:g} de {comp:g} pts ({hecho_pts / comp:.0%}) con {transcurrido:.0%} del tiempo transcurrido."
                if comp else "Sin puntos comprometidos.", "", "| Día | Restante real | Restante ideal |", "|---|---|---|"]
        d = ini
        while d <= min(hoy, fin):
            cerrado = sum(num(i.get("puntos")) for i in items_sp if i.get("estado") in hechos and fecha(i.get("fecha_cierre")) and fecha(i["fecha_cierre"]) <= d)
            ideal = comp * (1 - (d - ini).days / dias_tot)
            out.append(f"| {d.isoformat()} | {comp - cerrado:g} | {ideal:.1f} |")
            d += timedelta(days=1)
        out.append("")
        if comp and transcurrido - hecho_pts / comp > 0.25:
            out += ["**Alerta:** el avance del sprint va más de 25 puntos porcentuales detrás del tiempo transcurrido.", ""]

    # ---- Flujo y calidad ----
    wip = sum(1 for i in backlog if i.get("estado") in en_curso)
    bugs = sum(1 for i in backlog if i.get("tipo") == "bug" and i.get("estado") not in terminados)
    ciclos = [(fecha(i["fecha_cierre"]) - fecha(i["fecha_inicio"])).days for i in backlog
              if i.get("estado") in hechos and fecha(i.get("fecha_inicio")) and fecha(i.get("fecha_cierre"))
              and desde <= fecha(i["fecha_cierre"]) <= hoy]
    med += [("trabajo_en_curso", wip), ("bugs_abiertos", bugs)]
    if ciclos:
        med.append(("tiempo_ciclo_mediana_dias", statistics.median(ciclos)))
    out += ["## Flujo y calidad", "", f"- Trabajo en curso: {wip}" + (f" (límite {limite_wip})" if limite_wip else ""),
            f"- Bugs abiertos: {bugs}",
            f"- Tiempo de ciclo mediano: {statistics.median(ciclos):g} días ({len(ciclos)} ítems cerrados en la ventana)" if ciclos
            else "- Tiempo de ciclo: sin ítems cerrados con fechas en la ventana", ""]

    # ---- DORA ----
    desp = [d for d in leer(raiz / "ingenieria" / "despliegues.csv")
            if fecha(d.get("fecha")) and desde < fecha(d["fecha"]) <= hoy and d.get("entorno", "").lower() in ("produccion", "producción", "prod")]
    out += ["## Entrega (DORA, despliegues a producción)", ""]
    if desp:
        fallidos = [d for d in desp if d.get("resultado", "").lower() in ("falla", "rollback", "reversa") or d.get("causo_incidente", "").lower() in ("si", "sí")]
        freq = len(desp) / (a.ventana_dias / 7)
        lead = [num(d.get("lead_time_horas")) for d in desp if str(d.get("lead_time_horas", "")).strip()]
        rec = [num(d.get("minutos_recuperacion")) for d in fallidos if str(d.get("minutos_recuperacion", "")).strip()]
        med += [("frecuencia_despliegue_semana", freq), ("tasa_falla_cambios", len(fallidos) / len(desp))]
        if lead:
            med.append(("lead_time_cambios_horas", statistics.median(lead)))
        if rec:
            med.append(("tiempo_recuperacion_min", statistics.median(rec)))
        out += [f"- Despliegues: {len(desp)} ({freq:.1f} por semana)",
                f"- Tiempo de entrega mediano: {statistics.median(lead):g} h" if lead else "- Tiempo de entrega: sin datos",
                f"- Tasa de falla de cambios: {len(fallidos) / len(desp):.0%} ({len(fallidos)} de {len(desp)})",
                f"- Tiempo de recuperación mediano: {statistics.median(rec):g} min" if rec else "- Tiempo de recuperación: sin fallas con datos", ""]
    else:
        out += ["- Sin despliegues a producción registrados en la ventana.", ""]

    # ---- Deuda y trazabilidad ----
    deuda = [d for d in leer(raiz / "ingenieria" / "deuda-tecnica.csv") if d.get("estado", "").lower() not in ("resuelta", "cerrada", "descartada")]
    alta = [d for d in deuda if d.get("prioridad", "").lower() == "alta"]
    reqs = [r for r in leer(raiz / "ingenieria" / "requisitos.csv") if r.get("estado", "").lower() not in ("descartado", "eliminado")]
    sin_prueba = [r for r in reqs if not r.get("pruebas", "").strip()]
    sin_hist = [r for r in reqs if not r.get("historias", "").strip()]
    med += [("deuda_tecnica_abierta", len(deuda)), ("deuda_tecnica_alta", len(alta))]
    if reqs:
        med.append(("requisitos_sin_prueba", len(sin_prueba)))
    out += ["## Deuda técnica y trazabilidad", "", f"- Deuda abierta: {len(deuda)} (prioridad alta: {len(alta)})"]
    out += [f"  - {d['id']}: {d.get('titulo')} ({d.get('componente')})" for d in alta]
    out += [f"- Requisitos vigentes: {len(reqs)} · sin prueba: {len(sin_prueba)} · sin historia: {len(sin_hist)}"]
    out += [f"  - {r['id']} sin prueba: {r.get('requisito')}" for r in sin_prueba]
    out += [f"  - {r['id']} sin historia: {r.get('requisito')}" for r in sin_hist]
    texto = "\n".join(out) + "\n"

    if not a.no_registrar and med:
        ruta = raiz / "metricas" / "mediciones.csv"
        nuevas = [{"fecha": hoy.isoformat(), "entidad": "PROYECTO", "metrica": m, "valor": f"{v:.10g}", "fuente": FUENTE, "comentario": ""}
                  for m, v in med]
        _mediciones.registrar(ruta, nuevas, FUENTE, hoy.isoformat())
    print(texto)


if __name__ == "__main__":
    import _consola
    _consola.preparar()
    main()
