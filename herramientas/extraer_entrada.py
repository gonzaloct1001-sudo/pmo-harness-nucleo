#!/usr/bin/env python3
"""Inventario y extracción de texto de la carpeta _entrada de un proyecto.

Uso:
    python herramientas/extraer_entrada.py proyectos/<slug> [--max-filas 200]

Recorre proyectos/<slug>/_entrada (o la carpeta indicada con --origen, por ejemplo postulaciones),
excepto _procesado y _archivo, y para cada archivo:
- lo convierte a texto Markdown en _entrada/_procesado/texto/ (PDF, Word, Excel, PowerPoint,
  correos .eml, texto, CSV, JSON, exportaciones de ChatGPT y Claude);
- extrae las imágenes de encabezados de Word/PowerPoint (candidatas a logo) a _procesado/imagenes/;
- sugiere una categoría según el nombre y el contenido;
- detecta duplicados por hash;
- si la categoría está en `replicas.completas` (de proyecto.yaml o empresa/empresa.yaml: por defecto bases, contratos,
  lineamientos, actas e informes), deja una réplica fiel en fuentes/<id>-<nombre>.md, que sí se sube al repositorio
  privado y permite trabajar en otro computador sin los originales. CVs y estados financieros nunca se replican (solo
  ficha); lo que no calza con la política queda «por decidir» en el alta (`--replicar <id>` lo replica después).
Genera _procesado/inventario.md y _procesado/inventario.csv.

Es incremental: los archivos ya inventariados (mismo hash) no se vuelven a procesar,
así se puede ejecutar de nuevo cuando se agrega material.

Con --archivar (al cerrar el alta o el procesamiento de material nuevo) mueve los archivos ya procesados a
_archivo/AAAA-MM-DD/<subcarpeta de origen>/ y deja intactas las subcarpetas de carga (01-, 02-, ...).
"""
import argparse
import csv
import email
import hashlib
import json
import re
import shutil
import sys
import zipfile
from datetime import datetime
from email import policy
from pathlib import Path

# Se reconocen solo por el nombre del archivo (su vocabulario aparece en cualquier documento) y antes que la carpeta de
# bases: la normativa general y las charlas no son requisitos de la convocatoria; el formulario es la estructura a llenar.
POR_NOMBRE = [
    ("normativa", r"(?<![a-záéíóúñ])(ley\s*(n[°º.]?\s*)?\d|decreto|d\.?f\.?l\.?\s*\d|reglamento)"),
    ("charla", r"charla|capacitaci[oó]n|webinar|taller|transcripci[oó]n|grabaci[oó]n"),
    ("formulario", r"formulario(?!\s*22)|(?<![a-z])form\s?\d|formato vac[ií]o|ficha de postulaci"),
]
CATEGORIAS = [
    ("bases", r"\bbases\b|convocatoria|llamado a (concurso|licitaci)|t[eé]rminos de referencia|\brfp\b|aclaraci[oó]n|"
              r"foro de (preguntas|consultas)|preguntas y respuestas|pauta de evaluaci"),
    ("contrato", r"contrato|convenio|anexo|enmienda|adenda|addendum|orden de compra|\boc\b|bases de licitaci|t[eé]rminos de referencia"),
    ("propuesta", r"propuesta|cotizaci|oferta t[eé]cnica|oferta econ[oó]mica|reevaluaci"),
    ("lineamientos", r"lineamiento|directrices|acuerdos? (de|del) directorio|sesi[oó]n (de|del) directorio|instrucci[oó]n del directorio|"
                     r"pol[ií]tica (corporativa|interna|de la empresa)|definiciones estrat[eé]gicas|plan estrat[eé]gico|orientaciones estrat[eé]gicas"),
    ("cv", r"\bcv\b|curr[ií]cul|hoja de vida"),
    ("financiero", r"estados? financieros?|balance general|estado de resultados|\beeff\b|carpeta tributaria|"
                   r"declaraci[oó]n (anual )?de renta|formulario 22"),
    ("certificado", r"\bcertificado\b|\bcertificaci[oó]n\b"),
    ("cronograma", r"gantt|cronograma|carta gantt|planificaci|schedule|project plan|\.mpp|ms project|cronograma de ms project"),
    ("planilla-control", r"planilla de (control|estado|seguimiento)|estado del (programa|proyecto)|control de gesti"),
    ("plantilla", r"plantilla|template|formato"),
    ("minuta", r"minuta|acta|reuni[oó]n|meeting"),
    ("correo", r"\.eml$|asunto:|subject:|de:.*para:"),
    ("chat-ia", r"conversations\.json|chatgpt|gemini|copilot"),
    ("reporte", r"reporte|informe|estado de avance|status|avance semanal|avance mensual|presentaci|comit[eé]"),
    ("marca", r"logo|marca|brand|manual de identidad|colores corporativos"),
    ("riesgos", r"riesgo|risk|matriz"),
    ("organigrama", r"organigrama|contactos|stakeholder|directorio"),
]
SENSIBLES = ("cv", "financiero")  # datos personales o reservados: por defecto nunca se replican
# «CV» también es la sigla de instrumentos (CORFO Crea y Valida): sola, indica un currículum solo si hay datos personales
CV_FUERTE = r"curr[ií]cul|hoja de vida"
DATOS_PERSONALES = (r"fecha de nacimiento", r"estado civil", r"nacionalidad", r"experiencia (laboral|profesional)",
                    r"formaci[oó]n acad[eé]mica", r"antecedentes acad[eé]micos", r"t[ií]tulo profesional", r"\bedad\b")


