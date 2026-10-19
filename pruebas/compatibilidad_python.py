#!/usr/bin/env python3
"""Detecta f-strings que solo funcionan en Python 3.12+ (comillas iguales anidadas o barra invertida
dentro de la expresión), para que los scripts corran en Python 3.9–3.11. Requiere ejecutarse con 3.12+."""
import sys
import tokenize
from pathlib import Path


def revisar(ruta):
    problemas = []
    pila = []  # (comilla, profundidad_llaves)
    with open(ruta, "rb") as f:
        toks = list(tokenize.tokenize(f.readline))
    for t in toks:
        nombre = tokenize.tok_name[t.type]
        if nombre == "FSTRING_START":
            comilla = t.string.lstrip("rfRFbB")[:1]
            if pila and pila[-1][1] > 0 and comilla == pila[-1][0]:
                problemas.append((t.start[0], "f-string anidada con la misma comilla"))
            pila.append([comilla, 0])
        elif nombre == "FSTRING_END" and pila:
            pila.pop()
        elif pila and nombre == "OP" and t.string == "{":
            pila[-1][1] += 1
        elif pila and nombre == "OP" and t.string == "}":
            pila[-1][1] = max(0, pila[-1][1] - 1)
        elif pila and pila[-1][1] > 0 and nombre == "STRING":
            if t.string.lstrip("rbuRBU")[:1] == pila[-1][0]:
                problemas.append((t.start[0], "comillas iguales dentro de la expresión de una f-string"))
            if "\\" in t.string:
                problemas.append((t.start[0], "barra invertida dentro de la expresión de una f-string"))
    return problemas


def main():
    if sys.version_info < (3, 12):
        print("Omitido: este chequeo requiere Python 3.12+ para tokenizar f-strings.")
        return 0
    raiz = Path(__file__).resolve().parent.parent
    archivos = list((raiz / "herramientas").rglob("*.py")) + list((raiz / "ejemplos").glob("*/scripts/*.py")) + list((raiz / "pruebas").glob("*.py"))
    malos = 0
    for f in archivos:
        for linea, motivo in revisar(f):
            print(f"{f.relative_to(raiz)}:{linea}: {motivo}")
            malos += 1
    print(f"Compatibilidad Python 3.9+: {'OK' if not malos else str(malos) + ' problema(s)'}")
    return 1 if malos else 0


if __name__ == "__main__":
    sys.exit(main())
