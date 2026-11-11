#!/usr/bin/env python3
"""Control del harness antes de cada commit y antes de subir: funciona con cualquier asistente de IA, o sin asistente.

Uso:
    (automático) Git lo ejecuta desde .githooks/pre-commit y .githooks/pre-push si está activo
                 `git config core.hooksPath .githooks`
    python herramientas/hooks/precommit.py --archivos <ruta> [<ruta> ...]   # validar archivos recién editados
    python herramientas/hooks/precommit.py --push                           # lo que Git le pasa a pre-push (por la entrada)

Antes de un commit revisa los archivos en staging (o los indicados con --archivos):
- bloquea los confidenciales: los que el harness protege siempre (_entrada/, originales, banco de contenidos, paquete
  final, credenciales), los que la empresa definió en `empresa/confidencialidad.yaml` (`nunca_subir`), las réplicas de
  fuentes/ marcadas `confidencialidad: sensible` y los textos con una clave o llave pegada;
- avisa (sin detener, salvo que la empresa pida bloquear) de los Word, Excel, PDF e imágenes nuevos que no están en
  una carpeta de salidas, plantillas o marca: pueden ser material del cliente guardado donde no corresponde;
- valida los CSV (columnas, fechas AAAA-MM-DD) y YAML (sintaxis, definiciones de métricas) de proyectos/ y empresa/.
Antes de subir (--push) revisa todos los commits que todavía no están en el remoto: si alguno lleva un archivo
confidencial (por ejemplo, uno hecho en un computador sin el control activo), la subida no sale.
Termina con código 1 si encuentra problemas (Git cancela la operación) y explica qué hacer.
"""
import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comun import (binario_suelto, clave_en_texto, motivo_sensible, politica, preparar_salida, replica_sensible,  # noqa: E402
                    revisar)

CARPETAS_VALIDADAS = ("proyectos", "empresa")
CERO = "0" * 40


def git(*args, raiz=None, entrada=None):
    r = subprocess.run(["git", "-c", "core.quotepath=false", *args], cwd=raiz, capture_output=True, timeout=60, input=entrada)
    return r.returncode, r.stdout.decode("utf-8", errors="replace")


def en_staging(raiz, filtro="ACMR"):
    """Archivos agregados o modificados en el staging (sin los borrados)."""
    _, salida = git("diff", "--cached", "--name-only", f"--diff-filter={filtro}", "-z", raiz=raiz)
    return [x for x in salida.split("\0") if x.strip()]


def contenido_preparado(raiz, rel):
    rc, texto = git("show", f":{rel}", raiz=raiz)
    return texto if rc == 0 else ""


def validable(rel):
    partes = Path(rel).parts
    return (len(partes) > 1 and partes[0] in CARPETAS_VALIDADAS and "_entrada" not in partes
            and Path(rel).suffix.lower() in (".csv", ".yaml", ".yml"))


def es_replica(rel):
    partes = Path(rel).parts
    return "fuentes" in partes[:-1] and Path(rel).suffix.lower() == ".md" and Path(rel).name.upper() != "LEEME.MD"


def claves_agregadas(raiz):
    """{archivo: tipo de clave} mirando solo las líneas que este commit agrega en proyectos/ y empresa/ (una sola consulta)."""
    _, diff = git("diff", "--cached", "-U0", "--no-color", "--diff-filter=ACMR", "--", *CARPETAS_VALIDADAS, raiz=raiz)
    hallados, actual = {}, None
    for linea in diff.splitlines():
        if linea.startswith("+++ "):
            actual = linea[6:] if linea.startswith("+++ b/") else None
        elif actual and linea.startswith("+") and actual not in hallados:
            tipo = clave_en_texto(linea)
            if tipo:
                hallados[actual] = tipo
    return hallados


