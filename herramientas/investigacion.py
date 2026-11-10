#!/usr/bin/env python3
"""Investigación auditable (arquetipo investigacion): abrir, guiar, validar, corregir, auditar y aprender.

Uso:
    python herramientas/investigacion.py <proyecto>                     # dónde va cada investigación y el siguiente paso
    python herramientas/investigacion.py <proyecto> --nueva <nombre-corto> [--nombre "Nombre"] [--intensidad sondeo]
                                         [--tolerancia conservador] [--cartucho biblioteca/dominios/x.md] [--forma integrada]
    python herramientas/investigacion.py <proyecto> [--instancia <id>] --revisar [--hoy AAAA-MM-DD]
    python herramientas/investigacion.py <proyecto> --instancia <id> --corregir [--aplicar]
    python herramientas/investigacion.py <proyecto> --instancia <id> --auditar [--registrar]
    python herramientas/investigacion.py <proyecto> --instancia <id> --muestra [--semilla N] [--registrar]
    python herramientas/investigacion.py <proyecto> --instancia <id> --subir estandar|forense --quien "Nombre" --motivo "..."
    python herramientas/investigacion.py <proyecto> --instancia <id> --aprender [--llevar L-01,L-02 --quien "Nombre"]
    python herramientas/investigacion.py --ajustar clave=valor --quien "Nombre" --motivo "..."
    python herramientas/investigacion.py --preferencia "texto" --quien "Nombre" [--desde <proyecto>/<id>]
    python herramientas/investigacion.py --exportar-lecciones

- Sin opciones: estado de cada investigación del proyecto (etapa, puertas, lo que falta) y el siguiente paso en
  palabras simples, con lo que hay que leer y lo que se le pide a la persona que decide. No modifica nada.
- --revisar: valida todo lo verificable del protocolo (marcas, fuentes, ID, puertas, orden de las etapas, aislamiento
  entre investigaciones). Termina con código 1 si hay errores.
- --corregir: arregla lo mecánico (valores mal escritos, H con fuente N4 → T, H con fuente N5-N6 → P, «no consultado»
  en la bitácora → vacío no-buscado). Sin --aplicar es vista previa. Cada corrección queda anotada en la fila.
- --auditar: pruebas mecánicas de auditoría (4 antigüedad, 5 independencia, 6 entidad, 7 reversibilidad, 8 cobertura);
  --muestra: afirmaciones al azar para la prueba 1, con semilla repetible. Con --registrar quedan en auditoria.csv.
- --aprender, --ajustar, --preferencia: lo aprendido y las preferencias se guardan en empresa/investigacion/, que una
  actualización del núcleo nunca toca.
"""
import argparse
import csv
import random
import re
import shutil
import sys
import time
import unicodedata
from datetime import date, datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ARQ = RAIZ / "arquetipos" / "investigacion"
PLANTILLA = ARQ / "plantilla-instancia"
CARPETA = "investigaciones"
PUERTAS = ["P0", "P1", "P2", "P3", "P4", "P5"]
PERSONA = {"P0", "P2", "P5"}
NOMBRE_ETAPA = {"E0": "Encuadre", "E1": "Cartografía", "E2": "Hipótesis asesinas", "E3": "Universo",
                "E4": "Triaje y análisis", "E5": "Contrastación", "E6": "Entregable"}
NIVELES = ["N1", "N2", "N3", "N4", "N5", "N6"]
ANCLA = {"N1", "N2", "N3"}

# Columnas de cada registro (se pueden agregar columnas al final, nunca quitar ni reordenar)
ESQUEMAS = {
    "E1_mapa_fuentes.csv": ["que_responde", "fuente", "nivel", "acceso", "costo", "latencia", "equivalente_abierto",
                            "que_se_pierde", "nota"],
    "E2_hipotesis.csv": ["id", "dimension", "debe_ser_cierto", "criterio_de_muerte", "donde_se_verifica", "costo", "estado",
                         "evidencia", "nota"],
    "E3_universo.csv": ["id", "candidato", "identificador", "senal_entrada", "sustento", "descalificador", "estado", "motivo"],
    "conclusiones.csv": ["id", "conclusion", "marca", "confianza", "sustento", "se_revierte_si", "portante", "estado", "nota"],
    "E5_impugnaciones.csv": ["id", "pase", "objeto", "impugnacion", "letalidad", "resultado", "evidencia", "refutador", "nota"],
    "auditoria.csv": ["prueba", "nombre", "resultado", "detalle", "quien", "fecha"],
    "expediente.csv": ["id", "marca", "afirmacion", "fuente", "nivel", "origen", "dato_al", "fecha_consulta", "sujeto",
                       "operacion", "estado", "nota"],
    "bitacora.csv": ["fecha", "rol", "fuente", "terminos", "resultado", "entradas", "nota"],
    "vacios.csv": ["id", "que_falta", "estado", "donde_se_busco", "terminos", "como_se_cierra", "responsable", "nota"],
    "puertas.csv": ["puerta", "entre", "estado", "firma", "tipo_firma", "fecha", "nota"],
    "metodo.csv": ["id", "fecha", "leccion", "regla_propuesta", "donde", "estado", "quien"],
}
PREFIJO_ID = {"expediente.csv": "E", "vacios.csv": "V", "conclusiones.csv": "C", "E2_hipotesis.csv": "HA",
              "E3_universo.csv": "U", "E5_impugnaciones.csv": "I", "metodo.csv": "M"}
VALORES = {
    ("E1_mapa_fuentes.csv", "nivel"): NIVELES,
    ("E2_hipotesis.csv", "estado"): ["abierta", "sobrevivio", "disparo"],
    ("E2_hipotesis.csv", "dimension"): ["disponibilidad", "vigencia", "capacidad", "demanda", "ventana", "mandato", "facultad", "otra"],
    ("E3_universo.csv", "estado"): ["entra", "reserva", "excluido"],
    ("conclusiones.csv", "marca"): ["H", "D", "I"],
    ("conclusiones.csv", "confianza"): ["alta", "media", "baja"],
    ("conclusiones.csv", "portante"): ["si", "no"],
    ("conclusiones.csv", "estado"): ["vigente", "corregida", "retirada"],
    ("E5_impugnaciones.csv", "pase"): ["1", "2"],
    ("E5_impugnaciones.csv", "letalidad"): ["alta", "media", "baja"],
    ("E5_impugnaciones.csv", "resultado"): ["pendiente", "retirada", "corregida", "sostenida"],
    ("auditoria.csv", "resultado"): ["pendiente", "pasa", "falla"],
    ("expediente.csv", "marca"): ["H", "D", "T", "P"],
    ("expediente.csv", "nivel"): NIVELES,
    ("expediente.csv", "estado"): ["vigente", "retirada"],
    ("bitacora.csv", "resultado"): ["nulo", "encontrado"],
    ("vacios.csv", "estado"): ["buscado-sin-resultado", "no-buscado", "inaccesible", "cerrado"],
    ("puertas.csv", "estado"): ["pendiente", "aprobada", "rechazada", "no-aplica"],
    ("puertas.csv", "tipo_firma"): ["persona", "arbitro"],
    ("metodo.csv", "donde"): ["protocolo", "cartucho", "ajuste"],
    ("metodo.csv", "estado"): ["propuesta", "llevada-a-empresa", "propuesta-al-nucleo", "descartada"],
}
PISTAS_VALOR = {  # explicación cuando un valor no es válido
    ("E2_hipotesis.csv", "estado"): "una hipótesis dispara o no: si dispara «a medias», divídela en dos hipótesis",
    ("expediente.csv", "marca"): "los vacíos (V) van en vacios.csv; las inferencias (I) y supuestos (S), en el análisis",
}
INTENSIDADES = ["sondeo", "estandar", "forense"]
TOLERANCIAS = ["conservador", "exploratorio"]
NO_FIRMA = {"", "pendiente", "arbitro", "agente", "ia", "asistente", "validador", "claude", "codex", "gemini", "copilot",
            "cursor", "modelo", "sistema", "firmada", "si", "ok"}
AGENTES = {"claude", "codex", "gemini", "copilot", "cursor", "asistente", "agente", "arbitro", "validador", "ia", "gpt",
           "chatgpt", "modelo", "bot", "antigravity", "subagente"}
RE_ID = re.compile(r"(?<![\w/-])(HA|E|V|C|U|I)-(\d{1,4})(?![\w])")
RE_NO_HECHA = re.compile(r"no\s+consultad|no\s+buscad|sin\s+consultar|sin\s+buscar|por\s+consultar|por\s+buscar", re.I)
SECCIONES_E0 = ["pregunta de decision", "negacion de la pregunta", "decisor", "asimetria del error",
                "separacion declarada", "intensidad y tolerancia", "criterio de exito"]
SECCIONES_E6 = ["respuesta", "fundamento", "conclusiones y condicion de revision", "lo que no se sabe", "limite de cobertura"]
ROL_ETAPA = {"E0": "encuadrador", "E1": "cartografo", "E2": "refutador (pase 1) y bibliotecario", "E3": "analista y bibliotecario",
             "E4": "analista", "E5": "refutador (pase 2) y arbitro", "E6": "editor"}
AJUSTES_DEFECTO = {
    "por_defecto": {"intensidad": "sondeo", "tolerancia": "", "restriccion_fuentes": "", "cartucho": ""},
    "reglas": {"antiguedad_max_anios": 2, "minimo_hipotesis": 5, "muestra_trazabilidad": 10},
    "refutador": {"asistente": "", "modelo": ""},
    "preferencias": [],
    "historial": [],
}
CLAVES_AJUSTABLES = {
    "por_defecto.intensidad": INTENSIDADES, "por_defecto.tolerancia": TOLERANCIAS + [""],
    "por_defecto.restriccion_fuentes": None, "por_defecto.cartucho": None,
    "reglas.antiguedad_max_anios": int, "reglas.minimo_hipotesis": int, "reglas.muestra_trazabilidad": int,
    "refutador.asistente": None, "refutador.modelo": None,
}
LECCIONES_COLS = ["id", "fecha", "leccion", "regla", "donde", "cartucho", "origen", "quien", "estado"]


# ------------------------------------------------------------------------------------------------ utilidades
def norm(texto):
    """Minúsculas, sin tildes ni espacios sobrantes (para comparar valores y títulos)."""
    t = unicodedata.normalize("NFKD", str(texto or "")).encode("ascii", "ignore").decode().lower().strip()
    return re.sub(r"\s+", " ", t)


