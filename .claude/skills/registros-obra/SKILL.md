---
name: registros-obra
description: Registros de obra y proyectos de ingeniería en terreno — consultas técnicas (RFI), no conformidades, inspecciones, estados de pago y libro de obra — más el control de avance físico y financiero con valor ganado y ruta crítica. Úsala en proyectos de construcción, montaje u obras cuando el usuario mencione una consulta técnica, una observación de la inspección, una no conformidad, una inspección, un estado de pago, el libro de obra, o pida el avance físico-financiero, la ruta crítica o el pronóstico de término.
---

# Registros de obra

Carpeta `obra/` (arquetipo `obra`, junto con `ejecucion`).

## RFI (consultas técnicas)
Registra en `obra/rfi.csv` con emisor, destinatario, tema, pregunta y **plazo de respuesta** (por defecto el
del contrato o 5 días hábiles). Al responderse, registra fecha, respuesta e **impacto** (costo, plazo o
ninguno). Si hay impacto, sugiere `control-cambios`.

## No conformidades
En `obra/no-conformidades.csv`: partida, descripción objetiva, severidad (crítica / mayor / menor),
responsable, acción correctiva y fecha de compromiso. Se cierran solo con evidencia de la corrección
(registro de inspección o foto referenciada). Las críticas se informan de inmediato al responsable del proyecto.

## Inspecciones
Programa en `obra/inspecciones.csv` (tipo, partida, inspector, fecha). Registra el resultado (aprobada /
observada / rechazada) y, si es rechazada, crea la no conformidad y programa la reinspección.

## Estados de pago
En `obra/estados-pago.csv`: período, monto presentado, **avance declarado**, monto aprobado, fechas de
aprobación y pago, retención. Antes de presentar, verifica que el avance declarado coincida con el
cronograma (el validador alerta diferencias sobre 5 puntos) y que el acumulado no supere el contrato
vigente (`contractual/linea-base-vigente.md`).

## Libro de obra
Resumen diario en `obra/libro-de-obra.md` a partir de lo que informe el usuario: clima, personal,
actividades, incidentes. Los incidentes de seguridad o calidad generan también su registro correspondiente.

## Avance físico-financiero
`python herramientas/evm_cpm.py <proyecto> [--fecha AAAA-MM-DD] [--registrar]`: valor ganado (requiere `costo_plan` y
`costo_real` por tarea en el cronograma), ruta crítica y término pronosticado. Explícalo en simple:
SPI < 1 = atraso; CPI < 1 = sobrecosto; tareas críticas = las que no pueden atrasarse sin mover el término.
Revisión general: `validar_proyecto.py` (RFI vencidas, no conformidades, inspecciones, coherencia de estados de pago).
