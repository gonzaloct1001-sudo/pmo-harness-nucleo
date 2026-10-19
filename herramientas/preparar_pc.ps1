<#
Prepara un computador Windows para usar el PMO Harness: revisa e instala, con permiso del usuario, lo que falte.

Uso:
  Doble clic en INSTALAR-WINDOWS.bat            -> modo interactivo: pregunta S/N por cada cosa.
  powershell -File herramientas\preparar_pc.ps1 -SoloRevisar
                                                 -> solo informa qué falta (no instala nada).
  powershell -File herramientas\preparar_pc.ps1 -Instalar python,git,gh,libreoffice [-NombreGit "Nombre" -CorreoGit "correo"]
                                                 -> instala lo indicado sin preguntar (lo usa el asistente de IA
                                                    después de pedir permiso en el chat).
  powershell -File herramientas\preparar_pc.ps1 -IniciarGitHub
                                                 -> abre una ventana para iniciar sesión en GitHub (Enter y aceptar en el
                                                    navegador); el asistente de IA lo usa porque su consola no es interactiva.
  powershell -File herramientas\preparar_pc.ps1 -Clonar [-Repos "repo1,repo2" | -Repos todas] [-Destino carpeta] [-Propietario cuenta]
                                                 -> descarga las carpetas de empresa (repositorios con el tema
                                                    pmo-harness-empresa) para trabajar en este computador.

Instala con winget (incluido en Windows 10 y 11): Python 3.12, Git, GitHub CLI y, opcionalmente, LibreOffice.
Después instala las librerías de requirements.txt, activa el control de Git (core.hooksPath) y termina con el
diagnóstico de herramientas\verificar_entorno.py. No instala VS Code ni el asistente de IA.
#>
param(
    [switch]$SoloRevisar,
    [string[]]$Instalar = @(),
    [string]$NombreGit = "",
    [string]$CorreoGit = "",
    [switch]$IniciarGitHub,
    [switch]$Clonar,
    [string]$Repos = "",
    [string]$Destino = "",
    [string]$Propietario = ""
)

$ErrorActionPreference = "Continue"
$Raiz = Split-Path -Parent $PSScriptRoot
$Interactivo = (-not $SoloRevisar) -and ($Instalar.Count -eq 0) -and (-not $IniciarGitHub) -and (-not $Clonar -or -not $Repos)
$Instalar = @($Instalar | ForEach-Object { $_ -split "," } | ForEach-Object { $_.Trim().ToLower() } | Where-Object { $_ })

function Linea($texto) { Write-Host $texto }
function Ok($texto) { Write-Host "  [OK]    $texto" -ForegroundColor Green }
function Falta($texto) { Write-Host "  [FALTA] $texto" -ForegroundColor Yellow }
function Info($texto) { Write-Host "          $texto" }

function Preguntar($pregunta) {
    if (-not $Interactivo) { return $false }
    $r = Read-Host "$pregunta (S/N)"
    return $r -match "^(s|si|sí|y|yes)$"
}

function Refrescar-Path {
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
}

function Buscar-Python {
    # Devuelve el comando de un Python 3.9+ real (descarta el alias de Microsoft Store), o $null.
    foreach ($c in @(@("py", "-3"), @("python"), @("python3"))) {
        $cmd = Get-Command $c[0] -ErrorAction SilentlyContinue
        if (-not $cmd) { continue }
        $args_ = @()
        if ($c.Count -gt 1) { $args_ = $c[1..($c.Count - 1)] }
        try {
            $v = & $c[0] @args_ -c "import sys; print('%d.%d' % sys.version_info[:2])" 2>$null
            if ($LASTEXITCODE -eq 0 -and $v -match "^3\.(\d+)$" -and [int]$Matches[1] -ge 9) { return ,$c }
        } catch { }
    }
    return $null
}

