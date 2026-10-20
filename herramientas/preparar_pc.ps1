<#
Prepara un computador Windows para usar el PMO Harness: revisa e instala lo que falte.

Uso:
  Doble clic en INSTALAR-WINDOWS.bat            -> instala lo necesario y pide solo tu nombre, tu correo y conectar GitHub.
  powershell -File herramientas\preparar_pc.ps1 -SoloRevisar
                                                 -> solo informa qué falta (no instala nada). Es lo que hace sin opciones.
  powershell -File herramientas\preparar_pc.ps1 -Instalar python,git,gh,libreoffice [-NombreGit "Nombre" -CorreoGit "correo"]
                                                 -> instala lo indicado sin preguntar (lo usa el asistente de IA
                                                    después de pedir permiso en el chat).
  powershell -File herramientas\preparar_pc.ps1 -IniciarGitHub
                                                 -> conecta la cuenta de GitHub: abre el navegador con el código ya copiado.
  powershell -File herramientas\preparar_pc.ps1 -Clonar [-Repos "repo1,repo2" | -Repos todas] [-Destino carpeta] [-Propietario cuenta]
                                                 -> descarga las carpetas de empresa (repositorios con el tema
                                                    pmo-harness-empresa) para trabajar en este computador.
  -Simular                                       -> muestra los comandos de instalación sin ejecutarlos.

Nunca se queda esperando:
- Python, Git y GitHub CLI se instalan solo para el usuario: Windows no pide permiso de administrador.
- winget va con los términos aceptados y sin preguntas; si winget falta o falla, se usa la descarga oficial.
- Cada programa externo recibe una entrada vacía (no puede esperar una respuesta) y tiene un tiempo máximo.
- Las preguntas existen solo con doble clic, y si nadie responde se sigue con la respuesta por defecto.
Instala las librerías de requirements.txt, activa el control de Git y termina con verificar_entorno.py.
No instala VS Code ni el asistente de IA.
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
    [string]$Propietario = "",
    [switch]$DobleClic,
    [switch]$Simular
)

$ErrorActionPreference = "Continue"
$ProgressPreference = "SilentlyContinue"
$Raiz = Split-Path -Parent $PSScriptRoot
$Instalar = @($Instalar | ForEach-Object { $_ -split "," } | ForEach-Object { $_.Trim().ToLower() } | Where-Object { $_ })
function Abierto-DesdeExplorador {
    # Doble clic real: Explorador de archivos -> cmd (INSTALAR-WINDOWS.bat) -> este PowerShell. Un asistente de IA o una
    # terminal lo ejecutan desde otro programa, y su entrada puede parecer una consola sin que nadie pueda escribir.
    try {
        $yo = Get-CimInstance Win32_Process -Filter "ProcessId=$PID" -ErrorAction Stop
        $bat = Get-CimInstance Win32_Process -Filter "ProcessId=$($yo.ParentProcessId)" -ErrorAction Stop
        $origen = Get-CimInstance Win32_Process -Filter "ProcessId=$($bat.ParentProcessId)" -ErrorAction Stop
        return ($bat.Name -eq "cmd.exe") -and ($origen.Name -eq "explorer.exe") -and -not [Console]::IsInputRedirected
    } catch { return $false }
}
# Solo hay preguntas en la ventana del doble clic; si el asistente de IA lo ejecuta, nunca hay preguntas
$Interactivo = $DobleClic -and (Abierto-DesdeExplorador)
if (-not $DobleClic -and $Instalar.Count -eq 0 -and -not $IniciarGitHub -and -not $Clonar) { $SoloRevisar = $true }
$Vacio = Join-Path $env:TEMP "pmo-harness-entrada-vacia.txt"
$Necesarios = @("python", "git", "gh")

function Linea($texto) { Write-Host $texto }
function Ok($texto) { Write-Host "  [OK]    $texto" -ForegroundColor Green }
function Falta($texto) { Write-Host "  [FALTA] $texto" -ForegroundColor Yellow }
function Info($texto) { Write-Host "          $texto" }

