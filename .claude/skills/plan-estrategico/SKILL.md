---
name: plan-estrategico
description: Construye y lleva el plan estratégico o plan de negocio a 3 o 5 años (3YP, 5YP): diagnóstico con fuentes, lineamientos, objetivos con metas por año (OKR o cuadro de mando), iniciativas, plan financiero sobre finanzas, documento al directorio y revisión trimestral con decisiones. Úsala con «plan estratégico», «3YP», «5YP», «dónde queremos estar en…», «revisión del plan».
---

> Reglas que aplican (léelas si no están en tu contexto): `reglas/trabajo.md`, `reglas/datos.md`, `reglas/entregables.md`, `reglas/nucleo.md`.

# Plan estratégico (3YP / 5YP)

**Principio:** un plan es una cascada que cuadra —apuestas → objetivos → indicadores con meta por año → iniciativas
→ supuestos financieros— y una revisión que decide. Lo que no se puede medir ni financiar no es parte del plan. Las
decisiones son del directorio o la gerencia; el harness organiza, mide y plantea preguntas.

Arquetipo `estrategia` (`arquetipos/estrategia/ARQUETIPO.md`). Estado en todo momento:
`python herramientas/estrategia.py proyectos/<slug>` (dónde va y el siguiente paso).

## 0. Dónde va
- Proyecto propio con arquetipo `estrategia` (`crear_proyecto.py <slug> --arquetipos estrategia`), o sumado al
  proyecto `finanzas` de la empresa (`--arquetipos estrategia` sobre ese proyecto) cuando el plan y las finanzas los
  lleva la misma gerencia: así la proyección a 3 o 5 años vive en el mismo lugar.
- Completa `estrategia` en `proyecto.yaml`: horizonte (3 o 5), año de inicio, marco (okr, bsc, propio), cadencia de
  revisión, quién aprueba, proyecto de finanzas asociado. Material previo (plan anterior, presentaciones) a `_entrada/`.

## 1. Diagnóstico (`estrategia/diagnostico.md`) — `references/diagnostico.md`
- **Externo:** mercado, clientes, competencia, normativa, tecnología. Toda afirmación con fuente o marcada «sin
  verificar». Lo que sostiene una apuesta (tamaño de mercado, movimientos de competidores, un cambio normativo) se
  investiga con la skill `investigar` (sondeo) y entra con marca.
- **Interno:** resultados de los últimos cierres (`finanzas.py --estados`, si hay finanzas), capacidades, lo que limita.
- Síntesis en el marco de la empresa (FODA u otro) y la lista de decisiones que el plan debe tomar.

## 2. Lineamientos (`estrategia/lineamientos.md`)
Propósito, ambición medible al horizonte, tres a cinco apuestas, lo que no se hará, principios de decisión. Una
página; se propone y el usuario ajusta. Sin aprobación de quien corresponde, el plan queda «propuesto».

## 3. Cascada — `references/cascada.md`
1. `objetivos.csv`: de cada apuesta salen uno a tres objetivos (perspectiva según el marco; estado `propuesto` hasta
   la aprobación).
2. `metas.csv`: por objetivo, uno o dos indicadores con unidad, dirección, línea base (y su año) y **meta para cada
   año del horizonte**, con la fuente de donde saldrá el real (una métrica del proyecto, finanzas, un sistema).
3. `iniciativas.csv`: lo que mueve cada objetivo, con responsable, fechas, inversión e impacto (qué línea
   financiera mueve y cuánto por año). Las grandes se llevan como `cartera` o `programa` (`cartera_item`).
4. `python herramientas/estrategia.py proyectos/<slug> --revisar` hasta que la cascada no tenga errores.

## 4. Plan financiero a N años — `references/plan-financiero.md`
Las iniciativas se vuelven supuestos por línea y año de `finanzas/proyeccion.yaml` (horizonte = el del plan) y se
corre `finanzas.py --proyectar`; cada supuesto se rastrea a una iniciativa o a una tendencia declarada. El
`analista-financiero` revisa razonabilidad. Sin finanzas en el harness: tabla simple en el documento, marcada
«estimación», y propuesta de crear el proyecto finanzas.

## 5. Documento y presentación
Reporte `plan-estrategico` con la skill `reportes` (secciones del catálogo; `--roadmap` para el Gantt). Antes del
directorio: `red-team` con las perspectivas director exigente, competidor, cliente, CFO y regulador; luego
`revisor-independiente`; `verificar_autoria.py` en OK. Registra la aprobación en `lineamientos.md` y pasa objetivos e
iniciativas a `aprobado`/`aprobada`.

## 6. Revisión periódica — `references/revision.md`
Cada período (`estrategia.revision`): `estrategia.py --revision AAAA-Tn --quien "<nombre>"` arma las filas con los
reales disponibles; completa los que falten con su fuente; cada rojo termina en una **decisión** (mantener, ajustar
meta, reasignar, descartar) con quién. Reporte `revision-trimestral`. `--registrar` deja las métricas del plan en
`metricas/mediciones.csv` para el status.

## Qué no hacer
- Objetivos sin indicador, indicadores sin meta por año, metas sin línea base: no se dan por escritos.
- Cifras de mercado o de competidores de memoria: van por `investigar` o marcadas «sin verificar».
- Un plan financiero desconectado de las iniciativas.
- Dar por aprobado el plan o una decisión de la revisión sin quien corresponde.
