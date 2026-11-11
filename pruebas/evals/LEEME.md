# Evals de comportamiento

La batería (`python pruebas/ejecutar_pruebas.py`) prueba los scripts. Los evals prueban lo otro: **qué hace el
asistente** cuando recibe un pedido real. Son para quien mantiene el núcleo, antes de publicar una versión que
cambia reglas o skills.

## Cómo se usan
- Ver los escenarios: `python pruebas/evals/ejecutar_evals.py --listar`.
- Ejecutarlos todos, o algunos: `python pruebas/evals/ejecutar_evals.py [--solo saludo,agenda]`.
- Mirar qué quedó en la carpeta de prueba: agrega `--conservar`.

Cada escenario es una conversación real de una vuelta con el asistente: **consume cuota de su plan** y toma uno a
tres minutos. Por eso no corren con la batería ni al actualizar. Diez escenarios es una corrida razonable.

## Qué asistente
Por defecto, Claude Code en modo consola (`claude -p … --permission-mode acceptEdits`), que debe estar instalado y
con sesión iniciada. Para evaluar otro, indica su comando con `{mensaje}` donde va el pedido:

    python pruebas/evals/ejecutar_evals.py --asistente "codex exec {mensaje}"

En Windows, escribe las rutas del comando con `/`. `asistente_falso.py` no es un asistente: es el doble que usa la
batería para comprobar que el evaluador detecta lo bueno y lo malo.

## Cómo leer un resultado
Un escenario en FALLA dice qué comprobación no se cumplió y muestra el inicio de la respuesta. No siempre es un
error del asistente:
1. Si hizo algo que las reglas prohíben (tocó el núcleo, subió algo confidencial, inventó un dato): la regla o el
   control no alcanzaron. Refuerza el control (un hook, una validación) antes que el texto.
2. Si no encontró la skill o hizo algo razonable pero distinto: la descripción de la skill o el mapa no fueron claros.
3. Si la comprobación era demasiado estricta para una respuesta correcta: corrige el escenario.

Los resultados quedan en la carpeta `resultados/`, junto a este archivo (locales; no se suben).

## Agregar un escenario
En `escenarios.yaml`: `id`, `que_prueba`, `base` (un proyecto de `ejemplos/`), `mensaje`, y en `espera` solo lo que
de verdad debe pasar. Como es una sola vuelta, un pedido que exige confirmación termina sin cambios: eso también se
prueba. Pocos escenarios que importen valen más que muchos que nadie lee.
