#!/usr/bin/env python3
"""Adopta los formatos propios de la empresa (o de un proyecto) como el «por defecto» del harness.

Uso:
    python herramientas/adoptar_formatos.py empresa                        # analiza empresa/_entrada/ y propone
    python herramientas/adoptar_formatos.py proyectos/<slug>               # idem con _entrada/04-reportes-y-plantillas/
    python herramientas/adoptar_formatos.py empresa --asignar F-02=minuta  # corrige el tipo detectado
    python herramientas/adoptar_formatos.py empresa --descartar F-04 --quien "Nombre"
    python herramientas/adoptar_formatos.py empresa --aplicar --quien "Nombre" [--mejorado F-01,F-03] [--marca]
    python herramientas/adoptar_formatos.py --tipos                        # tipos de salida que conoce el harness

Qué hace:
- Inventaría los archivos entregados (Word, Excel, PowerPoint, Markdown, imágenes), lee su estructura (títulos,
  tablas, hojas, diapositivas, marcadores, logo, fuente y color) y detecta a qué salida del harness corresponde cada
  uno (informe de avance, minuta, presentación, carta, planilla de control o un reporte de un arquetipo).
- Compara cada formato con el contrato de esa salida (`herramientas/formatos/contratos/` y los catálogos de los
  arquetipos): qué sección falta en el formato propio (y qué se pierde si se omite) y qué sección propia el harness no
  sabe llenar (queda como insumo manual). Deja el detalle en `formatos/analisis/F-nn.md` y el resumen en
  `formatos/registro.csv`.
- Propone una mejora para los Word: una copia `_v2` con las secciones que faltan y marcadores, sin tocar el original.
- Con --aplicar copia el formato (original o mejorado) a `plantillas/`, escribe su definición en `reportes/catalogo/`
  (si no existe una), y en una minuta deja también el esqueleto `formatos/minuta.md`. Con --marca adopta el logo, la
  fuente y el color principal si el YAML todavía tiene los valores por defecto. Nunca sobrescribe lo que ya existe.
Todo lo adoptado vive fuera del núcleo: ninguna actualización lo toca.
"""
import argparse
import csv
import hashlib
import re
import shutil
import sys
import unicodedata
import zipfile
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CONTRATOS = RAIZ / "herramientas" / "formatos" / "contratos"
COLUMNAS = ["id", "archivo", "huella", "formato", "tipo", "confianza", "cobertura", "faltan", "propias", "marcadores",
            "version_adoptada", "destino", "estado", "aprobado_por", "fecha", "nota"]
EXT_DOC = {".docx": "docx", ".docm": "docx", ".xlsx": "xlsx", ".xlsm": "xlsx", ".pptx": "pptx", ".md": "md", ".txt": "md",
           ".csv": "csv"}
EXT_IMG = {".png", ".jpg", ".jpeg", ".svg", ".gif"}
STOP = {"de", "del", "la", "las", "el", "los", "y", "o", "en", "por", "para", "con", "sin", "al", "a", "un", "una", "unos",
        "unas", "se", "su", "sus", "que", "este", "esta", "esto", "mes", "ano", "anio", "n", "no", "si"}
DEFECTOS_YAML = {"fuente": "Arial", "color_primario": "1F3864"}
COLORES_DE_WORD = {"365F91", "2E74B5", "4F81BD", "2F5496", "1F3763", "000000"}  # colores de título por defecto de Word: no son marca


# ------------------------------------------------------------------------------------------------ utilidades
def norm(texto):
    t = unicodedata.normalize("NFKD", str(texto or "")).encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", t).strip()


def tokens(texto):
    """Palabras significativas, sin tildes ni plurales simples (riesgos → riesgo)."""
    salida = set()
    for w in re.findall(r"[a-z0-9]+", norm(texto)):
        if w in STOP or len(w) < 3:
            continue
        if len(w) > 4 and w.endswith("es") and not w.endswith("ses"):
            w = w[:-2]
        elif len(w) > 3 and w.endswith("s"):
            w = w[:-1]
        salida.add(w)
    return salida


def slug(texto):
    return re.sub(r"[^a-z0-9]+", "-", norm(texto)).strip("-")[:40] or "seccion"


def huella(ruta):
    return hashlib.sha256(Path(ruta).read_bytes()).hexdigest()[:12]


def frontmatter(texto):
    import yaml
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", texto, re.S)
    if not m:
        return {}, texto
    try:
        return (yaml.safe_load(m.group(1)) or {}), m.group(2)
    except yaml.YAMLError:
        return {}, m.group(2)


def leer_csv(ruta):
    if not Path(ruta).exists():
        return []
    with open(ruta, encoding="utf-8-sig", newline="") as f:
        return [dict(r) for r in csv.DictReader(f)]


def escribir_csv(ruta, filas):
    Path(ruta).parent.mkdir(parents=True, exist_ok=True)
    with open(ruta, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNAS, extrasaction="ignore")
        w.writeheader()
        for fila in filas:
            w.writerow({c: fila.get(c, "") for c in COLUMNAS})


def poner_campo(texto, clave, valor):
    v = '"' + str(valor).replace('"', "'") + '"'
    patron = rf"^([ \t]+{re.escape(clave)}:[ \t]*)(\"[^\"\n]*\"|'[^'\n]*'|[^#\n]*?)([ \t]*(#.*)?)$"
    nuevo, n = re.subn(patron, lambda m: m.group(1) + v + (("   " + m.group(4)) if m.group(4) else ""), texto, count=1, flags=re.M)
    return nuevo if n else texto


