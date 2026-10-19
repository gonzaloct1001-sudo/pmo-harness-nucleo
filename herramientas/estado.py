#!/usr/bin/env python3
"""Estado del harness al iniciar una sesión, para cualquier asistente de IA.

Uso:
    python herramientas/estado.py [--remoto]

Resume: instalación, empresa, asistentes configurados, controles de Git, proyectos, traspasos pendientes, material
sin procesar, altas en curso y cambios sin guardar. Con --remoto consulta además GitHub (git fetch con tiempo
límite) para avisar si hay commits que no están en este computador.
Solo lee: no modifica nada. No necesita librerías externas (sirve antes de instalarlas).
En Claude Code lo entrega el hook de inicio (herramientas/hooks/inicio_sesion.py); los demás asistentes lo
ejecutan como paso 0 (ver AGENTS.md).
"""
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
TERMINADA = re.compile(r"^\s*[-*]?\s*estado:\s*terminada\b", re.I | re.M)


def git(*args, timeout=10):
    try:
        r = subprocess.run(["git", *args], cwd=RAIZ, capture_output=True, timeout=timeout)
        return r.returncode, r.stdout.decode("utf-8", errors="replace").strip()
    except (OSError, subprocess.TimeoutExpired):
        return None, ""


def alta_en_curso(avance: Path) -> bool:
    """El alta está en curso si existe su punto de control y no declara `estado: terminada`."""
    if not avance.exists():
        return False
    return not TERMINADA.search(avance.read_text(encoding="utf-8", errors="replace"))


def ficha_completa(ruta: Path) -> bool:
    """True si la ficha tiene al menos una respuesta escrita después de los dos puntos de una pregunta."""
    if not ruta.exists():
        return False
    return any(re.match(r"^\s*-\s+[^:]+:\s*\S", l) for l in ruta.read_text(encoding="utf-8", errors="replace").splitlines())


def campo(texto, nombre):
    """Valor de una línea `nombre: valor` (sin comentario final), o cadena vacía."""
    m = re.search(rf"^\s*{nombre}:[ \t]*(.*)$", texto, re.M)
    return re.sub(r"\s+#.*$", "", m.group(1)).strip().strip("\"'") if m else ""


def asistentes_registrados():
    ruta = RAIZ / ".harness" / "asistentes.yaml"
    if not ruta.exists():
        return []
    return re.findall(r"^\s*-?\s*id:\s*([\w.-]+)", ruta.read_text(encoding="utf-8", errors="replace"), re.M)


def traspaso(carpeta: Path):
    """Resumen del traspaso de un proyecto si hay algo pendiente, o None."""
    ruta = carpeta / "seguimiento" / "traspaso.md"
    if not ruta.exists():
        return None
    texto = ruta.read_text(encoding="utf-8", errors="replace")
    estado, proximo = campo(texto, "estado").lower(), campo(texto, "proximo_paso")
    tarea = campo(texto, "tarea_en_curso")
    if estado != "en_curso" and not proximo:
        return None
    quien = ", ".join(x for x in (campo(texto, "fecha"), campo(texto, "asistente")) if x)
    partes = [f"tarea en curso «{tarea}»" if estado == "en_curso" and tarea else ""]
    partes.append(f"próximo paso «{proximo}»" if proximo else "")
    return f"traspaso{f' ({quien})' if quien else ''}: " + "; ".join(p for p in partes if p)


def cambios_sin_guardar():
    """Cantidad de archivos modificados sin commit, por carpeta de primer y segundo nivel (p. ej. proyectos/x)."""
    rc, salida = git("status", "--porcelain", "-z", "--untracked-files=all")
    if rc != 0:
        return None
    conteo, entradas = {}, iter(salida.split("\0"))
    for linea in entradas:
        if len(linea) < 4:
            continue
        if linea[0] in "RC":  # renombrado o copiado: la entrada siguiente es la ruta de origen
            next(entradas, None)
        partes = linea[3:].replace("\\", "/").split("/")
        clave = "/".join(partes[:2]) if partes[0] == "proyectos" and len(partes) > 2 else partes[0]
        conteo[clave] = conteo.get(clave, 0) + 1
    return conteo


