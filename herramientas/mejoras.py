#!/usr/bin/env python3
"""Mejoras al núcleo: registro local de ideas, aprendizajes y fallos del harness mismo, para entregarlos al mantenedor.

Nadie edita el núcleo en una carpeta de empresa. Lo que falta, sobra, estorba o falla se anota aquí; cuando el usuario
quiere, se exporta anonimizado y se lo entrega al mantenedor; el mantenedor decide; la versión nueva trae la decisión
y la actualización cierra lo resuelto. El registro es un log: conserva la versión sobre la que se hizo cada anotación
y crece con el tiempo.

Uso en una carpeta de empresa:
    python herramientas/mejoras.py                       # resumen por estado y cuántas hay sin enviar
    python herramientas/mejoras.py --listar [--todas]    # abiertas (nueva, enviada) o todas
    python herramientas/mejoras.py --anotar --tipo <agregar|quitar|cambiar|aprendizaje|fallo> --donde <skill, herramienta o regla>
                                   --que "<qué>" --evidencia "<archivo, comando o mensaje>" [--por-que "<motivo>"] [--quien <asistente>]
    python herramientas/mejoras.py --exportar [--salida <ruta>]   # archivo anonimizado para el mantenedor; marca «enviada»
    python herramientas/mejoras.py --cerrar-resueltas    # cruza con MEJORAS.md del núcleo instalado (lo llama actualizar_nucleo.py)
Uso en la carpeta del núcleo (mantenedor):
    python herramientas/mejoras.py --procesar <archivo exportado>   # suma las anotaciones a MEJORAS.md como «pendiente»
    python herramientas/mejoras.py --decidir <id> <aceptada|rechazada|diferida> [--version <x.y.z>] [--nota "<texto>"]

Las anotaciones no llevan datos del cliente. La exportación además reemplaza nombres de empresa, personas y proyectos
(de empresa.yaml y proyecto.yaml), correos, RUT y montos por marcadores; el usuario revisa el archivo antes de enviarlo.
"""
import argparse
import csv
import hashlib
import io
import re
import sys
from datetime import date
from pathlib import Path

import _nucleo

RAIZ = Path(__file__).resolve().parent.parent
REGISTRO = Path(".harness") / "mejoras-nucleo.csv"
MEJORAS_MD = "MEJORAS.md"
COLUMNAS = ["id", "fecha", "version_nucleo", "asistente", "tipo", "donde", "que", "por_que", "evidencia", "estado",
            "id_envio", "enviada_el", "decision", "version_resuelta", "nota_mantenedor"]
EXPORTADAS = ["id", "fecha", "version_nucleo", "asistente", "tipo", "donde", "que", "por_que", "evidencia"]
TABLA = ["id", "recibida", "version_origen", "tipo", "donde", "que", "decision", "version", "nota"]
TIPOS = ("agregar", "quitar", "cambiar", "aprendizaje", "fallo")
DECISIONES = ("aceptada", "rechazada", "diferida")
ABIERTAS = ("nueva", "enviada")
CABECERA = """# Mejoras recibidas de las carpetas de empresa

Cada fila llegó por `python herramientas/mejoras.py --exportar` desde una carpeta de empresa (el id empieza por el
origen anónimo de esa carpeta). El mantenedor decide con `mejoras.py --decidir`; la versión que resuelve una mejora se
cita en `CHANGELOG.md`, y la actualización cierra la anotación en la carpeta que la envió.
"""


# ---------------------------------------------------------------- registro de la carpeta de empresa
def leer(raiz):
    ruta = Path(raiz) / REGISTRO
    if not ruta.exists():
        return []
    with open(ruta, encoding="utf-8", newline="") as f:
        return [{c: (r.get(c) or "") for c in COLUMNAS} for r in csv.DictReader(f)]


def escribir(raiz, filas):
    ruta = Path(raiz) / REGISTRO
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with open(ruta, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNAS)
        w.writeheader()
        w.writerows(filas)


def norm(texto):
    return re.sub(r"\s+", " ", (texto or "").strip().lower())


