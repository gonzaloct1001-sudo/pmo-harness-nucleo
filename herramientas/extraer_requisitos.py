#!/usr/bin/env python3
"""Barrido exhaustivo de las bases de una convocatoria: candidatos a requisito para la matriz de cumplimiento.

Uso:
    python herramientas/extraer_requisitos.py proyectos/<slug> [--categorias bases,formulario,...] [--todo]
                                              [--origen carpeta ...] [--salida archivo.csv]

Lee los textos de las bases (por defecto las réplicas de `fuentes/*.md`, que sirven en cualquier computador; los textos
de `_entrada/_procesado/texto/*.md` que no tengan réplica, generados por extraer_entrada.py; y `postulacion/bases/*.md`).
Por defecto barre solo las categorías `bases` y `formulario` del inventario: la normativa general (leyes, decretos), las
charlas y los archivos de trabajo propios generan ruido; se agregan con --categorias o --todo. Lo que venga de una charla
queda con `vinculante = no: confirmar por consulta`. Marca cada frase o fila de tabla con lenguaje obligatorio o de plazo ("deberá",
"obligatorio", "excluyente", "adjuntar", "a más tardar", "no se aceptarán", topes, garantías, formatos...).
Para cada candidato sugiere tipo (admisibilidad, tecnico, economico, formal, declaracion), si parece excluyente,
y extrae fechas, horas, montos y porcentajes.

Escribe `postulacion/barrido-requisitos.csv`. Es incremental: los candidatos ya revisados (misma huella de
texto) conservan su estado; solo se agregan los nuevos (por ejemplo, al llegar una aclaración).
El barrido NO reemplaza la lectura de las bases: es la red de seguridad para que ningún requisito escrito en un
anexo, formulario o aclaración quede fuera de la matriz. Cada candidato debe quedar `incorporado` (con
requisito_id) o `descartado` (con motivo) en la skill matriz-cumplimiento.
"""
import argparse
import csv
import hashlib
import re
import sys
from pathlib import Path

OBLIGACION = re.compile(
    r"deber[áa]n?\b|\bdeben?\b|obligatori|exig(e|en|ir[áa]|id[oa]s?)\b|se requier|requisito|excluyente|inadmisib|"
    r"\bcausal|no ser[áa]n? (admitid|considerad|evaluad)|no se (aceptar|admitir|considerar)|quedar[áa]n? (fuera|excluid)|"
    r"ser[áa]n? rechazad|fuera de bases|adjuntar|acompañar|presentar|incluir|m[áa]ximo de|m[íi]nimo de|no podr[áa]n?|"
    r"a m[áa]s tardar|hasta las \d|plazo|garant[íi]a|boleta|declaraci[óo]n jurada|firmad|certificad|vigente|"
    r"formato|extensi[óo]n|p[áa]ginas|caracteres|inteligencia artificial|\bIA\b|tope|no (son |ser[áa]n? )?financiab|"
    r"no ser[áa]n? financiad|elegib|podr[áa]n (postular|participar|presentar)|hasta el \d|se recibir[áa]n|exclusivamente|"
    r"[úu]nicamente|s[óo]lo se|nota (final|m[íi]nima)|puntaje m[íi]nimo|desempate|prevalecer[áa]|prohib|prohíb|"
    r"generativ|chat\s?gpt|herramientas de (IA|inteligencia)|m[íi]nim[oa]s?|m[áa]xim[oa]s?|\d\s?%",
    re.I)
REFERENCIA = re.compile(r"^(La|El|Los|Las|Su|Sus)?\s*(omisi[óo]n|falta|ausencia|incumplimiento|no presentaci[óo]n|presentaci[óo]n)?\s*"
                        r"(de\s+)?(est[oa]s?|dich[oa]s?|tal(es)?|lo anterior|ello)\b", re.I)
EXCLUYENTE = re.compile(r"inadmisib|excluyente|\bcausal|no ser[áa]n? (admitid|considerad|evaluad)|no se (aceptar|admitir|considerar)|"
                        r"quedar[áa]n? (fuera|excluid)|ser[áa]n? rechazad|fuera de bases|so pena", re.I)
