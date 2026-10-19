# PMO Harness — entrada para Gemini y Antigravity

Las reglas de esta carpeta están en `AGENTS.md`, la fuente única para cualquier asistente de IA. Se importan aquí:

@AGENTS.md

Si no ves arriba el contenido de `AGENTS.md`, léelo completo ahora, antes de responder: sin él no sabrás cómo
operar esta carpeta.

## Propio de Gemini (CLI, Code Assist) y Google Antigravity
- **Estado al iniciar:** no llega solo. Tu primera acción en cada sesión es ejecutar
  `python herramientas/estado.py --remoto` (paso 0 de `AGENTS.md`).
- **Identidad:** en `.harness/asistentes.yaml` te corresponde el id `gemini` (o `antigravity` si eres Google Antigravity). Si no figura, sigue
  `.claude/skills/configurar-asistente/SKILL.md`.
- **Procedimientos:** cuando el pedido calce con una fila de la tabla de `AGENTS.md`, lee ese `SKILL.md` completo y
  síguelo paso a paso.
- **Roles (subagentes):** aplícalos tú en pasos separados, como indica `AGENTS.md`.
- **Controles:** corre el control de Git antes de cada commit. Después de editar un CSV o YAML, valida con
  `python herramientas/hooks/precommit.py --archivos <ruta>`.
