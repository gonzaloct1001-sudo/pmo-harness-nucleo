#!/usr/bin/env python3
"""Rentabilidad por cliente y por producto, con un mapa de clientes en cuatro cuadrantes.

Uso:
    python herramientas/rentabilidad.py <proyecto>                                       # estado y siguiente paso
    python herramientas/rentabilidad.py <proyecto> --importar-ventas <archivo.csv|.xlsx> [--mapa-columnas "cliente=Razón Social,precio=Neto"]
    python herramientas/rentabilidad.py <proyecto> --importar-cxc <archivo> [--fecha AAAA-MM-DD]
    python herramientas/rentabilidad.py <proyecto> --normalizar
    python herramientas/rentabilidad.py <proyecto> --quien <id o parte de un nombre>
    python herramientas/rentabilidad.py <proyecto> --analizar [--desde AAAA-MM-DD] [--hasta AAAA-MM-DD] [--costo-hora N]
                                       [--corte-afinidad X] [--corte-contribucion Y] [--con-nombres] [--abrir]
                                       [--hoy AAAA-MM-DD] [--json]

Datos, dentro de <proyecto>/finanzas/ (CSV en UTF-8, con coma; fechas AAAA-MM-DD; números con punto decimal al escribir):
- ventas.csv: fecha,documento,cliente_id,producto,cantidad,precio_unitario,costo_unitario,canal
- cxc.csv: fecha,cliente_id,saldo                       (cuentas por cobrar por cliente a una fecha)
- clientes.csv: cliente_id,horas_periodo,afinidad,fecha_afinidad,segmento,nota
- _local/clientes-mapa.csv: cliente_id,nombre,identificador,creado     (LOCAL: nunca se sube ni sale del computador)

Regla de privacidad: en los datos del proyecto los clientes van siempre como identificador (C-0001, C-0002…). El nombre
real vive solo en el mapa local. Si alguien escribe un nombre en ventas.csv, cxc.csv o clientes.csv, el script lo convierte
en identificador al comenzar cualquier comando. Los resultados agregados (cuadrantes, productos, totales) se usan libremente.

Cálculos de --analizar (sobre las líneas de venta del período):
- Producto: ventas = Σ cantidad × precio; costo = Σ cantidad × costo; margen = ventas − costo.
- Cliente: ventas, margen, cuentas por cobrar (su saldo más reciente con fecha ≤ hasta), días de cobro (saldo ÷ ventas × días
  del período), costo de servir (horas × costo por hora), contribución = margen − costo de servir, contribución % = contribución ÷ ventas.
- Mapa: x = afinidad, y = contribución %, tamaño = margen. Cortes en la mediana de cada eje (un cliente justo en el corte
  cuenta en el lado alto). Cuadrantes: Cuidar, Asegurar, Desarrollar, Revisar.
El mapa describe el período analizado y no predice. No estima el costo de un cliente ni escenarios de reemplazo o venta cruzada.
"""
import argparse
import csv
import json
import math
import re
import statistics
import sys
import unicodedata
import webbrowser
from datetime import date, datetime, timedelta
from pathlib import Path

import finanzas

RAIZ = Path(__file__).resolve().parent.parent
FUENTE = "herramientas/rentabilidad.py"

COLS_VENTAS = ["fecha", "documento", "cliente_id", "producto", "cantidad", "precio_unitario", "costo_unitario", "canal"]
COLS_CXC = ["fecha", "cliente_id", "saldo"]
COLS_CLIENTES = ["cliente_id", "horas_periodo", "afinidad", "fecha_afinidad", "segmento", "nota"]
COLS_MAPA = ["cliente_id", "nombre", "identificador", "creado"]
ARCHIVOS_DATOS = {"ventas.csv": COLS_VENTAS, "cxc.csv": COLS_CXC, "clientes.csv": COLS_CLIENTES}

RE_ID = re.compile(r"^C-\d{4,}$")
MIN_CLIENTES_MAPA = 8
PROPORCION_CONCENTRACION = 0.20
NOTA_MAPA = "El mapa describe el período analizado y no predice."

# Cuadrantes: clave (afinidad_contribución) → nombre.
Q_CUIDAR, Q_ASEGURAR, Q_DESARROLLAR, Q_REVISAR = "Cuidar", "Asegurar", "Desarrollar", "Revisar"
CUADRANTES = {"alto_alto": Q_CUIDAR, "bajo_alto": Q_ASEGURAR, "alto_bajo": Q_DESARROLLAR, "bajo_bajo": Q_REVISAR}
ORDEN_CUADRANTES = ["alto_alto", "bajo_alto", "alto_bajo", "bajo_bajo"]


# ------------------------------------------------------------------------------------------------ utilidades
def sin_tildes(s):
    return "".join(c for c in unicodedata.normalize("NFD", str(s)) if unicodedata.category(c) != "Mn")


def clave_nombre(nombre):
    """Nombre comparable: sin mayúsculas, sin tildes y con los espacios colapsados."""
    return re.sub(r"\s+", " ", sin_tildes(nombre).strip()).lower()


def limpiar_nombre(nombre):
    return re.sub(r"\s+", " ", str(nombre).strip())


def num_csv(v):
    """Número de un archivo propio (punto decimal); si no calza, acepta coma decimal y separador de miles. Vacío → None."""
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip()
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return finanzas.num(s)


def num_export(v):
    """Número de una exportación: acepta coma decimal y separador de miles. Vacío → None."""
    if v is None or (isinstance(v, str) and not v.strip()):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    return finanzas.num(v)


def texto_num(x):
    """Número para escribir en CSV: punto decimal, sin ceros sobrantes."""
    if x is None:
        return ""
    if abs(x - round(x)) < 1e-9:
        return str(int(round(x)))
    return repr(round(x, 6))


def fecha_de(v):
    """date de una celda (date, datetime o texto AAAA-MM-DD, DD-MM-AAAA, DD/MM/AAAA, AAAA/MM/DD); None si no se entiende."""
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v
    s = str(v or "").strip()[:10]
    for f in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(s, f).date()
        except ValueError:
            continue
    return None


