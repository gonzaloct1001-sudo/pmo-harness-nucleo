# Guía rápida: instalar el PMO Harness y empezar

En unos 15 minutos tendrás tu carpeta de trabajo lista, con un asistente de IA que lleva tus proyectos. No necesitas
saber programar: un instalador de doble clic deja listo tu computador y el asistente hace el resto conversando.

## Antes de empezar (5 minutos)
Solo necesitas dos cosas; todo lo demás lo instala el harness.
1. **Una herramienta de IA que trabaje con carpetas.** La más probada es **Claude Code** dentro de **VS Code** (editor
   gratuito, code.visualstudio.com; en *Extensiones* busca «Claude Code»). También sirven Codex, Gemini Code Assist,
   Cursor, Copilot o Antigravity. Un chat en el navegador no sirve: la IA tiene que trabajar dentro de tu carpeta.
2. **Una cuenta de GitHub** (gratuita), para respaldar tu trabajo en privado. Si no la tienes, el instalador te abre la
   página y te guía.

Windows o Mac, da lo mismo. Python, Git y GitHub CLI no los instalas tú: lo hace el instalador de doble clic.

## Instalar en tres pasos
1. **Descarga.** Abre https://github.com/gonzaloct1001-sudo/pmo-harness-nucleo, botón verde **Code** → **Download ZIP**.
   No uses «Fork»: crearía una copia pública.
2. **Descomprime y ordena.** Extrae el zip, cambia el nombre de la carpeta por el de tu empresa (sin tildes ni espacios,
   por ejemplo `Consultora-Sur`) y muévela a Documentos. No la dejes dentro de OneDrive, Dropbox ni Google Drive. Si
   solo ves otra carpeta adentro, entra en ella: esa es la correcta.
3. **Doble clic en el instalador.** En Windows, `INSTALAR-WINDOWS.bat` (si aparece «Windows protegió su PC»: *Más
   información* → *Ejecutar de todas formas*); en Mac, `INSTALAR-MAC.command` (clic derecho → Abrir). Presiona Enter,
   responde si ya tienes cuenta de GitHub y conecta tu cuenta cuando se abra el navegador (el código ya está copiado:
   Ctrl+V, *Continue*, *Authorize*). Cuando diga «Listo», cierra la ventana.

Luego abre la carpeta en tu herramienta de IA (*Archivo → Abrir carpeta*), acepta confiar en la carpeta, abre el chat y
escribe **hola**. Desde ahí el asistente te guía con preguntas de opción.

## Las preguntas que te hará (y qué responder)
El asistente pregunta de a una o dos, con opciones; basta con responder la letra o con tus palabras. Si no sabes algo,
di «no sé» y sigue con lo recomendado. Todo se puede cambiar después.

| Te preguntará | Opciones | Si no sabes |
|---|---|---|
| ¿Primera vez o ya usas el harness en otro computador? | Primera vez · Otro computador | Primera vez |
| ¿Para quién es esta carpeta? | A) mi empresa · B) una empresa cliente · C) uso personal, y el nombre | Tu nombre |
| ¿Qué vas a llevar primero? | Proyecto o programa · postulación · finanzas · investigación · evaluar propuestas · estudio · equipo de software · cartera · todavía no sé | Todavía no sé: lo decide contigo después |
| ¿En qué punto está? | a) parte de cero · b) en marcha y tengo documentos · c) en marcha, pero casi todo lo sé yo | a) |
| ¿Tienes formatos propios (informes, minutas, plantillas, logo)? | A) sí, los dejo en la carpeta de entrada de la empresa · B) no, usa los del harness · C) después | B) |
| ¿Respaldo en GitHub ahora? | Sí (recomendado) · después | Sí |
| ¿Reporte de status semanal en este computador? | No · lunes 9:00 · otro día y hora | No |
| Solo con Claude: ¿quieres revisar y encargar cosas desde el celular con el PC apagado? | A) no por ahora · B) sí, explícame y elijo qué programar | A) |

Si completas `FICHA-DE-INICIO.md` antes de decir «hola», el asistente la lee y solo pregunta lo que falte.

## Tu primer proyecto en diez minutos
Cuéntale al asistente de qué se trata, como a un colega: «quiero postular al fondo X», «llevo la ejecución del
proyecto Y», «quiero llevar las finanzas de la empresa». Él elige el tipo, te propone cómo medirlo y qué reportes
tendrá, y tú ajustas.
- **Si partes de cero**, queda listo para usar.
- **Si ya está en marcha y tienes documentos** (contratos, bases, cronogramas, reportes, actas, correos), déjalos en la
  carpeta que te indique, sin ordenar ni renombrar, y escribe «listo». El asistente los lee, configura todo y te
  pregunta solo lo que no pudo resolver.
- **Si está en marcha pero casi todo lo sabes tú**, te hace una entrevista corta y carga el estado actual.

Al final te muestra la guía de tu proyecto: qué va a gestionar, dónde está cada cosa y qué puedes pedir.

## Cómo seguir cada día
1. Abre la carpeta y escribe «hola»: verás cómo van tus proyectos en pocas líneas.
2. Pide lo que necesites con tus palabras: «estas son mis notas de la reunión», «prepara el informe de esta semana»,
   «¿qué llevo al comité?».
3. Deja los documentos nuevos en la carpeta de entrada y di «procesa lo nuevo».
4. Al terminar, «guarda»: tu trabajo queda respaldado en tu repositorio privado.

Si no sabes qué pedir, «¿qué puedo hacer?» te muestra todo lo disponible para tu tipo de proyecto.

## Cambiar algo después
Nada queda fijo. Di «quiero cambiar…» o «configura…» y el asistente te muestra qué cambia, pide tu sí y lo aplica:
- **Tus formatos:** «adopta mis formatos» (deja los archivos en la carpeta de entrada de la empresa).
- **La marca:** «usa este logo y estos colores en todo».
- **La IA:** abre la carpeta con otra herramienta y escribe «hola»; se configura sola.
- **El modo nube:** «¿puedo revisar las cosas desde el celular?» para activarlo tarea por tarea; «pausa la nube» para
  detenerlo.
- **Otra empresa u otro computador:** «crea la carpeta para la empresa X» · «trae mis empresas».
- **Versión nueva del harness:** «actualiza el harness»; tus datos y ajustes no se tocan.

Todo queda en el historial: si algo no te gusta, «vuelve a dejarlo como estaba».

## Si algo falla
| Pasa esto | Haz esto |
|---|---|
| La IA no reconoce el harness al decir «hola» | Escríbele: «lee el archivo AGENTS.md y sigue sus instrucciones» |
| Algo se queda detenido o pregunta «[Y] Sí [N] No» | Di «cancela esa tarea», haz doble clic en el instalador y luego escribe «ya corrí el instalador» |
| Windows dice «protegió su PC» | *Más información* → *Ejecutar de todas formas* |
| La conexión con GitHub no se completó | Di «conecta mi cuenta de GitHub» |
| Dice que falta Python aunque se instaló | Cierra y vuelve a abrir tu herramienta de IA |
| Un control no deja guardar un archivo | Es a propósito: es confidencial. El asistente te explica |
| «El nombre del archivo es demasiado largo» (Windows) | Usa una carpeta más corta (por ejemplo, `Documentos/Consultora-Sur`) |

Para más detalle, `MANUAL-DE-USUARIO.md`. Si nada funciona, pídele al asistente «revisa el entorno» y envía ese
resultado a quien te entregó el harness.
