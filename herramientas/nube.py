#!/usr/bin/env python3
"""Modo nube (opcional, solo Claude): registro de las tareas programadas de la empresa en .harness/nube.yaml.

Uso:
    python herramientas/nube.py --estado                       # qué está activado, catálogo y requisitos
    python herramientas/nube.py --catalogo                     # tareas que se pueden programar
    python herramientas/nube.py --habilitar --quien "Nombre" [--repositorio owner/repo]
    python herramientas/nube.py --deshabilitar --quien "Nombre" --motivo "..."
    python herramientas/nube.py --agregar <tarea> --quien "Nombre" [--cron "0 8 * * 1-5"] [--zona America/Santiago]
                                [--id-remoto trig_xxx] [--nota "..."]
    python herramientas/nube.py --pausar <tarea> --quien "Nombre" | --reanudar <tarea> --quien "Nombre" | --quitar <tarea> --quien "Nombre"
    python herramientas/nube.py --id-remoto-de <tarea> trig_xxx          # anotar el id de la tarea creada en claude.ai
    python herramientas/nube.py --instruccion <tarea>          # texto para pegar al crear la tarea programada
    python herramientas/nube.py --revisar                      # consistencia del registro y requisitos del PC

Nada de esto crea ni modifica tareas en la nube: solo lleva el registro de lo que el usuario aprobó (quién y cuándo) y
prepara los textos. La tarea en la nube la crea la skill `nube` con la aprobación explícita del usuario.
"""
import argparse
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parent.parent
REGISTRO = RAIZ / ".harness" / "nube.yaml"
CATALOGO = {
    "resumen-manana": {"nombre": "Resumen de la mañana", "cron": "0 8 * * 1-5",
                       "que_hace": "Resumen diario de la empresa (semáforos, vencimientos, decisiones, investigaciones abiertas, meses de "
                                   "finanzas sin cerrar y bandeja) como comentario en el issue «Resumen diario», con aviso al teléfono."},
    "bandeja": {"nombre": "Trabajar la bandeja", "cron": "0 9,13,17 * * 1-5",
                "que_hace": "Toma el siguiente pedido de la bandeja (issue harness:tarea sin estado) y lo trabaja en una rama propia con "
                            "un PR; las decisiones quedan como preguntas."},
    "status-semanal": {"nombre": "Status semanal", "cron": "0 9 * * 1",
                       "que_hace": "Status de todos los proyectos como reporte, en el issue «Status semanal»."},
    "recordatorio-cierre": {"nombre": "Recordatorio de cierre mensual", "cron": "0 9 10 * *",
                            "que_hace": "En los proyectos de finanzas, qué meses siguen sin cerrar y la checklist del cierre."},
}
RE_CRON = re.compile(r"^(\S+\s+){4}\S+$")


def cargar():
    if not REGISTRO.exists():
        return {"habilitada": False, "repositorio": "", "aviso_telefono": True, "tareas": [], "historial": []}
    datos = yaml.safe_load(REGISTRO.read_text(encoding="utf-8")) or {}
    datos.setdefault("tareas", [])
    datos.setdefault("historial", [])
    return datos


def guardar(datos):
    REGISTRO.parent.mkdir(parents=True, exist_ok=True)
    texto = ("# Modo nube del PMO Harness (opcional, solo Claude). Lo administra herramientas/nube.py y la skill `nube`.\n"
             "# Cada tarea queda con quién la aprobó y cuándo; las tareas se crean en claude.ai/code (routines) con ese sí.\n"
             + yaml.safe_dump(datos, allow_unicode=True, sort_keys=False))
    REGISTRO.write_text(texto, encoding="utf-8")


def anotar(datos, quien, accion, hoy):
    datos.setdefault("historial", []).append({"fecha": hoy.isoformat(), "quien": quien, "accion": accion})


def empresa():
    ruta = RAIZ / "empresa" / "empresa.yaml"
    if ruta.exists():
        m = re.search(r"^  nombre:\s*(.+)$", ruta.read_text(encoding="utf-8"), re.M)
        if m:
            return m.group(1).split("#")[0].strip().strip("\"'")
    return "(sin empresa)"


def repositorio_detectado():
    estado = RAIZ / ".harness" / "estado.yaml"
    url = ""
    if estado.exists():
        m = re.search(r"^repositorio_remoto:\s*\"?([^\"\n]+?)\"?\s*$", estado.read_text(encoding="utf-8"), re.M)
        if m and m.group(1) not in ("pendiente", ""):
            url = m.group(1)
    if not url:
        try:
            r = subprocess.run(["git", "remote", "get-url", "origin"], cwd=RAIZ, capture_output=True, text=True, timeout=10)
            url = r.stdout.strip() if r.returncode == 0 else ""
        except (OSError, subprocess.TimeoutExpired):
            url = ""
    m = re.search(r"github\.com[:/]([^/]+/[^/\s]+?)(\.git)?$", url)
    return m.group(1) if m else ""