def leer_filas(ruta):
    """(columnas, filas) de un CSV; ([], []) si no existe."""
    ruta = Path(ruta)
    if not ruta.exists():
        return [], []
    with open(ruta, encoding="utf-8-sig", newline="") as f:
        lector = csv.DictReader(f)
        columnas = [c.strip() for c in (lector.fieldnames or [])]
        filas = [{(k or "").strip(): (v or "").strip() for k, v in r.items() if k is not None} for r in lector]
    return columnas, filas


def escribir_filas(ruta, filas, columnas):
    Path(ruta).parent.mkdir(parents=True, exist_ok=True)
    with open(ruta, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columnas, extrasaction="ignore")
        w.writeheader()
        for fila in filas:
            w.writerow({c: fila.get(c, "") for c in columnas})


def asegurar_archivo(ruta, columnas):
    """Crea el archivo con su encabezado si no existe."""
    if not Path(ruta).exists():
        escribir_filas(ruta, [], columnas)


def carpeta_datos(proyecto):
    return Path(proyecto) / "finanzas"


def ruta_mapa(proyecto):
    return carpeta_datos(proyecto) / "_local" / "clientes-mapa.csv"


def miles(x, dec=0):
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def peso(x):
    return "—" if x is None else "$ " + miles(x)


def pct(x, dec=1):
    """x es una fracción (0,315 → «31,5 %»)."""
    return "—" if x is None else miles(x * 100, dec) + " %"


# ------------------------------------------------------------------------------------------------ mapa e identificadores
class Mapa:
    """Mapa local cliente_id ↔ nombre. Vive en finanzas/_local/ y nunca se sube."""

    def __init__(self, proyecto):
        self.ruta = ruta_mapa(proyecto)
        self.existe = self.ruta.exists()
        self.filas = leer_filas(self.ruta)[1]
        self.cambio = False
        self.por_nombre = {}
        self.por_identificador = {}
        for f in self.filas:
            self._indexar(f)

    def _indexar(self, f):
        if f.get("nombre"):
            self.por_nombre.setdefault(clave_nombre(f["nombre"]), f["cliente_id"])
        if f.get("identificador"):
            self.por_identificador.setdefault(re.sub(r"[.\s]", "", f["identificador"]).lower(), f["cliente_id"])

    def ids(self):
        return {f["cliente_id"] for f in self.filas}

    def nombre(self, cid):
        for f in self.filas:
            if f["cliente_id"] == cid:
                return f.get("nombre") or ""
        return ""

    def siguiente(self, usados=()):
        mayor = 0
        for cid in list(self.ids()) + list(usados):
            m = RE_ID.match(cid or "")
            if m:
                mayor = max(mayor, int(cid[2:]))
        return "C-%04d" % (mayor + 1)

    def id_de(self, nombre, identificador="", hoy=None, usados=()):
        """Id del cliente con ese nombre (o identificador); lo crea si no existe. Devuelve (id, creado)."""
        nombre = limpiar_nombre(nombre)
        clave = clave_nombre(nombre)
        cid = self.por_nombre.get(clave)
        if cid is None and identificador:
            cid = self.por_identificador.get(re.sub(r"[.\s]", "", identificador).lower())
        if cid is not None:
            if identificador:
                for f in self.filas:
                    if f["cliente_id"] == cid and not f.get("identificador"):
                        f["identificador"] = identificador.strip()
                        self.cambio = True
                        self._indexar(f)
            return cid, False
        cid = self.siguiente(usados)
        fila = {"cliente_id": cid, "nombre": nombre, "identificador": (identificador or "").strip(),
                "creado": (hoy or date.today()).isoformat()}
        self.filas.append(fila)
        self._indexar(fila)
        self.cambio = True
        return cid, True

    def guardar(self):
        if self.cambio:
            escribir_filas(self.ruta, self.filas, COLS_MAPA)
            self.existe = True
            self.cambio = False


def ids_en_datos(proyecto):
    """Ids con formato válido que aparecen en los archivos de datos (para no repetir números)."""
    usados = set()
    for nombre in ARCHIVOS_DATOS:
        for f in leer_filas(carpeta_datos(proyecto) / nombre)[1]:
            if RE_ID.match(f.get("cliente_id", "")):
                usados.add(f["cliente_id"])
    return usados


def normalizar(proyecto, hoy=None, mapa=None):
    """Convierte en identificador todo valor de `cliente_id` que sea un nombre, en ventas.csv, cxc.csv y clientes.csv.
    Reutiliza el id si el cliente ya está en el mapa (sin mayúsculas, tildes ni espacios dobles); si no, crea uno.
    Reescribe los archivos y deja el nombre solo en el mapa local. Devuelve {archivo: valores convertidos}."""
    base = carpeta_datos(proyecto)
    mapa = mapa or Mapa(proyecto)
    usados = ids_en_datos(proyecto)
    pendientes = []
    convertidos = {}
    for nombre_archivo, columnas in ARCHIVOS_DATOS.items():
        ruta = base / nombre_archivo
        cols, filas = leer_filas(ruta)
        if not filas:
            continue
        n = 0
        for f in filas:
            v = f.get("cliente_id", "")
            if v and not RE_ID.match(v):
                cid, _ = mapa.id_de(v, "", hoy, usados)
                usados.add(cid)
                f["cliente_id"] = cid
                n += 1
        if n:
            convertidos[nombre_archivo] = n
            pendientes.append((ruta, filas, cols or columnas))
    if pendientes:
        mapa.guardar()  # primero el mapa, para no perder ningún nombre
        for ruta, filas, cols in pendientes:
            escribir_filas(ruta, filas, cols)
    return convertidos


def informar_normalizacion(convertidos, salida=None):
    if not convertidos:
        return
    partes = ", ".join(f"{k}: {v}" for k, v in convertidos.items())
    print(f"Identificadores: se convirtieron {sum(convertidos.values())} nombres de clientes ({partes}); "
          "los nombres quedaron solo en finanzas/_local/clientes-mapa.csv.", file=salida or sys.stdout)


