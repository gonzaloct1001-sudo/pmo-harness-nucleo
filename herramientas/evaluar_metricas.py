#!/usr/bin/env python3
"""Evalúa métricas, reglas, requisitos de etapa y fichas de un proyecto (contrato común).

Uso:
    python herramientas/evaluar_metricas.py proyectos/<slug> [--hoy AAAA-MM-DD] [--salida archivo.md]

Lee metricas/metricas.yaml y metricas/metricas-*.yaml (métricas aportadas por arquetipos),
metricas/mediciones.csv y, si existen, items/items.csv,
items/etapas.yaml e items/fichas/. Toma el último valor de cada métrica por entidad hasta la
fecha de corte, aplica umbrales (semáforo), reglas y requisitos de etapa, detecta mediciones
desactualizadas y fichas con revisión vencida. No modifica archivos del proyecto.
Funciona igual para cualquier arquetipo: bots, acciones, postulaciones, proveedores, obras…
"""
import argparse
import csv
import operator
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import _config  # noqa: E402  (proyecto.yaml con herencia de programa)

try:
    import yaml
except ImportError:
    sys.exit("Falta pyyaml: pip install pyyaml")

OPS = {"<=": operator.le, "<": operator.lt, ">=": operator.ge, ">": operator.gt, "==": operator.eq, "!=": operator.ne}
VIGENCIA = {"diaria": 3, "semanal": 9, "quincenal": 17, "mensual": 40, "trimestral": 100, "semestral": 190, "anual": 380}