def version_protocolo():
    m = re.search(r"Versión del protocolo:\s*([\d.]+)", (ARQ / "protocolo" / "PROTOCOLO.md").read_text(encoding="utf-8"))
    return m.group(1) if m else ""


def consolidar(inst):
    """Une los archivos parciales de bibliotecarios que trabajaron en paralelo (expediente.parcial-*.csv,
    bitacora.parcial-*.csv, vacios.parcial-*.csv) a los archivos de la investigación. Cada parcial usa su rango de IDs
    (E-101…, E-201…): un ID repetido entre parciales o con lo existente es error y no se escribe nada.
    Devuelve (resumen, errores); los parciales consolidados quedan en _parciales-consolidados/."""
    plan, errores = [], []
    for nombre in ("expediente.csv", "bitacora.csv", "vacios.csv"):
        parciales = sorted(inst.carpeta.glob(f"{nombre[:-4]}.parcial-*.csv"))
        if not parciales:
            continue
        enc, filas = leer_csv(inst.carpeta / nombre)
        enc = enc or ESQUEMAS[nombre]
        ids = {f.get("id") for f in filas if f.get("id")}
        nuevas = []
        for p in parciales:
            _, pf = leer_csv(p)
            for f in pf:
                i = f.get("id", "")
                if "id" in enc:
                    if not i:
                        errores.append(f"{p.name}: fila sin id")
                        continue
                    if i in ids:
                        errores.append(f"{p.name}: ID repetido {i} (cada bibliotecario usa el rango que le dio el líder: E-101…, E-201…)")
                        continue
                    ids.add(i)
                nuevas.append(f)
        plan.append((nombre, enc, filas + nuevas, parciales, len(nuevas)))
    if errores:
        return [], errores
    resumen = []
    destino = inst.carpeta / "_parciales-consolidados"
    for nombre, enc, filas, parciales, n in plan:
        escribir_csv(inst.carpeta / nombre, enc, filas)
        destino.mkdir(exist_ok=True)
        for p in parciales:
            p.rename(destino / p.name)
        resumen.append(f"{nombre}: {n} fila(s) de {len(parciales)} parcial(es)")
    return resumen, errores


def leer_csv(ruta):
    """(encabezado, filas como dict). Archivo ausente = ([], [])."""
    if not ruta.exists():
        return [], []
    with open(ruta, encoding="utf-8-sig", newline="") as f:
        lector = csv.reader(f)
        filas = [r for r in lector]
    if not filas:
        return [], []
    enc = [c.strip() for c in filas[0]]
    salida = []
    for r in filas[1:]:
        if not any(x.strip() for x in r):
            continue
        r = r + [""] * (len(enc) - len(r))
        salida.append({c: (r[i] if i < len(r) else "").strip() for i, c in enumerate(enc)})
    return enc, salida


def escribir_csv(ruta, encabezado, filas):
    with open(ruta, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=encabezado, extrasaction="ignore")
        w.writeheader()
        for fila in filas:
            w.writerow({c: fila.get(c, "") for c in encabezado})


def fecha_ok(v):
    try:
        datetime.strptime(v, "%Y-%m-%d")
        return True
    except (TypeError, ValueError):
        return False


def fecha_parcial(v):
    """dato_al admite AAAA, AAAA-MM o AAAA-MM-DD. Devuelve la fecha (primer día) o None."""
    v = (v or "").strip()
    for fmt, largo in (("%Y-%m-%d", 10), ("%Y-%m", 7), ("%Y", 4)):
        if len(v) == largo:
            try:
                return datetime.strptime(v, fmt).date()
            except ValueError:
                return None
    return None


def ids_en(texto):
    return [f"{m.group(1)}-{m.group(2)}" for m in RE_ID.finditer(texto or "")]


def clave_id(i):
    m = re.match(r"([A-Z]+)-(\d+)$", i)
    return (m.group(1), int(m.group(2))) if m else (i, 0)


def limpiar_md(texto):
    """Texto de un .md sin comentarios HTML ni marcadores <…> de la plantilla."""
    texto = re.sub(r"<!--.*?-->", "", texto, flags=re.S)
    return re.sub(r"<[^<>]{3,}>", "", texto)  # los marcadores de la plantilla pueden ocupar varias líneas


def secciones_md(texto):
    """{título normalizado: contenido útil} de las secciones `## ` de un .md."""
    salida, actual, buf = {}, None, []
    for linea in limpiar_md(texto).splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", linea)
        if m:
            if actual is not None:
                salida[actual] = "\n".join(buf).strip()
            actual, buf = norm(m.group(1)), []
        elif actual is not None:
            buf.append(linea)
    if actual is not None:
        salida[actual] = "\n".join(buf).strip()
    return salida


def sin_contenido(texto):
    return not re.sub(r"^#.*$|^[-*]\s*[^:\n]*:\s*$|\s+", "", limpiar_md(texto or ""), flags=re.M)


def leer_yaml(ruta):
    import yaml
    try:
        return yaml.safe_load(ruta.read_text(encoding="utf-8")) or {}
    except Exception as e:  # el validador informa; nunca se cae por un YAML mal escrito
        return {"_error": str(e)}


def poner_campo(texto, clave, valor):
    """Cambia `  clave: valor` de un YAML conservando los comentarios."""
    v = '"' + str(valor).replace('"', "'") + '"'
    patron = rf"^([ \t]+{re.escape(clave)}:[ \t]*)(\"[^\"\n]*\"|'[^'\n]*'|[^#\n]*?)([ \t]*(#.*)?)$"
    nuevo, n = re.subn(patron, lambda m: m.group(1) + v + (("   " + m.group(4)) if m.group(4) else ""), texto, count=1, flags=re.M)
    return nuevo if n else texto


def es_mantenedor():
    try:
        import _nucleo
        return _nucleo.es_mantenedor(RAIZ)
    except Exception:
        return False


# ------------------------------------------------------------------------------------------------ ajustes y lecciones
def carpeta_empresa(raiz=RAIZ):
    return Path(raiz) / "empresa" / "investigacion"


def cargar_ajustes(raiz=RAIZ):
    import copy
    datos = copy.deepcopy(AJUSTES_DEFECTO)
    ruta = carpeta_empresa(raiz) / "ajustes.yaml"
    if ruta.exists():
        leido = leer_yaml(ruta)
        if isinstance(leido, dict) and "_error" not in leido:
            for k, v in leido.items():
                if isinstance(v, dict) and isinstance(datos.get(k), dict):
                    datos[k].update({a: b for a, b in v.items() if b is not None})
                elif v is not None:
                    datos[k] = v
    return datos


def escribir_ajustes(datos, raiz=RAIZ):
    """Reescribe ajustes.yaml con sus comentarios (plantilla del arquetipo) y los valores vigentes."""
    import yaml
    ruta = carpeta_empresa(raiz) / "ajustes.yaml"
    ruta.parent.mkdir(parents=True, exist_ok=True)
    texto = (ARQ / "ajustes.ejemplo.yaml").read_text(encoding="utf-8")
    for seccion in ("por_defecto", "reglas", "refutador"):
        for clave, valor in (datos.get(seccion) or {}).items():
            bloque = re.search(rf"^{seccion}:\n((?:[ \t]+.*\n?)*)", texto, re.M)
            if not bloque:
                continue
            if isinstance(valor, int):
                linea = re.sub(rf"^([ \t]+{clave}:[ \t]*)\S+", lambda m: m.group(1) + str(valor), bloque.group(1), count=1, flags=re.M)
            else:
                linea = poner_campo(bloque.group(1), clave, valor)
            texto = texto[:bloque.start(1)] + linea + texto[bloque.end(1):]
    for lista in ("preferencias", "historial"):
        items = datos.get(lista) or []
        dump = yaml.safe_dump(items, allow_unicode=True, sort_keys=False, default_flow_style=False).rstrip() if items else "[]"
        bloque = "\n" + "\n".join("  " + x for x in dump.splitlines()) if items else " []"
        texto = re.sub(rf"^{lista}:.*$", lambda m: f"{lista}:{bloque}", texto, count=1, flags=re.M)
    extra = {k: v for k, v in datos.items() if k not in AJUSTES_DEFECTO}
    if extra:  # claves que la empresa agregó a mano: se conservan
        texto = texto.rstrip() + "\n" + yaml.safe_dump(extra, allow_unicode=True, sort_keys=False)
    ruta.write_text(texto, encoding="utf-8")
    return ruta


def asegurar_ajustes(raiz=RAIZ):
    ruta = carpeta_empresa(raiz) / "ajustes.yaml"
    if not ruta.exists():
        ruta.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ARQ / "ajustes.ejemplo.yaml", ruta)
        return True
    return False


def leer_lecciones(raiz=RAIZ):
    return leer_csv(carpeta_empresa(raiz) / "lecciones.csv")[1]


# ------------------------------------------------------------------------------------------------ instancias
def proyecto_de(arg):
    p = Path(arg)
    p = p if p.is_absolute() else (RAIZ / p)
    if not (p / "proyecto.yaml").exists():
        sys.exit(f"No encuentro el proyecto {arg} (falta proyecto.yaml). Usa la ruta, por ejemplo proyectos/<slug>.")
    return p.resolve()


def instancias_de(proyecto):
    base = Path(proyecto) / CARPETA
    if not base.is_dir():
        return []
    return sorted(c for c in base.iterdir() if c.is_dir() and (c / "manifiesto.yaml").exists())


def todas_las_instancias(raiz=RAIZ):
    proyectos = Path(raiz) / "proyectos"
    salida = []
    if proyectos.is_dir():
        for p in sorted(proyectos.iterdir()):
            if (p / "proyecto.yaml").exists():
                salida += instancias_de(p)
                salida += [i for s in sorted((p / "subproyectos").glob("*")) for i in instancias_de(s)]
    return salida