TIPOS = [  # el orden importa: gana el primero que calza
    ("declaracion", re.compile(r"declaraci[óo]n jurada|inteligencia artificial|\bIA\b|chat\s?gpt|generativ|conflicto de inter[ée]s|"
                               r"inhabilidad", re.I)),
    ("evaluacion", re.compile(r"nota (final|m[íi]nima)|puntaje|ponderaci[óo]n|desempate|prevalecer[áa]|escala de \d|"
                              r"ser[áa]n evaluad|criterios? de evaluaci|\|\s*\d{1,3}([.,]\d+)?\s?%\s*\|", re.I)),
    ("admisibilidad", re.compile(r"inadmisib|excluyente|\bcausal|admisib|podr[áa]n postular|no podr[áa]n postular|"
                                 r"requisitos? de postulaci|inicio de actividades|personalidad jur[íi]dica|constituid", re.I)),
    ("economico", re.compile(r"aporte|cofinanc|presupuesto|\bmonto|pecuniari|gasto|garant[íi]a|boleta|precio|\bIVA\b|\bUF\b|\bUTM\b|"
                             r"\$\s?\d|financiab|tope", re.I)),
    ("formal", re.compile(r"formato|p[áa]ginas|caracteres|firmad|a m[áa]s tardar|hasta las \d|hasta el \d|plazo|plataforma|"
                          r"archivo|\bPDF\b|anexo|formulario|extensi[óo]n|foliad|original|copia|certificad|adjunt|acompañ|"
                          r"se recibir[áa]n|vigencia", re.I)),
]
MESES = r"(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|setiembre|octubre|noviembre|diciembre)"
DATOS = [
    ("fecha", re.compile(r"\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b|\b\d{4}-\d{2}-\d{2}\b|\b\d{1,2} de " + MESES + r"( de(l)? \d{4})?", re.I)),
    ("hora", re.compile(r"\b\d{1,2}:\d{2}\s?(hrs?|horas)?\b", re.I)),
    ("monto", re.compile(r"\$\s?[\d.]+(,\d+)?|\bUF\s?[\d.,]+|[\d.,]+\s?(UF|UTM)\b", re.I)),
    ("porcentaje", re.compile(r"\b\d{1,3}([.,]\d+)?\s?%")),
]
CAMPOS = ["id", "documento", "ubicacion", "texto", "tipo_sugerido", "excluyente_sugerido", "datos_detectados", "huella",
          "estado_revision", "requisito_id", "motivo_descarte", "vinculante"]
IA = re.compile(r"inteligencia artificial|\bIA\b|\bI\.A\.|chat\s?gpt|generativ|modelos? de lenguaje|\bLLM\b", re.I)
ITEM = re.compile(r"^([-*•]|\d+(\.\d+)*[.)]|[a-zA-Z][.)])\s+")
ABREV = re.compile(r"\b(arts?|inc|n[úu]m|p[áa]gs?|pp|lit|n[°º]|sra?|dra?|ej|etc)\.\s", re.I)
TITULO = re.compile(r"^(#{1,6}\s+.+|(ART[ÍI]CULO|Art[íi]culo|ART\.|Art\.)\s*\w+.*|[IVXLC]+\.\s+[A-ZÁÉÍÓÚÑ].{3,}|\d+(\.\d+)*\.?\s+[A-ZÁÉÍÓÚÑ].{3,80})$")


def huella(texto):
    norm = re.sub(r"\s+", " ", texto.lower()).strip()
    return hashlib.sha1(norm.encode("utf-8")).hexdigest()[:12]


def unidades(texto):
    """Divide un documento en frases y filas de tabla, conservando el título y la página vigentes."""
    titulo, pagina = "", ""
    parrafo, inicio = [], 0
    for n, linea in enumerate(texto.splitlines(), 1):
        s = linea.strip()
        m = re.match(r"^-+\s*P[áa]gina\s+(\d+)\s*-+$", s)
        if m:
            pagina = m.group(1)
            continue
        if s.startswith("<!--"):
            continue
        if s.startswith("|"):
            if parrafo:
                yield from _frases(" ".join(parrafo), titulo, pagina, inicio)
                parrafo = []
            celdas = [c.strip() for c in s.strip("|").split("|")]
            if not re.fullmatch(r"[\s:\-|]+", s) and any(celdas):
                yield (" | ".join(c for c in celdas if c), titulo, pagina, n)
            continue
        if not s:
            if parrafo:
                yield from _frases(" ".join(parrafo), titulo, pagina, inicio)
                parrafo = []
            continue
        es_titulo = TITULO.match(s) and len(s) < 120
        if es_titulo and (s.startswith("#") or not OBLIGACION.search(s)):
            if parrafo:
                yield from _frases(" ".join(parrafo), titulo, pagina, inicio)
                parrafo = []
            titulo = s.lstrip("#").strip()
            continue
        if es_titulo or ITEM.match(s):  # artículo o ítem numerado con contenido: se evalúa por sí mismo
            if parrafo:
                yield from _frases(" ".join(parrafo), titulo, pagina, inicio)
                parrafo = []
            yield from _frases(s, titulo, pagina, n)
            continue
        if not parrafo:
            inicio = n
        parrafo.append(s)
    if parrafo:
        yield from _frases(" ".join(parrafo), titulo, pagina, inicio)


