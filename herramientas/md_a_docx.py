#!/usr/bin/env python3
"""Convierte un Markdown simple en un Word con la marca del proyecto.

Uso:
    python herramientas/md_a_docx.py entrada.md salida.docx --proyecto proyectos/<slug>
    python herramientas/md_a_docx.py informe.md salida.docx --proyecto proyectos/<slug> --plantilla plantilla.docx
    (añade --sin-plantilla para forzar el modo por defecto; --borrador permite [PENDIENTE])

Soporta: títulos (#, ##, ###), párrafos, viñetas (- o *), listas numeradas (1.),
tablas Markdown, **negrita** y *cursiva*. En tablas, las celdas que dicen Verde,
Amarillo o Rojo se colorean como semáforo. Toma logo, colores, fuente, tamaño de
página y pie de página desde proyecto.yaml (sección formato).

Autoría limpia: normaliza caracteres invisibles, omite comentarios HTML, deja como autor a
autoria.nombre (o responsable.nombre) con fecha actual, elimina partes heredadas de la plantilla y usa el
modo de compatibilidad actual de Word. Si el texto tiene marcadores [PENDIENTE…] no genera el documento,
salvo con --borrador (uso interno; verificar_autoria.py lo marcará igual).

Documento largo sobre la plantilla Word de la empresa: con --plantilla <ruta.docx>, o si formato.plantilla_word
está definido en proyecto.yaml o empresa.yaml (ruta relativa a la carpeta del proyecto y, si no está ahí, a empresa/),
el Markdown se convierte dentro de esa plantilla en vez de armar el Word desde cero. El Markdown puede abrir con un
bloque YAML entre dos líneas `---` (titulo, subtitulo, codigo, version, fecha, cliente, revisiones, y cualquier otra
clave escalar); sin plantilla ese bloque se ignora. Contrato de la plantilla:
  - {{titulo}}, {{codigo}}, {{version}}, {{fecha}}… en portada, cuerpo, tablas, encabezados y pies se reemplazan
    (también si Word partió el marcador en varios fragmentos). `autor` y `fecha` toman por defecto la autoría del
    proyecto y la fecha de hoy (con formato.formato_fecha); también hay `proyecto` y `cliente` desde proyecto.yaml.
  - Historia de revisiones: la fila de una tabla con {{rev.version}}, {{rev.fecha}}, {{rev.descripcion}} y
    {{rev.autor}} se repite por cada elemento de `revisiones` (sin revisiones, la fila se elimina).
  - Un párrafo que dice {{indice}} pasa a ser una tabla de contenido de Word (niveles 1 a 3) y el documento queda
    marcado para actualizar campos al abrirlo. Un párrafo {{contenido}} marca dónde entra el cuerpo; si falta, va al final.
  - El cuerpo usa los estilos de la plantilla (Título 1 a 3, normal, listas, leyenda y, si trae uno propio, su estilo
    de tabla); los números de título los pone la plantilla. `![pie](ruta.png)` inserta la imagen centrada (ruta relativa
    al .md) con «Figura N. pie» debajo. Un título de nivel 1 «Anexos» o «Anexo» parte en página nueva.
  - Si tras generar queda algún {{marcador}} sin reemplazar, se lista y el código de salida es 1 (salvo --borrador).
"""
import argparse
import copy
import datetime
import re
import sys
from pathlib import Path

import _config  # noqa: E402  (proyecto.yaml con herencia de programa)

try:
    import yaml
    from docx import Document
    from docx.enum.section import WD_ORIENT  # noqa: F401
    from docx.enum.style import WD_STYLE_TYPE
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Cm, Pt, RGBColor
    from docx.text.paragraph import Paragraph
except ImportError:
    sys.exit("Faltan dependencias: pip install python-docx pyyaml")

import autoria  # noqa: E402  (módulo del harness en herramientas/)

SEMAFORO = {"verde": "C6EFCE", "amarillo": "FFEB9C", "rojo": "FFC7CE"}
PAGINAS = {"carta": (Cm(21.59), Cm(27.94)), "a4": (Cm(21.0), Cm(29.7))}


def cargar_cfg(ruta_proyecto):
    if not ruta_proyecto:
        return {}, None
    raiz = Path(ruta_proyecto)
    if not (raiz / "proyecto.yaml").exists():
        return {}, raiz
    return _config.cargar(raiz), raiz


