#!/bin/bash
# Prepara un Mac para usar el PMO Harness: revisa e instala lo que falte.
#
# Uso:
#   Doble clic en INSTALAR-MAC.command               -> instala lo necesario y pide solo tu nombre, tu correo y conectar GitHub.
#   bash herramientas/preparar_pc.sh --solo-revisar  -> solo informa qué falta (no instala nada). Es lo que hace sin opciones.
#   bash herramientas/preparar_pc.sh --instalar python,git,gh,libreoffice [--nombre-git "Nombre" --correo-git "correo"]
#                                                    -> instala lo indicado sin preguntar (lo usa el asistente de IA
#                                                       después de pedir permiso en el chat).
#   bash herramientas/preparar_pc.sh --iniciar-github -> conecta la cuenta de GitHub: abre el navegador con el código ya copiado.
#   bash herramientas/preparar_pc.sh --clonar [--repos "a,b" | --repos todas] [--destino carpeta] [--propietario cuenta]
#                                                    -> descarga las carpetas de empresa (repositorios con el tema
#                                                       pmo-harness-empresa) para trabajar en este computador.
#
# Nunca se queda esperando: las preguntas existen solo con doble clic y tienen tiempo máximo; GitHub se conecta sin
# preguntas en inglés. Usa Homebrew para Python, Git, GitHub CLI y, opcionalmente, LibreOffice; instalar Homebrew pide
# la contraseña del Mac, así que solo se hace con doble clic. Las librerías van en .venv/ dentro de la carpeta.
# Activa el control de Git y termina con herramientas/verificar_entorno.py. No instala VS Code ni el asistente de IA.
# Compatible con el bash 3.2 que trae macOS.

RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
SOLO_REVISAR=0; CLONAR=0; INICIAR_GITHUB=0; DOBLE_CLIC=0; INSTALAR=""; NOMBRE_GIT=""; CORREO_GIT=""; REPOS=""; DESTINO=""; PROPIETARIO=""
while [ $# -gt 0 ]; do
  case "$1" in
    --solo-revisar) SOLO_REVISAR=1 ;;
    --instalar) INSTALAR="$2"; shift ;;
    --nombre-git) NOMBRE_GIT="$2"; shift ;;
    --correo-git) CORREO_GIT="$2"; shift ;;
    --clonar) CLONAR=1 ;;
    --iniciar-github) INICIAR_GITHUB=1 ;;
    --doble-clic) DOBLE_CLIC=1 ;;
    --repos) REPOS="$2"; shift ;;
    --destino) DESTINO="$2"; shift ;;
    --propietario) PROPIETARIO="$2"; shift ;;
    *) echo "Opción desconocida: $1"; exit 2 ;;
  esac
  shift
done
# Solo hay preguntas en la ventana del doble clic (Terminal de macOS); si el asistente de IA lo ejecuta, nunca
INTERACTIVO=0
if [ $DOBLE_CLIC -eq 1 ] && [ -t 0 ] && [ "${TERM_PROGRAM:-}" != "vscode" ]; then INTERACTIVO=1; fi
if [ $DOBLE_CLIC -eq 0 ] && [ -z "$INSTALAR" ] && [ $INICIAR_GITHUB -eq 0 ] && [ $CLONAR -eq 0 ]; then SOLO_REVISAR=1; fi
NECESARIOS="python git gh"
export HOMEBREW_NO_ENV_HINTS=1 HOMEBREW_NO_INSTALL_CLEANUP=1

ok()    { printf "  [OK]    %s\n" "$1"; }
falta() { printf "  [FALTA] %s\n" "$1"; }
info()  { printf "          %s\n" "$1"; }
# respuesta "pregunta" "si Enter" "si nadie responde" segundos -> deja el resultado en RESPUESTA
respuesta() {
  RESPUESTA="$3"
  [ $INTERACTIVO -eq 1 ] || return 0
  local r
  if read -r -t "${4:-180}" -p "$1 " r; then
    if [ -n "$r" ]; then RESPUESTA="$r"; else RESPUESTA="$2"; fi
  else echo; fi
}
es_si() { case "$1" in [sSyY]*) return 0 ;; *) return 1 ;; esac; }

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
tiene_gh() { cargar_brew >/dev/null 2>&1; command -v gh >/dev/null 2>&1; }
tiene_lo() { [ -d /Applications/LibreOffice.app ]; }
presente() {
  case "$1" in
    python) [ -n "$(buscar_python)" ] ;;
    git) tiene_git ;;
    gh) tiene_gh ;;
    libreoffice) tiene_lo ;;
  esac
}
nombre_de() {
  case "$1" in
    python) echo "Python 3.12" ;;
    git) echo "Git" ;;
    gh) echo "GitHub CLI (conecta tu cuenta y crea el repositorio privado)" ;;
    libreoffice) echo "LibreOffice (opcional: revisión visual y PDF de los documentos)" ;;
  esac
}
formula_de() {
  case "$1" in
    python) echo "python@3.12" ;;
    git) echo "git" ;;
    gh) echo "gh" ;;
    libreoffice) echo "--cask libreoffice" ;;
  esac
}

