#!/usr/bin/env python3
"""Guía del usuario para un proyecto: qué es, cómo se organiza, rutina, reportes, qué pedir y controles automáticos.

Uso:
    python herramientas/guia_proyecto.py proyectos/<slug> [--no-escribir]
    python herramientas/guia_proyecto.py --general

Escribe `proyectos/<slug>/GUIA.md` (salvo --no-escribir) y la imprime. Toma los arquetipos del proyecto, los reportes
de su catálogo y el catálogo de skills de `.claude/skills/ayuda/catalogo.yaml`. Con --general muestra la guía sin
proyecto (instalación y creación de proyectos). La regenera la skill ayuda, instalar y nuevo-proyecto.
"""
import argparse
import re
import sys
from pathlib import Path

import yaml

import _config  # noqa: E402  (proyecto.yaml con herencia de programa)

RAIZ = Path(__file__).resolve().parent.parent
CATALOGO = RAIZ / ".claude" / "skills" / "ayuda" / "catalogo.yaml"


def frontmatter(ruta):
    m = re.match(r"^---\s*\n(.*?)\n---", ruta.read_text(encoding="utf-8", errors="replace"), re.S)
    try:
        return (yaml.safe_load(m.group(1)) or {}) if m else {}
    except yaml.YAMLError:
        return {}


