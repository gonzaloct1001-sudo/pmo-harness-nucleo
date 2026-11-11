#!/usr/bin/env python3
"""Grupos de clientes según cómo compran (se llama con `python herramientas/experto.py segmentar <proyecto>`).

Por cliente se calcula, sobre las ventas del período: recencia (días desde su última compra hasta `hasta`), frecuencia
(documentos distintos), monto (Σ cantidad × precio) y margen (monto − Σ cantidad × costo, si hay costos).
Los clientes van siempre por identificador (C-0001…): el nombre vive solo en finanzas/_local/clientes-mapa.csv.

Dos niveles (`--nivel auto | base | especialista`):
- base (biblioteca estándar): grupos por reglas. Puntaje de 1 a 3 por tercil en recencia, frecuencia y monto, y cinco
  grupos con nombres fijos y orden de prioridad.
- especialista (scikit-learn): grupos por datos, formados con recencia, frecuencia y monto (k-medias, k de 2 a 6 y
  nunca más de clientes ÷ 10, elegido por silueta; el margen se informa por grupo, no los forma), con dos comprobaciones: que haya grupos de verdad (contra datos con cada columna desordenada) y que sean
  estables (20 remuestreos, índice de Rand ajustado). Si falla una, la conclusión lo dice y se entregan los grupos por
  reglas.

Los grupos describen el período analizado y no predicen. Un grupo no dice por qué un cliente compra o deja de comprar.

Entrega, en <proyecto>/analisis/<id>/: informe.md, informe.html y resultado.json. Con --con-nombres (solo si existe el
mapa local) los archivos quedan en <proyecto>/finanzas/_local/<id>/ y no se suben. Con --json solo se imprime el JSON.
`--diagnosticar` mira los datos y dice qué nivel conviene, sin analizar. Código 1: datos insuficientes o argumentos mal
puestos; 3: se pidió el nivel especialista y no está instalado.
"""
import argparse
import json
import math
import statistics
import sys
import webbrowser
from datetime import date
from pathlib import Path

import experto
import rentabilidad as rent

MIN_CLIENTES = 6
UMBRAL_ESPECIALISTA = 30
K_MIN, K_MAX = 2, 6
REPETICIONES = 20
UMBRAL_ESTABILIDAD = 0.6
SEMILLA = 20261111
PROPORCION_CONCENTRACION = 0.5
MAX_CLIENTES_TABLA = 30

G_FRECUENTES = "Frecuentes y recientes"
G_ALEJANDO = "Se están alejando"
G_GRANDES = "Grandes y esporádicos"
G_NUEVOS = "Nuevos o de una vez"
G_HABITUALES = "Habituales"
GRUPOS_REGLAS = [
    (G_FRECUENTES, "compran seguido y compraron hace poco"),
    (G_ALEJANDO, "compraban seguido o con montos altos y dejaron de comprar"),
    (G_GRANDES, "pocas compras, de monto alto"),
    (G_NUEVOS, "una sola compra, reciente o intermedia"),
    (G_HABITUALES, "el resto: compras regulares sin rasgo extremo"),
]
DESCRIPCION_REGLAS = dict(GRUPOS_REGLAS)

NOTAS_LECTURA = [
    "Los grupos describen el período analizado: no predicen lo que hará cada cliente.",
    "Un grupo no dice por qué un cliente compra o deja de comprar; para eso hay que conversar con él.",
    "Con pocos clientes los cortes son orientación: un cliente de más o de menos puede cambiar un grupo.",
    "Las decisiones sobre un cliente son de la empresa; estos grupos son un insumo para esa conversación.",
]
MOTIVO_BASE = "con menos de 30 clientes los grupos por datos no son estables: reglas simples alcanzan"


def motivo_especialista(n):
    return f"con {n} clientes se pueden buscar grupos que las reglas fijas no ven, y comprobar si son estables"


