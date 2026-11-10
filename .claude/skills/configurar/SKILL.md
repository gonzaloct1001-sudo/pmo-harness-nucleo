---
name: configurar
description: Cambiar cualquier configuración del harness después de instalado, conversando y con confirmación — la empresa (nombre, responsable, autoría), la marca y el formato de los documentos, los formatos propios, el asistente de IA y los modelos por nivel, los umbrales de las métricas, la confidencialidad y las réplicas, el modo nube y sus tareas programadas, el status semanal local, las preferencias de investigación, los datos de un proyecto, el idioma y el formato de fechas. Úsala cuando el usuario diga «quiero cambiar…», «configura…», «ajusta…», «de ahora en adelante…», «ya no quiero…», «¿dónde se cambia…?», «vuelve a dejar…», o pregunte cómo deshacer un cambio.
---

# Configurar (cambiar algo después)

**Principio:** todo lo que se decidió al instalar se puede cambiar después, con una conversación corta y sin romper
nada. Cada ajuste vive fuera del núcleo (`empresa/`, `proyectos/`, `.harness/`), así que las actualizaciones no lo
tocan; y todo queda en Git, así que se puede deshacer.

## 1. Entender qué quiere cambiar
Si no está claro, muestra el menú en un mensaje y pide la letra:

| | Qué | Dónde vive | Cómo se cambia |
|---|---|---|---|
| A | La empresa: nombre, razón social, responsable, autoría de los documentos | `empresa/empresa.yaml` | Editas el campo y lo muestras |
| B | Marca y formato: logo, colores, fuente, pie de página, tamaño de hoja, formato de fecha | `empresa/empresa.yaml` (`formato`), `empresa/marca/` | Editas o `adoptar-formatos --marca` |
| C | Formatos propios: informes, minutas, presentaciones, plantillas | `empresa/_entrada/` → `adoptar-formatos` | Skill `adoptar-formatos` |
| D | Asistente de IA y modelos por nivel de capacidad | `.harness/asistentes.yaml`, `empresa/empresa.yaml` (`capacidad`) | `configurar-asistente`; editas `capacidad` |
| E | Métricas y umbrales (semáforos) | `proyectos/<slug>/metricas/*.yaml` | Skill `metricas` |
| F | Confidencialidad y réplicas: qué se replica en `fuentes/`, qué nunca se sube | `empresa/empresa.yaml` (`replicas`), `.gitignore` | Editas con confirmación; explicas el riesgo |
| G | Modo nube: activar, qué tareas, horarios, pausar, desactivar | `.harness/nube.yaml` y claude.ai/code | Skill `nube` (sección 6) |
| H | Status semanal en este computador (día y hora) | tarea programada del sistema | `agendar_status.py --dia --hora` / `--quitar` |
| I | Preferencias y ajustes de investigación | `empresa/investigacion/ajustes.yaml` | `investigacion.py --ajustar` / `--preferencia` |
| J | Un proyecto: nombre, cliente, responsable, umbrales, comité, reportes | `proyectos/<slug>/proyecto.yaml`, `reportes/catalogo/` | Editas; `nuevo-tipo-reporte` para reportes |
| K | Idioma y formato de fechas de los documentos | `formato.idioma`, `formato.formato_fecha` | Editas |
| L | Una regla de cómo trabajar («siempre…», «nunca…») | `proyectos/<slug>/CLAUDE.md` o `empresa/estilo.md` | Agregas la regla en palabras simples |
| M | Mejoras al harness mismo: ver lo anotado, entregarlo al mantenedor | `.harness/mejoras-nucleo.csv` | `mejoras.py --listar`; `--exportar` produce el archivo anonimizado que el usuario revisa y envía (nunca se edita el núcleo) |

## 2. Aplicar
1. Di en dos líneas qué vas a cambiar, dónde y qué efecto tiene («el logo nuevo saldrá en todos los documentos de la
   empresa desde ahora; los ya emitidos no cambian»). Pide el sí.
2. Haz el cambio (edición mínima; conserva comentarios y lo demás del archivo). Los YAML y CSV se validan solos al
   editarlos (hook) o con `precommit.py --archivos`.
3. Comprueba: `python herramientas/estado.py` y, si tocaste un proyecto, `evaluar_metricas.py` o `validar_proyecto.py`.
4. Registra la decisión si afecta a un proyecto (`seguimiento/decisiones.csv`) y ofrece `guardar-cambios`.

## 3. Deshacer
Todo está en Git: «vuelve a dejar el logo anterior» → `git log -- <archivo>` y restaurar ese archivo con
confirmación. Las actualizaciones del núcleo también se deshacen solas si algo falla.

## Qué no hacer
- No editar archivos del núcleo (`NUCLEO.txt` los lista): un cambio ahí se pierde al actualizar. Lo propio va en
  `empresa/`, `proyectos/` o en skills propias (`.claude/skills/<propia>/`).
- No cambiar `.claude/settings.json` por tu cuenta: dile al usuario qué línea agregar.
- No activar ni programar nada en la nube sin pasar por la skill `nube` y su sí.
