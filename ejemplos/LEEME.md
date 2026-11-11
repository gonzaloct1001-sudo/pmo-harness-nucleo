# Ejemplos: probar el harness con datos ficticios

Cada carpeta de `ejemplos/` es un proyecto ficticio completo (datos inventados, nombres inventados) con el que se puede
probar una capacidad del harness antes de usarla con datos reales. Ninguna prueba modifica los ejemplos: cada
herramienta se ejecuta sobre ellos y la batería (`python pruebas/ejecutar_pruebas.py`) trabaja sobre copias.
Para los comandos, usa `python` (en Windows, `py` si no responde; en Mac, `.venv/bin/python`).

Orden sugerido: primero lo que más se usa (cargar un proyecto desde documentos, finanzas, investigación) y después lo
específico.

### Prueba 1 — Alta a partir de documentos (arquetipo ejecución)
`ejemplos/` también trae un programa inventado ("Programa Andes Digital"):
- `paquete-alta-andes/`: documentos en bruto (contrato, enmienda, Gantt, informe semanal, PEP, acta,
  correos, exportación de ChatGPT, logo), con contradicciones sembradas a propósito.
- `demo-andes/`: cómo debería quedar el proyecto después del alta. Sirve como "respuesta correcta".

Prueba sugerida:
1. `/instalar` y como nombre del programa responde "Prueba Andes".
2. Copia las subcarpetas de `ejemplos/paquete-alta-andes/` dentro de `proyectos/prueba-andes/_entrada/`.
3. Escribe **listo** y compara el resultado con `ejemplos/demo-andes/`.

El `_LEEME-paquete.md` del paquete indica qué debería resolver sola y qué debería preguntar. Los datos están
fechados en torno al 25-09-2026: si pruebas después, pide "usa fecha de corte 25-09-2026".
Con el demo ya cargado, prueba también **"¿vamos atrasados? usa fecha de corte 25-09-2026"**: debería usar
valor ganado y ruta crítica (SPI 0,79, CPI 0,87, término pronosticado 29 días después del contractual).

### Prueba 2 — Finanzas (arquetipo finanzas)
`ejemplos/finanzas-demo/` es la gestión financiera ficticia de una distribuidora: plan de cuentas mapeado, enero a
septiembre de 2026 importados, presupuesto 2026, enero a agosto cerrados, una cuenta sin mapear en septiembre (6999) y
un exceso de arriendo en julio.
1. `python herramientas/finanzas.py ejemplos/finanzas-demo --hoy 2026-10-12`: dónde va y el siguiente paso (mapear la 6999).
2. `python herramientas/finanzas.py ejemplos/finanzas-demo --estados --periodo 2026-08 --excel estados.xlsx`: resultados
   mes y acumulado contra presupuesto, balance que cuadra, flujo de caja e indicadores; el Excel lleva fórmulas.
3. `python herramientas/finanzas.py ejemplos/finanzas-demo --importar ejemplos/paquete-finanzas-demo/balance_comprobacion_2026-10.xlsx --periodo 2026-10 --vista-previa`:
   detecta la fila de encabezados y las columnas de una exportación «de sistema contable» y comprueba que cuadra.
4. Para una propia: **«quiero llevar las finanzas de mi empresa»** y después, cada mes, **«cierra octubre»**.
---

### Prueba 3 — Investigación auditable (arquetipo investigación)
`ejemplos/investigacion-demo/` es una investigación ficticia cerrada (qué planta de compostaje contratar), con todas
sus puertas firmadas, un testimonio que no se deja pasar como hecho, una conclusión retirada por el refutador y una
planta en reserva por falta de evidencia.
1. `python herramientas/investigacion.py ejemplos/investigacion-demo --revisar --hoy 2026-10-30`: 0 errores.
2. `python herramientas/investigacion.py ejemplos/investigacion-demo --instancia 2026-01-planta-compostaje --auditar --hoy 2026-10-30`
   y `--muestra --semilla 7`: pruebas mecánicas y muestra al azar repetible.
