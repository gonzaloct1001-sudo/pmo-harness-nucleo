---
tipo: informe-estudio
nombre: Informe del estudio
formato: docx
modo: generar
plantilla: ""
cadencia: a pedido
periodo_archivo: mes
destinatarios: []
fuentes:
  - estudio/
  - metricas/mediciones.csv
  - riesgos/riesgos.csv
---

# Secciones
1. **Resumen ejecutivo** — decisión que apoya, recomendación y fundamentos en media página.
2. **Antecedentes y alcance** — qué se estudió y qué no.
3. **Preguntas y respuestas** — desde `preguntas.md`.
4. **Supuestos** — tabla con fuente y confianza; destacar los de alta sensibilidad.
5. **Análisis** — resultados del modelo (ej.: flujo de caja, VAN, TIR) y escenarios.
6. **Riesgos**.
7. **Conclusiones y recomendación** — desde `conclusiones.md`.
8. **Anexos** — fuentes consultadas.

# Validaciones
- Todo número del informe tiene fuente en `supuestos.csv`, el modelo o `mediciones.csv`.
- Los supuestos de baja confianza y alta sensibilidad se mencionan explícitamente.
