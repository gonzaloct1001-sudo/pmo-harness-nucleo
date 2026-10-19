# Diseño del proyecto — generado por `nuevo-proyecto` (ejemplo)

## Descripción del usuario
"Quiero armar un proyecto de búsqueda y confección de un portafolio de inversión de acciones, con
seguimiento de cada acción y de la cartera contra un índice."

## Arquetipo elegido
**Cartera de ítems con métricas** (cada acción es un ítem). No se usó *ejecución por plan* porque no hay
tareas con fechas ni contrato; tampoco *estudio*, porque el análisis de cada acción vive en su ficha.

## Diseño propuesto y confirmado
| Elemento | Decisión | Dónde quedó |
|---|---|---|
| Ítem | Una acción (id = ticker) | `items/items.csv` |
| Etapas | universo → preselección → análisis → en cartera → en revisión → retirada | `items/etapas.yaml` |
| Filtros de avance | ROE ≥ 12% y deuda/EBITDA ≤ 3,5x para preselección; ficha con tesis para análisis y cartera | `items/etapas.yaml` |
| Métricas por acción | peso, rentabilidad, volatilidad, caída máxima, ROE, deuda/EBITDA, P/U, dividendos | `metricas/metricas.yaml` |
| Métricas de cartera | valor, n° posiciones, retorno vs índice, volatilidad, caída máxima, Sharpe, concentración | `metricas/metricas.yaml` |
| Política (reglas) | máx. 20% por acción, 35% por sector, mín. 6 posiciones, deuda/EBITDA ≤ 3,5x (salvo bancos) | `metricas/metricas.yaml` → `reglas` |
| Datos | transacciones, precios mensuales (con índice), fundamentos trimestrales, en CSV | `datos/` |
| Cálculos propios | rentabilidad ponderada por tiempo, volatilidad, drawdown, Sharpe, pesos | `scripts/calcular_cartera.py` |
| Reporte | Revisión mensual del portafolio | `reportes/catalogo/revision-mensual.md` |
| Riesgos iniciales | concentración, rezago frente al índice, sensibilidad a tasas | `riesgos/riesgos.csv` |

## Preguntas que hizo el generador (y respuestas)
1. ¿Índice de referencia? → IDX.
2. ¿Límites de concentración? → 20% por acción, 35% por sector.
3. ¿De dónde salen los precios? → exportación mensual del broker a CSV.
4. ¿Cada cuánto se revisa? → mensual, a fin de mes.

## Advertencia incorporada
El proyecto organiza datos y análisis; las decisiones de inversión son del titular. Los reportes plantean
preguntas, no recomendaciones.
