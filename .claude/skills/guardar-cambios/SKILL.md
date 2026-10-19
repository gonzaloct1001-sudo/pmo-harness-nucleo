---
name: guardar-cambios
description: Guarda el trabajo del día en Git y lo sube a GitHub de forma segura, verificando que no se suban archivos confidenciales y dejando el traspaso al día para que otra sesión, otro computador u otra IA retome. Úsala cuando el usuario diga guardar, respaldar, subir, sincronizar, "commitear", cerrar la sesión o terminar el día, y ofrécela al final de cualquier tarea que haya modificado archivos. También para bajar los cambios más recientes al empezar a trabajar en otro computador.
---

# Guardar cambios

## Guardar y subir
1. `git status --short`. Si no hay cambios, dilo y termina.
2. **Traspaso:** si en la sesión se modificó un proyecto, verifica que su `seguimiento/traspaso.md` esté al día
   (regla 17 de `AGENTS.md`): qué se hizo, en qué quedó y el próximo paso. Actualízalo si falta.
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
7. `git pull --rebase` y luego `git push`.
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
