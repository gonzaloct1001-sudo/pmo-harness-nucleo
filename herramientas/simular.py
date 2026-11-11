#!/usr/bin/env python3
"""Simulación y sensibilidad: en vez de un solo número por supuesto, un rango; miles de escenarios; y la respuesta a
«¿qué tan probable es llegar a la meta?» y «¿qué variable pesa más?». Sin instalar nada (biblioteca estándar).

Uso:
    python herramientas/simular.py --modelos                                   # los modelos disponibles y sus entradas
    python herramientas/simular.py --nuevo <modelo> --proyecto proyectos/<slug> --id <nombre> [--pregunta "..."]
    python herramientas/simular.py <carpeta del análisis> [--revisar] [--corridas N] [--semilla S] [--abrir] [--json]
    python herramientas/simular.py <carpeta del análisis> --optimizar          # la mejor combinación de decisiones

Un análisis vive en `<proyecto>/analisis/<id>/analisis.yaml`:
    pregunta: "¿Conviene subir los precios 5 %?"
    modelo: precio-volumen             # uno de --modelos, o `formula` para uno propio
    resultado: cambio_margen_total     # cuál se analiza (por defecto, el principal del modelo)
    unidad: "%"                        # cómo se muestra el resultado ("%" lo multiplica por 100)
    meta: 0                            # opcional: se informa la probabilidad de cumplirla
    sentido: mayor                     # mayor (alcanzar o superar) | menor (quedar en o bajo)
    corridas: 5000
    semilla: 20261111                  # misma semilla, mismos resultados
    entradas:
      margen: 0.5                                                   # un valor fijo
      cambio_precio: 0.05
      perdida_volumen: {min: 0.02, probable: 0.08, max: 0.20, fuente: "ventas perdidas en el alza de 2025"}
Rangos: `{min, probable, max}` (triangular), `{min, max}` (uniforme), `{media, desv}` con `min` y `max` opcionales
(normal). `fuente` dice de dónde sale el rango; sin ella queda marcado como supuesto. Con `modelo: formula`:
    formula: "ventas * margen - gastos"          # o varios pasos: resultados: {bruto: "ventas * margen", neto: "bruto - gastos"}

Decisiones y optimización: una entrada que la empresa elige se escribe `{decision: true, min: 0, max: 0.10, paso: 0.01,
valor: 0.05}` (en una simulación normal vale `valor`). Una entrada que depende de otras se escribe con su fórmula,
`perdida_volumen: {formula: "sensibilidad * cambio_precio"}`, donde `sensibilidad` es otra entrada (con su rango): así
el modelo sabe qué frena una decisión. `--optimizar` prueba las combinaciones de decisiones (con los mismos escenarios
para todas) y entrega la mejor según `optimizar: {objetivo: media | p10 | p50 | p90 | probabilidad, sentido: maximizar |
minimizar, restricciones: ["cambio_precio <= 0.08"]}`; deja `optimizacion.html`, `.md` y `.json`. Si la mejor queda
en el borde de su rango, lo advierte: o el rango es estrecho, o al modelo le falta la relación que frena esa decisión.

Qué entrega (en la carpeta del análisis): `informe.html` (página con la probabilidad, el rango de resultados, el
histograma, el tornado y los supuestos), `informe.md`, `resultado.json` y una fila en `corridas.csv` (fecha, semilla y
cifras de cada corrida, para repetirla). Límites que la página declara: los supuestos se mueven de forma independiente
(no se modelan correlaciones) y el resultado vale lo que valgan los rangos.
"""
import argparse
import csv
import hashlib
import json
import math
import random
import re
import sys
import webbrowser
from datetime import date
from pathlib import Path

import _modelos
import experto

RAIZ = Path(__file__).resolve().parent.parent
ARCHIVO = "analisis.yaml"
CORRIDAS = 5000
INCIERTAS = ("triangular", "uniforme", "normal")
OBJETIVOS = ("media", "p10", "p50", "p90", "probabilidad")
MAX_COMBINACIONES = 3000


class Problema(Exception):
    """Algo de la definición que impide simular; el mensaje dice qué corregir."""


# ------------------------------------------------------------------------------------------- definición
def _num(v, donde):
    if isinstance(v, bool) or v is None:
        raise Problema(f"{donde}: falta un número")
    try:
        return float(str(v).replace(",", ".")) if not isinstance(v, (int, float)) else float(v)
    except ValueError:
        raise Problema(f"{donde}: «{v}» no es un número")


def entrada(nombre, crudo):
    """Una entrada como {forma, base, min, max, probable|media|desv, fuente}. forma: fijo, triangular, uniforme, normal."""
    donde = f"entrada «{nombre}»"
    if not isinstance(crudo, dict):
        return {"forma": "fijo", "base": _num(crudo, donde), "fuente": ""}
    fuente = str(crudo.get("fuente") or "").strip()
    if crudo.get("formula") is not None:
        return {"forma": "formula", "texto": str(crudo["formula"]), "base": None, "fuente": fuente}
    if crudo.get("decision"):
        if crudo.get("min") is None or crudo.get("max") is None:
            raise Problema(f"{donde}: una decisión lleva `min` y `max` (y `paso`)")
        lo, hi = _num(crudo["min"], donde), _num(crudo["max"], donde)
        if lo >= hi:
            raise Problema(f"{donde}: `min` debe ser menor que `max`")
        paso = _num(crudo["paso"], donde) if crudo.get("paso") is not None else (hi - lo) / 10
        if paso <= 0 or paso > hi - lo:
            raise Problema(f"{donde}: `paso` debe ser mayor que cero y caber en el rango")
        valor = _num(crudo["valor"], donde) if crudo.get("valor") is not None else lo
        if not lo <= valor <= hi:
            raise Problema(f"{donde}: `valor` debe quedar entre `min` y `max`")
        return {"forma": "decision", "base": valor, "min": lo, "max": hi, "paso": paso, "fuente": fuente}
    if "valor" in crudo:
        return {"forma": "fijo", "base": _num(crudo["valor"], donde), "fuente": fuente}
    if "media" in crudo:
        media, desv = _num(crudo["media"], donde), _num(crudo.get("desv"), donde + " (desv)")
        if desv <= 0:
            raise Problema(f"{donde}: `desv` debe ser mayor que cero")
        lo = _num(crudo["min"], donde) if crudo.get("min") is not None else None
        hi = _num(crudo["max"], donde) if crudo.get("max") is not None else None
        return {"forma": "normal", "base": media, "media": media, "desv": desv, "min": lo, "max": hi, "fuente": fuente}
    if crudo.get("min") is None or crudo.get("max") is None:
        raise Problema(f"{donde}: un rango lleva `min` y `max` (y `probable` si lo hay), o `media` y `desv`, o `valor`")
    lo, hi = _num(crudo["min"], donde), _num(crudo["max"], donde)
    if lo >= hi:
        raise Problema(f"{donde}: `min` debe ser menor que `max`")
    if crudo.get("probable") is None:
        return {"forma": "uniforme", "base": (lo + hi) / 2, "min": lo, "max": hi, "fuente": fuente}
    prob = _num(crudo["probable"], donde)
    if not lo <= prob <= hi:
        raise Problema(f"{donde}: `probable` debe quedar entre `min` y `max`")
    return {"forma": "triangular", "base": prob, "min": lo, "max": hi, "probable": prob, "fuente": fuente}


