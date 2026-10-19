#!/usr/bin/env python3
"""Control del harness antes de cada commit: funciona con cualquier asistente de IA, o sin asistente.

Uso:
    (automático) Git lo ejecuta desde .githooks/pre-commit si está activo `git config core.hooksPath .githooks`
    python herramientas/hooks/precommit.py --archivos <ruta> [<ruta> ...]   # validar archivos recién editados

Revisa los archivos en staging (o los indicados con --archivos):
- bloquea los confidenciales (mismos patrones que el hook de Claude Code: _entrada/, originales, banco de
  contenidos, paquete final, credenciales) y las réplicas de fuentes/ marcadas `confidencialidad: sensible`;
- valida los CSV (columnas, fechas AAAA-MM-DD) y YAML (sintaxis, definiciones de métricas) de proyectos/ y empresa/.
Termina con código 1 si encuentra problemas (Git cancela el commit) y explica qué hacer.
"""
import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comun import motivo_sensible, preparar_salida, replica_sensible, revisar  # noqa: E402

CARPETAS_VALIDADAS = ("proyectos", "empresa")


def git(*args, raiz=None):
    r = subprocess.run(["git", *args], cwd=raiz, capture_output=True, timeout=30)
    return r.returncode, r.stdout.decode("utf-8", errors="replace")


def en_staging(raiz):
    """Archivos agregados o modificados en el staging (sin los borrados), con su contenido preparado."""
    _, salida = git("diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z", raiz=raiz)
    return [x for x in salida.split("\0") if x.strip()]


def contenido_preparado(raiz, rel):
    rc, texto = git("show", f":{rel}", raiz=raiz)
    return texto if rc == 0 else ""


def validable(rel):
    partes = Path(rel).parts
    return (len(partes) > 1 and partes[0] in CARPETAS_VALIDADAS and "_entrada" not in partes
            and Path(rel).suffix.lower() in (".csv", ".yaml", ".yml"))


def es_replica(rel):
    partes = Path(rel).parts
    return "fuentes" in partes[:-1] and Path(rel).suffix.lower() == ".md" and Path(rel).name.upper() != "LEEME.MD"


def revisar_archivos(raiz, relativos, leer):
    confidenciales, invalidos = [], []
    for rel in relativos:
        rel = rel.replace("\\", "/")
        motivo = motivo_sensible(rel)
        if motivo:
            confidenciales.append(f"- {rel} ({motivo})")
            continue
        if es_replica(rel) and replica_sensible(leer(rel)):
            confidenciales.append(f"- {rel} (réplica marcada confidencialidad: sensible: solo debe quedar su ficha)")
            continue
        ruta = raiz / rel
        if validable(rel) and ruta.exists():
            problemas = revisar(ruta)
            if problemas:
                invalidos.append(f"{rel}:\n  - " + "\n  - ".join(problemas))
    return confidenciales, invalidos


def main():
    preparar_salida()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--archivos", nargs="+", help="valida estos archivos en vez del staging")
    a = ap.parse_args()

    rc, top = git("rev-parse", "--show-toplevel")
    raiz = Path(top.strip()).resolve() if rc == 0 and top.strip() else Path(__file__).resolve().parent.parent.parent
    if a.archivos:
        relativos = []
        for x in a.archivos:
            p = Path(x).resolve()
            try:
                relativos.append(p.relative_to(raiz).as_posix())
            except ValueError:
                relativos.append(Path(x).as_posix())

        def leer(rel):
            try:
                return (raiz / rel).read_text(encoding="utf-8", errors="replace")
            except OSError:
                return ""
    else:
        relativos = en_staging(raiz)

        def leer(rel):
            return contenido_preparado(raiz, rel)

    confidenciales, invalidos = revisar_archivos(raiz, relativos, leer)
    if not confidenciales and not invalidos:
        if a.archivos:
            print(f"OK: {len(relativos)} archivo(s) revisado(s) sin problemas.")
        return 0
    lineas = ["PMO Harness: " + ("commit detenido." if not a.archivos else "se encontraron problemas.")]
    if confidenciales:
        lineas += ["", "Archivos confidenciales (no se suben a Git):", *confidenciales,
                   "→ Quítalos del staging con `git restore --staged <archivo>` y agrega el patrón a .gitignore si corresponde.",
                   "  Si el usuario confirma explícitamente que uno debe versionarse, explícale el riesgo antes."]
    if invalidos:
        lineas += ["", "Planillas o definiciones con errores:", *invalidos, "→ Corrígelos y vuelve a intentar."]
    lineas += ["", "No uses `git commit --no-verify`: el control existe para proteger la información del proyecto."]
    print("\n".join(lineas), file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
