# Reglas: cómo se trabaja

Detalle de los principios 4, 9, 10, 11, 17, 18, 21 y 23 del mapa (`AGENTS.md`). Léelo al empezar una tarea que
modifique registros o que vaya a durar más de un rato.

4. **Pide confirmación antes de modificar registros** (riesgos, cronograma, línea base, cambios, ítems), salvo en
   `nuevo-proyecto` (en los dos caminos: desde la descripción o con documentos), que aplica y registra sus decisiones
   para revisión en bloque. Una confirmación por lote, no por fila: muestra lo que vas a cambiar y pide un sí.
9. **Decisiones sensibles** (inversiones, técnicas, legales, de salud): el harness organiza, mide y plantea
   preguntas; la decisión es del usuario y de los profesionales competentes. Nunca la des por tomada.
10. Al terminar una tarea que modificó archivos, actualiza el traspaso (17) y sugiere `guardar-cambios` en una línea.
11. **Si un control bloquea o reporta un problema** (hook de tu herramienta o control de Git), corrígelo antes de
    seguir; no lo esquives (nunca uses `git commit --no-verify`). Si el control está equivocado, anótalo con
    `mejoras.py --anotar` y dile al usuario; no lo apagues.
17. **Traspaso entre sesiones y asistentes.** Al terminar cada tarea que cambió algo, y en cada hito de una tarea
    larga, actualiza `proyectos/<slug>/seguimiento/traspaso.md`: fecha, asistente, tarea y estado, hecho, próximo
    paso, decisiones pendientes, archivos clave, **qué comprobaste**, **qué no pudiste comprobar** y **dónde tuviste
    que adivinar**. Reemplaza el contenido (el historial queda en Git). Así otra sesión, otro computador u otro
    asistente retoma sin que el usuario repita nada. Si tuviste que adivinar, una skill no cubrió el caso, una
    instrucción estorbó o un script falló, anótalo con `python herramientas/mejoras.py --anotar` (con evidencia, sin
    datos del cliente); nunca edites el núcleo: lo decide el mantenedor.
18. **Tu consola no es interactiva.** No ejecutes comandos que esperen una respuesta (S/N, términos que aceptar,
    contraseñas, un editor): quedan detenidos y el usuario no puede contestar. Para instalar usa solo
    `herramientas/preparar_pc.ps1` o `preparar_pc.sh` (nunca winget, choco ni brew directos; las bibliotecas del
    nivel especialista del análisis, solo con `python herramientas/experto.py instalar` y con el sí del usuario); para Git, usa `-m`,
    nunca `-i`, y `git --no-pager` si la carpeta no tiene `core.pager cat`. Ejecuta los scripts desde la carpeta con
    su ruta relativa (`herramientas/...`): algunos controles de seguridad detienen PowerShell si su línea de comando
    trae la ruta completa de la carpeta abierta en el editor. Si algo queda esperando, detenlo y ofrece el instalador
    de doble clic (`INSTALAR-WINDOWS.bat` o `INSTALAR-MAC.command`), que abre una ventana donde el usuario sí puede
    responder; tú no lo ejecutes.
21. **Cuida el contexto.** No releas archivos que ya tienes en la conversación; pide resúmenes a los scripts
    (`estado.py`, `status.py --breve`, `evaluar_metricas.py`) en vez de leer CSV o YAML enteros; para lotes de
    documentos usa el subagente `lector-documental`; lee las `references/` de una skill y las `reglas/` solo en la
    fase que las usa. La calidad del contexto baja antes de que la ventana se llene: una tarea larga se parte en
    hitos con traspaso, y después de unas 120 acciones conviene guardar y seguir en una sesión nueva (en Claude Code
    lo recuerda un hook). Para ver cuánto pesa cada pieza: `python herramientas/medir_contexto.py`.
23. **Plan antes de ejecutar, en proporción.** Por defecto (`trabajo.modo: proporcional` en `empresa/empresa.yaml`):
    una tarea chica y reversible se ejecuta de inmediato. Una tarea **grande** (toca varios registros o archivos, o
    toma más de un rato), **ambigua** (hay más de una forma razonable de entenderla) o **difícil de deshacer**
    (reemplaza una línea base, cierra un período, envía o publica algo) parte con un plan de hasta cinco líneas: qué
    entendí, qué voy a hacer, qué voy a tocar, qué necesito de ti. Cierra con tres salidas: «ejecuta», «ajusta» (y
    qué) o «plan detallado» (un documento, o una página con la skill `explicar`). Ese plan vale como la confirmación
    del principio 4: no se pregunta dos veces. Si el usuario pide ir directo («hazlo ya», «sin plan», «ejecuta»), se
    ejecuta. `siempre`: toda tarea parte con el plan. `directo`: nunca se ofrece (el principio 4 sigue vigente para
    modificar registros). En una tarea de la nube no hay a quién preguntar: el plan se escribe en el pedido y se
    ejecuta lo que la tarea autoriza. El estado de inicio avisa cuando el modo no es `proporcional`.

## Modo por defecto
Si el alta del proyecto está incompleta (`induccion.estado` distinto de `completa`), trabaja igual con los valores
por defecto. Menciona una sola vez, al final, qué pendientes críticos afectan el resultado.
