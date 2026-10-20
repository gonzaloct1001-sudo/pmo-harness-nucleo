# PMO Harness — reglas generales (para cualquier asistente de IA)

Marco de trabajo para diseñar, cargar y gestionar proyectos de cualquier tipo con un asistente de IA que trabaje
sobre carpetas y ejecute comandos: Claude Code, OpenAI Codex, Gemini (CLI o Code Assist), Google Antigravity, Cursor,
GitHub Copilot u otro. **Este archivo es la fuente única de reglas**: `CLAUDE.md`, `GEMINI.md` y cualquier otro archivo de entrada
solo remiten aquí. Si llegaste por otro archivo, sigue leyendo este completo.

Responde siempre en español (Chile), con tono profesional, directo y sin tecnicismos innecesarios.

## Al iniciar cada sesión (paso 0, siempre)

1. **Estado.** Ejecuta `python herramientas/estado.py --remoto` y usa su bloque `[Estado del PMO Harness]`. Si tu
   herramienta ya lo entregó al abrir la sesión (Claude Code lo hace con un hook), no lo repitas.
   Comando de Python: `python`; en Windows, si no responde, `py`; en Mac, `.venv/bin/python` (la crea el instalador;
   el `python3` del sistema no tiene las librerías).
   Si ninguno funciona, Python no está instalado: ofrece el instalador (`INSTALAR-WINDOWS.bat` o
   `INSTALAR-MAC.command`, o la skill `instalar`, que puede ejecutarlo por ti con permiso del usuario).
2. **Identidad.** Si el estado indica que tu asistente no está registrado en `.harness/asistentes.yaml`, sigue
   `.claude/skills/configurar-asistente/SKILL.md` antes de la primera tarea (toma un par de minutos y no pregunta
   casi nada). Si eres un asistente distinto del último que trabajó (campo `asistente` de los traspasos), aplica
   su sección «Cambio de asistente a mitad de camino».
3. **Dónde estamos.** Si el estado trae «Status de los proyectos», muéstraselo al usuario en 2 a 4 líneas junto al
   saludo: rojos y amarillos con su motivo, lo que vence pronto y las decisiones pendientes. El detalle y el reporte
   web, con la skill `status`.
4. Según el estado:
   - **No instalado** (no existe `.harness/estado.yaml`): sea cual sea el primer mensaje del usuario (incluso un
     saludo), respóndelo brevemente y ofrece comenzar con la skill `instalar`. Menciona que puede completar antes
     `FICHA-DE-INICIO.md` (o que la usarás si ya la completó) y que el manual está en `MANUAL-DE-USUARIO.md`.
   - **Traspaso pendiente:** si un proyecto tiene una tarea en curso o un próximo paso, menciónalo en una línea y
     ofrece continuar.
   - **Material sin procesar** en `_entrada/` o un **alta a medio camino** (`_entrada/_procesado/avance-alta.md`):
     menciónalo en una línea y ofrece continuar.
   - **Instalado sin proyectos:** ofrece crear uno (`nuevo-proyecto`) o cargar documentos (`alta-proyecto`),
     preguntando si parte de cero, está en marcha con documentos o está en marcha sin documentos.
   - **Controles de Git inactivos:** ofrece activarlos (`git config core.hooksPath .githooks`).
   - **Commits en GitHub que no están en este computador:** ofrece `git pull` antes de trabajar.
5. Si nada de lo anterior aplica, atiende directamente lo que pida el usuario.

## Organización

**El núcleo se publica en un repositorio público** (la URL está en la primera línea de `NUCLEO.txt`): cualquiera lo
descarga, pero solo su dueño puede modificarlo. Quien lo descarga (zip) o lo clona, lo instala como **su** carpeta de
empresa con **su** repositorio privado: `instalar` desconecta la copia clonada del núcleo antes de crear el privado.
**Nunca uses «Fork» en GitHub para esto:** un fork de un repositorio público es público y dejaría los datos a la vista.
La carpeta donde el dueño mantiene el núcleo está marcada (`git config pmo.mantenedor true`) y no lleva empresas ni proyectos.

