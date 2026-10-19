# Modos de salida — detalle técnico

Si están instaladas las skills oficiales de documentos de Anthropic (docx, xlsx, pptx), síguelas además de
estas notas: tienen mejores prácticas de verificación. Si no, esto basta.

## Word sin plantilla (formato por defecto)
```
python herramientas/md_a_docx.py proyectos/<slug>/reportes/emitidos/<periodo>/<archivo>.md \
       proyectos/<slug>/reportes/emitidos/<periodo>/<archivo>.docx --proyecto proyectos/<slug>
```
El script aplica logo, colores, fuente, tamaño de página y pie de página de `proyecto.yaml`.
En tablas, escribir exactamente `Verde`, `Amarillo` o `Rojo` colorea la celda.
Conserva el `.md` junto al `.docx`: es el registro legible en Git.

## Word con plantilla del cliente
Convención recomendada para plantillas: marcadores `{{nombre_campo}}` en el texto.
```python
from docx import Document
doc = Document("plantilla.docx")
valores = {"{{semana}}": "2026-S39", "{{estado}}": "Amarillo"}
def reemplazar(parrafos):
    for p in parrafos:
        texto = "".join(r.text for r in p.runs)
        if any(k in texto for k in valores):
            for k, v in valores.items():
                texto = texto.replace(k, v)
            for r in p.runs[1:]:
                r.text = ""
            if p.runs:
                p.runs[0].text = texto
reemplazar(doc.paragraphs)
for t in doc.tables:
    for fila in t.rows:
        for celda in fila.cells:
            reemplazar(celda.paragraphs)
# también encabezados y pies: doc.sections[i].header.paragraphs
doc.save("salida.docx")
```
Para secciones de largo variable (listas de riesgos, tablas), ubica el párrafo del marcador y agrega
filas o párrafos después de él copiando su estilo. Si la plantilla no tiene marcadores, identifica las
secciones por sus títulos y avísale al usuario que conviene agregarle marcadores.

## Excel oficial o de terceros (planillas de CORFO, del GORE, de un cliente): `llenar_xlsx.py`
Abrir y guardar con openpyxl **borra** las listas desplegables modernas, las formas y cuadros de texto y otras
extensiones que estas planillas suelen tener; una planilla dañada puede ser rechazada. Para cualquier planilla que no
creó el harness (o si `inspeccionar_xlsx.py` muestra «no guardar con openpyxl»):
1. `python herramientas/inspeccionar_xlsx.py <archivo>` → hojas, celdas de entrada, fórmulas, hojas protegidas.
2. Escribe el mapeo en un YAML (hoja, celda y valor), con los datos del proyecto:
   ```yaml
   celdas:
     - {hoja: "1. Información General", celda: C3, valor: "Programa X"}
     - {hoja: "3. Matriz de Resultados", celda: M4, valor: 0.55}      # porcentajes como fracción (o "55%")
     - {hoja: "1. Información General", celda: F3, valor: 2026-01-15}  # fechas AAAA-MM-DD
   ```
3. `python herramientas/llenar_xlsx.py <planilla> --valores valores.yaml --vista-previa` → muestra qué cambiaría.
4. `python herramientas/llenar_xlsx.py <planilla> --valores valores.yaml --salida emitidos/<periodo>/<nombre>.xlsx`.
   Nunca escribe sobre fórmulas, hojas protegidas ni celdas ocultas de un rango combinado; verifica que todo lo demás
   quedó idéntico. El original no se toca. Guarda el YAML junto al emitido: es el registro de qué se escribió.
5. Informa al usuario las celdas escritas y las rechazadas (con el motivo).

## Excel creado por el harness en modo actualizar (planillas de control propias, acumulativas)
1. Ejecuta `python herramientas/inspeccionar_xlsx.py <archivo>` si no conoces el archivo o cambió. Si advierte
   elementos que se perderían, usa `llenar_xlsx.py` (sección anterior).
2. Si el archivo tiene vínculos a otros libros, **detente** y avisa: guardarlo con openpyxl rompe esos vínculos.
3. Edita solo las celdas del mapeo de la definición:
```python
from openpyxl import load_workbook
wb = load_workbook("archivo.xlsx")          # nunca data_only=True si vas a guardar
ws = wb["Avance"]
ws["E5"] = 0.55                             # porcentajes como fracción si la celda tiene formato %
wb.calculation.fullCalcOnLoad = True        # Excel recalcula al abrir
wb.save("archivo.xlsx")
```
4. Para `.xlsm` usa `load_workbook(..., keep_vba=True)`.
5. openpyxl no calcula fórmulas: si necesitas leer resultados, recalcula con LibreOffice
   (`soffice --headless --convert-to xlsx --outdir tmp archivo.xlsx`) y lee la copia con `data_only=True`.
6. Informa al usuario qué celdas cambiaste (hoja, celda, valor anterior → nuevo).

## PowerPoint
```python
from pptx import Presentation
prs = Presentation("plantilla.pptx")
for i, layout in enumerate(prs.slide_layouts):
    print(i, layout.name, [ph.placeholder_format.idx for ph in layout.placeholders])
```
Usa los layouts de la plantilla (no crees formas sueltas), llena los placeholders y elimina las
diapositivas de ejemplo de la plantilla. Gráficos simples: `slide.shapes.add_chart` con los datos del
cronograma. Máximo 6 viñetas por diapositiva.

## Autoría de archivos creados con python-docx, openpyxl o python-pptx
Esas librerías dejan su nombre en las propiedades del archivo ("python-docx", "openpyxl", "python-pptx") y, en
Word, partes heredadas de su plantilla genérica. `md_a_docx.py` y `modelo_economico.py` ya lo limpian. Todo
archivo creado o modificado con código propio debe pasar, antes de entregarse, por:
```
python herramientas/verificar_autoria.py <archivo> --proyecto proyectos/<slug> --corregir
```
Deja como autor a `autoria.nombre` (o `responsable.nombre`), fecha actual, sin miniatura, customXml,
comentarios ni caracteres invisibles. Los términos o marcadores que encuentre se corrigen en el texto.

## Revisión visual
```
soffice --headless --convert-to pdf --outdir /tmp/revision <archivo>
```
En Windows, `soffice` suele estar en `C:\Program Files\LibreOffice\program\soffice.exe`. Si no hay
LibreOffice, pide al usuario que abra el archivo y confirme que se ve bien.
