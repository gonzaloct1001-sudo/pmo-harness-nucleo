# Reglas: datos del proyecto

Detalle de los principios 1, 2, 3, 5, 7 y 16 del mapa (`AGENTS.md`). Léelo cuando la tarea cree o modifique datos
del proyecto (CSV, YAML, Markdown de registro).

## Contrato común (todos los proyectos)
- `proyecto.yaml` → identidad, `arquetipos`, gobierno, formato, umbrales, estado del alta.
- `metricas/metricas.yaml` (propias) y `metricas/metricas-<arquetipo>.yaml` (de los arquetipos) → definiciones
  y reglas · `metricas/mediciones.csv` → valores.
- `reportes/catalogo/` → reportes del proyecto · `riesgos/` · `seguimiento/` (decisiones, acuerdos, traspaso) · `contexto/`.
- `fuentes/` → réplicas fieles en Markdown de las bases y documentos de definición (ver `reglas/confidencialidad.md`):
  permiten trabajar en cualquier computador sin los originales.
Gracias a esto, reportes, consistencia, riesgos y reuniones funcionan igual en cualquier tipo de proyecto.

## Principios
1. **La fuente de verdad son los datos del proyecto** (`.yaml`, `.csv`, `.md`). Word, Excel y PowerPoint son salidas:
   se regeneran desde los datos; nunca se corrige «a mano» una salida para tapar un dato.
2. **Nunca inventes datos.** Si falta algo, escribe `[PENDIENTE: qué falta]` y avísalo al final. Un dato supuesto
   para poder avanzar se marca como supuesto y queda en las decisiones pendientes del usuario.
3. **Distingue hechos de estimaciones.** Marca como "estimado" lo que no venga de una fuente; en documentos de
   salida, la estimación se dice como tal.
5. **Fechas:** en archivos de datos `AAAA-MM-DD`; en documentos de salida, el formato de `proyecto.yaml`
   (`formato.formato_fecha`). **Porcentajes** en datos como fracción (0,15 = 15%). Montos sin separador de miles en
   datos; el formato de salida lo pone la plantilla.
7. **Registros CSV:** conserva columnas y su orden (se pueden agregar columnas al final). UTF-8, coma, una fila por
   registro, ids estables (nunca se reutiliza un id borrado). El esquema de cada registro está en la plantilla del
   arquetipo (`arquetipos/<nombre>/estructura/`).
16. **Valida cada CSV o YAML que edites.** Claude Code lo hace solo (hook `validar_edicion`). En otras herramientas
    ejecuta después de editar `python herramientas/hooks/precommit.py --archivos <ruta>`; además, el control de Git lo
    revisa todo antes de cada commit. Un registro que no valida no se da por hecho.
