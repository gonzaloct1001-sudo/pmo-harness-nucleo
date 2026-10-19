---
tipo: reporte-semanal
nombre: Reporte de avance semanal
formato: docx
modo: generar
plantilla: ""                   # vacío = formato por defecto del harness (md_a_docx.py con la marca del proyecto)
cadencia: semanal
periodo_archivo: semana
destinatarios: [Carolina Pérez, Andrés Muñoz]
fuentes:
  - seguimiento/<semana>.md
  - cronograma/cronograma.csv
  - riesgos/riesgos.csv
  - riesgos/issues.csv
  - seguimiento/acuerdos.csv
  - seguimiento/decisiones.csv
---

# Propósito
Informar el estado del proyecto de la semana a la jefatura y al cliente. Debe leerse en 3 minutos.

# Secciones
1. **Encabezado** — proyecto, cliente, semana, fecha de emisión, responsable.
2. **Estado general** — semáforo (Verde / Amarillo / Rojo) y un párrafo de 3 a 5 líneas con lo más importante.
3. **Avance por subproyecto** — tabla: subproyecto, avance plan %, avance real %, desviación, estado. Sale de `validar_proyecto.py`.
4. **Logros de la semana** — desde la nota de seguimiento.
5. **Hitos próximos (30 días)** — desde el cronograma, tareas con `es_hito = si`.
6. **Riesgos principales** — los de severidad alta y los nuevos de la semana, con su plan de acción.
7. **Problemas abiertos** — issues abiertos con responsable y fecha.
8. **Decisiones y acuerdos** — decisiones de la semana y acuerdos vencidos o por vencer.
9. **Próximos pasos** — desde la nota de seguimiento.

# Reglas
- Semáforo: Verde si la desviación de todos los subproyectos es menor al umbral amarillo; Amarillo si alguno lo supera; Rojo si alguno supera el umbral rojo o hay un hito vencido.
- Máximo 2 páginas.
- No incluir montos salvo que la nota de la semana lo pida.

# Validaciones antes de entregar
- El avance de la tabla coincide con el cálculo de `validar_proyecto.py`.
- Todo riesgo alto mencionado existe en `riesgos.csv`.
- No quedan `[PENDIENTE]` sin avisar al usuario.
