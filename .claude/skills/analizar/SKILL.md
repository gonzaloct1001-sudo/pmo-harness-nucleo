---
name: analizar
description: Análisis con números para decidir: probabilidad de una meta y qué supuesto pesa más, la mejor combinación de decisiones, modelos de precio, equilibrio, palancas, caja y crecimiento, rentabilidad y grupos de clientes, pronósticos, qué variables explican un resultado y plazo del proyecto. Úsala con «análisis de sensibilidad», «¿qué tan probable es…?», «pronostica las ventas», «¿qué clientes me convienen?».
---

> Reglas que aplican (léelas si no están en tu contexto): `reglas/datos.md`, `reglas/trabajo.md`, `reglas/confidencialidad.md`.

# Analizar

Tres herramientas. Todas calculan siempre igual, dejan registro y arman su página:
- `python herramientas/simular.py`: simulación con rangos, probabilidad de una meta, sensibilidad y, con
  `--optimizar`, la mejor combinación de decisiones. `--modelos` lista los modelos con sus entradas.
- `python herramientas/rentabilidad.py <proyecto>`: rentabilidad por cliente y producto, con el mapa de clientes.
- `python herramientas/experto.py <pronosticar | regresion | segmentar | plazo>`: pronósticos, variables que explican
  un resultado, grupos de clientes y plazo del proyecto. Cada uno tiene `--help` y `--diagnosticar`.

Hay dos niveles. El **base** viene siempre (no instala nada). El **especialista** usa bibliotecas que se instalan
una vez (`experto.py instalar`, unos 450 MB) y agrega métodos más robustos, comparados siempre contra el simple.

Un análisis es una tarea grande y casi siempre ambigua: parte con el plan breve del principio 23 (la pregunta, el
modelo, qué supuestos llevarán rango y de dónde saldrá cada número) y espera el sí.

## 0. ¿Nivel base o especialista? Se decide antes de analizar
1. Mira si el nivel base alcanza: ejecuta el diagnóstico de la herramienta que corresponda (`experto.py <análisis> …
   --diagnosticar`; `simular.py --optimizar` avisa solo cuando hay demasiadas combinaciones). Dice qué nivel conviene
   y por qué (cuánto se equivoca ya el método simple, si queda un patrón sin aprovechar, cuántas variables o clientes).
2. Si el base alcanza: analiza con el base, sin preguntar, y dilo en una línea con su motivo.
3. Si conviene el especialista y está instalado (`experto.py estado`): úsalo.
4. Si conviene el especialista y **no** está instalado: **pregunta al usuario antes de analizar**, con las dos opciones
   y lo que implica cada una:
   - seguir con el nivel base: qué responde y qué deja sin responder (los motivos del diagnóstico, en simple);
   - instalar el especialista: una vez, unos 450 MB, en este computador, con internet; qué agrega para esta pregunta.
   No instales sin su sí (`python herramientas/experto.py instalar`). Si elige el base, analiza y deja dicho en la
   respuesta que el resultado es del nivel base. Recuerda su elección en `empresa/estilo.md` si dice «siempre así».
5. Nunca presentes un resultado del nivel base como si fuera el robusto, ni instales «por si acaso».

## 1. Primero la pregunta
Escríbela en una frase que se pueda responder con un número: «¿qué probabilidad hay de cerrar el año sobre 150 MM$?»,
«¿cuánto volumen puedo perder si subo 5 %?». Si el usuario pide «un análisis» sin pregunta, propón dos o tres y que elija.

## 2. Elegir el camino
| La pregunta | Camino |
|---|---|
| ¿Conviene subir o bajar el precio? | `simular.py`, modelo `precio-volumen` |
| ¿Cuánto hay que vender para cubrir los gastos y lo que se quiere retirar o contratar? | modelo `equilibrio` |
| ¿Qué mueve más el margen: más clientes, más frecuencia o más margen por venta? | modelo `palancas` |
| ¿Cuánta caja pide crecer y en cuánto vuelve? | modelo `caja-crecimiento` |
| ¿Cuánto puedo crecer sin financiamiento? ¿Cuánto pide el plan? | modelo `crecimiento-sostenible` (crúzalo con `finanzas.py --proyectar` y con las metas del plan estratégico) |
| Sensibilidad de un resultado propio (un estado de resultados, un flujo, un presupuesto) | `modelo: formula`, con la fórmula escrita desde las líneas reales |
| ¿Qué clientes y productos dejan margen? ¿Dónde está el riesgo? | `rentabilidad.py` |
| ¿Cuál es la mejor combinación de lo que yo decido (precio, dotación, inversión)? | `simular.py --optimizar` (sección 3) |
| ¿Cuánto venderé (o gastaré) los próximos meses? | `experto.py pronosticar --datos <serie mensual>` |
| ¿Qué variables explican este resultado, y cuánto? | `experto.py regresion --datos <tabla> --objetivo <columna>` |
| ¿Qué grupos de clientes tengo según cómo compran? | `experto.py segmentar <proyecto>` |
| ¿Qué probabilidad hay de terminar en la fecha comprometida? ¿Qué tareas la mueven? | `experto.py plazo <proyecto>` |

