# Cambios

## 3.3.0 — 2026-11-11

### Planea
- **Plan antes de ejecutar, en proporción (principio 23).** Una tarea chica y reversible se ejecuta; una grande,
  ambigua o difícil de deshacer parte con un plan de hasta cinco líneas (qué entendí, qué voy a hacer, qué voy a
  tocar, qué necesito) y tres salidas: «ejecuta», «ajusta» o «plan detallado». Vale como la confirmación del
  principio 4. Configurable por empresa en `trabajo.modo` de `empresa.yaml` (`proporcional`, `siempre`, `directo`); el
  estado de inicio avisa cuando no es el de fábrica. Detalle en `reglas/trabajo.md`.

### Explica
- **Skill `explicar` y `herramientas/explicar.py`**: una página web de un solo archivo desde un Markdown con bloques
  `cifras`, `grafico` (barras, columnas, líneas, tornado, histograma con probabilidad de cumplir una meta), `pasos` y
  `tiempo`. Sin internet ni recursos externos, en claro y oscuro, imprimible. Cada gráfico trae su tabla de datos,
  responde al cursor y al teclado, y usa una paleta comprobada para daltonismo; la herramienta rechaza lo que se lee
  mal (más de cuatro series, una sola barra) y dice qué corregir. Sirve también para el «plan detallado».

### Recuerda
- **Agenda del día (07a9bc-M-002)**: `herramientas/agenda.py` lista lo vencido, lo de hoy, lo que viene en 14 días
  (hitos, acuerdos, problemas, vencimientos, riesgos por revisar, cierres de postulación) y los reportes que tocan
  hoy y aún no se emiten, de todos los proyectos y subproyectos. En Claude Code llega sola en la primera interacción
  del día (hook `agenda_diaria.py`, una vez por día y por computador); en otras herramientas, `agenda.py --una-vez`.
  Nuevos campos opcionales: `proyecto.estado` (un proyecto `pausado` no aparece) y `dia` en la definición de un
  reporte (día de la semana, números del mes o `ultimo`; también se lee `programacion`).

### Documentos largos con la plantilla de la empresa (07a9bc-M-001)
- **`md_a_docx.py --plantilla`** (o `formato.plantilla_word` en `proyecto.yaml` o `empresa.yaml`): el Markdown se arma
  dentro de la plantilla Word oficial. Bloque inicial con título, código, versión, fecha y revisiones; marcadores
  `{{…}}` en portada, tablas, encabezados y pies; la fila de la historia de revisiones se repite; `{{indice}}` pasa a
  ser una tabla de contenido de Word; el cuerpo usa los estilos y la numeración de la plantilla; `![pie](ruta.png)`
  inserta la figura con «Figura N»; «Anexos» parte en página nueva. Sin plantilla, todo sigue igual. Al abrir un
  documento con índice, Word pregunta si actualiza los campos: se responde «Sí» (la herramienta lo avisa al generar). Ejemplo en
  `ejemplos/documento-largo-demo/`.
- **`llenar_docx.py`**: reemplazar un marcador ya no borra una imagen que comparte su párrafo (el logo de un
  encabezado), y cada fragmento conserva su formato.

### Para quien mantiene el núcleo
- **Evals de comportamiento** (`pruebas/evals/`): diez escenarios que le entregan un pedido real al asistente en una
  empresa de prueba y revisan qué respondió y qué tocó (plan ante una tarea grande, confirmación antes de registrar,
  no inventar, no subir confidenciales, no editar el núcleo, agenda, página visual, extensiones). Cada escenario
  consume cuota del asistente, así que no corren con la batería: `python pruebas/evals/ejecutar_evals.py`. La batería
  prueba el evaluador con un asistente de mentira.

### Al actualizar a esta versión
- Se agrega a `empresa/empresa.yaml` el bloque `trabajo` (modo `proporcional`). `formato.plantilla_word`,
  `proyecto.estado` y `dia` son opcionales: se escriben cuando se usan.
- Probado por el camino real desde una carpeta en 3.2.0 con skill propia, extensión con pruebas, líneas propias en
  `.gitignore` y archivos del núcleo modificados. Ese recorrido mostró que la batería, dentro de una empresa, llevaba a
  su copia de trabajo la sección propia de `.gitignore`: ahora la deja fuera, y la fusión por líneas nunca produce dos
  secciones propias.
- Batería: 462 pruebas.

## 3.2.0 — 2026-11-11

### Lo tuyo no se pisa
- **Extensiones propias (`empresa/extensiones/`)**: el lugar oficial para las herramientas, hooks y pruebas que una
  empresa le agrega al harness (su `LEEME.md` explica cómo). Ninguna actualización las toca. La batería ejecuta las
  pruebas propias (`empresa/extensiones/pruebas*.py`, `empresa/pruebas/*.py`) y las lista como «propia: …»; la
  actualización las ejecuta antes y después y **se revierte sola si una que pasaba deja de pasar**. El estado de
  inicio anuncia las extensiones.
- **La actualización nunca pisa lo propio en silencio** (`actualizar_nucleo.py`). La vista previa parte por «Lo tuyo
  en esta actualización»:
  - algo propio que se llama igual que algo nuevo del núcleo **queda entero con otro nombre** (`<nombre>-propia` para
    una skill, `<nombre>-propio.<ext>` para un archivo) y lo del núcleo entra con el nombre original; antes se
    sobrescribía y aparecía como un archivo «cambiado» más;
  - un archivo del núcleo modificado en la carpeta **se conserva si el núcleo nuevo no lo cambia**; antes se revertía
    en cada actualización;
  - `.gitignore` y `requirements.txt` **se fusionan** como ya lo hacía `.claude/settings.json` (lo propio queda bajo
    una marca); antes se reemplazaban, y una carpeta que la empresa había dejado fuera de Git volvía a quedar expuesta;
  - la fusión de `settings.json` conserva también los hooks y permisos propios que apuntan a archivos propios dentro
    de `herramientas/`;
  - lo modificado que el núcleo nuevo también cambia se respalda y se reemplaza como antes, pero queda nombrado al
    terminar y anotado como recordatorio en `mejoras.py` (suele ser un arreglo que el núcleo debería traer).
- **El catastro a la vista** (`.harness/nucleo-instalado.csv`, que ya existía y solo se consultaba al actualizar):
  `actualizar_nucleo.py --verificar` dice, sin internet, qué archivos del núcleo se modificaron en la carpeta, cuáles
  faltan y cuáles son propios; `--restaurar <archivo>` devuelve uno cambiado o borrado por error a su original
  instalado (comprobado por su huella, desde el historial de Git de la carpeta o desde `--desde`) y deja lo que había
  en el respaldo. El estado de inicio avisa si falta un archivo del núcleo o si alguno cambió en los últimos 7 días.
- **Un `settings.json` que no es JSON válido** ya no aparece como «se fusiona»: la vista previa dice que no se puede
  fusionar, que se reemplaza con respaldo, y que basta corregirlo antes de aplicar.
