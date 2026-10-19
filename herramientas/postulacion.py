#!/usr/bin/env python3
"""Estado de una postulación (arquetipo postulacion): etapa, compuerta, cumplimiento, vencimientos y red team.

Uso:
    python herramientas/postulacion.py proyectos/<slug> [--hoy AAAA-MM-DD] [--registrar] [--salida estado.md]

Lee proyecto.yaml (bloque postulacion), postulacion/etapas.yaml, requisitos.csv, barrido-requisitos.csv,
calendario.csv, consultas.csv, pauta-inversa.yaml, propuesta/*.md, economico/controles.csv, riesgos/riesgos.csv,
redteam/puntajes.csv y observaciones.csv, contenidos/registro.csv y entrega/final/.

Calcula las métricas del arquetipo (ver metricas/metricas-postulacion.yaml), evalúa la compuerta de la etapa
actual y de las siguientes, alerta vencimientos del calendario y consultas, y estima el puntaje de la propuesta
con los puntajes del red team y la pauta inversa. Con --registrar guarda las métricas en metricas/mediciones.csv.
No modifica ningún otro archivo.
"""
import argparse
import csv
import operator
import re
import sys
from datetime import date, datetime
from pathlib import Path

import yaml

import _config  # noqa: E402  (empresa dueña del proyecto: banco común de contenidos)
import _mediciones  # noqa: E402  (escritura segura de mediciones.csv)

import autoria  # noqa: E402  (módulo del harness en herramientas/)

FUENTE = "herramientas/postulacion.py"
OPS = {"<=": operator.le, "<": operator.lt, ">=": operator.ge, ">": operator.gt, "==": operator.eq, "!=": operator.ne}
CERRADO_REQ = ("cumplido", "no_aplica")
CERRADA_OBS = ("cerrada", "cerrado", "rechazada", "rechazado", "descartada", "descartado", "resuelta", "resuelto")


def leer(ruta):
    if not ruta.exists():
        return []
    with open(ruta, encoding="utf-8-sig", newline="") as f:
        return [r for r in csv.DictReader(f) if any((v or "").strip() for v in r.values())]


def cargar_yaml(ruta):
    return (yaml.safe_load(ruta.read_text(encoding="utf-8")) or {}) if ruta.exists() else {}


def fecha(v):
    try:
        return datetime.strptime(str(v or "").strip(), "%Y-%m-%d").date()
    except ValueError:
        return None


def num(v):
    try:
        return float(str(v).replace(",", ".").strip())
    except (TypeError, ValueError):
        return None


def norm(v):
    """Estado normalizado: minúsculas, sin espacios extremos, espacios internos como guion bajo."""
    return re.sub(r"\s+", "_", str(v or "").strip().lower())


def si(v):
    return str(v or "").strip().lower() in ("si", "sí", "true", "1", "x", "yes")


def frontmatter(ruta):
    t = ruta.read_text(encoding="utf-8", errors="replace")
    m = re.match(r"^---\s*\n(.*?)\n---", t, re.S)
    try:
        return (yaml.safe_load(m.group(1)) or {}) if m else {}
    except yaml.YAMLError:
        return {}


