---
name: riesgos-issues
description: Gestiona el registro de riesgos y el de problemas (issues) de un proyecto — registrar, evaluar, actualizar, revisar, escalar, convertir un riesgo materializado en problema y cerrar. Úsala siempre que el usuario mencione un riesgo, amenaza, preocupación, problema, bloqueo, incidente, contingencia o pida revisar la matriz de riesgos, aunque lo haga de pasada dentro de otro tema.
---

# Riesgos y problemas

Archivos: `riesgos/riesgos.csv` y `riesgos/issues.csv`. Un **riesgo** es algo que podría ocurrir; un
**problema (issue)** es algo que ya ocurrió y requiere acción.

## Evaluación de riesgos
- Probabilidad e impacto de 1 a 5. Severidad = probabilidad × impacto.
- Nivel: 1–6 bajo · 8–12 medio · 15–25 alto.
- Estrategia: evitar · mitigar · transferir · aceptar.
- Todo riesgo alto necesita plan de acción, responsable y fecha de revisión.
- Fecha de revisión por defecto: hoy + `umbrales.dias_revision_riesgos`.

## Operaciones
1. **Registrar**: redacta el riesgo como "Si <causa>, entonces <efecto> sobre <objetivo>". Propón
   probabilidad, impacto y estrategia con una justificación de una línea; el usuario confirma. Id correlativo R-001…
2. **Actualizar**: cambia solo los campos indicados y agrega en `comentario`/`plan_accion` la fecha del cambio.
3. **Revisar** (periódico o a pedido): lista riesgos con revisión vencida, altos sin plan, sin responsable,
   y propone cambios de evaluación según lo que se sabe hoy (notas de seguimiento, minutas).
4. **Materializar**: si un riesgo ocurrió, crea el issue (I-001…) con `riesgo_origen` y cambia el riesgo a "materializado".
5. **Cerrar**: estado "cerrado" con la razón en el comentario. No borres filas.
6. **Resumen**: tabla de riesgos abiertos ordenada por severidad, y problemas abiertos por fecha compromiso.

## Reglas
- Muestra siempre los cambios propuestos antes de escribir en el CSV.
- Si un problema afecta plazo, costo o alcance de forma relevante, sugiere evaluar un cambio con `control-cambios`.