- **La batería y la revisión de integridad prueban el núcleo, no lo propio.** Dentro de una carpeta de empresa ya no
  consideran las skills, hooks y archivos propios que viven en carpetas del núcleo. Antes, una sola skill propia hacía
  fallar dos pruebas y, con eso, **toda actualización se revertía**. Si la batería falla al actualizar, el mensaje
  nombra las pruebas que fallaron y los archivos del núcleo modificados aquí que podrían explicarlo.
- **El núcleo no se edita en una carpeta de empresa**: hook `proteger_nucleo` (Claude Code, antes de Edit/Write) que
  detiene la edición de un archivo del núcleo y encamina a `empresa/extensiones/`, a una skill propia, a
  `empresa/estilo.md` o a `mejoras.py --anotar`. No aplica donde se mantiene el núcleo, ni a lo propio que vive dentro
  de carpetas del núcleo, ni a los tres archivos que se fusionan.

### Lo confidencial no sale
- **Los controles miran el estado real, no el texto del comando.** El hook anterior interpretaba el comando y dejaba
  pasar un `git add` con la ruta entre comillas, precedido de `cd`, con `git -C` o `git --no-pager`, en dos líneas o
  con la salida recortada. Ahora: antes del comando bloquea saltarse el control (`--no-verify`, `git commit -n`,
  cambiar o quitar `core.hooksPath`), `git init` junto con `git add` o `git commit`, y guardar o subir con el control
  de Git inactivo; simula cada `git add` respetando comillas, `cd` y opciones globales; y **después del comando** saca
  del staging lo confidencial y avisa si el último commit sin subir se llevó algo.
- **Control antes de subir** (`.githooks/pre-push`): revisa todos los commits que aún no están en el remoto; uno con
  confidenciales (hecho sin control, en otro computador o con otra herramienta) no sale. Se activa con el mismo
  `git config core.hooksPath .githooks`.
- **Definición propia: `empresa/confidencialidad.yaml`** (`nunca_subir`, `binarios_sueltos`, `carpetas_de_binarios`,
  `claves_en_texto`), que leen todos los controles y ninguna actualización toca. Tres niveles documentados en
  `reglas/confidencialidad.md`: se versiona, réplica fiel, solo ficha.
- **`herramientas/confidencialidad.py`**: qué se protege y si los controles están activos; `--agregar "<carpeta/ o
  patrón>" --quien` (lo anota en el YAML y en la sección propia de `.gitignore`); `--auditar` (confidenciales
  versionados o en el historial, claves pegadas en textos, binarios fuera de lugar).
- **Aviso de Word, Excel, PDF e imágenes nuevos fuera de las carpetas de salida**: el commit lo dice y sigue (la
  empresa puede pedir `bloquear` o `permitir`). Una **clave o llave pegada en un texto** detiene el commit.

### Mejoras recibidas de una carpeta de empresa (primer envío, origen 07a9bc)
- **07a9bc-M-003**: `importar_msproject.py` acepta decimales con coma (Project Plan 365).
- **07a9bc-M-004** y **07a9bc-M-005**: el hook de confidencialidad ya no depende de cómo esté escrito el comando.
- **07a9bc-M-006**: `verificar_entorno.py` ve todos los asistentes registrados.
- **07a9bc-M-007**: la exportación de mejoras anonimiza también nombres cortos, siglas y el nombre de la carpeta, como
  palabra completa (también dentro de nombres de archivo); el archivo y el mensaje aclaran que se envía solo la
  exportación, no el registro `.harness/mejoras-nucleo.csv`.
- **07a9bc-M-008**: la batería ejecuta las pruebas propias de la empresa.
- 07a9bc-M-001 (Word largo con plantilla de la empresa) y 07a9bc-M-002 (agenda diaria) quedan aceptadas para la 3.3.0.

### Al actualizar a esta versión
- El actualizador se renueva solo, así que estas protecciones rigen desde esta misma actualización. Se agregan a
  `empresa/` el archivo `confidencialidad.yaml` y `extensiones/LEEME.md` (nada existente cambia).
- Si habías agregado carpetas a `.gitignore` para que no se subieran, quedan bajo la marca «Propio de esta carpeta»;
  conviene definirlas además con `confidencialidad.py --agregar`, para que también las detengan los controles.
- Probado por el camino real: una carpeta creada con la 3.1.0 publicada, con skill propia, extensión con pruebas,
  líneas propias en `.gitignore` y archivos del núcleo modificados, actualiza sin preguntas y conserva todo.
- Batería: 435 pruebas (más las propias de cada empresa). Dos pruebas dependían del entorno y se corrigieron: una
  pasaba solo si la plantilla de proyecto se había tocado en las últimas tres horas; otra tomaba la primera fila de
  `MEJORAS.md`, que ahora trae filas reales.

## 3.1.0 — 2026-11-10

### Plan estratégico (3YP / 5YP)
- **Arquetipo `estrategia`**: diagnóstico con fuentes (`estrategia/diagnostico.md`), lineamientos, cascada de
  objetivos → indicadores con línea base y meta por cada año del horizonte → iniciativas con responsable, fechas,
  inversión e impacto (`objetivos.csv`, `metas.csv`, `iniciativas.csv`), revisiones por período con decisión
  (`revisiones.csv`); bloque `estrategia` en `proyecto.yaml` (horizonte 3 o 5, año de inicio, marco OKR/BSC/propio,
  cadencia, quién aprueba, proyecto de finanzas asociado); métricas del plan; reportes `plan-estrategico` y
  `revision-trimestral`.
- **`herramientas/estrategia.py`**: estado y siguiente paso, `--revisar` (la cascada cuadra: cada objetivo activo
  con meta en todos los años, iniciativas y revisiones que apuntan a objetivos existentes, rojo sin decisión = error),
  `--revision AAAA-Tn` (arma la revisión del período y toma los reales de `metricas/mediciones.csv` cuando el
  indicador es una métrica), `--roadmap` (Gantt Mermaid), `--registrar`.
- **Skill `plan-estrategico`** con referencias de diagnóstico, cascada, plan financiero (las iniciativas se vuelven
  supuestos de `finanzas/proyeccion.yaml` a 3 o 5 años) y revisión (mantener, ajustar meta, reasignar, descartar).
- Ejemplo `ejemplos/estrategia-demo/` (plan 2027-2029 ficticio con una revisión decidida) y prueba 12.

## 3.0.0 — 2026-11-10

### Mapa, no enciclopedia
Versión mayor porque cambia dónde viven las reglas y cómo se llaman las skills. Una carpeta en 2.x se actualiza con
un solo sí (`actualizar_nucleo.py` retira las skills viejas que no se tocaron, respalda las modificadas, fusiona
`settings.json` y completa `empresa/`); los nombres anteriores están en la tabla «Nombres anteriores» del índice.
- **`AGENTS.md` es un mapa** de ~2.400 tokens (antes 5.100): arranque, organización, proyecto activo, los 22
  principios en una línea cada uno (conservan su número), modo por defecto, nube, procedimientos, roles y
  herramientas. El detalle de cada principio vive en **`reglas/`** (`datos`, `trabajo`, `confidencialidad`,
  `entregables`, `nucleo`, `organizacion`) y cada SKILL.md dice qué reglas carga («Reglas que aplican»). Nada crítico
  deja de cargarse: la esencia de cada regla sigue en el mapa; lo que se mueve es la elaboración.
