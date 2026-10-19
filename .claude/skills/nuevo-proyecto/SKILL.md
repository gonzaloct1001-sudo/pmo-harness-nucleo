---
name: nuevo-proyecto
description: Diseña y crea un proyecto de cualquier tipo a partir de una descripción libre y una mini entrevista — elige el arquetipo (ejecución por plan, cartera de ítems con métricas, estudio/análisis, o una combinación), propone entidades, etapas, métricas, reglas, reportes, riesgos y glosario según el dominio, y genera la estructura. Úsala cuando el usuario quiera empezar, crear, armar o llevar un proyecto nuevo y lo describa ("quiero llevar el seguimiento de una granja de bots", "quiero construir una casa", "quiero armar un portafolio de acciones", "quiero liderar un equipo de software", "quiero evaluar postulaciones a un fondo", "necesito una prefactibilidad"), o pida adaptar un proyecto existente a otro tipo o agregarle un arquetipo.
---

# Nuevo proyecto (diseño por conversación)

**Objetivo:** en una conversación corta, pasar de "quiero llevar X" a un proyecto funcionando con estructura,
métricas, reglas y reportes adecuados al dominio. El asistente propone desde su conocimiento del dominio y el
usuario ajusta: nunca empezar con un formulario en blanco.

## 0. ¿Dónde va? (siempre primero)
Si el usuario completó una ficha (`FICHA-DE-INICIO.md` o la que indique), úsala: resume lo que entendiste, pide
confirmación y pregunta solo lo que falte (también para la entrevista de estado y el diseño).
Revisa `proyectos/`: los programas son los que tienen `programa/subproyectos.csv`. Pregunta en una línea, con las
opciones que apliquen:
- **Proyecto independiente** (no comparte contrato ni presupuesto con nada) → `proyectos/<slug>/`, con su propio
  estado, minutas, formatos, objetivos, presupuesto y Gantt. Sigue en el paso 1.
- **Subproyecto de un programa existente** (nombra los programas que hay) → comparte el contrato padre, el presupuesto
  macro y las personas; tiene su propio Gantt, objetivos, riesgos, minutas y reportes. Sigue con `gestionar-programa`
  (sección "Agregar un subproyecto").
- **Programa nuevo** (un contrato general que se ejecuta en varios subproyectos) → crea el programa con
  `crear_proyecto.py <slug> --arquetipos programa,ejecucion` y luego cada subproyecto como arriba. En el diseño (paso 3)
  agrega: lista de subproyectos con responsable, reparto del presupuesto y la contingencia, personas compartidas y qué
  reportes son generales y cuáles por subproyecto.
Si la descripción del usuario ya lo deja claro ("agrega el proyecto J aparte", "un nuevo subproyecto del programa X"),
no preguntes: dilo en una línea y sigue.
**¿Es de otra empresa?** Una carpeta pertenece a una sola empresa (`empresa/empresa.yaml`). Si el proyecto es para otra
empresa (otro postulante, otro mandante con su propia marca), no lo crees aquí: ofrece «crear la carpeta para la empresa
X» (`nueva_empresa.py`, ver `instalar`).

## 1. Entender (un mensaje)
Si la descripción del usuario no alcanza, pregunta **solo** lo indispensable (máximo 3 preguntas):
qué se quiere lograr, qué se va a seguir (tareas, ítems, preguntas), y quién decide. Si ya se entiende, sigue.

## 2. Elegir arquetipo
Lee `arquetipos/*/ARQUETIPO.md` (solo las secciones "Cuándo usarlo" al principio, y luego el elegido completo).
- **ejecucion** — hay un plan con tareas, fechas, hitos y a menudo contrato (valor ganado, ruta crítica).
- **obra** — complemento de ejecución para trabajo en terreno: RFI, no conformidades, inspecciones, estados de pago.
- **agil** — equipos que entregan en iteraciones: backlog, sprints, DORA, ADR, deuda técnica, trazabilidad.
- **cartera** — muchos ítems similares con etapas y métricas (bots, acciones, proveedores, iniciativas).
- **evaluacion** — evaluar propuestas o postulaciones de terceros con una pauta (no combinar con cartera).
- **postulacion** — el lado del oferente: preparar y presentar una propuesta para ganar un fondo, licitación, RFP o
  concurso (matriz de cumplimiento, pauta inversa, red team, presupuesto con controles). Si hay bases de concurso
  en `_entrada/`, es la opción natural; ofrece el perfil de la entidad si existe. Con muchas postulaciones a la vez,
  `cartera` para el pipeline; si se adjudica, se agrega `ejecucion`.
