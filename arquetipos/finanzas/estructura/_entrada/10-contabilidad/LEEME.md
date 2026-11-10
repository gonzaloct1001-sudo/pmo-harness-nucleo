# Exportaciones de la contabilidad

Deja aquí el balance de comprobación o el libro mayor de cada mes (Excel o CSV) tal como sale del sistema contable.
No se sube a Git: lo que se sube es `finanzas/real.csv`, ya mapeado al plan de cuentas.
Importar: `python herramientas/finanzas.py proyectos/<slug> --importar _entrada/10-contabilidad/<archivo> --periodo AAAA-MM`.
