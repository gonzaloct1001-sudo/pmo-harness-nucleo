# Protocolo de Investigación Auditable — forma operativa

**Versión del protocolo: 1.1** (cada investigación anota en su `manifiesto.yaml` la versión bajo la que corre).

Definición: una investigación es confiable cuando un tercero hostil, con acceso solo al entregable y su expediente,
puede reconstruir cómo se llegó a cada afirmación y señalar el punto exacto donde se rompería.

Documentos del protocolo (se leen en este orden la primera vez):
1. este archivo (etapas, separaciones, intensidad, tolerancia, roles);
2. `marcas-y-fuentes.md` (cómo se marca cada afirmación y cuánto vale cada fuente);
3. `puertas.md` (las seis condiciones para avanzar);
4. `auditoria.md` (las ocho pruebas antes de cerrar).

## Las siete etapas

Cada etapa tiene su archivo en la carpeta de la investigación, con el mismo número.

| Etapa | Archivo | Qué produce | Esfuerzo | Rol | Puerta al terminar |
| --- | --- | --- | --- | --- | --- |
| E0 Encuadre | `E0_encuadre.md` | Pregunta de decisión, su negación, decisor, asimetría del error | 5% | encuadrador | P0 (persona) |
| E1 Cartografía | `E1_mapa_fuentes.csv` | Mapa de fuentes del dominio | 10% | cartógrafo | P1 (árbitro) |
| E2 Hipótesis asesinas | `E2_hipotesis.csv` | Las cinco o seis, escritas antes de buscar y corridas | 20% | refutador (las escribe) y bibliotecario (las corre) | P2 (persona) |
| E3 Universo | `E3_universo.csv` | Candidatos o alternativas con señal observable y fuente | 25% | analista, con el bibliotecario | P3 (árbitro) |
| E4 Triaje y análisis | `E4_analisis.md` y `conclusiones.csv` | Argumento citado por ID y conclusiones con su condición de reversión | 20% | analista | P4 (árbitro) |
| E5 Contrastación | `E5_impugnaciones.csv` y `auditoria.csv` | Impugnaciones del refutador y las ocho pruebas | 15% | refutador y árbitro | P5 (persona) |
| E6 Entregable | `E6_entregable.md` | Documento arbitrado | 5% | editor | cierre |

Registros que acompañan todas las etapas: `expediente.csv` (hechos), `bitacora.csv` (todas las búsquedas, incluidas
las nulas), `vacios.csv` (lo que falta), `puertas.csv` (firmas), `metodo.csv` (lo aprendido sobre cómo investigar) y
`manifiesto.yaml` (identidad y configuración de la investigación).

Si la pregunta no tiene un universo de candidatos (por ejemplo, «¿se puede hacer X?»), E3 queda vacía y P3 se marca
`no-aplica`.

El orden importa. **Construir antes de matar es el error que todo esto existe para impedir:** nada entra a E3 ni a E4
mientras P2 no esté firmada.

## Las tres separaciones

1. Recuperación separada de interpretación (quien busca no concluye; quien concluye no abre fuentes).
2. Construcción separada de refutación (quien refuta no ve el razonamiento de quien construyó).
3. Hecho separado de inferencia, marcado en el texto (ver `marcas-y-fuentes.md`).

## Niveles de intensidad

| Nivel | Etapas | Refutación | Duración | Cuándo |
| --- | --- | --- | --- | --- |
| Sondeo | E0, E2, E6 (con expediente y bitácora) | Solo el pase 1 (hipótesis asesinas) | 2 a 4 h | Decidir si vale la pena investigar |
| Estándar | Las siete | Pase 1 y un refutador en E5 | 2 a 5 días | Decisión con costo real pero reversible |
| Forense | Las siete, trazabilidad de todas las afirmaciones portantes | Pase 1 y dos refutadores independientes en E5 (otro asistente u otro modelo) | 2 a 4 semanas | Error irreversible o muy caro |

Se empieza en el nivel más bajo que sirva a la decisión y se sube cuando hace falta; nunca se empieza arriba. Subir de
nivel es una decisión de la persona que decide (se anota en `puertas.csv`, nota de la puerta en curso, y se cambia
`intensidad` en el manifiesto). Un sondeo termina con un entregable que dice «sondeo: sin contrastación».

## Eje de tolerancia

Se fija en E0 y no se cambia a mitad de camino.

- **Conservador:** pocos candidatos, todos verificados.
- **Exploratorio:** universo amplio con grados de confianza explícitos.

En modo conservador es obligatorio clasificar cada exclusión como *por evidencia negativa* (`excluido`, con su
evidencia) o *por ausencia de evidencia* (`reserva`). La segunda va a la lista de reserva y se reporta; nunca se
descarta en silencio.

