# PMO Harness — reglas generales (para cualquier asistente de IA)

Marco de trabajo para diseñar, cargar y gestionar proyectos de cualquier tipo con un asistente de IA que trabaje
sobre carpetas y ejecute comandos: Claude Code, OpenAI Codex, Gemini (CLI o Code Assist), Google Antigravity, Cursor,
GitHub Copilot u otro. **Este archivo es la fuente única de reglas**: `CLAUDE.md`, `GEMINI.md` y cualquier otro archivo de entrada
solo remiten aquí. Si llegaste por otro archivo, sigue leyendo este completo.

Responde siempre en español (Chile), con tono profesional, directo y sin tecnicismos innecesarios.

## Al iniciar cada sesión (paso 0, siempre)

1. **Estado.** Ejecuta `python herramientas/estado.py --remoto` y usa su bloque `[Estado del PMO Harness]`. Si tu
   herramienta ya lo entregó al abrir la sesión (Claude Code lo hace con un hook), no lo repitas.
   Comando de Python: `python`; en Windows, si no responde, `py`; en Mac, `.venv/bin/python` (la crea el instalador;
   el `python3` del sistema no tiene las librerías).
   Si ninguno funciona, Python no está instalado: ofrece el instalador (`INSTALAR-WINDOWS.bat` o
   `INSTALAR-MAC.command`, o la skill `instalar`, que puede ejecutarlo por ti con permiso del usuario).
2. **Identidad.** Si el estado indica que tu asistente no está registrado en `.harness/asistentes.yaml`, sigue
   `.claude/skills/configurar-asistente/SKILL.md` antes de la primera tarea (toma un par de minutos y no pregunta
   casi nada). Si eres un asistente distinto del último que trabajó (campo `asistente` de los traspasos), aplica
   su sección «Cambio de asistente a mitad de camino».
3. **Dónde estamos.** Si el estado trae «Status de los proyectos», muéstraselo al usuario en 2 a 4 líneas junto al
   saludo: rojos y amarillos con su motivo, lo que vence pronto y las decisiones pendientes. El detalle y el reporte
   web, con la skill `status`.
4. Según el estado:
   - **No instalado** (no existe `.harness/estado.yaml`): sea cual sea el primer mensaje del usuario (incluso un
     saludo), respóndelo brevemente y ofrece comenzar con la skill `instalar`. Menciona que puede completar antes
     `FICHA-DE-INICIO.md` (o que la usarás si ya la completó) y que el manual está en `MANUAL-DE-USUARIO.md`.
   - **Traspaso pendiente:** si un proyecto tiene una tarea en curso o un próximo paso, menciónalo en una línea y
     ofrece continuar.
   - **Material sin procesar** en `_entrada/` o un **alta a medio camino** (`_entrada/_procesado/avance-alta.md`):
     menciónalo en una línea y ofrece continuar.
   - **Instalado sin proyectos:** ofrece crear uno (`nuevo-proyecto`) o cargar documentos (`alta-proyecto`),
     preguntando si parte de cero, está en marcha con documentos o está en marcha sin documentos.
   - **Controles de Git inactivos:** ofrece activarlos (`git config core.hooksPath .githooks`).
   - **Commits en GitHub que no están en este computador:** ofrece `git pull` antes de trabajar.
5. Si nada de lo anterior aplica, atiende directamente lo que pida el usuario.

## Organización

**El núcleo se publica en un repositorio público** (URL en la primera línea de `NUCLEO.txt`): cualquiera lo descarga,
solo su dueño lo modifica. Quien lo descarga o clona lo instala como **su** carpeta de empresa con **su** repositorio
privado (`instalar` desconecta la copia del núcleo antes de crear el privado). **Nunca uses «Fork»:** un fork de un
repositorio público es público. La carpeta del dueño está marcada (`git config pmo.mantenedor true`) y no lleva
empresas ni proyectos.

Una carpeta del harness = un repositorio privado = **una empresa** (o persona); para otra empresa, otra carpeta
(`nueva_empresa.py`). **Nunca mezcles datos de dos empresas.** Si el usuario lleva varias, **pregúntale** si son
independientes o una misma entidad, separadas o juntas, y si quiere un **tablero único** o uno por empresa; el tablero
único va en una carpeta de panel con su propio repositorio privado (skill `status`).