Una carpeta del harness es un repositorio privado y pertenece a **una empresa** (o a una persona). Para otra
empresa se crea otra carpeta con `herramientas/nueva_empresa.py`. **Nunca mezcles datos de dos empresas.** Si el
usuario lleva varias empresas, **pregúntale** si son independientes o parte de una misma entidad, y si quiere llevarlas
separadas o juntas y un **tablero único** de status o uno por empresa: la estructura sigue su forma de gestionar. Cada
empresa tiene su status en su carpeta; un tablero único va en una **carpeta de panel con su propio repositorio
privado**, independiente de los de las empresas (skill `status`).

1. **Núcleo genérico** — sirve para cualquier proyecto. No se escribe nada específico de un proyecto aquí.
   `.claude/skills/` procedimientos (skills) · `.claude/agents/` roles (subagentes) · `herramientas/` scripts ·
   `.githooks/` controles de Git · `plantilla-proyecto/`, `plantilla-subproyecto/`, `plantilla-empresa/` bases.
   `NUCLEO.txt` lista las rutas del núcleo: se reemplazan al actualizarlo (`actualizar_nucleo.py`); todo lo demás
   es de la empresa y nunca se toca al actualizar.
2. **Arquetipos** — `arquetipos/<nombre>/`: estructura y guía de cada forma de trabajo.
   `ejecucion` (plan, hitos, contrato, valor ganado, ruta crítica) · `obra` (complemento de ejecución: RFI, no
   conformidades, inspecciones, estados de pago) · `agil` (backlog, sprints, DORA, ADR, deuda, trazabilidad) ·
   `cartera` (muchos ítems con etapas y métricas) · `evaluacion` (evaluar propuestas de terceros con pauta) ·
   `postulacion` (preparar y presentar una propuesta para ganar un fondo, licitación o concurso: matriz de
   cumplimiento, pauta inversa, red team, presupuesto con controles) · `programa` (contrato padre con varios
   subproyectos: presupuesto macro y por subproyecto, contingencia, personas compartidas, Gantt macro y por
   subproyecto, enmiendas que afectan subproyectos) · `estudio` (preguntas, supuestos, modelo económico,
   recomendación). Un proyecto puede combinar arquetipos.
3. **Empresa** — `empresa/`: lo común a todos los proyectos de la empresa dueña de la carpeta: `empresa.yaml`
   (identidad, autoría, marca, formato, política de réplicas), banco de antecedentes (`contenidos/`: descripción,
   experiencia, CVs, certificados con vigencia), `estilo.md`, `marca/`, `plantillas/` y formatos de reportes
   comunes (`reportes/catalogo/`). Los proyectos heredan de aquí lo que no definen.
4. **Proyecto** — `proyectos/<slug>/`: todo lo particular (datos, métricas, reglas, reportes con nombre propio,
   plantillas, marca, scripts de cálculo del dominio).

Además:
- `biblioteca/perfiles/` → diseños reutilizables. Incluye perfiles de convocatorias: `fondo-corfo`, `fondo-anid`,
  `licitacion-mercado-publico`, `fondo-regional-o-sectorial`, `licitacion-privada-rfp` (siempre se confirman contra las bases).
- `ejemplos/` → material ficticio de prueba (`demo-andes`, `paquete-alta-andes`, `portafolio-acciones`,
  `fondo-innovacion`, `estudio-solar`, `equipo-software`, `paquete-postulacion-demo`, `postulacion-demo`, `programa-demo`).
  No son proyectos reales.
- `.harness/estado.yaml` → registro de la instalación (empresa, origen del núcleo) · `.harness/asistentes.yaml` →
  asistentes de IA configurados · `pruebas/` → batería de pruebas.

