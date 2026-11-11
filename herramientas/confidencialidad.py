#!/usr/bin/env python3
"""Confidencialidad de esta carpeta: qué no sale nunca del computador, con qué controles, y una auditoría de Git.

Uso:
    python herramientas/confidencialidad.py              # qué se protege, lo propio de la empresa y si los controles están activos
    python herramientas/confidencialidad.py --auditar    # ¿hay algo confidencial versionado o en el historial? (código 1 si lo hay)
    python herramientas/confidencialidad.py --agregar "<carpeta/ o patrón>" --quien "<nombre>"   # desde hoy, eso no se sube

Tres niveles (detalle en reglas/confidencialidad.md):
  1. Se versiona: los datos y registros del proyecto (.yaml, .csv, .md) y las salidas que se generan.
  2. Réplica fiel: de bases, contratos y actas queda su texto en fuentes/ (repositorio privado); el original queda local.
  3. Solo ficha: CVs, datos personales, estados financieros y todo lo que la empresa defina en `nunca_subir`; el archivo
     y su texto no salen de este computador, y en Git queda, a lo más, una ficha resumen.
Lo propio de la empresa vive en `empresa/confidencialidad.yaml` (el núcleo nunca lo toca) y lo leen todos los controles:
el hook del asistente, el control de Git antes de cada commit y el control antes de subir. `--agregar` lo anota ahí y
en la sección propia de `.gitignore`, que se conserva al actualizar.
"""
import argparse
import re
import sys
from datetime import date
from pathlib import Path

import _nucleo

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "herramientas" / "hooks"))
import _comun  # noqa: E402

POLITICA = Path("empresa") / "confidencialidad.yaml"
TEXTOS = {".md", ".csv", ".yaml", ".yml", ".txt", ".json"}


def git(*args):
    return _comun.git_salida(list(args), RAIZ, timeout=120)


def agregar_a_lista(texto, clave, valor, nota=""):
    """El YAML con `valor` sumado a la lista `clave`, conservando comentarios y el resto del archivo."""
    item = f'  - "{valor}"' + (f"   # {nota}" if nota else "")
    lineas = texto.splitlines()
    for i, linea in enumerate(lineas):
        m = re.match(rf"^{re.escape(clave)}:\s*(.*?)\s*(#.*)?$", linea)
        if not m:
            continue
        if m.group(1).startswith("["):
            previos = [x.strip().strip("\"'") for x in m.group(1).strip("[]").split(",") if x.strip()]
            lineas[i:i + 1] = [f"{clave}:" + (f"   {m.group(2)}" if m.group(2) else "")] + [f'  - "{x}"' for x in previos] + [item]
        else:
            j = i + 1
            while j < len(lineas) and re.match(r"^\s+-\s", lineas[j]):
                j += 1
            lineas.insert(j, item)
        return "\n".join(lineas) + "\n"
    return texto.rstrip("\n") + f"\n{clave}:\n{item}\n"


