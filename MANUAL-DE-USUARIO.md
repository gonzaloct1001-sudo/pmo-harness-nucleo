# PMO Harness 2.1: manual de usuario

> Para instalarlo por primera vez, sigue la **guía de inicio** (`EMPEZAR-AQUI.md`). Este manual explica cómo se usa.

## 1. Qué es
Un asistente de gestión de proyectos que trabaja **conversando**, con la IA que prefieras (Google Antigravity, Claude
Code, OpenAI Codex, Gemini, Cursor o GitHub Copilot). Tú le cuentas lo que pasa y él mantiene ordenado el proyecto
(cronograma, riesgos, acuerdos, presupuesto, contratos, requisitos de unas bases), detecta problemas y prepara informes
y presentaciones con la marca y los formatos de tu empresa.

- Todo queda en archivos en tu computador y en un repositorio **privado** de GitHub, **uno por empresa**.
- Los documentos que entrega (Word, Excel, PowerPoint) salen **a tu nombre**.
- **Nunca inventa datos.** Lo que falta queda marcado como pendiente y te lo dice.
- **Las decisiones son tuyas.** Él organiza, mide, alerta y propone.

## 2. Lo que necesitas (una sola vez)
1. **Una herramienta de IA que trabaje con carpetas:** Google Antigravity, VS Code con una extensión de IA (Claude Code,
   Codex, Gemini Code Assist o GitHub Copilot), Claude Code o Cursor. Un chat en el navegador no sirve.
2. **Una cuenta de GitHub** gratuita (personal; no hace falta plan de pago ni organización). Si no la tienes, el
   asistente te abre la página para crearla.
3. **El harness**, descargado desde su página pública: botón **Code → Download ZIP**. **No uses «Fork»**: crearía
   una copia pública.
4. **Python y Git no tienes que instalarlos tú:** el asistente los instala con tu permiso.

## 3. Instalación
Paso a paso en la guía de inicio. En resumen:
1. Descomprime el zip, cambia el nombre de la carpeta por el de tu empresa y déjala en `Documentos`.
2. **Opcional:** completa `FICHA-DE-INICIO.md`. Así la instalación casi no te hace preguntas.
3. En tu herramienta de IA: **Archivo → Abrir carpeta** → tu carpeta. Abre el chat y escribe **«hola»**.
4. El asistente revisa el computador y, **con tu permiso**, instala lo que falta. Windows puede pedirte confirmar en
   pantalla. En Mac puede pedirte doble clic en `INSTALAR-MAC.command` y la contraseña del Mac.
5. Te ayuda con GitHub: abre una ventana para conectar tu cuenta (Enter, pegar el código en el navegador, autorizar)
   y crea tu **repositorio privado**.
6. Te pregunta lo de la sección 4 y crea tu primer proyecto. Al final te muestra la **guía de tu proyecto** (`GUIA.md`).

## 4. Lo que te va a preguntar (y conviene tener a mano)
| Tema | Pregunta |
|---|---|
| Tú | Nombre, cargo y correo (los documentos salen a tu nombre) |
| La empresa | De qué empresa es esta carpeta (cada empresa tiene su carpeta y su repositorio) |
| El proyecto | De qué se trata, nombre, cliente o mandante, fechas y monto |
| Tipo | ¿Una **postulación** a un fondo o licitación, la **ejecución** de un proyecto, un **programa** con varios subproyectos, evaluar propuestas de otros, un **estudio** o evaluación económica? Si no sabes, descríbelo y él propone |
| Punto de partida | (a) parte de cero · (b) en marcha **con** documentos · (c) en marcha, pero **casi todo lo sabes tú** |
| Si está en marcha | Hitos cumplidos y próximos, avance, problemas, riesgos, compromisos vigentes (máximo 8 preguntas, en un solo mensaje) |
| Gobierno | Quién es el sponsor o el directorio, quién aprueba cambios, si hay comité |
| Reportes | Qué informes entregas hoy (por ejemplo, el de avance), a quién, cada cuánto y con qué plantilla |
| Postulación | Convocatoria, cierre, quién postula y firma, monto y aporte propio |

Puedes contestar como quieras: viñetas, texto pegado de un correo o «no sé» (queda pendiente).

