---
tipo: pep
nombre: PEP — Planilla de Estado del Programa
formato: xlsx
modo: actualizar                # se actualiza el último emitido; nunca se regenera
plantilla: reportes/plantillas/pep.xlsx   # solo si no hay emitidos previos
cadencia: mensual
periodo_archivo: mes
destinatarios: [Rodrigo Soto, Control de Gestión]
fuentes:
  - cronograma/cronograma.csv   # avance plan y real (vía validar_proyecto.py con corte a fin de mes)
  - seguimiento/                # notas de las semanas del mes, para el comentario
  - insumo manual               # gasto acumulado por subproyecto (lo entrega Control de Gestión)
---

# Propósito
Planilla mensual para Control de Gestión y Finanzas: avance ponderado por subproyecto y ejecución presupuestaria.
Es un archivo acumulativo con fórmulas: se actualiza sobre la versión del mes anterior.

# Mapeo
| Hoja | Celda o rango | Dato | Fuente |
|---|---|---|---|
| Resumen | C4 | Período `AAAA-MM` | período del reporte |
| Resumen | C5 | Fecha de corte (último día hábil del mes) | calendario |
| Resumen | C6 | Estado general: Verde / Amarillo / Rojo | mismo criterio que el reporte semanal |
| Resumen | C7 | Comentario del mes (máx. 200 caracteres) | notas de seguimiento del mes |
| Avance | D5:D9 | Avance plan por subproyecto (fracción, 0,46 = 46%) | `validar_proyecto.py --hoy <corte>` |
| Avance | E5:E9 | Avance real por subproyecto (fracción) | `validar_proyecto.py --hoy <corte>` |
| Avance | I5:I9 | Comentario por subproyecto | notas de seguimiento |
| Presupuesto | D5:D9 | Gasto acumulado CLP | **insumo manual**: pedirlo al usuario |

Filas: 5 = SP0, 6 = SP1, 7 = SP2, 8 = SP3, 9 = SP4.

# Reglas
- No tocar columnas C (pesos), F, G, H ni la fila 10: son fórmulas o parámetros fijos.
- No tocar la hoja Presupuesto columna C (presupuesto vigente) salvo que haya una enmienda que lo cambie.
- Si el usuario no entrega el gasto del mes, dejar el del mes anterior y avisarlo como pendiente.

# Validaciones antes de entregar
- El avance real de cada subproyecto coincide con el cronograma (tolerancia 1 punto).
- La suma del presupuesto vigente (Presupuesto!C10) es igual a `linea_base.monto_vigente`.
- El gasto acumulado de cada subproyecto no disminuye respecto del mes anterior.
