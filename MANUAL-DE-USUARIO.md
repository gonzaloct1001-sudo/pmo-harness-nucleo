# PMO Harness 3.1: manual de usuario

> Para instalarlo por primera vez, sigue la **guía de inicio** (`EMPEZAR-AQUI.md`). Este manual explica cómo se usa,
> en palabras simples. Lo técnico está en `README.md` y en `AGENTS.md`.

## 1. Qué es el harness
El harness es una carpeta en tu computador donde una IA lleva tus proyectos como lo haría un buen PMO: ordena los
documentos, mide el avance, avisa lo que vence, prepara reportes y minutas, y respalda todo en un repositorio privado
tuyo. Tú conversas; él organiza.

Sirve para proyectos de ejecución y obras, equipos de software, carteras de ítems, postulaciones a fondos y
licitaciones, evaluación de propuestas, estudios, investigaciones con rigor y las finanzas de una empresa. Funciona con
Claude Code y con otros asistentes de IA, en Windows y Mac. No necesitas saber programar.

Lo que no hace: no decide por ti (te presenta los números y las opciones), no reemplaza al contador ni al abogado, y
nunca inventa un dato. Si algo falta, te lo pregunta.

## 2. Cómo se trabaja
Abres la carpeta en tu herramienta de IA y escribes «hola»: el asistente te dice en pocas líneas cómo van tus
proyectos, qué vence y qué decisiones te esperan. Desde ahí, pides las cosas con tus palabras: «prepara el informe de
esta semana», «estas son mis notas de la reunión». No hay comandos que memorizar.

| El asistente hace solo | El asistente te pregunta |
|---|---|
| Leer y ordenar tus documentos | Decisiones: quién aprueba, qué formato, si se cierra el mes |
| Calcular avance, métricas e indicadores | Datos que no están en ningún documento |
| Redactar borradores de informes, minutas y cartas | Confirmación antes de cambiar un registro (riesgos, cronograma, presupuesto) |
| Validar archivos y respaldar en GitHub | Qué hacer cuando dos fuentes se contradicen |

Si un dato falta, queda marcado como pendiente y te lo pide al final; nunca lo completa por su cuenta. Puedes cambiar
de asistente de IA cuando quieras: el nuevo retoma desde el traspaso que deja cada proyecto.

## 3. Lo que necesitas y cuánto cuesta usarlo
Instalarlo toma unos 15 minutos; el primer proyecto, 10 más; después, minutos al día.

| Qué | Para qué | Costo |
|---|---|---|
| Una herramienta de IA que trabaje con carpetas (Claude Code en VS Code, o Codex, Gemini, Cursor, Copilot, Antigravity) | Es quien conversa contigo y hace el trabajo | La cuenta de cada proveedor; un plan básico alcanza para el uso diario |
| Una cuenta de GitHub | Respaldo privado de tu trabajo y acceso desde otro computador | Gratuita |
| Python, Git y GitHub CLI | Los usa el asistente por dentro | Gratuitos; los instala el instalador de doble clic |
| LibreOffice (opcional) | Convertir a PDF y revisar documentos | Gratuito |

El harness está hecho para gastar poco: lee solo lo que la tarea necesita, usa modelos rápidos para lo mecánico y los
más capaces solo para juzgar, y resume con sus propias herramientas en vez de leer planillas enteras. Lo que más
consume es cargar muchos documentos de una vez (el alta): se hace una sola vez por proyecto.

## 4. Tu empresa y tus proyectos
Una carpeta es una empresa, con su propio repositorio privado; dentro caben todos sus proyectos. Si llevas varias
empresas (por ejemplo, como consultor), cada una tiene su carpeta y nada se cruza entre ellas; un tablero único te
muestra todas juntas.

El asistente elige el tipo de proyecto según lo que le cuentes, y puede combinar varios.

