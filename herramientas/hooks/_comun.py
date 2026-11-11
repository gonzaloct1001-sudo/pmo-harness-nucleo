"""Utilidades comunes de los controles del harness (hooks de Claude Code y control de Git antes de cada commit).

Los hooks nunca deben romper la sesión: ante un error inesperado, terminan con código 0 (no bloquean).
Aquí viven también las reglas que comparten todos los controles: qué archivos son confidenciales y cómo se
validan los CSV y YAML.
"""
import csv
import json
import os
import re
import subprocess
import sys
from fnmatch import fnmatch
from pathlib import Path

# --- Archivos confidenciales: nunca se suben a Git -------------------------------------------------------------
SENSIBLES = [
    (r"(^|/)_entrada/(?!LEEME\.md$)", "material sin procesar de _entrada/"),  # también empresa/_entrada/ (formatos propios)
    (r"(^|/)contractual/.*\.pdf$", "original contractual (PDF)"),
    (r"(^|/)original\.[^/]+$", "documento original"),
    (r"(^|/)documentos/.+/v\d+[^/]*\.(pdf|docx?|xlsx?|pptx?)$", "versión original de documento"),
    (r"(^|/)contenidos/archivos/", "documento del banco de contenidos (CV, certificados, antecedentes legales)"),
    (r"(^|/)entrega/final/", "paquete final presentado (firmas, declaraciones juradas, garantías)"),
    (r"(^|/)proyectos/[^/]+/postulaciones/(?!LEEME\.md$)", "documento de una postulación de terceros"),
    (r"(^|/)investigaciones/[^/]+/_crudo/", "material descargado sin procesar de una investigación (páginas y documentos de terceros)"),
    (r"(^|/)\.env(\.|$)", "archivo de variables de entorno"),
    (r"\.(pem|key|p12|pfx)$", "llave o certificado"),
    (r"(credencial|password|contrasena|contraseña|secret|token)", "posible credencial"),
]
MARCADORES = (".gitkeep", "LEEME.md")  # marcadores vacíos de carpeta e instrucciones: no son confidenciales
REPLICA_SENSIBLE = re.compile(r"^confidencialidad:\s*sensible\b", re.M)


# --- Confidencialidad propia de la empresa: empresa/confidencialidad.yaml (es de la empresa; el núcleo nunca lo toca) ---
RAIZ_HARNESS = Path(__file__).resolve().parent.parent.parent
POLITICA_DEFECTO = {"nunca_subir": [], "binarios_sueltos": "avisar", "carpetas_de_binarios": [], "claves_en_texto": "bloquear"}
_politicas = {}


def _yaml_minimo(texto):
    """Lector de respaldo para confidencialidad.yaml si PyYAML no está: `clave: valor`, `clave: [a, b]` y listas con guion."""
    datos, clave = {}, None
    for linea in texto.splitlines():
        sin = linea.split(" #", 1)[0].rstrip() if not linea.lstrip().startswith("#") else ""
        if not sin.strip():
            continue
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", sin)
        if m:
            clave, valor = m.group(1), m.group(2).strip()
            if valor.startswith("["):
                datos[clave] = [x.strip().strip("\"'") for x in valor.strip("[]").split(",") if x.strip()]
            elif valor:
                datos[clave] = valor.strip("\"'")
            else:
                datos[clave] = []
        elif clave and re.match(r"^\s+-\s+", sin) and isinstance(datos.get(clave), list):
            datos[clave].append(re.sub(r"^\s+-\s+", "", sin).strip().strip("\"'"))
    return datos