def preparar(definicion):
    """Plan listo para correr: {evaluar, entradas, resultado, etiquetas, notas, ...}. Lanza Problema si algo falta."""
    if not isinstance(definicion, dict):
        raise Problema(f"{ARCHIVO} debe ser una lista de claves (pregunta, modelo, entradas…)")
    modelo = str(definicion.get("modelo") or "").strip().lower()
    crudas = definicion.get("entradas")
    if not isinstance(crudas, dict) or not crudas:
        raise Problema("faltan las `entradas` (cada una con un valor fijo o un rango)")
    entradas = {str(k): entrada(str(k), v) for k, v in crudas.items()}
    primarias = [k for k, d in entradas.items() if d["forma"] != "formula"]
    calculadas, auxiliares = [], set()
    for k, d in entradas.items():
        if d["forma"] != "formula":
            continue
        try:
            codigo, usa = _modelos.compilar(d["texto"])
        except _modelos.FormulaInvalida as e:
            raise Problema(f"entrada «{k}»: {e}")
        faltan = [x for x in usa if x not in primarias]
        if faltan:
            raise Problema(f"entrada «{k}»: su fórmula usa {', '.join(faltan)}, que no es una entrada con valor, rango o decisión "
                           "(una entrada calculada no puede depender de otra calculada)")
        calculadas.append((k, codigo))
        auxiliares |= set(usa)
    if modelo == "formula":
        pasos = definicion.get("resultados") or ({"resultado": definicion["formula"]} if definicion.get("formula") else None)
        if not isinstance(pasos, dict) or not pasos:
            raise Problema("con `modelo: formula` falta `formula:` (o `resultados:` con varios pasos)")
        compilados, conocidos = [], set(entradas)
        for nombre, texto in pasos.items():
            try:
                codigo, usa = _modelos.compilar(texto)
            except _modelos.FormulaInvalida as e:
                raise Problema(str(e))
            faltan = [n for n in usa if n not in conocidos]
            if faltan:
                raise Problema(f"la fórmula de «{nombre}» usa {', '.join(faltan)}, que no está en las entradas ni en un paso anterior")
            compilados.append((str(nombre), codigo))
            conocidos.add(str(nombre))

        def evaluar(valores):
            v, salida = dict(valores), {}
            for nombre, codigo in compilados:
                salida[nombre] = _modelos.evaluar(codigo, v)
                if salida[nombre] is None:
                    return {x: None for x, _ in compilados}
                v[nombre] = salida[nombre]
            return salida
        resultados = {n: (n.replace("_", " ").capitalize(), "") for n, _ in compilados}
        principal, notas, titulo = compilados[-1][0], [], "Fórmula propia"
        etiquetas = {k: k.replace("_", " ").capitalize() for k in entradas}
    elif modelo in _modelos.MODELOS:
        m = _modelos.MODELOS[modelo]
        sobran = [k for k in entradas if k not in m["entradas"] and k not in auxiliares]
        if sobran:
            raise Problema(f"el modelo «{modelo}» no tiene la entrada {', '.join(sobran)}; las suyas son: {', '.join(m['entradas'])}")
        faltan = [k for k, d in m["entradas"].items() if not d["opcional"] and k not in entradas]
        if faltan:
            raise Problema(f"al modelo «{modelo}» le faltan entradas: {', '.join(faltan)}")
        evaluar, resultados, principal, notas, titulo = m["calcular"], m["resultados"], m["principal"], m["notas"], m["nombre"]
        etiquetas = {k: (m["entradas"][k]["que"] if k in m["entradas"] else k.replace("_", " ").capitalize()) for k in entradas}
    else:
        raise Problema("`modelo` debe ser uno de: " + ", ".join(list(_modelos.MODELOS) + ["formula"]))
    resultado = str(definicion.get("resultado") or principal)
    if resultado not in resultados:
        raise Problema(f"`resultado: {resultado}` no existe en este modelo; puede ser: {', '.join(resultados)}")
    nucleo = evaluar

    def evaluar(valores):  # primero las entradas calculadas (dependen de decisiones y supuestos), después el modelo
        v = dict(valores)
        for nombre, codigo in calculadas:
            v[nombre] = _modelos.evaluar(codigo, v)
            if v[nombre] is None:
                return {}
        return nucleo(v)
    valores_base = {k: entradas[k]["base"] for k in primarias}
    for nombre, codigo in calculadas:
        entradas[nombre]["base"] = _modelos.evaluar(codigo, valores_base)
    base = evaluar(valores_base).get(resultado)
    if base is None and resultado == principal and modelo in _modelos.MODELOS:
        otros = [k for k, v in evaluar(valores_base).items() if v is not None]
        raise Problema(f"con esas entradas el modelo no puede calcular «{resultado}» (falta una entrada opcional); "
                       f"sí puede: {', '.join(otros)}. Indica `resultado:` o completa las entradas")
    unidad = str(definicion.get("unidad") if definicion.get("unidad") is not None else
                 ("%" if resultados[resultado][1] == "fracción" else "")).strip()
    meta = _num(definicion["meta"], "meta") if definicion.get("meta") is not None else None
    return {"evaluar": evaluar, "entradas": entradas, "resultado": resultado, "que": resultados[resultado][0], "titulo": titulo,
            "modelo": modelo, "etiquetas": etiquetas, "notas": list(notas), "unidad": unidad,
            "escala": _num(definicion["escala"], "escala") if definicion.get("escala") is not None else (100.0 if unidad == "%" else 1.0),
            "meta": meta, "mayor": not str(definicion.get("sentido") or "mayor").strip().lower().startswith("men"),
            "corridas": int(definicion.get("corridas") or CORRIDAS), "semilla": int(definicion.get("semilla") or 0),
            "pregunta": str(definicion.get("pregunta") or "").strip(), "base": base,
            "optimizar": definicion.get("optimizar") if isinstance(definicion.get("optimizar"), dict) else {}}