## Contrato común (todos los proyectos)
- `proyecto.yaml` → identidad, `arquetipos`, gobierno, formato, umbrales, estado del alta.
- `metricas/metricas.yaml` (propias) y `metricas/metricas-<arquetipo>.yaml` (de los arquetipos) → definiciones
  y reglas · `metricas/mediciones.csv` → valores.
- `reportes/catalogo/` → reportes del proyecto · `riesgos/` · `seguimiento/` (decisiones, acuerdos, traspaso) · `contexto/`.
- `fuentes/` → réplicas fieles en Markdown de las bases y documentos de definición (ver regla 6): permiten trabajar
  en cualquier computador sin los originales.
Gracias a esto, reportes, consistencia, riesgos y reuniones funcionan igual en cualquier tipo de proyecto.

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

## Principios de trabajo

1. **La fuente de verdad son los datos del proyecto** (`.yaml`, `.csv`, `.md`). Word, Excel y PowerPoint son salidas.
2. **Nunca inventes datos.** Si falta algo, escribe `[PENDIENTE: qué falta]` y avísalo al final.
3. **Distingue hechos de estimaciones.** Marca como "estimado" lo que no venga de una fuente.
4. **Pide confirmación antes de modificar registros** (riesgos, cronograma, línea base, cambios, ítems),
   salvo en `alta-proyecto` y `nuevo-proyecto`, que aplican y registran sus decisiones para revisión en bloque.
5. **Fechas:** en archivos de datos `AAAA-MM-DD`; en documentos de salida, el formato de `proyecto.yaml`.
   **Porcentajes** en datos como fracción (0,15 = 15%).
6. **Confidencialidad:** `_entrada/`, originales contractuales, versiones originales de documentos, postulaciones de
   terceros, el banco de archivos (`contenidos/archivos/`) y el paquete firmado (`entrega/final/`) no se suben a Git
   (`.gitignore`, el control de Git y, en Claude Code, el hook `proteger_confidenciales` lo resguardan).
   **Réplicas:** de las bases y documentos de definición (bases, anexos, aclaraciones, lineamientos, contratos,
   actas, informes) se guarda una réplica fiel en `fuentes/`, que sí se sube al repositorio privado. De CVs, estados
   financieros y datos personales solo queda la ficha. La política está en `replicas` de `empresa/empresa.yaml`.
7. **Registros CSV:** conserva columnas y su orden (se pueden agregar columnas al final). UTF-8, coma.
8. **Lo específico va al proyecto (o a la empresa):** nombres de reportes, métricas del dominio, políticas y
   cálculos propios se guardan en `proyectos/<slug>/` o, si son comunes a todos los proyectos, en `empresa/`;
   nunca en el núcleo ni en los arquetipos.
9. **Decisiones sensibles** (inversiones, técnicas, legales, de salud): el harness organiza, mide y plantea
   preguntas; la decisión es del usuario y de los profesionales competentes.
10. Al terminar una tarea que modificó archivos, actualiza el traspaso (regla 17) y sugiere `guardar-cambios`.
11. **Si un control bloquea o reporta un problema** (hook de tu herramienta o control de Git), corrígelo antes de
    seguir; no lo esquives (nunca uses `git commit --no-verify`).
12. **Al modificar el núcleo** (skills, herramientas, arquetipos, plantillas) ejecuta `python pruebas/ejecutar_pruebas.py`
    y no des el cambio por terminado si alguna prueba falla.
