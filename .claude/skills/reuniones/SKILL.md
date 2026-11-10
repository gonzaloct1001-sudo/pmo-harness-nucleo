---
name: reuniones
description: Antes y después de cualquier reunión del proyecto (comité, seguimiento, kickoff, cliente, sprint review, cierre): arma la agenda con estado, pendientes, decisiones a pedir y preguntas difíciles; y convierte notas, transcripción o correo en la minuta formal, llevando acuerdos, decisiones y riesgos a los registros. Úsala cuando el usuario mencione una reunión, comité o acta, o pegue notas desordenadas.
---

> Reglas que aplican (léelas si no están en tu contexto): `reglas/trabajo.md`, `reglas/datos.md`, `reglas/entregables.md`.

# Reuniones

- **Antes** (agenda, estado, decisiones a pedir, preguntas difíciles): lo que sigue en este archivo.
- **Después** (notas, transcripción o correo → minuta con acuerdos, decisiones y riesgos a los registros):
  `references/minuta.md`; el formato de la minuta, en `references/formato-minuta.md`.

## Antes de la reunión

## 1. Contexto
Pregunta solo lo que falte: tipo de reunión, fecha y duración, asistentes y objetivo (qué debe salir de ella).

## 2. Reunir información (solo lo necesario)
- Estado: `evaluar_metricas.py` y/o `validar_proyecto.py` con fecha de corte de la reunión.
- Acuerdos abiertos y vencidos de `seguimiento/acuerdos.csv` (en especial los de la reunión anterior del mismo tipo).
- Decisiones pendientes: cambios en análisis, ítems por mover de etapa, reglas incumplidas, riesgos altos sin plan.
- Última minuta del mismo tipo de reunión (en `minutas/`).
- Asistentes en `contexto/stakeholders.csv`: rol, poder, interés y qué le importa a cada uno.

## 3. Documento de preparación
Guarda `minutas/AAAA-MM-DD_<tipo>_preparacion.md` con:
1. **Objetivo** de la reunión en una línea y **resultado esperado** (decisiones o acuerdos que se buscan).
2. **Agenda con tiempos** (que sume la duración; lo más importante primero, nunca al final).
3. **Estado en 5 líneas** y una tabla corta de indicadores con semáforo.
4. **Seguimiento de acuerdos anteriores**: cumplidos, vencidos y en curso.
5. **Decisiones a solicitar**: para cada una, opciones, recomendación del equipo si existe y consecuencia de no decidir.
6. **Preguntas difíciles probables** y respuesta sugerida con su dato de respaldo. Para una mirada externa,
   puedes pedir al subagente `revisor-independiente` que proponga las preguntas que haría un asistente escéptico.
7. **Material previo** a enviar y a quién (con 24–48 h de anticipación si es comité).
8. **Mensajes clave por asistente** si hay asistentes de alto poder con intereses distintos.

Según el tipo:
- **Comité**: foco en decisiones, desvíos, riesgos altos y cambios; nada operativo.
- **Kickoff**: objetivos, alcance, roles, gobierno, calendario de reuniones, riesgos iniciales, próximos pasos.
- **Sprint review / retrospectiva**: ver skill `gestionar-sprint`.
- **Cierre**: cumplimiento de objetivos, pendientes de traspaso, lecciones aprendidas.

## 4. Opcionales
- Presentación: si el usuario la pide, usa el catálogo (`reportes`) o crea el formato con `reportes`.
- Convocatoria: borrador de correo con agenda y material previo.
- Después de la reunión: `references/minuta.md` toma la preparación como base para no repetir trabajo.