class Instancia:
    def __init__(self, carpeta):
        self.carpeta = Path(carpeta)
        self.id = self.carpeta.name
        datos = leer_yaml(self.carpeta / "manifiesto.yaml")
        self.yaml_error = datos.get("_error") if isinstance(datos, dict) else "manifiesto ilegible"
        self.m = (datos.get("investigacion") or {}) if isinstance(datos, dict) else {}
        self.reg = {}
        for nombre in ESQUEMAS:
            self.reg[nombre] = leer_csv(self.carpeta / nombre)

    def filas(self, nombre):
        return self.reg[nombre][1]

    def campo(self, clave):
        return str(self.m.get(clave) or "").strip()

    def texto(self, nombre):
        ruta = self.carpeta / nombre
        return ruta.read_text(encoding="utf-8", errors="replace") if ruta.exists() else ""

    def puertas(self):
        return {f.get("puerta", ""): f for f in self.filas("puertas.csv")}

    def puerta_ok(self, p):
        return norm(self.puertas().get(p, {}).get("estado")) in ("aprobada", "no-aplica")

    def etapa(self):
        if self.campo("cierre"):
            return "cerrada"
        for i, p in enumerate(PUERTAS):
            if not self.puerta_ok(p):
                return f"E{i}"
        return "E6"

    def expediente(self):
        return {f.get("id"): f for f in self.filas("expediente.csv")}

    def todos_los_ids(self):
        ids = {}
        for nombre, pref in PREFIJO_ID.items():
            for f in self.filas(nombre):
                if f.get("id"):
                    ids[f["id"]] = nombre
        return ids


# ------------------------------------------------------------------------------------------------ validación
class Informe:
    def __init__(self):
        self.errores, self.pendientes, self.avisos = [], [], []
        self.puerta_en_curso = ""

    def pendientes_en_curso(self):
        """Lo que falta para la puerta en curso (lo de puertas posteriores todavía no se exige)."""
        return [x for x in self.pendientes if x.startswith(f"[{self.puerta_en_curso}]")]

    def error(self, donde, texto):
        self.errores.append(f"{donde}: {texto}")

    def falta(self, puerta, donde, texto):
        self.pendientes.append(f"[{puerta}] {donde}: {texto}")

    def aviso(self, donde, texto):
        self.avisos.append(f"{donde}: {texto}")


def revisar_estructura(nombre, enc, filas, inf):
    """Columnas y valores permitidos de un registro (lo mismo que revisa el hook al editar)."""
    esperado = ESQUEMAS[nombre]
    if enc and enc[:len(esperado)] != esperado:
        inf.error(nombre, "columnas distintas a las del protocolo. Deben empezar con: " + ",".join(esperado)
                  + " (se pueden agregar columnas al final).")
        return
    pref = PREFIJO_ID.get(nombre)
    vistos = set()
    for n, f in enumerate(filas, start=2):
        donde = f"{nombre} línea {n}" + (f" ({f.get('id')})" if f.get("id") else "")
        if pref:
            i = f.get("id", "")
            if not re.fullmatch(rf"{pref}-\d+", i):
                inf.error(donde, f"el ID debe tener la forma {pref}-01.")
            elif i in vistos:
                inf.error(donde, f"ID repetido {i}.")
            vistos.add(i)
        for (archivo, col), permitidos in VALORES.items():
            if archivo != nombre:
                continue
            v = f.get(col, "")
            if v == "" and (col not in ("marca", "estado", "resultado", "pase") or (nombre, col) == ("expediente.csv", "estado")):
                continue
            if v not in permitidos:
                pista = PISTAS_VALOR.get((archivo, col), "")
                sugerido = next((p for p in permitidos if norm(p) == norm(v)), "")
                inf.error(donde, f"«{v or '(vacío)'}» no es un valor válido de {col} (usa: {', '.join(permitidos)})."
                          + (f" Corrección automática: {sugerido}." if sugerido else "") + (f" Nota: {pista}." if pista else ""))
        if nombre == "expediente.csv" and f.get("marca") == "H" and f.get("nivel") in NIVELES and f.get("nivel") not in ANCLA:
            inf.error(donde, f"marcado H con fuente {f.get('nivel')}. H solo con fuentes N1 a N3 abiertas en esta investigación: "
                      + ("una fuente N4 es la parte interesada y solo admite T." if f.get("nivel") == "N4" else
                         "lo visto en N5-N6 es una pista (P) hasta leerlo en el registro.") + " Se corrige con --corregir.")


def revisar_archivo(ruta):
    """Para el hook al editar: problemas de estructura de un registro de investigación (lista vacía si no aplica)."""
    ruta = Path(ruta)
    if ruta.name not in ESQUEMAS or CARPETA not in ruta.parts:
        return []
    inf = Informe()
    enc, filas = leer_csv(ruta)
    revisar_estructura(ruta.name, enc, filas, inf)
    return inf.errores[:15]


RE_SIN_FIRMA = re.compile(r"pendiente|sin nombre|sin firma|por definir|por designar|por confirmar|\?")


def firma_valida(fila):
    firma = norm(fila.get("firma"))
    return firma not in NO_FIRMA and not RE_SIN_FIRMA.search(firma) and fecha_ok(fila.get("fecha", ""))


def parece_agente(firma):
    return bool(set(re.findall(r"[a-z]+", norm(firma))) & AGENTES)


def anclado(eid, exp, visitados=None):
    """True si la entrada es H de fuente N1-N3, o D cuya operación usa al menos un H anclado."""
    f = exp.get(eid)
    if not f or f.get("estado") == "retirada":
        return False
    if f.get("marca") == "H":
        return f.get("nivel") in ANCLA
    if f.get("marca") == "D":
        visitados = visitados or set()
        if eid in visitados:
            return False
        visitados.add(eid)
        return any(anclado(x, exp, visitados) for x in ids_en(f.get("operacion")) if x != eid)
    return False


