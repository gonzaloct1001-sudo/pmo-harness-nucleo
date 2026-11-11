#!/usr/bin/env python3
"""Regresión: qué variables explican un resultado y cuánto, comprobado en datos que el modelo no vio.

Uso:
    python herramientas/experto.py regresion --datos ventas.csv --objetivo ventas [--variables precio,visitas]
        [--nivel auto|base|especialista] [--diagnosticar] [--proyecto proyectos/<slug>] [--id nombre] [--salida carpeta]
        [--json] [--abrir] [--semilla N] [--unidad "$"]

Los datos: un archivo .csv o .xlsx con una fila por observación y encabezados. Sin `--variables`, se usan todas las
columnas numéricas menos el objetivo; las columnas con texto se dejan fuera y se avisa cuáles; las filas con algún
dato faltante en las columnas usadas se descartan y se dice cuántas.

Dos niveles:
- base: cada variable por separado (recta, correlación, R²), probada en el 25 % de las filas que se separa al azar.
- especialista: todas las variables a la vez (mínimos cuadrados), con error, valor p e intervalo de cada una, aviso de
  variables que se mueven juntas y validación cruzada de 5 partes repetida 3 veces.
En los dos, una variable «explica» solo si el modelo mejora de verdad al promedio en datos que no vio.

`--diagnosticar` solo mira los datos y dice qué nivel conviene. Deja `informe.html`, `informe.md` y `resultado.json`
en `<proyecto>/analisis/<id>/` (o en `analisis-<id>/`, junto a los datos, si no hay proyecto).
"""
import argparse
import json
import math
import random
import re
import sys
import warnings
import webbrowser
from datetime import date
from pathlib import Path

import experto

SEMILLA = 20261111
MIN_OBS = 8
UMBRAL_MEJORA = 5.0     # % mínimo de mejora sobre «predecir el promedio» para decir que explica
VIF_ALTO = 5.0
CORRELACION_ALTA = 0.5  # dos variables explicativas «se mueven juntas» desde aquí (diagnóstico, sin bibliotecas)
OBS_POR_VARIABLE = 10
FRACCION_PRUEBA = 0.25
REPARTOS = 20           # separaciones al azar del nivel base: una sola dejaría el resultado a merced de qué filas tocaron
PARTES, REPETICIONES = 5, 3


class Problema(Exception):
    """Algo de los datos o de las opciones que impide analizar; el mensaje dice qué corregir."""


# ------------------------------------------------------------------------------------------ formato
def n(v, unidad=""):
    """Número como se escribe en Chile, con su unidad."""
    if v is None or (isinstance(v, float) and not math.isfinite(v)):
        return "sin dato"
    a = abs(v)
    if a == 0 or v == int(v):
        dec = 0
    elif a >= 100:
        dec = 0
    else:
        dec = min(6, max(1, 2 - int(math.floor(math.log10(a)))))
    t = f"{v:,.{dec}f}".replace(",", "§").replace(".", ",").replace("§", ".")
    if dec and "," in t:
        t = t.rstrip("0").rstrip(",")
    u = str(unidad or "").strip()
    return ("$ " + t) if u == "$" else t + ((" " + u) if u else "")


def pct(v):
    return "sin dato" if v is None else n(v) + " %"


def valor_p(p):
    if p is None:
        return "sin dato"
    return "menor que 0,001" if p < 0.001 else n(p)


