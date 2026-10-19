---
name: gestionar-sprint
description: Gestión ágil del equipo — planificación de sprint (capacidad, velocidad, compromiso), seguimiento diario o standup, burndown, revisión de sprint, retrospectiva y cierre, manejo del backlog e importación desde GitHub o Jira, con métricas de velocidad, cumplimiento, trabajo en curso y tiempo de ciclo. Úsala en proyectos con arquetipo ágil cuando el usuario hable de sprints, backlog, historias, puntos, daily, standup, planning, review, retro, velocidad, tablero, o pida actualizar o importar el backlog.
---

# Gestionar sprint

Archivos: `agil/backlog.csv`, `agil/sprints.csv`, `agil/estados.yaml`, `agil/retrospectivas/`.
Métricas: `python herramientas/metricas_agil.py <proyecto> [--fecha AAAA-MM-DD]`.
Importación: `python herramientas/importar_backlog.py <proyecto> --desde github --repo X` o `--desde csv --archivo Y`
(usa `--simular` primero y muestra el resultado antes de escribir).

## Planificación
1. Ejecuta las métricas: velocidad promedio y cumplimiento de los últimos 3 sprints.
2. Pregunta la **capacidad** del sprint (ausencias, feriados, dedicación a otras tareas) y ajusta la velocidad proporcionalmente.
3. Propón el compromiso: ítems en orden de prioridad que cumplan la definición de listo, hasta la capacidad
   ajustada. Advierte si se compromete más del 110% de la velocidad ajustada o si hay ítems sin estimar.
4. Redacta con el equipo un **objetivo de sprint** (qué valor se entrega, en una frase).
5. Registra el sprint en `sprints.csv` (estado `activo`, comprometido_pts) y asigna el sprint a los ítems.

## Seguimiento diario (standup)
Con lo que informe el usuario, actualiza estados y fechas (`fecha_inicio` al pasar a en progreso,
`fecha_cierre` al terminar). Luego resume: avance vs tiempo transcurrido (burndown), bloqueos, ítems
estancados (más de 3 días en el mismo estado), trabajo en curso vs límite.

## Revisión y cierre
1. Métricas del sprint; qué se terminó según la definición de hecho y qué no.
2. Lo no terminado vuelve al backlog o pasa al siguiente sprint (decisión del dueño de producto).
3. Registra `completado_pts` y estado `cerrado` en `sprints.csv`.
4. Genera el resumen con `generar-reporte` (`sprint-review`).

## Retrospectiva
Estructura: qué funcionó, qué no, qué probaremos. Aporta datos (métricas, incidentes, bugs del sprint)
para que la conversación no sea solo de percepciones. Guarda `agil/retrospectivas/<sprint>.md` con
acciones y responsables; las acciones relevantes pasan al backlog o a `seguimiento/acuerdos.csv`.

## Backlog
- Toda historia con criterio de aceptación; bugs con pasos para reproducir; deuda enlazada a `ingenieria/deuda-tecnica.csv`.
- Si el backlog oficial vive en GitHub o Jira, **esa es la fuente de verdad**: importa antes de analizar y no
  edites estados localmente sin avisar que habrá diferencias.
