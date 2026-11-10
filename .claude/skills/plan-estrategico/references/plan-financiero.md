# Plan financiero a 3 o 5 años (3YP / 5YP)

El plan financiero **sale de las iniciativas**, no al revés. Cada supuesto de la proyección se rastrea a una
iniciativa (`impacto` en `iniciativas.csv`) o a una tendencia declarada (inflación, crecimiento vegetativo).

## Con finanzas en el harness (lo habitual)
1. Ubica el proyecto con arquetipo `finanzas` (este mismo, o el de `estrategia.proyecto_finanzas`).
2. En `finanzas/proyeccion.yaml`: `anios` = horizonte del plan (3 o 5) y `anio_base` = el último cierre anual.
3. Traduce cada iniciativa a supuestos por línea y año (ingresos por línea o unidad, costo de ventas, gastos por
   área, inversiones y su depreciación, dotación, financiamiento), con una nota que cite la iniciativa (`I-01`).
   Lo que no viene de una iniciativa es tendencia: dilo y cita el histórico.
4. `python herramientas/finanzas.py proyectos/<slug> --proyectar --excel plan-financiero.xlsx`: resultados, balance y
   caja proyectados; el balance debe cuadrar cada año; si la base no cuadra, el script lo dice y se corrige antes.
5. Escenarios: base, conservador y ambicioso (`finanzas/escenarios.csv`), con las dos o tres variables que más
   mueven el resultado; el `analista-financiero` revisa razonabilidad (márgenes, caja mínima, endeudamiento).
6. Las cifras del plan (ingresos, EBITDA, caja al cierre de cada año) se vuelven metas de los objetivos
   financieros en `metas.csv`, con `fuente_dato: finanzas`.

## Sin finanzas en el harness
Tabla simple en el documento (ingresos, costos, EBITDA, inversiones, caja por año) marcada «estimación», con sus
supuestos listados. Propón crear el proyecto `finanzas` (`gestion-financiera`, modo arranque): el plan se vuelve
mucho más defendible con la proyección integrada.

## Lo que el directorio preguntará
Cuánto cuesta el plan (inversión total y por año), de dónde sale la caja (operación, deuda, capital), cuándo se
recupera, qué pasa si las apuestas fallan a la mitad (escenario conservador) y qué decisión se pide hoy.