def limpio(x):
    """Reemplaza lo que no es JSON válido (nan, inf) por None, hacia adentro."""
    if isinstance(x, float):
        return x if math.isfinite(x) else None
    if isinstance(x, dict):
        return {k: limpio(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [limpio(v) for v in x]
    return x


def cuantas(k):
    return "1 variable" if k == 1 else f"{k} variables"


def celda_md(t):
    return str(t).replace("|", "/").replace("\n", " ")


# ------------------------------------------------------------------------------------------ lectura
def _numero(v):
    """float, None si está vacío (o no es finito); lanza ValueError si es texto."""
    if v is None or isinstance(v, bool):
        if isinstance(v, bool):
            raise ValueError("lógico")
        return None
    if isinstance(v, (int, float)):
        x = float(v)
        return x if math.isfinite(x) else None
    s = str(v).strip()
    if not s:
        return None
    s = s.replace(" ", "").replace(" ", "")
    try:
        x = float(s)
        return x if math.isfinite(x) else None
    except ValueError:
        pass
    t = s.lstrip("$")
    if not re.fullmatch(r"-?[\d.,]+", t):
        raise ValueError("texto")
    neg = t.startswith("-")
    t = t.lstrip("-")
    if "," in t and "." in t:
        t = t.replace(".", "").replace(",", ".") if t.rfind(",") > t.rfind(".") else t.replace(",", "")
    elif "," in t:
        t = t.replace(",", ".") if t.count(",") == 1 and len(t.split(",")[-1]) <= 2 else t.replace(",", "")
    elif t.count(".") > 1:
        t = t.replace(".", "")
    try:
        x = float(t)
    except ValueError:
        raise ValueError("texto")
    return -x if neg else x


def leer_datos(ruta):
    """(encabezados, columnas {nombre: [celdas crudas]}) del archivo."""
    import finanzas
    ruta = Path(ruta)
    if not ruta.is_file():
        raise Problema(f"No existe {ruta.as_posix()}")
    if ruta.suffix.lower() not in (".csv", ".xlsx", ".xlsm"):
        raise Problema("--datos debe ser un archivo .csv o .xlsx")
    try:
        filas, _ = finanzas.leer_tabla(ruta)
    except ImportError:
        raise Problema("Para leer un .xlsx falta la biblioteca openpyxl; guarda los datos como .csv o instálala.")
    except Exception as e:
        raise Problema(f"No se pudo leer {ruta.name}: {str(e)[:120]}")
    filas = [f for f in filas if any(str(c).strip() for c in f)]
    if len(filas) < 2:
        raise Problema("El archivo no trae encabezados y datos (una fila por observación).")
    nombres, vistos = [], {}
    for i, c in enumerate(filas[0]):
        nom = str(c).strip() or f"columna_{i + 1}"
        vistos[nom] = vistos.get(nom, 0) + 1
        nombres.append(nom if vistos[nom] == 1 else f"{nom}_{vistos[nom]}")
    cols = {nom: [] for nom in nombres}
    for f in filas[1:]:
        f = list(f) + [""] * (len(nombres) - len(f))
        for nom, v in zip(nombres, f):
            cols[nom].append(v)
    return nombres, cols


def preparar(nombres, cols, objetivo, variables):
    """Deja solo columnas numéricas, sin filas con vacíos. Devuelve (datos, y, X)."""
    num, texto = {}, []
    for nom in nombres:
        try:
            vals = [_numero(v) for v in cols[nom]]
        except ValueError:
            texto.append(nom)
            continue
        if all(v is None for v in vals):
            texto.append(nom)
            continue
        num[nom] = vals
    if objetivo not in cols:
        raise Problema(f"No hay una columna «{objetivo}». Columnas: {', '.join(nombres)}.")
    if objetivo not in num:
        raise Problema(f"El objetivo «{objetivo}» no es numérico: no se puede explicar con una regresión.")
    excluidas, avisos = [], []
    if variables:
        pedidas = [v.strip() for v in variables.split(",") if v.strip()]
        for v in pedidas:
            if v not in cols:
                raise Problema(f"No hay una columna «{v}». Columnas: {', '.join(nombres)}.")
        pedidas = [v for v in dict.fromkeys(pedidas) if v != objetivo]
    else:
        pedidas = [c for c in nombres if c != objetivo]
    vars_ok = []
    for v in pedidas:
        if v in num:
            vars_ok.append(v)
        else:
            excluidas.append(v)
    if excluidas:
        avisos.append("Columnas no numéricas, fuera del análisis: " + ", ".join(excluidas) + ".")
    if not vars_ok:
        raise Problema("No quedan variables numéricas para explicar el objetivo.")
    usadas = [objetivo] + vars_ok
    total = len(cols[objetivo])
    buenas = [i for i in range(total) if all(num[c][i] is not None for c in usadas)]
    descartadas = total - len(buenas)
    if descartadas:
        avisos.append(f"Se descartaron {descartadas} de {total} filas por tener datos faltantes en las columnas usadas.")
    y = [num[objetivo][i] for i in buenas]
    X = {v: [num[v][i] for i in buenas] for v in vars_ok}
    if len(y) < MIN_OBS:
        raise Problema(f"Quedan {len(y)} observaciones útiles; se necesitan al menos {MIN_OBS} para que el resultado signifique algo.")
    if max(y) == min(y):
        raise Problema(f"El objetivo «{objetivo}» es constante: no hay nada que explicar.")
    for v in list(vars_ok):
        if max(X[v]) == min(X[v]):
            avisos.append(f"«{v}» es constante en estos datos: no puede explicar nada y se dejó fuera.")
            excluidas.append(v)
            vars_ok.remove(v)
            del X[v]
    if not vars_ok:
        raise Problema("Todas las variables son constantes: no hay nada con qué explicar el objetivo.")
    datos = {"observaciones": len(y), "descartadas": descartadas, "objetivo": objetivo, "variables": vars_ok, "excluidas": excluidas}
    return datos, y, X, avisos


# ------------------------------------------------------------------------------------------ diagnóstico
def diagnosticar(datos, X):
    k, no = len(datos["variables"]), datos["observaciones"]
    if k == 1:
        rec = experto.recomendacion(False, ["con una sola variable, una recta alcanza"])
    else:
        motivos = ["con varias variables hay que separar el efecto de cada una: mirada de a una, cada variable queda tapada por las demás"]
        nombres, par = list(X), None
        for i, a in enumerate(nombres):  # el par de variables explicativas que más se mueve junto
            for b in nombres[i + 1:]:
                r = _recta(X[a], X[b])
                if r and (par is None or abs(r["r"]) > abs(par[2])):
                    par = (a, b, r["r"])
        if par and abs(par[2]) >= CORRELACION_ALTA:
            motivos.append(f"«{par[0]}» y «{par[1]}» se mueven juntas (correlación {n(round(par[2], 2))}) y de a una sus efectos se confunden")
        rec = experto.recomendacion(True, motivos)
    aviso = poca_data(no, k)
    return rec, ([aviso] if aviso else [])


def poca_data(no, k):
    if no < OBS_POR_VARIABLE * k:
        return f"{no} observaciones para {k} variables: es poco; cualquier resultado es frágil."
    return None


# ------------------------------------------------------------------------------------------ nivel base
def _recta(xs, ys):
    m = len(xs)
    mx, my = sum(xs) / m, sum(ys) / m
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((v - my) ** 2 for v in ys)
    if sxx <= 0:
        return None
    sxy = sum((x - mx) * (v - my) for x, v in zip(xs, ys))
    b = sxy / sxx
    r = sxy / math.sqrt(sxx * syy) if syy > 0 else 0.0
    return {"pendiente": b, "intercepto": my - b * mx, "r": r, "r2": r * r}


def _mejora(mae_modelo, mae_prom):
    if mae_modelo is None or mae_prom is None or mae_prom <= 0:
        return None
    return (mae_prom - mae_modelo) / mae_prom * 100.0


def analizar_base(y, X, semilla):
    no = len(y)
    rng = random.Random(semilla)
    n_prueba = max(3, int(round(FRACCION_PRUEBA * no)))
    suma_prom, suma_mod, valida = 0.0, {nom: 0.0 for nom in X}, {nom: True for nom in X}
    for _ in range(REPARTOS):
        idx = list(range(no))
        rng.shuffle(idx)
        prueba, entre = idx[:n_prueba], idx[n_prueba:]
        y_ent = [y[i] for i in entre]
        prom = sum(y_ent) / len(y_ent)
        suma_prom += sum(abs(y[i] - prom) for i in prueba) / n_prueba
        for nom, xs in X.items():
            rt = _recta([xs[i] for i in entre], y_ent)
            if rt is None:  # la variable quedó constante en las filas de ajuste
                valida[nom] = False
                continue
            suma_mod[nom] += sum(abs(y[i] - (rt["intercepto"] + rt["pendiente"] * xs[i])) for i in prueba) / n_prueba
    mae_prom = suma_prom / REPARTOS
    filas = []
    for nom, xs in X.items():
        full = _recta(xs, y)
        mae_mod = (suma_mod[nom] / REPARTOS) if valida[nom] else None
        mej = _mejora(mae_mod, mae_prom)
        filas.append({"nombre": nom, "coeficiente": full["pendiente"], "intercepto": full["intercepto"], "error_estandar": None,
                      "p": None, "ic_bajo": None, "ic_alto": None, "estandarizado": full["r"], "vif": None,
                      "correlacion": full["r"], "r2_individual": full["r2"], "n": no, "mae_modelo": mae_mod,
                      "mejora_pct": mej, "explica": bool(mej is not None and mej >= UMBRAL_MEJORA),
                      "minimo": min(xs), "maximo": max(xs)})
    filas.sort(key=lambda f: -f["r2_individual"])
    explican = [f for f in filas if f["explica"]]
    mejor = explican[0] if explican else filas[0]
    adv = []
    if len(filas) > 1:
        adv.append("Miradas de a una: si dos variables se mueven juntas, sus efectos se confunden.")
    if len(filas) > 2:
        adv.append("Con varias variables probadas por separado, alguna puede salir bien por pura casualidad; por eso cuenta solo lo que mejora en datos no vistos.")
    if n_prueba < 10:
        adv.append(f"Cada comprobación usa solo {n_prueba} filas separadas: con tan pocas, el resultado es poco estable.")
    if explican:
        nombres = ", ".join(f["nombre"] for f in explican)
        conclusion = (f"{'Mejora' if len(explican) == 1 else 'Mejoran'} al promedio en datos no vistos: {nombres}. "
                      f"La mejor, «{mejor['nombre']}», explica {n(mejor['r2_individual'] * 100)} % de la variación y reduce el error en "
                      f"{n(mejor['mejora_pct'])} % frente a predecir siempre el promedio.")
    else:
        conclusion = "Ninguna variable predice mejor que el promedio: no hay evidencia de que estas variables expliquen el resultado."
    return {"nivel": "base", "variables": filas, "r2": mejor["r2_individual"], "r2_ajustado": None,
            "fuera_de_muestra": {"mae_modelo": mejor["mae_modelo"], "mae_promedio": mae_prom, "mejora_pct": mejor["mejora_pct"],
                                 "metodo": f"promedio de {REPARTOS} separaciones al azar, cada una con {no - n_prueba} filas para ajustar y "
                                           f"{n_prueba} para comprobar"},
            "mejor": mejor["nombre"], "destacadas": [f["nombre"] for f in explican], "atipicos": None,
            "conclusion": conclusion, "advertencias": adv, "funciona": bool(explican)}


# ------------------------------------------------------------------------------------------ nivel especialista
def analizar_especialista(y, X, semilla):
    import numpy as np
    import statsmodels.api as sm
    from sklearn.model_selection import RepeatedKFold
    from statsmodels.stats.outliers_influence import variance_inflation_factor
    nombres = list(X)
    k, no = len(nombres), len(y)
    if no <= k + 1:
        raise Problema(f"Hay {k} variables y {no} observaciones: se necesitan más observaciones que variables (al menos {k + 2}).")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        A = np.array([X[v] for v in nombres], dtype=float).T
        yy = np.array(y, dtype=float)
        con = sm.add_constant(A, has_constant="add")
        res = sm.OLS(yy, con).fit()
        ic = res.conf_int(alpha=0.05)
        sx, sy = A.std(axis=0, ddof=1), yy.std(ddof=1)
        vifs = []
        for j in range(k):
            if k == 1:
                vifs.append(1.0)
            else:
                try:
                    vifs.append(float(variance_inflation_factor(con, j + 1)))
                except Exception:
                    vifs.append(float("inf"))
        # validación cruzada repetida
        errores, errores_prom = [], []
        for ent, pru in RepeatedKFold(n_splits=PARTES, n_repeats=REPETICIONES, random_state=semilla).split(A):
            coef, *_ = np.linalg.lstsq(sm.add_constant(A[ent], has_constant="add"), yy[ent], rcond=None)
            pred = sm.add_constant(A[pru], has_constant="add") @ coef
            errores.extend(np.abs(yy[pru] - pred).tolist())
            errores_prom.extend(np.abs(yy[pru] - yy[ent].mean()).tolist())
        mae_mod, mae_prom = float(np.mean(errores)), float(np.mean(errores_prom))
        escala = float(res.scale)
        atipicos = int((np.abs(res.resid) > 3 * math.sqrt(escala)).sum()) if escala > 0 else 0
        r2, r2a = float(res.rsquared), float(res.rsquared_adj)
        filas = []
        for j, nom in enumerate(nombres):
            b = float(res.params[j + 1])
            r = _recta(X[nom], y)
            filas.append({"nombre": nom, "coeficiente": b, "intercepto": None, "error_estandar": float(res.bse[j + 1]),
                          "p": float(res.pvalues[j + 1]), "ic_bajo": float(ic[j + 1][0]), "ic_alto": float(ic[j + 1][1]),
                          "estandarizado": b * float(sx[j]) / float(sy), "vif": vifs[j], "correlacion": r["r"],
                          "r2_individual": r["r2"], "n": no, "mae_modelo": None, "mejora_pct": None, "explica": False,
                          "minimo": min(X[nom]), "maximo": max(X[nom])})
    mejora = _mejora(mae_mod, mae_prom)
    funciona = bool(mejora is not None and mejora >= UMBRAL_MEJORA)
    adv = []
    juntas = [f for f in filas if f["vif"] is None or not math.isfinite(f["vif"]) or f["vif"] > VIF_ALTO]
    if juntas:
        adv.append("Variables que se mueven juntas (factor de inflación de varianza mayor que 5): "
                   + ", ".join(f"{f['nombre']} ({n(f['vif'])})" if math.isfinite(f["vif"]) else f"{f['nombre']} (sin límite)" for f in juntas)
                   + ". El modelo completo puede servir, pero el peso de cada una por separado es poco fiable.")
    if atipicos:
        adv.append((f"{atipicos} observaciones se alejan" if atipicos > 1 else "1 observación se aleja")
                   + " más de 3 desviaciones de lo que dice el modelo (posibles atípicos): revisa si son datos erróneos o casos especiales.")
    filas.sort(key=lambda f: -abs(f["estandarizado"]))
    destacadas = []
    if funciona:
        mezcladas = {f["nombre"] for f in juntas}
        destacadas = [f["nombre"] for f in filas if f["p"] is not None and f["p"] < 0.05 and f["nombre"] not in mezcladas]
        for f in filas:
            f["explica"] = f["nombre"] in destacadas
        conclusion = (f"El modelo mejora al promedio en datos que no vio: reduce el error en {n(mejora)} % y explica {n(r2a * 100)} % de la "
                      f"variación (R² ajustado). ")
        if destacadas:
            conclusion += "Con efecto distinguible del azar (valor p menor que 0,05), de mayor a menor peso: " + ", ".join(destacadas) + "."
        else:
            conclusion += ("Ninguna variable se puede destacar sola: " + ("las que se mueven juntas no permiten separar su efecto." if mezcladas
                           else "ninguna tiene un efecto claramente distinguible del azar."))
    else:
        conclusion = ("El modelo no predice mejor que el promedio: no hay evidencia de que estas variables expliquen el resultado.")
    return {"nivel": "especialista", "variables": filas, "r2": r2, "r2_ajustado": r2a,
            "fuera_de_muestra": {"mae_modelo": mae_mod, "mae_promedio": mae_prom, "mejora_pct": mejora,
                                 "metodo": f"validación cruzada de {PARTES} partes repetida {REPETICIONES} veces"},
            "mejor": None, "destacadas": destacadas, "atipicos": atipicos, "conclusion": conclusion, "advertencias": adv,
            "funciona": funciona}


# ------------------------------------------------------------------------------------------ resultado
def resultado_json(r, datos, rec, avisos, semilla, hoy, unidad):
    advertencias = list(avisos) + list(r["advertencias"])
    poca = poca_data(datos["observaciones"], len(datos["variables"]))
    if poca:
        advertencias.append(poca)
    return limpio({
        "nivel": r["nivel"], "recomendacion": rec, "fecha": hoy.isoformat(),
        "datos": datos, "unidad": unidad,
        "variables": r["variables"], "r2": r["r2"], "r2_ajustado": r["r2_ajustado"],
        "fuera_de_muestra": r["fuera_de_muestra"], "atipicos": r["atipicos"], "destacadas": r["destacadas"],
        "conclusion": r["conclusion"], "advertencias": advertencias, "semilla": semilla})


def tabla_variables(res, unidad):
    esp = res["nivel"] == "especialista"
    if esp:
        cab = ["Variable", "Si sube, el resultado", "Coeficiente", "Error estándar", "Valor p", "Intervalo de 95 %", "Peso estandarizado", "VIF"]
        filas = []
        for v in res["variables"]:
            filas.append([v["nombre"], "sube" if v["coeficiente"] > 0 else ("baja" if v["coeficiente"] < 0 else "no cambia"),
                          n(v["coeficiente"]), n(v["error_estandar"]), valor_p(v["p"]),
                          f"{n(v['ic_bajo'])} a {n(v['ic_alto'])}", n(v["estandarizado"]), n(v["vif"]) if v["vif"] is not None else "sin límite"])
    else:
        cab = ["Variable", "Si sube, el resultado", "Pendiente", "Intercepto", "Correlación", "R²", "Datos", "Mejora en datos no vistos"]
        filas = []
        for v in res["variables"]:
            filas.append([v["nombre"], "sube" if v["coeficiente"] > 0 else ("baja" if v["coeficiente"] < 0 else "no cambia"),
                          n(v["coeficiente"]), n(v["intercepto"]), n(v["correlacion"]), n(v["r2_individual"]), n(v["n"]), pct(v["mejora_pct"])])
    o = ["| " + " | ".join(cab) + " |", "|" + "---|" * len(cab)]
    o += ["| " + " | ".join(celda_md(c) for c in f) + " |" for f in filas]
    return o


def consola(res, datos, rec, avisos, r, unidad):
    fo = r["fuera_de_muestra"]
    o = [f"# Qué explica «{datos['objetivo']}»", "",
         f"- Datos: {n(datos['observaciones'])} observaciones útiles"
         + (f" ({n(datos['descartadas'])} descartadas por datos faltantes)" if datos["descartadas"] else "")
         + f"; {cuantas(len(datos['variables']))}: {', '.join(datos['variables'])}.",
         f"- Conclusión: {r['conclusion']}", ""]
    o += tabla_variables(r, unidad)
    o += ["", f"- Comprobación fuera de muestra ({fo['metodo']}): error absoluto medio {n(fo['mae_modelo'], unidad)} contra "
          f"{n(fo['mae_promedio'], unidad)} de predecir el promedio; mejora {pct(fo['mejora_pct'])}."]
    if r["r2_ajustado"] is not None:
        o.append(f"- R² {n(r['r2'])}; R² ajustado {n(r['r2_ajustado'])}.")
    for a in res["advertencias"]:
        o.append(f"- Advertencia: {a}")
    o += experto.texto_recomendacion(rec, r["nivel"])
    return o


def informe_md(res, r, datos, unidad, semilla, hoy, rec):
    esp = r["nivel"] == "especialista"
    fo = r["fuera_de_muestra"]
    obj = datos["objetivo"]
    o = ["---", f"titulo: \"Qué explica «{obj.replace(chr(34), chr(39))}»\"",
         f"subtitulo: \"Regresión de nivel {r['nivel']} · {n(datos['observaciones'])} observaciones · semilla {semilla}\"",
         f"fecha: {hoy.isoformat()}", "---", "", f"> {r['conclusion']}", "", "```cifras",
         f"Observaciones: {n(datos['observaciones'])} | filas útiles" + (f", {n(datos['descartadas'])} descartadas" if datos["descartadas"] else ""),
         (f"R² ajustado: {n(r['r2_ajustado'] * 100)} % | parte de la variación que explica el modelo" if esp else
          f"R² de la mejor variable: {n(r['r2'] * 100)} % | parte de la variación que explica, de a una"),
         f"Mejora fuera de muestra: {pct(fo['mejora_pct'])} | menos error que predecir el promedio",
         f"Variables: {len(datos['variables'])} | en el análisis", "```", ""]
    if len(r["variables"]) >= 2:
        if esp:
            pesos = {v["nombre"]: round(abs(v["estandarizado"]), 4) for v in r["variables"]}
            titulo = "Peso de cada variable (coeficiente estandarizado, valor absoluto)"
        else:
            pesos = {v["nombre"]: round(v["r2_individual"], 4) for v in r["variables"]}
            titulo = "R² de cada variable, mirada de a una"
        o += ["# Cuánto pesa cada variable", "", "```grafico", "tipo: barras", f"titulo: {json.dumps(titulo, ensure_ascii=False)}",
              "datos: " + json.dumps(pesos, ensure_ascii=False), "```", ""]
        if not r["funciona"]:
            o += ["El modelo no mejora al promedio en datos nuevos: estos pesos describen estos datos, no deben leerse como explicación.", ""]
    o += ["# Detalle por variable", ""] + tabla_variables(r, unidad) + [""]
    o += ["# Comprobación en datos que el modelo no vio", "",
          f"- Método: {fo['metodo']}.",
          f"- Error absoluto medio del modelo: {n(fo['mae_modelo'], unidad)}.",
          f"- Error absoluto medio de predecir siempre el promedio: {n(fo['mae_promedio'], unidad)}.",
          f"- Mejora: {pct(fo['mejora_pct'])} (se exige al menos {n(UMBRAL_MEJORA)} % para decir que explica).", ""]
    if res["advertencias"]:
        o += ["# Advertencias", ""] + [f"- {a}" for a in res["advertencias"]] + [""]
    o += ["# Cómo leer esto", "",
          "- Una relación no es una causa: que dos cosas se muevan juntas no prueba que una produzca la otra.",
          "- Vale solo dentro del rango de datos observado; fuera de él, el resultado es una extrapolación sin respaldo. Rangos: "
          + "; ".join(f"{v['nombre']} de {n(v['minimo'])} a {n(v['maximo'])}" for v in r["variables"]) + ".",
          f"- Con pocos datos o muchas variables aparecen relaciones por azar ({n(datos['observaciones'])} observaciones, "
          f"{cuantas(len(datos['variables']))}): por eso se comprueba en datos que el modelo no vio.",
          "- Si las filas son meses seguidos, dos series que crecen con el tiempo parecen relacionadas aunque no lo estén: "
          "en ese caso compara los cambios de un mes a otro, no los niveles.",
          ("- El valor p es la probabilidad de ver una relación tan fuerte como esta si en realidad no hubiera ninguna; mientras más bajo, "
           "menos probable que sea casualidad." if esp else
           "- El nivel base no calcula valor p: la comprobación en filas separadas cumple su papel."),
          f"- Para repetir esta corrida: semilla {semilla}.", "- " + experto.nota_de_nivel(rec, r["nivel"]), ""]
    return "\n".join(o)


def proyecto_de(carpeta):
    for p in [carpeta] + list(carpeta.parents):
        if (p / "proyecto.yaml").exists():
            return p
    return None


def guardar(carpeta, res, r, datos, unidad, semilla, hoy, proyecto):
    import explicar
    carpeta.mkdir(parents=True, exist_ok=True)
    md = informe_md(res, r, datos, unidad, semilla, hoy, res["recomendacion"])
    (carpeta / "informe.md").write_text(md, encoding="utf-8")
    cfg = {}
    if proyecto:
        import _config
        cfg = _config.cargar(proyecto)
    try:
        pagina, _ = explicar.generar(md, carpeta, cfg, proyecto, hoy)
    except explicar.Problema as e:
        raise Problema(f"No se pudo armar la página del informe: {e}")
    (carpeta / "informe.html").write_text(pagina, encoding="utf-8")
    (carpeta / "resultado.json").write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return carpeta / "informe.html"


# ------------------------------------------------------------------------------------------ consola
def main(argv=None):
    ap = argparse.ArgumentParser(prog="experto.py regresion", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--datos", required=True, help="archivo .csv o .xlsx, una fila por observación, con encabezados")
    ap.add_argument("--objetivo", required=True, help="columna que se quiere explicar")
    ap.add_argument("--variables", help="columnas explicativas separadas por coma (por defecto, todas las numéricas menos el objetivo)")
    ap.add_argument("--nivel", default="auto", choices=["auto", "base", "especialista"], help="nivel del análisis (por defecto auto)")
    ap.add_argument("--diagnosticar", action="store_true", help="solo mirar los datos y recomendar un nivel")
    ap.add_argument("--proyecto", help="carpeta del proyecto donde dejar el análisis")
    ap.add_argument("--id", help="nombre corto del análisis (por defecto regresion-<hoy>)")
    ap.add_argument("--salida", help="carpeta de salida (por defecto <proyecto>/analisis/<id>/ o analisis-<id>/ junto a los datos)")
    ap.add_argument("--json", action="store_true", help="imprimir solo el JSON, sin escribir archivos")
    ap.add_argument("--abrir", action="store_true", help="abrir la página en el navegador")
    ap.add_argument("--hoy", help="fecha AAAA-MM-DD (pruebas)")
    ap.add_argument("--semilla", type=int, default=SEMILLA, help=f"semilla del azar (por defecto {SEMILLA})")
    ap.add_argument("--unidad", default="", help="unidad del objetivo, para los errores (por ejemplo \"$\" o \"kg\")")
    a = ap.parse_args(argv)
    try:
        hoy = date.fromisoformat(a.hoy) if a.hoy else date.today()
    except ValueError:
        print("--hoy debe ser AAAA-MM-DD", file=sys.stderr)
        return 1
    ident = a.id or f"regresion-{hoy.isoformat()}"
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", ident):
        print("--id: solo minúsculas, números y guiones (por ejemplo, ventas-2026)", file=sys.stderr)
        return 1
    proyecto = None
    if a.proyecto:
        proyecto = Path(a.proyecto)
        if not (proyecto / "proyecto.yaml").exists():
            print(f"{a.proyecto} no es un proyecto (falta proyecto.yaml)", file=sys.stderr)
            return 1
    nivel = None
    if not a.diagnosticar:
        nivel = experto.resolver_nivel(a.nivel)   # con código 3 si piden el especialista y no está
    try:
        nombres, cols = leer_datos(a.datos)
        datos, y, X, avisos = preparar(nombres, cols, a.objetivo.strip(), a.variables)
        rec, avisos_diag = diagnosticar(datos, X)
        if a.diagnosticar:
            if a.json:
                print(json.dumps(limpio({"recomendacion": rec, "datos": datos, "advertencias": avisos + avisos_diag}), ensure_ascii=False, indent=2))
            else:
                print(f"# Diagnóstico: qué explica «{datos['objetivo']}»\n")
                print(f"- Datos: {n(datos['observaciones'])} observaciones útiles, {cuantas(len(datos['variables']))}: {', '.join(datos['variables'])}.")
                for t in avisos + avisos_diag:
                    print(f"- Advertencia: {t}")
                print("\n".join(experto.texto_recomendacion(rec, None)))
            return 0
        r = analizar_especialista(y, X, a.semilla) if nivel == "especialista" else analizar_base(y, X, a.semilla)
        res = resultado_json(r, datos, rec, avisos, a.semilla, hoy, a.unidad)
        if a.json:
            print(json.dumps(res, ensure_ascii=False, indent=2))
            return 0
        if a.salida:
            carpeta = Path(a.salida)
        elif proyecto:
            carpeta = proyecto / "analisis" / ident
        else:
            carpeta = Path(a.datos).resolve().parent / f"analisis-{ident}"
        pagina = guardar(carpeta, res, r, datos, a.unidad, a.semilla, hoy, proyecto or proyecto_de(carpeta.resolve()))
    except Problema as e:
        print(f"No se pudo analizar: {e}", file=sys.stderr)
        return 1
    print("\n".join(consola(res, datos, rec, avisos, r, a.unidad)))
    print(f"\nPágina: {pagina.as_posix()}")
    if a.abrir:
        webbrowser.open(pagina.resolve().as_uri())
    return 0


if __name__ == "__main__":
    import _consola
    _consola.preparar()
    sys.exit(main())