# ------------------------------------------------------------------------------------------- simulación
def muestra(d, rng):
    if d["forma"] == "triangular":
        return rng.triangular(d["min"], d["max"], d["probable"])
    if d["forma"] == "uniforme":
        return rng.uniform(d["min"], d["max"])
    for _ in range(40):  # normal, recortada a sus límites si los tiene
        x = rng.gauss(d["media"], d["desv"])
        if (d["min"] is None or x >= d["min"]) and (d["max"] is None or x <= d["max"]):
            return x
    return min(max(x, d["min"] if d["min"] is not None else x), d["max"] if d["max"] is not None else x)


def percentil(ordenados, q):
    return ordenados[min(len(ordenados) - 1, max(0, int(q * len(ordenados))))]


def rangos(valores):
    """Posición de cada valor en el orden (promedio en los empates)."""
    orden = sorted(range(len(valores)), key=lambda i: valores[i])
    r, i = [0.0] * len(valores), 0
    while i < len(orden):
        j = i
        while j + 1 < len(orden) and valores[orden[j + 1]] == valores[orden[i]]:
            j += 1
        for k in range(i, j + 1):
            r[orden[k]] = (i + j) / 2.0
        i = j + 1
    return r


def correlacion_de_orden(xs, ys):
    rx, ry = rangos(xs), rangos(ys)
    n = len(xs)
    mx, my = sum(rx) / n, sum(ry) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    sx, sy = math.sqrt(sum((a - mx) ** 2 for a in rx)), math.sqrt(sum((b - my) ** 2 for b in ry))
    return sxy / (sx * sy) if sx and sy else 0.0


def alcanzar(plan, nombre):
    """Valor de una sola entrada que lleva el resultado a la meta con las demás en su valor más probable, o None."""
    d, base = plan["entradas"][nombre], {k: x["base"] for k, x in plan["entradas"].items() if x["forma"] != "formula"}
    lo, hi = (d["media"] - 4 * d["desv"], d["media"] + 4 * d["desv"]) if d["forma"] == "normal" else (d["min"], d["max"])
    ancho = hi - lo
    lo, hi = lo - 2 * ancho, hi + 2 * ancho

    def f(x):
        r = plan["evaluar"]({**base, nombre: x}).get(plan["resultado"])
        return None if r is None else r - plan["meta"]
    a, b = f(lo), f(hi)
    if a is None or b is None or a * b > 0:
        return None
    for _ in range(80):
        medio = (lo + hi) / 2
        m = f(medio)
        if m is None:
            return None
        if a * m <= 0:
            hi = medio
        else:
            lo, a = medio, m
    return (lo + hi) / 2


def simular(plan, corridas=None, semilla=None, decisiones=None, liviano=False):
    """Corre la simulación y devuelve cifras, sensibilidad y los valores simulados (ya en la escala en que se muestran).
    `decisiones` fija las entradas de decisión en esos valores (si no, usan su `valor`); `liviano` omite la sensibilidad."""
    corridas = int(corridas or plan["corridas"])
    semilla = int(semilla if semilla is not None else plan["semilla"])
    variables = [k for k, d in plan["entradas"].items() if d["forma"] in INCIERTAS]
    if not variables:
        corridas = 100  # sin incertidumbre todos los escenarios son iguales
    if corridas < 100:
        raise Problema("al menos 100 corridas para que la probabilidad signifique algo")
    rng = random.Random(semilla)
    fijos = {k: d["base"] for k, d in plan["entradas"].items() if d["forma"] != "formula"}
    fijos.update(decisiones or {})
    muestras, valores, escala = {k: [] for k in variables}, [], plan["escala"]
    for _ in range(corridas):
        e = dict(fijos)
        for k in variables:
            e[k] = muestra(plan["entradas"][k], rng)
            muestras[k].append(e[k])
        valores.append(plan["evaluar"](e).get(plan["resultado"]))
    validos = [i for i, v in enumerate(valores) if v is not None]
    if len(validos) < corridas * 0.5:
        raise Problema(f"en más de la mitad de los escenarios el modelo no puede calcular «{plan['resultado']}»: revisa los rangos")
    vs = sorted(valores[i] * escala for i in validos)
    r = {"corridas": corridas, "semilla": semilla, "sin_resultado": corridas - len(validos), "variables": variables,
         "base": plan["base"] * escala if plan["base"] is not None else None, "media": sum(vs) / len(vs),
         "p10": percentil(vs, 0.10), "p50": percentil(vs, 0.50), "p90": percentil(vs, 0.90), "minimo": vs[0], "maximo": vs[-1],
         "valores": vs, "probabilidad": None, "tornado": [], "pesos": {}, "alcanzar": {}}
    r["base"] = (lambda b: b * escala if b is not None else None)(plan["evaluar"](fijos).get(plan["resultado"]))
    if plan["meta"] is not None:
        meta = plan["meta"] * escala
        r["probabilidad"] = sum(1 for v in vs if (v >= meta if plan["mayor"] else v <= meta)) / len(vs)
    if liviano:
        return r
    ys = [valores[i] for i in validos]
    rho = {k: correlacion_de_orden([muestras[k][i] for i in validos], ys) for k in variables}
    total = sum(x * x for x in rho.values())
    r["pesos"] = {k: {"parte": (rho[k] ** 2 / total if total else 0.0), "sentido": "sube" if rho[k] >= 0 else "baja"} for k in variables}
    for k in variables:
        orden = sorted(muestras[k])
        bajo, alto = percentil(orden, 0.10), percentil(orden, 0.90)
        en = lambda x: plan["evaluar"]({**fijos, k: x}).get(plan["resultado"])  # noqa: E731
        rb, ra = en(bajo), en(alto)
        if rb is not None and ra is not None:
            r["tornado"].append({"entrada": k, "bajo": bajo, "alto": alto, "resultado_bajo": rb * escala, "resultado_alto": ra * escala})
        if plan["meta"] is not None:
            x = alcanzar(plan, k)
            d = plan["entradas"][k]
            dentro = x is not None and (d.get("min") is None or x >= d["min"]) and (d.get("max") is None or x <= d["max"])
            r["alcanzar"][k] = {"valor": x, "dentro_del_rango": bool(dentro)}
    r["tornado"].sort(key=lambda t: -abs(t["resultado_alto"] - t["resultado_bajo"]))
    return r


