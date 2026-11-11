#!/usr/bin/env python3
"""Pronóstico de una serie mensual (ventas, gastos, unidades) con su error comprobado en datos que el método no vio.

Uso:
    python herramientas/experto.py pronosticar --datos <archivo.csv|.xlsx> [--fecha <columna>] [--valor <columna>]
                                   [--horizonte 6] [--unidad "MM$"] [--nivel auto|base|especialista] [--diagnosticar]
                                   [--proyecto <carpeta>] [--id <nombre>] [--salida <carpeta>] [--json] [--abrir]
                                   [--hoy AAAA-MM-DD] [--semilla N]

Datos: una columna de fecha (AAAA-MM-DD o AAAA-MM) y una de valor. Si no se indican, se buscan columnas llamadas
fecha, periodo o mes, y valor, monto, ventas o total. Varias filas del mismo mes se suman; un mes que falta dentro del
período se rellena por interpolación lineal y se avisa. Se necesitan al menos 6 meses.

Comprobación: se reservan los últimos meses (la cuarta parte de la serie, entre 2 y 6), cada método se ajusta con el
resto y pronostica esos meses; el error que se informa es el de esa prueba, no el del ajuste. Se elige el método de
menor error absoluto medio y el pronóstico final se hace con él sobre toda la serie.
- Nivel base (biblioteca estándar): último valor, promedio de los últimos 3 meses, tendencia lineal, mismo mes del año
  anterior (solo, o más el crecimiento anual) y tendencia lineal con estacionalidad; los tres últimos, según cuánta
  historia haya. El rango es el pronóstico más y menos el percentil 80 de los errores absolutos de la comprobación.
- Nivel especialista (statsmodels): suavizamiento exponencial con tendencia, con y sin estacionalidad de 12 meses.
  Solo se usa si mejora en al menos 5 % el error del mejor método simple; si no, se dice y se entrega el simple.

`--diagnosticar` mira los datos y dice qué nivel conviene, sin pronosticar. Recomienda el especialista cuando hay dos
años o más de historia, el mejor método simple se equivoca en más de 5 % al comprobarlo y hay algo que un modelo mejor
puede aprovechar: estacionalidad, o una tendencia que está cambiando (el método simple se queda siempre corto o largo). Deja `informe.html`, `informe.md` y
`resultado.json` en `<proyecto>/analisis/<id>/` (sin proyecto, junto al archivo de datos, en `analisis-<id>/`).
"""
import argparse
import json
import math
import re
import sys
import unicodedata
import warnings
import webbrowser
from datetime import date, datetime
from pathlib import Path

import experto

RAIZ = Path(__file__).resolve().parent.parent
MIN_MESES = 6
MEJORA_ESTACIONAL = 0.10   # hay estacionalidad si el mejor método que la usa reduce en 10 % el error del mejor que no
MEJORA_ESPECIALISTA = 0.05  # el especialista debe reducir el error del simple en 5 % para usarse
ERROR_ACEPTABLE = 0.05      # con estacionalidad, el nivel base alcanza si su mejor método se equivoca menos que esto
SEMILLA = 20261111

COLS_FECHA = ["fecha", "periodo", "mes"]
COLS_VALOR = ["valor", "monto", "ventas", "total", "venta", "unidades", "gastos", "gasto", "ingresos"]

ULTIMO, ESTACIONAL, TENDENCIA, PROMEDIO3 = "último valor", "mismo mes del año anterior", "tendencia lineal", "promedio de 3 meses"
ESTACIONAL_CRECE, TEND_ESTACIONAL = "mismo mes del año anterior más el crecimiento anual", "tendencia lineal con estacionalidad"
ESTACIONALES = (ESTACIONAL, ESTACIONAL_CRECE, TEND_ESTACIONAL)
MESES_NECESARIOS = {ESTACIONAL: 13, ESTACIONAL_CRECE: 18, TEND_ESTACIONAL: 24}  # historia mínima para ajustar cada método
HOLT, HW_ADD, HW_MUL = "Holt (tendencia)", "Holt-Winters aditivo", "Holt-Winters multiplicativo"
TEXTO_RANGO = "rango aproximado"


class Problema(Exception):
    """Algo de los datos o de las opciones que impide pronosticar; el mensaje dice qué corregir."""


# ------------------------------------------------------------------------------------------- utilidades
def sin_tildes(s):
    return "".join(c for c in unicodedata.normalize("NFD", str(s)) if unicodedata.category(c) != "Mn")


