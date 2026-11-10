#!/usr/bin/env python3
"""Plan estratégico (arquetipo estrategia): estado, validación de la cascada, revisión del período, roadmap y mediciones.

Uso:
    python herramientas/estrategia.py <proyecto>                        # dónde va el plan y el siguiente paso
    python herramientas/estrategia.py <proyecto> --revisar              # la cascada cuadra (objetivos, metas, iniciativas, revisiones)
    python herramientas/estrategia.py <proyecto> --revision 2027-T1 [--hoy AAAA-MM-DD] [--quien NOMBRE]
                                                                        # arma o completa la revisión del período en revisiones.csv
    python herramientas/estrategia.py <proyecto> --roadmap              # Gantt (Mermaid) de las iniciativas
    python herramientas/estrategia.py <proyecto> --registrar [--hoy]    # mediciones del arquetipo en metricas/mediciones.csv

La cascada: objetivos.csv (id, perspectiva, objetivo, responsable, estado) → metas.csv (objetivo_id, indicador,
unidad, direccion, linea_base, anio_base, anio, meta, fuente_dato) → iniciativas.csv (id, objetivo_id, iniciativa,
responsable, inicio, fin, inversion, impacto, estado, cartera_item). Las revisiones (revisiones.csv) comparan la meta
del año con el real: el real se toma de metricas/mediciones.csv cuando el indicador es una métrica del proyecto
(entidad PROYECTO, última medición del año); si no, queda vacío para que la persona lo complete con su fuente.
"""
import argparse
import csv
import re
import sys
from datetime import date, datetime
from pathlib import Path

import _config
import _mediciones

RAIZ = Path(__file__).resolve().parent.parent
FUENTE = "herramientas/estrategia.py"
ESTADOS_OBJ = ("propuesto", "aprobado", "activo", "cumplido", "descartado")
ESTADOS_INI = ("propuesta", "aprobada", "en_curso", "terminada", "descartada")
DIRECCIONES = ("mayor_mejor", "menor_mejor", "informativa")
ACTIVOS_OBJ = ("aprobado", "activo")
ACTIVAS_INI = ("aprobada", "en_curso")
COLS = {
    "objetivos.csv": ["id", "perspectiva", "objetivo", "responsable", "estado", "nota"],
    "metas.csv": ["objetivo_id", "indicador", "unidad", "direccion", "linea_base", "anio_base", "anio", "meta", "fuente_dato", "nota"],
    "iniciativas.csv": ["id", "objetivo_id", "iniciativa", "responsable", "inicio", "fin", "inversion", "impacto", "estado", "cartera_item", "nota"],
    "revisiones.csv": ["periodo", "fecha", "objetivo_id", "indicador", "meta_anio", "real", "desvio_pct", "semaforo", "decision", "quien", "nota"],
}


def leer_csv(ruta):
    if not ruta.exists():
        return []
    with open(ruta, encoding="utf-8-sig", newline="") as f:
        return [{k: (v or "").strip() for k, v in r.items()} for r in csv.DictReader(f) if any((x or "").strip() for x in r.values())]


def escribir_csv(ruta, columnas, filas):
    with open(ruta, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columnas, extrasaction="ignore")
        w.writeheader()
        for r in filas:
            w.writerow({c: r.get(c, "") for c in columnas})


def numero(v):
    try:
        return float(str(v).replace(".", "").replace(",", ".")) if re.match(r"^-?\d{1,3}(\.\d{3})+(,\d+)?$", str(v)) else float(str(v).replace(",", "."))
    except (TypeError, ValueError):
        return None