## 5. Si ya tienes documentos (el «alta»)
1. Déjalos en `proyectos/<tu-proyecto>/_entrada/`, **sin ordenar ni renombrar**:
   - bases, anexos, formularios y aclaraciones de una postulación → `00-bases-y-aclaraciones`;
   - contratos y enmiendas → `01-contratos-y-anexos`; cronograma → `03-cronogramas` (MS Project: Guardar como **XML**);
   - informes anteriores y plantillas → `04-reportes-y-plantillas`; actas → `05-actas-y-minutas`; lo demás → `09-otros`.
2. Escribe **listo**.
3. El asistente lee todo, configura el proyecto, deja un **registro de cada decisión con su fuente** y te hace **un solo
   mensaje de preguntas** (máximo 12, cada una con una propuesta).
4. Revisa `contexto/informe-de-alta.md`: qué entendió, qué quedó pendiente y qué conviene hacer.

**Qué se guarda en GitHub:** los archivos originales que dejas en `_entrada/` no se suben. Del texto de bases,
aclaraciones, lineamientos, contratos, actas e informes queda una **copia fiel** en `fuentes/`, dentro de tu repositorio
privado, para trabajar desde otro computador sin los originales. De CVs, estados financieros y datos personales solo
queda una ficha.

Si después llegan más documentos, déjalos en `_entrada/`: en la siguiente sesión te ofrece procesarlos.

## 6. Uso diario: pídelo con tus palabras
| Quieres… | Dile, por ejemplo |
|---|---|
| Preparar una reunión de avance | «tengo reunión de avance el jueves, ¿qué llevo?» |
| Una minuta | pega tus notas: «estas son las notas de la reunión de hoy» |
| El informe de avance | «genera el informe de avance de octubre» |
| Un informe con tu formato | deja tu Word, Excel o PowerPoint y dile «esta es la plantilla del informe de avance» |
| Revisar lineamientos del directorio | «llegaron los nuevos lineamientos del directorio, ¿qué cambia para el proyecto?» |
| Una evaluación financiera | «arma el flujo de caja con estos supuestos», «¿qué pasa si las ventas caen 20%?» |
| Actualizar el avance | «la configuración va en 70%», «terminamos el levantamiento el lunes» |
| Registrar un riesgo o problema | «el proveedor se va a atrasar dos semanas» |
| Revisar todo | «¿cuadra todo?», «¿qué está atrasado o vencido?» |
| Un contrato o enmienda | «llegó la enmienda 2» |
| Ver qué puedes hacer | «¿qué puedo hacer?» |
| Guardar | «guarda» (sube los cambios a GitHub de forma segura) |

## 7. Postulaciones a fondos y licitaciones
Deja las bases, anexos y aclaraciones en `_entrada/00-bases-y-aclaraciones/` y di «prepara la postulación». El harness:
1. revisa todas las bases y arma la lista de requisitos, incluidos los escondidos en anexos y aclaraciones;
2. te ayuda a decidir si conviene postular;
3. reconstruye cómo evaluará el comité y arma la propuesta por secciones;
4. hace el presupuesto con controles contra las bases (topes, cofinanciamiento, aportes);
5. somete la propuesta a un **red team** (revisores con miradas distintas) y revisa todo antes de entregar.

Los CVs, certificados y la descripción de la empresa se guardan una vez en el **banco de antecedentes** de la empresa
y sirven para todas sus postulaciones; te avisa si un certificado estará vencido al cierre.
Si las bases exigen declarar el uso de IA, te lo avisa: esa declaración la decides y la haces tú.

## 8. Varios proyectos y programas
Cada vez que digas **«nuevo proyecto»**, el asistente pregunta dónde va:
- **Independiente:** su propio contrato, presupuesto, Gantt, minutas, formatos y objetivos.
- **Programa:** un contrato general con varios **subproyectos**, cada uno con su Gantt, objetivos, riesgos, minutas y
  reportes; el programa lleva el presupuesto macro y por subproyecto, la contingencia, las personas compartidas, el
  Gantt macro y los reportes generales.
- **Subproyecto de un programa existente:** hereda la marca, los formatos y las plantillas del programa.

