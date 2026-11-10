---
name: adoptar-formatos
description: Adopta como formato por defecto las plantillas y archivos base propios de la empresa o de un cliente (informes, minutas, presentaciones, planillas, logo y marca) dejados en `_entrada/`: los analiza, dice qué les falta y qué se pierde, propone mejoras en copia y nunca modifica el original. Úsala con «adopta mis formatos», «así hacemos las minutas aquí», «usa nuestro logo», «nuestro formato».
---

> Reglas que aplican (léelas si no están en tu contexto): `reglas/trabajo.md`, `reglas/datos.md`, `reglas/entregables.md`, `reglas/confidencialidad.md`.

# Adoptar formatos propios («lo tuyo primero»)

**Regla:** toda salida del harness usa el formato del **proyecto** si lo tiene; si no, el de la **empresa**; si no, el
del **harness**. Esta skill carga los dos primeros niveles a partir de los archivos reales del usuario. Los originales
nunca se modifican; las mejoras son copias aparte; nada de lo adoptado lo toca una actualización del núcleo.

## 1. Recibir
- **Empresa** (lo normal): los archivos van en `empresa/_entrada/` (no se sube a Git). Si el usuario los menciona pero
  no están ahí, pídele que los copie (o cópialos tú si te da la ruta). Vale cualquier cosa que use hoy: informes,
  minutas, presentaciones, cartas, planillas de control, plan de cuentas, listas, guía de estilo, logo.
- **Proyecto** (formatos de un cliente o mandante): `proyectos/<slug>/_entrada/04-reportes-y-plantillas/` (y el logo
  en `08-marca/`). Es lo que `nuevo-proyecto` ya procesa; esta skill hace el análisis fino.

## 2. Analizar
`python herramientas/adoptar_formatos.py empresa` (o `proyectos/<slug>`). Por cada archivo dice, en simple:
- **qué es** (informe de avance, minuta, presentación, carta, planilla de control, un reporte de un arquetipo, o un
  archivo base que no es un reporte) y con qué confianza;
- **cuánto cubre** de lo que el harness sabe llenar para ese tipo (`herramientas/formatos/contratos/`);
- **qué le falta** y qué se pierde si se adopta tal cual («sin sección de riesgos, los riesgos no se reportan en este
  documento»);
- **qué sección propia** el harness no sabe llenar solo (queda como insumo manual, o se conecta a un dato);
- **la mejora propuesta**: para un Word, una copia `_v2` en `formatos/mejorados/` con las secciones que faltan y un
  marcador en cada una; para una planilla, el aviso de cómo se llena sin dañarla;
- **la marca** que trae (fuente, color de títulos, logo del encabezado).
El detalle queda en `formatos/analisis/F-nn.md` y el resumen en `formatos/registro.csv`.

Si un tipo quedó mal detectado: `--asignar F-nn=<tipo>` (`--tipos` lista los que existen). Si algo no se adopta:
`--descartar F-nn --quien "<nombre>"`.

## 3. Decidir con el usuario (una decisión por archivo, en dos líneas)
Muestra la tabla y pregunta, por archivo, con la respuesta exacta:
> «Informe mensual: le faltan Riesgos y Problemas. ¿Lo adopto **tal cual** (no se reportan ahí) o **mejorado** (los
> agrega al final con tu mismo estilo)?»

Explica una sola vez que el original no se toca y que la versión mejorada es una copia que puede abrir en Word
antes de decidir. Pregunta también si adopta la **marca** del documento (logo, fuente, color) para todos los
documentos: solo se aplica si `empresa.yaml` (o `proyecto.yaml`) todavía tiene los valores por defecto; si ya tenía
otra, se informa y no se cambia.

## 4. Aplicar
`python herramientas/adoptar_formatos.py empresa --aplicar --quien "<nombre>" [--mejorado F-01,F-03] [--marca]`
- Copia cada formato a `plantillas/<tipo>.<ext>` (original o mejorado, según lo decidido) y escribe su definición en
  `reportes/catalogo/<tipo>.md` con el mapeo «sección del harness → título en la plantilla». Si ya existía una
  definición, no la toca: dilo y ofrece revisarla con `reportes`.
- Una minuta deja además el esqueleto `formatos/minuta.md` (mismas secciones y orden): la skill `reuniones` lo usa.
- Un archivo base queda en `formatos/base/` hasta que un proyecto lo necesite (por ejemplo, el plan de cuentas en un
  proyecto de finanzas).
- Lo adoptado en la empresa llega solo a los proyectos nuevos (`crear_proyecto.py`); para los existentes, ofrece
  copiar la definición y la plantilla al proyecto que lo pida.

## 5. Usar
- Word: `reportes` llena la plantilla con `herramientas/llenar_docx.py` (marcadores y secciones por título,
  respetando estilos, viñetas y tablas de la plantilla). Excel: `llenar_xlsx.py`. PowerPoint: sus layouts.
- Si el usuario corrige algo del resultado («el título va en mayúsculas», «la tabla lleva una columna más»), ajusta
  la definición o la plantilla adoptada (no la original) y anota la regla en `estilo.md` si es de redacción.
- Cuando el usuario entregue un formato nuevo o una versión nueva de uno adoptado, repite desde el paso 2: el
  registro detecta el cambio por su huella y propone de nuevo; la plantilla anterior no se borra (queda `_f-nn`).

## Qué no hacer
- No modificar los archivos de `_entrada/` ni «arreglar» un formato sin que el usuario lo pida.
- No inventar secciones en un documento del cliente: si falta algo, se dice y se decide.
- No adoptar como formato de la empresa un documento de un cliente: ese va al proyecto.