def parece_cv(contenido):
    return sum(bool(re.search(p, contenido)) for p in DATOS_PERSONALES) >= 2
REPLICAS_POR_DEFECTO = {"completas": ["bases", "formulario", "normativa", "charla", "contrato", "lineamientos", "minuta", "reporte"],
                        "solo_ficha": ["cv", "financiero", "certificado", "correo", "chat-ia"]}
EXT_TEXTO = {".txt", ".md", ".csv", ".tsv", ".log"}
EXT_IMAGEN = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg"}


def sha(ruta):
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()[:16]


def categorizar(rel, texto):
    """Primero el nombre del archivo; si no basta, el contenido (por puntaje); al final la subcarpeta."""
    partes = Path(rel).parts
    nombre = partes[-1].lower().replace("_", " ")
    carpeta = " ".join(partes[:-1]).lower().replace("-", " ")
    for cat, patron in POR_NOMBRE:
        if re.search(patron, nombre):
            return cat
    if Path(rel).suffix.lower() in EXT_IMAGEN and re.search(dict(POR_NOMBRE)["charla"] + r"|video", carpeta):
        return "charla"  # capturas de una charla o de su video
    if re.search(r"\bbases\b", carpeta):  # la carpeta de bases (postulaciones) es una indicación explícita del usuario
        return "bases"
    contenido = (texto or "")[:5000].lower()
    inicio = contenido[:400]
    cv_dudoso = bool(texto) and not parece_cv(contenido)  # sin texto que leer, un nombre con «CV» se trata como currículum
    for cat, patron in CATEGORIAS:
        if cat == "cv" and cv_dudoso:
            patron = CV_FUERTE
        if re.search(patron, nombre):
            return cat
    for cat in SENSIBLES:  # un CV o un estado financiero se reconoce por su encabezado aunque el resto parezca un informe
        patron = CV_FUERTE if cat == "cv" and cv_dudoso else dict(CATEGORIAS)[cat]
        if re.search(patron, inicio):
            return cat
    puntajes = {}
    es_planilla = Path(rel).suffix.lower() in (".xlsx", ".xlsm", ".xls", ".csv", ".tsv")
    no_planilla = {"bases", "contrato", "correo", "chat-ia", "minuta", "marca"}  # una planilla propia no son bases
    for cat, patron in CATEGORIAS:
        if es_planilla and cat in no_planilla:
            continue
        if cat == "cv" and cv_dudoso:
            patron = CV_FUERTE
        pts = len(re.findall(patron, contenido)) + 2 * len(re.findall(patron, inicio))
        if pts:
            puntajes[cat] = pts
    if puntajes:
        return max(puntajes, key=lambda c: (puntajes[c], -[x for x, _ in CATEGORIAS].index(c)))
    for cat, patron in CATEGORIAS:
        if re.search(patron, carpeta):
            return cat
    return "otro"


# ------------------------- extractores -------------------------

