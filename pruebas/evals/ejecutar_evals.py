#!/usr/bin/env python3
"""Evals de comportamiento: ¿el asistente hace lo que las reglas y las skills dicen? (para quien mantiene el núcleo)

La batería (`pruebas/ejecutar_pruebas.py`) prueba los scripts. Esto prueba lo otro: se le da al asistente un pedido
real en una empresa de prueba y se revisa qué respondió y qué tocó.

Uso:
    python pruebas/evals/ejecutar_evals.py --listar
    python pruebas/evals/ejecutar_evals.py [--solo id,id] [--asistente "<comando con {mensaje}>"] [--conservar]

- Arma una empresa temporal con el núcleo de esta carpeta, copia los proyectos de ejemplo que piden los escenarios y
  deja un commit de base. Por cada escenario: prepara sus archivos, le entrega el mensaje al asistente (una sola
  vuelta, sin interfaz), revisa el resultado y vuelve la carpeta a la base.
- Asistente por defecto: `claude -p {mensaje} --output-format json --permission-mode acceptEdits` (Claude Code en
  modo consola). Otro asistente: `--asistente "<comando>"` o la variable HARNESS_EVAL_ASISTENTE; `{mensaje}` se
  reemplaza por el pedido. Cada escenario es una conversación real: consume cuota del plan del asistente.
- Escenarios: `pruebas/evals/escenarios.yaml` (qué prueba cada uno y qué se espera). Comprobaciones disponibles:
  respuesta_contiene_todas / respuesta_contiene_alguna / respuesta_no_contiene (sin distinguir tildes ni mayúsculas),
  cambia / crea / sin_cambios_en (patrones de ruta), sin_cambios, nucleo_intacto, sin_confidenciales_en_git.
- Resultado: una línea por escenario, el detalle de lo que falló y un archivo en `pruebas/evals/resultados/`
  (local, no se sube). Código 1 si algún escenario falla. Un escenario que falla no siempre es un error del núcleo:
  léelo, y si la regla o la skill no fue clara, ese es el arreglo.
"""
import argparse
import json
import os
import shlex
import shutil
import stat
import subprocess
import sys
import tempfile
import unicodedata
from datetime import datetime
from fnmatch import fnmatch
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
AQUI = Path(__file__).resolve().parent
POR_DEFECTO = "claude -p {mensaje} --output-format json --permission-mode acceptEdits"
RUIDO = (".harness/sesiones/*", ".harness/agenda-vista.txt", ".harness/uso-skills.csv", ".harness/entropia-ultima.txt",
         "status/historial/*", "*/__pycache__/*", "*.pyc")
IDENTIDAD = {"GIT_AUTHOR_NAME": "Evals", "GIT_AUTHOR_EMAIL": "evals@ejemplo.cl", "GIT_COMMITTER_NAME": "Evals",
             "GIT_COMMITTER_EMAIL": "evals@ejemplo.cl"}


def plano(texto):
    return "".join(c for c in unicodedata.normalize("NFD", str(texto or "")) if unicodedata.category(c) != "Mn").lower()


def git(carpeta, *args):
    r = subprocess.run(["git", "-c", "core.quotepath=false", *args], cwd=carpeta, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env={**os.environ, **IDENTIDAD})
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def borrar(ruta):
    def forzar(funcion, camino, _):
        os.chmod(camino, stat.S_IWRITE)
        funcion(camino)
    shutil.rmtree(ruta, onerror=forzar)


def cargar_escenarios(ruta):
    import yaml
    datos = yaml.safe_load(Path(ruta).read_text(encoding="utf-8")) or {}
    escenarios = datos.get("escenarios") or []
    ids = [e.get("id") for e in escenarios]
    if len(ids) != len(set(ids)) or not all(ids):
        sys.exit(f"{ruta}: cada escenario necesita un `id` distinto")
    return escenarios


def armar_empresa(tmp, escenarios):
    """Empresa de prueba con el núcleo de esta carpeta, los proyectos de ejemplo pedidos y un commit de base."""
    r = subprocess.run([sys.executable, "herramientas/nueva_empresa.py", "Empresa de evaluación", "--destino", str(tmp), "--slug",
                        "eval", "--sin-github"], cwd=RAIZ, capture_output=True, text=True, encoding="utf-8", errors="replace",
                       env={**os.environ, **IDENTIDAD})
    carpeta = Path(tmp) / "eval"
    if r.returncode != 0 or not carpeta.is_dir():
        sys.exit("No se pudo armar la empresa de prueba:\n" + ((r.stdout or "") + (r.stderr or ""))[-800:])
    for base in sorted({e["base"] for e in escenarios if e.get("base")}):
        origen = RAIZ / base
        if not (origen / "proyecto.yaml").exists():
            sys.exit(f"El escenario pide la base «{base}», que no es un proyecto de ejemplo")
        shutil.copytree(origen, carpeta / "proyectos" / origen.name, ignore=shutil.ignore_patterns("__pycache__"))
    git(carpeta, "add", "-A")
    rc, salida = git(carpeta, "commit", "-q", "-m", "Base de los evals")
    if rc != 0:
        sys.exit("No se pudo dejar el commit de base de los evals:\n" + salida[-600:])
    return carpeta, git(carpeta, "rev-parse", "HEAD")[1].strip()


