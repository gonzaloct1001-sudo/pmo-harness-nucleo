---
name: ayuda
description: Muestra qué puede hacer el harness en el proyecto activo — tipo de proyecto, dónde está cada cosa, rutina recomendada, reportes configurados, las skills disponibles con frases de ejemplo en lenguaje natural y los controles automáticos. Úsala cuando el usuario pregunte "¿qué puedo hacer?", "¿qué comandos tengo?", "ayuda", "¿cómo se usa esto?", "muéstrame la guía", o parezca no saber cómo pedir algo.
---

# Ayuda

1. Determina el proyecto activo (reglas de `AGENTS.md`). Si no hay proyectos o el usuario pregunta en
   general: `python herramientas/guia_proyecto.py --general`.
2. Con proyecto: `python herramientas/guia_proyecto.py proyectos/<slug>` (actualiza `proyectos/<slug>/GUIA.md`).
3. Responde con un resumen breve, no con la guía completa:
   - qué tipo de proyecto es, en una línea;
   - las 5 o 6 cosas más útiles para su situación actual, cada una con una frase de ejemplo;
   - dónde leer la guía completa (`GUIA.md`, enlace clicable).
4. Aclara que no hace falta usar el nombre exacto de la skill: basta con describir lo que se necesita.
5. Si el usuario pregunta por algo que el harness no hace, dilo y sugiere la alternativa más cercana
   (por ejemplo, crear un reporte propio con `nuevo-tipo-reporte` o una métrica con `metricas`).

Si cambian las skills del harness, actualiza `catalogo.yaml` (junto a este archivo) para que la guía siga completa.
