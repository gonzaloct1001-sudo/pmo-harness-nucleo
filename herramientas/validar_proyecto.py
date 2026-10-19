#!/usr/bin/env python3
"""Chequeos automáticos de un proyecto del PMO Harness.

Uso:
    python herramientas/validar_proyecto.py proyectos/<slug> [--hoy AAAA-MM-DD] [--corte-actualizacion] [--salida archivo.md]

Revisa: datos pendientes, cronograma (fechas, dependencias, atrasos, plazo contractual),
riesgos, issues, acuerdos y control de cambios. Calcula el avance plan vs real por subproyecto.
Si existe obra/, revisa RFI, no conformidades, inspecciones y estados de pago.
Las secciones que no existen en el proyecto (según sus arquetipos) se omiten.
Para métricas, reglas y etapas de ítems, usar evaluar_metricas.py.
Imprime un informe en Markdown. No modifica ningún archivo del proyecto.

Fecha de corte del avance: el avance real del cronograma corresponde a su última actualización
(`cronograma_actualizado` en proyecto.yaml). Si es anterior a la fecha de corte, el informe lo advierte, porque
comparar el plan a hoy con un avance real antiguo exagera el atraso. Con --corte-actualizacion el avance
planificado se calcula a la fecha de esa actualización (recomendado para reportes).
"""
import argparse
import csv
import sys
from datetime import date, datetime
from pathlib import Path

import _config  # noqa: E402  (proyecto.yaml con herencia de programa)

try:
    import yaml
except ImportError:
    sys.exit("Falta pyyaml: pip install pyyaml")


