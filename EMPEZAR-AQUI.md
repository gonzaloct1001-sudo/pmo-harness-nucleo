# Guía de inicio del PMO Harness

En unos 15 minutos tendrás tu carpeta de trabajo lista, con un asistente de IA que te ayuda a gestionar tus proyectos y
postulaciones. No necesitas saber programar: el asistente hace la parte técnica y te pide permiso antes de instalar algo.

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
asistente te abre la página de registro en el paso 4. No necesitas una cuenta de pago ni una "organización".

Python, Git y lo demás **no los instalas tú**: lo hace el asistente con tu permiso.

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
4. **Muévela a Documentos.** Evita carpetas muy profundas o con nombres largos.
5. **Comprueba:** al abrirla, debes ver archivos como `AGENTS.md`, `README.md` y la carpeta `herramientas`. Si solo ves
   otra carpeta, entra en ella: esa es la correcta.

> **Una carpeta = una empresa.** Si llevas proyectos de varias empresas, después el asistente te crea una carpeta para
> cada una, con un solo pedido.

## Paso 3. Abre la carpeta en tu herramienta de IA

1. En tu herramienta: menú **Archivo → Abrir carpeta** (*File → Open Folder*) y elige la carpeta del paso 2.
2. Si pregunta si confías en los autores de la carpeta, responde **Sí**.
3. Abre el **chat** de la IA (en VS Code, el ícono de la extensión en la barra lateral).

## Paso 4. Escribe «hola» y responde

El asistente se presenta y te guía. Durante la instalación:

- **Permisos.** Tu herramienta te preguntará si permites ejecutar comandos. Acepta los del harness (instalar, revisar el
  computador, guardar en Git). Si algo te parece raro, pregunta: «¿para qué es esto?».
- **Instalación.** Te dirá qué falta (por ejemplo, Python o Git) y te pedirá permiso. Responde **sí**. En Windows pueden
  aparecer ventanas pidiendo confirmación: acéptalas. En Mac puede pedirte hacer doble clic en `INSTALAR-MAC.command`
  (si no abre: clic derecho → **Abrir**) y escribir la contraseña del Mac.
- **GitHub.** Si no tienes cuenta, te abre la página para crearla. Para conectar tu cuenta abre una ventana: presiona
  **Enter**, pega en el navegador el código que aparece y presiona **Authorize**. Luego vuelve al chat y avisa.
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
- **Otro computador:** instala tu herramienta de IA, abre cualquier carpeta y pide «descarga mis empresas».
- **Otra IA:** abre la carpeta con la nueva y escribe «hola». Retoma donde quedaste.
- **Versión nueva del harness:** «actualiza el harness». Tus proyectos y datos no se tocan.

## Si algo no funciona

| Pasa esto | Haz esto |
|---|---|
| La IA no reconoce el harness al decir «hola» | Escríbele: «lee el archivo AGENTS.md y sigue sus instrucciones» |
| Dice que falta Python aunque se instaló | Cierra y vuelve a abrir tu herramienta de IA |
| «El nombre del archivo es demasiado largo» (Windows) | Usa una carpeta más corta (por ejemplo, `Documentos/Consultora-Sur`) o deja que el asistente active las rutas largas |
| Un control no deja guardar un archivo | Es a propósito: ese archivo es confidencial y no debe subirse. El asistente te explica qué hacer |

Manual completo: `MANUAL-DE-USUARIO.md`.