def ext_pdf(ruta, _):
    from pypdf import PdfReader
    r = PdfReader(str(ruta))
    partes = []
    for i, p in enumerate(r.pages, 1):
        t = (p.extract_text() or "").strip()
        partes.append(f"\n\n--- Página {i} ---\n\n{t}")
    texto = "".join(partes)
    info = f"{len(r.pages)} pág."
    if len(re.sub(r"\s|---|Página \d+", "", texto)) < 50 * max(len(r.pages), 1) / 4:
        info += " · POSIBLE ESCANEO (poco texto)"
    return texto, info


def ext_docx(ruta, carpeta_img):
    from docx import Document
    d = Document(str(ruta))
    out = []
    for p in d.paragraphs:
        t = p.text.strip()
        if not t:
            continue
        estilo = (p.style.name or "").lower()
        if estilo.startswith("heading") or estilo.startswith("título"):
            nivel = re.findall(r"\d", estilo)
            out.append("#" * int(nivel[0] if nivel else 2) + " " + t)
        else:
            out.append(t)
    for ti, tabla in enumerate(d.tables, 1):
        out.append(f"\n**Tabla {ti}**\n")
        for fi, fila in enumerate(tabla.rows):
            celdas = [c.text.strip().replace("\n", " ").replace("|", "/") for c in fila.cells]
            out.append("| " + " | ".join(celdas) + " |")
            if fi == 0:
                out.append("|" + "---|" * len(celdas))
    enc = []
    for s in d.sections:
        for p in s.header.paragraphs:
            if p.text.strip():
                enc.append(p.text.strip())
    if enc:
        out.insert(0, "Encabezado: " + " / ".join(dict.fromkeys(enc)))
    marcadores = sorted(set(re.findall(r"\{\{[^}]+\}\}", "\n".join(out))))
    if marcadores:
        out.append("\nMarcadores encontrados: " + ", ".join(marcadores))
    n_img = extraer_imagenes_zip(ruta, carpeta_img, ("word/media/",))
    return "\n".join(out), f"{len(d.paragraphs)} párrafos, {len(d.tables)} tablas, {n_img} imágenes"


def ext_xlsx(ruta, _, max_filas=200):
    from openpyxl import load_workbook
    wb = load_workbook(str(ruta), data_only=True, read_only=True)
    wb_f = load_workbook(str(ruta), read_only=True)
    out, hojas = [], []
    for ws in wb.worksheets:
        hojas.append(ws.title)
        n_form = 0
        try:
            for fila in wb_f[ws.title].iter_rows():
                n_form += sum(1 for c in fila if isinstance(c.value, str) and c.value.startswith("="))
        except Exception:
            pass
        out.append(f"\n## Hoja: {ws.title} (fórmulas: {n_form})\n")
        filas = 0
        for fila in ws.iter_rows(values_only=True):
            if all(v is None for v in fila):
                continue
            vals = ["" if v is None else (v.strftime("%Y-%m-%d") if hasattr(v, "strftime") else str(v)) for v in fila]
            while vals and vals[-1] == "":
                vals.pop()
            out.append("| " + " | ".join(x.replace("|", "/").replace("\n", " ") for x in vals) + " |")
            filas += 1
            if filas >= max_filas:
                out.append(f"… (truncado en {max_filas} filas)")
                break
    return "\n".join(out), f"{len(hojas)} hojas: {', '.join(hojas)}"


def ext_pptx(ruta, carpeta_img):
    from pptx import Presentation
    prs = Presentation(str(ruta))
    out = []
    for i, s in enumerate(prs.slides, 1):
        out.append(f"\n## Diapositiva {i} (layout: {s.slide_layout.name})")
        for sh in s.shapes:
            if sh.has_text_frame and sh.text_frame.text.strip():
                out.append(sh.text_frame.text.strip())
            if getattr(sh, "has_table", False) and sh.has_table:
                for fila in sh.table.rows:
                    out.append("| " + " | ".join(c.text.strip() for c in fila.cells) + " |")
    layouts = [l.name for l in prs.slide_layouts]
    out.insert(0, "Layouts disponibles: " + ", ".join(layouts))
    n_img = extraer_imagenes_zip(ruta, carpeta_img, ("ppt/media/",))
    return "\n".join(out), f"{len(prs.slides)} diapositivas, {n_img} imágenes"


