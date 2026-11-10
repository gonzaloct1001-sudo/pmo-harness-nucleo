# Modo nube (opcional, solo con Claude Code)

El modo nube permite que el asistente trabaje **con tu computador apagado**: tareas programadas que corren en la nube
de Claude sobre el repositorio privado de la empresa, y una **bandeja** en GitHub donde dejas pedidos y respondes
preguntas desde el celular. Es **opcional**: nada se programa sin tu sí, eliges qué tareas quieres y puedes pausarlas o
quitarlas cuando quieras. Si prefieres operar solo desde un PC, no actives nada: el harness funciona igual.

## Cómo funciona, en simple
1. Tu repositorio privado en GitHub es la única memoria compartida: lo que no está ahí, la nube no lo ve (las carpetas
   `_entrada/` nunca se suben, así que la carga de documentos sigue siendo trabajo del PC).
2. Una **tarea programada** (en claude.ai/code, sección *routines*) abre una sesión en la nube a la hora que elegiste,
   clona tu repositorio, lee `AGENTS.md` y este archivo, y hace una sola cosa: la tarea que le asignaste.
3. Lo que produce queda en una **rama propia y un PR** (nunca en `main`): tú lo revisas desde el teléfono (app de
   GitHub o de Claude) y dices si se integra. Las preguntas quedan en la **bandeja** (issues con etiqueta `harness:`),
   donde respondes cuando puedas.
4. Al terminar, la tarea deja un comentario con lo hecho y, si la herramienta existe, un aviso al teléfono.

## Qué se puede programar (catálogo)
| Tarea | Qué hace | Cuándo (por defecto) |
| --- | --- | --- |
| `resumen-manana` | Resumen diario de la empresa: semáforos, lo que vence, decisiones pendientes, investigaciones abiertas, meses de finanzas sin cerrar y la bandeja. Lo deja como comentario en el issue «Resumen diario» y avisa al teléfono | Lunes a viernes, 08:00 hora local |
| `bandeja` | Toma el siguiente pedido de la bandeja (issue `harness:tarea` sin estado) y lo trabaja según las skills: una rama, un PR, un comentario con el resultado. Si necesita una decisión, la deja como pregunta y sigue con otro pedido | Cada 4 horas en días hábiles |
| `status-semanal` | Status de todos los proyectos como reporte, dejado en el issue «Status semanal» | Lunes, 09:00 hora local |
| `recordatorio-cierre` | En proyectos de finanzas, revisa qué meses siguen sin cerrar y lo recuerda con la checklist | Día 10 de cada mes, 09:00 |

Cada tarea se elige por separado y se registra en `.harness/nube.yaml` (`python herramientas/nube.py --estado`),
con quién la activó y cuándo. La skill `nube` guía todo el proceso y la skill `configurar` permite cambiarlo después.

## Lo que necesitas
- Claude Code con un plan que incluya sesiones en la nube, y la **Claude GitHub App** instalada en el repositorio de la
  empresa (github.com → Settings → Applications → Claude → *Repository access*).
- El repositorio privado de la empresa en GitHub (lo crea `instalar`) y GitHub CLI con sesión en el PC (para la bandeja).
- Nada más: las otras IA (Codex, Gemini, Cursor, Copilot) trabajan solo en el PC.

## Desde el celular
- **Encargar algo:** en la app de GitHub, un issue nuevo con el pedido en tus palabras y la etiqueta `harness:tarea`
  (o desde el PC: `python herramientas/bandeja.py --nueva "…"`). La próxima corrida de `bandeja` lo toma.
- **Responder una pregunta:** comenta en el issue que la trae (etiqueta `estado:espera-usuario`); la corrida siguiente
  aplica tu respuesta.
- **Aprobar un resultado:** en el PR, «sí, intégralo» como comentario, o desde el PC `bandeja.py --integrar <n>`.
- **Ver cómo va todo:** el comentario de la mañana en el issue «Resumen diario».

## Reglas de una corrida en la nube (las cumple el asistente)
1. Empieza con `python herramientas/estado.py` y lee `AGENTS.md`. Trabaja en modo automático: nadie responde en el
   momento; lo que requiera una decisión se deja como pregunta en la bandeja (`bandeja.py --pregunta`) y la corrida sigue.
2. Solo con lo que está en el repositorio. No inventa lo que falta.
3. **Nunca escribe en `main`.** Cada tarea: rama `nube/<n>-<slug>`, commits en español sin coautoría, un PR con un
   resumen en palabras simples (qué se hizo, qué falta, qué decidir). Quien integra es el usuario (desde el PC, el
   teléfono o `bandeja.py --integrar`).
4. **Una tarea a la vez:** marca el issue `estado:en-curso` (`bandeja.py --tomar`); si otra corrida lo ve en curso hace
   menos de 3 horas, no lo toma. Al terminar, `bandeja.py --terminar` (etiqueta `estado:hecho`).
5. GitHub solo por **REST** (`gh api`): `gh issue` y `gh pr` no funcionan en la nube. `bandeja.py` ya lo hace así.
6. No instala nada, no cambia `.claude/settings.json`, `NUCLEO.txt`, `AGENTS.md` ni `.harness/nube.yaml`, no programa ni
   modifica tareas, y no toca ramas de otras corridas.
7. Al terminar: traspaso del proyecto al día, comentario en el issue con qué se hizo y qué falta, y aviso al teléfono
   si la herramienta de notificación existe. Respeta las mismas reglas de confidencialidad y autoría de `AGENTS.md`.
8. Una corrida que dura menos de 10 segundos no llegó a trabajar: el usuario mira su registro en la página de la tarea
   (skill `nube`, «Si algo falla»).

## Instrucción de una tarea programada
Es el texto que se pega al crear la tarea en la nube; `python herramientas/nube.py --instruccion <tarea>` lo imprime
con los datos de la empresa:

> Eres el asistente del PMO Harness en la nube para la empresa «<empresa>». Lee `NUBE.md` y `AGENTS.md` del
> repositorio y ejecuta la tarea «<tarea>» tal como la describe el catálogo de `NUBE.md`, cumpliendo sus reglas (modo
> automático, rama propia y PR, una tarea a la vez, solo REST). Si no puedes hacerla, deja un comentario en el issue
> «Resumen diario» diciendo por qué.
