# Qué extraer de cada tipo de documento

## Contrato, anexos, enmiendas, órdenes de compra, bases
- Partes, fecha de firma, vigencia, objeto (→ descripción y alcance).
- Plazo: inicio, término; condiciones de prórroga.
- Precio: monto, moneda, reajustes, forma de pago, hitos de pago.
- Multas, garantías (boletas, vencimientos), niveles de servicio.
- Cláusula de modificaciones (→ quién aprueba cambios y cómo se formalizan).
- Obligaciones de informar (→ reportes exigidos, periodicidad, destinatarios).
- Contrapartes nombradas (→ stakeholders, sponsor, administrador de contrato).
- Siempre con referencia a cláusula o página.

## Cronograma o carta Gantt
- Tareas con id, subproyecto (nivel superior de la jerarquía), responsable, fechas plan, fechas reales, avance, predecesoras, hitos.
- Fecha de la versión (para saber si es la vigente). Si hay varias versiones, la más reciente es el cronograma actual y la primera aprobada es la línea base.
- MS Project exportado: la columna de nivel de esquema o la sangría indica jerarquía; los resúmenes no son tareas.

## Reportes emitidos (semanales, mensuales, comité)
- Identificar series: mismo tipo de documento con distintas fechas (→ un tipo en el catálogo por serie).
- Del más reciente: estado general, avance por subproyecto, riesgos, problemas, próximos hitos (→ estado actual).
- Estructura: secciones, orden, tablas, semáforo y sus criterios (→ definición del reporte).
- Destinatarios y día de emisión si aparecen (→ cadencia).
- Logo, colores y fuentes del encabezado (→ marca).

## Excel acumulativos (planillas de control, estados de avance)
- Hojas, celdas de entrada vs fórmulas (usar `inspeccionar_xlsx.py` sobre el original), qué se actualiza cada período.
- Cifras vigentes: avance, presupuesto, gasto (→ línea base y estado actual).
- Se tratan como reporte en modo `actualizar`; el más reciente pasa a ser el primer emitido.

## Plantillas
- Marcadores `{{...}}` o secciones fijas; layouts en PowerPoint; celdas de entrada en Excel.
- Logo y colores.

## Actas y minutas
- Asistentes con cargo (→ stakeholders; quienes asisten a comité suelen tener poder alto).
- Decisiones (→ decisiones.csv), acuerdos con responsable y fecha (→ acuerdos.csv; si la fecha ya pasó y no hay evidencia de cumplimiento, queda "abierto" y se marca para revisar).
- Riesgos y problemas mencionados, solicitudes de cambio.

## Propuestas y cotizaciones
- Alcance ofrecido vs contratado (diferencias útiles para futuros cambios), supuestos, exclusiones, equipo, precio ofertado.
- Una propuesta nunca prevalece sobre un contrato firmado.

## Correos
- Remitente y destinatarios (→ stakeholders), fecha.
- Acuerdos, aprobaciones, solicitudes de cambio, alertas, problemas.
- Tono y preferencias del cliente (→ reglas de estilo).

## Conversaciones con otras IA
- Considera solo las relacionadas con el proyecto (por nombres, cliente, términos del glosario).
- Extrae lo que el **usuario** afirmó como hecho (fechas, decisiones, problemas, personas). Lo que la IA
  sugirió no es un hecho del proyecto: úsalo como idea o riesgo candidato, con confianza baja.
- Útil para detectar documentos que el usuario elaboró (reportes, planes) y su formato preferido.

## Imágenes
- Logos: preferir el de mayor resolución y fondo transparente. Si hay logo del cliente y de la consultora, preguntar cuál o ambos (confianza media).
- Capturas de Gantt o tableros: extraer los datos visibles con confianza media.

## Bases de concursos, fondos y licitaciones (arquetipo postulacion)
- Si el material son bases para **postular** (no un contrato vigente), el proyecto es del arquetipo `postulacion`:
  sigue `preparar-postulacion` desde la etapa 1 en vez de la línea base contractual.
- Ejecuta `extraer_requisitos.py` y revisa cada candidato con `matriz-cumplimiento`: bases administrativas,
  técnicas y económicas, anexos, formularios, aclaraciones y foro (una aclaración prevalece sobre lo que modifica).
- Extrae: entidad, instrumento, plataforma, calendario completo (con hora de cierre), reglas de financiamiento
  (tope, aporte propio, parte pecuniaria, topes por ítem, gastos no financiables), criterios y ponderaciones,
  umbrales y desempate, garantías, formatos y límites de extensión.
- Si las bases exigen declarar el uso de herramientas de IA, o lo restringen, regístralo y pregúntalo en la fase F.

## Cronogramas de MS Project
- `.xml` de MS Project: `extraer_entrada.py` lo resume como tabla de tareas (con ramas, hitos, dependencias y recursos);
  para cargarlo al proyecto usa `importar_msproject.py` (vista previa, confirmación, `--reemplazar`; en un programa,
  `--mapa` por rama). Si trae línea base 0, ofrece guardarla con `--linea-base`.
- `.mpp`: no se lee directo; pide al usuario el XML (Archivo > Guardar como > XML) y regístralo como pendiente.