function Leer-Respuesta($pregunta, $siEnter = "", $siNadieResponde = "", [int]$segundos = 180) {
    # Pregunta con tiempo máximo: si nadie responde, sigue con $siNadieResponde. Sin ventana interactiva no pregunta.
    if (-not $Interactivo) { return $siNadieResponde }
    Write-Host -NoNewline "$pregunta "
    $texto = ""
    $limite = (Get-Date).AddSeconds($segundos)
    try {
        while ((Get-Date) -lt $limite) {
            if ([Console]::KeyAvailable) {
                $k = [Console]::ReadKey($true)
                if ($k.Key -eq "Enter") {
                    Write-Host ""
                    if ($texto.Trim()) { return $texto.Trim() }
                    return $siEnter
                }
                if ($k.Key -eq "Backspace") {
                    if ($texto.Length -gt 0) { $texto = $texto.Substring(0, $texto.Length - 1); Write-Host -NoNewline "`b `b" }
                    continue
                }
                if ($k.KeyChar -and -not [char]::IsControl($k.KeyChar)) { $texto += $k.KeyChar; Write-Host -NoNewline $k.KeyChar }
            } else { Start-Sleep -Milliseconds 100 }
        }
    } catch { return $siNadieResponde }
    Write-Host ""
    return $siNadieResponde
}

function Es-Si($r) { return "$r" -match "^(s|si|sí|y|yes)$" }

function Unir-Argumentos([string[]]$argumentos) {
    # Start-Process no entrecomilla: cada argumento con espacios va entre comillas
    return ($argumentos | ForEach-Object {
        if ($_ -match '[\s"]') { '"' + ($_ -replace '"', '\"') + '"' } else { $_ }
    }) -join " "
}

function Ejecutar($exe, [string[]]$argumentos, [int]$minutos = 15) {
    # Ejecuta un programa sin que pueda quedarse esperando: entrada vacía y tiempo máximo. Devuelve el código de salida.
    if ($Simular) { Linea "  [simulación] $exe $(Unir-Argumentos $argumentos)"; return 0 }
    if (-not (Test-Path $Vacio)) { Set-Content -Path $Vacio -Value "" -Encoding ASCII }
    try {
        $p = Start-Process -FilePath $exe -ArgumentList (Unir-Argumentos $argumentos) -NoNewWindow -PassThru -RedirectStandardInput $Vacio -ErrorAction Stop
    } catch {
        Falta "No se pudo ejecutar ${exe}: $($_.Exception.Message)"
        return -1
    }
    $null = $p.Handle
    if (-not $p.WaitForExit($minutos * 60 * 1000)) {
        & taskkill /PID $p.Id /T /F 2>$null | Out-Null
        Falta "Se detuvo $(Split-Path $exe -Leaf): tardó más de $minutos minutos"
        return -2
    }
    return $p.ExitCode
}

function Refrescar-Path {
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
}

function Agregar-PathUsuario($carpeta) {
    $actual = [Environment]::GetEnvironmentVariable("Path", "User")
    if (-not $actual) { $actual = "" }
    if (($actual -split ";") -notcontains $carpeta) {
        [Environment]::SetEnvironmentVariable("Path", ($carpeta + ";" + $actual).TrimEnd(";"), "User")
    }
    Refrescar-Path
}

