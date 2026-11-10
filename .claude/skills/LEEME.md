# Índice de procedimientos (skills)

Cada procedimiento está en `.claude/skills/<nombre>/SKILL.md` (la carpeta se llama `.claude` por compatibilidad; sirve para
cualquier asistente). En Claude Code se activan solos por su descripción. **En otras herramientas:** lee este índice al
recibir el primer pedido de la sesión y, cuando el pedido calce con una fila, lee ese SKILL.md completo y síguelo paso a
paso aunque el usuario no lo nombre. Las carpetas de `.claude/skills/` que no están aquí son skills propias de la empresa
y también valen (el estado de inicio las lista). Este índice es del núcleo y se reemplaza al actualizarlo.

| Procedimiento | Para qué (frases típicas del usuario) | Archivo |
|---|---|---|
| `instalar` | Primer paso: prepara carpeta, computador y GitHub, y encamina el primer proyecto («instala», «empecemos», «computador nuevo») | `.claude/skills/instalar/SKILL.md` |
| `configurar-asistente` | Deja lista una IA nueva o distinta para operar igual que las demás («voy a usar Gemini», «cambié de IA») | `.claude/skills/configurar-asistente/SKILL.md` |
| `actualizar-nucleo` | Trae la última versión del núcleo sin tocar los datos de la empresa («actualiza el harness») | `.claude/skills/actualizar-nucleo/SKILL.md` |
| `nuevo-proyecto` | Diseña y crea un proyecto de cualquier tipo desde una descripción y una mini entrevista («quiero postular a…») | `.claude/skills/nuevo-proyecto/SKILL.md` |
| `alta-proyecto` | Carga documentos existentes: lee todo, configura, registra decisiones y pregunta lo mínimo («listo», «procesa la entrada») | `.claude/skills/alta-proyecto/SKILL.md` |
| `metricas` | Agregar métricas y reglas, cargar o importar datos, evaluar semáforos («quiero medir también…») | `.claude/skills/metricas/SKILL.md` |
| `gestionar-items` | Ítems de una cartera: agregar, mover de etapa, fichas, retirar, pipeline | `.claude/skills/gestionar-items/SKILL.md` |
| `nuevo-tipo-reporte` | Crear un reporte propio, desde un modelo o por conversación («este Word es la plantilla del informe») | `.claude/skills/nuevo-tipo-reporte/SKILL.md` |
| `adoptar-formatos` | Adoptar los formatos y archivos base propios de la empresa (o de un cliente, en el proyecto) como formato por defecto, con análisis de qué falta y qué se pierde («adopta mis formatos», «así hacemos las minutas aquí», «usa nuestro logo») | `.claude/skills/adoptar-formatos/SKILL.md` |
| `generar-reporte` | Generar cualquier reporte del catálogo («prepara el informe de avance», «arma la presentación») | `.claude/skills/generar-reporte/SKILL.md` |
| `minuta` | Convertir notas de reunión en minuta con acuerdos y decisiones («estas son mis notas del comité») | `.claude/skills/minuta/SKILL.md` |
| `preparar-reunion` | Agenda, estado, decisiones a pedir y preguntas difíciles («tengo comité el jueves») | `.claude/skills/preparar-reunion/SKILL.md` |
| `riesgos-issues` | Registrar, actualizar y revisar riesgos y problemas | `.claude/skills/riesgos-issues/SKILL.md` |
| `levantar-riesgos` | Identificar sistemáticamente riesgos nuevos (checklist, premortem, supuestos) | `.claude/skills/levantar-riesgos/SKILL.md` |
| `actualizar-gantt` | Actualizar avance y fechas del cronograma; importar MS Project | `.claude/skills/actualizar-gantt/SKILL.md` |
| `registrar-documento` | Incorporar contratos, anexos, enmiendas y propuestas | `.claude/skills/registrar-documento/SKILL.md` |
| `versiones-documentos` | Comparar documentos o versiones y llevar la bitácora («¿qué cambió en las bases?») | `.claude/skills/versiones-documentos/SKILL.md` |
| `control-cambios` | Gestionar solicitudes de cambio y su impacto | `.claude/skills/control-cambios/SKILL.md` |
| `consistencia` | Detectar contradicciones e incumplimientos en todo el proyecto («¿cuadra todo?») | `.claude/skills/consistencia/SKILL.md` |
| `revisar-documento` | Analizar correos, informes o documentos recibidos («mira este correo», «¿qué implica?») | `.claude/skills/revisar-documento/SKILL.md` |
| `definir-pauta` | Pauta de evaluación desde las bases (también la pauta inversa del postulante) | `.claude/skills/definir-pauta/SKILL.md` |
| `evaluar-propuestas` | Admisibilidad, evaluación con evidencia, ranking y comparación de propuestas de terceros | `.claude/skills/evaluar-propuestas/SKILL.md` |
| `evaluacion-economica` | Flujo de caja en Excel con fórmulas: VAN, TIR, recuperación y sensibilidad; presupuesto de postulación | `.claude/skills/evaluacion-economica/SKILL.md` |
| `revisar-estudio` | Revisar calidad y completitud de un estudio según su etapa | `.claude/skills/revisar-estudio/SKILL.md` |
| `gestionar-sprint` | Planificación, seguimiento, revisión y retrospectiva de sprints; backlog e importación | `.claude/skills/gestionar-sprint/SKILL.md` |
| `registro-ingenieria` | ADR, deuda técnica, trazabilidad, despliegues (DORA), postmortems | `.claude/skills/registro-ingenieria/SKILL.md` |
| `registros-obra` | RFI, no conformidades, inspecciones, estados de pago, libro de obra, valor ganado | `.claude/skills/registros-obra/SKILL.md` |
| `preparar-postulacion` | Preparar y presentar una postulación, oferta o propuesta para ganar: flujo con compuertas («prepara la postulación») | `.claude/skills/preparar-postulacion/SKILL.md` |
| `matriz-cumplimiento` | Todos los requisitos de las bases (barrido exhaustivo), dueños, evidencia y checklist de entrega | `.claude/skills/matriz-cumplimiento/SKILL.md` |
| `red-team` | Panel de revisores con perspectivas distintas: puntaje estimado, fallas fatales y plan de respuesta | `.claude/skills/red-team/SKILL.md` |
| `gestionar-programa` | Programa con subproyectos: personas, presupuesto y contingencia, enmiendas, estado consolidado | `.claude/skills/gestionar-programa/SKILL.md` |
| `investigar` | Investigación auditable: hechos verificados con fuente, hipótesis asesinas, refutador, puertas y entregable auditable; también auditar un informe que afirma hechos («investiga a quién ofrecer…», «¿es cierto que…?», «firmo P2») | `.claude/skills/investigar/SKILL.md` |
| `status` | Status de todos los proyectos (semáforos, lo que vence, decisiones), reporte web semanal y tablero de varias empresas («¿cómo vamos?») | `.claude/skills/status/SKILL.md` |
| `formulario-plataforma` | Formulario de una plataforma sin documento descargable: reconstruirlo, controlar límites, Word de trabajo y hoja para copiar y pegar | `.claude/skills/formulario-plataforma/SKILL.md` |
| `ayuda` | Qué puede hacer el harness en el proyecto activo, con frases de ejemplo («¿qué puedo hacer?») | `.claude/skills/ayuda/SKILL.md` |
| `guardar-cambios` | Guardar y subir el trabajo a GitHub («guarda», «terminé por hoy») | `.claude/skills/guardar-cambios/SKILL.md` |