def clave(s):
    return re.sub(r"\s+", " ", sin_tildes(s).strip()).lower()


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


def etiqueta(mes):
    """Índice de mes (año * 12 + mes - 1) como AAAA-MM."""
    return f"{mes // 12:04d}-{mes % 12 + 1:02d}"


def percentil(valores, q):
    """Percentil con interpolación lineal; q entre 0 y 1."""
    v = sorted(valores)
    if not v:
        return 0.0
    pos = q * (len(v) - 1)
    i = int(math.floor(pos))
    j = min(i + 1, len(v) - 1)
    return v[i] + (v[j] - v[i]) * (pos - i)


def redondear(x, dec=4):
    return None if x is None else round(float(x), dec)


# ------------------------------------------------------------------------------------------- lectura
def fecha_de(v):
    """(año, mes) de una celda (date, datetime o texto AAAA-MM-DD, AAAA-MM, AAAA/MM, DD-MM-AAAA, DD/MM/AAAA) o None."""
    if isinstance(v, (datetime, date)):
        return v.year, v.month
    s = str(v if v is not None else "").strip()
    m = re.match(r"^(\d{4})[-/](\d{1,2})(?:[-/](\d{1,2}))?(?:[ T].*)?$", s)
    if m:
        a, me, d = int(m.group(1)), int(m.group(2)), int(m.group(3) or 1)
    else:
        m = re.match(r"^(\d{1,2})[-/](\d{1,2})[-/](\d{4})(?:[ T].*)?$", s)
        if not m:
            return None
        d, me, a = int(m.group(1)), int(m.group(2)), int(m.group(3))
    try:
        date(a, me, d)
    except ValueError:
        return None
    return a, me


def numero_de(v):
    """float de una celda, con coma o punto decimal; None si no es un número."""
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v) if math.isfinite(v) else None
    s = str(v if v is not None else "").strip()
    if not s or not re.fullmatch(r"[\$\s]*\(?\s*[-+]?[\d.,\s]*\d[\d.,\s]*\)?", s):
        return None
    import finanzas
    return finanzas.num_propio(s)  # «1234.5» es mil doscientos treinta y cuatro coma cinco; «1.234,5» también


def buscar_columna(cabecera, pedida, candidatas, que):
    claves = [clave(c) for c in cabecera]
    if pedida:
        if clave(pedida) not in claves:
            raise Problema(f"no hay una columna «{pedida}» ({que}). Las columnas son: {', '.join(str(c) for c in cabecera)}")
        return claves.index(clave(pedida))
    for c in candidatas:
        if c in claves:
            return claves.index(c)
    raise Problema(f"no encuentro la columna de {que}: indícala con --{'fecha' if que == 'fecha' else 'valor'}. "
                   f"Las columnas son: {', '.join(str(c) for c in cabecera)}")


def leer_serie(archivo, col_fecha=None, col_valor=None):
    """Serie mensual continua: ({mes: valor}, meses_con_varias_filas) ya ordenada por mes, sin rellenar."""
    archivo = Path(archivo)
    if not archivo.is_file():
        raise Problema(f"no existe el archivo {archivo.as_posix()}")
    if archivo.suffix.lower() not in (".csv", ".xlsx", ".xlsm"):
        raise Problema("el archivo de datos debe ser .csv o .xlsx")
    import finanzas
    try:
        filas, _ = finanzas.leer_tabla(archivo)
    except ImportError:
        raise Problema("para leer un .xlsx hace falta la biblioteca openpyxl; guarda los datos como .csv")
    except Exception as e:
        raise Problema(f"no se pudo leer {archivo.name}: {e}")
    if len(filas) < 2:
        raise Problema("el archivo no tiene filas de datos")
    cab = filas[0]
    i_f = buscar_columna(cab, col_fecha, COLS_FECHA, "fecha")
    i_v = buscar_columna(cab, col_valor, COLS_VALOR, "valor")
    suma, cuenta = {}, {}
    for k, fila in enumerate(filas[1:], start=2):
        celdas = list(fila) + [""] * (max(i_f, i_v) + 1 - len(fila))
        if not any(str(c).strip() for c in celdas):
            continue
        fv = fecha_de(celdas[i_f])
        if fv is None:
            raise Problema(f"fila {k}: «{celdas[i_f]}» no es una fecha (AAAA-MM-DD o AAAA-MM)")
        x = numero_de(celdas[i_v])
        if x is None:
            raise Problema(f"fila {k}: «{celdas[i_v]}» no es un número")
        mes = fv[0] * 12 + fv[1] - 1
        suma[mes] = suma.get(mes, 0.0) + x
        cuenta[mes] = cuenta.get(mes, 0) + 1
    if not suma:
        raise Problema("el archivo no tiene filas de datos")
    return suma, sum(1 for c in cuenta.values() if c > 1)


