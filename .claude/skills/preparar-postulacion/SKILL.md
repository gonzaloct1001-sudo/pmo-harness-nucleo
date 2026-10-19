---
name: preparar-postulacion
description: Orquesta la preparación de una postulación o propuesta para ganar un fondo concursable (CORFO, ANID, fondos regionales o privados), una licitación pública (Mercado Público) o privada, un RFP o un concurso — desde la recepción de las bases hasta la entrega y el resultado — con compuertas Go/No-Go, matriz de cumplimiento, pauta inversa, estrategia, redacción por secciones, presupuesto con controles, riesgos, red team, revisión final y transición a ejecución si se adjudica. Úsala cuando el usuario quiera postular, presentar una oferta, "armar la propuesta", preparar un proyecto para un fondo o licitación, o pregunte cómo va una postulación, qué falta o qué vence.
---

# Preparar postulación

**Meta:** una propuesta que cumple el 100% de las bases, maximiza el puntaje y llega a tiempo, completa y firmada.
Arquetipo: `postulacion` (guía en `arquetipos/postulacion/ARQUETIPO.md`). Estado en todo momento:
`python herramientas/postulacion.py proyectos/<slug> --registrar` (con `--registrar` las métricas quedan en
`mediciones.csv` y las reglas POS-01 a POS-06 de `evaluar_metricas.py` y los reportes las ven).

## 0. Ubicarse
1. Si el proyecto no existe: `nuevo-proyecto` (propone el arquetipo `postulacion`) o
   `python herramientas/crear_proyecto.py <slug> --arquetipos postulacion [--perfil biblioteca/perfiles/<perfil>]`.
   Ofrece un perfil de `biblioteca/perfiles/` si calza con la entidad (fondo-corfo, fondo-anid,
   licitacion-mercado-publico, fondo-regional-o-sectorial, licitacion-privada-rfp).
2. Ejecuta `postulacion.py --registrar` y lee la etapa actual (`postulacion.etapa`) y su compuerta. Trabaja en la etapa actual;
   no saltes compuertas. Si el usuario pide algo de una etapa posterior, hazlo, pero avisa qué compuerta previa falta.
3. Días al cierre ≤ 7: prioriza en este orden: excluyentes pendientes → fallas fatales → controles económicos →
   documentos vencidos → puntaje.

## 1. Recepción de bases y calendario
- Pide al usuario dejar bases, anexos, formularios, aclaraciones y respuestas del foro en
  `_entrada/00-bases-y-aclaraciones/` y ejecuta `extraer_entrada.py` y `extraer_requisitos.py`.
- Crea una ficha por documento en `postulacion/bases/` (ver su LEEME). Si llega una nueva versión o aclaración:
  `versiones-documentos` para comparar y vuelve a correr `extraer_requisitos.py` (es incremental).
- Completa `postulacion/calendario.csv` con **todos** los hitos (consultas, visita, respuestas, cierre con hora,
  apertura, adjudicación, garantías) y alertas en días. Completa el bloque `postulacion` de `proyecto.yaml`.
- Si las bases mencionan inteligencia artificial, registra `declaracion_ia_exigida` y avísalo de inmediato.

## 2. Go / No-Go
Completa `postulacion/go-no-go.md` con el postulante: elegibilidad (si algo excluyente no se cumple, es No-Go o
se resuelve antes), evaluación ponderada y condiciones. La decisión es del postulante: regístrala en
`postulacion.decision_go`. Con No-Go, cierra en `lecciones.md` y termina.

## 3. Matriz de cumplimiento, pauta inversa y consultas
- `matriz-cumplimiento`: revisa cada candidato del barrido, arma la matriz, asigna dueños.
- `definir-pauta` en modo oferente → `postulacion/pauta-inversa.yaml` (criterios, ponderación, niveles,
  mínimos y un `puntaje_objetivo` que el equipo se fija para tener opción real).
- Ambigüedades de las bases → `postulacion/consultas.csv` (borrador), redactadas para enviarse dentro del plazo
  del foro. El usuario las envía; marca `enviada` y luego la respuesta, que puede cambiar la matriz.

## 4. Estrategia (revisión azul)
Completa `postulacion/estrategia.md`: solución, propuesta de valor, **temas ganadores por criterio** (partiendo
por los de mayor peso), competidores probables, equipo, socios y documentos necesarios (cartas, CVs, certificados).
Revisión azul: pide al subagente `revisor-independiente` que critique la estrategia contra la pauta inversa.