function Buscar-LibreOffice {
    foreach ($r in @("$env:ProgramFiles\LibreOffice\program\soffice.exe", "${env:ProgramFiles(x86)}\LibreOffice\program\soffice.exe")) {
        if ($r -and (Test-Path $r)) { return $r }
    }
    return $null
}

$Paquetes = [ordered]@{
    python      = @{ nombre = "Python 3.12"; id = "Python.Python.3.12"; override = "/quiet InstallAllUsers=0 PrependPath=1 Include_launcher=1 Include_test=0" }
    git         = @{ nombre = "Git"; id = "Git.Git"; override = "" }
    gh          = @{ nombre = "GitHub CLI (opcional: crea el repositorio privado desde el chat)"; id = "GitHub.cli"; override = "" }
    libreoffice = @{ nombre = "LibreOffice (opcional: revisión visual y PDF de los documentos)"; id = "TheDocumentFoundation.LibreOffice"; override = "" }
}

function Instalar-Paquete($clave) {
    $p = $Paquetes[$clave]
    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
        Falta "winget no está disponible: instala 'Instalador de aplicación' desde Microsoft Store, o instala $($p.nombre) a mano (enlaces en README.md)."
        return
    }
    Linea "  Instalando $($p.nombre)... (Windows puede pedir confirmación)"
    $a = @("install", "--id", $p.id, "-e", "--source", "winget", "--accept-package-agreements", "--accept-source-agreements", "--silent")
    if ($p.override) { $a += @("--override", $p.override) }
    & winget @a
    if ($LASTEXITCODE -eq 0) { Ok "$($p.nombre) instalado" } else { Falta "winget terminó con código $LASTEXITCODE al instalar $($p.nombre)" }
    Refrescar-Path
}

function Rutas-Largas-Activas {
    try { return ((Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name LongPathsEnabled -ErrorAction Stop).LongPathsEnabled -eq 1) }
    catch { return $false }
}

function Estado-Herramientas {
    return [ordered]@{
        python      = [bool](Buscar-Python)
        git         = [bool](Get-Command git -ErrorAction SilentlyContinue)
        gh          = [bool](Get-Command gh -ErrorAction SilentlyContinue)
        libreoffice = [bool](Buscar-LibreOffice)
    }
}

