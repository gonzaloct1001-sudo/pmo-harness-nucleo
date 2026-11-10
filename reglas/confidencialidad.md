# Reglas: confidencialidad e integridad

Detalle de los principios 6 y 14 del mapa (`AGENTS.md`). Léelo cuando entren documentos, se suba algo a Git o unas
bases hablen de inteligencia artificial.

6. **Confidencialidad:** `_entrada/`, originales contractuales, versiones originales de documentos, postulaciones de
   terceros, el banco de archivos (`contenidos/archivos/`), el material descargado de una investigación (`_crudo/`) y
   el paquete firmado (`entrega/final/`) no se suben a Git (`.gitignore`, el control de Git y, en Claude Code, el hook
   `proteger_confidenciales` lo resguardan). Tampoco credenciales, llaves ni archivos `.env`.
   **Réplicas:** de las bases y documentos de definición (bases, anexos, aclaraciones, lineamientos, contratos,
   actas, informes) se guarda una réplica fiel en Markdown en `fuentes/`, que sí se sube al repositorio privado: así se
   trabaja en otro computador sin los originales. De CVs, estados financieros y datos personales solo queda la ficha;
   su texto no sale del computador. La política (qué se replica completo y qué solo con ficha) está en `replicas` de
   `empresa/empresa.yaml` y un proyecto puede redefinirla. Una réplica marcada `confidencialidad: sensible` no pasa el
   control de Git.
   **Datos del cliente fuera del harness:** lo que se exporta para el mantenedor del núcleo (`mejoras.py --exportar`)
   sale anonimizado y el usuario lo revisa antes de enviarlo.
14. **Integridad.** Si unas bases, un contrato o una norma exigen declarar el uso de herramientas de IA, o lo
    restringen, es un requisito más: se registra en la matriz de cumplimiento, se avisa al usuario de forma destacada y
    la decisión es suya. Nunca se redacta una declaración falsa ni se oculta algo que se deba declarar; la declaración
    que exijan se redacta con veracidad y el archivo se lista en `autoria.excluir` (ver `reglas/entregables.md`).