def rgb(hexa, defecto="1F3864"):
    h = str(hexa or defecto).lstrip("#")
    if not re.fullmatch(r"[0-9A-Fa-f]{6}", h):
        h = defecto
    return RGBColor.from_string(h.upper()), h.upper()


def sombrear(celda, hexa):
    tcPr = celda._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hexa)
    tcPr.append(shd)


def agregar_inline(parrafo, texto, color=None, negrita_base=False):
    partes = re.split(r"(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)", texto)
    for parte in partes:
        if not parte:
            continue
        if parte.startswith("**") and parte.endswith("**"):
            run = parrafo.add_run(parte[2:-2])
            run.bold = True
        elif parte.startswith("*") and parte.endswith("*") and len(parte) > 2:
            run = parrafo.add_run(parte[1:-1])
            run.italic = True
        elif parte.startswith("`") and parte.endswith("`"):
            run = parrafo.add_run(parte[1:-1])
        else:
            run = parrafo.add_run(parte)
        if negrita_base:
            run.bold = True
        if color is not None:
            run.font.color.rgb = color


def campo_pagina(parrafo):
    run = parrafo.add_run()
    for tipo, texto in (("begin", None), (None, "PAGE"), ("end", None)):
        if tipo:
            el = OxmlElement("w:fldChar")
            el.set(qn("w:fldCharType"), tipo)
        else:
            el = OxmlElement("w:instrText")
            el.set(qn("xml:space"), "preserve")
            el.text = texto
        run._r.append(el)


def configurar(doc, cfg, raiz):
    fmt = cfg.get("formato", {}) or {}
    proy = cfg.get("proyecto", {}) or {}
    fuente = fmt.get("fuente", "Arial")
    color, _ = rgb(fmt.get("color_primario"))

    estilo = doc.styles["Normal"]
    estilo.font.name = fuente
    estilo.element.rPr.rFonts.set(qn("w:eastAsia"), fuente)
    estilo.font.size = Pt(10.5)
    for nivel, tam in ((1, 16), (2, 13), (3, 11.5)):
        st = doc.styles[f"Heading {nivel}"]
        st.font.name = fuente
        rfonts = st.element.rPr.rFonts
        for attr in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
            rfonts.attrib.pop(qn(attr), None)
        rfonts.set(qn("w:eastAsia"), fuente)
        st.font.size = Pt(tam)
        st.font.bold = True
        st.font.color.rgb = color

    ancho, alto = PAGINAS.get(str(fmt.get("tamano_pagina", "carta")).lower(), PAGINAS["carta"])
    sec = doc.sections[0]
    sec.page_width, sec.page_height = ancho, alto
    sec.left_margin = sec.right_margin = Cm(2.2)
    sec.top_margin, sec.bottom_margin = Cm(2.5), Cm(2.0)

    # Encabezado: logo a la izquierda, nombre del proyecto a la derecha
    enc = sec.header.paragraphs[0]
    logo = (raiz / fmt.get("logo", "marca/logo.png")) if raiz else None
    if logo and logo.exists():
        enc.add_run().add_picture(str(logo), height=Cm(1.2))
        enc.add_run("\t\t")
    nombre = proy.get("nombre", "")
    if cfg.get("_programa") and nombre and "PENDIENTE" not in str(nombre).upper():
        nombre = f"{cfg['_programa'].get('nombre', '')} · {nombre}"  # subproyecto: programa y subproyecto en el encabezado
    if nombre and "PENDIENTE" not in str(nombre).upper():
        r = enc.add_run(str(nombre))
        r.font.size = Pt(9)
        r.font.color.rgb = color

    # Pie: texto de confidencialidad + número de página
    pie = sec.footer.paragraphs[0]
    pie.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cliente = proy.get("cliente", "")
    texto_pie = fmt.get("pie_de_pagina", "Documento confidencial")
    if cliente and "PENDIENTE" not in str(cliente).upper():
        texto_pie = f"{texto_pie} - {cliente}"
    r = pie.add_run(f"{texto_pie}   |   Página ")
    r.font.size = Pt(8)
    campo_pagina(pie)
    return color, fmt