- **Skills: de 39 a 31.** `nuevo-proyecto` absorbe `alta-proyecto` (dos caminos: desde la descripción o con documentos,
  `references/alta.md`); `configurar` absorbe `configurar-asistente` (opción D, `references/asistente.md`);
  `reuniones` = `preparar-reunion` + `minuta`; `riesgos` = `riesgos-issues` + `levantar-riesgos`; `reportes` =
  `generar-reporte` + `nuevo-tipo-reporte`; `documentos` = `registrar-documento` + `versiones-documentos`;
  `evaluar-propuestas` absorbe `definir-pauta` (paso 1); `preparar-postulacion` absorbe `matriz-cumplimiento`.
  Las descripciones de skills bajan a 60 palabras o menos y las de subagentes a 45: son lo que toda sesión carga.
- **Contexto fijo real por sesión: de ~12.200 a ~6.300 tokens** (mapa 2.400 + puerta 300 + descripciones de skills
  2.900 + subagentes 700). Techos impuestos por la batería: `medir_contexto.py --techo` 2.800 para el texto fijo,
  `entropia.py --techo` 7.000 para el contexto real.
- **Tres reglas que dejan de ser solo texto:** `validar_proyecto.py` avisa si el traspaso no tiene sus apartados de
  evidencia o lleva días sin tocarse mientras los datos cambiaron; el control de Git (todas las IA) avisa cuando un
  proyecto cambia y su traspaso no va en el commit; `bandeja.py --proteger-main` hace que GitHub exija PR para
  `main`, también a la nube (solo con el sí del usuario; en privados de plan gratuito no está disponible).
- **`herramientas/integridad.py`**: todo contra todo antes de publicar (rutas citadas que no existen, skills y
  subagentes, índice, catálogo, `NUCLEO.txt`, hooks, herramientas, nombres viejos, compilación). Corre en la batería.
- Guías de los ejemplos regeneradas con los nombres nuevos.

## 2.7.0 — 2026-11-10

### El harness se observa
- **Mejoras al núcleo** (`herramientas/mejoras.py`, registro `.harness/mejoras-nucleo.csv`): en una carpeta de empresa
  nadie edita el núcleo; lo que falta, sobra, estorba o falla se anota con su versión, dónde, qué, por qué y evidencia.
  Anotan solos el actualizador (cuando revierte) y la batería (cuando falla en una empresa); el asistente anota por la
  regla 17 cuando tuvo que adivinar o una skill no cubrió el caso. `--exportar` produce un archivo **anonimizado**
  (sin nombres de empresa, personas, proyectos, correos, RUT ni montos) que el usuario revisa y entrega; el
  mantenedor lo incorpora a `MEJORAS.md` con `--procesar` y decide con `--decidir`; al actualizar, la carpeta cierra
  lo resuelto (`--cerrar-resueltas`). El estado de inicio avisa cuántas hay sin enviar; `configurar` (M) y
  `guardar-cambios` lo recuerdan.
- `traspaso.md` con tres apartados nuevos: *Comprobado*, *No se pudo comprobar* y *Tuve que adivinar* (regla 17).
- **Recolector de entropía** (`herramientas/entropia.py`): mide el contexto fijo **real** por sesión (AGENTS.md, puerta
  y las descripciones de todas las skills y subagentes, que se cargan aunque no se usen) contra un presupuesto que la
  batería impone; encuentra instrucciones repetidas entre README, MANUAL, EMPEZAR-AQUI, GUIA y NUBE, lecciones de
  empresa de más de 180 días sin confirmar, `[PENDIENTE` de más de 30 días, respaldos acumulados, mejoras sin enviar y
  skills sin uso. Propone; nunca borra. El estado de inicio lo recuerda a los 30 días; `configurar` (N).
- **Frenos al contexto, en Claude Code** (hooks nuevos; se activan pegando sus líneas en `.claude/settings.json`):
  `sesion_larga.py` avisa a las 120 acciones (la calidad baja entre el 20 y el 40 % de la ventana), `cierre_sesion.py`
  no deja terminar con cambios sin guardar y traspaso viejo, `registrar_uso.py` anota qué skill se usó. Para las demás
  IA, la regla está en `asistentes.md` («Sesiones largas»).
- **Arranque comprobado:** el estado de inicio dice cuántos críticos de validación tenía cada proyecto antes de que el
  asistente tocara nada (no se los atribuye a su último cambio) y la batería verifica que `CLAUDE.md` y `GEMINI.md`
  importan `AGENTS.md`.
- **`investigar` en paralelo:** el líder delega con objetivo, salida, fuentes, límites y presupuesto por intensidad
  (sondeo 1 bibliotecario y hasta 10 búsquedas; estándar 2 a 4 en paralelo por familia de fuentes, 10 a 15 cada uno;
  forense sin tope); cada bibliotecario escribe en sus archivos parciales con su rango de IDs y
  `investigacion.py --consolidar` los une sin pisarse; «amplio primero, luego acota». Lecciones del sistema de agentes
  de investigación de Anthropic.

## 2.6.1 — 2026-11-10

### Actualizar sin perder lo propio
- `actualizar_nucleo.py`: `.claude/settings.json` ya no se reemplaza: se **fusiona** (entran los permisos y hooks del
  núcleo nuevo; se conservan los permisos, hooks y claves que el usuario agregó). Y **completa `empresa/`** con lo que
  la plantilla nueva trae y la carpeta no tiene (por ejemplo `_entrada/`, `formatos/` y el bloque `capacidad` de
  `empresa.yaml`), sin cambiar nada existente. Probado el salto 2.2.4 → 2.6 en una carpeta real: una sola
  confirmación, 103 segundos, sin preguntas.
- El actualizador **se renueva solo**: si el núcleo nuevo trae un actualizador distinto, es ese el que actualiza la
  carpeta (las mejoras del actualizador valen desde esa actualización, no desde la siguiente). Una carpeta en 2.6.0 o
  anterior actualiza esta vez con su actualizador viejo: la skill `actualizar-nucleo` ejecuta una segunda pasada para
  completar `empresa/`, y los permisos propios que hubiera en `settings.json` quedan en el respaldo.
- Skill `investigar`: cómo entra el material que la persona ya tiene (`_entrada/` → mapa de fuentes con su nivel; lo
  que afirma, como T o P, nunca como H).
- Skill `nube`: `references/tarea-remota.md` con la forma comprobada de crear la tarea en la nube (primera corrida
  real: resumen diario publicado en el issue y aviso al teléfono).

## 2.6.0 — 2026-11-10