def ext_eml(ruta, _):
    with open(ruta, "rb") as f:
        msg = email.message_from_binary_file(f, policy=policy.default)
    cab = [f"**{k}:** {msg.get(k, '')}" for k in ("From", "To", "Cc", "Date", "Subject")]
    cuerpo = msg.get_body(preferencelist=("plain", "html"))
    texto = cuerpo.get_content() if cuerpo else ""
    if cuerpo is not None and cuerpo.get_content_type() == "text/html":
        texto = re.sub(r"<[^>]+>", " ", texto)
    adjuntos = [p.get_filename() for p in msg.iter_attachments() if p.get_filename()]
    if adjuntos:
        cab.append("**Adjuntos:** " + ", ".join(adjuntos))
    return "\n".join(cab) + "\n\n" + re.sub(r"\n{3,}", "\n\n", texto), f"correo de {msg.get('From', '?')}"


def ext_xml(ruta, _):
    """XML de MS Project (Guardar como > XML): tabla de tareas legible. Otro XML: texto plano."""
    import importar_msproject as msp
    if msp.es_mspdi(ruta):
        texto = msp.resumen_texto(ruta)
        n = texto.count("\n| T")
        return texto, f"cronograma de MS Project (XML): {n} tareas · importar con importar_msproject.py"
    return Path(ruta).read_text(encoding="utf-8", errors="replace")[:200000], "XML"


def ext_json(ruta, _):
    datos = json.loads(Path(ruta).read_text(encoding="utf-8", errors="replace"))
    # Exportación de ChatGPT: lista con "mapping"
    if isinstance(datos, list) and datos and isinstance(datos[0], dict) and "mapping" in datos[0]:
        return chats_chatgpt(datos), f"exportación ChatGPT: {len(datos)} conversaciones"
    # Exportación de Claude: lista con "chat_messages"
    if isinstance(datos, list) and datos and isinstance(datos[0], dict) and "chat_messages" in datos[0]:
        return chats_claude(datos), f"exportación Claude: {len(datos)} conversaciones"
    return json.dumps(datos, ensure_ascii=False, indent=1)[:200000], "JSON"


def chats_chatgpt(conv):
    out = []
    for c in conv:
        out.append(f"\n\n# Conversación: {c.get('title') or 'sin título'}")
        if c.get("create_time"):
            out.append(f"Fecha: {datetime.fromtimestamp(c['create_time']).strftime('%Y-%m-%d')}")
        nodos = [n for n in (c.get("mapping") or {}).values() if n.get("message")]
        nodos.sort(key=lambda n: n["message"].get("create_time") or 0)
        for n in nodos:
            m = n["message"]
            rol = (m.get("author") or {}).get("role", "")
            if rol not in ("user", "assistant"):
                continue
            partes = (m.get("content") or {}).get("parts") or []
            texto = "\n".join(p for p in partes if isinstance(p, str)).strip()
            if texto:
                out.append(f"\n**{'Usuario' if rol == 'user' else 'IA'}:** {texto}")
    return "\n".join(out)


def chats_claude(conv):
    out = []
    for c in conv:
        out.append(f"\n\n# Conversación: {c.get('name') or 'sin título'}")
        if c.get("created_at"):
            out.append(f"Fecha: {str(c['created_at'])[:10]}")
        for m in c.get("chat_messages") or []:
            texto = (m.get("text") or "").strip()
            if not texto and isinstance(m.get("content"), list):
                texto = "\n".join(x.get("text", "") for x in m["content"] if isinstance(x, dict)).strip()
            if texto:
                out.append(f"\n**{'Usuario' if m.get('sender') == 'human' else 'IA'}:** {texto}")
    return "\n".join(out)


def ext_texto(ruta, _):
    return Path(ruta).read_text(encoding="utf-8", errors="replace"), "texto"


def extraer_imagenes_zip(ruta, carpeta_img, prefijos):
    n = 0
    try:
        with zipfile.ZipFile(ruta) as z:
            for nombre in z.namelist():
                if nombre.startswith(prefijos) and Path(nombre).suffix.lower() in EXT_IMAGEN | {".emf", ".wmf"}:
                    destino = carpeta_img / f"{Path(ruta).stem}__{Path(nombre).name}"
                    destino.write_bytes(z.read(nombre))
                    n += 1
    except zipfile.BadZipFile:
        pass
    return n