def revisar_archivos(raiz, relativos, leer, claves=None):
    confidenciales, invalidos = [], []
    for rel in relativos:
        rel = rel.replace("\\", "/")
        motivo = motivo_sensible(rel, raiz)
        if motivo:
            confidenciales.append(f"- {rel} ({motivo})")
            continue
        if es_replica(rel) and replica_sensible(leer(rel)):
            confidenciales.append(f"- {rel} (réplica marcada confidencialidad: sensible: solo debe quedar su ficha)")
            continue
        if claves and rel in claves:
            confidenciales.append(f"- {rel} (trae pegada una {claves[rel]}: quítala del texto y cámbiala si ya se usó)")
            continue
        ruta = raiz / rel
        if validable(rel) and ruta.exists():
            problemas = revisar(ruta)
            if problemas:
                invalidos.append(f"{rel}:\n  - " + "\n  - ".join(problemas))
    return confidenciales, invalidos


def revisar_subida(raiz, lineas):
    """Código 1 si algún commit que se va a subir (y todavía no está en el remoto) lleva un archivo confidencial."""
    hallados = {}
    for linea in lineas:
        partes = linea.split()
        if len(partes) < 4 or partes[1] == CERO:  # borrar una rama remota no sube nada
            continue
        local, remoto = partes[1], partes[3]
        rango = [f"{remoto}..{local}"] if remoto != CERO else [local, "--not", "--remotes"]
        rc, salida = git("log", "--name-only", "--diff-filter=ACMR", "--format=%x00%h", *rango, raiz=raiz)
        if rc != 0:  # el remoto apunta a algo que aquí no existe: se revisa todo lo que no está en ningún remoto
            _, salida = git("log", "--name-only", "--diff-filter=ACMR", "--format=%x00%h", local, "--not", "--remotes", raiz=raiz)
        for bloque in salida.split("\0"):
            filas = [x for x in bloque.splitlines() if x.strip()]
            for rel in filas[1:]:
                motivo = motivo_sensible(rel, raiz)
                if motivo:
                    hallados.setdefault(rel, (filas[0], motivo))
    if not hallados:
        return 0
    print("PMO Harness: subida detenida. Estos commits, que todavía están solo en este computador, llevan archivos "
          "confidenciales:\n" + "\n".join(f"- {rel} (commit {c}: {m})" for rel, (c, m) in sorted(hallados.items()))
          + "\n→ Nada salió. Hay que sacarlos del historial local antes de subir. Si están en el último commit: "
            "`git reset --soft HEAD~1`, `git restore --staged <archivo>` y repite el commit sin ellos. Si están más atrás, "
            "pídele a tu asistente «saca del historial local estos archivos confidenciales» y revisa el resultado con "
            "`python herramientas/confidencialidad.py --auditar`.\n"
            "No uses `git push --no-verify`: el control existe para que lo confidencial no salga de este computador.",
          file=sys.stderr)
    return 1


