#!/usr/bin/env python3
"""Hook PreToolUse (Bash y PowerShell): impide que un comando de Git saque archivos confidenciales o se salte los controles.

Antes de ejecutar un comando que usa Git:
- bloquea los intentos de saltarse el control (`--no-verify`, `git commit -n`, cambiar o quitar `core.hooksPath`);
- bloquea `git init` junto con `git add` o `git commit` en el mismo comando: sin repositorio no hay cómo revisar qué
  entraría, y un repositorio recién creado todavía no tiene el control de Git activo;
- bloquea `git commit` y `git push` si el control de Git no está activo en este computador (se activa con una línea);
- revisa lo que ya está preparado para el commit y simula cada `git add` (con comillas, `cd`, `git -C`, `--no-pager`).
Después de ejecutar, `validar_edicion.py` mira el estado real del staging y saca lo confidencial: así el resultado no
depende de cómo esté escrito el comando. Los patrones están en `_comun.py` (los del harness) y en
`empresa/confidencialidad.yaml` (los de la empresa), y son los mismos del control de Git (.githooks/).
"""
import re
import shlex
import subprocess
import sys
from pathlib import Path

from _comun import (bloquear, carpeta_de, control_git_activo, git_salida, leer_evento, motivo_sensible, preparar_salida,
                    raiz_git, staging_sensible)

# `git` con sus opciones globales (-C carpeta, -c clave=valor, --no-pager…) antes del subcomando
GIT = r"(?<![\w./-])git(?:\.exe)?(?:\s+(?:-C\s+(?:\"[^\"]*\"|'[^']*'|\S+)|-c\s+\S+|--no-pager|-P|--git-dir[= ]\S+|--work-tree[= ]\S+))*\s+"
SEPARADORES = r"&&|\|\||;|\||\r?\n"
REDIRECCION = re.compile(r"^(\d*>>?|\d*>&\d+|<)")


def sin_comillas(texto):
    """El comando sin el contenido de sus comillas: para buscar opciones sin confundirlas con el texto de un mensaje."""
    return re.sub(r"\"(?:\\.|[^\"\\])*\"|'[^']*'", '""', texto)


def partir(segmento):
    try:
        return shlex.split(segmento, posix=True)
    except ValueError:
        return segmento.split()


def simular_add(segmento, cwd):
    """Archivos que agregaría un `git add` (con --dry-run), respetando sus opciones globales y sus comillas."""
    piezas = partir(segmento)
    try:
        i_git = next(i for i, x in enumerate(piezas) if re.fullmatch(r"(?:.*[\\/])?git(?:\.exe)?", x))
        i_add = next(i for i in range(i_git + 1, len(piezas)) if piezas[i] in ("add", "stage"))
    except StopIteration:
        return []
    args = []
    for x in piezas[i_add + 1:]:
        if REDIRECCION.match(x):
            break
        args.append(x)
    if "--dry-run" in args or "-n" in args:
        return []
    try:
        r = subprocess.run(["git", "-c", "core.quotepath=false", *piezas[i_git + 1:i_add], "add", "--dry-run", *args],
                           cwd=cwd, capture_output=True, timeout=20)
        salida = r.stdout.decode("utf-8", errors="replace")
    except Exception:
        return []
    return [re.sub(r"^add '(.*)'$", r"\1", l.strip()) for l in salida.splitlines() if l.startswith("add ")]


