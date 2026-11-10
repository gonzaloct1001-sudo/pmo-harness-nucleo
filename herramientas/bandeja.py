#!/usr/bin/env python3
"""Bandeja de la empresa en GitHub (modo nube): pedidos, preguntas, resultados y el resumen diario, solo por REST.

Uso:
    python herramientas/bandeja.py --listar [--breve]                  # pedidos, preguntas y PRs de la nube
    python herramientas/bandeja.py --nueva "<pedido>" [--proyecto slug]
    python herramientas/bandeja.py --responder <n> "<respuesta>"
    python herramientas/bandeja.py --pregunta <n> "<pregunta>"         # (desde la nube) deja una decisión pendiente
    python herramientas/bandeja.py --tomar <n> | --terminar <n> [--pr <url>]   # (desde la nube) estado de un pedido
    python herramientas/bandeja.py --integrar <n>                      # integra el PR n (squash) y borra su rama
    python herramientas/bandeja.py --resumen [--publicar] [--hoy AAAA-MM-DD]   # resumen diario (y lo deja en el issue)
    python herramientas/bandeja.py --etiquetas                         # crea las etiquetas en el repositorio

Funciona con `gh api` (REST): sirve en el PC y en la nube, donde `gh issue` y `gh pr` no están disponibles. El
repositorio sale de .harness/nube.yaml o del remoto `origin`. Para pruebas, HARNESS_GH puede apuntar a un `gh` falso.
"""
import argparse
import json
import os
import re
import shlex
import subprocess
import sys
from datetime import date, datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ETIQUETAS = {"harness:tarea": ("0E8A16", "Pedido para la nube"), "harness:resumen": ("1D76DB", "Resumen diario / status"),
             "estado:en-curso": ("FBCA04", "Una corrida lo está trabajando"), "estado:espera-usuario": ("D93F0B", "Hay una pregunta para el usuario"),
             "estado:hecho": ("5319E7", "Terminado")}
RAMA_NUBE = "nube/"


def comando_gh():
    override = os.environ.get("HARNESS_GH")
    return shlex.split(override, posix=(os.name != "nt")) if override else ["gh"]


def api(ruta, metodo="GET", datos=None, paginar=False):
    """Llama a la API REST de GitHub con gh. Devuelve (ok, json o texto)."""
    cmd = comando_gh() + ["api", ruta, "-X", metodo, "-H", "Accept: application/vnd.github+json"]
    if paginar:
        cmd.append("--paginate")
    entrada = None
    if datos is not None:
        cmd += ["--input", "-"]
        entrada = json.dumps(datos)
    try:
        r = subprocess.run(cmd, cwd=RAIZ, capture_output=True, text=True, encoding="utf-8", errors="replace", input=entrada, timeout=60)
    except (OSError, subprocess.TimeoutExpired) as e:
        return False, str(e)
    salida = (r.stdout or "").strip()
    if r.returncode != 0:
        return False, (r.stderr or salida).strip()
    try:
        return True, json.loads(salida) if salida else {}
    except json.JSONDecodeError:
        return True, salida


def repositorio():
    try:
        import yaml
        ruta = RAIZ / ".harness" / "nube.yaml"
        if ruta.exists():
            repo = (yaml.safe_load(ruta.read_text(encoding="utf-8")) or {}).get("repositorio")
            if repo:
                return repo
    except Exception:
        pass
    try:
        r = subprocess.run(["git", "remote", "get-url", "origin"], cwd=RAIZ, capture_output=True, text=True, timeout=10)
        m = re.search(r"github\.com[:/]([^/]+/[^/\s]+?)(\.git)?$", r.stdout.strip())
        return m.group(1) if m else ""
    except (OSError, subprocess.TimeoutExpired):
        return ""


def etiquetas_de(issue):
    return {l.get("name") for l in issue.get("labels") or [] if isinstance(l, dict)}


def issues_abiertos(repo):
    ok, datos = api(f"repos/{repo}/issues?state=open&per_page=100", paginar=True)
    if not ok:
        return ok, datos
    if isinstance(datos, dict):
        datos = [datos]
    return True, [i for i in datos if "pull_request" not in i]


