---
name: actualizar-gantt
description: Actualiza el cronograma o carta Gantt de un proyecto (avance de tareas, fechas reales, nuevas tareas, dependencias, hitos), lo importa desde MS Project (XML) y regenera su visualización. Úsala cuando el usuario informe avances, atrasos, reprogramaciones, término o inicio de tareas, pida ver o actualizar la carta Gantt, o cuando una nota de seguimiento o minuta traiga información de avance.
---

# Actualizar cronograma

Fuente de verdad: `cronograma/cronograma.csv`. Columnas: id, subproyecto, tarea, responsable, inicio_plan,
fin_plan, inicio_real, fin_real, avance_pct (0–100), predecesoras (ids separados por coma), es_hito (si/no),
estado, comentario y, opcionalmente, costo_plan y costo_real (para valor ganado). Fechas `AAAA-MM-DD`.

## Pasos
1. Interpreta lo informado y arma una tabla de cambios propuestos: tarea, campo, valor actual → nuevo.
2. Reglas automáticas al proponer:
   - avance > 0 y sin `inicio_real` → propone `inicio_real`.
   - avance = 100 → propone `fin_real` y estado "terminada".
   - una tarea no debería avanzar si su predecesora no terminó: adviértelo, no lo bloquees.
3. **Cambios a fechas plan** (`inicio_plan`, `fin_plan`): son una reprogramación. Pregunta si hay un cambio
   aprobado que la respalde. Si el nuevo término supera `linea_base.fecha_termino_vigente` o mueve un hito,
   sugiere abrir una solicitud en `control-cambios`. Registra el motivo en `comentario`.
4. Tras confirmación, escribe el CSV conservando orden de filas y columnas, y actualiza
   `cronograma_actualizado: AAAA-MM-DD` en `proyecto.yaml` con la fecha a la que corresponde el avance informado
   (no la fecha de hoy si el avance es de otro día). Así los reportes comparan plan y real a la misma fecha.
5. Regenera la vista: `python herramientas/gantt_mermaid.py proyectos/<slug>`.
6. Ejecuta `validar_proyecto.py` y comenta solo los hallazgos nuevos relacionados con el cronograma.
7. Si hay dependencias o costos, ejecuta `python herramientas/evm_cpm.py proyectos/<slug> --registrar` (registra
   SPI, CPI y término pronosticado en `mediciones.csv` como parte de la actualización confirmada): informa si cambió la
   ruta crítica, el término pronosticado frente al contractual y, si hay costos, SPI y CPI.

## Línea base del cronograma
- Al aprobarse el cronograma inicial o una reprogramación formal, guarda una copia en
  `cronograma/linea-base/AAAA-MM-DD.csv`. Así se puede comparar plan original vs actual.
- Si el usuario pide "comparar con la línea base", usa la copia más reciente y lista tareas con fin_plan
  desplazado, en días.

## Importar desde MS Project
1. El usuario guarda el cronograma como XML desde MS Project (Archivo > Guardar como > tipo "XML"). Si trae un `.mpp`,
   pídele ese XML: el `.mpp` es binario y no se lee directo.
2. Vista previa (no reemplaza nada):
   `python herramientas/importar_msproject.py <archivo.xml> proyectos/<slug>` → `cronograma/importado-msproject.csv`.
   En un programa, reparte cada rama de primer nivel a su subproyecto con `--mapa "Rama=sp1,Otra rama=sp2"` (los
   subproyectos deben existir) y usa `--nivel-subproyecto` si las ramas están en otro nivel.
3. Muestra al usuario: tareas, hitos, costo total (debe coincidir con MS Project; si no, `--costos-sin-centavos`), las
   dependencias no fin-comienzo o con desfase (quedan en el comentario) y cómo quedó repartido.
4. Con su confirmación, repite con `--reemplazar` (respalda el cronograma anterior en `cronograma/respaldos/`) y, si
   quiere conservar la línea base de MS Project, `--linea-base`. Luego actualiza `cronograma_actualizado`, regenera el
   Gantt (o `programa.py` en un programa) y ejecuta `validar_proyecto.py`.
5. Para actualizaciones periódicas desde MS Project, repite el mismo proceso: el harness no edita el .mpp, MS Project
   sigue siendo la fuente del plan si así lo decide el usuario (déjalo escrito en el `CLAUDE.md` del proyecto).

## Importar desde otro formato
Si el usuario trae un Excel o una exportación de MS Project, mapea sus columnas a las del CSV, muestra
las 5 primeras filas convertidas para validar el mapeo y luego importa todo.

## En un programa con subproyectos
- Cada subproyecto tiene su cronograma en `subproyectos/<id>/cronograma/cronograma.csv`; el programa tiene el suyo para
  gestión e hitos contractuales. Actualiza el del subproyecto que corresponda (nunca mezcles tareas de dos).
- Dependencia con otro subproyecto: en `predecesoras`, `<id>:<tarea>` (por ejemplo `sp1:T04`); con el programa, `PRG:T02`.
- Después de actualizar, `python herramientas/programa.py <programa>` regenera el consolidado, el Gantt macro, el
  detallado y el del subproyecto, y avisa si una dependencia entre subproyectos quedó violada.
- Actualiza `cronograma_actualizado` en el `proyecto.yaml` del subproyecto.
