# PMO Harness v3.4

Un arnés para que un asistente de IA —Claude Code, OpenAI Codex, Gemini, Google Antigravity, Cursor, GitHub Copilot u
otro que trabaje sobre carpetas— lleve con método y evidencia **tus proyectos, las finanzas de tu empresa y tus
investigaciones**, en una carpeta privada tuya. Cargas los documentos que ya tienes y en horas el proyecto queda
configurado; cada mes cierras las finanzas como un controller; cada afirmación sobre el mundo llega con fuente,
refutador y puertas que firmas tú. Todo vive en una carpeta local por empresa, respaldada en un repositorio
**privado** de GitHub de quien lo usa.

> **¿Primera vez?** Sigue la [guía de inicio](EMPEZAR-AQUI.md) (15 minutos, sin conocimientos técnicos). El uso
> diario está en el [manual de usuario](MANUAL-DE-USUARIO.md). Licencia MIT.

## Qué hace

**Gestión de proyectos de cualquier tipo.** Ejecución por plan (Gantt, hitos, contrato, valor ganado, ruta crítica),
obra (RFI, no conformidades, inspecciones, estados de pago), equipo ágil (backlog, sprints, DORA, decisiones de
arquitectura), cartera de ítems con etapas (acciones, bots, iniciativas, proveedores), programa con subproyectos y
estudios. Se carga desde los documentos que existen y el asistente configura el proyecto en horas: lee todo, decide
con reglas explícitas, deja registro de cada decisión y pregunta solo lo que no puede resolver. Después: status
diario, reportes con tus formatos, reuniones (agenda y minuta), riesgos, cambios, documentos y consistencia.

**Finanzas de la empresa, como un controller.** Plan de cuentas mapeado a líneas, presupuesto anual con supuestos y
versiones, cierre mensual que importa la contabilidad, cuadra, explica desvíos y se puede reabrir con huella;
resultados, balance y caja; forecast; proyección integrada a tres años en Excel con fórmulas; indicadores con
semáforo e informe y presentación al directorio. «¿Cómo vamos financieramente?», «cierra septiembre», «¿por qué subió
el gasto?». Y sobre esa base, el **plan estratégico a 3 o 5 años**: diagnóstico con fuentes, objetivos con metas por
año, iniciativas que se vuelven supuestos de la proyección y una revisión trimestral que decide.

**Investigación auditable, de cualquier ámbito.** Cuando una decisión o un entregable dependen de hechos del mundo
(a quién ofrecer una licencia, qué socios o proveedores califican, estado del arte, patentes, normativa, una due
diligence, «¿es cierto que…?»), el harness aplica un protocolo: encuadre con la decisión que se tomará, hipótesis
asesinas antes de construir, expediente con marcas (hecho, dato calculado, testimonio, pista) y niveles de fuente,
bibliotecarios que trabajan en paralelo sin interpretar, refutador y árbitro independientes, ocho pruebas y un
entregable que un tercero hostil puede reconstruir; las puertas las firma quien decide. Un validador guía, corrige lo
mecánico y aprende los ajustes de cada empresa.

**Evaluación de proyectos.** Estudios de perfil, prefactibilidad y factibilidad con preguntas, supuestos con fuente y
recomendación; evaluación económica privada (flujos del inversionista, con impuestos) o social (precios sociales y
tasa social), situación con y sin proyecto, alternativas, modelo en Excel con fórmulas (VAN, TIR, recuperación),
sensibilidad y escenarios; y revisión de la calidad de un estudio propio o de terceros según su etapa. Los hechos
externos del estudio entran por la investigación auditable.

**Postulaciones y evaluación de propuestas.** Preparar una postulación a un fondo (CORFO, ANID, regional, privado),
una oferta a una licitación o una respuesta a un RFP, desde las bases hasta la entrega: compuertas Go/No-Go, matriz
de cumplimiento con barrido exhaustivo de requisitos, pauta inversa, secciones trazables, presupuesto con controles,
red team y checklist de entrega. Y del otro lado de la mesa: pauta de evaluación, admisibilidad, evaluación
fundamentada de cada propuesta en contexto aislado, ranking y acta.

