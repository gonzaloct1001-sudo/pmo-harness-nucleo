# PMO Harness — mapa de reglas (para cualquier asistente de IA)

Marco para diseñar, cargar y gestionar proyectos de cualquier tipo con un asistente de IA que trabaje sobre carpetas y
ejecute comandos: Claude Code, OpenAI Codex, Gemini, Google Antigravity, Cursor, GitHub Copilot u otro. **Este archivo
es la fuente única de reglas**: `CLAUDE.md`, `GEMINI.md` y cualquier otra puerta de entrada solo remiten aquí. Es un
mapa: cada principio está en una línea y su detalle vive en `reglas/`, que lees cuando la tarea lo pide (cada SKILL.md
dice cuáles). Si llegaste por otro archivo, sigue leyendo este completo.

Responde siempre en español (Chile), con tono profesional, directo y sin tecnicismos innecesarios.

## Al iniciar cada sesión (paso 0, siempre)
1. **Estado.** `python herramientas/estado.py --remoto` y usa su bloque `[Estado del PMO Harness]` (Claude Code lo
   entrega por hook: no lo repitas). Python: `python`; en Windows `py` si no responde; en Mac `.venv/bin/python`. Si
   ninguno funciona, ofrece el instalador (`INSTALAR-WINDOWS.bat`, `INSTALAR-MAC.command` o la skill `instalar`).
2. **Identidad.** Si el estado dice que tu asistente no está registrado en `.harness/asistentes.yaml`, sigue la skill
   `configurar` (opción D: `references/asistente.md`) antes de la primera tarea. Si eres un asistente distinto del
   último que trabajó (campo `asistente` de los traspasos), aplica su «Cambio de asistente a mitad de camino».
3. **Dónde estamos.** Si el estado trae «Status de los proyectos», muéstraselo en 2 a 4 líneas junto al saludo:
   rojos y amarillos con su motivo, lo que vence pronto y las decisiones pendientes. El detalle, con la skill `status`.
4. Según el estado: **no instalado** → responde el saludo y ofrece `instalar` (puede completar antes
   `FICHA-DE-INICIO.md`; el manual es `MANUAL-DE-USUARIO.md`) · **traspaso pendiente**, **material en `_entrada/`** o
   **alta a medio camino** → menciónalo en una línea y ofrece continuar · **instalado sin proyectos** → ofrece
   `nuevo-proyecto` (de cero, en marcha con documentos o en marcha sin documentos) · **controles de Git inactivos** →
   ofrece `git config core.hooksPath .githooks` · **commits en GitHub que no están aquí** → ofrece `git pull` ·
   **críticos previos**, **mejoras sin enviar** o **revisión de entropía pendiente** → dilo en una línea, sin actuar.
5. Si nada de lo anterior aplica, atiende directamente lo que pida el usuario.

## Organización (detalle: `reglas/organizacion.md`)
- Una carpeta del harness = un repositorio privado = **una empresa** (o persona); otra empresa, otra carpeta
  (`nueva_empresa.py`). **Nunca mezcles datos de dos empresas.** El núcleo es público y solo lo modifica su dueño
  (`git config pmo.mantenedor true`); nunca «Fork».
- `NUCLEO.txt` lista lo que se reemplaza al actualizar; `empresa/`, `proyectos/` y `.harness/` son de la empresa y
  nunca se tocan.
- Tres capas: **núcleo** (`.claude/skills/`, `.claude/agents/`, `herramientas/`, `reglas/`, `arquetipos/`, plantillas)
  → **empresa** (`empresa/`: identidad, marca, formatos, banco de antecedentes, capacidad) → **proyecto**
  (`proyectos/<slug>/`: todo lo particular). Un proyecto combina arquetipos: `ejecucion`, `obra`, `agil`, `cartera`,
  `evaluacion`, `postulacion`, `programa`, `estudio`, `investigacion`, `finanzas`, `estrategia`.
- Contrato común de todo proyecto: `proyecto.yaml`, `metricas/`, `reportes/catalogo/`, `riesgos/`, `seguimiento/`
  (decisiones, acuerdos, traspaso), `contexto/`, `fuentes/` (réplicas fieles).

## Proyecto activo
El que nombra el usuario (`proyectos/<slug>/`; subproyecto: `proyectos/<programa>/subproyectos/<id>/`); si hay uno
solo, ese; los de `ejemplos/` solo si los nombra; con duda, pregunta. Nunca mezcles dos proyectos en un registro. Al
empezar, lee su `proyecto.yaml`, su `CLAUDE.md` y `seguimiento/traspaso.md`; el resto, solo cuando la tarea lo necesite.

## Principios (una línea cada uno; el detalle, en `reglas/`)
**Datos** (`reglas/datos.md`)
1. La fuente de verdad son los datos del proyecto (`.yaml`, `.csv`, `.md`); Word, Excel y PowerPoint son salidas.
2. Nunca inventes datos: escribe `[PENDIENTE: qué falta]` y avísalo al final.
3. Distingue hechos de estimaciones: «estimado» lo que no tenga fuente.
5. Fechas `AAAA-MM-DD` en datos; porcentajes como fracción; en salidas, el formato de `proyecto.yaml`.
7. CSV: conserva columnas y orden; UTF-8, coma; ids estables.
16. Valida cada CSV o YAML que edites (hook en Claude Code; `precommit.py --archivos` en otras herramientas).

**Trabajo** (`reglas/trabajo.md`)
4. Pide confirmación antes de modificar registros (salvo `nuevo-proyecto`, que registra sus decisiones para
   revisión en bloque).