def agregar_tabla(doc, filas, color_hex):
    encabezado = filas[0]
    cuerpo = filas[1:]
    tabla = doc.add_table(rows=1, cols=len(encabezado))
    tabla.style = "Table Grid"
    tabla.alignment = WD_TABLE_ALIGNMENT.CENTER
    for j, texto in enumerate(encabezado):
        celda = tabla.rows[0].cells[j]
        celda.text = ""
        agregar_inline(celda.paragraphs[0], texto, color=RGBColor(0xFF, 0xFF, 0xFF), negrita_base=True)
        sombrear(celda, color_hex)
    for fila in cuerpo:
        celdas = tabla.add_row().cells
        for j in range(len(encabezado)):
            texto = fila[j] if j < len(fila) else ""
            celdas[j].text = ""
            agregar_inline(celdas[j].paragraphs[0], texto)
            clave = re.sub(r"[^a-záéíóú]", "", texto.lower())
            if clave in SEMAFORO:
                sombrear(celdas[j], SEMAFORO[clave])
    for fila in tabla.rows:
        for celda in fila.cells:
            for par in celda.paragraphs:
                par.paragraph_format.space_after = Pt(0)
                for run in par.runs:
                    run.font.size = Pt(9)
    doc.add_paragraph()


def dividir_fila(linea):
    return [c.strip() for c in linea.strip().strip("|").split("|")]


def convertir(md, doc, color, color_hex):
    lineas = md.splitlines()
    i = 0
    while i < len(lineas):
        linea = lineas[i].rstrip()
        if not linea.strip() or linea.strip().startswith("<!--"):
            i += 1
            continue
        m = re.match(r"^(#{1,3})\s+(.*)", linea)
        if m:
            doc.add_heading(m.group(2).strip(), level=len(m.group(1)))
            i += 1
            continue
        if linea.strip().startswith("|"):
            bloque = []
            while i < len(lineas) and lineas[i].strip().startswith("|"):
                if not re.fullmatch(r"\|?[\s:\-|]+\|?", lineas[i].strip()):
                    bloque.append(dividir_fila(lineas[i]))
                i += 1
            if bloque:
                agregar_tabla(doc, bloque, color_hex)
            continue
        m = re.match(r"^\s*[-*]\s+(.*)", linea)
        if m:
            agregar_inline(doc.add_paragraph(style="List Bullet"), m.group(1))
            i += 1
            continue
        m = re.match(r"^\s*\d+[.)]\s+(.*)", linea)
        if m:
            agregar_inline(doc.add_paragraph(style="List Number"), m.group(1))
            i += 1
            continue
        if linea.strip().startswith(">"):
            p = doc.add_paragraph()
            agregar_inline(p, linea.strip().lstrip(">").strip())
            for run in p.runs:
                run.italic = True
            i += 1
            continue
        # párrafo: junta líneas seguidas
        texto = [linea.strip()]
        i += 1
        while i < len(lineas) and lineas[i].strip() and not re.match(r"^(#|\||\s*[-*]\s|\s*\d+[.)]\s|>)", lineas[i]):
            texto.append(lineas[i].strip())
            i += 1
        agregar_inline(doc.add_paragraph(), " ".join(texto))


# --- Documento largo sobre la plantilla Word de la empresa -------------------------------------------------------
MARCA = re.compile(r"\{\{[^{}]+\}\}")
RE_ANEXOS = re.compile(r"^anexos?$", re.I)
RE_IMAGEN = re.compile(r"^!\[(.*?)\]\((.+?)\)\s*$")
SIN_CLAVE = ("revisiones", "indice", "contenido")  # claves del bloque inicial que no son marcadores de texto
SIGUEN_A_UPDATEFIELDS = ("hdrShapeDefaults", "footnotePr", "endnotePr", "compat", "docVars", "rsids", "mathPr",
                         "attachedSchema", "themeFontLang", "clrSchemeMapping", "doNotIncludeSubdocsInStats",
                         "doNotAutoCompressPictures", "forceUpgrade", "captions", "readModeInkLockDown",
                         "smartTagType", "schemaLibrary", "shapeDefaults", "doNotEmbedSmartTags", "decimalSymbol",
                         "listSeparator")


