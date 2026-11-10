---
tipo: presupuesto-anual
nombre: Presupuesto anual
formato: xlsx
modo: generar
plantilla: ""
cadencia: anual
periodo_archivo: mes
destinatarios: []
fuentes:
  - finanzas/presupuesto.csv
  - finanzas/supuestos.csv
  - finanzas/escenarios.csv
claves: [presupuesto, anual, budget, supuestos, escenarios, plan financiero]
---

# Propósito
El presupuesto del año fiscal por línea y mes, con sus supuestos y escenarios, para que lo apruebe quien corresponda
(`finanzas.aprueba_presupuesto` en `proyecto.yaml`) y quede como la versión vigente contra la que se mide cada mes.

# Secciones (hojas)
1. **Supuestos** — cada supuesto con valor, fuente y confianza (`supuestos.csv`); celdas de entrada.
2. **Presupuesto** — líneas de resultado por mes y total anual, con fórmulas que referencian los supuestos.
3. **Escenarios** — base, optimista y pesimista (`escenarios.csv`) aplicados a las líneas que afectan.
4. **Resumen** — margen bruto, EBITDA y resultado neto del año; comparación con el año anterior si hay real.

# Validaciones antes de entregar
- Todo supuesto relevante tiene fuente; los de confianza baja están destacados.
- La versión queda registrada en `presupuesto.csv` (`version`) y en `proyecto.yaml` (`finanzas.version_presupuesto`).
- Quién aprobó y cuándo, en `seguimiento/decisiones.csv`.