function Descargar($url, $destino) {
    if ($Simular) { Linea "  [simulación] descargar $url"; return $true }
    try { [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12 } catch { }
    try {
        Invoke-WebRequest -Uri $url -OutFile $destino -UseBasicParsing -TimeoutSec 900 -ErrorAction Stop
        return $true
    } catch {
        Falta "No se pudo descargar ${url}: $($_.Exception.Message)"
        return $false
    }
}

function Url-UltimaVersion($repo, $patron) {
    # Enlace del archivo de la última versión publicada en GitHub (fuente oficial del programa)
    if ($Simular) { return "https://github.com/$repo/releases/latest ($patron)" }
    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
        $r = Invoke-RestMethod -Uri "https://api.github.com/repos/$repo/releases/latest" -UseBasicParsing -TimeoutSec 60 `
            -Headers @{ "User-Agent" = "pmo-harness" } -ErrorAction Stop
        return ($r.assets | Where-Object { $_.name -match $patron } | Select-Object -First 1).browser_download_url
    } catch { return $null }
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

# --- Descargas oficiales, si winget falta o falla (todas solo para el usuario, sin permiso de administrador) ---
$PythonArgs = @("/quiet", "InstallAllUsers=0", "InstallLauncherAllUsers=0", "PrependPath=1", "Include_launcher=1", "Include_test=0")

function Directo-Python {
    $exe = Join-Path $env:TEMP "python-3.12.10-amd64.exe"
    if (Descargar "https://www.python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe" $exe) { $null = Ejecutar $exe $PythonArgs 15 }
}

function Directo-Git {
    $url = Url-UltimaVersion "git-for-windows/git" '^Git-[\d.]+-64-bit\.exe$'
    if (-not $url) { Falta "No se encontró la descarga oficial de Git"; return }
    $exe = Join-Path $env:TEMP "instalador-git.exe"
    if (Descargar $url $exe) { $null = Ejecutar $exe @("/VERYSILENT", "/NORESTART", "/NOCANCEL", "/SP-", "/SUPPRESSMSGBOXES", "/CURRENTUSER") 15 }
    $propio = Join-Path $env:LOCALAPPDATA "Programs\Git\cmd"
    if (Test-Path $propio) { Agregar-PathUsuario $propio }
}

function Directo-GH {
    $url = Url-UltimaVersion "cli/cli" '^gh_[\d.]+_windows_amd64\.zip$'
    if (-not $url) { Falta "No se encontró la descarga oficial de GitHub CLI"; return }
    $zip = Join-Path $env:TEMP "github-cli.zip"
    $dest = Join-Path $env:LOCALAPPDATA "Programs\GitHub CLI"
    if (-not (Descargar $url $zip)) { return }
    if ($Simular) { Linea "  [simulación] descomprimir en $dest"; return }
    try { Expand-Archive -Path $zip -DestinationPath $dest -Force -ErrorAction Stop } catch { Falta "No se pudo descomprimir GitHub CLI"; return }
    Agregar-PathUsuario (Join-Path $dest "bin")
}

$Paquetes = [ordered]@{
    python      = @{ nombre = "Python 3.12"; id = "Python.Python.3.12"; scope = "user"; override = ($PythonArgs -join " ")
                     directo = ${function:Directo-Python}; presente = { [bool](Buscar-Python) }; web = "https://www.python.org/downloads/" }
    git         = @{ nombre = "Git"; id = "Git.Git"; scope = "user"; override = ""
                     directo = ${function:Directo-Git}; presente = { [bool](Get-Command git -ErrorAction SilentlyContinue) }; web = "https://git-scm.com/download/win" }
    gh          = @{ nombre = "GitHub CLI (conecta tu cuenta y crea el repositorio privado)"; id = "GitHub.cli"; scope = "user"; override = ""
                     directo = ${function:Directo-GH}; presente = { [bool](Get-Command gh -ErrorAction SilentlyContinue) }; web = "https://cli.github.com/" }
    libreoffice = @{ nombre = "LibreOffice (opcional: revisión visual y PDF de los documentos)"; id = "TheDocumentFoundation.LibreOffice"; scope = ""; override = ""
                     directo = $null; presente = { [bool](Buscar-LibreOffice) }; web = "https://www.libreoffice.org/download/" }
}

function Instalar-Paquete($clave) {
    $p = $Paquetes[$clave]
    if ($clave -eq "libreoffice") {
        Linea "  Instalando $($p.nombre)... Windows pedirá permiso: si no ves la ventana, haz clic en el ícono con escudo que parpadea en la barra de tareas (se cancela solo a los 10 minutos)."
    } else { Linea "  Instalando $($p.nombre)... (solo para tu usuario: no pide permiso de administrador)" }
    $listo = $false
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        $a = @("install", "--id", $p.id, "-e", "--source", "winget", "--accept-package-agreements", "--accept-source-agreements", "--silent")
        try {
            $vw = ((winget --version) -replace '^v', '') -replace '[-+].*$', ''
            if ([version]$vw -ge [version]"1.4") { $a += "--disable-interactivity" }
        } catch { }
        if ($p.scope) { $a += @("--scope", $p.scope) }
        if ($p.override) { $a += @("--override", $p.override) }
        $minutos = 15
        if ($clave -eq "libreoffice") { $minutos = 10 }
        $rc = Ejecutar (Get-Command winget).Source $a $minutos
        Refrescar-Path
        $listo = (-not $Simular) -and (& $p.presente)
        if (-not $listo -and -not $Simular -and $p.directo) { Info "winget no lo dejó listo (código $rc): se usa la descarga oficial." }
    } elseif (-not $p.directo) {
        Falta "winget no está disponible: instala $($p.nombre) desde $($p.web)"
        return
    }
    if (-not $listo -and $p.directo) { & $p.directo; Refrescar-Path; $listo = (-not $Simular) -and (& $p.presente) }
    if ($Simular) { return }
    if ($listo) { Ok "$($p.nombre) instalado" } else { Falta "No se pudo instalar $($p.nombre). Descárgalo de $($p.web), instálalo y vuelve a ejecutar el instalador." }
}

function Carpeta-Sincronizada($ruta) {
    # Dropbox, OneDrive, Google Drive o iCloud sincronizan solos: con Git pueden dañar el historial entre computadores
    $r = "$ruta".ToLower()
    if ($r -match "dropbox") { return "Dropbox" }
    if ($r -match "onedrive") { return "OneDrive" }
    if ($r -match "google ?drive|\\my drive|\\mi unidad") { return "Google Drive" }
    if ($r -match "icloud ?drive") { return "iCloud" }
    return ""
}

function Lugar-Sugerido {
    # Documentos si no se sincroniza solo (en muchos Windows está dentro de OneDrive); si no, una carpeta PMO del usuario
    $docs = [Environment]::GetFolderPath("MyDocuments")
    if ($docs -and -not (Carpeta-Sincronizada $docs)) { return $docs }
    return (Join-Path $env:USERPROFILE "PMO")
}

function Avisar-Sincronizada {
    $s = Carpeta-Sincronizada $Raiz
    if (-not $s) { return }
    Linea ""
    Falta "Esta carpeta está dentro de $s, que la sincroniza por su cuenta."
    Info "Con el historial de Git eso puede dañarse al trabajar desde dos computadores, y si la carpeta es compartida otros ven todo."
    Info "Cierra tu herramienta de IA y mueve esta carpeta a $(Lugar-Sugerido). El respaldo y el acceso desde otros"
    Info "computadores ya los da tu repositorio privado de GitHub. Tus documentos originales pueden seguir en $s."
}

function Rutas-Largas-Activas {
    try { return ((Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name LongPathsEnabled -ErrorAction Stop).LongPathsEnabled -eq 1) }
    catch { return $false }
}

function Activar-RutasLargas {
    # Pide permiso de administrador: solo si el usuario lo pidió expresamente. Nunca espera más de 2 minutos.
    Linea "  Activando las rutas largas: Windows pedirá permiso (si no ves la ventana, busca el ícono con escudo en la barra de tareas)."
    if ($Simular) { Linea "  [simulación] activar LongPathsEnabled con permiso de administrador"; return }
    $cmd = "New-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem' -Name LongPathsEnabled -Value 1 -PropertyType DWORD -Force"
    try { Start-Process powershell -Verb RunAs -ArgumentList @("-NoProfile", "-Command", $cmd) -ErrorAction Stop } catch { }
    $limite = (Get-Date).AddMinutes(2)
    while ((Get-Date) -lt $limite -and -not (Rutas-Largas-Activas)) { Start-Sleep -Seconds 2 }
    if (Rutas-Largas-Activas) { Ok "Rutas largas de Windows activadas" } else { Info "No se activaron las rutas largas (no se dio el permiso). No es necesario: el harness funciona igual." }
}

function Configurar-GitParaElAsistente($carpeta) {
    # La consola del asistente no deja salir de un paginador: en este repositorio git muestra todo sin paginar
    git -C $carpeta config core.pager cat 2>$null
}

function Conectar-GitHub([switch]$EnEstaVentana) {
    $gh = Get-Command gh -ErrorAction SilentlyContinue
    if (-not $gh) { Falta "Primero instala GitHub CLI: -Instalar gh"; return }
    gh auth status *> $null
    if ($LASTEXITCODE -eq 0) { Ok "La cuenta de GitHub ya está conectada"; return }
    $ghExe = $gh.Source
    $copia = ""
    if ((& $ghExe auth login --help 2>$null) -match "--clipboard") { $copia = " --clipboard" }
    # Sin preguntas en inglés: el navegador se abre en la página del código, que queda copiado
    $pasos = "`$env:GH_PROMPT_DISABLED = '1'; " +
             "Write-Host 'Conectar tu cuenta de GitHub' -ForegroundColor Cyan; " +
             "Write-Host '1) En el navegador, inicia sesión en GitHub (o crea tu cuenta gratuita).'; " +
             "Write-Host '2) Donde pide el código, pégalo con Ctrl+V (ya está copiado; también aparece abajo) y presiona Continue.'; " +
             "Write-Host '3) Presiona Authorize. Si creaste la cuenta recién, vuelve a abrir github.com/login/device y pega el código.'; " +
             "Write-Host ''; Start-Process 'https://github.com/login/device'; " +
             "& '$ghExe' auth login --web$copia --git-protocol https --hostname github.com; " +
             "if (`$LASTEXITCODE -eq 0) { & '$ghExe' auth setup-git --hostname github.com; & '$ghExe' config set prompt disabled; " +
             "Write-Host ''; Write-Host 'Listo: tu cuenta quedó conectada.' -ForegroundColor Green } " +
             "else { Write-Host ''; Write-Host 'No se completó. Vuelve al chat y pide conectar GitHub de nuevo.' -ForegroundColor Yellow }"
    if ($Simular) { Linea "  [simulación] $pasos"; return }
    if ($EnEstaVentana) {
        Invoke-Expression $pasos
        Remove-Item Env:GH_PROMPT_DISABLED -ErrorAction SilentlyContinue
        return
    }
    $ventana = "`$Host.UI.RawUI.WindowTitle = 'Conectar GitHub'; " + $pasos + "; Write-Host 'Esta ventana se cierra sola en 20 segundos.'; Start-Sleep -Seconds 20"
    $codificado = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($ventana))  # sin problemas de comillas
    Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -EncodedCommand $codificado"
    Linea "Se abrió el navegador en GitHub y una ventana «Conectar GitHub» con las instrucciones (si no la ves, está en la barra de tareas)."
    Linea "El código ya está copiado: en el navegador, pégalo con Ctrl+V, presiona Continue y luego Authorize. Después vuelve al chat y avisa."
}