def prs_nube(repo):
    ok, datos = api(f"repos/{repo}/pulls?state=open&per_page=100")
    if not ok:
        return ok, datos
    return True, [p for p in (datos if isinstance(datos, list) else [])
                  if p.get("state") == "open" and not p.get("merged") and (p.get("head") or {}).get("ref", "").startswith(RAMA_NUBE)]


def hace_horas(iso):
    try:
        t = datetime.strptime(iso, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - t).total_seconds() / 3600
    except (TypeError, ValueError):
        return 0.0


def listar(repo, breve):
    ok, issues = issues_abiertos(repo)
    if not ok:
        print(f"No se pudo leer la bandeja de {repo}: {issues}")
        return 1
    ok2, prs = prs_nube(repo)
    tareas = [i for i in issues if "harness:tarea" in etiquetas_de(i)]
    preguntas = [i for i in issues if "estado:espera-usuario" in etiquetas_de(i)]
    en_curso = [i for i in tareas if "estado:en-curso" in etiquetas_de(i)]
    pendientes = [i for i in tareas if not (etiquetas_de(i) & {"estado:en-curso", "estado:hecho", "estado:espera-usuario"})]
    if breve:
        partes = []
        if pendientes:
            partes.append(f"{len(pendientes)} pedido(s) por tomar")
        if en_curso:
            partes.append(f"{len(en_curso)} en curso")
        if preguntas:
            partes.append(f"{len(preguntas)} pregunta(s) para ti (" + ", ".join(f"#{i['number']}" for i in preguntas[:4]) + ")")
        if ok2 and prs:
            partes.append(f"{len(prs)} PR de la nube esperando tu revisión (" + ", ".join(f"#{p['number']}" for p in prs[:4]) + ")")
        print("Bandeja: " + ("; ".join(partes) if partes else "vacía") + ".")
        return 0
    print(f"# Bandeja · {repo}\n")
    print(f"## Pedidos por tomar ({len(pendientes)})")
    for i in pendientes:
        print(f"- #{i['number']} {i.get('title')}")
    print(f"\n## En curso ({len(en_curso)})")
    for i in en_curso:
        print(f"- #{i['number']} {i.get('title')} · desde hace {hace_horas(i.get('updated_at')):.1f} h")
    print(f"\n## Preguntas para ti ({len(preguntas)})")
    for i in preguntas:
        print(f"- #{i['number']} {i.get('title')} → responde con: python herramientas/bandeja.py --responder {i['number']} \"...\"")
    print(f"\n## PRs de la nube esperando revisión ({len(prs) if ok2 else '?'})")
    for p in (prs if ok2 else []):
        print(f"- #{p['number']} {p.get('title')} ({(p.get('head') or {}).get('ref')}) → python herramientas/bandeja.py --integrar {p['number']}")
    return 0


def etiquetas(repo):
    hechas = []
    for nombre, (color, desc) in ETIQUETAS.items():
        ok, r = api(f"repos/{repo}/labels", "POST", {"name": nombre, "color": color, "description": desc})
        hechas.append(f"{nombre}: {'creada' if ok else 'ya existía' if '422' in str(r) or 'already_exists' in str(r) else 'error ' + str(r)[:80]}")
    print("\n".join(f"- {h}" for h in hechas))
    return 0


def poner_etiqueta(repo, n, nombre):
    return api(f"repos/{repo}/issues/{n}/labels", "POST", {"labels": [nombre]})


def quitar_etiqueta(repo, n, nombre):
    return api(f"repos/{repo}/issues/{n}/labels/{nombre}", "DELETE")


def comentar(repo, n, texto):
    return api(f"repos/{repo}/issues/{n}/comments", "POST", {"body": texto})