# ------------------------------------------------------------------------------------------------ ámbito
def ambito_de(arg):
    """Dónde se lee y dónde se adopta: la empresa o un proyecto."""
    if arg in ("empresa", "empresa/"):
        emp = RAIZ / "empresa"
        if not (emp / "empresa.yaml").exists():
            sys.exit("No hay empresa configurada (empresa/empresa.yaml). Primero la skill instalar.")
        return {"nombre": "empresa", "raiz": emp, "entradas": [emp / "_entrada"], "plantillas": emp / "plantillas",
                "catalogo": emp / "reportes" / "catalogo", "formatos": emp / "formatos", "marca": emp / "marca",
                "cfg": emp / "empresa.yaml", "prefijo_plantilla": "empresa/plantillas/", "es_empresa": True}
    p = Path(arg)
    p = p if p.is_absolute() else RAIZ / p
    if not (p / "proyecto.yaml").exists():
        sys.exit(f"No encuentro el proyecto {arg} (falta proyecto.yaml). Usa «empresa» o proyectos/<slug>.")
    entradas = [p / "_entrada" / "04-reportes-y-plantillas", p / "_entrada" / "08-marca"]
    return {"nombre": p.name, "raiz": p, "entradas": entradas, "plantillas": p / "reportes" / "plantillas",
            "catalogo": p / "reportes" / "catalogo", "formatos": p / "formatos", "marca": p / "marca", "cfg": p / "proyecto.yaml",
            "prefijo_plantilla": "", "es_empresa": False}


def archivos_entrada(amb):
    salida = []
    for carpeta in amb["entradas"]:
        if not carpeta.is_dir():
            continue
        for x in sorted(carpeta.rglob("*")):
            if x.is_file() and x.name.upper() != "LEEME.MD" and not x.name.startswith(("~$", "_", ".")) and "_procesado" not in x.parts \
                    and "_archivo" not in x.parts and (x.suffix.lower() in EXT_DOC or x.suffix.lower() in EXT_IMG):
                salida.append(x)
    return salida


# ------------------------------------------------------------------------------------------------ contratos
def parsear_tabla(texto):
    filas = []
    for linea in texto.splitlines():
        if not linea.startswith("|") or re.match(r"^\|\s*-", linea):
            continue
        celdas = [c.strip() for c in linea.strip().strip("|").split("|")]
        filas.append(celdas)
    return filas[1:] if filas else []


def tipos_conocidos():
    """{tipo: {nombre, formatos, claves, secciones: [{nombre, claves, fuente, obligatoria}], origen}}."""
    tipos = {}
    for ruta in sorted(CONTRATOS.glob("*.md")):
        fm, cuerpo = frontmatter(ruta.read_text(encoding="utf-8"))
        secciones = []
        for celdas in parsear_tabla(cuerpo):
            if len(celdas) < 4:
                continue
            secciones.append({"nombre": celdas[0], "claves": [x.strip() for x in celdas[1].split(",") if x.strip()],
                              "fuente": celdas[2], "obligatoria": norm(celdas[3]).startswith("s")})
        tipos[fm.get("tipo", ruta.stem)] = {"nombre": fm.get("nombre", ruta.stem), "formatos": fm.get("formatos") or [],
                                            "claves": [str(x) for x in (fm.get("claves") or [])], "secciones": secciones,
                                            "origen": ruta.relative_to(RAIZ).as_posix()}
    for ruta in sorted((RAIZ / "arquetipos").glob("*/estructura/reportes/catalogo/*.md")):
        if ruta.name.startswith("_"):
            continue
        fm, cuerpo = frontmatter(ruta.read_text(encoding="utf-8"))
        tipo = fm.get("tipo", ruta.stem)
        if tipo in tipos:
            continue
        secciones = []
        bloque = re.search(r"^# Secciones\s*\n(.*?)(?=^# |\Z)", cuerpo, re.M | re.S)
        for linea in (bloque.group(1) if bloque else "").splitlines():
            m = re.match(r"^\s*\d+\.\s+(?:\*\*(.+?)\*\*|([^—:\-]+?))\s*(?:[—:\-]\s*(.*))?$", linea)
            if m:
                nombre = (m.group(1) or m.group(2) or "").strip()
                secciones.append({"nombre": nombre, "claves": [], "fuente": (m.group(3) or "").strip()[:80], "obligatoria": False})
        tipos[tipo] = {"nombre": fm.get("nombre", tipo), "formatos": [fm.get("formato", "docx")],
                       "claves": sorted(tokens(fm.get("nombre", "")) | tokens(tipo.replace("-", " "))), "secciones": secciones,
                       "origen": ruta.relative_to(RAIZ).as_posix() + f" (arquetipo {ruta.parts[-5]})"}
    return tipos


