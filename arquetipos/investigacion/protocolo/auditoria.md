# Las ocho pruebas de auditoría

Se aplican en E5, antes de P5, sobre las conclusiones y el borrador del entregable. Las corre el árbitro y quedan en
`auditoria.csv` (`pasa` o `falla`, con el detalle). Al cerrar, el validador repite las mecánicas sobre el entregable
final. Cada una tiene criterio de fallo.

| # | Prueba | Pregunta | Falla si | Quién la corre |
| --- | --- | --- | --- | --- |
| 1 | Trazabilidad | Diez afirmaciones al azar: ¿se reconstruye la cadena hasta la fuente? | Más de una no llega. Vuelve el entregable completo, no se parcha | Árbitro, con la muestra al azar del validador (`--muestra`; en forense, todas las portantes) |
| 2 | Tercero hostil | ¿Qué diría el abogado de la contraparte? Se responde por escrito | No hay nada que responder | Árbitro |
| 3 | Ausencia | ¿Qué debería existir si esto fuera cierto, y lo busqué? | Una conclusión descansa en algo que no apareció sin haberlo buscado donde correspondía | Árbitro |
| 4 | Antigüedad | ¿Cuál es el dato más viejo del que depende una conclusión portante? | Una conclusión del presente descansa en un dato de más de dos años sin verificar vigencia | Validador (`--auditar`) |
| 5 | Independencia | ¿Las fuentes que confirman derivan del mismo origen? | Una conclusión portante tiene un solo origen y ninguna fuente N1 (un registro constitutivo es su propio origen y basta) | Validador |
| 6 | Entidad | ¿Cada persona, empresa, documento o activo lleva identificador duro? | Cualquier entidad sin identificador | Validador (universo) y árbitro (texto) |
| 7 | Reversibilidad | Por cada conclusión portante, ¿qué hallazgo la revertiría? | La respuesta es «ninguno» o está vacía | Validador |
| 8 | Cobertura | ¿La bitácora registra todas las búsquedas, incluidas las nulas? | No hay búsquedas nulas registradas | Validador |

Al cerrar, cada conclusión lleva su condición de revisión en una línea: «Alta confianza. Cambiaría si aparece X.»

## Muestra al azar (prueba 1)

`python herramientas/investigacion.py <proyecto> --instancia <id> --muestra` elige las afirmaciones al azar con una
semilla que queda impresa (y en `auditoria.csv` con `--registrar`). Así el árbitro no elige qué revisar y cualquiera
puede repetir la misma muestra.

## Las pruebas fuera de una investigación

Para auditar un informe, un estudio o una sección de una postulación que afirma hechos del mundo, se pueden aplicar
las mismas ocho pruebas sobre sus afirmaciones portantes (ver la skill `investigar`, «Auditar un documento existente»).