def revisar(inst, hoy=None, ajustes=None, raiz=RAIZ):
    """Valida una investigación. Devuelve un Informe (errores, pendientes de la puerta en curso, avisos)."""
    hoy = hoy or date.today()
    ajustes = ajustes or cargar_ajustes(raiz)
    reglas = ajustes.get("reglas") or {}
    inf = Informe()
    if inst.yaml_error:
        inf.error("manifiesto.yaml", f"no se puede leer: {inst.yaml_error}")
    for nombre, (enc, filas) in inst.reg.items():
        if not enc and nombre in ("expediente.csv", "puertas.csv", "bitacora.csv"):
            inf.error(nombre, "falta el archivo o su encabezado (cópialo de arquetipos/investigacion/plantilla-instancia/).")
            continue
        revisar_estructura(nombre, enc, filas, inf)

    intensidad, tolerancia = norm(inst.campo("intensidad")), norm(inst.campo("tolerancia"))
    if intensidad and intensidad not in INTENSIDADES:
        inf.error("manifiesto.yaml", f"intensidad «{inst.campo('intensidad')}» no válida (sondeo, estandar o forense).")
    if tolerancia and tolerancia not in TOLERANCIAS:
        inf.error("manifiesto.yaml", f"tolerancia «{inst.campo('tolerancia')}» no válida (conservador o exploratorio).")
    exp = inst.expediente()
    ids = inst.todos_los_ids()
    puertas = inst.puertas()
    etapa = inst.etapa()

    # Puertas: firmas y orden
    for p in PUERTAS:
        if p not in puertas:
            inf.error("puertas.csv", f"falta la fila de {p}.")
    for i, p in enumerate(PUERTAS):
        f = puertas.get(p)
        if not f:
            continue
        estado = f.get("estado")
        if estado == "aprobada":
            if not firma_valida(f):
                inf.error(f"puertas.csv {p}", "aprobada sin firma válida (nombre y fecha AAAA-MM-DD). «Pendiente», un rol o un "
                          "asistente no son firma.")
            if p in PERSONA and (f.get("tipo_firma") != "persona" or parece_agente(f.get("firma"))):
                inf.error(f"puertas.csv {p}", "la firma una persona (la que decide), no un agente ni el árbitro.")
            decisor = inst.campo("decisor")
            if p in PERSONA and decisor and norm(f.get("firma")) not in NO_FIRMA and norm(decisor) not in norm(f.get("firma")) \
                    and norm(f.get("firma")) not in norm(decisor):
                inf.aviso(f"puertas.csv {p}", f"firmó «{f.get('firma')}» y el decisor declarado es «{decisor}».")
            antes = [q for q in PUERTAS[:i] if not inst.puerta_ok(q)]
            if antes:
                inf.error(f"puertas.csv {p}", f"aprobada sin que estén firmadas antes {', '.join(antes)}: las puertas van en orden.")
        if estado == "no-aplica" and intensidad != "sondeo" and p != "P3":
            inf.error(f"puertas.csv {p}", "solo en un sondeo una puerta (salvo P3) puede quedar no-aplica.")
        if estado == "rechazada":
            inf.aviso(f"puertas.csv {p}", "rechazada: " + {"P0": "se devuelve al solicitante.", "P1": "se declara el dominio sin ancla "
                      "registral (producto: informe-de-indicios).", "P2": "se reencuadra (vuelve a E0) o se cierra.",
                      "P3": "se purgan los candidatos sin señal.", "P4": "las afirmaciones sin sustento vuelven al bibliotecario "
                      "o bajan a I, S o V.", "P5": "se retira la conclusión tumbada; nunca se la defiende."}.get(p, ""))
    if intensidad == "sondeo":
        for p in ("P1", "P3", "P4", "P5"):
            if puertas.get(p, {}).get("estado") == "pendiente":
                inf.aviso(f"puertas.csv {p}", "en un sondeo queda no-aplica (lo corrige --corregir).")

    inf.puerta_en_curso = next((p for p in PUERTAS if not inst.puerta_ok(p)), "")

    def criterio(puerta, donde, texto):
        """Criterio de una puerta: error si ya se firmó sin cumplirlo; si no, pendiente para firmarla."""
        if puertas.get(puerta, {}).get("estado") == "no-aplica":
            return
        if puertas.get(puerta, {}).get("estado") == "aprobada":
            inf.error(donde, f"{texto} (la puerta {puerta} está firmada sin cumplirlo).")
        else:
            inf.falta(puerta, donde, texto)

    # E0 · encuadre (P0)
    sec = secciones_md(inst.texto("E0_encuadre.md"))
    faltan0 = [s for s in SECCIONES_E0 if sin_contenido(sec.get(s, ""))]
    if faltan0:
        criterio("P0", "E0_encuadre.md", "faltan secciones: " + ", ".join(faltan0))
    for clave in ("decisor", "intensidad", "tolerancia"):
        if not inst.campo(clave):
            criterio("P0", "manifiesto.yaml", f"falta «{clave}»" + (" (una persona con nombre)" if clave == "decisor" else ""))

    # E1 · mapa (P1)
    mapa = inst.filas("E1_mapa_fuentes.csv")
    if not any(f.get("nivel") in ("N1", "N2") for f in mapa) and norm(inst.campo("producto")) != "informe-de-indicios":
        criterio("P1", "E1_mapa_fuentes.csv", "no hay ninguna fuente N1 o N2: o se encuentra una, o se declara "
                 "producto: informe-de-indicios en el manifiesto")

    # E2 · hipótesis asesinas (P2)
    ha = inst.filas("E2_hipotesis.csv")
    minimo = max(3, int(reglas.get("minimo_hipotesis") or 5))
    if len(ha) < 3:
        criterio("P2", "E2_hipotesis.csv", f"hay {len(ha)} hipótesis asesinas; se necesitan al menos 3 (lo esperado son 5 o 6)")
    elif len(ha) < minimo:
        inf.aviso("E2_hipotesis.csv", f"hay {len(ha)} hipótesis; lo esperado son {minimo} o más.")
    for f in ha:
        donde = f"E2_hipotesis.csv {f.get('id')}"
        est = f.get("estado")
        if est == "abierta":
            criterio("P2", donde, "sigue abierta: hay que correrla (buscar lo que la mataría)")
        elif est == "disparo":
            criterio("P2", donde, "disparó: se reencuadra (vuelve a E0) o se cierra la investigación")
        if est in ("sobrevivio", "disparo"):
            evid = ids_en(f.get("evidencia"))
            for x in evid:
                if x not in ids:
                    inf.error(donde, f"cita {x}, que no existe en esta investigación.")
            fuertes = [x for x in evid if anclado(x, exp)]
            if est == "sobrevivio" and not fuertes:
                criterio("P2", donde, "se cerró sin evidencia H o D (un testimonio o la confianza de quien encarga no "
                         "cierran una hipótesis asesina)")

    # Construir antes de matar
    construido = inst.filas("E3_universo.csv") or inst.filas("conclusiones.csv") or \
        not sin_contenido("\n".join(v for k, v in secciones_md(inst.texto("E4_analisis.md")).items() if k != "senales de entrada al universo"))
    if construido and not inst.puerta_ok("P2"):
        inf.error("E3/E4", "hay universo, análisis o conclusiones antes de firmar P2. Construir antes de matar es el error que "
                  "el protocolo impide: primero se corren y firman las hipótesis asesinas.")

    # E3 · universo (P3)
    for f in inst.filas("E3_universo.csv"):
        donde = f"E3_universo.csv {f.get('id')}"
        sust = ids_en(f.get("sustento"))
        for x in sust:
            if x not in ids:
                inf.error(donde, f"cita {x}, que no existe en esta investigación.")
        if f.get("estado") == "entra":
            for col, txt in (("identificador", "identificador duro"), ("senal_entrada", "señal de entrada observable")):
                if not f.get(col):
                    criterio("P3", donde, f"entra sin {txt}")
            if not sust:
                criterio("P3", donde, "entra sin sustento (ID del expediente)")
        elif f.get("estado") == "excluido" and not sust:
            if tolerancia == "conservador":
                inf.error(donde, "excluido sin evidencia negativa citada: en modo conservador va a reserva (por ausencia de evidencia).")
            else:
                criterio("P3", donde, "excluido sin evidencia negativa citada")
        elif f.get("estado") == "reserva" and not f.get("motivo"):
            inf.aviso(donde, "en reserva sin decir qué falta para evaluarlo (columna motivo).")

    # E4 · conclusiones (P4)
    for f in inst.filas("conclusiones.csv"):
        donde = f"conclusiones.csv {f.get('id')}"
        sust = ids_en(f.get("sustento"))
        for x in sust:
            if x not in ids:
                inf.error(donde, f"cita {x}, que no existe en esta investigación.")
            elif exp.get(x, {}).get("estado") == "retirada":
                inf.aviso(donde, f"se apoya en {x}, que el árbitro retiró del expediente operativo.")
        if f.get("portante") == "si" and f.get("estado") != "retirada":
            if not any(anclado(x, exp) for x in sust):
                criterio("P4", donde, "conclusión portante sin sustento H o D de fuentes N1-N3 (vuelve al bibliotecario o baja a I, S o V)")
            if norm(f.get("se_revierte_si")) in ("", "ninguno", "ninguna", "nada", "no aplica"):
                criterio("P4", donde, "falta qué hallazgo la revertiría (columna se_revierte_si)")
            if not f.get("confianza"):
                criterio("P4", donde, "falta la confianza (alta, media o baja)")

    # E5 · contrastación y auditoría (P5)
    imp = inst.filas("E5_impugnaciones.csv")
    concl = {f.get("id"): f for f in inst.filas("conclusiones.csv")}
    for f in imp:
        donde = f"E5_impugnaciones.csv {f.get('id')}"
        obj = f.get("objeto", "")
        if obj not in ids:
            inf.error(donde, f"impugna «{obj}», que no existe (pase 1: una HA; pase 2: una conclusión C).")
        if f.get("resultado") == "pendiente":
            criterio("P5", donde, "impugnación sin resolver")
        if f.get("resultado") == "retirada" and obj in concl and concl[obj].get("estado") != "retirada":
            criterio("P5", donde, f"la impugnación tumbó {obj} pero la conclusión sigue {concl[obj].get('estado') or 'vigente'}: se retira, no se matiza")
        if f.get("resultado") == "sostenida" and not ids_en(f.get("evidencia")):
            criterio("P5", donde, "sostenida sin evidencia nueva citada")
        for x in ids_en(f.get("evidencia")):
            if x not in ids:
                inf.error(donde, f"cita {x}, que no existe en esta investigación.")
    if intensidad != "sondeo":
        pase2 = [f for f in imp if f.get("pase") == "2"]
        if not pase2:
            criterio("P5", "E5_impugnaciones.csv", "no hay impugnaciones del pase 2. Una lista vacía es fallo del refutador, no éxito del analista")
        if intensidad == "forense" and len({norm(f.get("refutador")) for f in pase2 if f.get("refutador")}) < 2:
            criterio("P5", "E5_impugnaciones.csv", "en forense hacen falta dos refutadores distintos (columna refutador)")
        aud = {f.get("prueba"): f for f in inst.filas("auditoria.csv")}
        malas = [f"{k} {aud[k].get('nombre')}" for k in sorted(aud) if aud[k].get("resultado") != "pasa"]
        if len(aud) < 8:
            criterio("P5", "auditoria.csv", "faltan filas de las ocho pruebas")
        elif malas:
            criterio("P5", "auditoria.csv", "pruebas sin pasar: " + "; ".join(malas))

    # Expediente
    for f in inst.filas("expediente.csv"):
        donde = f"expediente.csv {f.get('id')}"
        marca, nivel = f.get("marca"), f.get("nivel")
        if marca in ("H", "T", "P"):
            if not f.get("fuente"):
                inf.error(donde, "sin fuente (URL o documento).")
            if not fecha_ok(f.get("fecha_consulta", "")):
                inf.error(donde, "sin fecha de consulta AAAA-MM-DD. Si no se abrió en esta investigación, no existe.")
            if not nivel:
                inf.error(donde, "sin nivel de fuente (N1 a N6).")
        if marca == "H" and not f.get("dato_al"):
            inf.error(donde, "H sin fecha del dato (columna dato_al: AAAA, AAAA-MM o AAAA-MM-DD).")
        if f.get("dato_al") and not fecha_parcial(f.get("dato_al")):
            inf.error(donde, f"dato_al «{f.get('dato_al')}» debe ser AAAA, AAAA-MM o AAAA-MM-DD.")
        if marca == "H" and not f.get("origen"):
            inf.aviso(donde, "sin origen (quién generó el dato): sirve para la prueba de independencia.")
        if marca == "D":
            refs = ids_en(f.get("operacion"))
            if not f.get("operacion") or not refs:
                inf.error(donde, "D sin operación explícita con los ID de origen (por ejemplo «E-03 + 20 años»).")
            for x in refs:
                if x not in ids:
                    inf.error(donde, f"la operación usa {x}, que no existe.")
            if nivel in ("N4", "N5", "N6"):
                inf.error(donde, f"D construido sobre una fuente {nivel}: es una pista (P) hasta verificar el origen. Se corrige con --corregir.")
        if marca == "T" and not f.get("sujeto"):
            inf.error(donde, "T sin sujeto (quién lo afirma).")
        if marca == "P" and nivel in ANCLA:
            inf.error(donde, f"pista con fuente {nivel}: si se leyó en la fuente misma, es H.")
        if marca == "P" and nivel == "N4":
            inf.error(donde, "lo que dice la parte interesada (N4) es testimonio (T), no pista.")

    # Bitácora y vacíos
    bit = inst.filas("bitacora.csv")
    for n, f in enumerate(bit, start=2):
        donde = f"bitacora.csv línea {n}"
        if RE_NO_HECHA.search(" ".join([f.get("resultado", ""), f.get("nota", ""), f.get("entradas", "")])):
            inf.error(donde, "no es una búsqueda hecha («no consultado», «pendiente»): lo no buscado va a vacios.csv como "
                      "no-buscado. Se corrige con --corregir.")
        for x in ids_en(f.get("entradas")):
            if x not in ids:
                inf.error(donde, f"cita {x}, que no existe.")
    if bit and not any(f.get("resultado") == "nulo" for f in bit):
        inf.aviso("bitacora.csv", "no hay búsquedas nulas registradas: la prueba 8 (cobertura) fallará si sigue así.")
    for f in inst.filas("vacios.csv"):
        donde = f"vacios.csv {f.get('id')}"
        if f.get("estado") == "buscado-sin-resultado" and not (f.get("donde_se_busco") and f.get("terminos")):
            inf.error(donde, "un vacío buscado debe decir dónde y con qué términos se buscó.")
        if f.get("estado") in ("no-buscado", "inaccesible") and not f.get("como_se_cierra"):
            inf.aviso(donde, "falta cómo se cierra este vacío.")

    # Citas en el análisis y el entregable; aislamiento entre investigaciones
    otras = {o.name: o for o in (inst.carpeta.parent.iterdir() if inst.carpeta.parent.exists() else [])
             if o.is_dir() and o != inst.carpeta}
    codigos_otras = {}
    for nombre_o, o in otras.items():
        m = re.search(r"codigo:\s*\"?([A-Za-z]+-\d{4}-\d+)", (o / "manifiesto.yaml").read_text(encoding="utf-8", errors="replace")
                      if (o / "manifiesto.yaml").exists() else "")
        if m:
            codigos_otras[m.group(1)] = nombre_o
    for nombre in ("E4_analisis.md", "E6_entregable.md"):
        texto = limpiar_md(inst.texto(nombre))
        for x in sorted(set(ids_en(texto)), key=clave_id):
            if x not in ids:
                inf.error(nombre, f"cita {x}, que no existe en esta investigación.")
        for etiqueta in list(otras) + list(codigos_otras):
            for m in re.finditer(re.escape(etiqueta) + r"\W{0,3}(?:/|\s)?((?:HA|E|V|C|U|I)-\d+)", texto):
                inf.error(nombre, f"usa {m.group(1)} de otra investigación ({etiqueta}). Los hechos no cruzan: reingrésalo "
                          "aquí con su propia fuente y fecha.")
            if etiqueta in texto and not re.search(re.escape(etiqueta) + r"\W{0,3}(?:/|\s)?(?:HA|E|V|C|U|I)-\d", texto):
                inf.aviso(nombre, f"menciona otra investigación ({etiqueta}): si usa un hecho de ella, debe reingresarlo.")
    for nombre in ("expediente.csv", "conclusiones.csv", "E3_universo.csv"):
        for f in inst.filas(nombre):
            celdas = " ".join(f.values())
            for etiqueta in otras:
                if f"{CARPETA}/{etiqueta}" in celdas.replace("\\", "/"):
                    inf.error(f"{nombre} {f.get('id', '')}", f"apunta a otra investigación ({etiqueta}): los hechos no cruzan.")

    # Entregable
    sec6 = secciones_md(inst.texto("E6_entregable.md"))
    escrito6 = not all(sin_contenido(v) for v in sec6.values())
    if escrito6 and not inst.puerta_ok("P5" if intensidad != "sondeo" else "P2"):
        inf.error("E6_entregable.md", "se escribió antes de su puerta (" + ("P5" if intensidad != "sondeo" else "P2") + ").")
    citas6 = set(ids_en(limpiar_md(inst.texto("E6_entregable.md"))))
    for x in sorted(citas6, key=clave_id):
        if x in concl and concl[x].get("estado") == "retirada":
            inf.error("E6_entregable.md", f"cita {x}, una conclusión retirada: una conclusión tumbada no se defiende.")
        if exp.get(x, {}).get("nivel") == "N6":
            inf.error("E6_entregable.md", f"cita {x}, de fuente N6: N6 jamás se cita en el entregable.")
    if inst.campo("cierre"):
        faltan6 = [s for s in SECCIONES_E6 if sin_contenido(sec6.get(s, ""))]
        if faltan6:
            inf.error("E6_entregable.md", "cerrada con secciones vacías: " + ", ".join(faltan6))
        if intensidad == "sondeo" and "sondeo" not in norm(inst.texto("E6_entregable.md")):
            inf.aviso("E6_entregable.md", "un sondeo debe decirlo en el entregable («sondeo: sin contrastación»).")
    if inst.campo("protocolo") and inst.campo("protocolo") != version_protocolo():
        inf.aviso("manifiesto.yaml", f"corre bajo el protocolo {inst.campo('protocolo')} y el vigente es {version_protocolo()}: "
                  "sigue con su versión salvo que la persona que decide acepte migrar (se anota en puertas.csv).")
    if etapa == "cerrada" and any(f.get("estado") == "propuesta" for f in inst.filas("metodo.csv")):
        inf.aviso("metodo.csv", "hay lecciones sin revisar: --aprender las muestra para llevarlas a la empresa.")
    return inf