# ------------------------------------------------------------------------------------------------ importar
PATRONES_VENTAS = [
    ("rut", r"^(rut|r\.u\.t|identificador)\b"),
    ("cliente", r"^(cliente|raz[oó]n social|nombre( del)?( cliente)?|nombre fantas[ií]a)$|cliente"),
    ("documento", r"(documento|folio|factura|n[uú]mero|n[º°]|nro|n\.º)"),
    ("fecha", r"fecha"),
    ("producto", r"(producto|[ií]tem|item|servicio|descripci)"),
    ("cantidad", r"cant"),
    ("precio", r"(precio|valor)\s*(neto\s*)?unit|^precio|^valor unit"),
    ("costo", r"^costo|costo\s*unit"),
    ("total", r"(total|monto|neto|subtotal|valor l[ií]nea)"),
    ("canal", r"canal"),
]
REQUERIDAS_VENTAS = ["cliente", "producto", "cantidad", "fecha"]
CAMPOS_MAPA_VENTAS = {"cliente", "rut", "producto", "cantidad", "precio", "total", "costo", "fecha", "documento", "canal"}


def detectar_columnas_tabla(filas, patrones, requeridas, alguna_de=(), mapa=None):
    """(índice de la fila de encabezado, {campo: columna}, encabezados de la mejor fila). Si ninguna fila trae lo
    indispensable, el primer valor es None y se devuelve la fila que más se acercó."""
    mapa = {k: str(v).strip().lower() for k, v in (mapa or {}).items()}
    mejor = (-1, 0, {}, [])
    for i, fila in enumerate(filas[:40]):
        celdas = [str(c).strip().lower() for c in fila]
        if not any(celdas):
            continue
        cols = {}
        for campo, patron in patrones:
            if campo in mapa:
                idx = next((k for k, c in enumerate(celdas) if c == mapa[campo]), None)
            else:
                idx = next((k for k, c in enumerate(celdas) if c and k not in cols.values() and re.search(patron, c)), None)
            if idx is not None:
                cols[campo] = idx
        if all(r in cols for r in requeridas) and (not alguna_de or any(a in cols for a in alguna_de)):
            return i, cols, [str(c).strip() for c in fila]
        if len(cols) > mejor[1]:
            mejor = (i, len(cols), cols, [str(c).strip() for c in fila])
    return None, mejor[2], mejor[3]


def parsear_mapa_columnas(texto):
    mapa = {}
    for par in (texto or "").split(","):
        if "=" in par:
            k, v = par.split("=", 1)
            k = k.strip().lower()
            if k not in CAMPOS_MAPA_VENTAS and k != "saldo":
                sys.exit(f"--mapa-columnas: campo desconocido «{k}». Campos: {', '.join(sorted(CAMPOS_MAPA_VENTAS | {'saldo'}))}.")
            mapa[k] = v.strip()
    return mapa


def celda(fila, cols, campo):
    i = cols.get(campo)
    if i is None or i >= len(fila):
        return ""
    v = fila[i]
    return "" if v is None else v


def importar_ventas(proyecto, archivo, mapa_columnas=None, hoy=None):
    """Agrega a ventas.csv las líneas de una exportación (CSV o Excel) con nombres de clientes, que quedan como ids.
    Devuelve {agregadas, omitidas, sin_datos, clientes_nuevos} o {error: texto}."""
    if not Path(archivo).is_file():
        return {"error": f"No existe {archivo}"}
    filas, _hoja = finanzas.leer_tabla(archivo)
    i, cols, encabezados = detectar_columnas_tabla(filas, PATRONES_VENTAS, REQUERIDAS_VENTAS, ("precio", "total"), mapa_columnas)
    if i is None:
        faltan = [r for r in REQUERIDAS_VENTAS if r not in cols]
        if "precio" not in cols and "total" not in cols:
            faltan.append("precio o total")
        return {"error": "No se importó nada: falta(n) la(s) columna(s) indispensable(s): " + ", ".join(faltan) +
                         ". Encabezados encontrados: " + (", ".join(e for e in encabezados if e) or "(ninguno)") +
                         '. Indícalas con --mapa-columnas "cliente=...,producto=...".'}
    mapa = Mapa(proyecto)
    ruta = carpeta_datos(proyecto) / "ventas.csv"
    asegurar_archivo(ruta, COLS_VENTAS)
    cols_v, existentes = leer_filas(ruta)

    def llave(fecha, doc, cid, prod, cant, precio):
        return (fecha, doc, cid, prod, texto_num(cant), texto_num(precio))

    ya = set()
    for f in existentes:
        ya.add(llave(f.get("fecha", ""), f.get("documento", ""), f.get("cliente_id", ""), f.get("producto", ""),
                     num_csv(f.get("cantidad")) or 0.0, num_csv(f.get("precio_unitario")) or 0.0))
    usados = ids_en_datos(proyecto)
    nuevos_ids = set()
    agregadas, omitidas, sin_datos = [], 0, 0
    costo_total = "costo" in cols and "total" in str(encabezados[cols["costo"]]).lower()
    for fila in filas[i + 1:]:
        if not any(str(c).strip() for c in fila):
            continue
        nombre = limpiar_nombre(celda(fila, cols, "cliente"))
        fecha = fecha_de(celda(fila, cols, "fecha"))
        producto = limpiar_nombre(celda(fila, cols, "producto"))
        cant = num_export(celda(fila, cols, "cantidad"))
        precio = num_export(celda(fila, cols, "precio")) if "precio" in cols else None
        if precio is None and "total" in cols:
            total = num_export(celda(fila, cols, "total"))
            precio = (total / cant) if (total is not None and cant) else None
        if not nombre or fecha is None or not producto or not cant or precio is None:
            sin_datos += 1
            continue
        costo = num_export(celda(fila, cols, "costo")) if "costo" in cols else None
        if costo is not None and costo_total and cant:
            costo = costo / cant
        doc = str(celda(fila, cols, "documento")).strip()
        if doc.endswith(".0") and doc[:-2].isdigit():
            doc = doc[:-2]
        cid, nuevo = mapa.id_de(nombre, str(celda(fila, cols, "rut")).strip(), hoy, usados | nuevos_ids)
        if nuevo:
            nuevos_ids.add(cid)
        k = llave(fecha.isoformat(), doc, cid, producto, cant, precio)
        if k in ya:
            omitidas += 1
            continue
        agregadas.append({"fecha": fecha.isoformat(), "documento": doc, "cliente_id": cid, "producto": producto,
                          "cantidad": texto_num(cant), "precio_unitario": texto_num(precio), "costo_unitario": texto_num(costo),
                          "canal": str(celda(fila, cols, "canal")).strip()})
    mapa.guardar()
    if agregadas:
        escribir_filas(ruta, existentes + agregadas, cols_v or COLS_VENTAS)
    return {"agregadas": len(agregadas), "omitidas": omitidas, "sin_datos": sin_datos, "clientes_nuevos": len(nuevos_ids)}


