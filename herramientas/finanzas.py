#!/usr/bin/env python3
"""Finanzas de gestión (arquetipo finanzas): importar la contabilidad, estados, desvíos, indicadores, cierres, forecast y proyección.

Uso:
    python herramientas/finanzas.py <proyecto>                                   # dónde va y el siguiente paso
    python herramientas/finanzas.py <proyecto> --importar <archivo> --periodo AAAA-MM [--vista-previa] [--mapa mapa.yaml]
                                               [--acumulado] [--inicial]
    python herramientas/finanzas.py <proyecto> --estados [--periodo AAAA-MM] [--excel salida.xlsx]
    python herramientas/finanzas.py <proyecto> --cerrar AAAA-MM --quien "Nombre" [--forzar]
    python herramientas/finanzas.py <proyecto> --reabrir AAAA-MM --quien "Nombre" --motivo "..."
    python herramientas/finanzas.py <proyecto> --forecast [--metodo presupuesto|tendencia] [--version V]
    python herramientas/finanzas.py <proyecto> --proyectar [--excel salida.xlsx]
    python herramientas/finanzas.py <proyecto> --revisar
    python herramientas/finanzas.py <proyecto> --registrar [--periodo AAAA-MM] [--hoy AAAA-MM-DD]

Lee finanzas/plan-de-cuentas.csv (cuenta → tipo → línea), finanzas/lineas.yaml (líneas y subtotales de los tres
estados), finanzas/real.csv (movimientos por cuenta y período; el período «inicial» son los saldos de apertura),
presupuesto.csv, forecast.csv, cierres.csv y proyeccion.yaml, y el bloque `finanzas` de proyecto.yaml.
- Resultado: ingreso = haber − debe; costo y gasto = debe − haber (signo natural, como magnitud).
- Balance: activo = debe − haber acumulado; pasivo y patrimonio = haber − debe acumulado. El resultado del ejercicio
  se calcula (no se mapea). El balance cuadra si activo = pasivo + patrimonio + resultado acumulado.
- Un período cerrado guarda la huella de sus movimientos: si cambian, --revisar lo detecta y hay que reabrirlo.
No reemplaza la contabilidad ni al contador: consume sus salidas y nunca inventa una cifra.
"""
import argparse
import csv
import hashlib
import re
import sys
from datetime import date, datetime
from pathlib import Path

import yaml

import _config  # noqa: E402
import _mediciones  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
FUENTE = "herramientas/finanzas.py"
TIPOS_RESULTADO = {"ingreso", "costo", "gasto"}
TIPOS_BALANCE = {"activo", "pasivo", "patrimonio"}
TIPOS_CUENTA = TIPOS_RESULTADO | TIPOS_BALANCE | {"orden"}
TOLERANCIA = 1.0
COLS_REAL = ["periodo", "cuenta", "debe", "haber", "origen", "nota"]
COLS_FORECAST = ["periodo", "linea", "monto", "version", "metodo", "nota"]
COLS_CIERRES = ["periodo", "estado", "fecha", "quien", "motivo", "huella", "nota"]
RE_PERIODO = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")
UMBRAL_DESVIO = 0.10


# ------------------------------------------------------------------------------------------------ utilidades
def num_propio(v):
    """Número de un CSV del propio harness (real.csv, presupuesto.csv, forecast.csv): se escribe con punto decimal y sin
    separador de miles, así que «12.345» es doce coma tres, no doce mil. Lo que no tenga esa forma se lee con `num`."""
    s = str(v if v is not None else "").strip()
    if re.fullmatch(r"-?\d+(\.\d+)?([eE][-+]?\d+)?", s):
        return float(s)
    return num(v)


def num(v):
    if v is None:
        return 0.0
    s = str(v).strip().replace("$", "").replace(" ", "")
    if not s or s in ("-", "—"):
        return 0.0
    neg = s.startswith("(") and s.endswith(")")
    s = s.strip("()")
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".") if s.rfind(",") > s.rfind(".") else s.replace(",", "")
    elif "," in s:
        s = s.replace(",", ".") if len(s.split(",")[-1]) <= 2 else s.replace(",", "")
    elif s.count(".") > 1 or (s.count(".") == 1 and len(s.split(".")[-1]) == 3):
        s = s.replace(".", "")
    try:
        x = float(s)
    except ValueError:
        return 0.0
    return -x if neg else x


def fmt(x, unidad=""):
    if x is None:
        return "—"
    if unidad == "%":
        return f"{x * 100:+.1f}%" if x else "0,0%"
    if unidad in ("x", "meses", "días"):
        return f"{x:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".") + (f" {unidad}" if unidad != "x" else "x")
    if abs(x) < 0.5:
        x = 0.0
    return f"{x:,.0f}".replace(",", ".")


def leer_csv(ruta):
    if not Path(ruta).exists():
        return []
    with open(ruta, encoding="utf-8-sig", newline="") as f:
        return [{k.strip(): (v or "").strip() for k, v in r.items() if k is not None} for r in csv.DictReader(f)]


def escribir_csv(ruta, filas, columnas):
    Path(ruta).parent.mkdir(parents=True, exist_ok=True)
    with open(ruta, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columnas, extrasaction="ignore")
        w.writeheader()
        for fila in filas:
            w.writerow({c: fila.get(c, "") for c in columnas})


def cuenta_norm(v):
    s = str(v or "").strip()
    return s[:-2] if re.fullmatch(r"\d+\.0", s) else s


def mes_siguiente(p):
    y, m = int(p[:4]), int(p[5:7])
    return f"{y + (m // 12)}-{(m % 12) + 1:02d}"


def mes_anterior(p):
    y, m = int(p[:4]), int(p[5:7])
    return f"{y - 1}-12" if m == 1 else f"{y}-{m - 1:02d}"


def poner_campo(texto, clave, valor):
    v = '"' + str(valor).replace('"', "'") + '"'
    patron = rf"^([ \t]+{re.escape(clave)}:[ \t]*)(\"[^\"\n]*\"|'[^'\n]*'|[^#\n]*?)([ \t]*(#.*)?)$"
    nuevo, n = re.subn(patron, lambda m: m.group(1) + v + (("   " + m.group(4)) if m.group(4) else ""), texto, count=1, flags=re.M)
    return nuevo if n else texto


