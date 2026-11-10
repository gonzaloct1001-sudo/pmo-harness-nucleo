# Paquete ficticio de formatos propios

Material inventado de la «Cooperativa Agrícola Valle Sur» para probar la skill `adoptar-formatos`. Cópialo a
`empresa/_entrada/` y di «adopta mis formatos». Lo que debería pasar:

| Archivo | Tipo detectado | Qué debería decir el análisis |
|---|---|---|
| `Informe_Gestion_Mensual.docx` | informe-avance | Faltan **Riesgos** y **Problemas** (obligatorias) y «Decisiones requeridas» y «Presupuesto» (opcionales); «Indicadores de gestión» es sección propia (insumo manual); sin marcadores; propone `_v2` con las secciones que faltan; marca: fuente Calibri, color 7A1F1F, logo en el encabezado |
| `Acta_Reunion_Comite.docx` | minuta | Falta **Decisiones** (obligatoria) y «Próxima reunión» (opcional); «Compromisos» calza con Acuerdos |
| `Control_Presupuesto_2026.xlsx` | planilla-control | Hojas Presupuesto (con fórmulas) y Avance físico; modo `actualizar` |
| `Presentacion_Directorio.pptx` | presentacion | Cubre todas las secciones |
| `Plan_de_Cuentas.xlsx` | archivo-base | No es un reporte: se guarda en `empresa/formatos/base/` para cuando un proyecto lo use |
| `logo_valle_sur.png` | logo | Con `--marca` pasa a `empresa/marca/` si no hay otro |

Después de `--aplicar --mejorado F-01 --marca --quien "Nombre"`: plantillas en `empresa/plantillas/`, definiciones
en `empresa/reportes/catalogo/`, esqueleto `empresa/formatos/minuta.md`, y `empresa.yaml` con la fuente y el color
del informe (solo porque tenía los valores por defecto).
