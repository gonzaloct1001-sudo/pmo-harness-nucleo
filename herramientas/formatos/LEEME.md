# Formatos: contratos del núcleo

`contratos/` define, para cada tipo de documento que el harness produce sin un arquetipo específico (informe de
avance, minuta, presentación, carta, planilla de control), las **secciones mínimas** y de qué dato del harness sale
cada una. Los reportes propios de un arquetipo tienen su contrato en `arquetipos/<x>/estructura/reportes/catalogo/`.

`adoptar_formatos.py` usa estos contratos para comparar un formato propio de la empresa con lo que el harness sabe
llenar: qué sección falta en el formato del usuario (y qué se pierde si se omite) y qué sección propia el harness no
sabe llenar (queda como insumo manual, salvo que se la conecte a un dato).

Estos archivos son del núcleo: se actualizan con él. Lo adoptado por cada empresa vive en `empresa/formatos/`,
`empresa/plantillas/` y `empresa/reportes/catalogo/`, que ninguna actualización toca.