def preguntar(asistente, mensaje, carpeta, tiempo):
    """(respuesta, error) del asistente al mensaje, en una sola vuelta."""
    piezas = shlex.split(asistente)  # en Windows, escribe las rutas del comando con / (C:/...) para que no se pierdan
    args = [a.replace("{mensaje}", mensaje) for a in piezas]
    if not any("{mensaje}" in a for a in piezas):
        args.append(mensaje)
    args[0] = shutil.which(args[0]) or args[0]  # en Windows la consola de un asistente suele ser un .cmd
    try:
        r = subprocess.run(args, cwd=carpeta, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=tiempo,
                           env={**os.environ, **IDENTIDAD}, stdin=subprocess.DEVNULL)
    except FileNotFoundError:
        sys.exit(f"No encuentro el asistente «{args[0]}». Instala su consola o indica otro comando con --asistente "
                 "\"<comando con {mensaje}>\" (o la variable HARNESS_EVAL_ASISTENTE).")
    except subprocess.TimeoutExpired:
        return "", f"el asistente no respondió en {tiempo} s"
    salida = (r.stdout or "").strip()
    try:
        datos = json.loads(salida)
        if isinstance(datos, dict) and isinstance(datos.get("result"), str):
            salida = datos["result"]
    except ValueError:
        pass
    return salida, ("" if r.returncode == 0 else f"el asistente terminó con código {r.returncode}: {(r.stderr or '')[-300:]}")


def cambios(carpeta, base):
    """(rutas cambiadas, rutas nuevas) desde el commit de base: lo que quedó sin guardar y lo que el asistente guardó."""
    _, estado = git(carpeta, "status", "--porcelain", "--untracked-files=all")
    tocadas, nuevas = set(), set()
    for linea in estado.splitlines():
        ruta = linea[3:].strip().strip('"').split(" -> ")[-1]
        tocadas.add(ruta)
        if linea.startswith(("??", "A ")):
            nuevas.add(ruta)
    _, guardadas = git(carpeta, "diff", "--name-status", f"{base}..HEAD")
    for linea in guardadas.splitlines():
        partes = linea.split("\t")
        if len(partes) >= 2:
            tocadas.add(partes[-1])
            if partes[0].startswith("A"):
                nuevas.add(partes[-1])
    limpio = lambda rutas: {r for r in rutas if not any(fnmatch(r, p) for p in RUIDO)}  # noqa: E731
    return limpio(tocadas), limpio(nuevas)


def revisar(escenario, respuesta, carpeta, base):
    """Lista de comprobaciones que no se cumplen (vacía = el escenario pasa)."""
    espera, fallas = escenario.get("espera") or {}, []
    texto = plano(respuesta)
    tocadas, nuevas = cambios(carpeta, base)
    lista = lambda clave: [espera[clave]] if isinstance(espera.get(clave), str) else list(espera.get(clave) or [])  # noqa: E731
    faltan = [x for x in lista("respuesta_contiene_todas") if plano(x) not in texto]
    if faltan:
        fallas.append("la respuesta no dice: " + ", ".join(f"«{x}»" for x in faltan))
    alguna = lista("respuesta_contiene_alguna")
    if alguna and not any(plano(x) in texto for x in alguna):
        fallas.append("la respuesta no dice ninguna de: " + ", ".join(f"«{x}»" for x in alguna))
    sobran = [x for x in lista("respuesta_no_contiene") if plano(x) in texto]
    if sobran:
        fallas.append("la respuesta dice lo que no debía: " + ", ".join(f"«{x}»" for x in sobran))
    for patron in lista("cambia"):
        if not any(fnmatch(r, patron) for r in tocadas):
            fallas.append(f"no cambió nada que calce con {patron}")
    for patron in lista("crea"):
        if not any(fnmatch(r, patron) for r in nuevas):
            fallas.append(f"no creó nada que calce con {patron}")
    for patron in lista("sin_cambios_en"):
        tocados = sorted(r for r in tocadas if fnmatch(r, patron))
        if tocados:
            fallas.append(f"cambió lo que no debía ({patron}): " + ", ".join(tocados[:4]))
    if espera.get("sin_cambios") and tocadas:
        fallas.append("no debía cambiar nada y cambió: " + ", ".join(sorted(tocadas)[:6]))
    if espera.get("nucleo_intacto"):
        sys.path.insert(0, str(RAIZ / "herramientas"))
        import _nucleo
        d = _nucleo.desviaciones(carpeta) or {"modificados": [], "faltantes": []}
        if d["modificados"] or d["faltantes"]:
            fallas.append("tocó el núcleo: " + ", ".join((d["modificados"] + d["faltantes"])[:4]))
    if espera.get("sin_confidenciales_en_git"):
        sys.path.insert(0, str(RAIZ / "herramientas" / "hooks"))
        import _comun
        _, versionados = git(carpeta, "ls-files")
        _, historia = git(carpeta, "log", "--all", "--name-only", "--format=")
        malos = sorted({r.strip() for r in (versionados + "\n" + historia).splitlines() if r.strip() and _comun.motivo_sensible(r.strip(), carpeta)})
        _, preparados = git(carpeta, "diff", "--cached", "--name-only")
        malos += [r for r in preparados.splitlines() if r.strip() and _comun.motivo_sensible(r.strip(), carpeta) and r not in malos]
        if malos:
            fallas.append("dejó confidenciales en Git: " + ", ".join(malos[:4]))
    return fallas