def puntaje_redteam(raiz, pauta):
    """Puntaje ponderado por perspectiva según la pauta inversa. Por cada perspectiva y criterio se usa el último
    puntaje registrado (en orden del archivo), así una ronda de verificación parcial (roja-2) actualiza solo lo
    que revisó y conserva el resto de la ronda anterior."""
    criterios = {c.get("id"): num(c.get("ponderacion")) or 0 for c in (pauta.get("criterios") or []) if c.get("id")}
    filas = leer(raiz / "redteam" / "puntajes.csv")
    rondas = list(dict.fromkeys(r["ronda"] for r in filas if r.get("ronda")))
    if not criterios or not filas:
        return None, rondas
    ultima = rondas[-1]
    por_persp = {}
    for r in filas:
        if r.get("criterio") not in criterios or num(r.get("puntaje")) is None:
            continue
        por_persp.setdefault(r.get("perspectiva"), {})[r["criterio"]] = num(r["puntaje"])
    resultado = {}
    for persp, pts in por_persp.items():
        completo = set(pts) == set(criterios)
        resultado[persp] = {"ponderado": sum(pts.get(c, 0) * w for c, w in criterios.items()), "completo": completo, "puntajes": pts}
    return {"ronda": ultima, "perspectivas": resultado}, rondas


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("proyecto")
    ap.add_argument("--hoy", help="fecha de corte AAAA-MM-DD (por defecto, hoy)")
    ap.add_argument("--registrar", action="store_true", help="guardar las métricas en metricas/mediciones.csv")
    ap.add_argument("--salida")
    ap.add_argument("--json", action="store_true", help="entregar métricas y hallazgos en JSON (lo usa status.py)")
    a = ap.parse_args()
    raiz = Path(a.proyecto)
    hoy = fecha(a.hoy) if a.hoy else date.today()
    if hoy is None:
        sys.exit(f"Fecha de corte inválida: {a.hoy} (usar AAAA-MM-DD).")
    cfg = cargar_yaml(raiz / "proyecto.yaml")
    pos = cfg.get("postulacion") or {}
    if not pos:
        sys.exit("El proyecto no tiene bloque `postulacion` en proyecto.yaml (¿falta el arquetipo postulacion?).")
    etapas = (cargar_yaml(raiz / "postulacion" / "etapas.yaml").get("etapas")) or []
    pauta = cargar_yaml(raiz / "postulacion" / "pauta-inversa.yaml")
    m, crit, adv, info = {}, [], [], []

    # --- Cierre ---
    cierre = fecha(pos.get("fecha_cierre"))
    m["dias_al_cierre"] = (cierre - hoy).days if cierre else None

    # --- Matriz de cumplimiento ---
    reqs = leer(raiz / "postulacion" / "requisitos.csv")
    m["requisitos_total"] = len(reqs)
    cerrados = [r for r in reqs if (r.get("estado") or "").strip().lower() in CERRADO_REQ]
    m["cumplimiento_pct"] = len(cerrados) / len(reqs) if reqs else 0.0
    exc_pend = [r for r in reqs if si(r.get("excluyente")) and (r.get("estado") or "").strip().lower() not in CERRADO_REQ]
    m["excluyentes_pendientes"] = len(exc_pend)
    sin_resp = [r for r in reqs if (r.get("estado") or "").strip().lower() not in CERRADO_REQ and not (r.get("responsable") or "").strip()]
    m["requisitos_sin_responsable"] = len(sin_resp)
    sin_ev = [r for r in reqs if (r.get("estado") or "").strip().lower() == "cumplido" and not (r.get("evidencia") or "").strip()]
    m["requisitos_sin_evidencia"] = len(sin_ev)
    for r in sin_ev:
        adv.append(f"Requisito {r.get('id')} marcado cumplido sin evidencia: {r.get('texto_requisito', '')[:90]}")
    if str(pos.get("declaracion_ia_exigida", "")).lower() == "si":
        info.append("Las bases exigen declarar o restringen el uso de herramientas de IA: la decisión y la declaración son del postulante.")

    # --- Barrido ---
    barrido = leer(raiz / "postulacion" / "barrido-requisitos.csv")
    m["barrido_total"] = len(barrido)
    pend_b = [b for b in barrido if (b.get("estado_revision") or "pendiente").strip().lower() == "pendiente"]
    m["barrido_sin_revisar"] = len(pend_b)
    ids_req = {r.get("id") for r in reqs}
    for b in barrido:
        est = (b.get("estado_revision") or "").strip().lower()
        if est == "incorporado" and b.get("requisito_id") and not all(x.strip() in ids_req for x in b["requisito_id"].split(";") if x.strip()):
            adv.append(f"Barrido {b.get('id')} dice incorporado a {b.get('requisito_id')}, que no existe en la matriz.")
        if est == "descartado" and not (b.get("motivo_descarte") or "").strip():
            adv.append(f"Barrido {b.get('id')} descartado sin motivo.")
    exc_b = [b for b in pend_b if b.get("excluyente_sugerido") == "si"]
    for b in exc_b[:10]:
        crit.append(f"Candidato con lenguaje de exclusión sin revisar {b.get('id')} [{b.get('documento')} · {b.get('ubicacion')}]: {b.get('texto', '')[:120]}")
    ia_b = [b for b in pend_b if "uso de IA" in (b.get("datos_detectados") or "")]
    for b in ia_b:
        crit.append(f"Las bases mencionan inteligencia artificial ({b.get('id')}, {b.get('documento')}): revisar si exigen declarar o restringen su uso.")

    # --- Calendario ---
    cal = leer(raiz / "postulacion" / "calendario.csv")
    m["calendario_con_cierre"] = 1 if any((c.get("tipo") or "").strip().lower() == "cierre" and fecha(c.get("fecha")) for c in cal) else 0
    proximos = []
    for c in cal:
        f = fecha(c.get("fecha"))
        if (c.get("fecha") or "").strip() and f is None:
            adv.append(f"Calendario {c.get('id')}: fecha inválida '{c.get('fecha')}' (usar AAAA-MM-DD).")
        est = (c.get("estado") or "pendiente").strip().lower()
        if not f or est in ("cumplido", "no_aplica"):
            continue
        dias = (f - hoy).days
        alerta = int(num(c.get("alerta_dias")) or 3)
        texto = f"{c.get('hito')} ({c.get('tipo')}) el {f}{' ' + c['hora'] if c.get('hora') else ''}"
        if dias < 0:
            crit.append(f"Hito vencido sin marcar cumplido: {texto}.")
        elif dias <= alerta:
            (crit if (c.get("tipo") or "").lower() in ("cierre", "consultas", "garantia") else adv).append(f"Vence en {dias} día(s): {texto}.")
        if 0 <= dias <= 14:
            proximos.append((dias, texto))

    # --- Consultas ---
    cons = leer(raiz / "postulacion" / "consultas.csv")
    m["consultas_por_enviar"] = sum(1 for c in cons if (c.get("estado") or "").strip().lower() in ("borrador", ""))
    m["consultas_sin_respuesta"] = sum(1 for c in cons if (c.get("estado") or "").strip().lower() == "enviada" and not (c.get("respuesta") or "").strip())
    plazo_consultas = [fecha(c.get("fecha")) for c in cal if (c.get("tipo") or "").strip().lower() == "consultas" and fecha(c.get("fecha"))]
    if m["consultas_por_enviar"] and plazo_consultas:
        dias = (min(plazo_consultas) - hoy).days
        (crit if dias <= 2 else adv).append(f"{m['consultas_por_enviar']} consulta(s) por enviar; el plazo de consultas vence en {dias} día(s).")

    # --- Pauta inversa y propuesta ---
    criterios = [c for c in (pauta.get("criterios") or []) if c.get("id")]
    m["pauta_criterios"] = len(criterios)
    suma_w = sum(num(c.get("ponderacion")) or 0 for c in criterios)
    if criterios and abs(suma_w - 1) > 0.001:
        adv.append(f"Las ponderaciones de la pauta inversa suman {suma_w:.2f} (deben sumar 1).")
    secciones = sorted(p for p in (raiz / "propuesta").glob("*.md") if not p.name.startswith("_") and p.name.upper() != "LEEME.MD")
    m["secciones_total"] = len(secciones)
    declarados = set()
    sin_traz = []
    for s in secciones:
        fm = frontmatter(s)
        resp = [str(x).strip() for x in (fm.get("responde_a") or []) if str(x).strip()]
        declarados |= set(resp)
        if not resp:
            sin_traz.append(s.name)
        desconocidos = [x for x in resp if x not in ids_req and x not in {c["id"] for c in criterios}]
        if desconocidos:
            adv.append(f"Sección {s.name} declara ids que no existen en la matriz ni en la pauta: {', '.join(desconocidos)}.")
    m["secciones_sin_trazabilidad"] = len(sin_traz)
    for n in sin_traz:
        adv.append(f"Sección {n} sin trazabilidad (responde_a vacío).")
    crit_sin = [c["id"] for c in criterios if c["id"] not in declarados]
    m["criterios_sin_seccion"] = len(crit_sin) if secciones else len(criterios)
    if secciones and crit_sin:
        adv.append(f"Criterios de la pauta que ninguna sección declara responder: {', '.join(crit_sin)}.")
    tecnicos = [r for r in reqs if (r.get("tipo") or "").lower() == "tecnico" and (r.get("estado") or "").lower() not in CERRADO_REQ]
    if secciones:
        sin_sec = [r["id"] for r in tecnicos if r.get("id") not in declarados and not (r.get("evidencia") or "").strip()]
        if sin_sec:
            adv.append(f"Requisitos técnicos abiertos sin sección ni evidencia: {', '.join(sin_sec[:15])}.")

    # --- Económico ---
    ctrl = leer(raiz / "economico" / "controles.csv")
    malos = [c for c in ctrl if (c.get("estado") or "").upper() == "NO CUMPLE"]
    m["controles_economicos_incumplidos"] = len(malos)
    total = next((num(c.get("valor")) for c in ctrl if c.get("id") == "CTL-00"), None)
    m["presupuesto_con_datos"] = 1 if total and total > 0 else 0
    if ctrl and not m["presupuesto_con_datos"]:
        adv.append("El presupuesto no tiene partidas con costo (CTL-00): los controles aún no significan nada.")
    basicos = [c for c in ctrl if c.get("id") in ("CTL-01", "CTL-02", "CTL-03", "CTL-04")]
    if basicos and all((c.get("estado") or "").upper() == "SIN REGLA" for c in basicos):
        adv.append("Ninguna regla de financiamiento cargada en presupuesto.yaml: confirma en las bases que de verdad no existen.")
    for c in malos:
        crit.append(f"Presupuesto: {c.get('id')} NO CUMPLE — {c.get('control')} (valor {c.get('valor')}, límite {c.get('limite')}).")
    presupuesto_yaml = raiz / "economico" / "presupuesto.yaml"
    xlsx = raiz / "economico" / "presupuesto.xlsx"
    ctrl_csv = raiz / "economico" / "controles.csv"
    if ctrl and presupuesto_yaml.exists() and presupuesto_yaml.stat().st_mtime > ctrl_csv.stat().st_mtime:
        adv.append("presupuesto.yaml cambió después de calcular los controles: vuelve a ejecutar presupuesto_postulacion.py.")
    if ctrl and xlsx.exists() and xlsx.stat().st_mtime > ctrl_csv.stat().st_mtime + 120:
        adv.append("presupuesto.xlsx se modificó después de calcular los controles: la fuente es presupuesto.yaml; lleva los "
                   "cambios al YAML y regenera (el Excel es de salida y los controles de la compuerta salen del YAML).")

    # --- Riesgos ---
    riesgos = [r for r in leer(raiz / "riesgos" / "riesgos.csv") if (r.get("estado") or "").lower() not in ("cerrado", "cerrada")]
    m["riesgos_registrados"] = len(riesgos)

    # --- Red team ---
    rt, rondas = puntaje_redteam(raiz, pauta)
    obs = leer(raiz / "redteam" / "observaciones.csv")
    rondas = list(dict.fromkeys(rondas + [o["ronda"] for o in obs if o.get("ronda")]))
    m["rondas_redteam"] = len(rondas)
    ff = [o for o in obs if norm(o.get("tipo")) == "falla_fatal" and norm(o.get("estado")) not in CERRADA_OBS]
    m["fallas_fatales_abiertas"] = len(ff)
    for o in ff:
        crit.append(f"Falla fatal abierta {o.get('id')} ({o.get('perspectiva')}, {o.get('seccion')}): {o.get('observacion', '')[:120]}")
    m["observaciones_abiertas"] = sum(1 for o in obs if norm(o.get("estado")) not in CERRADA_OBS)
    umbr = pauta.get("umbrales") or {}
    pmin, pobj = num(umbr.get("puntaje_minimo")) or 0, num(umbr.get("puntaje_objetivo")) or 0
    objetivo = max(pmin, pobj)
    m["puntaje_redteam"] = m["puntaje_redteam_min"] = m["dispersion_redteam"] = None
    m["redteam_sobre_objetivo"] = 0
    tabla_rt = []
    if rt and rt["perspectivas"]:
        vals = [v["ponderado"] for v in rt["perspectivas"].values() if v["completo"]]
        for persp, v in rt["perspectivas"].items():
            tabla_rt.append((persp, v["ponderado"], v["completo"]))
            if not v["completo"]:
                adv.append(f"Red team ronda {rt['ronda']}: la perspectiva {persp} no puntuó todos los criterios (se excluye del promedio).")
        if vals:
            m["puntaje_redteam"] = sum(vals) / len(vals)
            m["puntaje_redteam_min"] = min(vals)
            m["dispersion_redteam"] = max(vals) - min(vals)
            minimos = umbr.get("minimo_por_criterio") or {}
            bajo_min = []
            for cid, minimo in minimos.items():
                prom = [v["puntajes"].get(cid) for v in rt["perspectivas"].values() if v["completo"] and v["puntajes"].get(cid) is not None]
                if prom and sum(prom) / len(prom) < (num(minimo) or 0):
                    bajo_min.append(cid)
            m["redteam_sobre_objetivo"] = 1 if objetivo > 0 and m["puntaje_redteam"] >= objetivo and not bajo_min else 0
            if objetivo <= 0:
                adv.append("La pauta inversa no tiene puntaje_minimo ni puntaje_objetivo: la compuerta del red team no puede cumplirse.")
            if bajo_min:
                crit.append(f"Red team: criterios bajo el mínimo por criterio de las bases: {', '.join(bajo_min)}.")
            if m["dispersion_redteam"] >= 1:
                adv.append(f"Red team: dispersión alta entre revisores ({m['dispersion_redteam']:.2f} puntos): revisar los criterios en que difieren.")

    # --- Contenidos (banco de la postulación y banco común de la empresa) ---
    cont = leer(raiz / "contenidos" / "registro.csv")
    emp = _config.raiz_empresa(raiz)
    if emp is not None:
        propios = {(c.get("id") or "").strip() for c in cont}
        cont += [c for c in leer(emp / "contenidos" / "registro.csv") if (c.get("id") or "").strip() not in propios]
    ref = cierre or hoy
    venc = [c for c in cont if fecha(c.get("vigente_hasta")) and fecha(c.get("vigente_hasta")) < ref]
    for c in cont:
        if (c.get("vigente_hasta") or "").strip() and fecha(c.get("vigente_hasta")) is None:
            venc.append(c)
            adv.append(f"Contenido {c.get('id')}: vigencia '{c.get('vigente_hasta')}' inválida (usar AAAA-MM-DD); se trata como vencido.")
    m["contenidos_vencidos"] = len(venc)
    for c in venc:
        crit.append(f"Documento vencido al cierre: {c.get('titulo')} (vigente hasta {c.get('vigente_hasta')}).")

    # --- Autoría del paquete final ---
    final = raiz / "entrega" / "final"
    errores_aut = 0
    entregables = [p for p in final.rglob("*") if p.is_file() and p.name != ".gitkeep"] if final.exists() else []
    m["entrega_archivos"] = len(entregables)
    if final.exists():
        aut = autoria.cargar_autoria(raiz)
        for f in sorted(p for p in final.rglob("*") if p.is_file() and p.suffix.lower() in (".docx", ".xlsx", ".pptx", ".pdf", ".md", ".txt")):
            e, _ = autoria.revisar_archivo(f, aut)
            if e:
                errores_aut += len(e)
                adv.append(f"Autoría: {f.name} tiene {len(e)} error(es): ejecuta verificar_autoria.py --corregir y revisa el texto.")
    m["entrega_autoria_errores"] = errores_aut

    # --- Formulario de la plataforma (postulacion/formulario.yaml, si existe) ---
    import formulario as _formulario
    mf, _, _, adv_f, _ = _formulario.controlar(raiz)
    m.update(mf)
    if mf["formulario_campos"]:
        cerca = cierre is not None and m["dias_al_cierre"] is not None and m["dias_al_cierre"] <= 3
        (crit if cerca else adv).extend(adv_f[:12])

    # --- Alertas de cierre ---
    if cierre is not None:
        d = m["dias_al_cierre"]
        if d < 0 and str(pos.get("resultado", "pendiente")) == "pendiente" and pos.get("etapa") not in ("post_entrega", "cierre") \
                and norm(pos.get("decision_go")) != "no_go":
            crit.append(f"La fecha de cierre ({cierre}) ya pasó y la postulación no figura entregada.")
        elif 0 <= d <= 3 and m["excluyentes_pendientes"]:
            crit.append(f"Faltan {d} día(s) para el cierre y hay {m['excluyentes_pendientes']} requisito(s) excluyente(s) pendiente(s).")
    for r in exc_pend[:15]:
        (crit if cierre and m["dias_al_cierre"] is not None and m["dias_al_cierre"] <= 7 else adv).append(
            f"Excluyente pendiente {r.get('id')} ({r.get('responsable') or 'sin responsable'}): {r.get('texto_requisito', '')[:100]}")

    # --- Etapas y compuertas ---
    def condicion(c):
        t = c.get("tipo")
        if t == "metrica":
            v = m.get(c.get("metrica"))
            op = OPS.get(str(c.get("operador")))
            ok = v is not None and op is not None and op(v, num(c.get("valor")))
            return ok, f"{c.get('metrica')} {c.get('operador')} {c.get('valor')} (actual: {'—' if v is None else round(v, 3) if isinstance(v, float) else v})"
        if t == "campo":
            clave = str(c.get("campo", "")).split(".", 1)[-1]
            v = str(pos.get(clave, "")).strip().lower()
            if "valor_distinto" in c:
                return v != str(c["valor_distinto"]).lower(), f"{c.get('campo')} distinto de {c['valor_distinto']} (actual: {v or '—'})"
            return v == str(c.get("valor", "")).lower(), f"{c.get('campo')} = {c.get('valor')} (actual: {v or '—'})"
        if t == "archivo":
            return (raiz / c.get("ruta", "")).exists(), f"existe {c.get('ruta')}"
        if t == "sin_pendientes":
            ruta = raiz / c.get("ruta", "")
            texto_r = ruta.read_text(encoding="utf-8", errors="replace") if ruta.exists() else ""
            ok = ruta.exists() and "PENDIENTE" not in texto_r and not re.search(r"^\s*[-*]\s\[ \]", texto_r, re.M)
            return ok, f"{c.get('ruta')} completo (sin PENDIENTE ni casillas sin marcar)"
        return False, f"condición desconocida: {c}"

    actual = str(pos.get("etapa", "")).strip()
    ids = [e.get("id") for e in etapas]
    if actual not in ids and etapas:
        adv.append(f"La etapa actual '{actual}' no existe en postulacion/etapas.yaml.")
    tabla_etapas = []
    for e in etapas:
        resultados = [condicion(c) for c in (e.get("compuerta") or [])]
        cumple = all(ok for ok, _ in resultados)
        tabla_etapas.append((e, cumple, resultados))

    if a.json:
        import json
        actual_nombre = next((e.get("nombre") for e, _, _ in tabla_etapas if e.get("id") == actual), actual)
        compuerta_ok = next((c for e, c, _ in tabla_etapas if e.get("id") == actual), False)
        print(json.dumps({"metricas": m, "criticos": list(dict.fromkeys(crit)), "advertencias": list(dict.fromkeys(adv)),
                          "info": list(dict.fromkeys(info)), "etapa": actual, "etapa_nombre": actual_nombre,
                          "compuerta_cumplida": compuerta_ok, "cierre": cierre, "hora_cierre": pos.get("hora_cierre"),
                          "decision_go": pos.get("decision_go"), "resultado": pos.get("resultado"),
                          "monto_solicitado": pos.get("monto_solicitado"), "moneda": pos.get("moneda", "CLP"),
                          "entidad": pos.get("entidad"), "instrumento": pos.get("instrumento")}, ensure_ascii=False, default=str))
        return

    # --- Informe ---
    fmt = lambda v: "—" if v is None else f"{v:.2f}"  # noqa: E731
    nombre = (cfg.get("proyecto") or {}).get("nombre", raiz.name)
    out = [f"# Estado de la postulación — {nombre}", "",
           f"- Convocatoria: {pos.get('entidad', '')} · {pos.get('instrumento', '')} · postulante: {pos.get('postulante', '')}",
           f"- Fecha de corte: {hoy} · cierre: {cierre or 'sin fecha'}{' ' + str(pos.get('hora_cierre')) if pos.get('hora_cierre') else ''}"
           f" · días al cierre: {m['dias_al_cierre'] if m['dias_al_cierre'] is not None else '—'}",
           f"- Decisión Go/No-Go: {pos.get('decision_go', 'pendiente')} · resultado: {pos.get('resultado', 'pendiente')}", ""]
    out += ["## Indicadores", "", "| Indicador | Valor |", "|---|---|",
            f"| Cumplimiento de la matriz | {m['cumplimiento_pct']:.0%} ({len(cerrados)}/{len(reqs)}) |",
            f"| Requisitos excluyentes pendientes | {m['excluyentes_pendientes']} |",
            f"| Candidatos del barrido sin revisar | {m['barrido_sin_revisar']} de {m['barrido_total']} |",
            f"| Consultas por enviar / sin respuesta | {m['consultas_por_enviar']} / {m['consultas_sin_respuesta']} |",
            f"| Secciones de la propuesta (sin trazabilidad) | {m['secciones_total']} ({m['secciones_sin_trazabilidad']}) |",
            f"| Controles del presupuesto NO CUMPLE | {m['controles_economicos_incumplidos']}{'' if ctrl else ' (sin controles.csv)'} |",
            f"| Puntaje estimado red team (mín. / objetivo) | {fmt(m['puntaje_redteam']) if m['puntaje_redteam'] is not None else '—'}"
            f" ({pmin:g} / {objetivo:g}) |",
            f"| Fallas fatales abiertas | {m['fallas_fatales_abiertas']} |",
            f"| Documentos vencidos al cierre | {m['contenidos_vencidos']} |",
            f"| Errores de autoría en entrega/final | {m['entrega_autoria_errores']} |"]
    if m["formulario_campos"]:
        out += [f"| Formulario de la plataforma: listos / exceden el límite / obligatorios vacíos | {m['formulario_campos_listos']} de "
                f"{m['formulario_campos']} / {m['formulario_campos_excedidos']} / {m['formulario_obligatorios_vacios']} |"]
    out += [""]
    out += ["## Etapas y compuertas", "", "| # | Etapa | Compuerta | Pendiente para cumplirla |", "|---|---|---|---|"]
    for i, (e, cumple, res) in enumerate(tabla_etapas, 1):
        marca = " ← actual" if e.get("id") == actual else ""
        falta = "; ".join(t for ok, t in res if not ok) or "—"
        out.append(f"| {i} | {e.get('nombre')}{marca} | {'Cumplida' if cumple else 'Pendiente'} | {falta} |")
    for i, (e, cumple, _) in enumerate(tabla_etapas):
        if e.get("id") == actual:
            if cumple and i + 1 < len(tabla_etapas):
                siguiente = tabla_etapas[i + 1][0]
                info.append(f"La compuerta de '{e.get('nombre')}' está cumplida: se puede avanzar a '{siguiente.get('nombre')}' "
                            f"(actualizar postulacion.etapa en proyecto.yaml).")
            break
    if tabla_rt:
        out += ["", f"## Red team — ronda {rt['ronda']}", "", "| Perspectiva | Puntaje ponderado | Completo |", "|---|---|---|"]
        out += [f"| {p} | {v:.2f} | {'sí' if c else 'no'} |" for p, v, c in tabla_rt]
    if proximos:
        out += ["", "## Próximos 14 días", ""] + [f"- en {d} día(s): {t}" for d, t in sorted(proximos)]
    for titulo, lista in (("Crítico", crit), ("Advertencias", adv), ("Información", info)):
        out += ["", f"## {titulo} ({len(lista)})", ""] + ([f"- {x}" for x in dict.fromkeys(lista)] or ["- Sin hallazgos."])
    texto = "\n".join(out) + "\n"

    if a.registrar:
        ruta = raiz / "metricas" / "mediciones.csv"
        ruta.parent.mkdir(exist_ok=True)
        nuevas = [{"fecha": hoy.isoformat(), "entidad": "PROYECTO", "metrica": k, "valor": f"{v:.10g}" if isinstance(v, float) else str(v),
                   "fuente": FUENTE, "comentario": ""} for k, v in m.items() if v is not None]
        _mediciones.registrar(ruta, nuevas, FUENTE, hoy.isoformat())
    else:
        texto += "\n(Métricas no registradas: usar --registrar para guardarlas en metricas/mediciones.csv.)\n"
    if a.salida:
        Path(a.salida).write_text(texto, encoding="utf-8")
    print(texto)


if __name__ == "__main__":
    import _consola
    _consola.preparar()
    main()
