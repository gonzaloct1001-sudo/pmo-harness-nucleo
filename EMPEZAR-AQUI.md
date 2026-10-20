# Guía de inicio del PMO Harness

En unos 15 minutos tendrás tu carpeta de trabajo lista, con un asistente de IA que te ayuda a gestionar tus proyectos y
postulaciones. No necesitas saber programar: un instalador de doble clic deja listo tu computador y el asistente hace
el resto de la parte técnica.

---

## Antes de empezar: lo único que debes instalar tú

**1. Una herramienta de IA que trabaje con carpetas** (elige una):

| Herramienta | Qué es |
|---|---|
| **Google Antigravity** | Editor con IA incluida (descarga en antigravity.google) |
| **VS Code** + una extensión de IA | Editor gratuito (code.visualstudio.com). Dentro de VS Code, en *Extensiones*, instala una de estas: **Claude Code**, **Codex** (OpenAI), **Gemini Code Assist** o **GitHub Copilot** |
| **Claude Code** o **Cursor** | Aplicaciones con IA que también sirven |

Cada herramienta te pedirá su propia cuenta (algunas son de pago). Un chat en el navegador, como ChatGPT o Gemini en la
web, **no sirve**: la IA necesita trabajar dentro de tu carpeta.

**2. Una cuenta de GitHub** (gratuita) para respaldar tu trabajo en la nube de forma **privada**. Si no la tienes, el
instalador del paso 3 te abre la página y te guía para crearla (correo, contraseña, nombre de usuario y un código que
llega a tu correo). No necesitas una cuenta de pago ni una "organización". Si prefieres, créala antes en
https://github.com/signup.

Python, Git y lo demás **no los instalas tú a mano**: lo hace el instalador del paso 3.

---

## Paso 1. Descarga el harness

1. Abre **https://github.com/gonzaloct1001-sudo/pmo-harness-nucleo**
2. Haz clic en el botón verde **Code** y luego en **Download ZIP**.

> ⚠️ **No uses el botón «Fork».** Crearía una copia pública, y lo que guardes ahí quedaría a la vista de cualquiera.
> Con el zip, tu trabajo queda en un repositorio privado tuyo.

¿Prefieres que lo haga la IA? Abre tu herramienta de IA y escríbele:
*«Descarga el PMO Harness desde https://github.com/gonzaloct1001-sudo/pmo-harness-nucleo en una carpeta nueva llamada
Mi-Empresa dentro de Documentos.»* Luego sigue en el paso 3.

## Paso 2. Descomprime y deja la carpeta lista

1. **Descomprime el zip:**
   - **Windows:** clic derecho sobre el archivo → **Extraer todo…** → **Extraer**.
   - **Mac:** doble clic sobre el archivo.
2. Aparece una carpeta llamada **`pmo-harness-nucleo-main`** (en Windows puede quedar una dentro de otra con el mismo
   nombre: usa la de adentro).
3. **Cámbiale el nombre** por el de tu empresa, sin tildes ni espacios. Por ejemplo, `Consultora-Sur`.
4. **Muévela a Documentos.** Evita carpetas muy profundas o con nombres largos, y **no la dejes dentro de Dropbox,
   OneDrive ni Google Drive**: sincronizan por su cuenta y pueden dañar el historial. El respaldo y el acceso desde
   otros computadores los da GitHub. Si tu carpeta Documentos está en OneDrive, el instalador te dice dónde dejarla.
5. **Comprueba:** al abrirla, debes ver archivos como `AGENTS.md`, `README.md` y la carpeta `herramientas`. Si solo ves
   otra carpeta, entra en ella: esa es la correcta.

> **Una carpeta = una empresa.** Si llevas proyectos de varias empresas, después el asistente te crea una carpeta para
> cada una, con un solo pedido.

## Paso 3. Doble clic en el instalador

Dentro de tu carpeta, haz **doble clic** en:
- **Windows:** `INSTALAR-WINDOWS.bat`. Si aparece «Windows protegió su PC», haz clic en **Más información** y luego en
  **Ejecutar de todas formas** (pasa con los archivos descargados de internet).
- **Mac:** `INSTALAR-MAC.command`. Si macOS no lo deja abrir: clic derecho → **Abrir** → **Abrir**. En Mac te pedirá la
  contraseña del computador (no se ve mientras la escribes).

Se abre una ventana que hace todo sola:
1. Presiona **Enter** para comenzar. Instala Python, Git y GitHub CLI (en Windows, solo para tu usuario: no pide
   permisos de administrador). Tarda unos minutos.
2. Te pregunta si ya tienes **cuenta en GitHub**:
   - **Si la tienes**, presiona Enter.
   - **Si no**, escribe N y presiona Enter: se abre la página para crearla y la ventana te indica los pasos (correo,
     contraseña y nombre de usuario; un desafío para comprobar que eres una persona; el código que llega a tu correo).
     Cuando termines, vuelve a la ventana y presiona Enter.
3. Se abre el navegador para **conectar tu cuenta**:
   - inicia sesión en GitHub si te lo pide;
   - donde pide un código, pega con **Ctrl+V** (Mac: **Cmd+V**): ya está copiado, y también aparece en la ventana;
   - presiona **Continue** y luego **Authorize**.

   No tienes que escribir tu nombre ni tu correo: se toman de tu cuenta de GitHub.
4. Cuando diga **«Listo»**, presiona Enter para cerrar la ventana.

Si no respondes una pregunta, la ventana sigue sola después de unos minutos: nada queda detenido. Lo que falte, el
asistente lo completa contigo en el chat.