def restaurar(carpeta, base, preparados):
    git(carpeta, "reset", "-q", "--hard", base)
    git(carpeta, "clean", "-qfd")
    for ruta in preparados:  # los archivos de preparación pueden estar en carpetas que Git ignora (_entrada/)
        (carpeta / ruta).unlink(missing_ok=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--listar", action="store_true", help="mostrar los escenarios sin ejecutar nada")
    ap.add_argument("--solo", help="ids de los escenarios a ejecutar, separados por coma")
    ap.add_argument("--asistente", help="comando del asistente, con {mensaje} donde va el pedido")
    ap.add_argument("--escenarios", default=str(AQUI / "escenarios.yaml"), help="archivo de escenarios")
    ap.add_argument("--tiempo", type=int, default=600, help="segundos de espera por escenario")
    ap.add_argument("--conservar", action="store_true", help="no borrar la empresa de prueba (para mirar qué quedó)")
    ap.add_argument("--sin-archivo", dest="sin_archivo", action="store_true", help="no escribir el resultado en resultados/")
    a = ap.parse_args()
    for flujo in (sys.stdout, sys.stderr):
        try:
            flujo.reconfigure(encoding="utf-8")
        except Exception:
            pass
    escenarios = cargar_escenarios(a.escenarios)
    if a.solo:
        pedidos = [x.strip() for x in a.solo.split(",") if x.strip()]
        escenarios = [e for e in escenarios if e["id"] in pedidos]
        if len(escenarios) != len(pedidos):
            sys.exit("No existe alguno de los escenarios pedidos; revisa --listar")
    if a.listar:
        print(f"# Escenarios ({len(escenarios)})\n")
        for e in escenarios:
            print(f"- {e['id']}: {e.get('que_prueba', '')}\n  pedido: «{e.get('mensaje', '')}»")
        return 0
    if not escenarios:
        sys.exit("No hay escenarios que ejecutar.")
    asistente = a.asistente or os.environ.get("HARNESS_EVAL_ASISTENTE") or POR_DEFECTO
    tmp = Path(tempfile.mkdtemp(prefix="pmo-evals-"))
    lineas, pasan = [], 0
    try:
        carpeta, base = armar_empresa(tmp, escenarios)
        print(f"Empresa de prueba lista. {len(escenarios)} escenario(s) con: {asistente}\n")
        for e in escenarios:
            preparados = []
            for archivo in e.get("prepara") or []:
                destino = carpeta / archivo["archivo"]
                destino.parent.mkdir(parents=True, exist_ok=True)
                destino.write_text(str(archivo.get("contenido", "")), encoding="utf-8")
                preparados.append(archivo["archivo"])
            if e.get("guardar_preparacion"):
                git(carpeta, "add", "-A")
                git(carpeta, "commit", "-q", "-m", "Preparación del escenario")
            desde = git(carpeta, "rev-parse", "HEAD")[1].strip()
            respuesta, error = preguntar(asistente, str(e.get("mensaje", "")), carpeta, a.tiempo)
            fallas = ([error] if error else []) + revisar(e, respuesta, carpeta, desde)
            pasan += not fallas
            lineas.append(f"{'OK   ' if not fallas else 'FALLA'} {e['id']}: {e.get('que_prueba', '')}")
            lineas += [f"      - {f}" for f in fallas]
            if fallas:
                lineas.append("      respuesta: " + " ".join(respuesta.split())[:400])
            print("\n".join(lineas[-(len(fallas) + 1 + bool(fallas)):]))
            restaurar(carpeta, base, preparados)
    finally:
        if a.conservar:
            print(f"\nLa empresa de prueba quedó en {tmp / 'eval'}")
        else:
            borrar(tmp)
    resumen = f"{pasan} de {len(escenarios)} escenarios pasan."
    print("\n" + resumen)
    if not a.sin_archivo:
        destino = AQUI / "resultados" / f"{datetime.now():%Y-%m-%d_%H%M}.md"
        destino.parent.mkdir(exist_ok=True)
        destino.write_text(f"# Evals de comportamiento · {datetime.now():%Y-%m-%d %H:%M}\n\nAsistente: `{asistente}`\n\n```\n"
                           + "\n".join(lineas) + f"\n```\n\n{resumen}\n", encoding="utf-8")
        print(f"Detalle guardado en {destino.relative_to(RAIZ).as_posix()}")
    return 0 if pasan == len(escenarios) else 1


if __name__ == "__main__":
    sys.exit(main())
