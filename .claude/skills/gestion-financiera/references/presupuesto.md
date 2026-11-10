# Modo presupuesto: el año por línea y mes, con supuestos

1. **Supuestos primero** (`finanzas/supuestos.csv`): crecimiento de ventas, margen, dotación y remuneraciones, arriendos
   y contratos, inversiones, deuda y tasas, impuestos, estacionalidad. Cada uno con valor, fuente y confianza. Lo que
   dependa de afuera (precios, normativa, mercado) se verifica con `investigar`; lo tributario, con el contador.
2. **Base:** el real acumulado del año en curso (`--estados`) y, si hay, el presupuesto anterior. Muestra la base al
   usuario antes de proyectar: «este año llevamos X de ingresos con margen Y».
3. **Construir** `finanzas/presupuesto.csv`: una fila por línea de resultado y mes, con `version` (por ejemplo
   `2027-v1`). Partidas con estacionalidad se reparten por mes; las fijas, en doce. Mantén un script de cálculo en
   `scripts/` del proyecto si la empresa tiene reglas propias (comisiones, bonos, estacionalidad), con su `datos/LEEME.md`.
4. **Escenarios** (`escenarios.csv`): al menos pesimista y optimista sobre las líneas sensibles; muestra el resultado
   neto y la caja de cada uno.
5. **Revisión:** `--revisar` sin errores; margen bruto, EBITDA y resultado del año comparados con el real del año anterior.
   Pide una mirada a `revisor-independiente` si va al directorio.
6. **Aprobación:** entrega el Excel (`generar-reporte`, reporte `presupuesto-anual`, con fórmulas y la hoja de
   supuestos) y pide la aprobación a quien dice `finanzas.aprueba_presupuesto`, en dos líneas. Con el sí:
   `finanzas.version_presupuesto` en `proyecto.yaml` y la decisión en `seguimiento/decisiones.csv`.
7. **Nueva versión** (reforecast de presupuesto, no confundir con el forecast mensual): nueva `version`, nunca se
   editan las filas de una versión aprobada.
