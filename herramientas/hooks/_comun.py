"""Utilidades comunes de los controles del harness (hooks de Claude Code y control de Git antes de cada commit).

Los hooks nunca deben romper la sesión: ante un error inesperado, terminan con código 0 (no bloquean).
Aquí viven también las reglas que comparten todos los controles: qué archivos son confidenciales y cómo se
validan los CSV y YAML.
"""
import csv
import json
import re
import sys
from pathlib import Path

# --- Archivos confidenciales: nunca se suben a Git -------------------------------------------------------------
SENSIBLES = [
    (r"(^|/)_entrada/(?!LEEME\.md$)", "material sin procesar de _entrada/"),
    (r"(^|/)contractual/.*\.pdf$", "original contractual (PDF)"),
    (r"(^|/)original\.[^/]+$", "documento original"),
    (r"(^|/)documentos/.+/v\d+[^/]*\.(pdf|docx?|xlsx?|pptx?)$", "versión original de documento"),
    (r"(^|/)contenidos/archivos/", "documento del banco de contenidos (CV, certificados, antecedentes legales)"),
    (r"(^|/)entrega/final/", "paquete final presentado (firmas, declaraciones juradas, garantías)"),
    (r"(^|/)proyectos/[^/]+/postulaciones/(?!LEEME\.md$)", "documento de una postulación de terceros"),
    (r"(^|/)\.env(\.|$)", "archivo de variables de entorno"),
    (r"\.(pem|key|p12|pfx)$", "llave o certificado"),
    (r"(credencial|password|contrasena|contraseña|secret|token)", "posible credencial"),
]
MARCADORES = (".gitkeep", "LEEME.md")  # marcadores vacíos de carpeta e instrucciones: no son confidenciales
REPLICA_SENSIBLE = re.compile(r"^confidencialidad:\s*sensible\b", re.M)


def motivo_sensible(ruta):
    """Motivo por el que `ruta` no debe subirse a Git, o None si no es confidencial."""
    ruta = ruta.replace("\\", "/")
    if ruta.rsplit("/", 1)[-1] in MARCADORES:
        return None
    for patron, motivo in SENSIBLES:
        if re.search(patron, ruta, re.I):
            return motivo
    return None


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


def revisar(ruta):
    ext = Path(ruta).suffix.lower()
    if ext == ".csv":
        return revisar_csv(ruta)
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
