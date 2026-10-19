# Arquetipo: Estudio / análisis

## Cuándo usarlo
Cuando el producto es **una respuesta o una recomendación**, no una obra ni una cartera: estudio de perfil,
prefactibilidad o factibilidad, evaluación económica de una inversión, análisis de mercado, due diligence,
evaluación de alternativas.

## Qué agrega a la base
- `estudio/preguntas.md` — decisión que apoya y preguntas que debe responder.
- `estudio/supuestos.csv` — cada supuesto con valor, fuente, confianza y sensibilidad.
- `estudio/escenarios.csv` — escenarios (base, optimista, pesimista u otros).
- `estudio/modelo/` — modelos de cálculo (Excel con fórmulas o scripts).
- `estudio/hallazgos.md` y `estudio/conclusiones.md`.
- Reporte por defecto: `informe-estudio`.

## Etapas típicas de un estudio de inversión
| Etapa | Qué se espera | Nivel de precisión habitual |
|---|---|---|
| Perfil | Identificar el problema, alternativas y descartar las inviables con información disponible | bajo |
| Prefactibilidad | Comparar alternativas con información secundaria y primaria parcial; elegir la mejor | medio |
| Factibilidad | Afinar la alternativa elegida con información primaria; diseño y evaluación detallados | alto |

El paso de una etapa a otra se justifica si la información adicional puede cambiar la decisión.

## Evaluación económica (guía mínima)
- Horizonte de evaluación y valor residual explícitos.
- Flujo de caja: inversiones, ingresos, costos, impuestos (evaluación privada), capital de trabajo.
- Indicadores: VAN a la tasa definida en el proyecto, TIR, período de recuperación; en evaluación social,
  precios sociales y tasa social según la metodología oficial aplicable.
- Sensibilidad sobre los supuestos de mayor impacto y escenarios.
- El modelo en Excel debe usar fórmulas (no valores calculados) y tener los supuestos en celdas propias.

## Métricas típicas
VAN, TIR, período de recuperación, costo por beneficiario, preguntas respondidas / total, supuestos con
confianza baja.

## Preguntas de la mini entrevista
1. ¿Qué decisión debe apoyar el estudio y quién la toma?
2. ¿En qué etapa está (perfil, prefactibilidad, factibilidad) o qué tipo de análisis es?
3. ¿Hay metodología obligatoria (de un fondo, de un organismo público, de la empresa)?
4. ¿Qué información existe y qué habrá que levantar?
5. ¿Plazo del estudio y formato del informe final?
