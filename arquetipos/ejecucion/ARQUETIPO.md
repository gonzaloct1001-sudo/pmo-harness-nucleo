# Arquetipo: Ejecución por plan

## Cuándo usarlo
Proyectos con un alcance definido, un plan de tareas con fechas y dependencias, hitos y, a menudo, un
contrato: construcción de una casa, implementación de un sistema, un evento, una mudanza de oficinas.

## Qué agrega a la base
- `cronograma/` — tareas, hitos, dependencias, avance y líneas base (`cronograma.csv`).
- `contractual/` — contrato, anexos, enmiendas, propuestas, línea base vigente y control de cambios.
- Bloque `linea_base` en `proyecto.yaml` (fecha de término y monto vigentes).
- Columnas opcionales `costo_plan` y `costo_real` por tarea en el cronograma, para valor ganado.
- `metricas/metricas-ejecucion.yaml` — SPI, CPI, EAC, VAC, desviación del término pronosticado, holgura y tareas críticas
  (`python herramientas/evm_cpm.py <proyecto>`: valor ganado, ruta crítica y pronóstico de término).
- Reporte por defecto: `reporte-semanal` (estado, avance por subproyecto, riesgos, hitos, próximos pasos).
- Para obras y trabajo en terreno, combinar con el arquetipo `obra`; para desarrollo de software, con `agil`.

## Skills que lo usan especialmente
`actualizar-gantt`, `registrar-documento`, `control-cambios`, `generar-reporte`, `consistencia`.

## Métricas típicas (proponer según el caso)
| id | Métrica | Nivel | Dirección |
|---|---|---|---|
| avance_real | Avance real ponderado | proyecto | mayor_mejor |
| desviacion_avance | Avance real − plan (puntos) | proyecto | mayor_mejor |
| hitos_vencidos | Hitos vencidos sin cumplir | proyecto | menor_mejor |
| ejecucion_presupuesto | Gasto / presupuesto | proyecto | informativa |
| cambios_abiertos | Solicitudes de cambio sin resolver | proyecto | menor_mejor |

El avance se calcula desde el cronograma con `validar_proyecto.py`, y el valor ganado y la ruta crítica con `evm_cpm.py`.

## Preguntas de la mini entrevista
1. ¿Cuáles son las grandes etapas o subproyectos, y quién es responsable de cada uno?
2. ¿Fecha de inicio y de término comprometidas? ¿Hay contrato o presupuesto aprobado?
3. ¿Qué hitos son críticos (pagos, entregas, permisos, inspecciones)?
4. ¿Quién recibe reportes y cada cuánto?

## Particularidades por dominio (sugerencias para el generador)
- **Construcción:** etapas típicas (anteproyecto, permisos, obra gruesa, terminaciones, recepción final);
  riesgos de permisos, clima, proveedores y sobrecostos; control de estados de pago. La normativa y los
  permisos aplicables deben confirmarse con profesionales competentes.
- **Implementación de sistemas:** levantamiento, configuración, migración, pruebas, puesta en producción, estabilización.