EXTRACTORES = {".xml": ext_xml, ".pdf": ext_pdf, ".docx": ext_docx, ".docm": ext_docx, ".xlsx": ext_xlsx, ".xlsm": ext_xlsx,
               ".pptx": ext_pptx, ".eml": ext_eml, ".json": ext_json}


def politica_replicas(proyecto: Path):
    """Bloque `replicas` del proyecto o, si no lo define, de empresa/empresa.yaml; si no hay, el valor por defecto."""
    try:
        import _config
        pol = _config.cargar(proyecto).get("replicas") or {}
    except Exception:
        pol = {}
    return {"completas": list(pol.get("completas") or REPLICAS_POR_DEFECTO["completas"]),
            "solo_ficha": list(pol.get("solo_ficha") or REPLICAS_POR_DEFECTO["solo_ficha"])}


def destino_replica(politica, categoria):
    """'replicar', 'solo_ficha' o 'por_decidir'. Lo sensible nunca se replica, aunque la política lo pida."""
    if categoria in SENSIBLES or categoria in politica["solo_ficha"]:
        return "solo_ficha"
    return "replicar" if categoria in politica["completas"] else "por_decidir"


def escribir_replica(proyecto: Path, fila, texto, origen):
    """Réplica fiel en fuentes/<id>-<nombre>.md (se sube al repositorio privado). Devuelve su ruta relativa."""
    nombre = re.sub(r"[^\w.-]", "_", Path(fila["archivo"]).stem)[:60]
    ruta = proyecto / "fuentes" / f"{fila['id']}-{nombre}.md"
    ruta.parent.mkdir(parents=True, exist_ok=True)
    palabras = len(texto.split())
    calidad = "sin_texto" if palabras < 20 else ("parcial" if "ESCANEO" in fila["detalle"] else "completa")
    paginas = re.search(r"(\d+) pág\.", fila["detalle"])
    ruta.write_text(
        "---\n"
        f"id: {fila['id']}\n"
        f"titulo: \"{Path(fila['archivo']).name}\"\n"
        f"archivo_original: \"{origen}/{fila['archivo']}\"\n"
        f"huella: {fila['hash']}\n"
        f"categoria: {fila['categoria_sugerida']}\n"
        f"fecha_extraccion: {datetime.now():%Y-%m-%d}\n"
        f"paginas: {paginas.group(1) if paginas else ''}\n"
        f"calidad: {calidad}              # completa | parcial (posible escaneo) | sin_texto\n"
        + ("ocr: pendiente               # es un escaneo: pásalo por OCR y deja el resultado en _entrada/ (ver inventario)\n"
           if "ESCANEO" in fila["detalle"] else "")
        + "confidencialidad: interna\n"
        "original: \"\"                  # enlace a la carpeta oficial del documento (Drive, OneDrive, SharePoint), si existe\n"
        "---\n"
        "<!-- Réplica fiel del texto del documento original, para trabajar en cualquier computador sin él. Ante dudas de\n"
        "     interpretación, firmas, formularios oficiales o elementos gráficos, prevalece el original. -->\n"
        f"# {Path(fila['archivo']).name}\n\n{texto}\n", encoding="utf-8")
    return ruta.relative_to(proyecto).as_posix()


OCR_INSTRUCCION = ("pásalo por OCR: ábrelo en Word (Archivo → Abrir: lo convierte en texto editable) y guárdalo como .docx, "
                   "o en Google Drive (clic derecho → Abrir con → Documentos de Google); deja el resultado con el mismo nombre en "
                   "la misma carpeta o en una subcarpeta ocr/ y vuelve a procesar la entrada")


