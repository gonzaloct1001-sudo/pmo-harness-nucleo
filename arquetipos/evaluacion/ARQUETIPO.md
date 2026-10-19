# Arquetipo: Evaluación de propuestas y postulaciones

## Cuándo usarlo
Cuando el trabajo es **evaluar muchas propuestas con una pauta**: postulaciones a un fondo, ofertas de una
licitación, propuestas de proveedores, proyectos de un concurso interno, candidatos de un programa.
Es una cartera especializada: cada propuesta es un ítem, los criterios de la pauta son métricas y la
admisibilidad son requisitos de etapa. **Úsalo solo** (no combinarlo con `cartera` en el mismo proyecto).

## Qué agrega a la base
- `evaluacion/pauta.yaml` — convocatoria, escala, admisibilidad, criterios con ponderación y descriptores por nivel, umbrales, desempate.
- `evaluacion/admisibilidad.csv`, `evaluacion/puntajes.csv` — registros por requisito y por criterio (admite varios evaluadores).
- `evaluacion/evaluaciones/<id>.md` — evaluación fundamentada de cada propuesta.
- `postulaciones/<id>/` — documentos de cada propuesta (no se suben a Git).
- Etapas: recibida → admisibilidad → en evaluación → evaluada → seleccionada / lista de espera / no seleccionada.
- Reporte: `acta-evaluacion`.
- Cálculo: `python herramientas/puntaje_pauta.py <proyecto>` (puntaje ponderado, umbrales, ranking,
  presupuesto, discrepancias entre evaluadores).

## Skills
`definir-pauta` (bases → pauta) y `evaluar-propuestas` (admisibilidad, evaluación con el subagente
`evaluador-propuestas`, ranking y comparación).

## Principios
- El asistente de IA **propone** puntajes con evidencia; el evaluador humano revisa, ajusta y firma.
- Evaluar cada propuesta en contexto aislado (subagente) para evitar sesgos de orden y comparación.
- Confidencialidad: revisar si las bases o el compromiso del evaluador permiten procesar las postulaciones con IA.
- Declarar y registrar conflictos de interés antes de evaluar.

## Preguntas de la mini entrevista
1. ¿Qué convocatoria o proceso es y dónde están las bases?
2. ¿Cuántas propuestas se esperan y cuál es el plazo de evaluación?
3. ¿Evalúa una persona o un comité? ¿Hay que consolidar puntajes de varios evaluadores?
4. ¿Hay presupuesto total a distribuir y montos máximos?
5. ¿Qué formato de acta o informe exige el mandante?
