---
name: alta-proyecto
description: Alta rápida de un proyecto o programa a partir de sus documentos. Lee todo lo que haya en la carpeta _entrada (contratos, cronogramas, reportes, plantillas, actas, correos, chats de otras IA), configura el harness completo tomando decisiones con reglas explícitas, deja registro de cada decisión y pregunta solo lo que no puede resolver. Úsala cuando el usuario diga "listo" después de cargar documentos, pida dar de alta, iniciar, crear o configurar un proyecto, procesar la entrada, incorporar material nuevo, continuar o retomar el alta, o completar lo que quedó pendiente.
---

# Alta de proyecto (documentos primero)

**Principio:** el usuario no debería pasar semanas configurando. Lee todo, decide rápido con las reglas de
`references/reglas-de-decision.md`, registra cada decisión con su fuente y confianza, y concentra las
preguntas en un solo mensaje al final. Es mejor decidir con confianza media y dejarlo marcado para revisión
que detener el trabajo por cada duda.

Archivos de referencia (léelos al comenzar la fase C):
- `references/cobertura.md` — qué datos debe quedar cubiertos, dónde se guardan, fuentes típicas y valores por defecto.
- `references/lectura-por-tipo.md` — qué extraer de cada tipo de documento.
- `references/reglas-de-decision.md` — cómo resolver contradicciones y cuándo preguntar.

## Punto de control (para no perder avance)
El alta puede tomar varias horas y más de una sesión. Mantén `_entrada/_procesado/avance-alta.md` con:
una primera línea `estado: en_curso` (pasa a `estado: terminada` al cerrar la fase G), fase actual,
archivos leídos (id del inventario), archivos pendientes y próximos pasos. Actualízalo al terminar cada
archivo o grupo. **Al iniciar, si existe y dice `en_curso`, retoma desde ahí sin repetir trabajo.**
El hook de inicio de sesión solo ofrece continuar el alta si el archivo dice `en_curso`.

## Fase A — Crear el proyecto (si no existe)
Si el proyecto se diseñó con `nuevo-proyecto`, ya existe: pasa a la fase B.
1. Propón un `slug` (minúsculas, guiones, sin tildes) a partir del nombre.
2. Determina el arquetipo (ver `arquetipos/*/ARQUETIPO.md`). Si no es evidente por la descripción, créalo
   como `ejecucion` y ajústalo en la fase D según los documentos (se puede agregar un arquetipo después).
3. `python herramientas/crear_proyecto.py <slug> --arquetipos <a> --nombre "<Nombre>"`
4. Completa en `proyecto.yaml` lo que ya sepas (nombre, cliente, responsable) y agrega el slug a `.harness/estado.yaml`.

**Programa con subproyectos:** si el material muestra un contrato único que se ejecuta en varios frentes o
subproyectos con presupuestos, equipos o cronogramas propios, crea un programa (`--arquetipos programa,ejecucion`) y un
subproyecto por frente (`crear_proyecto.py <id> --programa <programa>`). En las fases C a E, clasifica cada dato por
subproyecto (o PROGRAMA si es transversal): cronogramas, presupuesto y gastos, personas y dedicación, riesgos, minutas,
reportes y plantillas; y las enmiendas con sus afectaciones por subproyecto (`gestionar-programa`). Termina con
`programa.py` sin descuadres ni afectaciones pendientes.

## Fase B — Inventario
1. `python herramientas/extraer_entrada.py proyectos/<slug>`
   Convierte todo a texto en `_entrada/_procesado/texto/`, extrae imágenes candidatas a logo y genera `inventario.md`.
   Es incremental: si se agrega material después, solo procesa lo nuevo.
2. Revisa el inventario y corrige categorías evidentes (el script sugiere por nombre y contenido).
3. **Réplicas** (sección «Réplicas en fuentes/» del inventario): las bases y documentos de definición quedan con su
   texto fiel en `fuentes/`, que se sube al repositorio privado para trabajar sin los originales en otro computador.
   - **Por decidir:** aplica la política de `replicas` (empresa o proyecto) con criterio: si el documento define algo
     del proyecto (alcance, plazos, montos, compromisos, reglas) y no tiene datos personales ni reservados, replícalo con
     `python herramientas/extraer_entrada.py proyectos/<slug> --replicar <id> ...`; si no, déjalo solo con ficha.
     Registra la decisión en `registro-de-alta.md`.
   - **Si una categoría quedó mal** (por ejemplo, un CV clasificado como informe), borra su réplica de `fuentes/` antes
     de cualquier commit. El control de Git bloquea las réplicas marcadas `confidencialidad: sensible`.
   - Ordena la estructura de las réplicas clave (títulos y tablas) sin cambiar el contenido, y completa `original:` con
     el enlace a la carpeta oficial si el usuario lo tiene.