def emparejar_ocr(proyecto: Path, entrada: Path, filas, politica):
    """Un mismo documento en dos versiones (un escaneo y su OCR, o el original y una copia «ocr/»): queda una sola
    réplica, la de la versión con más texto. Se reconocen por el nombre, en la misma carpeta o en una subcarpeta ocr/."""
    def clave(f):
        partes = [p for p in Path(f["archivo"]).parts[:-1] if p.lower() != "ocr"]
        nombre = re.sub(r"(^|[-_ .])ocr($|[-_ .])", " ", Path(f["archivo"]).stem.lower())
        return "/".join(partes).lower(), re.sub(r"[^a-z0-9]", "", nombre)

    grupos = {}
    for f in filas:
        if f["estado"] == "extraido" and f.get("texto"):
            grupos.setdefault(clave(f), []).append(f)
    for grupo in grupos.values():
        if len(grupo) < 2 or not any("ocr" in f["archivo"].lower() or "ESCANEO" in f["detalle"] for f in grupo):
            continue
        principal = max(grupo, key=lambda f: int(f["palabras"] or 0))
        otros = [f for f in grupo if f is not principal]
        replicar = any((f.get("replica") or "").startswith("fuentes/") for f in grupo)
        for f in otros:
            if (f.get("replica") or "").startswith("fuentes/"):
                (proyecto / f["replica"]).unlink(missing_ok=True)
            f["replica"] = f"version de {principal['id']}"
            if "otra versión de" not in f["detalle"]:
                f["detalle"] += f" · otra versión de {principal['id']} (se usa la de más texto)"
        if replicar and not (principal.get("replica") or "").startswith("fuentes/") \
                and destino_replica(politica, principal["categoria_sugerida"]) != "solo_ficha":
            cuerpo = (entrada / principal["texto"]).read_text(encoding="utf-8").split("\n\n", 1)[-1]
            principal["replica"] = escribir_replica(proyecto, principal, cuerpo, entrada.name)
        if "versión preferida" not in principal["detalle"]:
            principal["detalle"] += f" · versión preferida (también: {', '.join(f['id'] for f in otros)})"


