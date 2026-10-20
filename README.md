# PMO Harness v2.2

Marco de trabajo para diseñar y gestionar proyectos **de cualquier tipo** con un asistente de IA —Claude Code,
OpenAI Codex, Gemini, Google Antigravity, Cursor, GitHub Copilot u otro que trabaje sobre carpetas— para un programa
de implementación, una obra, un portafolio de acciones, la evaluación de postulaciones a un fondo, la preparación de
una postulación a CORFO o a una licitación, o un estudio de prefactibilidad. Todo vive en una carpeta local por
empresa, respaldada en un repositorio **privado** de GitHub de quien lo usa.

> **¿Primera vez?** Sigue la [guía de inicio](EMPEZAR-AQUI.md) (10 minutos, sin conocimientos técnicos). El uso
> diario está en el [manual de usuario](MANUAL-DE-USUARIO.md). Licencia MIT.

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

Está organizado en tres capas:
1. **Núcleo genérico** (`.claude/skills/`, `herramientas/`, `plantilla-proyecto/`): métodos que sirven para todo.
2. **Arquetipos** (`arquetipos/`): formas de trabajo — `ejecucion` (plan, hitos, contrato, valor ganado),
   `obra` (terreno: RFI, no conformidades, inspecciones, estados de pago), `agil` (sprints, DORA, ingeniería),
   `cartera` (muchos ítems con etapas y métricas), `evaluacion` (evaluar propuestas de terceros con pauta),
   `postulacion` (preparar y presentar una propuesta para ganar un fondo, licitación o concurso), `programa` (un
   contrato padre ejecutado en varios subproyectos, cada uno con su Gantt, presupuesto, equipo y reportes) y `estudio`
   (preguntas, supuestos, modelo económico, recomendación).
3. **Proyecto** (`proyectos/<slug>/`): todo lo particular — métricas, reglas, reportes con nombre propio,
   plantillas, marca y cálculos del dominio.

**La idea central:** no pasar semanas configurando. Se cargan los documentos que ya existen y el asistente
configura el proyecto en horas: lee todo, decide con reglas explícitas, deja registro de cada decisión y
pregunta solo lo que no puede resolver.

---

## Inicio rápido (tres pasos)

> Paso a paso y para cualquier usuario: [guía de inicio](EMPEZAR-AQUI.md). Si quieres que la instalación casi no te
> pregunte, completa antes `FICHA-DE-INICIO.md`.

### 1. Preparar la carpeta
1. Crea una carpeta con el nombre de tu empresa, por ejemplo `Consultora-Sur`.
2. Descomprime el contenido del zip **directamente dentro de ella**. Debe quedar así:
   ```
   Consultora-Sur/
   ├── .claude/
   ├── AGENTS.md
   ├── herramientas/
   ├── plantilla-proyecto/
   └── ...
   ```
   Si te quedó una subcarpeta intermedia (`Consultora-Sur/pmo-harness-nucleo-main/...`), mueve su contenido un nivel
   arriba, o abre directamente esa subcarpeta. Lo importante es que la carpeta que abras contenga `AGENTS.md`.

### 2. Abrir e instalar
1. Abre la carpeta en VS Code (Archivo → Abrir carpeta) y abre tu asistente de IA (Claude Code, Codex, Gemini…).
2. Escribe **"hola"** (o `/instalar` en Claude Code): el asistente detecta que falta instalar y te lo ofrece.
3. El asistente revisa el computador y, **con tu permiso, instala lo que falte** (Python, Git, GitHub CLI y
   librerías; no toca VS Code). Después define la empresa dueña de la carpeta, prepara Git y GitHub (siempre privado),
   se registra a sí mismo y te pregunta **de qué se trata tu proyecto**, en tus palabras. Con eso propone el diseño
   (arquetipo, etapas, métricas, reglas, reportes), te hace unas pocas preguntas y crea el proyecto.
   - **Recomendado antes de abrir la IA:** doble clic en `INSTALAR-WINDOWS.bat` o `INSTALAR-MAC.command`. Instala lo
     necesario sin preguntas técnicas, pide nombre y correo, y conecta GitHub con el código ya copiado. Nunca se queda
     detenido: cada pregunta tiene un tiempo máximo.

