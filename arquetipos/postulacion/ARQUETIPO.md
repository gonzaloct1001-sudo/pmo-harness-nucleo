# Arquetipo: Postulación (el lado del oferente)

## Cuándo usarlo
Cuando el trabajo es **preparar y presentar una propuesta para ganar**: postulación a un fondo concursable
(CORFO, ANID, fondos regionales o sectoriales, fondos privados), oferta a una licitación pública (Mercado
Público) o privada, respuesta a un RFP o concurso. Lo usa quien postula o quien asesora a empresas que postulan.

El resultado buscado es una propuesta que:
1. cumple el **100%** de los requisitos de las bases (administrativos, técnicos, económicos y formales);
2. responde a cada criterio de evaluación para **maximizar el puntaje**;
3. se sostiene en su evaluación económica, sus riesgos y su impacto;
4. llega a tiempo, completa y firmada, por el canal que exigen las bases.

Es el opuesto del arquetipo `evaluacion` (que evalúa propuestas de terceros) y reutiliza su formato de pauta.
Se combina con `cartera` si se gestionan muchas postulaciones a la vez (pipeline por etapa, tasa de
adjudicación) y se transforma en `ejecucion` si se adjudica.

## Método
Buenas prácticas profesionales de elaboración de propuestas (método Shipley/APMP) adaptadas a concursos
chilenos:
- **Compuertas Go/No-Go:** se decide formalmente si vale la pena postular y se revisa en cada etapa.
- **Matriz de cumplimiento:** cada requisito de las bases, con su fuente, dueño, forma de cumplirlo y evidencia.
- **Barrido exhaustivo de las bases** (`extraer_requisitos.py`): todo párrafo con lenguaje obligatorio se
  revisa y se incorpora a la matriz o se descarta con motivo. Así no se escapan requisitos escondidos en
  anexos, formularios o aclaraciones.
- **Pauta inversa:** la pauta con que evaluará la entidad, reconstruida desde las bases.
- **Temas ganadores:** propuesta de valor y diferenciadores mapeados a los criterios de mayor peso.
- **Revisiones por equipos de colores**, siempre por quien no redactó:
  azul (estrategia) · rosa (primer borrador completo) · roja (casi final, puntuada como el comité) ·
  oro (aprobación final de precio, riesgos y compromisos) · guante blanco (revisión formal final).
- **Red team** (skill `red-team`): panel de revisores aislados con perspectivas distintas (evaluador técnico,
  fiscalizador de admisibilidad, financiero, experto escéptico, competidor, beneficiario, auditor de rendición y
  abogado del diablo).

## Flujo estándar (`postulacion/etapas.yaml`, modificable)
| # | Etapa | Compuerta para avanzar |
|---|---|---|
| 1 | Recepción de bases y calendario | Bases inventariadas y barridas; calendario con cierre |
| 2 | Go / No-Go | Decisión `go` registrada con fundamentos |
| 3 | Matriz de cumplimiento, pauta inversa y consultas | Barrido revisado, requisitos con dueño, consultas enviadas |
| 4 | Estrategia (revisión azul) | Estrategia sin pendientes |
| 5 | Redacción por secciones (revisión rosa) | Secciones con trazabilidad a requisitos y criterios; ronda rosa hecha |
| 6 | Presupuesto y evaluación económica | Controles del presupuesto sin incumplimientos |
| 7 | Riesgos, impacto e indicadores | Riesgos registrados con mitigación |
| 8 | Red team (revisión roja) | Puntaje estimado sobre el objetivo y sin fallas fatales abiertas |
| 9 | Revisión oro, guante blanco y entrega | 0 excluyentes pendientes, 100% de cumplimiento, documentos vigentes, autoría OK |
| 10 | Post-entrega | Resultado registrado |
| 11 | Cierre y lecciones | Lecciones escritas; si se adjudicó, transición a `ejecucion` |

El flujo vive en el proyecto: si las bases definen otras etapas (pertinencia, pitch, entrevista, evaluación en
dos fases) se agregan o renombran allí, registrando la decisión.

