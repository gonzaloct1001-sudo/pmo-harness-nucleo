# Herramientas del PMO Harness

Se ejecutan desde la raíz de la carpeta con `python` (en Windows, `py` si `python` no responde; en Mac,
`.venv/bin/python`). Cada SKILL.md nombra las que usa; esta es la lista completa con sus opciones.

- `estado.py [--remoto]` → estado al iniciar: instalación, empresa, asistentes, controles, proyectos, traspasos, material pendiente y status breve.
- `medir_contexto.py [--techo]` → cuánto pesa cada pieza del contexto (mapa, puerta, skills, subagentes); con `--techo`, código 1 si el texto fijo supera el techo.
- `integridad.py [--nombres-viejos a,b]` → todo contra todo antes de publicar (mantenedor): rutas citadas, skills y subagentes, índice, catálogo, NUCLEO.txt, hooks, herramientas, nombres viejos, compilación.
- `entropia.py [--informe] [--techo]` → lo que crece sin que nadie lo retire: contexto fijo real (con descripciones de skills y subagentes), instrucciones repetidas entre documentos, lecciones viejas, `[PENDIENTE` antiguos, respaldos, mejoras sin enviar, skills sin uso. Propone; no borra.
- `hooks/sesion_larga.py`, `hooks/cierre_sesion.py`, `hooks/registrar_uso.py` → hooks de Claude Code: aviso a las 120 acciones, no terminar con traspaso viejo, registro de uso de skills (`.claude/settings.json`).
- `estrategia.py <proyecto> [--revisar | --revision AAAA-Tn [--quien] | --roadmap | --registrar] [--hoy]` → plan estratégico: estado y siguiente paso, cascada que cuadra, revisión del período con reales desde mediciones, Gantt de iniciativas, mediciones.
- `mejoras.py [--listar [--todas]] | --anotar --tipo agregar|quitar|cambiar|aprendizaje|fallo --donde ... --que ... --evidencia ... [--por-que ...] [--quien ...] | --exportar [--salida ruta] | --cerrar-resueltas` → ideas, aprendizajes y fallos del harness mismo, para el mantenedor (nunca se edita el núcleo en una empresa). Mantenedor: `--procesar <archivo exportado>`, `--decidir <id> aceptada|rechazada|diferida [--version] [--nota]`.
- `status.py [--breve] [--formato html,md,xlsx,json] [--abrir] [--panel carpeta] [--crear-panel carpeta --empresas ...]` → status de gestión.
- `agenda.py [--dias 14] [--hoy AAAA-MM-DD] [--una-vez]` → agenda del día de todos los proyectos: lo vencido, lo de hoy, lo que viene y los reportes que tocan hoy (definición con `dia:`); respeta los proyectos pausados. `hooks/agenda_diaria.py` la entrega en Claude Code en la primera interacción del día.
- `experto.py estado | instalar | pronosticar … | regresion … | segmentar <proyecto> … | plazo <proyecto> …` → análisis a fondo en dos niveles (`--nivel auto|base|especialista`): pronóstico de una serie mensual con su error comprobado; qué variables explican un resultado; grupos de clientes por reglas o por datos (con sus comprobaciones); probabilidad de terminar en fecha y tareas que más la mueven. `--diagnosticar` dice antes si el nivel base alcanza. `instalar` trae las bibliotecas del nivel especialista (`requirements-analisis.txt`) a este mismo Python, solo con el sí del usuario. Cada análisis deja `informe.html`, `informe.md` y `resultado.json`.
- `simular.py --modelos | --nuevo <modelo> --proyecto <ruta> --id <nombre> [--pregunta "…"] | <carpeta del análisis> [--revisar] [--optimizar] [--corridas N] [--semilla S] [--abrir] [--json]` → simulación con rangos (sin instalar nada): probabilidad de cumplir una meta, rango de resultados, tornado, parte de la variación que explica cada supuesto y cuánto tendría que moverse cada uno solo. Modelos: `precio-volumen`, `equilibrio`, `palancas`, `caja-crecimiento`, `crecimiento-sostenible` y `formula` (una fórmula propia). Deja `informe.html`, `resultado.json` y `corridas.csv` en `<proyecto>/analisis/<nombre>/`.
- `rentabilidad.py <proyecto> [--importar-ventas archivo | --importar-cxc archivo | --normalizar | --quien <id> | --analizar [--desde --hasta] [--costo-hora N] [--corte-afinidad X] [--corte-contribucion Y] [--con-nombres] [--abrir] [--json]]` → rentabilidad por cliente y producto desde las ventas por línea, con mapa de cuatro cuadrantes (afinidad × contribución), margen en riesgo y concentración. Los clientes van por identificador (C-0001): el nombre queda en `finanzas/_local/clientes-mapa.csv`, que no sale del computador.
- `explicar.py <entrada.md> [--proyecto ruta] [--salida ruta.html] [--abrir] [--borrador]` → página web de un solo archivo desde un Markdown con bloques `cifras`, `grafico` (barras, columnas, lineas, tornado, histograma), `pasos` y `tiempo`; sin internet, claro y oscuro, imprimible, con la tabla de datos de cada gráfico.
- `agendar_status.py --dia lunes --hora 09:00 [--panel carpeta] | --ver | --quitar` → reporte web semanal agendado en este computador.
- `formulario.py <proyecto> [--reconstruir archivos] [--limpiar] [--word] [--hoja-carga]` → formulario de una plataforma de postulación.
- `llenar_xlsx.py <planilla> --valores valores.yaml [--vista-previa]` → llena planillas oficiales sin borrar listas, formas ni fórmulas.
- `crear_proyecto.py <slug> --arquetipos a,b [--nombre N] [--perfil ruta]` → crea o amplía un proyecto (hereda de `empresa/`).
- `crear_proyecto.py <id> --programa <programa>` → crea un subproyecto dentro de un programa.
- `nueva_empresa.py "<Nombre>" --destino <carpeta> [--sin-github]` → carpeta y repositorio privado nuevos para otra empresa.
- `actualizar_nucleo.py [--desde url|carpeta] [--aplicar]` → trae la última versión del núcleo sin tocar los datos.
- `preparar_pc.ps1` (Windows) / `preparar_pc.sh` (Mac) → revisa e instala con permiso Python, Git, GitHub CLI y LibreOffice.
- `verificar_entorno.py` → diagnóstico del computador y del repositorio.
- `hooks/precommit.py [--archivos rutas | --push]` → control de confidenciales (los del harness, los de `empresa/confidencialidad.yaml`, claves pegadas en textos), aviso de Word/PDF/imágenes fuera de carpetas de salida y validación de CSV/YAML; lo usa Git antes de cada commit y, con `--push`, antes de subir.
- `actualizar_nucleo.py --verificar | --restaurar <archivo> [...] [--desde origen]` → el catastro a la vista: compara el núcleo de la carpeta con `.harness/nucleo-instalado.csv` (modificados aquí, faltantes, propios; sin internet) y devuelve un archivo cambiado o borrado por error a su original instalado, dejando lo que había en el respaldo.
- `confidencialidad.py [--auditar | --agregar "<carpeta/ o patrón>" --quien <nombre>]` → qué no sale nunca de este computador (tres niveles), lo propio de la empresa y si los controles están activos; `--auditar` busca confidenciales ya versionados o en el historial; `--agregar` define algo como confidencial (queda en `empresa/confidencialidad.yaml` y en la sección propia de `.gitignore`).
- `hooks/proteger_confidenciales.py`, `hooks/proteger_nucleo.py` → hooks de Claude Code: antes de un comando de Git, bloquea saltarse el control o agregar confidenciales (después, `validar_edicion.py` saca del staging lo que haya entrado); antes de editar, impide cambiar un archivo del núcleo en una carpeta de empresa (lo propio va en `empresa/extensiones/`).
- `evaluar_metricas.py <ruta-proyecto>` → métricas, semáforos, reglas, requisitos de etapa, fichas vencidas.
- `validar_proyecto.py <ruta-proyecto> [--corte-actualizacion]` → cronograma, riesgos, acuerdos, cambios, registros de obra, pendientes.
- `evm_cpm.py <ruta-proyecto> [--registrar]` → valor ganado, ruta crítica y término pronosticado.
- `metricas_agil.py <ruta-proyecto>` → velocidad, burndown, trabajo en curso, DORA, deuda, trazabilidad.
- `importar_backlog.py <ruta-proyecto> --desde github|csv` → trae el backlog desde GitHub o Jira.
- `importar_msproject.py <archivo.xml> <ruta-proyecto> [--mapa "Rama=sp1"] [--reemplazar] [--linea-base]` → cronograma desde MS Project (XML).
- `puntaje_pauta.py <ruta-proyecto>` → admisibilidad, puntajes ponderados, umbrales, ranking y presupuesto.
- `extraer_requisitos.py <ruta-proyecto> [--categorias ...|--todo]` → barrido de bases y formularios: candidatos a requisito con fuente (incremental).
- `postulacion.py <ruta-proyecto> [--registrar]` → etapa y compuerta, cumplimiento, vencimientos, red team, controles y autoría.
- `presupuesto_postulacion.py <presupuesto.yaml>` → Excel del presupuesto con fórmulas, fuentes y controles contra las bases.
- `guia_proyecto.py <ruta-proyecto> | --general` → guía del usuario (`GUIA.md`).
- `programa.py <ruta-programa> [--excel] [--registrar]` → estado consolidado del programa, presupuesto, personas, enmiendas y Gantt macro.
- `investigacion.py <ruta-proyecto> [--instancia id] [--nueva nombre | --revisar | --corregir [--aplicar] | --auditar | --muestra | --subir nivel | --aprender]`
  → investigaciones: siguiente paso, validación del protocolo, corrección de lo mecánico, auditoría y aprendizaje;
  `--ajustar clave=valor` y `--preferencia "texto"` guardan los ajustes de la empresa.
