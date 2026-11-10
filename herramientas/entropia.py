#!/usr/bin/env python3
"""Recolector de entropía: lo que crece en el harness sin que nadie lo retire. Propone; nunca borra solo.

Uso:
    python herramientas/entropia.py [--informe] [--techo] [--hoy AAAA-MM-DD]

Revisa:
1. Contexto fijo real por sesión: AGENTS.md + puerta de entrada + las descripciones de todas las skills y subagentes
   (Claude Code las carga en toda sesión, aunque la skill no se use) contra el presupuesto PRESUPUESTO_REAL.
2. Instrucciones repetidas: párrafos iguales en README, MANUAL-DE-USUARIO, EMPEZAR-AQUI, GUIA y NUBE (deriva segura:
   un día se corrige uno y el otro queda viejo).
3. Memoria sin revisar: lecciones de la empresa de más de 180 días que nadie confirmó ni descartó.
4. `[PENDIENTE` de más de 30 días en proyectos/ y empresa/.
5. Respaldos de actualización acumulados en .harness/respaldo-nucleo/ (más de 2).
6. Mejoras al núcleo anotadas hace más de 30 días y nunca enviadas.
7. Skills sin uso en 90 días, si existe el registro de uso (.harness/uso-skills.csv, lo escribe un hook de Claude Code).

Con --informe guarda el resultado en .harness/entropia-<fecha>.md. Con --techo termina con código 1 si el contexto
fijo real supera el presupuesto (lo usa la batería para que el núcleo no crezca sin que se note). Siempre deja la
fecha en .harness/entropia-ultima.txt: el estado de inicio avisa cuando pasaron más de 30 días sin revisar.
"""
import argparse
import csv
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import _nucleo
import medir_contexto

RAIZ = Path(__file__).resolve().parent.parent
PRESUPUESTO_REAL = 12500   # tokens aprox.: AGENTS.md + CLAUDE.md + descripciones de skills y subagentes (2.7: congelar en ~12.200; 3.0: 7000)
DOCS = ["README.md", "MANUAL-DE-USUARIO.md", "EMPEZAR-AQUI.md", "GUIA.md", "NUBE.md"]
DIAS_LECCION, DIAS_PENDIENTE, DIAS_MEJORA, DIAS_SKILL, RESPALDOS_MAX = 180, 30, 30, 90, 2


def descripcion(ruta):
    """Texto del campo description del frontmatter (lo que carga la sesión)."""
    try:
        texto = ruta.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    partes = texto.split("---")
    m = re.search(r"^description:\s*(.+)$", partes[1] if len(partes) > 2 else texto, re.M | re.S)
    if not m:
        return ""
    return m.group(1).split("\n---")[0].strip()