## Qué agrega a la base
- `postulacion/`: `etapas.yaml`, `requisitos.csv` (matriz), `barrido-requisitos.csv`, `calendario.csv`,
  `consultas.csv`, `pauta-inversa.yaml`, `go-no-go.md`, `estrategia.md`, `bases/` (fichas y versiones).
- `propuesta/`: una sección `.md` por capítulo del formulario, cada una con los requisitos y criterios que responde.
- `economico/`: `presupuesto.yaml` → Excel con fórmulas y controles (`presupuesto_postulacion.py`) y, si
  corresponde, evaluación económica (`modelo_economico.py`).
- `redteam/`: `perspectivas.yaml`, `puntajes.csv`, `observaciones.csv` (plan de respuesta) e informes por ronda.
- `entrega/`: `checklist.md` y `final/` (paquete presentado; no se sube a Git).
- `contenidos/`: banco reutilizable por cliente (descripción de la empresa, experiencia, CVs, certificados) con
  vigencia; los archivos van en `contenidos/archivos/` (no se suben a Git).
- Bloque `postulacion` en `proyecto.yaml` y métricas en `metricas/metricas-postulacion.yaml`.
- Reportes: `estado-postulacion` e `informe-red-team`.

## Herramientas
- `python herramientas/extraer_requisitos.py <proyecto>`: barrido de las bases (texto en `_entrada/_procesado/texto/`
  o `postulacion/bases/`) → `postulacion/barrido-requisitos.csv`, incremental.
- `python herramientas/postulacion.py <proyecto> [--registrar]`: etapa actual y su compuerta, cumplimiento,
  excluyentes pendientes, vencimientos del calendario, consultas, puntaje del red team, fallas fatales,
  controles económicos, documentos vencidos y autoría del paquete final.
- `python herramientas/presupuesto_postulacion.py <presupuesto.yaml>`: Excel del presupuesto con fórmulas,
  fuentes de financiamiento y hoja de controles contra los parámetros de las bases.
- `python herramientas/puntaje_pauta.py`: no aplica (es del evaluador); el puntaje del red team lo calcula `postulacion.py`.

## Skills
`preparar-postulacion` (orquesta el flujo) · `matriz-cumplimiento` · `red-team` · `definir-pauta` (modo
oferente: pauta inversa) · `evaluacion-economica` (modo postulación) · `levantar-riesgos` (checklist de
postulación) · `versiones-documentos` (bases y aclaraciones) · `revisar-documento` · `generar-reporte`.

## Principios
- **Las bases mandan.** Porcentajes de cofinanciamiento, topes, garantías, plazos, formatos y límites de páginas
  se leen de las bases vigentes y sus aclaraciones; nunca se asumen de otra convocatoria ni de un perfil.
- **Lo formal es tan importante como lo técnico:** una propuesta excelente fuera de plazo o sin un anexo firmado
  queda fuera. Los requisitos excluyentes se verifican dos veces (matriz y guante blanco).
- **Nada se promete que no se pueda cumplir y rendir:** lo que se ofrece será la línea base si se adjudica.
- **Integridad:** si las bases exigen declarar el uso de herramientas de IA, o lo restringen, es un requisito
  (tipo `declaracion`) y la decisión es del postulante. Declaraciones juradas, firmas y datos del postulante los
  valida el postulante; el harness no los inventa ni los firma.
- **Autoría limpia:** todo lo que se entrega pasa por `verificar_autoria.py`.
- Decisiones legales, tributarias y técnicas especializadas: el harness organiza y alerta; deciden el
  postulante y sus asesores.

## Preguntas de la mini entrevista
1. ¿Qué convocatoria es (entidad, instrumento, enlace o bases) y cuándo cierra?
2. ¿Quién postula (empresa, tamaño, antigüedad) y quién firma?
3. ¿Qué proyecto o solución se propone, en pocas líneas, y con qué equipo o socios?
4. ¿Cuánto se pide y cuánto aporta el postulante (pecuniario y no pecuniario)?
5. ¿Hay postulaciones anteriores, evaluaciones recibidas o material reutilizable?
