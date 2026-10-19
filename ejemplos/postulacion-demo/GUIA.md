# Guía del proyecto: Riego inteligente AgroSur - Fondo Impulsa 2026

Trabajas conversando: describe lo que necesitas con tus palabras. No hace falta usar el nombre exacto de la
skill; los ejemplos muestran cómo pedirlo. Para volver a ver esta guía: «¿qué puedo hacer?».

## Qué tipo de proyecto es

- **Postulación (oferente)** (`postulacion`): Preparar y presentar una propuesta para ganar un fondo, licitación, RFP o concurso, cumpliendo el 100% de las bases.

En una frase: Postulación al Fondo Impulsa Innovación Regional 2026 para validar un sistema de riego con sensores de humedad para pequeños productores.

## Dónde está cada cosa

- `proyecto.yaml`: configuración (identidad, gobierno, formato, umbrales, autoría).
- `CLAUDE.md`: reglas propias del proyecto · `contexto/`: alcance, interesados, glosario, estilo.
- `_entrada/`: aquí dejas documentos nuevos (no se suben a GitHub).
- `riesgos/` · `seguimiento/` (acuerdos, decisiones, notas semanales) · `minutas/` · `metricas/` · `reportes/`.
- postulacion/ (etapas, matriz de requisitos, barrido de bases, calendario, consultas, pauta inversa, Go/No-Go, estrategia)
- propuesta/ (una sección por capítulo)
- economico/ (presupuesto con controles)
- redteam/ (revisiones)
- entrega/ (checklist y paquete final, que no se sube a Git)
- contenidos/ (banco reutilizable del postulante)

## Rutina recomendada

- Cada vez que llega material de las bases (aclaraciones, foro): barrer requisitos y actualizar la matriz.
- Cada semana, y a diario en la última semana: revisar el estado (etapa, compuerta, vencimientos).
- Antes de entregar: red team, revisión oro y guante blanco, verificación de autoría.
- Al terminar una sesión de trabajo: «guarda» (sube los cambios a GitHub de forma segura).

## Reportes configurados

| Reporte | Formato | Cadencia | Destinatarios |
|---|---|---|---|
| Estado de la postulación | md | a pedido | por definir |
| Informe consolidado del red team | md | a pedido | por definir |

Pídelo por su nombre o describiéndolo («prepara el reporte de esta semana»).

## Lo específico de este tipo de proyecto

| Para qué | Puedes decirlo así | Skill |
|---|---|---|
| Pauta de evaluación desde las bases (también la pauta inversa del oferente) | «arma la pauta con estas bases» · «¿cómo nos va a evaluar el comité?» | `definir-pauta` |
| Flujo de caja, VAN, TIR y sensibilidad; presupuesto de postulaciones con controles | «¿es rentable el proyecto?» · «arma el presupuesto de la postulación con los controles de las bases» | `evaluacion-economica` |
| Llevar la postulación de las bases a la entrega, con compuertas | «prepara la postulación» · «¿cómo vamos con la postulación?» · «¿qué falta para entregar?» | `preparar-postulacion` |
| Todos los requisitos de las bases con dueño, evidencia y checklist de entrega | «¿qué exigen las bases?» · «llegó una aclaración» · «¿cumplimos todo?» | `matriz-cumplimiento` |

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
