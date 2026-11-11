#!/usr/bin/env python3
"""Plazo del proyecto bajo incertidumbre: ¿qué probabilidad hay de terminar en la fecha comprometida y qué tareas la mueven?

Uso:
    python herramientas/experto.py plazo <proyecto> [--fecha AAAA-MM-DD] [--meta AAAA-MM-DD] [--optimista -10] [--pesimista 30]
                                                    [--corridas N] [--semilla S] [--diagnosticar] [--id nombre] [--salida carpeta] [--json] [--abrir]

Lee `cronograma/cronograma.csv` y simula la red de tareas con las mismas reglas del pronóstico de `evm_cpm.py` (días corridos,
dependencias fin-inicio): una tarea terminada usa su fecha real; una en curso termina en (corte + lo que le queda); una no iniciada
parte cuando terminan sus predecesoras y no antes de su inicio plan ni del corte. La duración que le queda a cada tarea no
terminada se sortea en un rango triangular (mínimo, más probable = lo que dice el plan, máximo):
- por defecto, un porcentaje de su duración restante (`--optimista -10`, `--pesimista 30`): es un supuesto sin fuente;
- por tarea, en `cronograma/incertidumbre.csv` (id,optimista_dias,probable_dias,pesimista_dias,fuente), que reemplaza el
  rango por defecto de esa tarea.
La fecha comprometida (`--meta`) es la de la línea base de proyecto.yaml; si no hay, el mayor `fin_plan`.

Entrega: la probabilidad de terminar en la meta o antes, las fechas de los percentiles 50, 80 y 90, las tareas que más mueven la
fecha (índice de criticidad y correlación de orden), el tornado, y la probabilidad de cada hito pendiente. Deja `informe.html`,
`informe.md` y `resultado.json` en `<proyecto>/analisis/<id>/`. Es del nivel base (biblioteca estándar): `--nivel` se acepta por
uniformidad con los demás análisis, pero no cambia nada.
"""
import argparse
import json
import math
import random
import re
import sys
import webbrowser
from datetime import date, timedelta
from pathlib import Path

import _config
import evm_cpm
import experto
import simular

CORRIDAS = 5000
SEMILLA = 20261111
OPTIMISTA = -10.0
PESIMISTA = 30.0
POR_DEFECTO = "supuesto sin fuente"
TORNADO_MAX = 8
SI = ("si", "sí", "true", "1", "x", "yes")


class Problema(Exception):
    """Algo que impide analizar el plazo; el mensaje dice qué corregir."""


def fd(d):
    return f"{d:%d-%m-%Y}"


def fecha_de(o):
    return date.fromordinal(int(o))


# ------------------------------------------------------------------------------------------- lectura
def leer_red(raiz, hoy):
    """La red de tareas con la misma interpretación que el pronóstico de evm_cpm.py."""
    ruta = raiz / "cronograma" / "cronograma.csv"
    if not ruta.exists():
        raise Problema(f"no existe {ruta.as_posix()}: sin cronograma no hay plazo que analizar")
    filas = evm_cpm.leer(ruta)
    tareas = [t for t in filas if (t.get("id") or "").strip() and evm_cpm.f(t.get("inicio_plan")) and evm_cpm.f(t.get("fin_plan"))]
    sin_fechas = len(filas) - len(tareas)
    if not tareas:
        raise Problema("el cronograma no tiene tareas con fechas plan (inicio_plan y fin_plan)")
    for t in tareas:
        t["id"] = t["id"].strip()
    try:
        orden, por_id = evm_cpm.orden_topologico(tareas)
    except SystemExit as e:  # dependencia circular
        raise Problema(str(e))
    h0 = hoy.toordinal()
    red = {}
    for i in orden:
        t = por_id[i]
        ini_p, fin_p = evm_cpm.f(t["inicio_plan"]), evm_cpm.f(t["fin_plan"])
        dur = max((fin_p - ini_p).days, 0)
        av = (evm_cpm.num(t.get("avance_pct"), 0) or 0) / 100
        ini_r, fin_r = evm_cpm.f(t.get("inicio_real")), evm_cpm.f(t.get("fin_real"))
        r = {"id": i, "tarea": (t.get("tarea") or i).strip(), "hito": (t.get("es_hito") or "").strip().lower() in SI,
             "estado": (t.get("estado") or "").strip().lower(), "preds": [p for p in evm_cpm.preds(t) if p in por_id],
             "fin_plan": fin_p, "ini_plan_o": ini_p.toordinal()}
        if av >= 1:
            r.update(tipo="terminada", ini_o=(ini_r or ini_p).toordinal(), fin_o=(fin_r or fin_p).toordinal(), d=0)
        elif av > 0 or ini_r:
            ini = (ini_r or ini_p).toordinal()
            r.update(tipo="curso", ini_o=ini, d=round(dur * (1 - av)))
        else:
            r.update(tipo="nueva", d=dur)
        red[i] = r
    return orden, red, sin_fechas, h0


