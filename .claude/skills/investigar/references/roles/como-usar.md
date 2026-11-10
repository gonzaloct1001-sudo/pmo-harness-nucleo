# Cómo usar los roles

Cada archivo de esta carpeta es la instrucción de un rol. En Claude Code, bibliotecario, refutador y árbitro tienen
subagente propio (`.claude/agents/`); los demás roles los aplica el asistente principal en un paso separado. En otros
asistentes, cada rol se aplica en un paso separado: se lee su ficha, se adopta solo esa perspectiva, se leen solo los
archivos que indica y se escribe su resultado antes de seguir (regla de AGENTS.md).

**Regla de contexto:** cada rol trabaja con su propio contexto. No se encadenan en una sola conversación larga. La
separación existe para que el que razona trabaje sobre material depurado, no sobre un basurero de HTML.

**Orden de ejecución:** encuadrador → cartógrafo → refutador (pase 1: escribe las hipótesis asesinas) → bibliotecario
(las corre y arma el expediente) → analista → refutador (pase 2: impugna las conclusiones) → árbitro → editor.

El refutador corre dos veces. En E2 escribe lo que tendría que ser cierto, antes de que exista trabajo que defender:
matar es barato. En E5 refuta los hallazgos ya construidos.

## Delegar al bibliotecario (el líder escribe el encargo)
Cada encargo lleva cinco cosas, o el bibliotecario adivina y duplica trabajo: **objetivo** (qué hipótesis o pregunta),
**salida** (qué archivo y qué filas: expediente, bitácora, vacíos; estado de la hipótesis), **fuentes** (cuáles usar
primero, por nombre), **límites** (qué no cubrir, porque lo cubre otro encargo) y **presupuesto** (cuántas búsquedas
y cuántas fuentes antes de parar y reportar).

El esfuerzo sigue a la intensidad, no al entusiasmo:

| Intensidad | Bibliotecarios | Presupuesto por encargo |
|---|---|---|
| Sondeo | 1 | hasta 10 búsquedas, 3 fuentes |
| Estándar | 2 a 4 en paralelo, uno por familia de fuentes (registros públicos, prensa, académicas, sitios de las contrapartes) | 10 a 15 búsquedas cada uno |
| Forense | los que pida el mapa de fuentes | sin tope; cada uno reporta al agotar su familia |

**En paralelo sin pisarse:** cuando hay más de uno, cada bibliotecario escribe en sus archivos parciales
(`expediente.parcial-<nombre>.csv`, `bitacora.parcial-<nombre>.csv`, `vacios.parcial-<nombre>.csv`, mismas columnas)
y con el rango de IDs que le dio el líder (E-101…, E-201…, E-301…). Al terminar todos, el líder une con
`python herramientas/investigacion.py <proyecto> --instancia <id> --consolidar` y recién entonces `--revisar`. Así
nada se pierde en el relato de un agente a otro: lo que cada uno encontró está en su archivo, no en su resumen.

**Todos los roles:**
- escriben solo dentro de la carpeta de su investigación;
- citan por ID (E-01, V-02, C-03, HA-1, U-04, I-01);
- nunca leen material de otra investigación;
- terminan ejecutando `python herramientas/investigacion.py <proyecto> --instancia <id> --revisar` y corrigen lo que
  les corresponda.