def armar_serie(suma):
    """(primer mes, valores continuos, cantidad de meses rellenados). Los huecos se interpolan linealmente."""
    ini, fin = min(suma), max(suma)
    y, rellenados = [], 0
    for mes in range(ini, fin + 1):
        y.append(suma.get(mes))
    conocidos = [i for i, v in enumerate(y) if v is not None]
    for i, v in enumerate(y):
        if v is None:
            a = max(c for c in conocidos if c < i)
            b = min(c for c in conocidos if c > i)
            y[i] = y[a] + (y[b] - y[a]) * (i - a) / (b - a)
            rellenados += 1
    return ini, y, rellenados


# ------------------------------------------------------------------------------------------- nivel base
def m_ultimo(y, h):
    return [y[-1]] * h


def m_estacional(y, h):
    base = y[-12:]
    return [base[k % 12] for k in range(h)]


def m_tendencia(y, h):
    m = len(y)
    mt, my = (m - 1) / 2.0, sum(y) / m
    sxx = sum((t - mt) ** 2 for t in range(m))
    b = sum((t - mt) * (v - my) for t, v in zip(range(m), y)) / sxx if sxx else 0.0
    a = my - b * mt
    return [a + b * (m + k) for k in range(h)]


def m_promedio3(y, h):
    return [sum(y[-3:]) / len(y[-3:])] * h


