---
tipo: nombre-del-reporte        # sin espacios; se usa en el nombre del archivo
nombre: Nombre visible del reporte
formato: docx                   # docx | xlsx | pptx | md
modo: generar                   # generar (desde plantilla o formato por defecto) | actualizar (edita el vigente)
plantilla: ""                   # ruta en reportes/plantillas/, vacío = formato por defecto
cadencia: semanal               # semanal | mensual | quincenal | a pedido
dia: ""                         # día en que toca: lunes…domingo, números del mes (1,15) o ultimo; vacío = la agenda no lo recuerda
periodo_archivo: semana         # semana (AAAA-Sxx) | mes (AAAA-MM)
destinatarios: []
fuentes: []                     # carpetas o archivos que alimentan el reporte
---

# Propósito
Para qué sirve este reporte y quién lo usa.

# Secciones
1. Sección — qué contiene y de qué fuente sale.

# Mapeo (solo xlsx/pptx en modo actualizar)
| Hoja / diapositiva | Celda o rango | Dato | Fuente |
|---|---|---|---|

# Reglas
- 

# Validaciones antes de entregar
- 
