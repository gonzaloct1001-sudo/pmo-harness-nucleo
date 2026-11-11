# Reglas: confidencialidad e integridad

Detalle de los principios 6 y 14 del mapa (`AGENTS.md`). Léelo cuando entren documentos, se suba algo a Git o unas
bases hablen de inteligencia artificial.

6. **Confidencialidad, en tres niveles.**
   **Nivel 1, se versiona:** los datos y registros del proyecto (`.yaml`, `.csv`, `.md`) y las salidas que se generan.
   **Nivel 2, réplica fiel:** de bases, contratos y actas queda su texto en `fuentes/` (repositorio privado); el
   original queda local. **Nivel 3, solo ficha:** el archivo y su texto no salen de este computador; en Git queda, a
   lo más, una ficha resumen. Son de nivel 3: `_entrada/`, originales contractuales, versiones originales de
   documentos, postulaciones de terceros, el banco de archivos (`contenidos/archivos/`), el material descargado de
   una investigación (`_crudo/`), el paquete firmado (`entrega/final/`), credenciales, llaves y archivos `.env`, y
   **todo lo que la empresa defina** en `nunca_subir` de `empresa/confidencialidad.yaml` (carpetas o patrones propios).
   **Definir algo como confidencial:** `python herramientas/confidencialidad.py --agregar "<carpeta/ o patrón>" --quien
   "<nombre>"`; lo anota en ese archivo y en la sección propia de `.gitignore`, y ninguna actualización lo borra. No
   edites `.gitignore` a mano para esto. Sin argumentos, el script muestra qué se protege y si los controles están
   activos; con `--auditar`, busca confidenciales ya versionados o en el historial.
   **Controles (miran el estado real, no el texto del comando):** en Claude Code, un hook antes de cada comando de Git
   (bloquea `--no-verify`, cambiar `core.hooksPath`, `git init` junto con `git add`, y guardar con el control de Git
   inactivo) y otro después (saca del staging lo confidencial); en toda herramienta, el control de Git antes de cada
   commit y **antes de subir** (`.githooks/`). Si uno detiene algo, corrige lo que indica; nunca lo esquives.
   **Archivos de Office, PDF e imágenes fuera de las carpetas de salida** (`reportes/`, `plantillas/`, `marca/`,
   `status/` y similares): el commit lo avisa y sigue. Cuando aparezca el aviso, dile al usuario en una línea qué
   archivos son y pregunta si son material del cliente: si lo son, van en `_entrada/` o en `nunca_subir`. La empresa
   puede pedir `bloquear` o `permitir` en `binarios_sueltos`. Una clave o llave pegada en un texto detiene el commit.
   Lo que es de nivel 3 solo existe en este computador: si importa, el usuario lo respalda en un lugar seguro.
   **Réplicas:** de las bases y documentos de definición (bases, anexos, aclaraciones, lineamientos, contratos,
   actas, informes) se guarda una réplica fiel en Markdown en `fuentes/`, que sí se sube al repositorio privado: así se
   trabaja en otro computador sin los originales. De CVs, estados financieros y datos personales solo queda la ficha;
   su texto no sale del computador. La política (qué se replica completo y qué solo con ficha) está en `replicas` de
   `empresa/empresa.yaml` y un proyecto puede redefinirla. Una réplica marcada `confidencialidad: sensible` no pasa el
   control de Git.
   **Clientes de la empresa, por identificador.** En los datos de ventas (`finanzas/ventas.csv`, `cxc.csv`,
   `clientes.csv`) cada cliente es un identificador (`C-0001`); su nombre y su RUT viven solo en
   `finanzas/_local/clientes-mapa.csv`. Toda carpeta `_local/` es de nivel 3: no se sube, no se copia a un registro ni a
   un traspaso, y no viaja a una tarea de la nube. Si aparece un nombre en esos datos, `rentabilidad.py --normalizar` lo
   convierte y el control de Git no deja guardarlo antes. Los agregados (por cuadrante, por producto, totales) sí se
   usan y se comparten; una versión con nombres para revisar en el computador se pide con `--con-nombres` y queda en
   `_local/`.
   **Datos del cliente fuera del harness:** lo que se exporta para el mantenedor del núcleo (`mejoras.py --exportar`)
   sale anonimizado (nombres, siglas, nombre de la carpeta, correos, RUT y montos) y el usuario lo revisa antes de
   enviarlo. Se envía solo ese archivo: el registro `.harness/mejoras-nucleo.csv` guarda los textos sin anonimizar.
14. **Integridad.** Si unas bases, un contrato o una norma exigen declarar el uso de herramientas de IA, o lo
    restringen, es un requisito más: se registra en la matriz de cumplimiento, se avisa al usuario de forma destacada y
    la decisión es suya. Nunca se redacta una declaración falsa ni se oculta algo que se deba declarar; la declaración
    que exijan se redacta con veracidad y el archivo se lista en `autoria.excluir` (ver `reglas/entregables.md`).