### Modo nube opcional, instalación por opciones y «configurar»
- **Modo nube (solo Claude Code, opcional):** tareas programadas que corren en la nube de Claude sobre el repositorio
  privado de la empresa, con el PC apagado, y una **bandeja** en GitHub para encargar, responder y aprobar desde el
  celular. Nada se programa sin el sí del usuario, tarea por tarea; se pausa o se quita cuando quiera. `NUBE.md` trae
  las reglas de una corrida (rama propia y PR, nunca `main`; una tarea a la vez; solo REST; sin tocar `settings`,
  `NUCLEO.txt` ni el registro) y el catálogo: resumen de la mañana, trabajar la bandeja, status semanal, recordatorio
  de cierre. `herramientas/nube.py` lleva el registro (`.harness/nube.yaml`: quién aprobó qué y cuándo) y el texto
  de cada tarea; `herramientas/bandeja.py` opera la bandeja por REST (`gh api`, probado con `pruebas/gh_falso.py`).
  Skill `nube` (explica, requisitos, una decisión por tarea, crea la tarea con la herramienta de la cuenta, corrida de
  prueba, uso desde el celular, pausar). El estado de inicio avisa el modo nube y la bandeja; `guardar-cambios` mira
  los PRs de la nube antes de empujar.
- **Instalación por opciones:** `instalar` pregunta con letras (para quién es la carpeta, qué va a llevar primero, en
  qué punto está, formatos propios, status semanal, modo nube) con una opción recomendada en cada una; todo se cambia
  después.
- **Skill `configurar`:** menú para cambiar cualquier configuración conversando y con confirmación (empresa, marca,
  formatos, IA y modelos, umbrales, confidencialidad, modo nube, status semanal, investigación, proyecto, idioma,
  reglas), con dónde vive cada cosa y cómo deshacer.
- Manual de usuario y guía rápida reescritos para usuarios no técnicos (`MANUAL-DE-USUARIO.md`, `EMPEZAR-AQUI.md`).

## 2.5.0 — 2026-11-10

### Finanzas: llevar el área como un controller (arquetipo `finanzas`)
- Nuevo arquetipo para gestionar las finanzas de una empresa en cualquier rubro y país: plan de cuentas mapeado a las
  líneas del reporte (`finanzas/lineas.yaml`, adaptable), importación del balance de comprobación o libro mayor desde
  cualquier contabilidad (detecta la fila de encabezados y las columnas; `--acumulado`, `--inicial`, `--mapa`),
  presupuesto por línea y mes con supuestos, escenarios y versiones, **cierre mensual que se puede reabrir** con quién
  y motivo (cada cierre guarda la huella de sus movimientos: si cambian, `--revisar` lo detecta), resultados mes y
  acumulado contra presupuesto y forecast, balance con cuadre, flujo de caja por método indirecto, indicadores (margen,
  EBITDA, caja y meses de caja, DSO, DPO, DIO, liquidez, endeudamiento, desvíos) con semáforos en el status
  (`metricas-finanzas.yaml`, reglas FIN-01 a FIN-06), forecast (presupuesto o tendencia) y **proyección integrada a
  varios años** (resultados, balance y caja cuadrados por construcción). Los Excel salen con fórmulas.
- Skill `gestion-financiera` con un modo por proceso (arranque, presupuesto, cierre, desvíos y forecast, proyección,
  directorio), subagente `analista-financiero` (sonnet), reportes `informe-financiero-mensual`, `presupuesto-anual`
  y `reporte-directorio` (usan los formatos de la empresa si están adoptados), `biblioteca/finanzas/` (plan de cuentas
  base, definiciones de indicadores, referencia por país: `paises/chile.md`, siempre a confirmar con el contador),
  `_entrada/10-contabilidad/` para las exportaciones (no se suben a Git).
- Principios: el harness consume la contabilidad, no la reemplaza; ninguna cifra se escribe a mano; cuadres antes que
  análisis; lo tributario y contable lo decide el contador. Ejemplo ficticio `ejemplos/finanzas-demo` y paquete
  `ejemplos/paquete-finanzas-demo` (exportación de octubre para probar la importación). `nuevo-proyecto` y
  `alta-proyecto` reconocen las señales; `actualizar_nucleo.py` revisa los proyectos de finanzas antes y después.

## 2.4.0 — 2026-11-10

### Tus formatos, primero
- **Skill `adoptar-formatos` y `herramientas/adoptar_formatos.py`:** la empresa deja sus formatos y archivos base en
  `empresa/_entrada/` (no se sube a Git) y el harness los analiza: qué es cada uno (informe de avance, minuta,
  presentación, carta, planilla de control, un reporte de un arquetipo, o un archivo base como un plan de cuentas),
  cuánto cubre del **contrato** de esa salida (`herramientas/formatos/contratos/`), **qué sección le falta y qué se
  pierde si se adopta tal cual**, qué sección propia el harness no sabe llenar solo, y qué marca trae (logo del
  encabezado, fuente, color). Propone una **versión mejorada** de cada Word (copia `_v2` con las secciones que faltan
  y marcadores) que el usuario acepta o no. Con `--aplicar --quien` deja la plantilla en `empresa/plantillas/`, la
  definición con el mapeo de secciones en `empresa/reportes/catalogo/`, el esqueleto de la minuta en
  `empresa/formatos/minuta.md`, los archivos base en `empresa/formatos/base/` y, con `--marca`, logo, fuente y color
  en `empresa.yaml` (solo si tenía los valores por defecto). Los originales nunca se modifican; nada de lo que existe
  se sobrescribe; todo queda en `empresa/formatos/registro.csv` con quién y cuándo. También sirve para los formatos
  de un cliente dentro de un proyecto (`adoptar_formatos.py proyectos/<slug>`).
- **`herramientas/llenar_docx.py`:** llena una plantilla Word propia sin cambiar su estructura: marcadores `{{...}}`
  (también en tablas, encabezados y pies) y secciones ubicadas por su título, con el estilo de párrafo y de viñeta que
  la plantilla usaba, tablas con semáforo, secciones vacías eliminadas; un `[PENDIENTE]` impide generar y la autoría
  queda limpia. `generar-reporte` lo usa para todo Word con plantilla; `minuta` usa el esqueleto y la plantilla de la
  empresa si existen.
- Regla 22 de `AGENTS.md` («lo tuyo primero»): proyecto → empresa → harness, para toda salida. El estado de inicio
  avisa los formatos dejados en `empresa/_entrada/` que aún no se adoptan; `alta-proyecto` y `nuevo-tipo-reporte`
  usan el análisis para las plantillas de un proyecto. Ejemplo ficticio `ejemplos/paquete-formatos-demo/`.

## 2.3.0 — 2026-11-09

### Investigación auditable (arquetipo `investigacion`)
- Nuevo arquetipo para cuando la respuesta depende de hechos del mundo que hay que verificar con fuentes, en cualquier
  área: a quién ofrecer una licencia o alianza, qué socios o proveedores califican, estado del arte, patentes, due
  diligence, normativa. Trae el **Protocolo de Investigación Auditable 1.1**: encuadre con la decisión y su negación,
  mapa de fuentes, hipótesis asesinas antes de construir, expediente con marcas (H, D, T, P, I, S, V) y niveles de
  fuente (N1 a N6), refutador en contexto estéril, árbitro, ocho pruebas de auditoría y seis puertas, tres de ellas
  firmadas por la persona que decide.
- **Tres formas de uso, a elección:** integrada en otro proyecto (por ejemplo, para sostener la sección de mercado de
  una postulación), como proyecto propio o aislada en otra carpeta de empresa. Cada investigación vive en
  `investigaciones/<AAAA-NN-nombre>/` y no usa hechos de otra (el validador lo controla).