def leer_incertidumbre(raiz, red):
    """{id: (optimista, probable, pesimista, fuente)} desde cronograma/incertidumbre.csv, validado."""
    ruta = raiz / "cronograma" / "incertidumbre.csv"
    if not ruta.exists():
        return {}, False
    filas = evm_cpm.leer(ruta)
    if filas and not {"id", "optimista_dias", "probable_dias", "pesimista_dias"} <= set(filas[0]):
        raise Problema(f"{ruta.as_posix()} debe traer las columnas id, optimista_dias, probable_dias, pesimista_dias y fuente")
    rangos = {}
    for n, fila in enumerate(filas, start=2):
        i = (fila.get("id") or "").strip()
        if not i:
            continue
        donde = f"{ruta.name}, línea {n} (id {i})"
        if i not in red:
            raise Problema(f"{donde}: el id no existe en el cronograma")
        if i in rangos:
            raise Problema(f"{donde}: el id está repetido")
        v = [evm_cpm.num(fila.get(k)) for k in ("optimista_dias", "probable_dias", "pesimista_dias")]
        if any(x is None for x in v):
            raise Problema(f"{donde}: optimista_dias, probable_dias y pesimista_dias deben ser números")
        if v[0] < 0:
            raise Problema(f"{donde}: las duraciones no pueden ser negativas")
        if not v[0] <= v[1] <= v[2]:
            raise Problema(f"{donde}: debe cumplirse optimista ≤ probable ≤ pesimista (llegó {v[0]:g}, {v[1]:g}, {v[2]:g})")
        rangos[i] = (v[0], v[1], v[2], (fila.get("fuente") or "").strip() or "incertidumbre.csv (sin fuente indicada)")
    return rangos, True


def armar_rangos(orden, red, propios, opt, pes):
    """Rango de cada tarea pendiente: {id: {opt, prob, pes, fuente, propio}}."""
    out = {}
    for i in orden:
        r = red[i]
        if r["tipo"] == "terminada":
            continue
        if i in propios:
            o, p, s, fuente = propios[i]
            out[i] = {"opt": o, "prob": p, "pes": s, "fuente": fuente, "propio": True}
        else:
            d = r["d"]
            out[i] = {"opt": max(0.0, d * (1 + opt / 100)), "prob": float(d), "pes": max(0.0, d * (1 + pes / 100)),
                      "fuente": f"{POR_DEFECTO} ({opt:+g} % / {pes:+g} %)".replace(".", ","), "propio": False}
    return out


# ------------------------------------------------------------------------------------------- cálculo
def propagar(orden, red, h0, durs):
    """Inicio y fin (en días ordinales) de cada tarea con las duraciones dadas a las pendientes."""
    ini, fin = {}, {}
    for i in orden:
        r = red[i]
        if r["tipo"] == "terminada":
            ini[i], fin[i] = r["ini_o"], r["fin_o"]
        elif r["tipo"] == "curso":
            ini[i] = r["ini_o"]
            fin[i] = max(h0, ini[i]) + durs[i]
        else:
            ini[i] = max([r["ini_plan_o"], h0] + [fin[p] for p in r["preds"]])
            fin[i] = ini[i] + durs[i]
    return ini, fin


def ruta_del_termino(orden, red, h0, fin):
    """Las tareas pendientes que definen el término: desde la última, la predecesora que determinó su inicio."""
    cur = max(orden, key=lambda i: fin[i])
    marcadas = set()
    while True:
        r = red[cur]
        if r["tipo"] == "terminada":
            break
        marcadas.add(cur)
        if r["tipo"] != "nueva" or not r["preds"]:
            break
        p = max(r["preds"], key=lambda x: fin[x])
        if fin[p] >= max(r["ini_plan_o"], h0):
            cur = p
        else:
            break
    return marcadas