13. **Autoría limpia de los entregables.** Todo documento que se entrega (Word, Excel, PowerPoint, PDF, Markdown de
    salida) sale a nombre del usuario (`autoria.nombre` o `responsable.nombre`) y sin rastros del proceso:
    - en el texto, nunca menciones el proceso de elaboración (asistentes, "generado automáticamente", el harness,
      nombres de skills o scripts, rutas del repositorio, ids internos) ni dejes marcadores `[PENDIENTE`. Hablar de IA
      cuando es el **tema** del proyecto es legítimo (se permite con `autoria.terminos_permitidos`);
    - **excepción:** las declaraciones que exijan unas bases o un contrato (regla 14) se redactan con veracidad y el
      archivo se lista en `autoria.excluir`, igual que los documentos de terceros (cartas, certificados);
    - sigue `contexto/estilo.md` del proyecto (o `empresa/estilo.md`);
    - antes de entregar, `python herramientas/verificar_autoria.py <archivo> --proyecto proyectos/<slug>` debe dar OK
      (con `--corregir` limpia propiedades, partes heredadas y caracteres invisibles).
    Los archivos internos del harness (registros, informes de alta, definiciones, réplicas) no están sujetos a esta regla.
14. **Integridad.** Si unas bases, un contrato o una norma exigen declarar el uso de herramientas de IA, o lo
    restringen, es un requisito más: se registra, se avisa al usuario de forma destacada y la decisión es suya.
    Nunca se redacta una declaración falsa ni se oculta algo que se deba declarar.
15. **Commits:** mensajes en español, descriptivos, sin líneas de coautoría ni menciones a herramientas de IA.
16. **Valida cada CSV o YAML que edites.** Claude Code lo hace solo (hook). En otras herramientas ejecuta después de
    editar `python herramientas/hooks/precommit.py --archivos <ruta>`; además, el control de Git lo revisa todo
    antes de cada commit.
17. **Traspaso entre sesiones y asistentes.** Al terminar cada tarea que cambió algo, y en cada hito de una tarea
    larga, actualiza `proyectos/<slug>/seguimiento/traspaso.md`: fecha, asistente, tarea en curso y su estado, qué
    se hizo, próximo paso, decisiones pendientes del usuario y archivos clave. Reemplaza el contenido (el historial
    queda en Git). Así otra sesión, otro computador u otro asistente retoma sin que el usuario repita nada.
18. **Tu consola no es interactiva.** No ejecutes comandos que esperen una respuesta (S/N, términos que aceptar,
    contraseñas, un editor): quedan detenidos y el usuario no puede contestar. Para instalar usa solo
    `herramientas/preparar_pc.ps1` o `preparar_pc.sh` (nunca winget, choco ni brew directos); para Git, usa `-m` y
    nunca `-i`. Si algo queda esperando, detenlo y ofrece el instalador de doble clic (`INSTALAR-WINDOWS.bat` o
    `INSTALAR-MAC.command`), que abre una ventana donde el usuario sí puede responder.

## Modo por defecto
Si el alta del proyecto está incompleta (`induccion.estado` distinto de `completa`), trabaja igual con
los valores por defecto. Menciona una sola vez, al final, qué pendientes críticos afectan el resultado.

## Procedimientos (skills)

Cada procedimiento está en `.claude/skills/<nombre>/SKILL.md` (la carpeta se llama `.claude` por compatibilidad;
sirve para cualquier asistente). En Claude Code se activan solos. **En otras herramientas, cuando el pedido del
usuario calce con una fila, lee ese SKILL.md completo y síguelo paso a paso**, aunque el usuario no lo nombre.
Si un SKILL.md menciona un subagente o un hook, usa las equivalencias de la sección siguiente.
**Skills propias de la empresa:** las carpetas de `.claude/skills/` que no están en esta tabla también valen (el
estado de inicio las lista): lee su SKILL.md cuando su descripción calce con el pedido. Esta tabla es del núcleo y se
reemplaza al actualizarlo; las skills propias no.

