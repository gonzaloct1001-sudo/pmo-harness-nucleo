# Arquetipo: Cartera de ítems con métricas

## Cuándo usarlo
Cuando el trabajo consiste en **muchos ítems similares**, cada uno con su ciclo de vida (etapas) y sus
métricas, que se evalúan, comparan, promueven o descartan con reglas:
- granja de bots de trading (cada bot: idea → backtest → paper → real → retirado);
- portafolio de acciones (universo → preselección → análisis → en cartera → vendida);
- evaluación de postulaciones a un fondo (recibida → admisible → evaluada → seleccionada / rechazada);
- cartera de proveedores, de clientes, de iniciativas o de proyectos (portafolio de proyectos).

## Qué agrega a la base
- `items/items.csv` — registro de ítems: id, nombre, etapa, fecha de etapa, responsable, categoría, etiquetas.
  Se pueden agregar columnas propias del dominio al final.
- `items/etapas.yaml` — etapas en orden y requisitos para estar en cada una (métricas o archivos).
- `items/fichas/<id>.md` — ficha por ítem: tesis, riesgos, condiciones de salida, fecha de revisión, historial.
- Reporte por defecto: `revision-periodica`.

## Cómo encaja con el contrato común
- Métricas por ítem: `nivel: item`, la entidad en `mediciones.csv` es el id del ítem.
- Métricas de la cartera completa: `nivel: proyecto`, entidad `PROYECTO`.
- Políticas y límites (ej.: "ningún ítem puede pesar más de 20%"): `reglas` en `metricas.yaml`.
- Criterios de avance entre etapas: `requisitos` en `etapas.yaml`.
- Cálculos propios del dominio (rentabilidad, drawdown, puntajes ponderados): script en `scripts/` que
  escribe en `mediciones.csv`.

## Skills que lo usan especialmente
`gestionar-items`, `metricas`, `generar-reporte`, `consistencia`, `riesgos-issues`.

## Preguntas de la mini entrevista
1. ¿Qué es un ítem en este proyecto y cuántos esperas manejar?
2. ¿Por qué etapas pasa un ítem, y qué se necesita para avanzar de una a otra?
3. ¿Qué métricas importan para cada ítem y para el conjunto? ¿De dónde salen los datos y cada cuánto?
4. ¿Qué límites o políticas deben cumplirse siempre?
5. ¿Cada cuánto se revisa la cartera y quién decide?

## Métricas sugeridas por dominio (el generador propone, el usuario ajusta)
- **Bots de trading:** retorno neto, drawdown máximo, profit factor, ratio de Sharpe, % operaciones
  ganadoras, n° de operaciones, exposición, correlación entre bots; reglas de promoción (ej.: n° mínimo de
  operaciones en paper antes de pasar a real) y de retiro (drawdown sobre umbral).
- **Acciones:** peso en cartera, rentabilidad, volatilidad, drawdown, métricas fundamentales (ROE, P/U,
  deuda/EBITDA, dividendos); cartera: rentabilidad vs índice de referencia, concentración por acción y
  sector, Sharpe. Es una herramienta de organización y análisis; las decisiones de inversión son del usuario.
- **Postulaciones a fondos:** puntaje por criterio de la pauta, puntaje ponderado, cumplimiento de
  admisibilidad, monto solicitado; cartera: monto total vs presupuesto del fondo.
- **Proveedores:** cumplimiento de plazos, calidad, precio relativo, incidentes.