- **Se activa sola cuando corresponde:** `nuevo-proyecto` y `alta-proyecto` reconocen las señales; una regla nueva
  de AGENTS.md (19) pide no escribir hechos del mundo de memoria y ofrecer el protocolo en cualquier proyecto;
  `preparar-postulacion` y `revisar-estudio` lo usan en las secciones que afirman hechos de afuera.
- **`herramientas/investigacion.py`:** dice el siguiente paso en palabras simples (qué hacer, qué leer, qué pedirle a
  la persona, con la frase exacta para firmar); valida todo lo verificable (marcas, fuentes, ID, puertas en orden,
  construir antes de matar, aislamiento); **corrige solo lo mecánico** con vista previa y lo deja anotado; corre las
  pruebas mecánicas de auditoría y la muestra al azar con semilla repetible; sube la intensidad.
- **Aprende de cada empresa:** `--ajustar`, `--preferencia` y `--aprender` guardan valores por defecto, preferencias
  de las personas y lecciones de método en `empresa/investigacion/`, con quién y cuándo. Las investigaciones nuevas
  los aplican. Ninguna actualización del núcleo toca esa carpeta. Las lecciones que valgan para todos se exportan sin
  datos del caso (`--exportar-lecciones`).
- Skill `investigar` (orquesta el flujo y explica cada firma en dos líneas), subagentes `bibliotecario`, `refutador`
  y `arbitro`, fichas de los siete roles, reporte `informe-investigacion`, cartuchos de dominio en
  `biblioteca/dominios/` (incluye `propiedad-industrial`; los propios de la empresa se conservan al actualizar) y
  ejemplo ficticio `ejemplos/investigacion-demo`.
- Arreglos sobre la versión 1.0 del protocolo: quién escribe las hipótesis asesinas, un solo momento para las ocho
  pruebas, registro de las seis puertas, «no buscado» separado de «buscado sin resultado», marca P para pistas,
  columna de origen para la independencia, numeración de archivos por etapa, intensidades precisas y fuente de
  verdad en los archivos (detalle en `arquetipos/investigacion/protocolo/PROTOCOLO.md`).
- Controles: el hook de edición y el control de Git validan los registros de investigación; el material descargado
  (`investigaciones/<id>/_crudo/`) no se sube a Git; el estado de inicio lista las investigaciones abiertas y quién
  debe firmar.

### Capacidad según la tarea y menos contexto
- Regla 20 de `AGENTS.md`: la capacidad se asigna por verificabilidad (alta, media, baja), no por costo. Los ocho
  subagentes declaran su modelo: lector-documental, analista-datos y bibliotecario (trabajo verificable) en `sonnet`;
  evaluador-propuestas, revisor-independiente, revisor-red-team, refutador y arbitro (juicio) en `opus`. Cada empresa
  puede cambiar el mapa en `empresa/empresa.yaml` (`capacidad`) sin tocar el núcleo. El nivel de cada skill está en
  `catalogo.yaml`; `asistentes.md` dice cómo se elige el modelo en Codex, Gemini, Antigravity, Cursor y Copilot.
- Regla 21: cuidar el contexto (no releer, resúmenes por script, lotes al lector-documental, references solo en su fase).
- `AGENTS.md` pesa un 28% menos (de ~6.900 a ~5.000 tokens): la lista completa de herramientas pasó a `herramientas/LEEME.md` y el índice de
  procedimientos con sus frases típicas a `.claude/skills/LEEME.md`; Claude Code no los necesita (las skills se activan
  solas) y las demás IA leen el índice al recibir el primer pedido. `herramientas/medir_contexto.py` mide la carga
  fija, cada skill y cada subagente; la batería exige que la carga fija no supere el techo.

### Corrección
- `actualizar_nucleo.py`: dos actualizaciones en el mismo segundo ya no comparten la carpeta de respaldo (la segunda
  usa `_2`, `_3`…); antes, revertir la segunda podía restaurar también lo de la primera.

## 2.2.4 — 2026-10-20

### Menos pasos en la instalación
- El instalador ya no pide nombre ni correo: la «firma» del historial de Git se toma de la cuenta de GitHub conectada
  (nombre o usuario, y el correo privado `id+usuario@users.noreply.github.com`, que asocia los cambios a la cuenta sin
  publicar el correo real). `preparar_pc.ps1 -IdentidadGitHub` / `preparar_pc.sh --identidad-github` lo hacen por
  separado; la ventana de conexión de GitHub también lo hace al terminar.
- Una sola pregunta para GitHub: «¿Ya tienes cuenta?». Con Enter se conecta; con N se abre el registro con los pasos
  en español y espera a que termine. Sin respuesta, queda para el chat.
- `instalar` no pide nombre ni correo: conecta GitHub y toma la firma de la cuenta; guía la creación de la cuenta.

## 2.2.3 — 2026-10-20

### Otro computador sin duplicar la empresa, y carpetas sincronizadas
- En una carpeta nueva, `instalar` pregunta primero si es la primera vez o si ya usa el harness en otro computador
  (y nombra las carpetas de empresa que ya tiene en GitHub). Antes, un «hola» en la carpeta del zip de un segundo
  computador empezaba una instalación nueva y podía duplicar la empresa.
- El instalador de doble clic, después de conectar GitHub, ofrece descargar las carpetas de empresa de la cuenta y
  dice cuál abrir. Al descargar, configura Git para usar la cuenta conectada.
- Aviso cuando la carpeta del harness está dentro de Dropbox, OneDrive, Google Drive o iCloud (estado de inicio e
  instaladores), con la ubicación recomendada. Las empresas descargadas quedan fuera de OneDrive aunque Documentos
  esté sincronizado.

## 2.2.2 — 2026-10-20

### Instalador que nunca se queda detenido
- **Windows sin permisos de administrador:** Python, Git y GitHub CLI se instalan solo para el usuario (winget
  `--scope user`), así que no aparece la ventana de permiso de Windows, que a veces queda escondida. Si winget falta o
  falla, se usa la descarga oficial (python.org y las versiones publicadas de Git y GitHub CLI).
- **Nada puede esperar una respuesta:** cada programa externo recibe una entrada vacía y tiene un tiempo máximo; las
  preguntas solo existen en la ventana del doble clic (abierta desde el Explorador), con tiempo máximo y respuesta por
  defecto. Ejecutado por un asistente de IA, el instalador nunca pregunta. Sin opciones, solo revisa.
- **Doble clic recomendado antes de abrir la IA:** instala lo necesario sin preguntas técnicas, pide nombre y correo, y
  conecta GitHub.
- **GitHub sin preguntas en inglés:** se abre el navegador en la página del código, que queda copiado; se pega,
  Continue y Authorize. Después configura Git para usar esa cuenta y desactiva las preguntas de GitHub CLI.
- `INSTALAR-WINDOWS.bat` llama al script con ruta relativa: algunos controles de seguridad detienen PowerShell si su
  línea de comando trae la ruta completa de la carpeta abierta en un editor con IA (se reprodujo en Windows 11).
