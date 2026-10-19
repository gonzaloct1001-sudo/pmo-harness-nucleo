# Contexto particular del proyecto

> PROYECTO FICTICIO DE PRUEBA del arquetipo `postulacion`. Nada es real.

## En una frase
Postulación de AgroSur Tecnología al Fondo Impulsa Innovación Regional 2026 (cierre 10-11-2026, 15:00) para
validar su sistema de riego con sensores de humedad con 3 productores y la Universidad Regional como asociada.

## Arquetipos y cómo se trabaja
- Postulación: matriz en `postulacion/requisitos.csv`, barrido en `barrido-requisitos.csv`, estado con
  `python herramientas/postulacion.py ejemplos/postulacion-demo`.
- Presupuesto: `economico/presupuesto.yaml` → `python herramientas/presupuesto_postulacion.py ejemplos/postulacion-demo/economico/presupuesto.yaml`.

## Reglas particulares
- Las bases vigentes son B01 + Anexo 2 + Aclaración N°1 (la aclaración baja el límite a 12 páginas y exige
  declarar el uso de IA en el formulario: esa declaración la decide y la hace el postulante).
- Firma el representante legal: Paula Soto.

## Notas de estilo
- Ver `contexto/estilo.md`.