def version_tupla(v):
    return tuple(int(x) for x in re.findall(r"\d+", v or "")) or (0,)


def origen(raiz):
    """Identificador anónimo y estable de la carpeta (hash del nombre de la empresa): distingue envíos sin nombrarla."""
    nombre = ""
    ey = Path(raiz) / "empresa" / "empresa.yaml"
    if ey.exists():
        m = re.search(r"^\s+nombre:\s*\"?([^\"#\n]+?)\"?\s*(#.*)?$", ey.read_text(encoding="utf-8", errors="replace"), re.M)
        nombre = m.group(1).strip() if m else ""
    if not nombre or nombre.upper() == "PENDIENTE":
        nombre = str(Path(raiz).resolve()).lower()
    return hashlib.sha1(nombre.encode("utf-8")).hexdigest()[:6]


def anotar(raiz, tipo, donde, que, evidencia, por_que="", quien="sistema", hoy=None):
    """Agrega una anotación y devuelve su id; si ya había una abierta con el mismo dónde y qué, devuelve ese id.
    None en la carpeta del núcleo (ahí el núcleo se cambia directamente)."""
    raiz = Path(raiz)
    if _nucleo.es_mantenedor(raiz):
        return None
    if tipo not in TIPOS:
        raise ValueError("tipo debe ser uno de: " + ", ".join(TIPOS))
    if not (donde or "").strip() or not (que or "").strip() or not (evidencia or "").strip():
        raise ValueError("faltan --donde, --que o --evidencia: una anotación sin evidencia no le sirve al mantenedor")
    filas = leer(raiz)
    for f in filas:
        if f["estado"] in ABIERTAS and norm(f["donde"]) == norm(donde) and norm(f["que"]) == norm(que):
            return f["id"]
    n = max((int(f["id"].rsplit("-", 1)[-1]) for f in filas if re.match(r"^M-\d+$", f["id"])), default=0) + 1
    fila = {c: "" for c in COLUMNAS}
    fila.update(id=f"M-{n:03d}", fecha=(hoy or date.today()).isoformat(), version_nucleo=_nucleo.version(raiz) or "?",
                asistente=(quien or "sistema").strip(), tipo=tipo, donde=donde.strip(), que=que.strip(),
                por_que=(por_que or "").strip(), evidencia=evidencia.strip(), estado="nueva")
    filas.append(fila)
    escribir(raiz, filas)
    return fila["id"]


def resumen(raiz):
    filas = leer(raiz)
    r = {e: 0 for e in ("nueva", "enviada", "resuelta", "rechazada", "diferida")}
    for f in filas:
        r[f["estado"]] = r.get(f["estado"], 0) + 1
    r["total"] = len(filas)
    return r


# ---------------------------------------------------------------- exportación anonimizada
def terminos_sensibles(raiz):
    """Nombres de empresa, personas y proyectos (empresa.yaml, proyecto.yaml y slugs) que la exportación reemplaza."""
    raiz = Path(raiz)
    terminos = set()
    archivos = [raiz / "empresa" / "empresa.yaml"] + sorted(raiz.glob("proyectos/*/proyecto.yaml")) \
        + sorted(raiz.glob("proyectos/*/subproyectos/*/proyecto.yaml"))
    patron = re.compile(r"^\s*(nombre|razon_social|representante_legal|cliente|organizacion|mandante|contraparte):\s*\"?([^\"#\n]+?)\"?\s*(#.*)?$", re.M)
    for a in archivos:
        if not a.exists():
            continue
        for m in patron.finditer(a.read_text(encoding="utf-8", errors="replace")):
            v = m.group(2).strip()
            if len(v) >= 4 and v.upper() != "PENDIENTE":
                terminos.add(v)
    for p in raiz.glob("proyectos/*"):
        if p.is_dir() and len(p.name) >= 4:
            terminos.add(p.name)
    return sorted(terminos, key=len, reverse=True)