- Las carpetas de empresa quedan con `core.pager cat` (`git log` o `git diff` no esperan una tecla en la consola del
  asistente). Lo opcional (LibreOffice, rutas largas) solo se instala si se pide, y avisa del permiso de Windows.
- Mac: mismas reglas (preguntas solo con doble clic y con tiempo máximo; Homebrew sin confirmaciones en inglés).
- Guía de inicio, manual, README e `instalar` actualizados; regla 18 de `AGENTS.md` ampliada (rutas relativas, sin
  paginador, el asistente no ejecuta los instaladores de doble clic).

## 2.2.1 — 2026-10-20

### Correcciones
- Instalación en Windows: un asistente que ejecutaba winget por su cuenta quedaba detenido esperando que se aceptaran
  los términos de Microsoft Store, en una consola donde el usuario no puede responder. `AGENTS.md` (regla 18) e
  `instalar` prohíben ahora los comandos que esperan respuesta y obligan a instalar solo con `preparar_pc`; si algo
  queda detenido, se ofrece el instalador de doble clic. `preparar_pc.ps1` agrega `--disable-interactivity` a winget.
- Guía de inicio y manual: qué hacer si la instalación se queda detenida y dónde aparece el permiso de Windows cuando
  no se ve la ventana.

## 2.2 — 2026-10-19

### Nuevo: status diario y reporte web
- `herramientas/status.py` (skill `status`): semáforo por proyecto con reglas fijas, a partir de los cálculos que ya hacen
  `postulacion.py`, `validar_proyecto.py` y `evaluar_metricas.py` (ahora con `--json`), el calendario de la postulación,
  los hitos, acuerdos, issues, el traspaso y los compromisos propios de `seguimiento/vencimientos.csv` (nuevo en la
  plantilla). Muestra lo que viene en 14 días, las decisiones que esperan al usuario y el pipeline de postulaciones.
- En el chat («¿cómo vamos?») y **al iniciar cada sesión** (`estado.py` agrega un resumen breve).
- Reporte en página web autocontenida (claro y oscuro), Markdown, Excel o JSON en `status/`; guarda un historial y
  compara con el status anterior (qué mejoró o empeoró).
- `herramientas/agendar_status.py`: deja el reporte listo cada semana, el día y la hora que elija el usuario (Tareas
  programadas en Windows, launchd en Mac); `--ver`, `--quitar` y `--simular`.
- **Tablero único** de varias empresas (`status.py --crear-panel` / `--panel`): en una carpeta y un repositorio privado
  aparte, solo del usuario; lee el status de cada empresa sin copiar sus datos. `instalar` pregunta, al sumar otra
  empresa, si son independientes o de una misma entidad y si prefiere un tablero por empresa o uno general.

### Nuevo: formulario de la plataforma de postulación
- `herramientas/formulario.py` (skill `formulario-plataforma`): reconstruye el formulario desde su versión impresa (PDF
  de Fondos.gob.cl u otro portal) o el Word de preguntas (instrucciones en color, contador «0 / 250»); controla límites
  de caracteres, campos obligatorios vacíos y caracteres que la plataforma podría rechazar (`--limpiar` quita los
  invisibles); genera el Word de trabajo y una **hoja de carga** HTML con un botón «Copiar» por campo.
- `postulacion.py` muestra el estado del formulario; la compuerta de entrega exige que ningún campo exceda su límite
  ni quede un obligatorio vacío.

### Nuevo: planillas oficiales sin pérdidas
- `herramientas/llenar_xlsx.py`: escribe valores directamente en el XML de la hoja y deja todo lo demás idéntico byte a
  byte (listas desplegables modernas, formas, tablas, formato condicional). Rechaza celdas con fórmula, hojas protegidas
  y celdas combinadas ocultas; verifica lo conservado al terminar. Guardar con openpyxl borra esos elementos.
- `inspeccionar_xlsx.py` advierte cuando una planilla no debe guardarse con openpyxl.

### Mejoras del barrido de requisitos
- Categorías por nombre: `normativa` (leyes, decretos, reglamentos), `charla` (charlas, capacitaciones,
  transcripciones) y `formulario` (formatos vacíos, fichas de postulación). Se replican, pero no se barren por defecto.
- `extraer_requisitos.py` barre por defecto solo bases y formularios (`--categorias`, `--todo`), informa lo omitido y
  marca como no vinculante lo que viene de una charla (columna nueva `vinculante`).
- Escaneos: `extraer_entrada.py` marca las réplicas sin texto (`ocr: pendiente`), indica cómo pasarlas por OCR y, si
  aparece la versión con texto (por ejemplo, en una subcarpeta `ocr/`), usa esa y descarta la otra.

### Correcciones
- «CV» en el nombre de un archivo ya no basta para tratarlo como currículum (es también la sigla de Crea y Valida de
  CORFO): sin datos personales en el contenido, se clasifica por lo que es. Un archivo sin texto con «CV» en el nombre
  sigue tratándose como currículum, por precaución.
- Las capturas de pantalla dentro de una carpeta de charla o video se clasifican como charla.
- Compatibilidad con Python 3.9 en los textos HTML de `formulario.py` y `status.py`.

## 2.1 — 2026-10-19

### Nuevo: funciona con cualquier asistente de IA
- `AGENTS.md` es la fuente única de reglas (antes en `CLAUDE.md`), con redacción neutra, paso 0 de cada sesión, tabla de
  procedimientos (frase del usuario → `SKILL.md`) y equivalencias para herramientas sin subagentes ni hooks.
  `CLAUDE.md` y `GEMINI.md` son puertas de entrada que la importan; Codex, Cursor y Copilot la leen directamente.
- Skill `configurar-asistente`: identifica la IA, crea solo la puerta de entrada que falte, activa los controles, hace una
  prueba de humo y la registra en `.harness/asistentes.yaml`; ante una IA desconocida, averigua y pregunta lo necesario.
- `herramientas/estado.py`: el estado de inicio para cualquier asistente (empresa, asistentes, controles, proyectos,
  traspasos, material pendiente, cambios sin guardar y, con `--remoto`, commits por bajar). El hook de inicio de Claude lo usa.
- **Traspaso:** `seguimiento/traspaso.md` en cada proyecto (tarea en curso, próximo paso, decisiones pendientes); se
  actualiza al cerrar cada tarea (regla 17) para que otra sesión, otro computador u otra IA retome sin repetir nada.

### Nuevo: controles en Git, con cualquier IA o sin IA
- `.githooks/pre-commit` → `herramientas/hooks/precommit.py`: bloquea commits con material confidencial (mismos
  patrones que el hook de Claude) o con réplicas marcadas sensibles, y valida CSV y YAML. `--archivos` valida archivos sueltos.
- `herramientas/py.sh`: encuentra Python (`.venv`, `python3`, `python` o `py -3`); lo usan los hooks de Claude y el de Git.
- Reglas compartidas en `herramientas/hooks/_comun.py` (confidenciales y validación).

