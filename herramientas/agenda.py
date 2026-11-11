#!/usr/bin/env python3
"""Agenda del día: lo vencido, lo de hoy y lo que viene, de todos los proyectos de la empresa, en una sola lista.

Uso:
    python herramientas/agenda.py [--dias 14] [--hoy AAAA-MM-DD]     # la minuta de pendientes de hoy
    python herramientas/agenda.py --una-vez                          # solo si todavía no se mostró hoy (lo usa el hook del día)

Reúne, leyendo los registros de cada proyecto y de sus subproyectos (no modifica nada):
- hitos del cronograma sin terminar, acuerdos y problemas abiertos con fecha de compromiso, vencimientos propios,
  riesgos con fecha de revisión, y el cierre y el calendario de una postulación;
- los reportes del catálogo que tocan hoy y aún no se emiten en su período. Un reporte toca cuando su definición
  (`reportes/catalogo/<tipo>.md`) trae `dia:`: un día de la semana (`lunes`…), números del mes (`1,15`) o `ultimo`.
Respeta lo pausado: un proyecto con `proyecto.estado: pausado` (o detenido, o cerrado) no lista sus pendientes, y una
fila pausada, detenida o cancelada no cuenta.

A diferencia de `status.py` (semáforos y decisiones, para saber cómo va cada proyecto), la agenda responde «¿qué tengo
que mirar hoy?». En Claude Code la entrega una vez al día el hook `agenda_diaria.py`, en la primera interacción.
"""
import argparse
import calendar
import csv
import re
import sys
import unicodedata
from datetime import date, datetime, timedelta
from pathlib import Path

import _nucleo

RAIZ = Path(__file__).resolve().parent.parent
MARCA = Path(".harness") / "agenda-vista.txt"   # fecha de la última vez que se mostró (propio de cada computador)
ABIERTO = ("", "abierto", "abierta", "pendiente", "en curso", "en_curso", "en progreso")
EN_PAUSA = ("pausado", "pausada", "en pausa", "detenido", "detenida", "suspendido", "suspendida")
CERRADO = ("cerrado", "cerrada", "terminado", "terminada", "resuelto", "resuelta", "cumplido", "cumplida", "cancelado",
           "cancelada", "descartado", "descartada", "materializado", "materializada")
DIAS = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]
MAXIMO = 12


def sin_tildes(texto):
    return "".join(c for c in unicodedata.normalize("NFD", str(texto or "")) if unicodedata.category(c) != "Mn").strip().lower()