def main():
    preparar_salida()
    ev = leer_evento()
    comando = (ev.get("tool_input") or {}).get("command", "")
    if not re.search(r"\bgit\b", comando):
        return
    cwd = carpeta_de(ev)
    segmentos = [s.strip() for s in re.split(SEPARADORES, comando) if s.strip()]
    planos = [sin_comillas(s) for s in segmentos]
    hay = lambda sub: any(re.search(GIT + sub + r"\b", s) for s in planos)  # noqa: E731
    hay_add, hay_commit, hay_push, hay_init = hay("(?:add|stage)"), hay("commit"), hay("push"), hay("init")

    # 1. Saltarse el control
    for s in planos:
        if re.search(GIT + r"(?:commit|push)\b", s) and "--no-verify" in s:
            bloquear("BLOQUEADO por el harness: `--no-verify` se salta el control que protege lo confidencial. Vuelve a "
                     "intentar sin esa opción; si el control detiene algo, corrige lo que indica (principio 11).")
        if re.search(GIT + r"commit\b", s) and re.search(r"(?<![\w-])-[a-zA-Z]*n[a-zA-Z]*(?![\w-])", s):
            bloquear("BLOQUEADO por el harness: `git commit -n` se salta el control que protege lo confidencial. Vuelve a "
                     "intentar sin esa opción.")
    valido = r"git\s+config\s+(?:--local\s+)?(?:--get\s+core\.hooksPath|core\.hooksPath\s+\.githooks/?)"
    for s, sp in zip(segmentos, planos):
        if re.search(r"core\.hookspath", sp, re.I) and not re.fullmatch(valido, s, re.I):
            bloquear("BLOQUEADO por el harness: ese comando cambia o quita `core.hooksPath`, que es lo que mantiene activo el "
                     "control de Git. El único valor válido es: git config core.hooksPath .githooks")

    # 2. Repositorio nuevo y contenido en el mismo comando
    if hay_init and (hay_add or hay_commit):
        bloquear("BLOQUEADO por el harness: `git init` junto con `git add` o `git commit` en el mismo comando. Sin "
                 "repositorio no se puede revisar qué entraría. Hazlo en pasos: primero `git init`, después "
                 "`git config core.hooksPath .githooks`, y recién entonces agrega y guarda.")
    if not (hay_add or hay_commit or hay_push):
        return

    # La carpeta donde corre el comando: la del evento, o la de un `cd` que lo encabeza
    for s in segmentos:
        m = re.fullmatch(r"(?:cd|Set-Location|sl|pushd)\s+(?:\"([^\"]+)\"|'([^']+)'|(\S+))", s)
        if not m:
            break
        destino = Path(cwd) / next(g for g in m.groups() if g)
        if destino.is_dir():
            cwd = str(destino)
    raiz = raiz_git(cwd)
    if raiz is None:
        return  # sin repositorio, Git mismo rechaza el comando

    # 3. Control de Git inactivo: no se guarda ni se sube hasta activarlo
    es_harness = (raiz / ".githooks" / "pre-commit").is_file() and (raiz / "herramientas" / "hooks" / "precommit.py").is_file()
    if es_harness and (hay_commit or hay_push) and not control_git_activo(raiz):
        bloquear("BLOQUEADO por el harness: el control de Git no está activo en este computador, así que nada revisaría lo "
                 "confidencial al guardar o subir. Actívalo (una sola vez) y repite el comando:\n"
                 "git config core.hooksPath .githooks")

    # 4. Lo que entraría: lo ya preparado y lo que agrega este comando
    candidatos = []
    for s, sp in zip(segmentos, planos):
        if re.search(GIT + r"(?:add|stage)\b", sp):
            candidatos += simular_add(s, cwd)
        elif re.search(GIT + r"commit\b", sp):
            candidatos += [r for r, _ in staging_sensible(raiz)]
            if re.search(r"(?<![\w-])(?:--all|-[a-zA-Z]*a[a-zA-Z]*)(?![\w-])", sp):
                candidatos += git_salida(["diff", "--name-only"], raiz)[1].splitlines()
    hallazgos = []
    for f in dict.fromkeys(c.strip() for c in candidatos if c.strip()):
        rel = f
        try:  # `git add` informa rutas relativas a la carpeta del comando; los patrones son relativos a la raíz
            rel = (Path(cwd) / f).resolve().relative_to(raiz.resolve()).as_posix() if not (raiz / f).exists() else f
        except (ValueError, OSError):
            pass
        motivo = motivo_sensible(rel, raiz)
        if motivo:
            hallazgos.append(f"- {rel} ({motivo})")
    if hallazgos:
        bloquear("BLOQUEADO por el harness: el comando incluiría archivos confidenciales en Git:\n"
                 + "\n".join(hallazgos)
                 + "\nQuítalos del staging (git restore --staged <archivo>), agrega el patrón con "
                   "`python herramientas/confidencialidad.py --agregar` si corresponde, y vuelve a intentar sin ellos. "
                   "Si el usuario confirma explícitamente que uno de ellos debe versionarse, explícale el riesgo antes "
                   "de proceder.")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        sys.exit(0)