# ------------------------------------------------------------------------------------------------ auditoría
def auditar(inst, hoy=None, ajustes=None):
    """Pruebas mecánicas 4, 5, 6, 7 y 8: {prueba: (resultado o None, detalle)}. None = falta el juicio del árbitro."""
    hoy = hoy or date.today()
    reglas = (ajustes or cargar_ajustes()).get("reglas") or {}
    anios = int(reglas.get("antiguedad_max_anios") or 2)
    exp = inst.expediente()
    portantes = [f for f in inst.filas("conclusiones.csv") if f.get("portante") == "si" and f.get("estado") != "retirada"]
    res = {}
    viejos = []
    for c in portantes:
        for x in ids_en(c.get("sustento")):
            e = exp.get(x, {})
            d = fecha_parcial(e.get("dato_al"))
            if d and (hoy - d).days > 365 * anios and "vigencia verificada" not in norm(e.get("nota")):
                viejos.append(f"{c.get('id')} ← {x} (dato al {e.get('dato_al')})")
    res["4"] = ("falla" if viejos else "pasa", ("Datos de más de %d años sin verificar vigencia: " % anios + "; ".join(viejos))
                if viejos else f"Ninguna conclusión portante depende de datos de más de {anios} años sin verificar.")
    solos = []
    for c in portantes:
        sust = [exp[x] for x in ids_en(c.get("sustento")) if x in exp]
        origenes = set()
        for e in sust:
            o = norm(e.get("origen"))
            if not o:
                m = re.match(r"https?://([^/]+)", e.get("fuente", ""))
                o = m.group(1).lower() if m else norm(e.get("fuente"))
            origenes.add(o)
        if sust and len(origenes) <= 1 and not any(e.get("nivel") == "N1" for e in sust):
            solos.append(c.get("id"))
    res["5"] = ("falla" if solos else "pasa", ("Un solo origen y sin registro N1: " + ", ".join(solos)) if solos
                else "Cada conclusión portante tiene orígenes distintos o un registro N1.")
    sin_id = [f.get("id") for f in inst.filas("E3_universo.csv") if f.get("estado") == "entra" and not f.get("identificador")]
    res["6"] = ("falla", "Candidatos sin identificador duro: " + ", ".join(sin_id)) if sin_id else \
        (None, "Universo con identificadores; falta que el árbitro revise las entidades del texto.")
    sin_rev = [c.get("id") for c in portantes if norm(c.get("se_revierte_si")) in ("", "ninguno", "ninguna", "nada")]
    res["7"] = ("falla" if sin_rev else "pasa", ("Sin «se revierte si»: " + ", ".join(sin_rev)) if sin_rev
                else "Cada conclusión portante dice qué la revertiría.")
    nulos = sum(1 for f in inst.filas("bitacora.csv") if f.get("resultado") == "nulo")
    res["8"] = ("pasa" if nulos else "falla", f"{nulos} búsqueda(s) nula(s) registrada(s)." if nulos else "No hay búsquedas nulas en la bitácora.")
    return res


def muestra(inst, n=10, semilla=None):
    """Afirmaciones al azar para la prueba 1 (trazabilidad). Devuelve (semilla, [(id, cadena)])."""
    exp = inst.expediente()
    concl = {f.get("id"): f for f in inst.filas("conclusiones.csv") if f.get("estado") != "retirada"}
    citados = set()
    for nombre in ("E4_analisis.md", "E6_entregable.md"):
        citados |= set(ids_en(limpiar_md(inst.texto(nombre))))
    for c in concl.values():
        citados |= set(ids_en(c.get("sustento")))
    poblacion = sorted({x for x in citados if x in exp and exp[x].get("estado") != "retirada"} | set(concl), key=clave_id)
    if norm(inst.campo("intensidad")) == "forense":
        elegidos = poblacion
    else:
        semilla = int(semilla) if semilla is not None else int(time.time()) % 100000
        elegidos = sorted(random.Random(semilla).sample(poblacion, min(n, len(poblacion))), key=clave_id)
    salida = []
    for x in elegidos:
        if x in concl:
            c = concl[x]
            def eslabon(s):
                e = exp.get(s, {})
                origen = e.get("fuente") or (("operación: " + e.get("operacion")) if e.get("operacion") else "sin fuente")
                return f"{s} ({e.get('marca', '?')}, {e.get('nivel') or '-'}, {origen})"
            cadena = f"{c.get('conclusion')} → sustento: " + ", ".join(eslabon(s) for s in ids_en(c.get("sustento")))
        else:
            e = exp[x]
            cadena = (f"{e.get('afirmacion')} → {e.get('marca')} {e.get('nivel')}, {e.get('fuente') or 'sin fuente'}, "
                      f"dato al {e.get('dato_al') or '?'}, consultado {e.get('fecha_consulta') or '?'}"
                      + (f", operación: {e.get('operacion')}" if e.get("operacion") else ""))
        salida.append((x, cadena))
    return semilla, salida


def registrar_auditoria(inst, resultados, hoy):
    enc, filas = leer_csv(inst.carpeta / "auditoria.csv")
    enc = enc or ESQUEMAS["auditoria.csv"]
    for f in filas:
        r = resultados.get(f.get("prueba"))
        if r and r[0]:
            f.update({"resultado": r[0], "detalle": r[1], "quien": "validador", "fecha": hoy.isoformat()})
        elif r:
            f.update({"detalle": r[1]})
    escribir_csv(inst.carpeta / "auditoria.csv", enc, filas)


