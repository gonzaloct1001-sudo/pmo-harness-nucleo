---
tipo: informe-red-team
nombre: Informe consolidado del red team
formato: md
modo: generar
plantilla: ""
cadencia: a pedido              # uno por ronda (rosa, roja, segunda roja)
periodo_archivo: semana
destinatarios: []               # equipo que redacta y quien aprueba (revisión oro)
fuentes:
  - redteam/
  - postulacion/pauta-inversa.yaml
  - herramientas/postulacion.py
---

# Propósito
Consolidar la ronda del red team en decisiones: qué corregir, en qué orden y quién, para subir el puntaje y
eliminar riesgos de inadmisibilidad. Documento interno.

# Secciones
1. **Resultado de la ronda** — puntaje estimado (promedio, mínimo, máximo) frente a mínimo y objetivo; por criterio.
2. **Fallas fatales** — cada una con responsable y fecha; bloquean la entrega.
3. **Debilidades priorizadas** — por impacto en el puntaje (peso del criterio × brecha de puntaje).
4. **Plan de respuesta** — cada observación: aceptar / rechazar con fundamento / investigar (de `redteam/observaciones.csv`).
5. **Preguntas probables del comité** — con la respuesta que debe quedar en la propuesta o en la presentación.
6. **Coincidencias entre perspectivas** — lo que señalan dos o más revisores pesa más.
7. **Siguiente ronda** — qué debe verificar la próxima revisión.
