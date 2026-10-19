"""Carga de proyecto.yaml con herencia de empresa y de programa (empresa → programa → subproyecto).

Empresa: un proyecto bajo `proyectos/` hereda de `empresa/empresa.yaml` (carpeta hermana de `proyectos/`) lo que no
define: responsable, formato y logo, autoría, política de réplicas y el bloque `empresa`. En esta capa, un valor
"PENDIENTE" del proyecto cuenta como no definido. El logo de la empresa se resuelve como ruta absoluta.

Un subproyecto vive en `proyectos/<programa>/subproyectos/<id>/` y su proyecto.yaml declara `programa: ../..`.
cargar(raiz) devuelve la configuración del subproyecto completada con la del programa: lo que el subproyecto no
define (cliente, formato, logo, autoría, umbrales, reportes) lo toma del programa; lo que define, prevalece.
No se heredan: arquetipos, induccion ni los bloques propios del programa (programa, recursos).
El logo heredado se resuelve como ruta absoluta del programa, para que los documentos del subproyecto lo usen.
"""
from pathlib import Path

import yaml

NO_HEREDAR = {"arquetipos", "induccion", "programa_info", "cronograma_actualizado"}


def _leer(raiz):
    archivo = Path(raiz) / "proyecto.yaml"
    if not archivo.exists():
        return {}
    return yaml.safe_load(archivo.read_text(encoding="utf-8")) or {}


HEREDA_DE_EMPRESA = ("empresa", "responsable", "formato", "autoria", "replicas")
VACIOS = (None, "", [], {})


def _fusionar(base, propio, vacios=VACIOS):
    """Copia de `base` actualizada con `propio` (recursivo en diccionarios; el valor propio vacío no pisa)."""
    salida = dict(base)
    for k, v in (propio or {}).items():
        if isinstance(v, dict) and isinstance(salida.get(k), dict):
            salida[k] = _fusionar(salida[k], v, vacios)
        elif v not in vacios or k not in salida:
            salida[k] = v
    return salida


def raiz_empresa(raiz):
    """Carpeta `empresa/` de la empresa dueña de un proyecto bajo `proyectos/`, o None si no hay empresa configurada."""
    raiz = Path(raiz).resolve()
    for p in [raiz] + list(raiz.parents):
        if p.name == "proyectos":
            emp = p.parent / "empresa"
            return emp if (emp / "empresa.yaml").exists() else None
    return None


def cargar_empresa(emp):
    archivo = Path(emp) / "empresa.yaml"
    return (yaml.safe_load(archivo.read_text(encoding="utf-8")) or {}) if archivo.exists() else {}


def _con_empresa(raiz, propio):
    emp = raiz_empresa(raiz)
    if emp is None:
        return propio
    datos = cargar_empresa(emp)
    base = {k: datos[k] for k in HEREDA_DE_EMPRESA if isinstance(datos.get(k), dict)}
    nombre = str((base.get("empresa") or {}).get("nombre") or "")
    if nombre and nombre != "PENDIENTE" and not (base.get("autoria") or {}).get("organizacion"):
        base.setdefault("autoria", {})["organizacion"] = nombre
    cfg = _fusionar(base, propio, VACIOS + ("PENDIENTE",))
    logo = (cfg.get("formato") or {}).get("logo")
    logo_emp = (datos.get("formato") or {}).get("logo")
    if logo_emp and (not logo or not (Path(raiz) / str(logo)).exists()) and (emp / str(logo_emp)).exists():
        cfg.setdefault("formato", {})["logo"] = str((emp / str(logo_emp)).resolve())
    cfg["_empresa"] = {"raiz": str(emp), "nombre": nombre}
    return cfg


def raiz_programa(raiz):
    """Carpeta del programa al que pertenece `raiz`, o None si es un proyecto independiente o un programa."""
    ref = _leer(raiz).get("programa")
    if not ref or not isinstance(ref, str):
        return None
    padre = (Path(raiz) / ref).resolve()
    return padre if (padre / "proyecto.yaml").exists() else None


def cargar(raiz):
    raiz = Path(raiz)
    propio = _leer(raiz)
    padre = raiz_programa(raiz)
    if padre is None:
        return _con_empresa(raiz, propio)
    cfg_padre = cargar(padre)
    heredable = {k: v for k, v in cfg_padre.items() if k not in NO_HEREDAR}
    cfg = _fusionar(heredable, propio)
    for k in NO_HEREDAR:
        if k in propio:
            cfg[k] = propio[k]
        else:
            cfg.pop(k, None)
    logo_propio = ((propio.get("formato") or {}).get("logo"))
    logo_padre = ((cfg_padre.get("formato") or {}).get("logo"))
    if not logo_propio and logo_padre and not Path(str(logo_padre)).is_absolute():
        cfg.setdefault("formato", {})["logo"] = str((padre / logo_padre).resolve())
    elif logo_propio and not (raiz / str(logo_propio)).exists() and logo_padre:
        ruta_padre = padre / str(logo_padre)
        if ruta_padre.exists():
            cfg["formato"]["logo"] = str(ruta_padre.resolve())
    cfg["_programa"] = {"raiz": str(padre), "nombre": ((cfg_padre.get("proyecto") or {}).get("nombre", padre.name))}
    return cfg