function Preparar-Herramientas {
    Linea ""
    Linea "PMO Harness - preparación de este computador (Windows)"
    Linea "Carpeta: $Raiz"
    Linea ""
    $estado = Estado-Herramientas
    foreach ($k in $Paquetes.Keys) {
        if ($estado[$k]) { Ok $Paquetes[$k].nombre } else { Falta $Paquetes[$k].nombre }
    }
    $pendientes = @($Paquetes.Keys | Where-Object { -not $estado[$_] })
    $largas = Rutas-Largas-Activas
    if ($largas) { Ok "Rutas largas de Windows" }
    else {
        Falta "Rutas largas de Windows (opcional; recomendado con OneDrive o carpetas profundas; pide permiso de administrador)"
        $pendientes += "rutaslargas"
    }
    if ($SoloRevisar) {
        Linea ""
        if ($pendientes.Count) {
            Linea "Para instalar lo que falta: powershell -ExecutionPolicy Bypass -File herramientas\preparar_pc.ps1 -Instalar $($pendientes -join ',')"
        } else { Linea "Herramientas: todo instalado." }
    } else {
        foreach ($k in $pendientes) {
            if ($k -eq "rutaslargas") {
                if ($Instalar -contains $k -or (Preguntar "¿Activar las rutas largas de Windows? (pide permiso de administrador)")) {
                    $cmd = "New-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem' -Name LongPathsEnabled -Value 1 -PropertyType DWORD -Force"
                    try { Start-Process powershell -Verb RunAs -Wait -ArgumentList @("-NoProfile", "-Command", $cmd) } catch { }
                    if (Rutas-Largas-Activas) { Ok "Rutas largas de Windows activadas" } else { Falta "No se activaron las rutas largas (se canceló el permiso de administrador)" }
                }
                continue
            }
            if ($Instalar -contains $k -or (Preguntar "¿Instalar $($Paquetes[$k].nombre)?")) { Instalar-Paquete $k }
        }
    }

    # Librerías de Python
    Linea ""
    $py = Buscar-Python
    if (-not $py) {
        Falta "Python no responde todavía. Si recién se instaló, cierra y vuelve a abrir VS Code (o esta ventana) y repite."
    } else {
        $pyArgs = @()
        if ($py.Count -gt 1) { $pyArgs = $py[1..($py.Count - 1)] }
        & $py[0] @pyArgs -c "import docx, openpyxl, pptx, yaml, pypdf" 2>$null
        if ($LASTEXITCODE -eq 0) { Ok "Librerías de Python" }
        elseif ($SoloRevisar) { Falta "Librerías de Python (se instalan con: $($py -join ' ') -m pip install -r requirements.txt)" }
        else {
            Linea "  Instalando librerías de Python..."
            & $py[0] @pyArgs -m pip install --disable-pip-version-check -r (Join-Path $Raiz "requirements.txt")
            if ($LASTEXITCODE -ne 0) { & $py[0] @pyArgs -m pip install --user --disable-pip-version-check -r (Join-Path $Raiz "requirements.txt") }
            if ($LASTEXITCODE -eq 0) { Ok "Librerías de Python instaladas" } else { Falta "No se pudieron instalar las librerías (revisa la conexión a internet)" }
        }
    }

    # Git: identidad y control del harness
    if (Get-Command git -ErrorAction SilentlyContinue) {
        $nombre = (git config --global user.name) 2>$null
        $correo = (git config --global user.email) 2>$null
        if ($NombreGit) { git config --global user.name $NombreGit; $nombre = $NombreGit }
        if ($CorreoGit) { git config --global user.email $CorreoGit; $correo = $CorreoGit }
        if (-not $nombre -and $Interactivo) { $n = Read-Host "Tu nombre para Git (aparece en el historial)"; if ($n) { git config --global user.name $n; $nombre = $n } }
        if (-not $correo -and $Interactivo) { $c = Read-Host "Tu correo para Git (el de tu cuenta de GitHub)"; if ($c) { git config --global user.email $c; $correo = $c } }
        if ($nombre -and $correo) { Ok "Identidad de Git: $nombre <$correo>" } else { Falta "Identidad de Git (nombre y correo): se piden al instalar o con -NombreGit y -CorreoGit" }
        if (-not $SoloRevisar) { git config --global core.longpaths true }  # Git en Windows: rutas de más de 260 caracteres

        Push-Location $Raiz
        $top = (git rev-parse --show-toplevel) 2>$null
        $propio = $top -and ((Resolve-Path $top).Path -eq (Resolve-Path $Raiz).Path)
        if ($propio) {
            $hp = (git config --get core.hooksPath) 2>$null
            if ($hp -eq ".githooks") { Ok "Control de Git del harness activo" }
            elseif ($SoloRevisar) { Falta "Control de Git del harness (se activa con: git config core.hooksPath .githooks)" }
            else { git config core.hooksPath .githooks; Ok "Control de Git del harness activado" }
        } else {
            Info "La carpeta aún no tiene su propio repositorio: el control de Git se activa al crearlo (skill instalar)."
        }
        Pop-Location

        if (Get-Command gh -ErrorAction SilentlyContinue) {
            gh auth status *> $null
            if ($LASTEXITCODE -eq 0) { Ok "Sesión de GitHub CLI iniciada" }
            elseif ($Interactivo -and (Preguntar "¿Iniciar sesión en GitHub ahora (se abre el navegador)?")) { gh auth login --web --git-protocol https --hostname github.com }
            else { Falta "Sesión de GitHub CLI (el usuario la inicia con: gh auth login --web)" }
        }
    }

    Linea ""
    $py = Buscar-Python
    if ($py) {
        $pyArgs = @()
        if ($py.Count -gt 1) { $pyArgs = $py[1..($py.Count - 1)] }
        & $py[0] @pyArgs (Join-Path $Raiz "herramientas\verificar_entorno.py")
    }
}