- `modelo_economico.py <supuestos.yaml>` → Excel con flujo de caja, VAN, TIR y sensibilidad (con fórmulas).
- `comparar_documentos.py <anterior> <nuevo>` → diferencias entre documentos, destacando las sustantivas.
- `extraer_entrada.py <ruta-proyecto> [--origen carpeta]` → inventario, texto y réplicas en `fuentes/` (incremental).
- `md_a_docx.py <entrada.md> <salida.docx> --proyecto <ruta> [--plantilla plantilla.docx | --sin-plantilla] [--borrador]` → Word con la marca y autoría del proyecto; con una plantilla Word de la empresa (`--plantilla` o `formato.plantilla_word`), documento largo sobre ella: portada y encabezados con marcadores, historia de revisiones, índice, estilos y numeración de la plantilla, figuras con leyenda y anexos (07a9bc-M-001).
- `verificar_autoria.py <archivo|carpeta> --proyecto <ruta> [--corregir]` → revisa que un entregable no tenga rastros del proceso.
- `inspeccionar_xlsx.py <archivo.xlsx>` → estructura de un Excel (hojas, fórmulas, celdas de entrada) y si se puede guardar con openpyxl.
- `gantt_mermaid.py <ruta-proyecto>` → `cronograma/gantt.md` para visualizar la carta Gantt.
- `pruebas/ejecutar_pruebas.py` → batería de pruebas del harness (ver también `pruebas/escenarios-skills.md`).

