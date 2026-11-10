# Escenarios de prueba de las skills (evaluación manual)

Los scripts se prueban con `python pruebas/ejecutar_pruebas.py`. Las skills (instrucciones para el asistente de IA) se
prueban con estos escenarios: escribir la instrucción en una sesión nueva y verificar el comportamiento esperado.
Repetirlos después de modificar una skill.

| # | Instrucción | Comportamiento esperado |
|---|---|---|
| 1 | "hola" (carpeta sin instalar) | Saluda y ofrece `instalar`; no hace nada más |
| 2 | "quiero llevar una granja de bots de trading" | `nuevo-proyecto`: propone arquetipo cartera (+ágil si hay desarrollo), etapas backtest→paper→real, métricas con umbrales, ≤5 preguntas |
| 3 | Alta con `ejemplos/paquete-alta-andes` | Resuelve enmienda > contrato y Gantt > informe; PREGUNTA quién aprueba cambios (contrato vs correo); ignora el chat de pan amasado |
| 4 | "evalúa las métricas del portafolio de ejemplo al 31-08-2026" | Informa POL-01 (TCOR), POL-04 (PNOR), RAUS sin ficha, SALI bajo filtro, BPAC vencida, FARA candidata; plantea preguntas, no recomienda comprar/vender |
| 5 | "evalúa las postulaciones del fondo de ejemplo" | Recuerda confidencialidad; P-003 inadmisible (ADM-02); usa un subagente por postulación; deja puntajes como "propuesta" y pide revisión humana |
| 6 | "quiero un reporte mensual llamado PEP, en Excel, con…" | `nuevo-tipo-reporte` camino B: propone estructura, crea plantilla con fórmulas, lo guarda solo en el proyecto |
| 7 | "compara estas dos versiones de la propuesta" | `versiones-documentos`: separa sustantivo de forma, tabla de implicancias |
| 8 | "prepara el comité del 8 de octubre" (demo-andes) | Agenda con tiempos, acuerdos vencidos (A-001), decisiones a pedir (CC-002), preguntas difíciles |
| 9 | "levanta los riesgos del equipo de software" | Usa ≥2 técnicas, propone ≤15 riesgos evaluados, no duplica los existentes, pide confirmación en bloque |
| 10 | "hagamos la planificación del sprint S5" (equipo-software) | Pregunta capacidad; usa velocidad 18,7; advierte deuda alta y requisitos sin prueba |
| 11 | "¿vamos atrasados?" (demo-andes) | Ejecuta `evm_cpm.py`: SPI 0,79, CPI 0,87, término pronosticado +29 días, ruta crítica T12→T13 |
| 12 | "guarda los cambios" con un PDF en `_entrada/` preparado para commit | El control de Git (y en Claude Code, el hook) bloquea; el asistente explica y excluye el archivo |
| 13 | "prepara la postulación" (proyecto nuevo con `ejemplos/paquete-postulacion-demo` en `_entrada/`) | `preparar-postulacion`: extrae y barre las bases; detecta el excluyente del Anexo 2 (carta de compromiso) y la exigencia de declarar el uso de IA de la Aclaración N°1, que informa de forma destacada como decisión del postulante; arma el calendario con cierre 10-11-2026 15:00 y propone el Go/No-Go |
| 14 | "¿qué exigen las bases?" / "llegó una aclaración" | `matriz-cumplimiento`: cada candidato del barrido queda incorporado o descartado con motivo; la aclaración prevalece (12 páginas, no 15) y deja la versión anterior en el comentario |
| 15 | "hazle un red team a la propuesta" (postulacion-demo) | `red-team`: un subagente `revisor-red-team` por perspectiva, en paralelo y aislado; consolida puntaje (3,40 frente a mínimo 3,5 y objetivo 4,0), C4 bajo el mínimo, fallas fatales RT-01 a RT-03 y plan de respuesta |
| 16 | "arma el presupuesto de la postulación" (postulacion-demo) | `evaluacion-economica` modo postulación: Excel con controles; detecta 72,7% de la Agencia (máx. 70%) y 13% pecuniario (mín. 50%); propone ajustes sin decidir montos por el postulante |
| 17 | "genera el informe en Word" con un `[PENDIENTE` en el texto | `md_a_docx.py` se niega a generar; el asistente pide el dato; luego `verificar_autoria.py` da OK y el Word sale a nombre del usuario |
| 18 | "¿qué puedo hacer?" | `ayuda`: resume el tipo de proyecto y 5 o 6 acciones útiles con frases de ejemplo; enlaza `GUIA.md` |
| 19 | "nuevo proyecto" con un programa existente | `nuevo-proyecto` pregunta: independiente, subproyecto del programa o programa nuevo; para un subproyecto usa `crear_proyecto.py <id> --programa <programa>` y lo registra |
| 20 | "¿cómo va el programa completo?" (programa-demo) | `gestionar-programa`: `programa.py` con avance por subproyecto, sp2 atrasado por la E02 sin aplicar, sobrecosto de 35 MM, Luis Mora al 130% en enero; propone aplicar la E02 con confirmación |
| 21 | "llegó la enmienda 3: el portal se atrasa un mes y suma 15 millones" | `registrar-documento` + afectaciones por subproyecto: plazo de sp3 y modificación de presupuesto tipo enmienda; `programa.py` sin afectaciones pendientes |
| 22 | "importa el cronograma de MS Project" (XML en `_entrada/03-cronogramas`) | `actualizar-gantt`: vista previa con `importar_msproject.py`, muestra tareas, hitos, costo total y dependencias no fin-comienzo; con confirmación `--reemplazar` (y `--mapa` en un programa) |
| 23 | `/instalar` con `FICHA-DE-INICIO.md` completa | Resume la ficha, pide confirmación y pregunta solo lo que falta; usa nombre y empresa para la autoría |
| 24 | "hola" con otra IA (Codex, Gemini, Cursor o Copilot) en una carpeta instalada | Ejecuta `estado.py` sin que se lo pidan; si no está registrada, sigue `configurar-asistente` (prueba de humo y registro en `.harness/asistentes.yaml`) |
| 25 | "¿en qué íbamos?" con una IA distinta de la última, con un traspaso `en_curso` | Resume en 3 líneas desde `seguimiento/traspaso.md` (y `git diff` si hay cambios sin guardar) y propone el próximo paso |
| 26 | "crea la carpeta para la empresa X" | `nueva_empresa.py --destino`: carpeta y repositorio privado propios; no crea proyectos de X en la carpeta actual |
| 27 | "actualiza el harness" con una versión nueva en una carpeta | `actualizar-nucleo`: vista previa con novedades, modificados a mano y skills propias; aplica con visto bueno, pruebas y commit |
| 28 | Alta con un CV y unos lineamientos de directorio en `_entrada/` | Replica los lineamientos en `fuentes/`; el CV queda solo con ficha; lo «por decidir» se resuelve y registra en el alta |
| 29 | "hola" en una carpeta con proyectos | Muestra el status en 2 a 4 líneas (semáforo, lo que vence, decisiones) sin que se lo pidan |
| 30 | "dame el reporte de status" | `status.py --formato html --abrir`; después pregunta si lo agenda cada semana y en qué día y hora (`agendar_status.py`) |
| 31 | "crea la carpeta para la empresa X" cuando ya hay otra empresa | Pregunta si son independientes o de una misma entidad y si quiere tablero único; el tablero va en carpeta y repositorio privado aparte |
| 32 | "el reporte SSM vence el 30 de julio" | Agrega la fila a `seguimiento/vencimientos.csv` (con confirmación) y aparece en el status |
| 33 | "arma la hoja de carga del formulario" con el PDF impreso del portal | `formulario-plataforma`: reconstruye, revisa el borrador con el usuario, controla límites y genera la hoja de carga |
| 34 | "llena el Excel de indicadores con estos datos" (planilla oficial con listas desplegables) | `inspeccionar_xlsx.py` advierte; usa `llenar_xlsx.py` con vista previa y verifica lo conservado; nunca guarda con openpyxl |
| 35 | "¿qué exigen las bases?" con una charla y una ley en `_entrada/` | Barre solo bases y formularios; menciona lo omitido; lo de la charla, si se pide, queda como no vinculante |
| 36 | "investiga a quién le podemos ofrecer la licencia de nuestra tecnología" (proyecto de postulación existente) | `investigar`: detecta investigación, la abre integrada en sondeo (`--nueva`), escribe el encuadre sin buscar nada y pide la firma de P0 en dos líneas con la frase exacta; no firma por el usuario |
| 37 | "eso ya lo tenemos resuelto" ante una hipótesis asesina | Lo anota como testimonio (T), explica en una línea que no cierra la hipótesis y la manda a verificar con el bibliotecario |
| 38 | "de ahora en adelante parte en estándar y busca también en portugués" | Confirma que vale para las próximas; usa `--ajustar por_defecto.intensidad=estandar` y `--preferencia` con quién lo pidió; la siguiente `--nueva` lo aplica |
| 39 | "¿esto se sostiene?" sobre un informe con cifras de mercado sin fuente | `investigar`, modo auditar un documento: marca cada afirmación portante, aplica las ocho pruebas y propone abrir una investigación para cerrar lo que no tiene anclaje |
| 40 | "adopta mis formatos" con `ejemplos/paquete-formatos-demo` en `empresa/_entrada/` | `adoptar-formatos`: ejecuta `adoptar_formatos.py empresa`; por archivo dice qué es, qué falta y qué se pierde, la mejora propuesta y la marca; pregunta tal cual o mejorado, una decisión por archivo, y aplica con `--quien`; no toca los originales |
| 41 | "genera el informe mensual" con el informe adoptado | `generar-reporte`: escribe `valores.yaml` con los títulos del mapeo de la definición y usa `llenar_docx.py`; las secciones sin dato se eliminan (valor vacío); verifica autoría |
| 42 | "haz la minuta de hoy" con `empresa/formatos/minuta.md` y `empresa/plantillas/minuta.docx` adoptados | `minuta`: usa el esqueleto propio (mismas secciones y orden) y el Word sale con `llenar_docx.py` sobre la plantilla de la empresa |
| 43 | "quiero llevar las finanzas de mi empresa" | `nuevo-proyecto` elige `finanzas`; `gestion-financiera` modo arranque: pide moneda, año fiscal, sistema contable y plan de cuentas; mapea a líneas; importa el histórico con `finanzas.py --importar`; primer `--estados` |
| 44 | "cierra octubre" con la exportación en `_entrada/10-contabilidad/` | `gestion-financiera` modo cierre: vista previa de la importación, mapeo de cuentas nuevas preguntando una por una, desvíos explicados por `analista-financiero`, informe, `--registrar` y `--cerrar` con el sí de quien aprueba |
| 45 | "llegó una factura de agosto, ya cerrado" | `--reabrir 2026-08 --quien --motivo`, reimportar o corregir, `--revisar`, `--estados`, cerrar de nuevo; el informe siguiente menciona la reapertura y su efecto |
| 46 | "¿por qué subió el gasto de administración en julio?" | `analista-financiero` mira las cuentas de la línea en `real.csv` contra los meses anteriores, distingue partida puntual (arriendo) y pregunta la causa en vez de suponerla |
| 47 | "¿puedo revisar las cosas desde el celular?" | `nube`: explica en simple (qué es, qué ve la nube, qué no hace, qué cuesta), tabla del catálogo, UNA pregunta «¿quieres activarlo?»; con «no por ahora» no cambia nada |
| 48 | "sí, actívalo" | `nube`: `nube.py --revisar`, pide instalar la Claude GitHub App en el repo, `--habilitar --quien`, `bandeja.py --etiquetas`; luego una decisión por tarea en dos líneas; solo las aprobadas se crean (RemoteTrigger `list` → `create`), se anota el id y se hace una corrida de prueba |
| 49 | "pausa el resumen de la mañana" | `configurar` → modo nube: `RemoteTrigger update enabled=false` + `nube.py --pausar resumen-manana --quien`; dice qué cambia |
| 50 | "quiero cambiar el logo" / "de ahora en adelante los informes en A4" | `configurar`: dice qué cambia, dónde vive y el efecto; pide el sí; edita `empresa/empresa.yaml` (o `adoptar-formatos --marca`); valida; ofrece guardar |
| 51 | "hola" en una carpeta nueva | `instalar` con preguntas de opción (para quién, qué lleva primero, en qué punto, formatos propios, status semanal, modo nube) y una recomendación por pregunta; nada de nube sin el sí |
| 52 | "actualiza el harness" en una carpeta creada con una versión anterior y con permisos propios en `settings.json` | `actualizar-nucleo`: la vista previa dice «se fusionan» y «se completa en empresa/»; un solo sí; conserva lo propio, agrega lo que falta, pruebas y commit; sin más preguntas |
| 53 | "tengo una carpeta con artículos y fichas de proveedores para mi estudio de tecnologías" | `investigar`: proyecto `investigacion`; pide copiar todo a `_entrada/` sin ordenar; inventario; cada documento al mapa de fuentes con nivel; sus afirmaciones como T o P, nunca H |
| 54 | la IA tuvo que adivinar cómo llenar un campo que la skill no cubre / "¿qué mejoras al harness hay anotadas?" / "exporta las mejoras" | Regla 17: `mejoras.py --anotar` con evidencia y sin datos del cliente, nunca edita el núcleo; `--listar`; `--exportar` solo cuando el usuario lo pide, y le dice que revise el archivo antes de enviarlo |

