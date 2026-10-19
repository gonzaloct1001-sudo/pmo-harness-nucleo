---
name: registro-ingenieria
description: Registros de ingeniería de software — decisiones de arquitectura (ADR), deuda técnica priorizada, matriz de trazabilidad requisito→diseño→historia→prueba, registro de despliegues y métricas DORA, postmortems de incidentes y checklist de despliegue. Úsala cuando el usuario tome o discuta una decisión técnica, mencione deuda técnica, requisitos o su cobertura de pruebas, un despliegue, un incidente o caída en producción, o pida preparar o revisar un pase a producción.
---

# Registros de ingeniería

Carpeta `ingenieria/` (arquetipo ágil). Métricas: `python herramientas/metricas_agil.py <proyecto>`.

## Decisión de arquitectura (ADR)
Cuando se decide algo difícil de revertir (tecnología, integración, modelo de datos, seguridad):
crea `ingenieria/adr/ADR-NNN.md` desde `_plantilla-adr.md` con contexto, opciones reales (al menos 2),
decisión y consecuencias. Estado `propuesta` hasta que se acepte. Si reemplaza otra, enlaza ambas.
Vincula el ADR en los requisitos que afecta.

## Deuda técnica
Registra en `deuda-tecnica.csv` con impacto (1–5), esfuerzo (1–5) y el **costo de no pagarla** en términos
del negocio. Prioridad sugerida: alta si impacto ≥ 4, o si causó un incidente; media si impacto 3; baja el
resto. Para abordarla, crea un ítem de backlog tipo `deuda` y enlázalo. En la planificación, recuerda la
deuda alta abierta.

## Trazabilidad
`requisitos.csv`: cada requisito con origen (especificación, cambio, postmortem, legal), ADR, historias y
pruebas. Revisa huecos: requisitos sin historia (no se va a construir), sin prueba (no se puede verificar),
historias sin requisito (¿alcance no acordado?). Cuando un cambio de alcance agrega requisitos, anota el
origen (ej.: la solicitud de cambio).

## Despliegues y DORA
Cada despliegue en `despliegues.csv`: fecha, versión, entorno, resultado (exito / falla / rollback), si causó
incidente, minutos de recuperación y tiempo de entrega (horas desde el commit). Antes de un pase a producción,
recorre `checklist-despliegue.md` con el usuario. Interpreta las métricas DORA con tendencia, no como nota:
lo importante es si mejoran.

## Postmortem
Tras un incidente: `postmortems/PM-NNN.md` desde la plantilla, **sin culpables** (qué condiciones lo
permitieron). Acciones con responsable y fecha, que pasan al backlog y, si corresponde, a deuda técnica,
requisitos (nuevos requisitos no funcionales) o al checklist de despliegue. Si el incidente afectó al
cliente, registra también un issue con `riesgos-issues`.