En todo: **tus formatos primero** (se adoptan tus plantillas y archivos base), **autoría limpia** de lo que se entrega,
**confidencialidad por diseño** (lo sensible nunca sale de tu computador) y evidencia de lo que se comprobó y de lo
que no.

## Cómo trabaja

- **Una carpeta = una empresa = un repositorio privado.** Para otra empresa, otra carpeta (`herramientas/nueva_empresa.py`);
  los datos de dos empresas nunca se mezclan. Un tablero único puede ver varias empresas sin copiar sus datos.
- **Tres capas.** El núcleo genérico (procedimientos, herramientas, reglas, arquetipos, plantillas) sirve para todo;
  `empresa/` guarda lo común de la empresa (identidad, marca, formatos, banco de antecedentes); `proyectos/<slug>/`
  guarda todo lo particular. Un proyecto combina arquetipos: `ejecucion`, `obra`, `agil`, `cartera`, `evaluacion`,
  `postulacion`, `programa`, `estudio`, `investigacion`, `finanzas`.
- **Reglas únicas, en un mapa.** `AGENTS.md` es un mapa de ~2.400 tokens: cada principio en una línea y el detalle en
  `reglas/`, que cada procedimiento carga cuando aplica. `CLAUDE.md` y `GEMINI.md` solo lo importan. Así todas las IA
  operan igual desde el primer mensaje, con un contexto fijo pequeño.
- **31 procedimientos (skills)** que se piden en lenguaje natural («haz la minuta», «cierra octubre», «investiga a
  quién…»); el índice está en `.claude/skills/LEEME.md`. **Subagentes** con un rol acotado (lector de documentos,
  revisor independiente, evaluador, red team, bibliotecario, refutador, árbitro, analistas), cada uno con el modelo
  que su nivel de capacidad exige; en las IA sin subagentes, el mismo rol se aplica en un paso separado.
- **Controles que no dependen de que la IA «se acuerde».** El control de Git (todas las IA) bloquea confidenciales y
  planillas mal formadas antes de cada commit y avisa si un proyecto cambia sin su traspaso; los hooks de Claude Code
  validan cada CSV o YAML al editarlo, entregan el estado al iniciar, avisan cuando una sesión lleva muchas acciones y
  no dejan cerrar con cambios sin guardar. Más de 370 pruebas automáticas y una revisión de integridad vigilan el núcleo.
- **El harness se observa.** Lo que el asistente tuvo que adivinar, lo que una skill no cubrió o un script que falló
  queda anotado y se exporta anonimizado para el mantenedor; un recolector de entropía propone qué retirar (nunca borra
  solo); el traspaso de cada proyecto dice qué se comprobó, qué no y dónde se adivinó.
- **Modo nube, opcional y solo con Claude Code:** tareas programadas con el PC apagado y una bandeja en GitHub para
  encargar y aprobar desde el celular; nada se programa sin tu sí, tarea por tarea (`NUBE.md`).
- **Actualizaciones que nunca pisan lo tuyo:** «actualiza el harness» trae la versión nueva con vista previa, respaldo,
  pruebas y reversión automática; fusiona tus permisos y completa `empresa/` sin tocar lo existente.

## Cómo obtenerlo

- **Opción simple (zip):** en esta página, botón verde **Code → Download ZIP**. Descomprímelo y sigue la
  [guía de inicio](EMPEZAR-AQUI.md).
- **Opción con Git:** `git clone https://github.com/gonzaloct1001-sudo/pmo-harness-nucleo.git <Nombre-de-tu-empresa>`.
  Al instalar, la copia se desconecta de este repositorio y se crea **tu propio repositorio privado**.
- **No uses «Fork»:** en GitHub, un fork de un repositorio público es **público**, y tus documentos quedarían a la vista.
- Este repositorio es **solo lectura** para todos excepto su dueño: nadie puede modificarlo, y tus datos nunca llegan
  aquí. Las mejoras se traen cuando tú quieras, con «actualiza el harness».

### Instrucciones para la IA que recibe solo este enlace
Si un usuario te pide «instala el PMO Harness desde este enlace»:
1. Pregunta (o propone) el nombre de su carpeta, idealmente el de su empresa, y dónde crearla (por defecto `Documentos`).
   Evita rutas muy largas, como carpetas profundas de OneDrive.
