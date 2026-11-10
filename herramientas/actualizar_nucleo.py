#!/usr/bin/env python3
"""Actualiza el núcleo del harness en esta carpeta de empresa sin tocar sus datos.

Uso:
    python herramientas/actualizar_nucleo.py [--desde <url del repositorio | carpeta>]            # vista previa
    python herramientas/actualizar_nucleo.py [--desde ...] --aplicar [--sin-pruebas] [--sin-commit]

- Origen: --desde, o `nucleo.origen` de .harness/estado.yaml. Puede ser la URL de un repositorio (se descarga una
  copia temporal) o una carpeta (por ejemplo, un zip descomprimido de la versión nueva).
- Solo cambia las rutas de NUCLEO.txt. Nunca toca proyectos/, empresa/, .harness/ (salvo su registro), la ficha de
  inicio ni lo propio de la empresa: una skill o un perfil propio dentro de una carpeta del núcleo se conserva.
- Los archivos del núcleo que se modificaron a mano se respaldan antes de reemplazarlos; los que el núcleo nuevo ya
  no trae se borran solo si no se modificaron.
- Con --aplicar: respalda en .harness/respaldo-nucleo/<fecha>/, aplica, revisa los proyectos reales de la carpeta (los
  scripts que no modifican datos, antes y después: si algo que funcionaba deja de funcionar, revierte), ejecuta la batería
  de pruebas y, si falla, revierte todo. Si pasa y la carpeta es un repositorio, hace el commit "Actualización del núcleo a <versión>".
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import _nucleo

RAIZ = Path(__file__).resolve().parent.parent
NUNCA = ("proyectos/", "empresa/", ".harness/", "FICHA-DE-INICIO.md")
SETTINGS = ".claude/settings.json"   # se fusiona, no se reemplaza: lo que el usuario agregó se conserva


def fusionar_settings(viejo, nuevo):
    """El settings.json del núcleo nuevo más lo propio del usuario en el viejo: permisos, hooks y claves que el núcleo
    no trae. Lo del núcleo viejo (menciona `herramientas/`) no se arrastra: lo trae el nuevo en su forma vigente.
    None si alguno no es JSON válido (entonces se reemplaza y el viejo queda en el respaldo)."""
    try:
        v, n = json.loads(viejo), json.loads(nuevo)
    except (ValueError, TypeError):
        return None
    if not isinstance(v, dict) or not isinstance(n, dict):
        return None
    propio = lambda x: "herramientas/" not in json.dumps(x)  # noqa: E731
    if isinstance(v.get("permissions"), dict):
        destino = n.setdefault("permissions", {})
        for clave, valor in v["permissions"].items():
            if isinstance(valor, list) and isinstance(destino.setdefault(clave, []), list):
                destino[clave].extend(x for x in valor if x not in destino[clave] and propio(x))
            elif clave not in destino:
                destino[clave] = valor
    if isinstance(v.get("hooks"), dict):
        for evento, entradas in v["hooks"].items():
            destino = n.setdefault("hooks", {}).setdefault(evento, [])
            if isinstance(entradas, list) and isinstance(destino, list):
                vistos = [json.dumps(x, sort_keys=True) for x in destino]
                destino.extend(x for x in entradas if json.dumps(x, sort_keys=True) not in vistos and propio(x))
    for clave, valor in v.items():
        if clave not in n:
            n[clave] = valor
    return json.dumps(n, indent=2, ensure_ascii=False) + "\n"


def bloques_yaml(texto):
    """[(clave, bloque)] de nivel superior de un YAML sencillo: la línea `clave:` y lo que sigue hasta la próxima clave."""
    bloques, clave, lineas = [], None, []
    for linea in texto.splitlines():
        m = re.match(r"^([A-Za-z_][\w-]*):", linea)
        if m:
            if clave:
                bloques.append((clave, "\n".join(lineas).rstrip("\n")))
            clave, lineas = m.group(1), [linea]
        elif clave is not None:
            lineas.append(linea)
    if clave:
        bloques.append((clave, "\n".join(lineas).rstrip("\n")))
    return bloques


def completar_empresa(fuente, aplicar=False):
    """[(ruta, descripción)] de lo que la plantilla de empresa del núcleo nuevo trae y empresa/ no tiene: archivos que
    faltan y bloques nuevos de empresa.yaml. Solo agrega; nunca cambia ni reemplaza lo existente."""
    plantilla, emp = Path(fuente) / "plantilla-empresa", RAIZ / "empresa"
    if not plantilla.is_dir() or not emp.is_dir():
        return []
    hechos = []
    for x in sorted(plantilla.rglob("*")):
        if not x.is_file() or "_procesado" in x.parts or x.name.startswith("~$"):
            continue
        rel = x.relative_to(plantilla).as_posix()
        destino = emp / rel
        if rel == "empresa.yaml" and destino.exists():
            local = destino.read_text(encoding="utf-8")
            claves = {k for k, _ in bloques_yaml(local)}
            faltan = [(k, b) for k, b in bloques_yaml(x.read_text(encoding="utf-8")) if k not in claves]
            if faltan:
                hechos.append(("empresa/empresa.yaml", "empresa/empresa.yaml: bloque(s) " + ", ".join(k for k, _ in faltan)))
                if aplicar:
                    destino.write_text(local.rstrip("\n") + "\n\n" + "\n\n".join(b for _, b in faltan) + "\n", encoding="utf-8")
            continue
        if destino.exists():
            continue
        hechos.append(("empresa/" + rel, "empresa/" + rel))
        if aplicar:
            destino.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(x, destino)
    return hechos


def anotar_fallo(que, evidencia):
    """Deja en el registro de mejoras de la carpeta que una actualización se revirtió: el mantenedor debe saberlo."""
    try:
        import mejoras
        return mejoras.anotar(RAIZ, "fallo", "actualizar_nucleo.py", que, evidencia, quien="sistema")
    except Exception:
        return None


def origen_configurado():
    """`nucleo.origen` de .harness/estado.yaml o, si no hay, el repositorio público del núcleo (NUCLEO.txt)."""
    estado = RAIZ / ".harness" / "estado.yaml"
    if estado.exists():
        m = re.search(r"^\s+origen:\s*\"?([^\"#\n]+?)\"?\s*(#.*)?$", estado.read_text(encoding="utf-8"), re.M)
        if m and m.group(1).strip() not in ("", "pendiente"):
            return m.group(1).strip()
    return _nucleo.origen_oficial(RAIZ)


def obtener_fuente(origen, tmp):
    p = Path(origen).expanduser()
    if p.is_dir():
        return p.resolve()
    destino = Path(tmp) / "nucleo"
    r = subprocess.run(["git", "-c", "core.autocrlf=false", "-c", "core.longpaths=true", "clone", "-q", "--depth", "1", origen,
                        str(destino)], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"No se pudo descargar el núcleo desde {origen}:\n{(r.stderr or r.stdout).strip()[:500]}")
    return destino


def plan(fuente):
    entradas_nuevas = _nucleo.rutas(fuente)
    entradas_locales = _nucleo.rutas(RAIZ) if (RAIZ / "NUCLEO.txt").exists() else []
    union = list(dict.fromkeys(entradas_locales + entradas_nuevas))
    union = [e for e in union if not any(e.startswith(n) for n in NUNCA)]
    nuevos = _nucleo.archivos(fuente, [e for e in entradas_nuevas if e in union])
    locales = _nucleo.archivos(RAIZ, union)
    manifiesto = _nucleo.leer_manifiesto(RAIZ)
    p = {"agregar": [], "reemplazar": [], "iguales": 0, "eliminar": [], "modificados": [], "propios": [], "revisar": [],
         "nuevos": nuevos, "union": union, "manifiesto": manifiesto is not None}
    for rel, h in nuevos.items():
        if rel not in locales:
            p["agregar"].append(rel)
        elif locales[rel] != h:
            p["reemplazar"].append(rel)
            if manifiesto and rel in manifiesto and manifiesto[rel] != locales[rel]:
                p["modificados"].append(rel)
        else:
            p["iguales"] += 1
    for rel, h in locales.items():
        if rel in nuevos:
            continue
        if manifiesto is None:
            p["revisar"].append(rel)
        elif rel not in manifiesto:
            p["propios"].append(rel)
        elif manifiesto[rel] == h:
            p["eliminar"].append(rel)
        else:
            p["modificados"].append(rel)
            p["propios"].append(rel)
    # settings.json con cambios del usuario (o sin registro de lo instalado): se fusiona en vez de reemplazar
    p["fusionar"] = [SETTINGS] if SETTINGS in p["reemplazar"] and (SETTINGS in p["modificados"] or manifiesto is None) else []
    p["modificados"] = [x for x in p["modificados"] if x not in p["fusionar"]]
    return p


def revisar_proyectos():
    """{"<proyecto> · <script>": funciona} ejecutando sobre cada proyecto real los scripts que no modifican datos.
    Sirve para comparar antes y después de actualizar: si algo que funcionaba deja de funcionar, se revierte."""
    resultado = {}
    for p in sorted((RAIZ / "proyectos").glob("*")):
        if not (p / "proyecto.yaml").exists():
            continue
        for c in [p] + sorted(s for s in (p / "subproyectos").glob("*") if (s / "proyecto.yaml").exists()):
            m = re.search(r"^arquetipos:\s*\[(.*?)\]", (c / "proyecto.yaml").read_text(encoding="utf-8", errors="replace"), re.M)
            arqs = m.group(1) if m else ""
            comandos = [["evaluar_metricas.py"], ["validar_proyecto.py"], ["guia_proyecto.py", "--no-escribir"]]
            if "postulacion" in arqs:
                comandos.append(["postulacion.py"])
            if "programa" in arqs:
                comandos.append(["programa.py", "--sin-gantt"])
            if "investigacion" in arqs and (RAIZ / "herramientas" / "investigacion.py").exists():
                comandos.append(["investigacion.py"])  # sin --revisar: comprueba que el script lee las investigaciones
            if "finanzas" in arqs and (RAIZ / "herramientas" / "finanzas.py").exists():
                comandos.append(["finanzas.py"])
            rel = c.relative_to(RAIZ).as_posix()
            for script, *extra in comandos:
                try:
                    r = subprocess.run([sys.executable, f"herramientas/{script}", rel, *extra], cwd=RAIZ, capture_output=True,
                                       text=True, encoding="utf-8", errors="replace", timeout=300)
                    resultado[f"{rel} · {script}"] = r.returncode == 0 and "Traceback" not in (r.stdout or "") + (r.stderr or "")
                except subprocess.TimeoutExpired:
                    resultado[f"{rel} · {script}"] = False
    return resultado


def lista(titulo, items, maximo=15):
    if not items:
        return []
    salida = [f"- {titulo}: {len(items)}"]
    salida += [f"  - {x}" for x in items[:maximo]]
    if len(items) > maximo:
        salida.append(f"  - … y {len(items) - maximo} más")
    return salida


def git(*args):
    r = subprocess.run(["git", *args], cwd=RAIZ, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--desde", help="URL del repositorio del núcleo o carpeta con la versión nueva")
    ap.add_argument("--aplicar", action="store_true", help="aplicar la actualización (sin esto, solo vista previa)")
    ap.add_argument("--sin-pruebas", action="store_true", help="no ejecutar la batería de pruebas después de aplicar")
    ap.add_argument("--sin-commit", action="store_true", help="no hacer el commit de la actualización")
    ap.add_argument("--carpeta", help=argparse.SUPPRESS)  # carpeta de empresa a actualizar (la usa el actualizador nuevo al relanzarse)
    a = ap.parse_args()
    global RAIZ
    if a.carpeta:
        RAIZ = Path(a.carpeta).resolve()

    if _nucleo.es_mantenedor(RAIZ):
        sys.exit("Esta carpeta es el núcleo que mantienes: se actualiza con Git (git pull / git push), no con este comando.")
    origen = a.desde or origen_configurado()
    if not origen:
        sys.exit("No sé de dónde traer el núcleo: indica --desde <url o carpeta>, o completa nucleo.origen en .harness/estado.yaml.")
    with tempfile.TemporaryDirectory(prefix="pmo-nucleo-") as tmp:
        fuente = obtener_fuente(origen, tmp)
        if fuente.resolve() == RAIZ.resolve():
            sys.exit("El origen es esta misma carpeta: indica la carpeta o el repositorio del núcleo nuevo.")
        # Si el núcleo nuevo trae un actualizador distinto, es ese el que actualiza esta carpeta: así las mejoras del
        # actualizador valen desde esta actualización y no desde la siguiente.
        nuevo = fuente / "herramientas" / "actualizar_nucleo.py"
        if (not a.carpeta and nuevo.is_file() and _nucleo.huella(nuevo) != _nucleo.huella(Path(__file__).resolve())
                and "--carpeta" in nuevo.read_text(encoding="utf-8", errors="replace")):  # uno anterior a 2.6.1 no sabría
            origen_hijo = str(Path(origen).expanduser().resolve()) if Path(origen).expanduser().is_dir() else origen
            args = [sys.executable, str(nuevo), "--carpeta", str(RAIZ), "--desde", origen_hijo]
            args += [x for x, v in (("--aplicar", a.aplicar), ("--sin-pruebas", a.sin_pruebas), ("--sin-commit", a.sin_commit)) if v]
            return subprocess.run(args, cwd=RAIZ).returncode
        p = plan(fuente)
        faltantes = completar_empresa(fuente)
        v_local, v_nueva = _nucleo.version(RAIZ), _nucleo.version(fuente)
        out = ["# Actualización del núcleo", "", f"- Origen: {origen}", f"- Versión: {v_local or '?'} → {v_nueva or '?'}",
               f"- Archivos: {len(p['agregar'])} nuevos · {len(p['reemplazar'])} cambiados · {len(p['eliminar'])} eliminados · "
               f"{p['iguales']} iguales"]
        out += lista("Nuevos", p["agregar"]) + lista("Cambiados", p["reemplazar"]) + lista("Eliminados (el núcleo nuevo ya no los trae)", p["eliminar"])
        out += lista("Modificados a mano en esta carpeta (se respaldan antes de reemplazarlos)", p["modificados"])
        out += lista("Se fusionan (entra lo del núcleo nuevo; tus permisos y hooks propios se conservan)", p["fusionar"])
        out += lista("Se completa en empresa/ (solo lo que falta; nada existente cambia)", [d for _, d in faltantes])
        out += lista("Propios de la empresa dentro de carpetas del núcleo (se conservan)", p["propios"])
        out += lista("Sin registro del núcleo instalado: no se borran, revísalos", p["revisar"])
        out += [f"- No se tocan: {', '.join(NUNCA)}"]
        nov = _nucleo.novedades(fuente, v_local)
        if nov and v_nueva != v_local:
            lineas = nov.splitlines()
            out += ["", "## Novedades", "", *lineas[:60]] + (["", f"(… {len(lineas) - 60} líneas más en CHANGELOG.md)"] if len(lineas) > 60 else [])
        cambios = p["agregar"] or p["reemplazar"] or p["eliminar"] or faltantes
        if not a.aplicar:
            out += ["", "Vista previa: nada cambió." + (" Para aplicar: python herramientas/actualizar_nucleo.py "
                    + (f"--desde {origen} " if a.desde else "") + "--aplicar" if cambios else " El núcleo ya está al día.")]
            print("\n".join(out))
            return 0
        print("\n".join(out))
        if not cambios:
            print("\nEl núcleo ya está al día.")
            _nucleo.escribir_manifiesto(RAIZ, p["nuevos"])
            return 0

        # Respaldo de todo lo que se reemplaza o elimina (y del registro), para poder revertir
        antes = revisar_proyectos()  # con el núcleo actual, para comparar después

        # Rutas largas de Windows: todas las operaciones de archivos pasan por el prefijo \\?\
        local, nueva = _nucleo.ruta_larga(RAIZ), _nucleo.ruta_larga(fuente)
        base_respaldo = local / ".harness" / "respaldo-nucleo" / datetime.now().strftime("%Y-%m-%d_%H%M%S")
        respaldo, n = base_respaldo, 1
        while respaldo.exists():  # dos actualizaciones en el mismo segundo no comparten respaldo (revertir una no toca la otra)
            n += 1
            respaldo = base_respaldo.with_name(f"{base_respaldo.name}_{n}")
        for rel in p["reemplazar"] + p["eliminar"] + [_nucleo.MANIFIESTO.as_posix(), ".harness/estado.yaml"]:
            src = local / rel
            if src.exists():
                (respaldo / rel).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, respaldo / rel)

        def revertir():
            for rel in p["agregar"]:
                (local / rel).unlink(missing_ok=True)
            for x in respaldo.rglob("*"):
                if x.is_file():
                    destino = local / x.relative_to(respaldo)
                    destino.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(x, destino)

        for rel in p["agregar"] + p["reemplazar"]:
            (local / rel).parent.mkdir(parents=True, exist_ok=True)
            if rel in p["fusionar"]:
                fusion = fusionar_settings((local / rel).read_text(encoding="utf-8"), (nueva / rel).read_text(encoding="utf-8"))
                if fusion is not None:
                    (local / rel).write_text(fusion, encoding="utf-8")
                    continue
            shutil.copy2(nueva / rel, local / rel)
        for rel in p["eliminar"]:
            (local / rel).unlink(missing_ok=True)
            carpeta = (local / rel).parent
            while carpeta != local and carpeta.exists() and not any(carpeta.iterdir()):
                carpeta.rmdir()
                carpeta = carpeta.parent
        for ejecutable in _nucleo.EJECUTABLES:
            x = RAIZ / ejecutable
            if x.exists():
                x.chmod(x.stat().st_mode | 0o111)
        # El registro guarda solo lo que vino del núcleo: lo propio de la empresa nunca entra (si no, se borraría después)
        _nucleo.escribir_manifiesto(RAIZ, p["nuevos"])
        estado = RAIZ / ".harness" / "estado.yaml"
        if estado.exists() and v_nueva:
            texto = estado.read_text(encoding="utf-8")
            texto = re.sub(r'^version_harness:.*$', f'version_harness: "{v_nueva}"', texto, count=1, flags=re.M)
            estado.write_text(texto, encoding="utf-8")
        print(f"\nAplicado. Respaldo de lo reemplazado: {respaldo.relative_to(local).as_posix()}/")

        if antes:
            print(f"Revisando los proyectos de esta carpeta con el núcleo nuevo ({len(antes)} revisiones)...")
            despues = revisar_proyectos()
            rotos = sorted(k for k, ok in antes.items() if ok and not despues.get(k, False))
            if rotos:
                revertir()
                print("Con el núcleo nuevo, estos proyectos dejarían de funcionar: se revirtió la actualización. Nada cambió.\n"
                      + "\n".join(f"- {k}" for k in rotos)
                      + "\nAvísale a quien mantiene el núcleo (puede ser un cambio de formato de los datos).")
                anotar_fallo(f"Actualizar a {v_nueva or '?'} deja de funcionar proyectos reales: se revirtió", "; ".join(rotos)[:300])
                return 1
            print("Proyectos: todos siguen funcionando.")

        if not a.sin_pruebas:
            print("Ejecutando la batería de pruebas...")
            r = subprocess.run([sys.executable, "pruebas/ejecutar_pruebas.py"], cwd=RAIZ, capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=1800)
            ultima = ((r.stdout or "") + (r.stderr or "")).strip().splitlines()[-1:] or ["sin salida"]
            if r.returncode != 0:
                revertir()
                print(f"Las pruebas fallaron ({ultima[0]}): se revirtió la actualización. Nada cambió.\n"
                      "Avísale a quien mantiene el núcleo; el detalle sale con: python pruebas/ejecutar_pruebas.py")
                anotar_fallo(f"La batería falla tras actualizar a {v_nueva or '?'}: se revirtió", ultima[0][:300])
                return 1
            print(f"Pruebas: {ultima[0]}")

        # Recién ahora (ya nada puede revertir): lo que la plantilla de empresa nueva trae y esta carpeta no tiene
        completados = completar_empresa(fuente, aplicar=True)
        if completados:
            print("Completado en empresa/ (solo lo que faltaba): " + ", ".join(d for _, d in completados))
        try:  # las mejoras que esta carpeta envió y el núcleo nuevo ya respondió
            import mejoras
            cerradas = mejoras.cerrar_resueltas(RAIZ)
            if cerradas:
                print("Mejoras al núcleo con respuesta del mantenedor: " + ", ".join(f"{i} {e}" for i, e in cerradas)
                      + " (python herramientas/mejoras.py --listar --todas)")
        except Exception:
            pass

        rc, top = git("rev-parse", "--show-toplevel")
        if not a.sin_commit and rc == 0 and Path(top).resolve() == RAIZ.resolve():
            rutas_git = ([e.rstrip("/") for e in p["union"]] + [".harness/estado.yaml", _nucleo.MANIFIESTO.as_posix(),
                          ".harness/mejoras-nucleo.csv"] + [r for r, _ in completados])
            git("add", "-A", "--", *[x for x in rutas_git if (RAIZ / x).exists() or any(r.startswith(x) for r in p["eliminar"])])
            git("update-index", "--chmod=+x", *[e for e in _nucleo.EJECUTABLES if (RAIZ / e).exists()])
            rc_c, salida = git("commit", "-q", "-m", f"Actualización del núcleo a {v_nueva or 'la versión nueva'}")
            print("Commit: «Actualización del núcleo" + (f" a {v_nueva}»" if v_nueva else "»") if rc_c == 0
                  else f"No se hizo el commit: {salida[:400]}")
        if p["modificados"]:
            print("Revisa los archivos que estaban modificados a mano: su versión anterior quedó en el respaldo. "
                  "Si eran ajustes propios, llévalos a la carpeta del proyecto o de la empresa (regla 8 de AGENTS.md).")
    return 0


if __name__ == "__main__":
    import _consola
    _consola.preparar()
    sys.exit(main())
