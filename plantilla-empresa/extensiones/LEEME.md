# Extensiones propias de la empresa

Aquí va lo que la empresa le agrega al harness: herramientas, hooks y pruebas propias. Esta carpeta es de la empresa:
**ninguna actualización del núcleo la toca**. Es el lugar correcto para cualquier ajuste al comportamiento del harness;
los archivos del núcleo (`herramientas/`, `.claude/skills/` del índice, `reglas/`, `pruebas/`) no se editan, porque se
reemplazan al actualizar.

| Quiero… | Va en… |
|---|---|
| Una herramienta propia, o una variante de una del núcleo | `empresa/extensiones/<nombre>.py` |
| Un hook propio (algo que corre solo al iniciar, al escribir, al terminar) | `empresa/extensiones/<nombre>.py` y su entrada en `.claude/settings.json` apuntando a esa ruta |
| Probar que mis extensiones siguen funcionando | `empresa/extensiones/pruebas.py` (o `pruebas_<tema>.py`) |
| Una skill propia | `.claude/skills/<nombre-propio>/SKILL.md` (un nombre que el índice del núcleo no use) |
| Una regla o preferencia propia | `empresa/estilo.md`, o el `CLAUDE.md` del proyecto |
| Definir qué es confidencial aquí | `empresa/confidencialidad.yaml` |

## Cómo se escribe una extensión
- Se ejecuta desde la raíz de la carpeta: `python empresa/extensiones/<nombre>.py`.
- Para usar funciones del núcleo, agrega `herramientas/` a la ruta de Python al inicio del archivo
  (`sys.path.insert(0, "herramientas")`) e impórtalas. No copies el archivo del núcleo: importa lo que necesites y
  escribe solo la diferencia.
- Las funciones del núcleo pueden cambiar con una versión nueva. Por eso existen las pruebas propias.

## Pruebas propias
`empresa/extensiones/pruebas*.py` (y `empresa/pruebas/*.py`) son scripts que terminan con código 0 si todo está bien y
distinto de 0 si algo falla. No deben modificar datos de los proyectos.
- `python pruebas/ejecutar_pruebas.py` las ejecuta junto con la batería del núcleo y las lista como «propia: …».
- Al actualizar el núcleo se ejecutan antes y después: **si una que pasaba deja de pasar, la actualización se revierte
  sola** y te dice cuál; nada cambia hasta que ajustes la extensión o el núcleo corrija.

## Si el núcleo debería traerlo
Si tu extensión resuelve algo que le serviría a cualquiera, o corrige un error del núcleo, anótalo para quien lo
mantiene: `python herramientas/mejoras.py --anotar --tipo agregar --donde <herramienta o skill> --que "..." --evidencia
"empresa/extensiones/<nombre>.py"`. Cuando una versión nueva lo traiga, puedes retirar tu extensión.