PATRONES_CXC = [
    ("cliente", r"^(cliente|raz[oó]n social|nombre( del)?( cliente)?|nombre fantas[ií]a)$|cliente"),
    ("rut", r"^(rut|r\.u\.t|identificador)\b"),
    ("saldo", r"(saldo|deuda|por cobrar|monto|total)"),
    ("fecha", r"fecha"),
]


def importar_cxc(proyecto, archivo, fecha=None, mapa_columnas=None, hoy=None):
    """Saldos por cliente → cxc.csv con ids. Si el cliente trae varias filas en el archivo, se suman. Reemplaza lo que ya
    hubiera para el mismo cliente y la misma fecha. Devuelve {importados, clientes_nuevos, fecha} o {error}."""
    if not Path(archivo).is_file():
        return {"error": f"No existe {archivo}"}
    filas, _ = finanzas.leer_tabla(archivo)
    i, cols, encabezados = detectar_columnas_tabla(filas, PATRONES_CXC, ["cliente", "saldo"], (), mapa_columnas)
    if i is None:
        faltan = [r for r in ("cliente", "saldo") if r not in cols]
        return {"error": "No se importó nada: falta(n) la(s) columna(s) indispensable(s): " + ", ".join(faltan) +
                         ". Encabezados encontrados: " + (", ".join(e for e in encabezados if e) or "(ninguno)") + "."}
    por_defecto = fecha_de(fecha) if fecha else (hoy or date.today())
    if por_defecto is None:
        return {"error": f"Fecha no válida: {fecha} (usa AAAA-MM-DD)."}
    mapa = Mapa(proyecto)
    ruta = carpeta_datos(proyecto) / "cxc.csv"
    asegurar_archivo(ruta, COLS_CXC)
    cols_c, existentes = leer_filas(ruta)
    usados = ids_en_datos(proyecto)
    nuevos_ids, acum = set(), {}
    for fila in filas[i + 1:]:
        nombre = limpiar_nombre(celda(fila, cols, "cliente"))
        saldo = num_export(celda(fila, cols, "saldo"))
        if not nombre or saldo is None:
            continue
        f = fecha_de(celda(fila, cols, "fecha")) if "fecha" in cols else None
        f = f or por_defecto
        cid, nuevo = mapa.id_de(nombre, str(celda(fila, cols, "rut")).strip() if "rut" in cols else "", hoy, usados | nuevos_ids)
        if nuevo:
            nuevos_ids.add(cid)
        acum[(f.isoformat(), cid)] = acum.get((f.isoformat(), cid), 0.0) + saldo
    mapa.guardar()
    existentes = [f for f in existentes if (f.get("fecha", ""), f.get("cliente_id", "")) not in acum]
    nuevas = [{"fecha": k[0], "cliente_id": k[1], "saldo": texto_num(v)} for k, v in sorted(acum.items())]
    if nuevas:
        escribir_filas(ruta, existentes + nuevas, cols_c or COLS_CXC)
    return {"importados": len(nuevas), "clientes_nuevos": len(nuevos_ids), "fecha": por_defecto.isoformat()}


# ------------------------------------------------------------------------------------------------ análisis
def asignar_cuadrante(afinidad, contribucion_pct, corte_x, corte_y):
    """Clave del cuadrante (alto_alto, bajo_alto, alto_bajo, bajo_bajo). Un valor justo en el corte cuenta en el lado alto."""
    return ("alto" if afinidad >= corte_x else "bajo") + "_" + ("alto" if contribucion_pct >= corte_y else "bajo")


def leer_ventas(proyecto, desde=None, hasta=None):
    lineas = []
    for f in leer_filas(carpeta_datos(proyecto) / "ventas.csv")[1]:
        fecha = fecha_de(f.get("fecha"))
        cant, precio = num_csv(f.get("cantidad")), num_csv(f.get("precio_unitario"))
        if fecha is None or cant is None or precio is None:
            continue
        if (desde and fecha < desde) or (hasta and fecha > hasta):
            continue
        costo = num_csv(f.get("costo_unitario"))
        lineas.append({"fecha": fecha, "cliente_id": f.get("cliente_id", ""), "producto": f.get("producto", ""),
                       "cantidad": cant, "precio": precio, "costo": costo})
    return lineas