def _frases(parrafo, titulo, pagina, linea):
    """Frases del párrafo; una frase que remite a la anterior ("La omisión de estas cartas...") se une a ella."""
    frases = []
    protegido = ABREV.sub(lambda m: m.group(0)[:-1] + "\u0000", parrafo)
    for f in re.split(r"(?<=[.;:])\s+(?=[A-ZÁÉÍÓÚÑ¿(\d])", protegido):
        f = f.replace("\u0000", " ").strip()
        if frases and REFERENCIA.match(f):
            frases[-1] = frases[-1] + " " + f
        elif f:
            frases.append(f)
    for f in frases:
        if len(f) >= 20:
            yield (f, titulo, pagina, linea)


def clasificar(texto):
    for tipo, patron in TIPOS:
        if patron.search(texto):
            return tipo
    return "tecnico"


def datos(texto):
    encontrados = []
    for nombre, patron in DATOS:
        vals = [m.group(0).strip() for m in patron.finditer(texto)]
        if vals:
            encontrados.append(f"{nombre}: {', '.join(dict.fromkeys(vals))}")
    if IA.search(texto):
        encontrados.append("uso de IA: revisar si exige declaración o lo restringe")
    return " · ".join(encontrados)


CATEGORIAS_POR_DEFECTO = ("bases", "formulario")  # la normativa general y las charlas se barren solo si se piden
NO_VINCULANTES = ("charla",)  # lo dicho en una charla o capacitación no es vinculante: se confirma por consulta formal


def categoria_replica(ruta):
    m = re.search(r"^categoria:\s*(\S+)", ruta.read_text(encoding="utf-8", errors="replace")[:1500], re.M)
    return m.group(1) if m else ""


def categorias_inventario(raiz):
    inv = raiz / "_entrada" / "_procesado" / "inventario.csv"
    if not inv.exists():
        return {}
    with open(inv, encoding="utf-8", newline="") as f:
        return {r["id"]: r.get("categoria_sugerida", "") for r in csv.DictReader(f)}