### Nuevo: instalación automática, con permiso (Windows y Mac)
- `INSTALAR-WINDOWS.bat` / `herramientas/preparar_pc.ps1` (winget) e `INSTALAR-MAC.command` / `herramientas/preparar_pc.sh`
  (Homebrew, librerías en `.venv`): Python, Git, GitHub CLI, LibreOffice opcional, librerías, control de Git, identidad de
  Git, sesión de GitHub y, en Windows, rutas largas. Modo interactivo (doble clic) o con parámetros (la IA pregunta en el
  chat y lo ejecuta). Opción para descargar las carpetas de empresa en un computador nuevo. No instala VS Code.
- `instalar` usa el instalador, define la empresa de la carpeta, activa los controles y registra el asistente.

### Nuevo: una empresa = una carpeta = un repositorio privado
- `plantilla-empresa/` → `empresa/`: identidad, responsable, marca y formato, autoría, política de réplicas, banco común de
  antecedentes con vigencias, estilo, plantillas y formatos de reportes comunes.
- Herencia empresa → programa → subproyecto en `_config.py`; `crear_proyecto.py` deja los formatos para heredar, copia los
  formatos comunes y el estilo, y pone a la empresa como postulante. `postulacion.py` revisa también el banco común.
- `herramientas/nueva_empresa.py`: carpeta nueva con solo el núcleo, repositorio con el control activo y repositorio privado
  en GitHub con el tema `pmo-harness-empresa`; `--aqui` configura la empresa de la carpeta actual.
- `NUCLEO.txt` y `herramientas/actualizar_nucleo.py` (skill `actualizar-nucleo`): trae la versión nueva del núcleo sin tocar
  proyectos ni datos; vista previa, respaldo de lo modificado a mano, skills propias conservadas, pruebas y reversión si fallan.

### Nuevo: réplicas fieles en Markdown
- `extraer_entrada.py` deja en `fuentes/` el texto completo de bases, contratos, lineamientos, actas e informes (se sube
  al repositorio privado); CVs y estados financieros nunca (solo ficha); lo dudoso queda «por decidir» (`--replicar <id>`).
  Categorías nuevas: lineamientos, cv, financiero, certificado. `extraer_requisitos.py` usa las réplicas, así el barrido
  funciona en cualquier computador sin los originales.

### Nuevo: núcleo público, de solo lectura, para cualquier persona
- Repositorio público `pmo-harness-nucleo` (licencia MIT). La primera línea de `NUCLEO.txt` guarda su URL: es el origen
  por defecto de las actualizaciones.
- Una copia descargada (zip) o clonada se instala como carpeta de empresa con repositorio **privado** propio. Una copia
  clonada se desconecta sola del núcleo (`nueva_empresa.py --aqui`). El estado de inicio reconoce la copia clonada y
  advierte si una instalación quedó apuntando al núcleo público. `instalar` advierte sobre los forks, que son públicos.
- La carpeta del mantenedor (`git config pmo.mantenedor true`) no acepta empresas, proyectos ni `actualizar_nucleo.py`.
- Cuenta de GitHub para usuarios básicos: `instalar` abre la página de registro (cuenta personal gratuita) y la ventana
  de inicio de sesión (`preparar_pc.ps1 -IniciarGitHub` / `preparar_pc.sh --iniciar-github`).
- `actualizar_nucleo.py` revisa también los **proyectos reales** de la carpeta, antes y después de actualizar, y revierte
  si alguno deja de funcionar.
- Guía de inicio para usuarios básicos (`EMPEZAR-AQUI.md`), manual revisado e instrucciones en el README para la IA que
  recibe solo el enlace. Google Antigravity en la tabla de asistentes.

### Correcciones
- Rutas de más de 260 caracteres en Windows (copias del núcleo, actualización y batería de pruebas; `core.longpaths`).
- Saltos de línea estables para los scripts (`.gitattributes`); scripts marcados como ejecutables para Mac.

## 2.0 — 2026-09-30

### Nuevo: importación desde MS Project
- `herramientas/importar_msproject.py`: lee el XML de MS Project (Archivo > Guardar como > XML) con jerarquía, fechas
  plan y reales, % completado, hitos, dependencias (tipo y desfase), recursos asignados, costos (convertidos desde
  centavos) y línea base 0. Vista previa por defecto; `--reemplazar` con respaldo; `--linea-base`; en un programa,
  `--mapa` reparte cada rama a su subproyecto y deja las dependencias entre ramas como `sp1:T12`.
- Las dependencias comienzo-comienzo, fin-fin o comienzo-fin, y los desfases, se conservan en el comentario (las fechas
  de MS Project no cambian). Un `.mpp` recibe la instrucción de exportarlo a XML.
- `extraer_entrada.py` reconoce el XML de MS Project en la carga documental y lo resume como tabla de tareas.

### Nuevo: manual y ficha de inicio
- `MANUAL-DE-USUARIO.md`: instalación, qué te preguntará, alta, uso diario, programas, postulaciones, controles y
  preguntas frecuentes.
- `FICHA-DE-INICIO.md`: las preguntas de la instalación y el alta para completarlas antes; `instalar` y `nuevo-proyecto`
  la usan y solo preguntan lo que falte.

### Todo lo incorporado desde la 1.5

### Nuevo: arquetipo `postulacion` (el lado del oferente)
Para preparar y presentar propuestas que ganen fondos concursables (CORFO, ANID, regionales, privados),
licitaciones públicas (Mercado Público) o privadas, RFP y concursos.
- Flujo de 11 etapas con compuertas verificables (`postulacion/etapas.yaml`, modificable por proyecto): recepción de
  bases y calendario → Go/No-Go → matriz de cumplimiento, pauta inversa y consultas → estrategia (revisión azul) →
  redacción por secciones (revisión rosa) → presupuesto → riesgos e impacto → red team (revisión roja) → revisión oro,
  guante blanco y entrega → post-entrega → cierre y transición a `ejecucion` si se adjudica.
- `herramientas/extraer_requisitos.py`: barrido exhaustivo e incremental de bases, anexos, formularios y aclaraciones;
  clasifica candidatos (admisibilidad, técnico, económico, formal, declaración, evaluación), marca lenguaje de
  exclusión, extrae fechas, horas, montos y porcentajes, y alerta menciones a inteligencia artificial.
- `herramientas/postulacion.py`: etapa y compuertas, cumplimiento, excluyentes pendientes, vencimientos, consultas,
  trazabilidad de secciones, controles económicos, puntaje estimado del red team frente a mínimo y objetivo,
  fallas fatales, documentos vencidos al cierre y autoría del paquete final.
- `herramientas/presupuesto_postulacion.py`: Excel del presupuesto con fórmulas (Parametros, Presupuesto, Resumen,
  Controles, Cronograma), reparto por fuente (entidad, propio pecuniario, propio no pecuniario, terceros) y
  controles contra las reglas de las bases; verificado en Excel.
- Skills `preparar-postulacion`, `matriz-cumplimiento` y `red-team`; subagente `revisor-red-team` (8 perspectivas:
  evaluador técnico, fiscalizador de admisibilidad, financiero, experto escéptico, competidor, beneficiario,
  auditor de rendición, abogado del diablo). `definir-pauta` agrega el modo oferente (pauta inversa) y
  `evaluacion-economica` el modo postulación. `levantar-riesgos` suma el checklist de postulación.