def tarea(datos, tid):
    return next((t for t in datos["tareas"] if t.get("id") == tid), None)


def revisar(datos):
    errores, avisos = [], []
    if datos.get("habilitada") and not datos.get("repositorio"):
        errores.append("modo nube habilitado sin repositorio (owner/repo).")
    for t in datos["tareas"]:
        if t.get("id") not in CATALOGO:
            errores.append(f"tarea «{t.get('id')}» no está en el catálogo.")
        if not RE_CRON.match(str(t.get("cron", ""))):
            errores.append(f"tarea {t.get('id')}: cron «{t.get('cron')}» no tiene 5 campos.")
        if not t.get("creada_por"):
            errores.append(f"tarea {t.get('id')}: sin quién la aprobó (creada_por).")
        if t.get("habilitada") and not t.get("id_remoto"):
            avisos.append(f"tarea {t.get('id')}: habilitada en el registro pero sin id de la tarea en la nube (anótalo con --id-remoto-de).")
    ids = [t.get("id") for t in datos["tareas"]]
    if len(ids) != len(set(ids)):
        errores.append("hay tareas repetidas en el registro.")
    if shutil.which("gh") is None:
        avisos.append("GitHub CLI (gh) no está instalado en este PC: la bandeja no se puede consultar desde aquí.")
    else:
        try:
            r = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True, timeout=15)
            if r.returncode != 0:
                avisos.append("GitHub CLI sin sesión (gh auth login): la bandeja no se puede consultar desde aquí.")
        except (OSError, subprocess.TimeoutExpired):
            avisos.append("no se pudo comprobar la sesión de GitHub CLI.")
    return errores, avisos


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--estado", action="store_true")
    ap.add_argument("--catalogo", action="store_true")
    ap.add_argument("--habilitar", action="store_true")
    ap.add_argument("--deshabilitar", action="store_true")
    ap.add_argument("--agregar", metavar="TAREA")
    ap.add_argument("--pausar", metavar="TAREA")
    ap.add_argument("--reanudar", metavar="TAREA")
    ap.add_argument("--quitar", metavar="TAREA")
    ap.add_argument("--id-remoto-de", nargs=2, metavar=("TAREA", "ID"))
    ap.add_argument("--instruccion", metavar="TAREA")
    ap.add_argument("--revisar", action="store_true")
    ap.add_argument("--repositorio")
    ap.add_argument("--cron")
    ap.add_argument("--zona", default="")
    ap.add_argument("--id-remoto", default="")
    ap.add_argument("--nota", default="")
    ap.add_argument("--quien", default="")
    ap.add_argument("--motivo", default="")
    ap.add_argument("--hoy")
    a = ap.parse_args()
    hoy = date.fromisoformat(a.hoy) if a.hoy else date.today()
    datos = cargar()

    if a.catalogo:
        print("# Tareas que se pueden programar en la nube\n")
        for tid, c in CATALOGO.items():
            print(f"- `{tid}` · {c['nombre']} · por defecto `{c['cron']}` · {c['que_hace']}")
        return 0
    if a.instruccion:
        if a.instruccion not in CATALOGO:
            sys.exit(f"Tarea desconocida: {a.instruccion}. Ver --catalogo.")
        print(f"Eres el asistente del PMO Harness en la nube para la empresa «{empresa()}». Lee `NUBE.md` y `AGENTS.md` del "
              f"repositorio y ejecuta la tarea «{a.instruccion}» ({CATALOGO[a.instruccion]['nombre']}) tal como la describe el "
              "catálogo de `NUBE.md`, cumpliendo sus reglas: modo automático, rama propia y PR (nunca main), una tarea a la vez, "
              "GitHub solo por REST con `gh api` o `herramientas/bandeja.py`. Si no puedes hacerla, deja un comentario en el issue "
              "«Resumen diario» diciendo por qué.")
        return 0
    if a.habilitar:
        if not a.quien:
            sys.exit("Indica --quien: el modo nube se activa con el sí explícito del usuario.")
        repo = a.repositorio or datos.get("repositorio") or repositorio_detectado()
        if not repo:
            sys.exit("No encuentro el repositorio privado de la empresa en GitHub: indícalo con --repositorio owner/repo (o crea el repositorio con la skill instalar).")
        datos["habilitada"], datos["repositorio"] = True, repo
        anotar(datos, a.quien, "habilita el modo nube", hoy)
        guardar(datos)
        print(f"Modo nube habilitado para {repo} por {a.quien}. Todavía no hay tareas: cada una se agrega con su sí (--agregar).")
        return 0
    if a.deshabilitar:
        if not (a.quien and a.motivo):
            sys.exit("Indica --quien y --motivo.")
        datos["habilitada"] = False
        for t in datos["tareas"]:
            t["habilitada"] = False
        anotar(datos, a.quien, f"deshabilita el modo nube: {a.motivo}", hoy)
        guardar(datos)
        print("Modo nube deshabilitado en el registro. Recuerda pausar o borrar las tareas en claude.ai/code (la skill nube lo hace contigo): "
              + ", ".join(t.get("id_remoto") or t.get("id") for t in datos["tareas"]) if datos["tareas"] else "Modo nube deshabilitado.")
        return 0
    if a.agregar:
        if a.agregar not in CATALOGO:
            sys.exit(f"Tarea desconocida: {a.agregar}. Ver --catalogo.")
        if not a.quien:
            sys.exit("Indica --quien: cada tarea se programa con el sí explícito del usuario.")
        if not datos.get("habilitada"):
            sys.exit("Primero habilita el modo nube (--habilitar --quien).")
        cron = a.cron or CATALOGO[a.agregar]["cron"]
        if not RE_CRON.match(cron):
            sys.exit("El cron debe tener 5 campos (minuto hora día mes día-semana), por ejemplo «0 8 * * 1-5».")
        t = tarea(datos, a.agregar)
        if t:
            t.update({"cron": cron, "zona_horaria": a.zona or t.get("zona_horaria", ""), "habilitada": True,
                      "id_remoto": a.id_remoto or t.get("id_remoto", ""), "nota": a.nota or t.get("nota", "")})
            accion = f"actualiza la tarea {a.agregar} ({cron})"
        else:
            datos["tareas"].append({"id": a.agregar, "nombre": CATALOGO[a.agregar]["nombre"], "cron": cron, "zona_horaria": a.zona,
                                    "habilitada": True, "id_remoto": a.id_remoto, "creada_por": a.quien, "fecha": hoy.isoformat(), "nota": a.nota})
            accion = f"aprueba la tarea {a.agregar} ({cron}{' ' + a.zona if a.zona else ''})"
        anotar(datos, a.quien, accion, hoy)
        guardar(datos)
        print(f"Tarea {a.agregar} registrada: cron «{cron}»{' (' + a.zona + ')' if a.zona else ''}, aprobada por {a.quien}."
              + ("" if a.id_remoto else " Falta crearla en la nube y anotar su id (--id-remoto-de)."))
        return 0
    for accion, tid in (("pausar", a.pausar), ("reanudar", a.reanudar), ("quitar", a.quitar)):
        if tid:
            if not a.quien:
                sys.exit("Indica --quien.")
            t = tarea(datos, tid)
            if not t:
                sys.exit(f"No hay una tarea {tid} en el registro.")
            if accion == "quitar":
                datos["tareas"] = [x for x in datos["tareas"] if x.get("id") != tid]
            else:
                t["habilitada"] = accion == "reanudar"
            anotar(datos, a.quien, f"{accion} la tarea {tid}", hoy)
            guardar(datos)
            print(f"Tarea {tid}: {accion} registrado por {a.quien}." + (f" Aplica lo mismo en la nube (id {t.get('id_remoto')})." if t.get("id_remoto") else ""))
            return 0
    if a.id_remoto_de:
        tid, rid = a.id_remoto_de
        t = tarea(datos, tid)
        if not t:
            sys.exit(f"No hay una tarea {tid} en el registro.")
        t["id_remoto"] = rid
        anotar(datos, a.quien or "asistente", f"anota el id de la tarea {tid} en la nube: {rid}", hoy)
        guardar(datos)
        print(f"Tarea {tid} ↔ {rid}.")
        return 0
    errores, avisos = revisar(datos)
    if a.revisar:
        print("# Revisión del modo nube\n")
        for e in errores:
            print(f"- ERROR: {e}")
        for w in avisos:
            print(f"- aviso: {w}")
        print(f"\nResultado: {len(errores)} error(es), {len(avisos)} aviso(s)." + (" OK." if not errores else ""))
        return 1 if errores else 0
    # --estado (por defecto)
    print(f"# Modo nube · {empresa()}\n")
    if not datos.get("habilitada"):
        print("- Desactivado (opcional). Para saber cómo funciona y activarlo: skill `nube` («quiero operar desde el celular»).")
    else:
        print(f"- Activado para {datos.get('repositorio')} · aviso al teléfono: {'sí' if datos.get('aviso_telefono', True) else 'no'}")
    if datos["tareas"]:
        print("- Tareas programadas:")
        for t in datos["tareas"]:
            print(f"  - {t.get('id')} ({t.get('nombre')}): {'activa' if t.get('habilitada') else 'pausada'} · cron «{t.get('cron')}»"
                  f"{' ' + t.get('zona_horaria') if t.get('zona_horaria') else ''} · aprobada por {t.get('creada_por')} el {t.get('fecha')}"
                  + (f" · nube {t.get('id_remoto')}" if t.get("id_remoto") else " · sin id en la nube"))
    else:
        print("- Sin tareas programadas.")
    print("- Catálogo: " + ", ".join(f"{tid} ({c['cron']})" for tid, c in CATALOGO.items()))
    if errores or avisos:
        print("- Revisión: " + "; ".join(errores + avisos))
    return 0


if __name__ == "__main__":
    import _consola
    _consola.preparar()
    sys.exit(main())
