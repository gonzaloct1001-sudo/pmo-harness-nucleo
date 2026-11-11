#!/usr/bin/env python3
"""Análisis a fondo: pronósticos, regresión, segmentación de clientes y plazo del proyecto bajo incertidumbre.

Uso:
    python herramientas/experto.py estado                 # qué bibliotecas del nivel especialista están instaladas
    python herramientas/experto.py instalar               # las instala en este mismo Python (solo con el sí del usuario)
    python herramientas/experto.py pronosticar --help     # una serie mensual hacia adelante, con su error comprobado
    python herramientas/experto.py regresion --help       # qué variables explican un resultado, y cuánto
    python herramientas/experto.py segmentar --help       # grupos de clientes según sus compras
    python herramientas/experto.py plazo --help           # probabilidad de terminar en fecha y tareas que más la mueven

Dos niveles en cada análisis (`--nivel auto | base | especialista`):
- **base**: solo la biblioteca estándar; siempre disponible. Responde con un método simple y dice su error.
- **especialista**: usa numpy, pandas, scipy, statsmodels y scikit-learn (`requirements-analisis.txt`, unos 450 MB, se
  instalan una vez). Métodos más robustos, comparados siempre contra el simple.
Con `auto` (por defecto) usa el especialista si está instalado y, si no, el base. Antes de analizar, `--diagnosticar`
mira los datos y dice si el nivel base alcanza o si conviene el especialista y por qué: cuando conviene y no está
instalado, **la decisión es del usuario** (seguir con el base o instalar). Si se pide `--nivel especialista` sin
tenerlo, termina con código 3 y explica cómo instalarlo.
Cada análisis deja `informe.html`, `informe.md` y `resultado.json` en `<proyecto>/analisis/<nombre>/`.
"""
import importlib
import importlib.util
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
REQUISITOS = "requirements-analisis.txt"
BIBLIOTECAS = {"numpy": "numpy", "pandas": "pandas", "scipy": "scipy", "statsmodels": "statsmodels", "scikit-learn": "sklearn"}
SUBCOMANDOS = {"pronosticar": "_pronostico", "regresion": "_regresion", "segmentar": "_segmentos", "plazo": "_plazo"}
SIN_ESPECIALISTA = 3  # código de salida: se pidió el nivel especialista y no está instalado


def disponibles():
    """{biblioteca: versión, o None si falta} sin cargar las bibliotecas."""
    from importlib import metadata
    estado = {}
    for nombre, modulo in BIBLIOTECAS.items():
        try:
            estado[nombre] = metadata.version(nombre) if importlib.util.find_spec(modulo) else None
        except Exception:
            estado[nombre] = None
    return estado


def listo():
    """True si el nivel especialista está completo en este Python."""
    return all(disponibles().values())


def como_instalar():
    return ("El nivel especialista no está instalado en este computador. Se instala una vez, con el sí del usuario: "
            "python herramientas/experto.py instalar (unos 450 MB; necesita internet).")


def resolver_nivel(pedido="auto"):
    """El nivel con que se va a trabajar: `base` o `especialista`. Si se pide el especialista y no está, termina con
    código 3 diciendo cómo instalarlo."""
    pedido = (pedido or "auto").strip().lower()
    if pedido == "base":
        return "base"
    if listo():
        return "especialista"
    if pedido == "especialista":
        print(como_instalar(), file=sys.stderr)
        sys.exit(SIN_ESPECIALISTA)
    return "base"


def recomendacion(especialista, motivos):
    """Forma única de decir si el nivel base alcanza: {"especialista": bool, "motivos": [...], "instalado": bool}."""
    return {"especialista": bool(especialista), "motivos": [str(m) for m in motivos], "instalado": listo()}


