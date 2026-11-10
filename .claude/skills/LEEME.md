# Índice de procedimientos (skills)

Cada procedimiento está en `.claude/skills/<nombre>/SKILL.md` (la carpeta se llama `.claude` por compatibilidad; sirve para
cualquier asistente). En Claude Code se activan solos por su descripción. **En otras herramientas:** lee este índice al
recibir el primer pedido de la sesión y, cuando el pedido calce con una fila, lee ese SKILL.md completo y síguelo paso a
paso aunque el usuario no lo nombre. Las carpetas de `.claude/skills/` que no están aquí son skills propias de la empresa
y también valen (el estado de inicio las lista). Este índice es del núcleo y se reemplaza al actualizarlo.

| Procedimiento | Para qué (frases típicas del usuario) | Archivo |
|---|---|---|
| `instalar` | Primer paso: prepara carpeta, computador y GitHub, y encamina el primer proyecto («instala», «empecemos», «computador nuevo») | `.claude/skills/instalar/SKILL.md` |
| `configurar` | Cambiar cualquier configuración después de instalado, con confirmación: empresa, marca, formatos, asistente de IA y modelos (opción D: dejar lista una IA nueva, «voy a usar Gemini», «cambié de IA»), umbrales, confidencialidad, modo nube, status semanal, un proyecto, mejoras y salud del harness («quiero cambiar…», «de ahora en adelante…», «¿dónde se cambia…?») | `.claude/skills/configurar/SKILL.md` |
| `nube` | Modo nube opcional (solo Claude): explicar, activar con el sí del usuario, elegir qué programar tarea por tarea, crear y pausar tareas, operar desde el celular («¿puedo revisar desde el celular?», «con el PC apagado», «programa el resumen de la mañana», «pausa la nube») | `.claude/skills/nube/SKILL.md` |
| `actualizar-nucleo` | Trae la última versión del núcleo sin tocar los datos de la empresa («actualiza el harness») | `.claude/skills/actualizar-nucleo/SKILL.md` |
| `nuevo-proyecto` | Empezar un proyecto de cualquier tipo: desde una descripción («quiero postular a…») o cargando sus documentos («listo, ya dejé los documentos», «procesa la entrada», «retomemos el alta») | `.claude/skills/nuevo-proyecto/SKILL.md` |
| `metricas` | Agregar métricas y reglas, cargar o importar datos, evaluar semáforos («quiero medir también…») | `.claude/skills/metricas/SKILL.md` |
| `gestionar-items` | Ítems de una cartera: agregar, mover de etapa, fichas, retirar, pipeline | `.claude/skills/gestionar-items/SKILL.md` |
| `reportes` | Crear un reporte propio, desde un modelo o por conversación («este Word es la plantilla del informe»); Generar cualquier reporte del catálogo («prepara el informe de avance», «arma la presentación») | `.claude/skills/reportes/SKILL.md` |
| `adoptar-formatos` | Adoptar los formatos y archivos base propios de la empresa (o de un cliente, en el proyecto) como formato por defecto, con análisis de qué falta y qué se pierde («adopta mis formatos», «así hacemos las minutas aquí», «usa nuestro logo») | `.claude/skills/adoptar-formatos/SKILL.md` |
| `reuniones` | Antes de una reunión: agenda, estado, decisiones a pedir y preguntas difíciles («tengo comité el jueves»); después: notas o transcripción → minuta con acuerdos y decisiones a los registros («estas son mis notas del comité», «haz el acta») | `.claude/skills/reuniones/SKILL.md` |
| `riesgos` | Registrar, actualizar y revisar riesgos y problemas; Identificar sistemáticamente riesgos nuevos (checklist, premortem, supuestos) | `.claude/skills/riesgos/SKILL.md` |
| `actualizar-gantt` | Actualizar avance y fechas del cronograma; importar MS Project | `.claude/skills/actualizar-gantt/SKILL.md` |
| `documentos` | Incorporar contratos, anexos, enmiendas y propuestas; Comparar documentos o versiones y llevar la bitácora («¿qué cambió en las bases?») | `.claude/skills/documentos/SKILL.md` |
| `control-cambios` | Gestionar solicitudes de cambio y su impacto | `.claude/skills/control-cambios/SKILL.md` |
| `consistencia` | Detectar contradicciones e incumplimientos en todo el proyecto («¿cuadra todo?») | `.claude/skills/consistencia/SKILL.md` |
| `revisar-documento` | Analizar correos, informes o documentos recibidos («mira este correo», «¿qué implica?») | `.claude/skills/revisar-documento/SKILL.md` |
| `evaluar-propuestas` | Pauta de evaluación desde las bases (también la pauta inversa del postulante); Admisibilidad, evaluación con evidencia, ranking y comparación de propuestas de terceros | `.claude/skills/evaluar-propuestas/SKILL.md` |
| `evaluacion-economica` | Flujo de caja en Excel con fórmulas: VAN, TIR, recuperación y sensibilidad; presupuesto de postulación | `.claude/skills/evaluacion-economica/SKILL.md` |
| `revisar-estudio` | Revisar calidad y completitud de un estudio según su etapa | `.claude/skills/revisar-estudio/SKILL.md` |
| `gestionar-sprint` | Planificación, seguimiento, revisión y retrospectiva de sprints; backlog e importación | `.claude/skills/gestionar-sprint/SKILL.md` |
| `registro-ingenieria` | ADR, deuda técnica, trazabilidad, despliegues (DORA), postmortems | `.claude/skills/registro-ingenieria/SKILL.md` |
| `registros-obra` | RFI, no conformidades, inspecciones, estados de pago, libro de obra, valor ganado | `.claude/skills/registros-obra/SKILL.md` |
| `preparar-postulacion` | Preparar y presentar una postulación, oferta o propuesta para ganar: flujo con compuertas («prepara la postulación»); Todos los requisitos de las bases (barrido exhaustivo), dueños, evidencia y checklist de entrega | `.claude/skills/preparar-postulacion/SKILL.md` |
| `red-team` | Panel de revisores con perspectivas distintas: puntaje estimado, fallas fatales y plan de respuesta | `.claude/skills/red-team/SKILL.md` |
| `gestionar-programa` | Programa con subproyectos: personas, presupuesto y contingencia, enmiendas, estado consolidado | `.claude/skills/gestionar-programa/SKILL.md` |
| `gestion-financiera` | Llevar las finanzas de una empresa: presupuesto anual, cierre mensual (importar la contabilidad, cuadrar, desvíos, indicadores, cerrar y reabrir), forecast, proyección integrada y reporte al directorio («¿cómo vamos financieramente?», «cierra septiembre», «¿por qué subió el gasto?») | `.claude/skills/gestion-financiera/SKILL.md` |
| `plan-estrategico` | Plan estratégico o de negocio a 3 o 5 años: diagnóstico con fuentes, lineamientos, objetivos con metas por año, iniciativas, plan financiero sobre finanzas, documento al directorio y revisión trimestral («armemos el plan 2027-2029», «¿dónde queremos estar en 2030?», «revisión del trimestre») | `.claude/skills/plan-estrategico/SKILL.md` |
| `investigar` | Investigación auditable: hechos verificados con fuente, hipótesis asesinas, refutador, puertas y entregable auditable; también auditar un informe que afirma hechos («investiga a quién ofrecer…», «¿es cierto que…?», «firmo P2») | `.claude/skills/investigar/SKILL.md` |
| `status` | Status de todos los proyectos (semáforos, lo que vence, decisiones), reporte web semanal y tablero de varias empresas («¿cómo vamos?») | `.claude/skills/status/SKILL.md` |
| `formulario-plataforma` | Formulario de una plataforma sin documento descargable: reconstruirlo, controlar límites, Word de trabajo y hoja para copiar y pegar | `.claude/skills/formulario-plataforma/SKILL.md` |
| `ayuda` | Qué puede hacer el harness en el proyecto activo, con frases de ejemplo («¿qué puedo hacer?») | `.claude/skills/ayuda/SKILL.md` |
| `guardar-cambios` | Guardar y subir el trabajo a GitHub («guarda», «terminé por hoy») | `.claude/skills/guardar-cambios/SKILL.md` |

## Nombres anteriores (hasta la versión 2.7)
Si una nota tuya o un documento nombra una de estas skills, hoy es la de la derecha.

| Nombre anterior | Hoy |
|---|---|
| `alta-proyecto` | `nuevo-proyecto` (camino A, con documentos) |
| `configurar-asistente` | `configurar` (opción D) |
| `preparar-reunion`, `minuta` | `reuniones` (antes y después) |
| `riesgos-issues`, `levantar-riesgos` | `riesgos` |
| `generar-reporte`, `nuevo-tipo-reporte` | `reportes` |
| `registrar-documento`, `versiones-documentos` | `documentos` |
| `definir-pauta` | `evaluar-propuestas` (paso 1, `references/pauta.md`) |
| `matriz-cumplimiento` | `preparar-postulacion` (`references/matriz-cumplimiento.md`) |
