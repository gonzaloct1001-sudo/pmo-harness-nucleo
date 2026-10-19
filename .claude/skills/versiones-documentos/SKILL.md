---
name: versiones-documentos
description: Compara documentos y lleva la bitácora de versiones — compara dos versiones del mismo documento (o dos documentos distintos) separando cambios sustantivos de cambios de forma, registra cada nueva versión con su resumen de cambios, y responde qué cambió entre versiones o cuál es la vigente. Úsala cuando el usuario reciba o emita una nueva versión de un documento (propuesta, bases, especificación, contrato en negociación, informe en revisión), pida comparar documentos o versiones, pregunte "qué cambió", o quiera el historial de un documento.
---

# Versiones y comparación de documentos

Herramienta: `python herramientas/comparar_documentos.py <anterior> <nuevo> [--salida archivo.md]`
(PDF, Word, Excel, PowerPoint, correos, texto). Marca como POSIBLE CAMBIO SUSTANTIVO lo que altera cifras,
fechas, montos o palabras de obligación. La clasificación final es tuya, con criterio.
Si un original no está en este computador (no se suben a Git), compara sus réplicas fieles de `fuentes/`.
**Lineamientos del directorio:** cada versión nueva se compara con la anterior; los cambios sustantivos (definiciones,
ajustes al objetivo, prioridades) se registran en `seguimiento/decisiones.csv` y se proponen para el próximo informe
de avance.

## Comparar (sin registrar)
1. Ejecuta el script y lee el resultado.
2. Clasifica cada cambio:
   - **Sustantivo**: altera alcance, plazos, montos, obligaciones, responsabilidades, riesgos, criterios o supuestos.
   - **Forma**: redacción, orden, formato, correcciones menores sin efecto.
3. Responde con: resumen en 3 líneas, tabla de cambios sustantivos (qué decía, qué dice, implicancia para
   el proyecto) y una línea con la cantidad de cambios de forma. Si comparas documentos distintos
   (ej.: propuesta vs contrato), enfoca en diferencias de compromisos.
4. Cruza los cambios sustantivos con los datos del proyecto: ¿contradicen la línea base, el cronograma,
   una regla o un acuerdo? Si corresponde, sugiere `control-cambios`, `riesgos-issues` o `registrar-documento`.

## Registrar una nueva versión
1. Identifica el documento (`doc_id` corto y estable, ej.: `propuesta-tecnica`, `bases-licitacion`). Si es nuevo,
   crea `documentos/<doc_id>/`.
2. Guarda el archivo como `documentos/<doc_id>/vNN_<nombre-original>` (NN correlativo: v01, v02…).
   Los originales no se suben a Git (ya está en `.gitignore`).
3. Si hay versión anterior, compara y guarda el resultado en `documentos/<doc_id>/cambios_vNN.md`, con tu
   clasificación agregada al inicio (resumen y tabla de cambios sustantivos).
4. Agrega la fila a `documentos/bitacora-versiones.csv`: versión, fecha del documento, archivo, hash
   (primeros 16 caracteres del SHA-256), origen (quién lo envió o emitió), autor, resumen de cambios en una
   línea, cantidad de cambios sustantivos, versión con que se comparó.
5. Si la versión cambia algo que el proyecto usa (alcance, fechas, montos, criterios), propone las actualizaciones.

## Consultas
- "¿Qué cambió entre la v2 y la v4?" → compara directamente esas versiones (no sumes comparaciones parciales).
- "¿Cuál es la vigente?" → la última registrada, salvo que la bitácora indique otra cosa en `comentario`.
- "Historial de X" → tabla desde la bitácora.