## 9. Varias empresas, otro computador y otra IA
- **Una carpeta por empresa.** Cada empresa tiene su carpeta y su repositorio privado, con su marca, sus formatos y su
  banco de antecedentes. Para otra empresa: «crea la carpeta para la empresa X». Los datos de dos empresas nunca se mezclan.
- **Otro computador:** instala tu herramienta de IA, abre cualquier carpeta del harness y pide «descarga mis empresas».
  Quedan en `Documentos/PMO-Empresas/`. Abre la que necesites y escribe «hola».
- **Otra IA, o cambiar a mitad de camino:** abre la carpeta con la otra IA y escribe «hola» o «¿en qué íbamos?». La
  primera vez se configura sola. Cada proyecto guarda un **traspaso** (qué se hizo, en qué quedó, el próximo paso), así
  que la nueva IA retoma sin que repitas nada. Antes de cambiar, di «guarda».

## 10. Privacidad: tu repositorio y el del harness
- El **harness** se publica en un repositorio público de **solo lectura**: cualquiera lo descarga, pero nadie puede
  modificarlo, salvo su autor.
- **Tus datos van solo a tus repositorios privados**, uno por empresa. Nunca llegan al repositorio del harness, y su
  autor no los ve.
- **Versiones nuevas del harness:** nada cambia en tu carpeta hasta que tú digas «actualiza el harness». Antes te
  muestra qué cambia; respalda, prueba y, si algo falla, deja todo como estaba. Tus proyectos, documentos e informes no
  se tocan.
- **No uses «Fork»** para obtener el harness: crearía una copia pública.
- La IA que usas procesa el contenido de tus documentos según las condiciones de su proveedor. Confirma que tus
  clientes lo permiten (la ficha de inicio lo pregunta).

## 11. Controles automáticos
- **No sube a GitHub** documentos confidenciales: la carpeta `_entrada`, originales de contratos, CVs, paquetes firmados.
  El control está en Git y funciona con cualquier IA.
- **Revisa cada planilla** antes de guardarla (columnas y fechas).
- **Al abrir** te dice qué hay pendiente: traspasos, documentos nuevos, altas a medio camino, cambios sin guardar.
- **Antes de entregar un documento** revisa que salga a tu nombre y sin rastros del proceso.

Si un control bloquea algo, el asistente te explica por qué y cómo seguir.

## 12. Preguntas frecuentes
- **¿Tengo que saber los nombres de los comandos?** No. Describe lo que necesitas.
- **¿Cuánto cuesta?** El harness es gratuito (licencia MIT) y GitHub también. La herramienta de IA tiene sus propios planes.
- **¿Puedo usar Gemini, Codex, Antigravity u otra IA?** Sí, siempre que trabaje sobre la carpeta. Puedes cambiar cuando
  quieras: la nueva retoma desde el traspaso.
- **¿Puedo usar MS Project?** Sí: guarda el cronograma como XML y di «importa el cronograma de MS Project». Primero ves
  una vista previa; nada se reemplaza sin tu confirmación.
- **¿Qué pasa si no sé un dato?** Queda como pendiente y aparece en el informe; no se inventa.
- **¿Dónde quedan mis informes?** En `reportes/emitidos/` de cada proyecto.
- **¿Necesito los documentos originales en otro computador?** Casi nunca: las bases y los documentos de definición
  están replicados en `fuentes/`. Los originales hacen falta para firmar o presentar, o ante una duda legal.
- **¿Cómo pruebo sin datos reales?** Pídele «prueba con el paquete de postulación de ejemplo».

## 13. Si algo falla
- **La IA no reconoce el harness:** escríbele «lee el archivo AGENTS.md y sigue sus instrucciones».
- **«python no se reconoce»:** pide «instala lo que falte». Si recién se instaló, cierra y vuelve a abrir tu herramienta.
- **Un control bloqueó un envío a GitHub:** el asistente te dirá qué archivo era confidencial; déjalo fuera.
- **«El nombre del archivo es demasiado largo» (Windows):** usa una carpeta más corta (por ejemplo,
  `Documentos/Consultora-Sur`) o deja que el asistente active las rutas largas.
- **Algo no cuadra en un informe:** «revisa este informe con ojo crítico» (hace una revisión independiente).
- **¿Funciona todo bien?** Pide «verifica que el harness funcione» (ejecuta su batería de pruebas).