# ------------------------------------------------------------------------------------------------ análisis
def analizar_docx(ruta):
    from docx import Document
    d = Document(str(ruta))
    titulos, estilos = [], {}
    for p in d.paragraphs:
        t = p.text.strip()
        if not t:
            continue
        estilo = (p.style.name or "") if p.style is not None else ""
        e = estilo.lower()
        if e.startswith("heading") or e.startswith("título") or e.startswith("titulo") or e == "title":
            nivel = re.findall(r"\d", e)
            titulos.append((int(nivel[0]) if nivel else 1, t))
            estilos[estilo] = estilos.get(estilo, 0) + 1
        elif len(t) < 80 and p.runs and all(r.bold for r in p.runs if r.text.strip()) and not t.endswith("."):
            titulos.append((9, t))
    tablas = []
    for tabla in d.tables:
        if tabla.rows:
            tablas.append([c.text.strip() for c in tabla.rows[0].cells])
    texto = "\n".join(p.text for p in d.paragraphs) + "\n" + "\n".join(" ".join(c) for c in tablas)
    for s in d.sections:
        for parte in (s.header, s.footer):
            for p in parte.paragraphs:
                texto += "\n" + p.text
    marcadores = sorted(set(re.findall(r"\{\{[^}]+\}\}", texto)))
    encabezado = " / ".join(dict.fromkeys(p.text.strip() for s in d.sections for p in s.header.paragraphs if p.text.strip()))
    fuente = d.styles["Normal"].font.name if "Normal" in [s.name for s in d.styles] else None
    color = None
    try:
        h1 = d.styles["Heading 1"].font.color
        color = str(h1.rgb) if h1 is not None and h1.rgb is not None else None
    except KeyError:
        pass
    logo = None
    try:
        with zipfile.ZipFile(ruta) as z:
            nombres = z.namelist()
            rels = [n for n in nombres if re.match(r"word/_rels/header\d*\.xml\.rels", n)]
            medios = []
            for r in rels:
                medios += re.findall(r'Target="media/([^"]+)"', z.read(r).decode("utf-8", "ignore"))
            if not medios:
                medios = [Path(n).name for n in nombres if n.startswith("word/media/")][:1]
            for m in medios[:1]:
                if Path(m).suffix.lower() in {".png", ".jpg", ".jpeg"}:
                    logo = (Path(m).suffix.lower(), z.read("word/media/" + m))
    except (zipfile.BadZipFile, KeyError):
        pass
    estilo_titulo = max(estilos, key=estilos.get) if estilos else ""
    return {"titulos": titulos, "tablas": tablas, "marcadores": marcadores, "encabezado": encabezado, "fuente": fuente,
            "color": color, "logo": logo, "estilo_titulo": estilo_titulo, "texto": texto, "formulas": 0}


def analizar_xlsx(ruta):
    from openpyxl import load_workbook
    wb = load_workbook(str(ruta), read_only=True)
    hojas, titulos, formulas, filas_total = [], [], 0, 0
    for ws in wb.worksheets:
        encabezados, n = [], 0
        for fila in ws.iter_rows(values_only=True):
            vals = ["" if v is None else str(v) for v in fila]
            if any(vals):
                n += 1
                formulas += sum(1 for v in vals if v.startswith("="))
                if not encabezados and sum(1 for v in vals if v and not v.startswith("=")) >= 2:
                    encabezados = [v for v in vals if v][:12]
        hojas.append({"nombre": ws.title, "encabezados": encabezados, "filas": n})
        filas_total += n
        titulos.append((1, ws.title))
        titulos += [(2, e) for e in encabezados]
    try:
        import inspeccionar_xlsx
        riesgos = inspeccionar_xlsx.riesgos_al_guardar(ruta)
    except Exception:
        riesgos = []
    texto = "\n".join(h["nombre"] + " " + " ".join(h["encabezados"]) for h in hojas)
    return {"titulos": titulos, "tablas": [h["encabezados"] for h in hojas], "marcadores": [], "encabezado": "", "fuente": None,
            "color": None, "logo": None, "estilo_titulo": "", "texto": texto, "formulas": formulas, "hojas": hojas,
            "riesgos": riesgos, "filas": filas_total}


def analizar_pptx(ruta):
    from pptx import Presentation
    prs = Presentation(str(ruta))
    titulos, texto = [], []
    for s in prs.slides:
        t = s.shapes.title.text.strip() if s.shapes.title is not None and s.shapes.title.text else ""
        if t:
            titulos.append((1, t))
        for sh in s.shapes:
            if sh.has_text_frame and sh.text_frame.text.strip():
                texto.append(sh.text_frame.text.strip())
    layouts = [l.name for l in prs.slide_layouts]
    return {"titulos": titulos, "tablas": [], "marcadores": sorted(set(re.findall(r"\{\{[^}]+\}\}", "\n".join(texto)))),
            "encabezado": "", "fuente": None, "color": None, "logo": None, "estilo_titulo": "", "texto": "\n".join(texto),
            "formulas": 0, "layouts": layouts, "diapositivas": len(prs.slides)}


def analizar_md(ruta):
    texto = ruta.read_text(encoding="utf-8", errors="replace")
    titulos = [(len(m.group(1)), m.group(2).strip()) for m in re.finditer(r"^(#{1,6})\s+(.+)$", texto, re.M)]
    return {"titulos": titulos, "tablas": [], "marcadores": sorted(set(re.findall(r"\{\{[^}]+\}\}", texto))), "encabezado": "",
            "fuente": None, "color": None, "logo": None, "estilo_titulo": "", "texto": texto, "formulas": 0}


def analizar(ruta):
    ext = ruta.suffix.lower()
    if ext in EXT_IMG:
        return {"titulos": [], "tablas": [], "marcadores": [], "encabezado": "", "fuente": None, "color": None, "logo": None,
                "estilo_titulo": "", "texto": "", "formulas": 0, "imagen": True}
    if EXT_DOC.get(ext) == "docx":
        return analizar_docx(ruta)
    if EXT_DOC.get(ext) == "xlsx":
        return analizar_xlsx(ruta)
    if ext == ".pptx":
        return analizar_pptx(ruta)
    if ext == ".csv":
        filas = leer_csv(ruta)
        enc = list(filas[0].keys()) if filas else []
        return {"titulos": [(2, e) for e in enc], "tablas": [enc], "marcadores": [], "encabezado": "", "fuente": None, "color": None,
                "logo": None, "estilo_titulo": "", "texto": " ".join(enc), "formulas": 0, "filas": len(filas)}
    return analizar_md(ruta)