1. **Núcleo genérico** — sirve para cualquier proyecto. No se escribe nada específico de un proyecto aquí.
   `.claude/skills/` procedimientos (skills) · `.claude/agents/` roles (subagentes) · `herramientas/` scripts ·
   `.githooks/` controles de Git · `plantilla-proyecto/`, `plantilla-subproyecto/`, `plantilla-empresa/` bases.
   `NUCLEO.txt` lista las rutas del núcleo: se reemplazan al actualizarlo (`actualizar_nucleo.py`); todo lo demás
   es de la empresa y nunca se toca al actualizar.
2. **Arquetipos** — `arquetipos/<nombre>/`: estructura y guía de cada forma de trabajo. `ejecucion` (plan, hitos,
   contrato, valor ganado, ruta crítica) · `obra` (RFI, no conformidades, inspecciones, estados de pago) · `agil`
   (backlog, sprints, DORA, ADR, deuda) · `cartera` (ítems con etapas y métricas) · `evaluacion` (propuestas de
   terceros con pauta) · `postulacion` (ganar un fondo, licitación o concurso: matriz de cumplimiento, pauta inversa,
   red team, presupuesto con controles) · `programa` (contrato padre con subproyectos, presupuesto macro, personas
   compartidas, Gantt macro) · `estudio` (preguntas, supuestos, modelo económico, recomendación) · `investigacion`
   (hechos del mundo verificados con fuente, hipótesis asesinas, refutador, árbitro, puertas que firma quien decide) ·
   `finanzas` (plan de cuentas, presupuesto, cierre mensual reabrible, resultados, balance, caja, forecast,
   proyección, indicadores; consume la contabilidad). Un proyecto puede combinar arquetipos.
3. **Empresa** — `empresa/`: lo común a todos los proyectos de la empresa dueña de la carpeta: `empresa.yaml`
   (identidad, autoría, marca, formato, política de réplicas), banco de antecedentes (`contenidos/`: descripción,
   experiencia, CVs, certificados con vigencia), `estilo.md`, `marca/`, `plantillas/` y formatos de reportes
   comunes (`reportes/catalogo/`), más `formatos/` (registro de los formatos propios adoptados) y `_entrada/` (donde
   se dejan los formatos y archivos base para adoptarlos; no se sube a Git). Los proyectos heredan de aquí lo que no definen.
4. **Proyecto** — `proyectos/<slug>/`: todo lo particular (datos, métricas, reglas, reportes con nombre propio,
   plantillas, marca, scripts de cálculo del dominio).

Además:
- `biblioteca/perfiles/` → diseños reutilizables. Incluye perfiles de convocatorias: `fondo-corfo`, `fondo-anid`,
  `licitacion-mercado-publico`, `fondo-regional-o-sectorial`, `licitacion-privada-rfp` (siempre se confirman contra las bases).
- `biblioteca/dominios/` → cartuchos de dominio para investigaciones (mapa de fuentes y modos de falla de un rubro);
  el núcleo trae `propiedad-industrial`; los demás son de la empresa.
- `empresa/investigacion/` → ajustes, preferencias y lecciones de investigación de la empresa (los escribe
  `investigacion.py`; una actualización del núcleo nunca los toca).
- `ejemplos/` → material ficticio de prueba (uno por arquetipo, listados en `README.md`). No son proyectos reales.
- `.harness/estado.yaml` → registro de la instalación (empresa, origen del núcleo) · `.harness/asistentes.yaml` →
  asistentes de IA configurados · `pruebas/` → batería de pruebas.

## Contrato común (todos los proyectos)
- `proyecto.yaml` → identidad, `arquetipos`, gobierno, formato, umbrales, estado del alta.
- `metricas/metricas.yaml` (propias) y `metricas/metricas-<arquetipo>.yaml` (de los arquetipos) → definiciones
  y reglas · `metricas/mediciones.csv` → valores.
- `reportes/catalogo/` → reportes del proyecto · `riesgos/` · `seguimiento/` (decisiones, acuerdos, traspaso) · `contexto/`.
- `fuentes/` → réplicas fieles en Markdown de las bases y documentos de definición (ver regla 6): permiten trabajar
  en cualquier computador sin los originales.
Gracias a esto, reportes, consistencia, riesgos y reuniones funcionan igual en cualquier tipo de proyecto.

## Proyecto activo

1. Si el usuario nombra un proyecto, usa `proyectos/<slug>/`. Si nombra un **subproyecto** de un programa, usa
   `proyectos/<programa>/subproyectos/<id>/` (su `proyecto.yaml` hereda del programa lo que no define). Lo del
   programa completo (contrato, enmiendas, presupuesto, contingencia, personas, Gantt macro) va en la carpeta del programa.