- **estudio** — el producto es una respuesta o recomendación (prefactibilidad, evaluación económica).
- Combinaciones cuando corresponda: programa con desarrollo de software = `ejecucion,agil`; obra = `ejecucion,obra`;
  granja de bots = `cartera` para los bots (+ `agil` si el equipo los desarrolla en sprints).
  Si existe un perfil en `biblioteca/perfiles/` que calce, ofrécelo como base.
- Aún no hay arquetipo de *operación continua* (actividades recurrentes con indicadores de servicio): adapta
  `cartera` (ítems = servicios o activos) o `ejecucion`, y dilo.

## 3. Proponer el diseño (un mensaje, en una tabla)
Usando la guía del arquetipo y el conocimiento del dominio, propone:
| Elemento | Propuesta |
|---|---|
| Qué es un ítem / tarea / pregunta | |
| Etapas y requisitos para avanzar | |
| Métricas por ítem (con definición y umbral sugerido) | |
| Métricas del conjunto | |
| Reglas o políticas | |
| Fuentes de datos y frecuencia | |
| Cálculos que requieren un script propio | |
| Reportes y cadencia | |
| Riesgos típicos del dominio | |
| Términos del glosario | |

Agrega hasta 5 preguntas para lo que no puedas proponer con criterio (ej.: el índice de referencia, los
límites de la política, de dónde vienen los datos). Cada pregunta con una propuesta por defecto.
Deja claro que las métricas y umbrales son sugerencias iniciales y que agregar o cambiar métricas después es simple.

## 4. Generar
Tras la confirmación (o con los valores por defecto si el usuario dice "dale"):
1. `python herramientas/crear_proyecto.py <slug> --arquetipos <a>[,<b>] --nombre "<Nombre>"`
   Si la carpeta tiene `empresa/`, el proyecto hereda su responsable, marca, autoría, estilo y formatos de reporte
   comunes (y en una postulación, el postulante): no los preguntes de nuevo; completa solo lo propio del proyecto.
2. Completa `proyecto.yaml`, `CLAUDE.md` del proyecto (frase, reglas, rutina de actualización de datos; vale para
   cualquier asistente), `contexto/alcance.md`, `contexto/glosario.md`, `contexto/stakeholders.csv`, y deja
   `seguimiento/traspaso.md` con lo hecho y el próximo paso.
3. Escribe `metricas/metricas.yaml` (métricas y reglas) y, si aplica, `items/etapas.yaml`.
4. Si hay cálculos del dominio que el núcleo no hace, escribe un script en `scripts/` que lea de `datos/` y
   registre en `metricas/mediciones.csv`. Documenta el formato de cada archivo de datos en `datos/LEEME.md`.
   Prueba el script con 2 o 3 filas de ejemplo y luego déjalo sin datos ficticios (salvo que el usuario quiera un ejemplo).
5. Ajusta el reporte por defecto del arquetipo o crea los reportes acordados con `nuevo-tipo-reporte`.
6. Registra los riesgos iniciales del dominio con `riesgos-issues` (sin pedir confirmación uno a uno; el usuario los revisa en bloque).
7. Guarda el diseño en `contexto/diseno-del-proyecto.md`: descripción del usuario, arquetipo y por qué,
   tabla de decisiones, preguntas y respuestas (ver ejemplo en `ejemplos/portafolio-acciones/contexto/`).
