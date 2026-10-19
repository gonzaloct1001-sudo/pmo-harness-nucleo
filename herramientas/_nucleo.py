"""Qué archivos son del núcleo del harness y en qué versión están.

- NUCLEO.txt (en la raíz) lista las rutas del núcleo; las que terminan en / son carpetas completas.
- .harness/nucleo-instalado.csv registra los archivos del núcleo instalados en una carpeta de empresa con su huella,
  para que una actualización sepa qué archivos borró el núcleo nuevo, cuáles se modificaron a mano y cuáles son
  propios de la empresa (por ejemplo, una skill propia dentro de .claude/skills/).
"""
import csv
import hashlib
import os
import re
from pathlib import Path

IGNORAR_PARTES = {"__pycache__", ".git", ".venv", "_procesado"}
IGNORAR_NOMBRES = {".DS_Store", "Thumbs.db", "desktop.ini"}
MANIFIESTO = Path(".harness") / "nucleo-instalado.csv"
EJECUTABLES = (".githooks/pre-commit", "herramientas/py.sh", "herramientas/preparar_pc.sh", "INSTALAR-MAC.command")


def ruta_larga(ruta):
    """En Windows, la ruta con prefijo \\\\?\\ para superar el límite de 260 caracteres (carpetas profundas u OneDrive)."""
    p = Path(ruta).resolve()
    if os.name == "nt" and not str(p).startswith("\\\\?\\"):
        return Path("\\\\?\\" + str(p))
    return p


def huella(ruta):
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()[:20]


def rutas(raiz):
    """Entradas de NUCLEO.txt de `raiz` (sin comentarios)."""
    lista = Path(raiz) / "NUCLEO.txt"
    if not lista.exists():
        raise SystemExit(f"No existe {lista}: esa carpeta no es un núcleo del PMO Harness.")
    return [l.strip() for l in lista.read_text(encoding="utf-8").splitlines() if l.strip() and not l.lstrip().startswith("#")]


def origen_oficial(raiz):
    """URL del repositorio público del núcleo (línea `# origen:` de NUCLEO.txt), o cadena vacía."""
    lista = Path(raiz) / "NUCLEO.txt"
    if not lista.exists():
        return ""
    m = re.search(r"^#\s*origen:\s*(\S+)", lista.read_text(encoding="utf-8"), re.M)
    return m.group(1) if m else ""


def es_mantenedor(raiz):
    """True si `raiz` es la carpeta donde se mantiene el núcleo (git config local pmo.mantenedor = true)."""
    import subprocess
    try:
        r = subprocess.run(["git", "config", "--local", "--get", "pmo.mantenedor"], cwd=raiz, capture_output=True, text=True, timeout=10)
        return r.stdout.strip().lower() == "true"
    except (OSError, subprocess.TimeoutExpired):
        return False


def misma_url(a, b):
    """True si dos URL de Git apuntan al mismo repositorio (https o ssh, con o sin .git)."""
    def norma(u):
        u = (u or "").strip().lower()
        u = re.sub(r"^git@([^:]+):", r"https://\1/", u)
        u = re.sub(r"^(https?|ssh)://(git@)?", "", u)
        return re.sub(r"(\.git)?/*$", "", u)
    return bool(a and b) and norma(a) == norma(b)


def _valido(rel: Path):
    return not (set(rel.parts) & IGNORAR_PARTES) and rel.name not in IGNORAR_NOMBRES and rel.suffix != ".pyc"


def archivos(raiz, entradas=None):
    """{ruta relativa con / : huella} de todos los archivos del núcleo presentes en `raiz`."""
    raiz = ruta_larga(raiz)
    salida = {}
    for e in entradas if entradas is not None else rutas(raiz):
        p = raiz / e
        if e.endswith("/"):
            if p.is_dir():
                for x in sorted(p.rglob("*")):
                    rel = x.relative_to(raiz)
                    if x.is_file() and _valido(rel):
                        salida[rel.as_posix()] = huella(x)
        elif p.is_file():
            salida[e] = huella(p)
    return salida


def dentro_del_nucleo(rel, entradas):
    """True si `rel` cae dentro de alguna ruta del núcleo."""
    return any(rel == e or (e.endswith("/") and rel.startswith(e)) for e in entradas)


def version(raiz):
    """Versión del primer encabezado `## x.y` de CHANGELOG.md, o cadena vacía."""
    log = Path(raiz) / "CHANGELOG.md"
    if not log.exists():
        return ""
    m = re.search(r"^##\s+(\d+(?:\.\d+)+)", log.read_text(encoding="utf-8"), re.M)
    return m.group(1) if m else ""


def novedades(raiz, desde_version):
    """Texto del CHANGELOG de `raiz` desde su inicio hasta el encabezado de `desde_version` (exclusivo)."""
    log = Path(raiz) / "CHANGELOG.md"
    if not log.exists():
        return ""
    texto = log.read_text(encoding="utf-8")
    inicio = re.search(r"^##\s+\d", texto, re.M)
    if not inicio:
        return ""
    fin = re.search(rf"^##\s+{re.escape(desde_version)}\b", texto, re.M) if desde_version else None
    return texto[inicio.start():fin.start() if fin and fin.start() > inicio.start() else len(texto)].strip()


def leer_manifiesto(raiz):
    ruta = Path(raiz) / MANIFIESTO
    if not ruta.exists():
        return None
    with open(ruta, encoding="utf-8", newline="") as f:
        return {r["ruta"]: r["huella"] for r in csv.DictReader(f)}


def escribir_manifiesto(raiz, archivos_nucleo):
    ruta = Path(raiz) / MANIFIESTO
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with open(ruta, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ruta", "huella"])
        for r in sorted(archivos_nucleo):
            w.writerow([r, archivos_nucleo[r]])
