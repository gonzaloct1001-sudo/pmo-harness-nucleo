# Después de la reunión: la minuta

Referencia de la skill `reuniones`. Se aplica cuando el usuario entrega notas, transcripción, resumen de audio o correo de una reunión ya hecha y quiere la minuta formal, con acuerdos, decisiones y riesgos llevados a los registros del proyecto.


## Pasos
1. Identifica el proyecto y lee `contexto/stakeholders.csv` (para normalizar nombres y cargos).
2. Formato, en este orden («lo tuyo primero»): `minutas/_formato.md` del proyecto; si no, `empresa/formatos/minuta.md`
   (el esqueleto del formato propio de la empresa, adoptado con `adoptar-formatos`); si no, `references/formato-minuta.md`.
   Si existe `empresa/plantillas/minuta.docx` (o la del proyecto), el Word del paso 8 sale con `llenar_docx.py` sobre
   esa plantilla, no con `md_a_docx.py`.
3. Extrae de las notas: datos de la reunión, asistentes, temas tratados, acuerdos, decisiones, riesgos o
   problemas mencionados y próxima reunión.
4. Para cada acuerdo exige responsable y fecha. Si faltan, marca `[PENDIENTE: responsable]` o
   `[PENDIENTE: fecha]` y pregúntalo al final. No asignes responsables por deducción.
5. Si un asistente no está en stakeholders, pregunta si se agrega.
6. Guarda la minuta en `minutas/AAAA-MM-DD_<tema-corto>.md`.
7. Propón (y aplica tras confirmar):
   - acuerdos → `seguimiento/acuerdos.csv` (id correlativo A-001…, origen = nombre del archivo de la minuta)
   - decisiones → `seguimiento/decisiones.csv` (D-001…)
   - riesgos o problemas → vía `riesgos`
   - solicitudes de cambio → vía `control-cambios`
8. Si el usuario lo pide o el catálogo lo define, genera el Word con `herramientas/md_a_docx.py` y/o un
   borrador de correo breve para enviar la minuta a los asistentes.

## Reglas
- Redacta los acuerdos como acciones verificables: "Andrés Muñoz enviará el listado de interfaces (02-10-2026)".
- Separa lo acordado de lo simplemente conversado. Ante la duda, pregunta.
- No incluyas comentarios personales ni juicios sobre personas.