def agregar(patron, quien, hoy=None):
    patron = patron.strip().replace("\\", "/").lstrip("/")
    if not patron or patron in ("*", "**", "/"):
        raise ValueError("indica una carpeta (terminada en /) o un patrón como los de .gitignore, por ejemplo `privado-cliente/` o `*.kdbx`")
    if not (RAIZ / "empresa").is_dir():
        raise ValueError("esta carpeta no tiene empresa/: la confidencialidad propia se define en la carpeta de una empresa")
    pol = _comun.politica(RAIZ)
    if pol.get("error"):
        raise ValueError(pol["error"])
    hechos = []
    if patron not in pol["nunca_subir"]:
        ruta = RAIZ / POLITICA
        plantilla = RAIZ / "plantilla-empresa" / "confidencialidad.yaml"
        texto = ruta.read_text(encoding="utf-8") if ruta.exists() else (plantilla.read_text(encoding="utf-8") if plantilla.exists() else "")
        ruta.write_text(agregar_a_lista(texto, "nunca_subir", patron, f"{quien}, {(hoy or date.today()).isoformat()}"), encoding="utf-8")
        hechos.append(f"{POLITICA.as_posix()} (nunca_subir)")
    ignorar = RAIZ / ".gitignore"
    actual = ignorar.read_text(encoding="utf-8") if ignorar.exists() else ""
    if patron not in [l.strip() for l in actual.splitlines()]:
        if _nucleo.MARCA_PROPIO not in actual:
            actual = actual.rstrip("\n") + "\n\n" + _nucleo.MARCA_PROPIO + "\n"
        ignorar.write_bytes((actual.rstrip("\n") + "\n" + patron + "\n").encode("utf-8"))
        hechos.append(".gitignore (sección propia)")
    _comun._politicas.clear()
    _, salida = git("ls-files", "-z")
    ya = [r for r in salida.split("\0") if r and _comun.coincide(patron, r)]
    return hechos, ya


def auditar():
    """(versionados, del historial, claves, sueltos): lo confidencial que Git ya tiene, y los binarios fuera de lugar."""
    _, salida = git("ls-files", "-z")
    hoy = [r for r in salida.split("\0") if r]
    versionados = [(r, m) for r in hoy for m in [_comun.motivo_sensible(r, RAIZ)] if m]
    _, historia = git("log", "--all", "--name-only", "--diff-filter=A", "--format=")
    pasados = sorted(set(x.strip() for x in historia.splitlines() if x.strip()) - set(hoy))
    del_historial = [(r, m) for r in pasados for m in [_comun.motivo_sensible(r, RAIZ)] if m]
    claves = []
    for r in hoy:
        p = RAIZ / r
        if r.startswith(("proyectos/", "empresa/")) and p.suffix.lower() in TEXTOS and p.is_file() and p.stat().st_size < 2_000_000:
            tipo = _comun.clave_en_texto(p.read_text(encoding="utf-8", errors="replace"))
            if tipo:
                claves.append((r, tipo))
    sueltos = [r for r in hoy if r.startswith(("proyectos/", "empresa/")) and _comun.binario_suelto(r, RAIZ)]
    return versionados, del_historial, claves, sueltos