# ------------------------------------------------------------------------------------------------ emparejar y comparar
def emparejar(ruta, an, tipos):
    """[(tipo, puntaje)] de mayor a menor."""
    ext = EXT_DOC.get(ruta.suffix.lower(), "")
    t_nombre = tokens(ruta.stem.replace("_", " ").replace("-", " "))
    t_tit = set().union(*[tokens(t) for _, t in an["titulos"]]) if an["titulos"] else set()
    t_txt = tokens(an["texto"][:4000])
    puntajes = []
    for tipo, c in tipos.items():
        if ext and c["formatos"] and ext not in c["formatos"] and not (ext == "md"):
            continue
        claves = set().union(*[tokens(k) for k in c["claves"]]) if c["claves"] else set()
        p = 3 * len(claves & t_nombre) + 2 * len(claves & t_tit) + len(claves & t_txt)
        if c["secciones"]:
            p += 2 * sum(1 for s in c["secciones"] if presente(s, an["titulos"]))
        if p:
            puntajes.append((tipo, p))
    return sorted(puntajes, key=lambda x: -x[1])


def puntaje_seccion(seccion, titulo):
    """Cuánto calza un título de la plantilla con una sección del contrato (el nombre pesa más que los sinónimos)."""
    t = tokens(titulo)
    nombre = tokens(seccion["nombre"])
    sinonimos = set().union(*[tokens(k) for k in seccion["claves"]]) if seccion["claves"] else set()
    return 3 * len(nombre & t) + len((sinonimos - nombre) & t)


def titulos_utiles(an):
    """Títulos que cuentan como secciones: sin el título del documento ni los encabezados de columna de una planilla."""
    titulos = list(an["titulos"])
    if an.get("hojas"):
        return [(n, t) for n, t in titulos if n == 1]
    if titulos and titulos[0][0] == 1 and any(n > 1 for n, _ in titulos[1:]):
        titulos = titulos[1:]
    return titulos


def presente(seccion, titulos):
    """El título de la plantilla que mejor corresponde a la sección del contrato, o ''."""
    mejor = max(((puntaje_seccion(seccion, t), t) for _, t in titulos), default=(0, ""))
    return mejor[1] if mejor[0] > 0 else ""


def comparar(an, contrato):
    """Empareja secciones del contrato con títulos de la plantilla (mejor calce primero, un título por sección)."""
    titulos = titulos_utiles(an)
    pares = []
    for s in contrato["secciones"]:
        for _, t in titulos:
            p = puntaje_seccion(s, t)
            if p > 0:
                pares.append((p, s["nombre"], t))
        if an.get("layouts") and an["titulos"] and norm(s["nombre"]) == "portada":  # la primera diapositiva es la portada
            pares.append((99, s["nombre"], an["titulos"][0][1]))
    pares.sort(key=lambda x: -x[0])
    asignado, usados = {}, set()
    for p, nombre, t in pares:
        if nombre in asignado or t in usados:
            continue
        asignado[nombre] = t
        usados.add(t)
    presentes = [(s, asignado[s["nombre"]]) for s in contrato["secciones"] if s["nombre"] in asignado]
    faltan = [s for s in contrato["secciones"] if s["nombre"] not in asignado]
    propias = [t for nivel, t in titulos if t not in usados and nivel <= 2 and not re.match(r"^\d+(\.\d+)*\.?$", t)]
    total = len(contrato["secciones"])
    return {"presentes": presentes, "faltan": faltan, "propias": propias, "cobertura": f"{len(presentes)}/{total}" if total else "-"}


def mejorar_docx(origen, faltan, destino, estilo_titulo):
    """Copia del Word con las secciones que faltan al final (mismo estilo de título) y un marcador en cada una."""
    from docx import Document
    doc = Document(str(origen))
    estilo = estilo_titulo if estilo_titulo and estilo_titulo in [s.name for s in doc.styles] else None
    agregadas = []
    for s in faltan:
        p = doc.add_paragraph(s["nombre"])
        if estilo:
            p.style = doc.styles[estilo]
        else:
            for r in p.runs:
                r.bold = True
        doc.add_paragraph("{{" + slug(s["nombre"]) + "}}")
        agregadas.append(s["nombre"])
    destino.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(destino))
    return agregadas


# ------------------------------------------------------------------------------------------------ registro y análisis
def siguiente_id(filas):
    n = max([int(m.group(1)) for f in filas for m in [re.match(r"F-(\d+)", f.get("id", ""))] if m] + [0])
    return f"F-{n + 1:02d}"


def texto_analisis(fila, an, contrato, comp, ruta):
    out = [f"# {fila['id']} · {ruta.name}", "",
           f"- Tipo detectado: **{fila['tipo']}**" + (f" ({contrato['nombre']})" if contrato else "") + f" · confianza {fila['confianza']}",
           f"- Cobertura del contrato: {fila['cobertura']}" + (f" · marcadores: {', '.join(an['marcadores'])}" if an["marcadores"] else " · sin marcadores (el harness ubica las secciones por sus títulos)")]
    if an.get("hojas"):
        out.append(f"- Hojas: " + "; ".join(f"{h['nombre']} ({h['filas']} filas)" for h in an["hojas"]) + f" · fórmulas: {an['formulas']}"
                   + (" · ADVERTENCIA: " + ", ".join(an["riesgos"]) + " (se llena solo con llenar_xlsx.py)" if an.get("riesgos") else ""))
    if an.get("layouts"):
        out.append(f"- Diapositivas: {an['diapositivas']} · layouts: " + ", ".join(an["layouts"][:8]))
    if an.get("fuente") or an.get("color") or an.get("logo"):
        out.append("- Marca encontrada: " + " · ".join(x for x in [f"fuente {an['fuente']}" if an.get("fuente") else "",
                                                                   f"color de títulos {an['color']}" if an.get("color") else "",
                                                                   "logo en el encabezado" if an.get("logo") else ""] if x))
    if contrato:
        out += ["", "## Lo que el harness sabe llenar y cómo queda en tu formato", "",
                "| Sección del harness | En tu formato | De dónde sale | Si falta |", "|---|---|---|---|"]
        for s, t in comp["presentes"]:
            out.append(f"| {s['nombre']} | «{t}» | {s['fuente']} | |")
        for s in comp["faltan"]:
            out.append(f"| {s['nombre']} | **falta** | {s['fuente']} | "
                       + ("no se reportará en este documento; la versión mejorada la agrega" if s["obligatoria"] else "opcional: se omite sin pérdida grave") + " |")
        if comp["propias"]:
            out += ["", "## Secciones tuyas que el harness no sabe llenar solo", ""]
            out += [f"- «{t}»: queda como insumo manual (se te pide el contenido) o se conecta a un dato del proyecto en la definición." for t in comp["propias"]]
    else:
        out += ["", "No calza con ninguna salida del harness: se registra como **archivo base** (se usará cuando un proyecto lo necesite)."]
    return "\n".join(out) + "\n"


