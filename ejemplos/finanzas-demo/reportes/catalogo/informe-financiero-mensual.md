---
tipo: informe-financiero-mensual
nombre: Informe financiero mensual
formato: docx
modo: generar
plantilla: ""
cadencia: mensual
periodo_archivo: mes
destinatarios: []
fuentes:
  - finanzas/
  - metricas/mediciones.csv
claves: [informe, financiero, mensual, resultados, balance, caja, cierre, control de gestión, P&L, EBITDA]
---

# Propósito
Contar en pocas páginas cómo le fue a la empresa en el mes y en el acumulado del año, contra lo presupuestado y lo
proyectado, y qué se hace con los desvíos. Lo leen la gerencia y el directorio.

# Secciones
1. **Resumen del mes** — resultado, caja y los dos o tres hechos que explican el mes (`finanzas.py --estados`).
2. **Estado de resultados** — mes y acumulado: real, presupuesto, forecast y desvíos por línea.
3. **Desvíos explicados** — cada desvío relevante con causa, si es permanente o temporal y la acción.
4. **Caja** — saldo, variación del mes, meses de caja, vencimientos próximos.
5. **Balance de gestión** — activo, pasivo y patrimonio al cierre, con DSO, DPO, DIO, liquidez y endeudamiento.
6. **Forecast del año** — cómo cierra el año si siguen las tendencias; versión vigente.
7. **Alertas y decisiones requeridas** — lo que necesita una decisión de la gerencia o el directorio.
8. **Anexo** — cuentas sin mapear, reaperturas del período, supuestos usados.

# Validaciones antes de entregar
- `finanzas.py --revisar` sin errores; el período está cerrado (o se dice que es preliminar).
- Cada cifra sale de `finanzas.py --estados`; cada desvío relevante tiene explicación; sin `[PENDIENTE`.
- `verificar_autoria.py` en OK; revisión de `revisor-independiente` para el directorio.
