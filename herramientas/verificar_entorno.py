#!/usr/bin/env python3
"""Verifica que el computador y la carpeta estén listos para usar el harness.

Uso:
    python herramientas/verificar_entorno.py

Revisa: versión de Python, librerías, Git (instalado, repositorio, remoto, cambios sin subir),
GitHub CLI, LibreOffice, estado de instalación del harness y proyectos existentes.
Solo lee: no instala ni modifica nada.
"""
import importlib
import platform
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
LIBRERIAS = {"docx": "python-docx", "openpyxl": "openpyxl", "pptx": "python-pptx", "yaml": "pyyaml", "pypdf": "pypdf"}


def cmd(*args):
    try:
        r = subprocess.run(args, cwd=RAIZ, capture_output=True, text=True, timeout=20)
        return r.returncode, (r.stdout or r.stderr).strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None, ""


def buscar_soffice():
    for nombre in ("soffice", "libreoffice"):
        if shutil.which(nombre):
            return shutil.which(nombre)
    for ruta in (r"C:\Program Files\LibreOffice\program\soffice.exe",
                 r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
                 "/Applications/LibreOffice.app/Contents/MacOS/soffice"):
        if Path(ruta).exists():
            return ruta
    return None


def main():
    ok, faltas = [], []
    print("# Verificación del entorno\n")
    print(f"- Sistema: {platform.system()} {platform.release()}")
    v = sys.version_info
    linea = f"- Python {v.major}.{v.minor}.{v.micro} ({sys.executable})"
    if (v.major, v.minor) < (3, 9):
        faltas.append("Python 3.9 o superior")
        linea += " → **ACTUALIZAR**"
    print(linea)

    venv = RAIZ / ".venv" / "bin" / "python"
    en_venv = Path(sys.prefix).resolve() == (RAIZ / ".venv").resolve()
    if venv.exists() and not en_venv:
        print("- Esta carpeta tiene su propio Python en `.venv`: ejecuta los scripts con `.venv/bin/python` (en Mac, en vez de `python3`)")
    faltantes = []
    for mod, pip in LIBRERIAS.items():
        try:
            importlib.import_module(mod)
        except ImportError:
            faltantes.append(pip)
    if faltantes:
        instalador = "INSTALAR-MAC.command" if platform.system() == "Darwin" else "INSTALAR-WINDOWS.bat"
        print(f"- Librerías faltantes: {', '.join(faltantes)} → instalar con: "
              f"`{Path(sys.executable).name} -m pip install -r requirements.txt` (o con {instalador})")
        faltas.append("librerías Python")
    else:
        print("- Librerías Python: todas instaladas" + (" (en .venv)" if en_venv else ""))

    rc, out = cmd("git", "--version")
    if rc is None:
        print("- Git: **NO INSTALADO** (https://git-scm.com/downloads)")
        faltas.append("Git")
    else:
        print(f"- {out}")
        rc, _ = cmd("git", "rev-parse", "--is-inside-work-tree")
        _, raiz_git = cmd("git", "rev-parse", "--show-toplevel")
        anidado = rc == 0 and raiz_git and Path(raiz_git).resolve() != RAIZ.resolve()
        if rc != 0:
            print("- Repositorio Git: **no inicializado** en esta carpeta")
        elif anidado:
            _, remoto_padre = cmd("git", "remote", "get-url", "origin")
            print(f"- Repositorio Git: **no propio**. Esta carpeta está DENTRO de otro repositorio: {Path(raiz_git).as_posix()}"
                  f" (remoto: {remoto_padre if remoto_padre and 'fatal' not in remoto_padre.lower() else 'sin remoto'}).")
            print("  → La skill instalar debe crear un repositorio propio aquí (git init) y excluir esta carpeta del"
                  " repositorio padre en su .git/info/exclude.")
            faltas.append("repositorio propio (la carpeta está dentro de otro repositorio)")
        else:
            _, rama = cmd("git", "branch", "--show-current")
            _, remoto = cmd("git", "remote", "get-url", "origin")
            _, estado = cmd("git", "status", "--short")
            print(f"- Repositorio Git: sí · rama `{rama or '(sin commits)'}`")
            print(f"- Remoto (GitHub): {remoto if remoto and 'fatal' not in remoto.lower() and 'error' not in remoto.lower() else '**no configurado**'}")
            n = len([x for x in estado.splitlines() if x.strip()])
            print(f"- Cambios sin guardar: {n}")
            rc_u, sinsubir = cmd("git", "rev-list", "--count", "@{u}..HEAD")
            if rc_u == 0:
                print(f"- Commits sin subir: {sinsubir}")
            _, usuario = cmd("git", "config", "user.name")
            if not usuario:
                print("- Git sin nombre de usuario configurado → `git config --global user.name \"Nombre\"` y `user.email`")
            _, ruta_hooks = cmd("git", "config", "--get", "core.hooksPath")
            if ruta_hooks.replace("\\", "/").rstrip("/") == ".githooks":
                print("- Control de Git del harness (antes de cada commit): activo")
            else:
                print("- Control de Git del harness: **INACTIVO** → `git config core.hooksPath .githooks`")
                faltas.append("activar el control de Git")

    rc, out = cmd("gh", "--version")
    print(f"- GitHub CLI (gh): {'instalado' if rc == 0 else 'no instalado (opcional: permite crear el repo privado desde aquí)'}")
    so = buscar_soffice()
    print(f"- LibreOffice: {so if so else 'no encontrado (opcional: revisión visual de documentos)'}")

    estado = RAIZ / ".harness" / "estado.yaml"
    print(f"- Harness instalado en esta carpeta: {'sí' if estado.exists() else 'NO → ejecutar la skill instalar'}")
    asis = RAIZ / ".harness" / "asistentes.yaml"
    if estado.exists():
        import re
        ids = re.findall(r"^\s*-?\s*id:\s*([\w.-]+)", asis.read_text(encoding="utf-8")) if asis.exists() else []
        print(f"- Asistentes de IA configurados: {', '.join(ids) if ids else 'ninguno → skill configurar-asistente'}")
    proyectos = [p.name for p in (RAIZ / "proyectos").iterdir() if p.is_dir()] if (RAIZ / "proyectos").exists() else []
    print(f"- Proyectos dados de alta: {', '.join(proyectos) if proyectos else 'ninguno'}")
    for p in proyectos:
        entrada = RAIZ / "proyectos" / p / "_entrada"
        if entrada.exists():
            n = sum(1 for x in entrada.rglob("*") if x.is_file() and x.name not in ("LEEME.md", ".gitkeep") and not x.name.startswith("_LEEME")
                    and "_procesado" not in x.parts and "_archivo" not in x.parts)
            if n:
                print(f"  - {p}: {n} archivo(s) en _entrada")

    print("\nResultado: " + ("LISTO" if not faltas else "FALTA: " + ", ".join(faltas)))


if __name__ == "__main__":
    import _consola
    _consola.preparar()
    main()