# ------------------------------------------------------------------------------------------------ modelo
class Finanzas:
    def __init__(self, proyecto):
        self.raiz = Path(proyecto)
        self.carpeta = self.raiz / "finanzas"
        self.cfg = _config.cargar(self.raiz) if (self.raiz / "proyecto.yaml").exists() else {}
        self.fin = self.cfg.get("finanzas") or {}
        self.moneda = str(self.fin.get("moneda") or (self.cfg.get("formato") or {}).get("moneda") or "")
        self.m0 = int(self.fin.get("anio_fiscal_inicio") or 1)
        ruta_lineas = self.carpeta / "lineas.yaml"
        self.lineas = yaml.safe_load(ruta_lineas.read_text(encoding="utf-8")) if ruta_lineas.exists() else {}
        self.plan = {}
        for f in leer_csv(self.carpeta / "plan-de-cuentas.csv"):
            if f.get("cuenta"):
                self.plan[cuenta_norm(f["cuenta"])] = f
        self.real = [f for f in leer_csv(self.carpeta / "real.csv") if f.get("cuenta")]
        self.ppto = leer_csv(self.carpeta / "presupuesto.csv")
        self.fc = leer_csv(self.carpeta / "forecast.csv")
        self.cierres = leer_csv(self.carpeta / "cierres.csv")
        self.def_lineas = {}
        for seccion in ("resultado", "balance"):
            for l in self.lineas.get(seccion) or []:
                self.def_lineas[l["id"]] = dict(l, seccion=seccion)
        self.linea_de = {}
        for c, f in self.plan.items():
            self.linea_de[c] = f.get("linea", "")

    # --- períodos y año fiscal
    def periodos(self):
        return sorted({f["periodo"] for f in self.real if RE_PERIODO.match(f.get("periodo", ""))})

    def ultimo_periodo(self):
        p = self.periodos()
        return p[-1] if p else ""

    def anio_fiscal(self, periodo):
        y, m = int(periodo[:4]), int(periodo[5:7])
        return y if m >= self.m0 else y - 1

    def periodos_fy(self, fy):
        return [f"{fy + ((self.m0 - 1 + i) // 12)}-{((self.m0 - 1 + i) % 12) + 1:02d}" for i in range(12)]

    def version_vigente(self, filas, clave_cfg):
        v = str(self.fin.get(clave_cfg) or "").strip()
        if v:
            return v
        versiones = sorted({f.get("version", "") for f in filas})
        return versiones[-1] if versiones else ""

    # --- cuentas
    def tipo_linea(self, linea):
        return (self.def_lineas.get(linea) or {}).get("tipo", "")

    def cuentas_sin_mapear(self, hasta=None):
        salida = {}
        for f in self.real:
            if hasta and RE_PERIODO.match(f["periodo"]) and f["periodo"] > hasta:
                continue
            c = cuenta_norm(f["cuenta"])
            if c not in self.plan or not self.linea_de.get(c) or self.linea_de.get(c) not in self.def_lineas:
                salida.setdefault(c, set()).add(f["periodo"])
        return salida

    # --- montos
    def monto_linea_mes(self, linea, periodo):
        tipo = self.tipo_linea(linea)
        total = 0.0
        for f in self.real:
            if f["periodo"] != periodo or self.linea_de.get(cuenta_norm(f["cuenta"])) != linea:
                continue
            d, h = num_propio(f.get("debe")), num_propio(f.get("haber"))
            total += (h - d) if tipo == "ingreso" else (d - h)
        return total

    def saldo_linea(self, linea, periodo):
        tipo = self.tipo_linea(linea)
        total = 0.0
        for f in self.real:
            p = f["periodo"]
            if not (p == "inicial" or (RE_PERIODO.match(p) and p <= periodo)) or self.linea_de.get(cuenta_norm(f["cuenta"])) != linea:
                continue
            d, h = num_propio(f.get("debe")), num_propio(f.get("haber"))
            total += (d - h) if tipo == "activo" else (h - d)
        return total

    def evaluar(self, seccion, base):
        """Valores de todas las líneas de la sección (las de fórmula se calculan en orden)."""
        vals = dict(base)
        for l in self.lineas.get(seccion) or []:
            if l.get("formula"):
                total = 0.0
                for signo, ident in re.findall(r"([+-]?)\s*([a-z_0-9]+)", l["formula"]):
                    total += (-1 if signo == "-" else 1) * vals.get(ident, 0.0)
                vals[l["id"]] = total
        return vals

    def resultado_mes(self, periodo):
        base = {l["id"]: self.monto_linea_mes(l["id"], periodo) for l in self.lineas.get("resultado") or [] if not l.get("formula")}
        return self.evaluar("resultado", base)

    def resultado_acumulado(self, periodo, desde=None):
        fy = self.anio_fiscal(periodo)
        pers = [p for p in self.periodos_fy(fy) if p <= periodo and p in set(self.periodos())] if desde is None else desde
        base = {}
        for l in self.lineas.get("resultado") or []:
            if not l.get("formula"):
                base[l["id"]] = sum(self.monto_linea_mes(l["id"], p) for p in pers)
        return self.evaluar("resultado", base)

    def resultado_total_hasta(self, periodo):
        pers = [p for p in self.periodos() if p <= periodo]
        base = {l["id"]: sum(self.monto_linea_mes(l["id"], p) for p in pers) for l in self.lineas.get("resultado") or [] if not l.get("formula")}
        return self.evaluar("resultado", base).get("resultado_neto", 0.0)

    def balance(self, periodo):
        vals = {}
        for l in self.lineas.get("balance") or []:
            if l.get("calculado"):
                continue
            vals[l["id"]] = self.saldo_linea(l["id"], periodo)
        res_fy = self.resultado_acumulado(periodo).get("resultado_neto", 0.0)
        res_total = self.resultado_total_hasta(periodo)
        vals["resultado_del_ejercicio"] = res_fy
        vals["_resultados_no_traspasados"] = res_total - res_fy
        grupos = {}
        for l in self.lineas.get("balance") or []:
            grupos[l.get("grupo", "")] = grupos.get(l.get("grupo", ""), 0.0) + vals.get(l["id"], 0.0)
        grupos["patrimonio"] = grupos.get("patrimonio", 0.0) + vals["_resultados_no_traspasados"]
        activo = sum(v for g, v in grupos.items() if g.startswith("activo"))
        pasivo = sum(v for g, v in grupos.items() if g.startswith("pasivo"))
        patrimonio = grupos.get("patrimonio", 0.0)
        return {"lineas": vals, "grupos": grupos, "activo": activo, "pasivo": pasivo, "patrimonio": patrimonio,
                "diferencia": activo - pasivo - patrimonio}

    def monto_version(self, filas, linea, periodo, version):
        return sum(num_propio(f.get("monto")) for f in filas if f.get("periodo") == periodo and f.get("linea") == linea
                   and (not version or f.get("version", "") == version))

    def presupuesto_mes(self, periodo):
        v = self.version_vigente(self.ppto, "version_presupuesto")
        base = {l["id"]: self.monto_version(self.ppto, l["id"], periodo, v) for l in self.lineas.get("resultado") or [] if not l.get("formula")}
        return self.evaluar("resultado", base)

    def forecast_mes(self, periodo):
        v = self.version_vigente(self.fc, "version_forecast")
        base = {l["id"]: self.monto_version(self.fc, l["id"], periodo, v) for l in self.lineas.get("resultado") or [] if not l.get("formula")}
        return self.evaluar("resultado", base)

    def hay_presupuesto(self, periodo):
        v = self.version_vigente(self.ppto, "version_presupuesto")
        return any(f.get("periodo") == periodo and (not v or f.get("version") == v) for f in self.ppto)

    # --- cierres
    def estado_cierre(self, periodo):
        filas = [f for f in self.cierres if f.get("periodo") == periodo]
        return filas[-1] if filas else None

    def cerrado(self, periodo):
        e = self.estado_cierre(periodo)
        return bool(e) and e.get("estado") == "cerrado"

    def huella(self, periodo):
        filas = sorted((cuenta_norm(f["cuenta"]), f.get("debe", ""), f.get("haber", "")) for f in self.real if f["periodo"] == periodo)
        return hashlib.sha256(repr(filas).encode("utf-8")).hexdigest()[:16]

    def periodos_sin_cerrar(self):
        return [p for p in self.periodos() if not self.cerrado(p)]

    # --- indicadores
    def kpis(self, periodo):
        r = self.resultado_mes(periodo)
        ra = self.resultado_acumulado(periodo)
        b = self.balance(periodo)
        pp = self.presupuesto_mes(periodo)
        pers = [p for p in self.periodos() if p <= periodo][-3:]
        ingresos3 = sum(self.resultado_mes(p).get("ingresos", 0.0) + self.resultado_mes(p).get("otros_ingresos", 0.0) for p in pers)
        costo3 = sum(self.resultado_mes(p).get("costo_ventas", 0.0) for p in pers)
        gastos_ids = [l["id"] for l in self.lineas.get("resultado") or [] if l.get("tipo") in ("costo", "gasto") and l["id"] not in ("impuestos", "resultado_financiero")]
        operacion3 = sum(sum(self.resultado_mes(p).get(g, 0.0) for g in gastos_ids) for p in pers)
        gastos_op_ids = [l["id"] for l in self.lineas.get("resultado") or [] if l.get("tipo") == "gasto" and l["id"] not in ("depreciacion", "impuestos", "resultado_financiero")]
        gastos_real = sum(r.get(g, 0.0) for g in gastos_op_ids)
        gastos_ppto = sum(pp.get(g, 0.0) for g in gastos_op_ids)
        ingresos = r.get("ingresos", 0.0) + r.get("otros_ingresos", 0.0)
        ingresos_ppto = pp.get("ingresos", 0.0) + pp.get("otros_ingresos", 0.0)
        n3 = max(len(pers), 1)
        caja = b["lineas"].get("caja", 0.0)
        k = {
            "ingresos": ingresos,
            "margen_bruto_pct": (r.get("margen_bruto", 0.0) / ingresos) if ingresos else None,
            "ebitda": r.get("ebitda", 0.0),
            "margen_ebitda_pct": (r.get("ebitda", 0.0) / ingresos) if ingresos else None,
            "resultado_neto": r.get("resultado_neto", 0.0),
            "resultado_neto_acumulado": ra.get("resultado_neto", 0.0),
            "caja": caja,
            "meses_de_caja": (caja / (operacion3 / n3)) if operacion3 > 0 else None,
            "dso": (b["lineas"].get("cuentas_por_cobrar", 0.0) / ingresos3 * 30 * n3) if ingresos3 > 0 else None,
            "dpo": (b["lineas"].get("cuentas_por_pagar", 0.0) / costo3 * 30 * n3) if costo3 > 0 else None,
            "dio": (b["lineas"].get("inventario", 0.0) / costo3 * 30 * n3) if costo3 > 0 else None,
            "liquidez_corriente": (b["grupos"].get("activo_corriente", 0.0) / b["grupos"].get("pasivo_corriente", 0.0)) if b["grupos"].get("pasivo_corriente") else None,
            "endeudamiento": (b["pasivo"] / b["patrimonio"]) if b["patrimonio"] else None,
            "desvio_ingresos_pct": ((ingresos - ingresos_ppto) / ingresos_ppto) if ingresos_ppto else None,
            "desvio_gastos_pct": ((gastos_real - gastos_ppto) / gastos_ppto) if gastos_ppto else None,
            "cuentas_sin_mapear": float(len(self.cuentas_sin_mapear(periodo))),
            "periodos_sin_cerrar": float(len([p for p in self.periodos_sin_cerrar() if p <= periodo])),
            "balance_cuadra": 1.0 if abs(b["diferencia"]) <= TOLERANCIA and not self.cuentas_sin_mapear(periodo) else 0.0,
        }
        return k

    # --- desvíos
    def desvios(self, periodo):
        r, pp = self.resultado_mes(periodo), self.presupuesto_mes(periodo)
        salida = []
        for l in self.lineas.get("resultado") or []:
            real, ppto = r.get(l["id"], 0.0), pp.get(l["id"], 0.0)
            if not ppto and not real:
                continue
            desv = real - ppto
            pct = (desv / abs(ppto)) if ppto else None
            favorable = desv >= 0 if l.get("tipo") == "ingreso" or l.get("formula") else desv <= 0
            salida.append({"linea": l["id"], "nombre": l["nombre"], "real": real, "ppto": ppto, "desvio": desv, "pct": pct,
                           "favorable": favorable, "relevante": pct is not None and abs(pct) >= UMBRAL_DESVIO and abs(desv) > TOLERANCIA})
        return salida