# ------------------------------------------------------------------------------------------- informe
def n(v, unidad=""):
    """Número como se escribe en Chile, con su unidad."""
    if v is None:
        return "sin dato"
    a = abs(v)
    dec = 0 if a >= 100 or v == int(v) else (1 if a >= 10 else (2 if a >= 1 else 3))
    t = f"{v:,.{dec}f}".replace(",", "§").replace(".", ",").replace("§", ".")
    if dec and "," in t:
        t = t.rstrip("0").rstrip(",")
    u = str(unidad or "").strip()
    return ("$ " + t) if u == "$" else t + ((" " + u) if u else "")


def describir(d):
    if d["forma"] == "fijo":
        return n(d["base"]), "valor fijo"
    if d["forma"] == "decision":
        return f"{n(d['base'])} (se puede elegir entre {n(d['min'])} y {n(d['max'])})", "decisión"
    if d["forma"] == "formula":
        return f"{d['texto']} (con los valores más probables: {n(d['base'])})", "se calcula"
    if d["forma"] == "triangular":
        return f"{n(d['min'])} a {n(d['max'])}, más probable {n(d['probable'])}", "triangular"
    if d["forma"] == "uniforme":
        return f"{n(d['min'])} a {n(d['max'])}", "uniforme (cualquier valor del rango por igual)"
    limites = "" if d["min"] is None and d["max"] is None else f", entre {n(d['min']) if d['min'] is not None else '…'} y {n(d['max']) if d['max'] is not None else '…'}"
    return f"media {n(d['media'])}, desviación {n(d['desv'])}{limites}", "normal"


def informe_md(plan, r, hoy):
    """El informe en el Markdown que entiende explicar.py."""
    u, et = plan["unidad"], plan["etiquetas"]
    corto = lambda k: k.replace("_", " ").capitalize()  # noqa: E731
    titulo = (plan["pregunta"] or f"{plan['titulo']}: {plan['que'].lower()}").replace('"', "'")
    mayor_peso = max(r["pesos"], key=lambda k: r["pesos"][k]["parte"]) if r["pesos"] else None
    if r["probabilidad"] is not None:
        clave = (f"Con estos supuestos, la probabilidad de que «{plan['que'].lower()}» "
                 f"{'alcance o supere' if plan['mayor'] else 'quede en o bajo'} {n(plan['meta'] * plan['escala'], u)} es de **{n(r['probabilidad'] * 100)} %**.")
    else:
        clave = (f"Con estos supuestos, «{plan['que'].lower()}» ronda **{n(r['p50'], u)}**; ocho de cada diez escenarios quedan entre "
                 f"{n(r['p10'], u)} y {n(r['p90'], u)}.")
    if mayor_peso and len(r["pesos"]) > 1:
        clave += f" Lo que más pesa es **{corto(mayor_peso).lower()}**: explica cerca del {n(r['pesos'][mayor_peso]['parte'] * 100)} % de la variación."
    o = ["---", f"titulo: \"{titulo}\"", f"subtitulo: \"{plan['titulo']} · {n(r['corridas'])} escenarios · semilla {r['semilla']}\"", f"fecha: {hoy.isoformat()}", "---", "",
         f"> {clave}", "", "```cifras"]
    if r["probabilidad"] is not None:
        o.append(f"Probabilidad de cumplir la meta: {n(r['probabilidad'] * 100)} % | meta: {n(plan['meta'] * plan['escala'], u)}")
    o += [f"Resultado central: {n(r['p50'], u)} | la mitad de los escenarios queda bajo este valor",
          f"Ocho de cada diez escenarios: {n(r['p10'], u)} a {n(r['p90'], u)} | entre el percentil 10 y el 90",
          f"Con los valores más probables: {n(r['base'], u)} | sin incertidumbre", "```", "", "# Qué tan probable es cada resultado", "",
          "```grafico", "tipo: histograma", f"titulo: \"{plan['que']} en {n(r['corridas'] - r['sin_resultado'])} escenarios\""]
    if u:
        o.append(f"unidad: \"{u}\"")
    if plan["meta"] is not None:
        o += [f"meta: {plan['meta'] * plan['escala']:.6g}", f"sentido: {'mayor' if plan['mayor'] else 'menor'}"]
    o += ["valores: [" + ", ".join(f"{v:.5g}" for v in r["valores"]) + "]", "```", ""]
    if len(r["tornado"]) >= 2 and r["base"] is not None:
        o += ["# Qué supuesto pesa más", "", "Cada barra muestra el resultado si ese supuesto toma un valor bajo o alto de su rango "
              "(percentiles 10 y 90) y los demás quedan en su valor más probable.", "", "```grafico", "tipo: tornado",
              f"titulo: \"{plan['que']} según cada supuesto\""] + ([f"unidad: \"{u}\""] if u else []) + [f"base: {r['base']:.6g}", "datos:"]
        o += [f"  \"{corto(t['entrada'])}\": [{t['resultado_bajo']:.6g}, {t['resultado_alto']:.6g}]" for t in r["tornado"]]
        o += ["```", "", "| Supuesto | Parte de la variación que explica | Si sube, el resultado |", "|---|---|---|"]
        o += [f"| {corto(k)} | {n(p['parte'] * 100)} % | {p['sentido']} |" for k, p in sorted(r["pesos"].items(), key=lambda x: -x[1]["parte"])]
        o.append("")
    elif len(r["tornado"]) == 1:
        t = r["tornado"][0]
        o += ["# Qué supuesto pesa más", "", f"Hay un solo supuesto con rango ({corto(t['entrada']).lower()}): con un valor bajo el resultado es "
              f"{n(t['resultado_bajo'], u)} y con uno alto, {n(t['resultado_alto'], u)}.", ""]
    if r["alcanzar"]:
        o += ["# Cuánto tendría que moverse cada supuesto, solo, para llegar a la meta", ""]
        for k, a in r["alcanzar"].items():
            if a["valor"] is None:
                o.append(f"- **{corto(k)}**: moviéndolo solo no se llega a la meta.")
            else:
                o.append(f"- **{corto(k)}**: tendría que valer {n(a['valor'])}"
                         + (" (dentro del rango que se le dio)." if a["dentro_del_rango"] else " (fuera del rango que se le dio)."))
        o.append("")
    con_que = any(et.get(k) and et[k] != corto(k) for k in plan["entradas"])  # en una fórmula propia el nombre ya lo dice todo
    o += ["# Los supuestos", "", "| Entrada | " + ("Qué es | " if con_que else "") + "Valor o rango | Forma | De dónde sale |",
          "|---|---|---|---|" + ("---|" if con_que else "")]
    sin_fuente = []
    for k, d in plan["entradas"].items():
        valor, forma = describir(d)
        if d["forma"] in INCIERTAS and not d["fuente"]:
            sin_fuente.append(corto(k))
        o.append(f"| {corto(k)} | " + (f"{et.get(k, '')} | " if con_que else "")
                 + f"{valor} | {forma} | {d['fuente'] or ('supuesto sin fuente' if d['forma'] in INCIERTAS else '')} |")
    o += ["", "# Cómo leer esto", ""]
    o += [f"- {x}" for x in plan["notas"]]
    if sin_fuente:
        o.append(f"- Rangos sin fuente declarada ({', '.join(sin_fuente)}): son supuestos; el resultado vale lo que valgan ellos.")
    if r["sin_resultado"]:
        o.append(f"- En {n(r['sin_resultado'])} escenarios el modelo no pudo calcular el resultado con esos valores; quedaron fuera.")
    o += ["- Los supuestos se mueven de forma independiente entre sí: si en la realidad dos de ellos se mueven juntos, el rango de resultados es más ancho.",
          "- Una simulación ordena la incertidumbre que se le entrega; no la reduce ni predice lo que no está en los supuestos.",
          f"- Para repetir exactamente esta corrida: {n(r['corridas'])} escenarios con la semilla {r['semilla']}.", ""]
    return "\n".join(o)