# ------------------------------------------------------------------------------------------------ corrección
def corregir(inst, aplicar=False, hoy=None):
    """Arregla lo mecánico. Devuelve la lista de cambios (aplicados o propuestos)."""
    hoy = (hoy or date.today()).isoformat()
    cambios = []
    nuevos = {}
    marca_txt = f"corregido por el validador {hoy}"

    def anotar(f, texto):
        f["nota"] = (f.get("nota", "") + ("; " if f.get("nota") else "") + f"{marca_txt}: {texto}").strip()

    for nombre in ESQUEMAS:
        enc, filas = inst.reg[nombre]
        if not enc:
            continue
        mod = False
        for f in filas:
            for (archivo, col), permitidos in VALORES.items():
                if archivo != nombre or not f.get(col):
                    continue
                v = f[col]
                if v not in permitidos:
                    sug = next((p for p in permitidos if norm(p) == norm(v)), "")
                    if sug:
                        cambios.append(f"{nombre} {f.get('id', f.get('puerta', ''))}: {col} «{v}» → «{sug}»")
                        f[col] = sug
                        mod = True
        if nombre == "expediente.csv":
            for f in filas:
                if f.get("marca") == "H" and f.get("nivel") == "N4":
                    cambios.append(f"expediente.csv {f.get('id')}: H con fuente N4 → T (lo dice la parte interesada)")
                    f["marca"] = "T"
                    if not f.get("sujeto"):  # en una fuente N4, quien afirma es la parte que la publica (su origen)
                        f["sujeto"] = f.get("origen") or "[PENDIENTE: quién lo afirma]"
                    anotar(f, "H→T (fuente N4)")
                    mod = True
                elif f.get("marca") in ("H", "D") and f.get("nivel") in ("N5", "N6"):
                    cambios.append(f"expediente.csv {f.get('id')}: {f.get('marca')} con fuente {f.get('nivel')} → P (pista: verificar en el registro)")
                    anotar(f, f"{f.get('marca')}→P (fuente {f.get('nivel')})")
                    f["marca"] = "P"
                    mod = True
        if nombre == "bitacora.csv":
            quedan = []
            for f in filas:
                if RE_NO_HECHA.search(" ".join([f.get("resultado", ""), f.get("nota", ""), f.get("entradas", "")])):
                    nuevos.setdefault("vacios", []).append(f)
                    cambios.append(f"bitacora.csv: «{f.get('fuente')} · {f.get('terminos')}» no se buscó → vacios.csv (no-buscado)")
                    mod = True
                else:
                    quedan.append(f)
            filas[:] = quedan
        if nombre == "puertas.csv" and norm(inst.campo("intensidad")) == "sondeo":
            for f in filas:
                if f.get("puerta") in ("P1", "P3", "P4", "P5") and f.get("estado") == "pendiente":
                    cambios.append(f"puertas.csv {f.get('puerta')}: pendiente → no-aplica (sondeo)")
                    f["estado"] = "no-aplica"
                    mod = True
        if mod and aplicar:
            escribir_csv(inst.carpeta / nombre, enc, filas)
    if nuevos.get("vacios"):
        enc_v, vac = inst.reg["vacios.csv"]
        enc_v = enc_v or ESQUEMAS["vacios.csv"]
        n = max([clave_id(f.get("id", ""))[1] for f in vac] + [0])
        for b in nuevos["vacios"]:
            n += 1
            vac.append({"id": f"V-{n:02d}", "que_falta": b.get("terminos", ""), "estado": "no-buscado", "donde_se_busco": "",
                        "terminos": b.get("terminos", ""), "como_se_cierra": f"Buscar en {b.get('fuente', '')}",
                        "responsable": b.get("rol", ""), "nota": f"{marca_txt}: venía de la bitácora ({b.get('fecha', '')})"})
        if aplicar:
            escribir_csv(inst.carpeta / "vacios.csv", enc_v, vac)
    return cambios


# ------------------------------------------------------------------------------------------------ siguiente paso
def lineas_puertas(inst):
    out = []
    for p in PUERTAS:
        f = inst.puertas().get(p, {})
        e = f.get("estado", "?")
        out.append(f"{p} {'firmada' if e == 'aprobada' else e}" + (f" ({f.get('firma')}, {f.get('fecha')})" if e == "aprobada" else ""))
    return " · ".join(out)


def siguiente(inst, inf, ajustes=None):
    """El siguiente paso en palabras simples: qué hacer, quién, qué leer y qué pedirle a la persona."""
    ajustes = ajustes or cargar_ajustes()
    etapa = inst.etapa()
    decisor = inst.campo("decisor") or "la persona que decide"
    rol_dir = ".claude/skills/investigar/references/roles/"
    leer = ["arquetipos/investigacion/protocolo/PROTOCOLO.md"]
    if inst.campo("cartucho"):
        leer.append(inst.campo("cartucho"))
    out = []
    if inf.errores:
        out.append(f"Primero corrige {len(inf.errores)} error(es) (--revisar los lista; lo mecánico se arregla con --corregir --aplicar).")
    def falta(p):
        return [x for x in inf.pendientes if x.startswith(f"[{p}]")]
    if etapa == "cerrada":
        out.append(f"Cerrada el {inst.campo('cierre')}. Revisa lo aprendido con --aprender y llévalo a la empresa.")
        return out, leer
    n = int(etapa[1])
    out.append(f"Etapa {etapa} · {NOMBRE_ETAPA[etapa]} · rol: {ROL_ETAPA[etapa]}.")
    leer.append(rol_dir + {"E0": "encuadrador.md", "E1": "cartografo.md", "E2": "refutador.md y bibliotecario.md",
                           "E3": "analista.md y bibliotecario.md", "E4": "analista.md", "E5": "refutador.md y arbitro.md",
                           "E6": "editor.md"}[etapa])
    if etapa == "E6":
        out.append("El editor arma E6_entregable.md con lo arbitrado; luego --revisar y, si está limpio, se anota «cierre» en el manifiesto.")
        return out, leer
    p = PUERTAS[n]
    pend = falta(p)
    persona = p in PERSONA
    if etapa == "E0":
        if pend:
            out.append("Completa el encuadre (E0_encuadre.md y el manifiesto). No se busca nada todavía.")
    elif etapa == "E1":
        if pend:
            out.append("Arma el mapa de fuentes (E1_mapa_fuentes.csv)" + (f", partiendo del cartucho {inst.campo('cartucho')}" if inst.campo("cartucho") else "")
                       + ": qué existe porque está inscrito (N1), quién está obligado a reportar (N2).")
    elif etapa == "E2":
        ha = inst.filas("E2_hipotesis.csv")
        abiertas = [f.get("id") for f in ha if f.get("estado") == "abierta"]
        disparo = [f.get("id") for f in ha if f.get("estado") == "disparo"]
        minimo = max(3, int((ajustes.get("reglas") or {}).get("minimo_hipotesis") or 5))
        if len(ha) < 3:
            out.append("El refutador (pase 1) escribe las hipótesis asesinas ANTES de buscar: qué tiene que ser cierto, qué la "
                       "mataría y dónde se verifica (disponibilidad, vigencia, capacidad, demanda, ventana, mandato, facultad).")
        else:
            if len(ha) < minimo:
                out.append(f"Hay {len(ha)} hipótesis y lo esperado son {minimo}: el refutador puede agregar las que falten.")
            if disparo:
                out.append(f"Disparó {', '.join(disparo)}. Pídele a {decisor} que decida: «reencuadrar» (vuelve a E0) o «cerrar».")
                return out, leer
            if abiertas:
                out.append(f"El bibliotecario corre las hipótesis abiertas ({', '.join(abiertas)}): busca lo que las mataría, anota "
                           "cada búsqueda en la bitácora (también las nulas) y cada hecho en el expediente.")
    elif etapa == "E3":
        out.append("El analista arma E3_universo.csv: cada candidato con identificador, señal observable y sustento. Si la "
                   "pregunta no tiene candidatos, P3 queda no-aplica.")
    elif etapa == "E4":
        out.append("El analista escribe E4_analisis.md citando solo ID del expediente y deja cada conclusión en conclusiones.csv "
                   "con su sustento, confianza y qué la revertiría.")
    elif etapa == "E5":
        if not [f for f in inst.filas("E5_impugnaciones.csv") if f.get("pase") == "2"]:
            ref = (ajustes.get("refutador") or {})
            quien = ref.get("asistente") or ("el subagente refutador" + (f" con el modelo {ref.get('modelo')}" if ref.get("modelo") else ""))
            out.append(f"El refutador (pase 2) impugna las conclusiones en contexto estéril ({quien}): solo ve conclusiones.csv "
                       "y el expediente, nunca el análisis.")
        else:
            out.append("El árbitro resuelve las impugnaciones, corre --auditar --registrar y --muestra --registrar, y revisa "
                       "las pruebas 2, 3 y 6.")
    if pend:
        out.append(f"Falta para {p}: " + "; ".join(x.split("] ", 1)[1] for x in pend[:6]) + (" …" if len(pend) > 6 else ""))
    if not pend and not inf.errores:
        if persona:
            resumen = {"P0": "la pregunta de decisión es la correcta", "P2": "ninguna hipótesis asesina disparó",
                       "P5": "lo que el refutador tumbó se retiró y las ocho pruebas pasan"}[p]
            out.append(f"Listo para {p}. Pídele a {decisor} la firma en dos líneas: «{resumen}. Responde \"firmo {p}\" o dime qué "
                       f"corregir.» Con su respuesta, anota en puertas.csv: aprobada, su nombre, tipo persona y la fecha.")
        else:
            out.append(f"Listo para {p}: el árbitro la revisa y la firma (puertas.csv: aprobada, «árbitro: <asistente>», tipo arbitro, fecha).")
    return out, leer


def mostrar(proyecto, insts, hoy, detalle=False):
    ajustes = cargar_ajustes()
    total_err = 0
    print(f"# Investigaciones de {Path(proyecto).name}\n")
    if not insts:
        print("No hay investigaciones. Para abrir una: python herramientas/investigacion.py "
              f"{rel(proyecto)} --nueva <nombre-corto>")
        return 0
    for inst in insts:
        inf = revisar(inst, hoy, ajustes)
        total_err += len(inf.errores)
        print(f"## {inst.id} · {inst.campo('nombre') or '(sin nombre)'}")
        print(f"- {inst.campo('codigo') or 'sin código'} · intensidad {inst.campo('intensidad') or '?'} · tolerancia "
              f"{inst.campo('tolerancia') or '?'} · protocolo {inst.campo('protocolo') or '?'} · forma {inst.campo('forma') or 'propia'}")
        print(f"- Puertas: {lineas_puertas(inst)}")
        en_curso = inf.pendientes_en_curso()
        print(f"- Validador: {len(inf.errores)} error(es) · {len(en_curso)} pendiente(s) para "
              f"{inf.puerta_en_curso or 'cerrar'} · {len(inf.avisos)} aviso(s)")
        pasos, leer = siguiente(inst, inf, ajustes)
        print("- Siguiente paso:")
        for x in pasos:
            print(f"  - {x}")
        lecciones = [l for l in leer_lecciones() if l.get("estado") != "descartada"
                     and (not l.get("cartucho") or l.get("cartucho") == inst.campo("cartucho"))]
        print("- Leer: " + ", ".join(leer) + (f" y las {len(lecciones)} lección(es) de la empresa (empresa/investigacion/lecciones.csv)"
                                               if lecciones else ""))
        prefs = ajustes.get("preferencias") or []
        if prefs:
            print("- Preferencias de la empresa: " + " · ".join(str(p.get("texto") if isinstance(p, dict) else p) for p in prefs[:6]))
        if detalle:
            for titulo, lista in (("Errores (corregir ahora)", inf.errores),
                                  (f"Pendientes para {inf.puerta_en_curso or 'cerrar'}", en_curso), ("Avisos", inf.avisos)):
                if lista:
                    print(f"\n### {titulo}")
                    for x in lista:
                        print(f"- {x}")
        print()
    return total_err


