# Guía del proyecto: Programa Andes Digital

Trabajas conversando: describe lo que necesitas con tus palabras. No hace falta usar el nombre exacto de la
skill; los ejemplos muestran cómo pedirlo. Para volver a ver esta guía: «¿qué puedo hacer?».

## Qué tipo de proyecto es

- **Ejecución por plan** (`ejecucion`): Proyecto con alcance, plan de tareas, hitos y a menudo contrato. Se controla avance, plazo y costo.

En una frase: Modernización de la operación de distribución mediante nuevo ERP, app móvil de despacho, integración con tableros BI y portal de clientes.

## Dónde está cada cosa

- `proyecto.yaml`: configuración (identidad, gobierno, formato, umbrales, autoría).
- `CLAUDE.md`: reglas propias del proyecto · `contexto/`: alcance, interesados, glosario, estilo.
- `_entrada/`: aquí dejas documentos nuevos (no se suben a GitHub).
- `riesgos/` · `seguimiento/` (acuerdos, decisiones, notas semanales) · `minutas/` · `metricas/` · `reportes/`.
- cronograma/ (plan, línea base, carta Gantt)
- contractual/ (contrato, enmiendas, cambios, línea base vigente)

## Rutina recomendada

- Cada semana: contar el avance y generar el reporte semanal.
- Ante un cambio de alcance, plazo o costo: registrarlo como solicitud de cambio.
- Antes de cada comité: preparar la reunión y revisar la consistencia.
- Al terminar una sesión de trabajo: «guarda» (sube los cambios a GitHub de forma segura).

## Reportes configurados

| Reporte | Formato | Cadencia | Destinatarios |
|---|---|---|---|
| PEP — Planilla de Estado del Programa | xlsx | mensual | Rodrigo Soto, Control de Gestión |
| Reporte de avance semanal | docx | semanal | Carolina Pérez, Andrés Muñoz |

Pídelo por su nombre o describiéndolo («prepara el reporte de esta semana»).

## Lo específico de este tipo de proyecto

| Para qué | Puedes decirlo así | Skill |
|---|---|---|
| Actualizar avance y fechas del cronograma | «la configuración va en 70%» · «importa el cronograma de MS Project» · «muéstrame la carta Gantt» | `actualizar-gantt` |
| Gestionar solicitudes de cambio y su impacto | «el cliente pidió un módulo nuevo» · «necesitamos más plazo» | `control-cambios` |

## Útil en cualquier proyecto

| Para qué | Puedes decirlo así | Skill |
|---|---|---|
| Empezar un proyecto: diseñarlo desde una descripción o cargar sus documentos y configurar todo | «quiero llevar la construcción de una casa» · «quiero postular a un fondo CORFO» · «listo, ya dejé los documentos» | `nuevo-proyecto` |
| Ver qué puedo hacer en este proyecto y cómo pedirlo | «¿qué puedo hacer?» · «muéstrame la guía del proyecto» · «¿qué comandos tengo?» | `ayuda` |
| Status de todos los proyectos: semáforos, lo que vence, decisiones; reporte web semanal y tablero de varias empresas | «¿cómo vamos?» · «dame el reporte de status» · «agéndalo los lunes a las 9» | `status` |
| Generar cualquier reporte del catálogo del proyecto · Crear un reporte propio, desde un modelo o conversando | «prepara el reporte de esta semana» · «actualiza la planilla de septiembre» · «arma la presentación para el comité» | `reportes` |
| Antes de una reunión: agenda, estado, decisiones a pedir y preguntas difíciles; después: notas o transcripción → minuta con acuerdos y decisiones | «tengo comité el jueves» · «¿qué llevo a la reunión con el cliente?» · «estas son mis notas de la reunión de hoy» | `reuniones` |
| Registrar y actualizar riesgos y problemas · Identificar riesgos nuevos de forma sistemática | «el proveedor se va a atrasar» · «registra este problema» · «revisemos la matriz de riesgos» | `riesgos` |
| Detectar contradicciones, atrasos e incumplimientos | «¿cuadra todo?» · «¿qué está pendiente o vencido?» · «revisa el proyecto antes del comité» | `consistencia` |
| Analizar correos, informes o documentos recibidos | «mira este correo del cliente» · «¿qué implica este informe?» · «¿qué respondo?» | `revisar-documento` |
| Comparar versiones y llevar la bitácora · Incorporar contratos, anexos, enmiendas y propuestas | «¿qué cambió en la nueva versión de las bases?» · «compara estos dos documentos» · «llegó la enmienda 2» | `documentos` |
| Agregar métricas y reglas, cargar datos y ver semáforos | «quiero medir también la rotación» · «carga estos datos» · «¿cómo va el indicador?» | `metricas` |
| Someter una propuesta o informe a revisores con perspectivas distintas | «revísalo como el comité» · «hazle un red team a la propuesta» · «¿qué le falta para ganar?» | `red-team` |
| Investigación auditable: hechos del mundo verificados con fuente, hipótesis asesinas, refutador y entregable que un tercero puede auditar | «investiga a quién le podemos ofrecer la licencia» · «¿es cierto lo que dice este informe?» · «¿cuál es el siguiente paso de la investigación?» | `investigar` |
| Guardar y subir el trabajo a GitHub de forma segura | «guarda» · «respalda el trabajo del día» · «sube los cambios» | `guardar-cambios` |

## Controles automáticos

| Control | Qué hace | Si bloquea algo |
|---|---|---|
| Estado al iniciar la sesión | Resume proyectos, traspasos pendientes, material nuevo en _entrada, altas en curso y cambios sin guardar (en Claude Code llega solo; otras IA lo ejecutan al empezar). | No bloquea: solo informa. |
| Control de Git antes de cada commit | Con cualquier IA, o sin IA: impide guardar en Git material confidencial y planillas mal formadas. | Corrige o quita del commit el archivo que indica. Nunca se salta el control. |
| Protección de confidenciales | Antes de cada comando de Git (en Bash o PowerShell) impide subir material de _entrada, originales contractuales, CVs, paquetes firmados y credenciales. | Quita el archivo del staging; si de verdad debe versionarse, confírmalo explícitamente sabiendo el riesgo. |
| Validación de CSV y YAML | Después de cada edición revisa columnas, fechas AAAA-MM-DD y definiciones de métricas. | Corrige el archivo que indica antes de seguir. |

## Reglas que conviene saber

- Los datos del proyecto (`.yaml`, `.csv`, `.md`) son la fuente de verdad; Word, Excel y PowerPoint son salidas.
- Nada se inventa: lo que falta queda marcado como pendiente y se te avisa.
- Los documentos que se entregan salen a tu nombre y se verifican antes de entregarlos.
- Las decisiones (técnicas, legales, de inversión, declaraciones) son tuyas; el harness organiza, mide y alerta.