| Procedimiento | Para qué (frases típicas del usuario) | Archivo |
|---|---|---|
| `instalar` | Primer paso: prepara carpeta, computador y GitHub, y encamina el primer proyecto («instala», «empecemos», «computador nuevo») | `.claude/skills/instalar/SKILL.md` |
| `configurar-asistente` | Deja lista una IA nueva o distinta para operar igual que las demás («voy a usar Gemini», «cambié de IA») | `.claude/skills/configurar-asistente/SKILL.md` |
| `actualizar-nucleo` | Trae la última versión del núcleo sin tocar los datos de la empresa («actualiza el harness») | `.claude/skills/actualizar-nucleo/SKILL.md` |
| `nuevo-proyecto` | Diseña y crea un proyecto de cualquier tipo desde una descripción y una mini entrevista («quiero postular a…») | `.claude/skills/nuevo-proyecto/SKILL.md` |
| `alta-proyecto` | Carga documentos existentes: lee todo, configura, registra decisiones y pregunta lo mínimo («listo», «procesa la entrada») | `.claude/skills/alta-proyecto/SKILL.md` |
| `metricas` | Agregar métricas y reglas, cargar o importar datos, evaluar semáforos («quiero medir también…») | `.claude/skills/metricas/SKILL.md` |
| `gestionar-items` | Ítems de una cartera: agregar, mover de etapa, fichas, retirar, pipeline | `.claude/skills/gestionar-items/SKILL.md` |
| `nuevo-tipo-reporte` | Crear un reporte propio, desde un modelo o por conversación («este Word es la plantilla del informe») | `.claude/skills/nuevo-tipo-reporte/SKILL.md` |
| `generar-reporte` | Generar cualquier reporte del catálogo («prepara el informe de avance», «arma la presentación») | `.claude/skills/generar-reporte/SKILL.md` |
| `minuta` | Convertir notas de reunión en minuta con acuerdos y decisiones («estas son mis notas del comité») | `.claude/skills/minuta/SKILL.md` |
| `preparar-reunion` | Agenda, estado, decisiones a pedir y preguntas difíciles («tengo comité el jueves») | `.claude/skills/preparar-reunion/SKILL.md` |
| `riesgos-issues` | Registrar, actualizar y revisar riesgos y problemas | `.claude/skills/riesgos-issues/SKILL.md` |
| `levantar-riesgos` | Identificar sistemáticamente riesgos nuevos (checklist, premortem, supuestos) | `.claude/skills/levantar-riesgos/SKILL.md` |
| `actualizar-gantt` | Actualizar avance y fechas del cronograma; importar MS Project | `.claude/skills/actualizar-gantt/SKILL.md` |
| `registrar-documento` | Incorporar contratos, anexos, enmiendas y propuestas | `.claude/skills/registrar-documento/SKILL.md` |
| `versiones-documentos` | Comparar documentos o versiones y llevar la bitácora («¿qué cambió en las bases?») | `.claude/skills/versiones-documentos/SKILL.md` |
| `control-cambios` | Gestionar solicitudes de cambio y su impacto | `.claude/skills/control-cambios/SKILL.md` |
| `consistencia` | Detectar contradicciones e incumplimientos en todo el proyecto («¿cuadra todo?») | `.claude/skills/consistencia/SKILL.md` |
| `revisar-documento` | Analizar correos, informes o documentos recibidos («mira este correo», «¿qué implica?») | `.claude/skills/revisar-documento/SKILL.md` |
| `definir-pauta` | Pauta de evaluación desde las bases (también la pauta inversa del postulante) | `.claude/skills/definir-pauta/SKILL.md` |
| `evaluar-propuestas` | Admisibilidad, evaluación con evidencia, ranking y comparación de propuestas de terceros | `.claude/skills/evaluar-propuestas/SKILL.md` |
| `evaluacion-economica` | Flujo de caja en Excel con fórmulas: VAN, TIR, recuperación y sensibilidad; presupuesto de postulación | `.claude/skills/evaluacion-economica/SKILL.md` |
| `revisar-estudio` | Revisar calidad y completitud de un estudio según su etapa | `.claude/skills/revisar-estudio/SKILL.md` |
| `gestionar-sprint` | Planificación, seguimiento, revisión y retrospectiva de sprints; backlog e importación | `.claude/skills/gestionar-sprint/SKILL.md` |
| `registro-ingenieria` | ADR, deuda técnica, trazabilidad, despliegues (DORA), postmortems | `.claude/skills/registro-ingenieria/SKILL.md` |
| `registros-obra` | RFI, no conformidades, inspecciones, estados de pago, libro de obra, valor ganado | `.claude/skills/registros-obra/SKILL.md` |
| `preparar-postulacion` | Preparar y presentar una postulación, oferta o propuesta para ganar: flujo con compuertas («prepara la postulación») | `.claude/skills/preparar-postulacion/SKILL.md` |
| `matriz-cumplimiento` | Todos los requisitos de las bases (barrido exhaustivo), dueños, evidencia y checklist de entrega | `.claude/skills/matriz-cumplimiento/SKILL.md` |
| `red-team` | Panel de revisores con perspectivas distintas: puntaje estimado, fallas fatales y plan de respuesta | `.claude/skills/red-team/SKILL.md` |
| `gestionar-programa` | Programa con subproyectos: personas, presupuesto y contingencia, enmiendas, estado consolidado | `.claude/skills/gestionar-programa/SKILL.md` |
| `status` | Status de todos los proyectos (semáforos, lo que vence, decisiones), reporte web semanal y tablero de varias empresas («¿cómo vamos?») | `.claude/skills/status/SKILL.md` |
| `formulario-plataforma` | Formulario de una plataforma sin documento descargable: reconstruirlo, controlar límites, Word de trabajo y hoja para copiar y pegar | `.claude/skills/formulario-plataforma/SKILL.md` |
| `ayuda` | Qué puede hacer el harness en el proyecto activo, con frases de ejemplo («¿qué puedo hacer?») | `.claude/skills/ayuda/SKILL.md` |
| `guardar-cambios` | Guardar y subir el trabajo a GitHub («guarda», «terminé por hoy») | `.claude/skills/guardar-cambios/SKILL.md` |