def analizar(proyecto, desde=None, hasta=None, costo_hora=None, corte_afinidad=None, corte_contribucion=None, cfg=None):
    """Análisis de rentabilidad con ids (los nombres se aplican al presentar). desde/hasta son date o None; costo_hora en $;
    corte_afinidad en puntos de afinidad; corte_contribucion en % (22.0 = 22 %). Devuelve un dict con periodo, totales,
    productos, clientes, cuadrantes, metricas, cortes y advertencias."""
    advertencias = []
    lineas = leer_ventas(proyecto, desde, hasta)
    if costo_hora is None:
        costo_hora = num_csv(((cfg or {}).get("rentabilidad") or {}).get("costo_hora"))
    if not costo_hora:
        costo_hora = 0.0
        advertencias.append("El costo por hora está en 0 (usa --costo-hora o `rentabilidad.costo_hora` en proyecto.yaml): "
                            "la contribución es igual al margen.")
    resultado = {"periodo": None, "totales": {}, "productos": [], "clientes": [], "cuadrantes": [], "metricas": {},
                 "cortes": {}, "costo_hora": costo_hora, "advertencias": advertencias, "nota": NOTA_MAPA}
    if not lineas:
        advertencias.append("No hay líneas de venta en el período.")
        return resultado
    d0 = desde or min(l["fecha"] for l in lineas)
    d1 = hasta or max(l["fecha"] for l in lineas)
    dias = (d1 - d0).days + 1
    resultado["periodo"] = {"desde": d0.isoformat(), "hasta": d1.isoformat(), "dias": dias}

    sin_costo = sum(1 for l in lineas if l["costo"] is None)
    if sin_costo:
        advertencias.append(f"{sin_costo} línea(s) de venta con costo en blanco: se trataron como costo 0.")
    prods, cli = {}, {}
    for l in lineas:
        v = l["cantidad"] * l["precio"]
        c = l["cantidad"] * (l["costo"] or 0.0)
        for tabla, k in ((prods, l["producto"]), (cli, l["cliente_id"])):
            t = tabla.setdefault(k, {"ventas": 0.0, "costo": 0.0, "lineas": 0})
            t["ventas"] += v
            t["costo"] += c
            t["lineas"] += 1
    ventas_total = sum(p["ventas"] for p in prods.values())
    costo_total = sum(p["costo"] for p in prods.values())
    margen_total = ventas_total - costo_total

    productos = []
    for nombre, p in prods.items():
        m = p["ventas"] - p["costo"]
        productos.append({"producto": nombre, "lineas": p["lineas"], "ventas": p["ventas"], "costo": p["costo"], "margen": m,
                          "margen_pct": m / p["ventas"] if p["ventas"] else None,
                          "part_ventas": p["ventas"] / ventas_total if ventas_total else None,
                          "part_margen": m / margen_total if margen_total else None})
    productos.sort(key=lambda p: (-p["margen"], p["producto"]))
    for p in productos:
        if p["margen"] < 0:
            advertencias.append(f"El producto «{p['producto']}» tiene margen negativo ({peso(p['margen'])}).")

    ficha = {f["cliente_id"]: f for f in leer_filas(carpeta_datos(proyecto) / "clientes.csv")[1]}
    cxc = {}
    for f in leer_filas(carpeta_datos(proyecto) / "cxc.csv")[1]:
        fd, s = fecha_de(f.get("fecha")), num_csv(f.get("saldo"))
        if fd is None or s is None or fd > d1:
            continue
        if f["cliente_id"] not in cxc or fd >= cxc[f["cliente_id"]][0]:
            cxc[f["cliente_id"]] = (fd, s)
    hay_cxc = bool(cxc)

    clientes = []
    for cid, t in cli.items():
        fi = ficha.get(cid, {})
        horas = num_csv(fi.get("horas_periodo")) or 0.0
        afin = num_csv(fi.get("afinidad"))
        margen = t["ventas"] - t["costo"]
        servir = horas * costo_hora
        contrib = margen - servir
        saldo = cxc[cid][1] if cid in cxc else None
        clientes.append({"cliente_id": cid, "lineas": t["lineas"], "ventas": t["ventas"], "margen": margen,
                         "margen_pct": margen / t["ventas"] if t["ventas"] else None,
                         "cxc": saldo,
                         "dias_cobro": (saldo / t["ventas"] * dias) if (hay_cxc and saldo is not None and t["ventas"]) else None,
                         "horas": horas, "costo_servir": servir, "contribucion": contrib,
                         "contribucion_pct": contrib / t["ventas"] if t["ventas"] else None,
                         "afinidad": afin, "segmento": fi.get("segmento", ""), "cuadrante": None})
    clientes.sort(key=lambda c: (-c["margen"], c["cliente_id"]))

    en_mapa = [c for c in clientes if c["afinidad"] is not None and c["ventas"] and c["contribucion_pct"] is not None]
    fuera = [c for c in clientes if c["afinidad"] is None]
    if fuera:
        mf = sum(c["margen"] for c in fuera)
        advertencias.append(f"{len(fuera)} cliente(s) con ventas no tienen afinidad ({pct(mf / margen_total if margen_total else None)} "
                            "del margen): quedan fuera del mapa.")
    if len(en_mapa) < MIN_CLIENTES_MAPA:
        advertencias.append(f"Con {len(en_mapa)} clientes en el mapa el corte en la mediana es inestable: tómalo como orientación.")

    cortes = {"afinidad": None, "contribucion_pct": None, "afinidad_manual": corte_afinidad is not None,
              "contribucion_manual": corte_contribucion is not None}
    if en_mapa:
        cx = corte_afinidad if corte_afinidad is not None else statistics.median(c["afinidad"] for c in en_mapa)
        cy = (corte_contribucion if corte_contribucion is not None
              else statistics.median(c["contribucion_pct"] * 100 for c in en_mapa))
        cortes["afinidad"], cortes["contribucion_pct"] = float(cx), float(cy)
        for c in en_mapa:
            c["cuadrante"] = asignar_cuadrante(c["afinidad"], c["contribucion_pct"] * 100, cx, cy)

    cuadrantes = []
    for k in ORDEN_CUADRANTES:
        miembros = [c for c in en_mapa if c["cuadrante"] == k]
        m = sum(c["margen"] for c in miembros)
        cuadrantes.append({"clave": k, "nombre": CUADRANTES[k], "clientes": len(miembros),
                           "pct_clientes": len(miembros) / len(en_mapa) if en_mapa else None,
                           "margen": m, "pct_margen": m / margen_total if margen_total else None})
    riesgo = next(q for q in cuadrantes if q["clave"] == "bajo_alto")
    n_top = int(math.ceil(len(clientes) * PROPORCION_CONCENTRACION))
    top_margen = sum(c["margen"] for c in clientes[:n_top])
    resultado.update({
        "totales": {"lineas": len(lineas), "ventas": ventas_total, "costo": costo_total, "margen": margen_total,
                    "margen_pct": margen_total / ventas_total if ventas_total else None,
                    "costo_servir": sum(c["costo_servir"] for c in clientes),
                    "contribucion": sum(c["contribucion"] for c in clientes),
                    "clientes": len(clientes), "clientes_mapa": len(en_mapa), "productos": len(productos),
                    "lineas_sin_costo": sin_costo, "hay_cxc": hay_cxc},
        "productos": productos, "clientes": clientes, "cuadrantes": cuadrantes, "cortes": cortes,
        "metricas": {"margen_en_riesgo": riesgo["margen"], "margen_en_riesgo_pct": riesgo["pct_margen"],
                     "concentracion_clientes_top": n_top,
                     "concentracion_pct": top_margen / margen_total if margen_total else None,
                     "margen_baja_afinidad_pct": (sum(q["margen"] for q in cuadrantes if q["clave"].startswith("bajo")) / margen_total
                                                  if (margen_total and en_mapa) else None)}})
    return resultado


