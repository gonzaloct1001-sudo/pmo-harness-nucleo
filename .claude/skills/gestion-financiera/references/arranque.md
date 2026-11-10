# Modo arranque: dejar las finanzas operando

Objetivo: plan de cuentas mapeado, histórico cargado, presupuesto vigente y primer estado de gestión. Suele tomar una o
dos sesiones. Pregunta lo mínimo (mini entrevista del arquetipo) y propone el resto.

1. **Configurar** el bloque `finanzas` de `proyecto.yaml`: moneda, mes de inicio del año fiscal, sistema contable, quién
   aprueba el presupuesto y el cierre, día objetivo de cierre.
2. **Plan de cuentas.** Pide el plan de cuentas de la empresa (Excel o CSV en `_entrada/10-contabilidad/`). Mapea cada
   cuenta a una línea de `finanzas/lineas.yaml` (tipo + línea) en `finanzas/plan-de-cuentas.csv`. Si no tiene plan,
   parte de `biblioteca/finanzas/plan-de-cuentas-base.csv` y adáptalo. Si las líneas del harness no calzan con cómo
   la empresa lee sus números (otros subtotales, otra apertura de gastos), ajusta `lineas.yaml` del proyecto: es suyo.
   Cuentas de orden → tipo `orden` (no entran a los estados).
3. **Saldos de apertura.** Importa el balance al cierre del año anterior con `--importar <archivo> --inicial` (o los
   saldos de apertura del primer mes). Sin apertura, el balance del harness solo muestra los movimientos del año.
4. **Histórico del año.** Un `--importar <archivo> --periodo AAAA-MM` por mes (o `--acumulado` si el sistema exporta
   acumulados). Después de cada uno: cuentas sin mapear → mapearlas → `--revisar` hasta 0 errores.
5. **Presupuesto.** Si ya existe, cárgalo en `presupuesto.csv` por línea y mes con su versión; si no, modo presupuesto.
6. **Primer estado:** `--estados --periodo <último>` y `--registrar`. Explica al usuario las tres cosas que más llaman
   la atención y pregunta si los umbrales de `metricas-finanzas.yaml` calzan con su rubro.
7. **Formatos:** si la empresa tiene su informe o su presentación, `adoptar-formatos` antes del primer cierre.
8. Cierra los meses ya revisados (`--cerrar`) para que el historial quede protegido, y deja el traspaso con la fecha
   del próximo cierre.
