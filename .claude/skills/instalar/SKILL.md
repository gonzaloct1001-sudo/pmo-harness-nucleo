---
name: instalar
description: Punto de partida del harness. Prepara la carpeta y el computador (instala con permiso Python, Git, GitHub CLI y librerías; activa los controles), define la empresa dueña de la carpeta, crea el repositorio privado en GitHub, registra el asistente de IA, crea el proyecto o programa y deja lista la carpeta de carga documental para iniciar el alta. Úsala cuando el usuario escriba instalar, inicializar, configurar, empezar, comenzar, /instalar, o cuando salude o pida cualquier cosa en una carpeta donde el harness aún no está instalado (no existe .harness/estado.yaml). También cuando abra el harness en un computador nuevo.
---

# Instalar

Meta: en pocos minutos, dejar todo listo para que el usuario cargue sus documentos y empiece el alta.
Habla en simple: el usuario puede no ser técnico. Informa el avance en una línea por paso.
VS Code y el asistente de IA ya están en uso: **no se instalan**.

## Paso 0 — Diagnóstico
Ejecuta `python herramientas/verificar_entorno.py` (en Windows, si `python` no responde, prueba `py`; en Mac,
`.venv/bin/python` o `python3`). Si ninguno responde, Python falta: pasa directo al paso 1, que no lo necesita.
Según el resultado:
- **Carpeta del núcleo del mantenedor** (el estado lo indica): no instales; ofrece una carpeta de empresa aparte.
- **Carpeta nueva** (no existe `.harness/estado.yaml`, descargada como zip o clonada del núcleo): **antes de crear
  nada**, pregunta si es su primera vez con el harness o si ya lo usa en otro computador. Si `gh auth status` está OK,
  revisa además `gh repo list --topic pmo-harness-empresa --json name --jq ".[].name"`: si ya tiene carpetas de
  empresa, nómbralas en la pregunta.
  - **Primera vez:** sigue todos los pasos.
  - **Ya lo usa en otro computador:** no crees una empresa nueva (quedaría duplicada). Haz el paso 1 si faltan
    herramientas, conecta su cuenta de GitHub (paso 2.5) y descarga sus empresas (sección «Otra empresa, u otro
    computador»). Luego pídele abrir en su herramienta de IA la carpeta descargada (`Documentos/PMO-Empresas/<nombre>`),
    no esta, y escribir «hola»; esta carpeta del zip ya no la necesita.
- **Computador nuevo** (existe `estado.yaml` pero faltan herramientas o librerías, o el control de Git está inactivo):
  pasos 1 y 2.4, luego `git pull`, el paso 4b y termina.
- **Todo listo**: dilo en una línea y pasa al paso 3 para un proyecto nuevo (las mismas tres preguntas).

## Paso 1 — Entorno (se instala solo, con permiso)
Lo más simple para el usuario es el **instalador de doble clic** (`INSTALAR-WINDOWS.bat` / `INSTALAR-MAC.command`):
instala Python, Git y GitHub CLI, pide su nombre y correo y conecta su cuenta de GitHub, en una ventana donde sí puede
responder. Si ya lo usó, el diagnóstico sale completo y este paso se salta.
1. Revisa qué falta, sin instalar nada (desde la carpeta, **con la ruta relativa** tal cual; ver regla 18):
   - Windows: `powershell -NoProfile -ExecutionPolicy Bypass -File herramientas/preparar_pc.ps1 -SoloRevisar`
   - Mac: `bash herramientas/preparar_pc.sh --solo-revisar`
2. Si falta algo, muestra en **un solo mensaje** qué falta y para qué sirve (Python, Git y GitHub CLI, para conectar
   su cuenta y crear el repositorio privado) y ofrece dos caminos: que lo instales tú desde aquí, o que él haga doble
   clic en el instalador. En el mismo mensaje, si Git no tiene nombre y correo, pídelos.
3. Si te pide instalarlo tú:
   - Windows: `powershell -NoProfile -ExecutionPolicy Bypass -File herramientas/preparar_pc.ps1 -Instalar python,git,gh -NombreGit "<nombre>" -CorreoGit "<correo>"`
   - Mac: `bash herramientas/preparar_pc.sh --instalar python,git,gh --nombre-git "<nombre>" --correo-git "<correo>"`
   En Windows todo se instala solo para su usuario: **no aparece ninguna ventana de permiso** y nada pregunta; cada
   programa tiene un tiempo máximo y, si winget falla, usa la descarga oficial. Instala también las librerías de
   `requirements.txt` (en Mac, en `.venv`) y termina con el diagnóstico. Tarda unos minutos: avísale.
   **Instala solo con este script.** Nunca ejecutes winget, choco, brew ni instaladores por tu cuenta (tampoco
   `winget show` o `winget list` para revisar): tu consola no es interactiva y, si un comando pregunta algo (por
   ejemplo, «¿Está de acuerdo con los términos…? [Y] Sí [N] No»), queda esperando para siempre sin que el usuario
   pueda responder. Tampoco ejecutes tú los instaladores de doble clic: son para el usuario.
