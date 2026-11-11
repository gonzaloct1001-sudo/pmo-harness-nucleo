---
name: explicar
description: Explica algo complejo en una página web de un solo archivo, con cifras clave, gráficos (barras, líneas, tornado, histograma), pasos y línea de tiempo, que se abre con doble clic y se puede imprimir. Úsala con «explícamelo simple», «muéstramelo visual», «hazme un gráfico», «en una página para el comité», o cuando se pida el «plan detallado» de una tarea.
---

> Reglas que aplican (léelas si no están en tu contexto): `reglas/datos.md`, `reglas/entregables.md`, `reglas/confidencialidad.md`.

# Explicar (página visual)

Herramienta: `python herramientas/explicar.py <entrada.md> --proyecto proyectos/<slug> [--abrir]`. Tú escribes un
Markdown corto con bloques; la herramienta arma la página (un solo `.html`, sin internet, claro y oscuro, imprimible)
en `proyectos/<slug>/explicaciones/`. El formato de los bloques está en su encabezado: léelo la primera vez.

## 1. Antes de escribir
1. **Qué tiene que entender quien la lea, en una frase.** Esa frase abre la página (una cita con `>`). Si no puedes
   escribirla, falta entender el asunto: pregunta o revisa los datos primero.
2. **De dónde salen los números.** De los registros del proyecto o de la salida de un script (`status.py`,
   `evaluar_metricas.py`, `finanzas.py --estados`, `evm_cpm.py`…), nunca de memoria (principio 2). Lo que falte se
   escribe `[PENDIENTE: …]` y la página no se genera hasta completarlo (salvo `--borrador`).
3. **Para quién es.** Si va a salir de la empresa, es un entregable: `verificar_autoria.py` antes de enviarla.

## 2. Elegir la forma (la pregunta manda, no el gusto)
| Lo que hay que mostrar | Bloque |
|---|---|
| Uno a cuatro números que resumen todo | `cifras` (no un gráfico) |
| Comparar categorías (áreas, frentes, proveedores) | `grafico` tipo `barras`; si los nombres son cortos y pocos, `columnas` |
| Cómo cambia algo en el tiempo, real contra plan | `grafico` tipo `lineas` |
| Qué variable pesa más en un resultado | `grafico` tipo `tornado` |
| Qué tan probable es un resultado (muchos escenarios o mediciones) | `grafico` tipo `histograma`, con `meta:` si hay un objetivo |
| El detalle exacto, o estados por ítem | una tabla (Verde, Amarillo y Rojo llevan su punto de color) |
| Un proceso o un plan de acción | `pasos` |
| Fechas que vienen | `tiempo` |

Límites que la herramienta hace cumplir: hasta cuatro series por gráfico (con más, agrupa en «Otros» o divide en dos),
nunca dos escalas en un mismo gráfico, y una sola barra no es un gráfico (usa `cifras`). Un gráfico por idea; si la
tabla lo dice mejor, usa la tabla.

## 3. Escribir y generar
1. Escribe el Markdown en `proyectos/<slug>/explicaciones/<tema>.md`: bloque inicial con `titulo` y `subtitulo`, la
   frase clave, y de tres a seis secciones cortas. Cada gráfico lleva `titulo` (lo que se ve, no «Gráfico 1») y `unidad`.
2. `python herramientas/explicar.py proyectos/<slug>/explicaciones/<tema>.md --proyecto proyectos/<slug> --abrir`.
   Si termina con «No se generó la página», corrige lo que indica (dice el bloque y el motivo).
3. Revisa la salida contra los datos: abre «Ver los datos» de un gráfico y compara dos cifras con su fuente.
4. Dile al usuario la ruta, qué muestra en una línea y qué quedó fuera.

## 4. Plan detallado de una tarea (principio 23)
Cuando el usuario elige «plan detallado»: la frase clave es el resultado esperado; `pasos` con lo que se hará y qué
toca cada paso; una tabla «Qué necesito de ti» (decisión, quién, para cuándo); `tiempo` si hay fechas; y los riesgos
en una lista. No ejecutes nada hasta su sí.

## 5. Compartir
La página queda en la carpeta del proyecto y se sube al repositorio privado como cualquier salida. **No la publiques
en ningún servicio por tu cuenta**: publicar saca información de la carpeta. Si el usuario pide un enlace para
compartir, explícale qué se expone y hazlo solo con su sí.