3. Para una propia: **«investiga a quién le podríamos ofrecer la licencia de X»**. El asistente abre la investigación
   en sondeo, te pide la firma del encuadre (P0) y después de las hipótesis asesinas (P2), y en cada momento puedes
   preguntar **«¿cuál es el siguiente paso de la investigación?»**.

### Prueba 4 — Diseño desde cero
Escribe algo como **"quiero llevar el seguimiento de una granja de bots de trading, con sus métricas"** o
**"quiero llevar la construcción de una casa"** y revisa qué diseño propone `nuevo-proyecto`.

### Prueba 5 — Formatos propios
`ejemplos/paquete-formatos-demo/` trae los formatos ficticios de una cooperativa: un informe mensual sin sección de
riesgos, un acta sin decisiones, una planilla con fórmulas, una presentación completa, un plan de cuentas y un logo.
1. Copia el paquete a `empresa/_entrada/` y di **«adopta mis formatos»**: debería detectar el tipo de cada archivo,
   avisar lo que falta en el informe y el acta, proponer la versión mejorada y reconocer el plan de cuentas como
   archivo base.
2. Adopta el informe mejorado y la marca; luego **«genera el informe mensual de octubre»**: sale con tu plantilla,
   tus estilos y tu logo, con las secciones vacías eliminadas.

### Prueba 6 — Programa con subproyectos (arquetipo programa)
`ejemplos/programa-demo/` es un programa ficticio con un contrato padre, dos enmiendas y tres subproyectos (ERP, app
ágil y portal) con dependencias entre ellos, contingencia del programa y por subproyecto, y una persona compartida.
1. `python herramientas/programa.py ejemplos/programa-demo --hoy 2026-10-15 --excel`: avance y plazo por subproyecto,
   presupuesto y contingencia, sobreasignación, enmienda pendiente y ruta crítica del programa; genera el Gantt macro, el
   detallado, el de cada subproyecto y el control presupuestario en Excel.
2. Para uno propio: «nuevo proyecto» → «programa nuevo», y luego «agrega un subproyecto». Un proyecto sin relación con el
   programa se crea aparte («nuevo proyecto» → «independiente»).

### Prueba 7 — Portafolio de acciones (arquetipo cartera)
`ejemplos/portafolio-acciones/` es un portafolio ficticio completo: 12 acciones inventadas en distintas
etapas, transacciones, precios mensuales con un índice de referencia, datos fundamentales, fichas con tesis,
política de inversión como reglas y un script propio que calcula rentabilidad, volatilidad, caída máxima,
Sharpe y concentración. Instrucciones sugeridas en el chat de tu asistente:

1. **"Evalúa las métricas del portafolio de ejemplo con corte al 31-08-2026."**
   Debería encontrar: una acción sobre el límite de 20% (TCOR), una con deuda/EBITDA sobre la política
   (PNOR), una en análisis sin tesis escrita (RAUS), una en preselección que no cumple el filtro de ROE
   (SALI), una ficha con revisión vencida (BPAC), una candidata a avanzar (FARA) y la cartera rindiendo
   bajo el índice.
2. **"Genera la revisión mensual de agosto del portafolio de ejemplo."**
3. **"Agrega la métrica 'dividendos recibidos en 12 meses' al portafolio de ejemplo."**
4. **"Pasa FARA a preselección"** y luego **"crea la ficha de RAUS"** (te ayudará a escribir la tesis).
5. **"Quiero un reporte trimestral llamado Informe de Gestión, en PowerPoint, con desempeño, política y
   decisiones."** (diseño de un reporte propio por conversación).

Todo es ficticio y sirve para probar la herramienta: no es información ni recomendación de inversión.

### Prueba 8 — Estudio económico (arquetipo estudio)
`ejemplos/estudio-solar/` tiene los supuestos de una planta solar ficticia y su modelo en Excel.
**"Revisa la evaluación económica del estudio solar: ¿qué tan robusta es?"** Debería explicar VAN, TIR y
recuperación, señalar que con 10% menos de ahorro el VAN queda cerca de cero y que dos supuestos críticos
tienen confianza baja o media.