def fecha(v):
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v
    try:
        return datetime.strptime(str(v).strip()[:10], "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def leer_csv(ruta):
    if not ruta.exists():
        return []
    with open(ruta, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def bloque(texto, nombre):
    """El bloque de primer nivel `nombre:` de un YAML sencillo como {clave: valor} (sin depender de PyYAML)."""
    m = re.search(rf"^{nombre}:[ \t]*(?:#.*)?\n((?:[ \t]+.*\n?|[ \t]*\n)*)", texto, re.M)
    datos = {}
    for linea in (m.group(1).splitlines() if m else []):
        k = re.match(r"^[ \t]+([A-Za-z_][\w-]*):[ \t]*(.*?)[ \t]*(#.*)?$", linea)
        if k:
            datos[k.group(1)] = k.group(2).strip().strip("\"'")
    return datos


def frontmatter(texto):
    """Las claves del encabezado `---` de una definición de reporte, como {clave: valor en texto}."""
    m = re.match(r"\A---\s*\n(.*?)\n---", texto, re.S)
    datos = {}
    for linea in (m.group(1).splitlines() if m else []):
        k = re.match(r"^([A-Za-z_][\w-]*):[ \t]*(.*?)[ \t]*(#.*)?$", linea)
        if k:
            datos[k.group(1)] = k.group(2).strip().strip("\"'")
    return datos


def proyectos(raiz):
    """[(carpeta, etiqueta)] de los proyectos de la empresa y de sus subproyectos."""
    salida = []
    for p in sorted((raiz / "proyectos").glob("*")) if (raiz / "proyectos").is_dir() else []:
        if (p / "proyecto.yaml").exists():
            salida.append((p, p.name))
            salida += [(s, f"{p.name}/{s.name}") for s in sorted((p / "subproyectos").glob("*")) if (s / "proyecto.yaml").exists()]
    return salida


def pendientes(carpeta, hoy):
    """[(fecha, tipo, texto)] de todo lo abierto y con fecha de un proyecto: pasado y futuro."""
    items = []

    def abierto(fila, permisivo=False):
        estado = sin_tildes(fila.get("estado"))
        return estado not in CERRADO + EN_PAUSA if permisivo else estado in ABIERTO

    for x in leer_csv(carpeta / "cronograma" / "cronograma.csv"):
        try:
            avance = float(str(x.get("avance_pct") or 0).replace(",", "."))
        except ValueError:
            avance = 0
        if sin_tildes(x.get("es_hito")) in ("si", "x", "1", "true") and avance < 100 and abierto(x, permisivo=True):
            items.append((fecha(x.get("fin_plan")), "hito", f"Hito: {x.get('tarea')}"))
    for archivo, etiqueta, clave in (("seguimiento/acuerdos.csv", "Acuerdo", "acuerdo"), ("riesgos/issues.csv", "Problema", "titulo")):
        for x in leer_csv(carpeta / archivo):
            if abierto(x):
                quien = f" ({x.get('responsable')})" if (x.get("responsable") or "").strip() else ""
                items.append((fecha(x.get("fecha_compromiso")), etiqueta.lower(), f"{etiqueta}: {x.get(clave)}{quien}"))
    for x in leer_csv(carpeta / "seguimiento" / "vencimientos.csv"):
        if abierto(x):
            items.append((fecha(x.get("fecha")), (x.get("tipo") or "vencimiento").strip().lower(), x.get("compromiso") or "vencimiento"))
    for x in leer_csv(carpeta / "riesgos" / "riesgos.csv"):
        if abierto(x, permisivo=True):
            items.append((fecha(x.get("fecha_revision")), "riesgo", f"Revisar el riesgo: {x.get('titulo')}"))
    yml = (carpeta / "proyecto.yaml").read_text(encoding="utf-8", errors="replace")
    post = bloque(yml, "postulacion")
    if post and sin_tildes(post.get("resultado") or "pendiente") == "pendiente" and sin_tildes(post.get("decision_go")) != "no_go":
        hora = f" a las {post['hora_cierre']}" if post.get("hora_cierre") else ""
        items.append((fecha(post.get("fecha_cierre")), "cierre", f"Cierre de la postulación{hora}"))
        for x in leer_csv(carpeta / "postulacion" / "calendario.csv"):
            if abierto(x, permisivo=True):
                items.append((fecha(x.get("fecha")), (x.get("tipo") or "hito").strip().lower(), x.get("hito") or "hito de la postulación"))
    return [i for i in items if i[0]]


def periodo(definicion, hoy):
    if sin_tildes(definicion.get("periodo_archivo")).startswith("mes") or sin_tildes(definicion.get("cadencia")) == "mensual":
        return f"{hoy:%Y-%m}"
    anio, semana, _ = hoy.isocalendar()
    return f"{anio}-S{semana:02d}"


def toca_hoy(dia, hoy):
    """True si `dia` (de la definición del reporte) cae hoy: día de la semana, números del mes o `ultimo`."""
    for v in re.split(r"[,;/ ]+", sin_tildes(dia)):
        if v in DIAS and DIAS.index(v) == hoy.weekday():
            return True
        if v.isdigit() and int(v) == hoy.day:
            return True
        if v in ("ultimo", "fin") and hoy.day == calendar.monthrange(hoy.year, hoy.month)[1]:
            return True
    return False


def reportes_de_hoy(carpeta, hoy):
    """[(tipo, nombre, período)] de los reportes del catálogo que tocan hoy y no están emitidos en su período."""
    salida = []
    emitidos = [x.name for x in (carpeta / "reportes" / "emitidos").rglob("*") if x.is_file()] if (carpeta / "reportes" / "emitidos").is_dir() else []
    for d in sorted((carpeta / "reportes" / "catalogo").glob("*.md")) if (carpeta / "reportes" / "catalogo").is_dir() else []:
        if d.name.startswith("_"):
            continue
        definicion = frontmatter(d.read_text(encoding="utf-8", errors="replace"))
        dia = definicion.get("dia") or definicion.get("programacion") or ""
        if not dia or not toca_hoy(dia, hoy):
            continue
        tipo, per = definicion.get("tipo") or d.stem, periodo(definicion, hoy)
        if not any(n.startswith(tipo + "_") and per in n for n in emitidos):
            salida.append((tipo, definicion.get("nombre") or tipo, per))
    return salida


def reunir(raiz, hoy, dias):
    """{"vencido": [...], "hoy": [...], "proximos": [...], "reportes": [...], "pausa": [...]} de toda la empresa."""
    r = {"vencido": [], "hoy": [], "proximos": [], "reportes": [], "pausa": [], "proyectos": 0}
    for carpeta, etiqueta in proyectos(raiz):
        yml = (carpeta / "proyecto.yaml").read_text(encoding="utf-8", errors="replace")
        estado = sin_tildes(bloque(yml, "proyecto").get("estado"))
        if estado in EN_PAUSA:
            r["pausa"].append(etiqueta)
            continue
        if estado in CERRADO:
            continue
        r["proyectos"] += 1
        for f, tipo, texto in pendientes(carpeta, hoy):
            destino = "vencido" if f < hoy else ("hoy" if f == hoy else ("proximos" if f <= hoy + timedelta(days=dias) else None))
            if destino:
                r[destino].append((f, etiqueta, tipo, texto))
        r["reportes"] += [(etiqueta, *x) for x in reportes_de_hoy(carpeta, hoy)]
    for k in ("vencido", "hoy", "proximos"):
        r[k].sort(key=lambda x: (x[0], x[1]))
    return r


def texto(r, hoy, dias):
    """La agenda como texto para el chat. Cadena vacía si no hay proyectos activos ni nada que decir."""
    if not (r["vencido"] or r["hoy"] or r["proximos"] or r["reportes"] or r["pausa"]):
        return "" if not r["proyectos"] else f"Agenda del {hoy:%d-%m-%Y}: nada vencido y nada con fecha en los próximos {dias} días."
    nombre_dia = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"][hoy.weekday()]
    out = [f"# Agenda del {nombre_dia} {hoy:%d-%m-%Y}"]

    def seccion(titulo, items, formato):
        if not items:
            return
        out.append(f"\n## {titulo} ({len(items)})")
        out.extend(formato(x) for x in items[:MAXIMO])
        if len(items) > MAXIMO:
            out.append(f"- … y {len(items) - MAXIMO} más (python herramientas/agenda.py)")

    seccion("Vencido", r["vencido"], lambda x: f"- [{x[1]}] {x[3]} · venció el {x[0]:%d-%m} (hace {(hoy - x[0]).days} día(s))")
    seccion("Hoy", r["hoy"], lambda x: f"- [{x[1]}] {x[3]}")
    seccion(f"Próximos {dias} días", r["proximos"],
            lambda x: f"- {x[0]:%d-%m} ({'mañana' if (x[0] - hoy).days == 1 else f'en {(x[0] - hoy).days} días'}) · [{x[1]}] {x[3]}")
    seccion("Reportes que tocan hoy", r["reportes"], lambda x: f"- [{x[0]}] {x[2]} (`{x[1]}`): aún no emitido para {x[3]}")
    if r["pausa"]:
        out.append(f"\nEn pausa (no se listan sus pendientes): {', '.join(r['pausa'])}.")
    return "\n".join(out)


def del_dia(raiz=RAIZ, hoy=None, dias=14, una_vez=False):
    """El texto de la agenda. Con `una_vez`, cadena vacía si ya se mostró hoy en este computador (y deja la marca)."""
    hoy = hoy or date.today()
    marca = Path(raiz) / MARCA
    if una_vez:
        if marca.exists() and marca.read_text(encoding="utf-8").strip() == hoy.isoformat():
            return ""
        marca.parent.mkdir(parents=True, exist_ok=True)
        marca.write_text(hoy.isoformat() + "\n", encoding="utf-8")
    return texto(reunir(Path(raiz), hoy, dias), hoy, dias)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dias", type=int, default=14, help="cuántos días hacia adelante (por defecto 14)")
    ap.add_argument("--hoy", help="fecha AAAA-MM-DD (por defecto, hoy)")
    ap.add_argument("--una-vez", dest="una_vez", action="store_true", help="no repetir si ya se mostró hoy")
    a = ap.parse_args()
    hoy = fecha(a.hoy) if a.hoy else date.today()
    if hoy is None:
        sys.exit("Fecha inválida (usar AAAA-MM-DD).")
    if _nucleo.es_mantenedor(RAIZ):
        print("Esta es la carpeta donde se mantiene el núcleo: no tiene proyectos propios que agendar.")
        return 0
    salida = del_dia(RAIZ, hoy, max(1, a.dias), a.una_vez)
    print(salida or ("" if a.una_vez else "Sin proyectos activos con pendientes."))
    return 0


if __name__ == "__main__":
    import _consola
    _consola.preparar()
    sys.exit(main())
