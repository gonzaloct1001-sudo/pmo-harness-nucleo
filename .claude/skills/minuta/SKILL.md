---
name: minuta
description: Convierte notas de una reunión (apuntes en bruto, transcripción, resumen de audio, correo) en una minuta formal con asistentes, temas, acuerdos con responsable y fecha, decisiones y riesgos detectados, y actualiza los registros del proyecto. Úsala siempre que el usuario mencione una reunión, comité, junta, kickoff, sesión de seguimiento o pida un acta o minuta, aunque solo pegue notas desordenadas.
---

# Minuta de reunión

## Pasos
1. Identifica el proyecto y lee `contexto/stakeholders.csv` (para normalizar nombres y cargos).
2. Si el proyecto tiene `minutas/_formato.md`, úsalo. Si no, usa `references/formato-minuta.md`.
3. Extrae de las notas: datos de la reunión, asistentes, temas tratados, acuerdos, decisiones, riesgos o
   problemas mencionados y próxima reunión.
4. Para cada acuerdo exige responsable y fecha. Si faltan, marca `[PENDIENTE: responsable]` o
   `[PENDIENTE: fecha]` y pregúntalo al final. No asignes responsables por deducción.
5. Si un asistente no está en stakeholders, pregunta si se agrega.
6. Guarda la minuta en `minutas/AAAA-MM-DD_<tema-corto>.md`.
7. Propón (y aplica tras confirmar):
   - acuerdos → `seguimiento/acuerdos.csv` (id correlativo A-001…, origen = nombre del archivo de la minuta)
   - decisiones → `seguimiento/decisiones.csv` (D-001…)
   - riesgos o problemas → vía `riesgos-issues`
   - solicitudes de cambio → vía `control-cambios`
8. Si el usuario lo pide o el catálogo lo define, genera el Word con `herramientas/md_a_docx.py` y/o un
   borrador de correo breve para enviar la minuta a los asistentes.

## Reglas
- Redacta los acuerdos como acciones verificables: "Andrés Muñoz enviará el listado de interfaces (02-10-2026)".
- Separa lo acordado de lo simplemente conversado. Ante la duda, pregunta.
- No incluyas comentarios personales ni juicios sobre personas.
