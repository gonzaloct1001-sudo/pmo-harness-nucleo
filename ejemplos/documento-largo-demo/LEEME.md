# Documento largo sobre la plantilla Word de la empresa

Ejemplo del segundo modo de `herramientas/md_a_docx.py`: un informe escrito en Markdown que se arma dentro de una plantilla Word propia de la empresa, en vez de construirse desde cero. Todo es ficticio (empresa, personas y montos).

## Contenido

| Archivo | Para qué sirve |
|---|---|
| `plantilla-informe.docx` | Plantilla ficticia: portada con marcadores, tabla de historia de revisiones, índice, punto de entrada del cuerpo, encabezado con logo y pie. Trae numeración de títulos, estilo de leyenda y un estilo de tabla propio. |
| `informe.md` | Informe de avance de 2 a 3 páginas con bloque inicial, títulos de tres niveles, tablas con semáforo, lista, lista numerada, una figura y la sección «Anexos». |
| `figura-avance.png` | Imagen del informe (avance acumulado por mes). |

## Cómo generarlo

Desde la carpeta del repositorio:

```
python herramientas/md_a_docx.py ejemplos/documento-largo-demo/informe.md informe-avance.docx --plantilla ejemplos/documento-largo-demo/plantilla-informe.docx --proyecto ejemplos/demo-andes
```

`--proyecto` es opcional: aporta el autor, el formato de fecha (`formato.formato_fecha`) y los datos de autoría. Para que la plantilla se use sola, define `formato.plantilla_word` en `proyecto.yaml` o en `empresa.yaml` (ruta relativa a la carpeta del proyecto y, si no está ahí, a `empresa/`). Con `--sin-plantilla` se vuelve al formato por defecto; en ese caso el bloque inicial del Markdown se ignora.

## Qué debería verse

- Portada con el título, el subtítulo, el código INF-2026-014, la versión 2.0, la fecha del 10-11-2026 (con el formato de fecha del proyecto) y el cliente.
- Historia de revisiones con dos filas (1.0 y 2.0), con el mismo formato que la fila de la plantilla.
- Un índice: Word lo muestra vacío con un aviso hasta que se actualice el campo. Al abrir el documento pide actualizar campos; se acepta, o se hace clic derecho sobre el índice y «Actualizar campo».
- Títulos con los estilos de la plantilla y numerados por ella (1, 1.1, 1.1.1), sin números escritos a mano.
- Tres tablas del cuerpo con el estilo de tabla de la plantilla (cabecera azul); las celdas Verde, Amarillo y Rojo de la tabla de hitos van coloreadas.
- La figura centrada, con «Figura 1. Avance físico acumulado por mes, de junio a octubre de 2026» debajo.
- «Anexos» en una página nueva, con sus dos anexos.
- Encabezado con el logo y el código `INF-2026-014`; pie con «Informe de avance trimestral · versión 2.0».
- El archivo figura a nombre del autor del proyecto, sin propiedades heredadas de la plantilla.

## Contrato de la plantilla

1. Marcadores `{{titulo}}`, `{{subtitulo}}`, `{{codigo}}`, `{{version}}`, `{{fecha}}`, `{{cliente}}` y cualquier otra clave escalar del bloque inicial, en portada, cuerpo, tablas, encabezados y pies. `{{autor}}` y `{{fecha}}` tienen valor por defecto (autoría del proyecto y fecha de hoy); `{{proyecto}}` y `{{cliente}}` toman por defecto los de `proyecto.yaml`.
2. Una fila de tabla con `{{rev.version}}`, `{{rev.fecha}}`, `{{rev.descripcion}}` y `{{rev.autor}}` se repite por cada elemento de `revisiones`; sin revisiones se elimina.
3. Un párrafo `{{indice}}` pasa a ser una tabla de contenido (niveles 1 a 3).
4. Un párrafo `{{contenido}}` marca dónde entra el cuerpo; si no está, el cuerpo va al final.
5. Si queda algún `{{marcador}}` sin reemplazar, se lista y el comando termina con código 1.