def rejilla(d):
    """Los valores que puede tomar una decisión: de `min` a `max` en pasos de `paso` (el `max` siempre incluido)."""
    cantidad = int(math.floor((d["max"] - d["min"]) / d["paso"] + 1e-9))
    valores = [round(d["min"] + i * d["paso"], 10) for i in range(cantidad + 1)]
    return valores if abs(valores[-1] - d["max"]) < 1e-9 else valores + [d["max"]]


def optimizar(plan, corridas=None, semilla=None):
    """Busca la combinación de decisiones que mejor cumple el objetivo, evaluando cada una con los mismos escenarios."""
    cfg = plan["optimizar"]
    decisiones = [k for k, d in plan["entradas"].items() if d["forma"] == "decision"]
    if not decisiones:
        raise Problema("no hay ninguna entrada de decisión (`{decision: true, min, max, paso}`): no hay nada que optimizar")
    objetivo = str(cfg.get("objetivo") or ("probabilidad" if plan["meta"] is not None else "media")).strip().lower()
    if objetivo not in OBJETIVOS:
        raise Problema("`optimizar.objetivo` debe ser uno de: " + ", ".join(OBJETIVOS))
    if objetivo == "probabilidad" and plan["meta"] is None:
        raise Problema("para optimizar la probabilidad hace falta una `meta`")
    maximizar = not str(cfg.get("sentido") or "maximizar").strip().lower().startswith("min")
    restricciones = []
    for texto in cfg.get("restricciones") or []:
        try:
            codigo, usa = _modelos.compilar(texto)
        except _modelos.FormulaInvalida as e:
            raise Problema(f"restricción: {e}")
        if [x for x in usa if x not in decisiones]:
            raise Problema(f"la restricción «{texto}» solo puede usar decisiones ({', '.join(decisiones)})")
        restricciones.append((str(texto), codigo))
    corridas = max(200, min(int(corridas or plan["corridas"]), 2000))
    semilla = int(semilla if semilla is not None else plan["semilla"])
    cumple = lambda c: all(_modelos.evaluar(codigo, c) for _, codigo in restricciones)  # noqa: E731

    def valor(c):
        r = simular(plan, corridas, semilla, decisiones=c, liviano=True)
        v = r[objetivo]
        return v * 100 if objetivo == "probabilidad" else v
    ejes = {k: rejilla(plan["entradas"][k]) for k in decisiones}
    total = 1
    for k in decisiones:
        total *= len(ejes[k])
    metodo, probadas = "todas las combinaciones", []
    if total <= MAX_COMBINACIONES:
        combos = [{}]
        for k in decisiones:
            combos = [{**c, k: x} for c in combos for x in ejes[k]]
        for c in combos:
            if cumple(c):
                try:
                    probadas.append((valor(c), c))
                except Problema:
                    continue
    elif experto.listo():
        from scipy.optimize import differential_evolution
        metodo = "búsqueda evolutiva (nivel especialista)"

        def ajustar(x):
            return {k: min(plan["entradas"][k]["max"], max(plan["entradas"][k]["min"], round(
                round((float(xi) - plan["entradas"][k]["min"]) / plan["entradas"][k]["paso"]) * plan["entradas"][k]["paso"] + plan["entradas"][k]["min"], 10)))
                for k, xi in zip(decisiones, x)}

        vistos = {}

        def costo(x):
            c = ajustar(x)
            clave = tuple(c[k] for k in decisiones)
            if clave not in vistos:
                try:
                    vistos[clave] = valor(c) if cumple(c) else None
                except Problema:
                    vistos[clave] = None
            v = vistos[clave]
            return 1e18 if v is None else (-v if maximizar else v)
        differential_evolution(costo, [(plan["entradas"][k]["min"], plan["entradas"][k]["max"]) for k in decisiones], seed=semilla,
                               maxiter=40, popsize=12, tol=1e-6, polish=False)
        probadas = [(v, dict(zip(decisiones, clave))) for clave, v in vistos.items() if v is not None]
    else:
        rec = experto.recomendacion(True, [f"hay {total:,} combinaciones de decisiones".replace(",", "."),
                                           "probarlas todas una por una tomaría demasiado; una búsqueda dirigida las recorre bien"])
        raise Problema("demasiadas combinaciones para probarlas todas (" + f"{total:,}".replace(",", ".") + f"; el límite es {MAX_COMBINACIONES}). "
                       "Agranda el `paso` de alguna decisión, o usa el nivel especialista.\n" + "\n".join(experto.texto_recomendacion(rec, None)))
    if not probadas:
        raise Problema("ninguna combinación de decisiones cumple las restricciones (o el modelo no pudo calcularlas)")
    probadas.sort(key=lambda x: -x[0] if maximizar else x[0])
    mejor_valor, mejor = probadas[0]
    actual = {k: plan["entradas"][k]["base"] for k in decisiones}
    tolerancia = 1.0 if objetivo == "probabilidad" else abs(mejor_valor) * 0.02
    en_borde = [k for k in decisiones if abs(mejor[k] - plan["entradas"][k]["min"]) < 1e-9 or abs(mejor[k] - plan["entradas"][k]["max"]) < 1e-9]
    return {"objetivo": objetivo, "maximizar": maximizar, "metodo": metodo, "decisiones": decisiones, "combinaciones": len(probadas),
            "corridas": corridas, "semilla": semilla, "mejor": mejor, "valor_mejor": mejor_valor, "actual": actual,
            "valor_actual": valor(actual) if cumple(actual) else None, "parecidas": sum(1 for v, _ in probadas if abs(v - mejor_valor) <= tolerancia),
            "en_borde": en_borde, "primeras": [{"valor": v, **c} for v, c in probadas[:10]],
            "curva": [(c[decisiones[0]], v) for v, c in sorted(probadas, key=lambda x: x[1][decisiones[0]])] if len(decisiones) == 1 else [],
            "restricciones": [texto for texto, _ in restricciones], "detalle_mejor": simular(plan, None, semilla, decisiones=mejor, liviano=True)}


