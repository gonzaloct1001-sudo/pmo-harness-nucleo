# Crear la tarea en la nube con `RemoteTrigger` (forma comprobada)

`RemoteTrigger create` con este cuerpo creó y corrió una tarea real (noviembre de 2026). Sustituye empresa,
repositorio, tarea, cron y zona horaria; la instrucción sale de `python herramientas/nube.py --instruccion <tarea>`.
Si `list` muestra tareas existentes de la cuenta, copia de ellas el `environment_id` y el conector `Claude_Code_Remote`.

```json
{
  "name": "harness · <Empresa> · <tarea>",
  "cron_expression": "CRON_TZ=<zona horaria> <cron>",
  "enabled": true,
  "persist_session": true,
  "job_config": {
    "ccr": {
      "environment_id": "<environment_id de una tarea existente, o el ambiente por defecto de la cuenta>",
      "events": [{"data": {"message": {"content": "<instrucción de nube.py --instruccion>", "role": "user"}, "type": "user"}}],
      "session_context": {
        "allowed_tools": ["Bash", "Read", "Write", "Edit", "Glob", "Grep", "Skill", "TodoWrite", "Artifact", "RemoteTrigger"],
        "model": "claude-sonnet-5-5",
        "sources": [{"git_repository": {"url": "https://github.com/<owner>/<repo>"}}]
      }
    }
  },
  "mcp_connections": [{"connector_uuid": "<uuid del conector Claude_Code_Remote de una tarea existente>", "name": "Claude_Code_Remote",
                       "transport_type": "http", "url": "https://api.anthropic.com/v1/code/mcp/meta",
                       "permitted_tools": [], "tool_policy_overrides": [], "clear_tool_policy_overrides": false}]
}
```

- `persist_session: true` deja una sesión fija donde llega cada corrida; el usuario puede responder ahí desde la app
  de Claude. Para `bandeja` conviene `false` (cada pedido en su propia sesión).
- Sin `mcp_connections` el servidor pega todos los conectores de la cuenta (Canva, Docs, etc.): mejor solo
  `Claude_Code_Remote`, que es el que permite avisar al teléfono.
- Si `create` devuelve `403 repo_access_denied`, la Claude GitHub App no incluye el repositorio: no se creó nada.
- Después de crearla: `nube.py --id-remoto-de <tarea> <id>`, `run` de prueba y `list_runs`. Una corrida del resumen
  tarda menos de un minuto; publica como comentario en el issue «Resumen diario» (el comentario lleva el pie «Generated
  by Claude Code» que agrega la plataforma; no es un problema de autoría: no es un entregable).
- Cambiar el horario: `update` con `cron_expression`; pausar: `update` con `enabled: false`.