# ------------------------------------------------------------------------------------------------ presentación
def tabla_md(cabeza, filas, derecha=()):
    def esc(x):
        return str(x).replace("|", "/")
    salida = ["| " + " | ".join(cabeza) + " |",
              "|" + "|".join("---:" if i in derecha else "---" for i in range(len(cabeza))) + "|"]
    salida += ["| " + " | ".join(esc(x) for x in f) + " |" for f in filas]
    return "\n".join(salida)


def etiquetas(res, mapa, con_nombres):
    """Función id → texto a mostrar: el nombre (si se pidió y está en el mapa) o el id tal cual."""
    nombres = {}
    if con_nombres and mapa is not None:
        nombres = {f["cliente_id"]: f["nombre"] for f in mapa.filas if f.get("nombre")}
    return lambda cid: nombres.get(cid, cid)


def filas_productos(res):
    return [[p["producto"], peso(p["ventas"]), peso(p["costo"]), peso(p["margen"]), pct(p["margen_pct"]),
             pct(p["part_ventas"]), pct(p["part_margen"])] for p in res["productos"]]


CAB_PRODUCTOS = ["Producto", "Ventas", "Costo", "Margen", "Margen %", "% ventas", "% margen"]


def filas_cuadrantes(res):
    return [[q["nombre"], q["clientes"], pct(q["pct_clientes"]), peso(q["margen"]), pct(q["pct_margen"])] for q in res["cuadrantes"]]


CAB_CUADRANTES = ["Cuadrante", "Clientes", "% clientes", "Margen", "% del margen"]


def filas_clientes(res, etq, limite=None):
    nombre_q = lambda k: CUADRANTES.get(k, "—") if k else "—"
    filas = []
    for c in res["clientes"][:limite]:
        filas.append([etq(c["cliente_id"]), peso(c["ventas"]), peso(c["margen"]), pct(c["margen_pct"]), peso(c["costo_servir"]),
                      peso(c["contribucion"]), pct(c["contribucion_pct"]),
                      "—" if c["afinidad"] is None else texto_num(c["afinidad"]), peso(c["cxc"]),
                      "—" if c["dias_cobro"] is None else miles(c["dias_cobro"], 0), nombre_q(c["cuadrante"])])
    return filas


CAB_CLIENTES = ["Cliente", "Ventas", "Margen", "Margen %", "Costo de servir", "Contribución", "Contribución %",
                "Afinidad", "CxC", "Días de cobro", "Cuadrante"]


def lineas_metricas(res):
    m, t = res["metricas"], res["totales"]
    top = m["concentracion_clientes_top"]
    return [f"- Margen en riesgo (cuadrante «{Q_ASEGURAR}»): {peso(m['margen_en_riesgo'])} ({pct(m['margen_en_riesgo_pct'])} del margen).",
            f"- Concentración: los {top} cliente(s) con más margen (el 20 % de {t['clientes']}) aportan {pct(m['concentracion_pct'])} del margen."]


def resumen_consola(res, etq):
    p = res["periodo"]
    if not p:
        return "# Rentabilidad\n\n" + "\n".join(f"- {a}" for a in res["advertencias"])
    t = res["totales"]
    sal = [f"# Rentabilidad: {p['desde']} a {p['hasta']} ({p['dias']} días)", "",
           f"- Ventas {peso(t['ventas'])} · costo {peso(t['costo'])} · margen {peso(t['margen'])} ({pct(t['margen_pct'])})",
           f"- Costo de servir {peso(t['costo_servir'])} (costo por hora {peso(res['costo_hora'])}) · contribución {peso(t['contribucion'])}",
           f"- {t['lineas']} líneas · {t['clientes']} clientes ({t['clientes_mapa']} en el mapa) · {t['productos']} productos",
           "", "## Por producto", "", tabla_md(CAB_PRODUCTOS, filas_productos(res), range(1, 7)), ""]
    if t["clientes_mapa"]:
        c = res["cortes"]
        sal += ["## Cuadrantes", "",
                f"Cortes: afinidad {texto_num(round(c['afinidad'], 2))}{' (manual)' if c['afinidad_manual'] else ' (mediana)'}, "
                f"contribución {miles(c['contribucion_pct'], 1)} %{' (manual)' if c['contribucion_manual'] else ' (mediana)'}.", "",
                tabla_md(CAB_CUADRANTES, filas_cuadrantes(res), range(1, 5)), ""] + lineas_metricas(res) + [""]
    sal += ["## Clientes con más margen (10)", "", tabla_md(CAB_CLIENTES, filas_clientes(res, etq, 10), range(1, 10)), ""]
    if res["advertencias"]:
        sal += ["## Advertencias", ""] + [f"- {a}" for a in res["advertencias"]] + [""]
    sal.append(NOTA_MAPA)
    return "\n".join(sal)


def clave_yaml(texto):
    s = str(texto)
    return s if re.match(r"^[\w][\w .\-]*$", s) and not re.match(r"^[\d.\-]+$", s) else json.dumps(s, ensure_ascii=False)