def fecha(v):
    if isinstance(v, date):
        return v
    try:
        return datetime.strptime(str(v).strip()[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def num(v):
    try:
        return float(str(v).replace(",", ".").strip())
    except (TypeError, ValueError):
        return None


def fmt(valor, unidad):
    if valor is None:
        return "—"
    if unidad == "%":
        return f"{valor * 100:.1f}%"
    if unidad in ("CLP", "USD", "UF", "$") or abs(valor) >= 10000:
        return f"{valor:,.0f}".replace(",", ".") + (f" {unidad}" if unidad and unidad != "$" else "")
    if unidad == "x":
        return f"{valor:.2f}x"
    txt = f"{valor:.2f}".rstrip("0").rstrip(".")
    return f"{txt} {unidad}".strip()


def semaforo(m, v):
    if v is None:
        return "Sin dato"
    d = m.get("direccion", "informativa")
    am, ro = num(m.get("umbral_amarillo")), num(m.get("umbral_rojo"))
    if d == "mayor_mejor":
        if ro is not None and v < ro:
            return "Rojo"
        if am is not None and v < am:
            return "Amarillo"
        return "Verde" if (am is not None or ro is not None) else "—"
    if d == "menor_mejor":
        if ro is not None and v > ro:
            return "Rojo"
        if am is not None and v > am:
            return "Amarillo"
        return "Verde" if (am is not None or ro is not None) else "—"
    return "—"


def frontmatter(ruta):
    try:
        t = ruta.read_text(encoding="utf-8")
    except OSError:
        return {}
    if not t.startswith("---"):
        return {}
    partes = t.split("---", 2)
    try:
        return (yaml.safe_load(partes[1]) or {}) if len(partes) > 2 else {}
    except yaml.YAMLError:
        return {}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("proyecto")
    ap.add_argument("--hoy")
    ap.add_argument("--salida")
    ap.add_argument("--json", action="store_true", help="entregar hallazgos y métricas en JSON (lo usa status.py)")
    a = ap.parse_args()
    raiz = Path(a.proyecto)
    hoy = fecha(a.hoy) if a.hoy else date.today()

    def cargar_yaml(rel):
        p = raiz / rel
        return (yaml.safe_load(p.read_text(encoding="utf-8")) or {}) if p.exists() else {}

    cfg = _config.cargar(raiz)
    # Definiciones: metricas/metricas.yaml (propias del proyecto) + metricas/metricas-*.yaml (aportadas por arquetipos)
    metricas, reglas, duplicadas = {}, [], []
    archivos_def = sorted((raiz / "metricas").glob("metricas*.yaml"), key=lambda p: (p.name != "metricas.yaml", p.name))
    for arch in archivos_def:
        defs = yaml.safe_load(arch.read_text(encoding="utf-8")) or {}
        for m in defs.get("metricas") or []:
            if not m.get("id"):
                continue
            if m["id"] in metricas:
                duplicadas.append(f"{m['id']} ({arch.name})")
                continue
            metricas[m["id"]] = m
        reglas += defs.get("reglas") or []
    etapas = (cargar_yaml("items/etapas.yaml").get("etapas") or [])
    orden_etapas = [e["id"] for e in etapas]

    # Mediciones: último valor por (entidad, métrica) hasta la fecha de corte
    ultimo, previo = {}, {}
    p_med = raiz / "metricas" / "mediciones.csv"
    if p_med.exists():
        with open(p_med, encoding="utf-8-sig", newline="") as f:
            filas = [r for r in csv.DictReader(f) if fecha(r.get("fecha")) and fecha(r["fecha"]) <= hoy]
        filas.sort(key=lambda r: fecha(r["fecha"]))
        for r in filas:
            k = (r["entidad"].strip(), r["metrica"].strip())
            if k in ultimo:
                previo[k] = ultimo[k]
            ultimo[k] = (fecha(r["fecha"]), num(r["valor"]), r.get("fuente", ""))

    items = []
    p_items = raiz / "items" / "items.csv"
    if p_items.exists():
        with open(p_items, encoding="utf-8-sig", newline="") as f:
            items = list(csv.DictReader(f))

    criticos, advert, info = [], [], []
    if duplicadas:
        info.append("Métricas definidas en más de un archivo (se usa la primera): " + ", ".join(duplicadas) + ".")
    val = lambda ent, met: (ultimo.get((ent, met)) or (None, None, None))[1]

    # --- Métricas sin definición o desactualizadas ---
    for (ent, met), (f_, v, _) in ultimo.items():
        m = metricas.get(met)
        if not m:
            info.append(f"Medición de '{met}' ({ent}) sin definición en metricas.yaml.")
            continue
        dias = VIGENCIA.get(str(m.get("frecuencia", "")).lower())
        activo = ent == "PROYECTO" or any(i["id"] == ent and i.get("etapa") != "retirado" for i in items) or not items
        if dias and activo and (hoy - f_).days > dias:
            advert.append(f"'{m.get('nombre', met)}' de {ent} desactualizada: último dato {f_} (frecuencia {m.get('frecuencia')}).")

    # --- Reglas ---
    for r in reglas:
        op = OPS.get(str(r.get("operador", "")).strip())
        lim = num(r.get("valor"))
        met = r.get("metrica")
        if not op or lim is None or not met:
            info.append(f"Regla {r.get('id')} mal definida (revisar operador, valor y métrica).")
            continue
        alcance = r.get("aplica_a") or {"nivel": "proyecto"}
        if "etapa" in alcance:
            etapas_obj = alcance["etapa"] if isinstance(alcance["etapa"], list) else [alcance["etapa"]]
            entidades = [i["id"] for i in items if i.get("etapa") in etapas_obj]
        elif "categoria" in alcance:
            entidades = [i["id"] for i in items if i.get("categoria") == alcance["categoria"]]
        else:
            entidades = ["PROYECTO"]
        entidades = [e for e in entidades if e not in (alcance.get("excluir") or [])]
        unidad = (metricas.get(met) or {}).get("unidad", "")
        for ent in entidades:
            v = val(ent, met)
            if v is None:
                advert.append(f"Regla {r.get('id')} ({r.get('descripcion', '')}): sin dato de '{met}' para {ent}.")
            elif not op(v, lim):
                texto = (f"Regla {r.get('id')} incumplida — {r.get('descripcion', '')}: {ent} tiene "
                         f"{met} = {fmt(v, unidad)} (límite {r.get('operador')} {fmt(lim, unidad)}).")
                (criticos if r.get("severidad", "critico") == "critico" else advert).append(texto)

    # --- Requisitos de etapa ---
    def cumple(item, etapa):
        fallas = []
        for q in etapa.get("requisitos") or []:
            if q.get("tipo") == "archivo":
                ruta = raiz / str(q.get("ruta", "")).replace("{id}", item["id"])
                if not ruta.exists():
                    fallas.append(f"falta {ruta.relative_to(raiz).as_posix()}")
            elif q.get("tipo") == "metrica":
                v, op, lim = val(item["id"], q.get("metrica")), OPS.get(str(q.get("operador"))), num(q.get("valor"))
                u = (metricas.get(q.get("metrica")) or {}).get("unidad", "")
                if v is None:
                    fallas.append(f"sin dato de {q.get('metrica')}")
                elif op and lim is not None and not op(v, lim):
                    fallas.append(f"{q.get('metrica')} = {fmt(v, u)} no cumple {q.get('operador')} {fmt(lim, u)}")
        return fallas

    candidatos = []
    etapa_por_id = {e["id"]: e for e in etapas}
    for it in items:
        e = etapa_por_id.get(it.get("etapa"))
        if not e:
            if etapas:
                criticos.append(f"Ítem {it['id']} tiene etapa desconocida '{it.get('etapa')}'.")
            continue
        fallas = cumple(it, e)
        if fallas:
            advert.append(f"Ítem {it['id']} ({it.get('nombre')}) en '{e.get('nombre', e['id'])}' no cumple requisitos: {'; '.join(fallas)}.")
        idx = orden_etapas.index(e["id"])
        if idx + 1 < len(orden_etapas) and orden_etapas[idx + 1] != "retirado":
            sig = etapa_por_id[orden_etapas[idx + 1]]
            if sig.get("requisitos") and sig.get("sugerir_avance", True) and not cumple(it, sig):
                candidatos.append(f"{it['id']} ({it.get('nombre')}) cumple los requisitos para pasar a '{sig.get('nombre', sig['id'])}'.")

    # --- Fichas con revisión vencida ---
    fichas_dir = raiz / "items" / "fichas"
    if fichas_dir.exists():
        activos = {i["id"] for i in items if i.get("etapa") != "retirado"}
        for fch in sorted(fichas_dir.glob("*.md")):
            if fch.name.startswith("_"):
                continue
            fm = frontmatter(fch)
            fr = fecha(fm.get("fecha_revision")) if fm.get("fecha_revision") else None
            iid = str(fm.get("id") or fch.stem)
            if fr and iid in activos:
                if fr < hoy:
                    advert.append(f"Ficha {iid}: revisión vencida desde {fr}.")
                elif (fr - hoy).days <= 30:
                    info.append(f"Ficha {iid}: revisión vence el {fr}.")

    if a.json:
        import json
        m_json = []
        for m in metricas.values():
            if m.get("nivel") == "proyecto":
                u = ultimo.get(("PROYECTO", m["id"]))
                m_json.append({"id": m["id"], "nombre": m.get("nombre", m["id"]), "valor": u[1] if u else None,
                               "fecha": u[0] if u else None, "unidad": m.get("unidad", ""), "semaforo": semaforo(m, u[1] if u else None)})
        print(json.dumps({"criticos": criticos, "advertencias": advert, "info": info, "candidatos": candidatos,
                          "reglas_criticas": sum(1 for x in criticos if x.startswith("Regla")),
                          "reglas_advertencia": sum(1 for x in advert if x.startswith("Regla") and "incumplida" in x),
                          "metricas_proyecto": m_json}, ensure_ascii=False, default=str))
        return

    # --- Informe ---
    nombre = (cfg.get("proyecto") or {}).get("nombre", raiz.name)
    out = [f"# Evaluación de métricas — {nombre}", "", f"Fecha de corte: {hoy.isoformat()}", ""]
    m_proy = [m for m in metricas.values() if m.get("nivel") == "proyecto"]
    if m_proy:
        out += ["## Métricas del proyecto", "", "| Métrica | Valor | Anterior | Fecha | Estado |", "|---|---|---|---|---|"]
        for m in m_proy:
            u = ultimo.get(("PROYECTO", m["id"]))
            pv = previo.get(("PROYECTO", m["id"]))
            out.append(f"| {m.get('nombre', m['id'])} | {fmt(u[1] if u else None, m.get('unidad', ''))} | "
                       f"{fmt(pv[1] if pv else None, m.get('unidad', ''))} | {u[0] if u else '—'} | {semaforo(m, u[1] if u else None)} |")
        out.append("")
    m_item = [m for m in metricas.values() if m.get("nivel") == "item" and m.get("clave", True)]
    if items:
        out += ["## Ítems por etapa", "", "| Etapa | Cantidad |", "|---|---|"]
        for e in etapas:
            out.append(f"| {e.get('nombre', e['id'])} | {sum(1 for i in items if i.get('etapa') == e['id'])} |")
        out.append("")
        visibles = [i for i in items if i.get("etapa") != "retirado"]
        if visibles and m_item:
            out += ["## Ítems vigentes", "",
                    "| Ítem | Nombre | Etapa | " + " | ".join(m.get("nombre", m["id"]) for m in m_item) + " |",
                    "|---|---|---|" + "---|" * len(m_item)]
            for it in sorted(visibles, key=lambda i: (-(orden_etapas.index(i["etapa"]) if i.get("etapa") in orden_etapas else -1), i["id"])):
                celdas = []
                for m in m_item:
                    v = val(it["id"], m["id"])
                    s = semaforo(m, v)
                    celdas.append(fmt(v, m.get("unidad", "")) + (f" ({s})" if s in ("Amarillo", "Rojo") else ""))
                out.append(f"| {it['id']} | {it.get('nombre', '')} | {it.get('etapa', '')} | " + " | ".join(celdas) + " |")
            out.append("")
    for titulo, lista in (("Crítico", criticos), ("Advertencias", advert), ("Candidatos a avanzar de etapa", candidatos), ("Información", info)):
        out += [f"## {titulo} ({len(lista)})", ""] + ([f"- {x}" for x in lista] or ["- Sin hallazgos."]) + [""]
    texto = "\n".join(out)
    if a.salida:
        Path(a.salida).parent.mkdir(parents=True, exist_ok=True)
        Path(a.salida).write_text(texto, encoding="utf-8")
    print(texto)


if __name__ == "__main__":
    import _consola
    _consola.preparar()
    main()