| Tipo | Para qué sirve | Cómo pedirlo |
|---|---|---|
| Ejecución | Un plan con tareas, hitos y contrato: avance, plazo, costo | «llevo la implementación del sistema para el cliente X» |
| Obra | Trabajo en terreno: consultas técnicas, inspecciones, estados de pago | «estoy construyendo una bodega» |
| Ágil | Un equipo que entrega por sprints | «lidero un equipo de desarrollo» |
| Cartera | Muchos ítems parecidos con etapas y métricas | «quiero llevar mi portafolio de acciones» |
| Evaluación | Evaluar propuestas de terceros con una pauta | «evalúo postulaciones a un fondo» |
| Postulación | Ganar un fondo, licitación o concurso | «quiero postular al fondo X» |
| Programa | Un contrato con varios subproyectos | «un programa con tres frentes» |
| Estudio | Una recomendación con modelo económico | «necesito una prefactibilidad» |
| Investigación | Hechos del mundo verificados con fuente | «investiga a quién ofrecer la licencia» |
| Finanzas | Llevar el área de finanzas de una empresa | «quiero llevar las finanzas de la empresa» |

## 5. Tus formatos primero
No te adaptas al harness: él se adapta a ti. Deja tus informes, minutas, presentaciones, cartas, planillas, plan de
cuentas y logo en la carpeta `empresa/_entrada/` y di «adopta mis formatos».

Por cada archivo te dirá qué es, qué sección le falta respecto de lo que el harness sabe llenar y qué se pierde si lo
adoptas tal cual (por ejemplo, «sin sección de riesgos, los riesgos no se reportan en este documento»), qué parte tuya
no sabe llenar solo, y te propondrá una versión mejorada que puedes aceptar o no. Decides archivo por archivo.

Lo adoptado pasa a ser el formato por defecto: si un proyecto tiene el suyo, manda el del proyecto; si no, el de la
empresa; si no, el del harness. Tus originales nunca se modifican y ninguna actualización los toca. Los formatos de un
cliente se adoptan igual, dentro de su proyecto.

## 6. Día a día: lo que más vas a pedir
Basta con describir lo que quieres; estas frases son ejemplos.

| Quieres | Dilo así |
|---|---|
| Saber cómo van las cosas | «¿cómo vamos?» · «dame el reporte de status» |
| Convertir notas en una minuta con acuerdos | «estas son mis notas de la reunión de hoy» |
| Sacar el informe del período | «prepara el informe de esta semana» · «arma la presentación para el comité» |
| Registrar un riesgo o un problema | «el proveedor se va a atrasar» · «registra este problema» |
| Prepararte para una reunión | «tengo comité el jueves, ¿qué llevo?» |
| Entender un correo o documento recibido | «mira este correo del cliente, ¿qué implica?» |
| Comparar versiones | «¿qué cambió en la nueva versión de las bases?» |
| Incorporar un contrato o enmienda | «llegó la enmienda 2» |
| Ver todo lo disponible | «¿qué puedo hacer?» |
| Respaldar el trabajo | «guarda» · «terminé por hoy» |

Al terminar cada tarea, el asistente deja un traspaso en el proyecto: así tú, otro computador u otra IA retoman sin
repetir nada.

## 7. Postulaciones a fondos y licitaciones
Deja las bases, anexos y aclaraciones en la carpeta de entrada del proyecto y di «prepara la postulación». El harness
barre todas las bases y arma la lista completa de requisitos (incluidos los escondidos en anexos), te ayuda a decidir
si conviene postular, reconstruye cómo evaluará el comité, redacta la propuesta por secciones, arma el presupuesto con
controles contra las bases y somete todo a un red team de revisores antes de entregar.

Si se postula en una plataforma web, reconstruye el formulario, controla el límite de caracteres de cada campo y te
entrega una hoja para copiar y pegar. Los CV, certificados y la descripción de la empresa se guardan una vez y sirven
para todas las postulaciones; te avisa si un certificado estará vencido al cierre. Si las bases exigen declarar el uso
de IA, te lo dice: esa declaración la decides y la firmas tú.

## 8. Finanzas: llevar el área como un controller
Di «quiero llevar las finanzas de la empresa» y el harness arma el ciclo completo:
1. **Arranque:** tu plan de cuentas se mapea a las líneas del reporte (ingresos, costo, margen, gastos, EBITDA, caja,
   cuentas por cobrar…) y se carga el histórico desde la contabilidad.
