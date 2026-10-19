#!/usr/bin/env python3
"""Verifica que los documentos entregables no tengan rastros del proceso de generación.

Uso:
    python herramientas/verificar_autoria.py <archivo|carpeta> [--proyecto proyectos/<slug>] [--corregir]

Revisa .docx, .xlsx, .pptx, .pdf, .md, .txt y .html:
- propiedades internas (autor, aplicación, comentarios, fecha de creación heredada de plantillas);
- partes ocultas del paquete (miniatura y customXml de plantillas, comentarios, control de cambios, texto oculto);
- términos que delatan herramientas o el proceso (lista fija + `autoria.terminos_prohibidos` del proyecto;
  `autoria.terminos_permitidos` exime los que sean tema legítimo, p. ej. "inteligencia artificial");
- marcadores internos ([PENDIENTE], comentarios HTML, rutas del repositorio, ids de inventario);
- caracteres invisibles (ancho cero, guion blando: error) o atípicos (espacios especiales, signo menos: advertencia);
- nombre del archivo.

Errores = rastros inequívocos del proceso (restos de conversación con un asistente, marcadores y rutas internas,
nombres de librerías). Advertencias = términos que pueden ser legítimos (nombres de herramientas o modelos de IA
cuando son el tema del proyecto, nombres propios, términos técnicos): se revisan y se eximen con
`autoria.terminos_permitidos`. Los documentos de terceros (cartas de socios, certificados) y las declaraciones que las
bases exigen (por ejemplo, declarar el uso de herramientas de IA) se listan en `autoria.excluir` (patrones de nombre):
no se verifican ni se modifican.

Con --corregir limpia lo que se puede limpiar sin cambiar el contenido: propiedades (autor = autoria.nombre o
responsable.nombre), partes heredadas, modo de compatibilidad y caracteres invisibles. Los términos y
marcadores no se corrigen solos: hay que editar el texto de origen y volver a generar.

Termina con código 0 si no hay errores y 1 si los hay (las advertencias no bloquean).
"""
import argparse
import sys
from pathlib import Path

import autoria

EXTENSIONES = {".docx", ".docm", ".xlsx", ".xlsm", ".pptx", ".pptm", ".pdf", ".md", ".txt", ".html"}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ruta", help="archivo o carpeta")
    ap.add_argument("--proyecto", help="carpeta del proyecto (autor y listas de términos)")
    ap.add_argument("--corregir", action="store_true", help="limpiar propiedades, partes heredadas y caracteres invisibles")
    a = ap.parse_args()

    ruta = Path(a.ruta)
    if not ruta.exists():
        sys.exit(f"No existe {ruta}")
    aut = autoria.cargar_autoria(a.proyecto)
    archivos = [ruta] if ruta.is_file() else sorted(p for p in ruta.rglob("*") if p.is_file() and p.suffix.lower() in EXTENSIONES)
    total_err = 0
    print(f"# Verificación de autoría — {ruta.as_posix()}\n")
    if not aut.get("nombre"):
        print("> Sin autor configurado (autoria.nombre o responsable.nombre en proyecto.yaml): las propiedades quedarán sin autor.\n")
    for f in archivos:
        if a.corregir and not autoria.excluido(f, aut):  # nunca se reescriben documentos de terceros ni declaraciones excluidas
            cambios = autoria.limpiar_ooxml(f, aut.get("nombre", ""), "", aut.get("organizacion", ""))
            if f.suffix.lower() in (".md", ".txt", ".html"):
                texto = f.read_text(encoding="utf-8", errors="replace")
                limpio = autoria.normalizar_texto(texto)
                if limpio != texto:
                    f.write_text(limpio, encoding="utf-8")
                    cambios.append("caracteres invisibles o atípicos normalizados")
            for c in cambios:
                print(f"- corregido en {f.name}: {c}")
        errores, advert = autoria.revisar_archivo(f, aut)
        total_err += len(errores)
        estado = "OK" if not errores else f"{len(errores)} error(es)"
        print(f"## {f.as_posix()} — {estado}" + (f", {len(advert)} advertencia(s)" if advert else ""))
        for e in errores:
            print(f"- ERROR: {e}")
        for w in advert:
            print(f"- revisar: {w}")
        print()
    print(f"Resultado: {'OK' if not total_err else 'CON ERRORES'} · archivos: {len(archivos)} · errores: {total_err}")
    return 0 if not total_err else 1


if __name__ == "__main__":
    import _consola
    _consola.preparar()
    sys.exit(main())