def politica(raiz=None):
    """Política de confidencialidad de la empresa sobre los valores por defecto. Nunca falla: si el archivo existe y no
    se puede leer, devuelve la clave `error` para que los controles lo digan (y no dejen pasar nada por las dudas)."""
    raiz = Path(raiz) if raiz else RAIZ_HARNESS
    if str(raiz) in _politicas:
        return _politicas[str(raiz)]
    pol = {k: (list(v) if isinstance(v, list) else v) for k, v in POLITICA_DEFECTO.items()}
    ruta = raiz / "empresa" / "confidencialidad.yaml"
    if ruta.is_file():
        try:
            texto = ruta.read_text(encoding="utf-8")
            try:
                import yaml
                datos = yaml.safe_load(texto) or {}
            except ImportError:
                datos = _yaml_minimo(texto)
            if not isinstance(datos, dict):
                raise ValueError("debe ser una lista de claves")
            for k in ("nunca_subir", "carpetas_de_binarios"):
                v = datos.get(k) or []
                if isinstance(v, str):
                    v = [v]
                if not isinstance(v, list):
                    raise ValueError(f"{k} debe ser una lista")
                pol[k] = [str(x).strip() for x in v if str(x).strip()]
            for k, validos in (("binarios_sueltos", ("avisar", "bloquear", "permitir")), ("claves_en_texto", ("bloquear", "avisar"))):
                v = str(datos.get(k) or pol[k]).strip().lower()
                if v not in validos:
                    raise ValueError(f"{k} debe ser uno de: {', '.join(validos)}")
                pol[k] = v
        except Exception as e:
            pol["error"] = f"empresa/confidencialidad.yaml no se puede leer ({e}): corrígelo; mientras tanto no se sube nada"
    _politicas[str(raiz)] = pol
    return pol


def coincide(patron, ruta):
    """True si `ruta` (con /) cae en `patron`, escrito como en .gitignore: `carpeta/` (en cualquier nivel si no trae /),
    `ruta/con/carpetas/`, `*.ext` o un nombre de archivo."""
    patron, ruta = patron.strip().lstrip("/"), ruta.lstrip("/")
    if not patron:
        return False
    carpetas = ruta.split("/")[:-1]
    if patron.endswith("/"):
        base = patron.rstrip("/")
        if "/" in base:
            return fnmatch(ruta, base + "/*")
        return any(fnmatch(c, base) for c in carpetas)
    if "/" in patron:
        return fnmatch(ruta, patron) or fnmatch(ruta, patron + "/*")
    return fnmatch(ruta.rsplit("/", 1)[-1], patron) or any(fnmatch(c, patron) for c in carpetas)


def motivo_sensible(ruta, raiz=None):
    """Motivo por el que `ruta` no debe subirse a Git, o None si no es confidencial. Reúne lo que el harness protege
    siempre (SENSIBLES) y lo que la empresa definió en `nunca_subir` de empresa/confidencialidad.yaml."""
    ruta = ruta.replace("\\", "/")
    if ruta.rsplit("/", 1)[-1] in MARCADORES:
        return None
    for patron, motivo in SENSIBLES:
        if re.search(patron, ruta, re.I):
            return motivo
    pol = politica(raiz)
    if pol.get("error"):
        return pol["error"] if ruta.startswith(("proyectos/", "empresa/")) else None
    for patron in pol["nunca_subir"]:
        if coincide(patron, ruta):
            return f"la empresa lo definió como confidencial: {patron}"
    return None