def separar_frontmatter(md):
    """(datos, resto): el bloque YAML inicial entre dos líneas `---`, si lo hay. Sin bloque válido, ({}, md)."""
    lineas = md.splitlines()
    k = 0
    while k < len(lineas) and not lineas[k].strip():
        k += 1
    if k >= len(lineas) or lineas[k].strip() != "---":
        return {}, md
    fin = next((j for j in range(k + 1, len(lineas)) if lineas[j].strip() == "---"), None)
    if fin is None:
        return {}, md
    try:
        datos = yaml.safe_load("\n".join(lineas[k + 1:fin]))
    except yaml.YAMLError as e:
        sys.exit(f"El bloque inicial del Markdown (entre --- y ---) no es YAML válido: {e}")
    if datos is None:
        datos = {}
    if not isinstance(datos, dict):
        return {}, md
    return datos, "\n".join(lineas[fin + 1:])


def formato_strftime(fmt):
    tabla = {"AAAA": "%Y", "YYYY": "%Y", "AA": "%y", "YY": "%y", "DD": "%d", "MM": "%m"}
    return re.sub(r"AAAA|YYYY|AA|YY|DD|MM", lambda m: tabla[m.group(0)], str(fmt or "DD-MM-AAAA"))


def texto_fecha(valor, fmt):
    """Fecha (objeto de YAML o texto AAAA-MM-DD) con el formato de fecha del proyecto; otro valor, tal cual."""
    if isinstance(valor, datetime.datetime):
        valor = valor.date()
    if isinstance(valor, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", valor.strip()):
        try:
            valor = datetime.date.fromisoformat(valor.strip())
        except ValueError:
            pass
    if isinstance(valor, datetime.date):
        return valor.strftime(formato_strftime(fmt))
    return str(valor)


def armar_marcadores(front, cfg, aut):
    """Marcadores de texto: valores por defecto del proyecto, completados y pisados por el bloque inicial."""
    fmt = (cfg.get("formato") or {}).get("formato_fecha")
    proy = cfg.get("proyecto") or {}
    marcas = {}
    for clave, valor in (("proyecto", proy.get("nombre")), ("cliente", proy.get("cliente")), ("autor", aut.get("nombre"))):
        valor = str(valor or "").strip()
        if valor and "PENDIENTE" not in valor.upper():
            marcas[clave] = valor
    marcas["fecha"] = texto_fecha(datetime.date.today(), fmt)
    for clave, valor in front.items():
        if clave in SIN_CLAVE or valor is None or isinstance(valor, (dict, list)):
            continue
        marcas[str(clave)] = texto_fecha(valor, fmt) if clave == "fecha" or isinstance(valor, datetime.date) else str(valor)
    return marcas


def filas_de_revision(front, marcas, fmt):
    filas = []
    for rev in front.get("revisiones") or []:
        if not isinstance(rev, dict):
            continue
        filas.append({
            "rev.version": str(rev.get("version", "")),
            "rev.fecha": texto_fecha(rev["fecha"], fmt) if rev.get("fecha") not in (None, "") else "",
            "rev.descripcion": str(rev.get("descripcion", "")),
            "rev.autor": str(rev.get("autor") or marcas.get("autor", "")),
        })
    return filas


def resolver_plantilla(arg, sin_plantilla, cfg, raiz):
    """Ruta de la plantilla Word a usar, o None para el modo por defecto."""
    if sin_plantilla:
        return None
    if arg:
        ruta = Path(arg)
        if not ruta.is_file():
            sys.exit(f"No existe la plantilla {arg}.")
        return ruta
    valor = str((cfg.get("formato") or {}).get("plantilla_word") or "").strip()
    if not valor or "PENDIENTE" in valor.upper():
        return None
    ruta = Path(valor)
    if ruta.is_absolute():
        candidatas = [ruta]
    else:
        emp = (cfg.get("_empresa") or {}).get("raiz") or (_config.raiz_empresa(raiz) if raiz else None)
        prog = (cfg.get("_programa") or {}).get("raiz")
        candidatas = [Path(base) / valor for base in (raiz, emp, prog) if base]
    for c in candidatas:
        if c.is_file():
            return c
    sys.exit(f"formato.plantilla_word apunta a «{valor}», que no existe (se buscó en: "
             + ", ".join(str(c.parent) for c in candidatas) + ").")


# Reemplazo de marcadores. Opera sobre el XML para alcanzar también tablas anidadas, encabezados, pies y cuadros
# de texto, y solo toca los fragmentos de texto puro: un fragmento con imagen, campo o tabulación no se modifica
# (el logo que comparte párrafo con un marcador no se pierde).
def _grupos_de_runs(p):
    grupos, actual = [], []
    for r in list(p.iter(qn("w:r"))):
        if next(r.iterancestors(qn("w:p")), None) is not p:
            continue
        if all(h.tag in (qn("w:rPr"), qn("w:t")) for h in r):
            actual.append(r)
        elif actual:
            grupos.append(actual)
            actual = []
    if actual:
        grupos.append(actual)
    return grupos


def _texto_run(r):
    return "".join(t.text or "" for t in r.findall(qn("w:t")))


def _poner_texto(r, texto):
    ts = r.findall(qn("w:t"))
    if not ts:
        t = OxmlElement("w:t")
        r.append(t)
        ts = [t]
    for extra in ts[1:]:
        r.remove(extra)
    ts[0].text = texto
    ts[0].set(qn("xml:space"), "preserve")


def reemplazar_marcadores_en(raiz, valores):
    """Reemplaza {{nombre}} por valores[nombre] en todos los párrafos bajo `raiz` (aunque Word haya partido el
    marcador en varios fragmentos). Devuelve el conjunto de nombres reemplazados."""
    hechos = set()
    for p in list(raiz.iter(qn("w:p"))):
        for grupo in _grupos_de_runs(p):
            originales = [_texto_run(r) for r in grupo]
            total = "".join(originales)
            if "{{" not in total:
                continue
            ediciones = [(m.start(), m.end(), m.group(0)[2:-2].strip()) for m in MARCA.finditer(total)
                         if m.group(0)[2:-2].strip() in valores]
            if not ediciones:
                continue
            inicios, acum = [], 0
            for t in originales:
                inicios.append(acum)
                acum += len(t)
            textos = list(originales)

            def donde(pos):
                return max(k for k in range(len(originales))
                           if originales[k] and inicios[k] <= pos < inicios[k] + len(originales[k]))

            for ini, fin, nombre in reversed(ediciones):
                nuevo = str(valores[nombre]).replace("\n", " ")
                i, j = donde(ini), donde(fin - 1)
                if i == j:
                    textos[i] = textos[i][:ini - inicios[i]] + nuevo + textos[i][fin - inicios[i]:]
                else:
                    textos[i] = textos[i][:ini - inicios[i]] + nuevo
                    for k in range(i + 1, j):
                        textos[k] = ""
                    textos[j] = textos[j][fin - inicios[j]:]
                hechos.add(nombre)
            for r, antes, despues in zip(grupo, originales, textos):
                if antes != despues:
                    _poner_texto(r, despues)
    return hechos


def raices_del_documento(doc):
    """Cuerpo, encabezados, pies y notas del documento (también los de primera página y páginas pares)."""
    raices = [doc.element]
    for rel in doc.part.rels.values():
        if rel.is_external or not rel.reltype.endswith(("/header", "/footer", "/footnotes", "/endnotes")):
            continue
        parte = rel.target_part
        el = getattr(parte, "element", None)
        if el is None:
            el = getattr(parte, "_element", None)
        if el is not None and not any(el is x for x in raices):
            raices.append(el)
    return raices


def marcadores_pendientes(doc):
    res = set()
    for raiz in raices_del_documento(doc):
        for p in raiz.iter(qn("w:p")):
            res.update(MARCA.findall("".join(t.text or "" for t in p.iter(qn("w:t")))))
    return sorted(res)


def _texto_de(el):
    return "".join(t.text or "" for t in el.iter(qn("w:t")))


def expandir_revisiones(doc, filas):
    """Repite la fila de la tabla que trae {{rev.*}} una vez por revisión (conserva su formato); sin revisiones, la quita."""
    for tr in [t for t in doc.element.iter(qn("w:tr")) if "{{rev." in _texto_de(t)]:
        for valores in filas:
            copia = copy.deepcopy(tr)
            reemplazar_marcadores_en(copia, valores)
            tr.addprevious(copia)
        tbl = tr.getparent()
        tbl.remove(tr)
        if tbl.tag == qn("w:tbl") and not tbl.findall(qn("w:tr")):
            padre = tbl.getparent()
            padre.remove(tbl)
            if padre.tag == qn("w:tc") and not padre.findall(qn("w:p")):
                padre.append(OxmlElement("w:p"))


def _run_campo(p, tipo=None, instr=None, texto=None):
    r = OxmlElement("w:r")
    if tipo:
        el = OxmlElement("w:fldChar")
        el.set(qn("w:fldCharType"), tipo)
        if tipo == "begin":
            el.set(qn("w:dirty"), "true")
    elif instr:
        el = OxmlElement("w:instrText")
        el.set(qn("xml:space"), "preserve")
        el.text = instr
    else:
        el = OxmlElement("w:t")
        el.set(qn("xml:space"), "preserve")
        el.text = texto
    r.append(el)
    p.append(r)


def poner_indice(parrafo):
    """Reemplaza el contenido del párrafo por un campo de tabla de contenido (niveles 1 a 3)."""
    p = parrafo._p
    for hijo in list(p):
        if hijo.tag != qn("w:pPr"):
            p.remove(hijo)
    _run_campo(p, tipo="begin")
    _run_campo(p, instr=' TOC \\o "1-3" \\h \\z \\u ')
    _run_campo(p, tipo="separate")
    _run_campo(p, texto="Actualiza el campo (clic derecho, «Actualizar campo») para generar el índice.")
    _run_campo(p, tipo="end")


def marcar_actualizar_campos(doc):
    ajustes = doc.settings.element
    existente = ajustes.find(qn("w:updateFields"))
    if existente is not None:
        existente.set(qn("w:val"), "true")
        return
    el = OxmlElement("w:updateFields")
    el.set(qn("w:val"), "true")
    posteriores = {qn("w:" + n) for n in SIGUEN_A_UPDATEFIELDS}
    for hijo in ajustes:
        if hijo.tag in posteriores:
            hijo.addprevious(el)
            return
    ajustes.append(el)


def buscar_estilo(doc, ids, nombres, tipo=WD_STYLE_TYPE.PARAGRAPH):
    """Estilo por su id (Heading1, ListBullet…) y, si no está, por su nombre (Word guarda los nombres en inglés
    aunque se vea en otro idioma; el id sí cambia con el idioma)."""
    estilos = [s for s in doc.styles if s.type == tipo]
    for s in estilos:
        if s.style_id in ids:
            return s
    nombres = [n.lower() for n in nombres]
    for s in estilos:
        if (s.name or "").lower() in nombres:
            return s
    return None


def estilos_de_plantilla(doc):
    titulos = {n: buscar_estilo(doc, [f"Heading{n}", f"Ttulo{n}"], [f"heading {n}", f"título {n}", f"titulo {n}"])
               for n in (1, 2, 3, 4)}
    tabla = None
    for s in doc.styles:  # estilo de tabla propio de la plantilla (los de fábrica de Word no cuentan)
        if s.type == WD_STYLE_TYPE.TABLE and s.element.get(qn("w:customStyle")) in ("1", "true", "on"):
            tabla = s
            break
    return {
        "titulos": titulos,
        "vineta": buscar_estilo(doc, ["ListBullet", "Listaconvietas"], ["list bullet", "lista con viñetas"]),
        "numero": buscar_estilo(doc, ["ListNumber", "Listaconnmeros"], ["list number", "lista con números"]),
        "leyenda": buscar_estilo(doc, ["Caption", "Epgrafe"], ["caption", "leyenda", "epígrafe"]),
        "tabla": tabla,
    }


def agregar_tabla_con_estilo(doc, filas, estilo):
    tabla = doc.add_table(rows=1, cols=len(filas[0]))
    tabla.style = estilo
    for j, texto in enumerate(filas[0]):
        agregar_inline(tabla.rows[0].cells[j].paragraphs[0], texto)
    for fila in filas[1:]:
        celdas = tabla.add_row().cells
        for j in range(len(filas[0])):
            texto = fila[j] if j < len(fila) else ""
            agregar_inline(celdas[j].paragraphs[0], texto)
            clave = re.sub(r"[^a-záéíóú]", "", texto.lower())
            if clave in SEMAFORO:
                sombrear(celdas[j], SEMAFORO[clave])
    doc.add_paragraph()


def ancho_util(doc):
    sec = doc.sections[-1]
    try:
        return int(sec.page_width - sec.left_margin - sec.right_margin)
    except TypeError:
        return int(Cm(16))


def convertir_con_plantilla(md, doc, est, color_hex, dir_md):
    """Agrega el cuerpo al final del documento usando los estilos de la plantilla."""
    lineas = md.splitlines()
    i, n_figura, n_lista = 0, 0, 0
    tam = {1: 16, 2: 13, 3: 11.5, 4: 11}

    def parrafo(estilo=None):
        p = doc.add_paragraph()
        if estilo is not None:
            p.style = estilo
        return p

    while i < len(lineas):
        linea = lineas[i].rstrip()
        if not linea.strip() or linea.strip().startswith("<!--"):
            i += 1
            continue
        num_item = re.match(r"^\s*\d+[.)]\s+(.*)", linea)
        if not num_item:
            n_lista = 0
        m = re.match(r"^(#{1,4})\s+(.*)", linea)
        if m:
            nivel, texto = len(m.group(1)), m.group(2).strip()
            estilo = est["titulos"].get(nivel) or est["titulos"].get(3)
            p = parrafo(estilo)
            r = p.add_run(texto)
            if estilo is None:
                r.bold = True
                r.font.size = Pt(tam[nivel])
            if nivel == 1 and RE_ANEXOS.match(texto):
                p.paragraph_format.page_break_before = True
            i += 1
            continue
        m = RE_IMAGEN.match(linea.strip())
        if m:
            n_figura += 1
            p = parrafo()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.keep_with_next = True
            forma = p.add_run().add_picture(str(dir_md / m.group(2).strip()))
            maximo = ancho_util(doc)
            if forma.width > maximo:
                forma.height = int(forma.height * maximo / forma.width)
                forma.width = maximo
            pie = parrafo(est["leyenda"])
            if est["leyenda"] is None:
                pie.alignment = WD_ALIGN_PARAGRAPH.CENTER
            agregar_inline(pie, f"Figura {n_figura}. {m.group(1).strip()}".rstrip(), negrita_base=est["leyenda"] is None)
            i += 1
            continue
        if linea.strip().startswith("|"):
            bloque = []
            while i < len(lineas) and lineas[i].strip().startswith("|"):
                if not re.fullmatch(r"\|?[\s:\-|]+\|?", lineas[i].strip()):
                    bloque.append(dividir_fila(lineas[i]))
                i += 1
            if bloque:
                if est["tabla"] is not None:
                    agregar_tabla_con_estilo(doc, bloque, est["tabla"])
                else:
                    agregar_tabla(doc, bloque, color_hex)
            continue
        m = re.match(r"^\s*[-*]\s+(.*)", linea)
        if m:
            p = parrafo(est["vineta"])
            if est["vineta"] is None:
                p.paragraph_format.left_indent = Cm(0.9)
                p.paragraph_format.first_line_indent = Cm(-0.5)
                agregar_inline(p, "• " + m.group(1))
            else:
                agregar_inline(p, m.group(1))
            i += 1
            continue
        if num_item:
            n_lista += 1
            p = parrafo(est["numero"])
            if est["numero"] is None:
                p.paragraph_format.left_indent = Cm(0.9)
                p.paragraph_format.first_line_indent = Cm(-0.6)
                agregar_inline(p, f"{n_lista}. " + num_item.group(1))
            else:
                agregar_inline(p, num_item.group(1))
            i += 1
            continue
        if linea.strip().startswith(">"):
            p = parrafo()
            agregar_inline(p, linea.strip().lstrip(">").strip())
            for run in p.runs:
                run.italic = True
            i += 1
            continue
        texto = [linea.strip()]
        i += 1
        while i < len(lineas) and lineas[i].strip() and not re.match(r"^(#|\||!\[|\s*[-*]\s|\s*\d+[.)]\s|>)", lineas[i]):
            texto.append(lineas[i].strip())
            i += 1
        agregar_inline(parrafo(), " ".join(texto))


def generar_con_plantilla(args, front, cuerpo, cfg, raiz, plantilla):
    """Convierte `cuerpo` dentro de la plantilla Word. Devuelve el código de salida."""
    salida = Path(args.salida)
    if salida.resolve() == plantilla.resolve():
        sys.exit("La salida no puede ser la misma plantilla: se conserva intacta.")
    dir_md = Path(args.entrada).resolve().parent
    faltan = [m.group(2).strip() for m in (RE_IMAGEN.match(l.strip()) for l in cuerpo.splitlines())
              if m and not (dir_md / m.group(2).strip()).is_file()]
    if faltan:
        sys.exit("No existe la imagen: " + ", ".join(faltan) + f" (se busca junto a {args.entrada}).")
    try:
        doc = Document(str(plantilla))
    except Exception as e:
        sys.exit(f"No se pudo abrir la plantilla {plantilla}: {e}")

    aut = autoria.cargar_autoria(raiz)
    fmt_fecha = (cfg.get("formato") or {}).get("formato_fecha")
    marcas = armar_marcadores(front, cfg, aut)
    expandir_revisiones(doc, filas_de_revision(front, marcas, fmt_fecha))
    for raiz_xml in raices_del_documento(doc):
        reemplazar_marcadores_en(raiz_xml, marcas)

    indices = [Paragraph(p, None) for p in doc.element.iter(qn("w:p")) if _texto_de(p).strip() == "{{indice}}"]
    for p in indices:
        poner_indice(p)
    if indices:
        marcar_actualizar_campos(doc)

    body = doc.element.body
    ancla = next((p._p for p in doc.paragraphs if p.text.strip() == "{{contenido}}"), None)
    previos = list(body)
    color_hex = rgb((cfg.get("formato") or {}).get("color_primario"))[1]
    convertir_con_plantilla(cuerpo, doc, estilos_de_plantilla(doc), color_hex, dir_md)
    if ancla is not None:
        ids = {id(e) for e in previos}
        for el in [e for e in body if id(e) not in ids and e.tag != qn("w:sectPr")]:
            ancla.addprevious(el)
        body.remove(ancla)

    restantes = marcadores_pendientes(doc)
    salida.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(salida))
    titulo = str(front.get("titulo") or "") or next((m.group(1).strip() for m in re.finditer(r"^#\s+(.+)$", cuerpo, re.M)), "")
    autoria.limpiar_ooxml(salida, aut.get("nombre", ""), titulo, aut.get("organizacion", ""))
    print(f"Documento generado: {salida} (plantilla {plantilla.name})")
    if ancla is None:
        print("- La plantilla no trae {{contenido}}: el cuerpo se agregó al final.")
    if restantes:
        print("- Marcadores de la plantilla sin valor: " + ", ".join(restantes))
        print("  Defínelos en el bloque inicial del Markdown o quítalos de la plantilla.")
        return 0 if args.borrador else 1
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("entrada")
    p.add_argument("salida")
    p.add_argument("--proyecto", help="carpeta del proyecto (para marca, formato y autoría)")
    p.add_argument("--borrador", action="store_true", help="permitir marcadores [PENDIENTE] (documento interno)")
    p.add_argument("--plantilla", help="plantilla Word de la empresa (.docx) donde se arma el documento largo")
    p.add_argument("--sin-plantilla", action="store_true", help="ignora formato.plantilla_word y usa el formato por defecto")
    args = p.parse_args()

    md = Path(args.entrada).read_text(encoding="utf-8")
    md = autoria.normalizar_texto(re.sub(r"<!--.*?-->", "", md, flags=re.S))
    pendientes = [n for n, linea in enumerate(md.splitlines(), 1) if "[PENDIENTE" in linea.upper()]
    if pendientes and not args.borrador:
        sys.exit(f"El texto tiene {len(pendientes)} marcador(es) [PENDIENTE] (líneas {', '.join(map(str, pendientes[:10]))}). "
                 "Complétalos antes de emitir, o usa --borrador para un documento interno.")

    cfg, raiz = cargar_cfg(args.proyecto)
    front, md = separar_frontmatter(md)  # el bloque inicial solo sirve con plantilla; si no, se ignora
    plantilla = resolver_plantilla(args.plantilla, args.sin_plantilla, cfg, raiz)
    if plantilla is not None:
        return generar_con_plantilla(args, front, md, cfg, raiz, plantilla)
    doc = Document()
    color, fmt = configurar(doc, cfg, raiz)
    _, color_hex = rgb(fmt.get("color_primario"))
    convertir(md, doc, color, color_hex)
    Path(args.salida).parent.mkdir(parents=True, exist_ok=True)
    doc.save(args.salida)
    aut = autoria.cargar_autoria(raiz)
    titulo = next((m.group(1).strip() for m in re.finditer(r"^#\s+(.+)$", md, re.M)), "")
    autoria.limpiar_ooxml(args.salida, aut.get("nombre", ""), titulo, aut.get("organizacion", ""))
    print(f"Documento generado: {args.salida}")


if __name__ == "__main__":
    import _consola
    _consola.preparar()
    sys.exit(main())