function Preparar-Herramientas {
    Linea ""
    Linea "PMO Harness - preparación de este computador (Windows)"
    Linea "Carpeta: $Raiz"
    if ($Interactivo) { Linea "No necesita permisos de administrador ni te hará preguntas técnicas." }
    Avisar-Sincronizada
    Linea ""
    if (-not $SoloRevisar -and -not $Simular) {
        # Archivos descargados de internet: que Windows no vuelva a advertir al abrir los instaladores del harness
        Get-ChildItem -LiteralPath $Raiz -Recurse -File -Include *.bat, *.ps1, *.cmd -ErrorAction SilentlyContinue | Unblock-File -ErrorAction SilentlyContinue
    }
    $pendientes = @()
    foreach ($k in $Paquetes.Keys) {
        $hay = & $Paquetes[$k].presente
        if ($hay) { Ok $Paquetes[$k].nombre } else { Falta $Paquetes[$k].nombre; $pendientes += $k }
    }
    if (Rutas-Largas-Activas) { Ok "Rutas largas de Windows" } else { Info "Rutas largas de Windows: no activadas (opcional; el harness funciona igual)." }
    if ($Simular) { $pendientes = @($Paquetes.Keys | Where-Object { $Instalar -contains $_ }) }

    $porInstalar = @()
    if ($SoloRevisar) {
        Linea ""
        $necesarios = @($pendientes | Where-Object { $Necesarios -contains $_ })
        if ($necesarios.Count) {
            Linea "Para instalar lo que falta: powershell -NoProfile -ExecutionPolicy Bypass -File herramientas\preparar_pc.ps1 -Instalar $($necesarios -join ',')"
        } else { Linea "Herramientas necesarias: todo instalado." }
    } elseif ($Instalar.Count) {
        $porInstalar = @($pendientes | Where-Object { $Instalar -contains $_ })
    } else {
        # Doble clic: lo necesario se instala sin preguntar uno por uno; lo opcional lo ofrece después el asistente
        $porInstalar = @($pendientes | Where-Object { $Necesarios -contains $_ })
        if ($porInstalar.Count) {
            Linea ""
            Linea "Se instalará: $(($porInstalar | ForEach-Object { $Paquetes[$_].nombre }) -join ', '). Toma unos minutos."
            $null = Leer-Respuesta "Presiona Enter para comenzar (o cierra esta ventana para cancelar)." "" "" 120
        }
    }
    foreach ($k in $porInstalar) { Instalar-Paquete $k }
    if ($Instalar -contains "rutaslargas" -and -not (Rutas-Largas-Activas)) { Activar-RutasLargas }

    # Librerías de Python
    Linea ""
    $py = Buscar-Python
    if ($Simular) {
        Linea "  [simulación] python -m pip install --no-input --disable-pip-version-check --timeout 60 --retries 2 -r requirements.txt"
    } elseif (-not $py) {
        Falta "Python no responde todavía. Si recién se instaló, cierra y vuelve a abrir tu herramienta de IA (o esta ventana) y repite."
    } else {
        $pyArgs = @()
        if ($py.Count -gt 1) { $pyArgs = $py[1..($py.Count - 1)] }
        & $py[0] @pyArgs -c "import docx, openpyxl, pptx, yaml, pypdf" 2>$null
        if ($LASTEXITCODE -eq 0) { Ok "Librerías de Python" }
        elseif ($SoloRevisar) { Falta "Librerías de Python (se instalan con el instalador o con: $($py -join ' ') -m pip install -r requirements.txt)" }
        else {
            Linea "  Instalando librerías de Python..."
            $exe = (Get-Command $py[0]).Source
            $pip = $pyArgs + @("-m", "pip", "install", "--no-input", "--disable-pip-version-check", "--timeout", "60", "--retries", "2", "-r", (Join-Path $Raiz "requirements.txt"))
            $rc = Ejecutar $exe $pip 15
            if ($rc -ne 0) { $rc = Ejecutar $exe ($pip + @("--user")) 15 }
            if ($rc -eq 0) { Ok "Librerías de Python instaladas" } else { Falta "No se pudieron instalar las librerías (revisa la conexión a internet y repite)" }
        }
    }

    # Git: identidad, control del harness y GitHub (en simulación solo se mira)
    $soloMirar = $SoloRevisar -or $Simular
    if (Get-Command git -ErrorAction SilentlyContinue) {
        $nombre = (git config --global user.name) 2>$null
        $correo = (git config --global user.email) 2>$null
        if ($NombreGit -and -not $soloMirar) { git config --global user.name $NombreGit; $nombre = $NombreGit }
        if ($CorreoGit -and -not $soloMirar) { git config --global user.email $CorreoGit; $correo = $CorreoGit }
        if (-not $nombre) { $n = Leer-Respuesta "Tu nombre y apellido (firma el historial de tus cambios; no es para entrar a GitHub):" "" "" 300; if ($n) { git config --global user.name $n; $nombre = $n } }
        if (-not $correo) { $c = Leer-Respuesta "Tu correo (conviene el mismo de tu cuenta de GitHub; no se envía a nadie):" "" "" 300; if ($c) { git config --global user.email $c; $correo = $c } }
        if ($nombre -and $correo) { Ok "Identidad de Git: $nombre <$correo>" } else { Falta "Nombre y correo para Git: el asistente te los pedirá en el chat" }
        if (-not $soloMirar) { git config --global core.longpaths true }  # Git en Windows: rutas de más de 260 caracteres

        Push-Location $Raiz
        $top = (git rev-parse --show-toplevel) 2>$null
        $propio = $top -and ((Resolve-Path $top).Path -eq (Resolve-Path $Raiz).Path)
        if ($propio) {
            $hp = (git config --get core.hooksPath) 2>$null
            if ($hp -eq ".githooks") { Ok "Control de Git del harness activo" }
            elseif ($soloMirar) { Falta "Control de Git del harness (se activa con: git config core.hooksPath .githooks)" }
            else { git config core.hooksPath .githooks; Ok "Control de Git del harness activado" }
            if (-not $soloMirar) { Configurar-GitParaElAsistente $Raiz }
        } else {
            Info "La carpeta aún no tiene su propio repositorio: el control de Git se activa al crearlo (skill instalar)."
        }
        Pop-Location

        if (Get-Command gh -ErrorAction SilentlyContinue) {
            gh auth status *> $null
            if ($LASTEXITCODE -eq 0) { Ok "Cuenta de GitHub conectada" }
            elseif ($Interactivo -and (Es-Si (Leer-Respuesta "¿Conectar ahora tu cuenta de GitHub? Se abre el navegador. (Enter = sí, escribe N = después)" "s" "n" 120))) {
                Conectar-GitHub -EnEstaVentana
            } else { Falta "Cuenta de GitHub: el asistente te ayuda a conectarla en el chat" }
        }
    }

    Linea ""
    $py = Buscar-Python
    if ($py -and -not $Simular) {
        $pyArgs = @()
        if ($py.Count -gt 1) { $pyArgs = $py[1..($py.Count - 1)] }
        & $py[0] @pyArgs (Join-Path $Raiz "herramientas\verificar_entorno.py")
    }

    # Otro computador: si esta carpeta aún no es de una empresa y la cuenta ya tiene carpetas de empresa, se ofrecen
    $descargadas = @()
    if ($Interactivo -and -not (Test-Path (Join-Path $Raiz ".harness\estado.yaml")) -and (Get-Command gh -ErrorAction SilentlyContinue)) {
        gh auth status *> $null
        if ($LASTEXITCODE -eq 0) {
            $suyas = @(gh repo list --topic pmo-harness-empresa --limit 200 --json name --jq ".[].name" 2>$null | Where-Object { $_ })
            if ($suyas.Count) {
                Linea ""
                Linea "Ya tienes carpetas de empresa en GitHub: $($suyas -join ', ')."
                $r = Leer-Respuesta "¿Es otro computador y quieres descargarlas a $(Join-Path (Lugar-Sugerido) 'PMO-Empresas')? (Enter = sí, escribe N = no)" "s" "n" 120
                if (Es-Si $r) {
                    $script:Repos = "todas"
                    Clonar-Empresas
                    $descargadas = $suyas
                }
            }
        }
    }
    if ($DobleClic) {
        Linea ""
        if ($descargadas.Count) {
            $base = Join-Path (Lugar-Sugerido) "PMO-Empresas"
            Linea "Listo. Ahora abre en tu herramienta de IA (Antigravity, VS Code...) la carpeta de tu empresa, dentro de"
            Linea "$base (por ejemplo, $(Join-Path $base $descargadas[0])), y escribe «hola»."
            Linea "Esta carpeta (la que descargaste como zip) ya no la necesitas: puedes borrarla."
        } elseif (Carpeta-Sincronizada $Raiz) {
            Avisar-Sincronizada
            Linea ""
            Linea "Cuando la hayas movido, abre la carpeta en su nueva ubicación en tu herramienta de IA y escribe «hola»."
        } else {
            Linea "Listo. Ahora abre esta carpeta en tu herramienta de IA (Antigravity, VS Code...) y escribe «hola»."
        }
        Linea "Si tu herramienta de IA ya estaba abierta, ciérrala y vuelve a abrirla para que vea lo instalado."
        $null = Leer-Respuesta "Presiona Enter para cerrar esta ventana." "" "" 600
    }
}