def bloque_cuadrantes(res, etq):
    c = res["cortes"]
    n = {k: CUADRANTES[k] for k in ORDEN_CUADRANTES}
    lineas = ["```grafico", "tipo: cuadrantes", "titulo: Clientes según afinidad y contribución", "eje_x: Afinidad (1 a 10)",
              "eje_y: Contribución %", "tamano: el margen del cliente", f"corte_x: {texto_num(round(c['afinidad'], 2))}", f"corte_y: {c['contribucion_pct']:.1f}",
              "nombres: {" + ", ".join(f"{k}: {v}" for k, v in n.items()) + "}", "datos:"]
    for cl in res["clientes"]:
        if cl["cuadrante"]:
            lineas.append(f"  {clave_yaml(etq(cl['cliente_id']))}: [{texto_num(cl['afinidad'])}, "
                          f"{cl['contribucion_pct'] * 100:.1f}, {texto_num(round(cl['margen']))}]")
    lineas.append("```")
    return "\n".join(lineas)


def markdown_pagina(res, etq):
    """Markdown con el formato de explicar.py."""
    p, t = res["periodo"], res["totales"]
    m = res["metricas"]
    if t["clientes_mapa"]:
        frase = f"El {miles(m['margen_baja_afinidad_pct'] * 100, 0)} % del margen viene de clientes de baja afinidad."
    else:
        frase = "Sin afinidad registrada no hay mapa de clientes: falta completar clientes.csv."
    sal = ["---", "titulo: Rentabilidad por cliente y producto", f"subtitulo: Período {p['desde']} a {p['hasta']}", "---", "",
           f"> {frase}", "", "```cifras",
           f"Ventas: {peso(t['ventas'])} | {t['lineas']} líneas",
           f"Margen: {peso(t['margen'])} | {pct(t['margen_pct'])} de las ventas",
           f"Contribución: {peso(t['contribucion'])} | costo de servir {peso(t['costo_servir'])}",
           f"Clientes: {t['clientes']} | {t['clientes_mapa']} en el mapa",
           f"Margen en riesgo: {peso(m['margen_en_riesgo'])} | {pct(m['margen_en_riesgo_pct'])} del margen",
           f"Concentración: {pct(m['concentracion_pct'])} | del margen en el 20 % de clientes",
           "```", "", "## Margen por producto", "", "```grafico", "tipo: barras", "titulo: Margen por producto", 'unidad: "$"',
           "datos: {" + ", ".join(f"{json.dumps(pr['producto'], ensure_ascii=False)}: {texto_num(round(pr['margen']))}"
                                  for pr in res["productos"]) + "}", "```", "", tabla_md(CAB_PRODUCTOS, filas_productos(res), range(1, 7)), ""]
    if t["clientes_mapa"]:
        sal += ["## Mapa de clientes", "", bloque_cuadrantes(res, etq), "", tabla_md(CAB_CUADRANTES, filas_cuadrantes(res), range(1, 5)),
                ""] + lineas_metricas(res) + [""]
    sal += ["## Clientes", "", tabla_md(CAB_CLIENTES, filas_clientes(res, etq), range(1, 10)), ""]
    if res["advertencias"]:
        sal += ["## Advertencias", ""] + [f"- {a}" for a in res["advertencias"]] + [""]
    sal += [NOTA_MAPA, ""]
    return "\n".join(sal)


def comando_analizar(proyecto, a, cfg, mapa, hoy):
    desde = fecha_de(a.desde) if a.desde else None
    hasta = fecha_de(a.hasta) if a.hasta else None
    if (a.desde and desde is None) or (a.hasta and hasta is None):
        sys.exit("Fechas no válidas: usa AAAA-MM-DD.")
    res = analizar(proyecto, desde, hasta, a.costo_hora, a.corte_afinidad, a.corte_contribucion, cfg)
    con_nombres = a.con_nombres
    avisos = []
    if con_nombres and not mapa.existe:
        avisos.append("No hay mapa local de clientes (finanzas/_local/clientes-mapa.csv): se usan los identificadores.")
        con_nombres = False
    etq = etiquetas(res, mapa, con_nombres)
    if a.json:
        salida = dict(res)
        salida["clientes"] = [dict(c, cliente=etq(c["cliente_id"])) for c in res["clientes"]] if con_nombres else res["clientes"]
        print(json.dumps(salida, ensure_ascii=False, indent=2, default=str))
        return 0
    print(resumen_consola(res, etq))
    for av in avisos:
        print("\n" + av)
    if not res["periodo"]:
        return 0
    base = carpeta_datos(proyecto)
    destino = base / ("_local" if con_nombres else "analisis")
    destino.mkdir(parents=True, exist_ok=True)
    md_ruta = destino / f"rentabilidad-{hoy.isoformat()}.md"
    md = markdown_pagina(res, etq)
    md_ruta.write_text(md, encoding="utf-8")
    print(f"\nMarkdown: {md_ruta.as_posix()}")
    if con_nombres:
        print("Esta versión lleva nombres de clientes y queda en _local/: no se sube ni se comparte.")
    try:
        import explicar
    except Exception as e:  # pragma: no cover
        print(f"No se generó la página: no se pudo cargar explicar.py ({e}).")
        return 0
    if "cuadrantes" not in explicar.GRAFICOS:
        print("No se generó la página: explicar.py aún no admite el gráfico de tipo cuadrantes (queda el Markdown).")
        return 0
    try:
        html, _titulo = explicar.generar(md, md_ruta.parent, cfg, Path(proyecto), hoy, False)
    except explicar.Problema as e:
        print(f"No se generó la página: {e}")
        return 0
    html_ruta = md_ruta.with_suffix(".html")
    html_ruta.write_text(html, encoding="utf-8")
    print(f"Página: {html_ruta.as_posix()}")
    if a.abrir:
        webbrowser.open(html_ruta.resolve().as_uri())
    return 0