def optimizacion_md(plan, o, hoy):
    """El resultado de la optimización en el Markdown que entiende explicar.py."""
    u = plan["unidad"]
    corto = lambda k: k.replace("_", " ").capitalize()  # noqa: E731
    nombres = {"media": "el promedio del resultado", "p10": "el resultado en un escenario malo (percentil 10)", "p50": "el resultado central",
               "p90": "el resultado en un escenario bueno (percentil 90)", "probabilidad": "la probabilidad de cumplir la meta"}
    uo = "%" if o["objetivo"] == "probabilidad" else u
    mejor_txt = ", ".join(f"{corto(k).lower()} = {n(v)}" for k, v in o["mejor"].items())
    titulo = (plan["pregunta"] or plan["titulo"]).replace('"', "'")
    lineas = ["---", f"titulo: \"La mejor decisión: {titulo}\"",
              f"subtitulo: \"{plan['titulo']} · {n(o['combinaciones'])} combinaciones probadas · {n(o['corridas'])} escenarios cada una · semilla {o['semilla']}\"",
              f"fecha: {hoy.isoformat()}", "---", "",
              f"> Para {'maximizar' if o['maximizar'] else 'minimizar'} {nombres[o['objetivo']]}, la mejor combinación es **{mejor_txt}**: da {n(o['valor_mejor'], uo)}"
              + (f", contra {n(o['valor_actual'], uo)} con la decisión de hoy." if o["valor_actual"] is not None else "."), "", "```cifras",
              f"Con la mejor combinación: {n(o['valor_mejor'], uo)} | {nombres[o['objetivo']]}"]
    if o["valor_actual"] is not None:
        lineas.append(f"Con la decisión de hoy: {n(o['valor_actual'], uo)} | " + ", ".join(f"{corto(k).lower()} = {n(v)}" for k, v in o["actual"].items()))
    d = o["detalle_mejor"]
    lineas += [f"Resultado central con la mejor: {n(d['p50'], u)} | ocho de cada diez escenarios entre {n(d['p10'], u)} y {n(d['p90'], u)}",
               f"Otras que dan casi lo mismo: {n(o['parecidas'] - 1)} | de {n(o['combinaciones'])} combinaciones probadas", "```", ""]
    if o["curva"]:
        k = o["decisiones"][0]
        lineas += ["# Cómo cambia el objetivo con la decisión", "", "```grafico", "tipo: lineas", f"titulo: \"{nombres[o['objetivo']].capitalize()} según {corto(k).lower()}\""]
        lineas += ([f"unidad: \"{uo}\""] if uo else []) + ["categorias: [" + ", ".join(f"\"{n(x)}\"" for x, _ in o["curva"]) + "]",
                                                             "series:", "  Objetivo: [" + ", ".join(f"{v:.6g}" for _, v in o["curva"]) + "]", "```", ""]
    lineas += ["# Las mejores combinaciones", "", "| " + " | ".join(corto(k) for k in o["decisiones"]) + f" | {nombres[o['objetivo']].capitalize()} |",
               "|" + "---|" * (len(o["decisiones"]) + 1)]
    lineas += ["| " + " | ".join(n(f[k]) for k in o["decisiones"]) + f" | {n(f['valor'], uo)} |" for f in o["primeras"]]
    lineas += ["", "# Cómo leer esto", ""]
    if o["en_borde"]:
        lineas.append("- **La mejor combinación queda en el borde del rango de " + ", ".join(corto(k).lower() for k in o["en_borde"])
                      + "**: o el rango permitido es estrecho, o al modelo le falta la relación que frena esa decisión (por ejemplo, que "
                        "subir el precio hace perder volumen). Revisa eso antes de decidir.")
    if o["parecidas"] > 1:
        lineas.append(f"- {n(o['parecidas'])} combinaciones (la mejor y {n(o['parecidas'] - 1)} más) dan prácticamente el mismo resultado: entre ellas "
                      "se puede elegir por otros criterios.")
    if o["restricciones"]:
        lineas.append("- Restricciones aplicadas: " + "; ".join(f"`{x}`" for x in o["restricciones"]) + ".")
    lineas += [f"- Método: {o['metodo']}; todas las combinaciones se compararon con los mismos {n(o['corridas'])} escenarios.",
               "- La optimización solo conoce lo que está en el modelo: una consecuencia que no esté escrita (reacción de la competencia, capacidad, "
               "plazos) no la ve. La decisión es de quien responde por ella.", ""]
    return "\n".join(lineas)


