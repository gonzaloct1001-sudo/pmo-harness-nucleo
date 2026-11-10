# Indicadores financieros de gestión: definición y lectura

Los calcula `finanzas.py` a partir de las líneas de `finanzas/lineas.yaml`; los umbrales están en
`metricas/metricas-finanzas.yaml` y cada empresa los ajusta a su rubro.

| Indicador | Cómo se calcula | Cómo se lee |
|---|---|---|
| Margen bruto % | (ingresos + otros ingresos − costo de ventas) / ingresos | Cuánto queda de cada peso vendido antes de los gastos; cae si suben los costos o bajan los precios |
| EBITDA y margen EBITDA % | margen bruto − gastos operacionales; EBITDA / ingresos | Resultado de la operación sin financiamiento, impuestos ni depreciación |
| Resultado neto | resultado antes de impuestos − impuestos | Lo que queda para los dueños |
| Caja | saldo de caja y bancos al cierre | Lo disponible; se concilia con los bancos |
| Meses de caja | caja / promedio mensual de (costo de ventas + gastos) de los últimos 3 meses | Cuántos meses de operación cubre la caja sin ingresos nuevos |
| DSO (días de cobro) | cuentas por cobrar / ingresos de los últimos 3 meses × 90 | Cuánto se demora en cobrar; sube si los clientes pagan tarde |
| DPO (días de pago) | cuentas por pagar / costo de ventas de los últimos 3 meses × 90 | Cuánto se demora en pagar a proveedores |
| DIO (días de inventario) | inventario / costo de ventas de los últimos 3 meses × 90 | Cuánto inventario hay en días de venta |
| Liquidez corriente | activo corriente / pasivo corriente | Bajo 1, los compromisos del año superan lo que se puede convertir en caja |
| Endeudamiento | (pasivo corriente + pasivo no corriente) / patrimonio | Cuánta deuda por cada peso de los dueños |
| Desvío de ingresos % | (real − presupuesto) / presupuesto, del mes | Positivo = se vendió más que lo presupuestado |
| Desvío de gastos % | (real − presupuesto) / presupuesto, de los gastos operacionales del mes | Positivo = se gastó más; es el que suele encender el semáforo |
| Cuentas sin mapear | cuentas de `real.csv` que no están en el plan de cuentas | Mientras haya, los estados no están completos |
| Períodos sin cerrar | meses con movimientos y sin cierre en `cierres.csv` | El cierre atrasado esconde desvíos |

Lectura conjunta: un mes con buen resultado y caja cayendo suele significar cobros atrasados (DSO sube) o inventario
creciendo (DIO sube). Un desvío de gastos aislado se explica; uno que se repite tres meses cambia el forecast.
