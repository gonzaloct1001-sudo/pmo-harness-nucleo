# PMO Harness 3.5: manual de usuario

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
| Ver tus pendientes del día | «¿qué tengo pendiente hoy?» (con Claude Code llega sola en tu primer mensaje del día) |
| Entender algo de un vistazo | «explícame el cierre de octubre en una página» · «hazme un gráfico del avance» |
| Decidir con números inciertos | «¿qué tan probable es cerrar el año sobre la meta?» · «¿conviene subir los precios?» |
| Un documento largo con el formato oficial | «pasa este informe a la plantilla de la empresa» |
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

**Antes de partir, un plan cuando hace falta.** Si lo que pides es chico, lo hace. Si es grande, se puede entender de
más de una forma o cuesta deshacerlo, primero te muestra en cinco líneas qué entendió, qué va a hacer y qué va a
tocar, y espera tu respuesta: «ejecuta», «ajusta…» o «plan detallado» (te lo arma como una página). Si quieres que
vaya directo, dilo: «hazlo ya». Y si prefieres que siempre parta con un plan, o que nunca lo ofrezca: «de ahora en
adelante, siempre con plan» o «sin planes previos».

**La agenda del día.** Una vez al día, en tu primer mensaje, te muestra lo vencido, lo de hoy y lo que viene en dos
semanas, de todos tus proyectos, más los informes que tocan ese día (si le dijiste «el informe semanal sale los
lunes»). Un proyecto en pausa no aparece: «pon el proyecto X en pausa».

**Páginas para explicar.** Cuando algo se entiende mejor viéndolo, pide una página: cifras clave, gráficos, pasos y
fechas en un archivo que se abre con doble clic, sin internet, y se puede imprimir o adjuntar a un correo. Cada
gráfico trae su tabla de datos, y los números salen de tus registros. No se publica en ningún sitio: queda en la
carpeta del proyecto.

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

### Análisis para decidir
Cuando una decisión depende de números inciertos, pide el análisis en vez de una sola cifra:
- **«¿Qué tan probable es…?»** En lugar de suponer que las ventas subirán exactamente 5 %, le das un rango (entre 2 y
  8 %, lo más probable 5) y dices de dónde sale. El harness prueba miles de combinaciones y te responde con una
  probabilidad («hay 62 % de cerrar sobre la meta»), el rango donde cae el resultado ocho de cada diez veces, y **qué
  supuesto pesa más**. Sirve sobre un estado de resultados, un flujo o un presupuesto: «quiero un análisis de
  sensibilidad de este estado de resultados».
- **Cinco preguntas frecuentes ya armadas:** «¿conviene subir los precios?», «¿cuánto tengo que vender para cubrir
  los gastos y mi retiro?», «¿qué mueve más mi margen: clientes, frecuencia o precio?», «¿cuánta caja me pide crecer
  y en cuánto vuelve?», «¿cuánto puedo crecer sin pedir financiamiento?».
- **«¿Qué clientes y productos me dejan margen?»** Con tus ventas por línea arma la rentabilidad por producto y por
  cliente, y un mapa de cuatro cuadrantes según cuánto contribuye cada cliente y qué tan bien calza con tu empresa.
  **Los nombres de tus clientes no salen de tu computador**: en los datos cada cliente es un código (C-0001) y el
  nombre queda en un archivo local; para revisar con nombres, pídelo «con nombres» y esa versión tampoco se sube.

- **«¿Cuál es la mejor decisión?»** Le dices qué puedes elegir (el precio, la dotación, cuánto invertir) y entre qué
  valores, y qué provoca cada decisión; prueba las combinaciones y te muestra la mejor según lo que tú priorices: el
  promedio, un escenario malo o la probabilidad de llegar a la meta. La decisión sigue siendo tuya.
- **«Pronostica las ventas de los próximos meses»**, **«¿qué explica este resultado?»**, **«¿qué grupos de clientes
  tengo?»**, **«¿terminamos en la fecha comprometida?»**: pronósticos con su error comprobado, variables que
  acompañan a un resultado, grupos de clientes según cómo compran, y la probabilidad de cumplir el plazo con las
  tareas que más lo mueven.

**Dos niveles.** Todo lo anterior funciona con lo que el harness ya trae (nivel base). Para algunos casos conviene el
nivel especialista, que usa programas adicionales de análisis: más datos, estacionalidad, varias variables a la vez,
muchos clientes. Antes de analizar, el asistente mira tus datos y te dice cuál conviene y por qué; si conviene el
especialista y no lo tienes, **te pregunta**: seguir con el nivel base (y qué deja sin responder) o instalarlo (una
vez, unos 450 MB, con internet). No instala nada sin tu sí, y nunca te presenta un resultado simple como si fuera el
robusto.