## Asignación de modelo

El criterio es la verificabilidad de la tarea, no el costo.

- Juicio no verificable (E0, E2, E5, arbitraje): máxima capacidad, contexto limpio.
- Trabajo verificable (recuperación, transcripción, normalización): cualquier modelo competente.
- E5: modelo distinto al que construyó, o al menos contexto estéril.

En el harness esto se configura por empresa en `empresa/investigacion/ajustes.yaml` (`refutador.asistente` y
`refutador.modelo`). Sin ajuste, el refutador y el árbitro corren como subagentes con contexto propio.

## Roles

Encuadrador → cartógrafo → refutador (pase 1: escribe las hipótesis asesinas) → bibliotecario (las corre y arma el
expediente) → analista → refutador (pase 2: impugna las conclusiones) → árbitro → editor.

Cada rol trabaja en su propio contexto y lee solo lo que su ficha indica (`.claude/skills/investigar/references/roles/`).
Bibliotecario, refutador y árbitro tienen además un subagente propio. Con asistentes sin subagentes, cada rol se
aplica en un paso separado (regla de AGENTS.md).

## Qué cruza entre investigaciones y qué no

Una investigación **lee** el protocolo, la biblioteca y los ajustes de la empresa, y **escribe** solo dentro de su
carpeta. Nunca al revés.

- **No cruzan hechos.** El expediente es de cada investigación. Si una necesita un hecho de otra, lo reingresa con su
  propia fuente y fecha.
- **No cruza el marco.** El encuadre de cada investigación se escribe sin leer los otros.
- **No cruza el contexto.** Quien trabaja una investigación carga el protocolo, el cartucho de dominio y el expediente
  de esa investigación, nunca material de otra.
- **Sí cruza el método.** Lo aprendido se anota en `metodo.csv` y, revisado, pasa a la empresa
  (`empresa/investigacion/`) o se propone para el núcleo (una versión nueva del protocolo).

## Por qué existen algunas reglas (modos de falla aprendidos)

| Modo de falla | Regla que generó |
| --- | --- |
| Quien encarga cierra una hipótesis asesina con una tranquilidad verbal («eso ya lo tenemos resuelto») | Una hipótesis asesina solo se cierra con evidencia (H o D), nunca con un testimonio |
| Tener mandato del titular se confunde con que el titular pueda hacer lo propuesto | Mandato y facultad son dimensiones separadas de las hipótesis asesinas |
| El modo conservador degenera en «solo lo que tiene buena presencia pública» | Toda exclusión se clasifica por evidencia negativa o por ausencia de evidencia; la segunda va a reserva |
| Un dato visto en un agregador se anota como hecho del registro que reproduce | Lo visto en fuentes N5 o N6 es una pista (P) hasta leerlo en la fuente misma |
| «No consultado todavía» se anota como búsqueda nula | La bitácora solo registra búsquedas hechas; lo no buscado es un vacío `no-buscado` |

## Historial del protocolo

**1.1 (núcleo del harness 2.3.0).** Sobre la versión 1.0:
1. Se asigna quién escribe las hipótesis asesinas: el refutador (pase 1); el bibliotecario las corre; la persona firma P2.
2. Las ocho pruebas de auditoría corren en un solo momento: en E5, antes de P5 (el árbitro); al cerrar, el validador
   repite las mecánicas sobre el entregable.
3. Las seis puertas se registran en `puertas.csv` (antes P3 y P4 no tenían dónde firmarse).
4. «Pendiente» deja de confundirse con «vacío»: la bitácora registra solo búsquedas hechas y los vacíos tienen estado
   (`buscado-sin-resultado`, `no-buscado`, `inaccesible`, `cerrado`).
5. Las puertas son binarias también en las hipótesis: una hipótesis está `abierta`, `sobrevivio` o `disparo`; si
   «dispara a medias», se divide en dos.
6. El expediente tiene columna `origen`, para la prueba de independencia.
7. Cada archivo lleva el número de su etapa (antes había siete etapas y ocho archivos numerados de otra forma).
8. Marca P (pista) para lo visto en fuentes N5 o N6: orienta la búsqueda y no sostiene nada.
9. Intensidad: el pase 1 del refutador corre siempre; estándar tiene un refutador en E5 y forense, dos independientes.
10. La fuente de verdad son los archivos de la investigación; una página o documento externo es solo una vista.

**1.0.** Versión original: tres capas (núcleo, biblioteca, instancias), siete etapas, seis puertas, siete roles y
ocho pruebas.
