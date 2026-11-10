# Desvíos y forecast

## Explicar un desvío
`finanzas.py --estados --periodo AAAA-MM` marca los desvíos relevantes (≥ 10 % y con monto). Para cada uno:
1. **Descomponer:** ¿precio o volumen (ingresos)? ¿costo unitario o mezcla (costo de ventas)? ¿una partida puntual o
   todas (gastos)? Mira las cuentas detrás de la línea en `real.csv` del mes contra los meses anteriores.
2. **Clasificar:** permanente (cambia el año) o temporal (se compensa); favorable o desfavorable.
3. **Acción:** qué se hace y quién, o qué decisión se necesita.
4. Lo que los datos no explican se pregunta: «el arriendo subió 3,5 millones en julio: ¿hubo un reajuste o un pago
   doble?». Nunca se inventa la causa.

## Forecast del año
- `finanzas.py --forecast --metodo presupuesto` (real a la fecha + presupuesto del resto) o `--metodo tendencia`
  (real a la fecha + promedio de los últimos tres meses). Queda en `forecast.csv` con versión y en `proyecto.yaml`.
- Ajustes manuales (un contrato nuevo, un gasto que no se repite): edita las filas de esa versión en `forecast.csv`
  con `metodo: manual` y la razón en `nota`.
- En el informe, el año se muestra como «real + forecast» contra presupuesto; la versión del forecast se nombra.
- Un desvío que se repite tres meses no es ruido: cambia el forecast y, si corresponde, propón una nueva versión del
  presupuesto (modo presupuesto).