- `adoptar_formatos.py empresa|proyectos/<slug> [--aplicar --quien N] [--mejorado F-nn] [--marca] [--asignar F-nn=tipo] [--descartar F-nn] | --tipos`
  → adopta los formatos propios: detecta el tipo, compara con el contrato (qué falta, qué se pierde, qué es propio), propone
  mejoras y registra lo adoptado en `formatos/registro.csv`.
- `llenar_docx.py <plantilla.docx> --valores valores.yaml --salida x.docx [--proyecto ruta] [--vista-previa]` → llena una plantilla
  Word propia (marcadores y secciones por título, respetando estilos, viñetas y tablas) con autoría limpia.

- `finanzas.py <ruta-proyecto> [--importar archivo --periodo AAAA-MM [--vista-previa] | --estados [--excel x.xlsx] | --cerrar P --quien N |
  --reabrir P --quien N --motivo M | --forecast [--metodo presupuesto|tendencia] | --proyectar [--excel x.xlsx] | --revisar | --registrar]`
  → finanzas de gestión: importar la contabilidad, resultados/balance/caja con desvíos e indicadores, cierres con huella,
  forecast, proyección integrada; sin opciones dice dónde va y el siguiente paso.

- `nube.py [--estado | --catalogo | --habilitar --quien N | --agregar <tarea> --quien N [--cron] [--zona] | --pausar|--reanudar|--quitar <tarea> --quien N |
  --id-remoto-de <tarea> <id> | --instruccion <tarea> | --deshabilitar --quien N --motivo M | --revisar]` → registro del modo nube (`.harness/nube.yaml`):
  qué aprobó el usuario, quién y cuándo; el texto de cada tarea programada. No crea nada en la nube.
- `bandeja.py [--listar [--breve] | --nueva "texto" [--proyecto s] | --responder n "texto" | --pregunta n "texto" | --tomar n | --terminar n [--pr url] |
  --integrar n | --resumen [--publicar] | --etiquetas] [--repositorio owner/repo]` → bandeja en GitHub por REST (`gh api`): pedidos,
  preguntas, PRs de la nube y el resumen diario. `HARNESS_GH` permite usar un `gh` falso en pruebas.

Dependencias: `pip install -r requirements.txt` (en Mac, dentro de `.venv`, que crea el instalador).