### 3. Si tienes documentos: cargarlos y decir "listo"
1. Deja **todo** el material del programa en `proyectos/<tu-programa>/_entrada/`: contratos, enmiendas,
   carta Gantt, reportes emitidos, plantillas, actas, correos, conversaciones de otras IA, logos.
   No hace falta ordenar ni renombrar. Los archivos de esa carpeta no se suben a GitHub; del texto de las bases y
   documentos de definición queda una copia fiel en `fuentes/` (en tu repositorio privado), para trabajar desde
   cualquier computador sin los originales.
   El archivo `_entrada/LEEME.md` explica qué conviene dejar y cómo exportar chats de otras IA.
2. Escribe **listo**.
3. El asistente ejecuta el alta: inventario → lectura → decisiones → configuración → **un solo mensaje con
   las preguntas pendientes** (máximo 12, cada una con una propuesta) → verificación → informe.
4. Al terminar tendrás:
   - `contexto/informe-de-alta.md`: lo que el asistente entendió del programa, cobertura y pendientes.
   - `contexto/registro-de-alta.md`: cada decisión tomada, con su fuente y nivel de confianza.
   - El proyecto completo configurado y un reporte semanal de prueba.

Si el alta se interrumpe (se cierra el editor, se acaba la sesión), escribe "continúa el alta": el asistente
retoma desde su punto de control sin repetir trabajo.

Si partes de cero, este paso no es necesario: el proyecto queda listo después del paso 2.

---

## Tipos de proyecto

No hay un catálogo cerrado: describes el proyecto y la skill `nuevo-proyecto` elige el arquetipo (o una
combinación) y propone lo propio del dominio. Algunos ejemplos:

| Proyecto | Arquetipo | Qué propone el generador |
|---|---|---|
| Implementar un sistema para un cliente | ejecución (+ ágil si hay desarrollo) | Gantt, hitos, contrato, valor ganado, ruta crítica, reporte semanal |
| Construir una casa u obra | ejecución + obra | Partidas, RFI, inspecciones, no conformidades, estados de pago, informe de obra |
| Equipo de desarrollo de software | ágil | Backlog, sprints, velocidad, DORA, ADR, deuda técnica, trazabilidad |
| Portafolio de acciones | cartera | Etapas de selección, tesis por acción, política de inversión, revisión mensual vs índice |
| Granja de bots de trading | cartera (+ ágil para su desarrollo) | Etapas backtest → paper → real, drawdown, profit factor, reglas de promoción y retiro |
| Evaluar postulaciones a un fondo o licitación | evaluación | Pauta, admisibilidad, evaluación fundamentada por propuesta, ranking, acta |
| Postular a un fondo (CORFO, ANID, regional) o presentar una oferta a una licitación | postulación | Go/No-Go, barrido de bases y matriz de cumplimiento, pauta inversa, estrategia, secciones trazables, presupuesto con controles en Excel, red team, checklist de entrega |
| Programa con un contrato general y varios subproyectos (presupuesto macro y por subproyecto, personas compartidas, enmiendas que afectan subproyectos) | programa + ejecución | Subproyectos con su Gantt, objetivos, riesgos, minutas y reportes; Gantt macro, control presupuestario con contingencia, dotación y sobreasignación, estado consolidado |
| Prefactibilidad o evaluación económica | estudio | Preguntas, supuestos con fuente, modelo en Excel con VAN/TIR y sensibilidad |

Los diseños que quieras reutilizar se guardan como perfiles en `biblioteca/perfiles/`. Vienen incluidos perfiles
de convocatorias: `fondo-corfo`, `fondo-anid`, `licitacion-mercado-publico`, `fondo-regional-o-sectorial` y
`licitacion-privada-rfp` (dicen qué revisar; los valores siempre se confirman en las bases vigentes).
Pendiente: arquetipo *operación continua* (servicios recurrentes con indicadores de servicio).

---

