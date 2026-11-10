# Arquetipo: Estrategia (plan estratégico y plan de negocio a 3 o 5 años)

## Cuándo usarlo
Cuando el trabajo es **definir hacia dónde va una empresa o un área** y llevar ese plan: diagnóstico, lineamientos,
objetivos con indicadores y metas por año, iniciativas que los mueven, el plan financiero a 3 o 5 años (3YP, 5YP) y
la revisión periódica que compara metas con reales y ajusta. Sirve para una empresa, una gerencia o una unidad.

Señales para reconocerlo: «plan estratégico», «planificación estratégica», «3YP», «5YP», «plan de negocio a tres
años», «OKR», «cuadro de mando», «dónde queremos estar en 2030», «revisión trimestral del plan».

No es lo mismo que `estudio` (evalúa una inversión o responde una pregunta) ni que `finanzas` (lleva el día a día
financiero). Se **combina** con ellos: el diagnóstico externo entra por `investigacion` (hechos de mercado,
competencia y normativa con fuente); el diagnóstico interno y el plan financiero salen de `finanzas` (cierres,
proyección integrada con `proyeccion.yaml` a 3 o 5 años); las iniciativas grandes pueden llevarse como `cartera` o
`programa`.

## Cómo funciona (en simple)
1. **Diagnóstico** (`estrategia/diagnostico.md`): externo e interno; cada afirmación sobre el mundo lleva su marca y
   fuente (o «sin verificar»); síntesis en el marco que use la empresa (FODA u otro) y las decisiones que el plan debe
   tomar.
2. **Lineamientos** (`estrategia/lineamientos.md`): propósito, ambición medible al horizonte, tres a cinco apuestas y
   lo que **no** se hará.
3. **Cascada** (`objetivos.csv`, `metas.csv`, `iniciativas.csv`): objetivos → indicadores con línea base y meta por
   cada año del horizonte → iniciativas con responsable, fechas, inversión e impacto. Marco OKR o BSC, a elección
   (`estrategia.marco` en `proyecto.yaml`).
4. **Plan financiero** (3YP/5YP): las iniciativas se traducen en supuestos por línea y año de `finanzas/proyeccion.yaml`
   (del mismo proyecto, si combina `finanzas`, o del proyecto que indique `estrategia.proyecto_finanzas`); el
   horizonte de la proyección se fija en 3 o 5. Sin `finanzas`, una tabla simple en el documento, marcada como estimación.
5. **Documento y presentación** (`plan-estrategico`), con el formato de la empresa, revisados por red team y revisor
   independiente antes de ir al directorio.
6. **Revisión periódica** (`revisiones.csv`, reporte `revision-trimestral`): `estrategia.py --revision AAAA-Tn` arma
   la revisión del período con los reales disponibles; la persona decide qué se mantiene, se ajusta o se descarta.

## Qué agrega a la base
- `estrategia/diagnostico.md` y `estrategia/lineamientos.md` (plantillas con secciones fijas).
- `estrategia/objetivos.csv` (id, perspectiva, objetivo, responsable, estado) · `estrategia/metas.csv` (objetivo,
  indicador, unidad, dirección, línea base, año, meta, fuente del dato) · `estrategia/iniciativas.csv` (iniciativa,
  objetivo, responsable, fechas, inversión, impacto, estado) · `estrategia/revisiones.csv` (período, indicador, meta,
  real, desvío, semáforo, decisión).
- `metricas/metricas-estrategia.yaml`: cobertura de la cascada, iniciativas en curso y atrasadas, cumplimiento de
  metas de la última revisión, revisión al día.
- Reportes: `plan-estrategico` (documento y presentación al directorio) y `revision-trimestral`.
- Bloque `estrategia` en `proyecto.yaml`: horizonte (3 o 5), año de inicio, marco, cadencia de revisión, quién
  aprueba, proyecto de finanzas asociado.

## Herramientas
- `python herramientas/estrategia.py <proyecto>` → dónde va el plan y el siguiente paso.
- `--revisar` → la cascada cuadra: cada objetivo con indicador y meta para cada año del horizonte, iniciativas que
  apuntan a objetivos existentes, fechas y estados válidos, revisiones consistentes.
- `--revision AAAA-Tn [--hoy]` → arma o completa la revisión del período: metas del año, reales desde
  `metricas/mediciones.csv` cuando el indicador coincide con una métrica, desvío y semáforo.
- `--roadmap` → Gantt (Mermaid) de las iniciativas por año.
- `--registrar [--hoy]` → mediciones del arquetipo en `metricas/mediciones.csv`.

## Skills y roles
- Skill `plan-estrategico` (diagnóstico, lineamientos, cascada, plan financiero, documento, revisión).
- `investigar` para los hechos de afuera; `gestion-financiera` para el 3YP/5YP; `riesgos` para los riesgos del plan.
- Subagentes: `revisor-red-team` (perspectivas: director exigente, competidor, cliente, CFO, regulador) antes de
  presentar; `revisor-independiente` antes de entregar; `analista-financiero` para la proyección.

## Principios
- **Una meta por año y por indicador**, con línea base y fuente del dato: sin eso no hay plan, hay deseos.
- **Cada afirmación del diagnóstico con fuente** o marcada «sin verificar»; lo que sostiene una apuesta se
  investiga con protocolo.
- **El plan financiero sale de las iniciativas**, no al revés: cada supuesto de la proyección se rastrea a una
  iniciativa o a una tendencia declarada.
- **La revisión es una decisión, no un informe**: cada desvío termina en mantener, ajustar la meta, reasignar
  recursos o descartar, con quién lo decidió.
- Las decisiones estratégicas son del directorio o de la gerencia; el harness organiza, mide y plantea preguntas.

## Preguntas de la mini entrevista
1. ¿Para quién es el plan (empresa, gerencia, unidad) y quién lo aprueba?
2. ¿Horizonte: 3 o 5 años? ¿Primer año del plan?
3. ¿Marco preferido: OKR, cuadro de mando (BSC) o el propio de la empresa?
4. ¿Hay finanzas en el harness (proyecto con arquetipo `finanzas`) para apoyar el plan financiero?
5. ¿Qué material existe (plan anterior, diagnóstico, presentaciones al directorio)? Va a `_entrada/`.
6. ¿Cada cuánto se revisa (trimestral por defecto) y en qué instancia?