def termino(v):
    """Día entero en que termina (redondeo hacia arriba)."""
    return int(math.ceil(v - 1e-9))


def analizar(orden, red, h0, rangos, meta, corridas, semilla):
    rng = random.Random(semilla)
    pend = [i for i in orden if i in rangos]
    var = [i for i in pend if rangos[i]["pes"] > rangos[i]["opt"]]
    prob = {i: float(rangos[i]["prob"]) for i in pend}
    _, fin0 = propagar(orden, red, h0, prob)
    probable = termino(max(fin0.values()))
    finales, muestras = [], {i: [] for i in var}
    cuenta = {i: 0 for i in pend}
    hitos = [i for i in pend if red[i]["hito"]]
    fin_hito = {i: [] for i in hitos}
    for _ in range(corridas):
        durs = dict(prob)
        for i in var:
            g = rangos[i]
            durs[i] = rng.triangular(g["opt"], g["pes"], min(max(g["prob"], g["opt"]), g["pes"]))
            muestras[i].append(durs[i])
        ini, fin = propagar(orden, red, h0, durs)
        finales.append(max(fin.values()))
        for i in ruta_del_termino(orden, red, h0, fin):
            cuenta[i] += 1
        for i in hitos:
            fin_hito[i].append(termino(fin[i]))
    dias = sorted(termino(v) for v in finales)
    r = {"probable": probable, "dias": dias, "finales": finales,
         "probabilidad": sum(1 for d in dias if d <= meta) / corridas,
         "p": {q: simular.percentil(dias, q / 100) for q in (50, 80, 90)}}
    r["criticidad"] = {i: cuenta[i] / corridas for i in pend}
    r["correlacion"] = {i: (simular.correlacion_de_orden(muestras[i], finales) if i in muestras else 0.0) for i in pend}
    r["hitos"] = {}
    for i in hitos:
        v = sorted(fin_hito[i])
        r["hitos"][i] = {"probabilidad": sum(1 for d in v if d <= red[i]["fin_plan"].toordinal()) / corridas,
                         "p80": simular.percentil(v, 0.80)}
    # tornado: la tarea en su duración optimista o pesimista y las demás en la más probable
    orden_peso = sorted(var, key=lambda i: (-abs(r["correlacion"][i]), -r["criticidad"][i], i))
    r["tornado"] = []
    for i in orden_peso[:TORNADO_MAX]:
        res = []
        for lado in ("opt", "pes"):
            d = dict(prob)
            d[i] = rangos[i][lado]
            res.append(termino(max(propagar(orden, red, h0, d)[1].values())) - meta)
        r["tornado"].append({"id": i, "optimista": res[0], "pesimista": res[1]})
    r["tornado"] = [t for t in r["tornado"] if t["optimista"] != t["pesimista"]]
    r["mueven"] = orden_peso[:5]
    return r


# ------------------------------------------------------------------------------------------- resultado
def armar_resultado(red, rangos, r, hoy, meta, corridas, semilla, rec, advertencias):
    pend = list(rangos)
    hitos = [i for i in pend if red[i]["hito"]]
    p = r["p"]
    f_ = lambda o: fecha_de(o).isoformat()  # noqa: E731
    return {
        "nivel": "base", "recomendacion": rec,
        "datos": {"tareas": len(red), "pendientes": len(pend), "hitos": len(hitos), "corte": hoy.isoformat(),
                  "meta": fecha_de(meta).isoformat(), "corridas": corridas, "semilla": semilla},
        "probabilidad": r["probabilidad"],
        "termino": {"probable": f_(r["probable"]), "p50": f_(p[50]), "p80": f_(p[80]), "p90": f_(p[90]),
                    "dias_p50": p[50] - meta, "dias_p80": p[80] - meta, "dias_p90": p[90] - meta},
        "tareas": [{"id": i, "tarea": red[i]["tarea"], "criticidad": round(r["criticidad"][i], 4), "correlacion": round(r["correlacion"][i], 4),
                    "optimista": round(rangos[i]["opt"], 2), "probable": round(rangos[i]["prob"], 2),
                    "pesimista": round(rangos[i]["pes"], 2), "fuente": rangos[i]["fuente"]}
                   for i in pend if not red[i]["hito"]],
        "hitos": [{"id": i, "hito": red[i]["tarea"], "fecha_plan": red[i]["fin_plan"].isoformat(),
                   "probabilidad": r["hitos"][i]["probabilidad"], "p80": f_(r["hitos"][i]["p80"])} for i in hitos],
        "tornado": [{"id": t["id"], "dias_optimista": t["optimista"], "dias_pesimista": t["pesimista"]} for t in r["tornado"]],
        "advertencias": advertencias,
    }


