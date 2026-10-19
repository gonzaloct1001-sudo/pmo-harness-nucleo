#!/usr/bin/env python3
"""Valor ganado (EVM), ruta crítica (CPM) y pronóstico de término de un proyecto de ejecución.

Uso:
    python herramientas/evm_cpm.py <ruta-proyecto> [--fecha AAAA-MM-DD] [--registrar] [--salida informe.md]

Lee cronograma/cronograma.csv (columnas opcionales costo_plan y costo_real) y la línea base de proyecto.yaml.

Ruta crítica (plan): pasada hacia adelante y hacia atrás con dependencias fin-inicio sin desfase; una tarea
no empieza antes de su inicio planificado. Holgura total = inicio más tardío − inicio más temprano (días).
Pronóstico: las tareas terminadas usan su fecha real; las en curso terminan en (fecha de corte + duración
restante según avance); las no iniciadas empiezan cuando terminan sus predecesoras y no antes del corte.

Valor ganado (solo si hay costo_plan): PV = Σ costo_plan × % planificado a la fecha (lineal entre inicio y fin
plan); EV = Σ costo_plan × avance real; AC = Σ costo_real. SPI = EV/PV · CPI = EV/AC · EAC = BAC/CPI ·
ETC = EAC − AC · VAC = BAC − EAC · TCPI = (BAC − EV)/(BAC − AC).
"""
import argparse
import csv
from datetime import date, datetime, timedelta
from pathlib import Path

import yaml

import _config  # noqa: E402  (proyecto.yaml con herencia de programa)

import _mediciones  # noqa: E402  (escritura segura de mediciones.csv)

FUENTE = "herramientas/evm_cpm.py"


