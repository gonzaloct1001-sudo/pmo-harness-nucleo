---
name: generar-reporte
description: Motor único para generar cualquier reporte del catálogo de un proyecto (reporte semanal o mensual, planillas de control, presentaciones de avance, informes a comité, revisiones de cartera, informes de estudio, o cualquier reporte con nombre propio definido en el proyecto). Úsala siempre que el usuario pida sacar, generar, preparar, actualizar o emitir un reporte, informe, estado de avance, planilla de seguimiento o presentación de un proyecto, aunque no diga la palabra "reporte" o use el nombre propio que tenga en ese proyecto (por ejemplo "prepara lo de esta semana", "actualiza la planilla de septiembre", "arma la ppt para el comité").
---

# Generar reporte

Todos los reportes salen del mismo proceso. Lo que cambia entre uno y otro está en su definición:
`proyectos/<slug>/reportes/catalogo/<tipo>.md`.

## 1. Identificar reporte y período
1. Determina el proyecto activo (ver `AGENTS.md`) y lee su `proyecto.yaml`.
2. Si el usuario no dijo qué reporte, lista los tipos del catálogo (ignora los que empiezan con `_`) y pregunta.
3. Lee la definición del tipo. Si no existe, ofrece crearla con `nuevo-tipo-reporte`.
   **Programas:** los reportes generales (todos los subproyectos) están en el catálogo del programa y usan
   `programa.py` como fuente; los de un subproyecto, en `subproyectos/<id>/reportes/catalogo/`. Si un subproyecto no
   tiene la plantilla que su definición pide, usa la de `reportes/plantillas/` del programa (misma marca y formato).
   **Empresa:** si el proyecto no tiene la plantilla, búscala en `empresa/plantillas/` (formatos comunes de la
   empresa). La marca, la autoría y el estilo que el proyecto no define vienen de `empresa/` (ya resueltos en
   `md_a_docx.py`; para el estilo, usa `contexto/estilo.md` del proyecto o, si está sin completar, `empresa/estilo.md`).
4. Determina el período: semana ISO `AAAA-Sxx` o mes `AAAA-MM` según `periodo_archivo`. Por defecto, el actual.
   Si hoy es lunes o martes y el reporte es semanal, pregunta si corresponde a la semana anterior.

## 2. Asegurar los insumos
1. Lee solo las fuentes listadas en `fuentes` de la definición.
2. Si falta la nota de seguimiento del período (`seguimiento/AAAA-Sxx.md`), **pídela** antes de seguir.
   Usa las preguntas de `seguimiento/_plantilla-semana.md`, en un solo mensaje breve. El usuario puede
   responder en bruto (viñetas, audio transcrito, texto pegado de correos). Ordena la respuesta y guárdala
   como `seguimiento/AAAA-Sxx.md` antes de continuar.
3. Si la nota trae información que cambia los registros (avance de tareas, riesgos nuevos, issues, decisiones,
   acuerdos), propón las actualizaciones siguiendo `actualizar-gantt` y `riesgos-issues`, pide confirmación y
   aplícalas **antes** de redactar, para que el reporte y los registros digan lo mismo.

## 3. Calcular
Según lo que tenga el proyecto (ver `arquetipos` en `proyecto.yaml` y las fuentes de la definición):
- Si el proyecto tiene scripts propios de cálculo, ejecútalos primero según la rutina de su `CLAUDE.md`.
- `python herramientas/evaluar_metricas.py proyectos/<slug> --hoy <fecha de corte>` → métricas, semáforos, reglas, etapas.
- `python herramientas/validar_proyecto.py proyectos/<slug> --hoy <fecha de corte> --corte-actualizacion` → avance del
  cronograma y hallazgos (proyectos de ejecución). `--corte-actualizacion` compara plan y real a la fecha de la última
  actualización del cronograma; si esa fecha es anterior al período, dilo en el reporte ("avance al DD-MM") o pide
  actualizar el avance antes de emitir.
