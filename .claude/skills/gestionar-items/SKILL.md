---
name: gestionar-items
description: Gestiona los ítems de un proyecto de tipo cartera — agregar ítems, moverlos entre etapas verificando requisitos, crear y actualizar sus fichas (tesis, riesgos, condiciones de salida, fecha de revisión), retirarlos y listar el pipeline. Úsala cuando el usuario hable de agregar, evaluar, promover, pasar a otra etapa, descartar, retirar, vender o revisar un bot, acción, postulación, proveedor, iniciativa u otro ítem de una cartera, o pida ver el pipeline o una ficha.
---

# Gestionar ítems

Archivos: `items/items.csv`, `items/etapas.yaml`, `items/fichas/<id>.md` (plantilla `_plantilla-ficha.md`).

## Agregar ítems
1. Id corto y estable (ticker, código del bot, n° de postulación). Etapa inicial: la primera de `etapas.yaml`
   salvo que el usuario indique otra.
2. Completa nombre, categoría y etiquetas. Si trae datos (métricas), regístralos vía la skill `metricas`.
3. Para varios ítems de una vez (una lista o un Excel), muestra la tabla a crear y confirma una sola vez.

## Mover de etapa
1. Revisa los requisitos de la etapa destino en `etapas.yaml` (métricas y archivos). Puedes apoyarte en
   `python herramientas/evaluar_metricas.py <ruta-proyecto>`, que lista requisitos incumplidos y candidatos a avanzar.
2. Si no cumple, dilo con precisión (qué falta) y pregunta si igual se mueve; si el usuario insiste, muévelo y
   deja la excepción en `comentario` y en el historial de la ficha.
3. Actualiza `etapa` y `fecha_etapa` en `items.csv`, agrega una línea al historial de la ficha y, si es una
   decisión relevante (entrar, salir, retirar), regístrala en `seguimiento/decisiones.csv` con su fundamento.

## Fichas
- Crea la ficha desde `_plantilla-ficha.md` cuando el ítem llegue a la etapa que la exige, o antes si el usuario quiere.
- La **tesis** se escribe como afirmaciones verificables ("debe seguir siendo cierto que…"), y las condiciones
  de salida como umbrales o hechos observables. Ayuda al usuario a formularlas; no inventes datos.
- Fija `fecha_revision` (por defecto: la cadencia de revisión del proyecto) y actualízala en cada revisión.
- En "Métricas clave actuales" no copies números fijos: referencia la evaluación, o incluye una tabla con fecha.

## Pipeline
"¿Cómo está la cartera?" → cantidad por etapa, movimientos recientes, candidatos a avanzar, fichas con
revisión vencida y requisitos incumplidos, desde `evaluar_metricas.py`.

## Retirar
Etapa `retirado` (o la equivalente), motivo en `comentario`, cierre en el historial de la ficha y decisión
registrada. No se borran ítems ni fichas: la historia sirve para aprender.