## 5. Redacción por secciones (revisión rosa)
- Una sección por capítulo del formulario en `propuesta/` (plantilla `_plantilla-seccion.md`), con `responde_a`
  (requisitos y criterios) y `limite`. Usa `contexto/estilo.md` y reutiliza el banco de antecedentes adaptándolo:
  primero `empresa/contenidos/` (común a todas las postulaciones de la empresa) y luego `contenidos/` de la postulación.
- Escribe para el evaluador: los términos de la pauta, evidencia concreta, cifras con fuente, nada que no se pueda
  cumplir y rendir. Respeta los límites (cuenta caracteres o páginas).
- Revisión rosa con `red-team` (ronda `rosa`): estructura, cumplimiento y temas ganadores.

## 6. Presupuesto y evaluación económica
`evaluacion-economica` en modo postulación: `economico/presupuesto.yaml` con los parámetros de las bases (con
fuente) → `python herramientas/presupuesto_postulacion.py proyectos/<slug>/economico/presupuesto.yaml`. Los
controles NO CUMPLE deben quedar en cero. Si las bases piden VAN/TIR o flujo de caja, `modelo_economico.py`.

## 7. Riesgos, impacto e indicadores
`levantar-riesgos` con el checklist de postulación (inadmisibilidad, plazos, plataforma, documentos vencidos,
garantías, firmas de socios, sobrecompromiso) y los riesgos del proyecto propuesto. Impacto con indicadores
medibles, línea base y meta; plan de ejecución con hitos verificables.

## 8. Red team (revisión roja)
`red-team` (ronda `roja`): puntaje estimado frente a mínimo y objetivo, fallas fatales y plan de respuesta. Si hay
fallas fatales, corrige y haz una segunda ronda (`roja-2`) solo sobre lo cambiado y lo afectado.

## 9. Revisión oro, guante blanco y entrega
- **Oro:** el postulante aprueba monto, aportes, riesgos y compromisos. Si las bases exigen **declarar el uso de
  IA**, recuérdalo de forma destacada: la declaración la decide y la hace el postulante.
- **Guante blanco:** `matriz-cumplimiento` genera `entrega/checklist.md`; verifica nombres de archivo, formatos,
  límites, firmas, vigencias y coherencia de cifras en todo el paquete.
- Deja el paquete en `entrega/final/` y ejecuta `verificar_autoria.py entrega/final --proyecto proyectos/<slug>`.
  Los documentos de terceros (cartas de socios, certificados, garantías) y la declaración de uso de IA que exijan las
  bases van en `autoria.excluir`: no se verifican ni se modifican. La declaración se redacta con veracidad según lo
  que el postulante decida; si el tema del proyecto es la IA, agrega esos términos a `autoria.terminos_permitidos`.
- Recomienda cargar al menos 24 horas antes del cierre y guardar el comprobante.

## 10. Post-entrega
Registra el envío (calendario), atiende aclaraciones o subsanaciones dentro de plazo y registra el resultado en
`postulacion.resultado`.

## 11. Cierre
Completa `postulacion/lecciones.md` (puntaje real vs estimado, observaciones del evaluador) y actualiza el banco
de contenidos (lo que sirva para otras postulaciones, en `empresa/contenidos/`). **Si se adjudicó:** `crear_proyecto.py <slug> --arquetipos ejecucion` (agrega el arquetipo al mismo
proyecto) y lleva los compromisos de la propuesta (plazos, entregables, indicadores, presupuesto) al cronograma y
a la línea base; el convenio o contrato se incorpora con `registrar-documento`.

## Al avanzar de etapa
Cuando `postulacion.py` indique que la compuerta de la etapa actual está cumplida, propón avanzar y, con el visto
bueno del usuario, actualiza `postulacion.etapa`. Registra en `seguimiento/decisiones.csv` las decisiones de
compuerta (Go, cambios de flujo, aprobación oro).

## Qué no hacer
- No asumir porcentajes, topes, garantías ni plazos de otra convocatoria o de un perfil: se leen de las bases vigentes.
- No marcar un requisito como cumplido sin evidencia verificable.
- No redactar declaraciones juradas, firmas ni datos del postulante que él no haya entregado.
- No entregar nada que no pase `verificar_autoria.py`.