instalar_homebrew() {
  # Pide la contraseña del Mac: solo en la ventana del doble clic. Sin confirmaciones en inglés.
  if [ $INTERACTIVO -ne 1 ]; then
    falta "Homebrew no está instalado. Haz doble clic en INSTALAR-MAC.command (pide la contraseña del Mac) o instálalo desde https://brew.sh"
    return 1
  fi
  echo
  echo "Para instalar se necesita Homebrew (el instalador de programas más usado en Mac)."
  echo "Escribe la contraseña de tu Mac y presiona Enter (no se ve mientras la escribes):"
  sudo -v || { falta "Sin la contraseña no se puede instalar Homebrew"; return 1; }
  NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" </dev/null
  cargar_brew || { falta "Homebrew no quedó disponible"; return 1; }
}

instalar_paquete() {
  echo "  Instalando $(nombre_de "$1")..."
  cargar_brew || instalar_homebrew || return 1
  # shellcheck disable=SC2046
  brew install $(formula_de "$1") </dev/null && ok "$(nombre_de "$1") instalado" || falta "No se pudo instalar $(nombre_de "$1")"
}

pager_local() { git -C "$1" config core.pager cat 2>/dev/null; }  # la consola del asistente no deja salir de un paginador

conectar_github() {
  cargar_brew >/dev/null 2>&1
  GH="$(command -v gh)" || { falta "Primero instala GitHub CLI: --instalar gh"; return 1; }
  if "$GH" auth status >/dev/null 2>&1; then ok "La cuenta de GitHub ya está conectada"; return 0; fi
  copia=""
  "$GH" auth login --help 2>/dev/null | grep -q -- "--clipboard" && copia="--clipboard"
  # Sin preguntas en inglés: el navegador se abre en la página del código, que queda copiado
  pasos="export GH_PROMPT_DISABLED=1; clear; echo 'Conectar tu cuenta de GitHub'; \
echo '1) En el navegador, inicia sesión en GitHub (o crea tu cuenta gratuita).'; \
echo '2) Donde pide el código, pégalo con Cmd+V (ya está copiado; también aparece abajo) y presiona Continue.'; \
echo '3) Presiona Authorize. Si creaste la cuenta recién, vuelve a abrir github.com/login/device y pega el código.'; echo; \
open 'https://github.com/login/device'; \
if '$GH' auth login --web $copia --git-protocol https --hostname github.com </dev/null; then \
'$GH' auth setup-git --hostname github.com; '$GH' config set prompt disabled; echo; echo 'Listo: tu cuenta quedó conectada. Puedes cerrar esta ventana.'; \
else echo; echo 'No se completó. Vuelve al chat y pide conectar GitHub de nuevo.'; fi"
  if [ "${1:-}" = "aqui" ]; then bash -c "$pasos"; return; fi
  osascript -e "tell application \"Terminal\" to do script \"$(printf '%s' "$pasos" | sed 's/\\/\\\\/g; s/"/\\"/g')\"" \
            -e 'tell application "Terminal" to activate' >/dev/null
  echo "Se abrió el navegador en GitHub y una ventana de Terminal con las instrucciones."
  echo "El código ya está copiado: en el navegador, pégalo con Cmd+V, presiona Continue y luego Authorize. Después vuelve al chat y avisa."
}