4. Avisos:
   - Si después de instalar, Python o Git aún no responden, tu terminal no ve el cambio: pide al usuario cerrar y
     abrir su herramienta de IA, y retoma con «continúa la instalación».
   - **Si algo se queda detenido** o falla: detén esa tarea y pídele doble clic en el instalador (desde el Explorador
     de archivos o el Finder, en la carpeta). Al terminar, que vuelva a abrir su herramienta de IA y escriba «ya corrí el
     instalador»; revisa con `-SoloRevisar` y sigue con el paso 2.
   - **Mac sin Homebrew:** su instalación pide la contraseña del Mac y no puede hacerse desde el chat: doble clic en
     `INSTALAR-MAC.command` (si macOS no lo deja abrir: clic derecho → Abrir).
   - LibreOffice (opcional, revisión visual y PDF) se ofrece después, solo si hace falta: en Windows pide permiso de
     administrador (`-Instalar libreoffice`; avisa que aparecerá la ventana de permiso).
5. Si el usuario prefiere instalar a mano, o el instalador falla, usa los enlaces de `README.md` y espera.

## Paso 2 — Empresa, Git y GitHub (repositorio siempre privado)
0. **De dónde vino esta carpeta** (lo dice el estado de inicio):
   - **Carpeta del núcleo que mantiene el usuario** (`pmo.mantenedor`): no instales aquí. Ofrece crear su carpeta de
     empresa con `nueva_empresa.py --destino` y sigue allá.
   - **Zip descargado** (sin `.git`): sigue normal; el repositorio se crea en el punto 2.
   - **Clonada del núcleo público** (`origin` = la URL de `NUCLEO.txt`): el punto 1 la desconecta sola del núcleo. El
     núcleo es público y solo su dueño puede modificarlo: los datos del usuario van a **su** repositorio privado.
   - **`origin` apunta a otro repositorio público** (por ejemplo, un *fork*): **detente**. Un fork de un repositorio
     público es público: sus datos quedarían a la vista de cualquiera. Explícalo en simple, ejecuta
     `git remote remove origin` con su permiso y sigue; recomiéndale borrar ese fork en GitHub si no lo usa.
1. **Empresa:** pregunta para qué empresa (o persona) es esta carpeta, si la ficha no lo dice. Ejecuta
   `python herramientas/nueva_empresa.py "<Nombre de la empresa>" --aqui` (crea `empresa/` desde `plantilla-empresa/`
   y su registro). Si la carpeta es para **otra** empresa distinta de una ya configurada, no la mezcles: ofrece
   crear una carpeta aparte con `python herramientas/nueva_empresa.py "<Nombre>" --destino <carpeta padre>`.
2. Si la carpeta no es repositorio: `git init`, `git branch -M main`. Si Git no tiene nombre/correo configurado, pídelos y configúralos.
   **Si el diagnóstico dice que la carpeta está DENTRO de otro repositorio**, no hagas commit ahí: explica en
   simple que el harness conviene tenerlo en un repositorio propio y privado, pide confirmación y ejecuta
   `git init` y `git branch -M main` en la carpeta del harness. Luego agrega la ruta de la carpeta (relativa a la
   raíz del repositorio padre, con `/` al final) al archivo `.git/info/exclude` del padre, para que el padre la
   ignore sin modificar nada que se suba. Informa ambas cosas en una línea.
3. Primer commit: `git add -A`, luego marca los scripts como ejecutables para Mac
   (`git update-index --chmod=+x .githooks/pre-commit herramientas/py.sh herramientas/preparar_pc.sh INSTALAR-MAC.command`)
   y `git commit -m "Instalación del harness"` (sin líneas de coautoría).
4. **Control de Git:** `git config core.hooksPath .githooks` (una vez por computador). Desde aquí, cada commit revisa
   confidenciales y planillas con cualquier asistente. Además `git config core.pager cat`: tu consola no deja salir
   de un paginador, y sin esto `git log` o `git diff` se quedarían esperando una tecla.
