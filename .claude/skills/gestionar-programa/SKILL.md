---
name: gestionar-programa
description: Gestiona un programa con contrato padre y varios subproyectos — agregar o cerrar subproyectos, asignar personas a uno o varios subproyectos con su dedicación, presupuesto macro y por subproyecto (base, modificaciones, compromisos, gastos, pronóstico), contingencia del programa y de cada subproyecto, enmiendas que cambian plazos, alcances o montos de subproyectos específicos, Gantt macro y por subproyecto, y estado consolidado. Úsala cuando el usuario hable del programa completo, de sus subproyectos, del presupuesto o la contingencia, de quién trabaja en qué, de una enmienda que afecta a un subproyecto, o pida la visión general, la carta Gantt macro o el control presupuestario.
---

# Gestionar programa

Arquetipo `programa` (guía en `arquetipos/programa/ARQUETIPO.md`). Estado consolidado en todo momento:
`python herramientas/programa.py proyectos/<programa> --registrar` (agrega `--excel` para el control presupuestario y
`--corte-actualizacion` si algún cronograma no está al día).

## Dónde va cada cosa
| Tema | Nivel | Archivo |
|---|---|---|
| Contrato, enmiendas, cambios, línea base del programa | Programa | `contractual/`, `proyecto.yaml` → `linea_base` |
| Qué subproyecto afecta cada enmienda | Programa | `contractual/afectaciones.csv` |
| Presupuesto macro y por subproyecto, contingencia, gastos, pronóstico | Programa | `presupuesto/` |
| Personas y dedicación | Programa | `programa/recursos/personas.csv`, `asignaciones.csv` |
| Lista de subproyectos | Programa | `programa/subproyectos.csv` |
| Objetivos, alcance, Gantt, riesgos, minutas, acuerdos, reportes propios | Subproyecto | `subproyectos/<id>/…` |
| Término y monto vigentes de un subproyecto | Subproyecto | `subproyectos/<id>/proyecto.yaml` → `linea_base` |
| Marca, formatos, plantillas y estilo comunes | Programa (heredan los subproyectos) | `proyecto.yaml` → `formato`, `reportes/plantillas/`, `contexto/estilo.md` |

Regla: nunca mezcles datos de dos subproyectos en el mismo registro de subproyecto; lo transversal va en el programa.

## Agregar un subproyecto
1. Pregunta lo mínimo: nombre, responsable, objetivos, término y monto asignados (y qué documento los fija), si usa
   otro arquetipo (ágil, obra) y si depende de otro subproyecto.
2. `python herramientas/crear_proyecto.py <id> --programa <programa> --arquetipos ejecucion[,agil] --nombre "<Nombre>"`
   (el id en minúsculas: sp1, erp, portal…). Queda registrado en `programa/subproyectos.csv`.
3. Completa su `proyecto.yaml` (objetivos, responsable, línea base), `contexto/alcance.md` y su cronograma
   (`actualizar-gantt`; dependencias con otros subproyectos como `sp1:T04`).
4. Agrega su presupuesto en `presupuesto/presupuesto.csv` (o como `enmienda` en `modificaciones.csv` si nace de una
   enmienda) y sus personas en `asignaciones.csv`. Si tiene reportes o plantillas propias, van en su `reportes/`
   (`nuevo-tipo-reporte` sobre la carpeta del subproyecto); si no, usa los del programa.

## Personas compartidas
- `personas.csv`: una fila por persona (capacidad_pct 100 = jornada completa).
- `asignaciones.csv`: una fila por persona y subproyecto (o `PROGRAMA`), con dedicación % y período. Una persona puede
  tener varias filas. `programa.py` suma por mes y avisa si alguien supera su capacidad.
- Al pedir "¿quién está en qué?" o "¿hay alguien sobrecargado?", responde con la dotación por subproyecto y las
  sobreasignaciones, y propone ajustes (fechas, dedicación, reemplazo). La decisión es del usuario.

## Presupuesto y contingencia
- **Base** (`presupuesto.csv`): por subproyecto y cuenta; `PROGRAMA` para lo común; cuenta `CONTINGENCIA` para reservas.
- **Modificaciones** (`modificaciones.csv`, con quién aprobó):
  - `enmienda`: cambia el total (documento de la enmienda obligatorio);
  - `reasignacion` o `contingencia`: mueven dinero entre cuentas o subproyectos, en filas con el mismo id que suman cero
    (por ejemplo −25 MM en `sp1/CONTINGENCIA` y +25 MM en `sp1/RRHH`). Pide el acta o correo que lo aprueba.
- **Gastos** (`gastos.csv`): `comprometido` (orden de compra, contrato) y `real` (pagado o facturado). Al pagar un
  compromiso, registra el real y libera el compromiso con el mismo monto en negativo y el mismo documento.
- **Pronóstico** (`pronostico.csv`): lo que falta por gastar por subproyecto y cuenta; sin pronóstico se asume el vigente.
- Después de cada cambio: `programa.py`. Si un subproyecto cambia su monto vigente, actualiza su `linea_base.monto_vigente`
  (el informe avisa si no cuadran). Confirma con el usuario antes de registrar gastos o movimientos.

## Enmiendas que afectan subproyectos
Al llegar una enmienda (`registrar-documento` para la ficha y la línea base del programa):
1. Lee qué cambia **para cada subproyecto**: plazo, alcance, monto, hitos. Registra una fila por efecto en
   `contractual/afectaciones.csv` (documento, fecha de vigencia, subproyecto o PROGRAMA, tipo, antes, después,
   descripción, aplicado = no).
2. Propón la aplicación y, con confirmación: plazos en el `proyecto.yaml` del subproyecto (y su cronograma si
   corresponde), montos como `enmienda` en `presupuesto/modificaciones.csv`, alcance en su `contexto/alcance.md` (con el
   historial), hitos en su cronograma; marca `aplicado = si`.
3. `programa.py` debe quedar sin afectaciones pendientes y sin descuadres entre contrato, presupuesto y subproyectos.

## Estado consolidado y reportes
- `programa.py` da el avance por subproyecto y del programa (ponderado por presupuesto, peso o duración según
  `programa_info.ponderacion_avance`), términos frente a cada línea base, presupuesto y contingencia, equipo y
  enmiendas pendientes, y genera `cronograma/gantt-programa.md` (macro), `gantt-detalle.md` y el Gantt de cada subproyecto.
- Ruta crítica del programa completo: la incluye el informe (usa el cronograma consolidado).
- **Reportes generales** del programa: catálogo del programa (`estado-programa` u otros con nombre propio).
  **Reportes por subproyecto**: catálogo de cada subproyecto. Ambos con `generar-reporte` sobre la carpeta que
  corresponda; un subproyecto sin plantilla propia usa la del programa.

## Qué no hacer
- No cambiar términos ni montos de un subproyecto sin un documento (enmienda, acta) que lo respalde.
- No registrar movimientos de contingencia sin aprobación.
- No mezclar un proyecto independiente con el programa: si no comparte contrato, va aparte en `proyectos/<slug>/`.