2. **Presupuesto anual:** supuestos con fuente, montos por línea y mes, escenarios y una versión aprobada por quien
   corresponda.
3. **Cierre mensual:** exportas el balance de comprobación del sistema contable y dices «cierra octubre». Se importa,
   se cuadra, te pregunta a qué línea van las cuentas nuevas, te explica los desvíos contra el presupuesto, calcula los
   indicadores, emite el informe y cierra el mes. Si llega algo tarde, «reabre octubre» con el motivo, se corrige y se
   vuelve a cerrar; todo queda anotado.
4. **Forecast y proyección:** cómo cierra el año con lo que va, y una proyección a tres años (resultados, balance y
   caja) desde supuestos que puedes cambiar en un Excel con fórmulas.
5. **Directorio:** informe mensual y presentación con tus formatos.

Lo que no hace: no lleva la contabilidad formal, no declara impuestos ni paga. Eso sigue en tu sistema contable, en el
contador y en tesorería; el harness consume lo que ellos producen y nunca inventa una cifra. La referencia por país
(impuestos, calendario) siempre se confirma con el contador.

### Plan estratégico (3 o 5 años)
Sobre las finanzas se arma el plan: «armemos el plan estratégico 2027-2029». El asistente te lleva por el diagnóstico
(con fuentes; lo que sostiene una apuesta se investiga), los lineamientos, los objetivos con una meta por año y las
iniciativas que los mueven, y convierte las iniciativas en la proyección financiera a 3 o 5 años. Sale el documento
para el directorio, revisado por un red team. Cada trimestre: «hagamos la revisión del plan»: metas contra reales y
una decisión por cada desvío (mantener, ajustar la meta, reasignar, descartar), que queda registrada con quién la tomó.

## 9. Investigaciones con rigor
Cuando lo que necesitas saber depende de hechos de afuera (a quién ofrecer una licencia, qué socios o proveedores
califican, el estado del arte, patentes, normativa, si algo que te dijeron es cierto), di «investiga…». El harness abre
una investigación auditable: cualquiera, con solo el informe y su expediente, puede ver de dónde salió cada afirmación
y dónde se rompería.
1. **Tú confirmas la pregunta** antes de que se busque nada: qué decidirás con el resultado.
2. **Primero se intenta matar la idea** con las hipótesis asesinas: lo que tendría que ser cierto para que valga la
   pena seguir. Si alguna dispara, se reencuadra o se cierra; es el momento más barato para detenerse.
3. Se arma el **expediente**: cada hecho con su fuente, su fecha y una marca (hecho verificado, derivado, testimonio,
   pista, vacío). Lo que dice la propia parte interesada nunca pasa como hecho.
4. Un **refutador** que no vio el razonamiento intenta tumbar cada conclusión y un **árbitro** aplica las reglas y ocho
   pruebas. Lo tumbado se retira.
5. El **informe** empieza por la respuesta, dice qué no se sabe y qué la haría cambiar.

No necesitas saber el protocolo: pregunta «¿cuál es el siguiente paso de la investigación?» y responde con la frase que
te propone el asistente (por ejemplo, «firmo P2»). Las firmas son siempre tuyas. Sirve para investigación documental en
cualquier área; la investigación experimental (encuestas, mediciones, estadística) no está cubierta.

## 10. Modo nube (opcional): operar desde el celular
El modo nube permite que el asistente trabaje con tu computador apagado: tareas programadas que corren en la nube de
Claude sobre tu repositorio privado, y una bandeja en GitHub donde dejas pedidos y respondes preguntas desde el
teléfono. Es opcional y solo funciona con Claude Code; si prefieres operar desde el PC, no activas nada y todo sigue
igual.

Nada se programa sin tu sí, tarea por tarea. Eliges cuáles quieres y puedes pausarlas o quitarlas cuando quieras:

| Tarea | Qué hace | Cuándo (lo decides tú) |
|---|---|---|
| Resumen de la mañana | Cómo van tus proyectos, lo que vence, decisiones pendientes y la bandeja; te avisa al teléfono | Lunes a viernes, 08:00 |
| Trabajar la bandeja | Toma el siguiente pedido que dejaste y lo trabaja; el resultado llega como propuesta para que apruebes | Cada 4 horas en días hábiles |
| Status semanal | El reporte de status de todos los proyectos | Lunes, 09:00 |
| Recordatorio de cierre | En finanzas, qué meses siguen sin cerrar | Día 10 de cada mes |

