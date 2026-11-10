# La cascada: apuestas → objetivos → metas → iniciativas

## Marcos
- **OKR:** objetivos cualitativos e inspiradores, 2 a 4 resultados clave medibles por objetivo; `perspectiva` se
  usa para el ámbito (crecimiento, clientes, operación, personas) o se deja vacía.
- **BSC (cuadro de mando):** `perspectiva` ∈ financiera, clientes, procesos, aprendizaje; cada perspectiva con 1 a 3
  objetivos y relaciones causa-efecto de abajo hacia arriba.
- **Propio:** el marco de la empresa; `perspectiva` lleva su categoría.

## Cómo escribir cada fila
- **Objetivo** (`objetivos.csv`): verbo + qué + para quién; sin cifras (las cifras van en las metas).
  `O-01,crecimiento,Ganar la cuenta corporativa en la zona norte,Gerente comercial,propuesto,`
- **Meta** (`metas.csv`): un indicador por fila y por año; `direccion` mayor_mejor, menor_mejor o informativa; la
  **línea base** con su año; `fuente_dato` dice de dónde saldrá el real (una métrica del proyecto —mismo id que en
  `metricas/`, así `--revision` lo toma solo—, `finanzas`, un sistema, una encuesta).
  `O-01,ingresos_zona_norte,$,mayor_mejor,120000000,2026,2027,180000000,finanzas (línea ingresos zona norte),`
  Una fila por año del horizonte: 2027, 2028, 2029 (y 2030, 2031 en un 5YP).
- **Iniciativa** (`iniciativas.csv`): lo que cambia para mover el indicador, con responsable, fechas, inversión e
  **impacto** (qué línea financiera mueve y cuánto por año; es lo que alimenta la proyección).
  `I-01,O-01,Abrir oficina comercial en Antofagasta,Gerente comercial,2027-03-01,2027-09-30,45000000,ingresos +60M/año desde 2028; gastos +30M/año,aprobada,,`

## Validación mecánica (`estrategia.py --revisar`)
Error: objetivo activo sin indicador o sin meta en algún año del horizonte; meta fuera del horizonte; meta no
numérica; iniciativa o revisión que apunta a un objetivo inexistente; estados o fechas inválidos; rojo sin decisión.
Aviso: sin línea base, sin fuente del dato, sin responsable, objetivo activo sin iniciativa.

## Cuántos
Tres a cinco apuestas; uno a tres objetivos por apuesta; uno o dos indicadores por objetivo; una a tres
iniciativas por objetivo. Más que eso, el plan se vuelve un inventario y nadie lo sigue.
