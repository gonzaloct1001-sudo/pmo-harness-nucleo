# Cómo se trabaja esta investigación

No hace falta saber el protocolo de memoria: pídele a tu asistente **«¿cuál es el siguiente paso de la
investigación?»**. Él ejecuta `python herramientas/investigacion.py <proyecto> --instancia <esta carpeta>`, que dice en
qué etapa va, qué falta y qué se te va a pedir.

## Lo que haces tú (la persona que decide)

1. **Al empezar (P0):** confirmas que la pregunta es la correcta. No se busca nada antes de tu firma.
2. **Después de las hipótesis asesinas (P2):** confirmas que ninguna mató la idea. Si alguna disparó, se reencuadra o
   se cierra: es el momento más barato para detenerse.
3. **Antes del entregable (P5):** confirmas que lo que el refutador tumbó se retiró.

Para firmar basta con responder la frase que te propone el asistente (por ejemplo, «firmo P2»). Si algo no te calza,
dilo con tus palabras: el asistente lo corrige y, si es una preferencia tuya, la guarda para las próximas
investigaciones.

## Lo que hay en esta carpeta

| Archivo | Para qué |
| --- | --- |
| `manifiesto.yaml` | Identidad: pregunta, decisor, intensidad, tolerancia, versión del protocolo |
| `E0_encuadre.md` | La pregunta de decisión y su negación |
| `E1_mapa_fuentes.csv` | Dónde están los registros que prueban cosas en este dominio |
| `E2_hipotesis.csv` | Lo que tiene que ser cierto para que valga la pena seguir |
| `E3_universo.csv` | Candidatos o alternativas, cada uno con su señal y fuente |
| `E4_analisis.md`, `conclusiones.csv` | El argumento, citado por ID, y cada conclusión con lo que la revertiría |
| `E5_impugnaciones.csv`, `auditoria.csv` | Lo que encontró el refutador y las ocho pruebas |
| `E6_entregable.md` | El documento final |
| `expediente.csv` | Cada hecho con su marca, fuente y fechas |
| `bitacora.csv` | Todas las búsquedas, también las que no encontraron nada |
| `vacios.csv` | Lo que falta y cómo se consigue |
| `puertas.csv` | Las seis firmas |
| `metodo.csv` | Lo aprendido sobre cómo investigar (nunca hallazgos del caso) |

Marcas: **H** hecho verificado · **D** derivado · **T** testimonio · **P** pista · **I** inferencia · **S** supuesto ·
**V** vacío. El detalle está en `arquetipos/investigacion/protocolo/`.
