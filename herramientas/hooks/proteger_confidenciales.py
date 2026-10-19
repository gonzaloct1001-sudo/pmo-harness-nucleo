#!/usr/bin/env python3
"""Hook PreToolUse (Bash y PowerShell): impide agregar o commitear archivos confidenciales en Git.

Revisa los comandos `git add` (simulándolos con --dry-run) y `git commit` (archivos en staging).
Si detecta archivos sensibles, bloquea el comando y explica qué hacer.
Los patrones están en _comun.SENSIBLES y son los mismos del control de Git (.githooks/pre-commit).
"""
import re
import subprocess
import sys

from _comun import bloquear, leer_evento, motivo_sensible, preparar_salida


def archivos_de(cmd):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        return r.stdout
    except Exception:
        return ""


def main():
    preparar_salida()
    ev = leer_evento()
    comando = (ev.get("tool_input") or {}).get("command", "")
    if not re.search(r"\bgit\b", comando):
        return
    candidatos = []
    for parte in re.split(r"&&|;|\|\|", comando):
        parte = parte.strip()
        m_add = re.match(r"git\s+add\s+(.*)$", parte)
        if m_add:
            args = m_add.group(1).split()
            if "--dry-run" not in args and "-n" not in args:
                salida = archivos_de(["git", "add", "--dry-run"] + args)
                candidatos += [re.sub(r"^add '(.*)'$", r"\1", l.strip()) for l in salida.splitlines() if l.startswith("add ")]
        elif re.match(r"git\s+commit\b", parte):
            candidatos += archivos_de(["git", "diff", "--cached", "--name-only"]).splitlines()
            if re.search(r"\s-(a|am|[a-z]*a[a-z]*)\b", parte):
                candidatos += archivos_de(["git", "diff", "--name-only"]).splitlines()
    hallazgos = []
    for f in dict.fromkeys(c.strip() for c in candidatos if c.strip()):
        motivo = motivo_sensible(f)
        if motivo:
            hallazgos.append(f"- {f} ({motivo})")
    if hallazgos:
        bloquear("BLOQUEADO por el harness: el comando incluiría archivos confidenciales en Git:\n"
                 + "\n".join(hallazgos)
                 + "\nQuítalos del staging (git restore --staged <archivo>), agrega el patrón a .gitignore si "
                   "corresponde, y vuelve a intentar sin ellos. Si el usuario confirma explícitamente que uno "
                   "de ellos debe versionarse, explícale el riesgo antes de proceder.")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        sys.exit(0)