### Prueba 9 — Equipo de software (arquetipo ágil)
`ejemplos/equipo-software/` tiene 5 sprints, backlog, despliegues, deuda técnica, requisitos, ADR y un postmortem.
1. **"Planifiquemos el sprint S5 del equipo de software de ejemplo."**
2. **"¿Cómo estamos en entrega? Dame las métricas DORA."** (tasa de falla de 33%, dos incidentes).
3. **"¿Qué requisitos no tienen pruebas?"**

### Prueba 10 — Evaluación de postulaciones (arquetipo evaluación)
`ejemplos/fondo-innovacion/` trae las bases de un fondo ficticio, la pauta ya construida y 3 postulaciones.
1. **"Evalúa las postulaciones del fondo de ejemplo."** Debería: recordarte la confidencialidad, declarar
   inadmisible a P-003 (menos de 2 años de actividad), evaluar cada postulación con un subagente citando
   evidencia, dejar los puntajes como *propuesta* y pedirte la revisión antes del acta.
2. **"Construye de nuevo la pauta desde las bases"** para probar `evaluar-propuestas`.

### Prueba 11 — Postulación a un fondo (arquetipo postulación)
`ejemplos/paquete-postulacion-demo/` trae bases ficticias de un fondo de innovación con trampas sembradas: un
requisito excluyente escondido en un anexo, una aclaración que cambia el límite de páginas y exige declarar el uso
de IA, un certificado con vigencia máxima y un presupuesto del cliente que no cumple el cofinanciamiento.
`ejemplos/postulacion-demo/` muestra cómo debería verse a mitad de camino (etapa red team). Prueba:
1. `python herramientas/postulacion.py ejemplos/postulacion-demo --hoy 2026-11-03`: etapa, compuertas, fallas fatales.
2. `python herramientas/presupuesto_postulacion.py ejemplos/postulacion-demo/economico/presupuesto.yaml --salida prueba.xlsx`:
   abre `prueba.xlsx` y cambia un aporte en la hoja Presupuesto: la hoja Controles se recalcula sola (para cambios
   definitivos se edita el YAML y se vuelve a generar).
3. Crea `prueba-postulacion` con el arquetipo `postulacion`, copia las subcarpetas del paquete a `_entrada/` y di
   "prepara la postulación".

### Prueba 13 — Documento largo con la plantilla de la empresa y página para explicar
1. `python herramientas/md_a_docx.py ejemplos/documento-largo-demo/informe.md informe-avance.docx --plantilla
   ejemplos/documento-largo-demo/plantilla-informe.docx --proyecto ejemplos/demo-andes` y abre el Word: portada,
   historia de revisiones, índice (acepta «actualizar campos»), títulos numerados por la plantilla, figura con
   leyenda y anexos. El detalle de qué debería verse está en `ejemplos/documento-largo-demo/LEEME.md`.
2. Pide «explícame en una página cómo va demo-andes»: la skill `explicar` arma la página con cifras, gráficos y lo
   que viene, y te dice dónde quedó.

### Prueba 12 — Plan estratégico (arquetipo estrategia)
`ejemplos/estrategia-demo/` es el plan 2027-2029 ficticio de una empresa de mantención: diagnóstico con fuentes,
lineamientos aprobados, cuatro objetivos con metas por año, cinco iniciativas y la revisión del primer trimestre con
sus decisiones.
1. `python herramientas/estrategia.py ejemplos/estrategia-demo --hoy 2027-04-10`: dónde va el plan y el siguiente paso.
2. `python herramientas/estrategia.py ejemplos/estrategia-demo --revisar`: la cascada cuadra (sin errores; avisos sobre
   el objetivo propuesto que aún no tiene iniciativa).
3. `python herramientas/estrategia.py ejemplos/estrategia-demo --roadmap`: Gantt de las iniciativas por objetivo.
4. Para uno propio: **«armemos el plan estratégico 2027-2029»** y, cada trimestre, **«hagamos la revisión del plan»**.

