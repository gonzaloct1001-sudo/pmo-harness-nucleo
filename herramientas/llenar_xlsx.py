#!/usr/bin/env python3
"""Llena valores en una planilla Excel oficial (de una entidad o de terceros) sin dañarla.

Uso:
    python herramientas/llenar_xlsx.py <planilla.xlsx> --valores <valores.yaml|valores.csv> [--salida <nueva.xlsx>]
    python herramientas/llenar_xlsx.py <planilla.xlsx> --celda "Hoja!B3=texto" --celda "Hoja!C5=1200" [--salida ...]
    python herramientas/llenar_xlsx.py <planilla.xlsx> --valores ... --vista-previa      # muestra qué cambiaría

Por qué existe: abrir y guardar una planilla con openpyxl (la librería habitual) borra las listas desplegables
modernas, las formas y cuadros de texto y otras extensiones de Excel. Las planillas de CORFO, del GORE o de otras
entidades suelen tenerlas, y una planilla dañada puede ser rechazada. Este script escribe SOLO el valor de cada celda
indicada, directo en el XML; todo lo demás del archivo queda idéntico, byte a byte.

- Valores: YAML con `celdas: [{hoja: "...", celda: B3, valor: ...}]` (o un mapa {"Hoja!B3": valor}), o CSV con columnas
  hoja,celda,valor. Números, textos, fechas AAAA-MM-DD y porcentajes ("55%" se escribe 0,55).
- Nunca escribe sobre una celda con fórmula, en una hoja protegida ni en una celda oculta dentro de un rango combinado.
- Pide a Excel recalcular al abrir. Verifica después que las listas desplegables, formas, tablas, celdas combinadas y
  formatos condicionales sigan intactos, y que cada valor haya quedado escrito.
- Nunca reemplaza el original: por defecto crea <nombre>_completado.xlsx junto a él.
"""
import argparse
import csv
import re
import sys
import zipfile
from datetime import date, datetime
from pathlib import Path
from xml.sax.saxutils import escape

import _nucleo

REF = re.compile(r"^([A-Z]{1,3})([1-9]\d*)$")
CONSERVAR = ["<x14:dataValidation ", "<dataValidation ", "<drawing ", "<xdr:sp", "<xdr:pic", "<tablePart ", "<mergeCell ",
             "<conditionalFormatting", "<x14:conditionalFormatting", "<hyperlink ", "<legacyDrawing ", "<sheetProtection"]


class Rechazo(Exception):
    pass


def col_num(letras):
    n = 0
    for ch in letras:
        n = n * 26 + ord(ch) - 64
    return n


