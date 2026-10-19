#!/bin/bash
# Prepara un Mac para usar el PMO Harness: revisa e instala, con permiso del usuario, lo que falte.
#
# Uso:
#   Doble clic en INSTALAR-MAC.command               -> modo interactivo: pregunta S/N por cada cosa.
#   bash herramientas/preparar_pc.sh --solo-revisar  -> solo informa qué falta (no instala nada).
#   bash herramientas/preparar_pc.sh --instalar python,git,gh,libreoffice [--nombre-git "Nombre" --correo-git "correo"]
#                                                    -> instala lo indicado sin preguntar (lo usa el asistente de IA
#                                                       después de pedir permiso en el chat).
#   bash herramientas/preparar_pc.sh --iniciar-github -> abre una ventana de Terminal para iniciar sesión en GitHub
#                                                       (el asistente de IA lo usa porque su consola no es interactiva).
#   bash herramientas/preparar_pc.sh --clonar [--repos "a,b" | --repos todas] [--destino carpeta] [--propietario cuenta]
#                                                    -> descarga las carpetas de empresa (repositorios con el tema
#                                                       pmo-harness-empresa) para trabajar en este computador.
#
# Usa Homebrew (lo instala con permiso; pide la contraseña del Mac) para Python, Git, GitHub CLI y, opcionalmente,
# LibreOffice. Las librerías van en .venv/ dentro de la carpeta (el Python de Homebrew no admite instalar paquetes
# globales). Activa el control de Git (core.hooksPath) y termina con herramientas/verificar_entorno.py.
# No instala VS Code ni el asistente de IA. Compatible con el bash 3.2 que trae macOS.

RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
SOLO_REVISAR=0; CLONAR=0; INICIAR_GITHUB=0; INSTALAR=""; NOMBRE_GIT=""; CORREO_GIT=""; REPOS=""; DESTINO=""; PROPIETARIO=""
while [ $# -gt 0 ]; do
  case "$1" in
    --solo-revisar) SOLO_REVISAR=1 ;;
    --instalar) INSTALAR="$2"; shift ;;
    --nombre-git) NOMBRE_GIT="$2"; shift ;;
    --correo-git) CORREO_GIT="$2"; shift ;;
    --clonar) CLONAR=1 ;;
    --iniciar-github) INICIAR_GITHUB=1 ;;
    --repos) REPOS="$2"; shift ;;
    --destino) DESTINO="$2"; shift ;;
    --propietario) PROPIETARIO="$2"; shift ;;
    *) echo "Opción desconocida: $1"; exit 2 ;;
  esac
  shift
done
INTERACTIVO=0
if [ $SOLO_REVISAR -eq 0 ] && [ -z "$INSTALAR" ] && { [ $CLONAR -eq 0 ] || [ -z "$REPOS" ]; } && [ -t 0 ]; then INTERACTIVO=1; fi

ok()    { printf "  [OK]    %s\n" "$1"; }
falta() { printf "  [FALTA] %s\n" "$1"; }
info()  { printf "          %s\n" "$1"; }
pide()  { [ $INTERACTIVO -eq 1 ] || return 1; read -r -p "$1 (S/N) " r; case "$r" in [sSyY]*) return 0 ;; *) return 1 ;; esac; }
quiere() { case ",$INSTALAR," in *",$1,"*) return 0 ;; esac; pide "¿Instalar $2?"; }

clt_ok() { xcode-select -p >/dev/null 2>&1; }  # sin las herramientas de línea de comandos, /usr/bin/git y python3 son atajos que abren un instalador
cargar_brew() {
  for b in /opt/homebrew/bin/brew /usr/local/bin/brew; do
    if [ -x "$b" ]; then eval "$("$b" shellenv)"; return 0; fi
  done
  command -v brew >/dev/null 2>&1
}
buscar_python() {
  for c in /opt/homebrew/bin/python3.12 /usr/local/bin/python3.12 /opt/homebrew/bin/python3 /usr/local/bin/python3 python3; do
    if [ "$c" = "python3" ] && ! clt_ok; then continue; fi
    if command -v "$c" >/dev/null 2>&1 && "$c" -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)" >/dev/null 2>&1; then
      echo "$c"; return 0
    fi
  done
  return 1
}
tiene_git() { if [ -x /opt/homebrew/bin/git ] || [ -x /usr/local/bin/git ]; then return 0; fi; clt_ok && command -v git >/dev/null 2>&1; }
tiene_lo() { [ -d /Applications/LibreOffice.app ]; }
brew_instalar() {
  if ! cargar_brew; then
    if [ $INTERACTIVO -eq 1 ] && pide "Para instalar se necesita Homebrew. ¿Instalarlo ahora? (pedirá la contraseña del Mac)"; then
      /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
      cargar_brew || { falta "Homebrew no quedó disponible"; return 1; }
    else
      falta "Homebrew no está instalado. Ábrelo con doble clic en INSTALAR-MAC.command (pide la contraseña del Mac) o instálalo desde https://brew.sh"
      return 1
    fi
  fi
  echo "  Instalando $*..."
  brew install "$@" && ok "$* instalado"
}