def analizar_ambito(amb, tipos, asignaciones=None):
    """Analiza todo lo que hay en la entrada del ámbito y actualiza registro y análisis. Devuelve las filas."""
    registro = leer_csv(amb["formatos"] / "registro.csv")
    por_archivo = {f["archivo"]: f for f in registro}
    resultados = []
    for ruta in archivos_entrada(amb):
        rel = ruta.relative_to(amb["raiz"]).as_posix()
        h = huella(ruta)
        fila = por_archivo.get(rel)
        if fila is None:
            fila = {"id": siguiente_id(registro), "archivo": rel, "estado": "propuesto", "version_adoptada": "pendiente"}
            registro.append(fila)
            por_archivo[rel] = fila
        elif fila.get("huella") == h and fila.get("estado") in ("adoptado", "descartado") and not (asignaciones or {}).get(fila["id"]):
            resultados.append((fila, None, None, None, ruta))
            continue
        fila["huella"] = h
        fila["formato"] = "imagen" if ruta.suffix.lower() in EXT_IMG else EXT_DOC.get(ruta.suffix.lower(), ruta.suffix.lower().strip("."))
        try:
            an = analizar(ruta)
        except Exception as e:  # un archivo dañado no detiene la adopción de los demás
            fila.update({"tipo": "ilegible", "confianza": "", "nota": f"no se pudo leer: {e}"[:200], "estado": "propuesto"})
            resultados.append((fila, None, None, None, ruta))
            continue
        if an.get("imagen"):
            fila.update({"tipo": "logo" if "logo" in norm(ruta.stem) or "marca" in norm(ruta.stem) else "imagen", "confianza": "alta",
                         "cobertura": "-", "faltan": "", "propias": "", "marcadores": ""})
            resultados.append((fila, an, None, None, ruta))
            continue
        forzado = (asignaciones or {}).get(fila["id"]) or (fila.get("tipo") if fila.get("nota", "").startswith("tipo asignado") else "")
        if forzado and forzado in tipos:
            tipo, conf = forzado, "asignada"
        else:
            ranking = emparejar(ruta, an, tipos)
            if ranking and ranking[0][1] >= 3:
                tipo = ranking[0][0]
                conf = "alta" if len(ranking) == 1 or ranking[0][1] >= 2 * ranking[1][1] else "media"
                if ranking[0][0] != "planilla-control" and fila["formato"] == "xlsx" and an.get("formulas", 0) == 0 and an.get("filas", 0) > 30:
                    tipo, conf = "archivo-base", "media"
            elif fila["formato"] in ("xlsx", "csv") or (fila["formato"] == "md" and not an["titulos"]):
                tipo, conf = "archivo-base", "media"
            else:
                tipo, conf = "sin-tipo", "baja"
        contrato = tipos.get(tipo)
        comp = comparar(an, contrato) if contrato else {"presentes": [], "faltan": [], "propias": [t for _, t in an["titulos"][:10]], "cobertura": "-"}
        fila.update({"tipo": tipo, "confianza": conf, "cobertura": comp["cobertura"],
                     "faltan": "; ".join(s["nombre"] for s in comp["faltan"]), "propias": "; ".join(comp["propias"][:8]),
                     "marcadores": str(len(an["marcadores"]))})
        if fila.get("estado") not in ("adoptado", "descartado"):
            fila["estado"] = "propuesto"
        carpeta = amb["formatos"] / "analisis"
        carpeta.mkdir(parents=True, exist_ok=True)
        (carpeta / f"{fila['id']}.md").write_text(texto_analisis(fila, an, contrato, comp, ruta), encoding="utf-8")
        if fila["formato"] == "docx" and comp["faltan"] and fila.get("estado") == "propuesto":
            destino_v2 = amb["formatos"] / "mejorados" / f"{ruta.stem}_v2.docx"
            try:
                mejorar_docx(ruta, comp["faltan"], destino_v2, an.get("estilo_titulo", ""))
                fila["nota"] = f"versión mejorada propuesta: {destino_v2.relative_to(amb['raiz']).as_posix()} (agrega: " + ", ".join(s["nombre"] for s in comp["faltan"]) + ")"
            except Exception as e:
                fila["nota"] = f"no se pudo armar la versión mejorada: {e}"[:200]
        resultados.append((fila, an, contrato, comp, ruta))
    escribir_csv(amb["formatos"] / "registro.csv", registro)
    return registro, resultados


