---
tipo: acta-evaluacion
nombre: Acta de evaluación y ranking
formato: docx
modo: generar
plantilla: ""
cadencia: a pedido
periodo_archivo: mes
destinatarios: []
fuentes:
  - evaluacion/pauta.yaml
  - evaluacion/admisibilidad.csv
  - evaluacion/puntajes.csv
  - evaluacion/evaluaciones/
  - herramientas/puntaje_pauta.py
---

# Secciones
1. **Antecedentes** — convocatoria, presupuesto, fecha, evaluadores.
2. **Pauta aplicada** — criterios, ponderaciones y umbrales.
3. **Admisibilidad** — tabla por postulación con requisitos incumplidos.
4. **Ranking** — postulaciones admisibles ordenadas: puntaje ponderado, puntaje por criterio, cumple umbrales, monto solicitado y acumulado.
5. **Discrepancias entre evaluadores y cómo se resolvieron** (si hubo varios evaluadores).
6. **Propuesta de selección** — dentro del presupuesto, lista de espera y no seleccionadas con su causa.
7. **Firmas** — espacio para evaluadores responsables.

Pie: "Evaluación preparada con apoyo de IA; puntajes revisados y firmados por los evaluadores responsables."

# Validaciones
- Ponderaciones suman 1 y cada puntaje está dentro de la escala.
- No quedan evaluaciones en estado "propuesta" (todas revisadas por un evaluador humano).