def guardar_optimizacion(carpeta, plan, o, hoy):
    import explicar
    md = optimizacion_md(plan, o, hoy)
    (carpeta / "optimizacion.md").write_text(md, encoding="utf-8")
    proyecto = proyecto_de(carpeta.resolve())
    cfg = {}
    if proyecto:
        import _config
        cfg = _config.cargar(proyecto)
    pagina, _ = explicar.generar(md, carpeta, cfg, proyecto, hoy)
    (carpeta / "optimizacion.html").write_text(pagina, encoding="utf-8")
    resumen = {k: v for k, v in o.items() if k != "detalle_mejor"}
    resumen["resultado_con_la_mejor"] = {k: o["detalle_mejor"][k] for k in ("media", "p10", "p50", "p90", "probabilidad")}
    resumen["fecha"] = hoy.isoformat()
    (carpeta / "optimizacion.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return carpeta / "optimizacion.html"


def proyecto_de(carpeta):
    """La carpeta del proyecto que contiene este análisis (la primera hacia arriba con proyecto.yaml), o None."""
    for p in [carpeta] + list(carpeta.parents):
        if (p / "proyecto.yaml").exists():
            return p
    return None


def guardar(carpeta, plan, r, hoy):
    """Escribe informe.md, informe.html, resultado.json y la fila de corridas.csv. Devuelve la ruta de la página."""
    import explicar
    md = informe_md(plan, r, hoy)
    (carpeta / "informe.md").write_text(md, encoding="utf-8")
    proyecto = proyecto_de(carpeta.resolve())
    cfg = {}
    if proyecto:
        import _config
        cfg = _config.cargar(proyecto)
    pagina, _ = explicar.generar(md, carpeta, cfg, proyecto, hoy)
    (carpeta / "informe.html").write_text(pagina, encoding="utf-8")
    resumen = {k: v for k, v in r.items() if k != "valores"}
    resumen.update(fecha=hoy.isoformat(), modelo=plan["modelo"], resultado=plan["resultado"], unidad=plan["unidad"],
                   meta=plan["meta"] * plan["escala"] if plan["meta"] is not None else None, sentido="mayor" if plan["mayor"] else "menor",
                   entradas={k: {x: y for x, y in d.items() if y is not None} for k, d in plan["entradas"].items()})
    (carpeta / "resultado.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    registro = carpeta / "corridas.csv"
    nuevo = not registro.exists()
    huella = hashlib.sha256((carpeta / ARCHIVO).read_bytes()).hexdigest()[:10] if (carpeta / ARCHIVO).exists() else ""
    with open(registro, "a", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        if nuevo:
            w.writerow(["fecha", "corridas", "semilla", "base", "media", "p10", "p50", "p90", "probabilidad", "definicion"])
        w.writerow([hoy.isoformat(), r["corridas"], r["semilla"]] + [f"{r[k]:.6g}" if r[k] is not None else "" for k in ("base", "media", "p10", "p50", "p90", "probabilidad")] + [huella])
    return carpeta / "informe.html"


# ------------------------------------------------------------------------------------------- consola
def listar_modelos():
    o = ["# Modelos disponibles", "", "Además, `modelo: formula` para uno propio (`formula:` con las entradas que definas).", ""]
    for clave, m in _modelos.MODELOS.items():
        o += [f"## {clave} — {m['nombre']}", m["para_que"], "", "Entradas:"]
        o += [f"- `{k}`{' (opcional)' if d['opcional'] else ''}: {d['que']} [{d['unidad']}]" for k, d in m["entradas"].items()]
        o += ["Resultados:"] + [f"- `{k}`{' (principal)' if k == m['principal'] else ''}: {que} [{un}]" for k, (que, un) in m["resultados"].items()]
        o.append("")
    return "\n".join(o)


def plantilla(modelo, pregunta, hoy):
    o = [f"pregunta: \"{pregunta or 'PENDIENTE: la pregunta que se quiere responder'}\"", f"modelo: {modelo}"]
    if modelo == "formula":
        o += ["formula: \"ventas * margen - gastos\"      # o varios pasos: resultados: {bruto: \"ventas * margen\", neto: \"bruto - gastos\"}",
              "# unidad: \"$\"", "# meta: 0                               # opcional: se informa la probabilidad de cumplirla",
              "# sentido: mayor                        # mayor | menor", f"corridas: {CORRIDAS}", f"semilla: {hoy:%Y%m%d}", "entradas:",
              "  ventas: {min: 0, probable: 0, max: 0, fuente: \"\"}     # PENDIENTE: rango y de dónde sale",
              "  margen: 0.0                                             # un valor fijo", "  gastos: 0"]
        return "\n".join(o) + "\n"
    m = _modelos.MODELOS[modelo]
    o += [f"resultado: {m['principal']}          # puede ser: {', '.join(m['resultados'])}",
          "# meta: 0                               # opcional: se informa la probabilidad de cumplirla",
          "# sentido: mayor                        # mayor (alcanzar o superar) | menor (quedar en o bajo)", f"corridas: {CORRIDAS}",
          f"semilla: {hoy:%Y%m%d}                      # misma semilla, mismos resultados",
          "entradas:                               # un valor fijo, o un rango {min, probable, max, fuente} para lo incierto"]
    for k, d in m["entradas"].items():
        o.append(f"  {'# ' if d['opcional'] else ''}{k}:                    # {d['que']} [{d['unidad']}]")
    return "\n".join(o) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("carpeta", nargs="?", help="carpeta del análisis (la que tiene analisis.yaml)")
    ap.add_argument("--modelos", action="store_true", help="listar los modelos y sus entradas")
    ap.add_argument("--nuevo", metavar="MODELO", help="crear un análisis nuevo con ese modelo")
    ap.add_argument("--proyecto", help="proyecto donde crear el análisis (con --nuevo)")
    ap.add_argument("--id", help="nombre corto del análisis, sin espacios (con --nuevo)")
    ap.add_argument("--pregunta", default="", help="la pregunta que responde (con --nuevo)")
    ap.add_argument("--revisar", action="store_true", help="solo revisar la definición, sin simular")
    ap.add_argument("--optimizar", action="store_true", help="buscar la mejor combinación de las entradas de decisión")
    ap.add_argument("--corridas", type=int, help="cantidad de escenarios (por defecto, la de la definición)")
    ap.add_argument("--semilla", type=int, help="semilla (por defecto, la de la definición)")
    ap.add_argument("--abrir", action="store_true", help="abrir la página en el navegador")
    ap.add_argument("--json", action="store_true", help="imprimir las cifras en JSON")
    ap.add_argument("--hoy", help="fecha AAAA-MM-DD (pruebas)")
    a = ap.parse_args()
    hoy = date.fromisoformat(a.hoy) if a.hoy else date.today()
    if a.modelos:
        print(listar_modelos())
        return 0
    if a.nuevo:
        modelo = a.nuevo.strip().lower()
        if modelo != "formula" and modelo not in _modelos.MODELOS:
            sys.exit("Ese modelo no existe. Disponibles: " + ", ".join(list(_modelos.MODELOS) + ["formula"]))
        if not a.proyecto or not a.id or not (Path(a.proyecto) / "proyecto.yaml").exists():
            sys.exit("--nuevo necesita --proyecto <carpeta de un proyecto> y --id <nombre-corto>")
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", a.id):
            sys.exit("--id: solo minúsculas, números y guiones (por ejemplo, alza-precios-2027)")
        carpeta = Path(a.proyecto) / "analisis" / a.id
        if (carpeta / ARCHIVO).exists():
            sys.exit(f"Ya existe {(carpeta / ARCHIVO).as_posix()}: edítalo, o elige otro --id")
        carpeta.mkdir(parents=True, exist_ok=True)
        (carpeta / ARCHIVO).write_text(plantilla(modelo, a.pregunta, hoy), encoding="utf-8")
        print(f"Análisis creado: {(carpeta / ARCHIVO).as_posix()}\nCompleta las entradas (un valor fijo, o un rango con su fuente para lo "
              f"incierto) y ejecuta: python herramientas/simular.py {carpeta.as_posix()}")
        return 0
    if not a.carpeta:
        ap.error("indica la carpeta del análisis, o usa --modelos o --nuevo")
    carpeta = Path(a.carpeta)
    if not (carpeta / ARCHIVO).exists():
        sys.exit(f"No existe {(carpeta / ARCHIVO).as_posix()} (se crea con --nuevo)")
    import yaml
    try:
        texto = (carpeta / ARCHIVO).read_text(encoding="utf-8")
        if any("PENDIENTE" in linea.split("#")[0] for linea in texto.splitlines()):
            raise Problema("la definición todavía tiene PENDIENTE: completa la pregunta y las entradas")
        plan = preparar(yaml.safe_load(texto))
        if a.revisar:
            variables = [k for k, d in plan["entradas"].items() if d["forma"] in INCIERTAS]
            decisiones = [k for k, d in plan["entradas"].items() if d["forma"] == "decision"]
            print(f"Definición correcta: modelo {plan['modelo']}, resultado «{plan['resultado']}», supuestos con rango: "
                  f"{', '.join(variables) or 'ninguno'}" + (f"; decisiones: {', '.join(decisiones)}" if decisiones else "")
                  + f". Con los valores más probables: {n(plan['base'] * plan['escala'] if plan['base'] is not None else None, plan['unidad'])}.")
            return 0
        if a.optimizar:
            o = optimizar(plan, a.corridas, a.semilla)
            pagina = guardar_optimizacion(carpeta, plan, o, hoy)
            if a.json:
                print((carpeta / "optimizacion.json").read_text(encoding="utf-8"))
                return 0
            uo = "%" if o["objetivo"] == "probabilidad" else plan["unidad"]
            print(f"# La mejor decisión: {plan['pregunta'] or plan['titulo']}\n")
            print("- Mejor combinación: " + ", ".join(f"{k} = {n(v)}" for k, v in o["mejor"].items()) + f" → {o['objetivo']} {n(o['valor_mejor'], uo)}"
                  + (f" (hoy: {n(o['valor_actual'], uo)})" if o["valor_actual"] is not None else ""))
            print(f"- {n(o['combinaciones'])} combinaciones probadas con {n(o['corridas'])} escenarios cada una ({o['metodo']})"
                  + (f"; {n(o['parecidas'])} dan casi lo mismo que la mejor" if o["parecidas"] > 1 else "; ninguna otra da casi lo mismo"))
            if o["en_borde"]:
                print("- ATENCIÓN: la mejor queda en el borde del rango de " + ", ".join(o["en_borde"]) + ": revisa si al modelo le falta lo que frena esa decisión")
            print(f"\nPágina: {pagina.as_posix()}")
            if a.abrir:
                webbrowser.open(pagina.resolve().as_uri())
            return 0
        if not any(d["forma"] in INCIERTAS for d in plan["entradas"].values()):
            raise Problema("ninguna entrada tiene rango: sin incertidumbre no hay nada que simular (dale a lo incierto `{min, probable, max}`)")
        r = simular(plan, a.corridas, a.semilla)
        pagina = guardar(carpeta, plan, r, hoy)
    except yaml.YAMLError as e:
        sys.exit(f"No se pudo simular: {ARCHIVO} no se puede leer ({str(e).splitlines()[0]})")
    except Problema as e:
        sys.exit(f"No se pudo simular: {e}")
    if a.json:
        print((carpeta / "resultado.json").read_text(encoding="utf-8"))
        return 0
    u = plan["unidad"]
    print(f"# {plan['pregunta'] or plan['titulo']}\n")
    if r["probabilidad"] is not None:
        print(f"- Probabilidad de {'alcanzar o superar' if plan['mayor'] else 'quedar en o bajo'} {n(plan['meta'] * plan['escala'], u)}: {n(r['probabilidad'] * 100)} %")
    print(f"- {plan['que']}: central {n(r['p50'], u)} · ocho de cada diez escenarios entre {n(r['p10'], u)} y {n(r['p90'], u)} · con los valores más probables {n(r['base'], u)}")
    for k, p in sorted(r["pesos"].items(), key=lambda x: -x[1]["parte"])[:3]:
        print(f"- Pesa {n(p['parte'] * 100)} %: {k} (si sube, el resultado {p['sentido']})")
    print(f"- {n(r['corridas'])} escenarios, semilla {r['semilla']}" + (f" · {n(r['sin_resultado'])} sin resultado" if r["sin_resultado"] else ""))
    print(f"\nPágina: {pagina.as_posix()}")
    if a.abrir:
        webbrowser.open(pagina.resolve().as_uri())
    return 0


if __name__ == "__main__":
    import _consola
    _consola.preparar()
    sys.exit(main())
