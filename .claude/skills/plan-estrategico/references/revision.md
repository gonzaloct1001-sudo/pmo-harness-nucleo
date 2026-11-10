# Revisión periódica del plan

**La revisión es una decisión, no un informe.** Cada desvío termina en una de cuatro decisiones con quién la tomó.

## Antes de la reunión
1. `python herramientas/estrategia.py proyectos/<slug> --revision AAAA-Tn --quien "<nombre>"`: crea las filas del
   período (metas del año de cada objetivo activo) y toma los reales de `metricas/mediciones.csv` cuando el indicador
   es una métrica del proyecto (misma `id`).
2. Completa en `revisiones.csv` los reales que falten, con su fuente en `nota` (finanzas, un sistema, una encuesta).
   Vuelve a ejecutar `--revision`: calcula desvío y semáforo (verde ≥ meta; amarillo hasta −10 %; rojo más allá;
   en indicadores `menor_mejor`, al revés).
3. Iniciativas: estado real de cada una (`iniciativas.csv`), atrasadas y por qué.
4. Borrador del reporte `revision-trimestral` con `reportes`.

## En la reunión
Por cada rojo y amarillo, una decisión en `revisiones.csv` (`decision`, `quien`):
- **mantener** (el desvío es temporal y hay plan para recuperarlo);
- **ajustar meta** (el supuesto cambió; se cambia la meta en `metas.csv` con nota y fecha);
- **reasignar** (recursos de otra iniciativa; se refleja en `iniciativas.csv`);
- **descartar** (objetivo o iniciativa; estado `descartado`/`descartada` con el motivo).
Un rojo sin decisión es error de `--revisar`.

## Después
- `estrategia.py --registrar`: las métricas del plan quedan en `metricas/mediciones.csv` y en el status.
- Si cambiaron metas o iniciativas con impacto financiero, actualiza los supuestos de la proyección y vuelve a
  correr `finanzas.py --proyectar`.
- Traspaso (regla 17) con lo decidido y la fecha de la próxima revisión.