def advertir(orden, red, rangos, propios, hoy, meta):
    av = []
    raros = [i for i in orden if red[i]["estado"] in ("pausada", "detenida", "cancelada") and red[i]["tipo"] != "terminada"]
    if raros:
        av.append("Tareas con estado pausada, detenida o cancelada (" + ", ".join(raros) + "): se tratan como cualquier otra tarea "
                  "pendiente, igual que en evm_cpm.py (una cancelada sigue sumando plazo; corrige su avance o quítala del cronograma).")
    for i in propios:
        if i in red and red[i]["tipo"] == "terminada":
            av.append(f"incertidumbre.csv trae un rango para {i}, que ya está terminada: se ignora.")
    por_defecto = [i for i in rangos if not rangos[i]["propio"] and rangos[i]["pes"] > rangos[i]["opt"]]
    if por_defecto:
        av.append((f"{len(por_defecto)} tareas usan" if len(por_defecto) > 1 else "1 tarea usa")
                  + " el rango por defecto, que es un supuesto sin fuente: el resultado vale lo que valga ese rango.")
    if meta < hoy.toordinal():
        av.append("La meta es anterior a la fecha de corte.")
    return av


def cargar_todo(a):
    """Valida los argumentos y la carpeta; devuelve el contexto del análisis."""
    raiz = Path(a.proyecto)
    if not raiz.is_dir():
        raise Problema(f"no existe la carpeta del proyecto: {raiz.as_posix()}")
    hoy = evm_cpm.f(a.fecha) if a.fecha else date.today()
    if hoy is None:
        raise Problema("--fecha debe ser AAAA-MM-DD")
    if a.meta and evm_cpm.f(a.meta) is None:
        raise Problema("--meta debe ser AAAA-MM-DD")
    if a.optimista > a.pesimista:
        raise Problema("--optimista no puede ser mayor que --pesimista")
    if a.optimista <= -100:
        raise Problema("--optimista debe ser mayor que -100 (un porcentaje de la duración que queda)")
    if a.corridas < 100:
        raise Problema("al menos 100 corridas para que la probabilidad signifique algo")
    orden, red, sin_fechas, h0 = leer_red(raiz, hoy)
    propios, hay = leer_incertidumbre(raiz, red)
    rangos = armar_rangos(orden, red, propios, a.optimista, a.pesimista)
    if not rangos:
        raise Problema("no hay tareas pendientes: todas están terminadas, no hay plazo que simular")
    try:
        cfg = _config.cargar(raiz)
    except Exception:
        cfg = {}
    if a.meta:
        meta = evm_cpm.f(a.meta)
    else:
        meta = evm_cpm.f(((cfg.get("linea_base") or {}).get("fecha_termino_vigente"))) or max(r["fin_plan"] for r in red.values())
    advertencias = advertir(orden, red, rangos, propios, hoy, meta.toordinal())
    if sin_fechas:
        advertencias.append((f"{sin_fechas} filas del cronograma sin id o sin fechas plan quedaron" if sin_fechas > 1 else
                             "1 fila del cronograma sin id o sin fechas plan quedó") + " fuera.")
    return {"raiz": raiz, "hoy": hoy, "orden": orden, "red": red, "h0": h0, "propios": propios, "hay_incertidumbre": hay,
            "rangos": rangos, "meta": meta.toordinal(), "cfg": cfg, "advertencias": advertencias}


# ------------------------------------------------------------------------------------------- informe
def n(v, u=""):
    return simular.n(v, u)


def signo(d):
    return f"{d:+d}".replace("-", "−")


def en_dias(d):
    return "en la meta" if d == 0 else (f"{abs(d)} día{'s' if abs(d) != 1 else ''} {'después' if d > 0 else 'antes'} de la meta")


