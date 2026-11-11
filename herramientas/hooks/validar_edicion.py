#!/usr/bin/env python3
"""Hook PostToolUse (Edit/Write/MultiEdit y Bash): valida CSV y YAML del harness justo después de editarlos.

- Con Edit/Write/MultiEdit revisa el archivo editado.
- Con Bash (por ejemplo `cat >> archivo.csv` o un script) revisa los CSV y YAML de proyectos/ modificados en
  los últimos minutos, porque un comando de consola no informa qué archivos tocó.
- CSV: todas las filas con la misma cantidad de columnas que el encabezado; fechas AAAA-MM-DD en columnas
  de fecha; sin encabezados duplicados.
- YAML: que se pueda leer; en metricas.yaml, campos obligatorios y valores permitidos.
Si encuentra problemas, se los muestra a Claude para que los corrija de inmediato.
Las reglas de validación están en _comun.py y son las mismas del control de Git (.githooks/pre-commit).
"""
import sys
import re
import time
from pathlib import Path

from _comun import (bloquear, carpeta_de, git_salida, leer_evento, motivo_sensible, preparar_salida, quitar_del_staging,
                    raiz_git, revisar, staging_sensible)

RAIZ = Path(__file__).resolve().parent.parent.parent
VENTANA_SEG = 120


def confidenciales_tras_git(ev):
    """Después de un comando que usó Git, mira el estado real (no el texto del comando): saca del staging lo
    confidencial y avisa si el último commit, todavía sin subir, se llevó algo. Devuelve los avisos."""
    comando = (ev.get("tool_input") or {}).get("command", "")
    if not re.search(r"\bgit\b", comando):
        return []
    raiz = raiz_git(carpeta_de(ev))
    if raiz is None:
        return []
    avisos = []
    preparados = staging_sensible(raiz)
    if preparados:
        fuera = quitar_del_staging(raiz, [r for r, _ in preparados])
        detalle = "\n".join(f"- {r} ({m})" for r, m in preparados)
        avisos.append(("Saqué del staging" if len(fuera) == len(preparados) else "Hay en el staging") + " archivos confidenciales "
                      "(siguen en tu carpeta, intactos):\n" + detalle + "\nNo los vuelvas a agregar: no se suben a Git. Si la "
                      "carpeta debe quedar siempre fuera, usa `python herramientas/confidencialidad.py --agregar`."
                      + ("" if len(fuera) == len(preparados) else "\nNo pude sacarlos todos: usa `git restore --staged <archivo>`."))
    if re.search(r"\bcommit\b", comando):
        rc, archivos = git_salida(["log", "-1", "--name-only", "--diff-filter=ACMR", "--format="], raiz)
        en_commit = [(r, m) for r in archivos.splitlines() if r.strip() for m in [motivo_sensible(r.strip(), raiz)] if m] if rc == 0 else []
        if en_commit and not git_salida(["branch", "-r", "--contains", "HEAD"], raiz)[1].strip():
            avisos.append("El último commit incluye archivos confidenciales y todavía no se ha subido:\n"
                          + "\n".join(f"- {r} ({m})" for r, m in en_commit)
                          + "\nDeshazlo ahora: `git reset --soft HEAD~1`, luego `git restore --staged <archivo>` para cada uno, y "
                            "repite el commit sin ellos. No lo subas así: el control de subida lo detendría.")
    return avisos


def main():
    preparar_salida()
    ev = leer_evento()
    ruta = (ev.get("tool_input") or {}).get("file_path") or ""
    avisos = []
    if ruta:
        rutas = [Path(ruta)] if Path(ruta).exists() else []
    elif ev.get("tool_name") in ("Bash", "PowerShell"):
        rutas = recientes(RAIZ)
        avisos = confidenciales_tras_git(ev)
    else:
        return
    mensajes = []
    for r in rutas:
        problemas = revisar(r)
        if problemas:
            mensajes.append(f"{r}:\n- " + "\n- ".join(problemas))
    texto = []
    if avisos:
        texto.append("El harness protegió archivos confidenciales:\n" + "\n".join(avisos))
    if mensajes:
        texto.append("El harness detectó problemas tras la edición:\n" + "\n".join(mensajes) + "\nCorrígelos antes de continuar.")
    if texto:
        bloquear("\n\n".join(texto))


def recientes(base, segundos=VENTANA_SEG):
    """CSV y YAML bajo base/proyectos y base/empresa modificados hace menos de `segundos` (excluye _entrada)."""
    limite = time.time() - segundos
    rutas = []
    for carpeta in (base / "proyectos", base / "empresa"):
        if carpeta.exists():
            rutas += [p for p in carpeta.rglob("*") if p.is_file() and p.suffix.lower() in (".csv", ".yaml", ".yml")
                      and "_entrada" not in p.parts and p.stat().st_mtime >= limite]
    return rutas


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        sys.exit(0)