# ------------------------------------------------------------------------------------------------ revisión
def revisar(fz):
    errores, avisos = [], []
    if not fz.lineas:
        errores.append("falta finanzas/lineas.yaml (cópialo de arquetipos/finanzas/estructura/finanzas/).")
        return errores, avisos
    for c, f in fz.plan.items():
        if f.get("tipo") not in TIPOS_CUENTA:
            errores.append(f"plan-de-cuentas.csv {c}: tipo «{f.get('tipo')}» no válido (activo, pasivo, patrimonio, ingreso, costo, gasto, orden).")
        linea = f.get("linea", "")
        if f.get("tipo") != "orden":
            if not linea:
                errores.append(f"plan-de-cuentas.csv {c}: sin línea del reporte.")
            elif linea not in fz.def_lineas:
                errores.append(f"plan-de-cuentas.csv {c}: la línea «{linea}» no existe en lineas.yaml.")
            elif fz.def_lineas[linea].get("calculado"):
                errores.append(f"plan-de-cuentas.csv {c}: la línea «{linea}» se calcula, no se mapea.")
            else:
                tl = fz.tipo_linea(linea)
                if tl and f.get("tipo") != tl:
                    errores.append(f"plan-de-cuentas.csv {c}: tipo {f.get('tipo')} pero la línea «{linea}» es de tipo {tl}.")
    for n, f in enumerate(fz.real, start=2):
        if f.get("periodo") != "inicial" and not RE_PERIODO.match(f.get("periodo", "")):
            errores.append(f"real.csv línea {n}: período «{f.get('periodo')}» no es AAAA-MM ni «inicial».")
    for f in fz.ppto + fz.fc:
        if f.get("linea") and f["linea"] not in fz.def_lineas:
            errores.append(f"presupuesto/forecast: la línea «{f['linea']}» no existe en lineas.yaml.")
        if f.get("periodo") and not RE_PERIODO.match(f["periodo"]):
            errores.append(f"presupuesto/forecast: período «{f.get('periodo')}» no es AAAA-MM.")
    sin = fz.cuentas_sin_mapear()
    for c, pers in sorted(sin.items()):
        avisos.append(f"cuenta {c} sin mapear en el plan ({', '.join(sorted(pers))}): sus movimientos no entran a los estados.")
    for p in fz.periodos():
        d = sum(num_propio(f.get("debe")) for f in fz.real if f["periodo"] == p)
        h = sum(num_propio(f.get("haber")) for f in fz.real if f["periodo"] == p)
        if abs(d - h) > TOLERANCIA:
            errores.append(f"{p}: debe {fmt(d)} ≠ haber {fmt(h)}: la importación no cuadra.")
        e = fz.estado_cierre(p)
        if e and e.get("estado") == "cerrado" and e.get("huella") and e["huella"] != fz.huella(p):
            errores.append(f"{p} está cerrado y sus movimientos cambiaron después del cierre: reábrelo (--reabrir {p} --quien --motivo) o restaura los datos.")
        b = fz.balance(p)
        if abs(b["diferencia"]) > TOLERANCIA and not sin:
            errores.append(f"{p}: el balance no cuadra (activo − pasivo − patrimonio − resultado = {fmt(b['diferencia'])}).")
    for f in fz.cierres:
        if f.get("estado") not in ("cerrado", "reabierto"):
            errores.append(f"cierres.csv {f.get('periodo')}: estado «{f.get('estado')}» no válido (cerrado, reabierto).")
        if f.get("estado") == "reabierto" and not (f.get("quien") and f.get("motivo")):
            errores.append(f"cierres.csv {f.get('periodo')}: una reapertura lleva quién y motivo.")
    return errores, avisos


# ------------------------------------------------------------------------------------------------ estado y siguiente paso
def estado(fz, hoy):
    ult = fz.ultimo_periodo()
    print(f"# Finanzas · {(fz.cfg.get('proyecto') or {}).get('nombre') or fz.raiz.name}\n")
    errores, avisos = revisar(fz)
    if not fz.plan:
        print("- Sin plan de cuentas mapeado. Siguiente paso: mapear `finanzas/plan-de-cuentas.csv` a las líneas de `lineas.yaml` "
              "(parte de biblioteca/finanzas/plan-de-cuentas-base.csv si no tienes uno).")
        return 0
    if not ult:
        print(f"- Plan de cuentas: {len(fz.plan)} cuentas. Sin movimientos todavía. Siguiente paso: importar el primer período "
              "(`--importar <archivo> --periodo AAAA-MM`; los saldos de apertura con `--inicial`).")
        return 0
    fy = fz.anio_fiscal(ult)
    sin = fz.cuentas_sin_mapear()
    cerrados = [p for p in fz.periodos() if fz.cerrado(p)]
    abiertos = fz.periodos_sin_cerrar()
    k = fz.kpis(ult)
    print(f"- Último período con movimientos: {ult} · año fiscal {fy} · períodos cerrados: {', '.join(cerrados) or 'ninguno'} · "
          f"abiertos: {', '.join(abiertos) or 'ninguno'}")
    print(f"- Presupuesto {fy}: {'cargado (versión ' + (fz.version_vigente(fz.ppto, 'version_presupuesto') or 'única') + ')' if fz.hay_presupuesto(ult) else 'NO cargado para ' + ult}"
          f" · forecast: {'versión ' + fz.version_vigente(fz.fc, 'version_forecast') if fz.fc else 'ninguno'}")
    print(f"- Cuentas sin mapear: {len(sin)}" + (f" ({', '.join(sorted(sin))})" if sin else ""))
    print(f"- {ult}: ingresos {fmt(k['ingresos'])} · margen bruto {fmt(k['margen_bruto_pct'], '%')} · EBITDA {fmt(k['ebitda'])} · "
          f"resultado {fmt(k['resultado_neto'])} · caja {fmt(k['caja'])} ({fmt(k['meses_de_caja'], 'meses')} de operación) · "
          f"liquidez {fmt(k['liquidez_corriente'], 'x')} · balance {'cuadra' if k['balance_cuadra'] else 'NO cuadra'}")
    relevantes = [d for d in fz.desvios(ult) if d["relevante"]]
    if relevantes:
        print("- Desvíos del mes contra presupuesto (≥ 10 %): " + "; ".join(
            f"{d['nombre']} {fmt(d['pct'], '%')} ({'favorable' if d['favorable'] else 'desfavorable'})" for d in relevantes[:6]))
    if errores:
        print(f"- Errores de consistencia: {len(errores)} (ver --revisar).")
    # siguiente paso
    pasos = []
    if sin:
        pasos.append(f"mapear las cuentas sin mapear en plan-de-cuentas.csv ({', '.join(sorted(sin)[:5])}) y volver a revisar.")
    if errores:
        pasos.append("corregir los errores de --revisar antes de cerrar o reportar.")
    if not fz.hay_presupuesto(ult):
        pasos.append(f"cargar el presupuesto {fy} en presupuesto.csv (skill gestion-financiera, modo presupuesto).")
    dia = int(fz.fin.get("dia_cierre") or 10)
    for p in abiertos:
        limite = mes_siguiente(p)
        vence = date(int(limite[:4]), int(limite[5:7]), min(dia, 28))
        if hoy >= vence:
            pasos.append(f"cerrar {p} (checklist en finanzas/cierre/checklist.md; luego `--cerrar {p} --quien`)" + (" — ATRASADO" if hoy > vence else ""))
            break
    if fz.fc and fz.version_vigente(fz.fc, "version_forecast"):
        pers_fc = sorted({f.get("periodo") for f in fz.fc if f.get("version") == fz.version_vigente(fz.fc, "version_forecast")})
        if pers_fc and pers_fc[0] <= ult:
            pasos.append(f"actualizar el forecast: la versión vigente parte en {pers_fc[0]} y ya hay real hasta {ult} (`--forecast`).")
    elif fz.hay_presupuesto(ult):
        pasos.append("generar el primer forecast del año (`--forecast --metodo presupuesto`).")
    if not pasos:
        pasos.append(f"nada pendiente: el siguiente cierre es el de {mes_siguiente(ult)} cuando llegue la contabilidad.")
    print("- Siguiente paso: " + pasos[0] + ("".join(f"\n  - después: {x}" for x in pasos[1:3]) if len(pasos) > 1 else ""))
    return 0


# ------------------------------------------------------------------------------------------------ estados
def tabla_resultado(fz, periodo):
    r, pp, fc = fz.resultado_mes(periodo), fz.presupuesto_mes(periodo), fz.forecast_mes(periodo)
    ra = fz.resultado_acumulado(periodo)
    fy = fz.anio_fiscal(periodo)
    pers_fy = [p for p in fz.periodos_fy(fy) if p <= periodo]
    base_pp = {l["id"]: sum(fz.monto_version(fz.ppto, l["id"], p, fz.version_vigente(fz.ppto, "version_presupuesto")) for p in pers_fy)
               for l in fz.lineas.get("resultado") or [] if not l.get("formula")}
    ppa = fz.evaluar("resultado", base_pp)
    # año: real de los meses con movimientos + forecast de los restantes (si no hay forecast, presupuesto)
    reales = set(fz.periodos())
    vfc = fz.version_vigente(fz.fc, "version_forecast")
    base_anio = {}
    for l in fz.lineas.get("resultado") or []:
        if l.get("formula"):
            continue
        total = 0.0
        for p in fz.periodos_fy(fy):
            if p in reales and p <= periodo:
                total += fz.monto_linea_mes(l["id"], p)
            elif vfc and any(f.get("periodo") == p and f.get("version") == vfc for f in fz.fc):
                total += fz.monto_version(fz.fc, l["id"], p, vfc)
            else:
                total += fz.monto_version(fz.ppto, l["id"], p, fz.version_vigente(fz.ppto, "version_presupuesto"))
        base_anio[l["id"]] = total
    anio = fz.evaluar("resultado", base_anio)
    base_pp_anio = {l["id"]: sum(fz.monto_version(fz.ppto, l["id"], p, fz.version_vigente(fz.ppto, "version_presupuesto")) for p in fz.periodos_fy(fy))
                    for l in fz.lineas.get("resultado") or [] if not l.get("formula")}
    ppto_anio = fz.evaluar("resultado", base_pp_anio)
    filas = []
    for l in fz.lineas.get("resultado") or []:
        i = l["id"]
        filas.append({"id": i, "nombre": l["nombre"], "subtotal": bool(l.get("formula")), "real": r.get(i, 0.0), "ppto": pp.get(i, 0.0),
                      "desv": r.get(i, 0.0) - pp.get(i, 0.0), "real_acum": ra.get(i, 0.0), "ppto_acum": ppa.get(i, 0.0),
                      "desv_acum": ra.get(i, 0.0) - ppa.get(i, 0.0), "anio": anio.get(i, 0.0), "ppto_anio": ppto_anio.get(i, 0.0)})
    return filas


