---
tipo: estado-programa
nombre: Estado general del programa
formato: docx
modo: generar
plantilla: ""                   # formato por defecto con la marca del programa; reemplázalo por la plantilla del programa
cadencia: mensual
periodo_archivo: mes
destinatarios: []
fuentes:
  - herramientas/programa.py
  - subproyectos/*/seguimiento/
  - riesgos/
  - contractual/linea-base-vigente.md
---

# Propósito
Visión consolidada del programa para el cliente o el comité: todos los subproyectos en una página y el detalle
necesario para decidir. Los reportes de cada subproyecto van en el catálogo de cada subproyecto.

# Secciones
1. **Resumen ejecutivo** — estado general (semáforo), hitos logrados y próximos, decisiones que se necesitan.
2. **Avance por subproyecto** — tabla: subproyecto, avance plan, avance real, desviación, término planificado vs
   término vigente, estado (de `programa.py`). Avance del programa ponderado.
3. **Carta Gantt macro** — una barra por subproyecto con sus hitos contractuales (`cronograma/gantt-programa.md`).
4. **Presupuesto** — por subproyecto: vigente, comprometido, real, disponible, estimado al término y desviación;
   contingencia del programa y por subproyecto (saldo y usos del período).
5. **Contrato y enmiendas** — línea base vigente y afectaciones de las enmiendas por subproyecto.
6. **Equipo** — dotación por subproyecto y personas sobreasignadas.
7. **Riesgos y problemas del programa** — los de severidad alta de cualquier subproyecto y los transversales.
8. **Próximos pasos**.

# Reglas
- Semáforo del programa: Rojo si un subproyecto termina después de su línea base o el estimado al término supera el
  presupuesto vigente; Amarillo si la desviación de avance del programa supera el umbral amarillo o la contingencia
  queda bajo la alerta; Verde en otro caso.
- Las cifras salen de `programa.py` con la misma fecha de corte para todos los subproyectos.
