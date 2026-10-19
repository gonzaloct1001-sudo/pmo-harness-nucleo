#!/usr/bin/env python3
"""Crea la carpeta de un proyecto combinando la plantilla base con uno o más arquetipos.

Uso:
    python herramientas/crear_proyecto.py <slug> --arquetipos cartera[,estudio,...] [--nombre "Nombre visible"]
                                          [--perfil biblioteca/perfiles/<perfil>] [--programa <slug-del-programa>]

Tres casos:
- Proyecto independiente: proyectos/<slug>/ (sin --programa y sin el arquetipo programa).
- Programa (contrato padre con subproyectos): --arquetipos programa,ejecucion → proyectos/<slug>/.
- Subproyecto de un programa: --programa <programa> → proyectos/<programa>/subproyectos/<slug>/, con la plantilla de
  subproyecto (hereda del programa lo que no define) y registrado en programa/subproyectos.csv. No lleva contractual/,
  _entrada/ ni presupuesto propios: esos se gestionan en el programa.

- Copia la estructura del perfil (si se indica), la de cada arquetipo y la plantilla base, sin sobrescribir
  nada: si un archivo existe en varias fuentes, gana el perfil, luego el arquetipo y al final la base.
- Agrega a proyecto.yaml los bloques propios de cada arquetipo y registra arquetipos, slug y nombre.
- Si la carpeta tiene empresa (`empresa/empresa.yaml`), el proyecto nuevo hereda su marca, autoría y responsable
  (los campos de formato quedan vacíos para tomar los de la empresa), recibe los formatos de reporte comunes de
  `empresa/reportes/catalogo/` y su guía de estilo, y en una postulación el postulante es la empresa.
Si el proyecto ya existe, solo agrega lo que falte (sirve para sumar un arquetipo después).
"""
import argparse
import csv
import re
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


SOLO_PROGRAMA = {"contractual", "_entrada", "presupuesto", "programa", "subproyectos"}


def copiar_sin_sobrescribir(origen: Path, destino: Path, excluir=()):
    creados = 0
    for p in origen.rglob("*"):
        rel = p.relative_to(origen)
        if rel.parts and rel.parts[0] in excluir:
            continue
        d = destino / rel
        if p.is_dir():
            d.mkdir(parents=True, exist_ok=True)
        elif not d.exists():
            d.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, d)
            creados += 1
    return creados


def heredar_de_empresa(dest: Path, es_subproyecto, nuevo):
    """Copia al proyecto nuevo lo común de la empresa (formatos de reporte y estilo). Devuelve sus datos o None."""
    emp = RAIZ / "empresa"
    if not (emp / "empresa.yaml").exists() or es_subproyecto:
        return None
    import yaml
    datos = yaml.safe_load((emp / "empresa.yaml").read_text(encoding="utf-8")) or {}
    nombre = str((datos.get("empresa") or {}).get("nombre") or "")
    info = {"nombre": "" if nombre == "PENDIENTE" else nombre, "formato": datos.get("formato") or {}, "formatos": []}
    if not nuevo:
        return info
    for d in sorted((emp / "reportes" / "catalogo").glob("*.md")):
        if d.name.startswith("_") or d.name.upper() == "LEEME.MD":
            continue
        destino = dest / "reportes" / "catalogo" / d.name
        if not destino.exists():
            destino.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(d, destino)
            info["formatos"].append(d.stem)
    estilo_emp, estilo_base = emp / "estilo.md", RAIZ / "plantilla-empresa" / "estilo.md"
    estilo_proy, estilo_plantilla = dest / "contexto" / "estilo.md", RAIZ / "plantilla-proyecto" / "contexto" / "estilo.md"
    if (estilo_emp.exists() and estilo_proy.exists() and estilo_plantilla.exists()
            and estilo_proy.read_text(encoding="utf-8") == estilo_plantilla.read_text(encoding="utf-8")
            and not (estilo_base.exists() and estilo_emp.read_text(encoding="utf-8") == estilo_base.read_text(encoding="utf-8"))):
        shutil.copy2(estilo_emp, estilo_proy)
    return info