def texto_recomendacion(rec, nivel_usado=None):
    """Líneas para mostrar la recomendación. `nivel_usado` es None en un diagnóstico (todavía no se analiza)."""
    motivos = "; ".join(rec["motivos"]) or "sin observaciones"
    if not rec["especialista"]:
        return [f"- Nivel recomendado: base. Alcanza para esta pregunta: {motivos}."]
    if nivel_usado == "especialista":
        return [f"- Nivel usado: especialista ({motivos})."]
    lineas = [f"- Nivel recomendado: especialista, porque {motivos}."]
    if rec["instalado"]:
        lineas.append("- Está instalado: repite sin `--nivel base` para usarlo.")
    else:
        hecho = "Este resultado es del nivel base. " if nivel_usado == "base" else ""
        lineas.append(f"- {hecho}No está instalado. Pregunta al usuario qué prefiere: seguir con el nivel base (y sus límites) o "
                      "instalar el especialista (`python herramientas/experto.py instalar`, unos 450 MB, una sola vez).")
    return lineas


def nota_de_nivel(rec, nivel_usado):
    """Una línea para la página del análisis (la lee una persona): con qué nivel se hizo y si convenía el otro."""
    motivos = "; ".join(rec["motivos"]) or "sin observaciones"
    if nivel_usado == "especialista":
        return f"Nivel del análisis: especialista ({motivos})."
    if not rec["especialista"]:
        return f"Nivel del análisis: base. Alcanza para esta pregunta: {motivos}."
    return (f"Nivel del análisis: base. Para esta pregunta conviene el nivel especialista, porque {motivos}. Se instala una vez, "
            "a pedido, y el análisis se puede repetir con él.")


def estado():
    d = disponibles()
    print("# Nivel especialista del análisis\n")
    for nombre, version in d.items():
        print(f"- {nombre}: {version or 'no instalado'}")
    print("\n" + ("Completo: los análisis usan el nivel especialista." if all(d.values()) else
                  "Incompleto: los análisis usan el nivel base. " + como_instalar()))
    return 0


def instalar():
    """Instala las bibliotecas del nivel especialista en este mismo Python, sin hacer preguntas."""
    requisitos = RAIZ / REQUISITOS
    if not requisitos.exists():
        print(f"Falta {REQUISITOS} en la carpeta del harness.", file=sys.stderr)
        return 1
    if listo():
        print("El nivel especialista ya está instalado.")
        return estado()
    print("Instalando las bibliotecas del nivel especialista (puede tardar varios minutos)...")
    try:
        r = subprocess.run([sys.executable, "-m", "pip", "install", "--no-input", "--disable-pip-version-check", "--timeout", "60",
                            "--retries", "2", "-q", "-r", str(requisitos)], stdin=subprocess.DEVNULL, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=3600)
    except subprocess.TimeoutExpired:
        print("La instalación no terminó en una hora: revisa la conexión y vuelve a intentar.", file=sys.stderr)
        return 1
    importlib.invalidate_caches()
    if r.returncode != 0 or not listo():
        print("No se pudo completar la instalación. Los análisis siguen funcionando en el nivel base.\n"
              + ((r.stderr or r.stdout or "").strip()[-600:]), file=sys.stderr)
        return 1
    print("Instalado.")
    return estado()


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "ayuda"):
        print(__doc__)
        return 0
    orden = sys.argv[1].strip().lower()
    if orden == "estado":
        return estado()
    if orden == "instalar":
        return instalar()
    if orden not in SUBCOMANDOS:
        print(f"No conozco «{orden}». Opciones: estado, instalar, " + ", ".join(SUBCOMANDOS) + ".", file=sys.stderr)
        return 1
    try:
        modulo = importlib.import_module(SUBCOMANDOS[orden])
    except ModuleNotFoundError as e:
        if e.name != SUBCOMANDOS[orden]:
            raise
        print(f"El análisis «{orden}» no está en esta versión del harness: actualiza el núcleo.", file=sys.stderr)
        return 1
    return modulo.main(sys.argv[2:])


if __name__ == "__main__":
    import _consola
    _consola.preparar()
    sys.exit(main())