preparar() {
  echo
  echo "PMO Harness - preparación de este computador (Mac)"
  echo "Carpeta: $RAIZ"
  [ $INTERACTIVO -eq 1 ] && echo "No te hará preguntas técnicas."
  echo
  cargar_brew && ok "Homebrew" || info "Homebrew no instalado (se instala si hace falta)"
  pend=""
  for k in python git gh libreoffice; do
    if presente "$k"; then ok "$(nombre_de "$k")"; else falta "$(nombre_de "$k")"; pend="$pend $k"; fi
  done

  por_instalar=""
  if [ $SOLO_REVISAR -eq 1 ]; then
    nec=""
    for k in $pend; do case " $NECESARIOS " in *" $k "*) nec="$nec,$k" ;; esac; done
    echo
    if [ -n "$nec" ]; then echo "Para instalar lo que falta: bash herramientas/preparar_pc.sh --instalar ${nec#,}"; else echo "Herramientas necesarias: todo instalado."; fi
  elif [ -n "$INSTALAR" ]; then
    for k in $pend; do case ",$INSTALAR," in *",$k,"*) por_instalar="$por_instalar $k" ;; esac; done
  else
    # Doble clic: lo necesario se instala sin preguntar uno por uno; lo opcional lo ofrece después el asistente
    for k in $pend; do case " $NECESARIOS " in *" $k "*) por_instalar="$por_instalar $k" ;; esac; done
    if [ -n "$por_instalar" ]; then
      echo
      echo "Se instalará lo necesario:$(for k in $por_instalar; do printf ' %s;' "$(nombre_de "$k")"; done) toma unos minutos."
      respuesta "Presiona Enter para comenzar (o cierra esta ventana para cancelar)." "" "" 120
    fi
  fi
  for k in $por_instalar; do instalar_paquete "$k"; done
  [ $SOLO_REVISAR -eq 1 ] || chmod +x "$RAIZ"/.githooks/* "$RAIZ"/herramientas/*.sh "$RAIZ"/INSTALAR-MAC.command 2>/dev/null

  echo
  PY="$(buscar_python)"
  VENV="$RAIZ/.venv/bin/python"
  if [ -x "$VENV" ] && "$VENV" -c "import docx, openpyxl, pptx, yaml, pypdf" >/dev/null 2>&1; then
    ok "Librerías de Python (en .venv)"
  elif [ $SOLO_REVISAR -eq 1 ]; then
    falta "Librerías de Python (se instalan con el instalador, en .venv)"
  elif [ -z "$PY" ]; then
    falta "Python no responde todavía: instálalo y repite."
  else
    echo "  Instalando librerías de Python en .venv..."
    [ -x "$VENV" ] || "$PY" -m venv "$RAIZ/.venv"
    "$VENV" -m pip install --no-input --disable-pip-version-check --timeout 60 --retries 2 -q -r "$RAIZ/requirements.txt" </dev/null \
      && ok "Librerías de Python instaladas en .venv" || falta "No se pudieron instalar las librerías (revisa la conexión a internet y repite)"
  fi

  if tiene_git; then
    if [ $SOLO_REVISAR -eq 0 ]; then
      [ -n "$NOMBRE_GIT" ] && git config --global user.name "$NOMBRE_GIT"
      [ -n "$CORREO_GIT" ] && git config --global user.email "$CORREO_GIT"
    fi
    nombre="$(git config --global user.name)"; correo="$(git config --global user.email)"
    if [ -z "$nombre" ]; then respuesta "Tu nombre y apellido (así aparecerás en tus documentos):" "" "" 300; nombre="$RESPUESTA"; [ -n "$nombre" ] && git config --global user.name "$nombre"; fi
    if [ -z "$correo" ]; then respuesta "Tu correo (el de tu cuenta de GitHub, o el que usarás para crearla):" "" "" 300; correo="$RESPUESTA"; [ -n "$correo" ] && git config --global user.email "$correo"; fi
    if [ -n "$nombre" ] && [ -n "$correo" ]; then ok "Identidad de Git: $nombre <$correo>"; else falta "Nombre y correo para Git: el asistente te los pedirá en el chat"; fi

    top="$(git -C "$RAIZ" rev-parse --show-toplevel 2>/dev/null)"
    if [ -n "$top" ] && [ "$(cd "$top" && pwd -P)" = "$(cd "$RAIZ" && pwd -P)" ]; then
      if [ "$(git -C "$RAIZ" config --get core.hooksPath)" = ".githooks" ]; then ok "Control de Git del harness activo"
      elif [ $SOLO_REVISAR -eq 1 ]; then falta "Control de Git del harness (se activa con: git config core.hooksPath .githooks)"
      else git -C "$RAIZ" config core.hooksPath .githooks && ok "Control de Git del harness activado"; fi
      [ $SOLO_REVISAR -eq 1 ] || pager_local "$RAIZ"
    else
      info "La carpeta aún no tiene su propio repositorio: el control de Git se activa al crearlo (skill instalar)."
    fi
    if tiene_gh; then
      if gh auth status >/dev/null 2>&1; then ok "Cuenta de GitHub conectada"
      else
        respuesta "¿Conectar ahora tu cuenta de GitHub? Se abre el navegador. (Enter = sí, escribe N = después)" "s" "n" 120
        if [ $INTERACTIVO -eq 1 ] && es_si "$RESPUESTA"; then conectar_github aqui
        else falta "Cuenta de GitHub: el asistente te ayuda a conectarla en el chat"; fi
      fi
    fi
  fi

  echo
  if [ -x "$VENV" ]; then "$VENV" "$RAIZ/herramientas/verificar_entorno.py" </dev/null; elif [ -n "$PY" ]; then "$PY" "$RAIZ/herramientas/verificar_entorno.py" </dev/null; fi
  if [ $DOBLE_CLIC -eq 1 ]; then
    echo
    echo "Listo. Ahora abre esta carpeta en tu herramienta de IA (Antigravity, VS Code...) y escribe «hola»."
    echo "Si tu herramienta de IA ya estaba abierta, ciérrala y vuelve a abrirla para que vea lo instalado."
  fi
}

clonar() {
  tiene_gh || { falta "Para descargar las empresas se necesita GitHub CLI: --instalar gh"; return 1; }
  gh auth status >/dev/null 2>&1 || { falta "Primero conecta tu cuenta de GitHub: --iniciar-github"; return 1; }
  [ -n "$DESTINO" ] || DESTINO="$HOME/Documents/PMO-Empresas"
  lista="$(gh repo list $PROPIETARIO --topic pmo-harness-empresa --limit 200 --json nameWithOwner,description \
           --jq '.[] | .nameWithOwner + "\t" + (.description // "")' </dev/null)"
  [ -n "$lista" ] || { echo "No hay repositorios con el tema pmo-harness-empresa en esta cuenta."; return 0; }
  echo; echo "Carpetas de empresa disponibles:"
  echo "$lista" | awk -F'\t' '{ printf "  %d. %s  %s\n", NR, $1, $2 }'
  if [ "$REPOS" = "todas" ]; then elegidos="$(echo "$lista" | cut -f1)"
  elif [ -n "$REPOS" ]; then
    elegidos=""
    for r in $(echo "$REPOS" | tr ',' ' '); do elegidos="$elegidos $(echo "$lista" | cut -f1 | grep -E "(^|/)$r\$")"; done
  elif [ $INTERACTIVO -eq 1 ]; then
    respuesta "¿Cuáles descargar? (números separados por coma, o 'todas'):" "" "" 300; r="$RESPUESTA"
    if [ "$r" = "todas" ]; then elegidos="$(echo "$lista" | cut -f1)"
    else elegidos=""; for n in $(echo "$r" | tr ',' ' '); do elegidos="$elegidos $(echo "$lista" | sed -n "${n}p" | cut -f1)"; done; fi
  else echo "Indica cuáles con --repos \"a,b\" o --repos todas."; return 1; fi
  mkdir -p "$DESTINO"
  PY="$(buscar_python)"
  for r in $elegidos; do
    carpeta="$DESTINO/${r##*/}"
    if [ -d "$carpeta" ]; then info "${r##*/}: ya existe en $carpeta (para actualizarla: git pull)"; continue; fi
    if gh repo clone "$r" "$carpeta" </dev/null; then
      git -C "$carpeta" config core.hooksPath .githooks
      pager_local "$carpeta"
      chmod +x "$carpeta"/.githooks/* "$carpeta"/herramientas/*.sh "$carpeta"/INSTALAR-MAC.command 2>/dev/null
      if [ -n "$PY" ]; then "$PY" -m venv "$carpeta/.venv" && "$carpeta/.venv/bin/python" -m pip install --no-input -q --disable-pip-version-check -r "$carpeta/requirements.txt" </dev/null; fi
      ok "${r##*/} -> $carpeta"
    else falta "No se pudo descargar $r"; fi
  done
  echo; echo "Abre en tu herramienta de IA la carpeta de la empresa con la que vas a trabajar y escribe 'hola'."
}

if [ $INICIAR_GITHUB -eq 1 ]; then
  if [ $INTERACTIVO -eq 1 ]; then conectar_github aqui; else conectar_github; fi
elif [ $CLONAR -eq 1 ]; then clonar
else preparar; fi
exit 0