Desde el celular: encargas algo creando un pedido en la app de GitHub, respondes una pregunta comentando en ella,
apruebas un resultado con «sí, intégralo» y ves cómo va todo en el resumen de la mañana. La nube nunca escribe directo
sobre tu trabajo: todo llega como propuesta que tú integras. Lo que dejas en las carpetas de entrada no sale de tu PC:
la carga de documentos sigue siendo trabajo del computador.

Para empezar, di «¿puedo revisar las cosas desde el celular?»: el asistente te explica, revisa lo que hace falta (la
app de Claude en tu repositorio) y te pregunta tarea por tarea. Usa las sesiones en la nube de tu plan de Claude. Las
reglas que cumple la nube están en `NUBE.md`.

## 11. Cambiar algo después
Todo lo que decidiste al instalar se cambia conversando: di «quiero cambiar…», «configura…» o «de ahora en
adelante…». El asistente te dice qué va a cambiar y qué efecto tiene, pide tu sí y lo aplica.

| Qué puedes cambiar | Ejemplo |
|---|---|
| La empresa: nombre, responsable, a nombre de quién salen los documentos | «los informes salen a nombre de María Pérez» |
| Marca y formato: logo, colores, fuente, tamaño de hoja, formato de fecha | «usa este logo nuevo en todo» |
| Tus formatos propios | «adopta mi nueva plantilla de informe» |
| El asistente de IA y qué modelo usa para cada tipo de tarea | «voy a usar Gemini en esta carpeta» |
| Los umbrales de los semáforos | «el rojo de caja es con menos de un mes» |
| Qué se replica y qué nunca se sube | «los contratos también quedan solo en el PC» |
| El modo nube y sus tareas | «pausa el resumen de la mañana» · «ya no quiero la nube» |
| El status semanal del computador | «el reporte los viernes a las 5» |
| Un proyecto: nombre, cliente, comité, reportes | «el comité ahora es mensual» |
| Una regla de cómo trabajar | «siempre pregunta antes de registrar un riesgo» |

Nada de esto se pierde al actualizar el harness: tus ajustes viven en tu carpeta, fuera del núcleo. Y todo queda en el
historial, así que se puede deshacer: «vuelve a dejar el logo anterior».

### Ideas para mejorar el harness
Tú no editas el núcleo (las skills, herramientas y plantillas comunes): lo mantiene una persona para todas las
empresas. Lo que sí pasa es que el harness **anota solo** lo que detecta sobre sí mismo (una actualización que se
revirtió, una prueba que falla, algo que el asistente tuvo que adivinar o que una skill no cubrió) en un registro de tu
carpeta. Cuando quieras, pides «exporta las mejoras al harness»: se produce un archivo **sin nombres, correos, RUT ni
montos**, lo revisas y se lo envías al mantenedor. Él decide, y cuando actualizas, tu carpeta marca cuáles entraron.
Para verlas: «¿qué mejoras al harness hay anotadas?».

### Salud del harness (entropía)
Todo lo que se acumula y nadie retira termina estorbando: instrucciones repetidas en dos documentos, lecciones
viejas que nadie confirmó, pendientes olvidados, respaldos de actualizaciones pasadas. Cada tanto (el harness te lo
recuerda a los 30 días) pide «revisa la salud del harness»: te muestra qué propone retirar y **no borra nada** sin tu
sí. Si trabajas con Claude Code, además te avisa cuando una sesión lleva muchas acciones (conviene guardar y abrir una
nueva: la calidad baja antes de que la ventana se llene) y no te deja cerrar con cambios sin guardar y el traspaso viejo.

## 12. Privacidad y seguridad
Tu trabajo vive en tu computador y en un repositorio **privado** de tu cuenta de GitHub, que solo tú ves. El harness
que descargas es público, pero al instalarlo se desconecta de él: nada tuyo va a parar allá.

