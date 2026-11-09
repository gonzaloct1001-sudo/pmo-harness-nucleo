# Tarjeta de referencia — marcas y fuentes

## Marcas de afirmación

Toda frase del entregable lleva marca. Sin marca no se publica.

| Marca | Estado | Qué prueba | Debe llevar | Dónde vive |
| --- | --- | --- | --- | --- |
| H | Hecho verificado | Que algo es así | Fuente N1–N3 abierta en esta investigación, fecha del dato, fecha de consulta | `expediente.csv` |
| D | Derivado | Que se sigue de uno o más H | Los H de origen (por ID) y la operación explícita | `expediente.csv` |
| T | Testimonio | Que alguien lo afirmó, no que sea cierto | El sujeto, dónde y cuándo lo dijo | `expediente.csv` |
| P | Pista | Dónde buscar; nada sobre el fondo | La fuente N5–N6 donde se vio y qué registro habría que leer para convertirla en H | `expediente.csv` |
| I | Inferencia | Juicio del analista | Confianza y el hallazgo que la revertiría | `conclusiones.csv` y `E4_analisis.md` |
| S | Supuesto | Nada: se asume para avanzar | Qué costo tiene si es falso | `E4_analisis.md` |
| V | Vacío | Que se buscó y no se encontró (o que no se pudo buscar) | Dónde se buscó y con qué términos | `vacios.csv` |

Las cuatro confusiones que destruyen informes: T leído como H, D leído como H, P leída como H, V ausente.

En el texto, una afirmación se cita por su ID: `E-07` (expediente), `V-02` (vacío), `C-03` (conclusión),
`HA-2` (hipótesis), `U-04` (universo), `I-01` (impugnación).

## Niveles de fuente

| Nivel | Qué es | Qué puede sostener | Marca que admite |
| --- | --- | --- | --- |
| N1 | Registro constitutivo: el hecho *es* el registro | Existencia, titularidad, vigencia, estado formal | H |
| N2 | Documento bajo obligación legal o profesional | Cifras, fechas, relaciones declaradas | H |
| N3 | Revisado por pares o firmado por responsable identificable | Método, evidencia técnica | H |
| N4 | Comunicación de la parte interesada | Lo que dicen, no lo que es | T |
| N5 | Prensa especializada | Pistas y cronología | P (o T si se cita a alguien) |
| N6 | Agregadores, wikis, foros, memoria del modelo | Nada. Solo puntero | P |

1. Toda afirmación portante necesita anclaje en N1–N3.
2. N4 nunca prueba un hecho del mundo.
3. N6 jamás se cita en el entregable.
4. Dos fuentes del mismo origen son una sola fuente. La métrica es orígenes distintos, no URLs (columna `origen`).
5. Un documento entregado por quien encarga la investigación vale como la fuente que es (un contrato firmado es N2),
   pero su `origen` es quien lo entregó: no confirma por sí solo lo que esa misma parte afirma.

## Fechas

- **Fecha del dato** (`dato_al`): la fecha de corte que da la fuente, es decir, a qué momento corresponde lo que dice.
  Para un registro consultado hoy, la fecha de la consulta o de su última actualización; para un informe anual, el
  año que informa. No es la fecha que aparece dentro de la afirmación: «la patente se presentó en 2008», leído hoy en
  el registro, tiene dato al día de hoy. Admite AAAA, AAAA-MM o AAAA-MM-DD.
- **Fecha de consulta** (`fecha_consulta`): cuándo se abrió la fuente en esta investigación (AAAA-MM-DD).
- La prueba 4 mira la fecha del dato: lo que describe el presente con datos de hace más de dos años necesita
  verificar su vigencia (se anota «vigencia verificada con E-xx» en la nota).

## Estados

- Expediente: `vigente` o `retirada` (el árbitro retira lo no portante sin borrarlo: queda en el archivo).
- Hipótesis asesinas: `abierta`, `sobrevivio` (se buscó lo que la mataría y no apareció) o `disparo`.
- Universo: `entra`, `reserva` (falta evidencia para evaluarlo) o `excluido` (hay evidencia negativa, citada).
- Conclusiones: `vigente`, `corregida` o `retirada`.
- Vacíos: `buscado-sin-resultado`, `no-buscado`, `inaccesible` o `cerrado`.
- Bitácora: `nulo` (se buscó y no hubo nada) o `encontrado`. Lo no buscado no va en la bitácora.
