# Propuesta

Una sección `.md` por capítulo del formulario o índice que exigen las bases, numeradas en el mismo orden
(`01-resumen.md`, `02-problema.md`, …). Se parte de `_plantilla-seccion.md`.

- El encabezado de cada sección declara qué requisitos (`REQ-…`) y criterios (`C…`) responde: así se verifica
  que ningún requisito ni criterio quede sin respuesta (`postulacion.py` informa las secciones sin trazabilidad).
- Respeta los límites de las bases (caracteres, páginas, formato) y escríbelos en `limite`.
- Redacta con `contexto/estilo.md` y sin marcas del proceso (ver principio de autoría limpia).
- El texto final se lleva al formulario de la plataforma o se convierte a Word (`md_a_docx.py`) y se verifica
  con `verificar_autoria.py` antes de entregarlo.