| Nunca se sube a GitHub | Sí se sube (a tu repositorio privado) |
|---|---|
| Lo que dejas en las carpetas de entrada (originales, PDF, exportaciones de la contabilidad) | Los datos del proyecto: registros, métricas, minutas, informes |
| CV, certificados, estados financieros y datos personales (solo queda una ficha) | Copias fieles en texto de bases, contratos y actas, para trabajar desde otro computador |
| El paquete firmado de una postulación | Tus formatos adoptados y tu configuración |
| Claves y contraseñas | |

Dos controles automáticos lo garantizan: uno impide guardar en Git un archivo confidencial, y otro revisa que las
planillas estén bien formadas. Si uno bloquea algo, es a propósito: el asistente te explica qué hacer. Nunca mezcla
datos de dos empresas. Si una norma o un contrato exige declarar el uso de IA, te lo avisa y la decisión es tuya.

## 13. Varias empresas, otro computador, otra IA
- **Otra empresa:** «crea la carpeta para la empresa X». Te preguntará si son empresas independientes o de una misma
  entidad, y si quieres un tablero único para ver todas juntas (va en una carpeta y un repositorio privado aparte, solo
  tuyo). Cada empresa queda en su carpeta y su repositorio; nada se cruza.
- **Otro computador:** antes de dejar el primero, di «guarda». En el otro, instala tu herramienta de IA y haz doble
  clic en el instalador: después de conectar GitHub te ofrece descargar tus empresas. Desde ahí, «guarda» al terminar
  en uno y «hola» al empezar en el otro.
- **Otra IA:** abre la carpeta con la nueva y escribe «hola». Se configura sola y retoma desde el traspaso de cada
  proyecto.
- **Versión nueva del harness:** «actualiza el harness». Se reemplaza solo el núcleo; tus proyectos, formatos, ajustes
  y datos no se tocan, y si algo fallara, la actualización se deshace sola.

## 14. Si algo falla
| Pasa esto | Haz esto |
|---|---|
| La IA no reconoce el harness al decir «hola» | Escríbele: «lee el archivo AGENTS.md y sigue sus instrucciones» |
| Algo se queda detenido en el chat o pregunta «[Y] Sí [N] No» | Di «cancela esa tarea» y haz doble clic en el instalador; al terminar, escribe «ya corrí el instalador» |
| Un control no deja guardar un archivo | Es a propósito: ese archivo es confidencial. El asistente te dice qué hacer |
| Dice que falta Python aunque se instaló | Cierra y vuelve a abrir tu herramienta de IA |
| La conexión con GitHub no se completó | Di «conecta mi cuenta de GitHub» |
| Un número del informe no te cuadra | Pregunta «¿de dónde sale esta cifra?»: todo tiene fuente en los datos del proyecto |
| No sabes qué pedir | «¿qué puedo hacer?» |

Si nada de esto resuelve el problema, pídele al asistente que ejecute el diagnóstico («revisa el entorno») y envía ese
resultado a quien te entregó el harness.

## 15. Glosario mínimo
| Término | Qué es |
|---|---|
| Harness | La carpeta con las reglas, herramientas y procedimientos que guían a la IA |
| Núcleo | La parte del harness que se actualiza desde el repositorio público; nunca lleva tus datos |
| Empresa | La dueña de la carpeta; una carpeta = una empresa = un repositorio privado |
| Proyecto | Cada cosa que llevas dentro de la empresa, con su tipo (arquetipo) |
| Arquetipo | El tipo de proyecto: ejecución, obra, ágil, cartera, evaluación, postulación, programa, estudio, investigación, finanzas |
| Skill | Un procedimiento que la IA sigue (preparar la postulación, cerrar el mes); se activa solo al pedirlo con tus palabras |
| Entrada (`_entrada/`) | La carpeta donde dejas documentos tal cual; no se sube a GitHub |
| Traspaso | La nota que deja la IA al terminar, para retomar después sin repetir |
| Status | El resumen de cómo van todos los proyectos: semáforos, vencimientos, decisiones |
| Repositorio privado | Tu copia de respaldo en GitHub, que solo tú ves |
| Modo nube | Opción para que la IA trabaje tareas programadas con el computador apagado (solo con Claude) |