2. Descarga **sin Git** (puede no estar instalado aún):
   - Windows (PowerShell): `Invoke-WebRequest https://github.com/gonzaloct1001-sudo/pmo-harness-nucleo/archive/refs/heads/main.zip -OutFile harness.zip`
     y `Expand-Archive harness.zip -DestinationPath <temporal>`.
   - Mac: `curl -L -o harness.zip https://github.com/gonzaloct1001-sudo/pmo-harness-nucleo/archive/refs/heads/main.zip` y `unzip harness.zip -d <temporal>`.
3. Mueve **el contenido** de la subcarpeta `pmo-harness-nucleo-main/` a la carpeta del usuario: `AGENTS.md` debe quedar
   directamente dentro. Borra el zip y la carpeta temporal.
4. Pídele al usuario abrir esa carpeta en su editor (Archivo → Abrir carpeta) y escribir «hola». Si tu herramienta ya
   trabaja en esa carpeta, lee `AGENTS.md` y sigue su paso 0.

## Inicio rápido (tres pasos)

> Paso a paso y para cualquier usuario: [guía de inicio](EMPEZAR-AQUI.md). Si quieres que la instalación casi no te
> pregunte, completa antes `FICHA-DE-INICIO.md`.

1. **Preparar la carpeta.** Crea una carpeta con el nombre de tu empresa (por ejemplo `Consultora-Sur`) y descomprime
   el zip **directamente dentro**: `AGENTS.md`, `reglas/`, `herramientas/` y `.claude/` deben quedar en el primer nivel.
   Si quedó una subcarpeta intermedia, mueve su contenido un nivel arriba.
2. **Abrir e instalar.** Abre la carpeta en VS Code con tu asistente de IA y escribe **«hola»**: el asistente detecta
   que falta instalar y, con tu permiso, instala lo que falte (Python, Git, GitHub CLI y librerías), define la
   empresa, prepara Git y GitHub (siempre privado), se registra y te pregunta de qué se trata tu proyecto, en tus
   palabras. Con preguntas de opción (para quién es la carpeta, qué llevará primero, formatos propios, status
   semanal, modo nube) deja todo listo. **Recomendado antes de abrir la IA:** doble clic en `INSTALAR-WINDOWS.bat` o
   `INSTALAR-MAC.command`, que instala sin preguntas técnicas y nunca se queda detenido.
3. **Si tienes documentos: cargarlos y decir «listo».** Deja todo el material en `proyectos/<tu-proyecto>/_entrada/`
   (contratos, cronograma, reportes, plantillas, actas, correos, chats de otras IA, logos; sin ordenar ni renombrar;
   esa carpeta no se sube a GitHub) y escribe **listo**. El asistente hace el alta: inventario → lectura → decisiones →
   configuración → **un solo mensaje con las preguntas pendientes** → verificación → informe (`contexto/informe-de-alta.md`
   y `contexto/registro-de-alta.md`, con cada decisión, su fuente y su confianza). Si se interrumpe, «continúa el alta»
   retoma desde su punto de control. Si partes de cero, este paso no hace falta.

## Tipos de proyecto

No hay un catálogo cerrado: describes el proyecto y el asistente elige el arquetipo (o una combinación) y propone lo
propio del dominio.