5. **Cuenta de GitHub** (explícalo en simple; no hace falta saber de Git):
   - Pregunta si ya tiene cuenta. Si no: basta una **cuenta personal gratuita** (no se necesita plan de pago ni
     organización). Abre la página de registro (`Start-Process https://github.com/signup` en Windows, `open
     https://github.com/signup` en Mac) y espera a que diga que la creó.
   - **Sesión:** si `gh auth status` falla, ejecuta `powershell -NoProfile -ExecutionPolicy Bypass -File
     herramientas/preparar_pc.ps1 -IniciarGitHub` (Mac: `bash herramientas/preparar_pc.sh --iniciar-github`). Abre el
     navegador en la página del código y lo deja **copiado**; no hace preguntas. Explícale: «se abrió GitHub en tu
     navegador: inicia sesión, pega el código con Ctrl+V (Cmd+V en Mac), presiona Continue y luego Authorize; después
     avísame». Si tuvo que crear la cuenta en ese momento, que vuelva a abrir github.com/login/device y pegue el código.
     Verifica con `gh auth status`. Si no se completó (el código vence en 15 minutos), repite el comando.
6. **Repositorio privado de la empresa:**
   - Con `gh` con sesión: `gh repo create <nombre-carpeta> --private --source . --push` y
     `gh repo edit --add-topic pmo-harness-empresa` (así se encuentra desde otro computador). Anota la URL en
     `repositorio_remoto` de `.harness/estado.yaml`.
   - Sin `gh`: pídele que cree en github.com un repositorio **privado y vacío** (botón «New», marcar «Private», sin
     README) y te pegue la URL; luego `git remote add origin <url>` y `git push -u origin main`.
   - Si prefiere hacerlo después, sigue: no es bloqueante (el trabajo queda guardado en el computador).
7. Nunca crees un repositorio público para una empresa, ni subas sus datos al núcleo.

## Paso 3 — El proyecto (un solo mensaje)
**Primero revisa `FICHA-DE-INICIO.md`** (en la raíz, o la ficha que el usuario indique). Si tiene respuestas:
resume en un mensaje lo que entendiste (quién eres, la empresa, el proyecto, su tipo, punto de partida, fechas,
montos, gobierno, reportes), pide confirmación y pregunta **solo lo que falte**. Usa sus respuestas en todo lo que
sigue: responsable y `autoria` en `empresa/empresa.yaml` y `proyecto.yaml`, diseño del proyecto, programa o
postulación, y la entrevista de estado si está en marcha.
Si la ficha está vacía o no existe, pregunta:
1. **De qué se trata**, en sus palabras (ej.: "seguimiento de un programa de implementación para un cliente",
   "un portafolio de acciones", "evaluar postulaciones a un fondo", "postular a un fondo CORFO").
2. Nombre del proyecto y quién lo gestiona.
3. **¿En qué punto está?** Ofrece las tres opciones tal cual:
   - **a) Parte de cero** (aún no empieza).
   - **b) Está en marcha y tengo documentos** (contratos, bases, cronogramas, reportes, actas, correos).
   - **c) Está en marcha, pero casi todo lo sé yo** (pocos o ningún documento).

Luego, siempre, diseña y crea el proyecto con la skill `nuevo-proyecto` (elige arquetipo y propone métricas,
etapas y reportes). Después, según la respuesta 3:
- **a)** Omite el paso 5: el proyecto queda listo para usar.
- **b)** Paso 5 (carga) y después `alta-proyecto` desde la fase B, que completa y ajusta el diseño con lo que digan
  los documentos. Si los documentos no cubren el estado actual (avance, riesgos, acuerdos), el alta hace la
  entrevista de estado para lo que falte.
- **c)** Haz la **entrevista de estado** de `nuevo-proyecto` (sección "Proyecto en marcha") para cargar dónde va el
  proyecto hoy. Si después aparecen documentos, se cargan en `_entrada/` y se procesan con `alta-proyecto`.

## Paso 4 — Registrar la instalación
Completa `.harness/estado.yaml` (lo crea `nueva_empresa.py`; si no existe, créalo):
```yaml
instalado: true
fecha_instalacion: AAAA-MM-DD
version_harness: "2.2.3"
empresa: <nombre>                      # dueña de esta carpeta (detalle en empresa/empresa.yaml)
nucleo:
  origen: <url del núcleo>   # por defecto, la de NUCLEO.txt (repositorio público); de ahí actualizar_nucleo.py trae las mejoras
repositorio_remoto: <url o "pendiente">
proyectos: [<slug>]
```
Haz commit: `git commit -am "Alta inicial de <slug>"` (y push si hay remoto).

## Paso 4b — Asistente de IA
Sigue `configurar-asistente`: registra el asistente con el que se está trabajando en `.harness/asistentes.yaml` y hace
su prueba de humo. Si el usuario dice que usará otra IA además (Codex, Gemini, Cursor, Copilot), explícale que la
carpeta ya sirve para todas: al abrirla con la otra IA, esta se configura sola la primera vez.

