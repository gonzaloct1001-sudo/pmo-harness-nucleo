# Guía del proyecto: Programa Logística Integrada

Trabajas conversando: describe lo que necesitas con tus palabras. No hace falta usar el nombre exacto de la
skill; los ejemplos muestran cómo pedirlo. Para volver a ver esta guía: «¿qué puedo hacer?».

## Qué tipo de proyecto es

- **Programa con subproyectos** (`programa`): Un contrato general ejecutado en varios subproyectos, cada uno con su Gantt, presupuesto, equipo, riesgos, minutas y reportes; visión consolidada del programa.
- **Ejecución por plan** (`ejecucion`): Proyecto con alcance, plan de tareas, hitos y a menudo contrato. Se controla avance, plazo y costo.

En una frase: Programa con contrato único para implementar ERP, app de despacho y portal de clientes en tres subproyectos.

## Subproyectos del programa

| Id | Subproyecto | Carpeta | Responsable |
|---|---|---|---|
| sp1 | ERP | `subproyectos/sp1` | Pedro Soto |
| sp2 | App de despacho | `subproyectos/sp2` | Carla Vidal |
| sp3 | Portal de clientes | `subproyectos/sp3` | Diego Paz |

Para trabajar en uno, nómbralo («actualiza el Gantt del sp2»). Para uno nuevo: «agrega un subproyecto al programa».

## Dónde está cada cosa

- `proyecto.yaml`: configuración (identidad, gobierno, formato, umbrales, autoría).
- `CLAUDE.md`: reglas propias del proyecto · `contexto/`: alcance, interesados, glosario, estilo.
- `_entrada/`: aquí dejas documentos nuevos (no se suben a GitHub).
- `riesgos/` · `seguimiento/` (acuerdos, decisiones, notas semanales) · `minutas/` · `metricas/` · `reportes/`.
- programa/ (subproyectos, personas y asignaciones)
- presupuesto/ (macro y por subproyecto, contingencia, gastos, pronóstico)
- contractual/afectaciones.csv (qué cambia cada enmienda en cada subproyecto)
- subproyectos/<id>/ (todo lo propio de cada subproyecto)
- cronograma/gantt-programa.md (macro) y gantt-detalle.md
- cronograma/ (plan, línea base, carta Gantt)
- contractual/ (contrato, enmiendas, cambios, línea base vigente)

## Rutina recomendada

- Cada semana: actualizar el avance de cada subproyecto y revisar el estado consolidado.
- Cada mes: registrar gastos y compromisos, actualizar el pronóstico y generar el control presupuestario.
- Al llegar una enmienda: registrar sus efectos por subproyecto y aplicarlos.
- Cada semana: contar el avance y generar el reporte semanal.
- Ante un cambio de alcance, plazo o costo: registrarlo como solicitud de cambio.
- Antes de cada comité: preparar la reunión y revisar la consistencia.
- Al terminar una sesión de trabajo: «guarda» (sube los cambios a GitHub de forma segura).

## Reportes configurados

| Reporte | Formato | Cadencia | Destinatarios |
|---|---|---|---|
| Estado general del programa | docx | mensual | por definir |
| Reporte de avance semanal | docx | semanal | por definir |

Pídelo por su nombre o describiéndolo («prepara el reporte de esta semana»).

## Lo específico de este tipo de proyecto

| Para qué | Puedes decirlo así | Skill |
|---|---|---|
| Programa con subproyectos: personas, presupuesto, contingencia, enmiendas por subproyecto y estado consolidado | «¿cómo va el programa completo?» · «agrega un subproyecto de integración» · «Luis pasa al 50% en el portal» | `gestionar-programa` |
| Actualizar avance y fechas del cronograma | «la configuración va en 70%» · «terminamos el levantamiento el lunes» · «muéstrame la carta Gantt» | `actualizar-gantt` |
| Incorporar contratos, anexos, enmiendas y propuestas | «llegó la enmienda 2» · «¿qué dice el contrato sobre multas?» | `registrar-documento` |
| Gestionar solicitudes de cambio y su impacto | «el cliente pidió un módulo nuevo» · «necesitamos más plazo» | `control-cambios` |

