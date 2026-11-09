# Cartuchos de dominio (para investigaciones)

El protocolo de investigación es el motor; un **cartucho** es lo que cambia de un rubro a otro. Tiene dos módulos:

- **Módulo A — Mapa de fuentes:** dónde están los registros que prueban cosas en ese dominio (N1, N2), qué cuestan y
  cuál es su equivalente abierto.
- **Módulo B — Modos de falla del dominio:** lo que mata proyectos en ese rubro y que un no especialista no mira.
  Alimenta directamente las hipótesis asesinas.

Al abrir una investigación, el cartógrafo parte del cartucho que calce (`--cartucho biblioteca/dominios/<x>.md`) y lo
amplía; no empieza de cero.

## Núcleo y cartuchos propios

- Los cartuchos que trae el núcleo (`propiedad-industrial.md`) se actualizan con el núcleo: **no los edites**.
- Para un rubro nuevo, copia `_plantilla-dominio.md` con otro nombre (`biblioteca/dominios/<rubro>.md`): es de tu
  empresa y ninguna actualización lo toca.
- Lo que aprendas sobre un cartucho del núcleo queda en `empresa/investigacion/lecciones.csv` (columna `cartucho`):
  cada investigación nueva con ese cartucho lo lee junto con él.
- Un cartucho no lleva hechos de ningún caso: solo dónde buscar y qué suele fallar.