- Según el arquetipo: `evm_cpm.py` (valor ganado, ruta crítica; con `--registrar` si el reporte usa sus métricas),
  `metricas_agil.py` (sprints, DORA), `puntaje_pauta.py` (evaluación).
Si hay hallazgos críticos, menciónalos al usuario: pueden cambiar el estado general del reporte.

## 4. Redactar y producir según formato y modo
Lee `references/modos-salida.md` para el detalle técnico de cada caso.

| formato | modo | Qué hacer |
|---|---|---|
| docx | generar, sin plantilla | Escribe el contenido en `emitidos/<periodo>/<tipo>.md` siguiendo las secciones de la definición y conviértelo con `herramientas/md_a_docx.py` |
| docx | generar, con plantilla | Copia la plantilla a `emitidos/<periodo>/` y reemplaza sus marcadores o secciones |
| xlsx | actualizar | Copia el último emitido (o la plantilla si es el primero) a `emitidos/<periodo>/` y actualiza **solo** las celdas del mapeo (típico de planillas de control acumulativas). **Planilla oficial o de terceros** (por ejemplo, el SSM de CORFO): siempre con `llenar_xlsx.py`, nunca con openpyxl |
| xlsx | generar | Crea la planilla desde la plantilla con openpyxl, usando fórmulas en vez de valores calculados |
| pptx | generar | Usa la plantilla y sus layouts con python-pptx; una idea por diapositiva |
| md | generar | Deja el `.md` en `emitidos/<periodo>/` |

Nombre de archivo: según `autoria.patron_nombre_archivo` de `proyecto.yaml` (por defecto `{tipo}_{periodo}`,
ej.: `reporte-semanal_2026-S39.docx`). Si ya existe, crea `_v2`, `_v3`… nunca sobrescribas un emitido.

**Redacción de entregables (autoría limpia):** el documento debe verse elaborado por el usuario.
- Sigue `contexto/estilo.md` del proyecto (tono, largo de párrafos, vocabulario), si existe.
- Nunca menciones el proceso de elaboración: ni las herramientas con que se redactó, ni "generado automáticamente",
  ni nombres de skills, scripts, rutas del repositorio o ids internos (F001, R-001 solo si el usuario los usa con su
  cliente). Si una norma o contrato exige declarar el uso de IA, esa declaración va aparte (regla 14 de `AGENTS.md`).
- Distingue hechos de estimaciones con lenguaje profesional ("estimado", "según información de…").
- Un `[PENDIENTE` impide emitir: pide el dato al usuario. `md_a_docx.py` se niega a generar si queda uno.
- Varía la estructura de las frases y evita muletillas; usa la puntuación habitual del usuario.

## 5. Validar antes de entregar
1. Aplica las validaciones de la definición.
2. Verifica que cada número del reporte coincide con su fuente (avance, fechas, montos).
3. Busca `[PENDIENTE` en el contenido y lístalos.
4. **Autoría:** `python herramientas/verificar_autoria.py <archivo> --proyecto proyectos/<slug>`. Si reporta
   errores de propiedades o partes ocultas, ejecuta de nuevo con `--corregir`; si reporta términos o marcadores,
   corrige el texto de origen y vuelve a generar. No entregues con errores.
5. Para docx/xlsx/pptx, si hay LibreOffice disponible, conviértelo a PDF y revisa visualmente la primera página.

## 5b. Revisión independiente (reportes importantes)
Para reportes a comité, cliente o mandante, pide al subagente `revisor-independiente` que revise el
documento contra los datos antes de entregarlo, y corrige lo que encuentre.

## 6. Entregar
Responde con: ruta del archivo, estado general (semáforo) en una línea, supuestos usados, pendientes,
y los registros que se actualizaron. Sugiere `guardar-cambios`.

## Qué no hacer
- No regeneres desde cero un Excel en modo `actualizar`: se pierden fórmulas, formatos y vínculos.
- No escribas en celdas con fórmula ni en hojas protegidas.
- No cambies la estructura de una plantilla del cliente (secciones, orden, logos) salvo que se pida.
- No incluyas información de otros proyectos.
