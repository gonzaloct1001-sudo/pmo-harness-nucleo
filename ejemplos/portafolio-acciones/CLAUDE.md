# Contexto particular — Portafolio de acciones (FICTICIO)

## En una frase
Portafolio personal de acciones locales: selección por etapas, tesis escrita por acción, política de
inversión con límites y revisión mensual contra un índice de referencia (IDX, ficticio).

## Arquetipos y cómo se trabaja
Cartera de ítems: cada acción es un ítem que avanza por etapas
(universo → preselección → análisis → en cartera → en revisión → retirada). Ver `items/etapas.yaml`.
Las métricas se calculan con `scripts/calcular_cartera.py` y se evalúan con `herramientas/evaluar_metricas.py`.

## Política de inversión (resumen; las reglas formales están en metricas/metricas.yaml)
- Máximo 20% de la cartera en una sola acción.
- Máximo 35% en un mismo sector.
- Mínimo 6 posiciones.
- Deuda/EBITDA de las acciones en cartera idealmente bajo 3,5x.
- Toda acción en análisis o en cartera debe tener ficha con tesis y fecha de revisión.

## Reglas particulares
- Esta es una herramienta de organización y análisis. Las decisiones de compra y venta son del titular:
  Claude presenta datos, incumplimientos y preguntas, pero no recomienda comprar ni vender.
- Toda decisión de compra o venta se registra en `seguimiento/decisiones.csv` con su fundamento.
- Montos en pesos chilenos, sin decimales.

## Rutina de actualización de datos (mensual)
1. Agregar transacciones del mes a `datos/transacciones.csv`.
2. Agregar precios de cierre del mes a `datos/precios.csv` (exportados del broker u otra fuente), incluido el índice IDX.
3. Si hay estados financieros nuevos, actualizar `datos/fundamentos.csv`.
4. `python scripts/calcular_cartera.py proyectos/portafolio-acciones --fecha AAAA-MM-DD` (en este ejemplo: `ejemplos/portafolio-acciones`).
5. `python herramientas/evaluar_metricas.py <ruta-proyecto> --hoy AAAA-MM-DD`
6. Generar la revisión mensual con `generar-reporte`.

## Notas de estilo
- Reportes breves, con tablas y sin jerga innecesaria.
