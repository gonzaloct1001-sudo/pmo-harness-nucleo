# PMO Harness — entrada para Claude Code

Las reglas de esta carpeta están en `AGENTS.md`, la fuente única para cualquier asistente de IA. Se importan aquí:

@AGENTS.md

## Propio de Claude Code
- **Estado al iniciar:** el hook de inicio entrega el bloque `[Estado del PMO Harness]` (equivale a
  `herramientas/estado.py --remoto`); úsalo y no vuelvas a ejecutar el script.
- **Identidad:** en `.harness/asistentes.yaml` te corresponde el id `claude-code`. Si no figura, sigue
  `configurar-asistente`.
- **Skills:** las de `.claude/skills/` se activan solas según su descripción; la tabla de procedimientos de
  `AGENTS.md` es la misma lista.
- **Subagentes:** los de `.claude/agents/` están disponibles; invócalos como indica cada skill.
- **Hooks** (`.claude/settings.json`): al iniciar sesión, resumen de estado; antes de comandos Git, bloqueo de
  archivos confidenciales; después de editar CSV o YAML, validación de columnas, fechas y métricas. Además corre el
  control de Git (`.githooks/pre-commit`), igual que con cualquier otro asistente.
- **Edita CSV y YAML con Edit/Write:** así los valida el hook al instante. Si usas la consola, el hook revisa igual los
  CSV y YAML de `proyectos/` modificados en los últimos 2 minutos.