# ------------------------------------------------------------------------------------------------ aplicar
def escribir_definicion(amb, fila, contrato, comp, an, ruta_plantilla, tipo=None):
    """Definición de reporte en el catálogo del ámbito, a partir del contrato y de las secciones del formato propio."""
    tipo = tipo or fila["tipo"]
    destino = amb["catalogo"] / f"{tipo}.md"
    if destino.exists():
        return destino, False
    formato = fila["formato"] if fila["formato"] in ("docx", "xlsx", "pptx", "md") else "docx"
    modo = "actualizar" if formato == "xlsx" and an.get("formulas", 0) > 0 else "generar"
    nombre_archivo = Path(fila["archivo"]).stem.replace("_", " ")
    cadencia = next((c for c in ("semanal", "quincenal", "mensual") if c in norm(nombre_archivo) or c in norm(an.get("texto", "")[:500])), "a pedido")
    fuentes = []
    for s, _ in comp["presentes"]:
        for f in re.split(r",\s*", s["fuente"]):
            if f and f not in fuentes and ("/" in f or f.endswith(".py") or f.endswith(".csv")):
                fuentes.append(f)
    lineas = ["---", f"tipo: {tipo}", f"nombre: {contrato['nombre'] if contrato else nombre_archivo}", f"formato: {formato}", f"modo: {modo}",
              f'plantilla: "{ruta_plantilla}"', f"cadencia: {cadencia}", f"periodo_archivo: {'semana' if cadencia == 'semanal' else 'mes'}",
              "destinatarios: []", "fuentes:"] + [f"  - {f}" for f in fuentes] + ["---", "",
              "# Propósito", f"Formato propio de la {'empresa' if amb['es_empresa'] else 'del proyecto'} adoptado desde «{Path(fila['archivo']).name}». "
              "Se llena con `llenar_docx.py` (Word), `llenar_xlsx.py` (Excel) o la plantilla de PowerPoint, respetando su estructura.", "",
              "# Secciones"]
    n = 0
    for s, t in comp["presentes"]:
        n += 1
        lineas.append(f"{n}. **{s['nombre']}** — en la plantilla: «{t}». Fuente: {s['fuente']}.")
    for t in comp["propias"]:
        n += 1
        lineas.append(f"{n}. **{t}** — sección propia: insumo manual (se pide al usuario) hasta conectarla a un dato del proyecto.")
    if comp["faltan"]:
        lineas += ["", "# No se reporta en este formato (faltaba en el original)"] + \
                  [f"- {s['nombre']}" + (" (recomendado agregarlo: la versión mejorada lo trae)" if s["obligatoria"] else "") for s in comp["faltan"]]
    lineas += ["", "# Mapeo de secciones", "| Sección del harness | Título en la plantilla |", "|---|---|"] + \
              [f"| {s['nombre']} | {t} |" for s, t in comp["presentes"]]
    if an.get("hojas"):
        lineas += ["", "# Mapeo (xlsx)", "| Hoja | Celda o rango | Dato | Fuente |", "|---|---|---|---|"] + \
                  [f"| {h['nombre']} | [PENDIENTE: celdas] | {', '.join(h['encabezados'][:6])} | |" for h in an["hojas"]]
    lineas += ["", "# Reglas", "- No cambiar la estructura de la plantilla (secciones, orden, logo) salvo que el usuario lo pida.", "",
               "# Validaciones antes de entregar", "- Sin `[PENDIENTE` en el texto; `verificar_autoria.py` en OK."]
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    return destino, True


def esqueleto_minuta(amb, an, comp):
    destino = amb["formatos"] / "minuta.md"
    if destino.exists():
        return destino, False
    lineas = ["# Minuta — <tema>", "", "<!-- Esqueleto tomado del formato propio: mismas secciones y orden. -->", ""]
    for nivel, t in an["titulos"]:
        if nivel <= 2 or nivel == 9:
            lineas += [f"## {t}", ""]
    for s in comp["faltan"]:
        if s["obligatoria"]:
            lineas += [f"## {s['nombre']}", "<!-- no estaba en el formato original; recomendado -->", ""]
    destino.write_text("\n".join(lineas), encoding="utf-8")
    return destino, True


