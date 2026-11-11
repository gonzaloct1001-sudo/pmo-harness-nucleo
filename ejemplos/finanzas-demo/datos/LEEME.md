# Datos de entrada del proyecto

Archivos de datos que alimentan los cálculos (exportaciones de sistemas, planillas de precios,
registros de transacciones, resultados de pruebas, etc.), en CSV cuando sea posible.
Documentar aquí el origen y el formato de cada archivo.

- `ventas-mensuales.csv`: serie ficticia de 48 meses (columnas `mes`, `ventas` en MM$), con crecimiento que se acelera
  y un patrón que se repite cada año. Sirve para probar `experto.py pronosticar` (ver `ejemplos/LEEME.md`).
