---
name: evaluar-propuestas
description: Evalúa propuestas o postulaciones contra la pauta del proyecto — registro, revisión de admisibilidad, evaluación fundamentada de cada una en contexto aislado (subagente evaluador-propuestas), consolidación de puntajes de uno o varios evaluadores, ranking, comparación entre propuestas y ajuste al presupuesto. Úsala cuando el usuario reciba postulaciones, ofertas o propuestas para evaluar, pida revisarlas, puntuarlas, compararlas, rankearlas, preparar comentarios para los postulantes o el acta de evaluación.
---

# Evaluar propuestas

Requiere `evaluacion/pauta.yaml` completa (si no, usa `definir-pauta` primero).
Herramienta de consolidación: `python herramientas/puntaje_pauta.py <proyecto> [--fecha AAAA-MM-DD]`.

## 0. Antes de empezar
- Recuerda al usuario (una vez) verificar que las bases o su compromiso como evaluador permiten procesar
  las postulaciones con herramientas de IA, y registrar cualquier conflicto de interés.

## 1. Registrar
1. Cada propuesta en `postulaciones/<id>/` (ids correlativos: P-001, P-002…).
2. Fila en `items/items.csv` con nombre, postulante, monto solicitado, categoría (línea o región si aplica), etapa `recibida`.
3. Texto: `python herramientas/extraer_entrada.py <proyecto> --origen postulaciones`.

## 2. Admisibilidad
Para cada propuesta y cada requisito de la pauta, registra en `evaluacion/admisibilidad.csv`:
cumple `si` / `no` / `na`, evidencia (documento y página) y evaluador. Un requisito excluyente incumplido deja
la propuesta como no admisible; uno subsanable queda como pendiente de subsanación. Mueve las etapas
(`admisibilidad` → `en_evaluacion` o `retirado` con el motivo) con los criterios de `gestionar-items`.

## 3. Evaluación (una propuesta por subagente)
Para cada propuesta admisible, invoca al subagente **`evaluador-propuestas`** con: ruta del proyecto, id,
ruta de sus textos en `postulaciones/_procesado/texto/` y la pauta. Pueden ir en paralelo (en lotes de 3 a 5).
Cada uno escribe `evaluacion/evaluaciones/<id>.md` con estado `propuesta`.
Luego transcribe los puntajes a `evaluacion/puntajes.csv` con evaluador `IA (propuesta)`.

## 4. Consolidar y calibrar
1. Ejecuta `puntaje_pauta.py`.
2. **Calibración**: revisa si hay deriva (propuestas parecidas con puntajes muy distintos, o un criterio
   donde todas obtienen lo mismo). Si detectas inconsistencias, relee las evaluaciones afectadas y corrige
   con justificación.
3. Opcional para procesos importantes: pide al subagente `revisor-independiente` que revise el ranking y las
   3 evaluaciones más cercanas al corte.

## 5. Revisión humana (obligatoria)
Presenta al usuario el ranking y, por propuesta, los puntajes con su evidencia. El evaluador ajusta: registra
sus puntajes en `puntajes.csv` con su nombre como evaluador (el script promedia por evaluador y alerta
discrepancias) o reemplaza los de `IA (propuesta)` si así lo decide. Cambia el `estado` de cada evaluación
a `revisada` o `final`. Sin esta revisión, no hay acta final.

## 6. Comparar y cerrar
- **Comparación**: tabla de propuestas por criterio, fortalezas distintivas de cada una y qué separa a las que
  quedan justo sobre y bajo el corte o el presupuesto.
- **Selección**: dentro del presupuesto, lista de espera, no seleccionadas con su causa (etapas correspondientes).
- **Acta**: `generar-reporte` con `acta-evaluacion`. **Comentarios a postulantes**: desde la sección de mejora de
  cada evaluación, en tono constructivo.
