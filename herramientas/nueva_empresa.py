#!/usr/bin/env python3
"""Crea la carpeta de una empresa: el núcleo del harness + su carpeta empresa/, en un repositorio privado propio.

Uso:
    python herramientas/nueva_empresa.py "<Nombre de la empresa>" --destino <carpeta padre> [--slug nombre-carpeta]
                                         [--sin-github] [--propietario cuenta-u-organizacion] [--nucleo-origen url]
    python herramientas/nueva_empresa.py "<Nombre de la empresa>" --aqui

- Con --destino: copia a <destino>/<slug>/ solo las rutas del núcleo (NUCLEO.txt), nunca proyectos ni datos de
  otra empresa; crea empresa/ desde plantilla-empresa/, .harness/estado.yaml y el registro de archivos del núcleo;
  inicia Git (rama main), activa el control de Git, hace el primer commit y, si GitHub CLI tiene sesión, crea el
  repositorio PRIVADO con el tema `pmo-harness-empresa` (así se encuentra desde otro computador) y lo sube.
- Con --aqui: configura la empresa en la carpeta actual del harness (lo usa la skill instalar). No toca Git.
Una carpeta es una empresa: los datos de dos empresas nunca se mezclan.
"""
import argparse
import re
import shutil
import subprocess
import sys
import unicodedata
from datetime import date
from pathlib import Path

import _nucleo

RAIZ = Path(__file__).resolve().parent.parent


def slug_de(nombre):
    s = unicodedata.normalize("NFKD", nombre).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-") or "empresa"


