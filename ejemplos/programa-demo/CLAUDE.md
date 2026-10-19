# Contexto particular del programa

> PROGRAMA FICTICIO DE PRUEBA del arquetipo `programa`. Nada es real.

## En una frase
Contrato único con Distribuidora Austral (01-06-2026 al 30-04-2027, $1.090 MM tras la Enmienda N°1) ejecutado en tres
subproyectos: sp1 ERP, sp2 App de despacho (ágil) y sp3 Portal de clientes (incorporado por la Enmienda N°1).

## Cómo se trabaja
- Estado consolidado: `python herramientas/programa.py ejemplos/programa-demo --hoy 2026-10-15 --excel`.
- Cada subproyecto se gestiona en `subproyectos/<id>/` con su cronograma, riesgos, minutas y reportes.
- Presupuesto, contingencia, personas y enmiendas se gestionan en el programa.

## Problemas sembrados a propósito
- La Enmienda N°2 extiende el plazo de sp2 al 31-03-2027, pero no se aplicó en su línea base.
- Luis Mora está asignado a tres subproyectos a la vez desde enero (130%).
- El pronóstico de sp2 supera su presupuesto vigente.
