---
name: red-team
description: Panel de revisores con perspectivas distintas (evaluador duro, competidor, auditor, usuario final) que ataca una propuesta, informe o entregable antes de enviarlo: puntaje estimado, fallas fatales, dudas que haría un jurado y plan de respuesta, cada perspectiva en contexto aislado. Úsala con «red team», «revísalo como el jurado», «¿qué le falta?», o antes de una entrega importante.
---

> Reglas que aplican (léelas si no están en tu contexto): `reglas/trabajo.md`, `reglas/datos.md`, `reglas/entregables.md`, `reglas/nucleo.md`.

# Red team

Objetivo: descubrir antes que el comité por qué la propuesta podría perder o quedar fuera, y convertirlo en
correcciones concretas. En postulaciones, los archivos van en `redteam/`; fuera de postulaciones, en
`seguimiento/revisiones/red-team-<fecha>/`.

## 1. Preparar la ronda
1. Ronda: `rosa` (primer borrador completo), `roja` (casi final), `roja-2` (verificación de correcciones) u otra.
2. Material que recibe cada revisor (y **solo** eso): bases vigentes con sus aclaraciones (o los términos de
   referencia del informe), la pauta inversa (`postulacion/pauta-inversa.yaml`), las secciones de `propuesta/` y el
   presupuesto en formato legible: `economico/presupuesto.yaml` y `economico/controles.csv` (el subagente no puede
   leer el .xlsx). Nunca borradores anteriores, estrategia interna ni
   discusiones del equipo: el revisor debe leer como el comité.
3. Perspectivas: `redteam/perspectivas.yaml` (configurable). Para un informe que no es postulación, usa las
   pertinentes (evaluador, experto escéptico, auditor, abogado del diablo) y una pauta simple acordada con el usuario.

## 2. Ejecutar (en paralelo, contexto aislado)
Lanza un subagente `revisor-red-team` por perspectiva, en paralelo, con: ruta del proyecto, ronda, perspectiva
(id, nombre y foco), lista exacta de archivos que puede leer y ruta del informe a escribir
(`redteam/<fecha>_<ronda>_<perspectiva>.md`, plantilla `redteam/_plantilla-informe.md`). En la ronda `roja-2` basta con
repuntuar los criterios afectados: el puntaje estimado usa, por perspectiva y criterio, el último puntaje registrado.
Cada revisor recibe además la lista de observaciones de la ronda anterior para verificar si se cerraron.

## 3. Consolidar
1. Puntajes: agrega a `redteam/puntajes.csv` una fila por perspectiva que puntúa y criterio
   (ronda, perspectiva, criterio, puntaje, justificacion, fecha).
2. Observaciones: agrega a `redteam/observaciones.csv` cada falla fatal, debilidad, recomendación y pregunta
   (id RT-nn, ronda, perspectiva, tipo, seccion, observacion), sin duplicar: si dos perspectivas señalan lo mismo,
   una sola fila que lo mencione ("coinciden: financiero, auditor") y con más prioridad.
3. `python herramientas/postulacion.py proyectos/<slug> --registrar` → puntaje estimado (promedio, mínimo, dispersión) frente al
   mínimo de las bases y al objetivo, criterios bajo el mínimo y fallas fatales abiertas.
4. Escribe el consolidado de la ronda (`redteam/<fecha>_ronda-<ronda>.md`) según el reporte `informe-red-team`:
   resultado, fallas fatales, debilidades priorizadas por impacto (peso del criterio × brecha), preguntas probables.

## 4. Plan de respuesta (con el usuario)
Para cada observación propone `respuesta` (aceptar | rechazar con fundamento | investigar), `accion` concreta
(qué cambiar y en qué sección), `responsable` y estado. El usuario decide; tú aplicas las correcciones aceptadas en
las secciones (o las delegas) y marcas `cerrada` solo cuando están hechas. Las fallas fatales bloquean la entrega.

## 5. Criterios de calidad
- Cada puntaje cita evidencia de la propuesta (sección y frase); sin evidencia, el mínimo de la escala.
- Nada de crítica genérica: toda debilidad trae una recomendación accionable.
- Dispersión alta entre revisores (≥ 1 punto) en un criterio: revisarlo; suele indicar que la propuesta es ambigua.
- El red team propone; el equipo y el postulante deciden.
