# Reglas: entregables y formatos

Detalle de los principios 13, 15 y 22 del mapa (`AGENTS.md`). Léelo antes de generar un documento que salga de la
carpeta (Word, Excel, PowerPoint, PDF, Markdown de salida) y antes de un commit.

13. **Autoría limpia de los entregables.** Todo documento que se entrega sale a nombre del usuario (`autoria.nombre` o
    `responsable.nombre`; organización `autoria.organizacion` o `empresa.nombre`) y sin rastros del proceso:
    - en el texto, nunca menciones el proceso de elaboración (asistentes, "generado automáticamente", el harness,
      nombres de skills o scripts, rutas del repositorio, ids internos) ni dejes marcadores `[PENDIENTE`. Hablar de IA
      cuando es el **tema** del proyecto es legítimo (se permite con `autoria.terminos_permitidos`);
    - **excepción:** las declaraciones que exijan unas bases o un contrato (principio 14) se redactan con veracidad y
      el archivo se lista en `autoria.excluir`, igual que los documentos de terceros (cartas, certificados);
    - sigue `contexto/estilo.md` del proyecto (o `empresa/estilo.md`);
    - antes de entregar, `python herramientas/verificar_autoria.py <archivo> --proyecto proyectos/<slug>` debe dar OK
      (con `--corregir` limpia propiedades, partes heredadas y caracteres invisibles).
    Los archivos internos del harness (registros, informes de alta, definiciones, réplicas, traspasos) no están
    sujetos a esta regla.
15. **Commits:** mensajes en español, descriptivos, en una línea que diga qué se hizo; sin líneas de coautoría ni
    menciones a herramientas de IA. Un commit por tarea o hito, no uno por archivo.
22. **Lo tuyo primero.** Toda salida usa el formato del proyecto; si no, el de la empresa (`empresa/plantillas/`,
    `empresa/reportes/catalogo/`, `empresa/formatos/`); si no, el del harness. Los formatos propios se cargan con la
    skill `adoptar-formatos` (desde `empresa/_entrada/` o `proyectos/<slug>/_entrada/04-reportes-y-plantillas/`), que
    dice qué falta en el formato y qué el harness no sabe llenar; los originales nunca se modifican (las mejoras van
    en una copia `_v2`). Si el usuario dice «nuestro formato» y no está adoptado, ofrécelo antes de generar.
