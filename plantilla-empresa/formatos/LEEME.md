# Formatos propios adoptados

`registro.csv` lleva cada formato o archivo base que la empresa entregó en `_entrada/`: qué es, a qué salida del
harness reemplaza, cuánto cubre, qué le falta, qué parte propia el harness no sabe llenar, si se adoptó el original
o la versión mejorada, y quién lo aprobó. `analisis/` guarda el detalle de cada uno.

Los archivos adoptados viven en `../plantillas/` (Word, Excel, PowerPoint) y sus definiciones en
`../reportes/catalogo/`. Los archivos base que no son reportes (plan de cuentas, listas, guías) quedan en `base/`
hasta que un proyecto los use. Lo administra `herramientas/adoptar_formatos.py` y la skill `adoptar-formatos`.
