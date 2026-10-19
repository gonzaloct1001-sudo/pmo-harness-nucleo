---
name: revisar-estudio
description: Revisa la calidad y completitud de un estudio de preinversión o análisis (perfil, prefactibilidad, factibilidad, estudio de mercado, due diligence, evaluación de alternativas), propio o de terceros — verifica que tenga lo esperable según su etapa, que los supuestos tengan fuente, que la evaluación sea consistente y que la recomendación se sostenga. Úsala cuando el usuario pida revisar un estudio o informe técnico-económico, decidir si un estudio puede pasar a la siguiente etapa, o preparar observaciones a un consultor.
---

# Revisar estudio

## 1. Ubicar el estudio
Si es propio, está en `estudio/`. Si es de un tercero, conviértelo a texto (`extraer_entrada.py`) y, si
viene con planilla, inspecciónala (`inspeccionar_xlsx.py`). Identifica la etapa declarada y la decisión que apoya.

## 2. Revisión por etapa
Aplica `references/checklist-etapas.md` según la etapa. Marca cada punto como Cumple / Parcial / No cumple
/ No aplica, con la evidencia (sección o página).

## 3. Revisión transversal
- **Supuestos**: ¿tienen fuente? ¿son consistentes entre secciones (mismo precio, misma demanda)?
- **Evaluación económica**: flujos incrementales, sin doble conteo, impuestos y depreciación correctos
  (privada) o precios sociales (social), valor residual razonable, tasa justificada, moneda consistente.
  Si hay planilla, recalcula los indicadores principales (puedes reconstruir el caso con `modelo_economico.py`).
- **Sensibilidad**: ¿se analizan las variables críticas? ¿la conclusión resiste escenarios razonables?
- **Alternativas**: ¿se compararon alternativas reales, incluida la situación base optimizada?
- **Riesgos**: identificados y con mitigación; usa `levantar-riesgos` si el estudio los omite.
- **Coherencia de la recomendación** con los resultados.

## 4. Resultado
Informe en `estudio/revision_<AAAA-MM-DD>.md` (o el formato que pida el usuario) con: veredicto (apto para
decidir / apto para pasar a la siguiente etapa / requiere correcciones), tabla del checklist, observaciones
priorizadas (críticas, importantes, menores) redactadas para entregar al autor, y preguntas abiertas.
Para estudios importantes, pide una segunda mirada al subagente `revisor-independiente`.
