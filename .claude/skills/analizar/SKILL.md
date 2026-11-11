---
name: analizar
description: Análisis con números para decidir: qué tan probable es llegar a una meta y qué supuesto pesa más (simulación y tornado), modelos de precio y volumen, punto de equilibrio, palancas del margen, caja para crecer y crecimiento sostenible, y rentabilidad por cliente y producto. Úsala con «análisis de sensibilidad», «¿qué tan probable es…?», «¿conviene subir precios?», «¿qué clientes me convienen?».
---

> Reglas que aplican (léelas si no están en tu contexto): `reglas/datos.md`, `reglas/trabajo.md`, `reglas/confidencialidad.md`.

# Analizar

Dos herramientas del nivel base (no instalan nada). Las dos calculan siempre igual, dejan registro y arman su página:
- `python herramientas/simular.py`: simulación con rangos, probabilidad de una meta y sensibilidad. `--modelos` lista
  los modelos con sus entradas.
- `python herramientas/rentabilidad.py <proyecto>`: rentabilidad por cliente y producto, con el mapa de clientes.

Un análisis es una tarea grande y casi siempre ambigua: parte con el plan breve del principio 23 (la pregunta, el
modelo, qué supuestos llevarán rango y de dónde saldrá cada número) y espera el sí.

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

## 6. Lo que este nivel no hace
Pronósticos de series de tiempo, regresión con varias variables, segmentación por datos y optimización piden
bibliotecas que no vienen instaladas: dilo, y resuelve lo que se pueda con escenarios y los modelos de este nivel.
Tampoco simula las fórmulas de un Excel ajeno: se escribe la fórmula del resultado como `modelo: formula`.
