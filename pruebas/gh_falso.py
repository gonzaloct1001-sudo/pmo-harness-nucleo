#!/usr/bin/env python3
"""GitHub CLI falso para la batería de pruebas de la bandeja: responde a `gh api` con datos fijos y anota cada llamada.

Uso (lo hace la batería): HARNESS_GH="python pruebas/gh_falso.py" HARNESS_GH_LOG=<archivo> python herramientas/bandeja.py ...
Estado simulado: issue #3 (pedido sin estado), #4 (en curso hace 5 h), #5 (pregunta al usuario), #7 (resumen diario);
PR #9 de la rama nube/3-minuta (abierto, sin conflictos), PR #10 ya integrado.
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone

HACE_1H = (datetime.now(timezone.utc) - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
args = sys.argv[1:]
log = os.environ.get("HARNESS_GH_LOG")
entrada = sys.stdin.read() if "--input" in args else ""
if log:
    with open(log, "a", encoding="utf-8") as f:
        f.write(" ".join(args) + (" <<< " + entrada if entrada else "") + "\n")

if args[:1] != ["api"]:
    print(json.dumps({"error": "solo api"}))
    sys.exit(1)
ruta = args[1]
metodo = args[args.index("-X") + 1] if "-X" in args else "GET"
L = lambda n: {"name": n}  # noqa: E731
issues = [
    {"number": 3, "title": "Minuta del comité de ayer", "labels": [L("harness:tarea")], "updated_at": "2026-11-10T10:00:00Z"},
    {"number": 4, "title": "Revisar riesgos del proyecto X", "labels": [L("harness:tarea"), L("estado:en-curso")], "updated_at": HACE_1H},
    {"number": 5, "title": "¿Qué logo usar en el informe?", "labels": [L("harness:tarea"), L("estado:espera-usuario")], "updated_at": "2026-11-10T09:00:00Z"},
    {"number": 7, "title": "Resumen diario", "labels": [L("harness:resumen")], "updated_at": "2026-11-10T08:00:00Z"},
    {"number": 8, "title": "Un PR disfrazado", "labels": [], "pull_request": {"url": "x"}, "updated_at": "2026-11-10T08:00:00Z"},
]
prs = [{"number": 9, "title": "Minuta del comité (nube)", "state": "open", "merged": False, "mergeable": True, "head": {"ref": "nube/3-minuta"}},
       {"number": 10, "title": "Vieja", "state": "closed", "merged": True, "mergeable": None, "head": {"ref": "nube/1-x"}},
       {"number": 11, "title": "Del PC", "state": "open", "merged": False, "mergeable": True, "head": {"ref": "fix/algo"}}]


def salir(obj, codigo=0):
    print(json.dumps(obj))
    sys.exit(codigo)


if ruta.startswith("repos/") and "/issues?" in ruta and metodo == "GET":
    salir(issues)
if "/pulls?" in ruta and metodo == "GET":
    salir(prs)
if "/labels" in ruta and metodo == "POST" and "/issues/" not in ruta:
    datos = json.loads(entrada or "{}")
    if datos.get("name") == "harness:tarea":
        print("gh: HTTP 422: Validation Failed (already_exists)", file=sys.stderr)
        sys.exit(1)
    salir({"name": datos.get("name")})
if "/issues/" in ruta and ruta.endswith("/labels") and metodo == "POST":
    salir([L(x) for x in json.loads(entrada or "{}").get("labels", [])])
if "/issues/" in ruta and "/labels/" in ruta and metodo == "DELETE":
    salir([])
if "/issues/" in ruta and ruta.endswith("/comments") and metodo == "POST":
    salir({"id": 100, "body": json.loads(entrada or "{}").get("body")})
if ruta.endswith("/issues") and metodo == "POST":
    datos = json.loads(entrada or "{}")
    salir({"number": 12, "title": datos.get("title"), "labels": [L(x) for x in datos.get("labels", [])]})
if "/issues/" in ruta and metodo == "GET":
    n = int(ruta.rsplit("/", 1)[1])
    salir(next((i for i in issues if i["number"] == n), {"message": "Not Found"}), 0 if any(i["number"] == n for i in issues) else 1)
if "/pulls/" in ruta and ruta.endswith("/merge") and metodo == "PUT":
    salir({"merged": True, "sha": "abc123"})
if "/pulls/" in ruta and metodo == "GET":
    n = int(ruta.rsplit("/", 1)[1])
    salir(next((p for p in prs if p["number"] == n), {"message": "Not Found"}))
if "/git/refs/heads/" in ruta and metodo == "DELETE":
    salir({})
print("gh falso: ruta no simulada " + ruta, file=sys.stderr)
sys.exit(1)
