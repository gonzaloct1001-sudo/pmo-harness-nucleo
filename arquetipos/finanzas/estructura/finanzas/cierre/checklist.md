# Checklist del cierre mensual

<!-- Se copia a cierre/AAAA-MM.md en cada cierre y se marca. Lo que no aplica se tacha con el motivo. -->

Período: AAAA-MM · Responsable: · Fecha de inicio:

## Antes de importar
- [ ] La contabilidad del mes está cerrada en el sistema contable (sin asientos pendientes del período).
- [ ] Exportación del balance de comprobación o libro mayor del mes en `_entrada/10-contabilidad/`.

## Importar y cuadrar
- [ ] `finanzas.py --importar <archivo> --periodo AAAA-MM --vista-previa`: columnas detectadas correctas.
- [ ] Importado; **cero cuentas sin mapear** (o mapeadas en `plan-de-cuentas.csv` y reimportado).
- [ ] El período cuadra: debe = haber; activo = pasivo + patrimonio (`finanzas.py --revisar`).
- [ ] Caja conciliada con los bancos (saldo del balance = cartolas).

## Revisar
- [ ] Provisiones y devengos del mes (remuneraciones, servicios, intereses) están registrados.
- [ ] Desvíos contra presupuesto explicados línea por línea (`finanzas.py --estados`): causa, si es permanente o
      temporal, y qué se hace.
- [ ] Indicadores revisados: caja y meses de caja, DSO, DPO, liquidez, endeudamiento.
- [ ] Forecast actualizado (`finanzas.py --forecast`) si el desvío cambia el año.

## Cerrar
- [ ] Informe financiero mensual emitido (`generar-reporte`) y revisado por `revisor-independiente`.
- [ ] Indicadores registrados (`finanzas.py --registrar`).
- [ ] `finanzas.py --cerrar AAAA-MM --quien "<nombre>"`.

## Si llega algo tarde
`finanzas.py --reabrir AAAA-MM --quien "<nombre>" --motivo "<qué llegó>"`, corregir, repetir «Importar y cuadrar» y
cerrar de nuevo. La reapertura queda en `cierres.csv`.