# ------------------------------------------------------------------------------------------------ datos
def leer_clientes(proyecto, desde=None, hasta=None):
    """(clientes, info). Cada cliente: cliente_id, recencia, frecuencia, monto, margen (None sin costos). info: lineas,
    desde, hasta, hay_costos, sin_costo."""
    filas = rent.leer_filas(rent.carpeta_datos(proyecto) / "ventas.csv")[1]
    lineas = []
    for f in filas:
        fecha = rent.fecha_de(f.get("fecha"))
        cant, precio = rent.num_csv(f.get("cantidad")), rent.num_csv(f.get("precio_unitario"))
        cid = f.get("cliente_id", "")
        if fecha is None or cant is None or precio is None or not cid:
            continue
        if (desde and fecha < desde) or (hasta and fecha > hasta):
            continue
        doc = f.get("documento", "") or ("f:" + fecha.isoformat())
        lineas.append((fecha, doc, cid, cant * precio, rent.num_csv(f.get("costo_unitario")), cant))
    info = {"lineas": len(lineas), "desde": None, "hasta": None, "hay_costos": False, "sin_costo": 0}
    if not lineas:
        return [], info
    info["desde"] = min(l[0] for l in lineas)
    info["hasta"] = hasta or max(l[0] for l in lineas)
    info["hay_costos"] = any(l[4] is not None for l in lineas)
    info["sin_costo"] = sum(1 for l in lineas if l[4] is None) if info["hay_costos"] else 0
    por = {}
    for fecha, doc, cid, venta, costo, cant in lineas:
        c = por.setdefault(cid, {"cliente_id": cid, "ultima": fecha, "docs": set(), "monto": 0.0, "costo": 0.0})
        c["ultima"] = max(c["ultima"], fecha)
        c["docs"].add(doc)
        c["monto"] += venta
        c["costo"] += cant * (costo or 0.0)
    clientes = []
    for cid in sorted(por):
        c = por[cid]
        clientes.append({"cliente_id": cid, "recencia": (info["hasta"] - c["ultima"]).days, "frecuencia": len(c["docs"]),
                         "monto": c["monto"], "margen": (c["monto"] - c["costo"]) if info["hay_costos"] else None})
    return clientes, info


# ------------------------------------------------------------------------------------------------ nivel base
def tercil(valores, v):
    """Puntaje 1 a 3 de v entre `valores` (mayor valor = mayor puntaje; los empates quedan en el mismo tercil)."""
    n = len(valores)
    debajo = sum(1 for x in valores if x < v)
    if 3 * debajo < n:
        return 1
    if 3 * debajo < 2 * n:
        return 2
    return 3


def grupo_por_reglas(pr, pf, pm):
    if pr == 3 and pf == 3:
        return G_FRECUENTES
    if pr == 1 and (pf >= 2 or pm >= 2):
        return G_ALEJANDO
    if pm == 3 and pf <= 2:
        return G_GRANDES
    if pf == 1 and pr >= 2:
        return G_NUEVOS
    return G_HABITUALES


def asignar_reglas(clientes):
    """Agrega a cada cliente p_recencia, p_frecuencia, p_monto y grupo_reglas."""
    rec = [-c["recencia"] for c in clientes]
    frec = [c["frecuencia"] for c in clientes]
    mon = [c["monto"] for c in clientes]
    for c in clientes:
        c["p_recencia"] = tercil(rec, -c["recencia"])
        c["p_frecuencia"] = tercil(frec, c["frecuencia"])
        c["p_monto"] = tercil(mon, c["monto"])
        c["grupo_reglas"] = grupo_por_reglas(c["p_recencia"], c["p_frecuencia"], c["p_monto"])


# ------------------------------------------------------------------------------------------------ resumen de grupos
def resumen_grupos(clientes, clave, nombres, descripciones, hay_costos):
    ventas_t = sum(c["monto"] for c in clientes)
    margen_t = sum(c["margen"] for c in clientes) if hay_costos else None
    grupos = []
    for nombre in nombres:
        m = [c for c in clientes if c[clave] == nombre]
        if not m:
            continue
        ventas = sum(c["monto"] for c in m)
        margen = sum(c["margen"] for c in m) if hay_costos else None
        grupos.append({"nombre": nombre, "descripcion": descripciones.get(nombre, ""), "clientes": len(m),
                       "pct_clientes": len(m) / len(clientes), "ventas": ventas,
                       "pct_ventas": ventas / ventas_t if ventas_t else None, "margen": margen,
                       "pct_margen": (margen / margen_t) if (hay_costos and margen_t) else None,
                       "recencia_mediana": statistics.median(c["recencia"] for c in m),
                       "frecuencia_mediana": statistics.median(c["frecuencia"] for c in m),
                       "monto_mediano": statistics.median(c["monto"] for c in m)})
    return grupos