def vaciar_formato_heredado(texto, formato_empresa):
    """Deja vacíos en el bloque `formato:` del proyecto los campos que define la empresa (salvo el logo), para heredarlos."""
    m = re.search(r"^formato:[ \t]*\n((?:[ \t]+.*\n?)*)", texto, re.M)
    if not m:
        return texto
    bloque = m.group(1)
    for clave, valor in formato_empresa.items():
        if clave == "logo" or valor in (None, ""):
            continue
        bloque = re.sub(rf"^(  {re.escape(clave)}:).*$", r'\g<1> ""  # vacío = el de la empresa', bloque, count=1, flags=re.M)
    return texto[:m.start(1)] + bloque + texto[m.end(1):]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slug")
    ap.add_argument("--arquetipos", default="", help="lista separada por comas: ejecucion, cartera, estudio... "
                    "(obligatoria salvo en un subproyecto, donde por defecto es ejecucion)")
    ap.add_argument("--nombre", default="")
    ap.add_argument("--perfil", default="", help="carpeta de un perfil de biblioteca (opcional)")
    ap.add_argument("--destino", default="proyectos", help="carpeta contenedora (por defecto proyectos/)")
    ap.add_argument("--programa", default="", help="slug del programa al que pertenece este subproyecto")
    a = ap.parse_args()

    import _nucleo
    if _nucleo.es_mantenedor(RAIZ):
        sys.exit("Esta carpeta es el núcleo que mantienes (repositorio público): no lleva proyectos. Crea tus proyectos en "
                 "una carpeta de empresa: python herramientas/nueva_empresa.py \"<Nombre>\" --destino <carpeta>")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", a.slug):
        sys.exit("El slug debe tener solo minúsculas, números y guiones (sin tildes ni espacios).")
    arqs = [x.strip() for x in a.arquetipos.split(",") if x.strip()]
    if not arqs:
        if not a.programa:
            sys.exit("Indica --arquetipos (por ejemplo ejecucion, o programa,ejecucion para un programa).")
        arqs = ["ejecucion"]
    disponibles = sorted(p.name for p in (RAIZ / "arquetipos").iterdir() if p.is_dir())
    for x in arqs:
        if x not in disponibles:
            sys.exit(f"Arquetipo desconocido: {x}. Disponibles: {', '.join(disponibles)}")

    excluir = ()
    base = RAIZ / "plantilla-proyecto"
    if a.programa:
        if "programa" in arqs:
            sys.exit("Un subproyecto no puede ser a su vez un programa.")
        raiz_prog = RAIZ / a.destino / a.programa
        yaml_prog = raiz_prog / "proyecto.yaml"
        if not yaml_prog.exists():
            sys.exit(f"No existe el programa {raiz_prog.relative_to(RAIZ).as_posix()}.")
        m = re.search(r"^arquetipos:\s*\[(.*?)\]", yaml_prog.read_text(encoding="utf-8"), re.M)
        if not m or "programa" not in m.group(1):
            sys.exit(f"{a.programa} no tiene el arquetipo programa: agrégalo con --arquetipos programa sobre ese proyecto.")
        dest = raiz_prog / "subproyectos" / a.slug
        base, excluir = RAIZ / "plantilla-subproyecto", SOLO_PROGRAMA
    else:
        dest = RAIZ / a.destino / a.slug
    nuevo = not dest.exists()
    # Orden de precedencia (nunca se sobrescribe lo existente): perfil > arquetipos (en el orden dado) > base.
    n = 0
    if a.perfil:
        perfil = (RAIZ / a.perfil) if not Path(a.perfil).is_absolute() else Path(a.perfil)
        if (perfil / "estructura").exists():
            n += copiar_sin_sobrescribir(perfil / "estructura", dest, excluir)
    for x in arqs:
        n += copiar_sin_sobrescribir(RAIZ / "arquetipos" / x / "estructura", dest, excluir)
    n += copiar_sin_sobrescribir(base, dest)

    yml = dest / "proyecto.yaml"
    texto = yml.read_text(encoding="utf-8")
    actuales = re.search(r"^arquetipos:\s*\[(.*?)\]", texto, re.M)
    previos = [x.strip() for x in actuales.group(1).split(",") if x.strip()] if actuales else []
    todos = list(dict.fromkeys(previos + arqs))
    texto = re.sub(r"^arquetipos:\s*\[.*?\]", f"arquetipos: [{', '.join(todos)}]", texto, count=1, flags=re.M)
    texto = re.sub(r"^(  slug:\s*)PENDIENTE", rf"\g<1>{a.slug}", texto, count=1, flags=re.M)
    if a.nombre:
        texto = re.sub(r"^(  nombre:\s*)PENDIENTE", lambda m: m.group(1) + a.nombre, texto, count=1, flags=re.M)
    if a.perfil:
        texto = re.sub(r'^perfil:\s*""', f'perfil: "{a.perfil}"', texto, count=1, flags=re.M)
    for x in arqs:
        frag = RAIZ / "arquetipos" / x / "proyecto.fragmento.yaml"
        if frag.exists():
            contenido = frag.read_text(encoding="utf-8")
            clave = re.search(r"^(\w+):", contenido, re.M)
            if clave and not re.search(rf"^{clave.group(1)}:", texto, re.M):
                texto = texto.rstrip() + "\n" + contenido
    empresa = heredar_de_empresa(dest, a.programa, nuevo)
    if empresa and nuevo and not a.programa:
        texto = vaciar_formato_heredado(texto, empresa["formato"])
        if empresa["nombre"]:
            texto = re.sub(r"^(  postulante:\s*)PENDIENTE", lambda m: m.group(1) + empresa["nombre"], texto, count=1, flags=re.M)
    yml.write_text(texto, encoding="utf-8")

    if a.programa:
        lista = raiz_prog / "programa" / "subproyectos.csv"
        campos = ["id", "nombre", "carpeta", "responsable", "estado", "peso", "comentario"]
        filas = []
        if lista.exists():
            with open(lista, encoding="utf-8-sig", newline="") as fh:
                filas = list(csv.DictReader(fh))
        if not any(f.get("id") == a.slug for f in filas):
            lista.parent.mkdir(parents=True, exist_ok=True)
            nuevo_csv = not lista.exists() or not filas and lista.stat().st_size == 0
            with open(lista, "a", encoding="utf-8", newline="") as fh:
                w = csv.DictWriter(fh, fieldnames=campos)
                if nuevo_csv:
                    w.writeheader()
                w.writerow({"id": a.slug, "nombre": a.nombre or a.slug, "carpeta": f"subproyectos/{a.slug}",
                            "responsable": "", "estado": "activo", "peso": "", "comentario": ""})

    tipo = "Subproyecto" if a.programa else ("Programa" if "programa" in todos else "Proyecto")
    print(f"{tipo} {'creado' if nuevo else 'actualizado'}: {dest.relative_to(RAIZ).as_posix()}")
    if a.programa:
        print(f"Registrado en {(raiz_prog / 'programa' / 'subproyectos.csv').relative_to(RAIZ).as_posix()}; hereda formato y marca del programa.")
    if empresa and not a.programa:
        print(f"Hereda de la empresa «{empresa['nombre'] or 'sin nombre'}»: marca, autoría y responsable"
              + (f"; formatos comunes copiados: {', '.join(empresa['formatos'])}" if empresa["formatos"] else ""))
    print(f"Arquetipos: {', '.join(todos)} · archivos nuevos: {n}")
    for x in arqs:
        print(f"Guía del arquetipo: arquetipos/{x}/ARQUETIPO.md")


if __name__ == "__main__":
    import _consola
    _consola.preparar()
    main()