## Roles (subagentes) y equivalencias por herramienta

Roles en `.claude/agents/`: `lector-documental` (lee lotes de documentos y devuelve hechos con fuente) ·
`revisor-independiente` (revisa con ojo crítico antes de entregar) · `evaluador-propuestas` (evalúa una propuesta
por vez contra la pauta) · `analista-datos` (procesa y revisa datos sin modificarlos) · `revisor-red-team` (una
perspectiva del red team por vez).

- **Con subagentes** (Claude Code): invócalos como dice cada SKILL.md.
- **Sin subagentes:** aplica el rol tú mismo en un paso separado: lee su `.md`, adopta solo esa perspectiva, lee
  solo los archivos que el rol indica y escribe su resultado antes de seguir. Para evaluaciones y red team, haz una
  propuesta o perspectiva por vez y no mires los resultados de las otras hasta consolidar.
- **Controles:** en Claude Code corren los hooks de `.claude/settings.json`. En todas las herramientas corre el
  control de Git (`.githooks/pre-commit`), que bloquea commits con archivos confidenciales o planillas mal formadas.
  Si tu herramienta no tiene hooks, el paso 0 y la regla 16 los haces tú.
- Detalle por herramienta (qué archivo lee, qué soporta): `.claude/skills/configurar-asistente/references/asistentes.md`.

