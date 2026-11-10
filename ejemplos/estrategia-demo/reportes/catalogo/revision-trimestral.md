---
tipo: revision-trimestral
nombre: Revisión del plan estratégico
formato: docx
modo: generar
plantilla: ""
cadencia: trimestral
periodo_archivo: trimestre
destinatarios: []
fuentes:
  - estrategia/revisiones.csv
  - estrategia/metas.csv
  - estrategia/iniciativas.csv
  - metricas/mediciones.csv
claves: [revisión, trimestral, plan estratégico, metas, avance, desvíos, decisiones]
---

# Propósito
Comparar las metas del año con lo real a la fecha, ver cómo avanzan las iniciativas y dejar decididas las
correcciones. Es una reunión de decisiones, no un informe de lectura.

# Secciones
1. **Semáforo del plan** — indicadores en verde, amarillo y rojo; cumplimiento global (`estrategia.py --revision`).
2. **Metas contra reales** — por objetivo: meta del año, real a la fecha, desvío, tendencia.
3. **Iniciativas** — en curso, atrasadas, terminadas y por partir; qué las frena.
4. **Desvíos y decisiones** — por cada rojo o amarillo: causa, decisión (mantener, ajustar meta, reasignar,
   descartar), quién y cuándo (`revisiones.csv`).
5. **Ajustes al plan** — cambios de metas, iniciativas o supuestos financieros que salen de la revisión.
6. **Próxima revisión** — fecha y qué debe estar listo.

# Validaciones antes de entregar
- `estrategia.py --revision AAAA-Tn` ejecutado; cada rojo con decisión y responsable en `revisiones.csv`.
- Los reales salen de `metricas/mediciones.csv` o de una fuente nombrada; sin `[PENDIENTE`.
- `verificar_autoria.py` en OK.
