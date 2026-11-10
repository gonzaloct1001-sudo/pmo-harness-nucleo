---
name: nube
description: Modo nube opcional, solo con Claude Code: operar desde el celular con el PC apagado. Explica cómo funciona, activa con el sí explícito del usuario, deja elegir qué tareas programar (resumen de la mañana, bandeja, status semanal, recordatorio de cierre), las pausa o quita. Úsala con «desde el celular», «con el PC apagado», «programa», «modo nube», «pausa el resumen».
---

> Reglas que aplican (léelas si no están en tu contexto): `reglas/trabajo.md`, `reglas/datos.md`, `reglas/confidencialidad.md`, `reglas/nucleo.md`, `reglas/organizacion.md`.

# Modo nube (opcional)

**Principio:** nada se programa sin el sí explícito del usuario, tarea por tarea. Si no está cómodo, no se activa nada
y el harness funciona igual desde el PC. Todo se puede pausar o quitar después. Solo con Claude Code: las otras IA
trabajan en el PC.

## 1. Explicar primero (siempre, aunque ya lo haya oído)
En un mensaje corto, con las palabras de `NUBE.md`:
- qué es (tareas programadas que corren en la nube de Claude sobre su repositorio privado, con el PC apagado) y qué no
  es (no procesa lo que está en `_entrada/`: la carga de documentos sigue en el PC);
- qué ve la nube (solo lo que está en el repositorio privado) y qué nunca toca (`main`: todo llega como PR);
- qué puede programar (el catálogo, en una tabla de 4 filas con «qué hace» y «cuándo») y que elige cada una;
- qué cuesta (usa las sesiones en la nube de su plan de Claude) y qué necesita (la Claude GitHub App en el repositorio).
Termina con una sola pregunta: «¿Quieres activarlo? Responde "sí, actívalo" o "no por ahora"». «No» cierra el tema
sin cambiar nada.

## 2. Requisitos (con el sí)
1. `python herramientas/nube.py --revisar`: GitHub CLI con sesión y repositorio privado detectado. Si falta el
   repositorio, créalo con `instalar` (paso 2) antes.
2. La **Claude GitHub App** instalada en el repositorio: pídele que entre a github.com → *Settings* → *Applications* →
   Claude → *Repository access* y agregue el repositorio de la empresa (si no tiene la app, github.com/apps/claude).
   No puedes comprobarlo desde aquí: se confirma con la corrida de prueba del paso 4.
3. `python herramientas/nube.py --habilitar --quien "<nombre>"` y `python herramientas/bandeja.py --etiquetas`.

## 3. Elegir qué programar (una decisión por tarea, dos líneas cada una)
Para cada tarea del catálogo (`nube.py --catalogo`), en este orden: `resumen-manana`, `bandeja`, `status-semanal`,
`recordatorio-cierre` (esta solo si hay proyectos de finanzas):
> «**Resumen de la mañana**: lunes a viernes a las 08:00 te deja en GitHub cómo van tus proyectos y te avisa al
> teléfono. Responde "sí" (o "sí, a las 7:30"), o "no".»

Con cada sí: `python herramientas/nube.py --agregar <tarea> --quien "<nombre>" --cron "<cron>" --zona "<zona horaria del
usuario>"`. La zona horaria sale de `empresa.yaml` o se pregunta una vez. Las que diga «no», no se registran.

## 4. Crear cada tarea en la nube (solo las aprobadas)
Por cada tarea registrada sin `id_remoto`:
1. `python herramientas/nube.py --instruccion <tarea>` → el texto de la instrucción.
2. Si tienes la herramienta `RemoteTrigger`: primero `list` para tomar de una tarea existente el `environment_id` y el
   conector `Claude_Code_Remote`; luego `create` con el cuerpo de `references/tarea-remota.md` (forma comprobada):
   nombre `harness · <empresa> · <tarea>`, el cron con la zona horaria del usuario, solo el repositorio de la empresa,
   modelo `sonnet` (`opus` solo para `bandeja` si el usuario lo pide), la instrucción del punto 1 y solo ese conector.
   Relaya al usuario la hora de la próxima corrida y el enlace que devuelve.
   Si no tienes la herramienta: dale los pasos para crearla en claude.ai/code → *Routines* (nombre, horario,
   repositorio, modelo, y el texto de la instrucción para pegar).
3. Anota el id: `python herramientas/nube.py --id-remoto-de <tarea> <id>`.
4. **Corrida de prueba** (con `run`): si dura menos de 10 segundos, falló antes de empezar; mira `list_runs` y
   `get_run_log` y explícale en simple (lo más común: la app de GitHub no incluye el repositorio, o el plan no tiene
   sesiones en la nube). Si corrió, muéstrale dónde quedó el resultado (el issue «Resumen diario» o el PR).

## 5. Cómo se usa desde el celular (explícalo al terminar)
- Encargar: issue nuevo con etiqueta `harness:tarea` en la app de GitHub (o `bandeja.py --nueva` desde el PC).
- Responder una pregunta: comentar en el issue con etiqueta `estado:espera-usuario`.
- Aprobar un resultado: comentar «sí, intégralo» en el PR, o `bandeja.py --integrar <n>` desde el PC.
- Ver cómo va todo: el comentario de la mañana en el issue «Resumen diario».
- Desde el PC, el estado de inicio avisa pedidos en curso, preguntas y PRs de la nube (`bandeja.py --listar`).

## 6. Cambiar después (skill `configurar` → modo nube)
- Pausar o reanudar una tarea: `RemoteTrigger update` con `enabled` + `nube.py --pausar|--reanudar <tarea> --quien`.
- Cambiar el horario: `update` del cron + `nube.py --agregar <tarea> --cron ... --quien`.
- Quitar una tarea: borrarla o dejarla deshabilitada en la nube + `nube.py --quitar <tarea> --quien`.
- Desactivar todo: `nube.py --deshabilitar --quien --motivo` y pausar cada tarea en la nube.
Siempre con el sí del usuario y diciendo qué cambia.

## 7. Si algo falla
- Corrida de menos de 10 s: `get_run_log`; casi siempre es acceso al repositorio (la app) o el plan.
- Dos corridas chocan en una rama: la regla es una tarea a la vez (`bandeja.py --tomar`); si pasó, se cierra una de
  las dos ramas y se repite el pedido.
- Un PR con conflictos no se integra a ciegas: se pide a la nube actualizar la rama (comentario en el PR) o se
  resuelve desde el PC.
- La nube nunca debe tocar `main`, `settings.json`, `NUCLEO.txt` ni `nube.yaml`: si lo hizo, revisa el PR y avísame
  para corregir `NUBE.md`.

## Qué no hacer
- No crear, cambiar ni borrar tareas en la nube sin el sí explícito de ese paso.
- No activar el modo nube «por si acaso»: es una decisión del usuario.
- No prometer que la nube procesará documentos de `_entrada/`.