## Útil en cualquier proyecto

| Para qué | Puedes decirlo así | Skill |
|---|---|---|
| Cargar documentos existentes y configurar todo el proyecto | «listo, ya dejé los documentos» · «procesa lo nuevo de la entrada» · «retomemos el alta» | `alta-proyecto` |
| Ver qué puedo hacer en este proyecto y cómo pedirlo | «¿qué puedo hacer?» · «muéstrame la guía del proyecto» · «¿qué comandos tengo?» | `ayuda` |
| Generar cualquier reporte del catálogo del proyecto | «prepara el reporte de esta semana» · «actualiza la planilla de septiembre» · «arma la presentación para el comité» | `generar-reporte` |
| Crear un reporte propio, desde un modelo o conversando | «quiero un informe mensual para el directorio en Excel» · «este Word es la plantilla del reporte quincenal» | `nuevo-tipo-reporte` |
| Convertir notas de reunión en minuta con acuerdos y decisiones | «estas son mis notas de la reunión de hoy» · «haz el acta del comité» | `minuta` |
| Agenda, estado, decisiones a pedir y preguntas difíciles | «tengo comité el jueves» · «¿qué llevo a la reunión con el cliente?» | `preparar-reunion` |
| Registrar y actualizar riesgos y problemas | «el proveedor se va a atrasar» · «registra este problema» · «revisemos la matriz de riesgos» | `riesgos-issues` |
| Identificar riesgos nuevos de forma sistemática | «hagamos un premortem» · «levanta los riesgos de la postulación» | `levantar-riesgos` |
| Detectar contradicciones, atrasos e incumplimientos | «¿cuadra todo?» · «¿qué está pendiente o vencido?» · «revisa el proyecto antes del comité» | `consistencia` |
| Analizar correos, informes o documentos recibidos | «mira este correo del cliente» · «¿qué implica este informe?» · «¿qué respondo?» | `revisar-documento` |
| Comparar versiones y llevar la bitácora | «¿qué cambió en la nueva versión de las bases?» · «compara estos dos documentos» | `versiones-documentos` |
| Agregar métricas y reglas, cargar datos y ver semáforos | «quiero medir también la rotación» · «carga estos datos» · «¿cómo va el indicador?» | `metricas` |
| Someter una propuesta o informe a revisores con perspectivas distintas | «revísalo como el comité» · «hazle un red team a la propuesta» · «¿qué le falta para ganar?» | `red-team` |
| Guardar y subir el trabajo a GitHub de forma segura | «guarda» · «respalda el trabajo del día» · «sube los cambios» | `guardar-cambios` |

## Controles automáticos

| Control | Qué hace | Si bloquea algo |
|---|---|---|
| Estado al iniciar la sesión | Resume proyectos, material nuevo en _entrada y altas en curso. | No bloquea: solo informa. |
| Protección de confidenciales | Antes de cada comando de Git (en Bash o PowerShell) impide subir material de _entrada, originales contractuales, CVs, paquetes firmados y credenciales. | Quita el archivo del staging; si de verdad debe versionarse, confírmalo explícitamente sabiendo el riesgo. |
| Validación de CSV y YAML | Después de cada edición revisa columnas, fechas AAAA-MM-DD y definiciones de métricas. | Corrige el archivo que indica antes de seguir. |

## Reglas que conviene saber

- Los datos del proyecto (`.yaml`, `.csv`, `.md`) son la fuente de verdad; Word, Excel y PowerPoint son salidas.
- Nada se inventa: lo que falta queda marcado como pendiente y se te avisa.
- Los documentos que se entregan salen a tu nombre y se verifican antes de entregarlos.
- Las decisiones (técnicas, legales, de inversión, declaraciones) son tuyas; el harness organiza, mide y alerta.
