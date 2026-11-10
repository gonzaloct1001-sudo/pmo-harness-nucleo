# Modo cierre mensual

Sigue `finanzas/cierre/checklist.md` (cópialo a `finanzas/cierre/AAAA-MM.md` y márcalo). En resumen:

1. **Importar:** la exportación del mes está en `_entrada/10-contabilidad/`. Primero
   `finanzas.py --importar <archivo> --periodo AAAA-MM --vista-previa`: revisa que la fila de encabezados y las
   columnas detectadas sean las correctas y que cuadre (debe = haber). Si el sistema exporta acumulados del año,
   `--acumulado`. Si las columnas tienen otros nombres, `--mapa mapa.yaml`. Luego importa sin `--vista-previa`.
2. **Mapear:** por cada cuenta sin mapear, pregunta al usuario a qué línea va (propón la más probable por el nombre) y
   agrégala a `plan-de-cuentas.csv`. `--revisar` hasta 0 errores. Si el balance no cuadra con todo mapeado, el problema
   está en la exportación o en los saldos de apertura: no lo «arregles» con asientos; pide la exportación correcta.
3. **Revisar con el analista:** `analista-financiero` corre `--estados --periodo AAAA-MM`, explica cada desvío
   relevante (causa, permanente o temporal, acción propuesta) y los indicadores. Lo que no se pueda explicar con los
   datos se pregunta al usuario, no se supone.
4. **Forecast:** si el mes cambia la lectura del año, `--forecast` (ver `desvios-y-forecast.md`).
5. **Informe:** `generar-reporte` con `informe-financiero-mensual` (o el formato propio adoptado); revisión de
   `revisor-independiente`; `verificar_autoria.py`.
6. **Registrar y cerrar:** `--registrar --periodo AAAA-MM` y luego `--cerrar AAAA-MM --quien "<quien aprueba>"` con el
   sí de quien dice `finanzas.aprueba_cierre`. El cierre guarda la huella de los movimientos. Si no cuadra o hay cuentas
   sin mapear, no cierra; `--forzar` solo si el usuario lo decide sabiendo qué queda mal, y queda anotado.
7. **Si llega algo tarde:** `--reabrir AAAA-MM --quien "<nombre>" --motivo "<qué llegó>"`, reimportar o corregir,
   `--revisar`, `--estados`, y cerrar de nuevo. Si el ajuste cambia meses ya reportados, dilo en el informe siguiente
   («se reabrió agosto por una factura de proveedores recibida tarde: el resultado del año no cambia; el de agosto baja
   en X»).