def tabla_skills(skills):
    out = ["| Para qué | Puedes decirlo así | Skill |", "|---|---|---|"]
    for s in skills:
        ej = " · ".join(f"«{e}»" for e in s.get("ejemplos", [])[:3])
        out.append(f"| {s.get('para')} | {ej} | `{s.get('id')}` |")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("proyecto", nargs="?")
    ap.add_argument("--general", action="store_true")
    ap.add_argument("--no-escribir", action="store_true")
    a = ap.parse_args()
    cat = yaml.safe_load(CATALOGO.read_text(encoding="utf-8")) or {}
    skills = cat.get("skills") or []
    arq_info = cat.get("arquetipos") or {}

    if a.general or not a.proyecto:
        out = ["# PMO Harness: guía rápida", "",
               "Trabajas conversando: describe lo que necesitas con tus palabras. Los nombres de las skills son solo referencia.", "",
               "## Para empezar", ""] + tabla_skills([s for s in skills if not s.get("arquetipos")]) + [
               "", "## Tipos de proyecto disponibles", "", "| Tipo | Para qué sirve |", "|---|---|"]
        out += [f"| {v.get('nombre')} (`{k}`) | {v.get('que_es')} |" for k, v in arq_info.items()]
        out += ["", "## Útiles en cualquier proyecto", ""] + tabla_skills([s for s in skills if "todos" in (s.get("arquetipos") or [])])
        print("\n".join(out))
        return

    raiz = Path(a.proyecto)
    if not (raiz / "proyecto.yaml").exists():
        sys.exit(f"No encuentro {raiz / 'proyecto.yaml'}")
    cfg = _config.cargar(raiz)
    arqs = cfg.get("arquetipos") or []
    proy = cfg.get("proyecto") or {}
    nombre = proy.get("nombre", raiz.name)

    out = [f"# Guía del proyecto: {nombre}", "",
           "Trabajas conversando: describe lo que necesitas con tus palabras. No hace falta usar el nombre exacto de la",
           "skill; los ejemplos muestran cómo pedirlo. Para volver a ver esta guía: «¿qué puedo hacer?».", "",
           "## Qué tipo de proyecto es", ""]
    for x in arqs:
        info = arq_info.get(x, {})
        out.append(f"- **{info.get('nombre', x)}** (`{x}`): {info.get('que_es', '')}")
    if (proy.get("descripcion") or "") and "PENDIENTE" not in str(proy.get("descripcion")):
        out += ["", f"En una frase: {proy.get('descripcion')}"]
    if cfg.get("_programa"):
        out += ["", f"**Es un subproyecto del programa «{cfg['_programa'].get('nombre')}».** Aquí gestionas lo propio del "
                "subproyecto (Gantt, riesgos, minutas, reportes, objetivos). El contrato, las enmiendas, el presupuesto, la "
                "contingencia y las personas se gestionan en el programa; lo que este subproyecto no define (marca, formatos, "
                "plantillas) lo hereda del programa."]
    lista_sub = raiz / "programa" / "subproyectos.csv"
    if lista_sub.exists():
        import csv as _csv
        with open(lista_sub, encoding="utf-8-sig", newline="") as fh:
            subs = list(_csv.DictReader(fh))
        out += ["", "## Subproyectos del programa", "", "| Id | Subproyecto | Carpeta | Responsable |", "|---|---|---|---|"]
        out += [f"| {s.get('id')} | {s.get('nombre')} | `{s.get('carpeta')}` | {s.get('responsable') or '—'} |" for s in subs] or ["| — | (ninguno aún) | | |"]
        out += ["", "Para trabajar en uno, nómbralo («actualiza el Gantt del sp2»). Para uno nuevo: «agrega un subproyecto al programa»."]

    out += ["", "## Dónde está cada cosa", "",
            "- `proyecto.yaml`: configuración (identidad, gobierno, formato, umbrales, autoría).",
            "- `CLAUDE.md`: reglas propias del proyecto · `contexto/`: alcance, interesados, glosario, estilo.",
            "- `_entrada/`: aquí dejas documentos nuevos (no se suben a GitHub).",
            "- `riesgos/` · `seguimiento/` (acuerdos, decisiones, notas semanales) · `minutas/` · `metricas/` · `reportes/`."]
    for x in arqs:
        out += [f"- {c}" for c in arq_info.get(x, {}).get("carpetas", [])]

    out += ["", "## Rutina recomendada", ""]
    for x in arqs:
        out += [f"- {r}" for r in arq_info.get(x, {}).get("rutina", [])]
    out.append("- Al terminar una sesión de trabajo: «guarda» (sube los cambios a GitHub de forma segura).")

    reportes = sorted(p for p in (raiz / "reportes" / "catalogo").glob("*.md") if not p.name.startswith("_"))
    out += ["", "## Reportes configurados", ""]
    if reportes:
        out += ["| Reporte | Formato | Cadencia | Destinatarios |", "|---|---|---|---|"]
        for r in reportes:
            fm = frontmatter(r)
            dest = ", ".join(str(d) for d in (fm.get("destinatarios") or [])) or "por definir"
            out.append(f"| {fm.get('nombre', r.stem)} | {fm.get('formato', '')} | {fm.get('cadencia', '')} | {dest} |")
        out.append("")
        out.append("Pídelo por su nombre o describiéndolo («prepara el reporte de esta semana»).")
    else:
        out.append("- Aún no hay reportes: «quiero un reporte mensual para…» crea uno.")

    propias = [s for s in skills if any(x in (s.get("arquetipos") or []) for x in arqs)]
    comunes = [s for s in skills if "todos" in (s.get("arquetipos") or [])]
    out += ["", "## Lo específico de este tipo de proyecto", ""] + tabla_skills(propias)
    out += ["", "## Útil en cualquier proyecto", ""] + tabla_skills(comunes)

    out += ["", "## Controles automáticos", "", "| Control | Qué hace | Si bloquea algo |", "|---|---|---|"]
    out += [f"| {h.get('nombre')} | {h.get('que_hace')} | {h.get('si_bloquea')} |" for h in cat.get("hooks") or []]
    out += ["", "## Reglas que conviene saber", "",
            "- Los datos del proyecto (`.yaml`, `.csv`, `.md`) son la fuente de verdad; Word, Excel y PowerPoint son salidas.",
            "- Nada se inventa: lo que falta queda marcado como pendiente y se te avisa.",
            "- Los documentos que se entregan salen a tu nombre y se verifican antes de entregarlos.",
            "- Las decisiones (técnicas, legales, de inversión, declaraciones) son tuyas; el harness organiza, mide y alerta."]
    texto = "\n".join(out) + "\n"
    if not a.no_escribir:
        (raiz / "GUIA.md").write_text(texto, encoding="utf-8")
    print(texto)


if __name__ == "__main__":
    import _consola
    _consola.preparar()
    main()
