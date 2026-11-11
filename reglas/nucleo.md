# Reglas: núcleo, método y capacidad

Detalle de los principios 8, 12, 19 y 20 del mapa (`AGENTS.md`). Léelo al tocar algo del núcleo, al afirmar hechos
del mundo o al elegir con qué modelo corre un paso.

8. **Lo específico va al proyecto (o a la empresa):** nombres de reportes, métricas del dominio, políticas y
   cálculos propios se guardan en `proyectos/<slug>/` o, si son comunes a todos los proyectos, en `empresa/`; nunca
   en el núcleo ni en los arquetipos. Una skill propia va en `.claude/skills/<propia>/` (sobrevive a las
   actualizaciones); una regla propia, en el `CLAUDE.md` del proyecto o en `empresa/estilo.md`; una herramienta, un
   hook o una prueba propia, en `empresa/extensiones/` (su `LEEME.md` explica cómo: se importa lo del núcleo y se
   escribe solo la diferencia, con una prueba propia que la actualización ejecuta antes y después). Lo que el núcleo
   debería traer y no trae se anota con `mejoras.py --anotar`.
   **El núcleo no se edita en una carpeta de empresa** (en Claude Code lo impide el hook `proteger_nucleo`): un
   archivo del núcleo se reemplaza al actualizar. Si hay que corregir algo ya, se resuelve con una extensión y se
   anota la mejora. La actualización, por su parte, nunca pisa lo propio en silencio: conserva lo modificado si el
   núcleo nuevo no lo cambia, renombra lo propio que choca de nombre con algo nuevo (`<nombre>-propia`), fusiona
   `.gitignore`, `requirements.txt` y `.claude/settings.json`, y respalda y avisa lo demás. El catastro
   (`.harness/nucleo-instalado.csv`) dice en cualquier momento qué se modificó o falta
   (`actualizar_nucleo.py --verificar`); un cambio involuntario vuelve a su original con `--restaurar`, solo con el sí
   del usuario.
12. **Al modificar el núcleo** (skills, herramientas, arquetipos, plantillas, reglas) ejecuta
    `python pruebas/ejecutar_pruebas.py` y no des el cambio por terminado si alguna prueba falla. Esto aplica al
    mantenedor; en una carpeta de empresa el núcleo no se modifica.
19. **Hechos del mundo, con protocolo.** Si una tarea exige afirmar hechos de afuera (terceros, registros, mercado,
    normativa, tecnología) que sostienen una decisión o un entregable, no los escribas de memoria: ofrece abrir una
    investigación (skill `investigar`, parte en sondeo); si el usuario sigue sin ella, marca esas afirmaciones como
    sin verificar. Las firmas de las puertas P0, P2 y P5 son siempre del usuario.
20. **Capacidad según la tarea, no según el costo.** Nivel **alto** (juicio que nadie puede comprobar: diseñar un
    proyecto, evaluar, refutar, red team, encuadrar una investigación, revisar antes de entregar): el modelo más capaz
    disponible, con contexto limpio. Nivel **medio** (análisis con datos, borradores, lectura con extracción): un
    modelo competente y rápido. Nivel **bajo** (transcribir, formatear, validar, buscar): el más rápido. Los subagentes
    de `.claude/agents/` traen su nivel en `model:`; si `empresa/empresa.yaml` define `capacidad`, invoca cada subagente
    con ese modelo. El nivel de cada skill está en `.claude/skills/ayuda/catalogo.yaml` (`capacidad`). Si una tarea de
    nivel alto corre en un modelo liviano, dilo en una línea al usuario y sigue. Cómo se elige el modelo en cada
    herramienta: `.claude/skills/configurar/references/asistentes.md`.