def descripcion_automatica(g, glob):
    """Texto corto comparando las medianas del grupo con las generales."""
    partes = []
    r, r0 = g["recencia_mediana"] + 1, glob["recencia"] + 1
    if r <= r0 * 0.7:
        partes.append("recientes")
    elif r >= r0 * 1.4:
        partes.append("sin comprar hace tiempo")
    verbo = "compraban" if partes == ["sin comprar hace tiempo"] else "compran"
    if g["frecuencia_mediana"] >= glob["frecuencia"] * 1.25 and g["frecuencia_mediana"] > glob["frecuencia"]:
        partes.append(f"{verbo} seguido")
    elif g["frecuencia_mediana"] <= glob["frecuencia"] * 0.8 and g["frecuencia_mediana"] < glob["frecuencia"]:
        partes.append(f"{verbo} poco")
    if g["monto_mediano"] >= glob["monto"] * 1.25:
        partes.append("montos altos")
    elif g["monto_mediano"] <= glob["monto"] * 0.8:
        partes.append("montos bajos")
    return ", ".join(partes) if partes else "cerca del comportamiento general"


# ------------------------------------------------------------------------------------------------ nivel especialista
def analizar_especialista(clientes, hay_costos, semilla):
    """Agrupa con k-medias y hace las dos comprobaciones. Devuelve {etiquetas, k, silueta, p95, estabilidad, hay_grupos,
    estable, advertencias, fallo}. `fallo` es None si no hubo problema técnico; si no se pudo buscar, k es None."""
    import warnings
    n = len(clientes)
    kmax = min(K_MAX, n // 10)
    salida = {"etiquetas": None, "k": None, "silueta": None, "p95": None, "estabilidad": None, "hay_grupos": False,
              "estable": False, "advertencias": [], "kmax": kmax}
    if kmax < K_MIN:
        return salida
    import numpy as np
    from sklearn.cluster import KMeans
    from sklearn.metrics import adjusted_rand_score, silhouette_score

    with warnings.catch_warnings(record=True) as capturadas:
        warnings.simplefilter("always")
        cols = [[c["recencia"] for c in clientes],
                [math.log1p(c["frecuencia"]) for c in clientes],
                [math.log1p(max(c["monto"], 0.0)) for c in clientes]]
        X = np.array(cols, dtype=float).T
        sd = X.std(axis=0)
        sd[sd == 0] = 1.0
        X = (X - X.mean(axis=0)) / sd

        def ajustar(M, k):
            return KMeans(n_clusters=k, n_init=10, random_state=semilla).fit(M)

        def mejor(M):
            res = None
            for k in range(K_MIN, kmax + 1):
                etq = ajustar(M, k).labels_
                if len(set(etq)) < 2:
                    continue
                s = float(silhouette_score(M, etq))
                if res is None or s > res[1] + 1e-12:
                    res = (k, s, etq)
            return res

        real = mejor(X)
        if real is not None:
            k, silueta, etq = real
            rng = np.random.default_rng(semilla)
            azar = []
            for _ in range(REPETICIONES):
                Xd = np.column_stack([rng.permutation(X[:, j]) for j in range(X.shape[1])])
                r = mejor(Xd)
                azar.append(r[1] if r is not None else -1.0)
            p95 = float(np.percentile(azar, 95))
            rng2 = np.random.default_rng(semilla + 1)
            aris = []
            for _ in range(REPETICIONES):
                idx = rng2.integers(0, n, n)
                comunes = np.unique(idx)
                if len(comunes) <= k:
                    continue
                modelo = ajustar(X[idx], k)
                aris.append(float(adjusted_rand_score(etq[comunes], modelo.predict(X[comunes]))))
            estab = float(np.mean(aris)) if aris else None
            salida.update(etiquetas=[int(e) for e in etq], k=k, silueta=silueta, p95=p95, estabilidad=estab,
                          hay_grupos=silueta > p95, estable=(estab is not None and estab >= UMBRAL_ESTABILIDAD))
    vistos = []
    for w in capturadas:
        t = " ".join(str(w.message).split())[:160]
        if t and t not in vistos:
            vistos.append(t)
    salida["advertencias"] = ["Aviso de las bibliotecas: " + t for t in vistos]
    return salida


def nombrar_grupos_datos(clientes, etiquetas):
    """Etiquetas numéricas → «Grupo 1…k» ordenados por ventas (el mayor, primero). Asigna c['grupo_datos']."""
    ventas = {}
    for c, e in zip(clientes, etiquetas):
        ventas[e] = ventas.get(e, 0.0) + c["monto"]
    orden = sorted(ventas, key=lambda e: (-ventas[e], e))
    nombre = {e: f"Grupo {i + 1}" for i, e in enumerate(orden)}
    for c, e in zip(clientes, etiquetas):
        c["grupo_datos"] = nombre[e]
    return [nombre[e] for e in orden]


# ------------------------------------------------------------------------------------------------ conclusión
def concentracion(clientes):
    """(clientes necesarios para llegar al 50 % de las ventas, su parte de las ventas). Los de mayor monto primero."""
    total = sum(c["monto"] for c in clientes)
    if total <= 0:
        return 0, 0.0
    acum, n = 0.0, 0
    for c in sorted(clientes, key=lambda c: (-c["monto"], c["cliente_id"])):
        acum += c["monto"]
        n += 1
        if acum >= PROPORCION_CONCENTRACION * total:
            break
    return n, acum / total


def frase_concentracion(clientes):
    n, parte = concentracion(clientes)
    if not n:
        return ""
    return f"El {rent.miles(n / len(clientes) * 100, 0)} % de los clientes ({n}) concentra el {rent.miles(parte * 100, 0)} % de las ventas"


def frase_alejando(clientes):
    n = sum(1 for c in clientes if c["grupo_reglas"] == G_ALEJANDO and c["p_frecuencia"] >= 2)
    if not n:
        return ""
    return (f"{n} cliente que compraba seguido se está alejando" if n == 1
            else f"{n} clientes que compraban seguido se están alejando")


def armar_conclusion(clientes, esp):
    """Una frase (o dos) con lo principal."""
    conc, alej = frase_concentracion(clientes), frase_alejando(clientes)
    cola = "; ".join(p for p in (conc, alej) if p)
    if esp is None:
        return (cola + ".") if cola else "Grupos por reglas entregados."
    if esp["k"] is None:
        cabeza = (f"Con {len(clientes)} clientes no alcanza para comprobar grupos por datos (se necesitan al menos "
                  f"{K_MIN * 10}): se entregan los grupos por reglas")
    elif not esp["hay_grupos"]:
        cabeza = ("No se ven grupos naturales en estos datos: la separación no supera la de datos desordenados al azar. "
                  "Se recomienda usar los grupos por reglas, que se entregan igual")
    elif not esp["estable"]:
        cabeza = ("Los grupos cambian mucho al mover un poco los datos: no son estables. "
                  "Se recomienda usar los grupos por reglas, que se entregan igual")
    else:
        cabeza = f"Se distinguen {esp['k']} grupos de clientes y son estables al mover los datos"
    return cabeza + (". " + cola + "." if cola else ".")


# ------------------------------------------------------------------------------------------------ construcción del resultado
def analizar(clientes, info, nivel, rec, semilla, hoy):
    """Todo el análisis (con identificadores). `nivel` es el nivel realmente usado."""
    hay_costos = info["hay_costos"]
    asignar_reglas(clientes)
    adv = []
    if info["sin_costo"]:
        adv.append((f"{info['sin_costo']} líneas de venta con costo en blanco: se trataron" if info["sin_costo"] > 1 else
                    "1 línea de venta con costo en blanco: se trató") + " como costo 0.")
    if len(clientes) < UMBRAL_ESPECIALISTA:
        adv.append(f"Con {len(clientes)} clientes los cortes por tercil son orientación: un cliente de más o de menos puede cambiar un grupo.")
    nombres_reglas = [g for g, _ in GRUPOS_REGLAS]
    grupos_reglas = resumen_grupos(clientes, "grupo_reglas", nombres_reglas, DESCRIPCION_REGLAS, hay_costos)
    esp = None
    comp = {"silueta": None, "silueta_desordenada_p95": None, "estabilidad": None, "k": None}
    metodo, cruce = "reglas", None
    grupos = grupos_reglas
    for c in clientes:
        c["grupo"] = c["grupo_reglas"]
    if nivel == "especialista":
        esp = analizar_especialista(clientes, hay_costos, semilla)
        adv.extend(esp["advertencias"])
        comp = {"silueta": esp["silueta"], "silueta_desordenada_p95": esp["p95"], "estabilidad": esp["estabilidad"], "k": esp["k"]}
        if esp["k"] is not None and esp["hay_grupos"] and esp["estable"]:
            metodo = "datos"
            orden = nombrar_grupos_datos(clientes, esp["etiquetas"])
            glob = {"recencia": statistics.median(c["recencia"] for c in clientes),
                    "frecuencia": statistics.median(c["frecuencia"] for c in clientes),
                    "monto": statistics.median(c["monto"] for c in clientes)}
            grupos = resumen_grupos(clientes, "grupo_datos", orden, {}, hay_costos)
            for g in grupos:
                g["descripcion"] = descripcion_automatica(g, glob)
            for c in clientes:
                c["grupo"] = c["grupo_datos"]
            cruce = {"filas": orden, "columnas": [g["nombre"] for g in grupos_reglas],
                     "valores": [[sum(1 for c in clientes if c["grupo_datos"] == f and c["grupo_reglas"] == col)
                                  for col in [g["nombre"] for g in grupos_reglas]] for f in orden]}
    conclusion = armar_conclusion(clientes, esp)
    return {"nivel": nivel, "recomendacion": rec,
            "datos": {"clientes": len(clientes), "desde": info["desde"].isoformat(), "hasta": info["hasta"].isoformat(),
                      "lineas": info["lineas"]},
            "metodo_grupos": metodo, "grupos": grupos, "grupos_reglas": grupos_reglas, "tabla_cruzada": cruce,
            "clientes": [{"cliente_id": c["cliente_id"], "recencia": c["recencia"], "frecuencia": c["frecuencia"],
                          "monto": c["monto"], "margen": c["margen"], "grupo": c["grupo"], "grupo_reglas": c["grupo_reglas"]}
                         for c in sorted(clientes, key=lambda c: c["cliente_id"])],
            "comprobaciones": comp if nivel == "especialista" else {k: None for k in comp},
            "conclusion": conclusion, "advertencias": adv, "semilla": semilla, "hay_costos": hay_costos}


def redondear(x, d=2):
    return None if x is None else round(float(x), d)


def para_json(res, etq=None):
    """Copia del resultado lista para JSON (números redondeados; fracciones sin multiplicar por 100)."""
    def grupo(g):
        o = dict(g)
        for k in ("ventas", "margen", "monto_mediano", "recencia_mediana", "frecuencia_mediana"):
            o[k] = redondear(o[k])
        for k in ("pct_clientes", "pct_ventas", "pct_margen"):
            o[k] = redondear(o[k], 6)
        return o
    sal = dict(res)
    sal["grupos"] = [grupo(g) for g in res["grupos"]]
    sal["grupos_reglas"] = [grupo(g) for g in res["grupos_reglas"]]
    cl = []
    for c in res["clientes"]:
        o = dict(c, monto=redondear(c["monto"]), margen=redondear(c["margen"]))
        if etq:
            o["cliente"] = etq(c["cliente_id"])
        cl.append(o)
    sal["clientes"] = cl
    comp = dict(res["comprobaciones"])
    for k in ("silueta", "silueta_desordenada_p95", "estabilidad"):
        comp[k] = redondear(comp[k], 4)
    sal["comprobaciones"] = comp
    return sal


# ------------------------------------------------------------------------------------------------ presentación
CAB_GRUPOS = ["Grupo", "Clientes", "Ventas", "% de las ventas", "Margen", "Días desde la última compra", "Compras", "Monto por cliente"]
NUM_GRUPOS = range(1, 8)  # columnas que van alineadas como número
NOTA_GRUPOS = "Las tres últimas columnas son la mediana del grupo: el cliente del medio."


def filas_grupos(res):
    return [[g["nombre"], g["clientes"], rent.peso(g["ventas"]), rent.pct(g["pct_ventas"], 0), rent.peso(g["margen"]),
             rent.miles(g["recencia_mediana"], 0), rent.miles(g["frecuencia_mediana"], 1 if g["frecuencia_mediana"] % 1 else 0),
             rent.peso(g["monto_mediano"])] for g in res["grupos"]]


def lista_grupos(res):
    """Qué distingue a cada grupo, en una línea por grupo."""
    return [f"- **{g['nombre']}** ({g['clientes']} {'cliente' if g['clientes'] == 1 else 'clientes'}): {g['descripcion']}." for g in res["grupos"]]


def filas_clientes(res, etq, limite=None):
    orden = sorted(res["clientes"], key=lambda c: (-c["monto"], c["cliente_id"]))[:limite]
    return [[etq(c["cliente_id"]), rent.miles(c["recencia"]), rent.miles(c["frecuencia"]), rent.peso(c["monto"]), c["grupo"]]
            for c in orden]


CAB_CLIENTES = ["Cliente", "Días desde la última compra", "Compras", "Monto", "Grupo"]


def lineas_comprobaciones(res):
    c = res["comprobaciones"]
    if c["k"] is None:
        return ["- No se pudo buscar grupos por datos: faltan clientes para comprobarlos."]
    n_fmt = lambda x: "—" if x is None else rent.miles(x, 2)  # noqa: E731
    p95 = c["silueta_desordenada_p95"]
    ok1 = c["silueta"] is not None and p95 is not None and c["silueta"] > p95
    ok2 = c["estabilidad"] is not None and c["estabilidad"] >= UMBRAL_ESTABILIDAD
    return [f"- Cantidad de grupos probada: de {K_MIN} a {min(K_MAX, res['datos']['clientes'] // 10)}. La que mejor los separa: {c['k']} "
            "(coeficiente de silueta: 1 es separación perfecta, 0 es ninguna).",
            f"- ¿Hay grupos de verdad? Separación de {n_fmt(c['silueta'])} contra {n_fmt(p95)} que se logra con los mismos datos "
            "desordenados al azar (percentil 95): " + ("sí, la supera." if ok1 else "no la supera."),
            f"- ¿Son estables? Al repetir con {REPETICIONES} muestras distintas de los mismos clientes, los grupos coinciden en "
            f"{n_fmt(c['estabilidad'])} (1 es idénticos; se exige {rent.miles(UMBRAL_ESTABILIDAD, 1)}): " + ("sí." if ok2 else "no.")]


def resumen_consola(res, etq, nivel):
    d = res["datos"]
    sal = [f"# Grupos de clientes según cómo compran", "",
           f"- {d['clientes']} clientes con ventas · {d['lineas']} líneas · del {d['desde']} al {d['hasta']}",
           f"- Nivel usado: {nivel} · grupos {'por datos' if res['metodo_grupos'] == 'datos' else 'por reglas'}", "",
           f"**{res['conclusion']}**", "", "## Por grupo", ""] + lista_grupos(res) + ["", rent.tabla_md(CAB_GRUPOS, filas_grupos(res), NUM_GRUPOS), "",
                                                                                 NOTA_GRUPOS, ""]
    if nivel == "especialista":
        sal += ["## Comprobaciones", ""] + lineas_comprobaciones(res) + [""]
    if res["advertencias"]:
        sal += ["## Advertencias", ""] + [f"- {a}" for a in res["advertencias"]] + [""]
    return "\n".join(sal)


def tabla_cruce(res):
    c = res["tabla_cruzada"]
    return rent.tabla_md(["Grupo por datos"] + c["columnas"], [[f] + v for f, v in zip(c["filas"], c["valores"])], range(1, len(c["columnas"]) + 1))


def markdown_pagina(res, etq, nivel):
    d = res["datos"]
    gs = res["grupos"]
    total = sum(c["monto"] for c in res["clientes"])
    margen = sum(c["margen"] for c in res["clientes"]) if res["hay_costos"] else None
    n, parte = concentracion([{"monto": c["monto"], "cliente_id": c["cliente_id"]} for c in res["clientes"]])
    sal = ["---", "titulo: Grupos de clientes según cómo compran", f"subtitulo: Período {d['desde']} a {d['hasta']} · {d['clientes']} clientes", "---", "",
           f"> {res['conclusion']}", "", "```cifras",
           f"Clientes: {d['clientes']} | {d['lineas']} líneas de venta",
           f"Ventas: {rent.peso(total)} | " + (f"margen {rent.peso(margen)}, {rent.pct(margen / total if total else None)} de las ventas"
                                                if margen is not None else f"del {d['desde']} al {d['hasta']}")]
    sal += [f"Concentración: {rent.pct(parte, 0)} | de las ventas en {n} {'cliente' if n == 1 else 'clientes'}",
            f"Grupos: {len(gs)} | {'por datos (' + nivel + ')' if res['metodo_grupos'] == 'datos' else 'por reglas'}", "```", ""]
    if len(gs) >= 2:
        datos = ", ".join(f"{json.dumps(g['nombre'], ensure_ascii=False)}: [{rent.texto_num(round((g['pct_ventas'] or 0) * 100, 1))}, "
                          f"{rent.texto_num(round(g['pct_clientes'] * 100, 1))}]" for g in gs)
        sal += ["# Ventas y clientes por grupo", "", "```grafico", "tipo: barras", "titulo: Parte de las ventas y de los clientes por grupo",
                'unidad: "%"', 'series: ["% de las ventas", "% de los clientes"]', "datos: {" + datos + "}", "```", ""]
    sal += ["# Los grupos", ""] + lista_grupos(res) + ["", rent.tabla_md(CAB_GRUPOS, filas_grupos(res), NUM_GRUPOS), "", NOTA_GRUPOS, ""]
    if nivel == "especialista":
        sal += ["# Comprobaciones", ""] + lineas_comprobaciones(res) + [""]
        if res["tabla_cruzada"]:
            sal += ["# Grupos por datos contra grupos por reglas", "",
                    "Cuántos clientes de cada grupo por datos caen en cada grupo por reglas.", "", tabla_cruce(res), ""]
    if res["metodo_grupos"] == "datos":
        reglas = dict(res, grupos=res["grupos_reglas"])
        sal += ["# Grupos por reglas (referencia)", ""] + lista_grupos(reglas) + ["", rent.tabla_md(CAB_GRUPOS, filas_grupos(reglas), NUM_GRUPOS), ""]
    sal += [f"# Clientes de mayor monto ({min(MAX_CLIENTES_TABLA, len(res['clientes']))} de {len(res['clientes'])})", "",
            rent.tabla_md(CAB_CLIENTES, filas_clientes(res, etq, MAX_CLIENTES_TABLA), range(1, 4)), ""]
    if res["advertencias"]:
        sal += ["# Advertencias", ""] + [f"- {a}" for a in res["advertencias"]] + [""]
    sal += ["# Cómo leer esto", ""] + [f"- {t}" for t in NOTAS_LECTURA] + ["- " + experto.nota_de_nivel(res["recomendacion"], nivel), ""]
    return "\n".join(sal)


def escribir_salidas(res, proyecto, destino, etq, nivel, hoy, nombres):
    """Escribe informe.md, informe.html y resultado.json en `destino`. Devuelve (ruta html o None, avisos)."""
    destino.mkdir(parents=True, exist_ok=True)
    md = markdown_pagina(res, etq, nivel)
    (destino / "informe.md").write_text(md, encoding="utf-8")
    (destino / "resultado.json").write_text(json.dumps(para_json(res, etq if nombres else None), ensure_ascii=False, indent=2) + "\n",
                                            encoding="utf-8")
    avisos = []
    try:
        import explicar
        cfg = {}
        if (Path(proyecto) / "proyecto.yaml").exists():
            import _config
            cfg = _config.cargar(Path(proyecto))
        html, _ = explicar.generar(md, destino, cfg, Path(proyecto), hoy, False)
    except Exception as e:
        return None, [f"No se generó la página: {e} (queda el Markdown)."]
    (destino / "informe.html").write_text(html, encoding="utf-8")
    return destino / "informe.html", avisos


# ------------------------------------------------------------------------------------------------ principal
def main(argv=None):
    ap = argparse.ArgumentParser(prog="experto.py segmentar", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("proyecto", help="carpeta del proyecto (con finanzas/ventas.csv)")
    ap.add_argument("--desde", help="primera fecha de venta AAAA-MM-DD (por defecto, todo)")
    ap.add_argument("--hasta", help="última fecha AAAA-MM-DD (por defecto, la última venta)")
    ap.add_argument("--nivel", default="auto", choices=["auto", "base", "especialista"])
    ap.add_argument("--diagnosticar", action="store_true", help="mira los datos y dice qué nivel conviene, sin analizar")
    ap.add_argument("--id", help="nombre del análisis (por defecto segmentos-<hoy>)")
    ap.add_argument("--salida", help="carpeta de salida (por defecto <proyecto>/analisis/<id>/)")
    ap.add_argument("--con-nombres", action="store_true", help="usa nombres (solo con mapa local); los archivos quedan en finanzas/_local/")
    ap.add_argument("--json", action="store_true", help="solo el JSON, sin escribir archivos (siempre con identificadores)")
    ap.add_argument("--abrir", action="store_true")
    ap.add_argument("--hoy", help="fecha AAAA-MM-DD")
    ap.add_argument("--semilla", type=int, default=SEMILLA)
    a = ap.parse_args(argv)

    proyecto = Path(a.proyecto)
    if not (rent.carpeta_datos(proyecto) / "ventas.csv").exists():
        print(f"No se puede segmentar: falta {rent.carpeta_datos(proyecto).as_posix()}/ventas.csv.", file=sys.stderr)
        return 1
    hoy = date.today()
    if a.hoy:
        hoy = rent.fecha_de(a.hoy)
        if hoy is None:
            print("--hoy: usa AAAA-MM-DD", file=sys.stderr)
            return 1
    desde = rent.fecha_de(a.desde) if a.desde else None
    hasta = rent.fecha_de(a.hasta) if a.hasta else None
    if (a.desde and desde is None) or (a.hasta and hasta is None):
        print("Fechas no válidas: usa AAAA-MM-DD.", file=sys.stderr)
        return 1

    mapa = rent.Mapa(proyecto)
    convertidos = rent.normalizar(proyecto, hoy, mapa)
    rent.informar_normalizacion(convertidos, sys.stderr if a.json else None)

    clientes, info = leer_clientes(proyecto, desde, hasta)
    if len(clientes) < MIN_CLIENTES:
        print(f"No se puede segmentar: hay {len(clientes)} cliente(s) con ventas en el período y se necesitan al menos {MIN_CLIENTES}.",
              file=sys.stderr)
        return 1
    n = len(clientes)
    rec = experto.recomendacion(n >= UMBRAL_ESPECIALISTA, [motivo_especialista(n) if n >= UMBRAL_ESPECIALISTA else MOTIVO_BASE])
    datos = {"clientes": n, "desde": info["desde"].isoformat(), "hasta": info["hasta"].isoformat(), "lineas": info["lineas"]}

    if a.diagnosticar:
        if a.json:
            print(json.dumps({"recomendacion": rec, "datos": datos}, ensure_ascii=False, indent=2))
            return 0
        print("# Diagnóstico: grupos de clientes\n")
        print(f"- {n} clientes con ventas · {info['lineas']} líneas · del {datos['desde']} al {datos['hasta']}")
        print("\n".join(experto.texto_recomendacion(rec, None)))
        return 0

    nivel = experto.resolver_nivel(a.nivel)  # termina con código 3 si se pide el especialista y no está
    res = analizar(clientes, info, nivel, rec, a.semilla, hoy)
    avisos = []
    con_nombres = a.con_nombres
    if con_nombres and not mapa.existe:
        avisos.append("No hay mapa local de clientes (finanzas/_local/clientes-mapa.csv): se usan los identificadores.")
        con_nombres = False
    etq = rent.etiquetas(None, mapa, con_nombres)

    if a.json:
        print(json.dumps(para_json(res), ensure_ascii=False, indent=2))
        return 0

    print(resumen_consola(res, etq, nivel))
    print("\n".join(experto.texto_recomendacion(rec, nivel)))
    for av in avisos:
        print("\n" + av)
    nombre = a.id or f"segmentos-{hoy.isoformat()}"
    if con_nombres:
        destino = rent.carpeta_datos(proyecto) / "_local" / nombre
        if a.salida:
            print("\nCon --con-nombres los archivos se escriben solo en finanzas/_local/: se ignora --salida.")
    else:
        destino = Path(a.salida) if a.salida else proyecto / "analisis" / nombre
    html, extra = escribir_salidas(res, proyecto, destino, etq, nivel, hoy, con_nombres)
    print(f"\nInforme: {(destino / 'informe.md').as_posix()}")
    if html:
        print(f"Página: {html.as_posix()}")
    for av in extra:
        print(av)
    print(f"Datos: {(destino / 'resultado.json').as_posix()}")
    if con_nombres:
        print("Estos archivos llevan nombres de clientes y quedan en _local/: no se suben ni se comparten.")
    if a.abrir and html:
        webbrowser.open(html.resolve().as_uri())
    return 0


if __name__ == "__main__":
    import _consola
    _consola.preparar()
    sys.exit(main())