2. Si hay un solo proyecto en `proyectos/`, usa ese. Los de `ejemplos/` solo se usan si el usuario los nombra.
3. Si hay duda, pregunta cuál. Nunca mezcles datos de dos proyectos, ni de dos subproyectos en un mismo registro.
   Un proyecto independiente nunca se mezcla con un programa.
4. Al empezar a trabajar en un proyecto, lee primero su `proyecto.yaml`, su `CLAUDE.md` (reglas del proyecto; valen
   para cualquier asistente, aunque el archivo se llame así) y su `seguimiento/traspaso.md`.
   Lee el resto de archivos solo cuando la tarea los necesite (ahorra contexto y tokens).

## Principios de trabajo

1. **La fuente de verdad son los datos del proyecto** (`.yaml`, `.csv`, `.md`). Word, Excel y PowerPoint son salidas.
2. **Nunca inventes datos.** Si falta algo, escribe `[PENDIENTE: qué falta]` y avísalo al final.
3. **Distingue hechos de estimaciones.** Marca como "estimado" lo que no venga de una fuente.
4. **Pide confirmación antes de modificar registros** (riesgos, cronograma, línea base, cambios, ítems),
   salvo en `alta-proyecto` y `nuevo-proyecto`, que aplican y registran sus decisiones para revisión en bloque.
5. **Fechas:** en archivos de datos `AAAA-MM-DD`; en documentos de salida, el formato de `proyecto.yaml`.
   **Porcentajes** en datos como fracción (0,15 = 15%).
6. **Confidencialidad:** `_entrada/`, originales contractuales, versiones originales de documentos, postulaciones de
   terceros, el banco de archivos (`contenidos/archivos/`) y el paquete firmado (`entrega/final/`) no se suben a Git
   (`.gitignore`, el control de Git y, en Claude Code, el hook `proteger_confidenciales` lo resguardan).
   **Réplicas:** de las bases y documentos de definición (bases, anexos, aclaraciones, lineamientos, contratos,
   actas, informes) se guarda una réplica fiel en `fuentes/`, que sí se sube al repositorio privado. De CVs, estados
   financieros y datos personales solo queda la ficha. La política está en `replicas` de `empresa/empresa.yaml`.
7. **Registros CSV:** conserva columnas y su orden (se pueden agregar columnas al final). UTF-8, coma.
8. **Lo específico va al proyecto (o a la empresa):** nombres de reportes, métricas del dominio, políticas y
   cálculos propios se guardan en `proyectos/<slug>/` o, si son comunes a todos los proyectos, en `empresa/`;
   nunca en el núcleo ni en los arquetipos.
9. **Decisiones sensibles** (inversiones, técnicas, legales, de salud): el harness organiza, mide y plantea
   preguntas; la decisión es del usuario y de los profesionales competentes.
10. Al terminar una tarea que modificó archivos, actualiza el traspaso (regla 17) y sugiere `guardar-cambios`.
11. **Si un control bloquea o reporta un problema** (hook de tu herramienta o control de Git), corrígelo antes de
    seguir; no lo esquives (nunca uses `git commit --no-verify`).
12. **Al modificar el núcleo** (skills, herramientas, arquetipos, plantillas) ejecuta `python pruebas/ejecutar_pruebas.py`
    y no des el cambio por terminado si alguna prueba falla.
13. **Autoría limpia de los entregables.** Todo documento que se entrega (Word, Excel, PowerPoint, PDF, Markdown de
    salida) sale a nombre del usuario (`autoria.nombre` o `responsable.nombre`) y sin rastros del proceso:
    - en el texto, nunca menciones el proceso de elaboración (asistentes, "generado automáticamente", el harness,
      nombres de skills o scripts, rutas del repositorio, ids internos) ni dejes marcadores `[PENDIENTE`. Hablar de IA
      cuando es el **tema** del proyecto es legítimo (se permite con `autoria.terminos_permitidos`);
    - **excepción:** las declaraciones que exijan unas bases o un contrato (regla 14) se redactan con veracidad y el
      archivo se lista en `autoria.excluir`, igual que los documentos de terceros (cartas, certificados);
    - sigue `contexto/estilo.md` del proyecto (o `empresa/estilo.md`);
    - antes de entregar, `python herramientas/verificar_autoria.py <archivo> --proyecto proyectos/<slug>` debe dar OK
      (con `--corregir` limpia propiedades, partes heredadas y caracteres invisibles).
    Los archivos internos del harness (registros, informes de alta, definiciones, réplicas) no están sujetos a esta regla.
