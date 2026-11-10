# Scripts propios del proyecto

Aquí van los cálculos que son específicos de este proyecto y no forman parte del núcleo del harness
(por ejemplo: rentabilidad de una cartera, métricas de bots de trading, cubicaciones de una obra).

Convención: cada script lee de `datos/` y escribe sus resultados en `metricas/mediciones.csv`,
para que el resto del harness (reportes, validaciones, reuniones) los use sin saber cómo se calcularon.