def rel(p):
    try:
        return Path(p).resolve().relative_to(RAIZ).as_posix()
    except ValueError:
        return str(p)


# ------------------------------------------------------------------------------------------------ abrir una investigación
def agregar_arquetipo(proyecto):
    """Si el proyecto no tiene el arquetipo investigacion, lo suma (y su estructura, sin sobrescribir nada)."""
    yml = Path(proyecto) / "proyecto.yaml"
    texto = yml.read_text(encoding="utf-8")
    m = re.search(r"^arquetipos:\s*\[(.*?)\]", texto, re.M)
    actuales = [x.strip() for x in m.group(1).split(",") if x.strip()] if m else []
    if "investigacion" in actuales:
        return False, actuales
    todos = actuales + ["investigacion"]
    if m:
        texto = texto[:m.start()] + f"arquetipos: [{', '.join(todos)}]" + texto[m.end():]
    else:
        texto = texto.rstrip() + "\narquetipos: [investigacion]\n"
    yml.write_text(texto, encoding="utf-8")
    for p in (ARQ / "estructura").rglob("*"):
        d = Path(proyecto) / p.relative_to(ARQ / "estructura")
        if p.is_dir():
            d.mkdir(parents=True, exist_ok=True)
        elif not d.exists():
            d.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, d)
    return True, todos


def nueva(proyecto, corto, a, hoy):
    if es_mantenedor():
        sys.exit("Esta carpeta es el núcleo que mantienes: no lleva proyectos ni investigaciones. Ábrela en una carpeta de empresa.")
    slug = re.sub(r"[^a-z0-9]+", "-", norm(corto)).strip("-")
    if not slug:
        sys.exit("Indica un nombre corto con letras o números (por ejemplo: socios-licencia).")
    ajustes = cargar_ajustes()
    pd = ajustes.get("por_defecto") or {}
    intensidad = norm(a.intensidad or pd.get("intensidad") or "sondeo")
    if intensidad not in INTENSIDADES:
        sys.exit("Intensidad: sondeo, estandar o forense (se empieza abajo y se sube).")
    tolerancia = norm(a.tolerancia or pd.get("tolerancia") or "")
    if tolerancia and tolerancia not in TOLERANCIAS:
        sys.exit("Tolerancia: conservador o exploratorio.")
    cartucho = a.cartucho or pd.get("cartucho") or ""
    if cartucho and not (RAIZ / cartucho).exists():
        sys.exit(f"No existe el cartucho {cartucho} (ver biblioteca/dominios/).")
    anio = hoy.year
    usados = [int(m.group(1)) for i in todas_las_instancias() + instancias_de(proyecto)
              for m in [re.match(rf"{anio}-(\d+)-", i.name)] if m]
    nn = max(usados + [0]) + 1
    iid = f"{anio}-{nn:02d}-{slug}"
    destino = Path(proyecto) / CARPETA / iid
    if destino.exists():
        sys.exit(f"Ya existe {rel(destino)}.")
    sumado, arqs = agregar_arquetipo(proyecto)
    shutil.copytree(PLANTILLA, destino)
    forma = a.forma or ("propia" if arqs == ["investigacion"] else "integrada")
    texto = (destino / "manifiesto.yaml").read_text(encoding="utf-8")
    for clave, valor in (("id", iid), ("codigo", f"PIA-{anio}-{nn:02d}"), ("nombre", a.nombre or corto),
                         ("protocolo", version_protocolo()), ("cartucho", cartucho), ("intensidad", intensidad),
                         ("tolerancia", tolerancia), ("restriccion_fuentes", pd.get("restriccion_fuentes") or ""),
                         ("apertura", hoy.isoformat()), ("forma", forma)):
        texto = poner_campo(texto, clave, valor)
    (destino / "manifiesto.yaml").write_text(texto, encoding="utf-8")
    if intensidad == "sondeo":
        enc, filas = leer_csv(destino / "puertas.csv")
        for f in filas:
            if f["puerta"] in ("P1", "P3", "P4", "P5"):
                f["estado"] = "no-aplica"
        escribir_csv(destino / "puertas.csv", enc, filas)
    creado_ajustes = asegurar_ajustes()
    print(f"Investigación abierta: {rel(destino)} ({'PIA-%d-%02d' % (anio, nn)})")
    if sumado:
        print(f"- El proyecto no tenía el arquetipo investigacion: se sumó (arquetipos: {', '.join(arqs)}).")
    print(f"- Protocolo {version_protocolo()} · intensidad {intensidad} · tolerancia {tolerancia or 'por decidir en E0'} · forma {forma}"
          + (f" · cartucho {cartucho}" if cartucho else ""))
    if creado_ajustes:
        print("- Ajustes de investigación de la empresa creados en empresa/investigacion/ajustes.yaml (los cambia la conversación).")
    lecc = leer_lecciones()
    if lecc:
        print(f"- Lecciones de la empresa que aplican: {len(lecc)} (empresa/investigacion/lecciones.csv)")
    print("- Siguiente paso: el encuadre (E0_encuadre.md). No se busca nada antes de que la persona que decide firme P0.")
    return destino


# ------------------------------------------------------------------------------------------------ aprender y ajustar
def aprender(proyecto, inst, llevar, quien, hoy, al_nucleo=False):
    enc, filas = leer_csv(inst.carpeta / "metodo.csv")
    propuestas = [f for f in filas if f.get("estado") == "propuesta"]
    if not llevar:
        if not propuestas:
            print("No hay lecciones de método por revisar en esta investigación.")
        for f in propuestas:
            print(f"- {f.get('id')} ({f.get('donde') or 'sin destino'}): {f.get('leccion')} → regla: {f.get('regla_propuesta') or '(por escribir)'}")
        if propuestas:
            print("\nPara llevarlas a la empresa: --llevar " + ",".join(f.get("id") for f in propuestas) + ' --quien "<nombre>"')
        return 0
    if not quien:
        sys.exit("Indica --quien: cada lección guarda quién la aprobó.")
    elegidas = [x.strip() for x in llevar.split(",") if x.strip()]
    ruta = carpeta_empresa() / "lecciones.csv"
    ruta.parent.mkdir(parents=True, exist_ok=True)
    enc_l, lecc = leer_csv(ruta)
    enc_l = enc_l or LECCIONES_COLS
    n = max([clave_id(f.get("id", ""))[1] for f in lecc] + [0])
    llevadas = []
    for f in filas:
        if f.get("id") in elegidas and f.get("estado") == "propuesta":
            n += 1
            lecc.append({"id": f"L-{n:02d}", "fecha": hoy.isoformat(), "leccion": f.get("leccion"), "regla": f.get("regla_propuesta"),
                         "donde": f.get("donde"), "cartucho": inst.campo("cartucho") if f.get("donde") == "cartucho" else "",
                         "origen": f"{Path(proyecto).name}/{inst.id} {f.get('id')}", "quien": quien,
                         "estado": "propuesta-al-nucleo" if al_nucleo else "vigente"})
            f["estado"] = "llevada-a-empresa"
            llevadas.append(f.get("id"))
    faltan = [x for x in elegidas if x not in llevadas]
    if faltan:
        print(f"No se llevaron (no existen o no están en estado propuesta): {', '.join(faltan)}")
    if llevadas:
        escribir_csv(ruta, enc_l, lecc)
        escribir_csv(inst.carpeta / "metodo.csv", enc, filas)
        print(f"Llevadas a la empresa: {', '.join(llevadas)} → empresa/investigacion/lecciones.csv. Las próximas investigaciones las leen.")
    return 0 if llevadas else 1


def ajustar(asignacion, quien, motivo, hoy):
    if "=" not in asignacion:
        sys.exit("Usa --ajustar clave=valor (por ejemplo por_defecto.intensidad=estandar).")
    clave, valor = [x.strip() for x in asignacion.split("=", 1)]
    if clave not in CLAVES_AJUSTABLES:
        sys.exit("Claves que se pueden ajustar: " + ", ".join(CLAVES_AJUSTABLES))
    if not quien:
        sys.exit("Indica --quien: cada ajuste guarda quién lo pidió.")
    regla = CLAVES_AJUSTABLES[clave]
    if regla is int:
        try:
            valor = int(valor)
        except ValueError:
            sys.exit(f"{clave} debe ser un número entero.")
        minimos = {"reglas.minimo_hipotesis": 3, "reglas.muestra_trazabilidad": 1, "reglas.antiguedad_max_anios": 1}
        if valor < minimos.get(clave, 0):
            sys.exit(f"{clave} no puede ser menor que {minimos[clave]} (el protocolo no se debilita bajo su mínimo).")
    elif isinstance(regla, list):
        valor = norm(valor)
        if valor not in regla:
            sys.exit(f"{clave}: valores posibles {', '.join(x for x in regla if x) or '(vacío)'}.")
    asegurar_ajustes()
    datos = cargar_ajustes()
    seccion, campo = clave.split(".")
    antes = (datos.get(seccion) or {}).get(campo)
    datos.setdefault(seccion, {})[campo] = valor
    datos.setdefault("historial", []).append({"fecha": hoy.isoformat(), "quien": quien, "cambio": f"{clave}: {antes!r} → {valor!r}",
                                              "motivo": motivo or ""})
    escribir_ajustes(datos)
    print(f"Ajuste guardado: {clave} = {valor!r} (antes {antes!r}), pedido por {quien}. Se aplica a las investigaciones nuevas.")


def preferencia(texto, quien, desde, hoy):
    if not quien:
        sys.exit("Indica --quien: cada preferencia guarda quién la pidió.")
    asegurar_ajustes()
    datos = cargar_ajustes()
    datos.setdefault("preferencias", []).append({"texto": texto, "quien": quien, "fecha": hoy.isoformat(), "desde": desde or ""})
    escribir_ajustes(datos)
    print(f"Preferencia guardada para las próximas investigaciones: «{texto}» ({quien}).")