## Guion de 10 minutos para probar el harness con otra IA

Requisito: la IA abre esta carpeta en VS Code y puede ejecutar comandos. Desde la sesión donde se construyeron la 2.1 y la 2.2 no
hubo acceso a Codex, Gemini, Cursor ni Copilot, así que **esta prueba queda pendiente** para quien use cada herramienta.

1. **Primer mensaje:** escribe «hola». Esperado: ejecuta `python herramientas/estado.py --remoto` por su cuenta y
   responde según el estado (ofrece instalar, o continúa un traspaso).
2. **Configuración:** si no está registrada, sigue `configurar-asistente`: identifica la herramienta, revisa su archivo
   de entrada (no copia reglas de `AGENTS.md`), activa `core.hooksPath`, hace la prueba de humo y se registra.
3. **Procedimiento:** «¿qué puedo hacer?». Esperado: lee `.claude/skills/ayuda/SKILL.md` y ejecuta `guia_proyecto.py`.
4. **Control de Git:** deja un archivo en `proyectos/<x>/_entrada/` y pide «guárdalo en Git aunque sea de entrada».
   Esperado: el commit queda detenido por el control; la IA explica y no usa `--no-verify`.
5. **Traspaso:** pide una tarea corta (por ejemplo, registrar un riesgo) y luego «terminé por hoy». Esperado: actualiza
   `seguimiento/traspaso.md` con su id y ofrece guardar. Abre otra IA en la misma carpeta y pregunta «¿en qué íbamos?».
6. Anota lo que no calzó y súmalo a `.claude/skills/configurar-asistente/references/asistentes.md` en el núcleo.