# --- Claves pegadas dentro de un texto -------------------------------------------------------------------------
CLAVES = [
    (r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY", "llave privada"),
    (r"\bAKIA[0-9A-Z]{16}\b", "clave de acceso de AWS"),
    (r"\bgh[pousr]_[A-Za-z0-9]{36,}\b", "token de GitHub"),
    (r"\bgithub_pat_[A-Za-z0-9_]{40,}\b", "token de GitHub"),
    (r"\bsk-[A-Za-z0-9_-]{32,}\b", "clave de API"),
    (r"\bAIza[0-9A-Za-z_-]{35}\b", "clave de API de Google"),
    (r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b", "token de Slack"),
]


def clave_en_texto(texto):
    """Qué tipo de clave o llave aparece pegada en `texto`, o None."""
    for patron, motivo in CLAVES:
        if re.search(patron, texto or ""):
            return motivo
    return None


# --- Archivos de Office, PDF, imágenes y comprimidos fuera de las carpetas donde el harness los espera ----------
BINARIOS = {".doc", ".docx", ".xls", ".xlsx", ".xlsm", ".ppt", ".pptx", ".pdf", ".png", ".jpg", ".jpeg", ".gif", ".tif",
            ".tiff", ".bmp", ".heic", ".zip", ".rar", ".7z", ".msg", ".eml", ".mpp"}
ESPERAN_BINARIOS = {"reportes", "marca", "plantillas", "formatos", "status", "salida", "salidas", "presupuesto", "economico",
                    "estudio", "propuesta", "entrega", "cronograma", "finanzas", "estrategia", "minutas", "documentos",
                    "investigaciones", "explicaciones", "ejemplos", "arquetipos", "biblioteca", "plantilla-proyecto",
                    "plantilla-subproyecto", "plantilla-empresa"}


def binario_suelto(ruta, raiz=None):
    """True si `ruta` es un Word, Excel, PDF, imagen o comprimido que no está en una carpeta de salidas, plantillas o
    marca: puede ser material del cliente guardado donde no corresponde. La empresa suma carpetas con `carpetas_de_binarios`."""
    ruta = ruta.replace("\\", "/")
    if Path(ruta).suffix.lower() not in BINARIOS:
        return False
    if set(ruta.split("/")[:-1]) & ESPERAN_BINARIOS:
        return False
    return not any(coincide(pat, ruta) for pat in politica(raiz)["carpetas_de_binarios"])


# --- Lo que está preparado para el commit (se mira el estado real, no el texto del comando) ----------------------
def git_salida(args, cwd=None, timeout=20):
    """(código, salida) de un comando de Git; (1, "") si no se pudo ejecutar."""
    try:
        r = subprocess.run(["git", "-c", "core.quotepath=false", *args], cwd=cwd, capture_output=True, timeout=timeout)
        return r.returncode, r.stdout.decode("utf-8", errors="replace")
    except Exception:
        return 1, ""


def raiz_git(cwd=None):
    """Carpeta raíz del repositorio de `cwd`, o None si no hay repositorio."""
    rc, salida = git_salida(["rev-parse", "--show-toplevel"], cwd)
    return Path(salida.strip()) if rc == 0 and salida.strip() else None


def staging_sensible(raiz):
    """[(ruta, motivo)] de los archivos confidenciales preparados para el commit en el repositorio `raiz`."""
    _, salida = git_salida(["diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z"], raiz)
    return [(r, m) for r in salida.split("\0") if r.strip() for m in [motivo_sensible(r, raiz)] if m]


def quitar_del_staging(raiz, rutas):
    """Saca `rutas` del staging sin tocar los archivos. Devuelve las que ya no quedaron preparadas."""
    if not rutas:
        return []
    rc, _ = git_salida(["restore", "--staged", "--", *rutas], raiz)
    if rc != 0:  # repositorio sin commits todavía
        git_salida(["rm", "--cached", "-q", "--", *rutas], raiz)
    quedan = {r for r, _ in staging_sensible(raiz)}
    return [r for r in rutas if r not in quedan]


def control_git_activo(raiz):
    """True si el control de Git del harness está activo en este computador (core.hooksPath = .githooks)."""
    _, salida = git_salida(["config", "--get", "core.hooksPath"], raiz)
    return salida.strip().rstrip("/\\") in (".githooks", "./.githooks")


def carpeta_de(ev):
    """Carpeta donde corre el comando del evento (campo `cwd` de Claude Code), o la carpeta actual."""
    cwd = ev.get("cwd") or ""
    return cwd if cwd and os.path.isdir(cwd) else os.getcwd()


def replica_sensible(texto):
    """True si una réplica de fuentes/ declara `confidencialidad: sensible` en su encabezado."""
    return bool(REPLICA_SENSIBLE.search(texto.split("\n---", 1)[0][:2000]))


# --- Validación de CSV y YAML ---------------------------------------------------------------------------------
COL_FECHA = re.compile(r"^(fecha.*|inicio_.*|fin_.*|.*_fecha|fecha_.*|vigente_hasta|emitido|vigencia.*)$")
FECHA_OK = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def revisar_csv(ruta):
    problemas = []
    with open(ruta, encoding="utf-8-sig", newline="") as f:
        filas = list(csv.reader(f))
    if not filas:
        return problemas
    enc = filas[0]
    dups = {c for c in enc if enc.count(c) > 1}
    if dups:
        problemas.append(f"encabezados duplicados: {', '.join(sorted(dups))}")
    idx_fecha = [i for i, c in enumerate(enc) if COL_FECHA.match(c.strip())]
    for n, fila in enumerate(filas[1:], start=2):
        if not any(x.strip() for x in fila):
            continue
        if len(fila) != len(enc):
            problemas.append(f"línea {n}: {len(fila)} columnas y el encabezado tiene {len(enc)} (¿coma sin comillas?)")
            continue
        for i in idx_fecha:
            v = fila[i].strip()
            if v and not FECHA_OK.match(v):
                problemas.append(f"línea {n}, columna '{enc[i]}': fecha '{v}' no está en formato AAAA-MM-DD")
    return problemas[:15]


def revisar_yaml(ruta):
    try:
        import yaml
    except ImportError:
        return []
    try:
        datos = yaml.safe_load(Path(ruta).read_text(encoding="utf-8")) or {}
    except Exception as e:
        return [f"YAML inválido: {e}"]
    problemas = []
    if Path(ruta).name.startswith("metricas") and isinstance(datos, dict):
        for m in datos.get("metricas") or []:
            mid = m.get("id", "?")
            if not m.get("id"):
                problemas.append("una métrica no tiene id")
            if m.get("nivel") not in ("item", "proyecto"):
                problemas.append(f"métrica {mid}: nivel debe ser item o proyecto")
            if m.get("direccion", "informativa") not in ("mayor_mejor", "menor_mejor", "informativa"):
                problemas.append(f"métrica {mid}: direccion inválida")
        ids = set()
        for otro in Path(ruta).parent.glob("metricas*.yaml"):
            try:
                ids |= {m.get("id") for m in (yaml.safe_load(otro.read_text(encoding="utf-8")) or {}).get("metricas") or []}
            except Exception:
                pass
        for r in datos.get("reglas") or []:
            if str(r.get("operador")) not in ("<=", "<", ">=", ">", "==", "!="):
                problemas.append(f"regla {r.get('id')}: operador inválido")
            if r.get("metrica") not in ids:
                problemas.append(f"regla {r.get('id')}: la métrica '{r.get('metrica')}' no está definida")
    return problemas


def revisar_investigacion(ruta):
    """Registros de una investigación (investigaciones/<id>/*.csv): columnas y valores del protocolo. Nunca rompe el hook."""
    if "investigaciones" not in Path(ruta).parts:
        return []
    try:
        carpeta = str(Path(__file__).resolve().parent.parent)
        if carpeta not in sys.path:
            sys.path.insert(0, carpeta)
        import investigacion
        return investigacion.revisar_archivo(ruta)
    except Exception:
        return []


def revisar(ruta):
    ext = Path(ruta).suffix.lower()
    if ext == ".csv":
        return revisar_csv(ruta) + revisar_investigacion(ruta)
    if ext in (".yaml", ".yml"):
        return revisar_yaml(ruta)
    return []


# --- Entrada y salida de los hooks de Claude Code -------------------------------------------------------------
def preparar_salida():
    for flujo in (sys.stdout, sys.stderr):
        try:
            flujo.reconfigure(encoding="utf-8")
        except Exception:
            pass


def leer_evento():
    try:
        return json.load(sys.stdin)
    except Exception:
        return {}


def bloquear(mensaje):
    """Código 2: Claude Code bloquea la acción (PreToolUse) o le muestra el mensaje a Claude (PostToolUse)."""
    print(mensaje, file=sys.stderr)
    sys.exit(2)