def archivar(entrada: Path, fecha: str) -> int:
    """Mueve a _archivo/<fecha>/ los archivos de carga ya inventariados, conservando su subcarpeta."""
    inv = entrada / "_procesado" / "inventario.csv"
    if not inv.exists():
        sys.exit("No hay inventario: ejecuta primero extraer_entrada.py sin --archivar.")
    with open(inv, encoding="utf-8", newline="") as f:
        inventariados = {r["archivo"].replace("\\", "/") for r in csv.DictReader(f)}
    destino_base = entrada / "_archivo" / fecha
    movidos = 0
    for ruta in sorted(p for p in entrada.rglob("*") if p.is_file()):
        if "_procesado" in ruta.parts or "_archivo" in ruta.parts or ruta.name in ("LEEME.md", ".gitkeep") \
                or ruta.name.startswith("_LEEME"):
            continue
        rel = ruta.relative_to(entrada).as_posix()
        if rel not in inventariados:
            print(f"- sin procesar, no se archiva: {rel}")
            continue
        destino = destino_base / rel
        destino.parent.mkdir(parents=True, exist_ok=True)
        if destino.exists():
            destino = destino.with_name(f"{destino.stem}_{datetime.now():%H%M%S}{destino.suffix}")
        shutil.move(str(ruta), str(destino))
        movidos += 1
    return movidos


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("proyecto")
    ap.add_argument("--max-filas", type=int, default=200, help="filas máximas por hoja de Excel")
    ap.add_argument("--origen", default="_entrada", help="carpeta a procesar, relativa al proyecto (por defecto _entrada)")
    ap.add_argument("--archivar", action="store_true", help="mover lo ya procesado a _archivo/AAAA-MM-DD/ y terminar")
    ap.add_argument("--replicar", nargs="+", metavar="ID", help="crear la réplica en fuentes/ de estos documentos ya inventariados "
                    "(decisión del alta para los que quedaron «por decidir»)")
    a = ap.parse_args()

    entrada_visible = Path(a.proyecto) / a.origen
    if not entrada_visible.exists():
        sys.exit(f"No existe {entrada_visible}")
    # Windows: con rutas de más de 260 caracteres un archivo se saltaría en silencio; el prefijo \\?\ lo evita
    from _nucleo import ruta_larga
    entrada = ruta_larga(entrada_visible)
    if a.archivar:
        fecha = datetime.now().strftime("%Y-%m-%d")
        n = archivar(entrada, fecha)
        print(f"Archivados: {n} archivo(s) en {a.origen}/_archivo/{fecha}/ (las subcarpetas de carga se conservan).")
        return
    proc = entrada / "_procesado"
    (proc / "texto").mkdir(parents=True, exist_ok=True)
    (proc / "imagenes").mkdir(parents=True, exist_ok=True)
    inv_csv = proc / "inventario.csv"
    campos = ["id", "archivo", "hash", "extension", "kb", "modificado", "categoria_sugerida", "detalle",
              "palabras", "texto", "estado", "duplicado_de", "replica"]
    previos = []
    if inv_csv.exists():
        with open(inv_csv, encoding="utf-8", newline="") as f:
            previos = list(csv.DictReader(f))
    for p in previos:  # inventarios antiguos generados en Windows guardaban rutas con \
        p["archivo"] = p["archivo"].replace("\\", "/")
        p["texto"] = (p.get("texto") or "").replace("\\", "/")
        p.setdefault("replica", "")
    proyecto = ruta_larga(Path(a.proyecto))
    politica = politica_replicas(proyecto)
    if a.replicar:
        hechas = []
        for p in previos:
            if p["id"] in a.replicar and p.get("texto") and (entrada / p["texto"]).exists():
                cuerpo = (entrada / p["texto"]).read_text(encoding="utf-8").split("\n\n", 1)[-1]
                p["replica"] = escribir_replica(proyecto, p, cuerpo, a.origen)
                hechas.append(f"{p['id']} → {p['replica']}")
        with open(inv_csv, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=campos)
            w.writeheader()
            w.writerows({k: r.get(k, "") for k in campos} for r in previos)
        faltan = sorted(set(a.replicar) - {h.split(" ")[0] for h in hechas})
        print("Réplicas creadas:\n" + ("\n".join(f"- {h}" for h in hechas) or "- ninguna")
              + (f"\nSin texto extraído o no inventariados: {', '.join(faltan)}" if faltan else ""))
        return
    por_hash = {p["hash"]: p for p in previos}
    filas = list(previos)
    nuevos = 0

    archivos = sorted(p for p in entrada.rglob("*")
                      if p.is_file() and "_procesado" not in p.parts and "_archivo" not in p.parts
                      and p.name not in ("LEEME.md", ".gitkeep") and not p.name.startswith(("~$", "_LEEME")))
    for ruta in archivos:
        h = sha(ruta)
        rel = ruta.relative_to(entrada).as_posix()
        if h in por_hash:
            if por_hash[h]["archivo"] != rel and not any(f["archivo"] == rel for f in filas):
                filas.append({**por_hash[h], "id": f"F{len(filas) + 1:03d}", "archivo": rel,
                              "estado": "duplicado", "duplicado_de": por_hash[h]["id"]})
            continue
        fid = f"F{len(filas) + 1:03d}"
        ext = ruta.suffix.lower()
        texto, detalle, estado = "", "", "extraido"
        try:
            if ext in EXTRACTORES:
                fn = EXTRACTORES[ext]
                texto, detalle = fn(ruta, proc / "imagenes", a.max_filas) if fn is ext_xlsx else fn(ruta, proc / "imagenes")
            elif ext in EXT_TEXTO:
                texto, detalle = ext_texto(ruta, None)
            elif ext in EXT_IMAGEN:
                detalle, estado = "imagen (revisar visualmente)", "imagen"
            else:
                if ext == ".mpp":
                    detalle = ("MS Project (.mpp) no se lee directo: en MS Project, Archivo > Guardar como > tipo XML, "
                               "y deja ese .xml aquí")
                else:
                    detalle = f"formato {ext or 'sin extensión'} no soportado: convertir a PDF u otro formato"
                estado = "no_soportado"
        except Exception as e:  # un archivo dañado no detiene el inventario
            detalle, estado = f"error al leer: {e}", "error"
        destino_txt = ""
        if texto:
            nombre_limpio = re.sub(r"[^\w.-]", "_", ruta.stem)[:60]
            destino = proc / "texto" / f"{fid}__{nombre_limpio}.md"
            destino.write_text(f"<!-- Origen: {a.origen}/{rel} -->\n# {ruta.name}\n\n{texto}", encoding="utf-8")
            destino_txt = destino.relative_to(entrada).as_posix()
        fila = {"id": fid, "archivo": rel, "hash": h, "extension": ext, "kb": f"{ruta.stat().st_size / 1024:.0f}",
                "modificado": datetime.fromtimestamp(ruta.stat().st_mtime).strftime("%Y-%m-%d"),
                "categoria_sugerida": categorizar(rel, texto), "detalle": detalle,
                "palabras": str(len(texto.split())), "texto": destino_txt, "estado": estado, "duplicado_de": "", "replica": ""}
        decision = destino_replica(politica, fila["categoria_sugerida"]) if texto else ""
        if decision == "replicar":
            fila["replica"] = escribir_replica(proyecto, fila, texto, a.origen)
        elif decision:
            fila["replica"] = decision
        filas.append(fila)
        por_hash[h] = fila
        nuevos += 1

    emparejar_ocr(proyecto, entrada, filas, politica)
    with open(inv_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        w.writerows({k: r.get(k, "") for k in campos} for r in filas)

    total_pal = sum(int(f["palabras"] or 0) for f in filas if f["estado"] != "duplicado")
    resumen = {}
    for f in filas:
        if f["estado"] != "duplicado":
            resumen[f["categoria_sugerida"]] = resumen.get(f["categoria_sugerida"], 0) + 1
    md = [f"# Inventario de {a.origen}", "", f"Generado: {datetime.now():%Y-%m-%d %H:%M} · Archivos: {len(filas)} "
          f"(nuevos en esta pasada: {nuevos}) · Palabras extraídas: {total_pal:,}".replace(",", "."), "",
          "## Por categoría sugerida", "", "| Categoría | Archivos |", "|---|---|"]
    md += [f"| {k} | {v} |" for k, v in sorted(resumen.items(), key=lambda x: -x[1])]
    md += ["", "## Detalle", "", "| Id | Archivo | Categoría | Detalle | Palabras | Estado |", "|---|---|---|---|---|---|"]
    md += [f"| {f['id']} | {f['archivo']} | {f['categoria_sugerida']} | {f['detalle']} | {f['palabras']} | "
           f"{f['estado']}{' de ' + f['duplicado_de'] if f['duplicado_de'] else ''} |" for f in filas]
    sin_ocr = lambda f: "ESCANEO" in f["detalle"] and "otra versión de" not in f["detalle"]  # noqa: E731
    alertas = [f for f in filas if f["estado"] in ("error", "no_soportado") or sin_ocr(f)]
    if alertas:
        md += ["", "## Requieren atención", ""] + [f"- {f['id']} {f['archivo']}: {f['detalle']}"
                                                   + (f". Sin texto suficiente: {OCR_INSTRUCCION}" if sin_ocr(f) else "") for f in alertas]
    unicos = [f for f in filas if f["estado"] != "duplicado"]
    replicados = [f for f in unicos if (f.get("replica") or "").startswith("fuentes/")]
    solo_ficha = [f for f in unicos if f.get("replica") == "solo_ficha"]
    por_decidir = [f for f in unicos if f.get("replica") == "por_decidir"]
    if replicados or solo_ficha or por_decidir:
        md += ["", "## Réplicas en fuentes/ (texto fiel; se sube al repositorio privado)", "",
               f"- Replicados: {len(replicados)}" + "".join(f"\n  - {f['id']} → {f['replica']}" for f in replicados),
               f"- Solo ficha (datos personales o reservados; el texto queda local): {len(solo_ficha)}"
               + "".join(f"\n  - {f['id']} {f['archivo']} ({f['categoria_sugerida']})" for f in solo_ficha),
               f"- Por decidir en el alta (`extraer_entrada.py <proyecto> --replicar <id>`): {len(por_decidir)}"
               + "".join(f"\n  - {f['id']} {f['archivo']} ({f['categoria_sugerida']})" for f in por_decidir)]
    imgs = sorted((proc / "imagenes").glob("*"))
    if imgs:
        md += ["", "## Imágenes extraídas de documentos (candidatas a logo)", ""] + [f"- {p.name}" for p in imgs]
    (proc / "inventario.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md[:8 + len(resumen)]))
    print(f"\nRéplicas en fuentes/: {len(replicados)} · solo ficha: {len(solo_ficha)} · por decidir en el alta: {len(por_decidir)}")
    escaneos = [f for f in unicos if sin_ocr(f)]
    if escaneos:
        print(f"Escaneos sin texto suficiente: {len(escaneos)} ({', '.join(f['id'] for f in escaneos)}): hay que pasarlos por OCR "
              "(instrucciones en «Requieren atención» del inventario). Mientras tanto, su contenido no entra a la revisión de requisitos.")
    print(f"Inventario completo: {entrada_visible / '_procesado' / 'inventario.md'}")


if __name__ == "__main__":
    import _consola
    _consola.preparar()
    main()
