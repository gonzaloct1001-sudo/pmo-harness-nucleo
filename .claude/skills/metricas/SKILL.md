---
name: metricas
description: Gestiona las métricas y reglas de un proyecto — agregar o modificar métricas (con definición, fórmula, fuente, frecuencia y umbrales), registrar mediciones a mano o importarlas desde CSV/Excel, ejecutar los cálculos propios del proyecto, evaluar semáforos y reglas, y explicar el resultado. Úsala cuando el usuario quiera agregar una métrica ("quiero medir también…"), cambiar un umbral o una política, cargar datos o resultados, actualizar números, preguntar cómo va un indicador o ver qué incumple las reglas.
---

# Métricas y reglas

Contrato común (igual para todo arquetipo):
- Definiciones y reglas: `metricas/metricas.yaml` (propias del proyecto; ver comentarios del archivo) y
  `metricas/metricas-<arquetipo>.yaml` (aportadas por arquetipos: se pueden ajustar, pero las nuevas van en `metricas.yaml`).
- Valores: `metricas/mediciones.csv` → `fecha, entidad, metrica, valor, fuente, comentario`
  (entidad = id del ítem, o `PROYECTO` para métricas del conjunto; porcentajes como fracción).
- Evaluación: `python herramientas/evaluar_metricas.py <ruta-proyecto> [--hoy AAAA-MM-DD]`.

## Agregar o modificar una métrica
1. Precisa con el usuario, proponiendo valores: nombre, nivel (item/proyecto), unidad, dirección
   (mayor_mejor / menor_mejor / informativa), frecuencia, fuente y definición exacta (fórmula).
2. Propón umbrales amarillo/rojo razonables para el dominio, marcados como sugerencia.
3. Define cómo se obtendrá el valor: carga manual, importación de un archivo, o cálculo en un script del
   proyecto (`scripts/`). Si es cálculo, agrégalo al script existente o crea uno nuevo, y pruébalo.
4. Escribe el bloque en `metricas.yaml`. Si la métrica debe aparecer en la tabla de ítems, `clave: true`.
5. Si hay datos, registra valores y ejecuta la evaluación para mostrar el resultado.

## Reglas y políticas
Una regla = métrica + operador + valor + alcance (`aplica_a`) + severidad. Úsalas para límites y políticas
("ningún bot con drawdown sobre 20% en real", "máximo 20% por acción"). Si una regla no aplica a ciertos
ítems, usa `excluir` y deja el porqué en un comentario.

## Registrar o importar mediciones
- **Manual:** agrega filas a `mediciones.csv` (una por entidad y métrica) con la fuente ("manual", "informe X").
- **Importar:** si el usuario trae un CSV o Excel (exportación de una plataforma, un backtest, un broker),
  mapea sus columnas a entidad/métrica/valor, muestra 5 filas convertidas para validar y luego importa.
  Si el formato se repetirá, crea un script de importación en `scripts/` para la próxima vez.
- **Calcular:** ejecuta los scripts del proyecto según la rutina de su `CLAUDE.md`, y los de su arquetipo
  (`evm_cpm.py`, `metricas_agil.py`, `puntaje_pauta.py`).
- Nunca borres mediciones históricas; si hay un error, corrige la fila y anótalo en `comentario`.

## Evaluar y explicar
Ejecuta `evaluar_metricas.py` y explica en lenguaje simple: qué está en rojo o amarillo, qué reglas se
incumplen, qué datos están desactualizados y qué ítems pueden avanzar de etapa. Cuando una cifra sorprenda,
revisa su cálculo antes de concluir. Si el proyecto es de inversiones u otra decisión sensible, presenta
hallazgos y preguntas, no recomendaciones.
