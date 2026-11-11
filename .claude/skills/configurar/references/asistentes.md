# Asistentes de IA conocidos

Requisito para operar el harness: que el asistente **lea archivos de la carpeta abierta y ejecute comandos en la
consola** (con permiso del usuario). Un chat en el navegador (ChatGPT, Gemini o Claude en la web) no puede.

Las herramientas cambian seguido: si algo de esta tabla no calza con la versión instalada, manda la documentación
de la herramienta. Lo que no cambia es el principio: una sola fuente de reglas (`AGENTS.md`), puertas de entrada que
solo remiten a ella y controles en Git que no dependen del asistente.

| id | Herramienta | Lee al iniciar | Procedimientos (skills) | Controles automáticos | Subagentes |
|---|---|---|---|---|---|
| `claude-code` | Claude Code (extensión de VS Code, consola o app) | `CLAUDE.md`, que importa `AGENTS.md` | Nativos (`.claude/skills/`) | Hooks de `.claude/settings.json` + control de Git | Sí (`.claude/agents/`) |
| `codex` | OpenAI Codex (extensión de VS Code, consola o app) | `AGENTS.md` | Lee el SKILL.md según el índice `.claude/skills/LEEME.md` | Control de Git | No: roles en pasos separados |
| `gemini` | Gemini CLI o Gemini Code Assist en modo agente | `GEMINI.md`, que importa `AGENTS.md` | Lee el SKILL.md según el índice `.claude/skills/LEEME.md` | Control de Git | No: roles en pasos separados |
| `antigravity` | Google Antigravity (editor con agentes; Gemini, Claude u otros modelos) | `GEMINI.md` de la raíz (y `AGENTS.md` en versiones recientes) | Lee el SKILL.md según el índice `.claude/skills/LEEME.md` | Control de Git | Según la versión; si no, roles en pasos separados |
| `cursor` | Cursor (modo agente) | `AGENTS.md` | Lee el SKILL.md según el índice `.claude/skills/LEEME.md` | Control de Git | Según la versión; si no, roles en pasos separados |
| `copilot` | GitHub Copilot en modo agente (VS Code) | `AGENTS.md` (y `.github/copilot-instructions.md` si existe) | Lee el SKILL.md según el índice `.claude/skills/LEEME.md` | Control de Git | No: roles en pasos separados |

## Capacidad y modelos

El harness pide capacidad según la tarea (regla 20 de `AGENTS.md`): **alta** para el juicio que nadie puede comprobar,
**media** para análisis y borradores, **baja** para transcribir, validar y buscar. Cómo se traduce en cada herramienta:

- **Claude Code:** los subagentes traen `model:` en su archivo (`opus` = alta; `sonnet` = media y baja). Si
  `empresa/empresa.yaml` define `capacidad`, el asistente invoca cada subagente con ese modelo en vez del de su archivo.
  El modelo de la sesión principal lo elige el usuario (`/model`); para una skill de nivel alto conviene el más capaz.
- **Codex, Gemini, Antigravity, Cursor y Copilot:** no leen `model:`; el usuario elige el modelo en la herramienta
  (selector o configuración). Regla práctica: nivel alto = el modelo más capaz que ofrezca («pro», «thinking», «high»);
  medio y bajo = el rápido. Al aplicar un rol de nivel alto en pasos separados, el asistente avisa en una línea si
  está en un modelo liviano y sigue.
- El refutador de una investigación puede correr en otro proveedor (`empresa/investigacion/ajustes.yaml`,
  `refutador.asistente`): el asistente entrega la instrucción lista para pegar en esa herramienta.

## Sesiones largas
La calidad del contexto baja mucho antes de que la ventana se llene (entre el 20 y el 40 %). Regla para cualquier
asistente: cada tarea larga se parte en hitos; en cada hito, traspaso al día (regla 17) y `guardar-cambios`; después
de unas 120 acciones (ediciones, comandos), cerrar el hito y seguir en una sesión nueva: retoma desde el traspaso
sin perder nada. En Claude Code lo recuerda el hook `sesion_larga.py` y el hook `cierre_sesion.py` no deja terminar
con cambios sin guardar y traspaso viejo; en las demás herramientas, es el asistente quien lleva la cuenta.

## Notas por herramienta

### Claude Code
- La agenda del día llega sola en la primera interacción (hook `agenda_diaria.py`); en las demás herramientas,
  ejecuta `python herramientas/agenda.py --una-vez` al recibir el primer pedido del día y muéstrala si trae algo.
- Todo viene configurado: el hook de inicio entrega el estado, las skills se activan solas y los subagentes están
  disponibles. Solo falta registrarlo en `.harness/asistentes.yaml`.
- Los hooks usan `sh herramientas/py.sh`, que encuentra Python aunque en Windows solo responda `py`.

### OpenAI Codex
- Lee `AGENTS.md` de la raíz (y los `AGENTS.md` de subcarpetas, si existieran). No crees archivos extra.
- Modo de aprobación: el que el usuario prefiera; recomienda uno que pida confirmación antes de comandos que salgan
  de la carpeta o tengan acceso a red.
- Si la versión instalada soporta skills en formato SKILL.md, puede detectarlas sola; igual sigue la tabla.

### Gemini (CLI o Code Assist)
- Lee `GEMINI.md` por defecto, que importa `AGENTS.md` con `@AGENTS.md`. Si la versión no expande la importación, la
  frase de respaldo de `GEMINI.md` le pide leerlo.
- Alternativa: en `.gemini/settings.json` se puede configurar el nombre del archivo de contexto para que lea
  `AGENTS.md` directamente (la opción se llama `contextFileName` o `context.fileName`, según la versión). Pide
  confirmación antes de crear ese archivo.

### Google Antigravity
- Lee las reglas de la raíz de la carpeta abierta: `GEMINI.md` (que remite a `AGENTS.md`) y, en versiones recientes,
  también `AGENTS.md` directamente; si ambos dicen cosas distintas, prevalece `GEMINI.md` (por eso este solo remite).
- Tiene reglas propias por carpeta (`.agent/rules/` o `.agents/rules/`, según la versión): no son necesarias. Si el
  usuario ya tiene reglas ahí, que no contradigan `AGENTS.md`.
- Puede usar varios modelos: registra la herramienta (`antigravity`), no el modelo.

### Cursor
- Lee `AGENTS.md`. Las reglas propias de Cursor (`.cursor/rules/`) no son necesarias; si el usuario ya tiene reglas
  ahí, que no contradigan `AGENTS.md`.

### GitHub Copilot (modo agente)
- Lee `AGENTS.md`. Si el repositorio ya tiene `.github/copilot-instructions.md`, agrégale al inicio una línea que
  remita a `AGENTS.md` (con confirmación del usuario).

### Otra herramienta
Sigue el paso 2 de `SKILL.md` («Herramienta desconocida»): averiguar qué archivo lee, crear solo esa puerta de entrada,
activar el control de Git, hacer la prueba de humo y registrarla con `origen: configurado-en-sesion`.