function Clonar-Empresas {
    if (-not (Get-Command gh -ErrorAction SilentlyContinue)) { Falta "Para descargar las empresas se necesita GitHub CLI: -Instalar gh"; return }
    gh auth status *> $null
    if ($LASTEXITCODE -ne 0) { Falta "Primero conecta tu cuenta de GitHub: -IniciarGitHub"; return }
    if (-not $Destino) { $Destino = Join-Path (Lugar-Sugerido) "PMO-Empresas" }
    gh auth setup-git --hostname github.com 2>$null | Out-Null  # que Git use la cuenta conectada (sin otra ventana de inicio de sesión)
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
        $r = Leer-Respuesta "¿Cuáles descargar? (números separados por coma, o 'todas')" "" "" 300
        if ($r -eq "todas") { $elegidos = $lista } elseif ($r) { $elegidos = $r -split "," | ForEach-Object { $lista[[int]$_.Trim() - 1] } }
    } else { Linea "Indica cuáles con -Repos ""a,b"" o -Repos todas."; return }
    New-Item -ItemType Directory -Force -Path $Destino | Out-Null
    foreach ($r in $elegidos) {
        $carpeta = Join-Path $Destino $r.name
        if (Test-Path $carpeta) { Info "$($r.name): ya existe en $carpeta (para actualizarla: git pull)"; continue }
        $rc = Ejecutar (Get-Command gh).Source @("repo", "clone", $r.nameWithOwner, $carpeta, "--", "-c", "core.longpaths=true") 30
        if ($rc -eq 0) {
            git -C $carpeta config core.hooksPath .githooks
            Configurar-GitParaElAsistente $carpeta
            Ok "$($r.name) -> $carpeta"
        } else { Falta "No se pudo descargar $($r.name)" }
    }
    Linea ""
    Linea "Abre en tu herramienta de IA la carpeta de la empresa con la que vas a trabajar y escribe 'hola'."
}

if ($IniciarGitHub) { Conectar-GitHub }
elseif ($Clonar) { Clonar-Empresas }
else { Preparar-Herramientas }
exit 0
