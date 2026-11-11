#!/usr/bin/env python3
"""Llena una plantilla Word propia (de la empresa, del proyecto o del cliente) sin cambiar su estructura.

Uso:
    python herramientas/llenar_docx.py <plantilla.docx> --valores valores.yaml --salida <salida.docx>
                                       [--proyecto proyectos/<slug>] [--vista-previa] [--borrador]

valores.yaml:
    marcadores:                      # {{semana}} en la plantilla → valor (también en tablas, encabezados y pies)
      semana: "2026-S39"
      estado: "Amarillo"
    secciones:                       # título de una sección de la plantilla (o su inicio) → contenido en Markdown simple
      "Riesgos principales": |
        - Calidad de datos maestros (alto): depuración en curso.
        - Disponibilidad de usuarios clave (medio).
      "Avance por subproyecto": |
        | Subproyecto | Avance | Estado |
        |---|---|---|
        | ERP | 55% | Amarillo |
      "Presupuesto": ""              # vacío = la sección se elimina del documento (título y contenido)
    conservar_cuerpo: false          # true = no borra el texto que la plantilla trae bajo el título; inserta después

- Marcadores: se reemplazan donde estén. Los que queden sin valor se informan y el script termina con código 1.
- Secciones: se ubican por su título (estilo de título de Word, o párrafo corto en negrita); se reemplaza lo que hay
  bajo el título hasta el siguiente título del mismo nivel, con el estilo que tenía la plantilla (párrafos, viñetas y
  tablas; las celdas Verde/Amarillo/Rojo se colorean). Lo que no se nombra queda intacto.
- Un `[PENDIENTE` en los valores impide generar (salvo --borrador). Autoría limpia: el archivo sale a nombre del
  usuario del proyecto, sin rastros de la herramienta.
"""
import argparse
import re
import sys
import unicodedata
from pathlib import Path

try:
    import yaml
    from docx import Document
except ImportError:
    sys.exit("Faltan dependencias: pip install python-docx pyyaml")

import autoria  # noqa: E402
import md_a_docx  # noqa: E402  (negritas, tablas y semáforo con el mismo criterio que el formato por defecto)


def norm(t):
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKD", str(t or "")).encode("ascii", "ignore").decode().lower()).strip()


def es_titulo(p):
    estilo = (p.style.name or "") if p.style is not None else ""
    e = estilo.lower()
    if e.startswith("heading") or e.startswith("título") or e.startswith("titulo") or e == "title":
        n = re.findall(r"\d", e)
        return int(n[0]) if n else 1
    t = p.text.strip()
    if t and len(t) < 80 and p.runs and all(r.bold for r in p.runs if r.text.strip()) and not t.endswith("."):
        return 9
    return 0


def reemplazar_en(parrafos, valores):
    """Reemplaza los marcadores en los párrafos tocando solo sus fragmentos de texto: una imagen o un campo que
    comparte el párrafo (el logo de un encabezado) queda intacto, y cada fragmento conserva su formato."""
    nombres = {k.strip("{} "): v for k, v in valores.items()}
    hechos = set()
    for p in parrafos:
        hechos |= {"{{" + n + "}}" for n in md_a_docx.reemplazar_marcadores_en(p._p, nombres)}
    return hechos


def reemplazar_marcadores(doc, marcadores):
    valores = {"{{" + k.strip("{} ") + "}}": v for k, v in marcadores.items()}
    hechos = set()
    hechos |= reemplazar_en(doc.paragraphs, valores)
    for t in doc.tables:
        for fila in t.rows:
            for celda in fila.cells:
                hechos |= reemplazar_en(celda.paragraphs, valores)
    for s in doc.sections:
        for parte in (s.header, s.footer):
            hechos |= reemplazar_en(parte.paragraphs, valores)
            for t in parte.tables:
                for fila in t.rows:
                    for celda in fila.cells:
                        hechos |= reemplazar_en(celda.paragraphs, valores)
    return hechos, [k for k in valores if k not in hechos]


