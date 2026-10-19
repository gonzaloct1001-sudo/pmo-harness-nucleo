---
tipo: estado-entrega
nombre: Estado de ingeniería y entrega
formato: docx
modo: generar
plantilla: ""
cadencia: mensual
periodo_archivo: mes
destinatarios: []
fuentes: [metricas/mediciones.csv, ingenieria/, agil/sprints.csv, riesgos/riesgos.csv]
---

# Secciones
1. **Resumen** — estado de la entrega en 5 líneas para la jefatura (sin jerga).
2. **Métricas DORA** — frecuencia de despliegue, tiempo de entrega, tasa de falla, tiempo de recuperación, con tendencia.
3. **Previsibilidad** — cumplimiento de compromisos de los últimos sprints y velocidad.
4. **Calidad** — bugs abiertos, incidentes y postmortems del período con sus acciones.
5. **Deuda técnica** — deuda de prioridad alta y plan para abordarla.
6. **Trazabilidad** — requisitos sin prueba o sin historia.
7. **Decisiones de arquitectura** del período (ADR).
8. **Riesgos** y **próximos hitos**.