def anonimizar(texto, terminos):
    t = texto or ""
    for term in terminos:
        t = re.sub(re.escape(term), "[nombre]", t, flags=re.I)
    t = re.sub(r"[\w.+-]+@[\w-]+\.[\w.]+", "[correo]", t)
    t = re.sub(r"\b\d{1,2}\.\d{3}\.\d{3}-[\dkK]\b", "[rut]", t)
    t = re.sub(r"(?:\$|USD|CLP|UF)\s?[\d.,]+|\b\d{1,3}(?:\.\d{3}){2,}(?:,\d+)?\b", "[monto]", t)
    return t


def exportar(raiz, salida=None, hoy=None):
    """Escribe el archivo anonimizado con las anotaciones «nueva» y las marca «enviada». (ruta, cantidad) o (None, 0)."""
    raiz = Path(raiz)
    filas = leer(raiz)
    nuevas = [f for f in filas if f["estado"] == "nueva"]
    if not nuevas:
        return None, 0
    hoy = hoy or date.today()
    org, terminos = origen(raiz), terminos_sensibles(raiz)
    salida = Path(salida) if salida else raiz / ".harness" / f"mejoras-export-{hoy.isoformat()}.md"
    lineas = [f"# Mejoras al núcleo del PMO Harness · envío {org} del {hoy.isoformat()}", "",
              f"Núcleo {_nucleo.version(raiz) or '?'} · {len(nuevas)} anotación(es) · anonimizado por mejoras.py. Revísalo antes de "
              "enviarlo al mantenedor: no debe llevar nombres, correos, RUT ni montos.", "",
              "| id | fecha | versión | tipo | dónde | qué | por qué | evidencia |", "|---|---|---|---|---|---|---|---|"]
    exportadas = []
    for f in nuevas:
        f["id_envio"], f["estado"], f["enviada_el"] = f"{org}-{f['id']}", "enviada", hoy.isoformat()
        e = {c: (anonimizar(f[c], terminos) if c in ("donde", "que", "por_que", "evidencia") else f[c]) for c in EXPORTADAS}
        e["id"] = f["id_envio"]
        exportadas.append(e)
        lineas.append("| " + " | ".join(e[c].replace("|", "/").replace("\n", " ") for c in EXPORTADAS) + " |")
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=EXPORTADAS, lineterminator="\n")
    w.writeheader()
    w.writerows(exportadas)
    lineas += ["", "```csv", buf.getvalue().rstrip("\n"), "```", ""]
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text("\n".join(lineas), encoding="utf-8")
    escribir(raiz, filas)
    return salida, len(nuevas)


# ---------------------------------------------------------------- MEJORAS.md (lo escribe el mantenedor; lo leen las carpetas)
def tabla_mejoras(raiz):
    """Filas de la tabla de MEJORAS.md por id."""
    ruta = Path(raiz) / MEJORAS_MD
    filas = {}
    if not ruta.exists():
        return filas
    for linea in ruta.read_text(encoding="utf-8", errors="replace").splitlines():
        if not linea.startswith("| ") or linea.startswith("| id ") or linea.startswith("| ---"):
            continue
        celdas = [c.strip() for c in linea.strip().strip("|").split("|")]
        if len(celdas) >= len(TABLA):
            filas[celdas[0]] = dict(zip(TABLA, celdas[:len(TABLA)]))
    return filas


