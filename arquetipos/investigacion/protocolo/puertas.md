# Puertas de control

Una puerta no es una revisión de calidad: es una condición binaria. Se cumple o el trabajo vuelve.
P0, P2 y P5 las firma una persona, no un agente. Se registran en `puertas.csv` (estado, quién firma, fecha y nota).

| Puerta | Entre | Criterio de paso | Firma | Si no pasa |
| --- | --- | --- | --- | --- |
| P0 | E0→E1 | Pregunta de decisión escrita, decisor identificado, asimetría del error declarada. Si la pregunta implica universos distintos, se declara la separación en dos investigaciones | Persona | Se devuelve al solicitante |
| P1 | E1→E2 | Existe al menos una fuente N1 o N2 identificada | Árbitro | Se declara dominio sin ancla registral y se baja la pretensión a informe de indicios |
| P2 | E2→E3 | Las hipótesis asesinas corrieron y ninguna disparó | Persona | Se reencuadra y vuelve a E0 (P0 se firma de nuevo), o se cierra |
| P3 | E3→E4 | Cada candidato entró con señal observable y fuente | Árbitro | Se purgan los candidatos sin señal |
| P4 | E4→E5 | Cero afirmaciones portantes sin sustento | Árbitro | Vuelven al bibliotecario o bajan a I, S o V |
| P5 | E5→E6 | El refutador no tumbó ninguna conclusión portante, o las tumbadas se retiraron; las ocho pruebas pasan | Persona | Se retira la conclusión; nunca se la defiende |

**Sobre P5:** una lista vacía de impugnaciones es fallo del refutador, no éxito del analista. Y una conclusión tumbada
se retira, no se matiza.

**Sondeo:** solo P0 y P2; las demás quedan `no-aplica` y el entregable dice «sondeo: sin contrastación».

## Lo que el validador revisa en cada puerta

`python herramientas/investigacion.py <proyecto> --revisar` no deja pasar una puerta firmada sin su criterio mecánico:

| Puerta | El validador exige |
| --- | --- |
| P0 | Encuadre con pregunta, negación, decisor, asimetría, intensidad, tolerancia y criterio de éxito; `decisor` en el manifiesto; firma de una persona |
| P1 | Al menos una fuente N1 o N2 en el mapa, o `producto: informe-de-indicios` en el manifiesto |
| P2 | Al menos 3 hipótesis (lo esperado son 5 o 6), ninguna `abierta` ni `disparo`, y cada una cerrada con evidencia H o D (nunca solo con testimonios); firma de una persona |
| P3 | Cada candidato que `entra` con identificador, señal y sustento; cada `excluido` con su evidencia negativa |
| P4 | Cada conclusión portante vigente con sustento H o D de fuentes N1–N3 y con «se revierte si» |
| P5 | Al menos una impugnación del pase 2 y ninguna pendiente; las conclusiones tumbadas, retiradas; en forense, dos refutadores distintos; las ocho pruebas en `pasa`; firma de una persona |
| Todas | Que la anterior esté firmada (o `no-aplica`) y que la firma tenga nombre y fecha |

Lo que exige juicio (si la pregunta es la correcta, si una señal es observable, si una impugnación es buena) lo
deciden el árbitro y la persona; el validador solo impide que se salte lo verificable.
