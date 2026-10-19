# Datos de la cartera (FICTICIOS)

| Archivo | Formato | Origen |
|---|---|---|
| `transacciones.csv` | fecha, ticker, operacion (compra/venta), cantidad, precio, comision | registro propio / cartola del broker |
| `precios.csv` | fecha, ticker, cierre (incluye el índice de referencia) | exportación de precios de cierre mensuales |
| `fundamentos.csv` | fecha, ticker, roe, pu, deuda_ebitda, dividend_yield (fracciones y múltiplos) | estados financieros / proveedor de datos |
| `parametros.yaml` | índice de referencia, tasa libre de riesgo, ventana | definido por el titular |

Convención: fechas AAAA-MM-DD; porcentajes como fracción (0,12 = 12%); precios en CLP.
