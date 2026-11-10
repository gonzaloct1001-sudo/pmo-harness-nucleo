# Modo proyección: resultados, balance y caja a varios años

1. **Supuestos** en `finanzas/proyeccion.yaml`: crecimiento de ingresos por año, margen bruto, gastos como % de
   ingresos, depreciación y capex, días de cobro, pago e inventario, tasa de impuesto, deuda (tasa y amortización) y
   dividendos. La base sale del real acumulado si existe (o se escribe en `base`). Cada supuesto con fuente en
   `supuestos.csv`; los que dependen de afuera, con `investigar`.
2. `finanzas.py --proyectar --excel proyeccion.xlsx`: tabla por año y Excel con fórmulas (hoja Supuestos con celdas de
   entrada en azul; hoja Proyección que se recalcula al cambiar un supuesto). El balance cuadra por construcción; si
   la caja se vuelve negativa, el script lo dice: ahí hay una decisión de financiamiento.
3. **Sensibilidad:** cambia uno a uno los supuestos sensibles (crecimiento, margen, días de cobro) y muestra el efecto
   en caja y resultado; para una inversión específica, `evaluacion-economica` (VAN, TIR).
4. Presenta las alternativas con sus supuestos; la decisión (endeudarse, invertir, repartir) es de la gerencia y el
   directorio.