def contexto_real(raiz):
    """[(parte, tokens)] del contexto fijo real y el total."""
    partes = [("AGENTS.md", medir_contexto.tokens(raiz / "AGENTS.md")), ("CLAUDE.md", medir_contexto.tokens(raiz / "CLAUDE.md"))]
    skills = sorted((raiz / ".claude" / "skills").glob("*/SKILL.md"))
    agentes = sorted((raiz / ".claude" / "agents").glob("*.md"))
    partes.append((f"descripciones de {len(skills)} skills", sum(len(descripcion(s)) // 4 for s in skills)))
    partes.append((f"descripciones de {len(agentes)} subagentes", sum(len(descripcion(a)) // 4 for a in agentes)))
    return partes, sum(t for _, t in partes)


def parrafos(ruta):
    texto = ruta.read_text(encoding="utf-8", errors="replace")
    salida = []
    for bloque in re.split(r"\n\s*\n", texto):
        b = bloque.strip()
        if b.startswith(("#", "|", "```", "<!--", "- ", "* ", "1.")) or len(b.split()) < 25:
            continue
        salida.append((re.sub(r"\s+", " ", b).lower(), b[:90].replace("\n", " ")))
    return salida


def repetidos(raiz):
    vistos, hallazgos = {}, []
    for nombre in DOCS:
        ruta = raiz / nombre
        if not ruta.exists():
            continue
        for clave, muestra in parrafos(ruta):
            if clave in vistos and vistos[clave][0] != nombre:
                hallazgos.append((vistos[clave][0], nombre, muestra))
            else:
                vistos.setdefault(clave, (nombre, muestra))
    return hallazgos


def lecciones_viejas(raiz, hoy):
    ruta = raiz / "empresa" / "investigacion" / "lecciones.csv"
    if not ruta.exists():
        return []
    limite = hoy - timedelta(days=DIAS_LECCION)
    viejas = []
    with open(ruta, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            try:
                fecha = date.fromisoformat((r.get("fecha") or "")[:10])
            except ValueError:
                continue
            if fecha <= limite and (r.get("estado") or "") not in ("confirmada", "descartada", "retirada"):
                viejas.append(f"{r.get('id')} ({r.get('fecha')}): {(r.get('leccion') or '')[:80]}")
    return viejas


def pendientes_viejos(raiz, hoy):
    limite = (datetime.combine(hoy, datetime.min.time()) - timedelta(days=DIAS_PENDIENTE)).timestamp()
    salida = []
    for base in ("proyectos", "empresa"):
        carpeta = raiz / base
        if not carpeta.exists():
            continue
        for x in _nucleo.ruta_larga(carpeta).rglob("*.md"):
            if "_entrada" in x.parts or "_procesado" in x.parts or x.name == "LEEME.md":
                continue
            try:
                if x.stat().st_mtime > limite:
                    continue
                n = x.read_text(encoding="utf-8", errors="replace").count("[PENDIENTE")
            except OSError:
                continue
            if n:
                salida.append(f"{x.parent.name}/{x.name}: {n} marcador(es), sin tocar desde "
                              f"{datetime.fromtimestamp(x.stat().st_mtime).date().isoformat()}")
    return salida


def respaldos(raiz):
    carpeta = raiz / ".harness" / "respaldo-nucleo"
    return sorted(x.name for x in carpeta.iterdir() if x.is_dir()) if carpeta.exists() else []


def mejoras_olvidadas(raiz, hoy):
    ruta = raiz / ".harness" / "mejoras-nucleo.csv"
    if not ruta.exists():
        return []
    limite = hoy - timedelta(days=DIAS_MEJORA)
    with open(ruta, encoding="utf-8", newline="") as f:
        return [f"{r.get('id')} ({r.get('fecha')}): {(r.get('que') or '')[:70]}" for r in csv.DictReader(f)
                if r.get("estado") == "nueva" and (r.get("fecha") or "9999") <= limite.isoformat()]


def skills_sin_uso(raiz, hoy):
    registro = raiz / ".harness" / "uso-skills.csv"
    if not registro.exists():
        return None
    limite = (hoy - timedelta(days=DIAS_SKILL)).isoformat()
    usadas = set()
    with open(registro, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if (r.get("fecha") or "") >= limite:
                usadas.add(r.get("skill") or "")
    todas = sorted(d.name for d in (raiz / ".claude" / "skills").iterdir() if (d / "SKILL.md").exists())
    return [s for s in todas if s not in usadas]


def informe(raiz, hoy):
    partes, total = contexto_real(raiz)
    out = ["# Entropía del harness", "", f"Revisión del {hoy.isoformat()} · núcleo {_nucleo.version(raiz) or '?'}. Propone; no borra nada.", ""]
    out += ["## 1. Contexto fijo real por sesión", ""]
    out += [f"- {n}: ~{t}" for n, t in partes]
    estado = "bajo el presupuesto" if total <= PRESUPUESTO_REAL else "SUPERADO: recorta antes de agregar"
    out += [f"- **Total: ~{total}** (presupuesto {PRESUPUESTO_REAL}: {estado}). `medir_contexto.py` mide solo AGENTS.md y la puerta; "
            "las descripciones de skills y subagentes también se cargan en cada sesión.", ""]
    rep = repetidos(raiz)
    out += ["## 2. Instrucciones repetidas entre documentos", ""]
    out += ([f"- {a} y {b}: «{m}…»" for a, b, m in rep[:15]] + ([f"- … y {len(rep) - 15} más"] if len(rep) > 15 else [])
            + ["", f"Propuesta: dejar cada explicación en un solo documento y enlazarla desde los demás ({len(rep)} repetición(es))."]
            if rep else ["- Ninguna."])
    out.append("")
    lecc = lecciones_viejas(raiz, hoy)
    out += ["## 3. Memoria sin revisar", ""]
    out += ([f"- {x}" for x in lecc] + ["", f"Propuesta: confirmar (`estado: confirmada`) o descartar cada lección de más de {DIAS_LECCION} días; "
            "una memoria vieja puede repetir un error."] if lecc else ["- Ninguna lección de empresa vencida."])
    out.append("")
    pend = pendientes_viejos(raiz, hoy)
    out += [f"## 4. `[PENDIENTE` de más de {DIAS_PENDIENTE} días", ""]
    out += ([f"- {x}" for x in pend] + ["", "Propuesta: resolverlos o convertirlos en decisiones pendientes del usuario en el traspaso."]
            if pend else ["- Ninguno."])
    out.append("")
    resp = respaldos(raiz)
    out += ["## 5. Respaldos de actualización", ""]
    out += ([f"- {len(resp)} carpeta(s) en .harness/respaldo-nucleo/ ({', '.join(resp[:4])}{'…' if len(resp) > 4 else ''}).", "",
             f"Propuesta: conservar las {RESPALDOS_MAX} más recientes y borrar el resto (no se suben a Git; solo sirven para revertir la última actualización)."]
            if len(resp) > RESPALDOS_MAX else [f"- {len(resp)} carpeta(s): sin exceso."])
    out.append("")
    mej = mejoras_olvidadas(raiz, hoy)
    out += [f"## 6. Mejoras al núcleo sin enviar hace más de {DIAS_MEJORA} días", ""]
    out += ([f"- {x}" for x in mej] + ["", "Propuesta: `python herramientas/mejoras.py --exportar` y entregar el archivo al mantenedor."] if mej else ["- Ninguna."])
    out.append("")
    sin_uso = skills_sin_uso(raiz, hoy)
    out += [f"## 7. Skills sin uso en {DIAS_SKILL} días", ""]
    if sin_uso is None:
        out += ["- Sin registro de uso (.harness/uso-skills.csv): lo escribe el hook `registrar_uso.py` de Claude Code; con otras IA no hay dato."]
    elif sin_uso:
        out += [f"- {len(sin_uso)}: {', '.join(sin_uso)}", "",
                "Propuesta: candidatas a fusionarse o retirarse en la próxima versión mayor (anótalo con `mejoras.py --anotar --tipo quitar`)."]
    else:
        out += ["- Todas se usaron."]
    out.append("")
    n = len(rep) + len(lecc) + len(pend) + len(mej) + (len(sin_uso) if sin_uso else 0) + (1 if len(resp) > RESPALDOS_MAX else 0) + (1 if total > PRESUPUESTO_REAL else 0)
    out.append(f"**{n} propuesta(s).** Nada se borró." if n else "**Nada que retirar.**")
    return "\n".join(out), total


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--informe", action="store_true", help="guardar el informe en .harness/entropia-<fecha>.md")
    ap.add_argument("--techo", action="store_true", help="código 1 si el contexto fijo real supera el presupuesto")
    ap.add_argument("--hoy")
    a = ap.parse_args()
    hoy = date.fromisoformat(a.hoy) if a.hoy else date.today()
    texto, total = informe(RAIZ, hoy)
    print(texto)
    harness = RAIZ / ".harness"
    if harness.exists():
        (harness / "entropia-ultima.txt").write_text(hoy.isoformat() + "\n", encoding="utf-8")
        if a.informe:
            ruta = harness / f"entropia-{hoy.isoformat()}.md"
            ruta.write_text(texto + "\n", encoding="utf-8")
            print(f"\nInforme guardado en {ruta.relative_to(RAIZ).as_posix()}")
    return 1 if a.techo and total > PRESUPUESTO_REAL else 0


if __name__ == "__main__":
    import _consola
    _consola.preparar()
    sys.exit(main())
