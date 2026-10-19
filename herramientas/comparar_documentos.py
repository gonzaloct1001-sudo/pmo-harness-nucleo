#!/usr/bin/env python3
"""Compara dos documentos (o dos versiones del mismo) y lista las diferencias.

Uso:
    python herramientas/comparar_documentos.py <anterior> <nuevo> [--salida cambios.md] [--max 80]

Acepta PDF, Word, Excel, PowerPoint, correos .eml, Markdown, texto y CSV (reutiliza los extractores de
extraer_entrada.py). Entrega: similitud global, cantidad de cambios y cada cambio con el texto anterior y
el nuevo, marcando palabra a palabra lo que cambió ([-quitado-] {+agregado+}). Destaca como POSIBLE
CAMBIO SUSTANTIVO los cambios que alteran cifras, fechas, montos, porcentajes o palabras de obligación
(plazo, multa, deberá, no podrá, garantía…). La clasificación final la hace el asistente o el usuario.
"""
import argparse
import difflib
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import extraer_entrada as ex  # noqa: E402

CLAVES = re.compile(r"\b(plazo|monto|precio|multa|garant[ií]a|deber[áa]|no podr[áa]|obligaci[oó]n|alcance|"
                    r"responsab|exclu|penalidad|vigencia|t[eé]rmino|pago|hito|reajuste|indemniz|confidencial)", re.I)
CIFRA = re.compile(r"\d[\d.,]*\s*%?|\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b")


def texto_de(ruta: Path) -> str:
    ext = ruta.suffix.lower()
    if ext in ex.EXTRACTORES:
        fn = ex.EXTRACTORES[ext]
        tmp = Path("/tmp") if Path("/tmp").exists() else ruta.parent
        texto, _ = fn(ruta, tmp, 500) if fn is ex.ext_xlsx else fn(ruta, tmp)
        return texto
    return ruta.read_text(encoding="utf-8", errors="replace")


def lineas(texto):
    out = []
    for l in texto.splitlines():
        l = re.sub(r"\s+", " ", l).strip()
        if l and not re.fullmatch(r"-+ Página \d+ -+", l):
            out.append(l)
    return out


def diff_palabras(a, b):
    wa, wb = a.split(), b.split()
    res = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, wa, wb).get_opcodes():
        if op == "equal":
            res.append(" ".join(wa[i1:i2]))
        if op in ("delete", "replace"):
            res.append("[-" + " ".join(wa[i1:i2]) + "-]")
        if op in ("insert", "replace"):
            res.append("{+" + " ".join(wb[j1:j2]) + "+}")
    return " ".join(res)


def sustantivo(antes, despues):
    motivos = []
    if sorted(CIFRA.findall(antes)) != sorted(CIFRA.findall(despues)):
        motivos.append("cifras/fechas")
    ca = {m.lower() for m in CLAVES.findall(antes)}
    cd = {m.lower() for m in CLAVES.findall(despues)}
    if (ca or cd) and (antes != despues):
        motivos.append("términos de obligación: " + ", ".join(sorted(ca | cd)))
    return motivos


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("anterior")
    ap.add_argument("nuevo")
    ap.add_argument("--salida")
    ap.add_argument("--max", type=int, default=80, help="máximo de cambios a detallar")
    a = ap.parse_args()
    pa, pn = Path(a.anterior), Path(a.nuevo)
    la, ln = lineas(texto_de(pa)), lineas(texto_de(pn))
    sm = difflib.SequenceMatcher(None, la, ln, autojunk=False)
    cambios = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            continue
        antes, despues = " ".join(la[i1:i2]), " ".join(ln[j1:j2])
        tipo = {"replace": "Modificado", "delete": "Eliminado", "insert": "Agregado"}[op]
        cambios.append((tipo, i1 + 1, j1 + 1, antes, despues, sustantivo(antes, despues)))

    n_sust = sum(1 for c in cambios if c[5])
    out = [f"# Comparación de documentos", "",
           f"- Anterior: `{pa.name}` ({len(la)} líneas)", f"- Nuevo: `{pn.name}` ({len(ln)} líneas)",
           f"- Similitud global: {sm.ratio():.0%}",
           f"- Cambios: {len(cambios)} (modificados {sum(c[0] == 'Modificado' for c in cambios)}, "
           f"agregados {sum(c[0] == 'Agregado' for c in cambios)}, eliminados {sum(c[0] == 'Eliminado' for c in cambios)})",
           f"- Posibles cambios sustantivos: {n_sust}", ""]
    orden = sorted(cambios, key=lambda c: (not c[5], c[1]))
    for k, (tipo, la_n, ln_n, antes, despues, mot) in enumerate(orden[: a.max], 1):
        marca = " — **POSIBLE CAMBIO SUSTANTIVO** (" + "; ".join(mot) + ")" if mot else ""
        out.append(f"## {k}. {tipo} (línea {la_n} → {ln_n}){marca}")
        if tipo == "Modificado":
            out += [f"- Antes: {antes[:600]}", f"- Después: {despues[:600]}", f"- Diferencia: {diff_palabras(antes, despues)[:900]}"]
        elif tipo == "Eliminado":
            out.append(f"- Texto eliminado: {antes[:900]}")
        else:
            out.append(f"- Texto agregado: {despues[:900]}")
        out.append("")
    if len(cambios) > a.max:
        out.append(f"… y {len(cambios) - a.max} cambios más (usar --max para ver todos).")
    texto = "\n".join(out) + "\n"
    if a.salida:
        Path(a.salida).parent.mkdir(parents=True, exist_ok=True)
        Path(a.salida).write_text(texto, encoding="utf-8")
    print(texto)


if __name__ == "__main__":
    import _consola
    _consola.preparar()
    main()
