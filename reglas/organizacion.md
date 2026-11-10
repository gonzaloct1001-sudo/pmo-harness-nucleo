# Reglas: organización de la carpeta y roles

Detalle de las secciones «Organización», «Proyecto activo» y «Roles» del mapa (`AGENTS.md`). Léelo al instalar, al
crear una empresa o un proyecto, al actualizar el núcleo o cuando una skill nombre un subagente que tu herramienta no tiene.

## Núcleo público, empresas privadas
**El núcleo se publica en un repositorio público** (URL en la primera línea de `NUCLEO.txt`): cualquiera lo descarga,
solo su dueño lo modifica. Quien lo descarga o clona lo instala como **su** carpeta de empresa con **su** repositorio
privado (`instalar` desconecta la copia del núcleo antes de crear el privado). **Nunca uses «Fork»:** un fork de un
repositorio público es público. La carpeta del dueño está marcada (`git config pmo.mantenedor true`) y no lleva
empresas ni proyectos.

Una carpeta del harness = un repositorio privado = **una empresa** (o persona); para otra empresa, otra carpeta
(`nueva_empresa.py`). **Nunca mezcles datos de dos empresas.** Si el usuario lleva varias, **pregúntale** si son
independientes o una misma entidad, separadas o juntas, y si quiere un **tablero único** o uno por empresa; el tablero
único va en una carpeta de panel con su propio repositorio privado (skill `status`).

## Capas
1. **Núcleo genérico** — sirve para cualquier proyecto. No se escribe nada específico de un proyecto aquí.
   `.claude/skills/` procedimientos (skills) · `.claude/agents/` roles (subagentes) · `herramientas/` scripts ·
   `reglas/` detalle de los principios · `.githooks/` controles de Git · `plantilla-proyecto/`,
   `plantilla-subproyecto/`, `plantilla-empresa/` bases. `NUCLEO.txt` lista las rutas del núcleo: se reemplazan al
   actualizarlo (`actualizar_nucleo.py`, que fusiona `settings.json` y completa `empresa/` sin pisar lo propio); todo
   lo demás es de la empresa y nunca se toca al actualizar.
2. **Arquetipos** — `arquetipos/<nombre>/`: estructura y guía de cada forma de trabajo. `ejecucion` (plan, hitos,
   contrato, valor ganado, ruta crítica) · `obra` (RFI, no conformidades, inspecciones, estados de pago) · `agil`
   (backlog, sprints, DORA, ADR, deuda) · `cartera` (ítems con etapas y métricas) · `evaluacion` (propuestas de
   terceros con pauta) · `postulacion` (ganar un fondo, licitación o concurso: matriz de cumplimiento, pauta inversa,
   red team, presupuesto con controles) · `programa` (contrato padre con subproyectos, presupuesto macro, personas
   compartidas, Gantt macro) · `estudio` (preguntas, supuestos, modelo económico, recomendación) · `investigacion`
   (hechos del mundo verificados con fuente, hipótesis asesinas, refutador, árbitro, puertas que firma quien decide) ·
   `finanzas` (plan de cuentas, presupuesto, cierre mensual reabrible, resultados, balance, caja, forecast,
   proyección, indicadores; consume la contabilidad) · `estrategia` (plan estratégico o de negocio a 3 o 5 años:
   diagnóstico con fuentes, lineamientos, objetivos con metas por año, iniciativas, plan financiero sobre finanzas,
   revisión periódica con decisiones). Un proyecto puede combinar arquetipos.
3. **Empresa** — `empresa/`: lo común a todos los proyectos de la empresa dueña de la carpeta: `empresa.yaml`
   (identidad, autoría, marca, formato, capacidad, política de réplicas), banco de antecedentes (`contenidos/`:
   descripción, experiencia, CVs, certificados con vigencia), `estilo.md`, `marca/`, `plantillas/` y formatos de
   reportes comunes (`reportes/catalogo/`), más `formatos/` (registro de los formatos propios adoptados) y `_entrada/`
   (donde se dejan los formatos y archivos base para adoptarlos; no se sube a Git). Los proyectos heredan de aquí lo
   que no definen.
4. **Proyecto** — `proyectos/<slug>/`: todo lo particular (datos, métricas, reglas, reportes con nombre propio,
   plantillas, marca, scripts de cálculo del dominio).