## Paso 5 — Instrucciones de carga
Muestra al usuario, de forma breve y clara:
1. La ruta exacta de su carpeta de carga: `proyectos/<slug>/_entrada/`, y que puede abrirla desde el
   explorador de VS Code (clic derecho → "Revelar en el Explorador de archivos" / "Mostrar en Finder").
2. Qué dejar, en orden de importancia (resume la tabla de `_entrada/LEEME.md` en 5 líneas). Si es una
   **postulación**, lo primero son las bases, anexos, formularios, aclaraciones y respuestas del foro, en
   `_entrada/00-bases-y-aclaraciones/`; y aclara que toda aclaración posterior también debe dejarse ahí.
3. Que no necesita ordenar ni renombrar nada; que los originales no se suben a GitHub; y que de las bases y los
   documentos de definición se guarda una copia fiel en texto en `fuentes/` (repositorio privado), para poder
   trabajar desde otro computador sin los originales. De CVs, estados financieros y datos personales solo queda una ficha.
4. Que cuando termine escriba **listo**. En ese momento sigues con `alta-proyecto` desde la fase B.

Si el usuario dice que ya dejó los documentos antes de instalar, verifica `_entrada/` y continúa directo con la fase B.

## Paso 6 — Orientación (siempre, al terminar)
1. `python herramientas/guia_proyecto.py proyectos/<slug>` → escribe `proyectos/<slug>/GUIA.md`.
2. Muestra al usuario, en un mensaje breve y claro:
   - **qué tipo de proyecto es** (arquetipos en palabras simples) y qué va a gestionar el harness;
   - **dónde está cada cosa** (3 o 4 carpetas clave) y su **rutina** recomendada;
   - los **reportes** configurados y cuándo tocan;
   - una tabla con las **skills más útiles para su tipo de proyecto**, cada una con 1 o 2 frases de ejemplo, y la
     aclaración de que **no necesita usar el nombre exacto**: basta con describir lo que quiere;
   - los **controles automáticos** en una línea cada uno, y qué hacer si bloquean algo;
   - que puede **cambiar de IA** cuando quiera: la nueva retoma desde el traspaso de cada proyecto;
   - que puede volver a ver todo diciendo «¿qué puedo hacer?» (skill `ayuda`) y que la guía completa está en `GUIA.md`.

## Otra empresa, u otro computador
- **Antes de crear la segunda empresa, pregunta cómo quiere gestionarlas** (y respeta lo que decida):
  1. ¿Son empresas independientes o parte de una misma entidad?
  2. ¿Las lleva **separadas** (una carpeta y un repositorio privado por empresa: lo recomendado si son personas
     jurídicas distintas o si alguien más verá una de ellas) o **juntas** en una sola carpeta (misma marca, mismo banco
     de antecedentes y mismo repositorio, con un proyecto por cada una)?
  3. Si las lleva separadas: ¿quiere además un **tablero único** de status con todas? Ese tablero va en una carpeta y
     un repositorio privado propios, solo para él (skill `status`, sección 3).
  Registra su decisión en `seguimiento/decisiones.csv` de la empresa principal, si existe.
- **Otra empresa** («crea la carpeta para la empresa X»): pregunta dónde dejarla (por defecto, junto a esta carpeta, en
  la carpeta padre) y ejecuta `python herramientas/nueva_empresa.py "<Nombre>" --destino <carpeta padre>` (sin
  `--sin-github` si `gh` tiene sesión: crea el repositorio privado con el tema `pmo-harness-empresa`). Luego indica que
  abra esa carpeta en VS Code y escriba «hola»; ahí se crean sus proyectos. Nunca crees proyectos de otra empresa aquí.
- **Computador nuevo** («es otro computador», «trae mis empresas», «descarga mis empresas»; también lo ofrece el
  instalador de doble clic): requiere GitHub CLI con sesión. Lista y descarga:
  - Windows: `powershell -NoProfile -ExecutionPolicy Bypass -File herramientas/preparar_pc.ps1 -Clonar -Repos <a,b|todas>`
  - Mac: `bash herramientas/preparar_pc.sh --clonar --repos <a,b|todas>`
  Primero muestra la lista (ejecuta sin `-Repos` / `--repos` solo en modo interactivo; desde el chat usa
  `gh repo list --topic pmo-harness-empresa` y pregunta cuáles). Las deja en `Documentos/PMO-Empresas/` con el control
  de Git activo (en Mac, también su `.venv`).

## Si el usuario quiere probar primero
Ofrece el paquete de prueba: copiar las subcarpetas `01-` a `08-` de `ejemplos/paquete-alta-andes/` a la carpeta `_entrada/`
de un proyecto de prueba y ejecutar el alta. El resultado se puede comparar con `ejemplos/demo-andes/`,
que es cómo debería quedar.