def corto(texto, k=34):
    texto = str(texto).replace("|", "/").replace('"', "'")
    return texto if len(texto) <= k else texto[:k - 1].rstrip() + "…"


def informe_md(c, r, res):
    red, rangos, meta, hoy, d = c["red"], c["rangos"], c["meta"], c["hoy"], res["datos"]
    p, t = r["p"], res["termino"]
    prob = n(r["probabilidad"] * 100)
    clave = (f"Hay {prob} % de probabilidad de terminar el {fd(fecha_de(meta))} o antes; para tener 80 % de seguridad, la fecha es el "
             f"{fd(fecha_de(p[80]))}.")
    o = ["---", "titulo: \"¿Se termina en la fecha comprometida?\"",
         f"subtitulo: \"Plazo del proyecto · corte {fd(hoy)} · {n(d['corridas'])} corridas · semilla {d['semilla']}\"", f"fecha: {hoy.isoformat()}",
         "---", "", f"> {clave}", "", "```cifras",
         f"Probabilidad de cumplir: {prob} % | terminar el {fd(fecha_de(meta))} o antes",
         f"Con 50 % de seguridad: {fd(fecha_de(p[50]))} | {en_dias(t['dias_p50'])}; la mitad de los escenarios termina antes",
         f"Con 80 % de seguridad: {fd(fecha_de(p[80]))} | {en_dias(t['dias_p80'])}; 8 de cada 10 escenarios terminan antes",
         f"Si todo dura lo más probable: {fd(fecha_de(r['probable']))} | sin incertidumbre, {en_dias(r['probable'] - meta)}", "```", "",
         "# Qué tan probable es cada fecha de término", ""]
    dias = r["dias"]
    rel = [x - meta for x in dias]
    if rel[0] == rel[-1]:
        o += [f"Con estos rangos todos los escenarios terminan el mismo día ({fd(fecha_de(dias[0]))}): no hay incertidumbre que graficar.", ""]
    else:
        o += ["Días de término respecto de la meta: negativo = antes, positivo = después.", "", "```grafico", "tipo: histograma",
              f"titulo: \"Término del proyecto en {n(d['corridas'])} escenarios\"", "unidad: \"días\"", "meta: 0", "sentido: menor",
              "valores: [" + ", ".join(str(x) for x in rel) + "]", "```", ""]
    o += ["# Qué tareas mueven la fecha", ""]
    if r["mueven"]:
        mas = ", ".join(f"**{red[i]['tarea']}** ({i})" for i in r["mueven"])
        o += [f"Las que más mueven la fecha de término: {mas}.", ""]
    if len(r["tornado"]) >= 2:
        o += ["Cada barra muestra el término (en días respecto de la meta) si esa tarea toma su duración optimista o pesimista y las demás "
              "la más probable.", "", "```grafico", "tipo: tornado", "titulo: \"Término según la duración de cada tarea\"", "unidad: \"días\"",
              f"base: {r['probable'] - meta}", "etiquetas: [\"Con su duración optimista\", \"Con su duración pesimista\"]", "datos:"]
        for x in r["tornado"]:
            nombre = corto(x["id"] + " " + red[x["id"]]["tarea"])
            o.append(f"  {json.dumps(nombre, ensure_ascii=False)}: [{x['optimista']}, {x['pesimista']}]")
        o += ["```", ""]
    elif r["tornado"]:
        x = r["tornado"][0]
        o += [f"Solo **{red[x['id']]['tarea']}** mueve el término por sí sola: con su duración optimista termina {en_dias(x['optimista'])} y con la pesimista, "
              f"{en_dias(x['pesimista'])}.", ""]
    else:
        o += ["Ninguna tarea, movida sola dentro de su rango, cambia la fecha de término.", ""]
    o += ["| Id | Tarea | Criticidad | Correlación con el término |", "|---|---|---|---|"]
    filas = sorted((i for i in rangos if not red[i]["hito"]), key=lambda i: (-r["criticidad"][i], -abs(r["correlacion"][i]), i))
    o += [f"| {i} | {corto(red[i]['tarea'], 60)} | {n(r['criticidad'][i] * 100)} % | {n(round(r['correlacion'][i], 2))} |" for i in filas]
    o += ["", "Criticidad: en qué proporción de los escenarios la tarea está en la cadena que define el término (la que determinó el inicio de la "
          "siguiente, hasta la última tarea). Correlación: de orden, entre la duración sorteada de la tarea y la fecha de término.", ""]
    if res["hitos"]:
        o += ["# Hitos pendientes", "", "```tiempo"]
        for h in sorted(res["hitos"], key=lambda x: x["p80"]):
            o.append(f"{h['p80']}: {corto(h['hito'], 60)} (con 80 % de seguridad; plan {fd(date.fromisoformat(h['fecha_plan']))}; "
                     f"probabilidad de cumplir su fecha {n(h['probabilidad'] * 100)} %)")
        o += ["```", ""]
    o += ["# Los supuestos", "", "| Id | Tarea | Optimista | Más probable | Pesimista | De dónde sale |", "|---|---|---|---|---|---|"]
    for i in rangos:
        g = rangos[i]
        o.append(f"| {i} | {corto(red[i]['tarea'], 60)} | {n(round(g['opt'], 1))} d | {n(round(g['prob'], 1))} d | {n(round(g['pes'], 1))} d | {g['fuente']} |")
    o += ["", "Las duraciones son lo que le queda a cada tarea, en días corridos.", "", "# Cómo leer esto", "",
          f"- Los rangos por defecto ({n(c['opt'])} % y +{n(c['pes'])} % de la duración que queda) son supuestos sin fuente: el resultado vale lo que valgan los rangos. "
          "Cámbialos por los de cada tarea en `cronograma/incertidumbre.csv`.",
          "- Las tareas se sortean independientes entre sí. Si varias dependen de la misma causa (un proveedor, un equipo, una aprobación), "
          "el riesgo real es mayor que el que muestra esta simulación.",
          "- No incluye cambios de alcance, tareas nuevas ni recursos compartidos entre tareas.",
          "- Las tareas terminadas usan su fecha real; las en curso varían solo en lo que les queda; los días son corridos, como en el pronóstico del valor ganado.",
          f"- Para repetir exactamente esta corrida: {n(d['corridas'])} escenarios con la semilla {d['semilla']}."]
    o += [f"- {a}" for a in res["advertencias"]]
    o += ["- " + experto.nota_de_nivel(res["recomendacion"], "base"), ""]
    return "\n".join(o)