def fuentes_por_defecto(raiz, categorias=CATEGORIAS_POR_DEFECTO):
    """Réplicas de fuentes/ (sirven en cualquier computador) y textos de _entrada/_procesado/ sin réplica (mismo id del
    inventario), de las categorías pedidas; más las fichas de postulacion/bases/. Devuelve ([(ruta, categoría)], omitidos)."""
    replicas = sorted(p for p in (raiz / "fuentes").glob("*.md") if p.name.upper() != "LEEME.MD")
    con_replica = {p.name.split("-", 1)[0] for p in replicas}
    inv = categorias_inventario(raiz)
    elegidas, omitidas = [], {}
    candidatas = [(p, categoria_replica(p) or "bases") for p in replicas]
    candidatas += [(p, inv.get(p.name.split("__", 1)[0], "bases"))
                   for p in sorted((raiz / "_entrada" / "_procesado" / "texto").glob("*.md")) if p.name.split("__", 1)[0] not in con_replica]
    for p, cat in candidatas:
        if categorias is None or cat in categorias:
            elegidas.append((p, cat))
        else:
            omitidas[cat] = omitidas.get(cat, 0) + 1
    elegidas += [(p, "bases") for p in sorted((raiz / "postulacion" / "bases").glob("*.md")) if p.name.upper() != "LEEME.MD"]
    return elegidas, omitidas


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("proyecto")
    ap.add_argument("--origen", nargs="*", help="carpetas o archivos con el texto de las bases (por defecto, ver arriba)")
    ap.add_argument("--salida", help="por defecto postulacion/barrido-requisitos.csv")
    ap.add_argument("--categorias", help=f"categorías del inventario a barrer, separadas por coma (por defecto: {','.join(CATEGORIAS_POR_DEFECTO)}; "
                                         "agrega normativa o charla si hace falta)")
    ap.add_argument("--todo", action="store_true", help="barrer todos los documentos, de cualquier categoría")
    a = ap.parse_args()

    raiz = Path(a.proyecto)
    omitidas = {}
    if a.origen:
        rutas = []
        for o in a.origen:
            p = Path(o)
            rutas += [(x, "bases") for x in (sorted(p.rglob("*.md")) + sorted(p.rglob("*.txt")) if p.is_dir() else [p])]
    else:
        categorias = None if a.todo else tuple(c.strip() for c in (a.categorias or ",".join(CATEGORIAS_POR_DEFECTO)).split(",") if c.strip())
        rutas, omitidas = fuentes_por_defecto(raiz, categorias)
    if not rutas:
        sys.exit("No hay textos de bases: ejecuta primero extraer_entrada.py o indica --origen.")
    salida = Path(a.salida) if a.salida else raiz / "postulacion" / "barrido-requisitos.csv"
    salida.parent.mkdir(parents=True, exist_ok=True)

    previos = []
    if salida.exists():
        with open(salida, encoding="utf-8-sig", newline="") as f:
            previos = list(csv.DictReader(f))
    vistos = {p["huella"] for p in previos}
    filas = list(previos)
    nuevos = 0
    for ruta, categoria in rutas:
        texto = ruta.read_text(encoding="utf-8", errors="replace")
        texto = re.sub(r"\A---\n.*?\n---\n", "", texto, count=1, flags=re.S)  # encabezado de una réplica de fuentes/
        for frase, titulo, pagina, linea in unidades(texto):
            if not OBLIGACION.search(frase):
                continue
            h = huella(frase)
            if h in vistos:
                continue
            vistos.add(h)
            ubic = " · ".join(x for x in (titulo[:80], f"pág. {pagina}" if pagina else "", f"línea {linea}") if x)
            siguiente = max([int(re.sub(r"\D", "", r["id"]) or 0) for r in filas] + [0]) + 1
            filas.append({"id": f"B-{siguiente:03d}", "documento": ruta.stem, "ubicacion": ubic, "texto": frase[:600],
                          "tipo_sugerido": clasificar(frase), "excluyente_sugerido": "si" if EXCLUYENTE.search(frase) else "revisar",
                          "datos_detectados": datos(frase), "huella": h, "estado_revision": "pendiente",
                          "requisito_id": "", "motivo_descarte": "",
                          "vinculante": "no: confirmar por consulta" if categoria in NO_VINCULANTES else "si"})
            nuevos += 1

    with open(salida, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS)
        w.writeheader()
        w.writerows({k: r.get(k, "") for k in CAMPOS} for r in filas)

    pend = [r for r in filas if r["estado_revision"] == "pendiente"]
    por_tipo = {}
    for r in filas:
        por_tipo[r["tipo_sugerido"]] = por_tipo.get(r["tipo_sugerido"], 0) + 1
    print(f"# Barrido de requisitos — {raiz.as_posix()}\n")
    print(f"- Documentos leídos: {len(rutas)} · candidatos: {len(filas)} (nuevos en esta pasada: {nuevos}) · pendientes de revisar: {len(pend)}")
    if omitidas:
        print("- No barridos (otras categorías del inventario): " + ", ".join(f"{k} {v}" for k, v in sorted(omitidas.items()))
              + ". Para incluirlos: --categorias bases,formulario,<categoría> (o --todo).")
    no_vinc = [r for r in filas if r.get("vinculante", "si").startswith("no")]
    if no_vinc:
        print(f"- ATENCIÓN: {len(no_vinc)} candidato(s) vienen de charlas o capacitaciones: NO son vinculantes. Si agregan o "
              "contradicen algo de las bases, confírmalos con una consulta formal (postulacion/consultas.csv).")
    print("- Por tipo sugerido: " + ", ".join(f"{k} {v}" for k, v in sorted(por_tipo.items(), key=lambda x: -x[1])))
    exc = [r for r in filas if r["excluyente_sugerido"] == "si"]
    print(f"- Con lenguaje de exclusión (revisar como excluyentes): {len(exc)}")
    for r in exc[:15]:
        print(f"  - {r['id']} [{r['documento']} · {r['ubicacion']}] {r['texto'][:300]}")
    ia = [r for r in filas if "uso de IA" in r["datos_detectados"]]
    if ia:
        print(f"- ATENCIÓN: {len(ia)} candidato(s) mencionan inteligencia artificial: revisar si exigen declarar o restringen su uso.")
        for r in ia:
            print(f"  - {r['id']} [{r['documento']}] {r['texto'][:160]}")
    fechas = [r for r in filas if "fecha:" in r["datos_detectados"] or "hora:" in r["datos_detectados"]]
    print(f"- Con fechas u horas (candidatos al calendario): {len(fechas)}")
    print(f"\nArchivo: {salida.as_posix()}")


if __name__ == "__main__":
    import _consola
    _consola.preparar()
    main()