def repositorio_propio():
    rc, top = git("rev-parse", "--show-toplevel")
    return rc == 0 and top and Path(top).resolve() == RAIZ.resolve()


def resumen(remoto=False):
    lineas = ["[Estado del PMO Harness]"]
    if (RAIZ / ".venv" / "bin" / "python").exists():
        lineas.append("- Python de esta carpeta: `.venv/bin/python` (úsalo en vez de `python` para ejecutar los scripts).")
    estado_yaml = RAIZ / ".harness" / "estado.yaml"
    instalado = estado_yaml.exists()
    import _nucleo
    oficial = _nucleo.origen_oficial(RAIZ)
    _, origin = git("remote", "get-url", "origin")
    mantenedor = _nucleo.es_mantenedor(RAIZ)
    if mantenedor:
        lineas.append(f"- Carpeta del NÚCLEO que mantiene el usuario ({oficial or 'repositorio del núcleo'}): aquí no van empresas ni "
                      "proyectos (no ofrezcas instalar). Para sus proyectos, ofrece una carpeta de empresa (`nueva_empresa.py "
                      "--destino`). Los cambios al núcleo se guardan con commit y push, y deben pasar `python pruebas/ejecutar_pruebas.py`.")
    elif not instalado and _nucleo.misma_url(origin, oficial):
        lineas.append(f"- Copia clonada del núcleo público ({oficial}): al instalar se desconecta de él y se crea un repositorio "
                      "PRIVADO propio del usuario; el núcleo no se modifica (nadie más que su dueño puede cambiarlo).")
    elif instalado and _nucleo.misma_url(origin, oficial):
        lineas.append("- ATENCIÓN: el repositorio remoto de esta carpeta es el núcleo PÚBLICO. Los datos de la empresa no deben ir ahí: "
                      "sigue el paso 2 de `instalar` para crear el repositorio privado de la empresa antes de guardar.")
    if mantenedor:
        pass
    elif not instalado:
        lineas.append("- NO INSTALADO en esta carpeta: ofrece al usuario ejecutar la skill `instalar`.")
        if ficha_completa(RAIZ / "FICHA-DE-INICIO.md"):
            lineas.append("- FICHA-DE-INICIO.md tiene respuestas: úsalas en la instalación y pregunta solo lo que falte.")
        else:
            lineas.append("- Menciona que puede completar FICHA-DE-INICIO.md antes (opcional) y que el manual está en MANUAL-DE-USUARIO.md.")
    else:
        texto = estado_yaml.read_text(encoding="utf-8", errors="replace")
        version = campo(texto, "version_harness")
        empresa_yaml = RAIZ / "empresa" / "empresa.yaml"
        empresa = campo(empresa_yaml.read_text(encoding="utf-8", errors="replace"), "nombre") if empresa_yaml.exists() else ""
        empresa = empresa or campo(texto, "empresa")
        if empresa or version:
            lineas.append(f"- Empresa: {empresa or '(sin definir)'}" + (f" · núcleo {version}" if version else ""))
        registrados = asistentes_registrados()
        lineas.append(f"- Asistentes configurados: {', '.join(registrados)}" if registrados else
                      "- Ningún asistente registrado en .harness/asistentes.yaml: identifícate y sigue la skill `configurar-asistente`.")

    if repositorio_propio():
        _, ruta_hooks = git("config", "--get", "core.hooksPath")
        if ruta_hooks.replace("\\", "/").rstrip("/") != ".githooks" and (RAIZ / ".githooks").exists():
            lineas.append("- Controles de Git INACTIVOS en este computador: ofrece activarlos con `git config core.hooksPath .githooks`.")
        if remoto:
            rc_r, _ = git("remote", "get-url", "origin")
            if rc_r == 0:
                git("fetch", "--quiet", "origin", timeout=8)
                rc_b, atras = git("rev-list", "--count", "HEAD..@{u}")
                if rc_b == 0 and atras.isdigit() and int(atras) > 0:
                    lineas.append(f"- Hay {atras} commit(s) en GitHub que no están en este computador: ofrece `git pull` antes de trabajar.")

    agents = RAIZ / "AGENTS.md"
    if agents.exists() and (RAIZ / ".claude" / "skills").exists():
        tabla = agents.read_text(encoding="utf-8", errors="replace")
        propias = sorted(d.name for d in (RAIZ / ".claude" / "skills").iterdir()
                         if d.is_dir() and (d / "SKILL.md").exists() and f".claude/skills/{d.name}/SKILL.md" not in tabla)
        if propias:
            lineas.append(f"- Skills propias de esta carpeta (no están en la tabla de AGENTS.md): {', '.join(propias)}; "
                          "lee su SKILL.md cuando su descripción calce con el pedido.")

    proyectos = sorted(p for p in (RAIZ / "proyectos").glob("*") if p.is_dir()) if (RAIZ / "proyectos").exists() else []

    def etiqueta(p):
        lista = p / "programa" / "subproyectos.csv"
        if lista.exists():
            n = max(sum(1 for x in lista.read_text(encoding="utf-8", errors="replace").splitlines() if x.strip()) - 1, 0)
            return f"{p.name} (programa con {n} subproyecto(s) en {p.name}/subproyectos/)"
        return p.name

    lineas.append(f"- Proyectos: {', '.join(etiqueta(p) for p in proyectos) if proyectos else 'ninguno'}")
    if instalado and not proyectos and not mantenedor:
        lineas.append("- Instalado pero SIN PROYECTOS: sea cual sea el primer mensaje, ofrece en una línea crear uno "
                      "(«describe tu proyecto con tus palabras», skill nuevo-proyecto) o cargar documentos existentes "
                      "(skill alta-proyecto), y pregunta si el proyecto parte de cero o ya está en marcha.")
    cambios = cambios_sin_guardar() if instalado else None
    for p in proyectos:
        carpetas = [p] + sorted(x for x in (p / "subproyectos").glob("*") if x.is_dir())
        for c in carpetas:
            t = traspaso(c)
            if t:
                nombre = p.name if c == p else f"{p.name}/{c.name}"
                lineas.append(f"- {nombre}: {t}")
        entrada = p / "_entrada"
        if alta_en_curso(entrada / "_procesado" / "avance-alta.md"):
            lineas.append(f"- {p.name}: hay un alta en curso (ver _entrada/_procesado/avance-alta.md); ofrece continuarla.")
        if entrada.exists():
            n = sum(1 for x in entrada.rglob("*") if x.is_file() and x.name not in (".gitkeep", "LEEME.md") and not x.name.startswith("_LEEME")
                    and "_procesado" not in x.parts and "_archivo" not in x.parts)
            if n:
                lineas.append(f"- {p.name}: {n} archivo(s) en _entrada/ (pueden estar sin procesar).")
        n_cambios = (cambios or {}).get(f"proyectos/{p.name}", 0)
        if n_cambios:
            lineas.append(f"- {p.name}: {n_cambios} archivo(s) modificados sin guardar en Git; si el traspaso no los explica, "
                          "revisa `git status` y `git diff` antes de seguir, y ofrece `guardar-cambios`.")
    return "\n".join(lineas)


def main():
    import _consola
    _consola.preparar()
    print(resumen(remoto="--remoto" in sys.argv[1:]))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # el estado nunca debe impedir trabajar
        print(f"[Estado del PMO Harness]\n- No se pudo leer el estado completo ({e}).")