def nueva(repo, texto, proyecto):
    titulo = texto.strip().splitlines()[0][:80]
    cuerpo = texto.strip() + (f"\n\nProyecto: `{proyecto}`" if proyecto else "") + "\n\n_Pedido para la nube (bandeja del PMO Harness)._"
    ok, r = api(f"repos/{repo}/issues", "POST", {"title": titulo, "body": cuerpo, "labels": ["harness:tarea"]})
    if not ok:
        print(f"No se pudo crear el pedido: {r}")
        return 1
    print(f"Pedido #{r.get('number')} creado: {titulo}. La próxima corrida de «bandeja» lo toma.")
    return 0


def responder(repo, n, texto):
    ok, r = comentar(repo, n, texto)
    if not ok:
        print(f"No se pudo responder: {r}")
        return 1
    quitar_etiqueta(repo, n, "estado:espera-usuario")
    print(f"Respuesta publicada en #{n}; la próxima corrida la aplica.")
    return 0


def pregunta(repo, n, texto):
    ok, r = comentar(repo, n, "**Pregunta para el usuario:** " + texto + "\n\nResponde aquí mismo (o desde el PC: `bandeja.py --responder "
                     + str(n) + " \"...\"`).")
    if not ok:
        print(f"No se pudo dejar la pregunta: {r}")
        return 1
    poner_etiqueta(repo, n, "estado:espera-usuario")
    quitar_etiqueta(repo, n, "estado:en-curso")
    print(f"Pregunta dejada en #{n} (estado: espera al usuario).")
    return 0


def tomar(repo, n):
    ok, issue = api(f"repos/{repo}/issues/{n}")
    if not ok:
        print(f"No se pudo leer #{n}: {issue}")
        return 1
    et = etiquetas_de(issue)
    if "estado:en-curso" in et and hace_horas(issue.get("updated_at")) < 3:
        print(f"#{n} ya está en curso hace menos de 3 h: no se toma (una tarea a la vez).")
        return 2
    poner_etiqueta(repo, n, "estado:en-curso")
    comentar(repo, n, f"En curso desde {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC (corrida en la nube).")
    print(f"#{n} tomado.")
    return 0


def terminar(repo, n, pr):
    poner_etiqueta(repo, n, "estado:hecho")
    quitar_etiqueta(repo, n, "estado:en-curso")
    comentar(repo, n, "Terminado." + (f" Resultado en {pr}." if pr else ""))
    print(f"#{n} terminado.")
    return 0


def integrar(repo, n):
    ok, pr = api(f"repos/{repo}/pulls/{n}")
    if not ok:
        print(f"No se pudo leer el PR #{n}: {pr}")
        return 1
    if pr.get("merged"):
        print(f"El PR #{n} ya está integrado.")
        return 0
    if pr.get("state") != "open":
        print(f"El PR #{n} no está abierto ({pr.get('state')}).")
        return 1
    if pr.get("mergeable") is False:
        print(f"El PR #{n} tiene conflictos: la próxima corrida debe actualizar su rama; no se integra a ciegas.")
        return 1
    ok, r = api(f"repos/{repo}/pulls/{n}/merge", "PUT", {"merge_method": "squash"})
    if not ok:
        print(f"No se pudo integrar #{n}: {r}")
        return 1
    rama = (pr.get("head") or {}).get("ref", "")
    if rama:
        api(f"repos/{repo}/git/refs/heads/{rama}", "DELETE")
    print(f"PR #{n} integrado (squash) y rama {rama} borrada. En el PC: `git pull` antes de seguir.")
    return 0


