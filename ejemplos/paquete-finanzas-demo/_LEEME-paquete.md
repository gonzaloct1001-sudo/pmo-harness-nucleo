# Paquete ficticio de finanzas

`balance_comprobacion_2026-10.xlsx` es la exportación de octubre de 2026 de la contabilidad ficticia de la
Distribuidora Valle Sur, con el formato típico de un sistema contable (títulos arriba, fila de encabezados en la
fila 4, columnas Código / Cuenta / Débitos / Créditos / Saldo Deudor / Saldo Acreedor y una fila de totales).

Para probarlo sobre `ejemplos/finanzas-demo` (que tiene real hasta septiembre):
1. `python herramientas/finanzas.py ejemplos/finanzas-demo --importar ejemplos/paquete-finanzas-demo/balance_comprobacion_2026-10.xlsx --periodo 2026-10 --vista-previa`
   → detecta la fila 4 y las columnas, cuadra, omite la fila de totales.
2. Sin `--vista-previa` importa; luego `--estados --periodo 2026-10`.
