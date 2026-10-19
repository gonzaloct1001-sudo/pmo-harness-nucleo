---
name: nuevo-tipo-reporte
description: Incorpora un tipo de reporte nuevo al catálogo de UN proyecto, ya sea a partir de un archivo modelo (Word, Excel, PowerPoint) o diseñándolo por conversación desde cero ("quiero un reporte mensual que se llame X, en Excel, con estas hojas y estos datos"). Úsala cuando el usuario quiera crear, agregar, definir, configurar o modificar un reporte, informe, planilla, presentación o plantilla, con nombre propio o sin él, o deje un archivo modelo en _entrada diciendo que es un reporte periódico.
---

# Nuevo tipo de reporte

Resultado: una definición en `proyectos/<slug>/reportes/catalogo/<tipo>.md` y, si aplica, su plantilla en
`reportes/plantillas/`. **Todo queda en el proyecto, nunca en el núcleo del harness**: el nombre del reporte
(por ejemplo "PEP", "informe de gestión", "flash semanal") y su estructura son propios de ese proyecto.
Después basta con pedir "genera el <nombre> de <período>".

## Camino A — desde un archivo modelo
1. Analiza el archivo sin modificarlo:
   - xlsx/xlsm: `python herramientas/inspeccionar_xlsx.py <archivo>` → hojas, fórmulas, celdas de entrada, vínculos.
   - docx: títulos, tablas y marcadores `{{...}}` con python-docx.
   - pptx: layouts y placeholders con python-pptx.
2. Propón la definición (base: `reportes/catalogo/_plantilla-definicion.md`): modo `actualizar` si es un
   Excel acumulativo con fórmulas; `generar` si cada período es un documento nuevo. Mapea cada sección o
   celda a su fuente en el proyecto (cronograma, métricas, ítems, riesgos, seguimiento…) y marca como
   "insumo manual" lo que el harness no tiene.
3. Sigue en el paso común 4.

## Camino B — diseño por conversación (sin archivo)
1. Entiende en una o dos preguntas: nombre, para quién es y qué decisión apoya, cadencia, formato
   (Word, Excel, PowerPoint o Markdown). Si el usuario ya lo dijo, no preguntes.
2. Propón la estructura en una tabla: secciones (Word/PPT) u hojas y columnas (Excel), y para cada una qué
   contiene y de qué fuente del proyecto sale. Sugiere lo que suele faltar en ese tipo de reporte
   (resumen ejecutivo, semáforo, comparación con período anterior, próximos pasos).
3. Tras la confirmación, **construye la plantilla**:
   - Word: documento con la marca del proyecto (logo, colores, fuente), títulos de sección y marcadores
     `{{campo}}` donde van los datos.
   - Excel: libro con hojas, encabezados, **fórmulas** para todo lo calculable (totales, desviaciones,
     semáforos), celdas de entrada destacadas (fuente azul) y una leyenda. Si hay skill oficial xlsx
     disponible, síguela.
   - PowerPoint: plantilla con layouts coherentes y la marca del proyecto.
   - Markdown: no requiere plantilla; la definición basta.
4. Sigue en el paso común 4.

## Pasos comunes
4. Guarda la definición en el catálogo (`tipo` sin espacios, `nombre` visible con el nombre que eligió el
   usuario) y la plantilla en `reportes/plantillas/<tipo>.<ext>`.
   **¿Solo este proyecto o todos los de la empresa?** Si la carpeta tiene `empresa/` y el formato sirve para todos
   sus proyectos (por ejemplo, el informe de avance al directorio), pregúntalo en una línea. Si es común: guarda
   también la definición en `empresa/reportes/catalogo/` y la plantilla en `empresa/plantillas/`; los proyectos
   nuevos la reciben solos y a los existentes ofrécele copiarla.
5. **Prueba**: genera el reporte con `generar-reporte` para el período actual (o con datos de ejemplo
   marcados "PRUEBA" si aún no hay datos) y pide revisión. Ajusta según el feedback.
6. Si el reporte depende de métricas que el proyecto aún no tiene, ofrece crearlas con la skill `metricas`.
7. Sugiere `guardar-cambios`.

## Modificar un reporte existente
Edita la definición y la plantilla del proyecto; si ya hay emitidos, no los toques. Si el cambio altera la
estructura de un Excel en modo `actualizar`, aplícalo sobre el último emitido para no perder el historial.
