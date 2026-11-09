# Investigaciones de este proyecto

Una subcarpeta por investigación (`AAAA-NN-nombre-corto/`), creada con:

    python herramientas/investigacion.py proyectos/<proyecto> --nueva <nombre-corto>

Cada investigación es aislada: tiene su propio expediente y no cita hechos de otra. Si una necesita un hecho de otra,
lo reingresa con su propia fuente y fecha. Para saber dónde va cada una y cuál es el siguiente paso:

    python herramientas/investigacion.py proyectos/<proyecto>

El protocolo está en `arquetipos/investigacion/protocolo/` y la forma de trabajar, en la skill `investigar`.