def f(v):
    try:
        return datetime.strptime(str(v).strip()[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def num(v, d=None):
    try:
        return float(str(v).replace(",", ".").strip())
    except (TypeError, ValueError):
        return d


def leer(ruta):
    if not ruta.exists():
        return []
    with open(ruta, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def preds(t):
    return [x.strip() for x in (t.get("predecesoras") or "").replace(";", ",").split(",") if x.strip()]


def orden_topologico(tareas):
    ids = {t["id"] for t in tareas}
    visit, orden, en_curso = set(), [], set()

    def dfs(i):
        if i in visit:
            return
        if i in en_curso:
            raise SystemExit(f"Dependencia circular detectada en {i}.")
        en_curso.add(i)
        for p in preds(por_id[i]):
            if p in ids:
                dfs(p)
        en_curso.discard(i)
        visit.add(i)
        orden.append(i)

    por_id = {t["id"]: t for t in tareas}
    for t in tareas:
        dfs(t["id"])
    return orden, por_id


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("proyecto")
    ap.add_argument("--fecha")
    ap.add_argument("--registrar", action="store_true", help="guardar los resultados en metricas/mediciones.csv")
    ap.add_argument("--no-registrar", action="store_true", help="(obsoleto: ya es el comportamiento por defecto)")
    ap.add_argument("--salida")
    ap.add_argument("--cronograma", help="archivo de cronograma alternativo (por defecto cronograma/cronograma.csv)")
    a = ap.parse_args()
    raiz = Path(a.proyecto)
    hoy = f(a.fecha) if a.fecha else date.today()
    cfg = _config.cargar(raiz)
    lb = cfg.get("linea_base") or {}
    termino_ctto = f(lb.get("fecha_termino_vigente"))
    ruta_cron = Path(a.cronograma) if a.cronograma else raiz / "cronograma" / "cronograma.csv"
    tareas = [t for t in leer(ruta_cron) if f(t.get("inicio_plan")) and f(t.get("fin_plan"))]
    if not tareas:
        raise SystemExit("El cronograma no tiene tareas con fechas plan.")
    orden, por_id = orden_topologico(tareas)
    dur = {i: max((f(por_id[i]["fin_plan"]) - f(por_id[i]["inicio_plan"])).days, 0) for i in orden}

    # ---------- CPM sobre el plan ----------
    es, ef = {}, {}
    for i in orden:
        t = por_id[i]
        cand = [f(t["inicio_plan"])] + [ef[p] for p in preds(t) if p in ef]
        es[i] = max(cand)
        ef[i] = es[i] + timedelta(days=dur[i])
    fin_proy = max(ef.values())
    sucesores = {i: [j for j in orden if i in preds(por_id[j])] for i in orden}
    ls, lf = {}, {}
    for i in reversed(orden):
        lf[i] = min([ls[s] for s in sucesores[i]] or [fin_proy])
        ls[i] = lf[i] - timedelta(days=dur[i])
    holgura = {i: (ls[i] - es[i]).days for i in orden}
    criticas = [i for i in orden if holgura[i] <= 0]

    # ---------- Pronóstico con avance real ----------
    pes, pef = {}, {}
    for i in orden:
        t = por_id[i]
        av = (num(t.get("avance_pct"), 0) or 0) / 100
        fin_real, ini_real = f(t.get("fin_real")), f(t.get("inicio_real"))
        if av >= 1:
            pes[i] = ini_real or f(t["inicio_plan"])
            pef[i] = fin_real or f(t["fin_plan"])
        elif av > 0 or ini_real:
            pes[i] = ini_real or f(t["inicio_plan"])
            pef[i] = max(hoy, pes[i]) + timedelta(days=round(dur[i] * (1 - av)))
        else:
            pes[i] = max([f(t["inicio_plan"]), hoy] + [pef[p] for p in preds(t) if p in pef])
            pef[i] = pes[i] + timedelta(days=dur[i])
    fin_pron = max(pef.values())
    desvio = (fin_pron - termino_ctto).days if termino_ctto else None

    # ---------- EVM ----------
    con_costo = [t for t in tareas if num(t.get("costo_plan")) is not None]
    evm = {}
    if con_costo:
        bac = sum(num(t["costo_plan"]) for t in con_costo)
        pv = ev = ac = 0.0
        for t in con_costo:
            ini, fin = f(t["inicio_plan"]), f(t["fin_plan"])
            total = max((fin - ini).days, 1)
            plan = 0.0 if hoy < ini else 1.0 if hoy >= fin else (hoy - ini).days / total
            pv += num(t["costo_plan"]) * plan
            ev += num(t["costo_plan"]) * (num(t.get("avance_pct"), 0) or 0) / 100
            ac += num(t.get("costo_real"), 0) or 0
        evm = {"bac": bac, "pv": pv, "ev": ev, "ac": ac, "sv": ev - pv, "cv": ev - ac,
               "spi": ev / pv if pv else None, "cpi": ev / ac if ac else None}
        if evm["cpi"]:
            evm["eac"] = bac / evm["cpi"]
            evm["etc"] = evm["eac"] - ac
            evm["vac"] = bac - evm["eac"]
        evm["tcpi"] = (bac - ev) / (bac - ac) if bac != ac else None

    # ---------- Informe ----------
    m = lambda v: "—" if v is None else f"{v:,.0f}".replace(",", ".")
    r = lambda v: "—" if v is None else f"{v:.2f}"
    out = [f"# Valor ganado y ruta crítica — corte {hoy.isoformat()}", ""]
    if evm:
        interp_spi = "sin plan a la fecha" if evm["spi"] is None else ("adelantado" if evm["spi"] > 1.02 else "atrasado" if evm["spi"] < 0.98 else "en plan")
        interp_cpi = "sin costo real" if evm["cpi"] is None else ("bajo presupuesto" if evm["cpi"] > 1.02 else "sobre presupuesto" if evm["cpi"] < 0.98 else "en presupuesto")
        out += ["## Valor ganado", "", "| Indicador | Valor | Lectura |", "|---|---|---|",
                f"| Presupuesto total (BAC) | {m(evm['bac'])} | |",
                f"| Valor planificado (PV) | {m(evm['pv'])} | lo que debería estar hecho a la fecha |",
                f"| Valor ganado (EV) | {m(evm['ev'])} | lo realmente hecho, valorizado al presupuesto |",
                f"| Costo real (AC) | {m(evm['ac'])} | lo gastado |",
                f"| SPI (EV/PV) | {r(evm['spi'])} | {interp_spi} |",
                f"| CPI (EV/AC) | {r(evm['cpi'])} | {interp_cpi} |",
                f"| Costo estimado al término (EAC) | {m(evm.get('eac'))} | si se mantiene la eficiencia de costo actual |",
                f"| Desviación al término (VAC) | {m(evm.get('vac'))} | negativo = sobrecosto proyectado |",
                f"| TCPI | {r(evm.get('tcpi'))} | eficiencia necesaria en lo que queda para cumplir el presupuesto |", ""]
    else:
        out += ["## Valor ganado", "", "Sin costos por tarea: agregar las columnas `costo_plan` y `costo_real` al cronograma.", ""]
    out += ["## Plazo", "",
            f"- Término del plan (ruta crítica): {fin_proy}",
            f"- Término pronosticado con el avance real: {fin_pron}",
            f"- Término contractual vigente: {termino_ctto or 'no definido'}"
            + (f" → desviación pronosticada: {desvio:+d} días" if desvio is not None else ""), ""]
    cadena = " → ".join(f"{i}" for i in criticas)
    out += ["## Ruta crítica (plan)", "", f"{cadena or 'sin tareas críticas'}", "",
            "| Id | Tarea | Inicio temprano | Fin temprano | Inicio tardío | Holgura (días) | Pronóstico fin |",
            "|---|---|---|---|---|---|---|"]
    for i in orden:
        out.append(f"| {i}{' ★' if i in criticas else ''} | {por_id[i].get('tarea', '')} | {es[i]} | {ef[i]} | {ls[i]} | {holgura[i]} | {pef[i]} |")
    out += ["", "★ = tarea crítica (holgura 0): si se atrasa, se atrasa el proyecto."]
    texto = "\n".join(out) + "\n"

    if a.registrar and not a.no_registrar:
        med = [("holgura_minima_dias", min(holgura.values())), ("tareas_criticas", len(criticas))]
        if desvio is not None:
            med.append(("desvio_termino_dias", desvio))
        for k in ("pv", "ev", "ac", "spi", "cpi", "eac", "vac"):
            if evm.get(k) is not None:
                med.append((k, evm[k]))
        ruta = raiz / "metricas" / "mediciones.csv"
        ruta.parent.mkdir(exist_ok=True)
        nuevas = [{"fecha": hoy.isoformat(), "entidad": "PROYECTO", "metrica": k, "valor": f"{v:.10g}", "fuente": FUENTE, "comentario": ""} for k, v in med]
        _mediciones.registrar(ruta, nuevas, FUENTE, hoy.isoformat())
    else:
        texto += "\n(Resultados no registrados en metricas/mediciones.csv: usar --registrar para guardarlos.)\n"
    if a.salida:
        Path(a.salida).write_text(texto, encoding="utf-8")
    print(texto)


if __name__ == "__main__":
    import _consola
    _consola.preparar()
    main()