4. Muestra al usuario un resumen breve: cantidad de archivos por categoría, rango de fechas, cuántos quedaron
   replicados y problemas (escaneos sin texto, formatos no soportados, duplicados). No esperes respuesta si no hay
   bloqueos: sigue.
5. **Escaneos sin texto** (el inventario los lista en «Requieren atención» con instrucciones): pide al usuario pasarlos
   por OCR (Word o Google Drive lo hacen, en dos clics) y dejar el resultado en la misma carpeta o en `ocr/`; al
   volver a procesar, el harness une ambas versiones y se queda con la de más texto. Si el documento es corto y puedes
   leer imágenes, puedes transcribirlo tú en la réplica (marca `calidad: parcial` y «transcripción desde imagen»).
   Si un PDF trae texto pero con errores evidentes (palabras cambiadas de forma sistemática), avísalo: también conviene
   pasarlo por OCR de nuevo.
6. Categorías que importan para la postulación: `bases` y `formulario` entran al barrido de requisitos; `normativa`
   (leyes, decretos) y `charla` (capacitaciones, transcripciones) se replican pero no se barren por defecto, y lo dicho
   en una charla no es vinculante. Corrige en `inventario.csv` las categorías evidentes antes de barrer.

## Fase C — Lectura y extracción
Lee los textos de `_procesado/texto/` en este orden, aplicando `lectura-por-tipo.md`:
1. Contractuales (contrato → anexos → enmiendas, en orden cronológico) · 2. Cronogramas · 3. Reportes y planillas de control
más recientes · 4. Plantillas · 5. Actas y minutas · 6. Propuestas · 7. Correos · 8. Chats de IA · 9. Otros.

Mientras lees, anota cada dato relevante en `_entrada/_procesado/hechos.md`, agrupado por bloque de
`cobertura.md`, con formato: `- dato: valor — fuente: F003 pág. 4 / cláusula 7 — fecha del documento`.
No escribas todavía en los archivos del proyecto: primero se consolida.

Volumen grande: lee completos los contractuales y el cronograma; de las series de reportes, lee completos
los 2 o 3 más recientes y de los anteriores solo títulos y cifras clave; de correos y chats, extrae solo
decisiones, acuerdos, riesgos, cambios, personas y fechas. Si tu entorno permite subagentes, puedes
delegar la lectura de grupos de documentos en paralelo: usa el subagente `lector-documental` (uno por grupo
de 5 a 10 documentos, en paralelo) y consolida sus hechos en `hechos.md`.

## Fase D — Consolidar y decidir
1. Para cada dato de `cobertura.md`, elige el valor según `reglas-de-decision.md`.
2. Registra cada decisión relevante en `contexto/registro-de-alta.md` (plantilla en la sección final):
   dato, valor elegido, fuente, alternativas descartadas y por qué, confianza (alta / media / baja).
3. Clasifica cada punto:
   - **Decidido** (confianza alta) → se aplica.
   - **Decidido, revisar** (confianza media) → se aplica y queda marcado para revisión del usuario.
   - **Pregunta** → solo si es crítico y con confianza baja, o hay una contradicción que las reglas no resuelven,
     o falta un dato crítico sin valor por defecto razonable.

## Fase E — Configurar el proyecto (sin pedir permiso punto por punto)
Aplica todo lo decidido. Siguiendo los criterios de las skills correspondientes, pero sin sus pasos de
confirmación individual (el usuario revisará el registro de alta):
- `proyecto.yaml` (todos los bloques) y `CLAUDE.md` del proyecto (frase, reglas del cliente, estilo).
- `contexto/`: alcance, subproyectos, dependencias, glosario, `stakeholders.csv`.
- `cronograma/cronograma.csv` y copia en `cronograma/linea-base/AAAA-MM-DD.csv`; genera el Gantt.
- `riesgos/riesgos.csv`, `riesgos/issues.csv`, `seguimiento/acuerdos.csv`, `seguimiento/decisiones.csv`.
- Capa contractual: fichas, registro de documentos, línea base vigente, registro de cambios (criterios de
  `registrar-documento` y `control-cambios`). Los originales se mueven a su carpeta como `original.<ext>`.