## Requisitos
- [VS Code](https://code.visualstudio.com/) con un asistente de IA que trabaje sobre carpetas y ejecute comandos:
  **Claude Code**, **OpenAI Codex**, **Gemini** (CLI o Code Assist), **Cursor** o **GitHub Copilot** en modo agente.
  Un chat en el navegador no sirve: necesita leer la carpeta y ejecutar los scripts.
- Una cuenta de GitHub (el repositorio de cada empresa es siempre privado).
- Lo demás lo instala el harness **con tu permiso** (`instalar`, o doble clic en `INSTALAR-WINDOWS.bat` /
  `INSTALAR-MAC.command`): [Python 3.9+](https://www.python.org/downloads/), [Git](https://git-scm.com/downloads),
  [GitHub CLI](https://cli.github.com/) (opcional: crea el repositorio privado desde el chat) y
  [LibreOffice](https://www.libreoffice.org/) (opcional: revisión visual y PDF). En Windows usa winget, solo para el
  usuario (sin permisos de administrador), con tiempo máximo por programa y la descarga oficial si winget falla; en Mac,
  Homebrew (pide la contraseña del Mac) y deja las librerías en `.venv/`. Si prefieres instalar a mano, usa los enlaces.
- Opcional: extensión de VS Code **Markdown Preview Mermaid Support** (ver la carta Gantt).
- Recomendado con Claude Code: las skills oficiales de documentos de Anthropic (Word, Excel, PowerPoint, PDF), desde
  [github.com/anthropics/skills](https://github.com/anthropics/skills). El harness funciona sin ellas.

## Con qué IA funciona, y cómo cambiar de una a otra
- **Reglas únicas:** `AGENTS.md` tiene todas las reglas y la tabla de procedimientos. `CLAUDE.md` y `GEMINI.md` solo la
  importan; Codex, Cursor y Copilot la leen directamente. Así todas operan igual desde el primer mensaje.
- **Primera vez con una IA:** se configura sola (skill `configurar-asistente`): revisa qué archivo lee, activa los
  controles, hace una prueba rápida y queda registrada en `.harness/asistentes.yaml`. Si es una IA que el harness no
  conoce, averigua y te pregunta lo necesario.
- **Cambiar de IA a mitad de camino:** cada proyecto lleva un traspaso (`seguimiento/traspaso.md`) que se actualiza al
  cerrar cada tarea: qué se hizo, en qué quedó y el próximo paso. La IA nueva lo lee al empezar (el estado de inicio lo
  muestra) y retoma sin que repitas nada. Lo que no viaja es la conversación misma; los datos y el estado sí. Antes de
  cambiar, conviene decir «guarda».
- **Controles:** los que protegen la información (no subir confidenciales, validar planillas) corren en Git antes de
  cada commit, con cualquier IA o sin IA. Claude Code agrega sus hooks y subagentes; en las demás, esos pasos los hace
  la IA según `AGENTS.md`.

## Varias empresas y varios computadores
- **Una carpeta por empresa**, cada una con su propio repositorio privado: `python herramientas/nueva_empresa.py
  "Empresa 2" --destino <carpeta>` crea la carpeta con el núcleo, su `empresa/` (marca, autoría, banco de antecedentes,
  formatos comunes) y el repositorio. Las postulaciones y proyectos de esa empresa viven en su `proyectos/` y heredan
  su marca y formatos. Los datos de dos empresas nunca se mezclan.
- **Otro computador:** abre VS Code con tu IA en cualquier carpeta del harness y pide «descarga mis empresas», o ejecuta
  `INSTALAR-WINDOWS.bat -Clonar` / `bash herramientas/preparar_pc.sh --clonar`: lista los repositorios con el tema
  `pmo-harness-empresa` de tu cuenta y descarga los que elijas. Luego abre la carpeta de la empresa y escribe «hola».
  Los originales de `_entrada/`, CVs y paquetes firmados no viajan por GitHub (son confidenciales): las réplicas fieles
  de las bases y documentos de definición, las fichas y todo lo configurado, sí.
- **Mejoras del núcleo:** cada carpeta trae su copia del núcleo (así cualquier IA la entiende sin instalar nada aparte).
  «Actualiza el harness» (`actualizar_nucleo.py`) trae la versión nueva desde el repositorio del núcleo o un zip, sin
  tocar proyectos ni datos, con respaldo, pruebas y reversión si algo falla.

## Status de todos los proyectos
- **Cada día:** al abrir la sesión, el asistente muestra en pocas líneas el status de los proyectos de la empresa
  (semáforo, lo que vence pronto, decisiones que esperan). En cualquier momento: «¿cómo vamos?».
- **Reporte web:** «dame el reporte de status» genera una página (también Markdown, Excel o JSON) en `status/`, con
  historial y comparación con el anterior. Después pregunta si se deja listo **cada semana**, en qué día y a qué hora
  (`herramientas/agendar_status.py`: Tareas programadas en Windows, launchd en Mac).
- **Reglas fijas del semáforo:** salen de los mismos cálculos de `postulacion.py`, `validar_proyecto.py` y
  `evaluar_metricas.py`, más el calendario, los hitos, los acuerdos y los compromisos propios
  (`seguimiento/vencimientos.csv`, por ejemplo un reporte semestral).
- **Varias empresas:** cada una tiene su status en su carpeta. Si se quieren ver juntas, un **tablero único**
  (`status.py --crear-panel`) va en una carpeta y un repositorio privado aparte, solo del usuario: lee el status de cada
  empresa sin copiar sus datos. Al sumar otra empresa, el asistente pregunta si son independientes o de una misma
  entidad, y si se prefiere un tablero por empresa o uno general.

---

## Probar antes con datos ficticios

### Prueba 1 — Portafolio de acciones (arquetipo cartera)
`ejemplos/portafolio-acciones/` es un portafolio ficticio completo: 12 acciones inventadas en distintas
etapas, transacciones, precios mensuales con un índice de referencia, datos fundamentales, fichas con tesis,
política de inversión como reglas y un script propio que calcula rentabilidad, volatilidad, caída máxima,
Sharpe y concentración. Instrucciones sugeridas en el chat de tu asistente:

1. **"Evalúa las métricas del portafolio de ejemplo con corte al 31-08-2026."**
   Debería encontrar: una acción sobre el límite de 20% (TCOR), una con deuda/EBITDA sobre la política
   (PNOR), una en análisis sin tesis escrita (RAUS), una en preselección que no cumple el filtro de ROE
   (SALI), una ficha con revisión vencida (BPAC), una candidata a avanzar (FARA) y la cartera rindiendo
   bajo el índice.
2. **"Genera la revisión mensual de agosto del portafolio de ejemplo."**
3. **"Agrega la métrica 'dividendos recibidos en 12 meses' al portafolio de ejemplo."**
4. **"Pasa FARA a preselección"** y luego **"crea la ficha de RAUS"** (te ayudará a escribir la tesis).
5. **"Quiero un reporte trimestral llamado Informe de Gestión, en PowerPoint, con desempeño, política y
   decisiones."** (diseño de un reporte propio por conversación).

Todo es ficticio y sirve para probar la herramienta: no es información ni recomendación de inversión.

### Prueba 2 — Evaluación de postulaciones (arquetipo evaluación)
`ejemplos/fondo-innovacion/` trae las bases de un fondo ficticio, la pauta ya construida y 3 postulaciones.
1. **"Evalúa las postulaciones del fondo de ejemplo."** Debería: recordarte la confidencialidad, declarar
   inadmisible a P-003 (menos de 2 años de actividad), evaluar cada postulación con un subagente citando
   evidencia, dejar los puntajes como *propuesta* y pedirte la revisión antes del acta.
2. **"Construye de nuevo la pauta desde las bases"** para probar `definir-pauta`.

### Prueba 3 — Estudio económico (arquetipo estudio)
`ejemplos/estudio-solar/` tiene los supuestos de una planta solar ficticia y su modelo en Excel.
**"Revisa la evaluación económica del estudio solar: ¿qué tan robusta es?"** Debería explicar VAN, TIR y
recuperación, señalar que con 10% menos de ahorro el VAN queda cerca de cero y que dos supuestos críticos
tienen confianza baja o media.

### Prueba 4 — Equipo de software (arquetipo ágil)
`ejemplos/equipo-software/` tiene 5 sprints, backlog, despliegues, deuda técnica, requisitos, ADR y un postmortem.
1. **"Planifiquemos el sprint S5 del equipo de software de ejemplo."**
2. **"¿Cómo estamos en entrega? Dame las métricas DORA."** (tasa de falla de 33%, dos incidentes).
3. **"¿Qué requisitos no tienen pruebas?"**

### Prueba 5 — Diseño desde cero
Escribe algo como **"quiero llevar el seguimiento de una granja de bots de trading, con sus métricas"** o
**"quiero llevar la construcción de una casa"** y revisa qué diseño propone `nuevo-proyecto`.

### Prueba 6 — Alta a partir de documentos (arquetipo ejecución)
`ejemplos/` también trae un programa inventado ("Programa Andes Digital"):
- `paquete-alta-andes/`: documentos en bruto (contrato, enmienda, Gantt, informe semanal, PEP, acta,
  correos, exportación de ChatGPT, logo), con contradicciones sembradas a propósito.
- `demo-andes/`: cómo debería quedar el proyecto después del alta. Sirve como "respuesta correcta".

Prueba sugerida:
1. `/instalar` y como nombre del programa responde "Prueba Andes".
2. Copia las subcarpetas de `ejemplos/paquete-alta-andes/` dentro de `proyectos/prueba-andes/_entrada/`.
3. Escribe **listo** y compara el resultado con `ejemplos/demo-andes/`.

El `_LEEME-paquete.md` del paquete indica qué debería resolver sola y qué debería preguntar. Los datos están
fechados en torno al 25-09-2026: si pruebas después, pide "usa fecha de corte 25-09-2026".
Con el demo ya cargado, prueba también **"¿vamos atrasados? usa fecha de corte 25-09-2026"**: debería usar
valor ganado y ruta crítica (SPI 0,79, CPI 0,87, término pronosticado 29 días después del contractual).

### Prueba 7 — Postulación a un fondo (arquetipo postulación)
`ejemplos/paquete-postulacion-demo/` trae bases ficticias de un fondo de innovación con trampas sembradas: un
requisito excluyente escondido en un anexo, una aclaración que cambia el límite de páginas y exige declarar el uso
de IA, un certificado con vigencia máxima y un presupuesto del cliente que no cumple el cofinanciamiento.
`ejemplos/postulacion-demo/` muestra cómo debería verse a mitad de camino (etapa red team). Prueba:
1. `python herramientas/postulacion.py ejemplos/postulacion-demo --hoy 2026-11-03`: etapa, compuertas, fallas fatales.
2. `python herramientas/presupuesto_postulacion.py ejemplos/postulacion-demo/economico/presupuesto.yaml --salida prueba.xlsx`:
   abre `prueba.xlsx` y cambia un aporte en la hoja Presupuesto: la hoja Controles se recalcula sola (para cambios
   definitivos se edita el YAML y se vuelve a generar).
3. Crea `prueba-postulacion` con el arquetipo `postulacion`, copia las subcarpetas del paquete a `_entrada/` y di
   "prepara la postulación".


### Prueba 8 — Programa con subproyectos (arquetipo programa)
`ejemplos/programa-demo/` es un programa ficticio con un contrato padre, dos enmiendas y tres subproyectos (ERP, app
ágil y portal) con dependencias entre ellos, contingencia del programa y por subproyecto, y una persona compartida.
1. `python herramientas/programa.py ejemplos/programa-demo --hoy 2026-10-15 --excel`: avance y plazo por subproyecto,
   presupuesto y contingencia, sobreasignación, enmienda pendiente y ruta crítica del programa; genera el Gantt macro, el
   detallado, el de cada subproyecto y el control presupuestario en Excel.
2. Para uno propio: «nuevo proyecto» → «programa nuevo», y luego «agrega un subproyecto». Un proyecto sin relación con el
   programa se crea aparte («nuevo proyecto» → «independiente»).
---

## Robustez: subagentes, hooks y pruebas

**Subagentes** (`.claude/agents/`): asistentes con un rol acotado que Claude Code invoca solo cuando conviene (las
demás IA aplican el mismo rol en un paso separado).
`lector-documental` lee muchos documentos en paralelo durante el alta; `revisor-independiente` revisa
reportes y evaluaciones antes de entregarlos; `evaluador-propuestas` evalúa cada postulación por separado
para evitar sesgos; `revisor-red-team` asume una perspectiva del red team (evaluador, fiscalizador, financiero,
experto escéptico, competidor, beneficiario, auditor, abogado del diablo); `analista-datos` procesa y verifica datos.

**Control de Git** (`.githooks/pre-commit`, para cualquier IA o sin IA): antes de cada commit bloquea material
confidencial y planillas mal formadas. Se activa una vez por computador (`git config core.hooksPath .githooks`; el
instalador y `instalar` lo hacen, y el estado de inicio avisa si falta).

**Hooks de Claude Code** (`.claude/settings.json`): controles adicionales que no dependen de que la IA "se acuerde".
Bloquean subir a GitHub archivos confidenciales (vigilan la consola Bash y PowerShell), validan cada CSV o YAML
justo después de editarlo (también si se modificó por consola), y al abrir una sesión informan el estado
(instalación, traspasos, material pendiente, altas en curso). Usan `sh herramientas/py.sh`, que encuentra Python
aunque en Windows solo responda `py` o en Mac esté en `.venv`.

**Pruebas** (`pruebas/`): `python pruebas/ejecutar_pruebas.py` ejecuta 200 pruebas sobre copias de los
ejemplos (no modifica nada) y verifica que cada herramienta detecte lo sembrado. Ejecútala después de
cambiar el núcleo. `pruebas/escenarios-skills.md` lista instrucciones para probar el comportamiento de las skills y un
guion para probar el harness con cada IA.

---

## Uso diario

| Quiero… | Pídele al asistente |
|---|---|
| Crear otro proyecto | Descríbelo: "quiero llevar…" |
| Incorporar documentos nuevos | Déjalos en `_entrada/` y di "procesa la entrada" |
| Agregar o cambiar una métrica o regla | "Quiero medir también…", "sube el límite a 25%" |
| Cargar datos | "Importa este CSV de resultados", "actualiza los precios de septiembre" |
| Mover un ítem de etapa | "Pasa el bot B-07 a paper trading", "descarta la postulación 12" |
| Crear un reporte propio | "Quiero un reporte mensual llamado PEP, en Excel, con…" (queda solo en ese proyecto) |
| Reporte semanal | "Genera el reporte semanal" (te pedirá los insumos de la semana si faltan) |
| Otro reporte del catálogo | Por su nombre: "genera la revisión mensual", "arma la presentación para el comité" |
| Agregar un formato nuevo de reporte | Deja el modelo en `_entrada/` y di "agrega este formato de reporte" |
| Minuta | Pega tus notas: "haz la minuta de esta reunión" |
| Riesgos | "Registra un riesgo: …", "revisa la matriz de riesgos" |
| Avance | "SP1 va en 60%, la migración parte el lunes" |
| Contratos | "Registra esta enmienda" (con el PDF en `_entrada/`) |
| Cambios | "El cliente pidió…, abre una solicitud de cambio" |
| Revisar un correo | Pega el correo: "¿qué implica esto para el proyecto?" |
| Comparar versiones | "Compara la v3 con la v4 de la propuesta", "registra esta nueva versión de las bases" |
| Preparar una reunión | "Prepara el comité del jueves" |
| Buscar riesgos nuevos | "Levanta los riesgos antes del hito de migración" |
| Valor ganado y ruta crítica | "¿Vamos atrasados? ¿cuál es la ruta crítica?" |
| Sprints | "Planifiquemos el sprint", "daily: H-12 pasó a revisión", "hagamos la retro" |
| Ingeniería | "Registra esta decisión de arquitectura", "tuvimos una caída, hagamos el postmortem" |
| Obra | "Registra la RFI de fundaciones", "la inspección de moldajes salió rechazada" |
| Evaluar propuestas | "Evalúa las postulaciones", "compara las tres ofertas", "arma el acta" |
| Evaluación económica | "Arma el flujo de caja con estos supuestos", "¿qué pasa si la demanda cae 20%?" |
| Chequear que todo cuadre | "Revisa la consistencia antes del comité" |
| Dar de alta otro proyecto | "Da de alta un proyecto nuevo" |
| Status | "¿Cómo vamos?", "dame el reporte de status", "agenda el reporte semanal los lunes a las 9" |
| Compromiso con fecha | "El reporte semestral SSM vence el 30 de julio" (queda en el status hasta cerrarlo) |
| Formulario de la plataforma | "Arma la hoja de carga del formulario" (límites de caracteres y botón Copiar por campo) |
| Llenar una planilla oficial | "Llena el Excel de indicadores con estos datos" (sin romper listas desplegables ni formas) |
| Guardar | "Guarda los cambios" |
| Cambiar de IA | Abre la carpeta con la otra IA y di "hola" o "¿en qué íbamos?" (retoma desde el traspaso) |
| Otra empresa | "Crea la carpeta para la empresa X" (repositorio propio, sin mezclar datos) |
| Trabajar en otro computador | "Descarga mis empresas" (o `INSTALAR-WINDOWS.bat -Clonar`) |
| Actualizar el harness | "Actualiza el harness" (muestra antes qué cambia; no toca proyectos ni datos) |

## Personalización: dónde está cada cosa

| Qué quiero cambiar | Dónde |
|---|---|
| Marca, autoría, responsable y formatos comunes de la empresa | `empresa/empresa.yaml`, `empresa/marca/`, `empresa/plantillas/`, `empresa/reportes/catalogo/` |
| Banco de antecedentes de la empresa (CVs, certificados con vigencia) | `empresa/contenidos/` (los archivos no se suben a Git) |
| Qué documentos se replican en `fuentes/` | `replicas` en `empresa/empresa.yaml` (o en `proyecto.yaml`) |
| Datos, stakeholders, umbrales, colores de un proyecto | `proyectos/<slug>/proyecto.yaml` y `contexto/` |
| Métricas y reglas (políticas, límites) | `proyectos/<slug>/metricas/metricas.yaml` (y `metricas-<arquetipo>.yaml`) |
| Pauta de evaluación | `proyectos/<slug>/evaluacion/pauta.yaml` |
| Supuestos del modelo económico | `proyectos/<slug>/estudio/modelo/supuestos-modelo.yaml` |
| Flujo del tablero ágil, definición de hecho | `proyectos/<slug>/agil/estados.yaml` |
| Reglas para todas las IA | `AGENTS.md` (núcleo: se reemplaza al actualizar; lo propio va al proyecto o a la empresa) |
| Subagentes y hooks | `.claude/agents/`, `.claude/settings.json` y `.githooks/` |
| Etapas de los ítems y requisitos para avanzar | `proyectos/<slug>/items/etapas.yaml` |
| Cálculos propios del dominio | `proyectos/<slug>/scripts/` |
| Reglas y estilo del cliente | `proyectos/<slug>/CLAUDE.md` |
| Secciones o reglas de un reporte | `proyectos/<slug>/reportes/catalogo/<tipo>.md` |
| Plantillas Word/Excel/PPT | `proyectos/<slug>/reportes/plantillas/` |
| Logo | `proyectos/<slug>/marca/logo.png` |
| Formato de minuta de un proyecto | crear `proyectos/<slug>/minutas/_formato.md` |
| Cómo decide el asistente en el alta | `.claude/skills/alta-proyecto/references/reglas-de-decision.md` |
| Qué datos debe cubrir el alta | `.claude/skills/alta-proyecto/references/cobertura.md` |
| Valores por defecto para todos los proyectos futuros | `plantilla-proyecto/` y `arquetipos/` |
| Diseños reutilizables | `biblioteca/perfiles/` |
| Cómo trabaja una skill | `.claude/skills/<skill>/SKILL.md` |
| Crear una skill nueva | Pídele al asistente que la cree en `.claude/skills/<nombre>/SKILL.md` (en Claude Code, con la skill `skill-creator` de Anthropic); es propia de tu carpeta y no se borra al actualizar |

## Autoría limpia de los entregables
Los documentos que se entregan (Word, Excel, PowerPoint, PDF) salen a nombre del usuario (`autoria.nombre` en
`proyecto.yaml`, o el responsable) y sin rastros del proceso: propiedades con autor y fecha actuales, sin partes
heredadas de plantillas genéricas, sin marcadores internos ni caracteres invisibles, y con el estilo del usuario
(`contexto/estilo.md`). `python herramientas/verificar_autoria.py <archivo|carpeta> --proyecto <ruta> [--corregir]`
lo verifica antes de entregar. **Integridad:** si unas bases o un contrato exigen declarar el uso de herramientas
de IA, o lo restringen, es un requisito más: se registra, se avisa y la decisión es del usuario.

## Guía de cada proyecto
Al instalar o crear un proyecto se genera `proyectos/<slug>/GUIA.md`: qué tipo de proyecto es, dónde está cada
cosa, la rutina, los reportes, las skills útiles con frases de ejemplo y los controles automáticos. Para verla
en cualquier momento, pregunta «¿qué puedo hacer?» (skill `ayuda`). No hace falta usar el nombre exacto de las skills.

## Confidencialidad: qué queda en GitHub
- **No se suben** a GitHub: `_entrada/` completa (los originales), los PDF u originales dentro de `contractual/`, las
  versiones originales de `documentos/`, los documentos de `postulaciones/` de terceros, el banco de archivos
  (`contenidos/archivos/` y `empresa/contenidos/archivos/`) y el paquete firmado que se presenta (`entrega/final/`).
- **Sí se sube**, al repositorio privado: lo configurado (registros, fichas, matrices, reportes en Markdown) y las
  **réplicas fieles** en `fuentes/` del texto de bases, anexos, aclaraciones, lineamientos, contratos, actas e
  informes. De CVs, estados financieros y datos personales nunca se sube el texto: solo su ficha.
- El control de Git (y, en Claude Code, también un hook) bloquea cualquier intento de agregar lo confidencial, aunque
  se pida por error.
- **Status:** el reporte de cada empresa queda en su carpeta (`status/`). El tablero único de varias empresas va en un
  repositorio privado aparte, para que quien tenga acceso a una empresa no vea las demás.
- El repositorio debe ser **privado**. Aun así, confirma que la política de la empresa y de sus clientes permite usar
  herramientas de IA y GitHub con su información. La IA que uses procesa el contenido de los documentos.
- `guardar-cambios` revisa que no se suban archivos sensibles antes de cada envío.

## Permisos
`.claude/settings.json` permite a Claude Code, sin pedir confirmación cada vez, ejecutar los scripts de
`herramientas/`, las pruebas y los comandos básicos de Git. Todo lo demás sigue pidiendo permiso. En otras IA, los
permisos se configuran en la propia herramienta: conviene un modo que pida confirmación antes de comandos que salgan de
la carpeta o borren archivos.

## Historial de versiones
- **2.2** — Status diario en el chat y al iniciar, reporte web con historial y agenda semanal, tablero único de varias
  empresas en su propio repositorio privado; formulario de la plataforma (límites, caracteres raros, hoja de carga);
  llenado de planillas oficiales sin pérdidas; barrido de requisitos selectivo (charlas y normativa aparte) y manejo de
  escaneos (ver CHANGELOG.md).
- **2.1** — Funciona con cualquier asistente de IA (`AGENTS.md` como fuente única, `configurar-asistente`, traspaso entre
  sesiones e IA, controles en Git); instalación automática con permiso en Windows y Mac; una empresa por carpeta y
  repositorio, con herencia de marca y banco común, y actualización del núcleo sin tocar los datos; réplicas fieles en
  Markdown de bases y documentos de definición (ver CHANGELOG.md).
- **2.0** — Importación de cronogramas de MS Project (XML); programas con subproyectos (presupuesto macro y por
  subproyecto, contingencia, personas compartidas, enmiendas por subproyecto, Gantt macro); manual de usuario y ficha de
  inicio. Arquetipo postulación (lado del oferente) con barrido exhaustivo de bases, matriz de cumplimiento,
  pauta inversa, red team de 8 perspectivas, presupuesto con controles en Excel y 5 perfiles de convocatorias;
  autoría limpia de los entregables; guía por proyecto y skill `ayuda`; 13 correcciones del núcleo (ver CHANGELOG.md).
- **1.5** — Valor ganado, ruta crítica y pronóstico de término; arquetipo obra (RFI, no conformidades,
  inspecciones, estados de pago).
- **1.4** — Arquetipo ágil: sprints, métricas DORA, ADR, deuda técnica, trazabilidad, postmortems,
  importación desde GitHub o Jira.
- **1.3** — Subagentes, hooks, batería de pruebas; comparación y versiones de documentos, preparación de
  reuniones, levantamiento de riesgos; arquetipo evaluación (pauta y propuestas); evaluación económica en Excel.
- **1.2** — Núcleo genérico con arquetipos ejecución, cartera y estudio; métricas y reglas; reportes propios por proyecto.
- **1.1** — Instalación guiada y alta documental.
- **Próximo** — Arquetipo *operación continua*.