## 3. Simulación y sensibilidad
1. `python herramientas/simular.py --nuevo <modelo> --proyecto proyectos/<slug> --id <nombre> --pregunta "…"` crea
   `analisis/<nombre>/analisis.yaml`.
2. Completa las entradas. Lo conocido va como valor fijo, tomado de los registros o de un script (`finanzas.py
   --estados`, `evaluar_metricas.py`), nunca de memoria. Lo incierto va como rango `{min, probable, max, fuente}`.
   **Cada rango lleva su fuente**: un dato histórico, una cotización, o «juicio de <quién>» si es una estimación; no
   inventes rangos: pregúntalos. Si hay objetivo, `meta` y `sentido`.
3. `python herramientas/simular.py proyectos/<slug>/analisis/<nombre> --revisar` y luego sin `--revisar` (`--abrir`
   para verla). Deja `informe.html`, `resultado.json` y la fila de `corridas.csv`.
4. Cuenta el resultado en este orden: la probabilidad o el rango (ocho de cada diez escenarios entre tal y tal), el
   supuesto que más pesa, cuánto tendría que moverse cada uno solo para llegar a la meta, y qué supuestos no tienen
   fuente. Una frase por punto.
5. **La mejor decisión** (`--optimizar`): lo que la empresa elige se escribe como decisión (`{decision: true, min, max,
   paso, valor}`), y lo que esa decisión provoca se escribe con su fórmula (`perdida_volumen: {formula: "sensibilidad *
   cambio_precio"}`, con `sensibilidad` como supuesto con rango y fuente). Sin esa relación, la «mejor» decisión será
   siempre el extremo del rango: la herramienta lo advierte y tú lo dices. El objetivo (`optimizar.objetivo`) lo elige
   el usuario: el promedio, un escenario malo (`p10`) o la probabilidad de la meta. La decisión es suya (principio 9).

## 4. Rentabilidad por cliente y producto
**Los clientes van siempre por identificador (C-0001).** El nombre queda solo en `finanzas/_local/clientes-mapa.csv`,
que no sale del computador; si alguien escribe un nombre en los datos, la herramienta lo convierte, y el control de
Git no deja guardarlo sin convertir. Los agregados (por cuadrante, por producto, totales) se usan libremente.
1. Sin opciones, la herramienta dice qué hay y qué falta.
2. `--importar-ventas <exportación .csv o .xlsx>` (del material de `_entrada/`) y, si hay, `--importar-cxc`. Las horas
   por cliente y la afinidad (1 a 10: qué tan bien calza el cliente con la empresa) se preguntan al usuario y van en
   `finanzas/clientes.csv`; el costo por hora, en `rentabilidad.costo_hora` de `proyecto.yaml` o con `--costo-hora`.
3. `--analizar [--desde --hasta]`: tablas por producto y cliente, mapa de cuatro cuadrantes (Cuidar, Asegurar,
   Desarrollar, Revisar), margen en riesgo y concentración; página en `finanzas/analisis/`.
4. Para revisar con nombres en este computador: `--con-nombres` (queda en `finanzas/_local/`) o `--quien <id>`.
   Nunca copies nombres de clientes a un registro, un traspaso, un informe versionado ni una tarea de la nube.

## 5. Cómo se lee, y lo que no se dice
- El resultado vale lo que valgan los supuestos: dilo siempre junto a la cifra, con los rangos sin fuente por su nombre.
- Los supuestos se simulan independientes; si dos se mueven juntos (precio y volumen), adviértelo.
- El mapa de clientes describe el período; no predice ni dice cuánto «cuesta» un cliente. Con menos de ocho clientes,
  los cortes son orientación. Una decisión sobre un cliente (subirle el precio, dejarlo) la toma el usuario (principio 9).
- Correlación no es causa: no expliques un patrón de los datos como efecto de algo sin evidencia aparte.
- Para explicar el resultado a otros, la página ya está hecha; si hay que resumirla, skill `explicar`.

## 6. Pronósticos, variables, grupos de clientes y plazo (`experto.py`)
Cada uno: primero `--diagnosticar` (sección 0), después el análisis; deja `informe.html` en `analisis/<nombre>/`.
- **Pronosticar**: una serie mensual con al menos 6 meses; sale con el error comprobado en los últimos meses y un
  rango. Cuenta siempre el error junto al número, y que un pronóstico supone que el futuro se parece al pasado.
- **Regresión**: qué variables acompañan a un resultado. Solo se destaca una variable si el modelo predice mejor que
  el promedio en datos que no vio; si no, dilo así. Una relación no es una causa, y vale dentro del rango observado.
- **Segmentar**: grupos por reglas (base) o por datos (especialista, con dos comprobaciones: que haya grupos de
  verdad y que sean estables). Si no pasan, se usan las reglas. Los clientes van por identificador (sección 4).
- **Plazo**: probabilidad de terminar en la fecha comprometida y tareas que más la mueven. Los rangos por defecto son
  supuestos: pide al responsable de cada tarea crítica su duración optimista y pesimista (`cronograma/incertidumbre.csv`).

## 7. Lo que no hace
No simula las fórmulas de un Excel ajeno: se escribe la fórmula del resultado como `modelo: formula`. No modela que
dos supuestos se muevan juntos, salvo que lo escribas con una fórmula. No decide: ordena la incertidumbre.