def flujo_caja(fz, periodo):
    ant = mes_anterior(periodo)
    b1, b0 = fz.balance(periodo), fz.balance(ant)
    r = fz.resultado_mes(periodo)
    l1, l0 = b1["lineas"], b0["lineas"]
    d = lambda k: l1.get(k, 0.0) - l0.get(k, 0.0)  # noqa: E731
    ac_no_caja = [l["id"] for l in fz.lineas.get("balance") or [] if l.get("grupo") == "activo_corriente" and l["id"] != "caja"]
    pc = [l["id"] for l in fz.lineas.get("balance") or [] if l.get("grupo") == "pasivo_corriente" and l["id"] != "deuda_corto_plazo"]
    anc = [l["id"] for l in fz.lineas.get("balance") or [] if l.get("grupo") == "activo_no_corriente" and l["id"] != "depreciacion_acumulada"]
    fin = [l["id"] for l in fz.lineas.get("balance") or [] if l.get("grupo") in ("pasivo_no_corriente", "patrimonio") and not l.get("calculado")] + ["deuda_corto_plazo"]
    operacion = r.get("resultado_neto", 0.0) + r.get("depreciacion", 0.0) - sum(d(k) for k in ac_no_caja) + sum(d(k) for k in pc)
    inversion = -sum(d(k) for k in anc)
    financiamiento = sum(d(k) for k in fin) + (b1["lineas"].get("_resultados_no_traspasados", 0.0) - b0["lineas"].get("_resultados_no_traspasados", 0.0)) \
        - (b1["lineas"].get("resultado_del_ejercicio", 0.0) - b0["lineas"].get("resultado_del_ejercicio", 0.0) - r.get("resultado_neto", 0.0))
    variacion = d("caja")
    return {"caja_inicial": l0.get("caja", 0.0), "operacion": operacion, "inversion": inversion, "financiamiento": financiamiento,
            "variacion": variacion, "caja_final": l1.get("caja", 0.0), "diferencia": variacion - operacion - inversion - financiamiento}


