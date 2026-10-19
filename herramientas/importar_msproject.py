#!/usr/bin/env python3
"""Importa un cronograma de Microsoft Project (XML) al formato del harness.

Uso:
    python herramientas/importar_msproject.py <archivo.xml> proyectos/<slug> [--nivel-subproyecto 1]
        [--mapa "Nombre rama=sp1,Otra rama=sp2"] [--reemplazar] [--linea-base] [--costos-sin-centavos]

Formato de entrada: el XML de MS Project (Archivo > Guardar como > "XML" / "Formato XML"). El archivo .mpp es binario y
no se lee directamente: guárdalo como XML desde MS Project (o Project para la web) y usa ese archivo.

Qué hace:
- Cada tarea (no resumen) pasa a una fila de cronograma.csv: id T<Id de MS Project>, subproyecto = tarea resumen del
  nivel indicado (--nivel-subproyecto, por defecto 1), fechas plan, fechas reales, % completado, hito, responsables
  (recursos asignados), predecesoras, costo y costo real.
- Dependencias: fin-inicio sin desfase quedan en `predecesoras`. Las de otro tipo (inicio-inicio, fin-fin, inicio-fin)
  o con desfase se registran en `comentario` (ej. "MSP: T12 CC+5d") y se informan, porque la ruta crítica del harness
  usa fin-inicio; las fechas de MS Project se conservan tal cual, así que el cronograma no cambia.
- Costos: MS Project guarda los montos en centavos en el XML; se dividen por 100 (usa --costos-sin-centavos si tu
  archivo ya viene en unidades). Revisa el total informado contra MS Project.
- En un programa (arquetipo programa), --mapa reparte cada rama de primer nivel a su subproyecto
  (subproyectos/<id>/cronograma/) y lo que no esté en el mapa queda en el cronograma del programa. Las dependencias
  entre ramas quedan como "sp1:T12".
- Por defecto NO reemplaza nada: escribe cronograma/importado-msproject.csv para revisar. Con --reemplazar respalda el
  cronograma.csv vigente en cronograma/respaldos/ y lo reemplaza. Con --linea-base guarda la línea base 0 de MS Project
  en cronograma/linea-base/<fecha>.csv.
"""
import argparse
import csv
import re
import shutil
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

CAMPOS = ["id", "subproyecto", "tarea", "responsable", "inicio_plan", "fin_plan", "inicio_real", "fin_real", "avance_pct",
          "predecesoras", "es_hito", "estado", "comentario", "costo_plan", "costo_real"]
TIPOS = {"0": "FF", "1": "FC", "2": "CF", "3": "CC"}  # fin-fin, fin-comienzo, comienzo-fin, comienzo-comienzo (como en MS Project en español)
NS = re.compile(r"^\{.*?\}")


def _t(nodo, tag, defecto=""):
    for h in list(nodo):
        if NS.sub("", h.tag) == tag:
            return (h.text or "").strip()
    return defecto


def _hijos(nodo, tag):
    return [h for h in list(nodo) if NS.sub("", h.tag) == tag]


def _fecha(v):
    return v[:10] if v and re.match(r"\d{4}-\d{2}-\d{2}", v) and not v.startswith("1984-01-01") else ""


def es_mspdi(ruta):
    try:
        cabeza = Path(ruta).read_text(encoding="utf-8", errors="replace")[:3000]
    except OSError:
        return False
    if "schemas.microsoft.com/project" in cabeza:
        return True
    return re.search(r"<Project[\s>]", cabeza) is not None and "<Tasks>" in Path(ruta).read_text(encoding="utf-8", errors="replace")


