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

**Todos los roles:**
- escriben solo dentro de la carpeta de su investigación;
- citan por ID (E-01, V-02, C-03, HA-1, U-04, I-01);
- nunca leen material de otra investigación;
- terminan ejecutando `python herramientas/investigacion.py <proyecto> --instancia <id> --revisar` y corrigen lo que
  les corresponda.