| Proyecto | Arquetipo | Qué propone |
|---|---|---|
| Implementar un sistema para un cliente | ejecución (+ ágil si hay desarrollo) | Gantt, hitos, contrato, valor ganado, ruta crítica, reporte semanal |
| Construir una casa u obra | ejecución + obra | Partidas, RFI, inspecciones, no conformidades, estados de pago, informe de obra |
| Equipo de desarrollo de software | ágil | Backlog, sprints, velocidad, DORA, ADR, deuda técnica, trazabilidad |
| Programa con contrato general y varios subproyectos | programa + ejecución | Subproyectos con Gantt, riesgos y reportes propios; Gantt macro, presupuesto con contingencia, dotación, estado consolidado |
| Portafolio de acciones, granja de bots, cartera de iniciativas | cartera | Etapas con requisitos para avanzar, tesis por ítem, política como reglas, revisión periódica contra un índice |
| Prefactibilidad, factibilidad o evaluación económica | estudio | Preguntas, supuestos con fuente, modelo en Excel con VAN, TIR y sensibilidad, recomendación |
| Llevar el área de finanzas de una empresa | finanzas | Plan de cuentas, presupuesto, cierre mensual reabrible, resultados, balance y caja, forecast, proyección integrada, indicadores, directorio |
| Plan estratégico o de negocio a 3 o 5 años de una empresa o gerencia | estrategia (+ finanzas) | Diagnóstico con fuentes, lineamientos, objetivos con metas por año, iniciativas con impacto, plan financiero proyectado, documento al directorio, revisión trimestral con decisiones |
| Investigar a quién ofrecer una licencia, qué socios califican, el estado del arte, patentes o si algo es cierto | investigación (sola o junto a otro arquetipo) | Protocolo auditable: encuadre, hipótesis asesinas, expediente con marcas y niveles de fuente, refutador, árbitro, ocho pruebas, puertas que firma quien decide |
| Evaluar postulaciones o propuestas de terceros | evaluación | Pauta, admisibilidad, evaluación fundamentada por propuesta, ranking, acta |
| Postular a un fondo o presentar una oferta a una licitación | postulación | Go/No-Go, matriz de cumplimiento, pauta inversa, secciones trazables, presupuesto con controles, red team, checklist de entrega; perfiles de convocatorias en `biblioteca/perfiles/` |

## Probar antes con datos ficticios

`ejemplos/` trae un proyecto ficticio por capacidad, listo para probar sin tocar datos reales. Los recorridos, paso a
paso y en orden de relevancia, están en `ejemplos/LEEME.md`:

| Ejemplo | Qué muestra |
|---|---|
| `ejemplos/paquete-alta-andes/` | Alta de un proyecto desde una carpeta de documentos: «listo» y el proyecto configurado |
| `ejemplos/finanzas-demo/` | Finanzas de una distribuidora: estados, cierre, importación de un balance, proyección |
| `ejemplos/estrategia-demo/` | Plan estratégico 2027-2029 con cascada validada, roadmap y una revisión trimestral decidida |
| `ejemplos/investigacion-demo/` | Investigación cerrada con 0 errores; el validador detecta 24 de 24 mutaciones sembradas |
| `ejemplos/paquete-formatos-demo/` | Adopción de formatos propios: qué falta, qué se pierde, versión mejorada |
| `ejemplos/programa-demo/` | Programa con subproyectos, presupuesto macro y enmiendas |
| `ejemplos/portafolio-acciones/` | Cartera con etapas, tesis y script propio de rentabilidad y riesgo |
| `ejemplos/estudio-solar/` | Estudio económico con modelo en Excel, sensibilidad y escenarios |
| `ejemplos/equipo-software/` | Equipo ágil: sprints, velocidad, DORA, ADR |
| `ejemplos/fondo-innovacion/` | Evaluación de postulaciones con pauta y ranking |
| `ejemplos/postulacion-demo/` | Postulación a un fondo: matriz de cumplimiento, pauta inversa, red team |