def leer_mspdi(ruta, nivel_sub=1, centavos=True):
    """Devuelve (nombre_proyecto, tareas, recursos, advertencias). Cada tarea: dict con campos del harness + extras."""
    raiz = ET.parse(ruta).getroot()
    nombre = _t(raiz, "Title") or _t(raiz, "Name") or Path(ruta).stem
    recursos = {}
    for r in (_hijos(raiz, "Resources")[0] if _hijos(raiz, "Resources") else []):
        uid = _t(r, "UID")
        if uid and _t(r, "Name"):
            recursos[uid] = _t(r, "Name")
    asig = {}
    for a in (_hijos(raiz, "Assignments")[0] if _hijos(raiz, "Assignments") else []):
        tuid, ruid = _t(a, "TaskUID"), _t(a, "ResourceUID")
        if ruid in recursos:
            unidades = _t(a, "Units") or "1"
            asig.setdefault(tuid, []).append((recursos[ruid], unidades))
    nodos = _hijos(raiz, "Tasks")[0] if _hijos(raiz, "Tasks") else []
    tareas, adv = [], []
    por_uid, pila = {}, {}
    for n in nodos:
        uid, tid = _t(n, "UID"), _t(n, "ID")
        nivel = int(_t(n, "OutlineLevel", "0") or 0)
        if _t(n, "IsNull") == "1" or nivel == 0 or not _t(n, "Name"):
            continue
        pila[nivel] = _t(n, "Name")
        for k in [k for k in pila if k > nivel]:
            del pila[k]
        if _t(n, "Summary") == "1":
            por_uid[uid] = {"uid": uid, "id": f"T{tid}", "resumen": True}
            continue
        sub = pila.get(nivel_sub, nombre) if nivel > nivel_sub else nombre
        costo, costo_r = _t(n, "Cost"), _t(n, "ActualCost")
        div = 100.0 if centavos else 1.0

        def monto(v):
            try:
                return f"{float(v) / div:.0f}" if v not in ("", None) else ""
            except ValueError:
                return ""
        pct = _t(n, "PercentComplete", "0") or "0"
        base = [b for b in _hijos(n, "Baseline") if _t(b, "Number", "0") == "0"]
        tarea = {"uid": uid, "id": f"T{tid}", "resumen": False, "subproyecto": sub, "tarea": _t(n, "Name"),
                 "responsable": "; ".join(x for x, _ in asig.get(uid, [])),
                 "asignaciones": asig.get(uid, []),
                 "inicio_plan": _fecha(_t(n, "Start")), "fin_plan": _fecha(_t(n, "Finish")),
                 "inicio_real": _fecha(_t(n, "ActualStart")), "fin_real": _fecha(_t(n, "ActualFinish")),
                 "avance_pct": pct, "es_hito": "si" if _t(n, "Milestone") == "1" else "no",
                 "estado": "terminada" if float(pct or 0) >= 100 else "en curso" if float(pct or 0) > 0 else "no iniciada",
                 "costo_plan": monto(costo), "costo_real": monto(costo_r),
                 "base_inicio": _fecha(_t(base[0], "Start")) if base else "", "base_fin": _fecha(_t(base[0], "Finish")) if base else "",
                 "links": [(_t(l, "PredecessorUID"), _t(l, "Type", "1"), _t(l, "LinkLag", "0"), _t(l, "LagFormat", "7"))
                           for l in _hijos(n, "PredecessorLink")],
                 "restriccion": _t(n, "ConstraintType", "0")}
        if not tarea["inicio_plan"] or not tarea["fin_plan"]:
            adv.append(f"{tarea['id']} '{tarea['tarea']}' sin fechas en MS Project.")
        tareas.append(tarea)
        por_uid[uid] = tarea
    # dependencias
    for t in tareas:
        fs, notas = [], []
        for puid, tipo, lag, _fmt in t["links"]:
            p = por_uid.get(puid)
            if not p:
                continue
            if p.get("resumen"):
                notas.append(f"depende de la tarea resumen {p['id']}")
                adv.append(f"{t['id']} depende de una tarea resumen ({p['id']}): revisa la dependencia en el harness.")
                continue
            try:
                dias = int(float(lag or 0)) / 4800  # LinkLag en décimas de minuto; 4800 = 1 día de 8 horas
            except ValueError:
                dias = 0
            if tipo == "1" and abs(dias) < 0.01:
                fs.append(p["uid"])
            else:
                desfase = f"{dias:+g}d" if abs(dias) >= 0.01 else ""
                notas.append(f"MSP: {p['id']} {TIPOS.get(tipo, tipo)}{desfase}")
                if tipo == "1":
                    fs.append(p["uid"])
        t["pred_uids"], t["notas"] = fs, notas
        if t["restriccion"] not in ("0", "1", ""):
            t["notas"].append("MSP: fecha con restricción")
    tipos_no_fc = sum(1 for t in tareas for n in t["notas"] if re.search(r"MSP: T\d+ (CC|FF|CF)", n))
    con_desfase = sum(1 for t in tareas for n in t["notas"] if re.search(r"MSP: T\d+ \w\w[+-]", n))
    if tipos_no_fc:
        adv.append(f"{tipos_no_fc} dependencia(s) no fin-comienzo (CC, FF o CF): quedan en el comentario; las fechas de MS Project se conservan.")
    if con_desfase:
        adv.append(f"{con_desfase} dependencia(s) con desfase: quedan en el comentario con su desfase.")
    return nombre, tareas, recursos, adv