Además:
- `biblioteca/perfiles/` → diseños reutilizables. Incluye perfiles de convocatorias: `fondo-corfo`, `fondo-anid`,
  `licitacion-mercado-publico`, `fondo-regional-o-sectorial`, `licitacion-privada-rfp` (siempre se confirman contra las bases).
- `biblioteca/dominios/` → cartuchos de dominio para investigaciones (mapa de fuentes y modos de falla de un rubro);
  el núcleo trae `propiedad-industrial`; los demás son de la empresa.
- `biblioteca/finanzas/` → plan de cuentas base, definiciones de indicadores y notas por país.
- `empresa/investigacion/` → ajustes, preferencias y lecciones de investigación de la empresa (los escribe
  `investigacion.py`; una actualización del núcleo nunca los toca).
- `ejemplos/` → material ficticio de prueba (uno por capacidad; recorridos en `ejemplos/LEEME.md`). No son proyectos reales.
- `.harness/estado.yaml` → registro de la instalación (empresa, origen del núcleo) · `.harness/asistentes.yaml` →
  asistentes de IA configurados · `.harness/mejoras-nucleo.csv` → mejoras anotadas para el mantenedor ·
  `.harness/nube.yaml` → tareas en la nube aprobadas · `pruebas/` → batería de pruebas.

## Proyecto activo
1. Si el usuario nombra un proyecto, usa `proyectos/<slug>/`. Si nombra un **subproyecto** de un programa, usa
   `proyectos/<programa>/subproyectos/<id>/` (su `proyecto.yaml` hereda del programa lo que no define). Lo del
   programa completo (contrato, enmiendas, presupuesto, contingencia, personas, Gantt macro) va en la carpeta del programa.
2. Si hay un solo proyecto en `proyectos/`, usa ese. Los de `ejemplos/` solo se usan si el usuario los nombra.
3. Si hay duda, pregunta cuál. Nunca mezcles datos de dos proyectos, ni de dos subproyectos en un mismo registro.
   Un proyecto independiente nunca se mezcla con un programa.
4. Al empezar a trabajar en un proyecto, lee primero su `proyecto.yaml`, su `CLAUDE.md` (reglas del proyecto; valen
   para cualquier asistente, aunque el archivo se llame así) y su `seguimiento/traspaso.md`.
   Lee el resto de archivos solo cuando la tarea los necesite (ahorra contexto y tokens).

## Roles (subagentes) y equivalencias por herramienta
Roles en `.claude/agents/`: `lector-documental` (lee lotes de documentos y devuelve hechos con fuente) ·
`revisor-independiente` (revisa con ojo crítico antes de entregar) · `evaluador-propuestas` (evalúa una propuesta
por vez contra la pauta) · `analista-datos` (procesa y revisa datos sin modificarlos) · `revisor-red-team` (una
perspectiva del red team por vez) · `bibliotecario`, `refutador` y `arbitro` (roles de una investigación auditable:
recuperar sin interpretar, refutar en contexto estéril, aplicar las reglas de evidencia) · `analista-financiero` (calcula
y explica desvíos e indicadores de finanzas; no decide ni cambia datos).

- **Con subagentes** (Claude Code): invócalos como dice cada SKILL.md. Cada encargo lleva objetivo, salida, fuentes o
  archivos, límites y presupuesto; los resultados se escriben en archivos del proyecto, no solo en el resumen.
- **Sin subagentes:** aplica el rol tú mismo en un paso separado: lee su `.md`, adopta solo esa perspectiva, lee
  solo los archivos que el rol indica y escribe su resultado antes de seguir. Para evaluaciones y red team, haz una
  propuesta o perspectiva por vez y no mires los resultados de las otras hasta consolidar.
- **Controles:** en Claude Code corren los hooks de `.claude/settings.json` (estado al iniciar, protección de
  confidenciales, validación al editar, uso de skills, sesión larga, cierre). En todas las herramientas corre el
  control de Git (`.githooks/pre-commit`), que bloquea commits con archivos confidenciales o planillas mal formadas.
  Si tu herramienta no tiene hooks, el paso 0 y el principio 16 los haces tú.
- Detalle por herramienta (qué archivo lee, qué soporta, sesiones largas): `.claude/skills/configurar/references/asistentes.md`.
