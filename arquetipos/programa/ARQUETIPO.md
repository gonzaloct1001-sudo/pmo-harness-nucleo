# Arquetipo: Programa (un contrato padre, varios subproyectos)

## Cuándo usarlo
Cuando se gestiona **un programa con un contrato general** (y sus enmiendas) que se ejecuta en **varios
subproyectos**, cada uno con su propio alcance, carta Gantt, presupuesto asignado, equipo, riesgos, minutas y
reportes, y además hay que ver y reportar **el programa completo**: Gantt macro, presupuesto macro, contingencia,
personas compartidas entre subproyectos y presentaciones generales.

Se combina con `ejecucion` (contrato, línea base, cambios y valor ganado a nivel programa). Cada subproyecto puede
usar además `agil`, `obra` u otro arquetipo. Un proyecto **sin relación** con el programa se crea aparte, como proyecto
independiente en `proyectos/<slug>/`.

## Estructura
```
proyectos/<programa>/
├── proyecto.yaml              contrato padre: identidad, gobierno, formato y marca comunes, línea base del programa
├── contractual/               contrato, enmiendas, cambios + afectaciones.csv (qué subproyecto afecta cada enmienda)
├── programa/
│   ├── subproyectos.csv       lista de subproyectos (id, nombre, carpeta, responsable, estado, peso)
│   └── recursos/              personas.csv y asignaciones.csv (una persona en uno o varios subproyectos, % de dedicación)
├── presupuesto/               presupuesto macro y por subproyecto: presupuesto.csv, modificaciones.csv, gastos.csv, pronostico.csv
├── cronograma/                tareas del programa (gestión, hitos contractuales); consolidado.csv, gantt-programa.md y gantt-detalle.md (generados)
├── reportes/                  reportes GENERALES del programa y plantillas y marca comunes
└── subproyectos/<id>/         cada subproyecto con lo suyo (hereda del programa lo que no define)
    ├── proyecto.yaml          programa: ../.. · objetivos · línea base del subproyecto (término, monto asignado)
    ├── cronograma/            su Gantt (puede depender de otro subproyecto: predecesora "SP2:T05")
    ├── riesgos/ seguimiento/ minutas/ contexto/ metricas/
    └── reportes/              reportes y plantillas PROPIOS del subproyecto (si no tiene, usa las del programa)
```

## Presupuesto
- `presupuesto.csv`: monto base por subproyecto y cuenta (usa `PROGRAMA` para lo que no pertenece a un subproyecto y
  la cuenta `CONTINGENCIA` para las reservas, del programa o de cada subproyecto).
- `modificaciones.csv`: cambios al presupuesto vigente. `enmienda` (cambia el total, con documento), `reasignacion` y
  `contingencia` (mueven dinero entre cuentas o subproyectos: filas con el mismo id que suman cero).
- `gastos.csv`: `comprometido` (órdenes de compra, contratos) y `real` (pagado o facturado). Al pagar un compromiso se
  registra el real y se libera el compromiso con un monto negativo del mismo documento.
- `pronostico.csv`: cuánto falta por gastar (estimación al término), por subproyecto y cuenta.
- `python herramientas/programa.py <programa> --excel` genera el control presupuestario en Excel con fórmulas
  (resumen por subproyecto y cuenta, contingencia, disponible, estimado al término y desviación).

## Enmiendas
Una enmienda modifica el contrato padre y puede afectar a uno, varios o ningún subproyecto. Cada efecto se registra en
`contractual/afectaciones.csv` (documento, subproyecto o PROGRAMA, tipo plazo | alcance | monto | hito, antes,
después) y se aplica: plazos y montos en el `proyecto.yaml` del subproyecto, montos en `presupuesto/modificaciones.csv`,
alcance en su `contexto/alcance.md`. `programa.py` avisa las afectaciones sin aplicar.

## Herramientas
- `python herramientas/programa.py proyectos/<programa> [--hoy AAAA-MM-DD] [--excel] [--registrar]`: consolida avance
  por subproyecto y del programa, términos frente a las líneas base, presupuesto y contingencia, personas
  sobreasignadas, afectaciones pendientes; genera el cronograma consolidado, el Gantt macro, el Gantt detallado y el
  Gantt de cada subproyecto.
- Cada subproyecto se valida como un proyecto: `validar_proyecto.py`, `evm_cpm.py`, `evaluar_metricas.py` sobre su carpeta.
- Ruta crítica del programa completo: `evm_cpm.py proyectos/<programa> --cronograma proyectos/<programa>/cronograma/consolidado.csv`.

## Skills
`gestionar-programa` (subproyectos, personas, presupuesto, contingencia, enmiendas por subproyecto, consolidación) ·
`nuevo-proyecto` (crea subproyectos dentro del programa o proyectos aparte) · `registrar-documento` (enmiendas con
afectaciones) · `actualizar-gantt` · `generar-reporte` (reportes generales del programa y por subproyecto).

## Preguntas de la mini entrevista
1. ¿Qué subproyectos tiene el programa y quién lidera cada uno?
2. ¿Monto del contrato y cómo se reparte entre subproyectos? ¿Hay contingencia (del programa o por subproyecto)?
3. ¿Qué personas trabajan en más de un subproyecto y con qué dedicación?
4. ¿Qué reportes y presentaciones son del programa completo y cuáles de cada subproyecto? ¿Tienen plantillas?