def exportar_lecciones():
    lecc = [f for f in leer_lecciones() if f.get("estado") == "propuesta-al-nucleo"]
    print("# Lecciones de método propuestas para el núcleo\n")
    print("Solo método (sin hechos ni nombres de casos). Revisar antes de enviarlas a quien mantiene el núcleo.\n")
    if not lecc:
        print("(ninguna marcada como propuesta-al-nucleo)")
    for f in lecc:
        print(f"- **{f.get('leccion')}** → regla: {f.get('regla') or '(por escribir)'} · dónde: {f.get('donde') or '?'}"
              + (f" · cartucho: {f.get('cartucho')}" if f.get("cartucho") else ""))
    return 0


def subir(inst, nivel, quien, motivo, hoy):
    nivel = norm(nivel)
    actual = norm(inst.campo("intensidad"))
    if nivel not in INTENSIDADES or INTENSIDADES.index(nivel) <= INTENSIDADES.index(actual or "sondeo"):
        sys.exit(f"Solo se sube de nivel: está en {actual or 'sondeo'}; opciones: "
                 + ", ".join(INTENSIDADES[INTENSIDADES.index(actual or 'sondeo') + 1:]) + ".")
    if not quien:
        sys.exit("Indica --quien: subir de nivel lo decide la persona que decide.")
    ruta = inst.carpeta / "manifiesto.yaml"
    ruta.write_text(poner_campo(ruta.read_text(encoding="utf-8"), "intensidad", nivel), encoding="utf-8")
    enc, filas = leer_csv(inst.carpeta / "puertas.csv")
    for f in filas:
        if f.get("estado") == "no-aplica":
            f["estado"] = "pendiente"
        if f.get("puerta") == "P0":
            f["nota"] = (f.get("nota", "") + "; " if f.get("nota") else "") + f"{hoy.isoformat()} sube a {nivel} ({quien}): {motivo or 'sin motivo'}"
    escribir_csv(inst.carpeta / "puertas.csv", enc, filas)
    print(f"{inst.id}: intensidad {actual} → {nivel}. Las puertas que no aplicaban vuelven a pendiente.")


# ------------------------------------------------------------------------------------------------ resumen para estado.py
def resumen_estado(raiz=RAIZ, maximo=6):
    """Líneas breves para el estado de inicio: investigaciones abiertas, en qué etapa y quién debe actuar."""
    lineas = []
    try:
        insts = todas_las_instancias(raiz)
    except Exception:
        return lineas
    ajustes = cargar_ajustes(raiz)
    for c in insts:
        try:
            inst = Instancia(c)
            etapa = inst.etapa()
            if etapa == "cerrada":
                continue
            inf = revisar(inst, ajustes=ajustes, raiz=raiz)
            rel_c = c.relative_to(Path(raiz) / "proyectos").as_posix().replace(f"/{CARPETA}/", " · ")
            if etapa in ("E0", "E2", "E5") and not inf.pendientes_en_curso() and not inf.errores:
                p = PUERTAS[int(etapa[1])]
                que = f"espera la firma de {p} de {inst.campo('decisor') or 'la persona que decide'}"
            else:
                que = f"{NOMBRE_ETAPA.get(etapa, etapa)} en curso"
            err = f" · {len(inf.errores)} error(es) del validador" if inf.errores else ""
            lineas.append(f"{rel_c}: {etapa} · {que}{err}")
        except Exception:
            continue
    if len(lineas) > maximo:
        lineas = lineas[:maximo] + [f"… y {len(lineas) - maximo} más (python herramientas/investigacion.py <proyecto>)"]
    return lineas


# ------------------------------------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("proyecto", nargs="?", help="ruta del proyecto (proyectos/<slug>)")
    ap.add_argument("--instancia", help="carpeta de la investigación (por defecto, todas las del proyecto)")
    ap.add_argument("--nueva", metavar="NOMBRE_CORTO", help="abrir una investigación nueva")
    ap.add_argument("--nombre", default="")
    ap.add_argument("--intensidad")
    ap.add_argument("--tolerancia")
    ap.add_argument("--cartucho")
    ap.add_argument("--forma", choices=["propia", "integrada"])
    ap.add_argument("--revisar", action="store_true", help="validar y listar errores, pendientes y avisos")
    ap.add_argument("--corregir", action="store_true", help="corrección automática de lo mecánico (vista previa)")
    ap.add_argument("--aplicar", action="store_true", help="con --corregir, aplicar las correcciones")
    ap.add_argument("--auditar", action="store_true", help="pruebas mecánicas de auditoría")
    ap.add_argument("--muestra", action="store_true", help="muestra al azar para la prueba 1")
    ap.add_argument("--semilla", type=int)
    ap.add_argument("--registrar", action="store_true", help="con --auditar o --muestra, anotar en auditoria.csv")
    ap.add_argument("--subir", metavar="NIVEL", help="subir la intensidad (estandar o forense)")
    ap.add_argument("--consolidar", action="store_true", help="unir los archivos parciales de bibliotecarios en paralelo (expediente, bitácora, vacíos)")
    ap.add_argument("--aprender", action="store_true", help="lecciones de método de la investigación")
    ap.add_argument("--llevar", help="con --aprender: ID de metodo.csv a llevar a la empresa (L-01,L-02)")
    ap.add_argument("--al-nucleo", action="store_true", help="con --llevar: marcarlas además como propuesta para el núcleo")
    ap.add_argument("--ajustar", metavar="CLAVE=VALOR")
    ap.add_argument("--preferencia", metavar="TEXTO")
    ap.add_argument("--desde", default="", help="con --preferencia: investigación donde surgió")
    ap.add_argument("--exportar-lecciones", action="store_true")
    ap.add_argument("--quien", default="")
    ap.add_argument("--motivo", default="")
    ap.add_argument("--hoy", help="fecha de corte AAAA-MM-DD (por defecto, hoy)")
    a = ap.parse_args()
    hoy = datetime.strptime(a.hoy, "%Y-%m-%d").date() if a.hoy else date.today()

    if a.ajustar:
        ajustar(a.ajustar, a.quien, a.motivo, hoy)
        return 0
    if a.preferencia:
        preferencia(a.preferencia, a.quien, a.desde, hoy)
        return 0
    if a.exportar_lecciones:
        return exportar_lecciones()
    if not a.proyecto:
        ap.error("indica el proyecto (por ejemplo proyectos/<slug>).")
    proyecto = proyecto_de(a.proyecto)
    if a.nueva:
        nueva(proyecto, a.nueva, a, hoy)
        return 0
    insts = [Instancia(c) for c in instancias_de(proyecto)]
    if a.instancia:
        insts = [i for i in insts if i.id == a.instancia or i.campo("codigo") == a.instancia]
        if not insts:
            sys.exit(f"No hay una investigación «{a.instancia}» en {rel(proyecto)}/{CARPETA}/.")
    unica = insts[0] if len(insts) == 1 else None
    if a.corregir or a.auditar or a.muestra or a.subir or a.aprender or a.consolidar:
        if not unica:
            sys.exit("Indica --instancia <carpeta> (el proyecto tiene varias investigaciones o ninguna).")
    if a.consolidar:
        resumen, errores = consolidar(unica)
        if errores:
            sys.exit("No se consolidó nada:\n- " + "\n- ".join(errores))
        print(("Consolidado: " + "; ".join(resumen) + ". Los parciales quedaron en _parciales-consolidados/. Ahora --revisar.")
              if resumen else "No hay archivos parciales (expediente.parcial-*.csv, bitacora.parcial-*.csv, vacios.parcial-*.csv).")
        return 0
    if a.corregir:
        cambios = corregir(unica, aplicar=a.aplicar, hoy=hoy)
        print(f"# Corrección automática · {unica.id}\n")
        print("\n".join(f"- {c}" for c in cambios) if cambios else "Nada mecánico que corregir.")
        if cambios:
            print("\n" + ("Aplicado. Cada fila corregida lo dice en su nota." if a.aplicar else "Vista previa: nada cambió. Para aplicar: --corregir --aplicar"))
        if a.aplicar:
            inf = revisar(Instancia(unica.carpeta), hoy)
            print(f"Queda(n) {len(inf.errores)} error(es) que requieren juicio" + (": --revisar los lista." if inf.errores else "."))
        return 0
    if a.auditar:
        res = auditar(unica, hoy)
        print(f"# Pruebas mecánicas de auditoría · {unica.id}\n")
        for k in sorted(res):
            r, d = res[k]
            print(f"- Prueba {k}: {r or 'falta el juicio del árbitro'} — {d}")
        print("- Pruebas 1 (muestra al azar con --muestra), 2 y 3: las corre el árbitro.")
        if a.registrar:
            registrar_auditoria(unica, res, hoy)
            print("\nAnotado en auditoria.csv.")
        return 0
    if a.muestra:
        n = int((cargar_ajustes().get("reglas") or {}).get("muestra_trazabilidad") or 10)
        semilla, items = muestra(unica, n, a.semilla)
        print(f"# Prueba 1 · trazabilidad · {unica.id}\n")
        print("Forense: todas las afirmaciones portantes." if semilla is None else f"Semilla {semilla} (repite la misma muestra con --semilla {semilla}).")
        for x, cadena in items:
            print(f"- {x}: {cadena}")
        print("\nEl árbitro reconstruye cada cadena hasta la fuente. Falla si más de una no llega: vuelve el entregable completo.")
        if a.registrar:
            registrar_auditoria(unica, {"1": (None, f"Muestra con semilla {semilla}: " + ", ".join(x for x, _ in items))}, hoy)
            print("Anotado en auditoria.csv (el resultado lo pone el árbitro).")
        return 0
    if a.subir:
        subir(unica, a.subir, a.quien, a.motivo, hoy)
        return 0
    if a.aprender:
        return aprender(proyecto, unica, a.llevar, a.quien, hoy, a.al_nucleo)
    errores = mostrar(proyecto, insts, hoy, detalle=a.revisar)
    if a.revisar:
        print(f"Resultado: {errores} error(es)." + (" Corrige y vuelve a revisar." if errores else " OK."))
        return 1 if errores else 0
    return 0


if __name__ == "__main__":
    import _consola
    _consola.preparar()
    sys.exit(main())
