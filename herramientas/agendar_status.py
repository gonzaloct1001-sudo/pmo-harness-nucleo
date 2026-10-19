#!/usr/bin/env python3
"""Agenda el reporte web de status para que se genere y se abra solo cada semana (Windows o Mac).

Uso:
    python herramientas/agendar_status.py --dia lunes --hora 09:00 [--panel <carpeta-panel>]
    python herramientas/agendar_status.py --ver          # muestra si hay una programación activa
    python herramientas/agendar_status.py --quitar       # elimina la programación
    python herramientas/agendar_status.py ... --simular  # muestra lo que haría, sin crear nada

Usa el programador del sistema (Programador de tareas en Windows; launchd en Mac): funciona aunque no haya ninguna
IA abierta. A la hora indicada, si el computador está encendido y con la sesión iniciada, genera el reporte web con
`status.py --formato html --abrir` y lo abre en el navegador. Es una programación de este computador: en otro
computador se agenda de nuevo. Crear o quitar la tarea pide confirmación al usuario (lo hace el asistente antes).
"""
import argparse
import plistlib
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

H = Path(__file__).resolve().parent
RAIZ = H.parent
DIAS = {"lunes": ("MON", 1), "martes": ("TUE", 2), "miercoles": ("WED", 3), "jueves": ("THU", 4), "viernes": ("FRI", 5),
        "sabado": ("SAT", 6), "domingo": ("SUN", 0)}


def sin_tildes(t):
    return unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()


def identificador(panel):
    base = Path(panel).resolve().name if panel else RAIZ.name
    return re.sub(r"[^a-z0-9]+", "-", sin_tildes(base)).strip("-") or "harness"


def comando(panel):
    args = [sys.executable, str(H / "status.py"), "--formato", "html", "--abrir"]
    if panel:
        args += ["--panel", str(Path(panel).resolve())]
    return args


def windows(accion, dia, hora, panel, simular):
    nombre = f"PMO Harness - status {identificador(panel)}"
    if accion == "ver":
        r = subprocess.run(["schtasks", "/Query", "/TN", nombre, "/FO", "LIST"], capture_output=True, text=True)
        print(r.stdout.strip() if r.returncode == 0 else "No hay una programación activa del status en este computador.")
        return 0
    if accion == "quitar":
        cmd = ["schtasks", "/Delete", "/TN", nombre, "/F"]
    else:
        # un .cmd en status/ evita el límite de largo del comando del Programador de tareas
        lanzador = (Path(panel).resolve() if panel else RAIZ / "status") / "abrir-status.cmd"
        contenido = "@echo off\r\ncd /d \"" + str(RAIZ) + "\"\r\n" + " ".join(f'"{a}"' if " " in a else a for a in comando(panel)) + "\r\n"
        cmd = ["schtasks", "/Create", "/F", "/SC", "WEEKLY", "/D", DIAS[dia][0], "/ST", hora, "/TN", nombre, "/TR", f'"{lanzador}"']
        if simular:
            print(f"Archivo {lanzador}:\n{contenido}")
        else:
            lanzador.parent.mkdir(parents=True, exist_ok=True)
            lanzador.write_text(contenido, encoding="utf-8")
    if simular:
        print("Comando: " + " ".join(cmd))
        return 0
    r = subprocess.run(cmd, capture_output=True, text=True)
    print((r.stdout or r.stderr).strip())
    return r.returncode


def mac(accion, dia, hora, panel, simular):
    etiqueta = f"cl.pmoharness.status.{identificador(panel)}"
    plist = Path.home() / "Library" / "LaunchAgents" / f"{etiqueta}.plist"
    if accion == "ver":
        print(f"Programación activa: {plist}" if plist.exists() else "No hay una programación activa del status en este computador.")
        return 0
    if accion == "quitar":
        if simular:
            print(f"Se eliminaría {plist}")
            return 0
        subprocess.run(["launchctl", "unload", str(plist)], capture_output=True)
        plist.unlink(missing_ok=True)
        print("Programación eliminada.")
        return 0
    hh, mm = (int(x) for x in hora.split(":"))
    datos = {"Label": etiqueta, "ProgramArguments": comando(panel), "WorkingDirectory": str(RAIZ),
             "StartCalendarInterval": {"Weekday": DIAS[dia][1], "Hour": hh, "Minute": mm}}
    if simular:
        print(f"Se crearía {plist} con:\n{plistlib.dumps(datos).decode()}")
        return 0
    plist.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["launchctl", "unload", str(plist)], capture_output=True)
    plist.write_bytes(plistlib.dumps(datos))
    r = subprocess.run(["launchctl", "load", "-w", str(plist)], capture_output=True, text=True)
    print("Programación creada." if r.returncode == 0 else (r.stderr or "No se pudo cargar la programación.").strip())
    return r.returncode


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dia", help="lunes, martes, miércoles, jueves, viernes, sábado o domingo")
    ap.add_argument("--hora", help="HH:MM (24 horas)")
    ap.add_argument("--panel", help="agendar el tablero único de un panel en vez del status de esta empresa")
    ap.add_argument("--ver", action="store_true")
    ap.add_argument("--quitar", action="store_true")
    ap.add_argument("--simular", action="store_true", help="mostrar lo que haría, sin crear nada")
    a = ap.parse_args()
    accion = "ver" if a.ver else ("quitar" if a.quitar else "crear")
    dia = sin_tildes(a.dia or "")
    if accion == "crear":
        if dia not in DIAS:
            sys.exit("Indica el día con --dia (lunes a domingo).")
        if not a.hora or not re.fullmatch(r"([01]?\d|2[0-3]):[0-5]\d", a.hora):
            sys.exit("Indica la hora con --hora HH:MM (24 horas), por ejemplo 09:00.")
        a.hora = f"{int(a.hora.split(':')[0]):02d}:{a.hora.split(':')[1]}"
    if sys.platform.startswith("win"):
        rc = windows(accion, dia, a.hora, a.panel, a.simular)
    elif sys.platform == "darwin":
        rc = mac(accion, dia, a.hora, a.panel, a.simular)
    else:
        sys.exit("Programación automática disponible en Windows y Mac. En Linux, agrega a cron: "
                 + " ".join(comando(a.panel)))
    if accion == "crear" and rc == 0 and not a.simular:
        print(f"Listo: cada {a.dia} a las {a.hora} se generará y abrirá el reporte de status (si el computador está encendido).")
    return rc


if __name__ == "__main__":
    import _consola
    _consola.preparar()
    sys.exit(main())
