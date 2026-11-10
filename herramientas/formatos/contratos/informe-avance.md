---
tipo: informe-avance
nombre: Informe de avance (semanal, quincenal o mensual)
formatos: [docx, md, pptx]
claves: [informe, avance, reporte, semanal, mensual, quincenal, estado, gestión, seguimiento, status]
---

# Secciones

| Sección | Sinónimos | Fuente en el harness | Obligatoria |
|---|---|---|---|
| Estado general | resumen, resumen ejecutivo, semáforo, situación | evaluar_metricas.py, validar_proyecto.py | sí |
| Avance | avance por subproyecto, avance del período, actividades, hitos, cumplimiento | cronograma/, evm_cpm.py, items/, agil/ | sí |
| Logros | hitos cumplidos, realizado, entregables, lo hecho | seguimiento/AAAA-Sxx.md | no |
| Riesgos | riesgos principales, alertas, amenazas | riesgos/riesgos.csv | sí |
| Problemas | issues, problemas abiertos, incidencias, bloqueos, dificultades | riesgos/issues.csv | sí |
| Próximos pasos | siguientes pasos, próximas actividades, próximas acciones, plan de la próxima semana, compromisos | cronograma/, seguimiento/acuerdos.csv | sí |
| Decisiones requeridas | decisiones pendientes, requerimientos al comité, solicitudes, apoyo requerido | seguimiento/decisiones.csv | no |
| Presupuesto | costos, gasto, financiero, presupuestario | evm_cpm.py, presupuesto/ | no |