## Requisitos
- [VS Code](https://code.visualstudio.com/) con un asistente de IA que trabaje sobre carpetas y ejecute comandos:
  **Claude Code**, **OpenAI Codex**, **Gemini** (CLI o Code Assist), **Google Antigravity**, **Cursor** o **GitHub
  Copilot** en modo agente. Un chat en el navegador no sirve: necesita leer la carpeta y ejecutar los scripts.
- Una cuenta de GitHub (el repositorio de cada empresa es siempre privado).
- Lo demás lo instala el harness **con tu permiso** (`instalar`, o doble clic en `INSTALAR-WINDOWS.bat` /
  `INSTALAR-MAC.command`): [Python 3.9+](https://www.python.org/downloads/), [Git](https://git-scm.com/downloads),
  [GitHub CLI](https://cli.github.com/) (opcional) y [LibreOffice](https://www.libreoffice.org/) (opcional: revisión
  visual y PDF). En Windows usa winget solo para el usuario, sin permisos de administrador; en Mac, Homebrew y `.venv/`.
- Opcional: extensión de VS Code **Markdown Preview Mermaid Support** (ver la carta Gantt) y, con Claude Code, las
  skills oficiales de documentos de Anthropic ([github.com/anthropics/skills](https://github.com/anthropics/skills)).

## Con qué IA funciona, y cómo cambiar de una a otra
- **Primera vez con una IA:** se configura sola (skill `configurar`, opción D): revisa qué archivo lee, activa los
  controles, hace una prueba rápida y queda registrada en `.harness/asistentes.yaml`.
- **Cambiar de IA a mitad de camino:** cada proyecto lleva un traspaso (`seguimiento/traspaso.md`) que se actualiza al
  cerrar cada tarea: qué se hizo, en qué quedó, el próximo paso, qué se comprobó y qué no. La IA nueva lo lee al empezar
  y retoma sin que repitas nada. Lo que no viaja es la conversación; los datos y el estado sí. Antes de cambiar, «guarda».
- **Controles:** los que protegen la información corren en Git antes de cada commit, con cualquier IA o sin IA. Claude
  Code agrega hooks y subagentes; en las demás, esos pasos los hace la IA según `AGENTS.md`.

## Varias empresas y varios computadores
- **Una carpeta por empresa**, cada una con su repositorio privado: `python herramientas/nueva_empresa.py "Empresa 2"
  --destino <carpeta>`. Los proyectos de cada empresa heredan su marca y sus formatos.
- **Otro computador:** el instalador de doble clic, después de conectar GitHub, ofrece descargar las empresas de la
  cuenta (`INSTALAR-WINDOWS.bat -Clonar` / `bash herramientas/preparar_pc.sh --clonar`), o pídele al asistente «es otro
  computador, trae mis empresas». Los originales de `_entrada/`, CVs y paquetes firmados no viajan por GitHub; las
  réplicas fieles, las fichas y todo lo configurado, sí. La carpeta no debe quedar dentro de Dropbox, OneDrive o Google
  Drive (dañan el historial de Git): el instalador y el estado de inicio lo advierten.
- **Mejoras del núcleo:** cada carpeta trae su copia del núcleo. «Actualiza el harness» (`herramientas/actualizar_nucleo.py`)
  trae la versión nueva desde el repositorio del núcleo o un zip, con vista previa, respaldo, pruebas y reversión si
  algo falla; si el núcleo nuevo trae un actualizador distinto, es ese el que actualiza.

## Status de todos los proyectos
- **Cada día**, al abrir la sesión, el asistente muestra en pocas líneas el status de los proyectos (semáforo, lo que
  vence pronto, decisiones que esperan, críticos previos). En cualquier momento: «¿cómo vamos?».
- **Reporte web:** «dame el reporte de status» genera una página (también Markdown, Excel o JSON) en `status/`, con
  historial; se puede dejar **cada semana** en el computador (`herramientas/agendar_status.py`).
- **Varias empresas:** un **tablero único** (`herramientas/status.py --crear-panel`) va en una carpeta y un repositorio
  privado aparte, solo del usuario: lee el status de cada empresa sin copiar sus datos.

## Tus formatos, primero
Si tu empresa ya tiene sus informes, minutas, presentaciones, cartas o planillas, deja los archivos en
`empresa/_entrada/` y di **«adopta mis formatos»**. El harness analiza cada uno y te dice, en simple, qué es, qué
sección le falta respecto de lo que él sabe llenar (y qué se pierde si se adopta tal cual), qué parte tuya no sabe
llenar solo, y te propone una versión mejorada que puedes aceptar o no. Lo adoptado pasa a ser el formato por defecto
(proyecto → empresa → harness); tus originales nunca se modifican. Los formatos de un cliente se adoptan igual, dentro
de su proyecto.

## Modo nube (opcional) y cambiar cosas después
Con Claude Code puedes activar el **modo nube**: tareas programadas que corren en la nube sobre tu repositorio privado
con el PC apagado (resumen de la mañana, trabajar la bandeja, status semanal, recordatorio de cierre) y una bandeja en
GitHub para encargar, responder y aprobar desde el celular. Nada se programa sin tu sí, tarea por tarea, y se pausa o
se quita cuando quieras. La nube trabaja en ramas propias y PR, nunca en `main` (`NUBE.md`); con tu sí, GitHub puede
exigirlo (`herramientas/bandeja.py --proteger-main`). Las otras IA operan solo en el PC.

Todo lo que decidiste al instalar se cambia conversando («quiero cambiar…», «configura…»): empresa, marca, formatos,
IA y modelos, umbrales, confidencialidad, modo nube, status semanal. Tus ajustes viven fuera del núcleo y ninguna
actualización los toca; todo queda en el historial y se puede deshacer.

## Uso diario (las frases más comunes; el resto, en el manual)

| Quiero… | Pídele al asistente |
|---|---|
| Empezar un proyecto | «Quiero llevar…» (de cero) o deja los documentos en `_entrada/` y di «listo» |
| Saber cómo vamos | «¿Cómo vamos?», «dame el reporte de status» |
| Un reporte | «Genera el reporte semanal», «arma la presentación para el comité» |
| Una reunión | «Prepara el comité del jueves»; después, pega tus notas: «haz la minuta» |
| Riesgos | «Registra un riesgo: …», «levanta los riesgos antes del hito» |
| Finanzas | «Arma el presupuesto», «cierra octubre», «¿por qué subió el gasto?», «proyecta a tres años» |
| Investigar | «Investiga a quién le podríamos ofrecer la licencia de X», «¿en qué va la investigación?», «firmo P2» |
| Evaluar un proyecto | «Arma el flujo de caja con estos supuestos», «¿qué pasa si la demanda cae 20 %?», «revisa este estudio» |
| Postular o evaluar propuestas | «Prepara la postulación», «¿cumplimos todo?», «evalúa las postulaciones y arma el acta» |
| Documentos | «Registra esta enmienda», «¿qué cambió entre la v3 y la v4?», pega un correo: «¿qué implica?» |
| Guardar, cambiar de IA, otro computador | «Guarda», «¿en qué íbamos?», «descarga mis empresas» |
| Mantener el harness | «Actualiza el harness», «¿qué mejoras al harness hay anotadas?», «revisa la salud del harness» |

## Personalización: dónde está cada cosa

| Qué quiero cambiar | Dónde |
|---|---|
| Marca, autoría, responsable, capacidad y formatos comunes de la empresa | `empresa/empresa.yaml`, `empresa/marca/`, `empresa/plantillas/`, `empresa/reportes/catalogo/` |
| Banco de antecedentes (CVs, certificados con vigencia) | `empresa/contenidos/` (los archivos no se suben a Git) |
| Qué documentos se replican en `fuentes/` | `replicas` en `empresa/empresa.yaml` (o en `proyecto.yaml`) |
| Datos, umbrales y reglas de un proyecto | `proyectos/<slug>/proyecto.yaml`, `metricas/`, `CLAUDE.md` del proyecto |
| Pauta de evaluación · supuestos del modelo económico · etapas de los ítems · flujo ágil | `evaluacion/pauta.yaml` · `estudio/modelo/supuestos-modelo.yaml` · `items/etapas.yaml` · `agil/estados.yaml` |
| Secciones de un reporte y sus plantillas | `proyectos/<slug>/reportes/catalogo/<tipo>.md`, `reportes/plantillas/` |
| Reglas para todas las IA | `AGENTS.md` (mapa) y `reglas/` (detalle); son núcleo y se reemplazan al actualizar: lo propio va al proyecto o a la empresa |
| Cómo decide el asistente en el alta y qué debe cubrir | `.claude/skills/nuevo-proyecto/references/reglas-de-decision.md` y `cobertura.md` |
| Valores por defecto para proyectos futuros · diseños reutilizables | `plantilla-proyecto/`, `arquetipos/` · `biblioteca/perfiles/` |
| Una skill propia | `.claude/skills/<nombre>/SKILL.md` (es tuya y no se borra al actualizar) |

## Robustez, autoría y confidencialidad
- **Subagentes** (`.claude/agents/`), **control de Git** (`.githooks/pre-commit`, se activa una vez por computador),
  **hooks de Claude Code** (`.claude/settings.json`) y **pruebas** (`pruebas/ejecutar_pruebas.py`, sobre copias de los
  ejemplos; `pruebas/escenarios-skills.md` para probar el comportamiento con cada IA). El mantenedor corre además
  `herramientas/integridad.py` antes de cada versión.
- **Autoría limpia:** lo que se entrega (Word, Excel, PowerPoint, PDF) sale a nombre del usuario y sin rastros del
  proceso; `herramientas/verificar_autoria.py` lo verifica. Si unas bases exigen declarar el uso de IA, es un requisito
  más: se registra, se avisa y la decisión es del usuario.
- **No se sube a GitHub:** `_entrada/` completa, originales contractuales, versiones originales, postulaciones de
  terceros, el banco de archivos y el paquete firmado. **Sí se sube**, al repositorio privado: lo configurado y las
  réplicas fieles de bases, contratos, actas e informes; de CVs y datos personales, solo la ficha. El control de Git
  bloquea lo confidencial aunque se pida por error. Lo que se exporta para el mantenedor sale anonimizado.
- El repositorio debe ser **privado**. Aun así, confirma que la política de la empresa y de sus clientes permite usar
  herramientas de IA y GitHub con su información.
- **Permisos:** `.claude/settings.json` deja a Claude Code ejecutar sin confirmar los scripts de `herramientas/`, las
  pruebas y los comandos básicos de Git; todo lo demás pide permiso. En otras IA, los permisos se configuran en la
  herramienta.

## Historial de versiones (completo en `CHANGELOG.md`)
- **3.4** — Análisis para decidir, sin instalar nada: simulación con rangos (probabilidad de una meta, tornado, qué
  supuesto pesa más), cinco modelos de negocio y fórmula propia (`simular.py`); rentabilidad por cliente y producto
  con mapa de cuadrantes (`rentabilidad.py`), con los clientes siempre por identificador y sus nombres solo en el
  computador; skill `analizar`.
- **3.3** — Planea, explica y recuerda: plan breve antes de las tareas grandes, ambiguas o difíciles de deshacer
  (`trabajo.modo`); skill `explicar` (página web de un solo archivo con cifras, gráficos, pasos y fechas); agenda del
  día en la primera interacción; documentos largos sobre la plantilla Word de la empresa; evals de comportamiento
  para quien mantiene el núcleo.
- **3.2** — Lo tuyo no se pisa y lo confidencial no sale: extensiones propias en `empresa/extensiones/` con pruebas
  que la actualización compara antes y después; la actualización conserva, renombra o fusiona lo propio en vez de
  reemplazarlo; controles de confidencialidad que miran el estado real (hook antes y después, control antes de subir),
  definición propia en `empresa/confidencialidad.yaml` y auditoría; primeras mejoras recibidas de una carpeta de empresa.
- **3.1** — Plan estratégico a 3 o 5 años (arquetipo `estrategia`, skill `plan-estrategico`, `estrategia.py`):
  diagnóstico con fuentes, cascada de objetivos, metas e iniciativas que cuadra, plan financiero sobre finanzas,
  revisión trimestral con decisiones.
- **3.0** — Mapa, no enciclopedia: `AGENTS.md` de 2.400 tokens con el detalle en `reglas/`; skills de 39 a 31 (nombres
  anteriores en el índice); contexto fijo real por sesión de 12.200 a 6.300 tokens; tres reglas mecánicas (traspaso,
  control de Git, `--proteger-main`); revisión de integridad. Una carpeta en 2.x se actualiza con un solo sí.
- **2.7** — El harness se observa: mejoras al núcleo anotadas y exportadas anonimizadas para el mantenedor, recolector
  de entropía, hooks de sesión larga y cierre, arranque comprobado, `investigar` en paralelo con `--consolidar`.
- **2.6** — Modo nube opcional, instalación por opciones, skill `configurar`, manual y guía rápida para usuarios no
  técnicos. Antes: 2.5 finanzas · 2.4 tus formatos primero · 2.3 investigación auditable y capacidad por tarea ·
  2.2 status diario y tablero único · 2.1 cualquier IA y una empresa por repositorio.