def resumen():
    pol = _comun.politica(RAIZ)
    out = ["# Confidencialidad de esta carpeta", ""]
    if pol.get("error"):
        out += [f"- ATENCIÓN: {pol['error']}", ""]
    out += ["- Nivel 1, se versiona: datos y registros del proyecto, y las salidas que se generan.",
            "- Nivel 2, réplica fiel: el texto de bases, contratos y actas en fuentes/ (repositorio privado); el original queda local.",
            "- Nivel 3, solo ficha: no sale de este computador:"]
    out += [f"  - {motivo}" for _, motivo in _comun.SENSIBLES]
    propios = pol["nunca_subir"]
    out += [f"  - definido por la empresa: {x}" for x in propios] or ["  - (la empresa no ha definido nada propio: `--agregar`)"]
    out += ["", f"- Word, Excel, PDF e imágenes fuera de carpetas de salida: {pol['binarios_sueltos']}"
            + (f" (carpetas propias: {', '.join(pol['carpetas_de_binarios'])})" if pol["carpetas_de_binarios"] else ""),
            f"- Una clave o llave pegada en un texto: {pol['claves_en_texto']}"]
    raiz = _comun.raiz_git(RAIZ)
    out += ["", "## Controles"]
    if raiz is None:
        out += ["- Esta carpeta todavía no es un repositorio de Git: nada puede subirse."]
    else:
        activo = _comun.control_git_activo(RAIZ)
        out += ["- Control de Git antes de cada commit y antes de subir: " + ("ACTIVO" if activo else
                "INACTIVO en este computador → git config core.hooksPath .githooks"),
                "- En Claude Code, además, un hook revisa cada comando de Git y saca del staging lo confidencial."]
        ignorar = (RAIZ / ".gitignore").read_text(encoding="utf-8", errors="replace") if (RAIZ / ".gitignore").exists() else ""
        faltan = [x for x in propios if x not in [l.strip() for l in ignorar.splitlines()]]
        if faltan:
            out += ["- En .gitignore faltan patrones propios (los controles los detienen igual): " + ", ".join(faltan)]
        _, locales = git("ls-files", "--others", "--ignored", "--exclude-standard", "-z")
        protegidos = [r for r in locales.split("\0") if r and _comun.motivo_sensible(r, RAIZ)]
        out += [f"- Archivos confidenciales que hoy están solo en este computador: {len(protegidos)}"
                + (" (no tienen copia en GitHub: si importan, respáldalos tú en un lugar seguro)" if protegidos else "")]
    out += ["", "Auditoría de lo ya versionado: python herramientas/confidencialidad.py --auditar"]
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--auditar", action="store_true")
    ap.add_argument("--agregar", metavar="PATRON")
    ap.add_argument("--quien", default="")
    ap.add_argument("--hoy", help="fecha AAAA-MM-DD (pruebas)")
    a = ap.parse_args()

    if a.agregar:
        if not a.quien.strip():
            sys.exit("--agregar necesita --quien \"<nombre>\": queda anotado quién lo definió.")
        try:
            hechos, ya = agregar(a.agregar, a.quien.strip(), date.fromisoformat(a.hoy) if a.hoy else None)
        except ValueError as e:
            sys.exit(str(e))
        print((f"«{a.agregar}» queda como confidencial: " + " y ".join(hechos)) if hechos else f"«{a.agregar}» ya estaba definido.")
        if ya:
            print(f"Ojo: {len(ya)} archivo(s) que calzan ya están versionados (el historial los conserva):\n"
                  + "\n".join(f"- {r}" for r in ya[:15]) + (f"\n- … y {len(ya) - 15} más" if len(ya) > 15 else "")
                  + "\nPara dejar de versionarlos sin borrarlos de tu carpeta: git rm -r --cached -- \"" + a.agregar.rstrip("/") + "\"")
        return 0

    if a.auditar:
        if _comun.raiz_git(RAIZ) is None:
            print("Esta carpeta no es un repositorio de Git: no hay nada versionado que auditar.")
            return 0
        versionados, del_historial, claves, sueltos = auditar()
        out = ["# Auditoría de confidencialidad", ""]
        out += [f"- Confidenciales versionados hoy: {len(versionados)}"] + [f"  - {r} ({m})" for r, m in versionados[:30]]
        out += [f"- Confidenciales que estuvieron versionados (siguen en el historial): {len(del_historial)}"] \
            + [f"  - {r} ({m})" for r, m in del_historial[:30]]
        out += [f"- Textos con una clave o llave pegada: {len(claves)}"] + [f"  - {r} ({t})" for r, t in claves[:30]]
        out += [f"- Word, Excel, PDF o imágenes fuera de carpetas de salida (revisa si son material del cliente): {len(sueltos)}"] \
            + [f"  - {r}" for r in sueltos[:30]]
        if versionados:
            out += ["", "Para dejar de versionar uno sin borrarlo de tu carpeta: git rm --cached -- <archivo> (y un commit)."]
        if versionados or del_historial or claves:
            out += ["", "Lo que ya se subió a GitHub debe darse por visto por quien tenga acceso al repositorio: cambia las claves "
                    "expuestas y, si hay que borrar algo del historial, hazlo con ayuda (reescribe el repositorio)."]
        else:
            out += ["", "Sin confidenciales en Git."]
        print("\n".join(out))
        return 1 if versionados or del_historial or claves else 0

    print(resumen())
    return 0


if __name__ == "__main__":
    import _consola
    _consola.preparar()
    sys.exit(main())