def git(destino, *args):
    r = subprocess.run(["git", *args], cwd=destino, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()


def preparar_empresa(destino: Path, nombre, nucleo_origen):
    """Crea empresa/ y .harness/ en `destino` si faltan. Devuelve la lista de lo creado."""
    creado = []
    emp = destino / "empresa"
    if not (emp / "empresa.yaml").exists():
        shutil.copytree(RAIZ / "plantilla-empresa", emp, dirs_exist_ok=True)
        texto = (emp / "empresa.yaml").read_text(encoding="utf-8")
        texto = re.sub(r"^(  nombre:\s*)PENDIENTE", lambda m: m.group(1) + nombre, texto, count=1, flags=re.M)
        (emp / "empresa.yaml").write_text(texto, encoding="utf-8")
        creado.append("empresa/")
    estado = destino / ".harness" / "estado.yaml"
    if not estado.exists():
        estado.parent.mkdir(parents=True, exist_ok=True)
        estado.write_text(
            "instalado: true\n"
            f"fecha_instalacion: {date.today().isoformat()}\n"
            f'version_harness: "{_nucleo.version(destino) or _nucleo.version(RAIZ)}"\n'
            f'empresa: "{nombre}"\n'
            "nucleo:\n"
            f'  origen: "{nucleo_origen or "pendiente"}"   # repositorio o carpeta de donde actualizar_nucleo.py trae las mejoras\n'
            'repositorio_remoto: "pendiente"\n'
            "proyectos: []\n", encoding="utf-8")
        creado.append(".harness/estado.yaml")
    if _nucleo.leer_manifiesto(destino) is None:
        _nucleo.escribir_manifiesto(destino, _nucleo.archivos(destino))
        creado.append(".harness/nucleo-instalado.csv")
    (destino / "proyectos").mkdir(exist_ok=True)
    return creado


def ficha_en_blanco(texto):
    """La ficha de inicio sin respuestas (la de la carpeta de origen puede tener datos de otra empresa)."""
    return re.sub(r"^(\s*-\s+[^:\n]+:)[ \t]*\S.*$", r"\1", texto, flags=re.M)


def origen_del_nucleo():
    """Origen registrado en esta carpeta o, si no hay, el repositorio público del núcleo (NUCLEO.txt)."""
    estado = RAIZ / ".harness" / "estado.yaml"
    if estado.exists():
        m = re.search(r"^\s+origen:\s*\"?([^\"#\n]+?)\"?\s*(#.*)?$", estado.read_text(encoding="utf-8"), re.M)
        if m and m.group(1).strip() not in ("", "pendiente"):
            return m.group(1).strip()
    return _nucleo.origen_oficial(RAIZ)


def desconectar_del_nucleo(carpeta: Path):
    """Si la carpeta se clonó desde el repositorio público del núcleo, quita ese remoto: los datos de la empresa van
    a su propio repositorio privado, nunca al núcleo (que además no admite cambios de terceros). Devuelve True si lo hizo."""
    rc, url = git(carpeta, "remote", "get-url", "origin")
    if rc == 0 and _nucleo.misma_url(url, _nucleo.origen_oficial(carpeta)):
        git(carpeta, "remote", "remove", "origin")
        return True
    return False


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("nombre", help="nombre de la empresa (o persona) dueña de la carpeta")
    ap.add_argument("--destino", help="carpeta donde crear la carpeta de la empresa")
    ap.add_argument("--aqui", action="store_true", help="configurar la empresa en esta misma carpeta")
    ap.add_argument("--slug", help="nombre de la carpeta y del repositorio (por defecto, a partir del nombre)")
    ap.add_argument("--sin-github", action="store_true", help="no crear el repositorio en GitHub")
    ap.add_argument("--propietario", default="", help="cuenta u organización de GitHub (por defecto, la del usuario)")
    ap.add_argument("--nucleo-origen", default="", help="repositorio o carpeta del núcleo para futuras actualizaciones")
    a = ap.parse_args()
    nucleo_origen = a.nucleo_origen or origen_del_nucleo()

    if a.aqui:
        if _nucleo.es_mantenedor(RAIZ):
            sys.exit("Esta carpeta es el núcleo que mantienes: no lleva empresas ni proyectos. Crea una carpeta de empresa "
                     "aparte con: python herramientas/nueva_empresa.py \"<Nombre>\" --destino <carpeta>")
        emp_actual = RAIZ / "empresa" / "empresa.yaml"
        if emp_actual.exists():
            m = re.search(r"^  nombre:\s*(.+)$", emp_actual.read_text(encoding="utf-8"), re.M)
            actual = (m.group(1).split("#")[0].strip().strip("\"'") if m else "")
            if actual not in ("", "PENDIENTE") and slug_de(actual) != slug_de(a.nombre):
                sys.exit(f"Esta carpeta ya es de la empresa «{actual}». Para «{a.nombre}» crea una carpeta aparte con --destino.")
        creado = preparar_empresa(RAIZ, a.nombre, nucleo_origen)
        print(f"Empresa «{a.nombre}» configurada en esta carpeta" + (f" (creado: {', '.join(creado)})" if creado else " (ya estaba)"))
        if desconectar_del_nucleo(RAIZ):
            print("- Esta carpeta venía clonada del núcleo público: se desconectó de él. Tus datos irán a tu propio "
                  "repositorio privado (skill instalar, paso 2); el núcleo sigue disponible para actualizar.")
        return

    if not a.destino:
        sys.exit("Indica --destino <carpeta padre> para una empresa nueva, o --aqui para esta carpeta.")
    slug = a.slug or slug_de(a.nombre)
    destino = Path(a.destino).expanduser().resolve() / slug
    if destino.exists() and any(destino.iterdir()):
        sys.exit(f"Ya existe {destino} y no está vacía: elige otro --slug o --destino.")
    try:
        destino.relative_to(RAIZ)
        sys.exit("El destino no puede quedar dentro de esta carpeta del harness: elige una carpeta aparte.")
    except ValueError:
        pass

    # 1. Núcleo (solo las rutas de NUCLEO.txt)
    entradas = _nucleo.rutas(RAIZ)
    copiados = 0
    origen_largo, destino_largo = _nucleo.ruta_larga(RAIZ), _nucleo.ruta_larga(destino)
    for rel in _nucleo.archivos(RAIZ, entradas):
        d = destino_largo / rel
        d.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(origen_largo / rel, d)
        copiados += 1
    for nombre_carpeta in ("biblioteca/perfiles",):
        (destino / nombre_carpeta).mkdir(parents=True, exist_ok=True)
    ficha = RAIZ / "FICHA-DE-INICIO.md"
    if ficha.exists():
        (destino / "FICHA-DE-INICIO.md").write_text(ficha_en_blanco(ficha.read_text(encoding="utf-8")), encoding="utf-8")
    for ejecutable in _nucleo.EJECUTABLES:
        p = destino / ejecutable
        if p.exists():
            p.chmod(p.stat().st_mode | 0o111)
    creado = preparar_empresa(destino, a.nombre, nucleo_origen)
    print(f"Carpeta de la empresa «{a.nombre}»: {destino}")
    print(f"- Núcleo copiado: {copiados} archivo(s) · creado: {', '.join(creado)}")

    # 2. Git
    if shutil.which("git") is None:
        print("- Git no está instalado: el repositorio se crea después con la skill instalar.")
        return
    git(destino, "init", "-q")
    git(destino, "checkout", "-q", "-b", "main")
    git(destino, "config", "core.hooksPath", ".githooks")
    git(destino, "config", "core.longpaths", "true")  # Windows: rutas de más de 260 caracteres
    git(destino, "add", "-A")
    git(destino, "update-index", "--chmod=+x", *[e for e in _nucleo.EJECUTABLES if (destino / e).exists()])
    rc, salida = git(destino, "commit", "-q", "-m", f"Instalación del harness para {a.nombre}")
    if rc != 0:
        print(f"- No se pudo hacer el primer commit (¿falta configurar nombre y correo de Git?):\n  {salida[:400]}")
        return
    print("- Repositorio Git creado (rama main) con el control de Git activo y el primer commit.")

    # 3. GitHub (siempre privado)
    if a.sin_github:
        print("- GitHub: omitido (--sin-github). Para subirlo después: skill instalar, paso 2.")
    elif shutil.which("gh") is None or subprocess.run(["gh", "auth", "status"], capture_output=True).returncode != 0:
        print("- GitHub: falta GitHub CLI o su sesión (gh auth login --web). Para subirlo después: skill instalar, paso 2.")
    else:
        repo = f"{a.propietario}/{slug}" if a.propietario else slug
        r = subprocess.run(["gh", "repo", "create", repo, "--private", "--source", str(destino), "--push",
                            "--description", f"PMO Harness · {a.nombre}"], cwd=destino, capture_output=True, text=True)
        if r.returncode == 0:
            subprocess.run(["gh", "repo", "edit", "--add-topic", "pmo-harness-empresa"], cwd=destino, capture_output=True)
            _, url = git(destino, "remote", "get-url", "origin")
            est = destino / ".harness" / "estado.yaml"
            est.write_text(est.read_text(encoding="utf-8").replace('repositorio_remoto: "pendiente"', f'repositorio_remoto: "{url}"'), encoding="utf-8")
            git(destino, "commit", "-q", "-am", "Registra el repositorio remoto")
            git(destino, "push", "-q")
            print(f"- GitHub: repositorio privado {url} (tema pmo-harness-empresa).")
        else:
            print(f"- GitHub: no se pudo crear el repositorio: {(r.stderr or r.stdout).strip()[:300]}")
    print(f"\nSiguiente paso: abre {destino} en tu editor con tu asistente de IA y escribe «hola».")
    print("Si llevas varias empresas y quieres ver su status en una sola vista: pide «quiero un tablero único» "
          "(se crea en una carpeta y un repositorio privado aparte, solo para ti).")


if __name__ == "__main__":
    import _consola
    _consola.preparar()
    main()
