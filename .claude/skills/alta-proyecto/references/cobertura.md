# Mapa de cobertura del alta

Qué debe quedar cubierto al terminar el alta. Criticidad: **C** = crítico (si falta, se pregunta),
**I** = importante (si falta, valor por defecto y pendiente), **O** = opcional.

## Bloque 1 — Identidad
| Dato | Dónde se guarda | Fuente típica | Por defecto | Crit. |
|---|---|---|---|---|
| Nombre del proyecto/programa | `proyecto.nombre` | instalación, contrato | — | C |
| Cliente | `proyecto.cliente` | contrato | — | C |
| Proyecto o programa | `proyecto.tipo` | contrato, cronograma (¿varios subproyectos?) | proyecto | I |
| Descripción (1–2 frases) | `proyecto.descripcion`, `CLAUDE.md` | contrato (objeto), propuesta | — | I |
| Fecha de inicio | `proyecto.fecha_inicio` | contrato, acta de inicio, cronograma | — | I |
| Responsable y cargo | `responsable` | instalación | — | C |
| Confidencialidad | `proyecto.confidencialidad` | cláusulas de confidencialidad | alta | O |

## Bloque 2 — Gobierno y stakeholders
| Dato | Dónde | Fuente típica | Por defecto | Crit. |
|---|---|---|---|---|
| Sponsor | `gobierno.sponsor`, `stakeholders.csv` | contrato (contraparte), actas de comité | — | C |
| Quién aprueba decisiones, presupuesto y cambios | `gobierno.aprueba_decisiones` (y campos adicionales si se distinguen) | contrato, cláusula de modificaciones, actas | comité o sponsor | I |
| Comité (nombre, frecuencia) | `gobierno.comite` | actas | mensual | I |
| Stakeholders (cargo, organización, rol, poder, interés) | `contexto/stakeholders.csv` | actas (asistentes), correos, organigrama, reportes (destinatarios) | — | I |

## Bloque 3 — Alcance y estructura
| Dato | Dónde | Fuente típica | Por defecto | Crit. |
|---|---|---|---|---|
| Objetivo | `contexto/alcance.md` | contrato, propuesta | — | I |
| Subproyectos/módulos y responsables | `contexto/alcance.md` | cronograma, reportes, propuesta | SP0 Gestión | I |
| Dependencias | `contexto/alcance.md`, predecesoras del cronograma | cronograma, propuesta | — | O |
| Hitos y entregables | `alcance.md`, cronograma (`es_hito`) | contrato (hitos de pago), cronograma | — | I |
| Fuera de alcance | `alcance.md` | contrato, propuesta | — | O |
| Cronograma | `cronograma/cronograma.csv` + línea base | Gantt, MS Project, reportes | vacío | C |
| Glosario y siglas | `contexto/glosario.md` | todos | — | O |

## Bloque 4 — Línea base contractual
| Dato | Dónde | Fuente típica | Por defecto | Crit. |
|---|---|---|---|---|
| Documentos contractuales | `contractual/` + `registro-documentos.csv` | contrato, anexos, enmiendas, OC | — | I |
| Fecha de término vigente | `linea_base.fecha_termino_vigente`, `linea-base-vigente.md` | última enmienda o contrato | — | C |
| Monto vigente y moneda | `linea_base.monto_vigente`, `moneda` | última enmienda o contrato | CLP | I |
| Hitos de pago, multas, garantías, SLA | `linea-base-vigente.md` | contrato, anexos | — | I |
| Cambios en trámite o históricos | `contractual/cambios/` | correos, actas, enmiendas | — | I |

## Bloque 5 — Reportes y cadencia
| Dato | Dónde | Fuente típica | Por defecto | Crit. |
|---|---|---|---|---|
| Tipos de reporte emitidos (con su nombre propio en el proyecto) | `reportes/catalogo/` | series de reportes en `_entrada`, contrato (obligaciones de informar) | el del arquetipo | C |
| Formato, secciones, destinatarios, día de entrega | definición de cada tipo | reportes emitidos, correos de envío | ver `reporte-semanal.md` | I |
| Plantillas | `reportes/plantillas/` | plantillas o último emitido | formato por defecto | I |
| Umbrales de semáforo | `umbrales` | reportes (criterios usados) | 5 y 10 puntos | O |

## Bloque 6 — Marca y formatos
| Dato | Dónde | Fuente típica | Por defecto | Crit. |
|---|---|---|---|---|
| Logo | `marca/logo.png` | `08-marca`, encabezados de plantillas | sin logo | O |
| Colores, fuente | `formato` | plantillas, manual de marca | 1F3864 / Arial | O |
| Tamaño de página, pie de página | `formato` | plantillas | carta / confidencial | O |
| Reglas de estilo del cliente | `CLAUDE.md` del proyecto | correos, comentarios en reportes | — | O |

## Bloque 7 — Estado actual
| Dato | Dónde | Fuente típica | Por defecto | Crit. |
|---|---|---|---|---|
| Avance por tarea (ejecución) o métricas vigentes por ítem (cartera) | cronograma / `metricas/mediciones.csv` | último reporte, planilla de control, Gantt actualizado | 0 % / sin dato | C |
| Riesgos vigentes | `riesgos.csv` | reportes, actas, matriz de riesgos, correos, chats | — | I |
| Problemas abiertos | `issues.csv` | reportes, correos, actas | — | I |
| Acuerdos pendientes | `acuerdos.csv` | actas | — | I |
| Decisiones relevantes | `decisiones.csv` | actas, correos | — | O |