def cuerpo_de(doc, elemento_titulo, nivel):
    """Elementos (párrafos y tablas) que siguen al título hasta el próximo título del mismo nivel o superior."""
    body = doc.element.body
    hijos = list(body.iterchildren())
    i = hijos.index(elemento_titulo)
    salida = []
    for el in hijos[i + 1:]:
        if el.tag.endswith("}p"):
            from docx.text.paragraph import Paragraph
            p = Paragraph(el, doc)
            n = es_titulo(p)
            if n and (n <= nivel or (nivel == 9 and n == 9)):
                break
            salida.append(el)
        elif el.tag.endswith("}tbl"):
            salida.append(el)
        elif el.tag.endswith("}sectPr"):
            break
    return salida


def estilos_del_cuerpo(doc, elementos):
    """Estilo de párrafo normal y de viñeta que usaba la plantilla bajo ese título."""
    from docx.text.paragraph import Paragraph
    normal, vineta = None, None
    for el in elementos:
        if el.tag.endswith("}p"):
            nombre = Paragraph(el, doc).style.name if Paragraph(el, doc).style is not None else ""
            if nombre.lower().startswith("list") and vineta is None:
                vineta = nombre
            elif normal is None and nombre:
                normal = nombre
    nombres = [s.name for s in doc.styles]
    if vineta is None:
        vineta = "List Bullet" if "List Bullet" in nombres else None
    return normal or "Normal", vineta


def insertar_contenido(doc, ancla, markdown, estilo_normal, estilo_vineta, color_hex):
    """Inserta el Markdown simple después del elemento `ancla`. Devuelve el último elemento insertado."""
    lineas = [l.rstrip() for l in markdown.strip("\n").splitlines()]
    i = 0
    actual = ancla
    while i < len(lineas):
        linea = lineas[i]
        if not linea.strip():
            i += 1
            continue
        if linea.lstrip().startswith("|"):
            filas = []
            while i < len(lineas) and lineas[i].lstrip().startswith("|"):
                if not re.match(r"^\s*\|\s*-", lineas[i]):
                    filas.append(md_a_docx.dividir_fila(lineas[i]))
                i += 1
            if filas:
                md_a_docx.agregar_tabla(doc, filas, color_hex)  # la agrega al final del documento (y un párrafo vacío)
                if doc.paragraphs and not doc.paragraphs[-1].text.strip():
                    vacio = doc.paragraphs[-1]._p
                    vacio.getparent().remove(vacio)
                tbl = doc.tables[-1]._tbl
                actual.addnext(tbl)
                actual = tbl
            continue
        m = re.match(r"^\s*(?:[-*]|\d+[.)])\s+(.*)$", linea)
        p = doc.add_paragraph()
        if m and estilo_vineta:
            p.style = doc.styles[estilo_vineta]
            md_a_docx.agregar_inline(p, m.group(1))
        elif m:
            p.style = doc.styles[estilo_normal]
            md_a_docx.agregar_inline(p, "• " + m.group(1))
        else:
            p.style = doc.styles[estilo_normal]
            md_a_docx.agregar_inline(p, linea.strip())
        actual.addnext(p._p)
        actual = p._p
        i += 1
    return actual


