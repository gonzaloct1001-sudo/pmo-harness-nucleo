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
SE_FUSIONAN = (".claude/settings.json", ".gitignore", "requirements.txt")  # del núcleo, pero hechos para llevar agregados propios
MARCA_PROPIO = "# --- Propio de esta carpeta (se conserva al actualizar el núcleo) ---"  # en .gitignore y requirements.txt
EJECUTABLES = (".githooks/pre-commit", ".githooks/pre-push", "herramientas/py.sh", "herramientas/preparar_pc.sh", "INSTALAR-MAC.command")


def ruta_larga(ruta):
    """En Windows, la ruta con prefijo \\\\?\\ para superar el límite de 260 caracteres (carpetas profundas u OneDrive)."""
    p = Path(ruta).resolve()
    if os.name == "nt" and not str(p).startswith("\\\\?\\"):
        return Path("\\\\?\\" + str(p))
    return p


def huella(ruta):
    """Huella del contenido. En archivos de texto ignora la diferencia CRLF/LF (Windows/Mac): el zip de GitHub y una
    copia clonada en Windows tienen el mismo contenido aunque sus saltos de línea difieran."""
    return huella_datos(Path(ruta).read_bytes())


def huella_datos(datos):
    """Huella de un contenido ya leído (la misma regla que `huella`)."""
    if b"\0" not in datos[:8192]:
        datos = datos.replace(b"\r\n", b"\n")
    return hashlib.sha256(datos).hexdigest()[:20]


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


SINCRONIZADAS = [("Dropbox", r"dropbox"), ("OneDrive", r"onedrive"), ("Google Drive", r"google ?drive|my drive|mi unidad"),
                 ("iCloud", r"icloud ?drive|mobile documents")]


def carpeta_sincronizada(ruta):
    """Nombre del servicio (Dropbox, OneDrive, Google Drive, iCloud) si `ruta` está dentro de una carpeta que se
    sincroniza sola, o cadena vacía. Git dentro de esas carpetas se puede dañar al usarlas desde dos computadores."""
    partes = [p.lower() for p in Path(ruta).parts]
    for nombre, patron in SINCRONIZADAS:
        if any(re.search(patron, p) for p in partes):
            return nombre
    return ""


def lugar_sugerido():
    """Carpeta recomendada para el harness: Documentos si no se sincroniza sola; si no, una carpeta PMO en el usuario."""
    documentos = Path.home() / "Documents"
    return documentos if documentos.exists() and not carpeta_sincronizada(documentos.resolve()) else Path.home() / "PMO"


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


def pruebas_propias(raiz):
    """Pruebas propias de la empresa (rutas relativas): `empresa/extensiones/pruebas*.py` y `empresa/pruebas/*.py`.
    Son de la empresa: el núcleo nunca las toca; la batería las ejecuta y la actualización las compara antes y después."""
    raiz = Path(raiz)
    halladas = sorted((raiz / "empresa" / "extensiones").glob("pruebas*.py")) + sorted((raiz / "empresa" / "pruebas").glob("*.py"))
    return [x.relative_to(raiz).as_posix() for x in halladas if x.is_file() and not x.name.startswith("_")]


def extensiones_propias(raiz):
    """Herramientas y hooks propios de la empresa en `empresa/extensiones/` (rutas relativas, sin las pruebas)."""
    base = Path(raiz) / "empresa" / "extensiones"
    if not base.is_dir():
        return []
    return sorted(x.relative_to(raiz).as_posix() for x in base.rglob("*.py")
                  if x.is_file() and "__pycache__" not in x.parts and not x.name.startswith("pruebas"))


def carpetas_nucleo(raiz):
    """Las carpetas completas del núcleo (entradas de NUCLEO.txt que terminan en /)."""
    return tuple(e for e in rutas(raiz) if e.endswith("/"))


def ajeno_al_nucleo(rel, es_carpeta, instalados, carpetas):
    """True si `rel` vive dentro de una carpeta del núcleo pero no vino con el núcleo (no está en el registro de lo
    instalado): es propio de la empresa, como una skill o un hook suyo. La batería y la revisión de integridad prueban
    el núcleo y no lo consideran. Donde se mantiene el núcleo no hay registro (`instalados` es None): nada es ajeno."""
    if instalados is None or not rel.startswith(tuple(carpetas)):
        return False
    if es_carpeta:
        return not any(x.startswith(rel.rstrip("/") + "/") for x in instalados)
    return rel not in instalados


def desviaciones(raiz, rapido=False, dias=None):
    """Diferencias entre el núcleo de esta carpeta y lo que se instaló, según el catastro (`.harness/nucleo-instalado.csv`):
    {"modificados": [...], "faltantes": [...], "propios": [...]}. None si no hay catastro (donde se mantiene el núcleo, o
    una carpeta sin instalar). Con `rapido` solo calcula la huella de los archivos tocados después del catastro y no lista
    los propios: es lo que usa el estado de inicio. Con `dias`, solo cuenta como modificados los tocados en ese plazo."""
    import time
    manifiesto = leer_manifiesto(raiz)
    if manifiesto is None:
        return None
    base = ruta_larga(raiz)
    referencia = (Path(raiz) / MANIFIESTO).stat().st_mtime
    desde = time.time() - dias * 86400 if dias else None
    modificados, fusionados, faltantes = [], [], []
    for rel, h in manifiesto.items():
        try:
            st = (base / rel).stat()
        except OSError:
            faltantes.append(rel)
            continue
        if (rapido and st.st_mtime <= referencia) or (desde and st.st_mtime < desde):
            continue
        if huella(base / rel) != h:
            (fusionados if rel in SE_FUSIONAN else modificados).append(rel)  # esos tres están hechos para llevar agregados propios
    propios = []
    if not rapido and (Path(raiz) / "NUCLEO.txt").exists():
        propios = sorted(r for r in archivos(raiz) if r not in manifiesto)
    return {"modificados": sorted(modificados), "fusionados": sorted(fusionados), "faltantes": sorted(faltantes), "propios": propios}


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
