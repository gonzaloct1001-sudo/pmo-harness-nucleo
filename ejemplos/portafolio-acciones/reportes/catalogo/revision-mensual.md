---
tipo: revision-mensual
nombre: Revisión mensual del portafolio
formato: docx
modo: generar
plantilla: ""
cadencia: mensual
periodo_archivo: mes
destinatarios: [Titular]
fuentes:
  - metricas/mediciones.csv          # previa ejecución de scripts/calcular_cartera.py
  - herramientas/evaluar_metricas.py # semáforos, reglas, etapas y fichas
  - items/items.csv
  - items/fichas/
  - seguimiento/decisiones.csv
  - riesgos/riesgos.csv
---

# Propósito
Revisión mensual del portafolio: desempeño contra el índice, cumplimiento de la política de inversión,
estado de cada posición, pipeline de candidatas y decisiones pendientes. Apoya las decisiones del titular;
no recomienda comprar ni vender.

# Secciones
1. **Resumen del mes** — 3 a 5 líneas: valor, retorno 12m vs índice, incumplimientos de política y decisiones pendientes.
2. **Desempeño** — tabla de métricas de cartera con valor actual, mes anterior y semáforo.
3. **Cumplimiento de la política** — cada regla (POL-01 a POL-04) con estado Cumple / No cumple y detalle.
4. **Posiciones** — tabla por acción: peso, rentabilidad, volatilidad, caída máxima, ROE, deuda/EBITDA, con semáforo.
5. **Pipeline de candidatas** — acciones por etapa, candidatas a avanzar y requisitos pendientes.
6. **Tesis por revisar** — fichas con revisión vencida o por vencer, y posiciones que activaron condiciones de revisión.
7. **Decisiones del mes** — desde `decisiones.csv`; si no hubo, indicarlo.
8. **Riesgos** — riesgos abiertos de severidad media y alta.
9. **Preguntas para el titular** — decisiones que la evaluación deja planteadas (ej.: rebalancear, pasar una acción a revisión). Redactar como preguntas, no como recomendaciones.

Pie: "Herramienta de seguimiento con datos del titular. No constituye recomendación de inversión."

# Reglas
- Ejecutar primero `scripts/calcular_cartera.py` con la fecha de cierre del mes y luego `evaluar_metricas.py`.
- Porcentajes con un decimal; montos en CLP sin decimales.

# Validaciones antes de entregar
- Las cifras coinciden con `mediciones.csv` a la fecha de cierre.
- Todas las reglas de la política aparecen en la sección 3.
