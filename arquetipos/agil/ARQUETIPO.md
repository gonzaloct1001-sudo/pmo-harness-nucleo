# Arquetipo: Ágil / desarrollo de software

## Cuándo usarlo
Equipos que entregan en iteraciones (Scrum, Kanban o híbrido): desarrollo de software, productos
digitales, equipos de datos. Se puede combinar con `ejecucion` cuando además hay contrato, hitos
comprometidos o un programa mayor (ej.: `--arquetipos ejecucion,agil`).

## Qué agrega a la base
- `agil/backlog.csv` — historias, bugs, tareas, deuda, épicas: estado, sprint, puntos, fechas.
- `agil/sprints.csv` — sprints con objetivo, comprometido y completado.
- `agil/estados.yaml` — flujo del tablero, equivalencias para importar, límite de trabajo en curso,
  definición de listo y de hecho.
- `agil/retrospectivas/` — una retrospectiva por sprint.
- `ingenieria/adr/` — registros de decisiones de arquitectura.
- `ingenieria/deuda-tecnica.csv` — deuda técnica priorizada por impacto y esfuerzo.
- `ingenieria/requisitos.csv` — matriz de trazabilidad requisito → ADR → historias → pruebas.
- `ingenieria/despliegues.csv` — registro de despliegues (base de las métricas DORA).
- `ingenieria/postmortems/` y `ingenieria/checklist-despliegue.md`.
- Métricas: velocidad, cumplimiento del compromiso, trabajo en curso, bugs, tiempo de ciclo, DORA,
  deuda técnica, requisitos sin prueba (`metricas/metricas-agil.yaml`, calculadas con `python herramientas/metricas_agil.py <proyecto>`).
- Reportes: `sprint-review` y `estado-entrega`.

## Integración con herramientas del equipo
El tablero oficial puede seguir en GitHub o Jira: `python herramientas/importar_backlog.py` trae los ítems
(GitHub con la CLI `gh`; Jira con una exportación CSV) y el harness agrega la capa de gestión.

## Skills
`gestionar-sprint`, `registro-ingenieria`, más las generales (`preparar-reunion`, `levantar-riesgos`, `generar-reporte`).

## Preguntas de la mini entrevista
1. ¿Scrum (sprints) o flujo continuo (Kanban)? ¿Duración del sprint?
2. ¿Dónde vive hoy el backlog (GitHub, Jira, planilla)?
3. ¿Quién es el dueño de producto y quién recibe los reportes?
4. ¿Se registran los despliegues? ¿Hay ambientes de prueba y producción separados?
5. ¿Hay contrato, hitos comprometidos o un programa mayor (combinar con `ejecucion`)?
