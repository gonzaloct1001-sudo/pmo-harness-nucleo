---
name: matriz-cumplimiento
description: Construye y mantiene la matriz de cumplimiento de una postulación o licitación — extrae todos los requisitos de las bases, anexos, formularios, aclaraciones y respuestas del foro (con barrido exhaustivo para no omitir ninguno), los clasifica (admisibilidad, técnico, económico, formal, declaración; excluyente o subsanable), asigna responsable y forma de cumplirlos, los verifica contra la propuesta y genera el checklist de entrega. Úsala cuando lleguen bases o una aclaración, cuando el usuario pregunte qué exige la convocatoria, qué falta para postular o si la propuesta cumple todo, y antes de entregar.
---

# Matriz de cumplimiento

Archivos: `postulacion/requisitos.csv` (matriz), `postulacion/barrido-requisitos.csv` (candidatos del barrido),
`entrega/checklist.md`. Columnas de la matriz: id, fuente (documento y sección/página), tipo
(admisibilidad | tecnico | economico | formal | anexo | declaracion), excluyente (si/no), subsanable (si/no),
texto_requisito, como_se_cumple, evidencia, responsable, estado (pendiente | en_curso | cumplido | no_aplica | riesgo),
verificado_por, comentario.

## 1. Barrido (red de seguridad)
`python herramientas/extraer_requisitos.py proyectos/<slug>` sobre el texto de todas las bases (incluidas
aclaraciones y foro). Es incremental: al llegar una aclaración, solo agrega lo nuevo.
- Por defecto barre las categorías `bases` y `formulario` del inventario. Si el inventario clasificó mal unas bases
  (por ejemplo, como `otro`), corrige su categoría en `_entrada/_procesado/inventario.csv` y vuelve a barrer.
- La **normativa** general (leyes, decretos) y las **charlas** se barren solo si hace falta:
  `--categorias bases,formulario,normativa,charla`. Lo que venga de una charla queda con `vinculante = no: confirmar
  por consulta`: si agrega o contradice algo de las bases, redacta la consulta formal en `postulacion/consultas.csv`
  y no lo incorpores como requisito hasta tener respuesta.
- Si el inventario avisa **escaneos sin texto** entre las bases, pide pasarlos por OCR antes de dar el barrido por
  completo: lo que exigen esos documentos todavía no está en la matriz.

## 2. Lectura completa y consolidación
1. Lee las bases completas en este orden: bases administrativas → técnicas → económicas → anexos y formularios →
   aclaraciones y foro (en orden de fecha). **Una aclaración posterior prevalece** sobre lo que modifica: actualiza
   el requisito afectado (fuente "B01 num. 5 modificado por AC01") y deja la versión anterior en el comentario.
2. Busca también requisitos **implícitos**: campos obligatorios de formularios, firmas que exigen los anexos, formatos
   de archivo, límites de extensión, vigencia de certificados, garantías y su forma de entrega.
3. Cada candidato del barrido termina `incorporado` (con `requisito_id`, puede ser el de un requisito existente) o
   `descartado` (con `motivo_descarte`: por ejemplo "hito del calendario", "regla de evaluación → pauta inversa",
   "información general"). No quedan `pendiente`.
4. **Excluyente o subsanable:** si las bases no lo dicen, trátalo como excluyente, márcalo en el comentario y agrega
   una consulta al foro si hay plazo.
5. Requisitos de **declaración** (declaraciones juradas, conflictos de interés, uso de herramientas de IA): van con
   tipo `declaracion` y responsable el postulante. Si las bases exigen declarar o restringen el uso de IA, actualiza
   `postulacion.declaracion_ia_exigida: si` y avísalo al usuario de forma destacada. La declaración es del postulante
   y se redacta con veracidad; su archivo se agrega a `autoria.excluir` para que la verificación de autoría no la bloquee.

## 3. Dueños y forma de cumplir
Cada requisito abierto tiene responsable y `como_se_cumple` concreto (qué documento, quién firma, cuándo).
Los documentos del banco (`contenidos/registro.csv` de la postulación y `empresa/contenidos/registro.csv`, el banco común
de la empresa) se revisan por vigencia a la fecha de cierre. Busca primero en el banco de la empresa: un certificado o un
CV que ya está ahí no se pide de nuevo.

## 4. Verificación contra la propuesta
- Técnicos: cada uno debe estar en `responde_a` de alguna sección de `propuesta/` o tener evidencia.
- Formales: límites de extensión (cuenta caracteres o páginas), formatos, nombres de archivo.
- Económicos: controles de `economico/controles.csv` (presupuesto_postulacion.py).
- Solo se marca `cumplido` con **evidencia** (sección, archivo, comprobante) y idealmente verificado por quien no lo preparó.

## 5. Checklist de entrega
Genera `entrega/checklist.md` a partir de la matriz (excluyentes primero, luego documentos y anexos, formato y envío),
manteniendo la estructura de la plantilla. Cada línea se marca `[x]` solo con evidencia; mientras quede un PENDIENTE,
`postulacion.py` no da la compuerta por cumplida.

## 6. Informar
Tabla breve: total de requisitos, cumplidos, excluyentes pendientes (con responsable y fecha), candidatos del barrido
descartados con su motivo, consultas sugeridas. Luego `python herramientas/postulacion.py proyectos/<slug> --registrar`.