def m_estacional_crece(y, h):
    """El mismo mes del año anterior más lo que la serie creció en un año (promedio de las diferencias a 12 meses)."""
    dif = [y[i] - y[i - 12] for i in range(12, len(y))]
    crece = sum(dif) / len(dif)
    base = y[-12:]
    return [base[k % 12] + crece * (k // 12 + 1) for k in range(h)]


def m_tendencia_estacional(y, h):
    """Recta de tendencia más el desvío promedio de cada mes del año respecto de ella. Usa años completos, y la pendiente
    sale de comparar el último año con el primero: así la estacionalidad no inclina la recta."""
    z = y[len(y) % 12:]
    m = len(z)
    b = (sum(z[-12:]) - sum(z[:12])) / 12.0 / (m - 12)
    a = sum(z) / m - b * (m - 1) / 2.0
    desvios = [[] for _ in range(12)]
    for t, v in enumerate(z):
        desvios[t % 12].append(v - (a + b * t))
    estacion = [sum(d) / len(d) for d in desvios]
    return [a + b * (m + k) + estacion[(m + k) % 12] for k in range(h)]


METODOS = {ULTIMO: m_ultimo, ESTACIONAL: m_estacional, TENDENCIA: m_tendencia, PROMEDIO3: m_promedio3,
           ESTACIONAL_CRECE: m_estacional_crece, TEND_ESTACIONAL: m_tendencia_estacional}


def reservados_de(m):
    return max(2, min(6, m // 4))


def errores(real, pred):
    """{mae, mape}: error absoluto medio y porcentual medio (se omiten los meses reales iguales a cero; None si todos lo son)."""
    abs_ = [abs(r - p) for r, p in zip(real, pred)]
    pct = [abs(r - p) / abs(r) for r, p in zip(real, pred) if r != 0]
    return {"mae": sum(abs_) / len(abs_), "mape": (sum(pct) / len(pct)) if pct else None}


def comprobar_base(y, h):
    """{método: pronóstico de los h meses reservados} ajustando cada método solo con lo anterior."""
    entren, out = y[:-h], {}
    for nombre, f in METODOS.items():
        if len(entren) < MESES_NECESARIOS.get(nombre, 1):
            continue
        out[nombre] = f(entren, h)
    return out


def mejor(errs):
    return min(errs, key=lambda k: errs[k]["mae"])  # empate: el primero en el orden de los métodos


# ------------------------------------------------------------------------------------------- diagnóstico
def diagnosticar(y):
    """(recomendación, mediciones). Solo biblioteca estándar."""
    m = len(y)
    med = {}
    if m < 12:
        rec = experto.recomendacion(False, ["menos de 12 meses: no se puede medir estacionalidad"])
    elif m < 24:
        rec = experto.recomendacion(False, ["menos de dos años completos: la estacionalidad no se puede comprobar"])
    else:
        h = reservados_de(m)
        real = y[-h:]
        pred = comprobar_base(y, h)
        todos = {k: errores(real, p) for k, p in pred.items()}
        e = {k: v["mae"] for k, v in todos.items()}
        e_con = min(v for k, v in e.items() if k in ESTACIONALES)      # el mejor método que repite el patrón del año
        e_sin = min(v for k, v in e.items() if k not in ESTACIONALES)  # el mejor que no lo mira
        mejora = (e_sin - e_con) / e_sin if e_sin > 0 else 0.0
        simple = mejor(todos)
        mape = todos[simple]["mape"]
        desvios = [r - p for r, p in zip(real, pred[simple])]
        sesgo = "corto" if all(d > 0 for d in desvios) else ("largo" if all(d < 0 for d in desvios) else None)
        estacional = mejora >= MEJORA_ESTACIONAL
        falla = f"{n(mape * 100)} %" if mape is not None else f"{n(e[simple])} al mes"
        med = {"reservados": h, "mae_sin_estacionalidad": redondear(e_sin), "mae_con_estacionalidad": redondear(e_con),
               "mejora_estacional": redondear(mejora), "mejor_simple": simple, "mape_mejor_simple": redondear(mape, 6), "sesgo": sesgo}
        if mape is not None and mape <= ERROR_ACEPTABLE:
            rec = experto.recomendacion(False, [(f"hay estacionalidad, y un método simple («{simple}») ya la sigue" if estacional else
                                                 f"un método simple («{simple}») alcanza: pronostica") + f" con {falla} de error"])
        elif estacional:
            rec = experto.recomendacion(True, [f"hay estacionalidad y el mejor método simple («{simple}») todavía se equivoca en {falla}: un modelo "
                                               "que ajusta tendencia y estacionalidad juntas, con más peso en lo reciente, puede bajar ese error"])
        elif sesgo and h >= 4:
            rec = experto.recomendacion(True, [f"el mejor método simple («{simple}») se quedó {sesgo} en los {h} meses de la comprobación (error de "
                                               f"{falla}): la tendencia está cambiando, y un modelo que da más peso a lo reciente puede seguirla mejor"])
        else:
            rec = experto.recomendacion(False, ["no se ve estacionalidad ni una tendencia que esté cambiando: un método simple alcanza (su error, "
                                                f"{falla}, es el vaivén propio de la serie)"])
    return rec, med


# ------------------------------------------------------------------------------------------- nivel especialista
def _ajustar(y, h, nombre, semilla=None, rango=False):
    """Pronóstico (y, si se pide, bajo y alto por simulación) de un modelo de suavizamiento exponencial; None si no
    converge o falla. Las bibliotecas pesadas se importan aquí, no al cargar el módulo."""
    import numpy as np
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    estacional = {HOLT: None, HW_ADD: "add", HW_MUL: "mul"}[nombre]
    with warnings.catch_warnings(record=True) as avisos:
        warnings.simplefilter("always")
        try:
            modelo = ExponentialSmoothing(np.asarray(y, dtype=float), trend="add", seasonal=estacional,
                                          seasonal_periods=12 if estacional else None, initialization_method="estimated")
            res = modelo.fit(optimized=True)
            pron = np.asarray(res.forecast(h), dtype=float)
            ok = getattr(getattr(res, "mle_retvals", None), "success", True)
            sim = None
            if rango and ok and np.all(np.isfinite(pron)):
                try:
                    sim = np.asarray(res.simulate(h, repetitions=1000, error="mul" if estacional == "mul" else "add",
                                                  random_state=int(semilla or 0)), dtype=float)
                except Exception:
                    sim = None
        except Exception:
            return None
    if any("convergence" in type(a.message).__name__.lower() or "converge" in str(a.message).lower() for a in avisos):
        return None
    if not ok or not np.all(np.isfinite(pron)):
        return None
    if sim is None or not np.all(np.isfinite(sim)):
        return {"pron": [float(v) for v in pron], "bajo": None, "alto": None}
    sim = sim.reshape(h, -1)
    return {"pron": [float(v) for v in pron], "bajo": [float(np.percentile(sim[k], 10)) for k in range(h)],
            "alto": [float(np.percentile(sim[k], 90)) for k in range(h)]}


def variantes(y):
    """Los modelos que se prueban: con tendencia, y con estacionalidad solo desde 24 meses (la multiplicativa solo con valores positivos)."""
    v = [HOLT]
    if len(y) >= 24:
        v.append(HW_ADD)
        if all(x > 0 for x in y):
            v.append(HW_MUL)
    return v


# ------------------------------------------------------------------------------------------- análisis
def analizar(y, horizonte, nivel, semilla):
    """Pronostica y comprueba. Devuelve un dict con método, errores, pronóstico (valor, bajo, alto) y advertencias."""
    m, adv = len(y), []
    h = reservados_de(m)
    real = y[-h:]
    pred_base = comprobar_base(y, h)
    errs = {k: errores(real, p) for k, p in pred_base.items()}
    elegido = mejor(errs)
    abs_err = [abs(r - p) for r, p in zip(real, pred_base[elegido])]
    ancho = percentil(abs_err, 0.8)
    f_base = METODOS[elegido](y, horizonte)
    todos_no_neg = all(x >= 0 for x in y)

    def recortar(x):
        return max(0.0, x) if todos_no_neg else x
    pron = [{"valor": f, "bajo": recortar(f - ancho), "alto": f + ancho} for f in f_base]
    razon = f"fue el de menor error al comprobarlo con los últimos {h} meses"
    metodo, rango_de = elegido, f"{TEXTO_RANGO}: el pronóstico más y menos {n(ancho)}, el percentil 80 de los errores de la comprobación"
    if nivel == "especialista":
        cand = {}
        for nombre in variantes(y):
            r = _ajustar(y[:-h], h, nombre)
            if r is None:
                adv.append(f"El modelo «{nombre}» no convergió en la comprobación y se descartó.")
                continue
            cand[nombre] = r["pron"]
        e_esp = {k: errores(real, p) for k, p in cand.items()}
        errs.update(e_esp)
        if not e_esp:
            adv.append("Ningún modelo del nivel especialista se pudo ajustar: se usa el método simple.")
        else:
            mejor_e = mejor(e_esp)
            e_b, e_e = errs[elegido]["mae"], e_esp[mejor_e]["mae"]
            mejora = (e_b - e_e) / e_b if e_b > 0 else 0.0
            if mejora < MEJORA_ESPECIALISTA:
                razon = ("el método simple pronostica igual de bien: se usa el simple (el mejor del nivel especialista, "
                         f"«{mejor_e}», no reduce el error en 5 % o más; lo reduce en {n(max(mejora, 0.0) * 100)} %)")
            else:
                fin = _ajustar(y, horizonte, mejor_e, semilla, rango=True)
                if fin is None:
                    adv.append(f"El modelo «{mejor_e}» no convergió con toda la serie y se descartó: se usa el método simple.")
                    razon = "el modelo del nivel especialista no convergió con toda la serie: se usa el simple"
                else:
                    metodo = mejor_e
                    razon = (f"redujo el error absoluto medio en {n(mejora * 100)} % frente al mejor método simple («{elegido}») "
                             f"al comprobarlo con los últimos {h} meses")
                    # el rango nunca es más angosto que el error que el modelo tuvo en los meses que no vio
                    ancho_e = percentil([abs(r - p) for r, p in zip(real, cand[mejor_e])], 0.8)
                    if fin["bajo"] is not None:
                        rango_de = (f"{TEXTO_RANGO}: el más ancho entre los percentiles 10 y 90 de 1.000 simulaciones del modelo y el "
                                    f"pronóstico más y menos {n(ancho_e)}, el percentil 80 de los errores de la comprobación")
                        pron = [{"valor": f, "bajo": min(recortar(min(b, f - ancho_e)), f), "alto": max(a, f + ancho_e)}
                                for f, b, a in zip(fin["pron"], fin["bajo"], fin["alto"])]
                    else:
                        rango_de = f"{TEXTO_RANGO}: el pronóstico más y menos {n(ancho_e)}, el percentil 80 de los errores de la comprobación"
                        pron = [{"valor": f, "bajo": min(recortar(f - ancho_e), f), "alto": f + ancho_e} for f in fin["pron"]]
    return {"metodo": metodo, "razon": razon, "rango_de": rango_de, "errores": errs, "reservados": h, "pronostico": pron,
            "advertencias": adv, "mejor_base": elegido}


# ------------------------------------------------------------------------------------------- informe
def lista_yaml(valores):
    return json.dumps(valores, ensure_ascii=False)


def informe_md(res, ini, y, unidad, hoy, nivel, rec, horizonte, semilla):
    m, h = len(y), res["reservados"]
    pron = res["pronostico"]
    total = sum(p["valor"] for p in pron)
    e = res["errores"][res["metodo"]]
    promedio = total / horizonte
    if e["mape"] is not None:
        precision = f"el método se equivocó en {n(e['mape'] * 100)} % al comprobarlo con los últimos {h} meses"
        err_txt = f"{n(e['mape'] * 100)} %"
    else:
        precision = f"el método se equivocó en promedio {n(e['mae'], unidad)} al mes al comprobarlo con los últimos {h} meses"
        err_txt = n(e["mae"], unidad)
    clave_ = f"Para los próximos {horizonte} meses se espera un promedio de {n(promedio, unidad)} al mes; {precision}."
    o = ["---", "titulo: \"Pronóstico mensual\"",
         f"subtitulo: \"{etiqueta(ini)} a {etiqueta(ini + m - 1)} · {m} meses de historia · {horizonte} meses hacia adelante\"",
         f"fecha: {hoy.isoformat()}", "---", "", f"> {clave_}", "", "```cifras",
         f"Total del horizonte: {n(total, unidad)} | próximos {horizonte} meses",
         f"Error comprobado: {err_txt} | promedio en los últimos {h} meses, que el método no vio",
         f"Método: {res['metodo']} | nivel {nivel}", f"Meses de historia: {m} | de {etiqueta(ini)} a {etiqueta(ini + m - 1)}", "```", ""]
    # gráfico: últimos 24 meses reales y el pronóstico, que parte del último mes real
    k = min(24, m)
    cats = [etiqueta(ini + m - k + i) for i in range(k)] + [etiqueta(ini + m + i) for i in range(horizonte)]
    real = [redondear(v) for v in y[-k:]] + [None] * horizonte
    pr = [None] * (k - 1) + [redondear(y[-1])] + [redondear(p["valor"]) for p in pron]
    o += ["# Lo real y lo pronosticado", "", "```grafico", "tipo: lineas", "titulo: \"Últimos meses reales y pronóstico\""]
    if unidad:
        o.append(f"unidad: {json.dumps(unidad, ensure_ascii=False)}")
    o += [f"categorias: {lista_yaml(cats)}", "series:", f"  Real: {lista_yaml(real)}", f"  Pronóstico: {lista_yaml(pr)}", "```", ""]
    o += ["# El pronóstico mes a mes", "", f"{res['rango_de'].capitalize()}.", "", "| Mes | Pronóstico | Rango |", "|---|---|---|"]
    o += [f"| {etiqueta(ini + m + i)} | {n(p['valor'], unidad)} | {n(p['bajo'])} a {n(p['alto'], unidad)} |" for i, p in enumerate(pron)]
    o += ["", "# Cómo se eligió el método", "", f"Se eligió **{res['metodo']}**: {res['razon']}.", "",
          f"Cada método se ajustó sin los últimos {h} meses y pronosticó esos meses; el error es la diferencia con lo que pasó de verdad.", "",
          "| Método | Error absoluto medio | Error porcentual medio |", "|---|---|---|"]
    for nombre, er in sorted(res["errores"].items(), key=lambda x: x[1]["mae"]):
        mape = "sin dato" if er["mape"] is None else f"{n(er['mape'] * 100)} %"
        o.append(f"| {nombre}{' (elegido)' if nombre == res['metodo'] else ''} | {n(er['mae'], unidad)} | {mape} |")
    o.append("")
    if res["advertencias"]:
        o += ["# Advertencias", ""] + [f"- {a}" for a in res["advertencias"]] + [""]
    o += ["# Cómo leer esto", "",
          f"- El rango viene de los errores que el método tuvo en el pasado ({TEXTO_RANGO}): no es una garantía de que el valor real quede dentro.",
          "- Un pronóstico supone que el futuro se parece al pasado. No incorpora hechos que la serie no ha visto: un cliente nuevo, un cambio de precio, una huelga, una campaña.",
          "- A más meses hacia adelante, más ancho debería leerse el rango: la comprobación midió el error en los primeros meses, y se acumula con la distancia.",
          f"- El error comprobado se midió con {h} meses; con tan pocos meses es una referencia, no una cifra exacta.",
          f"- Para repetir exactamente este resultado: semilla {semilla}."]
    if any(k in res["errores"] for k in (HOLT, HW_ADD, HW_MUL)):
        o.append("- «Holt» y «Holt-Winters» son suavizamientos exponenciales: dan más peso a los meses recientes. El primero sigue la "
                 "tendencia; el segundo, además, el patrón que se repite cada 12 meses (sumado, «aditivo», o como porcentaje, «multiplicativo»).")
    o += ["- " + experto.nota_de_nivel(rec, nivel), ""]
    return "\n".join(o)


def proyecto_valido(ruta):
    p = Path(ruta)
    if not p.is_dir():
        raise Problema(f"no existe la carpeta del proyecto {p.as_posix()}")
    return p


# ------------------------------------------------------------------------------------------- consola
def resumen_datos(ini, y, rellenados):
    return {"meses": len(y), "desde": etiqueta(ini), "hasta": etiqueta(ini + len(y) - 1), "rellenados": rellenados}


def ejecutar(a):
    try:
        hoy = date.fromisoformat(a.hoy) if a.hoy else date.today()
    except ValueError:
        raise Problema("--hoy debe ser AAAA-MM-DD")
    if a.horizonte < 1:
        raise Problema("--horizonte debe ser 1 o más")
    if not a.datos:
        raise Problema("indica el archivo con --datos <archivo .csv o .xlsx>")
    ident = a.id or f"pronostico-{hoy.isoformat()}"
    if not re.fullmatch(r"[\w.-]+", ident):
        raise Problema("--id: solo letras, números, guiones y puntos (por ejemplo, ventas-2027)")
    suma, varias = leer_serie(a.datos, a.fecha, a.valor)
    ini, y, rellenados = armar_serie(suma)
    adv = []
    if rellenados:
        adv.append(f"Faltaban {rellenados} {'mes' if rellenados == 1 else 'meses'} dentro del período: se rellenaron por interpolación lineal.")
    if varias:
        adv.append(f"Había varias filas en {varias} {'mes' if varias == 1 else 'meses'}: se sumaron.")
    datos = resumen_datos(ini, y, rellenados)
    rec, med = diagnosticar(y)
    if a.diagnosticar:
        if len(y) < MIN_MESES:
            adv.append(f"Hay solo {len(y)} meses: no alcanzan para pronosticar (se necesitan al menos {MIN_MESES}).")
        if a.json:
            print(json.dumps({"recomendacion": rec, "datos": datos, "mediciones": med, "advertencias": adv}, ensure_ascii=False, indent=2))
            return 0
        print(f"# Diagnóstico de la serie\n\n- Período: {datos['desde']} a {datos['hasta']} ({datos['meses']} meses)")
        if med:
            print(f"- Comprobación en los últimos {med['reservados']} meses: el mejor método que repite el patrón del año se equivoca en "
                  f"{n(med['mae_con_estacionalidad'])} al mes; el mejor que no lo mira, en {n(med['mae_sin_estacionalidad'])}.")
            if med["sesgo"]:
                print(f"- El mejor método simple («{med['mejor_simple']}») se quedó {med['sesgo']} en todos esos meses.")
        for x in adv:
            print(f"- Aviso: {x}")
        print("\n".join(experto.texto_recomendacion(rec, None)))
        return 0
    if len(y) < MIN_MESES:
        raise Problema(f"hay solo {len(y)} meses de datos: se necesitan al menos {MIN_MESES} para pronosticar")
    nivel = experto.resolver_nivel(a.nivel)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        res = analizar(y, a.horizonte, nivel, a.semilla)
    adv += res["advertencias"]
    res["advertencias"] = adv
    salida = {"nivel": nivel, "recomendacion": rec, "datos": datos, "metodo": res["metodo"],
              "errores": {k: {"mae": redondear(v["mae"]), "mape": redondear(v["mape"], 6)} for k, v in res["errores"].items()},
              "reservados": res["reservados"],
              "pronostico": [{"periodo": etiqueta(ini + len(y) + i), "valor": redondear(p["valor"]), "bajo": redondear(p["bajo"]),
                              "alto": redondear(p["alto"])} for i, p in enumerate(res["pronostico"])],
              "advertencias": adv, "semilla": a.semilla}
    if a.json:
        print(json.dumps(salida, ensure_ascii=False, indent=2))
        return 0
    unidad = (a.unidad or "").strip()
    md = informe_md(res, ini, y, unidad, hoy, nivel, rec, a.horizonte, a.semilla)
    proyecto, cfg = None, {}
    if a.proyecto:
        proyecto = proyecto_valido(a.proyecto)
        if (proyecto / "proyecto.yaml").exists():
            import _config
            cfg = _config.cargar(proyecto)
    else:
        proyecto = None
    if a.salida:
        carpeta = Path(a.salida)
    elif proyecto:
        carpeta = proyecto / "analisis" / ident
    else:
        carpeta = Path(a.datos).resolve().parent / f"analisis-{ident}"
    carpeta.mkdir(parents=True, exist_ok=True)
    import explicar
    try:
        pagina, _ = explicar.generar(md, carpeta, cfg, proyecto if (proyecto and (proyecto / "proyecto.yaml").exists()) else None, hoy)
    except explicar.Problema as e:
        raise Problema(f"no se pudo armar la página del informe: {e}")
    (carpeta / "informe.md").write_text(md, encoding="utf-8")
    (carpeta / "informe.html").write_text(pagina, encoding="utf-8")
    (carpeta / "resultado.json").write_text(json.dumps(salida, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    total = sum(p["valor"] for p in res["pronostico"])
    print(f"# Pronóstico: {datos['meses']} meses de historia ({datos['desde']} a {datos['hasta']})\n")
    print(f"- Método: **{res['metodo']}** (nivel {nivel}): {res['razon']}.")
    print(f"- Total de los próximos {a.horizonte} meses: {n(total, unidad)}\n")
    print("| Mes | Pronóstico | Rango |\n|---|---|---|")
    for p in salida["pronostico"]:
        print(f"| {p['periodo']} | {n(p['valor'], unidad)} | {n(p['bajo'])} a {n(p['alto'], unidad)} |")
    print(f"\n{res['rango_de'].capitalize()}.\n")
    print(f"Error comprobado en los últimos {res['reservados']} meses, que el método no vio:\n")
    print("| Método | Error absoluto medio | Error porcentual medio |\n|---|---|---|")
    for nombre, er in sorted(res["errores"].items(), key=lambda x: x[1]["mae"]):
        mape = "sin dato" if er["mape"] is None else f"{n(er['mape'] * 100)} %"
        print(f"| {nombre}{' (elegido)' if nombre == res['metodo'] else ''} | {n(er['mae'], unidad)} | {mape} |")
    if adv:
        print("\nAdvertencias:")
        for x in adv:
            print(f"- {x}")
    print()
    print("\n".join(experto.texto_recomendacion(rec, nivel)))
    ruta = carpeta / "informe.html"
    print(f"\nPágina: {ruta.as_posix()}")
    if a.abrir:
        webbrowser.open(ruta.resolve().as_uri())
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="experto.py pronosticar", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--datos", help="archivo .csv o .xlsx con una columna de fecha y una de valor")
    ap.add_argument("--fecha", help="nombre de la columna de fecha (por defecto: fecha, periodo o mes)")
    ap.add_argument("--valor", help="nombre de la columna de valor (por defecto: valor, monto, ventas o total)")
    ap.add_argument("--horizonte", type=int, default=6, help="meses hacia adelante (por defecto 6)")
    ap.add_argument("--unidad", default="", help="unidad con que se escriben los valores, por ejemplo \"MM$\"")
    ap.add_argument("--nivel", default="auto", choices=["auto", "base", "especialista"], help="nivel de análisis (por defecto auto)")
    ap.add_argument("--diagnosticar", action="store_true", help="solo mirar los datos y decir qué nivel conviene")
    ap.add_argument("--proyecto", help="carpeta del proyecto (marca y carpeta de salida)")
    ap.add_argument("--id", help="nombre del análisis (por defecto pronostico-<hoy>)")
    ap.add_argument("--salida", help="carpeta de salida (por defecto <proyecto>/analisis/<id>/ o analisis-<id>/ junto a los datos)")
    ap.add_argument("--json", action="store_true", help="imprimir solo el JSON, sin escribir archivos")
    ap.add_argument("--abrir", action="store_true", help="abrir la página en el navegador")
    ap.add_argument("--hoy", help="fecha AAAA-MM-DD (pruebas)")
    ap.add_argument("--semilla", type=int, default=SEMILLA, help=f"semilla de la simulación (por defecto {SEMILLA})")
    a = ap.parse_args(argv)
    try:
        return ejecutar(a)
    except Problema as e:
        print(f"No se pudo pronosticar: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    import _consola
    _consola.preparar()
    sys.exit(main())