Cada análisis queda guardado con su pregunta, sus supuestos y sus resultados, y se puede repetir exacto. El resultado
vale lo que valgan los rangos y los datos que le diste: por eso la página muestra los supuestos, marca los que no
tienen fuente y dice cuánto se equivocó el método al comprobarlo.

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
| Qué se replica y qué nunca se sube | «los contratos también quedan solo en el PC» · «la carpeta de sueldos nunca se sube» |
| Cómo parte cada tarea | «de ahora en adelante, siempre con plan» · «sin planes previos» |
| Algo que el harness no trae | «quiero un aviso cada mañana con lo que vence» (queda como extensión tuya) |
| El modo nube y sus tareas | «pausa el resumen de la mañana» · «ya no quiero la nube» |
| El status semanal del computador | «el reporte los viernes a las 5» |
| Un proyecto: nombre, cliente, comité, reportes | «el comité ahora es mensual» |
| Una regla de cómo trabajar | «siempre pregunta antes de registrar un riesgo» |

Nada de esto se pierde al actualizar el harness: tus ajustes viven en tu carpeta, fuera del núcleo. Y todo queda en el
historial, así que se puede deshacer: «vuelve a dejar el logo anterior».

### Lo tuyo y las actualizaciones
El harness tiene dos partes que nunca se mezclan: el **núcleo** (lo común, que llega con cada versión) y **lo tuyo**
(tus proyectos, tu empresa, tus skills propias y tus extensiones en `empresa/extensiones/`). Una actualización solo
reemplaza el núcleo, y antes de aplicar te muestra una sección «Lo tuyo en esta actualización»:
- lo que agregaste a la configuración, a la lista de lo que nunca se sube o a las dependencias **se fusiona** con lo nuevo;
- si creaste algo con el mismo nombre que algo nuevo del núcleo, lo tuyo **queda entero con otro nombre** (`-propia`);
- si cambiaste un archivo del núcleo y la versión nueva no lo toca, **queda como lo dejaste**; si también lo toca, tu
  versión queda en un respaldo y te dice exactamente cuál;
- si tienes extensiones con pruebas propias, se ejecutan antes y después: **si algo tuyo dejara de funcionar, la
  actualización se deshace sola** y te dice qué ajustar.
Tu carpeta guarda además un **catastro**: la lista de los archivos del núcleo tal como se instalaron. Con él puedes
preguntar en cualquier momento «¿mi harness está intacto?»: te dice qué archivos se cambiaron en tu carpeta, cuáles
faltan y cuáles son tuyos. Si algo se cambió o se borró sin querer, «restaura ese archivo» lo devuelve a su original
(lo que había queda en un respaldo); el asistente te avisa al empezar si falta algo o si algo cambió hace poco.

Por eso el asistente no edita el núcleo en tu carpeta: cuando pides algo que el harness no trae, lo construye como
extensión tuya y, si le serviría a cualquiera, lo anota como idea para el núcleo.

### Ideas para mejorar el harness
Tú no editas el núcleo (las skills, herramientas y plantillas comunes): lo mantiene una persona para todas las
empresas. Lo que sí pasa es que el harness **anota solo** lo que detecta sobre sí mismo (una actualización que se
revirtió, una prueba que falla, algo que el asistente tuvo que adivinar o que una skill no cubrió) en un registro de tu
carpeta. Cuando quieras, pides «exporta las mejoras al harness»: se produce un archivo **sin nombres, siglas, correos,
RUT ni montos**, lo revisas y se lo envías al mantenedor (**solo ese archivo**: el registro interno guarda los textos
tal como se escribieron). Él decide, y cuando actualizas, tu carpeta marca cuáles entraron.
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

Hay tres niveles: lo que **se versiona** (datos y salidas), lo que deja una **copia fiel en texto** (bases, contratos,
actas) y lo que deja **solo una ficha** (el archivo y su contenido no salen de tu computador). Tú puedes sumar al
tercer nivel lo que quieras: «la carpeta de sueldos nunca se sube». Queda anotado en un archivo tuyo
(`empresa/confidencialidad.yaml`) que ninguna actualización toca. Los nombres de tus clientes siguen la misma regla:
en los datos van como códigos y el nombre queda en una carpeta local.

Los controles miran lo que realmente está por guardarse, no cómo se escribió la instrucción: uno revisa cada guardado,
otro revisa **antes de subir** a GitHub (por si algo se guardó desde otro computador o con otra herramienta), y con
Claude Code un tercero saca de inmediato cualquier archivo confidencial que se haya preparado por error. Ninguno se
puede saltar desde el asistente. Si pones un Word, un PDF o una imagen fuera de las carpetas donde el harness los
espera, te **avisa** al guardar para que digas si es material del cliente (puedes pedir que lo bloquee). Para revisar
lo que ya está en tu repositorio: «audita la confidencialidad». Lo que queda solo en tu computador no tiene copia en
GitHub: si es importante, respáldalo tú en un lugar seguro.

Otro control revisa que las planillas estén bien formadas. Si uno bloquea algo, es a propósito: el asistente te
explica qué hacer. Nunca mezcla datos de dos empresas. Si una norma o un contrato exige declarar el uso de IA, te lo
avisa y la decisión es tuya.

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
