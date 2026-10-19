---
tipo: revision-periodica
nombre: Revisión periódica de la cartera
formato: docx
modo: generar
plantilla: ""
cadencia: mensual
periodo_archivo: mes
destinatarios: []
fuentes:
  - items/items.csv
  - items/fichas/
  - metricas/metricas.yaml
  - metricas/mediciones.csv
  - seguimiento/decisiones.csv
  - riesgos/riesgos.csv
---

# Propósito
Mostrar el estado de la cartera en el período: cómo se comportan los ítems activos, qué incumple reglas,
qué se movió entre etapas y qué decisiones hay que tomar.

# Secciones
1. **Resumen** — 3 a 5 líneas: estado general, lo más relevante del período, decisiones pendientes.
2. **Métricas de la cartera** — métricas de nivel proyecto con semáforo (de `evaluar_metricas.py`).
3. **Cumplimiento de reglas** — reglas incumplidas, con severidad y propuesta de acción.
4. **Ítems activos** — tabla con las métricas clave de cada ítem y su semáforo.
5. **Pipeline** — cantidad de ítems por etapa y movimientos del período.
6. **Fichas por revisar** — fichas con revisión vencida o por vencer en 30 días.
7. **Decisiones del período** — desde `seguimiento/decisiones.csv`.
8. **Riesgos** — riesgos altos y nuevos.
9. **Próximos pasos**.

# Validaciones antes de entregar
- Las cifras coinciden con la última ejecución de `evaluar_metricas.py`.
- Las mediciones usadas no están desactualizadas respecto de su frecuencia.