9. Decisiones sensibles (inversiones, técnicas, legales, de salud): el harness organiza y pregunta; decide el usuario.
10. Al terminar una tarea que modificó archivos: traspaso (17) y sugiere `guardar-cambios`.
11. Si un control bloquea o reporta un problema, corrígelo; nunca `git commit --no-verify`.
17. Traspaso al cerrar cada tarea e hito (`seguimiento/traspaso.md`): hecho, próximo paso, decisiones pendientes,
    comprobado, no comprobado, tuve que adivinar. Si adivinaste, una skill no cubrió el caso o un script falló:
    `python herramientas/mejoras.py --anotar`; nunca edites el núcleo.
18. Tu consola no es interactiva: nada que espere una respuesta; instala solo con `preparar_pc`; scripts por ruta relativa.
21. Cuida el contexto: no releas; resúmenes por script; lotes de documentos al `lector-documental`; `references/` y
    `reglas/` solo en su fase; tareas largas en hitos, y sesión nueva tras muchas acciones.

**Confidencialidad y entregables** (`reglas/confidencialidad.md`, `reglas/entregables.md`)
6. `_entrada/`, originales, banco de archivos y paquetes firmados no se suben a Git; de bases y contratos, réplica
   fiel en `fuentes/`; de CVs y datos personales, solo la ficha.
13. Autoría limpia: todo entregable sale a nombre del usuario, sin rastros del proceso; `verificar_autoria.py` en OK
    antes de entregar.
14. Integridad: si unas bases exigen o restringen declarar IA, es un requisito más; nunca una declaración falsa.
15. Commits en español, descriptivos, sin coautoría ni menciones a herramientas de IA.
22. Lo tuyo primero: formato del proyecto; si no, el de la empresa; si no, el del harness (skill `adoptar-formatos`).

**Núcleo y método** (`reglas/nucleo.md`)
8. Lo específico va al proyecto o a la empresa; nunca al núcleo ni a los arquetipos.
12. Al modificar el núcleo, `python pruebas/ejecutar_pruebas.py`; nada se da por terminado con una prueba en falla.
19. Hechos del mundo con protocolo: ofrece `investigar` (parte en sondeo); si no, márcalos «sin verificar». P0, P2 y
    P5 las firma el usuario.
20. Capacidad según la tarea: alto (juicio no comprobable) con el modelo más capaz y contexto limpio; medio
    (análisis, borradores); bajo (transcribir, validar, buscar). Los subagentes traen `model:`; `empresa.yaml` puede
    fijar `capacidad`.

## Modo por defecto
Alta incompleta (`induccion.estado` distinto de `completa`): trabaja con los valores por defecto y menciona una sola
vez, al final, los pendientes críticos que afectan el resultado.

## Trabajo en la nube (opcional, solo Claude Code)
Si `.harness/nube.yaml` dice `habilitada: true`, hay tareas programadas y una bandeja en GitHub (`bandeja.py`). Reglas
en `NUBE.md`: rama propia y PR (nunca `main`), una tarea a la vez, solo REST. En el PC, antes de editar un proyecto con
un PR de la nube abierto, revísalo o intégralo. Nada se programa sin el sí del usuario (skill `nube`).

## Procedimientos (skills)
Cada procedimiento está en `.claude/skills/<nombre>/SKILL.md` (la carpeta se llama `.claude` por compatibilidad; sirve
para cualquier asistente). En Claude Code se activan solos. **En otras herramientas, lee el índice
`.claude/skills/LEEME.md` al recibir el primer pedido de la sesión** y, cuando el pedido calce con una fila, lee ese
SKILL.md completo y síguelo paso a paso, aunque el usuario no lo nombre. Si menciona un subagente o un hook, usa las
equivalencias de `reglas/organizacion.md`. Los de uso diario: `instalar` · `nuevo-proyecto` (de cero o con documentos)
· `status` · `reportes` · `reuniones` · `riesgos` · `investigar` · `ayuda` · `guardar-cambios`. Las carpetas de
`.claude/skills/` que no están en el índice son skills propias de la empresa y también valen.

## Roles (subagentes)
`.claude/agents/`: `lector-documental` · `revisor-independiente` · `evaluador-propuestas` · `analista-datos` ·
`revisor-red-team` · `bibliotecario`, `refutador`, `arbitro` (investigación) · `analista-financiero`. Con subagentes,
invócalos como dice cada SKILL.md, con objetivo, salida, límites y presupuesto; sin ellos, aplica el rol tú mismo en un
paso separado (solo su perspectiva, solo sus archivos, una propuesta por vez). Controles: hooks de `.claude/settings.json`
en Claude Code; el control de Git (`.githooks/pre-commit`) en todas las herramientas; si la tuya no tiene hooks, el paso
0 y el principio 16 los haces tú. Detalle por herramienta: `.claude/skills/configurar/references/asistentes.md`.

## Herramientas (`python`, o `py` en Windows; `.venv/bin/python` en Mac)
De uso diario: `estado.py` · `status.py` · `crear_proyecto.py` · `evaluar_metricas.py` · `validar_proyecto.py` ·
`extraer_entrada.py` · `md_a_docx.py` · `verificar_autoria.py` · `guia_proyecto.py` · `investigacion.py` · `mejoras.py`.
La lista completa, con las opciones de cada una, está en `herramientas/LEEME.md`: léela solo cuando necesites una que no
conozcas (cada SKILL.md nombra las suyas). Dependencias: `pip install -r requirements.txt` (en Mac, dentro de `.venv`).