- Perfiles `fondo-corfo`, `fondo-anid`, `licitacion-mercado-publico`, `fondo-regional-o-sectorial` y
  `licitacion-privada-rfp` (qué revisar y fuentes oficiales; los valores se confirman siempre en las bases).
- Ejemplos: `paquete-postulacion-demo` (bases con trampas sembradas) y `postulacion-demo` (etapa red team).

### Nuevo: autoría limpia de los entregables
- `herramientas/autoria.py` y `herramientas/verificar_autoria.py [--corregir]`: propiedades a nombre del usuario
  (`autoria.nombre` o `responsable.nombre`) y fecha actual; elimina miniatura, customXml, comentarios y propiedades
  heredadas; modo de compatibilidad actual de Word; normaliza caracteres invisibles; detecta términos y marcadores
  internos. Verificado en Word, Excel y PowerPoint.
- `md_a_docx.py`, `modelo_economico.py` y `presupuesto_postulacion.py` aplican la limpieza al guardar;
  `md_a_docx.py` no emite si queda un `[PENDIENTE` (salvo `--borrador`).
- Bloque `autoria` en `proyecto.yaml`, guía de estilo `contexto/estilo.md` (la completa el alta) y reglas en
  `CLAUDE.md`: entregables sin rastros del proceso, integridad (si las bases exigen declarar el uso de IA es un
  requisito y la decisión es del usuario) y commits sin líneas de coautoría.

### Nuevo: orientación al usuario
- `herramientas/guia_proyecto.py` genera `GUIA.md` por proyecto (tipo, carpetas, rutina, reportes, skills con frases
  de ejemplo, controles automáticos); skill `ayuda` con catálogo de las 29 skills. `instalar` y `nuevo-proyecto`
  muestran la guía al terminar.

### Correcciones del núcleo
1. El hook de inicio ya no avisa "alta en curso" cuando el alta terminó (`estado: terminada` en `avance-alta.md`).
2. Los hooks usan la ruta del proyecto (`$CLAUDE_PROJECT_DIR`) y funcionan aunque cambie la carpeta de trabajo.
3. Rutas con `/` en todos los mensajes (fallaba una prueba en Windows); inventarios antiguos con `\` se normalizan.
4. Salida UTF-8 en todos los scripts: ya no caen con `UnicodeEncodeError` en consolas Windows (cp1252).
5. `verificar_entorno.py` detecta que la carpeta está dentro de otro repositorio; `instalar` crea uno propio y la
   excluye del repositorio padre.
6. Archivado seguro del alta: `extraer_entrada.py --archivar` conserva las subcarpetas de carga.
7. El LEEME del paquete de prueba se renombró (`_LEEME-paquete.md`) y ya no pisa el de `_entrada/`.
8. `validar_proyecto.py`: advierte si el avance real está desactualizado y `--corte-actualizacion` compara plan y
   real a la misma fecha (campo `cronograma_actualizado`, que mantiene `actualizar-gantt`).
9. `validar_proyecto.py` advierte tareas que comienzan antes de que termine su predecesora.
10. `evm_cpm.py` ya no escribe mediciones por defecto: usar `--registrar`.
11. El hook de validación revisa también CSV y YAML modificados por consola (Bash o PowerShell).
12. El hook de confidenciales vigila también PowerShell (antes solo Bash) y no bloquea los marcadores `.gitkeep`.
13. `extraer_entrada.py` reconoce las bases de concursos (categoría `bases`, carpeta `00-bases-y-aclaraciones`).

### Ajustes tras la revisión independiente
- Barrido: los requisitos escritos como listas numeradas o artículos con contenido ya no se confunden con títulos;
  detecta menciones a IA en mayúsculas, prohibiciones ("se prohíbe…", ChatGPT, herramientas generativas), mínimos,
  máximos y porcentajes; no corta frases en "art. 8"; ids que no se repiten; filas de la tabla de criterios como `evaluacion`.
- `--registrar` (postulacion, evm_cpm, metricas_agil, puntaje_pauta) conserva columnas extra y filas previas de
  `mediciones.csv` y escribe de forma atómica (antes podía vaciar el archivo).
- Autoría: solo son error los rastros inequívocos (restos de conversación con un asistente, marcadores y rutas
  internas, librerías); nombres de herramientas o modelos de IA, nombres propios y términos técnicos son advertencia.
  `autoria.excluir` deja fuera documentos de terceros y declaraciones exigidas (que se redactan con veracidad).
- Compuertas que ya no se cumplen sin datos: presupuesto vacío (CTL-00), pauta sin objetivo, paquete final vacío,
  checklist con casillas sin marcar; estados de observaciones normalizados; ronda parcial del red team (roja-2)
  combina con la anterior; fechas inválidas avisadas y vigencias ilegibles tratadas como vencidas.
- Presupuesto: acepta "0,7", "70%" y "1.500.000"; se detiene ante valores no numéricos o ítems no declarados.

### Guía de inicio
- `instalar` distingue tres puntos de partida: desde cero, en marcha con documentos y en marcha sin documentos.
- Entrevista de estado (`nuevo-proyecto` 4b, también desde el alta): carga hitos, avance, problemas, riesgos,
  compromisos y decisiones cuando no están en documentos, con fuente "entrevista" y estimaciones marcadas.
- El aviso de inicio guía cuando el harness está instalado pero no tiene proyectos.
- La guía de carga indica dónde van las bases y aclaraciones de una postulación.

### Nuevo: programas con subproyectos (arquetipo `programa`)
- Un contrato padre ejecutado en varios subproyectos (`proyectos/<programa>/subproyectos/<id>/`), cada uno con sus
  objetivos, Gantt, línea base (término y monto asignados), riesgos, minutas, acuerdos y reportes propios. Heredan del
  programa lo que no definen (cliente, marca, logo, formatos, plantillas, autoría, umbrales): `herramientas/_config.py`.
- Presupuesto macro y por subproyecto con cuentas y contingencia (del programa y de cada subproyecto): base,
  modificaciones (enmienda, reasignación y uso de contingencia, balanceadas), compromisos, real, pronóstico, disponible,
  estimado al término y desviación.
- Personas compartidas entre subproyectos con su dedicación: dotación por subproyecto y sobreasignación por mes.
- Enmiendas con afectaciones por subproyecto (plazo, alcance, monto, hito) y control de las no aplicadas.
- `herramientas/programa.py`: estado consolidado, ruta crítica del programa completo, cronograma consolidado con
  dependencias entre subproyectos (`sp1:T04`), Gantt macro, detallado y por subproyecto, y control presupuestario en
  Excel con fórmulas (verificado en Excel).
- `crear_proyecto.py <id> --programa <programa>`; skill `gestionar-programa`; `nuevo-proyecto` pregunta si va aparte,
  dentro de un programa o como programa nuevo; `validar_proyecto`, `evm_cpm` y `gantt_mermaid` aceptan `--cronograma`.
- Ejemplo `programa-demo` con problemas sembrados (enmienda sin aplicar, persona al 130%, sobrecosto proyectado).

### Pruebas
104 pruebas automáticas (antes 18) y 23 escenarios de skills.