## Paso 4. Abre la carpeta en tu herramienta de IA y escribe «hola»

1. En tu herramienta: menú **Archivo → Abrir carpeta** (*File → Open Folder*) y elige la carpeta del paso 2. Si ya la
   tenías abierta, ciérrala y vuelve a abrirla para que vea lo recién instalado.
2. Si pregunta si confías en los autores de la carpeta, responde **Sí**.
3. Abre el **chat** de la IA (en VS Code, el ícono de la extensión en la barra lateral) y escribe **«hola»**.

El asistente se presenta y te guía:
- **Permisos.** Tu herramienta te preguntará si permites ejecutar comandos. Acepta los del harness (revisar el
  computador, guardar en Git). Si algo te parece raro, pregunta: «¿para qué es esto?».
- Si te saltaste el paso 3, el asistente te ofrece instalar desde el chat o hacer el doble clic.
- Al final crea **tu repositorio privado** y te confirma que tu trabajo queda respaldado.

## Paso 5. Elige las opciones que calzan contigo

El asistente te hará unas pocas preguntas. Puedes responder con tus palabras; si no sabes algo, di «no sé».

| Te preguntará… | Qué responder |
|---|---|
| ¿De qué empresa es esta carpeta? | El nombre de tu empresa, o tu nombre si es de uso personal |
| ¿De qué se trata tu proyecto? | Cuéntalo como a un colega: «quiero postular al fondo X de CORFO», «llevo la ejecución del proyecto Y que ganamos», «evalúo postulaciones de terceros», «necesito una evaluación económica» |
| ¿En qué punto está? | **a)** parte de cero · **b)** está en marcha y tengo documentos · **c)** está en marcha, pero casi todo lo sé yo |
| ¿Tienes documentos? | Si es **b)**, déjalos en la carpeta que te indique (`proyectos/<tu-proyecto>/_entrada/`), sin ordenar ni renombrar, y escribe **listo** |

El asistente elige el tipo de proyecto, lo configura y te muestra la **guía de tu proyecto** con lo que puedes pedir.

¿Quieres que pregunte menos? Antes del paso 4, abre `FICHA-DE-INICIO.md`, completa lo que sepas y guárdalo.

---

## Listo. Así se usa todos los días

Cada vez que abras la carpeta y escribas «hola», el asistente te muestra en pocas líneas **cómo van tus proyectos**:
semáforo, lo que vence pronto y las decisiones que te esperan.

Pídele las cosas con tus palabras, por ejemplo:
- «¿Cómo vamos?» · «dame el reporte de status» (página web; te ofrece dejarlo listo cada semana)
- «Prepara la postulación» · «¿qué exigen las bases?» · «¿qué falta para entregar?»
- «Tengo reunión de avance el jueves, ¿qué llevo?» · «estas son mis notas de la reunión»
- «Genera el informe de avance» · «arma el flujo de caja con estos supuestos»
- «Llegaron los nuevos lineamientos del directorio, ¿qué cambia?»
- «¿Qué puedo hacer?» (muestra todo lo disponible) · «guarda» (respalda en GitHub)

**Más adelante:**
- **Otra empresa:** «crea la carpeta para la empresa X». Te preguntará si son empresas independientes o de una misma
  entidad, y si quieres ver todas juntas en un **tablero único** (va en una carpeta y un repositorio privado aparte, solo
  tuyo) o el status de cada una por separado.
- **Otro computador:** antes de dejar el primero, dile «guarda». En el otro, instala tu herramienta de IA, descarga el
  zip y haz doble clic en el instalador (pasos 1 a 3): después de conectar GitHub te ofrece descargar tus empresas.
  Abre en tu herramienta de IA la carpeta descargada (no la del zip) y escribe «hola». Desde ahí, cada vez que cambies
  de computador: «guarda» al terminar en uno y «hola» al empezar en el otro (te ofrece traer lo último).
- **Otra IA:** abre la carpeta con la nueva y escribe «hola». Retoma donde quedaste.
- **Versión nueva del harness:** «actualiza el harness». Tus proyectos y datos no se tocan.

## Si algo no funciona

| Pasa esto | Haz esto |
|---|---|
| La IA no reconoce el harness al decir «hola» | Escríbele: «lee el archivo AGENTS.md y sigue sus instrucciones» |
| En el chat, algo se queda detenido o pregunta «[Y] Sí [N] No» y no puedes escribir | Dile «cancela esa tarea». Luego haz el paso 3 (doble clic en el instalador). Al terminar, vuelve a abrir tu herramienta de IA y escribe «ya corrí el instalador» |
| Windows dice «Windows protegió su PC» al abrir el instalador | Haz clic en **Más información** y luego en **Ejecutar de todas formas** |
| Te piden aceptar un permiso de Windows y no ves ninguna ventana | Busca en la barra de tareas un ícono con escudo que parpadea y haz clic en él (solo pasa con instalaciones opcionales, como LibreOffice) |
| La conexión con GitHub no se completó | Pide en el chat «conecta mi cuenta de GitHub»: se abre de nuevo el navegador con el código copiado |
| Dice que falta Python aunque se instaló | Cierra y vuelve a abrir tu herramienta de IA |
| «El nombre del archivo es demasiado largo» (Windows) | Usa una carpeta más corta (por ejemplo, `Documentos/Consultora-Sur`) o deja que el asistente active las rutas largas |
| Un control no deja guardar un archivo | Es a propósito: ese archivo es confidencial y no debe subirse. El asistente te explica qué hacer |

Manual completo: `MANUAL-DE-USUARIO.md`.
