---
name: guardar-cambios
description: Guarda el trabajo en Git y lo sube a GitHub de forma segura: verifica que no suban archivos confidenciales, deja el traspaso al día y avisa de mejoras sin enviar. Úsala con «guarda», «respalda», «sube», «terminé por hoy», al cerrar la sesión, al final de cualquier tarea que modificó archivos, o para bajar cambios en otro computador.
---

> Reglas que aplican (léelas si no están en tu contexto): `reglas/trabajo.md`, `reglas/datos.md`, `reglas/entregables.md`, `reglas/confidencialidad.md`.

# Guardar cambios

## Guardar y subir
1. `git status --short`. Si no hay cambios, dilo y termina.
2. **Traspaso:** si en la sesión se modificó un proyecto, verifica que su `seguimiento/traspaso.md` esté al día
   (regla 17 de `AGENTS.md`): qué se hizo, en qué quedó, el próximo paso, qué se comprobó y qué no se pudo.
   Actualízalo si falta. Si `python herramientas/mejoras.py` muestra anotaciones sin enviar, dilo en una línea;
   no exportes sin que el usuario lo pida.
3. **Revisión de seguridad** antes de agregar: si aparece algún archivo dentro de `_entrada/`, cualquier
   `.pdf` dentro de `contractual/`, archivos de `contenidos/archivos/` o `entrega/final/`, o archivos que parezcan
   credenciales (`.env`, claves, contraseñas), detente y pregunta. Refuerza `.gitignore` si corresponde.
4. `git add -A`
5. Mensaje de commit en español, en una línea, que describa lo hecho. Ej.:
   `andes: reporte semanal S39, 2 riesgos nuevos, avance SP1 actualizado`
   Sin líneas de coautoría (`Co-Authored-By`) ni menciones a herramientas de IA.
6. `git commit`. El control de Git (`.githooks/pre-commit`) revisa confidenciales y planillas: si detiene el commit,
   corrige lo que indica y vuelve a intentar. **Nunca uses `--no-verify`.** Si el estado avisó que el control está
   inactivo, actívalo antes con `git config core.hooksPath .githooks`.
7. `git pull --rebase` y luego `git push`. Si el modo nube está activo (`.harness/nube.yaml`), antes revisa
   `python herramientas/bandeja.py --listar`: un PR de la nube sobre el mismo proyecto se integra o se revisa primero,
   para no pisar su trabajo ni que él pise el tuyo.
8. Si hay conflicto: no lo resuelvas a ciegas. Explica en simple qué archivo chocó y por qué (normalmente,
   cambios hechos en otro computador sin sincronizar). Para CSV y Markdown, propón la versión combinada y
   pide confirmación.
9. Confirma en una línea: qué se subió y a qué rama.

## Empezar en otro computador o retomar
- Primera vez: `git clone <url-del-repo-privado>` (o el instalador con la opción de clonar empresas; ver README),
  y luego `instalar`, que detecta que es un computador nuevo.
- Cada vez que se retoma: `git pull` antes de trabajar (el estado de inicio avisa si hay commits por bajar).

## Buenas prácticas que recuerdas al usuario solo si aplica
- Guardar al final de cada sesión de trabajo, no solo al final de la semana.
- No trabajar el mismo proyecto en dos computadores sin sincronizar entre medio.
- Antes de cambiar de IA, guardar: así la nueva retoma desde el traspaso y con todo sincronizado.
