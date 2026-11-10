# Contexto particular del proyecto

## En una frase
Gestión financiera ficticia de una distribuidora: presupuesto 2026, cierre mensual, estados de gestión, forecast y proyección.

## Arquetipos y cómo se trabaja
finanzas: cada mes se importa el balance de comprobación desde `_entrada/10-contabilidad/`, se mapean las cuentas nuevas,
se revisan desvíos e indicadores, se emite el informe y se cierra el período (`finanzas.py --cerrar`).

## Reglas particulares
- Ninguna cifra se escribe a mano: todo sale de `finanzas/real.csv` importado.
- Un período cerrado se reabre solo con motivo y quién (`--reabrir`).

## Rutina de actualización de datos
1) exportar el balance de comprobación del mes  2) `finanzas.py --importar ... --periodo AAAA-MM`  3) `--estados`  4) `--registrar`  5) `--cerrar`