def buscar_titulo(doc, pedido):
    """(párrafo, nivel) del título que calza con `pedido` (igual, empieza con, o contiene)."""
    candidatos = [(p, es_titulo(p)) for p in doc.paragraphs if es_titulo(p)]
    q = norm(pedido)
    for p, n in candidatos:
        if norm(p.text) == q:
            return p, n
    for p, n in candidatos:
        if norm(p.text).startswith(q) or q in norm(p.text):
            return p, n
    qt = {w for w in re.findall(r"[a-z0-9]+", q) if len(w) > 3}
    for p, n in candidatos:
        if qt and qt <= {w for w in re.findall(r"[a-z0-9]+", norm(p.text))}:
            return p, n
    return None, 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plantilla")
    ap.add_argument("--valores", required=True)
    ap.add_argument("--salida")
    ap.add_argument("--proyecto", default="")
    ap.add_argument("--vista-previa", action="store_true")
    ap.add_argument("--borrador", action="store_true", help="permite [PENDIENTE] en los valores (uso interno)")
    a = ap.parse_args()
    plantilla = Path(a.plantilla)
    if not plantilla.exists():
        sys.exit(f"No existe la plantilla {plantilla}.")
    datos = yaml.safe_load(Path(a.valores).read_text(encoding="utf-8")) or {}
    marcadores = {str(k): ("" if v is None else v) for k, v in (datos.get("marcadores") or {}).items()}
    secciones = {str(k): ("" if v is None else str(v)) for k, v in (datos.get("secciones") or {}).items()}
    conservar = bool(datos.get("conservar_cuerpo", False))
    todo = " ".join(map(str, marcadores.values())) + " " + " ".join(secciones.values())
    if "[PENDIENTE" in todo and not a.borrador:
        sys.exit("Hay [PENDIENTE] en los valores: completa el dato antes de generar (o --borrador para una versión interna).")
    if not a.salida and not a.vista_previa:
        sys.exit("Indica --salida <archivo.docx> (o --vista-previa).")

    doc = Document(str(plantilla))
    titulos = [(p.text.strip(), es_titulo(p)) for p in doc.paragraphs if es_titulo(p)]
    hechos, sin_valor = reemplazar_marcadores(doc, marcadores)
    cfg, _ = md_a_docx.cargar_cfg(a.proyecto) if a.proyecto else ({}, None)
    color_hex = str((cfg.get("formato") or {}).get("color_primario") or "1F3864")
    llenadas, no_encontradas, eliminadas = [], [], []
    for titulo, contenido in secciones.items():
        p, nivel = buscar_titulo(doc, titulo)
        if p is None:
            no_encontradas.append(titulo)
            continue
        elementos = cuerpo_de(doc, p._p, nivel)
        if not contenido.strip():  # sección sin contenido: se elimina entera (título incluido)
            if not a.vista_previa:
                for el in elementos + [p._p]:
                    el.getparent().remove(el)
            eliminadas.append(p.text.strip())
            continue
        estilo_normal, estilo_vineta = estilos_del_cuerpo(doc, elementos)
        if not conservar and not a.vista_previa:
            for el in elementos:
                el.getparent().remove(el)
        if not a.vista_previa:
            insertar_contenido(doc, p._p, contenido, estilo_normal, estilo_vineta, color_hex)
        llenadas.append(f"«{p.text.strip()}» ({len(contenido.splitlines())} líneas; estilo {estilo_normal}"
                        + (f", viñetas {estilo_vineta}" if estilo_vineta else "") + ")")
    print(f"# {'Vista previa' if a.vista_previa else 'Plantilla llenada'} · {plantilla.name}\n")
    print("- Títulos de la plantilla: " + ", ".join(f"«{t}»" for t, _ in titulos[:20]))
    print(f"- Marcadores reemplazados: {', '.join(sorted(hechos)) if hechos else 'ninguno'}")
    if sin_valor:
        print(f"- Marcadores de los valores que la plantilla no tiene: {', '.join(sin_valor)}")
    restantes = sorted(set(re.findall(r"\{\{[^}]+\}\}", "\n".join(p.text for p in doc.paragraphs))))
    if restantes:
        print(f"- Marcadores de la plantilla que quedaron sin valor: {', '.join(restantes)}")
    print("- Secciones llenadas: " + ("; ".join(llenadas) if llenadas else "ninguna"))
    if eliminadas:
        print("- Secciones eliminadas (sin contenido): " + "; ".join(f"«{t}»" for t in eliminadas))
    if no_encontradas:
        print("- Secciones pedidas que no están en la plantilla (revisa el título): " + "; ".join(f"«{t}»" for t in no_encontradas))
    if a.vista_previa:
        return 1 if no_encontradas else 0
    salida = Path(a.salida)
    salida.parent.mkdir(parents=True, exist_ok=True)
    if salida.resolve() == plantilla.resolve():
        sys.exit("La salida no puede ser la misma plantilla: se conserva intacta.")
    doc.save(str(salida))
    aut = autoria.cargar_autoria(a.proyecto or None)
    try:
        autoria.limpiar_ooxml(salida, autor=aut.get("nombre", ""), titulo="", organizacion=aut.get("organizacion", ""))
    except Exception as e:
        print(f"- Aviso: no se pudo limpiar la autoría ({e}); ejecuta verificar_autoria.py --corregir.")
    print(f"\nGuardado: {salida}" + (" · revisa con verificar_autoria.py antes de entregar." if not a.proyecto else ""))
    if restantes and not a.borrador:
        print("Quedan marcadores sin valor: dales contenido o elimina esas secciones (valor vacío) antes de entregar.")
    return 1 if (no_encontradas or (restantes and not a.borrador)) else 0


if __name__ == "__main__":
    import _consola
    _consola.preparar()
    sys.exit(main())