def resumen(repo, hoy, publicar):
    lineas = [f"# Resumen diario · {hoy.isoformat()}", ""]
    try:
        sys.path.insert(0, str(RAIZ / "herramientas"))
        import status as _status
        breve = _status.resumen_breve(RAIZ, hoy)
        lineas += ["## Proyectos"] + ([f"- {x}" for x in breve] if breve else ["- sin proyectos con datos"]) + [""]
    except Exception as e:
        lineas += [f"## Proyectos", f"- (no se pudo calcular el status: {e})", ""]
    try:
        import investigacion as _inv
        abiertas = _inv.resumen_estado(RAIZ)
        if abiertas:
            lineas += ["## Investigaciones abiertas"] + [f"- {x}" for x in abiertas] + [""]
    except Exception:
        pass
    try:
        import finanzas as _fin
        pend = []
        for p in sorted((RAIZ / "proyectos").glob("*")):
            if (p / "finanzas").is_dir() and (p / "proyecto.yaml").exists():
                fz = _fin.Finanzas(p)
                sc = fz.periodos_sin_cerrar()
                if sc:
                    pend.append(f"{p.name}: sin cerrar {', '.join(sc)}")
        if pend:
            lineas += ["## Finanzas"] + [f"- {x}" for x in pend] + [""]
    except Exception:
        pass
    if repo:
        ok, issues = issues_abiertos(repo)
        if ok:
            tareas = [i for i in issues if "harness:tarea" in etiquetas_de(i)]
            preguntas = [i for i in issues if "estado:espera-usuario" in etiquetas_de(i)]
            ok2, prs = prs_nube(repo)
            lineas += ["## Bandeja",
                       f"- Pedidos abiertos: {len(tareas)} · preguntas para ti: {len(preguntas)}" + (" (" + ", ".join(f"#{i['number']}" for i in preguntas) + ")" if preguntas else "")
                       + f" · PRs de la nube por revisar: {len(prs) if ok2 else '?'}" + (" (" + ", ".join(f"#{p['number']}" for p in prs) + ")" if ok2 and prs else ""), ""]
    texto = "\n".join(lineas).rstrip() + "\n"
    print(texto)
    if publicar and repo:
        ok, issues = issues_abiertos(repo)
        destino = next((i for i in (issues if ok else []) if "harness:resumen" in etiquetas_de(i) and i.get("title", "").startswith("Resumen diario")), None)
        if not destino:
            ok, destino = api(f"repos/{repo}/issues", "POST", {"title": "Resumen diario", "labels": ["harness:resumen"],
                                                               "body": "Aquí deja cada mañana su resumen la tarea programada «resumen-manana». Responde en los issues que menciona."})
            if not ok:
                print(f"No se pudo crear el issue del resumen: {destino}")
                return 1
        ok, r = comentar(repo, destino.get("number"), texto)
        print(f"Publicado en el issue #{destino.get('number')}." if ok else f"No se pudo publicar: {r}")
        return 0 if ok else 1
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--listar", action="store_true")
    ap.add_argument("--breve", action="store_true")
    ap.add_argument("--nueva", metavar="TEXTO")
    ap.add_argument("--proyecto", default="")
    ap.add_argument("--responder", nargs=2, metavar=("N", "TEXTO"))
    ap.add_argument("--pregunta", nargs=2, metavar=("N", "TEXTO"))
    ap.add_argument("--tomar", type=int, metavar="N")
    ap.add_argument("--terminar", type=int, metavar="N")
    ap.add_argument("--pr", default="")
    ap.add_argument("--integrar", type=int, metavar="N")
    ap.add_argument("--resumen", action="store_true")
    ap.add_argument("--publicar", action="store_true")
    ap.add_argument("--etiquetas", action="store_true")
    ap.add_argument("--repositorio")
    ap.add_argument("--hoy")
    a = ap.parse_args()
    hoy = date.fromisoformat(a.hoy) if a.hoy else date.today()
    repo = a.repositorio or repositorio()
    if a.resumen:
        return resumen(repo, hoy, a.publicar)
    if not repo:
        sys.exit("No encuentro el repositorio de la empresa en GitHub (.harness/nube.yaml o remoto origin). Indícalo con --repositorio owner/repo.")
    if a.listar:
        return listar(repo, a.breve)
    if a.etiquetas:
        return etiquetas(repo)
    if a.nueva:
        return nueva(repo, a.nueva, a.proyecto)
    if a.responder:
        return responder(repo, int(a.responder[0]), a.responder[1])
    if a.pregunta:
        return pregunta(repo, int(a.pregunta[0]), a.pregunta[1])
    if a.tomar:
        return tomar(repo, a.tomar)
    if a.terminar:
        return terminar(repo, a.terminar, a.pr)
    if a.integrar:
        return integrar(repo, a.integrar)
    return listar(repo, True)


if __name__ == "__main__":
    import _consola
    _consola.preparar()
    sys.exit(main())