def guardar(carpeta, c, r, res):
    import explicar
    carpeta.mkdir(parents=True, exist_ok=True)
    md = informe_md(c, r, res)
    (carpeta / "informe.md").write_text(md, encoding="utf-8")
    pagina, _ = explicar.generar(md, carpeta, c["cfg"], c["raiz"], c["hoy"])
    (carpeta / "informe.html").write_text(pagina, encoding="utf-8")
    (carpeta / "resultado.json").write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return carpeta / "informe.html"


def recomendar(extra=()):
    return experto.recomendacion(False, ["simular las fechas del cronograma no necesita bibliotecas adicionales"] + list(extra))


def diagnosticar(c):
    red, rangos = c["red"], c["rangos"]
    pend = [i for i in rangos if not red[i]["hito"]]
    hitos = [i for i in rangos if red[i]["hito"]]
    print("# Diagnóstico del plazo\n")
    print(f"- Tareas en el cronograma: {len(red)}; pendientes: {len(pend)}; hitos pendientes: {len(hitos)}.")
    print(f"- Archivo cronograma/incertidumbre.csv: {'sí, con ' + str(len(c['propios'])) + (' tarea' if len(c['propios']) == 1 else ' tareas') if c['hay_incertidumbre'] else 'no hay'}.")
    for a in c["advertencias"]:
        print(f"- Atención: {a}")
    for linea in experto.texto_recomendacion(recomendar([f"{len(rangos)} tareas pendientes"]), None):
        print(linea)
    return 0