# ------------------------------------------------------------------------------------------------ estado y consultas
def estado(proyecto, mapa):
    base = carpeta_datos(proyecto)
    lineas = leer_ventas(proyecto)
    fichas = leer_filas(base / "clientes.csv")[1]
    cxc = leer_filas(base / "cxc.csv")[1]
    print(f"# Rentabilidad: {Path(proyecto).name}", "")
    if not lineas:
        print("- Sin líneas de venta todavía.")
        print("\nSiguiente paso: importar las ventas con `--importar-ventas <archivo .csv o .xlsx>` "
              "(los clientes quedan como identificadores).")
        return 0
    clientes = {l["cliente_id"] for l in lineas}
    con_afin = sum(1 for f in fichas if num_csv(f.get("afinidad")) is not None and f.get("cliente_id") in clientes)
    print(f"- Ventas: {len(lineas)} líneas, del {min(l['fecha'] for l in lineas)} al {max(l['fecha'] for l in lineas)}.")
    print(f"- Clientes con ventas: {len(clientes)} · productos: {len({l['producto'] for l in lineas})}.")
    print(f"- Cuentas por cobrar: {'sí (' + str(len(cxc)) + ' saldos)' if cxc else 'no'}.")
    print(f"- Afinidad: {con_afin} de {len(clientes)} clientes.")
    print(f"- Mapa local de nombres: {'sí' if mapa.existe else 'no (los nombres no están en este computador)'}.")
    if not cxc:
        paso = "importar las cuentas por cobrar con `--importar-cxc <archivo>` (opcional: da los días de cobro)"
    elif con_afin < len(clientes):
        paso = "completar la afinidad (1 a 10) y las horas de cada cliente en finanzas/clientes.csv"
    else:
        paso = "correr `--analizar` (con `--costo-hora N` si aún no está `rentabilidad.costo_hora` en proyecto.yaml)"
    if cxc and con_afin == 0:
        paso = "completar la afinidad (1 a 10) y las horas de cada cliente en finanzas/clientes.csv"
    print(f"\nSiguiente paso: {paso}.")
    return 0


def quien(proyecto, consulta, mapa):
    if not mapa.existe or not mapa.filas:
        print("No hay mapa local de clientes en este computador (finanzas/_local/clientes-mapa.csv).")
        return 0
    q = clave_nombre(consulta)
    q_id = consulta.strip().lower()
    hallados = [f for f in mapa.filas if f["cliente_id"].lower() == q_id or q in clave_nombre(f.get("nombre", ""))
                or (q and q in clave_nombre(f.get("identificador", "")))]
    if not hallados:
        print(f"Sin coincidencias para «{consulta}» en el mapa local.")
        return 0
    print(tabla_md(["Id", "Nombre", "Identificador", "Creado"],
                   [[f["cliente_id"], f.get("nombre", ""), f.get("identificador", ""), f.get("creado", "")] for f in hallados]))
    print("\nEsta información es local: no la pegues en documentos ni en los datos del proyecto.")
    return 0


# ------------------------------------------------------------------------------------------------ principal
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("proyecto", help="carpeta del proyecto (con proyecto.yaml)")
    ap.add_argument("--importar-ventas", metavar="ARCHIVO")
    ap.add_argument("--mapa-columnas", metavar="campo=Encabezado,...")
    ap.add_argument("--importar-cxc", metavar="ARCHIVO")
    ap.add_argument("--fecha", help="fecha de los saldos de --importar-cxc (AAAA-MM-DD)")
    ap.add_argument("--normalizar", action="store_true")
    ap.add_argument("--quien", metavar="ID_O_NOMBRE")
    ap.add_argument("--analizar", action="store_true")
    ap.add_argument("--desde")
    ap.add_argument("--hasta")
    ap.add_argument("--costo-hora", type=float)
    ap.add_argument("--corte-afinidad", type=float)
    ap.add_argument("--corte-contribucion", type=float, help="en %% (22.0 = 22 %%)")
    ap.add_argument("--con-nombres", action="store_true", help="usa nombres (solo con mapa local); los archivos quedan en finanzas/_local/")
    ap.add_argument("--abrir", action="store_true")
    ap.add_argument("--hoy", help="fecha AAAA-MM-DD (nombre de los archivos y fecha por defecto de los saldos)")
    ap.add_argument("--json", action="store_true", help="con --analizar: solo el JSON, sin escribir archivos")
    a = ap.parse_args()

    proyecto = Path(a.proyecto)
    if not (proyecto / "proyecto.yaml").exists():
        sys.exit(f"{a.proyecto} no es un proyecto (falta proyecto.yaml)")
    hoy = date.today()
    if a.hoy:
        hoy = fecha_de(a.hoy)
        if hoy is None:
            sys.exit("--hoy: usa AAAA-MM-DD")
    mapa = Mapa(proyecto)
    convertidos = normalizar(proyecto, hoy, mapa)
    informar_normalizacion(convertidos, sys.stderr if a.json else None)
    try:
        import _config
        cfg = _config.cargar(proyecto)
    except Exception:
        cfg = {}

    if a.importar_ventas:
        r = importar_ventas(proyecto, a.importar_ventas, parsear_mapa_columnas(a.mapa_columnas), hoy)
        if "error" in r:
            sys.exit(r["error"])
        print(f"Ventas importadas: {r['agregadas']} líneas agregadas, {r['omitidas']} ya estaban, "
              f"{r['sin_datos']} sin datos completos (omitidas), {r['clientes_nuevos']} clientes nuevos.")
        return 0
    if a.importar_cxc:
        r = importar_cxc(proyecto, a.importar_cxc, a.fecha, parsear_mapa_columnas(a.mapa_columnas), hoy)
        if "error" in r:
            sys.exit(r["error"])
        print(f"Cuentas por cobrar al {r['fecha']}: {r['importados']} saldos, {r['clientes_nuevos']} clientes nuevos.")
        return 0
    if a.normalizar:
        if not convertidos:
            hay = any(leer_filas(carpeta_datos(proyecto) / n)[1] for n in ARCHIVOS_DATOS)
            print("Identificadores: los datos del proyecto ya usan solo identificadores." if hay
                  else "Identificadores: no hay datos que revisar.")
        return 0
    if a.quien:
        return quien(proyecto, a.quien, mapa)
    if a.analizar:
        return comando_analizar(proyecto, a, cfg, Mapa(proyecto), hoy)
    return estado(proyecto, mapa)


if __name__ == "__main__":
    import _consola
    _consola.preparar()
    sys.exit(main())