14. **Integridad.** Si unas bases, un contrato o una norma exigen declarar el uso de herramientas de IA, o lo
    restringen, es un requisito más: se registra, se avisa al usuario de forma destacada y la decisión es suya.
    Nunca se redacta una declaración falsa ni se oculta algo que se deba declarar.
15. **Commits:** mensajes en español, descriptivos, sin líneas de coautoría ni menciones a herramientas de IA.
16. **Valida cada CSV o YAML que edites.** Claude Code lo hace solo (hook). En otras herramientas ejecuta después de
    editar `python herramientas/hooks/precommit.py --archivos <ruta>`; además, el control de Git lo revisa todo
    antes de cada commit.
17. **Traspaso entre sesiones y asistentes.** Al terminar cada tarea que cambió algo, y en cada hito de una tarea
    larga, actualiza `proyectos/<slug>/seguimiento/traspaso.md`: fecha, asistente, tarea en curso y su estado, qué
    se hizo, próximo paso, decisiones pendientes del usuario y archivos clave. Reemplaza el contenido (el historial
    queda en Git). Así otra sesión, otro computador u otro asistente retoma sin que el usuario repita nada.
18. **Tu consola no es interactiva.** No ejecutes comandos que esperen una respuesta (S/N, términos que aceptar,
    contraseñas, un editor): quedan detenidos y el usuario no puede contestar. Para instalar usa solo
    `herramientas/preparar_pc.ps1` o `preparar_pc.sh` (nunca winget, choco ni brew directos); para Git, usa `-m`,
    nunca `-i`, y `git --no-pager` si la carpeta no tiene `core.pager cat`. Ejecuta los scripts desde la carpeta con
    su ruta relativa (`herramientas/...`): algunos controles de seguridad detienen PowerShell si su línea de comando
    trae la ruta completa de la carpeta abierta en el editor. Si algo queda esperando, detenlo y ofrece el instalador
    de doble clic (`INSTALAR-WINDOWS.bat` o `INSTALAR-MAC.command`), que abre una ventana donde el usuario sí puede
    responder; tú no lo ejecutes.
19. **Hechos del mundo, con protocolo.** Si una tarea exige afirmar hechos de afuera (terceros, registros, mercado,
    normativa) que sostienen una decisión o un entregable, no los escribas de memoria: ofrece abrir una investigación
    (skill `investigar`, parte en sondeo); si el usuario sigue sin ella, marca esas afirmaciones como sin verificar.
    Las firmas de P0, P2 y P5 son siempre del usuario.
20. **Capacidad según la tarea, no según el costo.** Nivel **alto** (juicio que nadie puede comprobar: diseñar un
    proyecto, evaluar, refutar, red team, encuadrar una investigación, revisar antes de entregar): el modelo más capaz
    disponible, con contexto limpio. Nivel **medio** (análisis con datos, borradores, lectura con extracción): un
    modelo competente y rápido. Nivel **bajo** (transcribir, formatear, validar, buscar): el más rápido. Los subagentes
    de `.claude/agents/` traen su nivel en `model:`; si `empresa/empresa.yaml` define `capacidad`, invoca cada subagente
    con ese modelo. El nivel de cada skill está en `.claude/skills/ayuda/catalogo.yaml` (`capacidad`). Si una tarea de
    nivel alto corre en un modelo liviano, dilo en una línea al usuario y sigue. Cómo se elige el modelo en cada
    herramienta: `.claude/skills/configurar-asistente/references/asistentes.md`.
21. **Cuida el contexto.** No releas archivos que ya tienes en la conversación; pide resúmenes a los scripts (`estado.py`,
    `status.py --breve`, `evaluar_metricas.py`) en vez de leer CSV o YAML enteros; para lotes de documentos usa el
    subagente `lector-documental`; lee las `references/` de una skill solo en la fase que las usa. Para ver cuánto pesa
    cada pieza: `python herramientas/medir_contexto.py`.
