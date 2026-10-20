# Cambios

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