- Catálogo de reportes: una definición por cada serie de reportes detectada y por cada plantilla, con el
  nombre propio que tenga en el proyecto (criterios de `nuevo-tipo-reporte`); las plantillas se copian a
  `reportes/plantillas/`; la última versión de un Excel acumulativo se copia como primer emitido.
- Métricas: si los documentos muestran indicadores que se siguen periódicamente, defínelos en
  `metricas/metricas.yaml` y registra sus valores históricos en `mediciones.csv` (criterios de la skill `metricas`).
- Estilo y autoría: completa `contexto/estilo.md` analizando 2 o 3 documentos escritos por el usuario o su
  organización (no por terceros): tono, largo de párrafos, vocabulario y puntuación. Completa `autoria.nombre` y
  `autoria.organizacion` en `proyecto.yaml` (por defecto, el responsable). Si las bases o contratos exigen
  declarar el uso de herramientas de IA, regístralo como requisito y pregúntalo en la fase F.
- Marca: el logo más probable (desde `08-marca` o las imágenes extraídas de encabezados) a `marca/logo.png`;
  colores y fuente desde las plantillas si se pueden identificar.
- Minutas relevantes: guárdalas en `minutas/` con el formato del harness (solo las del último trimestre o las de comité).

Informa el avance al usuario en una línea por grupo terminado.

Si el bloque 7 (estado actual: avance, riesgos, problemas, acuerdos) queda sin cubrir porque los documentos no lo
traen o son antiguos, agrega en la fase F las preguntas de la **entrevista de estado** de `nuevo-proyecto` (sección
4b) solo para lo que falte, y registra las respuestas con fuente "entrevista con <responsable>, AAAA-MM-DD".

## Fase F — Preguntas (un solo mensaje)
Reúne todas las preguntas en un mensaje, **máximo 12**, ordenadas por criticidad. Cada una con una
propuesta: "Propongo X porque <fuente>. ¿Confirmas o corriges?". Agrega al final: "Si no respondes alguna,
quedará con la propuesta y marcada para revisión." Aplica las respuestas.

## Fase G — Verificar y entregar
1. `python herramientas/validar_proyecto.py proyectos/<slug>` y corrige lo que sea error de carga (no del proyecto).
2. Genera un reporte semanal de prueba de la semana actual con `generar-reporte` (usa la información más
   reciente; márcalo "PRUEBA" en el título).
3. Escribe `contexto/informe-de-alta.md`:
   - El programa en 10 líneas (lo que entendiste).
   - Cobertura por bloque: tabla con bloque, estado (Completo / Parcial / Pendiente) y confianza.
   - Decisiones marcadas para revisión (enlaza al registro de alta).
   - Pendientes y qué documento los resolvería.
   - Hallazgos de la validación que requieren gestión (atrasos, riesgos sin plan, etc.).
   - Próximos pasos sugeridos.
4. Pide al subagente `revisor-independiente` que revise `informe-de-alta.md` y `registro-de-alta.md` contra
   los documentos; incorpora sus observaciones.
5. Actualiza `induccion` en `proyecto.yaml` (estado, bloques completos, pendientes, fecha).
6. Archiva lo procesado: `python herramientas/extraer_entrada.py proyectos/<slug> --archivar`. Mueve cada
   archivo a `_entrada/_archivo/AAAA-MM-DD/<subcarpeta de origen>/` (siguen siendo locales y no se suben) y
   deja intactas las subcarpetas `01-` a `09-` para el próximo material. No muevas carpetas completas a mano.
7. Escribe `estado: terminada` en `avance-alta.md` y ejecuta `guardar-cambios`.
8. Entrega al usuario un resumen corto: qué quedó configurado, cuántas decisiones tomaste y cuántas marcaste
   para revisar, pendientes críticos, y dónde leer el informe completo.

## Material nuevo después del alta
Cuando el usuario deje más archivos en `_entrada/` y pida procesarlos: fase B (incremental), C solo con lo
nuevo, D comparando contra lo ya configurado (lo nuevo y formal prevalece según las reglas), E aplicando
diferencias, y un resumen de cambios. Para un solo documento contractual basta `registrar-documento`.

## Plantilla de `contexto/registro-de-alta.md`
```markdown
# Registro de decisiones del alta — <proyecto>
Fecha: AAAA-MM-DD · Documentos procesados: N

| # | Dato | Valor elegido | Fuente | Alternativas descartadas | Confianza | Revisar |
|---|---|---|---|---|---|---|
| 1 | Fecha de término | 30-04-2027 | F002 Enmienda N°1, cl. 2 | 31-03-2027 (F001 contrato, reemplazado) | alta | |
```