def hojas(z):
    """{nombre de hoja: ruta de su XML dentro del zip}."""
    wb = z.read("xl/workbook.xml").decode("utf-8")
    rels = z.read("xl/_rels/workbook.xml.rels").decode("utf-8")
    destino = {m.group(1): m.group(2) for m in re.finditer(r'<Relationship[^>]*?Id="([^"]+)"[^>]*?Target="([^"]+)"', rels)}
    destino.update({m.group(2): m.group(1) for m in re.finditer(r'<Relationship[^>]*?Target="([^"]+)"[^>]*?Id="([^"]+)"', rels)})
    salida = {}
    for m in re.finditer(r"<sheet\b([^>]*)/>", wb):
        attrs = m.group(1)
        nombre = re.search(r'name="([^"]*)"', attrs).group(1)
        rid = re.search(r'r:id="([^"]*)"', attrs).group(1)
        t = destino[rid].lstrip("/")
        salida[nombre.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"').replace("&apos;", "'")] = \
            t if t.startswith("xl/") else "xl/" + t
    return salida


def convertir(valor, fecha1904=False):
    """(tipo, texto XML) para un valor: n (número), b (booleano) o inlineStr (texto)."""
    if isinstance(valor, bool):
        return "b", "1" if valor else "0"
    if isinstance(valor, (int, float)):
        return "n", repr(float(valor)) if isinstance(valor, float) else str(valor)
    if isinstance(valor, (date, datetime)):
        base = date(1904, 1, 1) if fecha1904 else date(1899, 12, 30)
        d = valor.date() if isinstance(valor, datetime) else valor
        return "n", str((d - base).days)
    texto = "" if valor is None else str(valor)
    if texto.startswith("="):
        raise Rechazo("el valor empieza con «=»: este script escribe valores, no fórmulas")
    if re.fullmatch(r"-?\d+(\.\d+)?", texto):
        return "n", texto
    if re.fullmatch(r"-?\d+(\.\d+)?\s*%", texto):
        return "n", repr(float(texto.rstrip("% ")) / 100)
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", texto):
        return convertir(datetime.strptime(texto, "%Y-%m-%d").date(), fecha1904)
    return "inlineStr", texto


def nueva_celda(ref, estilo, valor, fecha1904):
    tipo, contenido = convertir(valor, fecha1904)
    s = f' s="{estilo}"' if estilo else ""
    if tipo == "inlineStr":
        if contenido == "":
            return f'<c r="{ref}"{s}/>'
        return f'<c r="{ref}"{s} t="inlineStr"><is><t xml:space="preserve">{escape(contenido)}</t></is></c>'
    if tipo == "b":
        return f'<c r="{ref}"{s} t="b"><v>{contenido}</v></c>'
    return f'<c r="{ref}"{s}><v>{contenido}</v></c>'


def en_combinada_oculta(xml, ref):
    m = REF.match(ref)
    c, f = col_num(m.group(1)), int(m.group(2))
    for r in re.finditer(r'<mergeCell ref="([A-Z]+)(\d+):([A-Z]+)(\d+)"', xml):
        c1, f1, c2, f2 = col_num(r.group(1)), int(r.group(2)), col_num(r.group(3)), int(r.group(4))
        if c1 <= c <= c2 and f1 <= f <= f2 and (c, f) != (c1, f1):
            return f"{r.group(1)}{r.group(2)}"
    return None


def escribir(xml, ref, valor, fecha1904=False):
    """XML de la hoja con el valor escrito en `ref`. Lanza Rechazo si no corresponde escribir ahí."""
    m = REF.match(ref)
    if not m:
        raise Rechazo(f"«{ref}» no es una celda válida (ej.: B3)")
    if "<sheetProtection" in xml:
        raise Rechazo("la hoja está protegida: sus celdas se calculan o no se deben modificar")
    ancla = en_combinada_oculta(xml, ref)
    if ancla:
        raise Rechazo(f"está dentro de un rango combinado: escribe en {ancla}, su primera celda")
    fila = int(m.group(2))
    celda = re.search(rf'<c r="{ref}"(?P<attrs>[^>]*?)(?:/>|>(?P<inner>.*?)</c>)', xml, re.S)
    if celda:
        if "<f" in (celda.group("inner") or ""):
            raise Rechazo("tiene una fórmula: no se sobrescribe (cambia las celdas de las que depende)")
        est = re.search(r'\bs="(\d+)"', celda.group("attrs"))
        return xml[:celda.start()] + nueva_celda(ref, est.group(1) if est else "", valor, fecha1904) + xml[celda.end():]
    nueva = nueva_celda(ref, "", valor, fecha1904)
    row = re.search(rf'<row r="{fila}"(?P<attrs>[^>]*?)(?:/>|>(?P<inner>.*?)</row>)', xml, re.S)
    if row:
        inner = row.group("inner") or ""
        col = col_num(m.group(1))
        pos = len(inner)
        for c in re.finditer(r'<c r="([A-Z]+)\d+"', inner):
            if col_num(c.group(1)) > col:
                pos = c.start()
                break
        inner = inner[:pos] + nueva + inner[pos:]
        attrs = row.group("attrs")
        return xml[:row.start()] + f'<row r="{fila}"{attrs}>{inner}</row>' + xml[row.end():]
    nueva_fila = f'<row r="{fila}">{nueva}</row>'
    if re.search(r"<sheetData\s*/>", xml):
        return re.sub(r"<sheetData\s*/>", f"<sheetData>{nueva_fila}</sheetData>", xml, count=1)
    for r in re.finditer(r'<row r="(\d+)"', xml):
        if int(r.group(1)) > fila:
            return xml[:r.start()] + nueva_fila + xml[r.start():]
    return xml.replace("</sheetData>", nueva_fila + "</sheetData>", 1)


def recalcular_al_abrir(wb):
    if re.search(r"<calcPr\b", wb):
        if "fullCalcOnLoad=" in wb:
            return re.sub(r'fullCalcOnLoad="[^"]*"', 'fullCalcOnLoad="1"', wb, count=1)
        return re.sub(r"<calcPr\b", '<calcPr fullCalcOnLoad="1"', wb, count=1)
    for despues in ("</definedNames>", "</externalReferences>", "</sheets>"):
        if despues in wb:
            return wb.replace(despues, despues + '<calcPr fullCalcOnLoad="1"/>', 1)
    return wb


def firma(z):
    """Conteo de los elementos que deben conservarse, por parte del archivo."""
    out = {}
    for n in z.namelist():
        if n.endswith(".xml") or n.endswith(".rels"):
            x = z.read(n).decode("utf-8", "ignore")
            out[n] = tuple(len(re.findall(re.escape(e.rstrip()) + r"(?=[\s>/])", x)) for e in CONSERVAR)  # «<xdr:sp» no cuenta «<xdr:spPr»
    return out


def leer_valores(a):
    pares = []
    for c in a.celda or []:
        if "!" not in c or "=" not in c:
            sys.exit(f"--celda «{c}»: usa el formato \"Hoja!B3=valor\"")
        destino, valor = c.split("=", 1)
        hoja, ref = destino.rsplit("!", 1)
        pares.append((hoja.strip().strip("'"), ref.strip().upper(), valor))
    if a.valores:
        ruta = Path(a.valores)
        if ruta.suffix.lower() == ".csv":
            with open(ruta, encoding="utf-8-sig", newline="") as f:
                pares += [(r["hoja"], r["celda"].strip().upper(), r["valor"]) for r in csv.DictReader(f)]
        else:
            import yaml
            datos = yaml.safe_load(ruta.read_text(encoding="utf-8")) or {}
            if isinstance(datos, dict) and "celdas" in datos:
                pares += [(str(x["hoja"]), str(x["celda"]).strip().upper(), x.get("valor")) for x in datos["celdas"]]
            elif isinstance(datos, dict):
                for k, v in datos.items():
                    hoja, ref = str(k).rsplit("!", 1)
                    pares.append((hoja.strip().strip("'"), ref.strip().upper(), v))
    return pares


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("planilla")
    ap.add_argument("--valores", help="YAML o CSV con hoja, celda y valor")
    ap.add_argument("--celda", action="append", help='"Hoja!B3=valor" (se puede repetir)')
    ap.add_argument("--salida", help="archivo nuevo (por defecto <nombre>_completado.xlsx)")
    ap.add_argument("--vista-previa", action="store_true", help="mostrar qué cambiaría, sin escribir nada")
    a = ap.parse_args()

    origen = Path(a.planilla)
    if origen.suffix.lower() not in (".xlsx", ".xlsm"):
        sys.exit("Solo planillas .xlsx o .xlsm (un .xls antiguo hay que guardarlo antes como .xlsx).")
    pares = leer_valores(a)
    if not pares:
        sys.exit("No hay valores: usa --valores <archivo> o --celda \"Hoja!B3=valor\".")
    salida = Path(a.salida) if a.salida else origen.with_name(origen.stem + "_completado" + origen.suffix)
    if salida.resolve() == origen.resolve():
        sys.exit("La salida no puede ser el mismo archivo original: el original se conserva siempre.")

    with zipfile.ZipFile(_nucleo.ruta_larga(origen)) as z:
        infos = z.infolist()
        datos = {i.filename: z.read(i.filename) for i in infos}
        mapa = hojas(z)
        antes = firma(z)
    fecha1904 = 'date1904="1"' in datos["xl/workbook.xml"].decode("utf-8") or "date1904=\"true\"" in datos["xl/workbook.xml"].decode("utf-8")

    xmls, escritas, rechazos = {}, [], []
    for i, (hoja, ref, valor) in enumerate(pares):
        parte = mapa.get(hoja)
        if parte is None:  # los nombres de hoja a veces traen espacios al final ("3. Matriz de Resultados ")
            parecidas = [n for n in mapa if n.strip().lower() == hoja.strip().lower()]
            if len(parecidas) == 1:
                hoja = parecidas[0]
                pares[i] = (hoja, ref, valor)
                parte = mapa[hoja]
        if parte is None:
            rechazos.append(f"{hoja}!{ref}: no existe la hoja «{hoja}» (hojas: {', '.join(mapa)})")
            continue
        xml = xmls.get(parte, datos[parte].decode("utf-8"))
        try:
            actual = re.search(rf'<c r="{ref}"[^>]*?(?:/>|>(.*?)</c>)', xml, re.S)
            xmls[parte] = escribir(xml, ref, valor, fecha1904)
            previo = re.sub(r"<[^>]+>", "", actual.group(1) or "") if actual else ""
            escritas.append(f"{hoja}!{ref}: {previo[:40] or '(vacía)'} → {str(valor)[:60]}")
        except Rechazo as e:
            rechazos.append(f"{hoja}!{ref}: no se escribió: {e}")

    print(f"# Llenado de {origen.name}\n")
    print(f"- Celdas a escribir: {len(escritas)} · rechazadas: {len(rechazos)}")
    for x in escritas[:40]:
        print(f"  - {x}")
    if len(escritas) > 40:
        print(f"  - … y {len(escritas) - 40} más")
    for x in rechazos:
        print(f"  - ✗ {x}")
    if a.vista_previa:
        print("\nVista previa: no se escribió nada.")
        return 1 if rechazos else 0
    if not escritas:
        print("\nNada que escribir.")
        return 1

    datos["xl/workbook.xml"] = recalcular_al_abrir(datos["xl/workbook.xml"].decode("utf-8")).encode("utf-8")
    for parte, xml in xmls.items():
        datos[parte] = xml.encode("utf-8")
    destino = _nucleo.ruta_larga(salida)
    destino.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destino, "w") as zout:
        for i in infos:
            zout.writestr(i, datos[i.filename])

    # Verificación: lo que debía conservarse sigue igual, y los valores quedaron escritos
    with zipfile.ZipFile(destino) as z:
        despues = firma(z)
    perdidos = [n for n in antes if antes[n] != despues.get(n)]
    from openpyxl import load_workbook
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        wb = load_workbook(destino, read_only=True)
        no_quedaron = []
        for hoja, ref, valor in pares:
            if hoja in mapa and not any(x.startswith(f"{hoja}!{ref}: no se escribió") for x in rechazos):
                v = wb[hoja][ref].value
                if v is None and str(valor) != "":
                    no_quedaron.append(f"{hoja}!{ref}")
        wb.close()
    conservados = {e.strip("<: ").split(" ")[0]: sum(v[i] for v in despues.values()) for i, e in enumerate(CONSERVAR)}
    resumen = ", ".join(f"{k} {v}" for k, v in conservados.items() if v)
    print(f"\nArchivo: {salida.as_posix()}")
    print(f"- Elementos conservados: {resumen or 'sin elementos especiales'}")
    if perdidos or no_quedaron:
        print(f"- ATENCIÓN: cambió algo que debía conservarse ({', '.join(perdidos) or '—'}) o faltan valores "
              f"({', '.join(no_quedaron) or '—'}). No uses este archivo; revisa el detalle.")
        return 1
    print("- Verificación: OK (todo lo demás quedó idéntico; Excel recalcula las fórmulas al abrir).")
    return 1 if rechazos else 0


if __name__ == "__main__":
    import _consola
    _consola.preparar()
    sys.exit(main())