## Herramientas (`python`, o `py` en Windows; `.venv/bin/python` en Mac)
- `estado.py [--remoto]` → estado al iniciar: instalación, empresa, asistentes, controles, proyectos, traspasos, material pendiente y status breve.
- `status.py [--breve] [--formato html,md,xlsx,json] [--abrir] [--panel carpeta] [--crear-panel carpeta --empresas ...]` → status de gestión.
- `agendar_status.py --dia lunes --hora 09:00 [--panel carpeta] | --ver | --quitar` → reporte web semanal agendado en este computador.
- `formulario.py <proyecto> [--reconstruir archivos] [--limpiar] [--word] [--hoja-carga]` → formulario de una plataforma de postulación.
- `llenar_xlsx.py <planilla> --valores valores.yaml [--vista-previa]` → llena planillas oficiales sin borrar listas, formas ni fórmulas.
- `crear_proyecto.py <slug> --arquetipos a,b [--nombre N] [--perfil ruta]` → crea o amplía un proyecto (hereda de `empresa/`).
- `crear_proyecto.py <id> --programa <programa>` → crea un subproyecto dentro de un programa.
- `nueva_empresa.py "<Nombre>" --destino <carpeta> [--sin-github]` → carpeta y repositorio privado nuevos para otra empresa.
- `actualizar_nucleo.py [--desde url|carpeta] [--aplicar]` → trae la última versión del núcleo sin tocar los datos.
- `preparar_pc.ps1` (Windows) / `preparar_pc.sh` (Mac) → revisa e instala con permiso Python, Git, GitHub CLI y LibreOffice.
- `verificar_entorno.py` → diagnóstico del computador y del repositorio.
- `hooks/precommit.py [--archivos rutas]` → control de confidenciales y validación de CSV/YAML (lo usa Git antes de cada commit).
- `evaluar_metricas.py <ruta-proyecto>` → métricas, semáforos, reglas, requisitos de etapa, fichas vencidas.
- `validar_proyecto.py <ruta-proyecto> [--corte-actualizacion]` → cronograma, riesgos, acuerdos, cambios, registros de obra, pendientes.
- `evm_cpm.py <ruta-proyecto> [--registrar]` → valor ganado, ruta crítica y término pronosticado.
- `metricas_agil.py <ruta-proyecto>` → velocidad, burndown, trabajo en curso, DORA, deuda, trazabilidad.
- `importar_backlog.py <ruta-proyecto> --desde github|csv` → trae el backlog desde GitHub o Jira.
- `importar_msproject.py <archivo.xml> <ruta-proyecto> [--mapa "Rama=sp1"] [--reemplazar] [--linea-base]` → cronograma desde MS Project (XML).
- `puntaje_pauta.py <ruta-proyecto>` → admisibilidad, puntajes ponderados, umbrales, ranking y presupuesto.
- `extraer_requisitos.py <ruta-proyecto> [--categorias ...|--todo]` → barrido de bases y formularios: candidatos a requisito con fuente (incremental).
- `postulacion.py <ruta-proyecto> [--registrar]` → etapa y compuerta, cumplimiento, vencimientos, red team, controles y autoría.
- `presupuesto_postulacion.py <presupuesto.yaml>` → Excel del presupuesto con fórmulas, fuentes y controles contra las bases.
- `guia_proyecto.py <ruta-proyecto> | --general` → guía del usuario (`GUIA.md`).
- `programa.py <ruta-programa> [--excel] [--registrar]` → estado consolidado del programa, presupuesto, personas, enmiendas y Gantt macro.
- `modelo_economico.py <supuestos.yaml>` → Excel con flujo de caja, VAN, TIR y sensibilidad (con fórmulas).
- `comparar_documentos.py <anterior> <nuevo>` → diferencias entre documentos, destacando las sustantivas.
- `extraer_entrada.py <ruta-proyecto> [--origen carpeta]` → inventario, texto y réplicas en `fuentes/` (incremental).
- `md_a_docx.py <entrada.md> <salida.docx> --proyecto <ruta> [--borrador]` → Word con la marca y autoría del proyecto.
- `verificar_autoria.py <archivo|carpeta> --proyecto <ruta> [--corregir]` → revisa que un entregable no tenga rastros del proceso.
- `inspeccionar_xlsx.py <archivo.xlsx>` → estructura de un Excel (hojas, fórmulas, celdas de entrada) y si se puede guardar con openpyxl.
- `gantt_mermaid.py <ruta-proyecto>` → `cronograma/gantt.md` para visualizar la carta Gantt.
- `pruebas/ejecutar_pruebas.py` → batería de pruebas del harness (ver también `pruebas/escenarios-skills.md`).

Dependencias: `pip install -r requirements.txt` (en Mac, dentro de `.venv`, que crea el instalador).