preparar() {
  echo
  echo "PMO Harness - preparación de este computador (Mac)"
  echo "Carpeta: $RAIZ"
  echo
  cargar_brew && ok "Homebrew" || info "Homebrew no instalado (se ofrece si hace falta instalar algo)"
  PY="$(buscar_python)" && ok "Python 3.9 o superior ($PY)" || falta "Python 3.9 o superior"
  tiene_git && ok "Git" || falta "Git"
  command -v gh >/dev/null 2>&1 && ok "GitHub CLI" || falta "GitHub CLI (opcional: crea el repositorio privado desde el chat)"
  tiene_lo && ok "LibreOffice" || falta "LibreOffice (opcional: revisión visual y PDF de los documentos)"

  if [ $SOLO_REVISAR -eq 1 ]; then
    pend=""
    [ -n "$PY" ] || pend="$pend,python"; tiene_git || pend="$pend,git"
    command -v gh >/dev/null 2>&1 || pend="$pend,gh"; tiene_lo || pend="$pend,libreoffice"
    echo
    if [ -n "$pend" ]; then echo "Para instalar lo que falta: bash herramientas/preparar_pc.sh --instalar ${pend#,}"; else echo "Herramientas: todo instalado."; fi
  else
    [ -n "$PY" ] || { quiere python "Python 3.12" && brew_instalar python@3.12; }
    tiene_git || { quiere git "Git" && brew_instalar git; }
    command -v gh >/dev/null 2>&1 || { quiere gh "GitHub CLI" && brew_instalar gh; }
    tiene_lo || { quiere libreoffice "LibreOffice" && brew_instalar --cask libreoffice; }
    chmod +x "$RAIZ"/.githooks/* "$RAIZ"/herramientas/*.sh "$RAIZ"/INSTALAR-MAC.command 2>/dev/null
  fi

  echo
  PY="$(buscar_python)"
  VENV="$RAIZ/.venv/bin/python"
  if [ -x "$VENV" ] && "$VENV" -c "import docx, openpyxl, pptx, yaml, pypdf" >/dev/null 2>&1; then
    ok "Librerías de Python (en .venv)"
  elif [ $SOLO_REVISAR -eq 1 ]; then
    falta "Librerías de Python (se instalan en .venv con: bash herramientas/preparar_pc.sh --instalar librerias)"
  elif [ -z "$PY" ]; then
    falta "Python no responde todavía: instálalo y repite."
  else
    echo "  Instalando librerías de Python en .venv..."
    [ -x "$VENV" ] || "$PY" -m venv "$RAIZ/.venv"
    "$VENV" -m pip install --disable-pip-version-check -q -r "$RAIZ/requirements.txt" && ok "Librerías de Python instaladas en .venv" \
      || falta "No se pudieron instalar las librerías (revisa la conexión a internet)"
  fi

  if tiene_git; then
    [ -n "$NOMBRE_GIT" ] && git config --global user.name "$NOMBRE_GIT"
    [ -n "$CORREO_GIT" ] && git config --global user.email "$CORREO_GIT"
    nombre="$(git config --global user.name)"; correo="$(git config --global user.email)"
    if [ -z "$nombre" ] && [ $INTERACTIVO -eq 1 ]; then read -r -p "Tu nombre para Git (aparece en el historial): " nombre; [ -n "$nombre" ] && git config --global user.name "$nombre"; fi
    if [ -z "$correo" ] && [ $INTERACTIVO -eq 1 ]; then read -r -p "Tu correo para Git (el de tu cuenta de GitHub): " correo; [ -n "$correo" ] && git config --global user.email "$correo"; fi
    if [ -n "$nombre" ] && [ -n "$correo" ]; then ok "Identidad de Git: $nombre <$correo>"; else falta "Identidad de Git (nombre y correo): se piden al instalar o con --nombre-git y --correo-git"; fi

    top="$(git -C "$RAIZ" rev-parse --show-toplevel 2>/dev/null)"
    if [ -n "$top" ] && [ "$(cd "$top" && pwd -P)" = "$(cd "$RAIZ" && pwd -P)" ]; then
      if [ "$(git -C "$RAIZ" config --get core.hooksPath)" = ".githooks" ]; then ok "Control de Git del harness activo"
      elif [ $SOLO_REVISAR -eq 1 ]; then falta "Control de Git del harness (se activa con: git config core.hooksPath .githooks)"
      else git -C "$RAIZ" config core.hooksPath .githooks && ok "Control de Git del harness activado"; fi
    else
      info "La carpeta aún no tiene su propio repositorio: el control de Git se activa al crearlo (skill instalar)."
    fi
    if command -v gh >/dev/null 2>&1; then
      if gh auth status >/dev/null 2>&1; then ok "Sesión de GitHub CLI iniciada"
      elif pide "¿Iniciar sesión en GitHub ahora (se abre el navegador)?"; then gh auth login --web --git-protocol https --hostname github.com
      else falta "Sesión de GitHub CLI (el usuario la inicia con: gh auth login --web)"; fi
    fi
  fi

  echo
  if [ -x "$VENV" ]; then "$VENV" "$RAIZ/herramientas/verificar_entorno.py"; elif [ -n "$PY" ]; then "$PY" "$RAIZ/herramientas/verificar_entorno.py"; fi
}

clonar() {
  command -v gh >/dev/null 2>&1 || { falta "Para descargar las empresas se necesita GitHub CLI: --instalar gh"; return 1; }
  gh auth status >/dev/null 2>&1 || { falta "Primero inicia sesión en GitHub: gh auth login --web"; return 1; }
  [ -n "$DESTINO" ] || DESTINO="$HOME/Documents/PMO-Empresas"
  lista="$(gh repo list $PROPIETARIO --topic pmo-harness-empresa --limit 200 --json nameWithOwner,description \
           --jq '.[] | .nameWithOwner + "\t" + (.description // "")')"
  [ -n "$lista" ] || { echo "No hay repositorios con el tema pmo-harness-empresa en esta cuenta."; return 0; }
  echo; echo "Carpetas de empresa disponibles:"
  echo "$lista" | awk -F'\t' '{ printf "  %d. %s  %s\n", NR, $1, $2 }'
  if [ "$REPOS" = "todas" ]; then elegidos="$(echo "$lista" | cut -f1)"
  elif [ -n "$REPOS" ]; then
    elegidos=""
    for r in $(echo "$REPOS" | tr ',' ' '); do elegidos="$elegidos $(echo "$lista" | cut -f1 | grep -E "(^|/)$r\$")"; done
  elif [ $INTERACTIVO -eq 1 ]; then
    read -r -p "¿Cuáles descargar? (números separados por coma, o 'todas'): " r
    if [ "$r" = "todas" ]; then elegidos="$(echo "$lista" | cut -f1)"
    else elegidos=""; for n in $(echo "$r" | tr ',' ' '); do elegidos="$elegidos $(echo "$lista" | sed -n "${n}p" | cut -f1)"; done; fi
  else echo "Indica cuáles con --repos \"a,b\" o --repos todas."; return 1; fi
  mkdir -p "$DESTINO"
  PY="$(buscar_python)"
  for r in $elegidos; do
    carpeta="$DESTINO/${r##*/}"
    if [ -d "$carpeta" ]; then info "${r##*/}: ya existe en $carpeta (para actualizarla: git pull)"; continue; fi
    if gh repo clone "$r" "$carpeta"; then
      git -C "$carpeta" config core.hooksPath .githooks
      chmod +x "$carpeta"/.githooks/* "$carpeta"/herramientas/*.sh "$carpeta"/INSTALAR-MAC.command 2>/dev/null
      if [ -n "$PY" ]; then "$PY" -m venv "$carpeta/.venv" && "$carpeta/.venv/bin/python" -m pip install -q --disable-pip-version-check -r "$carpeta/requirements.txt"; fi
      ok "${r##*/} -> $carpeta"
    else falta "No se pudo descargar $r"; fi
  done
  echo; echo "Abre en VS Code la carpeta de la empresa con la que vas a trabajar y escribe 'hola'."
}

iniciar_github() {
  cargar_brew
  GH="$(command -v gh)" || { falta "Primero instala GitHub CLI: --instalar gh"; return 1; }
  if "$GH" auth status >/dev/null 2>&1; then ok "La sesión de GitHub ya está iniciada"; return 0; fi
  if [ -t 0 ]; then "$GH" auth login --web --git-protocol https --hostname github.com; return; fi
  osascript -e "tell application \"Terminal\" to do script \"'$GH' auth login --web --git-protocol https --hostname github.com\"" \
            -e 'tell application "Terminal" to activate' >/dev/null
  echo "Se abrió una ventana de Terminal para iniciar sesión en GitHub: presiona Enter, pega el código en el navegador y autoriza."
  echo "Cuando termines, vuelve al chat y avisa."
}

if [ $INICIAR_GITHUB -eq 1 ]; then iniciar_github; elif [ $CLONAR -eq 1 ]; then clonar; else preparar; fi
