# Arquetipo: Obra y proyectos de ingeniería en terreno (complemento de ejecución)

## Cuándo usarlo
Junto con `ejecucion` (`--arquetipos ejecucion,obra`) en construcción, montaje, obras civiles, instalaciones
industriales o cualquier proyecto con trabajo en terreno, inspecciones y estados de pago.

## Qué agrega
- `obra/rfi.csv` — consultas técnicas con plazo de respuesta e impacto.
- `obra/no-conformidades.csv` — hallazgos de calidad con severidad, acción correctiva y cierre.
- `obra/inspecciones.csv` — inspecciones programadas y su resultado.
- `obra/estados-pago.csv` — estados de pago con avance declarado, aprobación, pago y retenciones.
- `obra/libro-de-obra.md` — registro diario resumido.
- Reporte: `informe-obra`.
- `validar_proyecto.py` revisa RFI vencidas, no conformidades abiertas, inspecciones atrasadas y que el avance
  declarado en los estados de pago sea coherente con el cronograma; `evm_cpm.py` da valor ganado y ruta crítica.

## Skill
`registros-obra`, más `actualizar-gantt`, `control-cambios`, `registrar-documento`.

## Preguntas de la mini entrevista
1. ¿Tipo de obra y etapas principales (partidas)?
2. ¿Contrato a suma alzada, serie de precios unitarios u otro? ¿Cada cuánto se presentan estados de pago?
3. ¿Quién es la inspección técnica (ITO) y el plazo de respuesta a consultas?
4. ¿Hay presupuesto por partida para valor ganado (costo planificado y real)?
5. Normativa, permisos y recepciones aplicables: confirmarlos con los profesionales responsables.