def main():
    preparar_salida()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--archivos", nargs="+", help="valida estos archivos en vez del staging")
    ap.add_argument("--push", action="store_true", help="revisa los commits que se van a subir (entrada de pre-push)")
    a, _ = ap.parse_known_args()  # pre-push recibe además el nombre y la dirección del remoto

    rc, top = git("rev-parse", "--show-toplevel")
    raiz = Path(top.strip()).resolve() if rc == 0 and top.strip() else Path(__file__).resolve().parent.parent.parent
    if a.push:
        return revisar_subida(raiz, sys.stdin.read().splitlines())

    claves, nuevos = {}, []
    if a.archivos:
        relativos = []
        for x in a.archivos:
            p = Path(x).resolve()
            try:
                relativos.append(p.relative_to(raiz).as_posix())
            except ValueError:
                relativos.append(Path(x).as_posix())

        def leer(rel):
            try:
                return (raiz / rel).read_text(encoding="utf-8", errors="replace")
            except OSError:
                return ""
        for rel in relativos:
            if Path(rel).suffix.lower() in (".md", ".csv", ".yaml", ".yml", ".txt", ".json") and (raiz / rel).is_file() \
                    and (raiz / rel).stat().st_size < 2_000_000:
                tipo = clave_en_texto(leer(rel))
                if tipo:
                    claves[rel] = tipo
    else:
        relativos = en_staging(raiz)
        nuevos = en_staging(raiz, "A")
        claves = claves_agregadas(raiz)

        def leer(rel):
            return contenido_preparado(raiz, rel)

    pol = politica(raiz)
    avisos = []
    # Regla 17 (aviso, no bloqueo): un proyecto cambia en el commit y su traspaso no viene con él
    if not a.archivos:
        tocados = sorted({Path(r).parts[1] for r in relativos if Path(r).parts[:1] == ("proyectos",) and len(Path(r).parts) > 2
                          and "_entrada" not in Path(r).parts})
        sin_traspaso = [s for s in tocados if f"proyectos/{s}/seguimiento/traspaso.md" not in relativos
                        and (raiz / "proyectos" / s / "seguimiento" / "traspaso.md").exists()]
        if sin_traspaso:
            avisos.append("Aviso (regla 17): " + ", ".join(f"proyectos/{s}" for s in sin_traspaso) + " cambia en este commit y su "
                          "seguimiento/traspaso.md no va en él. Si la tarea terminó, actualízalo (hecho, próximo paso, comprobado, no "
                          "comprobado, tuve que adivinar) y agrégalo al commit.")

    claves_bloquean = pol["claves_en_texto"] == "bloquear"
    confidenciales, invalidos = revisar_archivos(raiz, relativos, leer, claves if claves_bloquean else None)
    if claves and not claves_bloquean:
        avisos.append("Aviso: estos textos traen pegada una clave o llave: " + ", ".join(f"{r} ({t})" for r, t in sorted(claves.items()))
                      + ". Quítala antes de subir y cámbiala si ya se usó.")
    sueltos = [r for r in nuevos if not motivo_sensible(r, raiz) and binario_suelto(r, raiz)] if pol["binarios_sueltos"] != "permitir" else []
    if sueltos and pol["binarios_sueltos"] == "bloquear":
        confidenciales += [f"- {r} (Word, Excel, PDF o imagen fuera de una carpeta de salidas: la empresa pide clasificarlo antes)" for r in sueltos]
    elif sueltos:
        avisos.append("Aviso: este commit agrega Word, Excel, PDF o imágenes que no están en una carpeta de salidas, plantillas o "
                      "marca:\n" + "\n".join(f"- {r}" for r in sueltos[:12]) + (f"\n- … y {len(sueltos) - 12} más" if len(sueltos) > 12 else "")
                      + "\nSi son material del cliente, van en `_entrada/` (no se suben) o en `nunca_subir` "
                        "(`python herramientas/confidencialidad.py --agregar`). Si son tuyos y deben subirse, sigue: es solo un aviso.")
    if avisos:
        print("\n".join(avisos), file=sys.stderr)

    if not confidenciales and not invalidos:
        if a.archivos:
            print(f"OK: {len(relativos)} archivo(s) revisado(s) sin problemas.")
        return 0
    lineas = ["PMO Harness: " + ("commit detenido." if not a.archivos else "se encontraron problemas.")]
    if confidenciales:
        lineas += ["", "Archivos confidenciales (no se suben a Git):", *confidenciales,
                   "→ Quítalos del staging con `git restore --staged <archivo>` y agrega el patrón a .gitignore si corresponde.",
                   "  Si el usuario confirma explícitamente que uno debe versionarse, explícale el riesgo antes."]
    if invalidos:
        lineas += ["", "Planillas o definiciones con errores:", *invalidos, "→ Corrígelos y vuelve a intentar."]
    lineas += ["", "No uses `git commit --no-verify`: el control existe para proteger la información del proyecto."]
    print("\n".join(lineas), file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
