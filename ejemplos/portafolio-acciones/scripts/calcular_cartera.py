#!/usr/bin/env python3
"""Calcula las métricas de la cartera y las registra en metricas/mediciones.csv.

Script PROPIO de este proyecto (no es parte del núcleo del harness).

Uso:
    python scripts/calcular_cartera.py <ruta-proyecto> [--fecha AAAA-MM-DD]

Lee datos/transacciones.csv, datos/precios.csv, datos/fundamentos.csv, datos/parametros.yaml e
items/items.csv. La fecha de corte por defecto es la última fecha de precios disponible.

Métricas por acción: peso, valor_mercado, rentabilidad (vs costo promedio), retorno_12m,
volatilidad_12m, drawdown_max_12m, roe, pu, deuda_ebitda, dividend_yield.
Métricas de cartera: valor_cartera, n_posiciones, peso_max_accion, peso_max_sector,
retorno_cartera_12m, retorno_benchmark_12m, exceso_retorno_12m, volatilidad_cartera_12m,
drawdown_cartera_12m, sharpe_12m.

Método de rentabilidad de la cartera: retorno ponderado por tiempo con datos mensuales. Las compras y
ventas se consideran flujos al cierre del mes en que ocurren: r_t = (V_t − F_t) / V_(t−1) − 1,
donde V es el valor de mercado y F el flujo neto invertido en el mes.
Volatilidad anualizada = desviación estándar de retornos mensuales × √12.
Sharpe = (retorno de la ventana − tasa libre de riesgo) / volatilidad (ventana de 12 meses).
Si se ejecuta de nuevo para la misma fecha, reemplaza las mediciones de esa fecha generadas por este script.
"""
import argparse
import csv
import math
import statistics
from collections import defaultdict
from pathlib import Path

import yaml

FUENTE = "scripts/calcular_cartera.py"