22. **Lo tuyo primero.** Toda salida usa el formato del proyecto; si no, el de la empresa (`empresa/plantillas/`,
    `empresa/reportes/catalogo/`, `empresa/formatos/`); si no, el del harness. Los formatos propios se cargan con la
    skill `adoptar-formatos` (desde `empresa/_entrada/`), que dice qué falta y qué se pierde; los originales nunca se
    modifican. Si el usuario dice «nuestro formato» y no está adoptado, ofrécelo.

## Modo por defecto
Si el alta del proyecto está incompleta (`induccion.estado` distinto de `completa`), trabaja igual con
los valores por defecto. Menciona una sola vez, al final, qué pendientes críticos afectan el resultado.

## Trabajo en la nube (opcional, solo Claude Code)

Si `.harness/nube.yaml` dice `habilitada: true`, hay tareas programadas en la nube y una bandeja en GitHub (`bandeja.py`).
Reglas en `NUBE.md`: rama propia y PR (nunca `main`), una tarea a la vez, solo REST. En el PC, antes de editar un proyecto
con un PR de la nube abierto, revísalo o intégralo. Nada se programa sin el sí del usuario (skill `nube`); se cambia con
`configurar`.

## Procedimientos (skills)

Cada procedimiento está en `.claude/skills/<nombre>/SKILL.md` (la carpeta se llama `.claude` por compatibilidad; sirve
para cualquier asistente). En Claude Code se activan solos. **En otras herramientas, lee el índice
`.claude/skills/LEEME.md` al recibir el primer pedido de la sesión** (una fila por skill, con las frases típicas del
usuario) y, cuando el pedido calce con una fila, lee ese SKILL.md completo y síguelo paso a paso, aunque el usuario no
lo nombre. Si un SKILL.md menciona un subagente o un hook, usa las equivalencias de la sección siguiente.
Los que todos usan: `instalar` (primer paso) · `nuevo-proyecto` y `alta-proyecto` (crear o cargar un proyecto) ·
`status` («¿cómo vamos?») · `generar-reporte` · `minuta` · `riesgos-issues` · `investigar` (hechos del mundo con
fuente) · `ayuda` («¿qué puedo hacer?») · `guardar-cambios`. **Skills propias de la empresa:** las carpetas de
`.claude/skills/` que no están en el índice también valen (el estado de inicio las lista).

## Roles (subagentes) y equivalencias por herramienta

Roles en `.claude/agents/`: `lector-documental` (lee lotes de documentos y devuelve hechos con fuente) ·
`revisor-independiente` (revisa con ojo crítico antes de entregar) · `evaluador-propuestas` (evalúa una propuesta
por vez contra la pauta) · `analista-datos` (procesa y revisa datos sin modificarlos) · `revisor-red-team` (una
perspectiva del red team por vez) · `bibliotecario`, `refutador` y `arbitro` (roles de una investigación auditable:
recuperar sin interpretar, refutar en contexto estéril, aplicar las reglas de evidencia) · `analista-financiero` (calcula
y explica desvíos e indicadores de finanzas; no decide ni cambia datos).

- **Con subagentes** (Claude Code): invócalos como dice cada SKILL.md.
- **Sin subagentes:** aplica el rol tú mismo en un paso separado: lee su `.md`, adopta solo esa perspectiva, lee
  solo los archivos que el rol indica y escribe su resultado antes de seguir. Para evaluaciones y red team, haz una
  propuesta o perspectiva por vez y no mires los resultados de las otras hasta consolidar.
- **Controles:** en Claude Code corren los hooks de `.claude/settings.json`. En todas las herramientas corre el
  control de Git (`.githooks/pre-commit`), que bloquea commits con archivos confidenciales o planillas mal formadas.
  Si tu herramienta no tiene hooks, el paso 0 y la regla 16 los haces tú.
- Detalle por herramienta (qué archivo lee, qué soporta): `.claude/skills/configurar-asistente/references/asistentes.md`.

## Herramientas (`python`, o `py` en Windows; `.venv/bin/python` en Mac)
De uso diario: `estado.py` (estado al iniciar) · `status.py` (status de gestión) · `crear_proyecto.py` · `evaluar_metricas.py` ·
`validar_proyecto.py` · `extraer_entrada.py` · `md_a_docx.py` · `verificar_autoria.py` · `guia_proyecto.py` · `investigacion.py`.
La lista completa, con las opciones de cada una, está en `herramientas/LEEME.md`: léela solo cuando necesites una herramienta
que no conozcas (cada SKILL.md nombra las suyas). Dependencias: `pip install -r requirements.txt` (en Mac, dentro de `.venv`).
