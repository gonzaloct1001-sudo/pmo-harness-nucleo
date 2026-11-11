#!/usr/bin/env python3
"""Actualiza el núcleo del harness en esta carpeta de empresa sin tocar sus datos.

Uso:
    python herramientas/actualizar_nucleo.py [--desde <url del repositorio | carpeta>]            # vista previa
    python herramientas/actualizar_nucleo.py [--desde ...] --aplicar [--sin-pruebas] [--sin-commit]
    python herramientas/actualizar_nucleo.py --verificar                       # ¿el núcleo está como se instaló? (sin internet)
    python herramientas/actualizar_nucleo.py --restaurar <archivo> [...] [--desde ...]   # vuelve un archivo a su original

- Catastro: `.harness/nucleo-instalado.csv` guarda cada archivo del núcleo con su huella tal como se instaló. Con él,
  `--verificar` dice qué se modificó en la carpeta, qué falta y qué es propio; `--restaurar` devuelve un archivo
  cambiado o borrado por error a su original (lo busca en el historial de Git de la carpeta o en `--desde`, y lo
  comprueba por su huella); la versión que había queda en el respaldo.

- Origen: --desde, o `nucleo.origen` de .harness/estado.yaml. Puede ser la URL de un repositorio (se descarga una
  copia temporal) o una carpeta (por ejemplo, un zip descomprimido de la versión nueva).
- Solo cambia las rutas de NUCLEO.txt. Nunca toca proyectos/, empresa/, .harness/ (salvo su registro), la ficha de
  inicio ni lo propio de la empresa: una skill o un perfil propio dentro de una carpeta del núcleo se conserva.
- Lo tuyo nunca se pierde ni se pisa en silencio: un archivo del núcleo que modificaste se conserva si el núcleo nuevo
  no lo cambia (si también lo cambia, se respalda y se reemplaza, y queda avisado); algo propio que choca de nombre con
  algo nuevo del núcleo se conserva con otro nombre (`<nombre>-propia`); `.gitignore`, `requirements.txt` y
  `.claude/settings.json` se fusionan (entra lo nuevo y queda lo que agregaste). Los archivos que el núcleo nuevo ya no
  trae se borran solo si no se modificaron.
- Las pruebas propias de la empresa (`empresa/extensiones/pruebas*.py`, `empresa/pruebas/*.py`) se ejecutan antes y
  después: si una que pasaba deja de pasar, se revierte.
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
from pathlib import Path, PurePosixPath

import _nucleo

RAIZ = Path(__file__).resolve().parent.parent
NUNCA = ("proyectos/", "empresa/", ".harness/", "FICHA-DE-INICIO.md")
SETTINGS = ".claude/settings.json"   # se fusiona, no se reemplaza: lo que el usuario agregó se conserva
POR_LINEAS = (".gitignore", "requirements.txt")   # también se fusionan: entra el del núcleo nuevo y quedan las líneas propias
MARCA_PROPIO = _nucleo.MARCA_PROPIO


def fusionar_settings(viejo, nuevo, archivo_propio=None):
    """El settings.json del núcleo nuevo más lo propio del usuario en el viejo: permisos, hooks y claves que el núcleo
    no trae. Lo del núcleo viejo (menciona `herramientas/`) no se arrastra: lo trae el nuevo en su forma vigente; salvo
    que apunte a un archivo propio de la empresa dentro de `herramientas/` (`archivo_propio(ruta)` lo dice).
    None si alguno no es JSON válido (entonces se reemplaza y el viejo queda en el respaldo)."""
    try:
        v, n = json.loads(viejo), json.loads(nuevo)
    except (ValueError, TypeError):
        return None
    if not isinstance(v, dict) or not isinstance(n, dict):
        return None
    def propio(x):
        texto = json.dumps(x)
        if "herramientas/" not in texto:
            return True
        return bool(archivo_propio) and any(archivo_propio(r) for r in re.findall(r"herramientas/[\w./-]+", texto))

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


def fusionar_lineas(viejo, nuevo, por_paquete=False):
    """El archivo del núcleo nuevo más las líneas que esta carpeta había agregado al suyo, bajo una marca. Sirve para
    `.gitignore` (lo que la empresa decidió no subir nunca) y `requirements.txt` (con `por_paquete`, una dependencia
    que el núcleo ya trae no se repite). Ante la duda, una línea se conserva: nunca se pierde una protección."""
    clave = (lambda l: re.split(r"[<>=!~\[; ]", l.strip(), maxsplit=1)[0].lower()) if por_paquete else (lambda l: l.strip())
    presentes = {clave(l) for l in nuevo.splitlines() if l.strip()}
    antes, _, bloque = viejo.partition(MARCA_PROPIO)
    candidatas = [l for l in antes.splitlines() if not l.lstrip().startswith("#")] + bloque.splitlines()
    propias = list(dict.fromkeys(l.rstrip() for l in candidatas if l.strip() and clave(l) not in presentes))
    if not propias:
        return nuevo
    return nuevo.rstrip("\n") + "\n\n" + MARCA_PROPIO + "\n" + "\n".join(propias) + "\n"


def renombres_por_choque(choques, manifiesto):
    """[(origen, destino)] para lo propio de la empresa que tiene el mismo nombre que algo que trae el núcleo nuevo.
    Lo propio no se pisa: una skill enteramente propia cambia de nombre completa (`<nombre>-propia`) y un archivo
    suelto pasa a `<nombre>-propio.<ext>`; después entra lo del núcleo con el nombre original."""
    def libre(rel):
        candidato, n = rel, 1
        while (RAIZ / candidato).exists():
            n += 1
            x = PurePosixPath(rel)
            candidato = str(x.with_name(f"{x.stem}-{n}{x.suffix}"))
        return candidato

    hechos, vistas = [], set()
    for rel in choques:
        partes = rel.split("/")
        carpeta = "/".join(partes[:3]) if rel.startswith(".claude/skills/") and len(partes) > 3 else ""
        if carpeta and not any(m.startswith(carpeta + "/") for m in (manifiesto or {})):
            if carpeta not in vistas:
                vistas.add(carpeta)
                hechos.append((carpeta, libre(carpeta + "-propia")))
            continue
        x = PurePosixPath(rel)
        hechos.append((rel, libre(str(x.with_name(f"{x.stem}-propio{x.suffix}")))))
    return hechos


def revisar_extensiones():
    """{"<archivo de pruebas propio>": pasa} con las pruebas propias de la empresa, ejecutadas tal como están. Sirve para
    comparar antes y después de actualizar: si una extensión que funcionaba deja de funcionar, se revierte."""
    resultado = {}
    for rel in _nucleo.pruebas_propias(RAIZ):
        try:
            r = subprocess.run([sys.executable, rel], cwd=RAIZ, capture_output=True, text=True, encoding="utf-8",
                               errors="replace", timeout=600)
            resultado[rel] = r.returncode == 0
        except subprocess.TimeoutExpired:
            resultado[rel] = False
    return resultado


def anotar_reemplazados(archivos, respaldo):
    """Deja anotado para el mantenedor que esta carpeta tenía archivos del núcleo cambiados a mano: suelen ser arreglos
    que el núcleo debería traer."""
    try:
        import mejoras
        return mejoras.anotar(RAIZ, "aprendizaje", "actualizar_nucleo.py",
                              "Esta carpeta tenía archivos del núcleo modificados a mano y la actualización los reemplazó: "
                              + ", ".join(archivos)[:300],
                              f"Sus versiones anteriores quedaron en {respaldo}/",
                              por_que="Si eran arreglos o ajustes que el núcleo debería traer, conviene describirlos como mejora",
                              quien="sistema")
    except Exception:
        return None


def verificar():
    """Compara el núcleo de esta carpeta con el catastro de lo instalado. Código 1 si falta algún archivo."""
    d = _nucleo.desviaciones(RAIZ)
    if d is None:
        print("Esta carpeta no tiene catastro del núcleo instalado (.harness/nucleo-instalado.csv): se crea al instalar "
              "o en la próxima actualización.")
        return 0
    registro = RAIZ / _nucleo.MANIFIESTO
    total = len(_nucleo.leer_manifiesto(RAIZ))
    out = ["# Catastro del núcleo instalado", "", f"- Versión instalada: {_nucleo.version(RAIZ) or '?'} · catastro del "
           f"{datetime.fromtimestamp(registro.stat().st_mtime).strftime('%Y-%m-%d')} con {total} archivos",
           f"- Intactos: {total - len(d['modificados']) - len(d['fusionados']) - len(d['faltantes'])} · modificados en esta carpeta: "
           f"{len(d['modificados'])} · con agregados tuyos: {len(d['fusionados'])} · faltantes: {len(d['faltantes'])} · "
           f"propios dentro de carpetas del núcleo: {len(d['propios'])}"]
    out += lista("Modificados en esta carpeta (se conservan al actualizar mientras el núcleo nuevo no los cambie)", d["modificados"], 40)
    out += lista("Con agregados tuyos (permisos, hooks, lo que nunca se sube, dependencias: se fusionan al actualizar)", d["fusionados"], 40)
    out += lista("Faltan (el núcleo los trae y aquí no están)", d["faltantes"], 40)
    out += lista("Propios de la empresa dentro de carpetas del núcleo (ninguna actualización los toca)", d["propios"], 40)
    ajustes = RAIZ / SETTINGS
    if ajustes.exists():
        try:
            json.loads(ajustes.read_text(encoding="utf-8"))
        except ValueError as e:
            out += [f"- ATENCIÓN: {SETTINGS} no es un JSON válido ({e}): la herramienta lo ignora y no se podrá fusionar al "
                    "actualizar. Corrígelo (suele faltar una coma o una llave)."]
    if d["modificados"] or d["faltantes"]:
        out += ["", "Si un cambio no fue a propósito, el archivo vuelve a su original con:",
                "  python herramientas/actualizar_nucleo.py --restaurar <archivo> [<archivo> ...]",
                "(la versión que hay queda en el respaldo). Si fue a propósito, lo propio dura más en empresa/extensiones/."]
    else:
        out += ["", "El núcleo está tal como se instaló."]
    print("\n".join(out))
    return 1 if d["faltantes"] else 0


def original_en_historial(rel, huella_esperada):
    """Contenido original de `rel` (el que tiene la huella del catastro) buscado en el historial de Git de la carpeta."""
    rc, commits = git("log", "--format=%H", "--", rel)
    if rc != 0:
        return None
    for c in commits.split()[:200]:
        r = subprocess.run(["git", "show", f"{c}:{rel}"], cwd=RAIZ, capture_output=True)
        if r.returncode == 0 and _nucleo.huella_datos(r.stdout) == huella_esperada:
            return r.stdout
    return None


def restaurar(pedidos, desde=None):
    """Devuelve archivos del núcleo a su original instalado. Lo que había queda en el respaldo. Código 1 si alguno no se pudo."""
    manifiesto = _nucleo.leer_manifiesto(RAIZ)
    if manifiesto is None:
        sys.exit("Esta carpeta no tiene catastro del núcleo instalado: no hay un original contra el cual restaurar.")
    local = _nucleo.ruta_larga(RAIZ)
    base_respaldo = local / ".harness" / "respaldo-nucleo" / datetime.now().strftime("%Y-%m-%d_%H%M%S")
    respaldo, n = base_respaldo, 1
    while respaldo.exists():
        n += 1
        respaldo = base_respaldo.with_name(f"{base_respaldo.name}_{n}")
    sin_resolver = 0
    with tempfile.TemporaryDirectory(prefix="pmo-nucleo-") as tmp:
        fuente = obtener_fuente(desde, tmp) if desde else None
        for pedido in pedidos:
            rel = pedido.replace("\\", "/")
            if Path(pedido).is_absolute():
                try:
                    rel = Path(pedido).resolve().relative_to(RAIZ.resolve()).as_posix()
                except ValueError:
                    pass
            elif rel.startswith("./"):
                rel = rel[2:]
            if rel not in manifiesto:
                print(f"- {rel}: no es un archivo del núcleo instalado (si es tuyo, no hay nada que restaurar).")
                continue
            destino = local / rel
            if destino.exists() and _nucleo.huella(destino) == manifiesto[rel]:
                print(f"- {rel}: ya está como se instaló.")
                continue
            datos = original_en_historial(rel, manifiesto[rel])
            if datos is None and fuente is not None and (fuente / rel).is_file() and _nucleo.huella(fuente / rel) == manifiesto[rel]:
                datos = (fuente / rel).read_bytes()
            if datos is None:
                sin_resolver += 1
                print(f"- {rel}: no encontré su original en el historial de Git de esta carpeta"
                      + (" ni en el origen indicado" if desde else "") + ". Indica de dónde traerlo con --desde <repositorio o "
                      "carpeta del núcleo en esta misma versión>, o actualiza el núcleo.")
                continue
            habia = destino.exists()
            if habia:
                (respaldo / rel).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(destino, respaldo / rel)
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_bytes(datos)
            print(f"- {rel}: restaurado a su original" + (f" (lo que había quedó en {respaldo.relative_to(local).as_posix()}/)." if habia else "."))
    return 1 if sin_resolver else 0


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
         "conservados": [], "choques": [], "nuevos": nuevos, "union": union, "manifiesto": manifiesto is not None}
    for rel, h in nuevos.items():
        if rel not in locales:
            p["agregar"].append(rel)
        elif locales[rel] == h:
            p["iguales"] += 1
        elif manifiesto is not None and rel not in manifiesto:
            p["choques"].append(rel)       # propio de la empresa con el nombre de algo nuevo del núcleo: no se pisa
        elif manifiesto and manifiesto[rel] == h:
            p["conservados"].append(rel)   # lo modificó la empresa y el núcleo nuevo no lo cambia: queda como está
        else:
            p["reemplazar"].append(rel)
            if manifiesto and manifiesto[rel] != locales[rel]:
                p["modificados"].append(rel)
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
    # Con cambios del usuario (o sin registro de lo instalado), estos archivos se fusionan en vez de reemplazarse
    p["fusionar"] = [x for x in (SETTINGS,) + POR_LINEAS if x in p["reemplazar"] and (x in p["modificados"] or manifiesto is None)]
    p["settings_invalido"] = False
    if SETTINGS in p["fusionar"]:  # un settings.json que no se puede leer no se puede fusionar: se dice con todas sus letras
        try:
            json.loads((RAIZ / SETTINGS).read_text(encoding="utf-8"))
        except (ValueError, OSError):
            p["fusionar"].remove(SETTINGS)
            p["settings_invalido"] = True
    p["modificados"] = [x for x in p["modificados"] if x not in p["fusionar"]]
    p["renombres"] = renombres_por_choque(p["choques"], manifiesto)
    movidas = tuple(o + "/" for o, _ in p["renombres"] if o not in p["choques"])
    p["propios"] = [x for x in p["propios"] if not x.startswith(movidas)] if movidas else p["propios"]
    p["archivo_propio"] = lambda r: (RAIZ / r).is_file() and r not in nuevos and (manifiesto is None or r not in manifiesto)
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
            if "estrategia" in arqs and (RAIZ / "herramientas" / "estrategia.py").exists():
                comandos.append(["estrategia.py"])
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
    ap.add_argument("--verificar", action="store_true", help="comparar el núcleo de esta carpeta con el catastro de lo instalado")
    ap.add_argument("--restaurar", nargs="+", metavar="ARCHIVO", help="devolver archivos del núcleo a su original instalado")
    a = ap.parse_args()
    global RAIZ
    if a.carpeta:
        RAIZ = Path(a.carpeta).resolve()

    if _nucleo.es_mantenedor(RAIZ):
        sys.exit("Esta carpeta es el núcleo que mantienes: se actualiza con Git (git pull / git push), no con este comando.")
    if a.verificar:
        return verificar()
    if a.restaurar:
        return restaurar(a.restaurar, a.desde)
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
        propias = _nucleo.pruebas_propias(RAIZ)
        out = ["# Actualización del núcleo", "", f"- Origen: {origen}", f"- Versión: {v_local or '?'} → {v_nueva or '?'}",
               f"- Archivos: {len(p['agregar']) + len(p['choques'])} nuevos · {len(p['reemplazar'])} cambiados · "
               f"{len(p['eliminar'])} eliminados · {p['iguales']} iguales",
               "", "## Lo tuyo en esta actualización (nada se pierde)", "", f"- No se tocan: {', '.join(NUNCA)}"]
        out += lista("Cambian de nombre para no chocar con algo nuevo del núcleo (lo tuyo queda entero; lo del núcleo entra con "
                     "el nombre original)", [f"{o} → {d}" for o, d in p["renombres"]])
        out += lista("Se conservan como los dejaste (los modificaste y el núcleo nuevo no los cambia)", p["conservados"])
        out += lista("Se fusionan (entra lo del núcleo nuevo; lo que agregaste se conserva)", p["fusionar"])
        if p["settings_invalido"]:
            out += [f"- ATENCIÓN: tu {SETTINGS} no es un JSON válido (suele faltar una coma o una llave), así que no se puede "
                    "fusionar: se reemplaza por el del núcleo nuevo y el tuyo queda en el respaldo. Si lo corriges antes de "
                    "aplicar, se fusiona."]
        out += lista("Modificados a mano en esta carpeta (el núcleo nuevo también los cambia: se respaldan antes de "
                     "reemplazarlos)", p["modificados"])
        out += lista("Propios de la empresa dentro de carpetas del núcleo (se conservan)", p["propios"])
        out += lista("Se completa en empresa/ (solo lo que falta; nada existente cambia)", [d for _, d in faltantes])
        out += lista("Pruebas propias que se ejecutan antes y después (si una deja de pasar, se revierte)", propias)
        out += ["", "## Lo del núcleo", ""]
        out += lista("Nuevos", p["agregar"] + p["choques"]) + lista("Cambiados", p["reemplazar"]) + lista("Eliminados (el núcleo nuevo ya no los trae)", p["eliminar"])
        out += lista("Sin registro del núcleo instalado: no se borran, revísalos", p["revisar"])
        nov = _nucleo.novedades(fuente, v_local)
        if nov and v_nueva != v_local:
            lineas = nov.splitlines()
            out += ["", "## Novedades", "", *lineas[:60]] + (["", f"(… {len(lineas) - 60} líneas más en CHANGELOG.md)"] if len(lineas) > 60 else [])
        cambios = p["agregar"] or p["choques"] or p["reemplazar"] or p["eliminar"] or faltantes
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
        antes_ext = revisar_extensiones()

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

        movidos, nombres_skill = [], []

        def revertir():
            for rel in p["agregar"] + p["choques"]:
                (local / rel).unlink(missing_ok=True)
            for origen_r, destino_r in reversed(movidos):  # lo propio vuelve a su nombre original
                o, d = local / origen_r, local / destino_r
                if d.exists():
                    if o.is_dir():
                        shutil.rmtree(o, ignore_errors=True)  # solo quedaba lo que el núcleo nuevo había puesto ahí
                    shutil.move(str(d), str(o))
            for ruta_skill, texto_skill in nombres_skill:
                ruta_skill.write_text(texto_skill, encoding="utf-8")
            for x in respaldo.rglob("*"):
                if x.is_file():
                    destino = local / x.relative_to(respaldo)
                    destino.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(x, destino)

        for origen_r, destino_r in p["renombres"]:  # lo propio que choca de nombre se aparta entero antes de que entre lo nuevo
            (local / destino_r).parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(local / origen_r), str(local / destino_r))
            movidos.append((origen_r, destino_r))
            skill = local / origen_r / "SKILL.md"  # todavía no existe: es donde volverá si se revierte
            skill_movida = local / destino_r / "SKILL.md"
            if skill_movida.is_file():
                texto_skill = skill_movida.read_text(encoding="utf-8", errors="replace")
                nombres_skill.append((skill, texto_skill))
                skill_movida.write_text(re.sub(r"^name:.*$", f"name: {PurePosixPath(destino_r).name}", texto_skill, count=1,
                                               flags=re.M), encoding="utf-8")
        for rel in p["agregar"] + p["choques"] + p["reemplazar"]:
            (local / rel).parent.mkdir(parents=True, exist_ok=True)
            if rel in p["fusionar"]:
                viejo_txt = (local / rel).read_text(encoding="utf-8", errors="replace")
                nuevo_txt = (nueva / rel).read_text(encoding="utf-8", errors="replace")
                fusion = (fusionar_settings(viejo_txt, nuevo_txt, p["archivo_propio"]) if rel == SETTINGS
                          else fusionar_lineas(viejo_txt, nuevo_txt, por_paquete=rel == "requirements.txt"))
                if fusion is not None:
                    (local / rel).write_bytes(fusion.encode("utf-8"))
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

        if antes_ext:
            despues_ext = revisar_extensiones()
            rotas = sorted(k for k, ok in antes_ext.items() if ok and not despues_ext.get(k, False))
            if rotas:
                revertir()
                print("Con el núcleo nuevo, estas pruebas propias de la empresa dejarían de pasar: se revirtió la actualización. "
                      "Nada cambió.\n" + "\n".join(f"- {k}" for k in rotas)
                      + "\nUna extensión tuya usa algo del núcleo que cambió: ajústala (o avísale a quien mantiene el núcleo) y "
                        "vuelve a actualizar.")
                anotar_fallo(f"Actualizar a {v_nueva or '?'} rompe extensiones propias que funcionaban: se revirtió", "; ".join(rotas)[:300])
                return 1
            print(f"Extensiones propias: {sum(1 for ok in despues_ext.values() if ok)} de {len(despues_ext)} prueba(s) pasan, "
                  "igual o mejor que antes.")

        if not a.sin_pruebas:
            print("Ejecutando la batería de pruebas...")
            r = subprocess.run([sys.executable, "pruebas/ejecutar_pruebas.py", "--sin-propias"], cwd=RAIZ, capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=1800)
            salida_p = ((r.stdout or "") + (r.stderr or "")).strip().splitlines()
            ultima = salida_p[-1:] or ["sin salida"]
            if r.returncode != 0:
                revertir()
                fallas = [l[6:].strip() for l in salida_p if l.startswith("FALLA ")]
                print(f"Las pruebas fallaron ({ultima[0]}): se revirtió la actualización. Nada cambió.\n"
                      + "".join(f"- {x}\n" for x in fallas[:6]) + (f"- … y {len(fallas) - 6} más\n" if len(fallas) > 6 else "")
                      + ("Puede deberse a archivos del núcleo que se modificaron en esta carpeta y se conservan: "
                         + ", ".join(p["conservados"][:8]) + ". Lleva ese ajuste a empresa/extensiones/ y repite.\n" if p["conservados"] else "")
                      + "Avísale a quien mantiene el núcleo; el detalle sale con: python pruebas/ejecutar_pruebas.py")
                anotar_fallo(f"La batería falla tras actualizar a {v_nueva or '?'}: se revirtió",
                             (ultima[0] + " · " + "; ".join(fallas))[:300])
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

        respaldo_rel = respaldo.relative_to(local).as_posix()
        if p["modificados"]:  # antes del commit, para que el recordatorio viaje con la actualización
            anotar_reemplazados(p["modificados"], respaldo_rel)

        rc, top = git("rev-parse", "--show-toplevel")
        if not a.sin_commit and rc == 0 and Path(top).resolve() == RAIZ.resolve():
            rutas_git = ([e.rstrip("/") for e in p["union"]] + [".harness/estado.yaml", _nucleo.MANIFIESTO.as_posix(),
                          ".harness/mejoras-nucleo.csv"] + [r for r, _ in completados])
            git("add", "-A", "--", *[x for x in rutas_git if (RAIZ / x).exists() or any(r.startswith(x) for r in p["eliminar"])])
            git("update-index", "--chmod=+x", *[e for e in _nucleo.EJECUTABLES if (RAIZ / e).exists()])
            rc_c, salida = git("commit", "-q", "-m", f"Actualización del núcleo a {v_nueva or 'la versión nueva'}")
            print("Commit: «Actualización del núcleo" + (f" a {v_nueva}»" if v_nueva else "»") if rc_c == 0
                  else f"No se hizo el commit: {salida[:400]}")
        if p["settings_invalido"]:
            print(f"Tu {SETTINGS} no era un JSON válido y no se pudo fusionar: quedó el del núcleo nuevo y el tuyo está en "
                  f"{respaldo_rel}/{SETTINGS}. Copia de ahí tus permisos y hooks propios.")
        if p["renombres"]:
            print("Cambiaron de nombre para no chocar con algo nuevo del núcleo (están enteros): "
                  + "; ".join(f"{o} → {d}" for o, d in p["renombres"])
                  + ". Si un hook o un permiso tuyo apuntaba al nombre anterior, actualízalo.")
        if p["modificados"]:
            print("Estos archivos del núcleo estaban modificados a mano y el núcleo nuevo también los cambia: quedó la versión "
                  f"nueva y la tuya está en {respaldo_rel}/: " + ", ".join(p["modificados"][:8])
                  + (f" y {len(p['modificados']) - 8} más" if len(p["modificados"]) > 8 else "")
                  + ". Lo propio va en empresa/ (extensiones, estilo) o en el proyecto; lo que el núcleo debería traer, con "
                    "mejoras.py --anotar (quedó anotado un recordatorio).")
    return 0


if __name__ == "__main__":
    import _consola
    _consola.preparar()
    sys.exit(main())