def leer_csv(ruta):
    if not ruta.exists():
        return None
    with open(ruta, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def fecha(valor):
    valor = (valor or "").strip()
    if not valor or "PENDIENTE" in valor.upper():
        return None
    try:
        return datetime.strptime(valor, "%Y-%m-%d").date()
    except ValueError:
        return "invalida"


def numero(valor, defecto=0.0):  # noqa: D401
    try:
        return float(str(valor).replace(",", ".").strip())
    except (ValueError, AttributeError):
        return defecto


def es_si(valor):
    return str(valor).strip().lower() in ("si", "sí", "true", "1", "x", "yes")


ABIERTO = ("abierto", "abierta", "en curso", "pendiente", "activo", "activa", "")


class Informe:
    def __init__(self):
        self.criticos, self.advertencias, self.info = [], [], []

    def c(self, t):
        self.criticos.append(t)

    def a(self, t):
        self.advertencias.append(t)

    def i(self, t):
        self.info.append(t)


def buscar_pendientes(nodo, prefijo=""):
    encontrados = []
    if isinstance(nodo, dict):
        for k, v in nodo.items():
            if k == "induccion":
                continue
            encontrados += buscar_pendientes(v, f"{prefijo}{k}.")
    elif isinstance(nodo, str) and "PENDIENTE" in nodo.upper():
        encontrados.append(prefijo.rstrip("."))
    return encontrados


def avance_plan_tarea(t, hoy):
    ini, fin = fecha(t.get("inicio_plan")), fecha(t.get("fin_plan"))
    if not isinstance(ini, date) or not isinstance(fin, date):
        return None
    if hoy < ini:
        return 0.0
    if hoy >= fin:
        return 100.0
    total = (fin - ini).days or 1
    return 100.0 * (hoy - ini).days / total


def duracion(t):
    ini, fin = fecha(t.get("inicio_plan")), fecha(t.get("fin_plan"))
    if isinstance(ini, date) and isinstance(fin, date):
        return max((fin - ini).days, 1)
    return 1


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("proyecto")
    p.add_argument("--hoy", help="fecha de corte AAAA-MM-DD (por defecto, hoy)")
    p.add_argument("--corte-actualizacion", action="store_true",
                   help="calcular el avance planificado a la fecha de la última actualización del cronograma")
    p.add_argument("--cronograma", help="archivo de cronograma alternativo (por defecto cronograma/cronograma.csv)")
    p.add_argument("--salida", help="guardar el informe en este archivo .md")
    p.add_argument("--json", action="store_true", help="entregar hallazgos, avance y conteos en JSON (lo usa status.py)")
    args = p.parse_args()

    raiz = Path(args.proyecto)
    if not (raiz / "proyecto.yaml").exists():
        sys.exit(f"No encuentro {raiz / 'proyecto.yaml'}")
    hoy = datetime.strptime(args.hoy, "%Y-%m-%d").date() if args.hoy else date.today()

    cfg = _config.cargar(raiz)
    um = cfg.get("umbrales", {}) or {}
    amarillo = numero(um.get("desvio_amarillo_pct", 5), 5)
    rojo = numero(um.get("desvio_rojo_pct", 10), 10)
    inf = Informe()

    # --- Inducción ---
    pend = buscar_pendientes(cfg)
    estado_ind = (cfg.get("induccion") or {}).get("estado", "pendiente")
    if pend:
        inf.a(f"Alta '{estado_ind}': {len(pend)} campo(s) pendiente(s) en proyecto.yaml: {', '.join(pend)}.")

    lb = cfg.get("linea_base", {}) or {}
    termino = fecha(str(lb.get("fecha_termino_vigente", "")))
    actualizado = fecha(str(cfg.get("cronograma_actualizado") or ""))
    corte_plan = hoy
    if isinstance(actualizado, date) and actualizado < hoy:
        if args.corte_actualizacion:
            corte_plan = actualizado
            inf.i(f"Avance planificado calculado al {actualizado} (última actualización del cronograma), no al {hoy}.")
        else:
            inf.a(f"El avance real del cronograma no se actualiza desde el {actualizado} ({(hoy - actualizado).days} días): "
                  f"el plan está calculado al {hoy} y el atraso puede verse mayor al real. Actualiza el avance o usa --corte-actualizacion.")

    # --- Cronograma ---
    tareas = leer_csv(Path(args.cronograma) if args.cronograma else raiz / "cronograma" / "cronograma.csv") or []
    ids = {t.get("id", "").strip() for t in tareas}
    por_id = {t.get("id", "").strip(): t for t in tareas}
    subproyectos = {}
    for t in tareas:
        tid = t.get("id", "").strip()
        ini, fin = fecha(t.get("inicio_plan")), fecha(t.get("fin_plan"))
        av = numero(t.get("avance_pct"))
        for campo in ("inicio_plan", "fin_plan", "inicio_real", "fin_real"):
            if fecha(t.get(campo)) == "invalida":
                inf.c(f"Cronograma {tid}: fecha inválida en '{campo}' ({t.get(campo)}). Usar AAAA-MM-DD.")
        if isinstance(ini, date) and isinstance(fin, date) and fin < ini:
            inf.c(f"Cronograma {tid}: fin_plan ({fin}) es anterior a inicio_plan ({ini}).")
        if not 0 <= av <= 100:
            inf.c(f"Cronograma {tid}: avance fuera de rango ({av}%).")
        for pred in [x.strip() for x in (t.get("predecesoras") or "").replace(";", ",").split(",") if x.strip()]:
            if ":" in pred:
                inf.i(f"Cronograma {tid} depende de '{pred}' (otro subproyecto): se verifica con programa.py.")
            elif pred not in ids:
                inf.c(f"Cronograma {tid}: predecesora '{pred}' no existe.")
            else:
                if av > 0 and numero(por_id[pred].get("avance_pct")) < 100:
                    inf.a(f"Cronograma {tid} tiene avance ({av:.0f}%) pero su predecesora {pred} no está terminada ({numero(por_id[pred].get('avance_pct')):.0f}%).")
                fin_pred = fecha(por_id[pred].get("fin_plan"))
                if isinstance(ini, date) and isinstance(fin_pred, date) and ini < fin_pred:
                    inf.a(f"Cronograma {tid} comienza el {ini}, antes de que termine su predecesora {pred} ({fin_pred}).")
        if isinstance(fin, date) and fin < hoy and av < 100:
            tipo = "Hito vencido" if es_si(t.get("es_hito")) else "Tarea atrasada"
            (inf.c if es_si(t.get("es_hito")) else inf.a)(
                f"{tipo} {tid} '{t.get('tarea')}': fin plan {fin}, avance {av:.0f}%.")
        if isinstance(termino, date) and isinstance(fin, date) and fin > termino:
            inf.c(f"Cronograma {tid} '{t.get('tarea')}' termina el {fin}, después del término contractual vigente ({termino}).")
        sp = (t.get("subproyecto") or "Sin subproyecto").strip()
        if es_si(t.get("es_hito")):
            continue  # los hitos no pesan en el avance
        d = duracion(t)
        ap = avance_plan_tarea(t, corte_plan)
        acc = subproyectos.setdefault(sp, {"peso": 0, "plan": 0.0, "real": 0.0})
        acc["peso"] += d
        acc["plan"] += d * (ap or 0)
        acc["real"] += d * av
    arquetipos = cfg.get("arquetipos") or []
    if not tareas and ("ejecucion" in arquetipos or not arquetipos):
        inf.a("El cronograma está vacío.")

    tabla_avance = []
    for sp, acc in sorted(subproyectos.items()):
        plan = acc["plan"] / acc["peso"] if acc["peso"] else 0
        real = acc["real"] / acc["peso"] if acc["peso"] else 0
        desv = real - plan
        estado = "Verde"
        if desv <= -rojo:
            estado = "Rojo"
        elif desv <= -amarillo:
            estado = "Amarillo"
        tabla_avance.append((sp, plan, real, desv, estado))

    # --- Riesgos ---
    riesgos = leer_csv(raiz / "riesgos" / "riesgos.csv") or []
    for r in riesgos:
        rid = r.get("id", "")
        if (r.get("estado") or "").strip().lower() in ("cerrado", "cerrada"):
            continue
        sev = numero(r.get("severidad")) or numero(r.get("probabilidad")) * numero(r.get("impacto"))
        if sev >= 15 and not (r.get("plan_accion") or "").strip():
            inf.c(f"Riesgo {rid} '{r.get('titulo')}' tiene severidad alta ({sev:.0f}) y no tiene plan de acción.")
        if not (r.get("responsable") or "").strip():
            inf.a(f"Riesgo {rid} '{r.get('titulo')}' no tiene responsable.")
        fr = fecha(r.get("fecha_revision"))
        if isinstance(fr, date) and fr < hoy:
            inf.a(f"Riesgo {rid} '{r.get('titulo')}': revisión vencida desde {fr}.")

    # --- Issues y acuerdos ---
    for nombre, archivo, campo_fecha in (("Issue", raiz / "riesgos" / "issues.csv", "fecha_compromiso"),
                                         ("Acuerdo", raiz / "seguimiento" / "acuerdos.csv", "fecha_compromiso")):
        for x in leer_csv(archivo) or []:
            est = (x.get("estado") or "").strip().lower()
            fc = fecha(x.get(campo_fecha))
            if est in ABIERTO and isinstance(fc, date) and fc < hoy:
                texto = x.get("titulo") or x.get("acuerdo") or ""
                inf.a(f"{nombre} {x.get('id')} vencido desde {fc}: '{texto}' (responsable: {x.get('responsable') or 'sin asignar'}).")

    # --- Control de cambios ---
    for cc in leer_csv(raiz / "contractual" / "cambios" / "registro-cambios.csv") or []:
        est = (cc.get("estado") or "").strip().lower()
        fs = fecha(cc.get("fecha_solicitud"))
        if est == "aprobada" and not (cc.get("documento_formal") or "").strip():
            inf.a(f"Cambio {cc.get('id')} aprobado pero sin documento formal (enmienda o acta).")
        if est in ("registrada", "en_analisis") and isinstance(fs, date) and (hoy - fs).days > 30:
            inf.a(f"Cambio {cc.get('id')} lleva {(hoy - fs).days} días sin resolverse.")

    # --- Obra (si existe la carpeta obra/) ---
    abiertos = ("abierta", "abierto", "pendiente", "en curso", "")
    for r in leer_csv(raiz / "obra" / "rfi.csv") or []:
        pl = fecha(r.get("plazo_respuesta"))
        if (r.get("estado") or "").strip().lower() in abiertos and not (r.get("fecha_respuesta") or "").strip() \
                and isinstance(pl, date) and pl < hoy:
            inf.a(f"RFI {r.get('id')} sin respuesta, vencida desde {pl}: '{r.get('tema')}' (impacto: {r.get('impacto') or 'sin evaluar'}).")
    for r in leer_csv(raiz / "obra" / "no-conformidades.csv") or []:
        if (r.get("estado") or "").strip().lower() in abiertos:
            fc = fecha(r.get("fecha_compromiso"))
            sev = (r.get("severidad") or "").strip().lower()
            if sev == "critica" or sev == "crítica":
                inf.c(f"No conformidad crítica abierta {r.get('id')}: '{r.get('descripcion')}'.")
            elif isinstance(fc, date) and fc < hoy:
                inf.a(f"No conformidad {r.get('id')} vencida desde {fc}: '{r.get('descripcion')}'.")
            if not (r.get("accion_correctiva") or "").strip():
                inf.a(f"No conformidad {r.get('id')} sin acción correctiva definida.")
    for r in leer_csv(raiz / "obra" / "inspecciones.csv") or []:
        fp = fecha(r.get("fecha_programada"))
        if (r.get("resultado") or "").strip().lower() in ("", "pendiente") and isinstance(fp, date) and fp < hoy:
            inf.a(f"Inspección {r.get('id')} ({r.get('tipo')}, {r.get('partida')}) programada para {fp} sin resultado registrado.")
        if (r.get("resultado") or "").strip().lower() == "rechazada":
            inf.i(f"Inspección {r.get('id')} rechazada ({r.get('partida')}): verificar reinspección.")
    avance_total = None
    if subproyectos:
        peso = sum(x["peso"] for x in subproyectos.values())
        avance_total = sum(x["real"] for x in subproyectos.values()) / peso if peso else None
    for r in leer_csv(raiz / "obra" / "estados-pago.csv") or []:
        est = (r.get("estado") or "").strip().lower()
        fp = fecha(r.get("fecha_presentacion"))
        if est in ("presentado", "en revisión", "en revision") and isinstance(fp, date) and (hoy - fp).days > 15:
            inf.a(f"Estado de pago {r.get('id')} presentado hace {(hoy - fp).days} días sin aprobación.")
        decl = numero(r.get("avance_declarado_pct"), None) if (r.get("avance_declarado_pct") or "").strip() else None
        if decl is not None and avance_total is not None and est not in ("pagado",) and abs(decl - avance_total) > 5:
            inf.a(f"Estado de pago {r.get('id')} declara {decl:.0f}% de avance y el cronograma indica {avance_total:.0f}%.")

    if args.json:
        import json
        cuenta = lambda lista, cond: sum(1 for x in lista if cond(x))  # noqa: E731
        conteos = {
            "hitos_vencidos": cuenta(inf.criticos, lambda x: x.startswith("Hito vencido")),
            "tareas_atrasadas": cuenta(inf.advertencias, lambda x: x.startswith("Tarea atrasada")),
            "acuerdos_vencidos": cuenta(inf.advertencias, lambda x: x.startswith("Acuerdo ") and "vencido" in x),
            "issues_vencidos": cuenta(inf.advertencias, lambda x: x.startswith("Issue ") and "vencido" in x),
            "riesgos_altos_sin_plan": cuenta(inf.criticos, lambda x: "no tiene plan de acción" in x),
            "fuera_de_plazo_contractual": cuenta(inf.criticos, lambda x: "después del término contractual" in x),
            "cambios_sin_resolver": cuenta(inf.advertencias, lambda x: x.startswith("Cambio ") and "sin resolverse" in x),
        }
        peso = sum(x["peso"] for x in subproyectos.values())
        total = ({"plan": sum(x["plan"] for x in subproyectos.values()) / peso, "real": sum(x["real"] for x in subproyectos.values()) / peso}
                 if peso else None)
        print(json.dumps({"criticos": inf.criticos, "advertencias": inf.advertencias, "info": inf.info, "conteos": conteos,
                          "avance_total": total, "termino_contractual": termino if isinstance(termino, date) else None,
                          "avance": [{"subproyecto": sp, "plan": pl, "real": re_, "desviacion": dv, "estado": es}
                                     for sp, pl, re_, dv, es in tabla_avance]}, ensure_ascii=False, default=str))
        return

    # --- Informe ---
    nombre = (cfg.get("proyecto") or {}).get("nombre", raiz.name)
    out = [f"# Validación automática — {nombre}", "", f"Fecha de corte: {hoy.isoformat()}", ""]
    if tabla_avance:
        nota = f" · plan al {corte_plan}" if corte_plan != hoy else ""
        out += [f"## Avance por subproyecto (ponderado por duración{nota})", "",
                "| Subproyecto | Avance plan % | Avance real % | Desviación (pts) | Estado |",
                "|---|---|---|---|---|"]
        for sp, plan, real, desv, estado in tabla_avance:
            out.append(f"| {sp} | {plan:.0f} | {real:.0f} | {desv:+.0f} | {estado} |")
    for titulo, lista in (("Crítico", inf.criticos), ("Advertencias", inf.advertencias), ("Información", inf.info)):
        out += ["", f"## {titulo} ({len(lista)})", ""]
        out += [f"- {x}" for x in lista] or ["- Sin hallazgos."]
    texto = "\n".join(out) + "\n"
    if args.salida:
        Path(args.salida).parent.mkdir(parents=True, exist_ok=True)
        Path(args.salida).write_text(texto, encoding="utf-8")
    print(texto)


if __name__ == "__main__":
    import _consola
    _consola.preparar()
    main()