def fecha(v):
    try:
        return datetime.strptime(v, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


class Plan:
    def __init__(self, proyecto):
        self.raiz = Path(proyecto)
        self.carpeta = self.raiz / "estrategia"
        cfg = _config.cargar(self.raiz)
        self.cfg = cfg.get("estrategia") or {}
        self.horizonte = int(self.cfg.get("horizonte_anios") or 3)
        self.anio_inicio = int(self.cfg["anio_inicio"]) if str(self.cfg.get("anio_inicio") or "").isdigit() else None
        self.objetivos = leer_csv(self.carpeta / "objetivos.csv")
        self.metas = leer_csv(self.carpeta / "metas.csv")
        self.iniciativas = leer_csv(self.carpeta / "iniciativas.csv")
        self.revisiones = leer_csv(self.carpeta / "revisiones.csv")

    @property
    def anios(self):
        return list(range(self.anio_inicio, self.anio_inicio + self.horizonte)) if self.anio_inicio else []

    def activos(self):
        return [o for o in self.objetivos if o.get("estado") in ACTIVOS_OBJ]

    def revisar(self, hoy):
        errores, avisos = [], []
        if not self.anio_inicio:
            errores.append("proyecto.yaml: estrategia.anio_inicio vacío (primer año del plan, AAAA).")
        if self.horizonte not in (3, 5):
            avisos.append(f"proyecto.yaml: horizonte_anios {self.horizonte} (lo habitual es 3 o 5).")
        ids = [o.get("id") for o in self.objetivos]
        for i in sorted({x for x in ids if ids.count(x) > 1}):
            errores.append(f"objetivos.csv: id repetido {i}.")
        for o in self.objetivos:
            if not o.get("id") or not o.get("objetivo"):
                errores.append("objetivos.csv: fila sin id u objetivo.")
            if o.get("estado") and o["estado"] not in ESTADOS_OBJ:
                errores.append(f"objetivos.csv {o.get('id')}: estado «{o['estado']}» no válido ({', '.join(ESTADOS_OBJ)}).")
        existentes = {o.get("id") for o in self.objetivos}
        por_obj = {}
        for m in self.metas:
            if m.get("objetivo_id") not in existentes:
                errores.append(f"metas.csv: objetivo {m.get('objetivo_id') or '(vacío)'} no existe en objetivos.csv.")
                continue
            if not m.get("indicador"):
                errores.append(f"metas.csv {m['objetivo_id']}: fila sin indicador.")
            if m.get("direccion") and m["direccion"] not in DIRECCIONES:
                errores.append(f"metas.csv {m['objetivo_id']}/{m.get('indicador')}: direccion «{m['direccion']}» no válida.")
            if not str(m.get("anio") or "").isdigit():
                errores.append(f"metas.csv {m['objetivo_id']}/{m.get('indicador')}: anio «{m.get('anio')}» no válido.")
            elif self.anios and int(m["anio"]) not in self.anios:
                errores.append(f"metas.csv {m['objetivo_id']}/{m.get('indicador')}: el año {m['anio']} está fuera del horizonte {self.anios[0]}-{self.anios[-1]}.")
            if numero(m.get("meta")) is None:
                errores.append(f"metas.csv {m['objetivo_id']}/{m.get('indicador')} {m.get('anio')}: meta «{m.get('meta')}» no es un número.")
            if m.get("linea_base") == "":
                avisos.append(f"metas.csv {m['objetivo_id']}/{m.get('indicador')}: sin línea base.")
            if not m.get("fuente_dato"):
                avisos.append(f"metas.csv {m['objetivo_id']}/{m.get('indicador')}: sin fuente del dato (de dónde saldrá el real).")
            por_obj.setdefault(m["objetivo_id"], {}).setdefault(m.get("indicador"), set()).add(m.get("anio"))
        for o in self.activos():
            inds = por_obj.get(o["id"], {})
            if not inds:
                errores.append(f"objetivo {o['id']} ({o.get('objetivo', '')[:40]}): sin indicador ni metas.")
            elif self.anios:
                completos = [i for i, a in inds.items() if all(str(x) in a for x in self.anios)]
                if not completos:
                    faltan = sorted({str(x) for x in self.anios} - set().union(*inds.values()))
                    errores.append(f"objetivo {o['id']}: ningún indicador tiene meta en todos los años (faltan {', '.join(faltan) or 'años'}).")
        ini_ids = [i.get("id") for i in self.iniciativas]
        for i in sorted({x for x in ini_ids if ini_ids.count(x) > 1}):
            errores.append(f"iniciativas.csv: id repetido {i}.")
        con_iniciativa = set()
        for i in self.iniciativas:
            if i.get("objetivo_id") not in existentes:
                errores.append(f"iniciativas.csv {i.get('id')}: objetivo {i.get('objetivo_id') or '(vacío)'} no existe.")
            if i.get("estado") and i["estado"] not in ESTADOS_INI:
                errores.append(f"iniciativas.csv {i.get('id')}: estado «{i['estado']}» no válido ({', '.join(ESTADOS_INI)}).")
            ini, fin = fecha(i.get("inicio")), fecha(i.get("fin"))
            if i.get("inicio") and not ini:
                errores.append(f"iniciativas.csv {i.get('id')}: inicio «{i['inicio']}» no es AAAA-MM-DD.")
            if i.get("fin") and not fin:
                errores.append(f"iniciativas.csv {i.get('id')}: fin «{i['fin']}» no es AAAA-MM-DD.")
            if ini and fin and fin < ini:
                errores.append(f"iniciativas.csv {i.get('id')}: fin anterior al inicio.")
            if not i.get("responsable"):
                avisos.append(f"iniciativas.csv {i.get('id')}: sin responsable.")
            if i.get("estado") in ACTIVAS_INI:
                con_iniciativa.add(i.get("objetivo_id"))
        for o in self.activos():
            if o["id"] not in con_iniciativa:
                avisos.append(f"objetivo {o['id']}: sin iniciativa aprobada o en curso.")
        for r in self.revisiones:
            if not re.match(r"^\d{4}-T[1-4]$", r.get("periodo", "")):
                errores.append(f"revisiones.csv: periodo «{r.get('periodo')}» no es AAAA-Tn.")
            if r.get("objetivo_id") not in existentes:
                errores.append(f"revisiones.csv {r.get('periodo')}: objetivo {r.get('objetivo_id')} no existe.")
            if r.get("semaforo") == "rojo" and not r.get("decision"):
                errores.append(f"revisiones.csv {r.get('periodo')} {r.get('objetivo_id')}/{r.get('indicador')}: rojo sin decisión.")
        return errores, avisos

    # ------------------------------------------------------------------ revisión
    def real_de(self, indicador, anio):
        """Última medición del año del proyecto (entidad PROYECTO) cuya métrica coincide con el indicador, o None."""
        ruta = self.raiz / "metricas" / "mediciones.csv"
        ultimo = None
        for r in leer_csv(ruta):
            if r.get("metrica") == indicador and r.get("entidad", "PROYECTO") == "PROYECTO" and r.get("fecha", "").startswith(str(anio)):
                if ultimo is None or r["fecha"] >= ultimo["fecha"]:
                    ultimo = r
        return numero(ultimo["valor"]) if ultimo else None

    @staticmethod
    def semaforo(direccion, meta, real):
        if real is None or meta is None:
            return "", ""
        if direccion == "informativa":
            return "", ""
        desvio = (real - meta) / abs(meta) if meta else (0.0 if real == meta else 1.0)
        if direccion == "menor_mejor":
            desvio = -desvio
        color = "verde" if desvio >= 0 else "amarillo" if desvio >= -0.1 else "rojo"
        return f"{desvio:.4f}", color

    def revision(self, periodo, hoy, quien):
        anio = int(periodo[:4])
        existentes = {(r["periodo"], r["objetivo_id"], r["indicador"]): r for r in self.revisiones}
        nuevas, completadas = 0, 0
        for m in self.metas:
            if str(m.get("anio")) != str(anio) or m.get("objetivo_id") not in {o["id"] for o in self.activos()}:
                continue
            clave = (periodo, m["objetivo_id"], m["indicador"])
            fila = existentes.get(clave)
            if fila is None:
                fila = {c: "" for c in COLS["revisiones.csv"]}
                fila.update(periodo=periodo, fecha=hoy.isoformat(), objetivo_id=m["objetivo_id"], indicador=m["indicador"],
                            meta_anio=m.get("meta", ""), quien=quien)
                self.revisiones.append(fila)
                existentes[clave] = fila
                nuevas += 1
            if fila.get("real") == "":
                real = self.real_de(m["indicador"], anio)
                if real is not None:
                    fila["real"] = f"{real:g}"
                    completadas += 1
            if fila.get("real") != "" and fila.get("semaforo") == "":
                fila["desvio_pct"], fila["semaforo"] = self.semaforo(m.get("direccion") or "mayor_mejor", numero(m.get("meta")), numero(fila["real"]))
        escribir_csv(self.carpeta / "revisiones.csv", COLS["revisiones.csv"], self.revisiones)
        filas = [r for r in self.revisiones if r["periodo"] == periodo]
        sin_real = [f"{r['objetivo_id']}/{r['indicador']}" for r in filas if r.get("real") == ""]
        rojos = [f"{r['objetivo_id']}/{r['indicador']}" for r in filas if r.get("semaforo") == "rojo" and not r.get("decision")]
        out = [f"# Revisión {periodo} · {len(filas)} indicador(es) del año {anio}",
               f"- Filas nuevas: {nuevas} · reales tomados de metricas/mediciones.csv: {completadas}"]
        for color in ("verde", "amarillo", "rojo"):
            n = sum(1 for r in filas if r.get("semaforo") == color)
            if n:
                out.append(f"- {color}: {n}")
        if sin_real:
            out.append("- Sin real todavía (complétalo con su fuente en revisiones.csv): " + ", ".join(sin_real))
        if rojos:
            out.append("- Rojos sin decisión (mantener, ajustar meta, reasignar, descartar): " + ", ".join(rojos))
        out.append("Siguiente: reporte `revision-trimestral` cuando cada rojo tenga decisión y quién.")
        return "\n".join(out)

    # ------------------------------------------------------------------ roadmap y mediciones
    def roadmap(self):
        out = ["```mermaid", "gantt", "    title Iniciativas del plan", "    dateFormat YYYY-MM-DD", "    axisFormat %Y-%m"]
        for o in self.objetivos:
            inis = [i for i in self.iniciativas if i.get("objetivo_id") == o.get("id") and fecha(i.get("inicio")) and fecha(i.get("fin"))]
            if not inis:
                continue
            out.append(f"    section {o.get('id')} {o.get('objetivo', '')[:40]}")
            for i in inis:
                estado = "done, " if i.get("estado") == "terminada" else "active, " if i.get("estado") == "en_curso" else ""
                out.append(f"    {i.get('iniciativa', '')[:50]} :{estado}{i.get('id')}, {i['inicio']}, {i['fin']}")
        out.append("```")
        return "\n".join(out)

    def mediciones(self, hoy):
        act = self.activos()
        por_obj = {}
        for m in self.metas:
            por_obj.setdefault(m.get("objetivo_id"), {}).setdefault(m.get("indicador"), set()).add(str(m.get("anio")))
        completos = sum(1 for o in act if any(all(str(a) in anios for a in self.anios) for anios in por_obj.get(o["id"], {}).values())) if self.anios else 0
        con_ini = {i.get("objetivo_id") for i in self.iniciativas if i.get("estado") in ACTIVAS_INI}
        en_curso = sum(1 for i in self.iniciativas if i.get("estado") == "en_curso")
        atrasadas = sum(1 for i in self.iniciativas if i.get("estado") in ACTIVAS_INI and fecha(i.get("fin")) and fecha(i["fin"]) < hoy)
        ultima = max((r["periodo"] for r in self.revisiones), default="")
        filas = [r for r in self.revisiones if r["periodo"] == ultima and r.get("real") != "" and r.get("semaforo")]
        cumpl = sum(1 for r in filas if r["semaforo"] in ("verde", "amarillo")) / len(filas) if filas else None
        tri_actual = f"{hoy.year}-T{(hoy.month - 1) // 3 + 1}"
        tri_anterior = f"{hoy.year}-T{(hoy.month - 1) // 3}" if hoy.month > 3 else f"{hoy.year - 1}-T4"
        return {
            "cascada_completa_pct": (completos / len(act)) if act else None,
            "objetivos_sin_iniciativa": sum(1 for o in act if o["id"] not in con_ini),
            "iniciativas_en_curso": en_curso,
            "iniciativas_atrasadas": atrasadas,
            "cumplimiento_metas_pct": cumpl,
            "revision_al_dia": 1 if ultima in (tri_actual, tri_anterior) else 0,
        }

    def estado(self, hoy):
        errores, avisos = self.revisar(hoy)
        n_obj, n_met, n_ini, n_rev = len(self.objetivos), len(self.metas), len(self.iniciativas), len(self.revisiones)
        diag = (self.carpeta / "diagnostico.md").exists() and "-\n" not in (self.carpeta / "diagnostico.md").read_text(encoding="utf-8", errors="replace")[:400]
        out = [f"# Plan estratégico · {self.raiz.name}",
               f"- Horizonte: {self.horizonte} años desde {self.anio_inicio or '(sin año de inicio)'} · marco {self.cfg.get('marco') or 'okr'} · revisión {self.cfg.get('revision') or 'trimestral'}",
               f"- Objetivos: {n_obj} ({len(self.activos())} activos) · metas: {n_met} · iniciativas: {n_ini} · revisiones: {n_rev}",
               f"- Cascada: {'sin errores' if not errores else str(len(errores)) + ' error(es)'}; {len(avisos)} aviso(s)"]
        if not self.anio_inicio:
            paso = "completar `estrategia` en proyecto.yaml (año de inicio, horizonte, marco, quién aprueba)"
        elif not diag:
            paso = "diagnóstico (`estrategia/diagnostico.md`): externo con fuentes (investigar) e interno (finanzas)"
        elif n_obj == 0:
            paso = "lineamientos y objetivos (`estrategia/lineamientos.md`, `objetivos.csv`)"
        elif errores:
            paso = "corregir la cascada: `estrategia.py --revisar`"
        elif n_ini == 0:
            paso = "iniciativas por objetivo (`iniciativas.csv`) y plan financiero (`finanzas.py --proyectar`)"
        elif n_rev == 0:
            paso = "documento `plan-estrategico` con red team y revisor independiente; luego la primera revisión (`--revision AAAA-Tn`)"
        else:
            paso = f"revisión del período en curso (`--revision {hoy.year}-T{(hoy.month - 1) // 3 + 1}`) y reporte `revision-trimestral`"
        out.append(f"- Siguiente paso: {paso}.")
        return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("proyecto")
    ap.add_argument("--revisar", action="store_true")
    ap.add_argument("--revision", metavar="AAAA-Tn")
    ap.add_argument("--roadmap", action="store_true")
    ap.add_argument("--registrar", action="store_true")
    ap.add_argument("--quien", default="")
    ap.add_argument("--hoy")
    a = ap.parse_args()
    hoy = datetime.strptime(a.hoy, "%Y-%m-%d").date() if a.hoy else date.today()
    raiz = Path(a.proyecto)
    if not (raiz / "proyecto.yaml").exists():
        sys.exit(f"No encuentro {raiz / 'proyecto.yaml'}")
    if not (raiz / "estrategia").exists():
        sys.exit(f"{raiz} no tiene el arquetipo estrategia (carpeta estrategia/). Agrégalo: python herramientas/crear_proyecto.py {raiz.name} --arquetipos estrategia")
    plan = Plan(raiz)
    if a.revisar:
        errores, avisos = plan.revisar(hoy)
        print(f"# Cascada del plan · {raiz.name}\n")
        print("\n".join(f"- ERROR {e}" for e in errores) if errores else "- Sin errores: cada objetivo activo tiene indicador y meta en todos los años.")
        if avisos:
            print("\n".join(f"- aviso {x}" for x in avisos))
        return 1 if errores else 0
    if a.revision:
        if not re.match(r"^\d{4}-T[1-4]$", a.revision):
            sys.exit("El período se escribe AAAA-Tn (por ejemplo 2027-T1).")
        print(plan.revision(a.revision, hoy, a.quien))
        return 0
    if a.roadmap:
        print(plan.roadmap())
        return 0
    if a.registrar:
        k = plan.mediciones(hoy)
        nuevas = [{"fecha": hoy.isoformat(), "entidad": "PROYECTO", "metrica": m, "valor": f"{v:.6f}".rstrip("0").rstrip("."), "fuente": FUENTE,
                   "comentario": "plan estratégico"} for m, v in k.items() if v is not None]
        n = _mediciones.registrar(raiz / "metricas" / "mediciones.csv", nuevas, FUENTE, hoy.isoformat())
        print(f"Registradas {n} mediciones del plan en metricas/mediciones.csv (fecha {hoy.isoformat()}).")
        return 0
    print(plan.estado(hoy))
    return 0


if __name__ == "__main__":
    import _consola
    _consola.preparar()
    sys.exit(main())
