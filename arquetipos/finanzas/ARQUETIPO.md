# Arquetipo: Finanzas (gestión financiera y control de gestión)

## Cuándo usarlo
Cuando el trabajo es **gestionar el área de finanzas de una empresa**, como gerente de finanzas, controller o
consultor a cargo: presupuesto anual, cierre mensual, estados financieros de gestión (resultados, balance, caja),
real contra presupuesto contra forecast, indicadores, proyección a varios años y reporte al directorio. Sirve para
cualquier rubro y país: lo propio del país (impuestos, calendario tributario, norma contable) va en
`biblioteca/finanzas/paises/`, y el plan de cuentas y las líneas del reporte son de cada empresa.

Señales para reconocerlo: «llevar las finanzas», «presupuesto anual», «cierre mensual», «P&L», «estado de
resultados», «flujo de caja de la empresa», «control de gestión», «forecast», «informe al directorio», «controller»,
un balance de comprobación o libro mayor en `_entrada/`.

No es lo mismo que `estudio` (evaluación económica de un proyecto o inversión: VAN, TIR) ni que el presupuesto de
una `postulacion`. Se combina con `investigacion` cuando un supuesto depende de hechos de afuera (benchmarks, precios
de terceros, normativa) y con `estudio` cuando hay que evaluar una inversión.

## Cómo funciona (en simple)
1. **Arranque:** el plan de cuentas de la empresa se mapea a las líneas del reporte (`finanzas/lineas.yaml`); se
   carga el histórico desde la contabilidad.
2. **Presupuesto anual:** supuestos con fuente → montos por línea y mes → versión aprobada por quien corresponda.
3. **Cierre mensual:** se importa el balance de comprobación o el libro mayor del mes, se revisan las cuentas sin
   mapear, se cuadra, se explican los desvíos, se calculan los indicadores, se emite el informe y se **cierra** el
   período. Un período cerrado se puede **reabrir** con motivo y quién (siempre llega algo tarde) y se vuelve a cerrar.
4. **Forecast:** lo real hasta la fecha más el resto del año (presupuesto o tendencia), con versión.
5. **Proyección:** resultados, balance y caja integrados a varios años desde supuestos explícitos; el balance cuadra
   por construcción.
6. **Reporte al directorio:** con el formato de la empresa (`adoptar-formatos`) o el del harness.

## Qué agrega a la base
- `finanzas/plan-de-cuentas.csv` (cuenta → tipo → línea), `finanzas/lineas.yaml` (líneas y subtotales de los tres
  estados; se puede adaptar), `finanzas/real.csv` (movimientos por cuenta y período, importados), `presupuesto.csv`,
  `forecast.csv`, `supuestos.csv`, `escenarios.csv`, `cierres.csv` (estado de cada período, con huella), `cierre/checklist.md`
  y `proyeccion.yaml`.
- `metricas/metricas-finanzas.yaml`: margen bruto, EBITDA, resultado, caja y meses de caja, DSO, DPO, DIO, liquidez,
  endeudamiento, desvíos contra presupuesto, cuentas sin mapear, períodos sin cerrar, con semáforos.
- Reportes: `informe-financiero-mensual`, `presupuesto-anual`, `reporte-directorio`.
- `_entrada/10-contabilidad/`: donde se dejan las exportaciones de la contabilidad (no se suben a Git; lo que se sube
  es `real.csv`, ya mapeado).
- Bloque `finanzas` en `proyecto.yaml`: moneda, inicio del año fiscal, sistema contable, versión vigente del
  presupuesto, quién aprueba.

## Herramientas
- `python herramientas/finanzas.py <proyecto>`: dónde va (último período, cierres, cuentas sin mapear, indicadores,
  alertas) y el siguiente paso.
- `--importar <archivo> --periodo AAAA-MM [--vista-previa] [--mapa mapa.yaml]`: balance de comprobación o libro
  mayor (Excel o CSV) → `real.csv`; detecta las columnas; lista las cuentas que no están en el plan.
- `--estados [--periodo AAAA-MM] [--excel salida.xlsx]`: resultados (mes y acumulado) real vs presupuesto vs
  forecast, balance, flujo de caja e indicadores; el Excel lleva fórmulas.
- `--cerrar AAAA-MM --quien N` / `--reabrir AAAA-MM --quien N --motivo M`: cierre y reapertura con bitácora.
- `--forecast [--metodo presupuesto|tendencia] --version V`: forecast del año.
- `--proyectar [--excel salida.xlsx]`: proyección integrada a varios años desde `proyeccion.yaml`.
- `--revisar`: consistencia (plan, líneas, períodos, cuadres, cierres intactos); `--registrar`: indicadores a
  `metricas/mediciones.csv` para el status.

## Skills y roles
`gestion-financiera` (orquesta: arranque, presupuesto, cierre, desvíos, forecast, proyección, directorio) · subagente
`analista-financiero` (calcula y explica; no decide) · `revisor-independiente` antes del directorio · `adoptar-formatos`
para los formatos propios · `investigar` para hechos de afuera · `evaluacion-economica` para inversiones.

## Principios
- **El harness no reemplaza la contabilidad ni al contador:** consume lo que ellos producen (balance de comprobación,
  libro mayor) y organiza la gestión. Asientos, libros, impuestos y tesorería operativa quedan en los sistemas y en el
  contador; las decisiones tributarias y legales, en los profesionales competentes.
- **Nunca se inventa una cifra:** lo que no está en `real.csv` o en un supuesto con fuente es `[PENDIENTE]`.
- **Un período cerrado no cambia sin reabrirlo** (quién y por qué quedan en `cierres.csv`).
- **Cuadres antes que análisis:** si el balance no cuadra o hay cuentas sin mapear, se resuelve eso primero.
- Las exportaciones de la contabilidad no se suben a Git; `real.csv` sí (va al repositorio privado de la empresa).

## Preguntas de la mini entrevista
1. ¿Moneda, inicio del año fiscal y periodicidad (mensual)?
2. ¿Qué sistema contable usan y qué se puede exportar (balance de comprobación, libro mayor, en Excel o CSV)?
3. ¿Hay plan de cuentas? (déjalo en `_entrada/`; si no, se parte del plan base de la biblioteca)
4. ¿Centros de costo o unidades de negocio que haya que separar?
5. ¿Quién aprueba el presupuesto y el cierre, y qué espera ver el directorio cada mes?