def leer(ruta):
    with open(ruta, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def retornos(serie):
    return [serie[i] / serie[i - 1] - 1 for i in range(1, len(serie)) if serie[i - 1]]


def drawdown_max(serie):
    pico, peor = None, 0.0
    for v in serie:
        pico = v if pico is None else max(pico, v)
        if pico:
            peor = min(peor, v / pico - 1)
    return -peor  # magnitud positiva: 0,25 = caída de 25% desde el máximo


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("proyecto")
    ap.add_argument("--fecha")
    a = ap.parse_args()
    raiz = Path(a.proyecto)
    par = yaml.safe_load((raiz / "datos" / "parametros.yaml").read_text(encoding="utf-8"))
    bench, rf, ventana = par["benchmark"], float(par["tasa_libre_riesgo_anual"]), int(par["ventana_meses"])

    precios = defaultdict(dict)  # ticker -> {fecha: cierre}
    for r in leer(raiz / "datos" / "precios.csv"):
        precios[r["ticker"]][r["fecha"]] = float(r["cierre"])
    fechas = sorted({f for t in precios.values() for f in t})
    corte = a.fecha or fechas[-1]
    fechas = [f for f in fechas if f <= corte]
    if corte not in fechas:
        raise SystemExit(f"No hay precios para la fecha de corte {corte}.")
    win = fechas[-(ventana + 1):]

    tx = sorted(leer(raiz / "datos" / "transacciones.csv"), key=lambda r: r["fecha"])
    items = {r["id"]: r for r in leer(raiz / "items" / "items.csv")}

    # Posiciones, costo promedio y flujos por fecha
    cantidad, costo = defaultdict(float), defaultdict(float)
    flujos = defaultdict(float)
    tenencia = {}  # fecha -> {ticker: cantidad}
    i = 0
    for f in fechas:
        while i < len(tx) and tx[i]["fecha"] <= f:
            r = tx[i]
            q, p, c = float(r["cantidad"]), float(r["precio"]), float(r.get("comision") or 0)
            t = r["ticker"]
            if r["operacion"].strip().lower() == "compra":
                costo[t] += q * p + c
                cantidad[t] += q
                flujos[f] += q * p + c
            else:
                if cantidad[t]:
                    costo[t] -= costo[t] * q / cantidad[t]
                cantidad[t] -= q
                flujos[f] -= q * p - c
            i += 1
        tenencia[f] = {t: q for t, q in cantidad.items() if q > 1e-9}

    valor = {f: sum(q * precios[t].get(f, 0) for t, q in tenencia[f].items()) for f in fechas}
    r_cart = []
    for k in range(1, len(win)):
        v0, v1 = valor[win[k - 1]], valor[win[k]]
        if v0 > 0:
            r_cart.append((v1 - flujos[win[k]]) / v0 - 1)
    indice = [1.0]
    for r in r_cart:
        indice.append(indice[-1] * (1 + r))
    ret_cart = indice[-1] - 1
    vol_cart = statistics.stdev(r_cart) * math.sqrt(12) if len(r_cart) > 1 else None
    b = [precios[bench][f] for f in win if f in precios[bench]]
    ret_bench = b[-1] / b[0] - 1 if len(b) > 1 else None

    total = valor[corte]
    pesos = {t: q * precios[t][corte] / total for t, q in tenencia[corte].items()} if total else {}
    sectores = defaultdict(float)
    for t, w in pesos.items():
        sectores[(items.get(t) or {}).get("categoria", "Sin sector")] += w

    med = []  # (entidad, metrica, valor, comentario)
    for t, q in tenencia[corte].items():
        vm = q * precios[t][corte]
        med += [(t, "peso", pesos[t], ""), (t, "valor_mercado", vm, ""),
                (t, "rentabilidad", vm / costo[t] - 1 if costo[t] else None, "vs costo promedio")]
    fund = {}
    for r in leer(raiz / "datos" / "fundamentos.csv"):
        if r["fecha"] <= corte and (r["ticker"] not in fund or r["fecha"] >= fund[r["ticker"]]["fecha"]):
            fund[r["ticker"]] = r
    for t, it in items.items():
        if it.get("etapa") == "retirado" or t not in precios:
            continue
        serie = [precios[t][f] for f in win if f in precios[t]]
        if len(serie) > 1:
            rs = retornos(serie)
            med += [(t, "retorno_12m", serie[-1] / serie[0] - 1, ""),
                    (t, "volatilidad_12m", statistics.stdev(rs) * math.sqrt(12) if len(rs) > 1 else None, ""),
                    (t, "drawdown_max_12m", drawdown_max(serie), "")]
        if t in fund:
            for m in ("roe", "pu", "deuda_ebitda", "dividend_yield"):
                if fund[t].get(m, "").strip():
                    med.append((t, m, float(fund[t][m]), f"estados al {fund[t]['fecha']}"))
    sector_max = max(sectores.items(), key=lambda x: x[1]) if sectores else ("", 0)
    med += [("PROYECTO", "valor_cartera", total, ""), ("PROYECTO", "n_posiciones", len(pesos), ""),
            ("PROYECTO", "peso_max_accion", max(pesos.values()) if pesos else None, max(pesos, key=pesos.get) if pesos else ""),
            ("PROYECTO", "peso_max_sector", sector_max[1], sector_max[0]),
            ("PROYECTO", "retorno_cartera_12m", ret_cart, f"TWR mensual {win[0]} a {win[-1]}"),
            ("PROYECTO", "retorno_benchmark_12m", ret_bench, bench),
            ("PROYECTO", "exceso_retorno_12m", ret_cart - ret_bench if ret_bench is not None else None, ""),
            ("PROYECTO", "volatilidad_cartera_12m", vol_cart, ""),
            ("PROYECTO", "drawdown_cartera_12m", drawdown_max(indice), ""),
            ("PROYECTO", "sharpe_12m", (ret_cart - rf) / vol_cart if vol_cart else None, f"rf {rf:.1%}")]

    ruta_med = raiz / "metricas" / "mediciones.csv"
    existentes = leer(ruta_med) if ruta_med.exists() else []
    existentes = [r for r in existentes if not (r["fecha"] == corte and r.get("fuente") == FUENTE)]
    nuevas = [{"fecha": corte, "entidad": e, "metrica": m, "valor": f"{v:.10g}", "fuente": FUENTE, "comentario": c}
              for e, m, v, c in med if v is not None]
    with open(ruta_med, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["fecha", "entidad", "metrica", "valor", "fuente", "comentario"])
        w.writeheader()
        w.writerows(sorted(existentes + nuevas, key=lambda r: (r["fecha"], r["entidad"], r["metrica"])))

    print(f"Corte {corte}: valor cartera {total:,.0f} CLP · {len(pesos)} posiciones".replace(",", "."))
    print(f"Retorno 12m cartera {ret_cart:.1%} vs {bench} {ret_bench:.1%} · volatilidad {vol_cart:.1%}")
    print("Pesos: " + ", ".join(f"{t} {w:.1%}" for t, w in sorted(pesos.items(), key=lambda x: -x[1])))
    print("Sectores: " + ", ".join(f"{s} {w:.1%}" for s, w in sorted(sectores.items(), key=lambda x: -x[1])))
    print(f"{len(nuevas)} mediciones registradas en {ruta_med}")


if __name__ == "__main__":
    main()