8. Ejecuta `evaluar_metricas.py` (y `validar_proyecto.py` si es ejecución) para verificar que todo carga sin errores.

## 4b. Proyecto en marcha: entrevista de estado
Si el proyecto ya empezó y el estado actual no viene en documentos (o solo en parte), cárgalo conversando para que
el harness no parta en 0%. **Un solo mensaje**, máximo 8 preguntas, adaptadas al arquetipo, cada una con un ejemplo de
respuesta; el usuario puede contestar en viñetas, en bruto o pegando un correo:
1. **Hitos:** ¿cuáles ya se cumplieron (con fecha) y cuáles vienen en los próximos 60 días?
2. **Avance:** ¿cuánto va cada etapa o subproyecto (en % o "terminado / en curso / sin empezar")? ¿Qué está atrasado y por qué?
3. **Fechas y montos comprometidos:** término, presupuesto o monto del contrato y gasto a la fecha, si aplica.
4. **Problemas abiertos** hoy (qué, quién lo resuelve, para cuándo).
5. **Riesgos** que le preocupan.
6. **Compromisos vigentes:** acuerdos con fecha y responsable, reuniones o comités próximos.
7. **Decisiones** relevantes ya tomadas (qué, quién, cuándo).
8. **Reportes** que ya entrega (a quién, cada cuánto, en qué formato) y si tiene un ejemplo para dejar en `_entrada/`.

Según el arquetipo: en `cartera`, pregunta por los ítems actuales y su etapa; en `agil`, por el sprint en curso,
la velocidad y el backlog (ofrece importarlo); en `postulacion`, por la etapa del flujo, la fecha de cierre y qué
bases tiene (y pide dejarlas en `_entrada/00-bases-y-aclaraciones/`).

Con las respuestas:
- Carga cronograma (`actualizar-gantt`), riesgos y problemas (`riesgos-issues`), acuerdos y decisiones, ítems o
  etapa, sin pedir confirmación punto por punto: muestra un resumen de lo cargado para revisión en bloque.
- En cada registro, la fuente es "entrevista con <responsable>, AAAA-MM-DD". Lo que el usuario estima va marcado
  como **estimado**. Nunca completes lo que no dijo: queda `[PENDIENTE: …]` y va al resumen final.
- Actualiza `induccion` en `proyecto.yaml` (bloque 7 "Estado actual": parcial o completo) y, en ejecución,
  `cronograma_actualizado` con la fecha de la entrevista.
- Si falta información crítica que existe en algún documento (contrato, bases, último reporte), pide solo ese
  documento y ofrece procesarlo con `alta-proyecto`.

## 5. Cerrar
- Genera la guía del proyecto: `python herramientas/guia_proyecto.py proyectos/<slug>` (`GUIA.md`).
- Resume en pocas líneas qué quedó y cuál es la **rutina** del usuario (qué datos cargar, cada cuánto, qué pedir),
  con las skills más útiles para su tipo de proyecto y una frase de ejemplo para cada una (de `GUIA.md`).
- Si el usuario tiene documentos existentes, ofrece cargarlos en `_entrada/` y ejecutar `alta-proyecto` (fase B en adelante).
- Ofrece guardar el diseño como **perfil reutilizable** en `biblioteca/perfiles/<nombre>/` si es probable que
  haga más proyectos de este tipo (ver `biblioteca/LEEME.md`).
- Sugiere `guardar-cambios`.

## Criterios de calidad
- Cada métrica tiene definición, unidad, dirección, frecuencia y fuente. Sin fuente clara, no es métrica: es un pendiente.
- Las reglas son verificables con una métrica (si no, van como texto en el `CLAUDE.md` del proyecto).
- Nada específico del dominio va al núcleo (`.claude/skills/`, `herramientas/`, `arquetipos/`): todo queda en el proyecto.
- En dominios regulados o de alto riesgo (construcción, inversiones, salud, legal), el diseño organiza y
  mide; las decisiones técnicas o de inversión son del usuario y de los profesionales competentes. Déjalo
  escrito en el `CLAUDE.md` del proyecto.