def aplicar(amb, registro, resultados, quien, mejorados, marca, hoy):
    hechos = []
    for fila, an, contrato, comp, ruta in resultados:
        if fila.get("estado") != "propuesto" or fila.get("tipo") in ("ilegible", "sin-tipo"):
            continue
        if fila.get("tipo") in ("logo", "imagen"):
            if marca:
                amb["marca"].mkdir(parents=True, exist_ok=True)
                destino = amb["marca"] / ("logo" + ruta.suffix.lower())
                if not destino.exists():
                    shutil.copy2(ruta, destino)
                    hechos.append(f"{fila['id']}: logo adoptado en {destino.relative_to(amb['raiz']).as_posix()}")
                fila.update({"estado": "adoptado", "destino": destino.relative_to(amb["raiz"]).as_posix(), "version_adoptada": "original"})
            continue
        if fila.get("tipo") == "archivo-base":
            destino = amb["formatos"] / "base" / ruta.name
            destino.parent.mkdir(parents=True, exist_ok=True)
            if not destino.exists():
                shutil.copy2(ruta, destino)
            fila.update({"estado": "adoptado", "destino": destino.relative_to(amb["raiz"]).as_posix(), "version_adoptada": "original",
                         "aprobado_por": quien, "fecha": hoy})
            hechos.append(f"{fila['id']}: archivo base guardado en {fila['destino']} (se usa cuando un proyecto lo necesite)")
            continue
        tipo = fila["tipo"]
        usar_mejorado = fila["id"] in mejorados and fila["formato"] == "docx"
        origen = (amb["formatos"] / "mejorados" / f"{ruta.stem}_v2.docx") if usar_mejorado else ruta
        if usar_mejorado and not origen.exists():
            origen, usar_mejorado = ruta, False
        amb["plantillas"].mkdir(parents=True, exist_ok=True)
        tipo_def = tipo  # un segundo formato del mismo tipo (otro informe) queda como tipo propio: informe-avance-f-04
        if (amb["catalogo"] / f"{tipo}.md").exists() or (amb["plantillas"] / f"{tipo}{ruta.suffix.lower()}").exists():
            tipo_def = f"{tipo}-{fila['id'].lower()}"
        destino = amb["plantillas"] / f"{tipo_def}{ruta.suffix.lower()}"
        shutil.copy2(origen, destino)
        rel_plantilla = amb["prefijo_plantilla"] + destino.name if amb["es_empresa"] else f"reportes/plantillas/{destino.name}"
        if usar_mejorado:
            comp = {"presentes": comp["presentes"] + [(s, s["nombre"]) for s in comp["faltan"]], "faltan": [], "propias": comp["propias"],
                    "cobertura": f"{len(comp['presentes']) + len(comp['faltan'])}/{len(contrato['secciones'])}"}
        definicion, nueva = escribir_definicion(amb, fila, contrato, comp, an, rel_plantilla, tipo_def)
        extra = ""
        if tipo == "minuta" and amb["es_empresa"]:
            esq, nuevo_esq = esqueleto_minuta(amb, an, comp)
            extra = f"; esqueleto {esq.relative_to(amb['raiz']).as_posix()}" if nuevo_esq else ""
        if tipo_def != tipo:
            extra += f" (ya había un {tipo}: este queda como tipo «{tipo_def}»)"
        fila.update({"estado": "adoptado", "destino": destino.relative_to(amb["raiz"]).as_posix(),
                     "version_adoptada": "mejorada" if usar_mejorado else "original", "aprobado_por": quien, "fecha": hoy,
                     "cobertura": comp["cobertura"], "faltan": "; ".join(s["nombre"] for s in comp["faltan"])})
        hechos.append(f"{fila['id']}: {tipo} adoptado ({fila['version_adoptada']}) → {fila['destino']}; definición "
                      + (f"{definicion.relative_to(amb['raiz']).as_posix()} creada" if nueva else f"{definicion.relative_to(amb['raiz']).as_posix()} ya existía: no se tocó") + extra)
    if marca:  # la marca sale de UN documento: el Word con logo en el encabezado; si no, el informe de avance; si no, el primer Word
        docs = [(f, an, r) for f, an, c, comp, r in resultados if an and f.get("formato") == "docx"]
        elegido = next((x for x in docs if x[1].get("logo")), None) or next((x for x in docs if x[0].get("tipo") == "informe-avance"), None) \
            or (docs[0] if docs else None)
        if elegido:
            hechos += [f"marca tomada de {Path(elegido[0]['archivo']).name}"] + adoptar_marca(amb, elegido[1])
    escribir_csv(amb["formatos"] / "registro.csv", registro)
    return hechos


def adoptar_marca(amb, an):
    hechos = []
    cfg = amb["cfg"]
    texto = cfg.read_text(encoding="utf-8")
    cambios = []
    for clave, valor in (("fuente", an.get("fuente")), ("color_primario", (an.get("color") or "").upper() or None)):
        if not valor or (clave == "color_primario" and valor in COLORES_DE_WORD):
            continue
        m = re.search(rf"^[ \t]+{clave}:[ \t]*\"?([^\"#\n]*?)\"?[ \t]*(#.*)?$", texto, re.M)
        actual = m.group(1).strip() if m else ""
        if actual in ("", DEFECTOS_YAML[clave]) and actual != valor:
            texto = poner_campo(texto, clave, valor)
            cambios.append(f"{clave}: {actual or '(vacío)'} → {valor}")
        elif actual and actual != valor:
            hechos.append(f"marca: {clave} ya estaba en {actual} (la plantilla usa {valor}); no se cambió")
    if cambios:
        cfg.write_text(texto, encoding="utf-8")
        hechos.append(f"marca adoptada en {cfg.name}: " + "; ".join(cambios))
    if an.get("logo"):
        amb["marca"].mkdir(parents=True, exist_ok=True)
        ext, datos = an["logo"]
        destino = amb["marca"] / ("logo" + ext)
        if not any(amb["marca"].glob("logo.*")):
            destino.write_bytes(datos)
            hechos.append(f"marca: logo tomado del encabezado del Word → {destino.relative_to(amb['raiz']).as_posix()}")
            if ext != ".png":
                hechos.append("marca: el logo no es PNG; proyecto.yaml/empresa.yaml esperan marca/logo.png: conviértelo o ajusta formato.logo")
    return hechos