def imprimir_estados(fz, periodo):
    print(f"# Estados de gestión · {periodo}" + (f" · {fz.moneda}" if fz.moneda else "") + "\n")
    print("## Resultados\n")
    print("| Línea | Mes real | Mes ppto | Desvío | Acum. real | Acum. ppto | Desvío | Año (real + fc) | Año ppto |")
    print("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for f in tabla_resultado(fz, periodo):
        n = f"**{f['nombre']}**" if f["subtotal"] else f["nombre"]
        print(f"| {n} | {fmt(f['real'])} | {fmt(f['ppto'])} | {fmt(f['desv'])} | {fmt(f['real_acum'])} | {fmt(f['ppto_acum'])} | "
              f"{fmt(f['desv_acum'])} | {fmt(f['anio'])} | {fmt(f['ppto_anio'])} |")
    rel = [d for d in fz.desvios(periodo) if d["relevante"]]
    if rel:
        print("\nDesvíos relevantes del mes (≥ 10 %): " + "; ".join(f"{d['nombre']} {fmt(d['desvio'])} ({fmt(d['pct'], '%')}, "
                                                                     f"{'favorable' if d['favorable'] else 'desfavorable'})" for d in rel))
    b = fz.balance(periodo)
    print(f"\n## Balance al cierre de {periodo}\n")
    print("| Grupo / línea | Saldo |\n|---|---:|")
    for g in fz.lineas.get("grupos") or []:
        print(f"| **{g['nombre']}** | {fmt(b['grupos'].get(g['id'], 0.0))} |")
        for l in fz.lineas.get("balance") or []:
            if l.get("grupo") == g["id"]:
                print(f"| {l['nombre']} | {fmt(b['lineas'].get(l['id'], 0.0))} |")
        if g["id"] == "patrimonio" and abs(b["lineas"].get("_resultados_no_traspasados", 0.0)) > TOLERANCIA:
            print(f"| Resultados de ejercicios anteriores no traspasados | {fmt(b['lineas']['_resultados_no_traspasados'])} |")
    print(f"| **Activo** | {fmt(b['activo'])} |\n| **Pasivo + patrimonio** | {fmt(b['pasivo'] + b['patrimonio'])} |")
    print(f"\nEl balance {'cuadra' if abs(b['diferencia']) <= TOLERANCIA else 'NO cuadra: diferencia ' + fmt(b['diferencia'])}"
          + ("; hay cuentas sin mapear: " + ", ".join(sorted(fz.cuentas_sin_mapear(periodo))) if fz.cuentas_sin_mapear(periodo) else "") + ".")
    c = flujo_caja(fz, periodo)
    print(f"\n## Flujo de caja del mes (método indirecto)\n")
    print(f"| Concepto | Monto |\n|---|---:|\n| Caja inicial | {fmt(c['caja_inicial'])} |\n| Flujo de operación | {fmt(c['operacion'])} |"
          f"\n| Flujo de inversión | {fmt(c['inversion'])} |\n| Flujo de financiamiento | {fmt(c['financiamiento'])} |"
          f"\n| Variación de caja | {fmt(c['variacion'])} |\n| Caja final | {fmt(c['caja_final'])} |"
          + (f"\n| Diferencia no explicada | {fmt(c['diferencia'])} |" if abs(c["diferencia"]) > TOLERANCIA else ""))
    k = fz.kpis(periodo)
    print("\n## Indicadores\n")
    print("| Indicador | Valor |\n|---|---:|")
    for i, u in (("margen_bruto_pct", "%"), ("margen_ebitda_pct", "%"), ("meses_de_caja", "meses"), ("dso", "días"), ("dpo", "días"),
                 ("dio", "días"), ("liquidez_corriente", "x"), ("endeudamiento", "x"), ("desvio_ingresos_pct", "%"), ("desvio_gastos_pct", "%"),
                 ("cuentas_sin_mapear", ""), ("periodos_sin_cerrar", "")):
        print(f"| {i} | {fmt(k[i], u)} |")


def excel_estados(fz, periodo, salida):
    from openpyxl import Workbook
    from openpyxl.styles import Font
    from openpyxl.utils import get_column_letter as L
    fy = fz.anio_fiscal(periodo)
    meses = fz.periodos_fy(fy)
    reales = set(fz.periodos())
    vp, vf = fz.version_vigente(fz.ppto, "version_presupuesto"), fz.version_vigente(fz.fc, "version_forecast")
    wb = Workbook()
    datos = wb.active
    datos.title = "Datos"
    datos.append(["periodo", "linea", "nombre", "real", "presupuesto", "forecast"])
    for p in meses:
        for l in fz.lineas.get("resultado") or []:
            if l.get("formula"):
                continue
            real = fz.monto_linea_mes(l["id"], p) if p in reales else None
            datos.append([p, l["id"], l["nombre"], real, fz.monto_version(fz.ppto, l["id"], p, vp), fz.monto_version(fz.fc, l["id"], p, vf) or None])
    saldos = wb.create_sheet("Saldos")
    saldos.append(["periodo", "linea", "nombre", "saldo"])
    for p in meses:
        if p not in reales:
            continue
        b = fz.balance(p)
        for l in fz.lineas.get("balance") or []:
            saldos.append([p, l["id"], l["nombre"], b["lineas"].get(l["id"], 0.0)])
        saldos.append([p, "_resultados_no_traspasados", "Resultados de ejercicios anteriores no traspasados", b["lineas"].get("_resultados_no_traspasados", 0.0)])
    negrita = Font(bold=True)
    res = wb.create_sheet("Resultados")
    filas_bloque = {}
    fila = 1
    for bloque, col in (("Real", "D"), ("Presupuesto", "E"), ("Forecast", "F")):
        res.cell(row=fila, column=1, value=bloque).font = negrita
        for j, p in enumerate(meses, start=2):
            res.cell(row=fila, column=j, value=p).font = negrita
        res.cell(row=fila, column=len(meses) + 2, value="Año").font = negrita
        encabezado = fila
        fila += 1
        filas_linea = {}
        for l in fz.lineas.get("resultado") or []:
            res.cell(row=fila, column=1, value=l["nombre"]).font = negrita if l.get("formula") else Font()
            for j, p in enumerate(meses, start=2):
                c = L(j)
                if l.get("formula"):
                    terminos = re.findall(r"([+-]?)\s*([a-z_0-9]+)", l["formula"])
                    f = "=" + "".join(f"{'-' if s == '-' else '+'}{c}{filas_linea[i]}" for s, i in terminos if i in filas_linea).lstrip("+")
                else:
                    f = f'=SUMIFS(Datos!${col}:${col},Datos!$A:$A,{c}${encabezado},Datos!$B:$B,"{l["id"]}")'
                res.cell(row=fila, column=j, value=f)
            res.cell(row=fila, column=len(meses) + 2, value=f"=SUM(B{fila}:{L(len(meses) + 1)}{fila})")
            filas_linea[l["id"]] = fila
            fila += 1
        filas_bloque[bloque] = (encabezado, filas_linea)
        fila += 1
    res.cell(row=fila, column=1, value="Desvío real − presupuesto").font = negrita
    for j, p in enumerate(meses, start=2):
        res.cell(row=fila, column=j, value=p).font = negrita
    fila += 1
    for l in fz.lineas.get("resultado") or []:
        res.cell(row=fila, column=1, value=l["nombre"])
        for j in range(2, len(meses) + 3):
            c = L(j)
            res.cell(row=fila, column=j, value=f"={c}{filas_bloque['Real'][1][l['id']]}-{c}{filas_bloque['Presupuesto'][1][l['id']]}")
        fila += 1
    bal = wb.create_sheet("Balance")
    bal.cell(row=1, column=1, value="Línea").font = negrita
    for j, p in enumerate(meses, start=2):
        bal.cell(row=1, column=j, value=p).font = negrita
    fila = 2
    filas_bal = {}
    for l in (fz.lineas.get("balance") or []) + [{"id": "_resultados_no_traspasados", "nombre": "Resultados de ejercicios anteriores no traspasados"}]:
        bal.cell(row=fila, column=1, value=l["nombre"])
        for j in range(2, len(meses) + 2):
            c = L(j)
            bal.cell(row=fila, column=j, value=f'=SUMIFS(Saldos!$D:$D,Saldos!$A:$A,{c}$1,Saldos!$B:$B,"{l["id"]}")')
        filas_bal[l["id"]] = fila
        fila += 1
    for grupo, etiqueta in (("activo", "Activo"), ("pasivo", "Pasivo"), ("patrimonio", "Patrimonio")):
        ids = [l["id"] for l in fz.lineas.get("balance") or [] if (l.get("grupo") or "").startswith(grupo)] + (["_resultados_no_traspasados"] if grupo == "patrimonio" else [])
        bal.cell(row=fila, column=1, value=etiqueta).font = negrita
        for j in range(2, len(meses) + 2):
            c = L(j)
            bal.cell(row=fila, column=j, value="=" + "+".join(f"{c}{filas_bal[i]}" for i in ids))
        filas_bal["_" + grupo] = fila
        fila += 1
    bal.cell(row=fila, column=1, value="Diferencia (debe ser 0)").font = negrita
    for j in range(2, len(meses) + 2):
        c = L(j)
        bal.cell(row=fila, column=j, value=f"={c}{filas_bal['_activo']}-{c}{filas_bal['_pasivo']}-{c}{filas_bal['_patrimonio']}")
    kpi = wb.create_sheet("KPI")
    kpi.cell(row=1, column=1, value="Indicador").font = negrita
    for j, p in enumerate(meses, start=2):
        kpi.cell(row=1, column=j, value=p).font = negrita
    rl = filas_bloque["Real"][1]
    defs = [("Margen bruto %", lambda c: f"=IFERROR(Resultados!{c}{rl['margen_bruto']}/Resultados!{c}{rl['ingresos']},\"\")"),
            ("Margen EBITDA %", lambda c: f"=IFERROR(Resultados!{c}{rl['ebitda']}/Resultados!{c}{rl['ingresos']},\"\")"),
            ("Liquidez corriente", lambda c: f"=IFERROR(({'+'.join('Balance!' + c + str(filas_bal[l['id']]) for l in fz.lineas.get('balance') or [] if l.get('grupo') == 'activo_corriente')})/"
                                              f"({'+'.join('Balance!' + c + str(filas_bal[l['id']]) for l in fz.lineas.get('balance') or [] if l.get('grupo') == 'pasivo_corriente')}),\"\")"),
            ("Endeudamiento", lambda c: f"=IFERROR(Balance!{c}{filas_bal['_pasivo']}/Balance!{c}{filas_bal['_patrimonio']},\"\")"),
            ("Caja", lambda c: f"=Balance!{c}{filas_bal['caja']}")]
    for i, (nombre, fn) in enumerate(defs, start=2):
        kpi.cell(row=i, column=1, value=nombre)
        for j in range(2, len(meses) + 2):
            kpi.cell(row=i, column=j, value=fn(L(j)))
    for ws in wb.worksheets:
        ws.column_dimensions["A"].width = 38
    wb.calculation.fullCalcOnLoad = True
    salida = Path(salida)
    salida.parent.mkdir(parents=True, exist_ok=True)
    wb.save(str(salida))
    try:
        import autoria
        aut = autoria.cargar_autoria(fz.raiz)
        autoria.limpiar_ooxml(salida, autor=aut.get("nombre", ""), titulo="", organizacion=aut.get("organizacion", ""))
    except Exception:
        pass
    return salida


# ------------------------------------------------------------------------------------------------ importar
def leer_tabla(archivo):
    """Filas (listas de celdas) de un Excel (primera hoja con datos) o CSV."""
    archivo = Path(archivo)
    if archivo.suffix.lower() in (".xlsx", ".xlsm"):
        from openpyxl import load_workbook
        wb = load_workbook(str(archivo), data_only=True, read_only=True)
        for ws in wb.worksheets:
            filas = [["" if v is None else v for v in fila] for fila in ws.iter_rows(values_only=True)]
            if any(any(str(c).strip() for c in fila) for fila in filas):
                return filas, ws.title
        return [], ""
    with open(archivo, encoding="utf-8-sig", newline="") as f:
        muestra = f.read(4096)
        f.seek(0)
        try:
            dialecto = csv.Sniffer().sniff(muestra, delimiters=",;\t")
        except csv.Error:
            dialecto = csv.excel
        return [list(r) for r in csv.reader(f, dialecto)], archivo.name


PATRONES = {"cuenta": r"^(c[oó]digo|cuenta|n[uú]mero|nro|cod)\b", "nombre": r"(nombre|descripci|glosa|denominaci|cuenta)",
            "debe": r"(d[eé]bito|debe|cargo)", "haber": r"(cr[eé]dito|haber|abono)",
            "saldo_deudor": r"saldo.*deudor|deudor", "saldo_acreedor": r"saldo.*acreedor|acreedor"}


def detectar_columnas(filas, mapa=None):
    """(índice de la fila de encabezado, {campo: índice de columna})."""
    mapa = mapa or {}
    for i, fila in enumerate(filas[:40]):
        celdas = [str(c).strip().lower() for c in fila]
        cols = {}
        for campo, patron in PATRONES.items():
            if mapa.get(campo):
                idx = next((k for k, c in enumerate(celdas) if c == str(mapa[campo]).strip().lower()), None)
            else:
                idx = next((k for k, c in enumerate(celdas) if c and re.search(patron, c) and k not in cols.values()), None)
            if idx is not None:
                cols[campo] = idx
        if "cuenta" in cols and ("debe" in cols or "saldo_deudor" in cols):
            if mapa.get("fila_encabezado") and i + 1 != int(mapa["fila_encabezado"]):
                continue
            return i, cols
    return None, {}


def importar(fz, archivo, periodo, vista_previa, mapa, acumulado, inicial, hoy):
    if not inicial and not RE_PERIODO.match(periodo or ""):
        sys.exit("Indica --periodo AAAA-MM (o --inicial para los saldos de apertura).")
    periodo = "inicial" if inicial else periodo
    if not inicial and fz.cerrado(periodo):
        sys.exit(f"{periodo} está cerrado: reábrelo con --reabrir {periodo} --quien --motivo antes de volver a importar.")
    filas, hoja = leer_tabla(archivo)
    enc, cols = detectar_columnas(filas, mapa)
    if enc is None:
        sys.exit("No encontré la fila de encabezados (busco columnas como «Código/Cuenta» y «Debe/Débito» o «Saldo deudor»). "
                 "Indica las columnas con --mapa mapa.yaml (cuenta, nombre, debe, haber, fila_encabezado).")
    nuevas, sin_plan, omitidas = [], set(), 0
    for fila in filas[enc + 1:]:
        cuenta = cuenta_norm(fila[cols["cuenta"]] if cols["cuenta"] < len(fila) else "")
        nombre = str(fila[cols["nombre"]]).strip() if "nombre" in cols and cols["nombre"] < len(fila) else ""
        if not cuenta or re.match(r"^(total|suma|totales)", cuenta.lower()) or re.match(r"^(total|suma)", nombre.lower()):
            omitidas += 1 if cuenta or nombre else 0
            continue
        if "debe" in cols:
            debe = num(fila[cols["debe"]] if cols["debe"] < len(fila) else 0)
            haber = num(fila[cols["haber"]] if "haber" in cols and cols["haber"] < len(fila) else 0)
        else:
            sd = num(fila[cols["saldo_deudor"]] if cols["saldo_deudor"] < len(fila) else 0)
            sa = num(fila[cols["saldo_acreedor"]] if "saldo_acreedor" in cols and cols["saldo_acreedor"] < len(fila) else 0)
            debe, haber = (sd, 0.0) if sd else (0.0, sa)
        if acumulado and not inicial:
            previos = [f for f in fz.real if cuenta_norm(f["cuenta"]) == cuenta and f["periodo"] != periodo]
            debe -= sum(num_propio(f.get("debe")) for f in previos)
            haber -= sum(num_propio(f.get("haber")) for f in previos)
        if not debe and not haber:
            continue
        if cuenta not in fz.plan:
            sin_plan.add(f"{cuenta} {nombre}".strip())
        nuevas.append({"periodo": periodo, "cuenta": cuenta, "debe": f"{debe:.2f}".rstrip("0").rstrip("."), "haber": f"{haber:.2f}".rstrip("0").rstrip("."),
                       "origen": Path(archivo).name, "nota": nombre if cuenta not in fz.plan else ""})
    td, th = sum(num_propio(f["debe"]) for f in nuevas), sum(num_propio(f["haber"]) for f in nuevas)
    print(f"# Importación · {Path(archivo).name} → {periodo}\n")
    print(f"- Hoja/archivo: {hoja} · fila de encabezados: {enc + 1} · columnas: " + ", ".join(f"{k}={cols[k] + 1}" for k in cols))
    print(f"- Movimientos: {len(nuevas)} cuentas · debe {fmt(td)} · haber {fmt(th)} · {'cuadra' if abs(td - th) <= TOLERANCIA else 'NO CUADRA (diferencia ' + fmt(td - th) + ')'}"
          + (f" · filas de totales omitidas: {omitidas}" if omitidas else ""))
    if sin_plan:
        print(f"- Cuentas que no están en el plan ({len(sin_plan)}): " + "; ".join(sorted(sin_plan)[:12]) + (" …" if len(sin_plan) > 12 else "")
              + "\n  Se importan igual, pero no entran a los estados hasta mapearlas en plan-de-cuentas.csv.")
    reemplaza = [f for f in fz.real if f["periodo"] == periodo]
    if reemplaza:
        print(f"- {periodo} ya tenía {len(reemplaza)} movimientos: se reemplazan por los del archivo.")
    if vista_previa:
        print("\nVista previa: nada cambió. Para importar, ejecuta sin --vista-previa.")
        return 1 if abs(td - th) > TOLERANCIA else 0
    if abs(td - th) > TOLERANCIA and not inicial:
        print("\nNo se importa: el archivo no cuadra (debe ≠ haber). Revisa que sea el balance de comprobación completo del período.")
        return 1
    otros = [f for f in fz.real if f["periodo"] != periodo]
    escribir_csv(fz.carpeta / "real.csv", otros + nuevas, COLS_REAL)
    print(f"\nImportado en finanzas/real.csv ({len(nuevas)} movimientos). " + ("Siguiente: mapear las cuentas que faltan y `--revisar`." if sin_plan else "Siguiente: `--estados --periodo " + periodo + "`."))
    return 0


# ------------------------------------------------------------------------------------------------ cierres
def cerrar(fz, periodo, quien, forzar, hoy):
    if not RE_PERIODO.match(periodo or ""):
        sys.exit("Indica el período AAAA-MM.")
    if not quien:
        sys.exit("Indica --quien: el cierre lleva quién lo aprobó.")
    if periodo not in fz.periodos():
        sys.exit(f"{periodo} no tiene movimientos en real.csv: importa primero.")
    if fz.cerrado(periodo):
        print(f"{periodo} ya está cerrado ({fz.estado_cierre(periodo).get('quien')}, {fz.estado_cierre(periodo).get('fecha')}).")
        return 0
    problemas = []
    sin = fz.cuentas_sin_mapear(periodo)
    if sin:
        problemas.append(f"cuentas sin mapear: {', '.join(sorted(sin))}")
    d = sum(num_propio(f.get("debe")) for f in fz.real if f["periodo"] == periodo)
    h = sum(num_propio(f.get("haber")) for f in fz.real if f["periodo"] == periodo)
    if abs(d - h) > TOLERANCIA:
        problemas.append(f"debe {fmt(d)} ≠ haber {fmt(h)}")
    b = fz.balance(periodo)
    if abs(b["diferencia"]) > TOLERANCIA:
        problemas.append(f"el balance no cuadra (diferencia {fmt(b['diferencia'])})")
    anteriores = [p for p in fz.periodos() if p < periodo and fz.anio_fiscal(p) == fz.anio_fiscal(periodo) and not fz.cerrado(p)]
    if problemas and not forzar:
        print(f"No se cierra {periodo}: " + "; ".join(problemas) + ".\nCorrige y vuelve a intentar (con --forzar se cierra igual y queda anotado).")
        return 1
    fz.cierres.append({"periodo": periodo, "estado": "cerrado", "fecha": hoy.isoformat(), "quien": quien, "motivo": "",
                       "huella": fz.huella(periodo), "nota": ("forzado: " + "; ".join(problemas)) if problemas else ""})
    escribir_csv(fz.carpeta / "cierres.csv", fz.cierres, COLS_CIERRES)
    print(f"{periodo} cerrado por {quien} el {hoy.isoformat()}" + (" (FORZADO con problemas: " + "; ".join(problemas) + ")" if problemas else "")
          + (f". Ojo: quedan abiertos antes {', '.join(anteriores)}." if anteriores else "."))
    return 0


def reabrir(fz, periodo, quien, motivo, hoy):
    if not (quien and motivo):
        sys.exit("Reabrir lleva --quien y --motivo (queda en cierres.csv).")
    if not fz.cerrado(periodo):
        print(f"{periodo} no está cerrado.")
        return 0
    fz.cierres.append({"periodo": periodo, "estado": "reabierto", "fecha": hoy.isoformat(), "quien": quien, "motivo": motivo, "huella": "", "nota": ""})
    escribir_csv(fz.carpeta / "cierres.csv", fz.cierres, COLS_CIERRES)
    print(f"{periodo} reabierto por {quien} ({motivo}). Cuando termines: --cerrar {periodo} --quien \"{quien}\".")
    return 0


# ------------------------------------------------------------------------------------------------ forecast
def forecast(fz, metodo, version, hoy):
    ult = fz.ultimo_periodo()
    if not ult:
        sys.exit("No hay movimientos: importa primero.")
    fy = fz.anio_fiscal(ult)
    restantes = [p for p in fz.periodos_fy(fy) if p > ult]
    version = version or f"{fy}-fc-{ult[5:7]}"
    vp = fz.version_vigente(fz.ppto, "version_presupuesto")
    ultimos = [p for p in fz.periodos() if p <= ult][-3:]
    nuevas = []
    for l in fz.lineas.get("resultado") or []:
        if l.get("formula"):
            continue
        for p in restantes:
            if metodo == "tendencia" and ultimos:
                monto = sum(fz.monto_linea_mes(l["id"], q) for q in ultimos) / len(ultimos)
            else:
                monto = fz.monto_version(fz.ppto, l["id"], p, vp)
            nuevas.append({"periodo": p, "linea": l["id"], "monto": f"{monto:.2f}".rstrip("0").rstrip("."), "version": version,
                           "metodo": metodo, "nota": f"real hasta {ult}"})
    otras = [f for f in fz.fc if f.get("version") != version]
    escribir_csv(fz.carpeta / "forecast.csv", otras + nuevas, COLS_FORECAST)
    yml = fz.raiz / "proyecto.yaml"
    if yml.exists():
        yml.write_text(poner_campo(yml.read_text(encoding="utf-8"), "version_forecast", version), encoding="utf-8")
    fz.fc = otras + nuevas
    fz.fin["version_forecast"] = version
    anio = tabla_resultado(fz, ult)
    rn = next((f for f in anio if f["id"] == "resultado_neto"), None)
    print(f"Forecast {version} ({metodo}): real hasta {ult} + {len(restantes)} meses ({', '.join(restantes[:3])}{'…' if len(restantes) > 3 else ''}). "
          f"Versión vigente en proyecto.yaml." + (f" Año {fy}: resultado neto {fmt(rn['anio'])} (presupuesto {fmt(rn['ppto_anio'])})." if rn else ""))
    return 0


# ------------------------------------------------------------------------------------------------ proyección
def lista(v, n):
    if isinstance(v, list):
        return [float(x) for x in (v + [v[-1]] * n)[:n]]
    return [float(v or 0)] * n


def proyectar(fz, salida_excel):
    ruta = fz.carpeta / "proyeccion.yaml"
    if not ruta.exists():
        sys.exit("Falta finanzas/proyeccion.yaml (cópialo de arquetipos/finanzas/estructura/finanzas/).")
    cfg = yaml.safe_load(ruta.read_text(encoding="utf-8")) or {}
    s = cfg.get("supuestos") or {}
    base = dict(cfg.get("base") or {})
    n = int(cfg.get("anios") or 3)
    anio0 = int(cfg.get("anio_base") or (fz.anio_fiscal(fz.ultimo_periodo()) if fz.ultimo_periodo() else date.today().year))
    if fz.ultimo_periodo() and not any(float(base.get(k) or 0) for k in ("ingresos", "caja", "capital")):
        ult = fz.ultimo_periodo()
        ra = fz.resultado_acumulado(ult)
        b = fz.balance(ult)["lineas"]
        gastos_ids = [l["id"] for l in fz.lineas.get("resultado") or [] if l.get("tipo") == "gasto" and l["id"] not in ("depreciacion", "impuestos", "resultado_financiero")]
        base.update({"ingresos": ra.get("ingresos", 0.0) + ra.get("otros_ingresos", 0.0), "costo_ventas": ra.get("costo_ventas", 0.0),
                     "gastos_operacionales": sum(ra.get(g, 0.0) for g in gastos_ids), "depreciacion": ra.get("depreciacion", 0.0),
                     "caja": b.get("caja", 0.0), "cuentas_por_cobrar": b.get("cuentas_por_cobrar", 0.0), "inventario": b.get("inventario", 0.0),
                     "activo_fijo_neto": b.get("activo_fijo", 0.0) + b.get("depreciacion_acumulada", 0.0),
                     "otros_activos": b.get("otros_activos_corrientes", 0.0) + b.get("otros_activos_no_corrientes", 0.0),
                     "cuentas_por_pagar": b.get("cuentas_por_pagar", 0.0),
                     "otros_pasivos": b.get("otros_pasivos_corrientes", 0.0) + b.get("otros_pasivos_no_corrientes", 0.0),
                     "deuda": b.get("deuda_corto_plazo", 0.0) + b.get("deuda_largo_plazo", 0.0), "capital": b.get("capital", 0.0),
                     "resultados_acumulados": b.get("resultados_acumulados", 0.0) + b.get("_resultados_no_traspasados", 0.0) + b.get("resultado_del_ejercicio", 0.0)})
        origen_base = f"real acumulado hasta {ult}"
    else:
        origen_base = "proyeccion.yaml (base)"
    g = lambda k, d=0.0: float(base.get(k) or d)  # noqa: E731
    crec, dep, capex, amort = lista(s.get("crecimiento_ingresos", 0), n), lista(s.get("depreciacion_anual", 0), n), lista(s.get("capex_anual", 0), n), lista(s.get("amortizacion_deuda_anual", 0), n)
    mb, gop, dc, dp, di = float(s.get("margen_bruto_pct") or 0), float(s.get("gastos_operacionales_pct") or 0), float(s.get("dias_cobro") or 0), float(s.get("dias_pago") or 0), float(s.get("dias_inventario") or 0)
    ti, tint, divp = float(s.get("tasa_impuesto") or 0), float(s.get("tasa_interes_deuda") or 0), float(s.get("dividendos_pct") or 0)
    anios = [anio0 + i + 1 for i in range(n)]
    dif_base = (g("caja") + g("cuentas_por_cobrar") + g("inventario") + g("activo_fijo_neto") + g("otros_activos")) \
        - (g("cuentas_por_pagar") + g("otros_pasivos") + g("deuda") + g("capital") + g("resultados_acumulados"))
    prev = {"ingresos": g("ingresos"), "resultado_neto": 0.0, "caja": g("caja"), "cxc": g("cuentas_por_cobrar"), "inv": g("inventario"),
            "afn": g("activo_fijo_neto"), "otros_a": g("otros_activos"), "cxp": g("cuentas_por_pagar"), "otros_p": g("otros_pasivos"),
            "deuda": g("deuda"), "capital": g("capital"), "ra": g("resultados_acumulados")}
    filas = []
    for i, a in enumerate(anios):
        ing = prev["ingresos"] * (1 + crec[i])
        costo = ing * (1 - mb)
        gastos = ing * gop
        ebitda = ing - costo - gastos
        interes = prev["deuda"] * tint
        rai = ebitda - dep[i] - interes
        imp = max(rai, 0.0) * ti
        rn = rai - imp
        cxc, inv, cxp = ing * dc / 365, costo * di / 365, costo * dp / 365
        afn = prev["afn"] + capex[i] - dep[i]
        deuda = max(prev["deuda"] - amort[i], 0.0)
        div = max(prev["resultado_neto"], 0.0) * divp
        ra = prev["ra"] + rn - div
        operacion = rn + dep[i] - (cxc - prev["cxc"]) - (inv - prev["inv"]) + (cxp - prev["cxp"])
        inversion = -capex[i]
        financiamiento = -(prev["deuda"] - deuda) - div
        caja = prev["caja"] + operacion + inversion + financiamiento
        activo = caja + cxc + inv + afn + prev["otros_a"]
        pasivo_pat = cxp + prev["otros_p"] + deuda + prev["capital"] + ra
        filas.append({"anio": a, "ingresos": ing, "costo": costo, "margen_bruto": ing - costo, "gastos": gastos, "ebitda": ebitda, "depreciacion": dep[i],
                      "intereses": interes, "rai": rai, "impuesto": imp, "resultado_neto": rn, "caja": caja, "cxc": cxc, "inv": inv, "afn": afn,
                      "otros_a": prev["otros_a"], "cxp": cxp, "otros_p": prev["otros_p"], "deuda": deuda, "capital": prev["capital"], "ra": ra,
                      "activo": activo, "pasivo_pat": pasivo_pat, "operacion": operacion, "inversion": inversion, "financiamiento": financiamiento,
                      "dividendos": div, "cuadra": abs(activo - pasivo_pat) <= TOLERANCIA})
        prev = {"ingresos": ing, "resultado_neto": rn, "caja": caja, "cxc": cxc, "inv": inv, "afn": afn, "otros_a": prev["otros_a"], "cxp": cxp,
                "otros_p": prev["otros_p"], "deuda": deuda, "capital": prev["capital"], "ra": ra}
    print(f"# Proyección · {cfg.get('nombre') or fz.raiz.name} · base {anio0} ({origen_base})\n")
    print("| Concepto | " + " | ".join(str(f["anio"]) for f in filas) + " |\n|---|" + "---:|" * len(filas))
    for k, nombre in (("ingresos", "Ingresos"), ("costo", "Costo de ventas"), ("margen_bruto", "Margen bruto"), ("gastos", "Gastos operacionales"), ("ebitda", "EBITDA"),
                      ("depreciacion", "Depreciación"), ("intereses", "Intereses"), ("impuesto", "Impuesto"), ("resultado_neto", "Resultado neto"),
                      ("operacion", "Flujo de operación"), ("inversion", "Flujo de inversión"), ("financiamiento", "Flujo de financiamiento"), ("caja", "Caja final"),
                      ("cxc", "Cuentas por cobrar"), ("inv", "Inventario"), ("afn", "Activo fijo neto"), ("cxp", "Cuentas por pagar"), ("deuda", "Deuda"),
                      ("ra", "Resultados acumulados"), ("activo", "Activo total"), ("pasivo_pat", "Pasivo + patrimonio")):
        print(f"| {nombre} | " + " | ".join(fmt(f[k]) for f in filas) + " |")
    if abs(dif_base) > TOLERANCIA:
        print(f"\nATENCIÓN: la base no cuadra (activo − pasivo − patrimonio = {fmt(dif_base)}): hay cuentas sin mapear o saldos de apertura "
              "incompletos. La proyección arrastra esa diferencia; corrige la base (--revisar) antes de usarla.")
    print("\nEl balance proyectado " + ("cuadra todos los años." if all(f["cuadra"] for f in filas) else
                                        ("arrastra la diferencia de la base." if abs(dif_base) > TOLERANCIA else "NO cuadra: revisa los supuestos de base.")))
    minimo = min(f["caja"] for f in filas)
    if minimo < 0:
        print(f"ALERTA: la caja se vuelve negativa (mínimo {fmt(minimo)}): hace falta financiamiento o ajustar supuestos.")
    if salida_excel:
        excel_proyeccion(fz, cfg, base, anio0, anios, salida_excel)
        print(f"Excel con fórmulas: {salida_excel}")
    return 0


def excel_proyeccion(fz, cfg, base, anio0, anios, salida):
    from openpyxl import Workbook
    from openpyxl.styles import Font
    from openpyxl.utils import get_column_letter as L
    s = cfg.get("supuestos") or {}
    n = len(anios)
    wb = Workbook()
    sup = wb.active
    sup.title = "Supuestos"
    azul, negrita = Font(color="0000FF"), Font(bold=True)
    sup.append(["Supuesto", "Valor"] + [str(a) for a in anios])
    celdas = {}
    fila = 2
    for clave, nombre in (("ingresos", "Ingresos año base"), ("costo_ventas", "Costo de ventas año base"), ("caja", "Caja inicial"), ("cuentas_por_cobrar", "Cuentas por cobrar inicial"),
                          ("inventario", "Inventario inicial"), ("activo_fijo_neto", "Activo fijo neto inicial"), ("otros_activos", "Otros activos"),
                          ("cuentas_por_pagar", "Cuentas por pagar inicial"), ("otros_pasivos", "Otros pasivos"), ("deuda", "Deuda inicial"),
                          ("capital", "Capital"), ("resultados_acumulados", "Resultados acumulados iniciales")):
        sup.cell(row=fila, column=1, value=nombre)
        c = sup.cell(row=fila, column=2, value=float(base.get(clave) or 0))
        c.font = azul
        celdas[clave] = f"Supuestos!$B${fila}"
        fila += 1
    for clave, nombre in (("margen_bruto_pct", "Margen bruto %"), ("gastos_operacionales_pct", "Gastos operacionales % ingresos"), ("dias_cobro", "Días de cobro"),
                          ("dias_pago", "Días de pago"), ("dias_inventario", "Días de inventario"), ("tasa_impuesto", "Tasa de impuesto"),
                          ("tasa_interes_deuda", "Tasa de interés de la deuda"), ("dividendos_pct", "Dividendos % del resultado anterior")):
        sup.cell(row=fila, column=1, value=nombre)
        c = sup.cell(row=fila, column=2, value=float(s.get(clave) or 0))
        c.font = azul
        celdas[clave] = f"Supuestos!$B${fila}"
        fila += 1
    por_anio = {}
    for clave, nombre in (("crecimiento_ingresos", "Crecimiento de ingresos"), ("depreciacion_anual", "Depreciación"), ("capex_anual", "Capex"), ("amortizacion_deuda_anual", "Amortización de deuda")):
        sup.cell(row=fila, column=1, value=nombre)
        vals = lista(s.get(clave, 0), n)
        for j, v in enumerate(vals, start=3):
            sup.cell(row=fila, column=j, value=v).font = azul
        por_anio[clave] = fila
        fila += 1
    p = wb.create_sheet("Proyeccion")
    p.cell(row=1, column=1, value="Concepto").font = negrita
    p.cell(row=1, column=2, value=f"Base {anio0}").font = negrita
    for j, a in enumerate(anios, start=3):
        p.cell(row=1, column=j, value=str(a)).font = negrita
    conceptos = ["Ingresos", "Costo de ventas", "Margen bruto", "Gastos operacionales", "EBITDA", "Depreciación", "Intereses", "Resultado antes de impuestos",
                 "Impuesto", "Resultado neto", "Dividendos", "Cuentas por cobrar", "Inventario", "Activo fijo neto", "Otros activos", "Caja", "Activo total",
                 "Cuentas por pagar", "Otros pasivos", "Deuda", "Capital", "Resultados acumulados", "Pasivo + patrimonio", "Diferencia (debe ser 0)",
                 "Flujo de operación", "Flujo de inversión", "Flujo de financiamiento"]
    R = {c: i + 2 for i, c in enumerate(conceptos)}
    for c, i in R.items():
        p.cell(row=i, column=1, value=c).font = negrita if c in ("Margen bruto", "EBITDA", "Resultado neto", "Activo total", "Pasivo + patrimonio") else Font()
    # columna base
    B = "B"
    for c, clave in (("Ingresos", "ingresos"), ("Costo de ventas", "costo_ventas"), ("Cuentas por cobrar", "cuentas_por_cobrar"), ("Inventario", "inventario"),
                     ("Activo fijo neto", "activo_fijo_neto"), ("Otros activos", "otros_activos"), ("Caja", "caja"), ("Cuentas por pagar", "cuentas_por_pagar"),
                     ("Otros pasivos", "otros_pasivos"), ("Deuda", "deuda"), ("Capital", "capital"), ("Resultados acumulados", "resultados_acumulados")):
        p.cell(row=R[c], column=2, value=f"={celdas[clave]}")
    p.cell(row=R["Resultado neto"], column=2, value=0)
    for j in range(3, n + 3):
        c, q = L(j), L(j - 1)
        k = j  # columna del supuesto por año en Supuestos (C.. para el año 1)
        p.cell(row=R["Ingresos"], column=j, value=f"={q}{R['Ingresos']}*(1+Supuestos!{L(k)}{por_anio['crecimiento_ingresos']})")
        p.cell(row=R["Costo de ventas"], column=j, value=f"={c}{R['Ingresos']}*(1-{celdas['margen_bruto_pct']})")
        p.cell(row=R["Margen bruto"], column=j, value=f"={c}{R['Ingresos']}-{c}{R['Costo de ventas']}")
        p.cell(row=R["Gastos operacionales"], column=j, value=f"={c}{R['Ingresos']}*{celdas['gastos_operacionales_pct']}")
        p.cell(row=R["EBITDA"], column=j, value=f"={c}{R['Margen bruto']}-{c}{R['Gastos operacionales']}")
        p.cell(row=R["Depreciación"], column=j, value=f"=Supuestos!{L(k)}{por_anio['depreciacion_anual']}")
        p.cell(row=R["Intereses"], column=j, value=f"={q}{R['Deuda']}*{celdas['tasa_interes_deuda']}")
        p.cell(row=R["Resultado antes de impuestos"], column=j, value=f"={c}{R['EBITDA']}-{c}{R['Depreciación']}-{c}{R['Intereses']}")
        p.cell(row=R["Impuesto"], column=j, value=f"=MAX({c}{R['Resultado antes de impuestos']},0)*{celdas['tasa_impuesto']}")
        p.cell(row=R["Resultado neto"], column=j, value=f"={c}{R['Resultado antes de impuestos']}-{c}{R['Impuesto']}")
        p.cell(row=R["Dividendos"], column=j, value=f"=MAX({q}{R['Resultado neto']},0)*{celdas['dividendos_pct']}")
        p.cell(row=R["Cuentas por cobrar"], column=j, value=f"={c}{R['Ingresos']}*{celdas['dias_cobro']}/365")
        p.cell(row=R["Inventario"], column=j, value=f"={c}{R['Costo de ventas']}*{celdas['dias_inventario']}/365")
        p.cell(row=R["Activo fijo neto"], column=j, value=f"={q}{R['Activo fijo neto']}+Supuestos!{L(k)}{por_anio['capex_anual']}-{c}{R['Depreciación']}")
        p.cell(row=R["Otros activos"], column=j, value=f"={q}{R['Otros activos']}")
        p.cell(row=R["Cuentas por pagar"], column=j, value=f"={c}{R['Costo de ventas']}*{celdas['dias_pago']}/365")
        p.cell(row=R["Otros pasivos"], column=j, value=f"={q}{R['Otros pasivos']}")
        p.cell(row=R["Deuda"], column=j, value=f"=MAX({q}{R['Deuda']}-Supuestos!{L(k)}{por_anio['amortizacion_deuda_anual']},0)")
        p.cell(row=R["Capital"], column=j, value=f"={q}{R['Capital']}")
        p.cell(row=R["Resultados acumulados"], column=j, value=f"={q}{R['Resultados acumulados']}+{c}{R['Resultado neto']}-{c}{R['Dividendos']}")
        p.cell(row=R["Flujo de operación"], column=j, value=f"={c}{R['Resultado neto']}+{c}{R['Depreciación']}-({c}{R['Cuentas por cobrar']}-{q}{R['Cuentas por cobrar']})"
                                                             f"-({c}{R['Inventario']}-{q}{R['Inventario']})+({c}{R['Cuentas por pagar']}-{q}{R['Cuentas por pagar']})")
        p.cell(row=R["Flujo de inversión"], column=j, value=f"=-Supuestos!{L(k)}{por_anio['capex_anual']}")
        p.cell(row=R["Flujo de financiamiento"], column=j, value=f"=-({q}{R['Deuda']}-{c}{R['Deuda']})-{c}{R['Dividendos']}")
        p.cell(row=R["Caja"], column=j, value=f"={q}{R['Caja']}+{c}{R['Flujo de operación']}+{c}{R['Flujo de inversión']}+{c}{R['Flujo de financiamiento']}")
        p.cell(row=R["Activo total"], column=j, value=f"={c}{R['Caja']}+{c}{R['Cuentas por cobrar']}+{c}{R['Inventario']}+{c}{R['Activo fijo neto']}+{c}{R['Otros activos']}")
        p.cell(row=R["Pasivo + patrimonio"], column=j, value=f"={c}{R['Cuentas por pagar']}+{c}{R['Otros pasivos']}+{c}{R['Deuda']}+{c}{R['Capital']}+{c}{R['Resultados acumulados']}")
        p.cell(row=R["Diferencia (debe ser 0)"], column=j, value=f"={c}{R['Activo total']}-{c}{R['Pasivo + patrimonio']}")
    p.column_dimensions["A"].width = 32
    sup.column_dimensions["A"].width = 36
    wb.calculation.fullCalcOnLoad = True
    salida = Path(salida)
    salida.parent.mkdir(parents=True, exist_ok=True)
    wb.save(str(salida))
    try:
        import autoria
        aut = autoria.cargar_autoria(fz.raiz)
        autoria.limpiar_ooxml(salida, autor=aut.get("nombre", ""), titulo="", organizacion=aut.get("organizacion", ""))
    except Exception:
        pass


# ------------------------------------------------------------------------------------------------ registrar
def registrar(fz, periodo, hoy):
    k = fz.kpis(periodo)
    nuevas = [{"fecha": hoy.isoformat(), "entidad": "PROYECTO", "metrica": m, "valor": f"{v:.6f}".rstrip("0").rstrip("."), "fuente": FUENTE,
               "comentario": f"período {periodo}"} for m, v in k.items() if v is not None]
    n = _mediciones.registrar(fz.raiz / "metricas" / "mediciones.csv", nuevas, FUENTE, hoy.isoformat())
    print(f"Registradas {n} mediciones de {periodo} en metricas/mediciones.csv (fecha {hoy.isoformat()}).")
    return 0


# ------------------------------------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("proyecto")
    ap.add_argument("--importar", metavar="ARCHIVO")
    ap.add_argument("--periodo")
    ap.add_argument("--vista-previa", action="store_true")
    ap.add_argument("--mapa", help="YAML con los nombres de columna: cuenta, nombre, debe, haber, fila_encabezado")
    ap.add_argument("--acumulado", action="store_true", help="el archivo trae debe/haber acumulados del año: se importa la diferencia")
    ap.add_argument("--inicial", action="store_true", help="saldos de apertura (período «inicial»)")
    ap.add_argument("--estados", action="store_true")
    ap.add_argument("--excel", metavar="SALIDA.xlsx")
    ap.add_argument("--cerrar", metavar="AAAA-MM")
    ap.add_argument("--reabrir", metavar="AAAA-MM")
    ap.add_argument("--forzar", action="store_true")
    ap.add_argument("--forecast", action="store_true")
    ap.add_argument("--metodo", choices=["presupuesto", "tendencia"], default="presupuesto")
    ap.add_argument("--version")
    ap.add_argument("--proyectar", action="store_true")
    ap.add_argument("--revisar", action="store_true")
    ap.add_argument("--registrar", action="store_true")
    ap.add_argument("--quien", default="")
    ap.add_argument("--motivo", default="")
    ap.add_argument("--hoy")
    a = ap.parse_args()
    hoy = datetime.strptime(a.hoy, "%Y-%m-%d").date() if a.hoy else date.today()
    proyecto = Path(a.proyecto)
    proyecto = proyecto if proyecto.is_absolute() else RAIZ / proyecto
    if not (proyecto / "proyecto.yaml").exists():
        sys.exit(f"No encuentro el proyecto {a.proyecto} (falta proyecto.yaml).")
    if not (proyecto / "finanzas").is_dir():
        sys.exit("El proyecto no tiene carpeta finanzas/: agrega el arquetipo con crear_proyecto.py <slug> --arquetipos finanzas.")
    fz = Finanzas(proyecto)
    if a.importar:
        mapa = yaml.safe_load(Path(a.mapa).read_text(encoding="utf-8")) if a.mapa else {}
        return importar(fz, a.importar, a.periodo, a.vista_previa, mapa or {}, a.acumulado, a.inicial, hoy)
    if a.cerrar:
        return cerrar(fz, a.cerrar, a.quien, a.forzar, hoy)
    if a.reabrir:
        return reabrir(fz, a.reabrir, a.quien, a.motivo, hoy)
    if a.forecast:
        return forecast(fz, a.metodo, a.version, hoy)
    if a.proyectar:
        return proyectar(fz, a.excel)
    if a.revisar:
        errores, avisos = revisar(fz)
        print(f"# Revisión de finanzas · {fz.raiz.name}\n")
        for e in errores:
            print(f"- ERROR: {e}")
        for w in avisos:
            print(f"- aviso: {w}")
        print(f"\nResultado: {len(errores)} error(es), {len(avisos)} aviso(s)." + (" OK." if not errores else ""))
        return 1 if errores else 0
    periodo = a.periodo or fz.ultimo_periodo()
    if a.estados or a.registrar:
        if not periodo:
            sys.exit("No hay movimientos: importa primero.")
        if not RE_PERIODO.match(periodo):
            sys.exit("Indica --periodo AAAA-MM.")
    if a.estados:
        imprimir_estados(fz, periodo)
        if a.excel:
            print(f"\nExcel con fórmulas: {excel_estados(fz, periodo, a.excel)}")
        return 0
    if a.registrar:
        return registrar(fz, periodo, hoy)
    return estado(fz, hoy)


if __name__ == "__main__":
    import _consola
    _consola.preparar()
    sys.exit(main())
