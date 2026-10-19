# Documentos con control de versiones

Documentos de trabajo que cambian en el tiempo y conviene seguir versión a versión
(propuestas, bases técnicas, especificaciones, informes en revisión, planes).

- `<doc-id>/vNN_<nombre>.<ext>` → cada versión recibida o emitida (los originales NO se suben a Git).
- `<doc-id>/cambios_vNN.md` → comparación de la versión NN con la anterior (sí se sube).
- `bitacora-versiones.csv` → registro de todas las versiones de todos los documentos (sí se sube).

Los contratos, anexos y enmiendas se gestionan en `contractual/` (arquetipo ejecución); si además se
quiere comparar versiones de un borrador de contrato, puede vivir aquí mientras se negocia.
