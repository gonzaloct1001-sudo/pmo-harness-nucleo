---
name: consistencia
description: Revisa la consistencia interna de un proyecto — cronograma vs línea base contractual, reportes emitidos vs sus fuentes, riesgos sin plan, acuerdos e issues vencidos, cambios aprobados no reflejados, datos de inducción pendientes. Úsala cuando el usuario pida revisar, auditar, validar o "chequear que todo cuadre", antes de una reunión de comité o de enviar un reporte importante, o cuando pregunte qué está pendiente o atrasado.
---

# Revisión de consistencia

## 1. Chequeo automático
```
python herramientas/validar_proyecto.py proyectos/<slug> [--hoy AAAA-MM-DD]
python herramientas/evaluar_metricas.py proyectos/<slug> [--hoy AAAA-MM-DD]
```
El primero cubre cronograma, riesgos, acuerdos, cambios y registros de obra; el segundo, métricas, reglas,
etapas de ítems y fichas. Según el arquetipo, ejecuta antes los cálculos que alimentan las métricas:
`evm_cpm.py` (ejecución), `metricas_agil.py` (ágil), `puntaje_pauta.py` (evaluación) o los scripts propios del proyecto.
Para una mirada externa en revisiones importantes, usa el subagente `revisor-independiente`.
Cubre: pendientes de inducción, fechas inválidas, dependencias, atrasos, hitos vencidos, tareas fuera del
plazo contractual, riesgos altos sin plan, revisiones vencidas, issues y acuerdos vencidos, cambios sin resolver.

## 2. Chequeo con criterio (lo que el script no ve)
Revisa, leyendo solo lo necesario:
1. **Reportes emitidos vs fuentes**: toma el último emitido de cada tipo del catálogo y compara sus cifras
   clave (avance por subproyecto, fechas de hitos, montos) con el cálculo actual y con los registros.
   Para Excel usa `herramientas/inspeccionar_xlsx.py` o lee las celdas del mapeo.
2. **Línea base**: `linea-base-vigente.md` vs `proyecto.yaml → linea_base` vs la última enmienda registrada.
3. **Cambios aprobados**: que su efecto esté en el cronograma y, si están formalizados, en la línea base.
4. **Trabajo sin respaldo**: tareas del cronograma o menciones en seguimiento/minutas que no aparecen en el
   alcance ni en un cambio aprobado.
5. **Stakeholders**: destinatarios de reportes que no están en `stakeholders.csv`.
6. **Notas de seguimiento**: semanas sin nota en el último mes.

## 3. Informe
Clasifica cada hallazgo como **Crítico** (afecta lo que se informa o compromete contractualmente),
**Advertencia** o **Información**. Para cada uno: qué está mal, dónde (archivo y fila/celda), y la corrección propuesta.
Guarda el informe en `reportes/emitidos/AAAA-MM-DD/consistencia.md` si el usuario lo pide.

No corrijas nada automáticamente: pregunta qué hallazgos quiere resolver y usa la skill correspondiente.
