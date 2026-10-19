---
name: control-cambios
description: Gestiona solicitudes de cambio de un proyecto (alcance, plazo, costo, recursos, calidad) desde su registro hasta su formalización, con análisis de impacto sobre cronograma, línea base contractual, presupuesto y riesgos. Úsala cuando el usuario mencione un cambio, requerimiento adicional, ampliación, extensión de plazo, trabajo extra, "el cliente pidió…", reprogramación mayor o pregunte por el estado de los cambios.
---

# Control de cambios

Registro: `contractual/cambios/registro-cambios.csv`. Detalle: `contractual/cambios/solicitudes/CC-xxx/`.

## Estados
registrada → en_analisis → presentada → aprobada | rechazada → formalizada (enmienda o acta) → implementada

## Abrir una solicitud
1. Id correlativo CC-001…
2. Crea `solicitudes/CC-xxx/solicitud.md` desde `contractual/_plantillas/solicitud-cambio.md` con la descripción,
   el solicitante y la razón.
3. Agrega la fila al registro con estado "registrada".

## Analizar impacto
1. **Plazo**: identifica tareas afectadas en el cronograma y sigue sus sucesoras (columna predecesoras) para
   estimar el efecto en hitos y en la fecha de término. Compáralo con `linea_base.fecha_termino_vigente`.
2. **Costo**: estima o pide el costo; compáralo con `linea_base.monto_vigente`. Distingue montos confirmados de estimados.
3. **Alcance**: qué entra o sale respecto de `contexto/alcance.md` y la línea base.
4. **Riesgos**: riesgos nuevos o que cambian de severidad.
5. **Otros subproyectos**: dependencias afectadas.
6. Plantea al menos una alternativa (incluida "no hacer el cambio") y una recomendación.
7. Estado → "en_analisis" o "presentada" según indique el usuario.

## Resolver
- **Aprobada**: registra quién y cuándo. Propón, y aplica tras confirmar: ajustes al cronograma
  (`actualizar-gantt`), riesgos (`riesgos-issues`). La línea base contractual **solo** cambia cuando el cambio
  se formaliza con un documento (`registrar-documento`); hasta entonces, anótalo como "aprobado sin formalizar".
- **Rechazada**: registra motivo y fecha. Si el cliente insiste en ejecutar igual, adviértelo como riesgo.

## Consultas
"¿Cómo van los cambios?" → tabla del registro con estado y días desde la solicitud, destacando los
aprobados sin formalizar y los que llevan más de 30 días sin resolverse.