def escribir_tabla(raiz, filas):
    ruta = Path(raiz) / MEJORAS_MD
    texto = ruta.read_text(encoding="utf-8") if ruta.exists() else CABECERA
    cabeza = texto.split("| id |")[0].rstrip("\n")
    lineas = [cabeza, "", "| id | recibida | versión origen | tipo | dónde | qué | decisión | versión | nota |",
              "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for f in filas.values():
        lineas.append("| " + " | ".join(f[c].replace("|", "/") for c in TABLA) + " |")
    ruta.write_text("\n".join(lineas) + "\n", encoding="utf-8")


def procesar(raiz, archivo, hoy=None):
    """Mantenedor: suma a MEJORAS.md las anotaciones de un archivo exportado. Devuelve los ids nuevos."""
    texto = Path(archivo).read_text(encoding="utf-8", errors="replace")
    m = re.search(r"```csv\n(.*?)\n```", texto, re.S)
    if not m:
        raise ValueError("el archivo no trae el bloque csv que escribe mejoras.py --exportar")
    tabla, nuevos = tabla_mejoras(raiz), []
    for n in csv.DictReader(io.StringIO(m.group(1))):
        if not n.get("id") or n["id"] in tabla:
            continue
        que = n.get("que", "") + (" — " + n["por_que"] if n.get("por_que") else "") + " · evidencia: " + n.get("evidencia", "")
        tabla[n["id"]] = dict(id=n["id"], recibida=(hoy or date.today()).isoformat(), version_origen=n.get("version_nucleo", ""),
                              tipo=n.get("tipo", ""), donde=n.get("donde", ""), que=que, decision="pendiente", version="", nota="")
        nuevos.append(n["id"])
    escribir_tabla(raiz, tabla)
    return nuevos


def decidir(raiz, id_, decision, version="", nota=""):
    if decision not in DECISIONES:
        raise ValueError("la decisión debe ser una de: " + ", ".join(DECISIONES))
    tabla = tabla_mejoras(raiz)
    if id_ not in tabla:
        raise ValueError(f"{id_} no está en {MEJORAS_MD}")
    tabla[id_].update(decision=decision, version=version or tabla[id_]["version"], nota=nota or tabla[id_]["nota"])
    escribir_tabla(raiz, tabla)
    return tabla[id_]


def cerrar_resueltas(raiz):
    """Carpeta de empresa: cruza las anotaciones enviadas con MEJORAS.md del núcleo instalado. Devuelve [(id, estado)]."""
    raiz = Path(raiz)
    filas, tabla = leer(raiz), tabla_mejoras(raiz)
    actual, cambios = version_tupla(_nucleo.version(raiz)), []
    for f in filas:
        d = tabla.get(f["id_envio"]) if f["id_envio"] else None
        if not d or f["estado"] not in ("enviada", "diferida"):
            continue
        if d["decision"] == "aceptada" and d["version"] and version_tupla(d["version"]) <= actual:
            nuevo = "resuelta"
        elif d["decision"] in ("rechazada", "diferida"):
            nuevo = d["decision"]
        else:
            continue
        if nuevo != f["estado"] or f["nota_mantenedor"] != d["nota"]:
            f.update(estado=nuevo, decision=d["decision"], version_resuelta=d["version"] if nuevo == "resuelta" else "",
                     nota_mantenedor=d["nota"])
            cambios.append((f["id"], nuevo))
    if cambios:
        escribir(raiz, filas)
    return cambios


# ---------------------------------------------------------------- consola
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--listar", action="store_true")
    ap.add_argument("--todas", action="store_true")
    ap.add_argument("--anotar", action="store_true")
    ap.add_argument("--tipo", choices=TIPOS)
    ap.add_argument("--donde")
    ap.add_argument("--que")
    ap.add_argument("--por-que", dest="por_que", default="")
    ap.add_argument("--evidencia")
    ap.add_argument("--quien", default="")
    ap.add_argument("--exportar", action="store_true")
    ap.add_argument("--salida")
    ap.add_argument("--cerrar-resueltas", dest="cerrar", action="store_true")
    ap.add_argument("--procesar", metavar="ARCHIVO")
    ap.add_argument("--decidir", nargs=2, metavar=("ID", "DECISION"))
    ap.add_argument("--version", default="")
    ap.add_argument("--nota", default="")
    ap.add_argument("--hoy", help="fecha AAAA-MM-DD (pruebas)")
    a = ap.parse_args()
    hoy = date.fromisoformat(a.hoy) if a.hoy else None
    mantenedor = _nucleo.es_mantenedor(RAIZ)

    if a.procesar or a.decidir:
        if not mantenedor:
            sys.exit("--procesar y --decidir son del mantenedor: se usan en la carpeta del núcleo (pmo.mantenedor).")
        if a.procesar:
            nuevos = procesar(RAIZ, a.procesar, hoy)
            print(f"{len(nuevos)} anotación(es) nueva(s) en {MEJORAS_MD}" + (": " + ", ".join(nuevos) if nuevos else "")
                  + "\nDecide cada una con: python herramientas/mejoras.py --decidir <id> aceptada|rechazada|diferida --version x.y.z --nota \"...\"")
        else:
            f = decidir(RAIZ, a.decidir[0], a.decidir[1], a.version, a.nota)
            print(f"{f['id']}: {f['decision']}" + (f" en la versión {f['version']}" if f["version"] else "") + (f" · {f['nota']}" if f["nota"] else "")
                  + "\nCita el id en CHANGELOG.md al publicar; la actualización cerrará la anotación en la carpeta de origen.")
        return 0

    if a.anotar:
        if mantenedor:
            sys.exit("Esta es la carpeta del núcleo que mantienes: el núcleo se cambia directamente y se registra en CHANGELOG.md.")
        if not a.tipo:
            sys.exit("--anotar necesita --tipo (" + ", ".join(TIPOS) + "), --donde, --que y --evidencia.")
        try:
            antes = {f["id"] for f in leer(RAIZ)}
            id_ = anotar(RAIZ, a.tipo, a.donde or "", a.que or "", a.evidencia or "", a.por_que, a.quien, hoy)
        except ValueError as e:
            sys.exit(str(e))
        r = resumen(RAIZ)
        if id_ in antes:
            print(f"Ya estaba anotada como {id_} (mismo dónde y qué). Sin enviar: {r['nueva']}.")
        else:
            print(f"Anotada {id_} ({a.tipo}, {a.donde}) sobre el núcleo {_nucleo.version(RAIZ) or '?'}. Sin enviar: {r['nueva']}. "
                  "Para entregarlas al mantenedor: python herramientas/mejoras.py --exportar")
        return 0

    if a.exportar:
        ruta, n = exportar(RAIZ, a.salida, hoy)
        if not ruta:
            print("No hay anotaciones sin enviar.")
            return 0
        print(f"{n} anotación(es) exportada(s) a {ruta.relative_to(RAIZ).as_posix() if ruta.is_relative_to(RAIZ) else ruta}\n"
              "Revisa el archivo (no debe llevar datos del cliente) y entrégaselo al mantenedor del núcleo.")
        return 0

    if a.cerrar:
        cambios = cerrar_resueltas(RAIZ)
        print("Sin novedades del mantenedor." if not cambios else
              "Con respuesta del mantenedor: " + ", ".join(f"{i} {e}" for i, e in cambios))
        return 0

    filas = leer(RAIZ)
    r = resumen(RAIZ)
    if a.listar:
        mostrar = filas if a.todas else [f for f in filas if f["estado"] in ABIERTAS]
        if not mostrar:
            print("Sin anotaciones" + ("" if a.todas else " abiertas") + ".")
        for f in mostrar:
            extra = f" · {f['decision']} {f['version_resuelta']} {f['nota_mantenedor']}".rstrip() if f["decision"] else ""
            print(f"- {f['id']} [{f['estado']}] {f['fecha']} v{f['version_nucleo']} {f['tipo']} · {f['donde']}: {f['que']}"
                  + (f" (por qué: {f['por_que']})" if f["por_que"] else "") + f" · evidencia: {f['evidencia']}{extra}")
        return 0
    print(f"Mejoras al núcleo anotadas en esta carpeta: {r['total']} (sin enviar {r['nueva']}, enviadas {r['enviada']}, "
          f"resueltas {r['resuelta']}, rechazadas {r['rechazada']}, diferidas {r['diferida']}).")
    if r["nueva"]:
        print("Siguiente paso: python herramientas/mejoras.py --exportar (cuando el usuario quiera entregarlas al mantenedor).")
    elif not r["total"]:
        print("Se anota con: python herramientas/mejoras.py --anotar --tipo ... --donde ... --que ... --evidencia ...")
    return 0


if __name__ == "__main__":
    import _consola
    _consola.preparar()
    sys.exit(main())
