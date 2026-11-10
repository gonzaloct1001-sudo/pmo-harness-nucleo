# Levantar riesgos de forma sistemática

Referencia de la skill `riesgos`. Se aplica al iniciar un proyecto, antes de un hito o comité, o cuando el usuario pide «qué riesgos se nos escapan»: no registra los ya conocidos, los busca con método y propone candidatos para confirmar en bloque.


Diferencia con `riesgos`: esa skill registra y gestiona riesgos conocidos; esta **busca** los que
nadie ha nombrado todavía. Al final, los riesgos aprobados se registran con los criterios de `riesgos`.

## 1. Fuentes a revisar (según existan)
- Contexto y alcance: `contexto/alcance.md`, `contexto/diseno-del-proyecto.md`.
- Supuestos: los explícitos (`estudio/supuestos.csv`, supuestos de propuestas) y los implícitos (lo que el plan
  da por hecho sin decirlo).
- Dependencias: predecesoras del cronograma, dependencias entre subproyectos, proveedores únicos.
- Contrato: multas, garantías, plazos de aviso, obligaciones del cliente (`contractual/`).
- Métricas y reglas: métricas en amarillo o con tendencia negativa, reglas cerca del límite.
- Historial: issues ya ocurridos (suelen repetirse), minutas, correos recientes.
- Registro actual: `riesgos/riesgos.csv` (para no duplicar).

## 2. Técnicas (usa al menos dos)
- **Checklist por categorías**: recorre `references/categorias-riesgo.md` (general + las del arquetipo del proyecto).
- **Premortem**: "Es la fecha de término y el proyecto fracasó. ¿Qué pasó?" Genera 5 a 10 causas plausibles.
- **Análisis de supuestos**: para cada supuesto crítico, ¿qué pasa si es falso? ¿qué tan probable es?
- **Puntos únicos de falla**: personas, proveedores, sistemas o permisos de los que depende todo.

## 3. Propuesta (un solo mensaje)
Tabla de riesgos candidatos (máximo 15, ordenados por severidad): enunciado "Si <causa>, entonces <efecto>
sobre <objetivo>", categoría, probabilidad e impacto (1–5) con justificación breve, fuente o técnica que
lo originó, responsable sugerido y respuesta sugerida. Indica cuáles ya estaban registrados y si alguno
existente debería reevaluarse.

## 4. Registrar
Tras la confirmación (el usuario puede aprobar todo, algunos o ajustar), registra en `riesgos/riesgos.csv`
con los criterios de `riesgos`. Si se hizo como taller o antes de un comité, guarda el análisis
en `riesgos/levantamiento_AAAA-MM-DD.md`.
