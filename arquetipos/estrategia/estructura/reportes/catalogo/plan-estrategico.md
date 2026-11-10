---
tipo: plan-estrategico
nombre: Plan estratégico
formato: docx
modo: generar
plantilla: ""
cadencia: anual
periodo_archivo: anio
destinatarios: []
fuentes:
  - estrategia/
  - finanzas/proyeccion.yaml
  - metricas/mediciones.csv
claves: [plan estratégico, estrategia, 3YP, 5YP, plan de negocio, objetivos, metas, iniciativas, directorio]
---

# Propósito
El documento que el directorio o la gerencia aprueba: de dónde partimos, adónde vamos en 3 o 5 años, con qué
objetivos, metas e iniciativas, cuánto cuesta y cómo se va a controlar. También sale como presentación.

# Secciones
1. **Resumen ejecutivo** — la ambición, las apuestas, las tres cifras del plan financiero y lo que se pide aprobar.
2. **Diagnóstico** — externo e interno (`estrategia/diagnostico.md`), con fuente en cada afirmación; síntesis.
3. **Lineamientos** — propósito, ambición, apuestas, lo que no haremos (`estrategia/lineamientos.md`).
4. **Objetivos y metas por año** — tabla por objetivo: indicador, línea base y meta de cada año del horizonte
   (`objetivos.csv`, `metas.csv`).
5. **Iniciativas y roadmap** — por objetivo: iniciativa, responsable, fechas, inversión, impacto; Gantt por año
   (`estrategia.py --roadmap`).
6. **Plan financiero a N años** — resultados, balance y caja proyectados (`finanzas.py --proyectar`) con los
   supuestos rastreados a iniciativas; sin finanzas, tabla simple marcada «estimación».
7. **Riesgos del plan** — los que podrían impedir las apuestas y su mitigación (`riesgos/`).
8. **Gobierno y revisión** — quién decide, cadencia de revisión, qué pasa con un desvío.
9. **Anexo** — supuestos, fuentes, afirmaciones sin verificar.

# Validaciones antes de entregar
- `estrategia.py --revisar` sin errores; cada afirmación del diagnóstico con fuente o marcada «sin verificar».
- Cada supuesto del plan financiero rastreable a una iniciativa o a una tendencia declarada; sin `[PENDIENTE`.
- Red team (director exigente, competidor, cliente, CFO) y `revisor-independiente` antes del directorio;
  `verificar_autoria.py` en OK.
