---
tipo: estado-postulacion
nombre: Estado de la postulación
formato: md
modo: generar
plantilla: ""
cadencia: a pedido              # recomendado: semanal y diario en la última semana antes del cierre
periodo_archivo: semana
destinatarios: []               # equipo interno y, si corresponde, el cliente que postula
fuentes:
  - herramientas/postulacion.py
  - postulacion/requisitos.csv
  - postulacion/calendario.csv
  - postulacion/consultas.csv
  - redteam/observaciones.csv
  - riesgos/riesgos.csv
---

# Propósito
Saber en 2 minutos si la postulación llega a tiempo y completa: etapa, compuerta, requisitos pendientes,
vencimientos y lo que decide el puntaje. Documento interno del equipo.

# Secciones
1. **Resumen** — convocatoria, días al cierre, etapa actual y si su compuerta se cumple.
2. **Semáforo** — cumplimiento de la matriz, excluyentes pendientes, controles económicos, fallas fatales,
   documentos vencidos (de `postulacion.py`).
3. **Próximos vencimientos** — hitos del calendario en los próximos 14 días.
4. **Requisitos pendientes** — primero los excluyentes, con responsable y acción.
5. **Consultas** — por enviar y sin respuesta; plazo del foro.
6. **Red team** — puntaje estimado frente a mínimo y objetivo, y observaciones abiertas priorizadas.
7. **Riesgos de la postulación** — los de severidad alta.
8. **Decisiones que se necesitan** — del postulante o del equipo, con fecha límite.

# Reglas
- Semáforo general: Rojo si hay excluyentes pendientes a 3 días o menos del cierre, fallas fatales abiertas o
  controles económicos incumplidos; Amarillo si el cumplimiento es menor a 100% o hay consultas sin respuesta;
  Verde en otro caso.
- Nunca informar un requisito como cumplido sin evidencia.
