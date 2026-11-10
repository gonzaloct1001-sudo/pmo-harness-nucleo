# Modo directorio: informe mensual y presentación

1. **Antes:** el período cerrado (`--cerrar`) o declarado preliminar; `--revisar` sin errores; `--registrar` hecho.
2. **Formato:** el de la empresa si está adoptado (`empresa/reportes/catalogo/informe-financiero-mensual.md` o
   `reporte-directorio.md` con su plantilla); si no, el del arquetipo. `reportes` arma el documento: Word con
   `llenar_docx.py` o `md_a_docx.py`, PowerPoint con la plantilla y sus layouts.
3. **Contenido, en este orden:** la respuesta primero (cómo le fue a la empresa y cuánta caja hay), luego los desvíos
   explicados con acción, el forecast del año con su versión, los indicadores con semáforo y las decisiones que se
   piden al directorio con la recomendación de la gerencia. Anexo: supuestos, reaperturas, cuentas sin mapear.
4. **Revisión:** `revisor-independiente` contrasta cada cifra con `--estados`; `verificar_autoria.py` en OK; nada de
   `[PENDIENTE`.
5. **Después:** las decisiones del directorio a `seguimiento/decisiones.csv`; lo que cambie el presupuesto o el
   forecast se refleja en su versión siguiente.
