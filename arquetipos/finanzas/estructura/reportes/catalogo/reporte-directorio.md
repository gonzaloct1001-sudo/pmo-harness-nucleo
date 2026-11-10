---
tipo: reporte-directorio
nombre: Reporte financiero al directorio
formato: pptx
modo: generar
plantilla: ""
cadencia: mensual
periodo_archivo: mes
destinatarios: []
fuentes:
  - finanzas/
  - metricas/mediciones.csv
  - seguimiento/decisiones.csv
claves: [directorio, reporte, presentación, resultados, caja, decisiones, board]
---

# Propósito
Una presentación corta para el directorio: cómo va el año, qué cambió este mes, cuánta caja hay y qué decisiones se
necesitan. Una idea por diapositiva; las cifras salen de `finanzas.py --estados` y los semáforos de
`evaluar_metricas.py`.

# Secciones (diapositivas)
1. **Portada** — empresa, período, fecha.
2. **En una página** — resultado del mes y acumulado contra presupuesto, caja y meses de caja, tres mensajes.
3. **Resultados** — tabla mes y acumulado con desvíos y forecast del año.
4. **Caja y balance** — saldo y variación, DSO, DPO, liquidez, endeudamiento.
5. **Desvíos y acciones** — los desvíos relevantes con causa y acción.
6. **Decisiones requeridas** — qué se pide al directorio, con la recomendación de la gerencia.
7. **Anexo** — supuestos, reaperturas, cuentas sin mapear.

# Validaciones antes de entregar
- El período está cerrado; `finanzas.py --revisar` sin errores; sin `[PENDIENTE`.
- Revisión de `revisor-independiente`; `verificar_autoria.py` en OK.
