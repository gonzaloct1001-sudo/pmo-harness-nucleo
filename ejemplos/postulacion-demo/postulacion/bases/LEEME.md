# Bases de la convocatoria

Aquí va una **ficha por documento** de las bases (bases administrativas, técnicas, económicas, anexos,
formularios, aclaraciones y respuestas del foro), con nombre `<id>-<nombre>.md`:

```markdown
---
id: B01                 # B01 bases administrativas, B02 técnicas, AN01 anexo, AC01 aclaración, FR01 foro
titulo: ""
version: ""             # número o fecha de la versión
fecha: ""               # AAAA-MM-DD de publicación
vigente: si             # una aclaración puede dejar sin efecto partes de otro documento
modifica_a: []          # ids que modifica
original: ""            # ruta en _entrada/_archivo/ o enlace oficial
---
Resumen en 5 líneas, qué exige y qué cambia respecto de la versión anterior.
```

- Los originales se quedan en `_entrada/` (y luego `_entrada/_archivo/`): no se suben a Git.
- Cada nueva versión o aclaración: `versiones-documentos` para comparar, `extraer_requisitos.py` para barrer lo
  nuevo y `matriz-cumplimiento` para actualizar la matriz.
- **Las aclaraciones y respuestas del foro forman parte de las bases**: pueden agregar, cambiar o eliminar requisitos.