function Clonar-Empresas {
    if (-not (Get-Command gh -ErrorAction SilentlyContinue)) { Falta "Para descargar las empresas se necesita GitHub CLI: -Instalar gh"; return }
    gh auth status *> $null
    if ($LASTEXITCODE -ne 0) { Falta "Primero inicia sesión en GitHub: gh auth login --web"; return }
    if (-not $Destino) { $Destino = Join-Path ([Environment]::GetFolderPath("MyDocuments")) "PMO-Empresas" }
    $a = @("repo", "list")
    if ($Propietario) { $a += $Propietario }
    $a += @("--topic", "pmo-harness-empresa", "--limit", "200", "--json", "name,nameWithOwner,description")
    $lista = (& gh @a | ConvertFrom-Json)
    if (-not $lista) { Linea "No hay repositorios con el tema pmo-harness-empresa en esta cuenta."; return }
    Linea ""
    Linea "Carpetas de empresa disponibles:"
    $i = 0
    foreach ($r in $lista) { $i++; Linea ("  {0}. {1}  {2}" -f $i, $r.nameWithOwner, $r.description) }
    $elegidos = @()
    if ($Repos -eq "todas") { $elegidos = $lista }
    elseif ($Repos) { $nombres = $Repos -split "," | ForEach-Object { $_.Trim() }; $elegidos = $lista | Where-Object { $nombres -contains $_.name -or $nombres -contains $_.nameWithOwner } }
    elseif ($Interactivo) {
        $r = Read-Host "¿Cuáles descargar? (números separados por coma, o 'todas')"
        if ($r -eq "todas") { $elegidos = $lista } else { $elegidos = $r -split "," | ForEach-Object { $lista[[int]$_.Trim() - 1] } }
    } else { Linea "Indica cuáles con -Repos ""a,b"" o -Repos todas."; return }
    New-Item -ItemType Directory -Force -Path $Destino | Out-Null
    foreach ($r in $elegidos) {
        $carpeta = Join-Path $Destino $r.name
        if (Test-Path $carpeta) { Info "$($r.name): ya existe en $carpeta (para actualizarla: git pull)"; continue }
        gh repo clone $r.nameWithOwner $carpeta -- -c core.longpaths=true
        if ($LASTEXITCODE -eq 0) { git -C $carpeta config core.hooksPath .githooks; Ok "$($r.name) -> $carpeta" } else { Falta "No se pudo descargar $($r.name)" }
    }
    Linea ""
    Linea "Abre en VS Code la carpeta de la empresa con la que vas a trabajar y escribe 'hola'."
}

function Iniciar-SesionGitHub {
    $gh = Get-Command gh -ErrorAction SilentlyContinue
    if (-not $gh) { Falta "Primero instala GitHub CLI: -Instalar gh"; return }
    gh auth status *> $null
    if ($LASTEXITCODE -eq 0) { Ok "La sesión de GitHub ya está iniciada"; return }
    $cmd = "Write-Host 'Inicio de sesión en GitHub para el PMO Harness' -ForegroundColor Cyan; " +
           "Write-Host '1) Presiona Enter: se abre el navegador.  2) Pega el código que aparece aquí.  3) Autoriza.'; " +
           "& '$($gh.Source)' auth login --web --git-protocol https --hostname github.com; " +
           "Write-Host ''; Write-Host 'Listo: puedes cerrar esta ventana y volver al chat.' -ForegroundColor Green"
    Start-Process powershell -ArgumentList @("-NoExit", "-NoProfile", "-Command", $cmd)
    Linea "Se abrió una ventana para iniciar sesión en GitHub. Cuando termines, vuelve al chat y avisa."
}

if ($IniciarGitHub) { Iniciar-SesionGitHub } elseif ($Clonar) { Clonar-Empresas } else { Preparar-Herramientas }
