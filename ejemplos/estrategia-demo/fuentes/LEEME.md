# Réplicas fieles de los documentos de referencia

Aquí queda, en Markdown, el **texto completo y fiel** de las bases y documentos de definición del proyecto (bases,
anexos, aclaraciones, lineamientos del directorio, contratos, actas e informes): `<id>-<nombre>.md`, con el mismo id
del inventario de `_entrada/` y las marcas `--- Página N ---` de los PDF.

- **Se sube al repositorio privado**: así cualquier computador y cualquier asistente de IA trabajan con el contenido
  completo sin necesitar los originales, que no se suben a Git.
- **No se replican** CVs, estados financieros ni datos personales: de esos queda solo la ficha. La política está en
  `replicas` de `empresa/empresa.yaml` (o de `proyecto.yaml`, si el proyecto la redefine).
- Cada réplica indica su `calidad` (`completa`, `parcial` si el original parece escaneado, `sin_texto`) y el campo
  `original` para el enlace a la carpeta oficial del documento.
- **Prevalece el original** ante dudas de interpretación, y para firmar, llenar formularios oficiales o ver elementos
  gráficos (planos, tablas complejas, timbres).
- Se ordena la estructura (títulos, tablas) sin cambiar el contenido. No se edita para "mejorarla": es una copia.