def consola(c, r, res, pagina):
    red, d, t = c["red"], res["datos"], res["termino"]
    print(f"# Plazo del proyecto — corte {fd(c['hoy'])}\n")
    print(f"- Meta: {fd(fecha_de(c['meta']))} · con las duraciones más probables: {fd(fecha_de(r['probable']))}")
    print(f"- Probabilidad de terminar en la meta o antes: {n(r['probabilidad'] * 100)} %")
    for q in (50, 80, 90):
        print(f"- Percentil {q}: {fd(fecha_de(r['p'][q]))} ({signo(t['dias_p' + str(q)])} días respecto de la meta)")
    if r["mueven"]:
        print("- Las que más mueven la fecha: " + "; ".join(
            f"{i} {corto(red[i]['tarea'], 40)} (criticidad {n(r['criticidad'][i] * 100)} %, correlación {n(round(r['correlacion'][i], 2))})" for i in r["mueven"]))
    riesgo = [h for h in res["hitos"] if h["probabilidad"] < 0.5]
    for h in riesgo:
        print(f"- Hito en riesgo: {h['id']} {corto(h['hito'], 40)}: {n(h['probabilidad'] * 100)} % de cumplir el {fd(date.fromisoformat(h['fecha_plan']))}; P80 {fd(date.fromisoformat(h['p80']))}")
    for a in res["advertencias"]:
        print(f"- Atención: {a}")
    print(f"- {n(d['corridas'])} corridas, semilla {d['semilla']}")
    for linea in experto.texto_recomendacion(res["recomendacion"], "base"):
        print(linea)
    if pagina:
        print(f"\nPágina: {pagina.as_posix()}")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="experto.py plazo", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("proyecto", help="carpeta del proyecto (con cronograma/cronograma.csv)")
    ap.add_argument("--fecha", "--hoy", dest="fecha", help="fecha de corte AAAA-MM-DD (por defecto, hoy)")
    ap.add_argument("--meta", help="fecha comprometida AAAA-MM-DD (por defecto, la de la línea base o el mayor fin_plan)")
    ap.add_argument("--optimista", type=float, default=OPTIMISTA, help="%% de la duración restante en el caso optimista (por defecto -10)")
    ap.add_argument("--pesimista", type=float, default=PESIMISTA, help="%% de la duración restante en el caso pesimista (por defecto 30)")
    ap.add_argument("--corridas", type=int, default=CORRIDAS)
    ap.add_argument("--semilla", type=int, default=SEMILLA)
    ap.add_argument("--nivel", default="auto", help="se acepta por uniformidad; este análisis siempre es del nivel base")
    ap.add_argument("--diagnosticar", action="store_true", help="resumir el cronograma y decir si el nivel base alcanza, sin simular")
    ap.add_argument("--id", help="nombre del análisis (por defecto plazo-<fecha de corte>)")
    ap.add_argument("--salida", help="carpeta de salida (por defecto <proyecto>/analisis/<id>/)")
    ap.add_argument("--json", action="store_true", help="imprimir solo el JSON, sin escribir archivos")
    ap.add_argument("--abrir", action="store_true", help="abrir la página en el navegador")
    a = ap.parse_args(argv)
    try:
        c = cargar_todo(a)
        c["opt"], c["pes"] = a.optimista, a.pesimista
        if a.diagnosticar:
            return diagnosticar(c)
        nombre = a.id or f"plazo-{c['hoy'].isoformat()}"
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", nombre):
            raise Problema("--id: letras, números, puntos y guiones, sin espacios (por ejemplo, plazo-2026-11-11)")
        r = analizar(c["orden"], c["red"], c["h0"], c["rangos"], c["meta"], a.corridas, a.semilla)
        rec = recomendar([f"{len(c['rangos'])} tareas pendientes"])
        res = armar_resultado(c["red"], c["rangos"], r, c["hoy"], c["meta"], a.corridas, a.semilla, rec, c["advertencias"])
        if a.json:
            print(json.dumps(res, ensure_ascii=False, indent=2))
            return 0
        carpeta = Path(a.salida) if a.salida else c["raiz"] / "analisis" / nombre
        pagina = guardar(carpeta, c, r, res)
    except Problema as e:
        print(f"No se pudo analizar el plazo: {e}", file=sys.stderr)
        return 1
    except ModuleNotFoundError:
        raise
    except Exception as e:  # explicar.Problema u otro fallo al escribir
        if type(e).__name__ == "Problema":
            print(f"No se pudo generar el informe: {e}", file=sys.stderr)
            return 1
        raise
    consola(c, r, res, pagina)
    if a.abrir:
        webbrowser.open(pagina.resolve().as_uri())
    return 0


if __name__ == "__main__":
    import _consola
    _consola.preparar()
    sys.exit(main())