def resumen_texto(ruta):
    """Texto legible del cronograma, para extraer_entrada (alta documental)."""
    nombre, tareas, recursos, adv = leer_mspdi(ruta)
    lineas = [f"Cronograma de MS Project: {nombre} · {len(tareas)} tareas · recursos: {', '.join(recursos.values()) or 'sin recursos'}", "",
              "| Id | Rama | Tarea | Responsable | Inicio | Fin | % | Hito | Predecesoras |", "|---|---|---|---|---|---|---|---|---|"]
    uid_id = {t["uid"]: t["id"] for t in tareas}
    for t in tareas:
        preds = ";".join(uid_id.get(u, "") for u in t["pred_uids"])
        lineas.append(f"| {t['id']} | {t['subproyecto']} | {t['tarea']} | {t['responsable']} | {t['inicio_plan']} | {t['fin_plan']} | "
                      f"{t['avance_pct']} | {t['es_hito']} | {preds} {' '.join(t['notas'])} |")
    return "\n".join(lineas + [""] + [f"- {a}" for a in adv])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("archivo")
    ap.add_argument("proyecto")
    ap.add_argument("--nivel-subproyecto", type=int, default=1, help="nivel de la tarea resumen que da el subproyecto (por defecto 1)")
    ap.add_argument("--mapa", default="", help='en un programa: "Rama de MS Project=id-subproyecto,..."')
    ap.add_argument("--reemplazar", action="store_true", help="reemplazar cronograma.csv (con respaldo)")
    ap.add_argument("--linea-base", action="store_true", help="guardar la línea base 0 de MS Project en cronograma/linea-base/")
    ap.add_argument("--costos-sin-centavos", action="store_true", help="los costos del XML ya vienen en unidades")
    a = ap.parse_args()
    archivo, raiz = Path(a.archivo), Path(a.proyecto)
    if archivo.suffix.lower() == ".mpp":
        sys.exit("El archivo .mpp no se puede leer directamente. En MS Project: Archivo > Guardar como > tipo 'XML' "
                 "(Formato XML de Project) y usa ese archivo.")
    if not archivo.exists():
        sys.exit(f"No existe {archivo}")
    if not es_mspdi(archivo):
        sys.exit("El archivo no parece un XML de MS Project (falta el esquema de Project o la lista de tareas).")
    if not (raiz / "proyecto.yaml").exists():
        sys.exit(f"No encuentro {raiz / 'proyecto.yaml'}")
    nombre, tareas, recursos, adv = leer_mspdi(archivo, a.nivel_subproyecto, centavos=not a.costos_sin_centavos)
    if not tareas:
        sys.exit("El XML no tiene tareas (no resumen) para importar.")

    mapa = {}
    for par in [x for x in a.mapa.split(",") if x.strip()]:
        if "=" not in par:
            sys.exit(f"Mapa inválido: {par!r} (usar \"Rama=id\")")
        rama, sid = par.split("=", 1)
        mapa[rama.strip().lower()] = sid.strip()
    destino_de = {}
    for t in tareas:
        sid = mapa.get(t["subproyecto"].lower(), "")
        if sid and not (raiz / "subproyectos" / sid / "proyecto.yaml").exists():
            sys.exit(f"El mapa envía '{t['subproyecto']}' a '{sid}', pero no existe subproyectos/{sid}/ (créalo antes con crear_proyecto.py --programa).")
        destino_de[t["uid"]] = sid
    if mapa:
        sin_mapa = sorted({t["subproyecto"] for t in tareas if not destino_de[t["uid"]]})
        if sin_mapa:
            adv.append(f"Ramas sin subproyecto en el mapa (quedan en el cronograma del programa): {', '.join(sin_mapa)}.")
    uid_t = {t["uid"]: t for t in tareas}
    grupos = {}
    for t in tareas:
        sid = destino_de[t["uid"]]
        preds = []
        for pu in t["pred_uids"]:
            p = uid_t[pu]
            psid = destino_de[pu]
            if psid == sid:
                preds.append(p["id"])
            else:
                preds.append(f"{psid or 'PRG'}:{p['id']}")
        fila = {k: t.get(k, "") for k in CAMPOS}
        fila["predecesoras"] = ";".join(preds)
        fila["comentario"] = " · ".join(t["notas"])
        grupos.setdefault(sid, []).append((fila, t))

    ahora = datetime.now().strftime("%Y-%m-%d-%H%M")
    total_costo = sum(float(t["costo_plan"] or 0) for t in tareas)
    print(f"# Importación de MS Project — {nombre}\n")
    print(f"- Tareas importadas: {len(tareas)} · hitos: {sum(1 for t in tareas if t['es_hito'] == 'si')} · "
          f"recursos: {len(recursos)} · costo planificado total: {total_costo:,.0f}".replace(",", "."))
    for sid, filas in grupos.items():
        carpeta = (raiz / "subproyectos" / sid) if sid else raiz
        cron = carpeta / "cronograma"
        cron.mkdir(parents=True, exist_ok=True)
        salida = cron / ("cronograma.csv" if a.reemplazar else "importado-msproject.csv")
        if a.reemplazar and salida.exists():
            (cron / "respaldos").mkdir(exist_ok=True)
            shutil.copy2(salida, cron / "respaldos" / f"cronograma-{ahora}.csv")
        with open(salida, "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=CAMPOS)
            w.writeheader()
            w.writerows(f for f, _ in filas)
        ramas = sorted({t["subproyecto"] for _, t in filas})
        print(f"- {len(filas)} tarea(s) → {salida.as_posix()} (ramas: {', '.join(ramas)})")
        if a.linea_base:
            con_base = [(f, t) for f, t in filas if t["base_inicio"] and t["base_fin"]]
            if con_base:
                (cron / "linea-base").mkdir(exist_ok=True)
                lb = cron / "linea-base" / f"{datetime.now():%Y-%m-%d}-msproject.csv"
                with open(lb, "w", encoding="utf-8", newline="") as fh:
                    w = csv.DictWriter(fh, fieldnames=CAMPOS)
                    w.writeheader()
                    w.writerows({**f, "inicio_plan": t["base_inicio"], "fin_plan": t["base_fin"]} for f, t in con_base)
                print(f"  línea base 0 de MS Project → {lb.as_posix()}")
            else:
                print("  (el XML no trae línea base 0 para estas tareas)")
    asignados = sorted({(n, u) for t in tareas for n, u in t["asignaciones"]})
    if asignados:
        print("\nRecursos asignados (unidades de MS Project, 1 = 100%): " + ", ".join(sorted({n for n, _ in asignados})))
    print("\nAdvertencias:" if adv else "\nSin advertencias.")
    for x in dict.fromkeys(adv):
        print(f"- {x}")
    if not a.reemplazar:
        print("\nVista previa: nada se reemplazó. Revisa el archivo importado y, si está bien, vuelve a ejecutar con --reemplazar.")


if __name__ == "__main__":
    import _consola
    _consola.preparar()
    main()