# ------------------------------------------------------------------------------------------------ salida
def resumen(amb, registro, resultados, tipos):
    print(f"# Formatos propios · {amb['nombre']}\n")
    if not resultados:
        print(f"No hay archivos en {' ni '.join(e.relative_to(amb['raiz']).as_posix() + '/' for e in amb['entradas'])}. "
              "Deja ahí tus formatos (Word, Excel, PowerPoint, logo) y vuelve a ejecutar.")
        return
    for fila, an, contrato, comp, ruta in resultados:
        estado = fila.get("estado", "")
        print(f"## {fila['id']} · {Path(fila['archivo']).name} · {estado}")
        if fila.get("tipo") == "ilegible":
            print(f"- No se pudo leer: {fila.get('nota')}\n")
            continue
        if an is None:
            print(f"- Ya {estado} ({fila.get('version_adoptada', '')}) → {fila.get('destino', '')}\n")
            continue
        if fila.get("tipo") in ("logo", "imagen"):
            print("- Imagen: se adopta como logo con --aplicar --marca (si no hay otro).\n")
            continue
        if contrato:
            print(f"- Es un **{contrato['nombre']}** (confianza {fila['confianza']}). Cubre {fila['cobertura']} de lo que el harness sabe llenar.")
            if comp["faltan"]:
                oblig = [s["nombre"] for s in comp["faltan"] if s["obligatoria"]]
                opc = [s["nombre"] for s in comp["faltan"] if not s["obligatoria"]]
                if oblig:
                    print(f"- Le falta: {', '.join(oblig)}. Si se adopta tal cual, eso no se reporta en este documento.")
                if opc:
                    print(f"- Opcional que no trae: {', '.join(opc)}.")
                if fila.get("nota", "").startswith("versión mejorada"):
                    print(f"- Mejora propuesta: {fila['nota'].split(': ', 1)[1]}. Para adoptarla: --aplicar --mejorado {fila['id']}.")
            if comp["propias"]:
                print(f"- Secciones tuyas que el harness no llena solo: {', '.join(comp['propias'][:6])} (insumo manual o se conectan a un dato).")
            if an.get("riesgos"):
                print(f"- Ojo: la planilla tiene {', '.join(an['riesgos'])}: se llena solo con llenar_xlsx.py para no dañarla.")
        elif fila.get("tipo") == "archivo-base":
            print("- No es un reporte: se guarda como archivo base para cuando un proyecto lo necesite (por ejemplo, un plan de cuentas).")
        else:
            print("- No calza con ninguna salida conocida. Asigna el tipo con --asignar " + fila["id"] + "=<tipo> (ver --tipos) o descártalo.")
        print(f"- Detalle: {(amb['formatos'] / 'analisis' / (fila['id'] + '.md')).relative_to(amb['raiz']).as_posix()}\n")
    pend = [f["id"] for f in registro if f.get("estado") == "propuesto" and f.get("tipo") not in ("ilegible", "sin-tipo")]
    if pend:
        print(f"Para adoptar lo propuesto ({', '.join(pend)}): python herramientas/adoptar_formatos.py {amb['nombre'] if amb['es_empresa'] else rel(amb['raiz'])} "
              "--aplicar --quien \"<nombre>\" [--mejorado F-xx] [--marca]. Nada de lo que ya existe se sobrescribe.")


def rel(p):
    try:
        return Path(p).resolve().relative_to(RAIZ).as_posix()
    except ValueError:
        return str(p)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ambito", nargs="?", help="«empresa» o proyectos/<slug>")
    ap.add_argument("--tipos", action="store_true", help="tipos de salida que conoce el harness")
    ap.add_argument("--asignar", action="append", default=[], metavar="F-nn=tipo")
    ap.add_argument("--descartar", help="F-nn que no se adopta")
    ap.add_argument("--aplicar", action="store_true")
    ap.add_argument("--mejorado", default="", help="F-nn,F-mm cuyas versiones mejoradas (_v2) se adoptan en vez del original")
    ap.add_argument("--marca", action="store_true", help="adoptar también logo, fuente y color si el YAML tiene los valores por defecto")
    ap.add_argument("--quien", default="")
    ap.add_argument("--hoy")
    a = ap.parse_args()
    tipos = tipos_conocidos()
    if a.tipos:
        print("# Salidas que el harness sabe llenar\n")
        for t, c in tipos.items():
            print(f"- {t}: {c['nombre']} ({', '.join(c['formatos'])}) · secciones: " + ", ".join(s["nombre"] for s in c["secciones"]) + f" · {c['origen']}")
        print("- archivo-base: cualquier archivo que no es un reporte (plan de cuentas, listas, guías); se guarda para cuando un proyecto lo use.")
        return 0
    if not a.ambito:
        ap.error("indica «empresa» o proyectos/<slug> (o --tipos).")
    try:
        import _nucleo
        if _nucleo.es_mantenedor(RAIZ):
            sys.exit("Esta carpeta es el núcleo que mantienes: los formatos propios se adoptan en una carpeta de empresa.")
    except ImportError:
        pass
    amb = ambito_de(a.ambito)
    hoy = a.hoy or date.today().isoformat()
    asignaciones = {}
    for x in a.asignar:
        if "=" not in x:
            sys.exit("--asignar F-nn=tipo")
        fid, tipo = x.split("=", 1)
        if tipo not in tipos and tipo != "archivo-base":
            sys.exit(f"Tipo desconocido «{tipo}». Ver --tipos.")
        asignaciones[fid.strip()] = tipo.strip()
    if a.descartar:
        registro = leer_csv(amb["formatos"] / "registro.csv")
        for f in registro:
            if f.get("id") == a.descartar:
                f.update({"estado": "descartado", "aprobado_por": a.quien, "fecha": hoy})
                escribir_csv(amb["formatos"] / "registro.csv", registro)
                print(f"{a.descartar} descartado: no se adopta (el archivo sigue en la entrada).")
                return 0
        sys.exit(f"No existe {a.descartar} en el registro.")
    registro, resultados = analizar_ambito(amb, tipos, asignaciones)
    if asignaciones:
        for f in registro:
            if f.get("id") in asignaciones:
                f["nota"] = "tipo asignado por el usuario" + ("; " + f["nota"] if f.get("nota") else "")
        escribir_csv(amb["formatos"] / "registro.csv", registro)
    if a.aplicar:
        if not a.quien:
            sys.exit("Indica --quien: queda registrado quién aprobó cada formato.")
        hechos = aplicar(amb, registro, resultados, a.quien, {x.strip() for x in a.mejorado.split(",") if x.strip()}, a.marca, hoy)
        print(f"# Formatos adoptados · {amb['nombre']}\n")
        print("\n".join(f"- {h}" for h in hechos) if hechos else "Nada que adoptar: no hay formatos propuestos.")
        print("\nLo adoptado es ahora el formato por defecto" + (" de todos los proyectos de la empresa (los nuevos lo reciben solos; a los "
              "existentes se les copia al pedirlo)." if amb["es_empresa"] else " de este proyecto."))
        return 0
    resumen(amb, registro, resultados, tipos)
    return 0


if __name__ == "__main__":
    import _consola
    _consola.preparar()
    sys.exit(main())
