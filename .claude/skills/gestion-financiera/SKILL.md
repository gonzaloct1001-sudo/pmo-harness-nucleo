---
name: gestion-financiera
description: Lleva el área de finanzas de una empresa con el arquetipo finanzas — arranque (plan de cuentas mapeado a las líneas del reporte e histórico), presupuesto anual con supuestos y versiones, cierre mensual (importar la contabilidad, cuadrar, mapear, explicar desvíos, indicadores, informe, cerrar y reabrir), forecast del año, proyección integrada a varios años y reporte al directorio con los formatos de la empresa. Úsala cuando el usuario pida llevar o revisar las finanzas, el presupuesto, el cierre del mes, el P&L o estado de resultados, el balance, la caja, el forecast, los indicadores financieros, el informe o la presentación financiera al directorio, importar un balance de comprobación, o pregunte «¿cómo vamos financieramente?», «¿por qué subió el gasto?», «¿cuánta caja tenemos?», «¿cómo cierra el año?». No la uses para evaluar una inversión (evaluacion-economica) ni para el presupuesto de una postulación.
---

# Gestión financiera

**Lo que manda:** el harness no reemplaza la contabilidad ni al contador; consume sus salidas (balance de comprobación,
libro mayor) y organiza la gestión. Ninguna cifra se escribe a mano: sale de `finanzas/real.csv` importado o de un
supuesto con fuente. Los cuadres van antes que el análisis. Un período cerrado no cambia sin reabrirlo.

**Tu guía:** `python herramientas/finanzas.py proyectos/<slug>` dice dónde va (último período, cierres, cuentas sin
mapear, indicadores, desvíos) y el siguiente paso. Ejecútalo al empezar y después de cada paso. El arquetipo está en
`arquetipos/finanzas/ARQUETIPO.md`; los indicadores, en `biblioteca/finanzas/kpi-definiciones.md`.

## 0. Ubicar y elegir el modo
- Proyecto con arquetipo `finanzas` (si no existe: `nuevo-proyecto` con `finanzas`, o `crear_proyecto.py <slug>
  --arquetipos finanzas` sobre uno existente). Una empresa cliente = su carpeta; sus finanzas = un proyecto dentro.
- Según lo que pida el usuario, sigue el modo que corresponda. Si acaba de empezar, el modo es **arranque**.

| Modo | Cuándo | Referencia |
|---|---|---|
| Arranque | No hay plan mapeado o no hay histórico | `references/arranque.md` |
| Presupuesto | Preparar o versionar el presupuesto del año | `references/presupuesto.md` |
| Cierre mensual | Llegó la contabilidad del mes; cerrar o reabrir | `references/cierre.md` |
| Desvíos y forecast | Explicar el mes; actualizar cómo cierra el año | `references/desvios-y-forecast.md` |
| Proyección | Varios años integrados desde supuestos | `references/proyeccion.md` |
| Directorio | Informe mensual o presentación | `references/directorio.md` |

Lee solo la referencia del modo en curso.

## 1. Reglas de conversación
- Habla en simple y con las cifras del script: «el margen bruto cayó a 33 % porque el costo subió 4 % y el precio no».
- Una decisión por vez, con la respuesta exacta: «¿Cierro septiembre con la cuenta 6999 mapeada a gastos de
  administración? Responde "sí, ciérralo" o dime a qué línea va».
- Nunca inventes una cifra ni completes un dato que falta: queda `[PENDIENTE: …]` y se pide.
- Lo que requiere criterio contable o tributario (provisiones, depreciación, impuestos, régimen) se pregunta al
  contador: propón la pregunta, no la respuesta.
- Decisiones de financiamiento, inversión o reparto de utilidades: la gerencia y el directorio deciden; tú organizas
  los números y las alternativas.

## 2. Subagentes y capacidad
- `analista-financiero` (media): ejecuta `finanzas.py`, revisa los datos, calcula y explica desvíos e indicadores,
  redacta el comentario del mes. No cambia datos.
- `revisor-independiente` (alta): antes de cualquier informe o presentación al directorio.
- `investigar` cuando un supuesto depende de hechos de afuera (precios de mercado, normativa, competidores).
- `adoptar-formatos` para que el informe y la presentación salgan con los formatos de la empresa.

## 3. Al terminar
- `finanzas.py --registrar` deja los indicadores en `metricas/mediciones.csv`: el status los muestra con semáforo
  (reglas FIN-01 a FIN-06 en `metricas/metricas-finanzas.yaml`; cada empresa ajusta los umbrales a su rubro).
- Traspaso (`seguimiento/traspaso.md`) con el período en curso, lo pendiente y la próxima fecha de cierre.
- Decisiones del usuario (presupuesto aprobado, cierre, reapertura) en `seguimiento/decisiones.csv`.
- `guardar-cambios`. Las exportaciones de la contabilidad quedan en `_entrada/10-contabilidad/` (no se suben).
